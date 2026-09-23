"""How much adjacent-word information survives stricter null models?
Baselines: global shuffle, shuffle within page, shuffle within line. Pairs: middle-only adjacent pairs (both words non-edge)."""
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
def midpairs(pages):
    return [(l[i-1],l[i]) for pg in pages for l in pg for i in range(2,len(l)-1)]
def shuffle_within_page(pages,rng):
    out=[]
    for pg in pages:
        ws=[w for l in pg for w in l]; rng.shuffle(ws); i=0; npg=[]
        for l in pg: npg.append(ws[i:i+len(l)]); i+=len(l)
        out.append(npg)
    return out
def shuffle_within_line(pages,rng):
    out=[]
    for pg in pages:
        npg=[]
        for l in pg: x=list(l); rng.shuffle(x); npg.append(x)
        out.append(npg)
    return out
def shuffle_global(pages,rng):
    ws=[w for pg in pages for l in pg for w in l]; rng.shuffle(ws); i=0; out=[]
    for pg in pages:
        npg=[]
        for l in pg: npg.append(ws[i:i+len(l)]); i+=len(l)
        out.append(npg)
    return out
def report(pages,label,reps=5):
    obs=mi(midpairs(pages)); res=[]
    for name,fn in [('global',shuffle_global),('page',shuffle_within_page),('line',shuffle_within_line)]:
        b=sum(mi(midpairs(fn(pages,random.Random(r))))/reps for r in range(reps)); res.append((name,obs-b))
    n=len(midpairs(pages))
    print(f"{label:<14} n={n:>6} obs={obs:.3f} | excess vs global={res[0][1]:.3f} vs page={res[1][1]:.3f} vs line={res[2][1]:.3f}")
# VMS pages
pages=defaultdict(list)
for ln in L:
    if ln.kind!='P': continue
    ws=[w for w in ln.words if ok(w)]
    if len(ws)>=4: pages[ln.page].append(ws)
P=list(pages.values())
report(P,'VMS raw'); report([[ [light(w) for w in l] for l in pg] for pg in P],'VMS light'); report([[ [heavy(w) for w in l] for l in pg] for pg in P],'VMS heavy')
for lang in 'AB':
    sub=[ [ [light(w) for w in l] for l in [ [w for w in ln.words if ok(w)] for ln in L if ln.kind=='P' and ln.page==pg and ln.lang==lang] if len(l)>=4] for pg in pages]
    sub=[pg for pg in sub if pg]; report(sub,f'VMS-{lang} light')
# natural texts chunked into VMS-like pages (same line lengths, same lines per page)
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
