"""Figures for paper 2, computed from results/mechanism/*.json (run from repo root)."""
import json
import os

import matplotlib

matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
import sys
sys.path.insert(0, 'paper2')
from labels import STAT, FITTED

R = 'results/mechanism'
OUT = 'paper2/figures'
os.makedirs(OUT, exist_ok=True)
L = lambda p: json.load(open(f'{R}/{p}'))
A, B, PH, RT = L('stageA.json'), L('stageB.json')['VOYNICH'], L('posthoc.json'), L('redteam.json')

# reference palette (dataviz skill, light mode; first three slots validated all-pairs)
INK, INK2, GRID = '#0b0b0b', '#52514e', '#e4e3de'
S1, S2, S3 = '#2a78d6', '#eb6834', '#1baf7a'     # languages / human gibberish (or 2nd series) / generators, ciphers
plt.rcParams.update({'font.family': 'DejaVu Sans', 'font.size': 8.5, 'axes.edgecolor': INK2, 'axes.labelcolor': INK,
                     'xtick.color': INK2, 'ytick.color': INK2, 'axes.grid': True, 'grid.color': GRID,
                     'grid.linewidth': 0.6, 'axes.axisbelow': True, 'axes.spines.top': False,
                     'axes.spines.right': False, 'legend.frameon': False, 'savefig.dpi': 300})


def save(fig, name):
    fig.savefig(f'{OUT}/{name}.png', bbox_inches='tight', facecolor='white')
    plt.close(fig)


def err(ax, x, y, xe=None, ye=None, **kw):
    ax.errorbar(x, y, xerr=xe, yerr=ye, fmt='none', ecolor=kw.pop('ecolor', INK2), elinewidth=0.8, capsize=0, zorder=2)


# ---------------------------------------------------------------- Figure 1: hardness vs rigidity
def fig1():
    fig, ax = plt.subplots(figsize=(6.2, 4.0))
    rows = [('VOYNICH', B, INK, 'D', 'Voynich (ZL3b)')]
    it = PH['it2a']
    langs = ['LAT', 'ITA', 'GER', 'ENG']
    gens = ['MK-sec', 'MK-page', 'RUGG', 'TS', 'NAIB-lines', 'NAIB-run']
    for n in langs:
        rows.append((n, A[n], S1, 's', {'LAT': 'Latin', 'ITA': 'Italian', 'GER': 'German', 'ENG': 'English'}[n]))
    rows.append(('GIB', A['GIB'], S2, 'o', 'Human gibberish (38 writers)'))
    lab = {'MK-sec': 'order-3 automaton', 'MK-page': 'automaton, page drift', 'RUGG': 'table and grille',
           'TS': 'copy-and-modify', 'NAIB-lines': 'Naibbe (lines)', 'NAIB-run': 'Naibbe (running)'}
    for n in gens:
        rows.append((n, A[n], S3, '^', lab[n]))
    for n, r, col, mk, name in rows:
        x, y = r['t3a']['rho'], r['t3b']['consistency']
        xe = [[x - r['t3a']['ci95'][0]], [r['t3a']['ci95'][1] - x]]
        ye = [[y - r['t3b']['cons_ci95'][0]], [r['t3b']['cons_ci95'][1] - y]]
        err(ax, [x], [y], xe, ye)
        ax.scatter([x], [y], s=46 if n != 'VOYNICH' else 60, marker=mk, color=col, edgecolor='white', linewidth=1.2, zorder=3)
    ax.scatter([it['t3a']['rho']], [it['t3b']['consistency']], s=60, marker='D', facecolor='white', edgecolor=INK, linewidth=1.2, zorder=3)
    ax.annotate('Voynich (ZL3b)', (B['t3a']['rho'], B['t3b']['consistency']), xytext=(12, -4), textcoords='offset points', color=INK, fontweight='bold')
    ax.annotate('Voynich (Takahashi)', (it['t3a']['rho'], it['t3b']['consistency']), xytext=(12, 2), textcoords='offset points', color=INK2)
    ax.annotate('human gibberish', (A['GIB']['t3a']['rho'], A['GIB']['t3b']['consistency']), xytext=(-10, -3), textcoords='offset points', ha='right', color=INK2)
    ax.annotate('natural languages', (0.101, 0.705), xytext=(4, 8), textcoords='offset points', color=INK2)
    ax.annotate('table and grille', (A['RUGG']['t3a']['rho'], A['RUGG']['t3b']['consistency']), xytext=(0, 8), textcoords='offset points', ha='center', color=INK2)
    ax.annotate('automata, copy-and-modify,\nNaibbe (fitted to or built from Voynich)', (0.045, 0.852), xytext=(30, -42), textcoords='offset points', color=INK2,
                arrowprops=dict(arrowstyle='-', color=INK2, lw=0.6))
    ax.set_xlabel('zero replication ρ (matched 250-token chunks; lower = harder zeros)')
    ax.set_ylabel('slot-order consistency')
    ax.set_xlim(0.015, 0.145)
    handles = [plt.Line2D([], [], marker=m, color=c, ls='', markersize=6) for c, m in ((INK, 'D'), (S1, 's'), (S2, 'o'), (S3, '^'))]
    ax.legend(handles, ['Voynich', 'natural language', 'human gibberish', 'generator / cipher'], loc='center right', bbox_to_anchor=(1.0, 0.52))
    save(fig, 'fig1_constraints')


# ---------------------------------------------------------------- Figure 2: line endings
def fig2():
    E2R, E3R = L('e2/report.json'), L('e3/report.json')
    rows = [
        ('Voynich, all pages', B['t2a_margin']['excess'], B['t2a_para']['excess']),
        ('Voynich, stars section (text-only)', RT['t2a_stars']['margin']['excess'], RT['t2a_stars']['para']['excess']),
        ('Human gibberish', A['GIB']['t2a_margin']['excess'], A['GIB']['t2a_para']['excess']),
        ('Latin, greedily wrapped', A['LATW']['t2a_margin']['excess'], None),
        ('Generator E2 (one end model), test half', E2R['HGR']['rows']['T2a_margin']['G'], E2R['HGR']['rows']['T2a_para']['G']),
        ('Generator E3 (margin-driven), test half', E3R['primary:HGR2']['rows']['T2a_margin']['G'], E3R['primary:HGR2']['rows']['T2a_para']['G']),
    ]
    fig, ax = plt.subplots(figsize=(6.2, 2.9))
    ys = np.arange(len(rows))[::-1]
    for y, (name, m, p) in zip(ys, rows):
        ax.plot([min(v for v in (m, p) if v is not None), max(v for v in (m, p) if v is not None)], [y, y], color=GRID, lw=2, zorder=1)
        ax.scatter([m], [y], color=S1, s=46, zorder=3, edgecolor='white', linewidth=1.2)
        if p is not None:
            ax.scatter([p], [y], color=S2, marker='s', s=40, zorder=3, edgecolor='white', linewidth=1.2)
    ax.set_yticks(ys)
    ax.set_yticklabels([r[0] for r in rows])
    ax.axvline(0, color=INK2, lw=0.8)
    ax.set_xlabel('final-form excess (JSD, line-final vs. line-internal tokens of equal length)')
    h = [plt.Line2D([], [], marker='o', color=S1, ls='', markersize=6), plt.Line2D([], [], marker='s', color=S2, ls='', markersize=6)]
    ax.legend(h, ['line ends at the margin', 'line ends the paragraph'], loc='lower right')
    ax.grid(axis='y', visible=False)
    save(fig, 'fig2_line_endings')


# ---------------------------------------------------------------- Figure 3: recency and boundaries
def fig3():
    E1A, E1B, E1I = L('e1_stageA.json'), L('e1_stageB.json')['VOYNICH'], L('e1_posthoc_it2a.json')['IT2a']
    fig, (a, b) = plt.subplots(1, 2, figsize=(6.6, 2.9), gridspec_kw={'width_ratios': [1.25, 1]})
    d = B['t6a']['d']
    k = [i for i, x in enumerate(d) if x <= 30]
    sm = lambda v: np.convolve(np.array(v), np.ones(3) / 3, mode='same')
    for name, prof, col, lw, ls in (('Voynich', B['t6a']['near_profile'], INK, 1.8, '-'),
                                    ('copy-and-modify', A['TS']['t6a']['near_profile'], S3, 1.4, '-'),
                                    ('English', A['ENG']['t6a']['near_profile'], S1, 1.2, '-'),
                                    ('order-3 automaton', A['MK-sec']['t6a']['near_profile'], INK2, 1.0, '--')):
        y = sm(prof)
        a.plot([d[i] for i in k][1:-1], [y[i] for i in k][1:-1], color=col, lw=lw, ls=ls, label=name)
    a.axhline(1, color=INK2, lw=0.6)
    a.set_xlabel('token distance d on the page')
    a.set_ylabel('near-repeat rate / permutation expectation')
    a.legend(loc='upper right', fontsize=7.5)
    a.set_title('a  Recency (T6a)', loc='left', fontsize=9)
    # b: E1 steps
    rows = [('Voynich', E1B), ('Voynich (Takahashi)', E1I)]
    ctrl = {}
    for nm in ('SET-line', 'SET-para', 'REC', 'MK-sec'):
        seeds = [E1A[f'{nm}-{s}'] for s in range(5)]
        ctrl[nm] = seeds
    labels = ['Voynich', 'Takahashi', 'settings per line', 'settings per paragraph', 'recency', 'automaton']
    ys = np.arange(6)[::-1]
    for stat, off, col, mk in (('LS_graded', 0.14, S1, 'o'), ('PS', -0.14, S2, 's')):
        vals = [E1B, E1I]
        for yi, r in zip(ys[:2], vals):
            v, ci = r['stats'][stat], r['ci95'][stat]
            b.plot(ci, [yi + off] * 2, color=INK2, lw=0.8)
            b.scatter([v], [yi + off], color=col, marker=mk, s=40, zorder=3, edgecolor='white', linewidth=1.0)
        for yi, nm in zip(ys[2:], ('SET-line', 'SET-para', 'REC', 'MK-sec')):
            xs = [s['stats'][stat] for s in ctrl[nm]]
            b.scatter(xs, [yi + off] * len(xs), color=col, marker=mk, s=16, alpha=0.55, zorder=2, linewidth=0)
            b.scatter([np.mean(xs)], [yi + off], color=col, marker=mk, s=40, zorder=3, edgecolor='white', linewidth=1.0)
    b.axvline(0, color=INK2, lw=0.6)
    b.set_yticks(ys)
    b.set_yticklabels(labels)
    b.set_xlabel('step: across − within boundary')
    b.grid(axis='y', visible=False)
    h = [plt.Line2D([], [], marker='o', color=S1, ls='', markersize=6), plt.Line2D([], [], marker='s', color=S2, ls='', markersize=6)]
    b.legend(h, ['line step (graded)', 'paragraph step'], loc='upper center', bbox_to_anchor=(0.45, -0.22), ncol=2, fontsize=7.5)
    b.set_title('b  Boundary steps (E1)', loc='left', fontsize=9)
    fig.tight_layout()
    save(fig, 'fig3_recency')


# ---------------------------------------------------------------- Figure 4: drift and burstiness
def fig4():
    E4A, E4B = L('e4_stageA.json'), L('e4_stageB.json')['VOYNICH']
    E5A, E5B = L('e5_stageA.json'), L('e5_stageB.json')['VOYNICH']
    fig, (a, b) = plt.subplots(1, 2, figsize=(6.6, 3.0))
    pts = [('Voynich', E4B, INK, 'D'), ('Latin', E4A['LAT'], S1, 's'), ('Italian', E4A['ITA'], S1, 's'), ('German', E4A['GER'], S1, 's'),
           ('English', E4A['ENG'], S1, 's'), ('verbose cipher', E4A['VB-run'], S2, 'o'), ('Naibbe', E4A['NAIB-run'], S2, 'o'),
           ('glyph-habit drift', E4A['GDRIFT'], S3, '^'), ('vocabulary drift', E4A['LDRIFT'], S3, '^'), ('automaton', E4A['MK-sec'], S3, '^')]
    for name, r, col, mk in pts:
        x, y = r['L'], r['S']
        err(a, [x], [y], [[x - r['L_ci95'][0]], [r['L_ci95'][1] - x]], [[y - r['S_ci95'][0]], [r['S_ci95'][1] - y]])
        a.scatter([x], [y], color=col, marker=mk, s=40 if name != 'Voynich' else 56, zorder=3, edgecolor='white', linewidth=1.0)
        if name in ('Voynich', 'Italian', 'glyph-habit drift', 'vocabulary drift', 'Naibbe', 'verbose cipher'):
            off = {'verbose cipher': (6, 6), 'Naibbe': (6, -12), 'Voynich': (8, -3), 'vocabulary drift': (-4, -14), 'glyph-habit drift': (-30, -16)}.get(name, (4, 4))
            a.annotate(name, (x, y), xytext=off, textcoords='offset points', fontsize=7, ha='right' if name == 'vocabulary drift' else 'left',
                       color=INK if name == 'Voynich' else INK2)
    a.axhline(0, color=INK2, lw=0.6)
    a.axvline(0, color=INK2, lw=0.6)
    a.set_xlabel('lexical drift slope L')
    a.set_ylabel('sublexical drift slope S')
    a.set_title('a  Within-page drift (E4)', loc='left', fontsize=9)
    hh = [plt.Line2D([], [], marker=m, color=c, ls='', markersize=5) for c, m in ((S1, 's'), (S2, 'o'), (S3, '^'))]
    a.legend(hh, ['natural language', 'cipher of Latin', 'synthetic production'], loc='lower right', fontsize=6.8, frameon=True, facecolor='white', edgecolor='none', framealpha=0.95)
    bands = ['R', 'M', 'F', 'VF']
    xl = ['2–4', '5–19', '20–99', '≥100']
    for n, lab in (('LAT', None), ('ITA', None), ('GER', None), ('ENG', 'natural languages')):
        b.plot(range(4), [E5A[n]['B'][x] for x in bands], color=S1, lw=1.0, marker='s', markersize=3.5, label=lab)
    b.plot(range(4), [E5A['NAIB-run']['B'][x] for x in bands], color=S2, lw=1.2, marker='o', markersize=4, label='Naibbe cipher')
    b.plot(range(4), [E5A['HGR2']['B'][x] for x in bands], color=S3, lw=1.2, marker='^', markersize=4, label='glyph generator (E3)')
    b.plot(range(4), [E5A['REP']['B'][x] for x in bands], color=S3, lw=1.2, ls='--', marker='^', markersize=4, label='repertoire + coinage')
    b.plot(range(4), [E5B['B'][x] for x in bands], color=INK, lw=2.0, marker='D', markersize=5, label='Voynich')
    b.axhline(1, color=INK2, lw=0.6)
    b.set_xticks(range(4))
    b.set_xticklabels(xl)
    b.set_xlabel('type frequency band')
    b.set_ylabel('same-page pairs / expectation')
    b.legend(fontsize=7, loc='upper right')
    b.set_title('b  Page clustering by frequency (E5)', loc='left', fontsize=9)
    fig.tight_layout()
    save(fig, 'fig4_drift_burstiness')


# ---------------------------------------------------------------- Figure 5: held-out phenotype matrix
def fig5():
    E2R, E3R, E6R = L('e2/report.json'), L('e3/report.json'), L('e6/report.json')
    cols = [('E2\nfull', E2R['HGR']), ('E2 plain\nautomaton', E2R['A0-baseline']), ('E3 full\nprimary', E3R['primary:HGR2']),
            ('E3 full\nsecondary', E3R['secondary:HGR2']), ('E3 w/o\nmargin rule', E3R['primary:B1-noC1']),
            ('E3 w/o\nslips etc.', E3R['primary:B3-noC3']), ('E6\ntwo-route', E6R['primary:TR']),
            ('E6 w/o\nboundary', E6R['primary:D4-noK'])]
    stats = list(E3R['primary:HGR2']['rows'].keys())
    fitted = FITTED
    M = np.array([[1 if c['rows'][s]['pass'] else 0 for _, c in cols] for s in stats])
    fig, ax = plt.subplots(figsize=(6.6, 7.8))
    ax.imshow(M, cmap=matplotlib.colors.ListedColormap(['#f3f2ee', '#9dbde8']), aspect='auto', vmin=0, vmax=1)
    for i in range(len(stats)):
        for j in range(len(cols)):
            if not M[i, j]:
                ax.text(j, i, '×', ha='center', va='center', color=INK, fontsize=8)
    ax.set_xticks(range(len(cols)))
    ax.set_xticklabels([c[0] for c in cols], fontsize=6.8)
    ax.xaxis.tick_top()
    ax.set_yticks(range(len(stats)))
    ax.set_yticklabels([STAT[s] + (' †' if s in fitted else '') for s in stats], fontsize=6.8)
    ax.set_xticks(np.arange(-.5, len(cols)), minor=True)
    ax.set_yticks(np.arange(-.5, len(stats)), minor=True)
    ax.grid(which='minor', color='white', linewidth=1.5)
    ax.grid(which='major', visible=False)
    ax.tick_params(which='both', length=0)
    for s in ax.spines.values():
        s.set_visible(False)
    tot = M.sum(0)
    for j, t in enumerate(tot):
        ax.text(j, len(stats) + 0.3, f'{t}/40', ha='center', va='top', fontsize=7.5, color=INK)
    save(fig, 'fig5_heldout_matrix')


# ---------------------------------------------------------------- Figure 6: E7 standardized differences
def fig6():
    R7 = L('e7/results.json')
    prng = [v['phenotype'] for k, v in R7.items() if k.startswith('prng')]
    stats = [k for k in prng[0] if k != 'T4_peak']
    fig, ax = plt.subplots(figsize=(6.6, 3.0))
    for kind, col, mk, off in (('lzma', S1, 'o', -0.18), ('raw', S2, 's', 0.18)):
        grp = [v['phenotype'] for k, v in R7.items() if k.startswith(kind)]
        z = []
        for s in stats:
            a = [x[s] for x in prng]
            b = [x[s] for x in grp]
            sd = np.sqrt(np.var(a, ddof=1) + np.var(b, ddof=1))
            z.append((np.mean(b) - np.mean(a)) / sd if sd > 0 else 0.0)
        ax.scatter(np.arange(len(stats)) + off, z, color=col, marker=mk, s=18, zorder=3, linewidth=0,
                   label='compressed plaintext' if kind == 'lzma' else 'raw plaintext bits')
    ax.axhspan(-2, 2, color='#eeede8', zorder=0)
    ax.axhline(0, color=INK2, lw=0.6)
    ax.set_xticks(range(len(stats)))
    ax.set_xticklabels([STAT[x] for x in stats], rotation=90, fontsize=6)
    ax.set_ylabel('difference / √(sd²₁ + sd²₂)')
    ax.grid(axis='x', visible=False)
    ax.set_ylim(-3.2, 3.2)
    ax.legend(loc='lower left', bbox_to_anchor=(0.0, 1.0), fontsize=7.5, ncol=2)
    save(fig, 'fig6_e7')


if __name__ == '__main__':
    for f in (fig1, fig2, fig3, fig4, fig5, fig6):
        f()
        print('ok', f.__name__)
