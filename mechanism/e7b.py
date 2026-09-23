"""R4a (mechanism/REVISION_PLAN.md): E7 with 20 runs per condition.

    python3 -m mechanism.e7b run       # 20 PRNG, 20 compressed-plaintext and 20 raw-plaintext runs
    python3 -m mechanism.e7b report    # Welch tests with Holm correction, tolerance rule, recovery
"""
import json
import math
import os
import sys
import warnings
from concurrent.futures import ProcessPoolExecutor

import numpy as np

from mechanism import e7 as E7

warnings.filterwarnings('ignore', category=RuntimeWarning)
OUT = 'results/mechanism/e7b'
OFFSETS = {'LAT': [0, 100000, 200000, 300000, 400000], 'GER': [0, 60000, 120000, 180000, 240000],
           'ITA': [0, 100000, 200000, 300000, 400000], 'ENG': [0, 100000, 200000, 300000, 400000]}


def pbits(lang, compressed, off, need=800000):
    """Plaintext bits from bit offset `off` (a multiple of 8), at most `need` bits, as in E7.plaintext_bits."""
    import lzma
    data = open(E7.LANGS[lang], encoding='utf-8', errors='replace').read().encode('utf-8')
    if compressed:
        data = lzma.compress(data, preset=9)
    return E7.bits_of(data[off // 8:(off + need) // 8])


def conditions():
    c = [('prng', s, 0) for s in range(101, 121)]
    for kind in ('lzma', 'raw'):
        c += [(kind, lang, off) for lang, offs in OFFSETS.items() for off in offs]
    return c


def _job(cond):
    kind, key, off = cond
    P = E7.Process()
    if kind == 'prng':
        c, raw = P.generate(E7.PRNG(key), f'prng-{key}')
        rec = None
    else:
        bits = pbits(key, kind == 'lzma', off)
        dec = E7.Decoder(bits)
        c, raw = P.generate(dec, f'{kind}-{key}-{off}')
        out = P.recover(raw)
        used = dec.pos - E7.PREC
        n = min(len(out), used)
        mism = sum(1 for a, b in zip(out[:n], bits[:n]) if a != b)
        glyphs = sum(len(s.replace(' ', '')) for _, _, s in raw)
        toks = sum(len([w for w in s.split(' ') if w]) for _, _, s in raw)
        rec = {'bits_available': len(bits), 'bits_consumed': used, 'bits_recovered_compared': n, 'mismatches': mism,
               'glyphs': glyphs, 'tokens': toks, 'bits_per_glyph': used / glyphs, 'bits_per_token': used / toks,
               'exhausted': used > len(bits)}
    ph = E7.E2.phenotype(c, double_coded=False)
    return f'{kind}:{key}:{off}', ph, rec


def run(conds, jobfn, out, workers=9):
    os.makedirs(os.path.dirname(out), exist_ok=True)
    res = json.load(open(out)) if os.path.exists(out) else {}
    todo = [c for c in conds if f'{c[0]}:{c[1]}:{c[2]}' not in res]
    with ProcessPoolExecutor(max_workers=workers) as ex:
        for key, ph, rec in ex.map(jobfn, todo):
            res[key] = {'phenotype': ph, 'recovery': rec}
            print(key, rec and {k: (round(v, 3) if isinstance(v, float) else v) for k, v in rec.items()}, flush=True)
            json.dump(res, open(out, 'w'), indent=1)
    return res


def compare(res, base='prng', kinds=('lzma', 'raw')):
    """Primary: Welch t-test per continuous statistic, Holm-corrected; T4 peak counts by Fisher's exact test.
    Secondary: tolerance rule 2*sqrt(sd_a^2 + sd_b^2) + 1% and the count of unadjusted p < 0.05."""
    from scipy.stats import fisher_exact, ttest_ind
    A = [v['phenotype'] for k, v in res.items() if k.startswith(base + ':')]
    summary = {'n_base': len(A)}
    for kind in kinds:
        B = [v['phenotype'] for k, v in res.items() if k.startswith(kind + ':')]
        if not B:
            continue
        rows = {}
        for s in A[0]:
            a = np.array([x[s] for x in A if x.get(s) is not None], float)
            b = np.array([x[s] for x in B if x.get(s) is not None], float)
            if len(a) < 2 or len(b) < 2:
                continue
            if s == 'T4_peak':
                p = float(fisher_exact([[int(a.sum()), len(a) - int(a.sum())], [int(b.sum()), len(b) - int(b.sum())]])[1])
                tol_ok = abs(a.sum() / len(a) - b.sum() / len(b)) <= 0.1
            else:
                p = float(ttest_ind(a, b, equal_var=False).pvalue) if (a.std() > 0 or b.std() > 0) else 1.0
                tol = 2 * math.sqrt(a.var(ddof=1) + b.var(ddof=1)) + 0.01 * abs(a.mean())
                tol_ok = bool(abs(a.mean() - b.mean()) <= tol)
            rows[s] = {'base_mean': float(a.mean()), 'base_sd': float(a.std(ddof=1)), 'mean': float(b.mean()),
                       'sd': float(b.std(ddof=1)), 'p': p if p == p else 1.0, 'tol_ok': tol_ok, 'n': [len(a), len(b)]}
        ps = sorted(rows, key=lambda s: rows[s]['p'])
        m = len(ps)
        running = 0.0
        for i, s in enumerate(ps):
            running = max(running, min(1.0, (m - i) * rows[s]['p']))
            rows[s]['p_holm'] = running
        summary[kind] = {'n_runs': len(B), 'n_stats': m,
                         'holm_significant': [s for s in rows if rows[s]['p_holm'] < 0.05],
                         'unadjusted_p05': [s for s in rows if rows[s]['p'] < 0.05],
                         'tolerance_agree': sum(r['tol_ok'] for r in rows.values()),
                         'tolerance_disagree': [s for s in rows if not rows[s]['tol_ok']],
                         'min_p': min(r['p'] for r in rows.values()), 'rows': rows}
    return summary


def recovery_summary(res):
    rec = [v['recovery'] for v in res.values() if v['recovery']]
    out = {}
    for kind in ('lzma', 'raw'):
        r = [v['recovery'] for k, v in res.items() if v['recovery'] and k.startswith(kind + ':')]
        if r:
            out[kind] = {'runs': len(r), 'total_mismatches': sum(x['mismatches'] for x in r),
                         'any_exhausted': any(x['exhausted'] for x in r),
                         'bits_per_glyph_mean': float(np.mean([x['bits_per_glyph'] for x in r])),
                         'bits_per_glyph_sd': float(np.std([x['bits_per_glyph'] for x in r], ddof=1)),
                         'bits_consumed_mean': float(np.mean([x['bits_consumed'] for x in r])),
                         'glyphs_mean': float(np.mean([x['glyphs'] for x in r])),
                         'tokens_mean': float(np.mean([x['tokens'] for x in r]))}
    out['all_runs_exact'] = all(x['mismatches'] == 0 and not x['exhausted'] for x in rec)
    return out


def report(res_path, out_path, base='prng'):
    res = json.load(open(res_path))
    s = compare(res, base=base)
    s['recovery'] = recovery_summary(res)
    json.dump(s, open(out_path, 'w'), indent=1, default=lambda o: o.item() if hasattr(o, 'item') else str(o))
    for kind in ('lzma', 'raw'):
        if kind in s:
            k = s[kind]
            print(f"{kind}: {k['n_runs']} runs vs {s['n_base']}; Holm-significant {k['holm_significant']}; "
                  f"unadjusted p<0.05: {len(k['unadjusted_p05'])}/{k['n_stats']} {k['unadjusted_p05']}; "
                  f"tolerance {k['tolerance_agree']}/{k['n_stats']}; min p {k['min_p']:.4f}")
    print(s['recovery'])


if __name__ == '__main__':
    if sys.argv[1] == 'run':
        run(conditions(), _job, f'{OUT}/results.json')
    report(f'{OUT}/results.json', f'{OUT}/report.json')
