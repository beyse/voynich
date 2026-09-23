"""Does word order carry information? Word-bigram mutual information at distance d, minus shuffled baseline."""
import sys, re, math, random
sys.path.insert(0,'.')
from voynich.ivtff import parse, words_of
from voynich.stats import clean_gutenberg, tokenize_natural
from collections import Counter
def mi(words,d):
    pa=Counter(words[:-d]); pb=Counter(words[d:]); pab=Counter(zip(words[:-d],words[d:])); n=len(words)-d
    return sum(c/n*math.log2((c/n)/((pa[a]/n)*(pb[b]/n))) for (a,b),c in pab.items())
def mi_corrected(words,d,reps=3):
    obs=mi(words,d); base=[]
    for r in range(reps):
        w=list(words); random.Random(r).shuffle(w); base.append(mi(w,d))
    return obs, sum(base)/reps
L=parse('data/ZL3b-n.txt')
# VMS: build word stream respecting line order within pages; only paragraph text
V=words_of(L,kind='P'); N=len(V)
corp={'VMS':V,'VMS-A':words_of(L,kind='P',lang='A'),'VMS-B':words_of(L,kind='P',lang='B')}
for name,path in [('de','data/ref/de_faust.txt'),('it','data/ref/it_dante.txt'),('la','data/ref/la_caesar.txt'),('en','data/ref/en_war_and_peace.txt')]:
    t=clean_gutenberg(path) if name!='la' else open(path).read()
    corp[name]=tokenize_natural(t)[:N]
corp['he']=re.findall(r'[א-ת]+',open('data/ref/he_genesis.txt',encoding='utf-8').read())
print(f"{'corpus':<8}{'N':>7} | d=1: obs  base  excess | d=2 excess | d=5 excess | d=20 excess")
for name,w in corp.items():
    row=f"{name:<8}{len(w):>7} |"
    for d in (1,2,5,20):
        o,b=mi_corrected(w,d)
        row+= f" {o:5.2f} {b:5.2f} {o-b:6.3f} |" if d==1 else f" {o-b:6.3f} |"
    print(row)
# Same, but conditioned on word being frequent (top 100 words only, others mapped to OTHER) to reduce sparsity
print("\nMI with vocabulary reduced to top-100 words (+OTHER):")
for name,w in corp.items():
    top={x for x,_ in Counter(w).most_common(100)}
    r=[x if x in top else '#' for x in w]
    row=f"{name:<8}|"
    for d in (1,2,5,20):
        o,b=mi_corrected(r,d); row+=f" d={d}: {o-b:6.3f}"
    print(row)
