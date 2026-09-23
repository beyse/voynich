"""Revision analyses R1-R3 (mechanism/REVISION_PLAN.md).

    python3 -m mechanism.revision fetch   # Greshko's published Naibbe data -> data/ref/naibbe_greshko/
    python3 -m mechanism.revision r1      # human gibberish per writer (post hoc)
    python3 -m mechanism.revision r2      # Naibbe reimplementation against the author's output
    python3 -m mechanism.revision r3      # Naibbe exclusion statistics on the author's output
Results go to results/mechanism/revision/.
"""
import json
import math
import os
import random
import sys
import urllib.request
import warnings
from collections import Counter

import numpy as np

from mechanism import corpus as C
from mechanism import tests as T

warnings.filterwarnings('ignore', category=RuntimeWarning)
OUT = 'results/mechanism/revision'
GRESHKO_COMMIT = 'f2675ec5dd275268bc64dd48ea64fc0e0e9827a2'
GRESHKO_FILES = ['encrypted/nathist_output_ciphertext.txt', 'encrypted/nathist_output_ciphertext_respaced.txt',
                 'respaced_plaintext/nathist_pre_encryption_respaced_plaintext.txt', 'references/naibbe_tables.csv']
GDIR = 'data/ref/naibbe_greshko'
TABLES = ['alpha', 'beta1', 'beta2', 'beta3', 'gamma1', 'gamma2']
DECK = {'alpha': 20, 'beta1': 8, 'beta2': 8, 'beta3': 8, 'gamma1': 4, 'gamma2': 4}


def save(name, obj):
    os.makedirs(OUT, exist_ok=True)
    json.dump(obj, open(f'{OUT}/{name}.json', 'w'), indent=1, default=float)


# ------------------------------------------------------------------ fetch

def fetch():
    os.makedirs(GDIR, exist_ok=True)
    base = f'https://raw.githubusercontent.com/greshko/naibbe-cipher/{GRESHKO_COMMIT}/'
    for f in GRESHKO_FILES:
        dst = os.path.join(GDIR, os.path.basename(f))
        if not os.path.exists(dst):
            urllib.request.urlretrieve(base + f, dst)
        print(f, os.path.getsize(dst))


# ------------------------------------------------------------------ R1: gibberish per writer

def _t3a_lines(lines, U):
    A = T._bigram_counts(lines[0::2], U)
    B = T._bigram_counts(lines[1::2], U)
    o1, e1, _ = T._zero_rep(A, B, 3)
    o2, e2, _ = T._zero_rep(B, A, 3)
    return (o1 + o2) / (e1 + e2) if e1 + e2 else float('nan')


def _voynich_windows(V, n, k, rng):
    """k windows of contiguous lines within one hand, each with at least n tokens."""
    byhand = {}
    for p in V.pages:
        byhand.setdefault(p.hand, []).extend(p.lines)
    seqs = [ls for ls in byhand.values() if sum(len(l.toks) for l in ls) >= 3 * n]
    out = []
    while len(out) < k:
        ls = rng.choice(seqs)
        i = rng.randrange(len(ls))
        win, m = [], 0
        while i < len(ls) and m < n:
            win.append(ls[i])
            m += len(ls[i].toks)
            i += 1
        if m >= n:
            out.append(win)
    return out


def r1(k=50):
    G, V = C.load_gibberish(), C.load_voynich()
    rng = random.Random(0)
    rows = []
    for p in G.pages:
        n = sum(len(l.toks) for l in p.lines)
        if n < 150:
            continue
        g_cons = T.slot_rigidity(p.lines, G.units, random.Random(0))
        g_rho = _t3a_lines(p.lines, G.units)
        wins = _voynich_windows(V, n, k, rng)
        v_cons = [r['consistency'] for r in (T.slot_rigidity(w, V.units, random.Random(0)) for w in wins) if r]
        v_rho = [x for x in (_t3a_lines(w, V.units) for w in wins) if x == x]
        rows.append({'writer': p.id, 'tokens': n,
                     't3b': g_cons['consistency'] if g_cons else None,
                     't3b_pct': float(np.mean([x <= g_cons['consistency'] for x in v_cons])) if g_cons else None,
                     'v_t3b_median': float(np.median(v_cons)), 'v_t3b_p05': float(np.percentile(v_cons, 5)),
                     't3a': g_rho, 't3a_pct_ge': float(np.mean([x >= g_rho for x in v_rho])) if g_rho == g_rho else None,
                     'v_t3a_median': float(np.median(v_rho))})
        print(rows[-1], flush=True)
    scored = [r for r in rows if r['t3b'] is not None]
    below = sum(r['t3b_pct'] < 0.05 for r in scored)
    share = below / len(scored)
    verdict = 'supported' if share >= 0.90 else ('weakened' if share < 0.75 else 'partial')
    res = {'writers': rows, 'n_writers': len(scored), 'below_p05': below, 'share_below_p05': share,
           'verdict': verdict, 'writer_t3b': {'min': min(r['t3b'] for r in scored), 'median': float(np.median([r['t3b'] for r in scored])),
                                               'max': max(r['t3b'] for r in scored)},
           'label': 'post hoc (REVISION_PLAN.md R1)'}
    save('r1', res)
    print({k: v for k, v in res.items() if k != 'writers'})


# ------------------------------------------------------------------ R2: validation of the Naibbe reimplementation

def _tables():
    import csv
    out = {}
    with open(os.path.join(GDIR, 'naibbe_tables.csv'), encoding='utf-8-sig', newline='') as fh:
        for row in csv.DictReader(fh):
            out[row['code'].strip()] = row['glyphs'].strip()
    return out


def _read_tokens(name):
    return open(os.path.join(GDIR, name), encoding='utf-8').read().split()


def _em_shares(obs, iters=200):
    """MLE of table shares from sets of consistent (t1[, t2]) assignments; obs: list of lists of tuples."""
    pi = {t: 1 / len(TABLES) for t in TABLES}
    for _ in range(iters):
        acc = Counter()
        for cands in obs:
            w = [math.prod(pi[t] for t in c) for c in cands]
            z = sum(w)
            for c, x in zip(cands, w):
                for t in c:
                    acc[t] += x / z
        tot = sum(acc.values())
        pi = {t: acc[t] / tot for t in TABLES}
    return pi


def _shape(tokens, name):
    from voynich import generators as Gn
    return C.with_vmeta(name, list(Gn.pages.keys()), Gn.chunk(tokens), 'eva', 'C')


def _stats8(tokens, name):
    from voynich.battery import battery
    from mechanism import e2 as E2
    c = _shape(tokens, name)
    b = battery(E2.to_lists(c), name)
    words = [w for p in c.pages for l in p.lines for w in l.toks]
    t3c = T.t3c(c)
    return {'hapax': b['hapax'], 'types': float(b['types']), 'wlen': float(np.mean([len(w) for w in words])),
            'h2': b['h2'], 'edge_mi': b['edge_mi'], 'token_mi': b['token_mi'], 'T3c_e1': t3c['e1'], 'T3c_s1': t3c['s1']}


def _encipher_tokens(ptoks, tables, seed, removal=0.03):
    from voynich import generators as Gn
    rng = random.Random(seed)
    deck = Gn._Deck(rng)
    out = []
    for tok in ptoks:
        try:
            if len(tok) == 1:
                out.append(tables[f'unigram_{deck.draw()}_{tok}'])
            elif len(tok) == 2:
                out.append(tables[f'prefix_{deck.draw()}_{tok[0]}'] + tables[f'suffix_{deck.draw()}_{tok[1]}'])
        except KeyError:        # letter outside the cipher alphabet: skipped, as it cannot be enciphered
            continue
    merged = [out[0]]
    for w in out[1:]:
        if rng.random() < removal:
            merged[-1] += w
        else:
            merged.append(w)
    return merged


def r2():
    tab = _tables()
    P = _read_tokens('nathist_pre_encryption_respaced_plaintext.txt')
    C0 = _read_tokens('nathist_output_ciphertext.txt')
    C1 = _read_tokens('nathist_output_ciphertext_respaced.txt')
    res = {'tokens': {'plaintext': len(P), 'cipher_before_removal': len(C0), 'cipher_final': len(C1)}}
    # R2a tokenisation
    uni = sum(len(t) == 1 for t in P) / len(P)
    res['R2a'] = {'unigram_share': uni, 'expected': 17 / 36, 'pass': abs(uni - 17 / 36) <= 0.02}
    # R2b mapping, R2c table usage
    valid, unamb, obs = 0, Counter(), []
    n = min(len(P), len(C0))
    for p, c in zip(P[:n], C0[:n]):
        if len(p) == 1:
            cands = [(t,) for t in TABLES if tab.get(f'unigram_{t}_{p}') == c]
        elif len(p) == 2:
            cands = [(t1, t2) for t1 in TABLES for t2 in TABLES
                     if tab.get(f'prefix_{t1}_{p[0]}') is not None and tab.get(f'suffix_{t2}_{p[1]}') is not None
                     and tab[f'prefix_{t1}_{p[0]}'] + tab[f'suffix_{t2}_{p[1]}'] == c]
        else:
            cands = []
        if cands:
            valid += 1
            obs.append(cands)
            if len(cands) == 1:
                unamb.update(cands[0])
    res['R2b'] = {'aligned': n, 'valid': valid, 'share_valid': valid / n, 'pass': valid / n >= 0.99}
    tot = sum(unamb.values())
    shares = {t: unamb[t] / tot for t in TABLES}
    expect = {t: DECK[t] / 52 for t in TABLES}
    res['R2c'] = {'unambiguous_cards': tot, 'shares': shares, 'expected': expect,
                  'pass': all(abs(shares[t] - expect[t]) <= 0.03 for t in TABLES),
                  'em_shares_secondary': _em_shares(obs)}
    # R2d statistics at identical tokenisation
    his = _stats8(C1, 'NAIB-greshko')
    ours = [_stats8(_encipher_tokens(P, tab, seed), f'NAIB-ours-{seed}') for seed in range(5)]
    rows, npass = {}, 0
    for k in his:
        xs = np.array([o[k] for o in ours], float)
        m, sd = float(xs.mean()), float(xs.std(ddof=1))
        ok = abs(his[k] - m) <= 2 * sd + 0.01 * abs(m)
        npass += ok
        rows[k] = {'author': his[k], 'ours_mean': m, 'ours_sd': sd, 'pass': bool(ok)}
    res['R2d'] = {'rows': rows, 'n_pass': npass, 'n': len(rows)}
    res['validated'] = bool(res['R2a']['pass'] and res['R2b']['pass'] and res['R2c']['pass'] and npass >= 6)
    save('r2', res)
    print(json.dumps({k: v for k, v in res.items() if k != 'R2d'}, indent=1, default=float))
    for k, r in rows.items():
        print(k, r)


# ------------------------------------------------------------------ R3: exclusion statistics on the author's output

def r3():
    from voynich.battery import battery
    from mechanism import e2 as E2
    from mechanism import e4 as E4
    from mechanism import e5 as E5
    c = _shape(_read_tokens('nathist_output_ciphertext_respaced.txt'), 'NAIB-greshko')
    b = battery(E2.to_lists(c), c.name)
    t6 = T.t6a(c)
    res = {'pages': len(c.pages), 'tokens': c.ntok(),
           'T6a_near': t6['DI_near'], 'T6a_exact': t6['DI_exact'],
           'E4': E4.stats(c), 'edge_mi': b['edge_mi'], 'hapax': b['hapax'], 'page_mi': b['page_mi'],
           'T7b_rec': T.t7b(c, double_coded_only=False)['recurrence_share'], 'E5_descriptive': E5.stats(c)}
    # reference values: Voynich and our reimplementation (running text)
    A = json.load(open('results/mechanism/stageA.json'))
    B = json.load(open('results/mechanism/stageB.json'))['VOYNICH']
    E4A = json.load(open('results/mechanism/e4_stageA.json'))
    N = json.load(open('paper/numbers.json'))
    V = C.load_voynich()
    # Voynich page MI with a leave-one-quire-out jackknife (the profile reports no interval for it)
    quires = sorted({str(p.quire) for p in V.pages})
    full = battery(E2.to_lists(V), 'V')['page_mi']
    jk = []
    for q in quires:
        sub = C.Corpus('V', [p for p in V.pages if str(p.quire) != q], 'eva', 'V')
        jk.append(battery(E2.to_lists(sub), 'V')['page_mi'])
    m = float(np.mean(jk))
    se = math.sqrt((len(jk) - 1) / len(jk) * sum((x - m) ** 2 for x in jk))
    ref = {'voynich': {'T6a_near': B['t6a']['DI_near'], 'T6a_near_ci95': B['t6a']['DI_near_ci95'],
                       'edge_mi': N['jack']['point']['edge_mi'], 'edge_mi_ci95': N['jack']['ci95']['edge_mi'],
                       'page_mi': full, 'page_mi_ci95': [full - 1.96 * se, full + 1.96 * se]},
           'ours_run': {'T6a_near': A['NAIB-run']['t6a']['DI_near'], 'edge_mi': N['mech']['naibbe running']['edge_mi'],
                        'page_mi': N['mech']['naibbe running']['page_mi'], 'hapax': N['mech']['naibbe running']['hapax'],
                        'E4': {k: E4A['NAIB-run'][k] for k in ('L', 'S')}, 'T7b_rec': A['NAIB-run']['t7b']['recurrence_share']}}
    crit = {}
    for k in ('T6a_near', 'edge_mi', 'page_mi'):
        v, lo, hi = ref['voynich'][k], ref['voynich'][k + '_ci95'][0], ref['voynich'][k + '_ci95'][1]
        same_side = (res[k] - v) * (ref['ours_run'][k] - v) > 0
        outside = res[k] < lo or res[k] > hi
        crit[k] = {'author': res[k], 'voynich': v, 'ours': ref['ours_run'][k], 'same_side': bool(same_side),
                   'outside_voynich_ci': bool(outside), 'pass': bool(same_side and outside)}
    res['reference'] = ref
    res['criterion'] = crit
    res['exclusion_holds'] = all(x['pass'] for x in crit.values())
    save('r3', res)
    print(json.dumps(crit, indent=1, default=float), 'exclusion_holds:', res['exclusion_holds'])


if __name__ == '__main__':
    {'fetch': fetch, 'r1': r1, 'r2': r2, 'r3': r3}[sys.argv[1]]()
