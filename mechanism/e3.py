"""E3: revised generator HGR2 (margin-driven endings, slow within-page drift, one-off slips), cross-fitted
(mechanism/E3_PREREG.md).

    python3 -m mechanism.e3 fit          # fit all models (primary: fit even; secondary: fit odd)
    python3 -m mechanism.e3 generate
    python3 -m mechanism.e3 phenotype    # test halves + quire jackknife + generated corpora
    python3 -m mechanism.e3 report
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
from mechanism import tests as T
from mechanism.corpus import Corpus, Ln, Pg, eva_units

warnings.filterwarnings('ignore', category=RuntimeWarning, message='.*encountered in matmul')
OUT = 'results/mechanism/e3'
ORDER = 3
ENDS = ('$', '%')


def halves():
    odd, even = E2.split()          # E2: train = odd bifolios, test = even bifolios
    return {'odd': odd, 'even': even}


def _counts(strings):
    m = defaultdict(Counter)
    for s in strings:
        t = '^' * ORDER + s
        for i in range(ORDER, len(t)):
            m[t[i - ORDER:i]][t[i]] += 1
    return m


def _prune(m, thr):
    if thr <= 1:
        return m
    out = {}
    for ctx, c in m.items():
        keep = Counter({k: v for k, v in c.items() if v >= thr})
        out[ctx] = keep if keep else Counter(c)
    return out


class HGR2:
    def __init__(self, train, m=2, c1=True):
        self.c1 = c1
        by_group, by_lang, by_quire, alls = defaultdict(list), defaultdict(list), defaultdict(list), []
        types, units = Counter(), Counter()
        for p in train.pages:
            for l in p.lines:
                end = ('%' if l.para_final else '$') if c1 else '$'
                s = ' '.join(l.toks) + end
                by_group[(p.lang, p.section)].append(s)
                by_lang[p.lang].append(s)
                by_quire[p.quire].append(s)
                alls.append(s)
                types.update(l.toks)
                for t in l.toks:
                    units.update(eva_units(t))
        self.glob = _prune(_counts(alls), m)
        self.group = {g: _prune(_counts(v), m) for g, v in by_group.items() if len(v) >= 30}
        self.lang = {g: _prune(_counts(v), m) for g, v in by_lang.items() if len(v) >= 30}
        self.quire = {q: _counts(v) for q, v in by_quire.items()}
        self.types = types
        tl = list(types)
        near = T.ed1_pairs(tl, eva_units)
        self.nb = defaultdict(list)
        for a, b in near:
            self.nb[tl[a]].append(tl[b])
        self.units = list(units)
        self.unit_w = [units[u] for u in self.units]
        self.glyphs = sorted({ch for ctx in self.glob for ch in self.glob[ctx]} - {' ', '$', '%'})

    def model_for(self, p):
        return self.group.get((p.lang, p.section)) or self.lang.get(p.lang) or self.glob

    def dist(self, ctx, gm, qm, prm, logtilt, allow):
        base = gm.get(ctx) or self.glob.get(ctx)
        if not base:
            return None
        n = sum(base.values())
        out = {c: v / n for c, v in base.items()}
        lam = prm['lam']
        q = qm.get(ctx) if (qm is not None and lam > 0) else None
        if q:
            qa = {c: v for c, v in q.items() if c in out}
            nq = sum(qa.values())
            if nq > 0:
                out = {c: (1 - lam) * out[c] + lam * qa.get(c, 0) / nq for c in out}
        th = prm['theta']
        if th != 1.0:
            out = {c: v ** (1.0 / th) for c, v in out.items()}
        if logtilt:
            out = {c: v * math.exp(logtilt.get(c, 0.0)) for c, v in out.items()}
        out = {c: v for c, v in out.items() if c in allow or c not in (' ', '$', '%')}
        return out or None

    def slip(self, tok, rng):
        u = list(eva_units(tok))
        op = rng.randrange(3)
        if op == 0 and u:
            u[rng.randrange(len(u))] = rng.choices(self.units, self.unit_w)[0]
        elif op == 1:
            u.insert(rng.randrange(len(u) + 1), rng.choices(self.units, self.unit_w)[0])
        elif len(u) > 1:
            del u[rng.randrange(len(u))]
        return ''.join(u)

    def sample_token(self, prefix, gm, qm, prm, lt, rng, maxlen=15):
        tok = ''
        while True:
            ctx = ('^' * ORDER + prefix + tok)[-ORDER:]
            allow = {' '} if tok else set()
            d = self.dist(ctx, gm, qm, prm, lt, allow)
            if not d:
                return tok or rng.choice(list(self.types))
            ks = list(d)
            c = rng.choices(ks, [d[k] for k in ks])[0]
            if c == ' ' or len(tok) >= maxlen:
                return tok
            tok += c

    def p_end(self, prefix, end, gm, qm, prm, lt):
        d = self.dist(('^' * ORDER + prefix)[-ORDER:], gm, qm, prm, lt, {' ', end})
        if not d:
            return 0.0
        z = sum(d.values())
        return d.get(end, 0.0) / z if z else 0.0

    def generate(self, layout, prm, seed=0, name='HGR2'):
        rng = random.Random(seed)
        pages = []
        for p in layout.pages:
            gm, qm = self.model_for(p), self.quire.get(p.quire)
            lt = {c: prm['sig'] * rng.gauss(0, 1) for c in self.glyphs} if prm['sig'] > 0 else {c: 0.0 for c in self.glyphs}
            hist, lines = [], []
            for li, l in enumerate(p.lines):
                if li > 0 and prm['sigw'] > 0:
                    for c in lt:
                        lt[c] += prm['sigw'] * rng.gauss(0, 1)
                target = len(' '.join(l.toks))
                end = ('%' if l.para_final else '$') if self.c1 else '$'
                toks = self._line_c1(target, end, gm, qm, prm, lt, hist, rng) if self.c1 else \
                    self._line_loose(target, gm, qm, prm, lt, hist, rng)
                lines.append(Ln(toks=toks, para_final=l.para_final, eligible=l.eligible))
            pages.append(Pg(id=p.id, lines=lines, hand=p.hand, quire=p.quire, section=p.section, lang=p.lang))
        return Corpus(name, pages, 'eva', 'G')

    def _choose_recent(self, hist, prm, rng):
        k = len(hist)
        w = [math.exp(-(k - 1 - i) / prm['tau']) for i in range(k)]
        src = rng.choices(hist, w)[0]
        if rng.random() >= prm['e'] and self.nb.get(src):
            cand = self.nb[src]
            src = rng.choices(cand, [self.types[x] for x in cand])[0]
        return src

    def _emit(self, s, intended, toks, hist, prm, rng):
        out = self.slip(intended, rng) if (prm['eps'] and rng.random() < prm['eps']) else intended
        toks.append(out)
        hist.append(intended)        # memory keeps the intended form (C3)
        return (s + ' ' if s else '') + out

    def _line_c1(self, target, end, gm, qm, prm, lt, hist, rng):
        s, toks = '', []
        while True:
            remaining = target - len(s) - (1 if s else 0)
            final = remaining <= 5 or len(toks) >= 30
            prefix = s + (' ' if s else '')
            if final:
                cands = [self.sample_token(prefix, gm, qm, prm, lt, rng) for _ in range(20)]
                w = [self.p_end(prefix + c, end, gm, qm, prm, lt) for c in cands]
                tok = rng.choices(cands, w)[0] if sum(w) > 0 else rng.choice(cands)
                self._emit(s, tok, toks, hist, prm, rng)
                return toks
            if hist and rng.random() < prm['rho']:
                tok = self._choose_recent(hist, prm, rng)
            else:
                tok = self.sample_token(prefix, gm, qm, prm, lt, rng)
            s = self._emit(s, tok, toks, hist, prm, rng)

    def _line_loose(self, target, gm, qm, prm, lt, hist, rng):
        """E2's line model (end symbol allowed after 60% of the target, stop at 140%)."""
        s, toks = '', []
        while True:
            prefix = s + (' ' if s else '')
            if hist and rng.random() < prm['rho']:
                tok = self._choose_recent(hist, prm, rng)
            else:
                tok = self.sample_token(prefix, gm, qm, prm, lt, rng)
            s = self._emit(s, tok, toks, hist, prm, rng)
            if len(s) >= 1.4 * target or len(toks) >= 30:
                return toks
            if len(s) >= 0.6 * target and rng.random() < self.p_end(s, '$', gm, qm, prm, lt):
                return toks


# ------------------------------------------------------------------ fitting

def targets(c, double_coded):
    t = E2.targets(c, double_coded)
    b = T.t7b(c, double_coded_only=double_coded)
    t['T7b_rec'] = b['recurrence_share']
    words = [w for p in c.pages for l in p.lines if len(l.toks) >= 2 for w in l.toks]
    cnt = Counter(words)
    t['hapax'] = sum(1 for v in cnt.values() if v == 1) / len(cnt)
    t['ttr'] = len(cnt) / len(words)
    t['T6b_slope'] = T.t4c(c, reps=10)['slope_1_8']
    t['T3a_rho'] = T.t3a(c)['rho']
    return t


FLOORS = {'DI_near': 0.05, 'DI_exact': 0.05, 'T7b_rec': 0.02, 'T6b_slope': 0.002}
TKEYS = ['DI_near', 'DI_exact', 'dev_rate', 'T7b_rec', 'page_mi', 'cons_excess', 'hapax', 'ttr', 'T6b_slope', 'T3a_rho']


def objective(g, v):
    return sum(((g[k] - v[k]) / max(abs(v[k]), FLOORS.get(k, 0.0))) ** 2 for k in TKEYS if v[k] is not None and g[k] is not None)


GRIDS = {'m': [1, 2, 3], 'theta': [1.0, 1.25, 1.5], 'eps': [0, 0.01, 0.02, 0.04, 0.08],
         'rho': [0.03, 0.05, 0.08, 0.12], 'tau': [4, 8, 16], 'e': [0.1, 0.3, 0.6],
         'lam': [0, 0.25, 0.5], 'sig': [0, 0.2, 0.4], 'sigw': [0, 0.05, 0.1, 0.2]}
ORDER_PARAMS = ['m', 'theta', 'eps', 'rho', 'tau', 'e', 'lam', 'sig', 'sigw']
START = {'m': 2, 'theta': 1.0, 'eps': 0.01, 'rho': 0.08, 'tau': 8, 'e': 0.1, 'lam': 0.25, 'sig': 0.4, 'sigw': 0.05}
MODELS = {  # name: (c1, fixed params)
    'HGR2': (True, {}),
    'B1-noC1': (False, {}),
    'B2-noC2': (True, {'sigw': 0}),
    'B3-noC3': (True, {'eps': 0, 'theta': 1.0, 'm': 2}),
    'B0-E2class': (False, {'sigw': 0, 'eps': 0, 'theta': 1.0, 'm': 2}),
}
RUNS = [('primary', 'even', 'odd', m) for m in MODELS] + [('secondary', 'odd', 'even', 'HGR2')]

_CACHE = {}


def _gen(train_half, c1, m):
    key = (train_half, c1, m)
    if key not in _CACHE:
        _CACHE[key] = HGR2(halves()[train_half], m=m, c1=c1)
    return _CACHE[key]


def _eval(args):
    train_half, c1, prm = args
    g = _gen(train_half, c1, prm['m'])
    c = g.generate(halves()[train_half], prm, seed=0)
    return targets(c, double_coded=False)


def fit_one(train_half, model, vt, ex):
    c1, fixed = MODELS[model]
    prm = dict(START, **fixed)
    free = [k for k in ORDER_PARAMS if k not in fixed]
    log = []
    for _ in range(3):
        for k in free:
            cands = [dict(prm, **{k: v}) for v in GRIDS[k]]
            res = list(ex.map(_eval, [(train_half, c1, c) for c in cands]))
            sc = [objective(r, vt) for r in res]
            i = int(np.argmin(sc))
            prm = cands[i]
            log.append({'param': k, 'value': prm[k], 'score': sc[i]})
        print(train_half, model, 'pass done', {k: prm[k] for k in ORDER_PARAMS}, round(sc[i], 3),
              {kk: round(v, 4) for kk, v in res[i].items()}, flush=True)
    return prm, log, res[i]


def main(cmd):
    os.makedirs(OUT, exist_ok=True)
    H = halves()
    if cmd == 'fit':
        fits = {}
        vts = {h: targets(H[h], double_coded=True) for h in ('even', 'odd')}
        fits['training_targets'] = vts
        print('targets', vts, flush=True)
        with ProcessPoolExecutor(max_workers=8) as ex:
            for run, tr, te, model in RUNS:
                prm, log, got = fit_one(tr, model, vts[tr], ex)
                fits[f'{run}:{model}'] = {'train': tr, 'test': te, 'params': prm, 'fit_values': got, 'log': log}
                json.dump(fits, open(f'{OUT}/fits.json', 'w'), indent=1)
    elif cmd == 'generate':
        fits = json.load(open(f'{OUT}/fits.json'))
        for run, tr, te, model in RUNS:
            f = fits[f'{run}:{model}']
            g = HGR2(H[tr], m=f['params']['m'], c1=MODELS[model][0])
            for seed in range(3):
                c = g.generate(H[te], f['params'], seed=200 + seed, name=f'{run}-{model}-{seed}')
                pickle.dump(c, open(f'{OUT}/gen_{run}-{model}-{seed}.pkl', 'wb'))
            print('generated', run, model, flush=True)
    elif cmd == 'phenotype':
        jobs = []
        for half in ('odd', 'even'):
            jobs.append(('V', half, 'full'))
            for q in sorted({p.quire for p in H[half].pages}):
                jobs.append(('V', half, q))
        for run, tr, te, model in RUNS:
            for s in range(3):
                jobs.append(('G', None, f'{run}-{model}-{s}'))
        res = {}
        with ProcessPoolExecutor(max_workers=8) as ex:
            for key, ph in ex.map(_pheno, jobs):
                res[key] = ph
                print(key, 'done', flush=True)
                json.dump(res, open(f'{OUT}/phenotype.json', 'w'), indent=1)
    elif cmd == 'report':
        report()


def _pheno(job):
    kind, half, key = job
    if kind == 'V':
        c = halves()[half]
        if key != 'full':
            c = Corpus(c.name, [p for p in c.pages if p.quire != key], 'eva', 'V')
        return f'V:{half}:{key}', E2.phenotype(c, double_coded=True)
    c = pickle.load(open(f'{OUT}/gen_{key}.pkl', 'rb'))
    return f'G:{key}', E2.phenotype(c, double_coded=False)


FITTED = {'T6a_near', 'T6a_exact', 'T7b_rate', 'T7b_rec', 'page_mi', 'hapax', 'ttr', 'T6b_slope', 'T3a_rho'}


def report():
    R = json.load(open(f'{OUT}/phenotype.json'))
    out, txt = {}, []
    for run, tr, te, model in RUNS:
        V = R[f'V:{te}:full']
        jk = [v for k, v in R.items() if k.startswith(f'V:{te}:') and not k.endswith(':full')]
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
            rows[k] = {'V': v, 'G': gm, 'se_V': se, 'sd_G': sd, 'tol': tol, 'pass': abs(gm - v) <= tol,
                       'fitted': k in FITTED}
        n = sum(1 for r in rows.values() if r['pass'])
        nb = sum(1 for k, r in rows.items() if r['pass'] and k not in FITTED)
        out[f'{run}:{model}'] = {'n_pass': n, 'n': len(rows), 'n_pass_unfitted': nb,
                                 'n_unfitted': sum(1 for k in rows if k not in FITTED), 'rows': rows}
        txt.append(f"{run}:{model} (fit {tr}, test {te}): {n}/{len(rows)} pass "
                   f"(unfitted {nb}/{out[f'{run}:{model}']['n_unfitted']}); fail: {[k for k, r in rows.items() if r['pass'] is False]}")
    json.dump(out, open(f'{OUT}/report.json', 'w'), indent=1)
    print('\n'.join(txt))
    names = list(out)
    print(f"{'statistic':14s} {'V(odd)':>9s} " + ' '.join(f'{n.split(":")[1][:9]:>11s}' for n in names))
    Vodd = R['V:odd:full']
    for k in Vodd:
        cells = []
        for n in names:
            rr = out[n]['rows'][k]
            g = rr['G']
            cells.append(f"{(g if g is not None else float('nan')):9.4f}{'✓' if rr['pass'] else '✗'} ")
        print(f"{k:14s} {Vodd[k] if Vodd[k] is not None else float('nan'):9.4f} " + ' '.join(cells) + ('  (fitted)' if k in FITTED else ''))


if __name__ == '__main__':
    main(sys.argv[1])
