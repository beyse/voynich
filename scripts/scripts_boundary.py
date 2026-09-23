"""Where is the within-line ordering information? (1) cross-boundary glyph MI vs within-line shuffle.
(2) word-pair excess MI vs within-line null decomposed by ED. (3) line composition clumpiness."""
import sys, re, random, math
sys.path.insert(0,'.')
from voynich.ivtff import parse
from voynich.stats import clean_gutenberg, tokenize_natural
from collections import Counter, defaultdict
ok=lambda w: w and '?' not in w and '*' not in w
def lev(a,b):
    if a==b: return 0
    prev=list(range(len(b)+1))
    for i,ca in enumerate(a,1):
        cur=[i]
        for j,cb in enumerate(b,1): cur.append(min(prev[j]+1,cur[j-1]+1,prev[j-1]+(ca!=cb)))
        prev=cur
    return prev[-1]
def mi(pairs):
    pa=Counter(a for a,b in pairs); pb=Counter(b for a,b in pairs); pab=Counter(pairs); n=len(pairs)
    return sum(c/n*math.log2((c/n)/((pa[a]/n)*(pb[b]/n))) for (a,b),c in pab.items())
def within_null(inner,rng): return [rng.sample(s,len(s)) for s in inner]
def adj(inner,f=lambda a,b:(a,b)): return [f(s[i],s[i+1]) for s in inner for i in range(len(s)-1)]
def excess(inner,f,reps=8):
    obs=mi(adj(inner,f)); b=sum(mi(adj(within_null(inner,random.Random(r)),f)) for r in range(reps))/reps; return obs-b
def analyse(lines,label):
    inner=[l[1:-1] for l in lines if len(l)>=5]
    r={}
    r['word']=excess(inner,lambda a,b:(a,b))
    r['last1|first1']=excess(inner,lambda a,b:(a[-1],b[0])); r['last2|first2']=excess(inner,lambda a,b:(a[-2:],b[:2]))
    r['last1|word_b']=excess(inner,lambda a,b:(a[-1],b)); r['word_a|first1']=excess(inner,lambda a,b:(a,b[0]))
    r['last2|word_b']=excess(inner,lambda a,b:(a[-2:],b)); r['word_a|first2']=excess(inner,lambda a,b:(a,b[:2]))
    r['len_a|len_b']=excess(inner,lambda a,b:(len(a),len(b)))
    print(f"{label:<14} "+" ".join(f"{k}={v:6.3f}" for k,v in r.items()))
    return inner
print("excess MI (bits) of adjacent inner pairs over within-line shuffle, for various projections:")
for comma in (False,True):
    L=parse('data/ZL3b-n.txt',comma_is_space=comma)
    for lang in (None,'A','B'):
        lines=[[w for w in ln.words if ok(w)] for ln in L if ln.kind=='P' and (lang is None or ln.lang==lang)]
        analyse(lines,f"VMS{lang or ''} {'c=sp' if comma else 'c=jn'}")
L=parse('data/ZL3b-n.txt'); lens=[len([w for w in ln.words if ok(w)]) for ln in L if ln.kind=='P']
def chunk(words):
    rng=random.Random(2); out=[]; i=0
    while i<len(words)-12:
        k=rng.choice(lens); out.append(words[i:i+k]); i+=k
    return out
la=tokenize_natural(open('data/ref/la_caesar.txt').read())[:35000]; it=tokenize_natural(clean_gutenberg('data/ref/it_dante.txt'))[:35000]; de=tokenize_natural(clean_gutenberg('data/ref/de_faust.txt'))[:35000]
he=re.findall(r'[א-ת]+',open('data/ref/he_genesis.txt',encoding='utf-8').read())
analyse(chunk(la),'Latin'); analyse(chunk(it),'Italian'); analyse(chunk(de),'German'); analyse(chunk(he),'Hebrew')

# (2) decomposition of word-level excess (within-line null) by ED bucket + top pairs vs null expectation
print("\nVMS (comma joined): word-pair excess over within-line null by ED bucket, and top over-represented adjacent pairs")
L=parse('data/ZL3b-n.txt',comma_is_space=False)
lines=[[w for w in ln.words if ok(w)] for ln in L if ln.kind=='P']; inner=[l[1:-1] for l in lines if len(l)>=5]
def contrib(pairs):
    pa=Counter(a for a,b in pairs); pb=Counter(b for a,b in pairs); pab=Counter(pairs); n=len(pairs)
    return {ab:c/n*math.log2((c/n)/((pa[ab[0]]/n)*(pb[ab[1]]/n))) for ab,c in pab.items()}, pab
obs,pab=contrib(adj(inner)); ob=defaultdict(float)
def bucket(a,b):
    if a==b: return 'ED=0'
    d=lev(a,b); return f'ED={d}' if d<=2 else 'ED>=3'
for ab,v in obs.items(): ob[bucket(*ab)]+=v
base=defaultdict(float); nullcount=Counter(); reps=8
for r in range(reps):
    sh,pn=contrib(adj(within_null(inner,random.Random(r))))
    for ab,v in sh.items(): base[bucket(*ab)]+=v/reps
    for ab,c in pn.items(): nullcount[ab]+=c/reps
print("  "+" ".join(f"{k}: {ob[k]-base[k]:6.3f}" for k in ('ED=0','ED=1','ED=2','ED>=3')))
top=sorted(((c-nullcount[ab])/math.sqrt(nullcount[ab]+1),ab,c,nullcount[ab]) for ab,c in pab.items() if c>=8)
print("  top pairs by (obs-null)/sqrt(null):")
for z,(a,b),c,e in top[::-1][:20]: print(f"    {a:>8} {b:<8} obs={c:>3} null={e:5.1f} z={z:4.1f}")
print("  most UNDER-represented (obs<<null):")
for z,(a,b),c,e in top[:10]: print(f"    {a:>8} {b:<8} obs={c:>3} null={e:5.1f} z={z:4.1f}")

# (3) line composition clumpiness: P(ED<=1) for random pairs within line / page / language
rng=random.Random(0)
pages=defaultdict(list)
for ln in L:
    if ln.kind!='P': continue
    ws=[w for w in ln.words if ok(w)]
    if len(ws)>=4: pages[ln.page].append((ln.lang,ws))
def p_sim(pairs): return sum(lev(a,b)<=1 for a,b in pairs)/len(pairs)
wl=[];wp=[];wg=[]
allw=defaultdict(list)
for pg,ls in pages.items():
    for lang,ws in ls: allw[lang].extend(ws)
for pg,ls in pages.items():
    pw=[w for _,ws in ls for w in ws]
    for lang,ws in ls:
        for _ in range(3):
            a,b=rng.sample(ws,2); wl.append((a,b)); wp.append((a,rng.choice(pw))); wg.append((a,rng.choice(allw[lang])))
print(f"\nP(ED<=1) for random word pairs: same line {p_sim(wl):.3f}, same page {p_sim(wp):.3f}, same language {p_sim(wg):.3f}")
