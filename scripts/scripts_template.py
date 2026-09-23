"""Template vs syntax: does the word (family) depend more on its POSITION in the line or on the PREVIOUS word?
I(F; pos) vs I(F_i; F_{i-1}), with vocabulary reduced to top-K families (+OTHER) to control sparsity."""
import sys, math, random, re
sys.path.insert(0,'.')
from voynich.ivtff import parse
from voynich.stats import clean_gutenberg, tokenize_natural
from collections import Counter, defaultdict
exec(open('scripts/scripts_families.py').read().split("L=parse")[0])
L=parse('data/ZL3b-n.txt')
ok=lambda w: w and '?' not in w and '*' not in w
def H(c):
    n=sum(c.values()); return -sum(v/n*math.log2(v/n) for v in c.values())
def mi(pairs):
    pa=Counter(a for a,b in pairs); pb=Counter(b for a,b in pairs); pab=Counter(pairs); n=len(pairs)
    return sum(c/n*math.log2((c/n)/((pa[a]/n)*(pb[b]/n))) for (a,b),c in pab.items())
def excess(pairs,reps=5):
    base=[]
    for r in range(reps):
        bs=[b for a,b in pairs]; random.Random(r).shuffle(bs); base.append(mi(list(zip([a for a,b in pairs],bs))))
    return mi(pairs)-sum(base)/reps
def analyse(lines,K=150,label=''):
    top={w for w,_ in Counter(x for l in lines for x in l).most_common(K)}
    R=[[x if x in top else '#' for x in l] for l in lines]
    pos=lambda i,l: 'F' if i==0 else ('L' if i==len(l)-1 else ('2' if i==1 else 'M'))
    pp=[(pos(i,l),l[i]) for l in R for i in range(len(l))]
    prev=[(l[i-1],l[i]) for l in R for i in range(1,len(l))]
    # previous word, but only for middle positions (exclude first/second/last to remove positional confound)
    prev_mid=[(l[i-1],l[i]) for l in R for i in range(2,len(l)-1)]
    posmid=[(pos(i,l),l[i]) for l in R for i in range(len(l)) if pos(i,l) in ('M','2')]
    print(f"{label:<14} I(word;position)={excess(pp):.3f}  I(word;prev)={excess(prev):.3f}  I(word;prev | middle only)={excess(prev_mid):.3f}   H(word)={H(Counter(x for l in R for x in l)):.2f}")
    return R
lines=[[w for w in ln.words if ok(w)] for ln in L if ln.kind=='P']; lines=[l for l in lines if len(l)>=4]
print("K=150 top families + OTHER; excess MI in bits")
analyse(lines,label='VMS raw'); analyse([[light(w) for w in l] for l in lines],label='VMS light'); Rh=analyse([[heavy(w) for w in l] for l in lines],label='VMS heavy')
lens=[len(l) for l in lines]
def chunk(words):
    rng=random.Random(2); out=[]; i=0
    while i<len(words)-12:
        k=rng.choice(lens); out.append(words[i:i+k]); i+=k
    return out
la=tokenize_natural(open('data/ref/la_caesar.txt').read())[:35000]; it=tokenize_natural(clean_gutenberg('data/ref/it_dante.txt'))[:35000]
analyse(chunk(la),label='Latin (chunks)'); analyse(chunk([x[:4] for x in la]),label='Latin stem4'); analyse(chunk(it),label='Italian')
# Dante is verse: real verse lines (tercets) -> line-structured natural text control
raw=clean_gutenberg('data/ref/it_dante.txt'); vlines=[tokenize_natural(x) for x in raw.split('\n')]; vlines=[l for l in vlines if 4<=len(l)<=12][:6000]
analyse(vlines,label='Dante verse lines')

# Per-position profile (heavy families): which families dominate at first/second/middle/last
print("\ntop heavy-families by line position:")
pos=lambda i,l: 'first' if i==0 else ('last' if i==len(l)-1 else ('second' if i==1 else 'middle'))
byp=defaultdict(Counter)
for l in [[heavy(w) for w in x] for x in lines]:
    for i,w in enumerate(l): byp[pos(i,l)][w]+=1
for p in ('first','second','middle','last'):
    n=sum(byp[p].values()); print(f"  {p:<7}",[(w,round(c/n,3)) for w,c in byp[p].most_common(8)])

# Isolated words vs labels: 'o'-initial share
single=[ln.words[0] for ln in L if ln.kind=='P' and len(ln.words)==1 and ok(ln.words[0])]
labels=[w for ln in L if ln.kind=='L' for w in ln.words if ok(w)]
print(f"\n'o'-initial share: single-word text lines {sum(w[0]=='o' for w in single)/len(single):.2f} (n={len(single)}), labels {sum(w[0]=='o' for w in labels)/len(labels):.2f}, line-first words {sum(l[0][0]=='o' for l in lines)/len(lines):.2f}, middle words {sum(w[0]=='o' for l in lines for w in l[2:-1])/sum(len(l)-3 for l in lines):.2f}")
