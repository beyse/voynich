"""Out-of-sample: fit the automaton on odd pages (per section), evaluate on even pages; per-hand and per-language batteries."""
import sys, random, lzma
sys.path.insert(0,'.')
from voynich.ivtff import parse
from voynich.battery import battery, twin_residual, _cond_entropy
from voynich.generators import fit, sample_line
from collections import defaultdict, Counter
ok=lambda w: w and '?' not in w and '*' not in w
L=parse('data/ZL3b-n.txt',comma_is_space=False)
pages=defaultdict(list); meta={}
for ln in L:
    if ln.kind!='P': continue
    ws=[w for w in ln.words if ok(w)]
    if len(ws)>=2: pages[ln.page].append(ws); meta[ln.page]=(ln.lang,ln.section,ln.hand)
keys=list(pages); train=keys[0::2]; test=keys[1::2]
def oos_twin(order,train,test,seed=0):
    rng=random.Random(seed); gs=defaultdict(list)
    for pg in train: gs[meta[pg][:2]].extend(' '.join(l) for l in pages[pg])
    models={g:fit(v,order) for g,v in gs.items() if len(v)>=30}; glob=fit([s for v in gs.values() for s in v],order)
    real=[]; twin=[]
    for pg in test:
        m=models.get(meta[pg][:2],glob)
        for l in pages[pg]:
            real.append(' '.join(l)); t=sample_line(m,order,len(' '.join(l)),rng); twin.append(' '.join(t))
    lz=lambda ss: len(lzma.compress('\n'.join(ss).encode(),preset=9))*8/sum(map(len,ss))
    return lz(real)-lz(twin), _cond_entropy(real,3)-_cond_entropy(twin,3), lz(real), lz(twin)
print("out-of-sample residual (fit on odd pages, evaluate on even pages):")
for order in (3,4):
    d,h,a,b=oos_twin(order,train,test); print(f"  order {order}: lzma real {a:.3f} twin {b:.3f} residual {d:+.3f}; h(3) residual {h:+.3f}")
d,h,a,b=oos_twin(3,test,train); print(f"  order 3 reversed split: residual {d:+.3f}; h(3) residual {h:+.3f}")
# battery on held-out real pages vs twin generated from the odd-page model (same line shapes)
rng=random.Random(1); gs=defaultdict(list)
for pg in train: gs[meta[pg][:2]].extend(' '.join(l) for l in pages[pg])
models={g:fit(v,3) for g,v in gs.items() if len(v)>=30}; glob=fit([s for v in gs.values() for s in v],3)
realP=[pages[pg] for pg in test]; twinP=[]
for pg in test:
    m=models.get(meta[pg][:2],glob); twinP.append([x for x in (sample_line(m,3,len(' '.join(l)),rng) for l in pages[pg]) if len(x)>=2])
cols=[('edge_mi','{:.3f}'),('token_mi','{:.3f}'),('break_mi','{:.3f}'),('space_gain','{:.1%}'),('hapax','{:.2f}'),('zipf','{:.2f}'),('lex_real','{:.2f}'),('lex_synth','{:.2f}'),('h2','{:.2f}'),('h4','{:.2f}'),('page_mi','{:.3f}')]
def show(pg,name):
    r=battery(pg,name); print(f"{name:<26}"+"".join(f" {f.format(r[k]):>9}" for k,f in cols),flush=True); return r
print("\n"+f"{'subset':<26}"+"".join(f" {k[:9]:>9}" for k,_ in cols))
show(realP,'held-out real (even pages)'); show(twinP,'twin from odd-page model')
# per hand and per language
for h in ('1','2','3','4','5'):
    sub=[pages[pg] for pg in pages if meta[pg][2]==h]
    if sum(len(x) for x in sub)>=150: show(sub,f'hand {h} ({len(sub)} pages)')
for lang in 'AB':
    show([pages[pg] for pg in pages if meta[pg][0]==lang],f'Currier {lang}')
