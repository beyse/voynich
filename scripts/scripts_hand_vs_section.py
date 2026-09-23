"""Do the glyph-process parameters follow the scribe (hand) or the content (section)?
JSD of glyph-bigram distributions between pages, grouped by same/different hand x same/different section (and language)."""
import sys, math, random, re
sys.path.insert(0,'.')
from voynich.ivtff import parse
from collections import Counter, defaultdict
ok=lambda w: w and '?' not in w and '*' not in w
L=parse('data/ZL3b-n.txt',comma_is_space=False)
pages=defaultdict(list); meta={}
for ln in L:
    if ln.kind!='P': continue
    ws=[w for w in ln.words if ok(w)]
    if len(ws)>=2: pages[ln.page].append(ws); meta[ln.page]=(ln.lang,ln.section,ln.hand)
def bigrams(lines,n,rng):
    s=' '.join(' '.join(l) for l in lines); st=rng.randrange(0,len(s)-n); s=s[st:st+n]; return Counter(zip(s,s[1:]))
def jsd(c1,c2,alpha=0.05):
    keys=set(c1)|set(c2); n1=sum(c1.values())+alpha*len(keys); n2=sum(c2.values())+alpha*len(keys)
    p=[(c1[k]+alpha)/n1 for k in keys]; q=[(c2[k]+alpha)/n2 for k in keys]; m=[(a+b)/2 for a,b in zip(p,q)]
    return 0.5*sum(a*math.log2(a/mm) for a,mm in zip(p,m))+0.5*sum(b*math.log2(b/mm) for b,mm in zip(q,m))
rng=random.Random(0); N=450
items=[(pg,meta[pg]) for pg,ls in pages.items() if len(' '.join(' '.join(l) for l in ls))>=N and all(meta[pg])]
print("pages per (language, section, hand):")
cnt=Counter(m for _,m in items)
for k,v in sorted(cnt.items(),key=str): print("  ",k,v)
groups=defaultdict(list)
for i,(p1,m1) in enumerate(items):
    for p2,m2 in items[i+1:]:
        for _ in range(2):
            v=jsd(bigrams(pages[p1],N,rng),bigrams(pages[p2],N,rng))
            key=('same lang' if m1[0]==m2[0] else 'diff lang','same sect' if m1[1]==m2[1] else 'diff sect','same hand' if m1[2]==m2[2] else 'diff hand')
            groups[key].append(v)
print("\nmean JSD between pages (n pairs):")
for k in sorted(groups): print(f"  {k[0]:<10}{k[1]:<11}{k[2]:<10} {sum(groups[k])/len(groups[k]):.4f}  (n={len(groups[k])})")
# Focused contrasts within the same language
print("\nwithin same Currier language:")
for lang in 'AB':
    sub=defaultdict(list)
    for i,(p1,m1) in enumerate(items):
        for p2,m2 in items[i+1:]:
            if m1[0]!=lang or m2[0]!=lang: continue
            v=jsd(bigrams(pages[p1],N,rng),bigrams(pages[p2],N,rng))
            sub[('same sect' if m1[1]==m2[1] else 'diff sect','same hand' if m1[2]==m2[2] else 'diff hand')].append(v)
    for k in sorted(sub): print(f"  lang {lang}: {k[0]:<10}{k[1]:<10} {sum(sub[k])/len(sub[k]):.4f} (n={len(sub[k])})")
