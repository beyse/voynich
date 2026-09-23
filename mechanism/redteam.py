"""Red-team checks of the major claims before writing the paper (all post hoc, labelled as such).

    python3 -m mechanism.redteam   -> results/mechanism/redteam.json
"""
import json
import math
import random
import re
import warnings
from collections import Counter, defaultdict
from concurrent.futures import ProcessPoolExecutor

import numpy as np

from mechanism import corpus as C
from mechanism import tests as T
from mechanism.corpus import Corpus, Ln, Pg

warnings.filterwarnings('ignore', category=RuntimeWarning, message='.*encountered in matmul')


# ---------------------------------------------------------------- C3: margin vs paragraph-final difference

def t2a_difference(c, reps=300, seed=0):
    """Difference of final-form excess (margin-bound minus paragraph-final), page bootstrap of the difference.
    Excess values use 100 label permutations per replicate; bootstrap is over pages (the statistic is a JSD of
    pooled distributions, so page duplication only reweights, it does not create spurious pairs)."""
    rng = np.random.default_rng(seed)
    base_m = T.t2a(c, 'margin', perms=200)['excess']
    base_p = T.t2a(c, 'para', perms=200)['excess']
    diffs = []
    P = len(c.pages)
    for r in range(reps):
        idx = rng.integers(0, P, P)
        sub = Corpus(c.name, [c.pages[i] for i in idx], c.kind, c.gclass)
        diffs.append(T.t2a(sub, 'margin', perms=30, seed=r)['excess'] - T.t2a(sub, 'para', perms=30, seed=r)['excess'])
    return {'margin': base_m, 'para': base_p, 'diff': base_m - base_p,
            'diff_ci95': [float(np.percentile(diffs, 2.5)), float(np.percentile(diffs, 97.5))]}


# ---------------------------------------------------------------- C7: alternative deviance definitions

def recurrence_variants(c, double_coded=False):
    """Recurrence share of deviant types under alternative definitions: n-gram order (2, 3) x block (quire, page)."""
    U = c.units
    out = {}
    for n in (2, 3):
        for block in ('quire', 'page'):
            key = lambda p: p.quire if block == 'quire' else p.id
            grams = defaultdict(Counter)
            seq = defaultdict(list)
            for p in c.pages:
                for l in p.lines:
                    flags = l.dc if (double_coded and l.dc is not None) else [True] * len(l.toks)
                    for t, f in zip(l.toks, flags):
                        u = ('^',) + U(t) + ('$',)
                        g = [tuple(u[i:i + n]) for i in range(len(u) - n + 1)]
                        grams[key(p)].update(g)
                        seq[key(p)].append((t, f, g))
            total = Counter()
            for v in grams.values():
                total.update(v)
            dev_types, rec = 0, 0
            for b, items in seq.items():
                own = grams[b]
                cnt = Counter(t for t, f, g in items if f and any(total[x] - own[x] == 0 for x in g))
                dev_types += len(cnt)
                rec += sum(1 for v in cnt.values() if v >= 2)
            out[f'{n}gram_{block}'] = rec / dev_types if dev_types else None
    return out


# ---------------------------------------------------------------- C1: raw EVA characters (no multigraph merging)

class RawCorpus(Corpus):
    def units(self, tok):
        return tuple(tok)


def raw_version(c):
    return RawCorpus(c.name + '-raw', c.pages, c.kind, c.gclass)


# ---------------------------------------------------------------- per-hand replication

def per_hand(c):
    out = {}
    for h in sorted({p.hand for p in c.pages if p.hand in ('1', '2', '3')}):
        sub = Corpus(f'H{h}', [p for p in c.pages if p.hand == h], 'eva', 'V')
        out[h] = {'pages': len(sub.pages), 'tokens': sub.ntok(), 't3a_rho': T.t3a(sub)['rho'],
                  't3b_cons': T.t3b(sub)['consistency'], 't6a_near': T.t6a(sub, reps=100)['DI_near'],
                  't7b_rec_dc': T.t7b(sub, double_coded_only=True)['recurrence_share'],
                  't2a_margin': T.t2a(sub, 'margin', perms=100)['excess'], 't2a_margin_p': T.t2a(sub, 'margin', perms=100)['p']}
    return out


def per_hand_recurrence_fullref(double_coded=True):
    """Deviance defined against the whole text (other quires), analysis restricted to one hand's tokens."""
    V = C.load_voynich()
    U = V.units
    tri = defaultdict(Counter)
    for p in V.pages:
        for l in p.lines:
            for t in l.toks:
                u = ('^',) + U(t) + ('$',)
                tri[p.quire].update(zip(u, u[1:], u[2:]))
    total = Counter()
    for v in tri.values():
        total.update(v)
    out = {}
    for h in ('1', '2', '3'):
        cnt = defaultdict(Counter)
        n_an = 0
        for p in V.pages:
            if p.hand != h:
                continue
            own = tri[p.quire]
            for l in p.lines:
                flags = l.dc if double_coded else [True] * len(l.toks)
                for t, f in zip(l.toks, flags):
                    if not f:
                        continue
                    n_an += 1
                    u = ('^',) + U(t) + ('$',)
                    if any(total[x] - own[x] == 0 for x in zip(u, u[1:], u[2:])):
                        cnt[p.quire][t] += 1
        types = sum(len(c) for c in cnt.values())
        rec = sum(1 for c in cnt.values() for v in c.values() if v >= 2)
        out[h] = {'analysed': n_an, 'deviant_types': types, 'recurrence_share': rec / types if types else None}
    return out



def _job(name):
    from mechanism import controls as K
    if name == 'VOYNICH':
        c = C.load_voynich()
    elif name == 'GIB':
        c = C.load_gibberish()
    elif name in C.LANGS:
        c = C.load_lang_chunked(name)
    elif name == 'HGR2':
        from mechanism import e5
        c = e5.hgr2_full()
    elif name == 'TS':
        c = K.ts()
    elif name == 'NAIB-run':
        c = K.naib(False)
    else:
        raise ValueError(name)
    r = {'recurrence_variants': recurrence_variants(c, double_coded=(name == 'VOYNICH'))}
    if name == 'VOYNICH':
        r['recurrence_variants_nodc'] = recurrence_variants(c, double_coded=False)
    if name in ('VOYNICH', 'GIB', 'LAT', 'ITA', 'GER', 'ENG'):
        rc = raw_version(c)
        r['raw_t3a'] = T.t3a(rc)['rho']
        r['raw_t3b'] = T.t3b(rc)['consistency']
    return name, r


def main():
    res = {}
    V = C.load_voynich()
    res['t2a_difference'] = {'VOYNICH': t2a_difference(V)}
    S = Corpus('V-stars', [p for p in V.pages if p.section == 'S'], 'eva', 'V')
    res['t2a_stars'] = {'margin': T.t2a(S, 'margin', perms=200), 'para': T.t2a(S, 'para', perms=200)}
    res['per_hand'] = per_hand(V)
    res['per_hand_recurrence_fullref'] = {'dc': per_hand_recurrence_fullref(True), 'nodc': per_hand_recurrence_fullref(False)}
    with ProcessPoolExecutor(max_workers=8) as ex:
        for name, r in ex.map(_job, ['VOYNICH', 'GIB', 'LAT', 'ITA', 'GER', 'ENG', 'HGR2', 'TS', 'NAIB-run']):
            res[name] = r
            print(name, json.dumps(r, default=lambda x: round(x, 4))[:400], flush=True)
    json.dump(res, open('results/mechanism/redteam.json', 'w'), indent=1, default=float)
    print('t2a difference', res['t2a_difference'])
    print('stars', {k: (round(v['excess'], 4), v['p'], v['n_final']) for k, v in res['t2a_stars'].items()})
    print('per hand', json.dumps(res['per_hand'], default=lambda x: round(x, 4)))


if __name__ == '__main__':
    main()
