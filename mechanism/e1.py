"""E1: boundary-conditioned recency (mechanism/E1_PREREG.md).

    python3 -m mechanism.e1 tune      # tune controls to the published T6a values
    python3 -m mechanism.e1 A         # controls, 5 seeds each -> results/mechanism/e1_stageA.json
    python3 -m mechanism.e1 B         # Voynich -> results/mechanism/e1_stageB.json
"""
import json
import math
import random
import sys
import warnings
from collections import Counter, defaultdict

import numpy as np

from mechanism import tests as T
from mechanism.corpus import Corpus, Ln, Pg, eva_units, load_voynich

warnings.filterwarnings('ignore', category=RuntimeWarning, message='.*encountered in matmul')
OUT = 'results/mechanism'


# ------------------------------------------------------------------ statistics

def _structure(p):
    """Per token of a page: (token, line index, paragraph index, eligible)."""
    rows = []
    para, first_line_of_para = 0, True
    for li, l in enumerate(p.lines):
        n = len(l.toks)
        for k, t in enumerate(l.toks):
            elig = (0 < k < n - 1) and not first_line_of_para
            rows.append((t, li, para, elig))
        first_line_of_para = False
        if l.para_final:
            para += 1
            first_line_of_para = True
    return rows


def _graded(a, b, cache={}):
    key = (a, b) if a < b else (b, a)
    v = cache.get(key)
    if v is None:
        ua, ub = eva_units(a), eva_units(b)
        # Levenshtein on units
        prev = list(range(len(ub) + 1))
        for i, x in enumerate(ua, 1):
            cur = [i]
            for j, y in enumerate(ub, 1):
                cur.append(min(prev[j] + 1, cur[j - 1] + 1, prev[j - 1] + (x != y)))
            prev = cur
        v = 1 - prev[-1] / max(len(ua), len(ub))
        cache[key] = v
    return v


def _pclass(k, n, parafinal):
    return (min(k, 2), min(n - 1 - k, 2), bool(parafinal))


def e1_stats(c, seed=0, reps=500, dmax=40, graded=True):
    """E1 statistics with position-stratified expectations (E1_DEVIATIONS.md, entry 2)."""
    types = sorted({t for p in c.pages for l in p.lines for t in l.toks})
    tid = {t: i for i, t in enumerate(types)}
    near = T.ed1_pairs(types, c.units)
    near_of = defaultdict(set)
    for a, b in near:
        near_of[a].add(b)
    CL = ('same_line', 'cross_line', 'same_para', 'cross_para')
    P = len(c.pages)
    S = {k: np.zeros((P, dmax + 1)) for k in CL}
    E = {k: np.zeros((P, dmax + 1)) for k in CL}
    G = {k: np.zeros((P, 8)) for k in ('same_line', 'cross_line')}
    GE = {k: np.zeros((P, 8)) for k in ('same_line', 'cross_line')}
    rng = random.Random(seed)
    for pi, p in enumerate(c.pages):
        rows = []   # (token, line, para, eligible, class)
        para, first = 0, True
        for li, l in enumerate(p.lines):
            n = len(l.toks)
            for k, t in enumerate(l.toks):
                el = (0 < k < n - 1) and not first
                rows.append((t, li, para, el, _pclass(k, n, l.para_final) if el else None))
            first = False
            if l.para_final:
                para += 1
                first = True
        elig = [r for r in rows if r[3]]
        if len(elig) < 10:
            continue
        byc = defaultdict(Counter)
        for r in elig:
            byc[r[4]][tid[r[0]]] += 1
        ncls = {x: sum(v.values()) for x, v in byc.items()}
        exp_bin = {}
        for x, cx in byc.items():
            for y, cy in byc.items():
                den = ncls[x] * ncls[y] - (ncls[x] if x == y else 0)
                if den <= 0:
                    continue
                num = sum(v * cy.get(t, 0) for t, v in cx.items()) - (ncls[x] if x == y else 0)
                num += sum(v * sum(cy.get(b, 0) for b in near_of.get(t, ())) for t, v in cx.items())
                exp_bin[x, y] = num / den
        if graded:
            toks_by = defaultdict(list)
            for r in elig:
                toks_by[r[4]].append(r[0])
            allt = [r[0] for r in elig]
            pg_all = float(np.mean([_graded(*rng.sample(allt, 2)) for _ in range(200)]))
            exp_gr = {}

        for i, r in enumerate(rows):
            if not r[3]:
                continue
            for d in range(2, dmax + 1):
                j = i + d
                if j >= len(rows) or not rows[j][3]:
                    continue
                q = rows[j]
                pe = exp_bin.get((r[4], q[4]))
                if pe is None:
                    continue
                if r[1] == q[1]:
                    cls = ['same_line']
                elif r[2] == q[2]:
                    cls = ['same_para'] + (['cross_line'] if q[1] == r[1] + 1 else [])
                else:
                    cls = ['cross_para']
                a, b = tid[r[0]], tid[q[0]]
                s = 1.0 if (a == b or b in near_of.get(a, ())) else 0.0
                for k in cls:
                    S[k][pi, d] += s
                    E[k][pi, d] += pe
                if graded and d <= 7 and ('same_line' in cls or 'cross_line' in cls):
                    key = (r[4], q[4])
                    if key not in exp_gr:
                        A, B = toks_by[r[4]], toks_by[q[4]]
                        smp = [_graded(rng.choice(A), rng.choice(B)) for _ in range(25)]
                        exp_gr[key] = float(np.mean(smp)) if smp else pg_all
                    k2 = 'same_line' if 'same_line' in cls else 'cross_line'
                    G[k2][pi, d] += _graded(r[0], q[0])
                    GE[k2][pi, d] += exp_gr[key]

    def compute(idx):
        R = {k: S[k][idx].sum(0) / np.maximum(E[k][idx].sum(0), 1e-12) for k in CL}
        N = {k: E[k][idx].sum(0) for k in CL}
        wld = R['same_line'][[2, 3]].mean() - R['same_line'][[5, 6, 7]].mean()

        def step(a, b, ds):
            w = np.array([min(N[a][d], N[b][d]) for d in ds])
            diff = np.array([R[b][d] - R[a][d] for d in ds])
            ok = w > 0
            return float((w[ok] * diff[ok]).sum() / w[ok].sum()) if ok.any() else float('nan')
        ls = step('same_line', 'cross_line', range(2, 8))
        ps = step('same_para', 'cross_para', range(8, dmax + 1))
        wpd = R['same_para'][8:16].mean() - R['same_para'][25:41].mean()
        out = {'WLD': float(wld), 'LS': ls, 'PS': ps, 'WPD': float(wpd)}
        if graded:
            gr = {k: G[k][idx].sum(0) / np.maximum(GE[k][idx].sum(0), 1e-12) for k in G}
            gn = {k: GE[k][idx].sum(0) for k in G}
            out['WLD_graded'] = float(gr['same_line'][[2, 3]].mean() - gr['same_line'][[5, 6, 7]].mean())
            w = np.array([min(gn['same_line'][d], gn['cross_line'][d]) for d in range(2, 8)])
            diff = np.array([gr['cross_line'][d] - gr['same_line'][d] for d in range(2, 8)])
            out['LS_graded'] = float((w * diff).sum() / w.sum()) if w.sum() else float('nan')
        return out, R, N

    full, R, N = compute(np.arange(P))
    g = np.random.default_rng(seed)
    boots = [compute(g.integers(0, P, P))[0] for _ in range(reps)]
    ci = {k: [float(np.nanpercentile([b[k] for b in boots], 2.5)), float(np.nanpercentile([b[k] for b in boots], 97.5))]
          for k in full}
    profiles = {k: {'ratio': [float(x) for x in R[k][2:]], 'pairs_expect': [float(x) for x in N[k][2:]]} for k in R}
    return {'stats': full, 'ci95': ci, 'profiles': profiles}


# ------------------------------------------------------------------ controls

def _base():
    V = load_voynich()
    groups = defaultdict(Counter)
    for p in V.pages:
        for l in p.lines:
            groups[(p.lang, p.section)].update(l.toks)
    glob = Counter()
    for c in groups.values():
        glob.update(c)
    return V, groups, glob


def _copy_structure(V, name, fill):
    """New corpus with V's pages/lines/paragraph flags; fill(page, line_index, n_tokens, state) -> tokens."""
    pages = []
    for p in V.pages:
        state = {}
        lines = []
        for li, l in enumerate(p.lines):
            lines.append(Ln(toks=fill(p, li, len(l.toks), state), para_final=l.para_final, eligible=l.eligible))
        pages.append(Pg(id=p.id, lines=lines, hand=p.hand, quire=p.quire, section=p.section, lang=p.lang))
    return Corpus(name, pages, 'eva', 'P')


class Sampler:
    def __init__(self, counter):
        self.toks = list(counter)
        self.w = np.array([counter[t] for t in self.toks], float)
        self.init = [eva_units(t)[0] for t in self.toks]
        self.fin = [eva_units(t)[-1] for t in self.toks]
        self.cum = np.cumsum(self.w)

    def draw(self, rng, cum=None):
        cum = self.cum if cum is None else cum
        return self.toks[int(np.searchsorted(cum, rng.random() * cum[-1], side='right'))]

    def tilted(self, rng, sigma):
        ui = {u: math.exp(sigma * rng.gauss(0, 1)) for u in set(self.init)}
        uf = {u: math.exp(sigma * rng.gauss(0, 1)) for u in set(self.fin)}
        w = self.w * np.array([ui[a] * uf[b] for a, b in zip(self.init, self.fin)])
        return np.cumsum(w)


def set_control(level, sigma, seed=0):
    V, groups, glob = _base()
    samplers = {g: Sampler(c) for g, c in groups.items()}
    rng = random.Random(seed)
    nrng = np.random.default_rng(seed)

    def fill(p, li, n, state):
        smp = samplers[(p.lang, p.section)]
        if level == 'line' or 'cum' not in state:
            state['cum'] = smp.tilted(rng, sigma)
        out = [smp.draw(nrng, state['cum']) for _ in range(n)]
        if level == 'para' and p.lines[li].para_final:
            state.pop('cum')
        return out
    return _copy_structure(V, f'SET-{level}', fill)


def rec_control(rho, tau, e, seed=0):
    V, groups, glob = _base()
    samplers = {g: Sampler(c) for g, c in groups.items()}
    types = list(glob)
    near = T.ed1_pairs(types, eva_units)
    nb = defaultdict(list)
    for a, b in near:
        nb[types[a]].append(types[b])
    rng = random.Random(seed)
    nrng = np.random.default_rng(seed)

    def fill(p, li, n, state):
        smp = samplers[(p.lang, p.section)]
        hist = state.setdefault('hist', [])
        out = []
        for _ in range(n):
            if hist and rng.random() < rho:
                k = len(hist)
                w = [math.exp(-(k - 1 - i) / tau) for i in range(k)]
                src = rng.choices(hist, w)[0]
                if rng.random() < e or not nb.get(src):
                    t = src
                else:
                    cand = nb[src]
                    t = rng.choices(cand, [glob[x] for x in cand])[0]
            else:
                t = smp.draw(nrng)
            out.append(t)
            hist.append(t)
        return out
    return _copy_structure(V, 'REC', fill)


def mk_control(seed=0, order=3):
    from voynich import generators as G
    V, groups, glob = _base()
    strs = defaultdict(list)
    for p in V.pages:
        for l in p.lines:
            strs[(p.lang, p.section)].append(' '.join(l.toks))
    allm = G.fit([s for v in strs.values() for s in v], order)
    models = {g: G.fit(v, order) for g, v in strs.items() if len(v) >= 30}
    rng = random.Random(seed)

    def fill(p, li, n, state):
        m = models.get((p.lang, p.section), allm)
        target = len(' '.join(p.lines[li].toks))
        for _ in range(20):
            toks = G.sample_line(m, order, target, rng)
            if toks:
                return toks
        return p.lines[li].toks[:1]
    return _copy_structure(V, 'MK-sec', fill)


# ------------------------------------------------------------------ stages

TARGET = {'DI_near': 0.153, 'DI_exact': 0.217}


def tune():
    res = {}
    for s in (0.5, 1.0, 1.5, 2.0, 3.0):
        for lvl in ('line', 'para'):
            r = T.t6a(set_control(lvl, s), reps=50)
            res[f'SET-{lvl}-{s}'] = (r['DI_near'], r['DI_exact'])
            print(lvl, s, round(r['DI_near'], 3), round(r['DI_exact'], 3), flush=True)
    for rho in (0.1, 0.2, 0.3):
        for tau in (3.0, 8.0):
            for e in (0.3, 0.6):
                r = T.t6a(rec_control(rho, tau, e), reps=50)
                res[f'REC-{rho}-{tau}-{e}'] = (r['DI_near'], r['DI_exact'])
                print('rec', rho, tau, e, round(r['DI_near'], 3), round(r['DI_exact'], 3), flush=True)
    json.dump(res, open(f'{OUT}/e1_tuning.json', 'w'), indent=1)


def stage(which, params=None):
    if which == 'A':
        pr = json.load(open(f'{OUT}/e1_params.json'))
        out = {}
        for seed in range(5):
            for name, c in (('SET-line', lambda s: set_control('line', pr['SET-line'], s)),
                            ('SET-para', lambda s: set_control('para', pr['SET-para'], s)),
                            ('REC', lambda s: rec_control(*pr['REC'], seed=s)),
                            ('MK-sec', lambda s: mk_control(s))):
                corp = c(seed)
                r = e1_stats(corp, seed=seed)
                r['t6a'] = {k: v for k, v in T.t6a(corp, reps=100).items() if k.startswith('DI')}
                out[f'{name}-{seed}'] = r
                print(name, seed, {k: round(v, 3) for k, v in r['stats'].items()},
                      {k: [round(x, 3) for x in v] for k, v in r['ci95'].items() if k in ('LS', 'PS', 'LS_graded', 'WPD')}, flush=True)
        json.dump(out, open(f'{OUT}/e1_stageA.json', 'w'), indent=1)
    else:
        r = e1_stats(load_voynich())
        json.dump({'VOYNICH': r}, open(f'{OUT}/e1_stageB.json', 'w'), indent=1)
        print({k: round(v, 4) for k, v in r['stats'].items()}, {k: [round(x, 4) for x in v] for k, v in r['ci95'].items()})


if __name__ == '__main__':
    if sys.argv[1] == 'tune':
        tune()
    else:
        stage(sys.argv[1])
