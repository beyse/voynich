"""Hand effect at fixed folio distance: herbal-B pages written by hands 2, 3 and 5."""
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
def folio(p):
    m=re.match(r'f(\d+)([rv])',p); return int(m.group(1))*2+(m.group(2)=='v')
def bigrams(lines,n,rng):
    s=' '.join(' '.join(l) for l in lines); st=rng.randrange(0,max(1,len(s)-n)); s=s[st:st+n]; return Counter(zip(s,s[1:]))
def jsd(c1,c2,alpha=0.05):
    keys=set(c1)|set(c2); n1=sum(c1.values())+alpha*len(keys); n2=sum(c2.values())+alpha*len(keys)
    p=[(c1[k]+alpha)/n1 for k in keys]; q=[(c2[k]+alpha)/n2 for k in keys]; m=[(a+b)/2 for a,b in zip(p,q)]
    return 0.5*sum(a*math.log2(a/mm) for a,mm in zip(p,m))+0.5*sum(b*math.log2(b/mm) for b,mm in zip(q,m))
rng=random.Random(0); N=350
for lang,sec in [('B','H'),('B','S'),('A','H')]:
    it=[p for p in pages if meta[p][0]==lang and meta[p][1]==sec and meta[p][2] and len(' '.join(' '.join(l) for l in pages[p]))>=N]
    print(f"\n{lang}-{sec}: {len(it)} pages; hands {Counter(meta[p][2] for p in it)}; folios {min(folio(p) for p in it)//2}-{max(folio(p) for p in it)//2}")
    bins=defaultdict(list)
    for i,p1 in enumerate(it):
        for p2 in it[i+1:]:
            d=abs(folio(p1)-folio(p2)); db='d<=6' if d<=6 else 'd<=20' if d<=20 else 'd>20'
            same='same hand' if meta[p1][2]==meta[p2][2] else 'diff hand'
            for _ in range(3): bins[(db,same)].append(jsd(bigrams(pages[p1],N,rng),bigrams(pages[p2],N,rng)))
    for k in sorted(bins): print(f"   {k[0]:<6} {k[1]:<10} {sum(bins[k])/len(bins[k]):.4f} (n={len(bins[k])//3} pairs)")
# also: which hand-specific glyph features? top bigram differences between hand 2 and hand 3 within herbal-B
it=[p for p in pages if meta[p][0]=='B' and meta[p][1]=='H']
c=defaultdict(Counter)
for p in it:
    s=' '.join(' '.join(l) for l in pages[p]); c[meta[p][2]].update(zip(s,s[1:]))
for h in c:
    n=sum(c[h].values()); c[h]=Counter({k:v/n for k,v in c[h].items()})
if '2' in c and '3' in c:
    diff=sorted(((c['2'][k]-c['3'][k]),k) for k in set(c['2'])|set(c['3']))
    print("\nherbal-B bigrams over-used by hand 2 vs hand 3:",[(''.join(k),round(v*100,2)) for v,k in diff[-8:][::-1]])
    print("herbal-B bigrams over-used by hand 3 vs hand 2:",[(''.join(k),round(-v*100,2)) for v,k in diff[:8]])
