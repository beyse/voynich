import sys
sys.path.insert(0,'.')
from voynich.battery import battery, twin_residual
from voynich.generators import *
from collections import Counter
real_lines={' '.join(l) for pg in P for l in pg}; real_bigrams=Counter((l[i],l[i+1]) for pg in P for l in pg for i in range(len(l)-1))
cols=[('edge_mi','{:.3f}'),('token_mi','{:.3f}'),('adj_mi_same_n','{:.3f}'),('break_mi','{:.3f}'),('space_gain','{:.1%}'),('hapax','{:.2f}'),('zipf','{:.2f}'),('lex_real','{:.2f}'),('lex_synth','{:.2f}'),('h4','{:.2f}'),('lzma_resid','{:+.3f}'),('page_mi','{:.3f}')]
print(f"{'mechanism':<20}"+"".join(f" {k[:9]:>9}" for k,_ in cols)+"  lines_copied bigr_att")
import json
RES=[]
def show(pg,name):
    r=battery(pg,name); r['lzma_resid'],_=twin_residual(pg,groups); RES.append(r)
    lines=[' '.join(l) for x in pg for l in x]; copied=sum(l in real_lines for l in lines)/len(lines)
    bg=[(l[i],l[i+1]) for x in pg for l in x for i in range(len(l)-1)]; att=sum(b in real_bigrams for b in bg)/len(bg)
    print(f"{name:<20}"+"".join(f" {f.format(r[k]):>9}" for k,f in cols)+f"  {copied:11.3f} {att:8.3f}",flush=True)
show(P,'VMS')
for order,lam in [(4,0.3),(4,0.5),(4,0.7),(3,0.5),(5,0.3)]:
    show(markov_pages_hier(order,lam),f'hier o{order} lam{lam}')

json.dump(RES,open('results/results_hier.json','w'),indent=1)
