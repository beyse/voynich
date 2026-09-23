"""Are line-initial / line-final words page-independent 'markers'?
(1) I(word; page) by line position, equal n.  (2) MI between adjacent lines by position class.  (3) diversity by position."""
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
def excess(pairs,reps=5):
    base=[]
    for r in range(reps):
        bs=[b for a,b in pairs]; random.Random(r).shuffle(bs); base.append(mi(list(zip([a for a,b in pairs],bs))))
    return mi(pairs)-sum(base)/reps
def H(ws):
    c=Counter(ws); n=len(ws); return -sum(v/n*math.log2(v/n) for v in c.values())
pages=defaultdict(list)
for ln in L:
    if ln.kind!='P': continue
    ws=[w for w in ln.words if ok(w)]
    if len(ws)>=4: pages[ln.page].append(ws)
def analyse(pages,label,f=lambda w:w):
    rng=random.Random(0)
    pos={'first':[],'second':[],'middle':[],'penult':[],'last':[]}
    for pg,ls in pages.items():
        for l in ls:
            l=[f(w) for w in l]
            pos['first'].append((pg,l[0])); pos['second'].append((pg,l[1])); pos['last'].append((pg,l[-1])); pos['penult'].append((pg,l[-2]))
            for w in l[2:-2]: pos['middle'].append((pg,w))
    n=min(len(v) for v in pos.values())
    print(f"\n{label}: I(word;page) and diversity, n={n} per position")
    for k,v in pos.items():
        vals=[excess(rng.sample(v,n)) for _ in range(4)]; m=sum(vals)/4
        ws=[w for _,w in rng.sample(v,n)]
        print(f"  {k:<7} I(word;page)={m:.3f}   types/n={len(set(ws))/n:.3f}  H={H(ws):.2f}")
    # adjacent lines: which positions are linked?
    combos={'mid_k -> mid_k+1':[], 'last_k -> first_k+1':[], 'mid_k -> first_k+1':[], 'last_k -> mid_k+1':[], 'first_k -> first_k+1':[], 'last_k -> last_k+1':[]}
    for pg,ls in pages.items():
        for k in range(len(ls)-1):
            a=[f(w) for w in ls[k]]; b=[f(w) for w in ls[k+1]]
            ma=rng.choice(a[2:-2]) if len(a)>4 else a[2]; mb=rng.choice(b[2:-2]) if len(b)>4 else b[2]
            combos['mid_k -> mid_k+1'].append((ma,mb)); combos['last_k -> first_k+1'].append((a[-1],b[0]))
            combos['mid_k -> first_k+1'].append((ma,b[0])); combos['last_k -> mid_k+1'].append((a[-1],mb))
            combos['first_k -> first_k+1'].append((a[0],b[0])); combos['last_k -> last_k+1'].append((a[-1],b[-1]))
    print("  excess MI between words of consecutive lines (same page):")
    for k,v in combos.items(): print(f"    {k:<22} n={len(v):>5}  {excess(v):.3f}")
analyse(pages,'VMS raw'); analyse(pages,'VMS light',light)
# natural control: Latin chunked into the same page/line shapes
shape=[[len(l) for l in pg] for pg in pages.values()]
def chunk(words):
    out={}; i=0
    for p,pg in enumerate(shape):
        npg=[]
        for k in pg:
            if i+k>len(words): break
            npg.append(words[i:i+k]); i+=k
        if npg: out[p]=npg
    return out
la=tokenize_natural(open('data/ref/la_caesar.txt').read()); it=tokenize_natural(clean_gutenberg('data/ref/it_dante.txt'))
analyse(chunk(la),'Latin (chunked)'); analyse(chunk(it),'Italian (chunked)')
