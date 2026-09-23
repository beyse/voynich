"""E2: explicit hard-grammar + recency + session + slip generator, fitted on odd bifolios, tested on even
bifolios against the frozen phenotype (mechanism/E2_PREREG.md).

    python3 -m mechanism.e2 fit        # fit full model and ablations on the training half
    python3 -m mechanism.e2 generate   # generate test-layout corpora (3 seeds per model)
    python3 -m mechanism.e2 phenotype  # Voynich test half (with quire jackknife) and generated corpora
    python3 -m mechanism.e2 report     # tolerance comparison
"""
import json
import math
import os
import pickle
import random
import re
import sys
import warnings
from collections import Counter, defaultdict
from concurrent.futures import ProcessPoolExecutor

import numpy as np

from mechanism import e1 as E1
from mechanism import tests as T
from mechanism.corpus import Corpus, Ln, Pg, eva_units, load_voynich

warnings.filterwarnings('ignore', category=RuntimeWarning, message='.*encountered in matmul')
OUT = 'results/mechanism/e2'
ORDER = 3
GLYPHS_EXCLUDED_FROM_TILT = {' ', '$'}


# ------------------------------------------------------------------ split

def bifolio():
    out = {}
    for l in open('data/ZL3b-n.txt', encoding='latin-1'):
        m = re.match(r'^<(f\w+)>\s+<!(.*)>', l)
        if m:
            b = dict(re.findall(r'\$(\w)=(\w+)', m.group(2))).get('B')
            out[m.group(1)] = int(b) if b and b.isdigit() else None
    return out


def split():
    V = load_voynich()
    B = bifolio()
    tr = [p for p in V.pages if B.get(p.id) and B[p.id] % 2 == 1]
    te = [p for p in V.pages if B.get(p.id) and B[p.id] % 2 == 0]
    return Corpus('V-train', tr, 'eva', 'V'), Corpus('V-test', te, 'eva', 'V')


# ------------------------------------------------------------------ generator

def _counts(strings):
    m = defaultdict(Counter)
    for s in strings:
        t = '^' * ORDER + s + '$'
        for i in range(ORDER, len(t)):
            m[t[i - ORDER:i]][t[i]] += 1
    return m


def _prune(m, prune):
    if not prune:
        return m
    out = {}
    for ctx, c in m.items():
        keep = Counter({k: v for k, v in c.items() if v >= 2})
        out[ctx] = keep if keep else Counter(c)
    return out


class HGR:
    def __init__(self, train, prune=True):
        self.prune = prune
        lines_by_group = defaultdict(list)
        lines_by_lang = defaultdict(list)
        lines_by_quire = defaultdict(list)
        allines = []
        types = Counter()
        units = Counter()
        for p in train.pages:
            for l in p.lines:
                s = ' '.join(l.toks)
                lines_by_group[(p.lang, p.section)].append(s)
                lines_by_lang[p.lang].append(s)
                lines_by_quire[p.quire].append(s)
                allines.append(s)
                types.update(l.toks)
                for t in l.toks:
                    units.update(eva_units(t))
        self.glob = _prune(_counts(allines), prune)
        self.group = {g: _prune(_counts(v), prune) for g, v in lines_by_group.items() if len(v) >= 30}
        self.lang = {g: _prune(_counts(v), prune) for g, v in lines_by_lang.items() if len(v) >= 30}
        self.quire = {q: _counts(v) for q, v in lines_by_quire.items()}
        self.types = types
        tl = list(types)
        near = T.ed1_pairs(tl, eva_units)
        self.nb = defaultdict(list)
        for a, b in near:
            self.nb[tl[a]].append(tl[b])
        self.units = list(units)
        self.unit_w = [units[u] for u in self.units]
        self.glyphs = sorted({ch for ctx in self.glob for ch in self.glob[ctx]} - {'$'})

    def model_for(self, p):
        return self.group.get((p.lang, p.section)) or self.lang.get(p.lang) or self.glob

    def dist(self, ctx, gm, qm, lam, tilt):
        base = gm.get(ctx) or self.glob.get(ctx)
        if not base:
            return None
        nb_ = sum(base.values())
        out = {c: v / nb_ for c, v in base.items()}
        q = qm.get(ctx) if (qm is not None and lam > 0) else None
        if q:
            qa = {c: v for c, v in q.items() if c in out}     # session reweights allowed transitions only
            nq = sum(qa.values())
            if nq > 0:
                out = {c: (1 - lam) * out[c] + lam * qa.get(c, 0) / nq for c in out}
        if tilt:
            out = {c: v * tilt.get(c, 1.0) for c, v in out.items()}
        return out

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

    def generate(self, layout, prm, seed=0, name='HGR'):
        lam, sig, rho, tau, e, eps = (prm[k] for k in ('lam', 'sig', 'rho', 'tau', 'e', 'eps'))
        rng = random.Random(seed)
        pages = []
        for p in layout.pages:
            gm = self.model_for(p)
            qm = self.quire.get(p.quire)
            tilt = {c: math.exp(sig * rng.gauss(0, 1)) for c in self.glyphs if c not in GLYPHS_EXCLUDED_FROM_TILT} if sig > 0 else None
            hist = []
            lines = []
            for l in p.lines:
                target = len(' '.join(l.toks))
                toks = []
                for _ in range(20):
                    toks = self._line(gm, qm, lam, tilt, target, hist, rho, tau, e, eps, rng)
                    if toks:
                        break
                if not toks:
                    toks = [rng.choice(list(self.types))]
                    hist.append(toks[0])
                lines.append(Ln(toks=toks, para_final=l.para_final, eligible=l.eligible))
            pages.append(Pg(id=p.id, lines=lines, hand=p.hand, quire=p.quire, section=p.section, lang=p.lang))
        return Corpus(name, pages, 'eva', 'G')

    def _line(self, gm, qm, lam, tilt, target, hist, rho, tau, e, eps, rng):
        s = ''
        toks = []
        cur_start = True
        while True:
            if cur_start and hist and rho > 0 and rng.random() < rho:
                k = len(hist)
                w = [math.exp(-(k - 1 - i) / tau) for i in range(k)]
                src = rng.choices(hist, w)[0]
                if rng.random() >= e and self.nb.get(src):
                    cand = self.nb[src]
                    src = rng.choices(cand, [self.types[x] for x in cand])[0]
                s += src
                # after a copied token: choose space or end from the automaton
                d = self.dist(('^' * ORDER + s)[-ORDER:], gm, qm, lam, None) or {' ': 1.0}
                opts = {c: d.get(c, 0) for c in (' ', '$')}
                if len(s) < 0.6 * target:
                    opts['$'] = 0
                if sum(opts.values()) <= 0:
                    opts = {' ': 1.0} if len(s) < 1.4 * target else {'$': 1.0}
                c = rng.choices(list(opts), list(opts.values()))[0]
                tok = s.split(' ')[-1]
                if eps and rng.random() < eps:
                    new = self.slip(tok, rng)
                    s = s[:len(s) - len(tok)] + new
                    tok = new
                toks.append(tok)
                hist.append(tok)
                if c == '$' or len(s) >= 1.4 * target:
                    return toks
                s += ' '
                cur_start = True
                continue
            d = self.dist(('^' * ORDER + s)[-ORDER:], gm, qm, lam, tilt)
            if not d:
                c = '$'
            else:
                if len(s) < 0.6 * target and len(d) > 1:
                    d = {k: v for k, v in d.items() if k != '$'}
                if cur_start:
                    d = {k: v for k, v in d.items() if k not in (' ', '$')} or d
                ks = list(d)
                c = rng.choices(ks, [d[k] for k in ks])[0]
            if c in (' ', '$') or len(s) >= 1.4 * target:
                tok = s.split(' ')[-1]
                if tok:
                    if eps and rng.random() < eps:
                        new = self.slip(tok, rng)
                        s = s[:len(s) - len(tok)] + new
                        tok = new
                    toks.append(tok)
                    hist.append(tok)
                if c == '$' or len(s) >= 1.4 * target or not tok:
                    return toks
                s += ' '
                cur_start = True
            else:
                s += c
                cur_start = False


# ------------------------------------------------------------------ fitting targets

def cons_excess(c, seed=0):
    rng = np.random.default_rng(seed)
    by = defaultdict(list)
    for p in c.pages:
        if p.hand and sum(len(l.toks) for l in p.lines) >= 100:
            by[p.hand].append(p)
    vals = []
    for h, ps in by.items():
        if len(ps) < 10:
            continue
        for a, b in zip(ps, ps[1:]):
            E = T._excess_matrix([a, b], c.units, rng)
            vals.append(E[0, 1])
    return float(np.mean(vals)) if vals else float('nan')


def page_mi(c):
    from voynich.battery import _excess_b
    rng = random.Random(1)
    pp = [(i, w) for i, p in enumerate(c.pages) for l in p.lines for w in l.toks]
    return _excess_b(rng.sample(pp, min(len(pp), 20000)))


def targets(c, double_coded):
    a = T.t6a(c, reps=20)
    b = T.t7b(c, double_coded_only=double_coded)
    return {'DI_near': a['DI_near'], 'DI_exact': a['DI_exact'], 'dev_rate': b['rate_per_1000'],
            'page_mi': page_mi(c), 'cons_excess': cons_excess(c)}


def objective(g, v, keys):
    return sum(((g[k] - v[k]) / v[k]) ** 2 for k in keys if v[k])


GRIDS = {'lam': [0, 0.25, 0.5, 0.75], 'sig': [0, 0.1, 0.2, 0.4], 'rho': [0, 0.03, 0.05, 0.08, 0.12],
         'tau': [4, 8, 16], 'e': [0.1, 0.3, 0.6], 'eps': [0, 0.005, 0.01, 0.02, 0.04]}
PARAM_TARGETS = {'lam': ['page_mi', 'cons_excess'], 'sig': ['page_mi', 'cons_excess'],
                 'rho': ['DI_near', 'DI_exact'], 'tau': ['DI_near', 'DI_exact'], 'e': ['DI_near', 'DI_exact'],
                 'eps': ['dev_rate']}
ALL_TARGETS = ['DI_near', 'DI_exact', 'dev_rate', 'page_mi', 'cons_excess']

MODELS = {
    'HGR': {'prune': True, 'fixed': {}},
    'A1-norecency': {'prune': True, 'fixed': {'rho': 0}},
    'A2-noprune-noslip': {'prune': False, 'fixed': {'eps': 0}},
    'A3-nosession': {'prune': True, 'fixed': {'lam': 0, 'sig': 0}},
    'A4-noprune-slip': {'prune': False, 'fixed': {}},
    'A0-baseline': {'prune': False, 'fixed': {'rho': 0, 'eps': 0, 'lam': 0, 'sig': 0}},
}
START = {'lam': 0.5, 'sig': 0.1, 'rho': 0.05, 'tau': 8, 'e': 0.3, 'eps': 0.01}

_G = {}


def _eval(args):
    model, prm = args
    if model not in _G:
        tr, _ = split()
        _G[model] = (HGR(tr, prune=MODELS[model]['prune']), tr)
    g, tr = _G[model]
    c = g.generate(tr, prm, seed=0)
    return targets(c, double_coded=False)


def fit(model, vt, ex):
    prm = dict(START)
    prm.update(MODELS[model]['fixed'])
    free = [k for k in ('eps', 'rho', 'tau', 'e', 'lam', 'sig') if k not in MODELS[model]['fixed']]
    if 'rho' not in free:
        free = [k for k in free if k not in ('tau', 'e')]
    log = []
    for _ in range(2):
        for k in free:
            cands = [dict(prm, **{k: v}) for v in GRIDS[k]]
            res = list(ex.map(_eval, [(model, c) for c in cands]))
            scores = [objective(r, vt, ALL_TARGETS) for r in res]
            i = int(np.argmin(scores))
            prm = cands[i]
            log.append({'param': k, 'value': prm[k], 'score': scores[i], 'targets': res[i]})
            print(model, k, prm[k], round(scores[i], 4), {kk: round(v, 4) for kk, v in res[i].items()}, flush=True)
    return prm, log


# ------------------------------------------------------------------ phenotype

def to_lists(c):
    return [[l.toks for l in p.lines if len(l.toks) >= 1] for p in c.pages]


def phenotype(c, double_coded):
    from voynich.battery import battery
    b = battery(to_lists(c), c.name)
    ph = {k: b[k] for k in ('hapax', 'ttr', 'zipf', 'wlen', 'edge_mi', 'token_mi', 'd2_mi', 'break_mi', 'break_edge',
                            'adj_edge_same_n', 'space_gain', 'lex_real', 'lex_synth', 'h2', 'h3', 'h4', 'lzma', 'page_mi')}
    ph['T1_R'] = T.t1(c)['R_LB']
    ph['T2a_margin'] = T.t2a(c, 'margin', perms=50)['excess']
    ph['T2a_para'] = T.t2a(c, 'para', perms=50)['excess']
    r = T.t2b(c, lambda p: p.section == 'S', sims=100)
    ph['T2b_T'] = r['T']
    ph['T2c_ratio'] = T.t2c(c, perms=100)['ratio_tok']
    ph['T3a_rho'] = T.t3a(c)['rho']
    r = T.t3b(c)
    ph['T3b_cons'], ph['T3b_mono'] = r['consistency'], r['monotone']
    r = T.t3c(c)
    ph['T3c_e1'], ph['T3c_s1'] = r['e1'], r['s1']
    a, bb, cc = T.t4a(c, reps=100), T.t4b(c, reps=100), T.t4c(c, reps=100)
    ph['T4_peak'] = float(bool(a['final']['peaks'] or a['initial']['peaks'] or cc['peaks'] or
                               any((bb[d]['z'] or 0) > 3 for d in bb)))
    ph['T5_S'] = T.t5(c)['S_pooled']
    r = T.t6a(c, reps=20)
    ph['T6a_near'], ph['T6a_exact'] = r['DI_near'], r['DI_exact']
    ph['T6b_slope'] = cc['slope_1_8']
    r = T.t7b(c, double_coded_only=double_coded)
    ph['T7b_rate'], ph['T7b_rec'], ph['T7b_slip'] = r['rate_per_1000'], r['recurrence_share'], r['slip_share']
    r = E1.e1_stats(c, reps=2)['stats']
    ph['E1_LSg'], ph['E1_PS'], ph['E1_WLDg'], ph['E1_WPD'] = r['LS_graded'], r['PS'], r['WLD_graded'], r['WPD']
    return {k: (None if v is None else float(v)) for k, v in ph.items()}


def _pheno_job(args):
    kind, key = args
    if kind == 'V':
        _, te = split()
        if key != 'full':
            te = Corpus('V-test', [p for p in te.pages if p.quire != key], 'eva', 'V')
        return (kind, key), phenotype(te, double_coded=True)
    c = pickle.load(open(f'{OUT}/gen_{key}.pkl', 'rb'))
    return (kind, key), phenotype(c, double_coded=False)


# ------------------------------------------------------------------ main

def main(cmd):
    os.makedirs(OUT, exist_ok=True)
    if cmd == 'fit':
        tr, _ = split()
        vt = targets(tr, double_coded=True)
        print('training targets', vt, flush=True)
        fits = {'training_targets': vt}
        with ProcessPoolExecutor(max_workers=8) as ex:
            for m in MODELS:
                if m == 'A0-baseline':
                    fits[m] = {'params': dict(START, **MODELS[m]['fixed']), 'log': []}
                    continue
                prm, log = fit(m, vt, ex)
                fits[m] = {'params': prm, 'log': log}
                json.dump(fits, open(f'{OUT}/fits.json', 'w'), indent=1)
        json.dump(fits, open(f'{OUT}/fits.json', 'w'), indent=1)
    elif cmd == 'generate':
        fits = json.load(open(f'{OUT}/fits.json'))
        tr, te = split()
        for m in MODELS:
            g = HGR(tr, prune=MODELS[m]['prune'])
            for seed in range(3):
                c = g.generate(te, fits[m]['params'], seed=100 + seed, name=f'{m}-{seed}')
                pickle.dump(c, open(f'{OUT}/gen_{m}-{seed}.pkl', 'wb'))
                print('generated', m, seed, c.ntok(), flush=True)
    elif cmd == 'phenotype':
        _, te = split()
        qs = sorted({p.quire for p in te.pages})
        jobs = [('V', 'full')] + [('V', q) for q in qs] + [('G', f'{m}-{s}') for m in MODELS for s in range(3)]
        res = {}
        with ProcessPoolExecutor(max_workers=8) as ex:
            for (kind, key), ph in ex.map(_pheno_job, jobs):
                res[f'{kind}:{key}'] = ph
                print(kind, key, 'done', flush=True)
                json.dump(res, open(f'{OUT}/phenotype.json', 'w'), indent=1)
    elif cmd == 'report':
        report()


def report():
    R = json.load(open(f'{OUT}/phenotype.json'))
    V = R['V:full']
    jk = [v for k, v in R.items() if k.startswith('V:') and k != 'V:full']
    G = len(jk)
    out = {}
    lines = []
    for m in MODELS:
        seeds = [R[f'G:{m}-{s}'] for s in range(3) if f'G:{m}-{s}' in R]
        rows = {}
        for k, v in V.items():
            if k == 'T4_peak':
                gv = [s[k] for s in seeds]
                ok = sum(x > 0 for x in gv) <= 1 and v == 0
                rows[k] = {'V': v, 'G': float(np.mean(gv)), 'pass': bool(ok)}
                continue
            vals = [x[k] for x in jk if x.get(k) is not None]
            se = math.sqrt((G - 1) / G * sum((x - np.mean(vals)) ** 2 for x in vals)) if len(vals) > 1 else 0.0
            gv = [s[k] for s in seeds if s.get(k) is not None]
            if v is None or not gv:
                rows[k] = {'V': v, 'G': None, 'pass': None}
                continue
            gm, sd = float(np.mean(gv)), float(np.std(gv, ddof=1)) if len(gv) > 1 else 0.0
            tol = 2 * math.sqrt(se ** 2 + sd ** 2) + 0.01 * abs(v)
            rows[k] = {'V': v, 'G': gm, 'se_V': se, 'sd_G': sd, 'tol': tol, 'pass': abs(gm - v) <= tol}
        npass = sum(1 for r in rows.values() if r['pass'])
        out[m] = {'n_pass': npass, 'n': len(rows), 'rows': rows}
        lines.append(f"{m}: {npass}/{len(rows)} pass; fail: {[k for k, r in rows.items() if r['pass'] is False]}")
    json.dump(out, open(f'{OUT}/report.json', 'w'), indent=1)
    print('\n'.join(lines))
    hdr = f"{'statistic':14s} {'V':>9s} {'tol':>8s} " + ' '.join(f'{m[:10]:>11s}' for m in MODELS)
    print(hdr)
    for k in V:
        r0 = out['HGR']['rows'][k]
        cells = []
        for m in MODELS:
            rr = out[m]['rows'][k]
            g = rr['G']
            cells.append(f"{(g if g is not None else float('nan')):9.4f}{'✓' if rr['pass'] else '✗'} ")
        print(f"{k:14s} {V[k] if V[k] is not None else float('nan'):9.4f} {r0.get('tol', float('nan')):8.4f} " + ' '.join(cells))


if __name__ == '__main__':
    main(sys.argv[1])
