"""Is the absence of across-line MI real? Compare against within-line pairs subsampled to the SAME n,
with bootstrap spread; restrict across-line pairs to consecutive lines of the same paragraph."""
import sys, math, random, re
sys.path.insert(0,'.')
from voynich.ivtff import parse
from voynich.stats import clean_gutenberg, tokenize_natural
from collections import Counter
exec(open('scripts/scripts_families.py').read().split("L=parse")[0])   # reuse light/heavy
L=parse('data/ZL3b-n.txt')
ok=lambda w: w and '?' not in w and '*' not in w
# paragraphs: consecutive P lines; a new paragraph starts at locus '@'/'*' or page change
paras=[]; cur=[]; prev_page=None
for ln in L:
    if ln.kind!='P': continue
    ws=[w for w in ln.words if ok(w)]
    if ln.locus[0] in '@*' or ln.page!=prev_page:
        if cur: paras.append(cur)
        cur=[]
    prev_page=ln.page
    if len(ws)>=2: cur.append(ws)
if cur: paras.append(cur)
print("paragraphs:",len(paras),"lines:",sum(map(len,paras)))

def mi_pairs(pairs):
    pa=Counter(a for a,b in pairs); pb=Counter(b for a,b in pairs); pab=Counter(pairs); n=len(pairs)
    return sum(c/n*math.log2((c/n)/((pa[a]/n)*(pb[b]/n))) for (a,b),c in pab.items())
def excess(pairs,reps=5,seed=0):
    obs=mi_pairs(pairs); base=[]
    for r in range(reps):
        bs=[b for a,b in pairs]; random.Random(seed*100+r).shuffle(bs); base.append(mi_pairs(list(zip([a for a,b in pairs],bs))))
    return obs-sum(base)/reps

def run(paras,f,label):
    across=[(f(p[k][-1]),f(p[k+1][0])) for p in paras for k in range(len(p)-1)]
    within=[(f(l[i]),f(l[i+1])) for p in paras for l in p for i in range(len(l)-1)]
    inner=[(f(l[i]),f(l[i+1])) for p in paras for l in p for i in range(1,len(l)-2)]
    # across-line pairs but skipping the edge words: last-but-one of line k with second of line k+1 (distance 3)
    across_inner=[(f(p[k][-2]),f(p[k+1][1])) for p in paras for k in range(len(p)-1) if len(p[k])>=3 and len(p[k+1])>=3]
    within_d3=[(f(l[i]),f(l[i+3])) for p in paras for l in p for i in range(len(l)-3)]
    n=len(across); rng=random.Random(1)
    def sub(pairs,reps=8):
        vals=[excess(rng.sample(pairs,min(n,len(pairs))),seed=r) for r in range(reps)]
        m=sum(vals)/len(vals); sd=(sum((v-m)**2 for v in vals)/len(vals))**0.5
        return m,sd
    a=excess(across); w=sub(within); i=sub(inner); ai=excess(across_inner); w3=sub(within_d3)
    print(f"{label:<12} n={n:>5} | across={a:6.3f} | within(same n)={w[0]:6.3f}±{w[1]:.3f} | inner(same n)={i[0]:6.3f}±{i[1]:.3f} | across-inner(d3)={ai:6.3f} | within d=3 (same n)={w3[0]:6.3f}±{w3[1]:.3f}")

for name,f in [('VMS none',lambda w:w),('VMS light',light),('VMS heavy',heavy)]:
    run(paras,f,name)
# language A / B separately
for lang in 'AB':
    pl=[]; cur=[]; prev=None
    for ln in L:
        if ln.kind!='P' or ln.lang!=lang: continue
        ws=[w for w in ln.words if ok(w)]
        if ln.locus[0] in '@*' or ln.page!=prev:
            if cur: pl.append(cur)
            cur=[]
        prev=ln.page
        if len(ws)>=2: cur.append(ws)
    if cur: pl.append(cur)
    run(pl,light,f'VMS-{lang} light')
# natural-language controls with VMS-like line lengths (sample real line lengths) and paragraphs of ~6 lines
lens=[len(l) for p in paras for l in p]
def chunk(words):
    rng=random.Random(2); out=[]; i=0
    while i<len(words)-12:
        para=[]
        for _ in range(rng.randint(3,10)):
            k=rng.choice(lens); para.append(words[i:i+k]); i+=k
        out.append(para)
    return out
la=tokenize_natural(open('data/ref/la_caesar.txt').read())[:35000]
it=tokenize_natural(clean_gutenberg('data/ref/it_dante.txt'))[:35000]
de=tokenize_natural(clean_gutenberg('data/ref/de_faust.txt'))[:35000]
run(chunk(la),lambda x:x,'Latin'); run(chunk(la),lambda x:x[:4],'Latin stem4')
run(chunk(it),lambda x:x,'Italian'); run(chunk(de),lambda x:x,'German')
