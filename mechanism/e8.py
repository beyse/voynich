"""R4b / E8 (mechanism/REVISION_PLAN.md): a message carried through the E3 generator (HGR2).

Only choices the receiver can observe carry message bits: each glyph of a token sampled from the grammar
(including the token-ending space), the choice of the reused recent form (source and neighbour steps combined
into one categorical over output strings), and the choice among the final-word candidates (identical
candidates merged). Everything else comes from a key PRNG shared by sender and receiver: route
(recency or grammar), exact or near reuse, page tilt and line random walk, final-word candidate generation,
and, for slipped tokens, the intended token and the slip. All choice probabilities are quantised to integer
counts (resolution 2^-16, minimum 1), identically in every condition, so the baseline and the
message-driven runs sample from the same quantised process.

    python3 -m mechanism.e8 check     # one short round trip: generate with a message, recover it
    python3 -m mechanism.e8 run       # 20 baseline and 20 message-driven runs + phenotype
    python3 -m mechanism.e8 report
"""
import json
import math
import random
import sys
import warnings

from mechanism import e2 as E2
from mechanism import e3 as E3
from mechanism import e7 as E7
from mechanism import e7b as E7B
from mechanism.corpus import Corpus, Ln, Pg, load_voynich

warnings.filterwarnings('ignore', category=RuntimeWarning)
OUT = 'results/mechanism/e8'
Q = 1 << 16


def quant(items, weights):
    agg = {}
    for it, w in zip(items, weights):
        if w > 0:
            agg[it] = agg.get(it, 0.0) + w
    syms = sorted(agg)
    tot = sum(agg.values())
    return syms, [max(1, int(round(agg[s] / tot * Q))) for s in syms]


class MsgChooser:
    def __init__(self, dec):
        self.dec = dec

    def choose(self, syms, counts, obs=None):
        return self.dec.choose(syms, counts)


class RandChooser:
    def __init__(self, rng):
        self.rng = rng

    def choose(self, syms, counts, obs=None):
        return self.rng.choices(syms, counts)[0]


class Observer:
    """Receiver: returns the observed symbol and re-encodes it."""

    def __init__(self, enc):
        self.enc = enc

    def choose(self, syms, counts, obs):
        self.enc.observe(syms, counts, obs)
        return obs


class MimicHGR2(E3.HGR2):
    def m_sample_token(self, prefix, gm, qm, prm, lt, key, ch, obs=None, maxlen=15):
        tok = ''
        while True:
            if len(tok) >= maxlen:          # the original draws and discards a symbol here; skipping the draw
                return tok                  # leaves the output distribution unchanged and keeps it decodable
            ctx = (('^' * E3.ORDER) + prefix + tok)[-E3.ORDER:]
            d = self.dist(ctx, gm, qm, prm, lt, {' '} if tok else set())
            if not d:
                return tok or key.choice(self._typelist)
            syms, counts = quant(list(d), [d[k] for k in d])
            o = None if obs is None else (obs[len(tok)] if len(tok) < len(obs) else ' ')
            c = ch.choose(syms, counts, o)
            if c == ' ':
                return tok
            tok += c

    def m_recent(self, hist, prm, key, ch, obs):
        k = len(hist)
        near = key.random() >= prm['e']
        agg = {}
        for i, src in enumerate(hist):
            w = math.exp(-(k - 1 - i) / prm['tau'])
            cand = self.nb.get(src) if near else None
            if cand:
                tw = [self.types[x] for x in cand]
                z = sum(tw)
                for x, t in zip(cand, tw):
                    agg[x] = agg.get(x, 0.0) + w * t / z
            else:
                agg[src] = agg.get(src, 0.0) + w
        syms, counts = quant(list(agg), list(agg.values()))
        return ch.choose(syms, counts, obs)

    def m_line(self, target, end, gm, qm, prm, lt, hist, key, ch, obs_toks):
        s, toks = '', []
        kc = RandChooser(key)
        while True:
            remaining = target - len(s) - (1 if s else 0)
            final = remaining <= 5 or len(toks) >= 30
            prefix = s + (' ' if s else '')
            slip = bool(prm['eps']) and key.random() < prm['eps']
            use = kc if slip else ch
            o = None if (obs_toks is None or slip) else obs_toks[len(toks)]
            if final:
                cands = [self.m_sample_token(prefix, gm, qm, prm, lt, key, kc) for _ in range(20)]
                w = [self.p_end(prefix + c, end, gm, qm, prm, lt) for c in cands]
                if sum(w) > 0:
                    syms, counts = quant(cands, w)
                    tok = use.choose(syms, counts, o)
                else:
                    tok = key.choice(cands)
            elif hist and key.random() < prm['rho']:
                tok = self.m_recent(hist, prm, key, use, o)
            else:
                tok = self.m_sample_token(prefix, gm, qm, prm, lt, key, use, o)
            out = self.slip(tok, key) if slip else tok
            if obs_toks is not None and out != obs_toks[len(toks)]:
                raise RuntimeError(f'receiver out of sync: {out!r} vs {obs_toks[len(toks)]!r}')
            toks.append(out)
            hist.append(tok)
            if final:
                return toks
            s = (s + ' ' if s else '') + out

    def m_generate(self, layout, prm, key_seed, ch, observed=None, name='E8'):
        self._typelist = sorted(self.types)
        key = random.Random(key_seed)
        pages, n = [], 0
        for p in layout.pages:
            gm, qm = self.model_for(p), self.quire.get(p.quire)
            lt = {c: (prm['sig'] * key.gauss(0, 1) if prm['sig'] > 0 else 0.0) for c in self.glyphs}
            hist, lines = [], []
            for li, l in enumerate(p.lines):
                if li > 0 and prm['sigw'] > 0:
                    for c in lt:
                        lt[c] += prm['sigw'] * key.gauss(0, 1)
                target = len(' '.join(l.toks))
                end = '%' if l.para_final else '$'
                obs = observed[n] if observed is not None else None
                toks = self.m_line(target, end, gm, qm, prm, lt, hist, key, ch, obs)
                n += 1
                lines.append(Ln(toks=toks, para_final=l.para_final, eligible=l.eligible))
            pages.append(Pg(id=p.id, lines=lines, hand=p.hand, quire=p.quire, section=p.section, lang=p.lang))
        return Corpus(name, pages, 'eva', 'G')


_G = {}


def setup():
    if not _G:
        V = load_voynich()
        prm = json.load(open('results/mechanism/e3/fits.json'))['primary:HGR2']['params']
        _G.update(V=V, prm=prm, g=MimicHGR2(V, m=prm['m'], c1=True))
    return _G['V'], _G['prm'], _G['g']


def send_and_recover(bits, key_seed, layout=None):
    V, prm, g = setup()
    layout = layout or V
    dec = E7.Decoder(bits)
    c = g.m_generate(layout, prm, key_seed, MsgChooser(dec), name='E8-msg')
    enc = E7.Encoder()
    g.m_generate(layout, prm, key_seed, Observer(enc), observed=[l.toks for p in c.pages for l in p.lines])
    used = dec.pos - E7.PREC
    n = min(len(enc.out), used)
    mism = sum(1 for a, b in zip(enc.out[:n], bits[:n]) if a != b)
    glyphs = sum(len(t) for p in c.pages for l in p.lines for t in l.toks)
    toks = sum(len(l.toks) for p in c.pages for l in p.lines)
    return c, {'bits_available': len(bits), 'bits_consumed': used, 'bits_recovered_compared': n, 'mismatches': mism,
               'glyphs': glyphs, 'tokens': toks, 'bits_per_glyph': used / glyphs, 'bits_per_token': used / toks,
               'exhausted': used > len(bits)}


def conditions():
    base = [('prng', 201 + i, 0, 301 + i) for i in range(20)]
    msg = [('lzma', lang, off, 301 + i) for i, (lang, off) in
           enumerate((lang, off) for lang, offs in E7B.OFFSETS.items() for off in offs)]
    return base + msg


def _job(cond):
    kind, a, off, key_seed = cond
    V, prm, g = setup()
    if kind == 'prng':
        c = g.m_generate(V, prm, key_seed, RandChooser(random.Random(a)), name=f'E8-base-{a}')
        rec = None
    else:
        c, rec = send_and_recover(E7B.pbits(a, True, off), key_seed)
    return f'{kind}:{a}:{off}', E2.phenotype(c, double_coded=False), rec


def check():
    """Round trip on the first 12 pages; must return 0 mismatches."""
    V, prm, g = setup()
    small = Corpus('V12', V.pages[:12], 'eva', 'V')
    c, rec = send_and_recover(E7B.pbits('LAT', True, 0), 301, layout=small)
    print(rec)
    assert rec['mismatches'] == 0 and not rec['exhausted']


if __name__ == '__main__':
    cmd = sys.argv[1]
    if cmd == 'check':
        check()
    else:
        if cmd == 'run':
            E7B.run(conditions(), _job, f'{OUT}/results.json')
        E7B.report(f'{OUT}/results.json', f'{OUT}/report.json')
