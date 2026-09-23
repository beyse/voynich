"""Post hoc checks run after Stage B (labelled as such in REPORT.md). No new metrics: re-runs and
decompositions of preregistered statistics.

    python3 -m mechanism.posthoc  -> results/mechanism/posthoc.json
"""
import json
import warnings
from collections import Counter, defaultdict

import numpy as np
from scipy.stats import binomtest

from mechanism import controls as K
from mechanism import corpus as C
from mechanism import tests as T
from mechanism.corpus import Corpus, Ln, Pg, certain
from voynich.ivtff import parse

warnings.filterwarnings('ignore', category=RuntimeWarning, message='.*encountered in matmul')


def t5_decomposition(c, seed=0):
    """Consecutive-page excess distances by boundary type (quire only, section only, both, none)."""
    rng = np.random.default_rng(seed)
    by = defaultdict(list)
    for p in c.pages:
        if p.hand and sum(len(l.toks) for l in p.lines) >= 100:
            by[p.hand].append(p)
    out = {}
    for h, ps in sorted(by.items()):
        if len(ps) < 10:
            continue
        E = T._excess_matrix(ps, c.units, rng)
        n = len(ps)
        cons = np.array([E[i, i + 1] for i in range(n - 1)])
        top = set(np.argsort(cons)[::-1][:max(1, len(cons) // 10)].tolist())
        q = [ps[i].quire != ps[i + 1].quire for i in range(n - 1)]
        s = [ps[i].section != ps[i + 1].section for i in range(n - 1)]
        cat = lambda i: 'both' if q[i] and s[i] else ('quire-only' if q[i] else ('section-only' if s[i] else 'none'))
        base = Counter(cat(i) for i in range(n - 1))
        out[h] = {'n_by_type': dict(base), 'top_decile_by_type': dict(Counter(cat(i) for i in top)),
                  'mean_excess_by_type': {k: float(np.mean([cons[i] for i in range(n - 1) if cat(i) == k])) for k in base}}
    return out


def load_it2a():
    pages, order = {}, []
    for ln in parse('data/IT2a-n.txt', comma_is_space=False):
        if ln.kind != 'P':
            continue
        toks = [w for w in ln.words if certain(w)]
        if not toks:
            continue
        if ln.page not in pages:
            m = ln.meta
            pages[ln.page] = Pg(id=ln.page, lines=[], hand=m.get('H'), quire=m.get('Q'), section=m.get('I'), lang=m.get('L'))
            order.append(ln.page)
        pages[ln.page].lines.append(Ln(toks=toks, para_final='<$>' in ln.raw,
                                       eligible=(len(toks) == len(ln.words) and '<->' not in ln.raw)))
    return Corpus('IT2a', [pages[p] for p in order], 'eva', 'V')


def main():
    V = C.load_voynich()
    res = {}
    res['t5_decomposition'] = {'VOYNICH': t5_decomposition(V), 'MK-sec': t5_decomposition(K.mk_sec())}
    res['t7b_without_double_coding'] = T.t7b(V, double_coded_only=False)
    ev = json.load(open('results/mechanism/stageB.json'))['VOYNICH']['t7a']['events']
    pct = [e['logprob_percentile'] for e in ev if e['logprob_percentile'] is not None]
    below = sum(p < 0.5 for p in pct)
    res['t7a_percentile_sign_test'] = {'n': len(pct), 'below_median': below,
                                       'p_two_sided': binomtest(below, len(pct), 0.5).pvalue,
                                       'comment_after_word': sum(e['position'] == 'final' for e in ev),
                                       'types': dict(Counter(e['comment'] for e in ev))}
    IT = load_it2a()
    res['it2a'] = {'tokens': IT.ntok(), 't1': T.t1(IT), 't2a_margin': T.t2a(IT, 'margin'), 't3a': T.t3a(IT),
                   't3b': T.t3b(IT), 't4a_peaks': {k: v['peaks'] for k, v in T.t4a(IT).items()},
                   't4c': {k: v for k, v in T.t4c(IT).items() if k in ('peaks', 'slope_1_8', 'slope_ci95')},
                   't5': T.t5(IT), 't6a': {k: v for k, v in T.t6a(IT).items() if not k.endswith('profile') and k != 'd'},
                   't7b': T.t7b(IT)}
    json.dump(res, open('results/mechanism/posthoc.json', 'w'), indent=1, default=float)
    print(json.dumps({k: v for k, v in res.items() if k != 'it2a'}, indent=1, default=lambda x: round(float(x), 4))[:3000])
    it = res['it2a']
    print('IT2a:', {'T1': round(it['t1']['R_LB'], 3), 'T1se': round(it['t1']['se'], 3), 'T2a': round(it['t2a_margin']['excess'], 4),
                    'T3a': round(it['t3a']['rho'], 3), 'T3b': round(it['t3b']['consistency'], 3), 'T5': round(it['t5']['S_pooled'], 3),
                    'T6a': round(it['t6a']['DI_near'], 3), 'T7b_rec': round(it['t7b']['recurrence_share'], 3),
                    'T7b_slip': round(it['t7b']['slip_share'], 3)})


if __name__ == '__main__':
    main()
