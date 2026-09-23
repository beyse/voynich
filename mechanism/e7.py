"""E7: plaintext carried by the free choices of a local glyph process via arithmetic decoding
(mechanism/E7_PREREG.md).

    python3 -m mechanism.e7 run      # generate, recover, phenotype
    python3 -m mechanism.e7 report
"""
import json
import lzma
import math
import os
import pickle
import random
import sys
import warnings
from collections import Counter, defaultdict
from concurrent.futures import ProcessPoolExecutor

import numpy as np

from mechanism import e2 as E2
from mechanism.corpus import Corpus, LANGS, Ln, Pg, load_voynich

warnings.filterwarnings('ignore', category=RuntimeWarning, message='.*encountered in matmul')
OUT = 'results/mechanism/e7'
ORDER = 3
PREC = 32
FULL = (1 << PREC) - 1
HALF = 1 << (PREC - 1)
QUART = 1 << (PREC - 2)


# ------------------------------------------------------------------ arithmetic coding (Witten, Neal, Cleary 1987)

class Decoder:
    """Reads a bitstream and turns it into symbol choices."""

    def __init__(self, bits):
        self.bits, self.pos = bits, 0
        self.low, self.high = 0, FULL
        self.code = 0
        for _ in range(PREC):
            self.code = (self.code << 1) | self._bit()

    def _bit(self):
        b = self.bits[self.pos] if self.pos < len(self.bits) else 0
        self.pos += 1
        return b

    def choose(self, syms, counts):
        total = sum(counts)
        rng = self.high - self.low + 1
        value = ((self.code - self.low + 1) * total - 1) // rng
        cum = 0
        for s, c in zip(syms, counts):
            if cum + c > value:
                lo, hi = cum, cum + c
                break
            cum += c
        self.high = self.low + rng * hi // total - 1
        self.low = self.low + rng * lo // total
        while True:
            if self.high < HALF:
                pass
            elif self.low >= HALF:
                self.low -= HALF
                self.high -= HALF
                self.code -= HALF
            elif self.low >= QUART and self.high < HALF + QUART:
                self.low -= QUART
                self.high -= QUART
                self.code -= QUART
            else:
                break
            self.low <<= 1
            self.high = (self.high << 1) | 1
            self.code = (self.code << 1) | self._bit()
        return s


class Encoder:
    """Receiver side: re-encodes the observed choices into bits."""

    def __init__(self):
        self.low, self.high, self.pending, self.out = 0, FULL, 0, []

    def _emit(self, b):
        self.out.append(b)
        self.out.extend([1 - b] * self.pending)
        self.pending = 0

    def observe(self, syms, counts, sym):
        total = sum(counts)
        cum = 0
        for s, c in zip(syms, counts):
            if s == sym:
                lo, hi = cum, cum + c
                break
            cum += c
        else:
            raise ValueError('symbol not in model')
        rng = self.high - self.low + 1
        self.high = self.low + rng * hi // total - 1
        self.low = self.low + rng * lo // total
        while True:
            if self.high < HALF:
                self._emit(0)
            elif self.low >= HALF:
                self._emit(1)
                self.low -= HALF
                self.high -= HALF
            elif self.low >= QUART and self.high < HALF + QUART:
                self.pending += 1
                self.low -= QUART
                self.high -= QUART
            else:
                break
            self.low <<= 1
            self.high = (self.high << 1) | 1


class PRNG:
    def __init__(self, seed):
        self.r = random.Random(seed)

    def choose(self, syms, counts):
        return self.r.choices(syms, counts)[0]


# ------------------------------------------------------------------ process (MK-sec line sampler with a chooser)

def fit(strings):
    m = defaultdict(Counter)
    for s in strings:
        t = '^' * ORDER + s + '$'
        for i in range(ORDER, len(t)):
            m[t[i - ORDER:i]][t[i]] += 1
    return {ctx: (sorted(c), [c[k] for k in sorted(c)]) for ctx, c in m.items()}


def options(m, ctx, s, target):
    """Deterministic modification of the model: suppress the end symbol below 60% of the target length."""
    c = m.get(ctx)
    if not c:
        return None
    syms, counts = c
    if len(s) < target * 0.6 and len(syms) > 1 and '$' in syms:
        i = syms.index('$')
        syms, counts = syms[:i] + syms[i + 1:], counts[:i] + counts[i + 1:]
    return syms, counts


def gen_line(m, target, chooser):
    s = ''
    while True:
        opt = options(m, ('^' * ORDER + s)[-ORDER:], s, target)
        if not opt:
            break
        x = chooser.choose(*opt)
        if x == '$':
            break
        s += x
        if len(s) >= target * 1.4:
            break
    return s


def replay_line(m, target, line, enc):
    """Receiver: same process, observing the generated line."""
    s = ''
    for ch in list(line) + ['$']:
        opt = options(m, ('^' * ORDER + s)[-ORDER:], s, target)
        if not opt:
            return
        if ch == '$' and len(s) >= target * 1.4:
            return             # stopped by the length rule, no choice made
        enc.observe(opt[0], opt[1], ch)
        if ch == '$':
            return
        s += ch


class Process:
    def __init__(self):
        self.V = load_voynich()
        gs = defaultdict(list)
        for p in self.V.pages:
            gs[(p.lang, p.section)].extend(' '.join(l.toks) for l in p.lines)
        self.glob = fit([s for v in gs.values() for s in v])
        self.models = {g: fit(v) for g, v in gs.items() if len(v) >= 30}

    def model(self, p):
        return self.models.get((p.lang, p.section), self.glob)

    def generate(self, chooser, name):
        pages, raw = [], []
        for p in self.V.pages:
            m = self.model(p)
            lines = []
            for l in p.lines:
                target = len(' '.join(l.toks))
                s = gen_line(m, target, chooser)
                raw.append((p.id, target, s))
                toks = [w for w in s.split(' ') if w] or ['o']
                lines.append(Ln(toks=toks, para_final=l.para_final, eligible=l.eligible))
            pages.append(Pg(id=p.id, lines=lines, hand=p.hand, quire=p.quire, section=p.section, lang=p.lang))
        return Corpus(name, pages, 'eva', 'G'), raw

    def recover(self, raw):
        enc = Encoder()
        pmap = {p.id: p for p in self.V.pages}
        for pid, target, s in raw:
            replay_line(self.model(pmap[pid]), target, s, enc)
        return enc.out


def bits_of(data):
    return [(b >> (7 - i)) & 1 for b in data for i in range(8)]


def plaintext_bits(name, compressed):
    txt = open(LANGS[name], encoding='utf-8', errors='replace').read()
    data = txt.encode('utf-8')
    return bits_of(lzma.compress(data, preset=9) if compressed else data)


# ------------------------------------------------------------------ run

def _job(cond):
    kind, key = cond
    P = Process()
    if kind == 'prng':
        c, raw = P.generate(PRNG(key), f'prng-{key}')
        rec = None
    else:
        bits = plaintext_bits(key, compressed=(kind == 'lzma'))
        dec = Decoder(bits)
        c, raw = P.generate(dec, f'{kind}-{key}')
        out = P.recover(raw)
        used = dec.pos - PREC
        n = min(len(out), used)
        mism = sum(1 for a, b in zip(out[:n], bits[:n]) if a != b)
        first_mism = next((i for i, (a, b) in enumerate(zip(out[:n], bits[:n])) if a != b), None)
        glyphs = sum(len(s.replace(' ', '')) for _, _, s in raw)
        toks = sum(len([w for w in s.split(' ') if w]) for _, _, s in raw)
        rec = {'bits_available': len(bits), 'bits_consumed': used, 'bits_recovered_compared': n,
               'mismatches': mism, 'first_mismatch': first_mism, 'bits_per_glyph': used / glyphs,
               'bits_per_token': used / toks, 'plaintext_bytes_carried': used / 8,
               'exhausted': used > len(bits)}
    ph = E2.phenotype(c, double_coded=False)
    return f'{kind}:{key}', ph, rec


def main(cmd):
    os.makedirs(OUT, exist_ok=True)
    if cmd == 'run':
        conds = [('prng', s) for s in (11, 12, 13)] + [('lzma', n) for n in ('LAT', 'ITA', 'GER')] + \
                [('raw', n) for n in ('LAT', 'ITA', 'GER')]
        res = {}
        with ProcessPoolExecutor(max_workers=8) as ex:
            for key, ph, rec in ex.map(_job, conds):
                res[key] = {'phenotype': ph, 'recovery': rec}
                print(key, rec, flush=True)
                json.dump(res, open(f'{OUT}/results.json', 'w'), indent=1)
    report()


def report():
    R = json.load(open(f'{OUT}/results.json'))
    A = [v['phenotype'] for k, v in R.items() if k.startswith('prng')]
    lines = []
    summary = {}
    for kind in ('lzma', 'raw'):
        B = [v['phenotype'] for k, v in R.items() if k.startswith(kind)]
        agree, rows = 0, {}
        for k in A[0]:
            a = [x[k] for x in A if x.get(k) is not None]
            b = [x[k] for x in B if x.get(k) is not None]
            if not a or not b:
                continue
            ma, mb = float(np.mean(a)), float(np.mean(b))
            if k == 'T4_peak':
                ok = abs(sum(a) - sum(b)) <= 1
            else:
                tol = 2 * math.sqrt(np.var(a, ddof=1) + np.var(b, ddof=1)) + 0.01 * abs(ma)
                ok = abs(ma - mb) <= tol
            agree += ok
            rows[k] = {'prng': ma, kind: mb, 'agree': bool(ok)}
        summary[kind] = {'agree': agree, 'n': len(rows), 'disagree': [k for k, r in rows.items() if not r['agree']], 'rows': rows}
        lines.append(f"{kind}: {agree}/{len(rows)} statistics agree with PRNG-driven output; disagree: {summary[kind]['disagree']}")
    summary['recovery'] = {k: v['recovery'] for k, v in R.items() if v['recovery']}
    json.dump(summary, open(f'{OUT}/report.json', 'w'), indent=1)
    print('\n'.join(lines))
    for k, v in summary['recovery'].items():
        print(k, {kk: (round(vv, 3) if isinstance(vv, float) else vv) for kk, vv in v.items()})


if __name__ == '__main__' and sys.argv[1] != 'tmcheck':
    main(sys.argv[1])


# ------------------------------------------------------------------ targeted follow-up (post hoc): token MI with 8 runs per condition

def _tm_job(cond):
    from voynich.battery import battery
    kind, key, off = cond
    P = Process()
    if kind == 'prng':
        c, _ = P.generate(PRNG(key), 'x')
    else:
        c, _ = P.generate(Decoder(plaintext_bits(key, compressed=True)[off:]), 'x')
    b = battery(E2.to_lists(c), 'x')
    return [kind, str(key), off], b['token_mi'], b['edge_mi']


def token_mi_check():
    from scipy.stats import mannwhitneyu, ttest_ind
    conds = [('prng', s, 0) for s in range(20, 28)] + \
            [('lzma', n, o) for n in ('LAT', 'ITA', 'GER') for o in (0, 200000, 400000)][:8]
    with ProcessPoolExecutor(max_workers=8) as ex:
        res = list(ex.map(_tm_job, conds))
    a = [t for c, t, e in res if c[0] == 'prng']
    b = [t for c, t, e in res if c[0] == 'lzma']
    out = {'runs': res, 'prng_mean': float(np.mean(a)), 'prng_sd': float(np.std(a, ddof=1)),
           'lzma_mean': float(np.mean(b)), 'lzma_sd': float(np.std(b, ddof=1)),
           'welch_p': float(ttest_ind(a, b, equal_var=False).pvalue), 'mwu_p': float(mannwhitneyu(a, b).pvalue)}
    json.dump(out, open(f'{OUT}/token_mi_check.json', 'w'), indent=1)
    print({k: (round(v, 4) if isinstance(v, float) else '') for k, v in out.items() if k != 'runs'})
    for r in res:
        print(r[0], round(r[1], 4), round(r[2], 4))


if __name__ == '__main__' and len(sys.argv) > 1 and sys.argv[1] == 'tmcheck':
    token_mi_check()
