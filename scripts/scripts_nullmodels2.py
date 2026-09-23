"""Ordered line vs bag-of-words line. Middle segments only (drop 2 words at each edge); pairs at d=1,2,3;
nulls that permute ONLY middle-segment words (marginals preserved): within line / within page / global."""
import sys, math, random, re
sys.path.insert(0,'.')
from voynich.ivtff import parse
from voynich.stats import clean_gutenberg, tokenize_natural
from collections import Counter, defaultdict
exec(open('scripts/scripts_families.py').read().split("L=parse")[0])
L=parse('data/ZL3b-n.txt'); ok=lambda w: w and '?' not in w and '*' not in w
def mi(pairs):
    pa=Counter(a for a,b in pairs); pb=Counter(b for a,b in pairs); pab=Counter(pairs); n=len(pairs)
    return sum(c/n*math.log2((c/n)/((pa[a]/n)*(pb[b]/n))) for (a,b),c in pab.items())
def segs_of(pages): return [[l[2:-2] for l in pg if len(l)>=7] for pg in pages]
def pairs(segs,d): return [(s[i],s[i+d]) for pg in segs for s in pg for i in range(len(s)-d)]
def null_line(segs,rng): return [[rng.sample(s,len(s)) for s in pg] for pg in segs]
def null_page(segs,rng):
    out=[]
    for pg in segs:
        ws=[w for s in pg for w in s]; rng.shuffle(ws); i=0; npg=[]
        for s in pg: npg.append(ws[i:i+len(s)]); i+=len(s)
        out.append(npg)
    return out
def null_global(segs,rng):
    ws=[w for pg in segs for s in pg for w in s]; rng.shuffle(ws); i=0; out=[]
    for pg in segs:
        npg=[]
        for s in pg: npg.append(ws[i:i+len(s)]); i+=len(s)
        out.append(npg)
    return out
def report(pages,label,reps=6):
    segs=segs_of(pages); row=f"{label:<13} n(d=1)={len(pairs(segs,1)):>5} |"
    for d in (1,2,3):
        obs=mi(pairs(segs,d)); ex=[]
        for name,fn in (('line',null_line),('page',null_page),('glob',null_global)):
            b=sum(mi(pairs(fn(segs,random.Random(r)),d)) for r in range(reps))/reps; ex.append(obs-b)
        row+=f" d={d}: line {ex[0]:6.3f} page {ex[1]:6.3f} glob {ex[2]:6.3f} |"
    print(row)
pages=defaultdict(list)
for ln in L:
    if ln.kind!='P': continue
    ws=[w for w in ln.words if ok(w)]
    if len(ws)>=2: pages[ln.page].append((ln.lang,ws))
P=[[ws for _,ws in v] for v in pages.values()]
print("excess MI (bits) of middle-segment pairs vs. marginal-preserving nulls")
report(P,'VMS raw'); report([[ [light(w) for w in l] for l in pg] for pg in P],'VMS light'); report([[ [heavy(w) for w in l] for l in pg] for pg in P],'VMS heavy')
for lang in 'AB':
    sub=[[ [light(w) for w in ws] for lg,ws in v if lg==lang] for v in pages.values()]; sub=[pg for pg in sub if pg]
    report(sub,f'VMS-{lang} light')
shape=[[len(l) for l in pg] for pg in P]
def chunk(words):
    out=[]; i=0
    for pg in shape:
        npg=[]
        for k in pg:
            if i+k>len(words): break
            npg.append(words[i:i+k]); i+=k
        if npg: out.append(npg)
    return out
la=tokenize_natural(open('data/ref/la_caesar.txt').read()); it=tokenize_natural(clean_gutenberg('data/ref/it_dante.txt')); de=tokenize_natural(clean_gutenberg('data/ref/de_faust.txt'))
report(chunk(la),'Latin'); report(chunk([x[:4] for x in la]),'Latin stem4'); report(chunk(it),'Italian'); report(chunk(de),'German')
# Dante's real verse lines as a line-structured natural control (lines are metrical units, syntax continues across)
raw=clean_gutenberg('data/ref/it_dante.txt'); vl=[tokenize_natural(x) for x in raw.split('\n')]; vl=[l for l in vl if len(l)>=4]
vp=[vl[i:i+20] for i in range(0,len(vl)-20,20)]
report(vp,'Dante verse')
