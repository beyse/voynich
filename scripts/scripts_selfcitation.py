"""Test the Timm & Schinner observation: adjacent/nearby words are unusually similar (edit distance)."""
import sys, random
sys.path.insert(0,'.')
from voynich.ivtff import parse, words_of
from voynich.stats import clean_gutenberg, tokenize_natural
from collections import Counter

def lev(a,b):
    if a==b: return 0
    prev=list(range(len(b)+1))
    for i,ca in enumerate(a,1):
        cur=[i]
        for j,cb in enumerate(b,1):
            cur.append(min(prev[j]+1,cur[j-1]+1,prev[j-1]+(ca!=cb)))
        prev=cur
    return prev[-1]

def adjacent_similarity(words, gap=1, n=20000, seed=0):
    random.seed(seed)
    pairs=[(words[i],words[i+gap]) for i in range(len(words)-gap)]
    pairs=random.sample(pairs,min(n,len(pairs)))
    d=[lev(a,b) for a,b in pairs]
    same=sum(1 for a,b in pairs if a==b)/len(pairs)
    d1=sum(1 for x in d if x<=1)/len(d)
    return sum(d)/len(d), same, d1

def shuffled_baseline(words, gap=1, n=20000, seed=1):
    w=list(words); random.Random(seed).shuffle(w)
    return adjacent_similarity(w,gap,n)

L=parse('data/ZL3b-n.txt')
corp={'VMS A':words_of(L,kind='P',lang='A'),'VMS B':words_of(L,kind='P',lang='B')}
for name,path in [('de_faust','data/ref/de_faust.txt'),('la_caesar','data/ref/la_caesar.txt'),('it_dante','data/ref/it_dante.txt')]:
    t=clean_gutenberg(path) if name!='la_caesar' else open(path).read()
    corp[name]=tokenize_natural(t)[:35000]
print(f"{'corpus':<10}{'gap':>4}{'meanED':>8}{'P(same)':>9}{'P(ED<=1)':>10} | shuffled: meanED P(same) P(ED<=1)")
for name,w in corp.items():
    for gap in (1,2,5):
        a=adjacent_similarity(w,gap); b=shuffled_baseline(w,gap)
        print(f"{name:<10}{gap:>4}{a[0]:>8.2f}{a[1]:>9.3f}{a[2]:>10.3f} | {b[0]:>8.2f}{b[1]:>8.3f}{b[2]:>8.3f}")

# Exact repeats of words within same line (e.g. 'qokeedy qokeedy')
rep=0; tot=0; ex=[]
for ln in L:
    if ln.kind!='P': continue
    ws=ln.words
    for i in range(len(ws)-1):
        tot+=1
        if ws[i]==ws[i+1] and len(ws[i])>2:
            rep+=1
            if len(ex)<12: ex.append((ln.page,ws[i]))
print(f"\nimmediate exact repeats in VMS: {rep}/{tot} = {rep/tot:.4f}; examples {ex}")
for name in ('de_faust','la_caesar','it_dante'):
    w=corp[name]; r=sum(1 for i in range(len(w)-1) if w[i]==w[i+1] and len(w[i])>2)
    print(f"{name}: {r}/{len(w)} = {r/len(w):.4f}")

# Triple repeats
tri=[(ln.page,ws[i]) for ln in L if ln.kind=='P' for ws in [ln.words] for i in range(len(ws)-2) if ws[i]==ws[i+1]==ws[i+2]]
print("triple repeats:",len(tri),tri[:10])
