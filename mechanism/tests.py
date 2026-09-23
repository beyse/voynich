"""Tests T1-T7 of mechanism/PREREG.md. Each function takes a Corpus and returns a JSON-serialisable dict."""
import math
import random
import re
from collections import Counter, defaultdict

import numpy as np

# ------------------------------------------------------------------ helpers


def mi(pairs):
    n = len(pairs)
    if n == 0:
        return 0.0
    pab = Counter(pairs)
    pa = Counter(a for a, _ in pairs)
    pb = Counter(b for _, b in pairs)
    return sum(c / n * math.log2(c * n / (pa[a] * pb[b])) for (a, b), c in pab.items())


def excess_mi(pairs, rng, reps=20):
    a = [p[0] for p in pairs]
    b = [p[1] for p in pairs]
    null = []
    for _ in range(reps):
        bb = b[:]
        rng.shuffle(bb)
        null.append(mi(list(zip(a, bb))))
    return mi(pairs) - float(np.mean(null))


def jackknife(groups, f):
    """Leave-one-group-out jackknife of statistic f(list of kept group keys)."""
    keys = sorted(groups)
    full = f(keys)
    vals = [f([k for k in keys if k != g]) for g in keys]
    G = len(vals)
    m = float(np.mean(vals))
    se = math.sqrt((G - 1) / G * sum((v - m) ** 2 for v in vals)) if G > 1 else float('nan')
    return full, se


def group_of(c, p):
    return p.quire


def ed1_pairs(types, units):
    """Ordered pairs (i, j) of type indices at unit edit distance exactly 1."""
    U = [units(t) for t in types]
    idx = {u: i for i, u in enumerate(U)}
    sub = defaultdict(list)
    out = set()
    for i, u in enumerate(U):
        for k in range(len(u)):
            d = u[:k] + u[k + 1:]
            sub[(k, d)].append(i)
            j = idx.get(d)
            if j is not None:
                out.add((i, j))
                out.add((j, i))
    for lst in sub.values():
        if len(lst) > 1:
            for a in lst:
                for b in lst:
                    if a != b:
                        out.add((a, b))
    return out


def gini(x):
    x = np.sort(np.clip(np.asarray(x, float), 0, None))
    if x.sum() == 0:
        return 0.0
    n = len(x)
    return float((2 * np.arange(1, n + 1) - n - 1).dot(x) / (n * x.sum()))


# ------------------------------------------------------------------ T1 line-break transparency


def _codes(pairs):
    A = {}
    B = {}
    a = np.array([A.setdefault(x, len(A)) for x, _ in pairs], dtype=np.int64)
    b = np.array([B.setdefault(y, len(B)) for _, y in pairs], dtype=np.int64)
    return a, b, len(A), len(B)


def _mi_codes(a, b, na, nb):
    n = len(a)
    J = np.bincount(a * nb + b, minlength=na * nb).astype(float)
    pa = np.bincount(a, minlength=na).astype(float)
    pb = np.bincount(b, minlength=nb).astype(float)
    nz = J > 0
    ia, ib = np.divmod(np.nonzero(nz)[0], nb)
    j = J[nz]
    return float(np.sum(j / n * np.log2(j * n / (pa[ia] * pb[ib]))))


def excess_mi_fast(pairs, rng, reps=500, pages=None):
    """Plug-in MI minus the mean plug-in MI of `reps` random re-pairings (numpy).
    With `pages`, re-pairing is restricted to pairs from the same page (DEVIATIONS.md, entry 5)."""
    if len(pairs) < 2:
        return float('nan')
    a, b, na, nb = _codes(pairs)
    obs = _mi_codes(a, b, na, nb)
    n = len(a)
    if pages is None:
        null = [_mi_codes(a, rng.permutation(b), na, nb) for _ in range(reps)]
    else:
        pg = np.asarray(pages)
        order = np.argsort(pg, kind='stable')
        spg = pg[order]
        null = []
        for _ in range(reps):
            perm = np.lexsort((rng.random(n), spg))
            bb = b.copy()
            bb[order] = b[order[perm]]
            null.append(_mi_codes(a, bb, na, nb))
    return obs - float(np.mean(null))


def _page_excess(pairs, rng, reps):
    """Excess plug-in MI of one page's pairs over re-pairing within that page; returns (excess, n)."""
    n = len(pairs)
    if n < 2:
        return 0.0, 0
    a, b, na, nb = _codes(pairs)
    obs = _mi_codes(a, b, na, nb)
    null = np.mean([_mi_codes(a, rng.permutation(b), na, nb) for _ in range(reps)])
    return obs - float(null), n


def t1(c, seed=0, drop_hyph=False, reps=200):
    """R_LB as the ratio of page-conditional excess MIs (DEVIATIONS.md, entries 4-6).

    Break coupling: per page, excess MI of (last unit of line n, first unit of line n+1) over re-pairing within
    the page, averaged over pages with weights n_p. Within-line coupling: per page, the within-line pairs in
    text order are cut into consecutive blocks of the page's number of break pairs; block excesses are averaged
    within the page and pages are weighted by their number of break pairs (equal numbers of pairs per page)."""
    U = c.units
    pages = []
    for p in c.pages:
        W, B = [], []
        for i, l in enumerate(p.lines):
            W.extend((U(a)[-1], U(b)[0]) for a, b in zip(l.toks, l.toks[1:]))
            if i + 1 < len(p.lines) and not (drop_hyph and l.hyph):
                B.append((U(l.toks[-1])[-1], U(p.lines[i + 1].toks[0])[0]))
        pages.append((group_of(c, p), W, B))
    rng = np.random.default_rng(seed)
    per = []
    for g, W, B in pages:
        k = len(B)
        if k < 2 or len(W) < k:
            continue
        eb, _ = _page_excess(B, rng, reps)
        blocks = [W[i:i + k] for i in range(0, len(W) - k + 1, k)]
        ew = float(np.mean([_page_excess(bl, rng, reps)[0] for bl in blocks]))
        per.append((g, k, eb, ew))
    groups = defaultdict(list)
    for row in per:
        groups[row[0]].append(row)

    def stat(keys):
        rows = [r for kk in keys for r in groups[kk]]
        w = np.array([r[1] for r in rows], float)
        eb = float(np.dot(w, [r[2] for r in rows]) / w.sum())
        ew = float(np.dot(w, [r[3] for r in rows]) / w.sum())
        return (eb / ew if ew > 0 else float('nan')), eb, ew

    full = stat(sorted(groups))
    R, se = jackknife(groups, lambda keys: stat(keys)[0])
    return {'R_LB': R, 'se': se, 'excess_break': full[1], 'excess_within': full[2],
            'n_break': int(sum(r[1] for r in per)), 'pages': len(per), 'groups': len(groups)}


# ------------------------------------------------------------------ T2 line-end behaviour


def _jsd(p, q):
    keys = set(p) | set(q)
    m = {k: 0.5 * (p.get(k, 0) + q.get(k, 0)) for k in keys}
    f = lambda a: sum(v * math.log2(v / m[k]) for k, v in a.items() if v > 0)
    return 0.5 * f(p) + 0.5 * f(q)


def t2a(c, which, seed=0, perms=200):
    """which: 'margin' (para_final False) or 'para' (para_final True)."""
    rng = random.Random(seed)
    U = c.units
    strata = defaultdict(list)   # stratum -> list of (is_final, last_unit)
    for p in c.pages:
        for l in p.lines:
            if len(l.toks) < 2:
                continue
            want = (l.para_final is True) if which == 'para' else (l.para_final is False)
            for t in l.toks[1:-1]:
                u = U(t)
                strata[min(len(u), 8)].append((False, u[-1]))
            if want:
                u = U(l.toks[-1])
                strata[min(len(u), 8)].append((True, u[-1]))

    def jsd_of(st):
        nfin = sum(1 for v in st.values() for f, _ in v if f)
        if nfin == 0:
            return float('nan'), 0
        pf, pi = Counter(), Counter()
        for s, v in st.items():
            fin = [u for f, u in v if f]
            inn = [u for f, u in v if not f]
            if not fin or not inn:
                continue
            w = len(fin) / nfin
            for u in fin:
                pf[u] += 1 / nfin
            for u, k in Counter(inn).items():
                pi[u] += w * k / len(inn)
        z = sum(pf.values())
        pf = {k: v / z for k, v in pf.items()}
        z = sum(pi.values())
        pi = {k: v / z for k, v in pi.items()}
        return _jsd(pf, pi), nfin

    obs, nfin = jsd_of(strata)
    null = []
    for _ in range(perms):
        st2 = {}
        for s, v in strata.items():
            labels = [f for f, _ in v]
            rng.shuffle(labels)
            st2[s] = [(f, u) for f, (_, u) in zip(labels, v)]
        null.append(jsd_of(st2)[0])
    fin_len = [min(len(U(l.toks[-1])), 99) for p in c.pages for l in p.lines if len(l.toks) >= 2 and
               ((l.para_final is True) if which == 'para' else (l.para_final is False))]
    int_len = [len(U(t)) for p in c.pages for l in p.lines for t in l.toks[1:-1]]
    return {'jsd': obs, 'null_mean': float(np.mean(null)), 'excess': obs - float(np.mean(null)),
            'p': (1 + sum(x >= obs for x in null)) / (1 + perms), 'n_final': nfin,
            'mean_len_final': float(np.mean(fin_len)) if fin_len else None,
            'mean_len_internal': float(np.mean(int_len)) if int_len else None}


def _line_len(toks, U):
    return sum(len(U(t)) for t in toks) + len(toks) - 1


def _slack(lengths, q=90):
    W = float(np.percentile(lengths, q))
    return W, [max(0.0, W - L) for L in lengths]


def t2b(c, pages_filter, seed=0, sims=200, drop_hyph=False):
    rng = random.Random(seed)
    U = c.units
    per_page = []
    for p in c.pages:
        if not pages_filter(p):
            continue
        lines = [l for l in p.lines if l.eligible and l.para_final is False and not (drop_hyph and l.hyph)]
        if len(lines) < 8:
            continue
        lengths = [_line_len(l.toks, U) for l in lines]
        W, sl = _slack(lengths)
        toks = [t for l in lines for t in l.toks]
        sim_means = []
        for _ in range(sims):
            tt = toks[:]
            rng.shuffle(tt)
            packed, cur, cl = [], [], 0
            for t in tt:
                lt = len(U(t))
                add = lt if not cur else lt + 1
                if cur and cl + add > W:
                    packed.append(cl)
                    cur, cl = [t], lt
                else:
                    cur.append(t)
                    cl += add
            if len(packed) < 2:
                continue
            _, s2 = _slack(packed)
            sim_means.append(float(np.mean(s2)))
        per_page.append((sum(sl), len(sl), float(np.mean(sim_means)), W))
    if not per_page:
        return {'T': None, 'pages': 0}
    arr = np.array(per_page)

    def T(a):
        return a[:, 0].sum() / (a[:, 2] * a[:, 1]).sum()

    boots = [T(arr[np.random.default_rng(seed + b).integers(0, len(arr), len(arr))]) for b in range(1000)]
    return {'T': float(T(arr)), 'ci95': [float(np.percentile(boots, 2.5)), float(np.percentile(boots, 97.5))],
            'pages': len(arr), 'lines': int(arr[:, 1].sum()), 'mean_W': float(arr[:, 3].mean()),
            'obs_mean_slack': float(arr[:, 0].sum() / arr[:, 1].sum()),
            'sim_mean_slack': float((arr[:, 2] * arr[:, 1]).sum() / arr[:, 1].sum())}


def t2c(c, seed=0, perms=200):
    rng = random.Random(seed)

    def count(lines):
        e1 = e2 = n1 = n2 = 0
        for a, b in zip(lines, lines[1:]):
            n1 += 1
            e1 += a.toks[-1] == b.toks[0]
            if len(a.toks) >= 2 and len(b.toks) >= 2:
                n2 += 1
                e2 += a.toks[-2:] == b.toks[:2]
        return e1, e2, n1, n2

    obs = np.array([0, 0, 0, 0])
    for p in c.pages:
        obs += np.array(count(p.lines))
    null = []
    for _ in range(perms):
        s = np.array([0, 0, 0, 0])
        for p in c.pages:
            ls = p.lines[:]
            rng.shuffle(ls)
            s += np.array(count(ls))
        null.append(s)
    null = np.array(null)
    r1 = obs[0] / obs[2]
    r2 = obs[1] / obs[3] if obs[3] else 0
    n1 = null[:, 0] / null[:, 2]
    n2 = null[:, 1] / np.maximum(null[:, 3], 1)
    return {'rate_tok': float(r1), 'null_tok': float(n1.mean()), 'ratio_tok': float(r1 / n1.mean()) if n1.mean() else None,
            'p_tok_excess': float((1 + (n1 >= r1).sum()) / (1 + perms)),
            'rate_big': float(r2), 'null_big': float(n2.mean()), 'count_big': int(obs[1]),
            'p_big_excess': float((1 + (n2 >= r2).sum()) / (1 + perms)), 'pairs': int(obs[2])}


# ------------------------------------------------------------------ T3 hard constraints, rigidity, positional entropy


def chunks(c, size=250, min_doc=150):
    """Units of analysis for the matched-size versions: 250-token chunks within a hand (or document)."""
    if c.name == 'GIB':
        return [[l for l in p.lines] for p in c.pages if sum(len(l.toks) for l in p.lines) >= min_doc]
    byhand = defaultdict(list)
    for p in c.pages:
        byhand[p.hand].append(p)
    out = []
    for h, ps in byhand.items():
        cur, n = [], 0
        for p in ps:
            for l in p.lines:
                cur.append(l)
                n += len(l.toks)
                if n >= size:
                    out.append(cur)
                    cur, n = [], 0
    return out


def _bigram_counts(lines, U):
    N = Counter()
    for l in lines:
        for t in l.toks:
            u = ('^',) + U(t) + ('$',)
            for a, b in zip(u, u[1:]):
                N[a, b] += 1
    return N


def _indep(N):
    R, C = Counter(), Counter()
    for (a, b), k in N.items():
        R[a] += k
        C[b] += k
    return R, C, sum(N.values())


def _zero_rep(A, B, tau):
    """Candidate cells: zero in A with independence expectation >= tau; returns (obs in B, expected in B, cells)."""
    Ra, Ca, na = _indep(A)
    Rb, Cb, nb = _indep(B)
    O = E = 0.0
    cells = 0
    for a in Ra:
        for b in Ca:
            if a == '^' and b == '$':
                continue
            if A.get((a, b), 0) == 0 and Ra[a] * Ca[b] / na >= tau:
                cells += 1
                O += B.get((a, b), 0)
                E += Rb.get(a, 0) * Cb.get(b, 0) / nb if nb else 0
    return O, E, cells


def t3a(c, seed=0):
    U = c.units
    res = []
    for ch in chunks(c):
        A = _bigram_counts(ch[0::2], U)
        B = _bigram_counts(ch[1::2], U)
        o1, e1, c1 = _zero_rep(A, B, 3)
        o2, e2, c2 = _zero_rep(B, A, 3)
        res.append((o1 + o2, e1 + e2, c1 + c2))
    arr = np.array(res)
    rho = arr[:, 0].sum() / arr[:, 1].sum() if arr[:, 1].sum() else float('nan')
    rng = np.random.default_rng(seed)
    boots = []
    for _ in range(1000):
        s = arr[rng.integers(0, len(arr), len(arr))]
        boots.append(s[:, 0].sum() / s[:, 1].sum() if s[:, 1].sum() else np.nan)
    return {'rho': float(rho), 'ci95': [float(np.nanpercentile(boots, 2.5)), float(np.nanpercentile(boots, 97.5))],
            'chunks': len(arr), 'cells': int(arr[:, 2].sum()), 'obs': float(arr[:, 0].sum()), 'exp': float(arr[:, 1].sum())}


def t3a_full(c, hand=None):
    U = c.units
    lines = [l for p in c.pages if hand is None or p.hand == hand for l in p.lines]
    A = _bigram_counts(lines[0::2], U)
    B = _bigram_counts(lines[1::2], U)
    o1, e1, c1 = _zero_rep(A, B, 5)
    o2, e2, c2 = _zero_rep(B, A, 5)
    return {'rho': (o1 + o2) / (e1 + e2) if e1 + e2 else None, 'cells': c1 + c2, 'obs': o1 + o2, 'exp': e1 + e2,
            'tokens': sum(len(l.toks) for l in lines)}


def slot_rigidity(lines, U, rng, min_occ=5):
    cnt = Counter(u for l in lines for t in l.toks for u in U(t))
    inv = [u for u, k in cnt.items() if k >= min_occ]
    ix = {u: i for i, u in enumerate(inv)}
    n = len(inv)
    Wm = np.zeros((n, n))
    toks = []
    relpos = defaultdict(list)
    for l in lines:
        for t in l.toks:
            u = U(t)
            if len(u) < 2 or any(x not in ix for x in u):
                continue
            toks.append(u)
            for i in range(len(u)):
                relpos[u[i]].append(i / (len(u) - 1))
                for j in range(i + 1, len(u)):
                    if u[i] != u[j]:
                        Wm[ix[u[i]], ix[u[j]]] += 1
    total = Wm.sum()
    if total == 0 or not toks:
        return None
    init = sorted(range(n), key=lambda i: np.mean(relpos[inv[i]]) if relpos[inv[i]] else 0.5)
    # local search from the mean-relative-position order plus 20 random restarts
    order, s = _best_order_from(Wm, init, rng)
    rank = {inv[i]: r for r, i in enumerate(order)}
    mono = sum(all(rank[a] <= rank[b] for a, b in zip(u, u[1:])) for u in toks) / len(toks)
    return {'consistency': s / total, 'monotone': mono, 'units': n, 'tokens': len(toks)}


def _best_order_from(Wm, init, rng, restarts=20):
    n = Wm.shape[0]
    best_o, best_s = None, -1

    def score(order):
        o = np.array(order)
        return np.triu(Wm[np.ix_(o, o)], 1).sum()

    for st in [init] + [rng.sample(range(n), n) for _ in range(restarts)]:
        order = list(st)
        cur = score(order)
        changed = True
        while changed:
            changed = False
            for u in list(order):
                s = [x for x in order if x != u]
                a = Wm[s, u]
                b = Wm[u, s]
                ca = np.concatenate([[0], np.cumsum(a)])
                cb = np.concatenate([[0], np.cumsum(b)])
                contrib = ca + (cb[-1] - cb)
                k = int(np.argmax(contrib))
                new = s[:k] + [u] + s[k:]
                sc = score(new)
                if sc > cur + 1e-9:
                    order, cur, changed = new, sc, True
        if cur > best_s:
            best_o, best_s = order, cur
    return best_o, best_s


def t3b(c, seed=0):
    rng = random.Random(seed)
    vals = [slot_rigidity(ch, c.units, rng) for ch in chunks(c)]
    vals = [v for v in vals if v]
    cons = np.array([v['consistency'] for v in vals])
    mono = np.array([v['monotone'] for v in vals])
    g = np.random.default_rng(seed)
    bc = [cons[g.integers(0, len(cons), len(cons))].mean() for _ in range(1000)]
    bm = [mono[g.integers(0, len(mono), len(mono))].mean() for _ in range(1000)]
    return {'consistency': float(cons.mean()), 'cons_ci95': [float(np.percentile(bc, 2.5)), float(np.percentile(bc, 97.5))],
            'monotone': float(mono.mean()), 'mono_ci95': [float(np.percentile(bm, 2.5)), float(np.percentile(bm, 97.5))],
            'chunks': len(vals)}


def t3c(c):
    U = c.units
    allu = Counter()
    pos = defaultdict(Counter)
    for p in c.pages:
        for l in p.lines:
            for t in l.toks:
                u = U(t)
                allu.update(u)
                for k in range(min(3, len(u))):
                    pos['s%d' % (k + 1)][u[k]] += 1
                    pos['e%d' % (k + 1)][u[-1 - k]] += 1
    H = lambda C: -sum(v / sum(C.values()) * math.log2(v / sum(C.values())) for v in C.values())
    h = H(allu)
    return {'H_unit': h, **{k: H(v) / h for k, v in sorted(pos.items())}}


# ------------------------------------------------------------------ T4 periodicity (and T6b)


def _page_boot(npages, reps, seed):
    g = np.random.default_rng(seed)
    return [g.integers(0, npages, npages) for _ in range(reps)]


def t4a(c, seed=0, lags=range(2, 9), reps=200):
    """Per page arrays of observed match counts and exact within-line permutation expectations."""
    U = c.units
    feats = {'final': lambda t: U(t)[-1], 'initial': lambda t: U(t)[0]}
    out = {}
    for fname, f in feats.items():
        obs = np.zeros((len(c.pages), max(lags) + 1))
        exp = np.zeros_like(obs)
        for pi, p in enumerate(c.pages):
            for l in p.lines:
                x = [f(t) for t in l.toks]
                n = len(x)
                if n < 3:
                    continue
                cnt = Counter(x)
                pl = sum(k * (k - 1) for k in cnt.values()) / (n * (n - 1))
                for k in lags:
                    if n > k:
                        obs[pi, k] += sum(x[i] == x[i + k] for i in range(n - k))
                        exp[pi, k] += (n - k) * pl
        ks = list(lags)
        ratio = lambda idx: obs[idx][:, ks].sum(0) / exp[idx][:, ks].sum(0)
        full = ratio(np.arange(len(c.pages)))
        boots = np.array([ratio(b) for b in _page_boot(len(c.pages), reps, seed)])
        se = boots.std(0)
        out[fname] = {'lags': ks, 'ratio': full.tolist(), 'se': se.tolist(),
                      'peaks': _peaks(ks, full, boots)}
    return out


def _peaks(ks, full, boots, zcrit=3.0):
    """Local maxima exceeding both neighbours and the null (ratio 1) by zcrit bootstrap standard errors."""
    peaks = []
    for i in range(1, len(ks) - 1):
        z0 = (full[i] - 1) / (boots[:, i].std() or np.inf)
        dl = boots[:, i] - boots[:, i - 1]
        dr = boots[:, i] - boots[:, i + 1]
        zl = (full[i] - full[i - 1]) / (dl.std() or np.inf)
        zr = (full[i] - full[i + 1]) / (dr.std() or np.inf)
        if z0 > zcrit and zl > zcrit and zr > zcrit:
            peaks.append({'k': ks[i], 'ratio': float(full[i]), 'z_null': float(z0), 'z_left': float(zl), 'z_right': float(zr)})
    return peaks


def t4b(c, seed=0, reps=200):
    U = c.units
    al = np.zeros((len(c.pages), 4))
    of = np.zeros_like(al)
    na = np.zeros_like(al)
    no = np.zeros_like(al)
    for pi, p in enumerate(c.pages):
        L = [[(U(t)[0], U(t)[-1]) for t in l.toks] for l in p.lines]
        for i in range(len(L)):
            for d in (1, 2, 3):
                if i + d >= len(L):
                    continue
                a, b = L[i], L[i + d]
                m = min(len(a), len(b)) - 2
                for j in range(1, m + 1):
                    na[pi, d] += 1
                    al[pi, d] += a[j] == b[j]
                    for o in (-2, -1, 1, 2):
                        jj = j + o
                        if 1 <= jj <= len(b) - 2:
                            no[pi, d] += 1
                            of[pi, d] += a[j] == b[jj]
    res = {}
    for d in (1, 2, 3):
        r = lambda idx: (al[idx, d].sum() / na[idx, d].sum()) / (of[idx, d].sum() / no[idx, d].sum())
        full = r(np.arange(len(c.pages)))
        boots = np.array([r(b) for b in _page_boot(len(c.pages), reps, seed)])
        res[d] = {'ratio': float(full), 'se': float(boots.std()), 'z': float((full - 1) / boots.std()) if boots.std() else None,
                  'aligned_pairs': int(na[:, d].sum())}
    return res


def _line_vec(l, U):
    v = Counter()
    for t in l.toks:
        u = ('^',) + U(t) + ('$',)
        v.update(zip(u, u[1:]))
    return v


def _cos(a, b):
    num = sum(v * b.get(k, 0) for k, v in a.items())
    den = math.sqrt(sum(v * v for v in a.values()) * sum(v * v for v in b.values()))
    return num / den if den else 0.0


def t4c(c, seed=0, K=12, reps=200):
    U = c.units
    obs = np.zeros((len(c.pages), K + 1))
    exp = np.zeros_like(obs)
    for pi, p in enumerate(c.pages):
        V = [_line_vec(l, U) for l in p.lines]
        n = len(V)
        if n < 3:
            continue
        S = np.zeros((n, n))
        for i in range(n):
            for j in range(i + 1, n):
                S[i, j] = S[j, i] = _cos(V[i], V[j])
        mean_pair = S[np.triu_indices(n, 1)].mean()
        for k in range(1, K + 1):
            if n > k:
                obs[pi, k] = np.diag(S, k).sum()
                exp[pi, k] = (n - k) * mean_pair
    ks = list(range(1, K + 1))
    ratio = lambda idx: obs[idx][:, ks].sum(0) / exp[idx][:, ks].sum(0)
    full = ratio(np.arange(len(c.pages)))
    boots = np.array([ratio(b) for b in _page_boot(len(c.pages), reps, seed)])
    x = np.arange(1, 9)
    slope = lambda r: float(np.polyfit(x, r[:8], 1)[0])
    sb = [slope(b) for b in boots]
    return {'k': ks, 'ratio': full.tolist(), 'se': boots.std(0).tolist(), 'peaks': _peaks(ks, full, boots),
            'slope_1_8': slope(full), 'slope_ci95': [float(np.percentile(sb, 2.5)), float(np.percentile(sb, 97.5))]}


# ------------------------------------------------------------------ T5 drift shape


def _page_vec(p, U):
    v = Counter()
    for l in p.lines:
        v.update(_line_vec(l, U))
    return v


def _jsd_vec(a, b):
    s = a + b
    pa, pb = a / a.sum(), b / b.sum()
    m = 0.5 * (pa + pb)
    f = lambda x: np.sum(x[x > 0] * np.log2(x[x > 0] / m[x > 0]))
    return 0.5 * f(pa) + 0.5 * f(pb)


def _excess_matrix(pages, U, rng, draws=20):
    vecs = [_page_vec(p, U) for p in pages]
    keys = sorted(set().union(*vecs))
    ix = {k: i for i, k in enumerate(keys)}
    M = np.zeros((len(vecs), len(keys)))
    for i, v in enumerate(vecs):
        for k, x in v.items():
            M[i, ix[k]] = x
    n = len(pages)
    E = np.zeros((n, n))
    for i in range(n):
        for j in range(i + 1, n):
            d = _jsd_vec(M[i], M[j])
            pool = M[i] + M[j]
            pr = pool / pool.sum()
            ni, nj = int(M[i].sum()), int(M[j].sum())
            fl = np.mean([_jsd_vec(rng.multinomial(ni, pr) + 0.0, rng.multinomial(nj, pr) + 0.0) for _ in range(draws)])
            E[i, j] = E[j, i] = d - fl
    return E


def _fit_smooth(E, idx):
    I, J = np.triu_indices(len(idx), 1)
    r = np.abs(np.array(idx)[J] - np.array(idx)[I]).astype(float)
    y = E[np.array(idx)[I], np.array(idx)[J]]
    A = np.vstack([np.ones_like(r), r]).T
    coef, *_ = np.linalg.lstsq(A, y, rcond=None)
    return coef


def _seg_path(E, idx, Kmax=6):
    """Greedy contiguous segmentation of the ordered pages idx for E = a + c*[different block].
    Returns {K: (bounds, coef)} for K = 1..Kmax; greedy boundaries are nested, so one pass serves all K."""
    n = len(idx)
    I, J = np.triu_indices(n, 1)
    y = E[np.array(idx)[I], np.array(idx)[J]]

    def sse_for(bs):
        lab = np.searchsorted(np.array(sorted(bs)), np.arange(n), side='right')
        x = (lab[I] != lab[J]).astype(float)
        A = np.vstack([np.ones_like(x), x]).T
        coef, *_ = np.linalg.lstsq(A, y, rcond=None)
        return float(((A @ coef - y) ** 2).sum()), coef

    bounds = []
    out = {1: ([], np.array([y.mean(), 0.0]))}
    for K in range(2, Kmax + 1):
        best = None
        for b in range(1, n):
            if b in bounds:
                continue
            sc, _ = sse_for(bounds + [b])
            if best is None or sc < best[0]:
                best = (sc, b)
        if best is None:
            break
        bounds.append(best[1])
        out[K] = (sorted(bounds), sse_for(bounds)[1])
    return out


def _pred_step(bounds, coef, pos_train, p_pos, other_pos):
    """Block label of a held-out page: block of the nearest training page (previous on ties)."""
    def lab_of_trainpos(k):
        return int(np.searchsorted(np.array(bounds), k, side='right'))
    # position of held-out page among training pages
    k = int(np.searchsorted(np.array(pos_train), p_pos))
    k = max(0, min(len(pos_train) - 1, k - 1 if k > 0 else 0))
    lp = lab_of_trainpos(k)
    out = []
    for q in other_pos:
        kq = pos_train.index(q)
        out.append(coef[0] + coef[1] * (lab_of_trainpos(kq) != lp))
    return np.array(out)


def _choose_K(E, idx, rng, Ks=range(2, 7), folds=5):
    n = len(idx)
    perm = list(range(n))
    rng.shuffle(perm)
    fold_of = {perm[i]: i % folds for i in range(n)}
    errs = {K: 0.0 for K in Ks}
    for f in range(folds):
        tr = [idx[i] for i in range(n) if fold_of[i] != f]
        te = [i for i in range(n) if fold_of[i] == f]
        path = _seg_path(E, tr, max(Ks))
        for K in Ks:
            if K not in path:
                errs[K] = float('inf')
                continue
            bounds, coef = path[K]
            for i in te:
                pred = _pred_step(bounds, coef, tr, idx[i], tr)
                errs[K] += float(((pred - E[idx[i], tr]) ** 2).sum())
    return min(errs, key=errs.get)


def t5(c, seed=0, min_tok=100, min_pages=10):
    rng_np = np.random.default_rng(seed)
    rng = random.Random(seed)
    U = c.units
    byhand = defaultdict(list)
    for p in c.pages:
        if p.hand and sum(len(l.toks) for l in p.lines) >= min_tok:
            byhand[p.hand].append(p)
    res = {}
    tot_step = tot_smooth = 0.0
    for h, ps in sorted(byhand.items()):
        if len(ps) < min_pages:
            continue
        E = _excess_matrix(ps, U, rng_np)
        n = len(ps)
        idx = list(range(n))
        se_step = se_smooth = 0.0
        for p in range(n):
            tr = [i for i in idx if i != p]
            a, b = _fit_smooth(E, tr)
            y = E[p, tr]
            se_smooth += float(((a + b * np.abs(np.array(tr) - p) - y) ** 2).sum())
            K = _choose_K(E, tr, rng)
            bounds, coef = _seg_path(E, tr, K)[K]
            pred = _pred_step(bounds, coef, tr, p, tr)
            se_step += float(((pred - y) ** 2).sum())
        cons = [E[i, i + 1] for i in range(n - 1)]
        top = np.argsort(cons)[::-1][:max(1, len(cons) // 10)]
        bnd = [ps[i].quire != ps[i + 1].quire or ps[i].section != ps[i + 1].section for i in range(n - 1)]
        res[h] = {'pages': n, 'S': se_step / se_smooth, 'gini_consecutive': gini(cons),
                  'mean_consecutive_excess': float(np.mean(cons)),
                  'top_decile_on_boundary': float(np.mean([bnd[i] for i in top])),
                  'base_boundary_share': float(np.mean(bnd))}
        tot_step += se_step
        tot_smooth += se_smooth
    return {'S_pooled': tot_step / tot_smooth if tot_smooth else None, 'hands': res}


# ------------------------------------------------------------------ T6 writer dynamics


def t6a(c, seed=0, dmax=40, reps=500):
    U = c.units
    types = sorted({t for p in c.pages for l in p.lines for t in l.toks})
    tid = {t: i for i, t in enumerate(types)}
    NT = len(types)
    near = ed1_pairs(types, U)
    near_codes = np.array(sorted(a * NT + b for a, b in near), dtype=np.int64)
    near_of = defaultdict(set)
    for a, b in near:
        near_of[a].add(b)
    ds = np.arange(2, dmax + 1)
    P = len(c.pages)
    oe = np.zeros((P, len(ds)))
    on = np.zeros_like(oe)
    ee = np.zeros_like(oe)
    en = np.zeros_like(oe)
    for pi, p in enumerate(c.pages):
        x = np.array([tid[t] for l in p.lines for t in l.toks], dtype=np.int64)
        n = len(x)
        if n < 10:
            continue
        cnt = Counter(x.tolist())
        pe = sum(k * (k - 1) for k in cnt.values()) / (n * (n - 1))
        pn = sum(cnt[a] * cnt[b] for a in cnt for b in near_of.get(a, ()) if b in cnt) / (n * (n - 1))
        for j, d in enumerate(ds):
            if n <= d:
                continue
            a, b = x[:-d], x[d:]
            oe[pi, j] = (a == b).sum()
            codes = a * NT + b
            pos = np.searchsorted(near_codes, codes)
            pos[pos >= len(near_codes)] = 0
            on[pi, j] = (near_codes[pos] == codes).sum() if len(near_codes) else 0
            ee[pi, j] = (n - d) * pe
            en[pi, j] = (n - d) * pn
    short = (ds >= 2) & (ds <= 5)
    long_ = (ds >= 21) & (ds <= 40)

    def prof(idx):
        re_ = oe[idx].sum(0) / np.maximum(ee[idx].sum(0), 1e-12)
        rn = on[idx].sum(0) / np.maximum(en[idx].sum(0), 1e-12)
        return re_, rn

    re_, rn = prof(np.arange(P))
    DIe = re_[short].mean() - re_[long_].mean()
    DIn = rn[short].mean() - rn[long_].mean()
    boots = [prof(b) for b in _page_boot(P, reps, seed)]
    be = [r[0][short].mean() - r[0][long_].mean() for r in boots]
    bn = [r[1][short].mean() - r[1][long_].mean() for r in boots]
    return {'DI_exact': float(DIe), 'DI_exact_ci95': [float(np.percentile(be, 2.5)), float(np.percentile(be, 97.5))],
            'DI_near': float(DIn), 'DI_near_ci95': [float(np.percentile(bn, 2.5)), float(np.percentile(bn, 97.5))],
            'DI_near_p99': float(np.percentile(bn, 99)), 'DI_near_p01': float(np.percentile(bn, 1)),
            'exact_profile': re_.tolist(), 'near_profile': rn.tolist(), 'd': ds.tolist()}


def t6c(c, run, min_pages=20):
    byhand = defaultdict(list)
    for p in c.pages:
        byhand[p.hand].append(p)
    out = {}
    for h, ps in sorted(byhand.items(), key=lambda x: str(x[0])):
        if len(ps) < min_pages:
            continue
        sub = type(c)(c.name + '-H' + str(h), ps, c.kind, c.gclass)
        a = t6a(sub, reps=200)
        b = t4c(sub, reps=100)
        out[h] = {'pages': len(ps), 'DI_near': a['DI_near'], 'DI_near_ci95': a['DI_near_ci95'],
                  'DI_exact': a['DI_exact'], 'slope_1_8': b['slope_1_8'], 'slope_ci95': b['slope_ci95']}
    return out


# ------------------------------------------------------------------ T7b deviant tokens


def t7b(c, seed=0, perms=100, double_coded_only=False):
    U = c.units
    rng = random.Random(seed)
    tri_by_q = defaultdict(Counter)
    seq_by_q = defaultdict(list)    # (token, analysable flag)
    for p in c.pages:
        for l in p.lines:
            flags = l.dc if (double_coded_only and l.dc is not None) else [True] * len(l.toks)
            for t, f in zip(l.toks, flags):
                u = ('^',) + U(t) + ('$',)
                tri_by_q[p.quire].update(zip(u, u[1:], u[2:]))
                seq_by_q[p.quire].append((t, f))
    total = Counter()
    for q, C in tri_by_q.items():
        total.update(C)
    n_an = n_dev = 0
    rec_types = dev_types = 0
    obs_d, null_meds = [], []
    slip = 0
    for q, seq in seq_by_q.items():
        own = tri_by_q[q]
        freq = Counter(t for t, _ in seq)
        common = [t for t, k in freq.items() if k >= 5]
        common_units = {U(t) for t in common}
        pos = defaultdict(list)
        for i, (t, f) in enumerate(seq):
            if not f:
                continue
            n_an += 1
            u = ('^',) + U(t) + ('$',)
            if any(total[x] - own[x] == 0 for x in zip(u, u[1:], u[2:])):
                n_dev += 1
                pos[t].append(i)
                ut = U(t)
                if any(_ed1(ut, cu) for cu in common_units):
                    slip += 1
        for t, ps in pos.items():
            dev_types += 1
            if len(ps) >= 2:
                rec_types += 1
                obs_d.extend(np.diff(ps).tolist())
        # random placement null for recurrent types
        rec = [len(ps) for ps in pos.values() if len(ps) >= 2]
        if rec:
            N = len(seq)
            null_meds.append((rec, N))
    med_obs = float(np.median(obs_d)) if obs_d else None
    meds = []
    for _ in range(perms):
        ds = []
        for rec, N in null_meds:
            for k in rec:
                ds.extend(np.diff(sorted(rng.sample(range(N), k))).tolist())
        meds.append(np.median(ds) if ds else np.nan)
    return {'analysed_tokens': n_an, 'deviant_tokens': n_dev, 'rate_per_1000': 1000 * n_dev / n_an if n_an else None,
            'deviant_types': dev_types, 'recurrence_share': rec_types / dev_types if dev_types else None,
            'median_gap': med_obs, 'null_median_gap': float(np.nanmean(meds)) if meds else None,
            'clustering_ratio': med_obs / float(np.nanmean(meds)) if med_obs and meds else None,
            'slip_share': slip / n_dev if n_dev else None}


def _ed1(a, b):
    la, lb = len(a), len(b)
    if abs(la - lb) > 1:
        return False
    if la == lb:
        return sum(x != y for x, y in zip(a, b)) == 1
    if la > lb:
        a, b = b, a
    for i in range(len(b)):
        if b[:i] + b[i + 1:] == a:
            return True
    return False


# ------------------------------------------------------------------ T7a annotated corrections (ZL comments)

KEYS = re.compile(r'corr|eras|above|inser|added', re.I)


def _replay(raw):
    """Replay IVTFF markup of one line; returns (tokens, events) where events are (token index, char offset,
    comment). Mirrors voynich.ivtff.clean_text with commas joined."""
    toks, cur, events = [], '', []
    i = 0
    while i < len(raw):
        ch = raw[i]
        if raw.startswith('<!', i):
            j = raw.index('>', i)
            com = raw[i + 2:j]
            if KEYS.search(com):
                events.append((len(toks), len(cur), com))
            i = j + 1
        elif ch == '<':
            j = raw.index('>', i)
            tag = raw[i:j + 1]
            if tag in ('<->', '<~>') and cur:
                toks.append(cur)
                cur = ''
            i = j + 1
        elif ch == '[':
            j = raw.index(']', i)
            alt = raw[i + 1:j].split(':')[0]
            cur += re.sub(r'@\d+;', '*', re.sub(r'\{[^}]*\}', '', alt))
            i = j + 1
        elif ch == '{':
            i = raw.index('}', i) + 1
        elif ch == '@' and re.match(r'@\d+;', raw[i:]):
            cur += '*'
            i = raw.index(';', i) + 1
        elif ch == '.':
            if cur:
                toks.append(cur)
            cur = ''
            i += 1
        elif ch in ',! \t':
            i += 1
        else:
            cur += ch
            i += 1
    if cur:
        toks.append(cur)
    return toks, events


def t7a(zl='data/ZL3b-n.txt'):
    from voynich.ivtff import parse
    from mechanism.corpus import eva_units, certain
    lines = parse(zl, comma_is_space=False)
    ev_lines, events, other_loci = set(), [], 0
    mismatch = 0
    for ln in lines:
        toks, ev = _replay(ln.raw)
        if not ev:
            continue
        if ln.kind != 'P':
            other_loci += len(ev)
            continue
        if toks != ln.words:
            mismatch += 1
        ev_lines.add((ln.page, ln.num))
        for ti, off, com in ev:
            tok = toks[ti] if ti < len(toks) else None
            if off == 0 and ti > 0:
                # comment right after a separator: refers to the boundary / previous token end
                pos, tok_ref = 'boundary', toks[ti - 1] if ti - 1 < len(toks) else None
            elif tok is None:
                pos, tok_ref = 'line-end', toks[-1] if toks else None
            else:
                u = eva_units(tok)
                cum, k = 0, 0
                for k, x in enumerate(u):
                    cum += len(x)
                    if cum >= off:
                        break
                pos = 'initial' if k == 0 else ('final' if k == len(u) - 1 else 'internal')
                if off == 0:
                    pos = 'before-first'
                tok_ref = tok
            events.append({'page': ln.page, 'line': ln.num, 'comment': com, 'token': tok_ref, 'position': pos,
                           'hand': ln.hand, 'section': ln.section})
    # order-2 unit model without annotated lines
    train = [w for ln in lines if ln.kind == 'P' and (ln.page, ln.num) not in ev_lines for w in ln.words if certain(w)]
    c2, c1, c0 = defaultdict(Counter), defaultdict(Counter), Counter()
    for w in train:
        u = ('^', '^') + eva_units(w) + ('$',)
        for i in range(2, len(u)):
            c2[u[i - 2:i]][u[i]] += 1
            c1[u[i - 1]][u[i]] += 1
            c0[u[i]] += 1
    V0 = len(c0) + 1
    N0 = sum(c0.values())

    def lp(w):
        u = ('^', '^') + eva_units(w) + ('$',)
        s = 0.0
        for i in range(2, len(u)):
            p0 = (c0[u[i]] + 1) / (N0 + V0)
            n1 = sum(c1[u[i - 1]].values())
            p1 = (c1[u[i - 1]][u[i]] + p0) / (n1 + 1)
            n2 = sum(c2[u[i - 2:i]].values())
            p2 = (c2[u[i - 2:i]][u[i]] + p1) / (n2 + 1)
            s += math.log2(p2)
        return s

    by_len = defaultdict(list)
    for w in train:
        by_len[len(eva_units(w))].append(lp(w))
    for e in events:
        t = e['token']
        if t and certain(t):
            ref = by_len.get(len(eva_units(t))) or []
            v = lp(t)
            e['logprob_percentile'] = float(np.mean([x <= v for x in ref])) if ref else None
        else:
            e['logprob_percentile'] = None
    units = Counter()
    for w in train:
        n = len(eva_units(w))
        units['initial'] += 1
        if n > 1:
            units['final'] += 1
        units['internal'] += max(0, n - 2)
    tot = sum(units.values())
    base = {k: v / tot for k, v in units.items()}
    counts = Counter(e['position'] for e in events)
    from scipy.stats import binomtest
    tests_ = {}
    n = len(events)
    for k in ('initial', 'internal', 'final'):
        if n:
            tests_[k] = {'count': counts.get(k, 0), 'share': counts.get(k, 0) / n, 'base': base[k],
                         'p_greater': binomtest(counts.get(k, 0), n, base[k], alternative='greater').pvalue}
    pct = [e['logprob_percentile'] for e in events if e['logprob_percentile'] is not None]
    return {'n_events_P': n, 'events_other_loci': other_loci, 'replay_mismatch_lines': mismatch,
            'position_counts': dict(counts), 'position_tests': tests_,
            'median_logprob_percentile': float(np.median(pct)) if pct else None, 'n_scored': len(pct),
            'events': events}
