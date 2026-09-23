"""Build the paper: results/mechanism/*.json + paper/numbers.json + paper/templates -> paper/paper.html|pdf, paper/supplement.html|pdf.
Every number in text and tables is computed here (or in paper/profile.py) from the result files."""
import datetime
import json
import os
import subprocess
import sys

import fitz
import numpy as np
from jinja2 import Environment, FileSystemLoader, StrictUndefined

sys.path.insert(0, 'paper')
import profile as profile_analysis  # noqa: E402  (paper/profile.py, not the stdlib profiler)
from labels import FITTED, STAT  # noqa: E402

R = 'results/mechanism'
L = lambda p: json.load(open(f'{R}/{p}'))
A, B, PH, RT = L('stageA.json'), L('stageB.json')['VOYNICH'], L('posthoc.json'), L('redteam.json')
E1A, E1B, E1I = L('e1_stageA.json'), L('e1_stageB.json')['VOYNICH'], L('e1_posthoc_it2a.json')['IT2a']
E2R, E3R, E6R = L('e2/report.json'), L('e3/report.json'), L('e6/report.json')
E2F, E3F, E6F = L('e2/fits.json'), L('e3/fits.json'), L('e6/fits.json')
E4A, E4B = L('e4_stageA.json'), L('e4_stageB.json')['VOYNICH']
E5A, E5B, E5I = L('e5_stageA.json'), L('e5_stageB.json')['VOYNICH'], L('e5_posthoc_it2a.json')['IT2a']
E7, E7T, E7C = L('e7/report.json'), L('e7/results.json'), L('e7/token_mi_check.json')


def _minus(t):
    if t.startswith('-') and float(t) == 0:
        t = t[1:]
    return t.replace('-', '\u2212')


def f(x, d=3):
    if x is None:
        return 'n/a'
    if x != x:
        return 'undef.'
    return _minus(('%.' + str(d) + 'f') % x)


def sg(x, d=3):
    t = ('%+.' + str(d) + 'f') % x
    if float(t) == 0:
        return ('%.' + str(d) + 'f') % 0.0
    return t.replace('-', '\u2212')


def pc(x, d=1):
    return ('%.' + str(d) + 'f') % (100 * x) + '%'


def ci(c, d=3):
    return f'({f(c[0], d)}, {f(c[1], d)})'


def rng(xs, d=3):
    lo, hi = min(xs), max(xs)
    return f'{f(lo, d)} to {f(hi, d)}' if lo < 0 else f'{f(lo, d)}–{f(hi, d)}'


LANGS = ['LAT', 'ITA', 'GER', 'ENG']
LN = {'LAT': 'Latin', 'ITA': 'Italian', 'GER': 'German', 'ENG': 'English'}
v = {}

# ---------------------------------------------------------------- corpus
v['v_pages'], v['v_tokens'] = B['_meta']['pages'], f"{B['_meta']['tokens']:,}"
v['gib_docs'], v['gib_tokens'] = A['GIB']['_meta']['pages'], f"{A['GIB']['_meta']['tokens']:,}"
v['it_tokens'] = f"{PH['it2a']['tokens']:,}"
v['date'] = datetime.date.today().strftime('%d %B %Y')
v['commit'] = subprocess.run(['git', 'rev-parse', '--short', 'HEAD'], capture_output=True, text=True).stdout.strip()

# ---------------------------------------------------------------- T1
v.update(t1_v=f(B['t1']['R_LB'], 2), t1_v_se=f(B['t1']['se'], 2), t1_v_b=f(B['t1']['excess_break']), t1_v_w=f(B['t1']['excess_within']),
         t1_it=f(PH['it2a']['t1']['R_LB'], 2), t1_it_se=f(PH['it2a']['t1']['se'], 2),
         t1_gib=f(A['GIB']['t1']['R_LB'], 2), t1_gib_se=f(A['GIB']['t1']['se'], 2), t1_latw=f(A['LATW']['t1']['R_LB'], 2), t1_latw_se=f(A['LATW']['t1']['se'], 2),
         t1_mk=f(A['MK-sec']['t1']['R_LB'], 2), t1_ts=f(A['TS']['t1']['R_LB'], 2))
# ---------------------------------------------------------------- T2
v.update(t2a_m=f(B['t2a_margin']['excess']), t2a_m_p=f(B['t2a_margin']['p']), t2a_m_n=f"{B['t2a_margin']['n_final']:,}",
         t2a_p=f(B['t2a_para']['excess']), t2a_p_p=f(B['t2a_para']['p']), t2a_p_n=f"{B['t2a_para']['n_final']:,}",
         t2a_it=f(PH['it2a']['t2a_margin']['excess']), t2a_gib_m=f(A['GIB']['t2a_margin']['excess'], 4), t2a_gib_m_p=f(A['GIB']['t2a_margin']['p'], 2),
         t2a_gib_p=f(A['GIB']['t2a_para']['excess']), t2a_gib_p_p=f(A['GIB']['t2a_para']['p'], 2),
         t2a_latw=f(A['LATW']['t2a_margin']['excess'], 4), t2a_latw_p=f(A['LATW']['t2a_margin']['p'], 2),
         t2a_diff=f(RT['t2a_difference']['VOYNICH']['diff']), t2a_diff_ci=ci(RT['t2a_difference']['VOYNICH']['diff_ci95']),
         t2a_star_m=f(RT['t2a_stars']['margin']['excess']), t2a_star_p=f(RT['t2a_stars']['para']['excess']),
         t2a_star_mn=RT['t2a_stars']['margin']['n_final'], t2a_star_pn=RT['t2a_stars']['para']['n_final'],
         t2b_v=f(B['t2b']['T'], 2), t2b_v_ci=ci(B['t2b']['ci95'], 2), t2b_v_pages=B['t2b']['pages'], t2b_v_lines=B['t2b']['lines'],
         t2b_gib=f(A['GIB']['t2b']['T'], 2), t2b_gib_ci=ci(A['GIB']['t2b']['ci95'], 2), t2b_latw=f(A['LATW']['t2b']['T'], 3), t2b_latw_ci=ci(A['LATW']['t2b']['ci95'], 3),
         t2c_v=f(B['t2c']['ratio_tok'], 2), t2c_v_p=f(B['t2c']['p_tok_excess'], 2), t2c_ts=f(A['TS']['t2c']['ratio_tok'], 2), t2c_ts_p=f(A['TS']['t2c']['p_tok_excess'], 2))
# ---------------------------------------------------------------- T3
gens = ['MK-sec', 'MK-page', 'RUGG', 'TS', 'NAIB-lines', 'NAIB-run']
v.update(t3a_v=f(B['t3a']['rho']), t3a_v_ci=ci(B['t3a']['ci95']), t3a_it=f(PH['it2a']['t3a']['rho']),
         t3a_gib=f(A['GIB']['t3a']['rho']), t3a_gib_ci=ci(A['GIB']['t3a']['ci95']),
         t3a_lang=rng([A[n]['t3a']['rho'] for n in LANGS]), t3a_gen=rng([A[n]['t3a']['rho'] for n in gens if n != 'RUGG']), t3a_rugg=f(A['RUGG']['t3a']['rho']),
         t3a_full_v=f(B['t3a_full']['all']['rho'], 4), t3a_full_lang=rng([A[n]['t3a_full']['all']['rho'] for n in LANGS], 4),
         t3a_raw_v=f(RT['VOYNICH']['raw_t3a']), t3a_raw_gib=f(RT['GIB']['raw_t3a']),
         t3b_v=f(B['t3b']['consistency']), t3b_v_ci=ci(B['t3b']['cons_ci95']), t3b_v_mono=f(B['t3b']['monotone'], 2), t3b_it=f(PH['it2a']['t3b']['consistency']),
         t3b_gib=f(A['GIB']['t3b']['consistency']), t3b_gib_mono=f(A['GIB']['t3b']['monotone'], 2),
         t3b_lang=rng([A[n]['t3b']['consistency'] for n in LANGS], 2), t3b_lang_mono=rng([A[n]['t3b']['monotone'] for n in LANGS], 2),
         t3b_gen=rng([A[n]['t3b']['consistency'] for n in gens], 2), t3b_raw_v=f(RT['VOYNICH']['raw_t3b']), t3b_raw_gib=f(RT['GIB']['raw_t3b']),
         t3c_v=f(B['t3c']['e1'], 2), t3c_naib=f(A['NAIB-run']['t3c']['e1'], 2), t3c_mk=f(A['MK-sec']['t3c']['e1'], 2),
         t3c_lang=rng([A[n]['t3c']['e1'] for n in LANGS], 2), t3c_gib=f(A['GIB']['t3c']['e1'], 2))
ph = RT['per_hand']
v.update(hand_t3a=rng([ph[h]['t3a_rho'] for h in ph]), hand_t3b=rng([ph[h]['t3b_cons'] for h in ph], 2),
         hand_t6a=rng([ph[h]['t6a_near'] for h in ph], 2), hand_t2a=rng([ph[h]['t2a_margin'] for h in ph]))
# ---------------------------------------------------------------- T4
pw = {}
for w in ('0.1', '0.2', '0.4'):
    rs = [A[f'DEV-{w}-{s}'] for s in range(10)]
    pw[w] = (sum(any(p['k'] == 5 for p in r['t4a']['final']['peaks'] + r['t4a']['initial']['peaks']) for r in rs),
             sum((r['t4b']['1']['z'] or 0) > 3 for r in rs), sum(any(p['k'] == 4 for p in r['t4c']['peaks']) for r in rs))
v.update(pw01=pw['0.1'], pw02=pw['0.2'], pw04=pw['0.4'], t4b_v=', '.join(f(B['t4b'][d]['z'], 1) for d in ('1', '2', '3')))
# ---------------------------------------------------------------- T5
v.update(t5_v=f(B['t5']['S_pooled'], 2), t5_h={h: f(d['S'], 2) for h, d in B['t5']['hands'].items()}, t5_it=f(PH['it2a']['t5']['S_pooled'], 2),
         t5_smooth=f(A['DRIFT-smooth']['t5']['S_pooled'], 2), t5_step=f(A['DRIFT-step']['t5']['S_pooled'], 2), t5_mk=f(A['MK-sec']['t5']['S_pooled'], 2))
dec = PH['t5_decomposition']['VOYNICH']['2']
v.update(t5_h2_q=f(dec['mean_excess_by_type']['quire-only']), t5_h2_s=f(dec['mean_excess_by_type']['section-only']),
         t5_h2_b=f(dec['mean_excess_by_type']['both']), t5_h2_n=f(dec['mean_excess_by_type']['none']))
# ---------------------------------------------------------------- T6
stat_p99 = [A[n]['t6a']['DI_near_p99'] for n in ('MK-sec', 'MK-page', 'RUGG', 'DEV-0.1-0', 'DEV-0.2-0', 'DEV-0.4-0')]
v.update(t6a_v=f(B['t6a']['DI_near']), t6a_v_ci=ci(B['t6a']['DI_near_ci95']), t6a_ve=f(B['t6a']['DI_exact']), t6a_ve_ci=ci(B['t6a']['DI_exact_ci95']),
         t6a_it=f(PH['it2a']['t6a']['DI_near']), t6a_p99=f(max(stat_p99)), t6a_ts=f(A['TS']['t6a']['DI_near'], 2),
         t6a_gib=f(A['GIB']['t6a']['DI_near']), t6a_gib_ci=ci(A['GIB']['t6a']['DI_near_ci95']),
         t6a_lang=rng([A[n]['t6a']['DI_near'] for n in LANGS], 2), t6a_eng=f(A['ENG']['t6a']['DI_near'], 2),
         t6a_naib=rng([A[n]['t6a']['DI_near'] for n in ('NAIB-lines', 'NAIB-run')], 2),
         t6b_v=f(B['t4c']['slope_1_8'], 4), t6b_v_ci=ci(B['t4c']['slope_ci95'], 4), t6b_lang=rng([A[n]['t4c']['slope_1_8'] for n in LANGS], 3),
         t6b_mk=f(A['MK-sec']['t4c']['slope_1_8'], 4), t6b_gib=f(A['GIB']['t4c']['slope_1_8'], 4), t6b_gib_ci=ci(A['GIB']['t4c']['slope_ci95'], 4))
t6c = B['t6c']
v.update(t6c_near=rng([t6c[h]['DI_near'] for h in t6c], 2), t6c_slope=rng([t6c[h]['slope_1_8'] for h in t6c], 4))
# ---------------------------------------------------------------- T7
t7a = B['t7a']
v.update(t7a_n=t7a['n_events_P'], t7a_final=t7a['position_counts'].get('final', 0), t7a_below=PH['t7a_percentile_sign_test']['below_median'],
         t7a_scored=PH['t7a_percentile_sign_test']['n'], t7a_p=f(PH['t7a_percentile_sign_test']['p_two_sided'], 4),
         t7b_rate=f(B['t7b']['rate_per_1000'], 1), t7b_rec=pc(B['t7b']['recurrence_share']), t7b_slip=pc(B['t7b']['slip_share'], 0),
         t7b_rec_nodc=pc(PH['t7b_without_double_coding']['recurrence_share']), t7b_dev=B['t7b']['deviant_types'],
         t7b_lang=f"{pc(min(A[n]['t7b']['recurrence_share'] for n in LANGS))}–{pc(max(A[n]['t7b']['recurrence_share'] for n in LANGS))}",
         t7b_lang_slip=f"{pc(min(A[n]['t7b']['slip_share'] for n in LANGS))}–{pc(max(A[n]['t7b']['slip_share'] for n in LANGS))}",
         t7b_ts=pc(A['TS']['t7b']['recurrence_share'], 0), t7b_mk=f"{pc(A['MK-sec']['t7b']['recurrence_share'])}–{pc(A['MK-page']['t7b']['recurrence_share'])}",
         t7b_naib=f"{pc(A['NAIB-lines']['t7b']['recurrence_share'])}–{pc(A['NAIB-run']['t7b']['recurrence_share'])}",
         t7b_page_v=pc(RT['VOYNICH']['recurrence_variants']['3gram_page']),
         t7b_page_lang=f"{pc(min(RT[n]['recurrence_variants']['3gram_page'] for n in LANGS))}–{pc(max(RT[n]['recurrence_variants']['3gram_page'] for n in LANGS))}",
         t7b_page_naib=pc(RT['NAIB-run']['recurrence_variants']['3gram_page']), t7b_page_hgr=pc(RT['HGR2']['recurrence_variants']['3gram_page']),
         t7b_hand=f"{pc(min(x['recurrence_share'] for x in RT['per_hand_recurrence_fullref']['nodc'].values()))}–{pc(max(x['recurrence_share'] for x in RT['per_hand_recurrence_fullref']['nodc'].values()))}")
# ---------------------------------------------------------------- E1
e1c = lambda nm, st: [E1A[f'{nm}-{s}']['stats'][st] for s in range(5)]
v.update(e1_lsg=sg(E1B['stats']['LS_graded']), e1_lsg_ci=ci(E1B['ci95']['LS_graded']), e1_ps=sg(E1B['stats']['PS']), e1_ps_ci=ci(E1B['ci95']['PS']),
         e1_ls=sg(E1B['stats']['LS']), e1_ls_ci=ci(E1B['ci95']['LS']),
         e1_wldg=f(E1B['stats']['WLD_graded']), e1_wldg_ci=ci(E1B['ci95']['WLD_graded']), e1_wpd=f(E1B['stats']['WPD']), e1_wpd_ci=ci(E1B['ci95']['WPD']),
         e1_it_lsg=sg(E1I['stats']['LS_graded']), e1_it_ps=sg(E1I['stats']['PS']),
         e1_setl_ls=f(np.mean(e1c('SET-line', 'LS')), 2), e1_setl_lsg=f(np.mean(e1c('SET-line', 'LS_graded')), 3),
         e1_setp_ps=f(np.mean(e1c('SET-para', 'PS')), 2), e1_rec_ls=f(np.mean(e1c('REC', 'LS')), 2), e1_rec_ps=f(np.mean(e1c('REC', 'PS')), 2),
         e1_mk_ls=f(np.mean(e1c('MK-sec', 'LS')), 3), e1_mk_lsg=f(np.mean(e1c('MK-sec', 'LS_graded')), 3),
         e1_wldg_ctrl=rng([x for nm in ('SET-line', 'SET-para', 'REC', 'MK-sec') for x in e1c(nm, 'WLD_graded')], 2))
# thresholds fixed in mechanism/E1_DEVIATIONS.md (entry 3) from the stratified calibration, before the Voynich run
v.update(e1_thr_l=f(-0.039), e1_thr_p=f(-0.116))
tun = json.load(open(f'{R}/e1_params.json'))
v.update(e1_sig_l=tun['SET-line'], e1_sig_p=tun['SET-para'], e1_rec=f"ρ = {tun['REC'][0]}, τ = {tun['REC'][1]:g}, e = {tun['REC'][2]}")


# ---------------------------------------------------------------- E2/E3/E6
def rep(rpt, key):
    r = rpt[key]
    rows = r['rows']
    fails = [k for k, x in rows.items() if x['pass'] is False]
    return r['n_pass'], fails


v['e2'] = rep(E2R, 'HGR')
v['e3p'] = rep(E3R, 'primary:HGR2')
v['e3s'] = rep(E3R, 'secondary:HGR2')
v['e3p_unf'] = E3R['primary:HGR2']['n_pass_unfitted']
v['e6'] = rep(E6R, 'primary:TR')
v['e6s'] = rep(E6R, 'secondary:TR')
v['e6_d4_edge'] = f(E6R['primary:D4-noK']['rows']['edge_mi']['G'], 4)
v['e6_edge_v'] = f(E6R['primary:D4-noK']['rows']['edge_mi']['V'])
v['e6_ttr'] = f(E6R['primary:TR']['rows']['ttr']['G'], 2)
v['e6_ttr_v'] = f(E6R['primary:TR']['rows']['ttr']['V'], 2)
v['e3_t2b'] = f(E3R['primary:HGR2']['rows']['T2b_T']['G'], 2)
v['e3_t2b_v'] = f(E3R['primary:HGR2']['rows']['T2b_T']['V'], 2)
v['e3_b1_t2b'] = f(E3R['primary:B1-noC1']['rows']['T2b_T']['G'], 2)
v['e3_t6b'] = f(E3R['primary:HGR2']['rows']['T6b_slope']['G'], 4)
v['e3_t6b_v'] = f(E3R['primary:HGR2']['rows']['T6b_slope']['V'], 4)
v['e3_rec'] = pc(E3R['primary:HGR2']['rows']['T7b_rec']['G'])
v['e3_rec_v'] = pc(E3R['primary:HGR2']['rows']['T7b_rec']['V'])
v['e3_t3a'] = f(E3R['primary:HGR2']['rows']['T3a_rho']['G'])
v['e3_t3a_v'] = f(E3R['primary:HGR2']['rows']['T3a_rho']['V'])
allrec = [x['rows']['T7b_rec']['G'] for rp in (E2R, E3R, E6R) for x in rp.values()]
v['gen_rec'] = f'{pc(min(allrec))}–{pc(max(allrec))}'
allt6b = [x['rows']['T6b_slope']['G'] for rp in (E2R, E3R, E6R) for x in rp.values()]
v['gen_t6b'] = f'{f(min(allt6b), 4)} to {f(max(allt6b), 4)}'
v['e3_params'] = E3F['primary:HGR2']['params']
# ---------------------------------------------------------------- E4 / E5
v.update(e4_L=sg(E4B['L'], 4), e4_L_ci=ci(E4B['L_ci95'], 4), e4_S=sg(E4B['S'], 4), e4_S_ci=ci(E4B['S_ci95'], 4),
         e4_lang_S={n: sg(E4A[n]['S'], 4) for n in LANGS}, e4_lang_L={n: sg(E4A[n]['L'], 4) for n in LANGS},
         e4_vb_S=sg(E4A['VB-run']['S'], 4), e4_vb_S_ci=ci(E4A['VB-run']['S_ci95'], 4), e4_naib_S=sg(E4A['NAIB-run']['S'], 4), e4_naib_L=sg(E4A['NAIB-run']['L'], 4),
         e4_vb_L=sg(E4A['VB-run']['L'], 4), e4_gd_S=sg(E4A['GDRIFT']['S'], 4), e4_ld_S=sg(E4A['LDRIFT']['S'], 4), e4_ld_L=sg(E4A['LDRIFT']['L'], 4),
         e4_ita_lo=f(E4A['ITA']['S_ci95'][0], 4))
v.update(e5_G=sg(E5B['G'], 3), e5_G_ci=ci(E5B['G_ci95']), e5_it_G=sg(E5I['G'], 3), e5_B={k: f(x, 2) for k, x in E5B['B'].items()},
         e5_lang_G=f"{sg(min(E5A[n]['G'] for n in LANGS), 2)} to {sg(max(E5A[n]['G'] for n in LANGS), 2)}", e5_vb_G=sg(E5A['VB-run']['G'], 2),
         e5_naib_G=sg(E5A['NAIB-run']['G'], 2), e5_rep_G=sg(E5A['REP']['G'], 2), e5_ld_G=sg(E5A['LDRIFT']['G'], 2), e5_hgr_G=sg(E5A['HGR2']['G'], 2),
         e5_lang_VF=f"{f(min(E5A[n]['B']['VF'] for n in LANGS), 2)}–{f(max(E5A[n]['B']['VF'] for n in LANGS), 2)}",
         e5_lang_R=f"{f(min(E5A[n]['B']['R'] for n in LANGS), 1)}–{f(max(E5A[n]['B']['R'] for n in LANGS), 1)}",
         e5_VF_ci=ci(E5B['B_ci95']['VF'], 2), e5_lang_lo=f(min(E5A[n]['G_ci95'][0] for n in LANGS), 2), e5_hgr_R=f(E5A['HGR2']['B']['R'], 2))
# ---------------------------------------------------------------- E7
rec = E7['recovery']
lz = [rec[k] for k in rec if k.startswith('lzma')]
raw = [rec[k] for k in rec if k.startswith('raw')]
v.update(e7_bpg=f(np.mean([r['bits_per_glyph'] for r in lz]), 2), e7_bpt=f(np.mean([r['bits_per_token'] for r in lz]), 1),
         e7_kb=f(np.mean([r['plaintext_bytes_carried'] for r in lz]) / 1000, 0), e7_bits=f"{int(np.mean([r['bits_consumed'] for r in lz])):,}",
         e7_mism=sum(r['mismatches'] for r in lz + raw), e7_lz_agree=E7['lzma']['agree'], e7_raw_agree=E7['raw']['agree'], e7_n=E7['lzma']['n'],
         e7_lz_dis=', '.join(STAT[k] for k in E7['lzma']['disagree']), e7_raw_dis=', '.join(STAT[k] for k in E7['raw']['disagree']),
         e7_tm_a=f(E7C['prng_mean'], 3), e7_tm_asd=f(E7C['prng_sd'], 3), e7_tm_b=f(E7C['lzma_mean'], 3), e7_tm_bsd=f(E7C['lzma_sd'], 3), e7_tm_p=f(E7C['welch_p'], 2),
         e7_latin_chars=f"{int(rec['lzma:LAT']['plaintext_bytes_carried'] * os.path.getsize('data/ref/la_caesar.txt') / (rec['lzma:LAT']['bits_available'] / 8) / 1000):,}")

# ---------------------------------------------------------------- revision analyses (mechanism/REVISION_PLAN.md)
RV = lambda n: json.load(open(f'{R}/revision/{n}.json'))
R1, R2, R3 = RV('r1'), RV('r2'), RV('r3')
E7B, E8R = L('e7b/report.json'), L('e8/report.json')
v.update(r1_n=R1['n_writers'], r1_below=R1['below_p05'], r1_min=f(R1['writer_t3b']['min'], 2), r1_max=f(R1['writer_t3b']['max'], 2),
         r1_vmed=rng([w['v_t3b_median'] for w in R1['writers']], 2), r1_vp05=rng([w['v_t3b_p05'] for w in R1['writers']], 2),
         r1_rho=sum(1 for w in R1['writers'] if w['t3a_pct_ge'] is not None and w['t3a_pct_ge'] < 0.05))
_dev = max(abs(R2['R2c']['shares'][t] - R2['R2c']['expected'][t]) for t in R2['R2c']['shares'])
v.update(r2_uni=f(R2['R2a']['unigram_share'], 3), r2_valid=pc(R2['R2b']['share_valid'], 1), r2_ntok=f"{R2['R2b']['aligned']:,}",
         r2_dev=f(_dev, 3), r2_pass=R2['R2d']['n_pass'], r2_n=R2['R2d']['n'],
         r2_hap_a=f(R2['R2d']['rows']['hapax']['author'], 3), r2_hap_o=f(R2['R2d']['rows']['hapax']['ours_mean'], 3),
         r3_t6a=f(R3['T6a_near'], 3), r3_edge=f(R3['edge_mi'], 4), r3_page=f(R3['page_mi'], 3), r3_hap=f(R3['hapax'], 2),
         r3_S=sg(R3['E4']['S'], 4), r3_rec=pc(R3['T7b_rec']), r3_ok=R3['exclusion_holds'], r3_tok=f"{R3['tokens']:,}")


def mimic(rep, kind='lzma'):
    k, r = rep[kind], rep['recovery'][kind]
    return dict(runs=k['n_runs'], base=rep['n_base'], holm=len(k['holm_significant']), unadj=len(k['unadjusted_p05']), n=k['n_stats'],
                tol=k['tolerance_agree'], minp=f(k['min_p'], 3), mism=r['total_mismatches'], bpg=f(r['bits_per_glyph_mean'], 2),
                kb=f(r['bits_consumed_mean'] / 8 / 1000, 0))


v['e7b'], v['e7b_raw'], v['e8'] = mimic(E7B), mimic(E7B, 'raw'), mimic(E8R)

# ---------------------------------------------------------------- table and figure numbers (order of first appearance)
MAIN_T = ['p_mech_small', 'framework', 'calib', 'battery', 'e1', 'gen', 'e45', 'cls', 'excl', 'e7', 'e78', 'redteam']
SUPP_T = ['p_basic', 'p_proj', 'p_lineunit', 'p_spaces', 'p_lexicon', 'p_entropy', 'p_mech', 'p_hier', 'p_naibbe_var', 'p_transcr', 'p_robust', 'p_jack',
          'p_drift', 'p_hand', 'p_tvi', 'p_pc', 'p_feat', 'p_sect', 'p_labels', 'p_agree', 'p_direction', 'p_vertical', 'p_pmi', 'p_pos', 'p_combo', 'p_bpe',
          's_dev', 's_prereg', 's_fits', 's_e2', 's_e3', 's_e6', 's_e5', 's_e4', 's_r1', 's_r2', 's_r3', 's_mimic']
TN = {k: str(i + 1) for i, k in enumerate(MAIN_T)}
TN.update({k: f'S{i + 1}' for i, k in enumerate(SUPP_T)})
FN = {k: str(i + 1) for i, k in enumerate(['profile', 'constraints', 'line_endings', 'recency', 'heldout', 'drift', 'e7'])}


# ---------------------------------------------------------------- tables


def table(head, rows, caption, note=None, cls=''):
    h = ''.join(f'<th>{x}</th>' for x in head)
    b = ''.join('<tr>' + ''.join(f'<td>{c}</td>' for c in r) + '</tr>' for r in rows)
    n = f'<p class="tabnote">{note}</p>' if note else ''
    return f'<p class="cap">{caption}</p><table class="tab {cls}"><tr>{h}</tr>{b}</table>{n}'


T = {}
pv, PT = profile_analysis.build(TN, table, f, sg, pc)
T.update({'p_' + k: x for k, x in PT.items()})
T['framework'] = table(
    ['Axis', 'Hypothesis', 'Operational definition', 'Signature predicted in advance'],
    [['Generation', 'P, fixed procedure', 'explicit rules plus an external randomiser or schedule; no free choices; parameters change only at discrete points', 'hard zeros; stationarity within a setting; possible device periodicity; slip-like deviations'],
     ['', 'I, skilled improvisation', 'internalised, soft habits of a writer producing pseudo-text online', 'priming; smooth drift; innovations that recur; sensitivity to layout'],
     ['', 'C, plaintext-driven procedure', 'explicit rules whose choices are driven by a plaintext (natural language as identity mapping)', 'content-driven recurrence and topic structure; no fixed prediction for randomised encodings'],
     ['Transmission', 'D', 'composed directly on the page', 'line-aware forms tied to the page\'s own lines'],
     ['', 'K-reflow', 'copied from a draft with different line breaks', 'no line-final forms; breaks as transparent as word boundaries'],
     ['', 'K-same', 'copied from a draft with the same line breaks', 'not separable from D by the transliteration (stated in advance)']],
    f'Table {TN["framework"]}. Hypotheses and their operational definitions as pre-specified. The two axes are independent.')
T['calib'] = table(
    ['Test', 'Calibration requirement', 'Outcome'],
    [['T1 break coupling', 'greedily wrapped Latin R ≥ 0.5', f"R = {v['t1_latw']} (SE {v['t1_latw_se']}): met, very noisy"],
     ['T2a final form', 'no effect in wrapped Latin', f"excess {v['t2a_latw']}, p = {v['t2a_latw_p']}: met"],
     ['T2b line fill', 'wrapped Latin T within 0.9–1.1', f"T = {v['t2b_latw']} {v['t2b_latw_ci']}: met"],
     ['T4 periodicity', 'power against a periodic device', f"mixing weight 0.1: {pw['0.1'][0]}/10, {pw['0.1'][1]}/10, {pw['0.1'][2]}/10; 0.2: {pw['0.2'][0]}/10, {pw['0.2'][1]}/10, {pw['0.2'][2]}/10; 0.4: {pw['0.4'][0]}/10, {pw['0.4'][1]}/10, {pw['0.4'][2]}/10 (lag, column, line-cycle tests)"],
     ['T5 drift shape', 'smooth control S > 1, step control S < 1', f"{v['t5_smooth']} and {v['t5_step']}: met"],
     ['T6a recency', 'stationary procedures near 0', f"highest 99th percentile {v['t6a_p99']}: met"],
     ['E1 boundary steps', 'settings controls step, recency control does not', 'met after position stratification (deviation, before the Voynich run)'],
     ['E4 drift', '≥ 3 languages with lexical drift; glyph-drift control sublexical; vocabulary-drift control lexical only', 'met'],
     ['E5 burstiness', '≥ 3 languages with positive gradient; Naibbe closer to 1', 'met (quire jackknife; deviation, before the Voynich run)']],
    f'Table {TN["calib"]}. Calibration requirements on controls with known mechanism. A falsifier is applied only when its calibration holds.')
T['battery'] = table(
    ['Test', 'Voynich (ZL3b)', 'Takahashi', 'Key controls', 'Reading'],
    [['T1 line-break ratio', f"{v['t1_v']} (SE {v['t1_v_se']})", f"{v['t1_it']} ({v['t1_it_se']})", f"gibberish {v['t1_gib']} ({v['t1_gib_se']}); automaton {v['t1_mk']}; copy-and-modify {v['t1_ts']}", 'strongly reduced coupling; K-reflow falsifier not triggered'],
     ['T2a final form, margin', f"{v['t2a_m']}, p = {v['t2a_m_p']}", v['t2a_it'], f"gibberish {v['t2a_gib_m']}; wrapped Latin {v['t2a_latw']}", 'K-reflow falsified'],
     ['T2a final form, paragraph end', f"{v['t2a_p']}, p = {v['t2a_p_p']}", '–', f"gibberish {v['t2a_gib_p']}", 'weaker than at the margin'],
     ['T2b line-fill slack', f"{v['t2b_v']} {v['t2b_v_ci']}", '–', f"gibberish {v['t2b_gib']} {v['t2b_gib_ci']}", 'more regular fill than naive online writers'],
     ['T2c dittography', f"{v['t2c_v']}, p = {v['t2c_v_p']}", '–', f"copy-and-modify {v['t2c_ts']}, p = {v['t2c_ts_p']}", 'no copying signature'],
     ['T3a zero replication (250 tokens)', f"{v['t3a_v']} {v['t3a_v_ci']}", v['t3a_it'], f"gibberish {v['t3a_gib']}; languages {v['t3a_lang']}; generators {v['t3a_gen']}", 'harder at short range; naive improvisation falsified'],
     ['T3b slot consistency', f"{v['t3b_v']} {v['t3b_v_ci']}", v['t3b_it'], f"gibberish {v['t3b_gib']}; languages {v['t3b_lang']}", 'rigid slot order'],
     ['T3c final-position entropy', v['t3c_v'], '–', f"Naibbe {v['t3c_naib']}; automaton {v['t3c_mk']}; languages {v['t3c_lang']}; gibberish {v['t3c_gib']}", 'collapse (Kinnison 2026) reproduced by cipher and automaton'],
     ['T4 periodicity', 'no peak', 'no peak', 'device detected from weight 0.2', 'device variants ≥ 0.2 excluded'],
     ['T5 drift shape S', v['t5_v'], v['t5_it'], f"smooth {v['t5_smooth']}; step {v['t5_step']}; section automaton {v['t5_mk']}", 'step-like (hands 2 and 3)'],
     ['T6a recency (near)', f"{v['t6a_v']} {v['t6a_v_ci']}", v['t6a_it'], f"stationary 99th pct ≤ {v['t6a_p99']}; copy-and-modify {v['t6a_ts']}; English {v['t6a_eng']}", 'stationary procedures falsified'],
     ['T6b within-page drift', f"{v['t6b_v']} {v['t6b_v_ci']}", f(PH['it2a']['t4c']['slope_1_8'], 4), f"automaton {v['t6b_mk']}; languages {v['t6b_lang']}", 'drift of natural-language strength'],
     ['T7b deviant recurrence', f"{v['t7b_rec']} (slip share {v['t7b_slip']})", pc(PH['it2a']['t7b']['recurrence_share']), f"languages {v['t7b_lang']}; copy-and-modify {v['t7b_ts']}; automata {v['t7b_mk']}; Naibbe {v['t7b_naib']}", 'rare forms not reused']],
    f'Table {TN["battery"]}. The pre-specified battery on the Voynich text (Stage B) with the controls that calibrate each reading. Intervals are 95%.',
    'Takahashi values are post hoc replications with identical code.')
m1 = lambda nm, st, d=3: f(np.mean(e1c(nm, st)), d)
T['e1'] = table(
    ['Statistic', 'Voynich', 'Takahashi', 'Settings per line', 'Settings per paragraph', 'Recency', 'Automaton'],
    [['line step, graded', f"{v['e1_lsg']} {v['e1_lsg_ci']}", v['e1_it_lsg']] + [m1(nm, 'LS_graded') for nm in ('SET-line', 'SET-para', 'REC', 'MK-sec')],
     ['line step, binary', f"{v['e1_ls']} {v['e1_ls_ci']}", sg(E1I['stats']['LS'])] + [m1(nm, 'LS') for nm in ('SET-line', 'SET-para', 'REC', 'MK-sec')],
     ['paragraph step', f"{v['e1_ps']} {v['e1_ps_ci']}", v['e1_it_ps']] + [m1(nm, 'PS') for nm in ('SET-line', 'SET-para', 'REC', 'MK-sec')],
     ['within-line decay, graded', f"{v['e1_wldg']} {v['e1_wldg_ci']}", f(E1I['stats']['WLD_graded'])] + [m1(nm, 'WLD_graded') for nm in ('SET-line', 'SET-para', 'REC', 'MK-sec')],
     ['within-paragraph decay', f"{v['e1_wpd']} {v['e1_wpd_ci']}", f(E1I['stats']['WPD'])] + [m1(nm, 'WPD') for nm in ('SET-line', 'SET-para', 'REC', 'MK-sec')]],
    f'Table {TN["e1"]}. E1: steps in pair similarity at line and paragraph boundaries at matched token distance, with position-stratified expectations. Control values are means over 5 seeds; intervals are 95% page-bootstrap intervals.')
gen_rows = [['E2', 'hard grammar + recency + session state', f"{v['e2'][0]}/40", '–', '; '.join(STAT[k] for k in v['e2'][1])],
            ['E3', '+ margin-driven endings, slips, drift, temperature', f"{v['e3p'][0]}/40 ({v['e3p_unf']}/31 unfitted)", f"{v['e3s'][0]}/40", '; '.join(STAT[k] for k in v['e3p'][1])],
            ['E6', 'two routes: drifting repertoire + one-off coinage', f"{v['e6'][0]}/40", f"{v['e6s'][0]}/40", '; '.join(STAT[k] for k in v['e6'][1][:10]) + '; …']]
T['gen'] = table(['Exp.', 'Generator', 'Held-out pass (primary)', 'Secondary', 'Failing statistics (primary)'], gen_rows,
                 f'Table {TN["gen"]}. Explicit generators of the surviving class, fitted on one half of the manuscript (bifolio parity) and tested on the other against 40 statistics.',
                 'E2 was fitted on odd and tested on even bifolios. E3 and E6 were cross-fitted, and their primary direction (fit on even, test on odd) used Voynich values not computed before.')
cls_rows = [
    ['C1', 'Rigid slot order within words; transition zeros consistent within short stretches', f"T3b {v['t3b_v']} vs gibberish {v['t3b_gib']}, languages {v['t3b_lang']}; T3a (250 tokens) {v['t3a_v']} vs {v['t3a_gib']}, {v['t3a_lang']}; pruning necessary (E2)", 'strong (T3b); moderate (T3a: not at full size)'],
    ['C2', 'Cross-token boundary dependency within lines (last glyph of a token, first glyph of the next), strongly reduced across line breaks', f"boundary MI {v['e6_edge_v']}; T1 ratio about 0.03 (pooled) to {v['t1_v']} (page-conditional); boundary rule necessary (E6: {v['e6_d4_edge']} without)", 'strong within lines; moderate at breaks'],
    ['C3', 'Margin-associated line-final forms, weaker at paragraph ends', f"T2a {v['t2a_m']} vs {v['t2a_p']}, difference {v['t2a_diff']} {v['t2a_diff_ci']}; stars section {v['t2a_star_m']} vs {v['t2a_star_p']}; necessary in E3", 'strong'],
    ['C4', 'Short-range recency, continuous across line and paragraph boundaries', f"T6a {v['t6a_v']} > {v['t6a_p99']}; E1 no steps; within-line decay {v['e1_wldg']}; necessary in E2", 'strong'],
    ['C5', 'Page- and quire-level variation in the weights of shared forms', f"T5 S = {v['t5_v']}; E5 very frequent forms clustered {v['e5_B']['VF']} vs languages {v['e5_lang_VF']} (descriptive); quire-level state necessary in the generator (E2)", 'moderate (hand 1 smooth)'],
    ['C6', 'Within-page drift of natural-language strength, mainly lexical', f"T6b {v['t6b_v']}; E4 L = {v['e4_L']}, S = {v['e4_S']}", 'strong (existence); undetermined (source)'],
    ['C7', 'Very low recurrence of locally deviant forms', f"T7b {v['t7b_rec']} vs languages {v['t7b_lang']}, copy-and-modify {v['t7b_ts']}, generators {v['gen_rec']}; page-level variant {v['t7b_page_v']}", 'strong; shared with homophonic ciphers'],
    ['C8', 'No periodicity of the tested kind', 'T4, power from mixing weight 0.2 (period 5, cycle 4)', 'moderate (tested design only)'],
    ['C9', 'No detected copying signature; copying from a re-lined draft excluded', f"T2c {v['t2c_v']}; no word-level corrections among {v['t7a_n']}; T2a", 'moderate (T7a thin)']]
T['e45'] = table(['Corpus', 'Lexical drift L (E4)', 'Sublexical drift S (E4)', 'Burstiness gradient G (E5)', 'Clustering of forms ≥100 (E5)'],
                 [[name, sg(E4.get('L'), 4) if E4 else '–', sg(E4.get('S'), 4) if E4 else '–', sg(E5['G'], 2) if E5 else '–', f(E5['B']['VF'], 2) if E5 else '–']
                  for name, E4, E5 in [('Voynich', E4B, E5B)] + [(LN[n], E4A[n], E5A[n]) for n in LANGS] +
                  [('verbose cipher (Latin)', E4A['VB-run'], E5A['VB-run']), ('Naibbe (Latin)', E4A['NAIB-run'], E5A['NAIB-run']),
                   ('glyph-habit drift', E4A['GDRIFT'], None), ('vocabulary drift', E4A['LDRIFT'], E5A['LDRIFT']),
                   ('repertoire + coinage', None, E5A['REP']), ('glyph generator (E3)', None, E5A['HGR2']), ('order-3 automaton', E4A['MK-sec'], E5A['MK-sec'])]],
                 f'Table {TN["e45"]}. E4 and E5: where the within-page drift and the page clustering live. Intervals in Tables {TN["s_e5"]} and {TN["s_e4"]}.')
T['cls'] = table(['#', 'Property', 'Evidence', 'Strength'], cls_rows, f'Table {TN["cls"]}. The nine properties that define the mechanism class, stated as measured, with their evidence and an explicit strength label. Causal readings of these properties are discussed in Section 9.')
T['excl'] = table(['Status', 'Mechanism variant', 'Decisive evidence'], [
    ['Excluded', 'naive improvisation (Gaskell & Bowern-type samples)', 'T3a, T3b'],
    ['Excluded', 'stationary procedures (tables, grilles, automata, devices constant within a page)', 'T6a'],
    ['Excluded', 'periodic devices of the tested design (period 5, cycle 4) with mixing weight ≥ 0.2', 'T4'],
    ['Excluded', 'improvisation with smooth drift across pages', 'T5'],
    ['Excluded', 'settings per line or paragraph as the source of the local dynamics', 'E1'],
    ['Excluded', 'copy-and-modify with propagating innovations and vertical copying', 'T7b, T2c, T4b'],
    ['Excluded', 'the tested natural-language controls, and systems that preserve lexical identity at the observed token boundaries', 'T3b, T7b'],
    ['Excluded', 'the Naibbe cipher as published', 'T6a, E4; boundary MI, hapax share and page MI (Section 3.3)'],
    ['Excluded', 'copying from a draft with different line breaks', 'T2a'],
    ['Unresolved', 'explicit rule set with randomiser vs. practised habit', 'same generator describes both'],
    ['Unresolved', 'message carried by the free choices (mimic-function encoding)', 'E7: not identifiable from text'],
    ['Unresolved', 'direct composition vs. copying with identical line breaks', 'not separable by the transliteration'],
    ['Open', 'a generator reproducing C6 and C7 together', f"best explicit generator {v['e3p'][0]}/40"]],
    f'Table {TN["excl"]}. What is excluded, and what remains open. "Excluded" means that a pre-specified falsifier was triggered under calibration; it applies to the variant as defined and tested. "Unresolved" entries are shown to be undecidable from the text, or not decidable with the data used here. E5 was undetermined by its own rule and is not used as evidence here.')
T['e7'] = table(['Condition', 'Bits consumed', 'Bits per glyph', 'Recovery mismatches', 'Statistics agreeing with random driving'],
                [[k.replace('lzma:', 'compressed ').replace('raw:', 'raw ').replace('LAT', 'Latin').replace('ITA', 'Italian').replace('GER', 'German'),
                  f"{r['bits_consumed']:,}", f(r['bits_per_glyph'], 2), r['mismatches'],
                  (f"{E7['lzma']['agree']}/{E7['lzma']['n']}" if k.startswith('lzma') else f"{E7['raw']['agree']}/{E7['raw']['n']}")] for k, r in rec.items()],
                f'Table {TN["e7"]}. E7: message-driven output of the order-3 glyph process. Bits per glyph are bits consumed divided by the number of EVA characters generated, spaces excluded. Agreement counts are per condition group (3 plaintexts against 3 random seeds).')
T['e78'] = table(['Process', 'Message', 'Runs (message / random)', 'Bits per glyph', 'Recovery errors', 'Holm-significant', 'Unadjusted p < 0.05', 'Tolerance rule'],
                 [['order-3 automaton (E7)', 'compressed', '3 / 3', v['e7_bpg'], sum(r['mismatches'] for r in lz), '–', '–', f"{v['e7_lz_agree']}/{v['e7_n']}"],
                  ['order-3 automaton (E7, 20 runs)', 'compressed', f"{v['e7b']['runs']} / {v['e7b']['base']}", v['e7b']['bpg'], v['e7b']['mism'], f"{v['e7b']['holm']}/{v['e7b']['n']}", f"{v['e7b']['unadj']}/{v['e7b']['n']}", f"{v['e7b']['tol']}/{v['e7b']['n']}"],
                  ['order-3 automaton (E7, 20 runs)', 'raw text bits', f"{v['e7b_raw']['runs']} / {v['e7b_raw']['base']}", v['e7b_raw']['bpg'], v['e7b_raw']['mism'], f"{v['e7b_raw']['holm']}/{v['e7b_raw']['n']}", f"{v['e7b_raw']['unadj']}/{v['e7b_raw']['n']}", f"{v['e7b_raw']['tol']}/{v['e7b_raw']['n']}"],
                  ['E3 generator (E8)', 'compressed', f"{v['e8']['runs']} / {v['e8']['base']}", v['e8']['bpg'], v['e8']['mism'], f"{v['e8']['holm']}/{v['e8']['n']}", f"{v['e8']['unadj']}/{v['e8']['n']}", f"{v['e8']['tol']}/{v['e8']['n']}"]],
                 f'Table {TN["e78"]}. Message-driven against randomly driven output over the 40 statistics. Holm-significant: Welch tests (Fisher for T4) with Holm correction at α = 0.05; about 2 unadjusted p < 0.05 are expected by chance among 40. The 20-run analyses and E8 were pre-specified in mechanism/REVISION_PLAN.md (R4). E8 carries the message only in choices the receiver can observe, so its capacity is lower.')
T['redteam'] = table(['Claim', 'Attack', 'Check', 'Result'], [
    ['C3 margin-associated endings', 'margin and paragraph effects not actually different', 'page bootstrap of the difference', f"{v['t2a_diff']} {v['t2a_diff_ci']}"],
    ['C3', 'lines end at drawings, not margins', 'text-only stars section', f"margin {v['t2a_star_m']} vs paragraph {v['t2a_star_p']} (n = {v['t2a_star_mn']}, {v['t2a_star_pn']})"],
    ['C1 rigidity', 'artefact of multigraph segmentation', 'raw EVA characters', f"Voynich {v['t3a_raw_v']} / {v['t3b_raw_v']} vs gibberish {v['t3a_raw_gib']} / {v['t3b_raw_gib']}"],
    ['C1 hardness', 'depends on sample size', 'full-size zero replication', f"Voynich {v['t3a_full_v']} vs languages {v['t3a_full_lang']}: no separation at full size"],
    ['C1, C3, C4', 'driven by one scribe', 'per hand (1, 2, 3)', f"T3a {v['hand_t3a']}; T3b {v['hand_t3b']}; T6a {v['hand_t6a']}; T2a {v['hand_t2a']}"],
    ['C7 low recurrence of deviant forms', 'depends on deviance definition', 'page-level blocks', f"Voynich {v['t7b_page_v']} vs languages {v['t7b_page_lang']}, generator {v['t7b_page_hgr']}, Naibbe {v['t7b_page_naib']}"],
    ['C7', 'depends on double coding or on one hand', 'no double coding; per hand, whole-text reference', f"{v['t7b_rec_nodc']}; hands {v['t7b_hand']}"],
    ['E7', 'single disagreement is a real trace', '8 runs per condition', f"word-pair MI {v['e7_tm_a']} ± {v['e7_tm_asd']} vs {v['e7_tm_b']} ± {v['e7_tm_bsd']}, p = {v['e7_tm_p']}"],
    ['All', 'transliteration choice', 'Takahashi transliteration', 'T3a, T3b, T5, T6a, T7b, T2a, E1, E5 replicate'],
    ['C1 rigidity', 'mean over writers hides writers as rigid as the Voynich text', 'each writer against Voynich stretches of the same length (R1)', f"{v['r1_below']} of {v['r1_n']} writers below the 5th percentile; writers {v['r1_min']}–{v['r1_max']}"],
    ['Naibbe exclusion', 'the reimplementation differs from the published cipher', "author's own ciphertext (R2, R3)", f"mapping {v['r2_valid']} valid, {v['r2_pass']}/{v['r2_n']} statistics agree; author's output: T6a {v['r3_t6a']}, boundary MI {v['r3_edge']}, page MI {v['r3_page']}"],
    ['E7', 'three runs per condition are too few', '20 runs per condition (R4a)', f"Holm-significant {v['e7b']['holm']}/{v['e7b']['n']}; unadjusted p < 0.05 {v['e7b']['unadj']}/{v['e7b']['n']}"],
    ['E7', 'only the simplest process was tested', 'message through the E3 generator (E8, R4b)', f"Holm-significant {v['e8']['holm']}/{v['e8']['n']}; recovery errors {v['e8']['mism']}"]],
    f'Table {TN["redteam"]}. Red-team checks. The first nine were run before writing and are post hoc. The last four respond to a review: R1 is post hoc; R2–R4 were pre-specified in mechanism/REVISION_PLAN.md before computation.')

# ---------------------------------------------------------------- supplement tables
def held_table(rpt, keys, names, caption):
    stats = list(rpt[keys[0]]['rows'].keys())
    V = rpt[keys[0]]['rows']
    rows = []
    for s in stats:
        row = [STAT[s] + (' †' if s in FITTED else ''), f(V[s]['V'], 4) if V[s]['V'] is not None else 'n/a']
        for k in keys:
            r = rpt[k]['rows'][s]
            row.append((f(r['G'], 4) if r['G'] is not None else 'n/a') + (' ✓' if r['pass'] else ' ✗'))
        rows.append(row)
    return table(['Statistic', 'Voynich'] + names, rows, caption, '† fitting target on the training half. ✓ within tolerance 2√(SE² + SD²) + 1%.', cls='small')


T['s_e2'] = held_table(E2R, ['HGR', 'A1-norecency', 'A2-noprune-noslip', 'A3-nosession', 'A0-baseline'],
                       ['full', 'no recency', 'no pruning', 'no session', 'plain automaton'], f'Table {TN["s_e2"]}. E2: held-out statistics (test: even bifolios).')
T['s_e3'] = held_table(E3R, ['primary:HGR2', 'primary:B1-noC1', 'primary:B2-noC2', 'primary:B3-noC3', 'primary:B0-E2class'],
                       ['full', 'no margin rule', 'no drift', 'no slips etc.', 'E2 class'], f'Table {TN["s_e3"]}. E3 primary direction (fit even, test odd).')
T['s_e6'] = held_table(E6R, ['primary:TR', 'primary:D1-nocoin', 'primary:D2-norepvar', 'primary:D3-norecency', 'primary:D4-noK'],
                       ['two-route', 'no coinage', 'no repertoire variation', 'no recency', 'no boundary rule'], f'Table {TN["s_e6"]}. E6 primary direction (fit even, test odd).')
T['s_fits'] = table(['Model', 'Fitted parameters (training half)'],
                    [['E2 HGR', ', '.join(f'{k} = {x}' for k, x in E2F['HGR']['params'].items())],
                     ['E3 HGR2 (fit even)', ', '.join(f'{k} = {x}' for k, x in E3F['primary:HGR2']['params'].items())],
                     ['E3 HGR2 (fit odd)', ', '.join(f'{k} = {x}' for k, x in E3F['secondary:HGR2']['params'].items())],
                     ['E6 TR (fit even)', ', '.join(f'{k} = {x}' for k, x in E6F['primary:TR']['params'].items())]],
                    f'Table {TN["s_fits"]}. Fitted generator parameters. λ (lam): quire session weight; σ (sig): page tilt; σ_w (sigw): line-to-line drift; ρ, τ, e: recency rate, range, exact share; ε (eps): slip rate; m: pruning threshold; θ (theta): choice temperature; c: coinage rate; sq, sp, sw: quire, page and line variation of repertoire weights.', cls='small')
T['s_e5'] = table(['Corpus', 'G', 'B 2–4', 'B 5–19', 'B 20–99', 'B ≥ 100'],
                  [[n, sg(r['G'], 2) + ' ' + ci(r['G_ci95'], 2)] + [f(r['B'][b], 2) for b in ('R', 'M', 'F', 'VF')]
                   for n, r in [('Voynich', E5B), ('Voynich (Takahashi)', E5I)] + [(LN.get(k, k), E5A[k]) for k in ('LAT', 'ITA', 'GER', 'ENG', 'VB-run', 'NAIB-run', 'LDRIFT', 'REP', 'HGR2', 'MK-sec')]],
                  f'Table {TN["s_e5"]}. E5: page clustering index B by frequency band and gradient G with quire-jackknife 95% intervals.', cls='small')
T['s_e4'] = table(['Corpus', 'L (lexical)', 'S (sublexical)'],
                  [[n, sg(r['L'], 4) + ' ' + ci(r['L_ci95'], 4), sg(r['S'], 4) + ' ' + ci(r['S_ci95'], 4)]
                   for n, r in [('Voynich', E4B)] + [(LN.get(k, k), E4A[k]) for k in ('LAT', 'ITA', 'GER', 'ENG', 'VB-run', 'NAIB-run', 'GDRIFT', 'LDRIFT', 'MK-sec')]],
                  f'Table {TN["s_e4"]}. E4: drift slopes of line similarity over line distance 2–8 with page-bootstrap 95% intervals.', cls='small')
T['s_r1'] = table(['Writer', 'Tokens', 'T3b writer', 'Voynich T3b, median (5th pct.)', 'Percentile of writer', 'T3a writer', 'Voynich T3a median'],
                  [[w['writer'], w['tokens'], f(w['t3b']), f"{f(w['v_t3b_median'])} ({f(w['v_t3b_p05'])})", pc(w['t3b_pct'], 0), f(w['t3a']), f(w['v_t3a_median'])]
                   for w in R1['writers']],
                  f'Table {TN["s_r1"]}. R1 (post hoc): each gibberish writer against 50 contiguous Voynich stretches of the same length within one hand. Percentile: share of Voynich stretches with slot consistency at or below the writer\'s. Verdict by the rule fixed in REVISION_PLAN.md: {R1["verdict"]}.', cls='small')
T['s_r2'] = table(['Statistic', "Author's ciphertext", 'Our reimplementation (5 seeds)', 'Within tolerance'],
                  [[STAT.get(k, k) if k in STAT else {'types': 'type count', 'wlen': 'mean token length', 'T3c_e1': 'final-position entropy (T3c)', 'T3c_s1': 'initial-position entropy (T3c)'}.get(k, k),
                    (f"{r['author']:,.0f}" if k == 'types' else f(r['author'], 4)),
                    (f"{r['ours_mean']:,.0f} ± {r['ours_sd']:.0f}" if k == 'types' else f"{f(r['ours_mean'], 4)} ± {f(r['ours_sd'], 4)}"),
                    'yes' if r['pass'] else 'no'] for k, r in R2['R2d']['rows'].items()],
                  f'Table {TN["s_r2"]}. R2: our Naibbe reimplementation enciphering the author\'s tokenised plaintext (Pliny, <i>Natural History</i> 16), against the author\'s published ciphertext (github.com/greshko/naibbe-cipher, commit f2675ec). Also: one-letter token share {v["r2_uni"]} (expected 0.472); {v["r2_valid"]} of {v["r2_ntok"]} ciphertext tokens are valid table outputs for their plaintext token; table shares within {v["r2_dev"]} of the deck proportions. Validated by the pre-specified rule: {"yes" if R2["validated"] else "no"}.', cls='small')
_r3ref = R3['reference']
T['s_r3'] = table(['Statistic', "Author's ciphertext", 'Our reimplementation', 'Voynich (95% interval)'],
                  [['T6a near recency', f(R3['T6a_near'], 3), f(_r3ref['ours_run']['T6a_near'], 3), f"{f(_r3ref['voynich']['T6a_near'], 3)} {ci(_r3ref['voynich']['T6a_near_ci95'])}"],
                   ['boundary MI', f(R3['edge_mi'], 4), f(_r3ref['ours_run']['edge_mi'], 4), f"{f(_r3ref['voynich']['edge_mi'], 3)} {ci(_r3ref['voynich']['edge_mi_ci95'])}"],
                   ['page MI', f(R3['page_mi'], 3), f(_r3ref['ours_run']['page_mi'], 3), f"{f(_r3ref['voynich']['page_mi'], 3)} {ci(_r3ref['voynich']['page_mi_ci95'])}"],
                   ['hapax share', f(R3['hapax'], 2), f(_r3ref['ours_run']['hapax'], 2), pv['vms_hap']],
                   ['E4 sublexical drift S', sg(R3['E4']['S'], 4) + ' ' + ci(R3['E4']['S_ci95'], 4), sg(_r3ref['ours_run']['E4']['S'], 4), v['e4_S'] + ' ' + v['e4_S_ci']],
                   ['T7b recurrence of deviant forms', pc(R3['T7b_rec']), pc(_r3ref['ours_run']['T7b_rec']), v['t7b_rec']]],
                  f'Table {TN["s_r3"]}. R3: the statistics behind the Naibbe exclusion, computed on the author\'s own ciphertext cut as running text into the Voynich page and line shape ({v["r3_tok"]} tokens). Criterion (REVISION_PLAN.md): for T6a, boundary MI and page MI the author\'s output lies outside the Voynich interval on the same side as our reimplementation. Met: {"yes" if R3["exclusion_holds"] else "no"}.', cls='small')
_m7, _m8 = E7B['lzma']['rows'], E8R['lzma']['rows']
T['s_mimic'] = table(['Statistic', 'E7 random', 'E7 message', 'p (Holm)', 'E8 random', 'E8 message', 'p (Holm)'],
                     [[STAT.get(k, k), f(_m7[k]['base_mean'], 4), f(_m7[k]['mean'], 4), f"{f(_m7[k]['p'], 3)} ({f(_m7[k]['p_holm'], 2)})",
                       f(_m8[k]['base_mean'], 4) if k in _m8 else '–', f(_m8[k]['mean'], 4) if k in _m8 else '–',
                       f"{f(_m8[k]['p'], 3)} ({f(_m8[k]['p_holm'], 2)})" if k in _m8 else '–'] for k in _m7],
                     f'Table {TN["s_mimic"]}. R4: means over 20 randomly driven and 20 message-driven (lzma-compressed plaintext) runs for each statistic, with Welch p-values (Fisher for T4) and Holm-adjusted values.', cls='small')
dev_files = [('Battery', 'mechanism/DEVIATIONS.md'), ('E1', 'mechanism/E1_DEVIATIONS.md'), ('E5', 'mechanism/E5_DEVIATIONS.md')]


def md_items(path):
    import re
    txt = open(path).read()
    items = re.findall(r'^\d+\. \*\*(.+?)\*\*', txt, flags=re.M)
    return items


T['s_dev'] = table(['File', 'Deviation (all made before the corresponding Voynich statistic was computed)'],
                   [[name, '; '.join(md_items(p))] for name, p in dev_files] + [['E2–E7', 'none beyond those recorded in PROGRAM.md (E6/E7: none)']],
                   f'Table {TN["s_dev"]}. Logged deviations from the analysis plans. Full texts in the repository.', cls='small')
_prereg_rows = [
    ['Battery analysis plan', 'b67bb47', 'PREREG.md frozen'], ['Battery Stage A', 'f282965', 'controls only'], ['Battery Stage B and report', '650abbd', 'Voynich'],
    ['E1 analysis plan', '889e908', ''], ['E1 calibration', 'c507641', 'before the Voynich run'], ['E2 analysis plan', '0b40d28', ''],
    ['E3 analysis plan', 'ca203c4', ''], ['E4 analysis plan', 'a647269', ''], ['E5 analysis plan', 'bc6c840', ''],
    ['E6 analysis plan', 'aadd173', ''], ['E7 analysis plan', '7b002ad', ''], ['Red-team checks', '355263d', 'post hoc'],
    ['Revision plan (R1–R4)', 'a0b0b86', 'REVISION_PLAN.md; R1 post hoc']]
T['s_prereg'] = table(['Stage', 'Commit', 'Committed (author date)', 'Content'],
                      [[st, h, subprocess.run(['git', 'log', '-1', '--format=%ad', '--date=format:%Y-%m-%d %H:%M %z', h], capture_output=True, text=True).stdout.strip(), c] for st, h, c in _prereg_rows],
                      f'Table {TN["s_prereg"]}. Commits of the analysis plans and stages. Each plan was committed before the corresponding Voynich outcome was computed. Commit identities were rewritten once before publication to remove an e-mail address; contents and dates are unchanged (mechanism/COMMIT_MAP.md).', cls='small')

# ---------------------------------------------------------------- render
env = Environment(loader=FileSystemLoader('paper/templates'), autoescape=False, undefined=StrictUndefined)
CSS = open('paper/templates/style.css').read() + open('paper/templates/extra.css').read()
for name, out, head in (('main', 'paper', 'Beyer — Constrained, not identifiable: statistical constraints on the production of the Voynich manuscript text'),
                        ('supplement', 'supplement', 'Supplementary material')):
    html = env.get_template(name + '.html').render(v=v, p=pv, T=T, TN=TN, FN=FN, STAT=STAT)
    open(f'paper/{out}.html', 'w').write(html)
    story = fitz.Story(html=html, user_css=CSS, archive=fitz.Archive('.'))
    path = f'paper/{out}.pdf'
    writer = fitz.DocumentWriter(path)
    mb = fitz.paper_rect('a4')
    where = mb + (60, 62, -60, -66)
    more, n = True, 0
    while more:
        dev = writer.begin_page(mb)
        more, _ = story.place(where)
        story.draw(dev)
        writer.end_page()
        n += 1
    writer.close()
    doc = fitz.open(path)
    for i, page in enumerate(doc):
        page.insert_text((60, 40), head, fontsize=7.5, fontname='helv', color=(0.35, 0.35, 0.35))
        page.insert_text((mb.width / 2 - 8, mb.height - 36), str(i + 1), fontsize=8.5, fontname='helv')
    doc.save(path + '.tmp', garbage=4, deflate=True, deflate_images=True, deflate_fonts=True)
    doc.close()
    os.replace(path + '.tmp', path)
    print(out, 'pages:', n)
