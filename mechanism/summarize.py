"""Print the battery results as plain tables: python3 -m mechanism.summarize [A|B|AB]."""
import json
import sys

f = lambda x, d=3: None if x is None else round(x, d)
MAIN = ['VOYNICH', 'GIB', 'LATW', 'LAT', 'ITA', 'GER', 'ENG', 'MK-sec', 'MK-page', 'RUGG', 'TS', 'NAIB-lines', 'NAIB-run']


def load(stages):
    R = {}
    for s in stages:
        try:
            R.update(json.load(open(f'results/mechanism/stage{s}.json')))
        except FileNotFoundError:
            pass
    return R


def main(stages='A'):
    R = load(stages)
    names = [n for n in MAIN if n in R]
    g = lambda n, t: R[n].get(t) if isinstance(R[n].get(t), dict) and 'error' not in R[n].get(t) else None
    print('T1 line-break transparency (page-conditional): R_LB, jackknife SE, excess break / within (bits)')
    for n in names:
        r = g(n, 't1')
        if r:
            print(f"  {n:11s} R={f(r['R_LB'])} se={f(r['se'])} break={f(r['excess_break'], 4)} within={f(r['excess_within'], 4)}")
    print('T2a final-form effect: excess JSD, p (margin-bound | paragraph-final)')
    for n in names:
        a, b = g(n, 't2a_margin'), g(n, 't2a_para')
        if a:
            print(f"  {n:11s} margin {f(a['excess'], 4)} p={f(a['p'])} n={a['n_final']} | para " +
                  (f"{f(b['excess'], 4)} p={f(b['p'])} n={b['n_final']}" if b else '-'))
    print('T2b slack tightness T (95% CI)')
    for n in names:
        r = g(n, 't2b')
        if r and r.get('T') is not None:
            print(f"  {n:11s} T={f(r['T'])} ci={[f(x) for x in r['ci95']]} pages={r['pages']} lines={r['lines']} W={f(r['mean_W'], 1)}")
    print('T2c dittography at line breaks: token ratio obs/null, p; bigram repeats, p')
    for n in names:
        r = g(n, 't2c')
        if r:
            print(f"  {n:11s} ratio={f(r['ratio_tok'])} p={f(r['p_tok_excess'])} bigrams={r['count_big']} p={f(r['p_big_excess'])}")
    print('T3a zero replication rho (matched 250-token chunks; full size) | T3b slot consistency, monotone share')
    for n in names:
        a, b = g(n, 't3a'), g(n, 't3b')
        full = (R[n].get('t3a_full') or {}).get('all')
        if a:
            print(f"  {n:11s} rho={f(a['rho'])} ci={[f(x) for x in a['ci95']]} full={f(full['rho']) if full else '-'} | "
                  f"cons={f(b['consistency'])} ci={[f(x) for x in b['cons_ci95']]} mono={f(b['monotone'])} ci={[f(x) for x in b['mono_ci95']]}")
    print('T3c positional entropy (share of unit entropy)')
    for n in names:
        c = g(n, 't3c')
        if c:
            print(f"  {n:11s}", {k: f(v, 2) for k, v in c.items()})
    print('T4 periodicity: T4a peaks (final, initial), T4b z (d=1,2,3), T4c peaks, T6b slope')
    for n in names:
        a, b, c = g(n, 't4a'), g(n, 't4b'), g(n, 't4c')
        if a:
            print(f"  {n:11s} t4a={[p['k'] for p in a['final']['peaks']]},{[p['k'] for p in a['initial']['peaks']]} "
                  f"t4b={[f(b[d]['z'], 1) for d in ('1', '2', '3')]} t4c={[p['k'] for p in c['peaks']]} "
                  f"slope={f(c['slope_1_8'], 4)} ci={[f(x, 4) for x in c['slope_ci95']]}")
    if any(k.startswith('DEV-') for k in R):
        print('T4 power (device control, 10 seeds)')
        for w in ('0.1', '0.2', '0.4'):
            rs = [R[f'DEV-{w}-{s}'] for s in range(10) if f'DEV-{w}-{s}' in R]
            da = sum(any(p['k'] == 5 for p in r['t4a']['final']['peaks'] + r['t4a']['initial']['peaks']) for r in rs)
            db = sum((r['t4b']['1']['z'] or 0) > 3 for r in rs)
            dc = sum(any(p['k'] == 4 for p in r['t4c']['peaks']) for r in rs)
            print(f"  w={w}: T4a {da}/{len(rs)}  T4b {db}/{len(rs)}  T4c {dc}/{len(rs)}")
    print('T5 drift shape: S = MSE(step)/MSE(smooth); per hand (pages, S, Gini, top-decile-on-boundary, base)')
    for n in names + ['DRIFT-smooth', 'DRIFT-step']:
        r = g(n, 't5') if n in R else None
        if r:
            print(f"  {n:12s} S={f(r['S_pooled'])}",
                  {h: (d['pages'], f(d['S'], 2), f(d['gini_consecutive'], 2), f(d['top_decile_on_boundary'], 2),
                       f(d['base_boundary_share'], 2)) for h, d in r['hands'].items()})
    print('T6a recency: DI exact, DI near (95% CI, 99th pct)')
    for n in names + [k for k in R if k.startswith('DEV-') and k.endswith('-0')]:
        r = g(n, 't6a')
        if r:
            print(f"  {n:11s} exact={f(r['DI_exact'])} ci={[f(x) for x in r['DI_exact_ci95']]} near={f(r['DI_near'])} "
                  f"ci={[f(x) for x in r['DI_near_ci95']]} p99={f(r['DI_near_p99'])}")
    print('T7b deviant tokens: rate/1000, recurrence share, clustering ratio, slip share')
    for n in names:
        r = g(n, 't7b')
        if r:
            print(f"  {n:11s} rate={f(r['rate_per_1000'], 1)} rec={f(r['recurrence_share'])} clust={f(r['clustering_ratio'])} "
                  f"slip={f(r['slip_share'])} types={r['deviant_types']}")


if __name__ == '__main__':
    main(sys.argv[1] if len(sys.argv) > 1 else 'A')
