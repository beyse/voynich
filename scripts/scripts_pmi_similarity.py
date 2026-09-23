"""Where does adjacent-word information come from? Decompose within-line d=1 excess MI by edit distance
between the two words. Language: information sits in DISSIMILAR collocations. Copy/table generation: in SIMILAR pairs."""
import sys, math, random
sys.path.insert(0,'.')
from voynich.ivtff import parse
from voynich.stats import clean_gutenberg, tokenize_natural
from collections import Counter, defaultdict
exec(open('scripts/scripts_families.py').read().split("L=parse")[0])
def lev(a,b):
    if a==b: return 0
    prev=list(range(len(b)+1))
    for i,ca in enumerate(a,1):
        cur=[i]
        for j,cb in enumerate(b,1): cur.append(min(prev[j]+1,cur[j-1]+1,prev[j-1]+(ca!=cb)))
        prev=cur
    return prev[-1]
def contrib(pairs):
    pa=Counter(a for a,b in pairs); pb=Counter(b for a,b in pairs); pab=Counter(pairs); n=len(pairs)
    return {ab:c/n*math.log2((c/n)/((pa[ab[0]]/n)*(pb[ab[1]]/n))) for ab,c in pab.items()}, pab
def bucket(a,b):
    if a==b: return 'ED=0'
    d=lev(a,b); return 'ED=1' if d==1 else ('ED=2' if d==2 else 'ED>=3')
def decompose(pairs,label,reps=3):
    obs,pab=contrib(pairs); ob=defaultdict(float)
    for ab,v in obs.items(): ob[bucket(*ab)]+=v
    base=defaultdict(float)
    for r in range(reps):
        bs=[b for a,b in pairs]; random.Random(r).shuffle(bs); sh,_=contrib(list(zip([a for a,b in pairs],bs)))
        for ab,v in sh.items(): base[bucket(*ab)]+=v/reps
    tot=sum(ob.values())-sum(base.values())
    print(f"{label:<12} total excess={tot:6.3f} | "+" ".join(f"{k}: {ob[k]-base[k]:6.3f}" for k in ('ED=0','ED=1','ED=2','ED>=3')))
    # top collocations by count*PMI (only pairs seen >=5 times)
    top=sorted(((v,ab,pab[ab]) for ab,v in obs.items() if pab[ab]>=5),reverse=True)[:12]
    print("   top:",", ".join(f"{a} {b}({c})" for v,(a,b),c in top))
L=parse('data/ZL3b-n.txt'); ok=lambda w: w and '?' not in w and '*' not in w
lines=[[w for w in ln.words if ok(w)] for ln in L if ln.kind=='P']; lines=[l for l in lines if len(l)>=5]
inner=lambda ls:[(l[i],l[i+1]) for l in ls for i in range(1,len(l)-2)]
decompose(inner(lines),'VMS raw'); decompose(inner([[light(w) for w in l] for l in lines]),'VMS light'); decompose(inner([[heavy(w) for w in l] for l in lines]),'VMS heavy')
for lang in 'AB':
    ls=[[w for w in ln.words if ok(w)] for ln in L if ln.kind=='P' and ln.lang==lang]; ls=[l for l in ls if len(l)>=5]
    decompose(inner([[light(w) for w in l] for l in ls]),f'VMS-{lang} light')
lens=[len(l) for l in lines]
def chunk(words):
    rng=random.Random(2); out=[]; i=0
    while i<len(words)-12:
        k=rng.choice(lens); out.append(words[i:i+k]); i+=k
    return out
la=tokenize_natural(open('data/ref/la_caesar.txt').read())[:35000]; it=tokenize_natural(clean_gutenberg('data/ref/it_dante.txt'))[:35000]; de=tokenize_natural(clean_gutenberg('data/ref/de_faust.txt'))[:35000]
decompose(inner(chunk(la)),'Latin'); decompose(inner(chunk([x[:4] for x in la])),'Latin stem4'); decompose(inner(chunk(it)),'Italian'); decompose(inner(chunk(de)),'German')
