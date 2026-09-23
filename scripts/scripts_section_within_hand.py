"""Secondary: predict the section of a page within one hand from text (words vs glyph bigrams), leave-one-out,
against a folio-position-only baseline. Sections are contiguous folio ranges, so this is confounded with drift."""
import sys, re
sys.path.insert(0,'.')
from voynich.ivtff import parse
from collections import Counter, defaultdict
import numpy as np
ok=lambda w: w and '?' not in w and '*' not in w
L=parse('data/ZL3b-n.txt',comma_is_space=False)
pages=defaultdict(list); meta={}
for ln in L:
    if ln.kind!='P': continue
    ws=[w for w in ln.words if ok(w)]
    if ws: pages[ln.page].extend(ws); meta[ln.page]=(ln.lang,ln.section,ln.hand)
def folio(p): m=re.match(r'f(\d+)([rv])',p); return int(m.group(1))*2+(m.group(2)=='v')
def vec_words(p):
    c=Counter(pages[p]); n=sum(c.values()); return {w:np.sqrt(v/n) for w,v in c.items()}
def vec_bigr(p):
    s=' '.join(pages[p]); c=Counter(zip(s,s[1:])); n=sum(c.values()); return {w:np.sqrt(v/n) for w,v in c.items()}
def dist(a,b): return np.sqrt(sum((a.get(k,0)-b.get(k,0))**2 for k in set(a)|set(b)))
def loo(ps,vec,exclude_radius):
    V={p:vec(p) for p in ps}; correct=0; n=0
    for p in ps:
        # nearest-centroid by section, excluding folio neighbours within radius (to reduce drift leakage)
        cands=[q for q in ps if q!=p and abs(folio(q)-folio(p))>exclude_radius]
        bysec=defaultdict(list)
        for q in cands: bysec[meta[q][1]].append(q)
        if len(bysec)<2: continue
        d={s:np.mean([dist(V[p],V[q]) for q in qs]) for s,qs in bysec.items()}
        pred=min(d,key=d.get); correct+= pred==meta[p][1]; n+=1
    return correct/max(n,1), n
def folio_baseline(ps,exclude_radius):
    correct=0; n=0
    for p in ps:
        cands=[q for q in ps if q!=p and abs(folio(q)-folio(p))>exclude_radius]
        if not cands: continue
        q=min(cands,key=lambda q: abs(folio(q)-folio(p))); correct+= meta[q][1]==meta[p][1]; n+=1
    return correct/max(n,1), n
for hand,secs in [('1',('H','P')),('2',('B','H')),('3',('S','H'))]:
    ps=[p for p in pages if meta[p][2]==hand and meta[p][1] in secs and len(pages[p])>=40]
    cnt=Counter(meta[p][1] for p in ps); maj=max(cnt.values())/len(ps)
    print(f"\nhand {hand}: {dict(cnt)} pages; majority baseline {maj:.2f}")
    for rad in (0,10,30):
        aw,n=loo(ps,vec_words,rad); ab,_=loo(ps,vec_bigr,rad); fb,_=folio_baseline(ps,rad)
        print(f"  exclude |folio diff|<={rad//2:>2} folios: words {aw:.2f}  glyph-bigrams {ab:.2f}  nearest-folio-only {fb:.2f}  (n={n})")
