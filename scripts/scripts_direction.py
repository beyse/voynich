"""Directionality of single-glyph edits between adjacent words (ED=1). Random copy: symmetric. Systematic encoding: asymmetric."""
import sys, math
sys.path.insert(0,'.')
from voynich.ivtff import parse
from collections import Counter
ok=lambda w: w and '?' not in w and '*' not in w
def edit1(a,b):
    """return (kind, glyph, relpos) for a single edit turning a into b, or None"""
    if a==b: return None
    if len(a)==len(b):
        d=[i for i in range(len(a)) if a[i]!=b[i]]
        if len(d)!=1: return None
        i=d[0]; return ('sub',a[i]+'>'+b[i],'start' if i==0 else ('end' if i==len(a)-1 else 'mid'))
    if len(b)==len(a)+1:
        for i in range(len(b)):
            if b[:i]+b[i+1:]==a: return ('ins',b[i],'start' if i==0 else ('end' if i==len(b)-1 else 'mid'))
    if len(a)==len(b)+1:
        r=edit1(b,a)
        if r: return ('del',r[1],r[2])
    return None
def inverse(e):
    k,g,p=e
    if k=='ins': return ('del',g,p)
    if k=='del': return ('ins',g,p)
    x,y=g.split('>'); return ('sub',y+'>'+x,p)
L=parse('data/ZL3b-n.txt',comma_is_space=False)
for lang in (None,'A','B'):
    lines=[[w for w in ln.words if ok(w)] for ln in L if ln.kind=='P' and (lang is None or ln.lang==lang)]
    fwd=Counter()
    for l in lines:
        s=l[1:-1]
        for i in range(len(s)-1):
            e=edit1(s[i],s[i+1])
            if e: fwd[e]+=1
    tot=sum(fwd.values())
    print(f"\n== VMS {lang or 'all'}: {tot} adjacent inner pairs with ED=1")
    rows=[]
    for e,n in fwd.items():
        m=fwd[inverse(e)]
        if n+m>=20 and n>=m:
            z=(n-m)/math.sqrt(n+m); rows.append((z,e,n,m))
    rows.sort(reverse=True)
    print(f"{'edit (a->b)':<24}{'a->b':>6}{'b->a':>6}{'z':>7}")
    for z,e,n,m in rows[:22]: print(f"{e[0]+' '+e[1]+' @'+e[2]:<24}{n:>6}{m:>6}{z:>7.1f}")
    # overall asymmetry: fraction of edit mass in edits whose inverse is < half as frequent
    asym=sum(n for e,n in fwd.items() if fwd[inverse(e)]*2<n); print(f"share of ED=1 pairs in strongly directional edits: {asym/tot:.2f}")
    # by position class
    pc=Counter(e[2] for e,n in fwd.items() for _ in range(n)); print("edit position:",dict(pc))
    kc=Counter(e[0] for e,n in fwd.items() for _ in range(n)); print("edit kind:",dict(kc))
