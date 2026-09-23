"""E6: two-route generator TR (drifting repertoire retrieval + one-off coinage), cross-fitted
(mechanism/E6_PREREG.md).

    python3 -m mechanism.e6 fit | generate | phenotype | report
"""
import json
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
from mechanism import e3 as E3
from mechanism import tests as T
from mechanism.corpus import Corpus, Ln, Pg, eva_units

warnings.filterwarnings('ignore', category=RuntimeWarning, message='.*encountered in matmul')
OUT = 'results/mechanism/e6'
ORDER = 3


def _tok_model(tokens, m):
    mdl = defaultdict(Counter)
    for t in tokens:
        s = '^' * ORDER + t + '$'
        for i in range(ORDER, len(s)):
            mdl[s[i - ORDER:i]][s[i]] += 1
    if m > 1:
        for ctx, c in list(mdl.items()):
            keep = Counter({k: v for k, v in c.items() if v >= m})
            if keep:
                mdl[ctx] = keep
    return mdl


def _ratio(cond, marg, units, a=0.5):
    nc, nm = sum(cond.values()), sum(marg.values())
    V = len(units)
    return np.array([((cond.get(u, 0) + a) / (nc + a * V)) / ((marg.get(u, 0) + a) / (nm + a * V)) for u in units])


class TR:
    def __init__(self, train, m=2, use_K=True):
        self.use_K = use_K
        toks_g, lines_g = defaultdict(list), defaultdict(int)
        first_all, last_int, first_line, first_para, last_margin, last_para = (Counter() for _ in range(6))
        pairs = Counter()
        glob_types = Counter()
        for p in train.pages:
            para_first = True
            keys = [('G', p.lang, p.section), ('L', p.lang), ('A',)]
            for l in p.lines:
                for k in keys:
                    toks_g[k].extend(l.toks)
                    lines_g[k] += 1
                glob_types.update(l.toks)
                U = [eva_units(t) for t in l.toks]
                for i, u in enumerate(U):
                    first_all[u[0]] += 1
                    if 0 < i < len(U) - 1:
                        last_int[u[-1]] += 1
                (first_para if para_first else first_line)[U[0][0]] += 1
                (last_para if l.para_final else last_margin)[U[-1][-1]] += 1
                for a, b in zip(U, U[1:]):
                    pairs[a[-1], b[0]] += 1
                para_first = bool(l.para_final)
        self.units = sorted(set(first_all) | set(last_int) | set(last_margin) | set(last_para) | {u for ab in pairs for u in ab})
        self.ui = {u: i for i, u in enumerate(self.units)}
        nu = len(self.units)
        # boundary table K[b][a] = P(a | b) / P(a)
        K = np.ones((nu + 1, nu + 1))
        tot_b = Counter()
        for (b, a), n in pairs.items():
            tot_b[b] += n
        pa = np.array([first_all.get(u, 0) + 0.5 for u in self.units])
        pa = pa / pa.sum()
        for b in self.units:
            if tot_b[b] == 0:
                continue
            row = np.array([pairs.get((b, u), 0) + 0.5 for u in self.units])
            K[self.ui[b], :nu] = (row / row.sum()) / pa
        self.K = K
        pad = lambda v: np.append(v, 1.0)
        self.I_line = pad(_ratio(first_line, first_all, self.units))
        self.I_para = pad(_ratio(first_para, first_all, self.units))
        self.F_margin = pad(_ratio(last_margin, last_int, self.units))
        self.F_para = pad(_ratio(last_para, last_int, self.units))
        self.rep, self.coin, self.repset = {}, {}, {}
        for k, toks in toks_g.items():
            if lines_g[k] < 30 and k[0] != 'A':
                continue
            c = Counter(toks)
            types = [t for t, n in c.items() if n >= 2]
            self.rep[k] = (types, np.array([c[t] for t in types], float),
                           np.array([self.ui.get(eva_units(t)[0], nu) for t in types]),
                           np.array([self.ui.get(eva_units(t)[-1], nu) for t in types]))
            self.repset[k] = set(types)
            self.coin[k] = _tok_model(toks, m)
        alltypes = [t for t, n in glob_types.items() if n >= 2]
        near = T.ed1_pairs(alltypes, eva_units)
        self.nb = defaultdict(list)
        for a, b in near:
            self.nb[alltypes[a]].append(alltypes[b])
        self.gcount = glob_types
        uc = Counter(u for t, n in glob_types.items() for u in eva_units(t) for _ in range(n))
        self.slip_units, self.slip_w = list(uc), [uc[u] for u in uc]

    def gkey(self, p):
        for k in (('G', p.lang, p.section), ('L', p.lang), ('A',)):
            if k in self.rep:
                return k

    def _uidx(self, u):
        return self.ui.get(u, len(self.units))

    def _factor_tok(self, tok, prev_last, initial, para_first, final, endkind):
        u = eva_units(tok)
        f = 1.0
        if initial:
            f *= (self.I_para if para_first else self.I_line)[self._uidx(u[0])]
        elif self.use_K and prev_last is not None:
            f *= self.K[prev_last, self._uidx(u[0])]
        if final:
            f *= (self.F_para if endkind == 'para' else self.F_margin)[self._uidx(u[-1])]
        return f

    def _coin(self, gk, rng, prev_last, initial, para_first, final, endkind):
        mdl, rs = self.coin[gk], self.repset[gk]
        cands = []
        for _ in range(30):
            s, out = '^' * ORDER, ''
            while len(out) < 15:
                c = mdl.get(s[-ORDER:])
                if not c:
                    break
                ks = list(c)
                x = rng.choices(ks, [c[k] for k in ks])[0]
                if x == '$':
                    break
                out += x
                s += x
            if out and out not in rs:
                cands.append(out)
        if not cands:
            return None
        w = [self._factor_tok(t, prev_last, initial, para_first, final, endkind) for t in cands]
        return rng.choices(cands, w)[0]

    def slip(self, tok, rng):
        u = list(eva_units(tok))
        op = rng.randrange(3)
        if op == 0 and u:
            u[rng.randrange(len(u))] = rng.choices(self.slip_units, self.slip_w)[0]
        elif op == 1:
            u.insert(rng.randrange(len(u) + 1), rng.choices(self.slip_units, self.slip_w)[0])
        elif len(u) > 1:
            del u[rng.randrange(len(u))]
        return ''.join(u)

    def generate(self, layout, prm, seed=0, name='TR'):
        rng = random.Random(seed)
        nrng = np.random.default_rng(seed)
        qvec = {}
        pages = []
        for p in layout.pages:
            gk = self.gkey(p)
            types, base, fidx, lidx = self.rep[gk]
            n = len(types)
            if (p.quire, gk) not in qvec:
                qvec[(p.quire, gk)] = prm['sq'] * nrng.standard_normal(n)
            logw = np.log(base) + qvec[(p.quire, gk)] + prm['sp'] * nrng.standard_normal(n)
            lv = np.zeros(n)
            hist, lines, para_first = [], [], True
            for li, l in enumerate(p.lines):
                if li > 0 and prm['sw'] > 0:
                    lv += prm['sw'] * nrng.standard_normal(n)
                w = np.exp(logw + lv)
                target = len(' '.join(l.toks))
                endkind = 'para' if l.para_final else 'margin'
                toks = self._line(gk, types, w, fidx, lidx, target, endkind, para_first, hist, prm, rng, nrng)
                lines.append(Ln(toks=toks, para_final=l.para_final, eligible=l.eligible))
                para_first = bool(l.para_final)
            pages.append(Pg(id=p.id, lines=lines, hand=p.hand, quire=p.quire, section=p.section, lang=p.lang))
        return Corpus(name, pages, 'eva', 'G')

    def _line(self, gk, types, w, fidx, lidx, target, endkind, para_first, hist, prm, rng, nrng):
        toks, length, prev_last = [], 0, None
        while True:
            remaining = target - length - (1 if toks else 0)
            final = remaining <= 5 or len(toks) >= 30
            initial = not toks
            tok, retrieved = None, False
            if rng.random() < prm['c']:
                tok = self._coin(gk, rng, prev_last, initial, para_first, final, endkind)
            if tok is None:
                retrieved = True
                if hist and not final and not initial and rng.random() < prm['rho']:
                    k = len(hist)
                    src = rng.choices(hist, [math.exp(-(k - 1 - i) / prm['tau']) for i in range(k)])[0]
                    if rng.random() >= prm['e'] and self.nb.get(src):
                        cand = self.nb[src]
                        src = rng.choices(cand, [self.gcount[x] for x in cand])[0]
                    tok = src
                else:
                    fac = np.ones(len(types))
                    if initial:
                        fac = fac * (self.I_para if para_first else self.I_line)[fidx]
                    elif self.use_K and prev_last is not None:
                        fac = fac * self.K[prev_last][fidx]
                    if final:
                        fac = fac * (self.F_para if endkind == 'para' else self.F_margin)[lidx]
                    cum = np.cumsum(w * fac)
                    tok = types[int(np.searchsorted(cum, nrng.random() * cum[-1], side='right'))]
            out = self.slip(tok, rng) if (prm['eps'] and rng.random() < prm['eps']) else tok
            toks.append(out)
            length += len(out) + (1 if len(toks) > 1 else 0)
            if retrieved:
                hist.append(tok)
            prev_last = self._uidx(eva_units(out)[-1])
            if final:
                return toks


# ------------------------------------------------------------------ fitting / stages

GRIDS = {'c': [0.1, 0.2, 0.3, 0.4], 'sq': [0, 0.2, 0.4], 'sp': [0, 0.2, 0.4, 0.6], 'sw': [0, 0.05, 0.1, 0.2],
         'rho': [0, 0.03, 0.05, 0.08], 'tau': [4, 8, 16], 'e': [0.1, 0.3, 0.6], 'eps': [0, 0.01, 0.02], 'm': [1, 2]}
ORDER_P = ['m', 'c', 'eps', 'rho', 'tau', 'e', 'sq', 'sp', 'sw']
START = {'m': 2, 'c': 0.3, 'eps': 0.01, 'rho': 0.05, 'tau': 8, 'e': 0.3, 'sq': 0.2, 'sp': 0.4, 'sw': 0.05}
MODELS = {'TR': (True, {}), 'D1-nocoin': (True, {'c': 0}), 'D2-norepvar': (True, {'sq': 0, 'sp': 0, 'sw': 0}),
          'D3-norecency': (True, {'rho': 0}), 'D4-noK': (False, {})}
RUNS = [('primary', 'even', 'odd', m) for m in MODELS] + [('secondary', 'odd', 'even', 'TR')]
_C = {}


def _gen(tr, useK, m):
    k = (tr, useK, m)
    if k not in _C:
        _C[k] = TR(E3.halves()[tr], m=m, use_K=useK)
    return _C[k]


def _eval(args):
    tr, useK, prm = args
    c = _gen(tr, useK, prm['m']).generate(E3.halves()[tr], prm, seed=0)
    return E3.targets(c, double_coded=False)


def fit_one(tr, model, vt, ex):
    useK, fixed = MODELS[model]
    prm = dict(START, **fixed)
    free = [k for k in ORDER_P if k not in fixed and not (fixed.get('rho') == 0 and k in ('tau', 'e'))]
    log = []
    for _ in range(3):
        for k in free:
            cands = [dict(prm, **{k: v}) for v in GRIDS[k]]
            res = list(ex.map(_eval, [(tr, useK, c) for c in cands]))
            sc = [E3.objective(r, vt) for r in res]
            i = int(np.argmin(sc))
            prm = cands[i]
            log.append({'param': k, 'value': prm[k], 'score': sc[i]})
        print(tr, model, {k: prm[k] for k in ORDER_P}, round(sc[i], 3), {kk: round(v, 4) for kk, v in res[i].items()}, flush=True)
    return prm, log, res[i]


def main(cmd):
    os.makedirs(OUT, exist_ok=True)
    H = E3.halves()
    if cmd == 'fit':
        vts = json.load(open('results/mechanism/e3/fits.json'))['training_targets']
        fits = {'training_targets': vts}
        with ProcessPoolExecutor(max_workers=8) as ex:
            for run, tr, te, model in RUNS:
                prm, log, got = fit_one(tr, model, vts[tr], ex)
                fits[f'{run}:{model}'] = {'train': tr, 'test': te, 'params': prm, 'fit_values': got, 'log': log}
                json.dump(fits, open(f'{OUT}/fits.json', 'w'), indent=1)
    elif cmd == 'generate':
        fits = json.load(open(f'{OUT}/fits.json'))
        for run, tr, te, model in RUNS:
            f = fits[f'{run}:{model}']
            g = TR(H[tr], m=f['params']['m'], use_K=MODELS[model][0])
            for s in range(3):
                pickle.dump(g.generate(H[te], f['params'], seed=300 + s, name=f'{run}-{model}-{s}'),
                            open(f'{OUT}/gen_{run}-{model}-{s}.pkl', 'wb'))
            print('generated', run, model, flush=True)
    elif cmd == 'phenotype':
        jobs = [f'{run}-{model}-{s}' for run, tr, te, model in RUNS for s in range(3)]
        res = {}
        with ProcessPoolExecutor(max_workers=8) as ex:
            for key, ph in ex.map(_pheno, jobs):
                res[f'G:{key}'] = ph
                print(key, 'done', flush=True)
                json.dump(res, open(f'{OUT}/phenotype.json', 'w'), indent=1)
    elif cmd == 'report':
        report()


def _pheno(key):
    c = pickle.load(open(f'{OUT}/gen_{key}.pkl', 'rb'))
    return key, E2.phenotype(c, double_coded=False)


def report():
    R3 = json.load(open('results/mechanism/e3/phenotype.json'))
    R6 = json.load(open(f'{OUT}/phenotype.json'))
    runs = [(r, tr, te, m, R6) for r, tr, te, m in RUNS] + \
           [('primary', 'even', 'odd', 'HGR2', R3), ('secondary', 'odd', 'even', 'HGR2', R3)]
    out, txt = {}, []
    for run, tr, te, model, R in runs:
        V = R3[f'V:{te}:full']
        jk = [v for k, v in R3.items() if k.startswith(f'V:{te}:') and not k.endswith(':full')]
        G = len(jk)
        seeds = [R[f'G:{run}-{model}-{s}'] for s in range(3) if f'G:{run}-{model}-{s}' in R]
        rows = {}
        for k, v in V.items():
            gv = [s[k] for s in seeds if s.get(k) is not None]
            if k == 'T4_peak':
                rows[k] = {'V': v, 'G': float(np.mean(gv)), 'pass': bool(sum(x > 0 for x in gv) <= 1 and v == 0)}
                continue
            vals = [x[k] for x in jk if x.get(k) is not None]
            se = math.sqrt((G - 1) / G * sum((x - np.mean(vals)) ** 2 for x in vals)) if len(vals) > 1 else 0.0
            if v is None or not gv:
                rows[k] = {'V': v, 'G': None, 'pass': None}
                continue
            gm, sd = float(np.mean(gv)), (float(np.std(gv, ddof=1)) if len(gv) > 1 else 0.0)
            tol = 2 * math.sqrt(se ** 2 + sd ** 2) + 0.01 * abs(v)
            rows[k] = {'V': v, 'G': gm, 'tol': tol, 'pass': abs(gm - v) <= tol, 'fitted': k in E3.FITTED}
        n = sum(1 for r in rows.values() if r['pass'])
        nu = sum(1 for k, r in rows.items() if r['pass'] and k not in E3.FITTED)
        key = f'{run}:{model}'
        out[key] = {'n_pass': n, 'n_pass_unfitted': nu, 'rows': rows}
        txt.append(f"{key} (fit {tr}, test {te}): {n}/40 pass (unfitted {nu}/31); fail: {[k for k, r in rows.items() if r['pass'] is False]}")
    json.dump(out, open(f'{OUT}/report.json', 'w'), indent=1)
    print('\n'.join(txt))
    names = [k for k in out if k.startswith('primary')]
    print(f"{'statistic':14s} {'V(odd)':>9s} " + ' '.join(f'{n.split(":")[1][:9]:>11s}' for n in names))
    for k in R3['V:odd:full']:
        cells = []
        for n in names:
            rr = out[n]['rows'][k]
            g = rr['G']
            cells.append(f"{(g if g is not None else float('nan')):9.4f}{'✓' if rr['pass'] else '✗'} ")
        print(f"{k:14s} {R3['V:odd:full'][k]:9.4f} " + ' '.join(cells) + ('  (fitted)' if k in E3.FITTED else ''))


if __name__ == '__main__':
    main(sys.argv[1])
