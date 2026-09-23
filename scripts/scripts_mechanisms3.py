import sys, json
sys.path.insert(0,'.')
from voynich.battery import battery, twin_residual
from voynich.generators import *
mech=[('VMS',P),('markov3+drift',markov_pages(3,True)),('markov4+drift',markov_pages(4,True)),('latin',chunk(la)),('latin rule-sp',chunk(rule_spaces(la))),('latin indep lines',latin_indep_pages()),
      ('rugg grille',rugg_pages()),('timm-schinner v2',ts_pages()),('verbose+indep',verbose_pages(0,True)),('autokey 1g/letter',autokey_pages(0,1)),('autokey 2g/letter',autokey_pages(0,2))]
results=[]
for name,pg in mech:
    r=battery(pg,name); r['lzma_resid'],r['h3_resid']=twin_residual(pg,groups[:len(pg)]); results.append(r); print(name,'done',flush=True)
cols=[('edge_mi','{:.3f}'),('token_mi','{:.3f}'),('break_mi','{:.3f}'),('adj_mi_same_n','{:.3f}'),('space_gain','{:.1%}'),('hapax','{:.2f}'),('zipf','{:.2f}'),('wlen','{:.2f}'),('lex_real','{:.2f}'),('lex_synth','{:.2f}'),('h2','{:.2f}'),('h4','{:.2f}'),('lzma','{:.2f}'),('lzma_resid','{:+.3f}'),('h3_resid','{:+.3f}'),('page_mi','{:.3f}')]
print("\n"+f"{'mechanism':<18}"+"".join(f" {k[:9]:>9}" for k,_ in cols))
for r in results: print(f"{r['label']:<18}"+"".join(f" {f.format(r[k]):>9}" for k,f in cols))
json.dump(results,open('results/results_mechanisms_final.json','w'),indent=1)
print("\nsamples: autokey1:",' '.join(autokey_pages(0,1)[3][1][:8]),"| autokey2:",' '.join(autokey_pages(0,2)[3][1][:8]),"| T&S v2:",' '.join(ts_pages()[3][2][:8]))
