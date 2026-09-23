"""E5: frequency-resolved burstiness (mechanism/E5_PREREG.md).

    python3 -m mechanism.e5 A    # controls -> results/mechanism/e5_stageA.json
    python3 -m mechanism.e5 B    # Voynich  -> results/mechanism/e5_stageB.json
"""
import json
import math
import random
import sys
import warnings
from collections import Counter, defaultdict
from concurrent.futures import ProcessPoolExecutor

import numpy as np

from mechanism.corpus import Corpus, Ln, Pg, load_voynich

warnings.filterwarnings('ignore', category=RuntimeWarning, message='.*encountered in matmul')
OUT = 'results/mechanism'
BANDS = {'R': (2, 4), 'M': (5, 19), 'F': (20, 99), 'VF': (100, 10 ** 9)}


def band_of(n):
    for b, (lo, hi) in BANDS.items():
        if lo <= n <= hi:
            return b
    return None


def stats(c, reps=500, seed=0):
    total = Counter(t for p in c.pages for l in p.lines for t in l.toks)
    band = {t: band_of(n) for t, n in total.items()}
    # per page: group, size, type counts
    pages = []
    for p in c.pages:
        cnt = Counter(t for l in p.lines for t in l.toks)
        pages.append(((p.hand, p.section), sum(cnt.values()), cnt))

    def compute(idx):
        by_g = defaultdict(list)
        for i in idx:
            by_g[pages[i][0]].append(i)
        O = Counter()
        E = Counter()
        for g, ids in by_g.items():
            Ng = sum(pages[i][1] for i in ids)
            if Ng < 2:
                continue
            frac = sum(pages[i][1] * (pages[i][1] - 1) for i in ids) / (Ng * (Ng - 1))
            ntg = Counter()
            for i in ids:
                for t, k in pages[i][2].items():
                    ntg[t] += k
                    b = band[t]
                    if b:
                        O[b] += k * (k - 1) / 2
            for t, n in ntg.items():
                b = band[t]
                if b:
                    E[b] += n * (n - 1) / 2 * frac
        B = {b: (O[b] / E[b] if E[b] else float('nan')) for b in BANDS}
        G = math.log(B['R']) - math.log(B['F']) if B['R'] > 0 and B['F'] > 0 else float('nan')
        return B, G

    P = len(pages)
    B, G = compute(list(range(P)))
    # leave-one-quire-out jackknife (E5_DEVIATIONS.md, entry 1)
    quires = sorted({str(p.quire) for p in c.pages})
    qof = [str(p.quire) for p in c.pages]
    jk = [compute([i for i in range(P) if qof[i] != q]) for q in quires]
    n = len(jk)

    def ci(full, xs):
        xs = [x for x in xs if x == x]
        m = float(np.mean(xs))
        se = math.sqrt((n - 1) / n * sum((x - m) ** 2 for x in xs))
        return [full - 1.96 * se, full + 1.96 * se]
    return {'B': B, 'B_ci95': {b: ci(B[b], [x[0][b] for x in jk]) for b in BANDS}, 'G': G,
            'G_ci95': ci(G, [x[1] for x in jk]), 'quires': n,
            'types_per_band': dict(Counter(band[t] for t in total if band[t]))}


# ------------------------------------------------------------------ REP control

def _tok_model(tokens, order=3):
    m = defaultdict(Counter)
    for t in tokens:
        s = '^' * order + t + '$'
        for i in range(order, len(s)):
            m[s[i - order:i]][s[i]] += 1
    return m


def _sample_tok(m, rng, order=3, maxlen=15):
    s = '^' * order
    out = ''
    while len(out) < maxlen:
        c = m.get(s[-order:])
        if not c:
            break
        ks = list(c)
        x = rng.choices(ks, [c[k] for k in ks])[0]
        if x == '$':
            break
        out += x
        s += x
    return out


def rep(step=0.3, K=300, seed=0):
    V = load_voynich()
    rng = random.Random(seed)
    nrng = np.random.default_rng(seed)
    groups = defaultdict(Counter)
    for p in V.pages:
        for l in p.lines:
            groups[(p.lang, p.section)].update(l.toks)
    top = {g: [t for t, _ in c.most_common(K)] for g, c in groups.items()}
    inside = sum(sum(c[t] for t in top[g]) for g, c in groups.items())
    coin = 1 - inside / sum(sum(c.values()) for c in groups.values())
    models = {g: _tok_model(list(c.elements())) for g, c in groups.items()}
    pages = []
    for p in V.pages:
        g = (p.lang, p.section)
        toks = top[g]
        tset = set(toks)
        w0 = np.array([groups[g][t] for t in toks], float)
        z = np.zeros(len(toks))
        lines = []
        for li, l in enumerate(p.lines):
            if li > 0:
                z += step * nrng.standard_normal(len(toks))
            cum = np.cumsum(w0 * np.exp(z))
            out = []
            for _ in l.toks:
                if rng.random() < coin:
                    for _ in range(50):
                        t = _sample_tok(models[g], rng)
                        if t and t not in tset:
                            break
                    out.append(t or toks[0])
                else:
                    out.append(toks[int(np.searchsorted(cum, nrng.random() * cum[-1], side='right'))])
            lines.append(Ln(toks=out, para_final=l.para_final))
        pages.append(Pg(id=p.id, lines=lines, hand=p.hand, quire=p.quire, section=p.section, lang=p.lang))
    c = Corpus('REP', pages, 'eva', 'P')
    c.note = f'coinage rate {coin:.3f}'
    return c


def hgr2_full(seed=0):
    from mechanism import e3
    V = load_voynich()
    prm = json.load(open('results/mechanism/e3/fits.json'))['primary:HGR2']['params']
    return e3.HGR2(V, m=prm['m'], c1=True).generate(V, prm, seed=seed, name='HGR2')


def build(name):
    from mechanism import e4
    if name == 'REP':
        return rep()
    if name == 'HGR2':
        return hgr2_full()
    return e4.build(name)


def job(name):
    warnings.filterwarnings('ignore', category=RuntimeWarning, message='.*encountered in matmul')
    c = build(name)
    r = stats(c)
    r['note'] = getattr(c, 'note', '')
    return name, r


def main(stage):
    names = ['LAT', 'ITA', 'GER', 'ENG', 'VB-run', 'NAIB-run', 'LDRIFT', 'REP', 'HGR2', 'MK-sec'] if stage == 'A' else ['VOYNICH']
    res = {}
    with ProcessPoolExecutor(max_workers=8) as ex:
        for n, r in ex.map(job, names):
            res[n] = r
            print(f"{n:9s} G={r['G']:+.3f} {[round(x, 3) for x in r['G_ci95']]}  B=" +
                  ' '.join(f"{b}:{r['B'][b]:.2f}[{r['B_ci95'][b][0]:.2f},{r['B_ci95'][b][1]:.2f}]" for b in BANDS) +
                  f"  types={r['types_per_band']} {r['note']}", flush=True)
    json.dump(res, open(f'{OUT}/e5_stage{stage}.json', 'w'), indent=1)


if __name__ == '__main__':
    main(sys.argv[1])
