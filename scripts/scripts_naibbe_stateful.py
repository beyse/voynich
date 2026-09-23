import sys, json
sys.path.insert(0,'.')
from voynich.battery import battery, twin_residual
from voynich.generators import *
cols=[('edge_mi','{:.3f}'),('token_mi','{:.3f}'),('adj_mi_same_n','{:.3f}'),('break_mi','{:.3f}'),('space_gain','{:.1%}'),('hapax','{:.2f}'),('zipf','{:.2f}'),('types','{:d}'),('lex_real','{:.2f}'),('lex_synth','{:.2f}'),('h2','{:.2f}'),('h4','{:.2f}'),('lzma_resid','{:+.3f}'),('page_mi','{:.3f}')]
print(f"{'mechanism':<30}"+"".join(f" {k[:9]:>9}" for k,_ in cols))
res=[]
def show(pg,name):
    r=battery(pg,name); r['lzma_resid'],_=twin_residual(pg,groups[:len(pg)]); res.append(r)
    print(f"{name:<30}"+"".join(f" {f.format(r[k]):>9}" for k,f in cols),flush=True)
show(P,'VMS')
for w,c in [(0.9,0.15),(1.0,0.05),(0.6,0.15)]:
    show(naibbe_stateful_pages(0,w,c),f'naibbe stateful w={w} c={c}')
json.dump(res,open('results/results_naibbe_stateful.json','w'),indent=1)
