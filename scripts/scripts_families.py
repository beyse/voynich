"""Within-line vs across-line word-order information, before/after collapsing variant glyphs into families."""
import sys, math, random, re
sys.path.insert(0,'.')
from voynich.ivtff import parse
from voynich.stats import clean_gutenberg, tokenize_natural, zipf_slope
from collections import Counter, defaultdict

def light(w):
    w=w.replace('sh','ch')
    for g in ('cth','cph','cfh'): w=w.replace(g,'ckh')
    w=re.sub(r'[tpf]','k',w)
    w=re.sub(r'i+','i',w); w=re.sub(r'e+','e',w)
    w=re.sub(r'[mg]$','in',w)   # line-final variants
    return w
def heavy(w):
    w=light(w); w=re.sub(r'^q','',w); w=w.replace('a','o'); w=re.sub(r'dy$','y',w)
    w=re.sub(r'^[ys]','',w) or w    # y-/s- prefixes at line starts
    return w

L=parse('data/ZL3b-n.txt')
ok=lambda w: w and '?' not in w and '*' not in w
lines=[[w for w in ln.words if ok(w)] for ln in L if ln.kind=='P']
lines=[l for l in lines if len(l)>=2]

def mi_pairs(pairs):
    pa=Counter(a for a,b in pairs); pb=Counter(b for a,b in pairs); pab=Counter(pairs); n=len(pairs)
    return sum(c/n*math.log2((c/n)/((pa[a]/n)*(pb[b]/n))) for (a,b),c in pab.items())
def excess(pairs,reps=3):
    obs=mi_pairs(pairs); base=[]
    for r in range(reps):
        bs=[b for a,b in pairs]; random.Random(r).shuffle(bs); base.append(mi_pairs(list(zip([a for a,b in pairs],bs))))
    return obs-sum(base)/reps, obs

def pairsets(lines, f=lambda w:w):
    within=[(f(l[i]),f(l[i+1])) for l in lines for i in range(len(l)-1)]
    within_inner=[(f(l[i]),f(l[i+1])) for l in lines for i in range(1,len(l)-2)]  # excludes first & last word of line
    across=[(f(lines[k][-1]),f(lines[k+1][0])) for k in range(len(lines)-1)]
    d2=[(f(l[i]),f(l[i+2])) for l in lines for i in range(len(l)-2)]
    return within,within_inner,across,d2

print(f"{'variant collapse':<10}{'types':>7}{'zipf':>6} | excess MI: {'within':>7}{'inner':>7}{'across':>7}{'d=2':>7}")
for name,f in [('none',lambda w:w),('light',light),('heavy',heavy)]:
    types=len({f(w) for l in lines for w in l}); z=zipf_slope([f(w) for l in lines for w in l])
    w,wi,a,d2=pairsets(lines,f)
    print(f"{name:<10}{types:>7}{z:>6.2f} | {excess(w)[0]:>18.3f}{excess(wi)[0]:>7.3f}{excess(a)[0]:>7.3f}{excess(d2)[0]:>7.3f}")

# Natural-language comparison: same measures for Latin with 'lines' of ~8 words; also with a crude
# 'family' collapse (first 4 letters = stem) to see how much MI survives collapsing inflection.
w=tokenize_natural(open('data/ref/la_caesar.txt').read())[:35000]
lat=[w[i:i+8] for i in range(0,len(w)-8,8)]
for name,f in [('la none',lambda x:x),('la stem4',lambda x:x[:4])]:
    types=len({f(x) for l in lat for x in l}); z=zipf_slope([f(x) for l in lat for x in l])
    wn,wi,a,d2=pairsets(lat,f)
    print(f"{name:<10}{types:>7}{z:>6.2f} | {excess(wn)[0]:>18.3f}{excess(wi)[0]:>7.3f}{excess(a)[0]:>7.3f}{excess(d2)[0]:>7.3f}")
it=tokenize_natural(clean_gutenberg('data/ref/it_dante.txt'))[:35000]
itl=[it[i:i+8] for i in range(0,len(it)-8,8)]
for name,f in [('it none',lambda x:x),('it stem4',lambda x:x[:4])]:
    types=len({f(x) for l in itl for x in l}); z=zipf_slope([f(x) for l in itl for x in l])
    wn,wi,a,d2=pairsets(itl,f)
    print(f"{name:<10}{types:>7}{z:>6.2f} | {excess(wn)[0]:>18.3f}{excess(wi)[0]:>7.3f}{excess(a)[0]:>7.3f}{excess(d2)[0]:>7.3f}")

# How much of the *variant* (word minus family) is explained by position in line?
print("\nvariant features by line position (share of words having the feature):")
feats={'starts q':lambda w:w.startswith('q'),'starts y':lambda w:w.startswith('y'),'starts s':lambda w:w.startswith('s'),
       'starts gallows':lambda w:w[0] in 'ktpf','starts ch/sh':lambda w:w.startswith(('ch','sh')),'ends m/g':lambda w:w[-1] in 'mg',
       'ends y':lambda w:w.endswith('y'),'ends n':lambda w:w.endswith('n'),'has sh':lambda w:'sh' in w,'has iii':lambda w:'iii' in w}
pos={'first':[l[0] for l in lines],'second':[l[1] for l in lines if len(l)>2],'middle':[x for l in lines for x in l[2:-1]],'last':[l[-1] for l in lines]}
print(f"{'feature':<16}"+"".join(f"{p:>8}" for p in pos))
for k,f in feats.items():
    print(f"{k:<16}"+"".join(f"{sum(map(f,v))/len(v):>8.3f}" for v in pos.values()))
