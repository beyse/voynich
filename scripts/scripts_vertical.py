"""Copy-process signature test.
For each word w_i in line n, similarity to (a) previous word in same line, (b) words directly above
(index i-1..i+1 in line n-1), (c) random word from the same page, (d) random word from same language elsewhere.
If a copy process (Timm & Schinner) generated the text, (a)/(b) should beat the same-page control (c)."""
import sys, random
sys.path.insert(0,'.')
from voynich.ivtff import parse
from collections import defaultdict, Counter

def lev(a,b):
    if a==b: return 0
    prev=list(range(len(b)+1))
    for i,ca in enumerate(a,1):
        cur=[i]
        for j,cb in enumerate(b,1):
            cur.append(min(prev[j]+1,cur[j-1]+1,prev[j-1]+(ca!=cb)))
        prev=cur
    return prev[-1]

L=parse('data/ZL3b-n.txt')
ok=lambda w: w and '?' not in w and '*' not in w
pages=defaultdict(list)   # page -> list of lines (each list of words), paragraph text only, in order
for ln in L:
    if ln.kind!='P': continue
    ws=[w for w in ln.words if ok(w)]
    if len(ws)>=2: pages[ln.page].append((ln.lang,ws))
rng=random.Random(0)
bylang=defaultdict(list)
for p,ls in pages.items():
    for lang,ws in ls: bylang[lang].extend(ws)

def stats(pairs):
    d=[lev(a,b) for a,b in pairs]; n=len(d)
    return n, sum(d)/n, sum(1 for x in d if x==0)/n, sum(1 for x in d if x<=1)/n, sum(1 for x in d if x<=2)/n

res={k:[] for k in ['prev word','word above (i-1..i+1, min)','word above (same index)','random same page','random same lang','2 lines above (same index)']}
for p,ls in pages.items():
    pagewords=[w for _,ws in ls for w in ws]
    for n,(lang,ws) in enumerate(ls):
        for i,w in enumerate(ws):
            if i>0: res['prev word'].append((w,ws[i-1]))
            if n>0:
                above=ls[n-1][1]
                cands=[above[j] for j in (i-1,i,i+1) if 0<=j<len(above)]
                if cands:
                    best=min(cands,key=lambda v: lev(w,v)); res['word above (i-1..i+1, min)'].append((w,best))
                if i<len(above): res['word above (same index)'].append((w,above[i]))
            if n>1:
                ab2=ls[n-2][1]
                if i<len(ab2): res['2 lines above (same index)'].append((w,ab2[i]))
            res['random same page'].append((w,rng.choice(pagewords)))
            res['random same lang'].append((w,rng.choice(bylang[lang])))
print(f"{'relation':<32}{'pairs':>7}{'meanED':>8}{'P(ED=0)':>9}{'P(ED<=1)':>10}{'P(ED<=2)':>10}")
for k,v in res.items():
    n,m,p0,p1,p2=stats(v); print(f"{k:<32}{n:>7}{m:>8.2f}{p0:>9.3f}{p1:>10.3f}{p2:>10.3f}")

# fair control for the 'min over 3 candidates' relation: min over 3 random same-page words
ctrl=[]
for p,ls in pages.items():
    pagewords=[w for _,ws in ls for w in ws]
    for n,(lang,ws) in enumerate(ls):
        if n==0: continue
        for i,w in enumerate(ws):
            cands=rng.sample(pagewords,min(3,len(pagewords)))
            ctrl.append((w,min(cands,key=lambda v: lev(w,v))))
n,m,p0,p1,p2=stats(ctrl); print(f"{'min over 3 random same page':<32}{n:>7}{m:>8.2f}{p0:>9.3f}{p1:>10.3f}{p2:>10.3f}")

# Split by language
for lang in ('A','B'):
    sub={k:[] for k in ['prev word','word above (same index)','random same page']}
    for p,ls in pages.items():
        pagewords=[w for _,ws in ls for w in ws]
        for n,(lg,ws) in enumerate(ls):
            if lg!=lang: continue
            for i,w in enumerate(ws):
                if i>0: sub['prev word'].append((w,ws[i-1]))
                if n>0 and i<len(ls[n-1][1]): sub['word above (same index)'].append((w,ls[n-1][1][i]))
                sub['random same page'].append((w,rng.choice(pagewords)))
    print(f"\nlanguage {lang}:")
    for k,v in sub.items():
        n,m,p0,p1,p2=stats(v); print(f"  {k:<30}{n:>7}{m:>8.2f}{p0:>9.3f}{p1:>10.3f}{p2:>10.3f}")
