"""Robustness: core battery on the Takahashi transcription (IT2a) vs Zandbergen-Landini (ZL3b)."""
import sys
sys.path.insert(0,'.')
from voynich.ivtff import parse
from voynich.battery import battery, twin_residual
from collections import defaultdict
ok=lambda w: w and '?' not in w and '*' not in w
cols=[('tokens','{:d}'),('types','{:d}'),('edge_mi','{:.3f}'),('token_mi','{:.3f}'),('adj_mi_same_n','{:.3f}'),('break_mi','{:.3f}'),('space_gain','{:.1%}'),('hapax','{:.2f}'),('zipf','{:.2f}'),('wlen','{:.2f}'),('lex_real','{:.2f}'),('lex_synth','{:.2f}'),('h2','{:.2f}'),('h4','{:.2f}'),('lzma_resid','{:+.3f}'),('page_mi','{:.3f}')]
print(f"{'transcription':<16}"+"".join(f" {k[:9]:>9}" for k,_ in cols))
for name,path in [('ZL3b',"data/ZL3b-n.txt"),('IT2a',"data/IT2a-n.txt")]:
    for comma in (False,True):
        L=parse(path,comma_is_space=comma); pages=defaultdict(list); meta={}
        for ln in L:
            if ln.kind!='P': continue
            ws=[w for w in ln.words if ok(w)]
            if len(ws)>=2: pages[ln.page].append(ws); meta[ln.page]=(ln.lang,ln.section)
        P=list(pages.values()); groups=[meta[p] for p in pages]
        r=battery(P,name); r['lzma_resid'],_=twin_residual(P,groups)
        print(f"{name+(' c=sp' if comma else ' c=jn'):<16}"+"".join(f" {f.format(r[k]):>9}" for k,f in cols),flush=True)
