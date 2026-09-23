"""E4: lexical vs sublexical within-page drift (mechanism/E4_PREREG.md).

    python3 -m mechanism.e4 A    # controls -> results/mechanism/e4_stageA.json
    python3 -m mechanism.e4 B    # Voynich  -> results/mechanism/e4_stageB.json
"""
import json
import math
import sys
import warnings
from collections import Counter, defaultdict
from concurrent.futures import ProcessPoolExecutor
from functools import lru_cache

import numpy as np

from mechanism.corpus import Corpus, Ln, Pg, load_voynich

warnings.filterwarnings('ignore', category=RuntimeWarning, message='.*encountered in matmul')
OUT = 'results/mechanism'
KS = list(range(2, 9))


def _ed_le2(a, b):
    """Unit edit distance <= 2 (banded Levenshtein)."""
    if abs(len(a) - len(b)) > 2:
        return False
    prev = list(range(len(b) + 1))
    for i, x in enumerate(a, 1):
        cur = [i] + [0] * len(b)
        lo = 10 ** 9
        for j, y in enumerate(b, 1):
            cur[j] = min(prev[j] + 1, cur[j - 1] + 1, prev[j - 1] + (x != y))
            lo = min(lo, cur[j])
        if lo > 2 and min(cur) > 2:
            return False
        prev = cur
    return prev[-1] <= 2


def _cos(a, b):
    num = sum(v * b.get(k, 0) for k, v in a.items())
    den = math.sqrt(sum(v * v for v in a.values()) * sum(v * v for v in b.values()))
    return num / den if den else 0.0


def stats(c, reps=500, seed=0, min_lines=6):
    U = c.units

    @lru_cache(maxsize=None)
    def near(a, b):
        return a == b or _ed_le2(U(a), U(b))

    @lru_cache(maxsize=None)
    def bigr(t):
        u = ('^',) + U(t) + ('$',)
        return tuple(zip(u, u[1:]))

    rows = []   # per page: arrays over k of (sum_lex, sum_sub, n_lex, n_sub) and page means
    for p in c.pages:
        L = [l.toks for l in p.lines if l.toks]
        n = len(L)
        if n < min_lines:
            continue
        types = [Counter(l) for l in L]
        tset = [set(l) for l in L]
        lex_all, sub_all = [], []
        sl = np.zeros(len(KS))
        ss = np.zeros(len(KS))
        nl = np.zeros(len(KS))
        ns = np.zeros(len(KS))
        for i in range(n):
            for j in range(i + 2, n):
                k = j - i
                lx = _cos(types[i], types[j])
                lex_all.append(lx)
                keep_i = [t for t in L[i] if not any(near(t, u) for u in tset[j])]
                keep_j = [t for t in L[j] if not any(near(t, u) for u in tset[i])]
                sb = None
                if len(keep_i) >= 2 and len(keep_j) >= 2:
                    vi, vj = Counter(), Counter()
                    for t in keep_i:
                        vi.update(bigr(t))
                    for t in keep_j:
                        vj.update(bigr(t))
                    sb = _cos(vi, vj)
                    sub_all.append(sb)
                if k in KS:
                    idx = KS.index(k)
                    sl[idx] += lx
                    nl[idx] += 1
                    if sb is not None:
                        ss[idx] += sb
                        ns[idx] += 1
        if not lex_all or not sub_all:
            continue
        rows.append((sl, nl, np.mean(lex_all), ss, ns, np.mean(sub_all)))

    def compute(idx):
        SL = sum(rows[i][0] for i in idx)
        EL = sum(rows[i][1] * rows[i][2] for i in idx)
        SS = sum(rows[i][3] for i in idx)
        ES = sum(rows[i][4] * rows[i][5] for i in idx)
        rl, rs = SL / np.maximum(EL, 1e-12), SS / np.maximum(ES, 1e-12)
        x = np.array(KS, float)
        return float(np.polyfit(x, rl, 1)[0]), float(np.polyfit(x, rs, 1)[0]), rl, rs

    P = len(rows)
    L_, S_, rl, rs = compute(list(range(P)))
    g = np.random.default_rng(seed)
    bl, bs = [], []
    for _ in range(reps):
        b = g.integers(0, P, P)
        l, s_, _, _ = compute(b)
        bl.append(l)
        bs.append(s_)
    return {'L': L_, 'L_ci95': [float(np.percentile(bl, 2.5)), float(np.percentile(bl, 97.5))],
            'S': S_, 'S_ci95': [float(np.percentile(bs, 2.5)), float(np.percentile(bs, 97.5))],
            'lex_ratio': [float(x) for x in rl], 'sub_ratio': [float(x) for x in rs], 'pages': P}


# ------------------------------------------------------------------ controls

def ldrift(step=0.3, seed=0):
    V = load_voynich()
    rng = np.random.default_rng(seed)
    groups = defaultdict(Counter)
    for p in V.pages:
        for l in p.lines:
            groups[(p.lang, p.section)].update(l.toks)
    base = {g: (list(c), np.array([c[t] for t in c], float)) for g, c in groups.items()}
    pages = []
    for p in V.pages:
        toks, w0 = base[(p.lang, p.section)]
        z = np.zeros(len(toks))
        lines = []
        for li, l in enumerate(p.lines):
            if li > 0:
                z += step * rng.standard_normal(len(toks))
            w = w0 * np.exp(z)
            cum = np.cumsum(w)
            pick = np.searchsorted(cum, rng.random(len(l.toks)) * cum[-1], side='right')
            lines.append(Ln(toks=[toks[i] for i in pick], para_final=l.para_final))
        pages.append(Pg(id=p.id, lines=lines, hand=p.hand, quire=p.quire, section=p.section, lang=p.lang))
    return Corpus('LDRIFT', pages, 'eva', 'P')


def gdrift(sigw=0.3, seed=0):
    from mechanism import e3
    V = load_voynich()
    fits = json.load(open('results/mechanism/e3/fits.json'))
    prm = dict(fits['primary:HGR2']['params'], sigw=sigw)
    g = e3.HGR2(V, m=prm['m'], c1=True)
    c = g.generate(V, prm, seed=seed, name='GDRIFT')
    c.gclass = 'P'
    return c


def build(name):
    from mechanism import controls as K
    from mechanism import corpus as C
    if name in C.LANGS:
        return C.load_lang_chunked(name)
    if name == 'VB-run':
        from voynich import generators as G
        return C.with_vmeta('VB-run', list(G.pages.keys()), G.verbose_pages(seed=0, independent_lines=False), 'eva', 'C')
    if name == 'NAIB-run':
        return K.naib(False)
    if name == 'MK-sec':
        return K.mk_sec()
    if name == 'LDRIFT':
        return ldrift()
    if name == 'GDRIFT':
        return gdrift()
    if name == 'VOYNICH':
        return load_voynich()
    raise ValueError(name)


def job(name):
    warnings.filterwarnings('ignore', category=RuntimeWarning, message='.*encountered in matmul')
    return name, stats(build(name))


def main(stage):
    names = ['LAT', 'ITA', 'GER', 'ENG', 'VB-run', 'NAIB-run', 'GDRIFT', 'LDRIFT', 'MK-sec'] if stage == 'A' else ['VOYNICH']
    res = {}
    with ProcessPoolExecutor(max_workers=8) as ex:
        for n, r in ex.map(job, names):
            res[n] = r
            print(f"{n:9s} L={r['L']:+.4f} {[round(x, 4) for x in r['L_ci95']]}  S={r['S']:+.4f} {[round(x, 4) for x in r['S_ci95']]}  pages={r['pages']}", flush=True)
    json.dump(res, open(f'{OUT}/e4_stage{stage}.json', 'w'), indent=1)


if __name__ == '__main__':
    main(sys.argv[1])
