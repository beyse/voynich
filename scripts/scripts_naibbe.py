import sys, json
sys.path.insert(0,'.')
from voynich.battery import battery, twin_residual
from voynich.generators import *
from voynich.stats import clean_gutenberg, tokenize_natural
from collections import Counter
cols=[('edge_mi','{:.3f}'),('token_mi','{:.3f}'),('adj_mi_same_n','{:.3f}'),('break_mi','{:.3f}'),('space_gain','{:.1%}'),('hapax','{:.2f}'),('zipf','{:.2f}'),('wlen','{:.2f}'),('types','{:d}'),('lex_real','{:.2f}'),('lex_synth','{:.2f}'),('h2','{:.2f}'),('h4','{:.2f}'),('lzma','{:.2f}'),('lzma_resid','{:+.3f}'),('page_mi','{:.3f}')]
print(f"{'mechanism':<26}"+"".join(f" {k[:9]:>9}" for k,_ in cols))
res=[]
def show(pg,name):
    r=battery(pg,name); r['lzma_resid'],_=twin_residual(pg,groups[:len(pg)]); res.append(r)
    print(f"{name:<26}"+"".join(f" {f.format(r[k]):>9}" for k,f in cols),flush=True)
show(P,'VMS')
show(naibbe_pages(0,True,'letter',0.03),'naibbe indep, card/letter')
show(naibbe_pages(0,True,'token',0.03),'naibbe indep, card/token')
show(naibbe_pages(0,False,'letter',0.03),'naibbe running')
show(naibbe_pages(0,True,'letter',0.0),'naibbe indep, no merge')
it=clean_gutenberg('data/ref/it_dante.txt')
show(naibbe_pages(0,False,'letter',0.03,text=it),'naibbe running Italian')
json.dump(res,open('results/results_naibbe.json','w'),indent=1)
pg=naibbe_pages(0,True,'letter',0.03); print("\nsample:",' '.join(pg[3][1][:12]))
w=[x for p in pg for l in p for x in l]; print("naibbe top words:",Counter(w).most_common(12))
