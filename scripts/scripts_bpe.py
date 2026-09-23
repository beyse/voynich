"""Unit-inventory inference: apply identical BPE merges to Voynichese and to natural languages and
track (units in use, h1, h2, h2/h1, units/word). If Voynichese were a verbose cipher, its curve should
reach natural-language h2/h1 (~0.8) at some inventory size ~20-40."""
import sys, re, math
sys.path.insert(0,'.')
from voynich.ivtff import parse, words_of
from voynich.stats import clean_gutenberg, tokenize_natural, char_entropies
from collections import Counter

def bpe_curve(words, merges=80, report=(0,5,10,15,20,25,30,40,50,60,80)):
    seqs=Counter(tuple(w) for w in words)   # word type -> count, as tuples of units
    res=[]; merged=[]
    for step in range(merges+1):
        if step in report:
            flat=[]; 
            for w,c in seqs.items(): flat.extend([w]*c)
            # entropies over unit stream with spaces; represent units as ids
            units={u for w in seqs for u in w}; uid={u:chr(0xE000+i) for i,u in enumerate(sorted(units))}
            ws=[''.join(uid[u] for u in w) for w in flat]
            h0,h1,h2,a=char_entropies(ws)
            res.append((step,a,h1,h2,h2/h1,sum(len(w) for w in ws)/len(ws)))
        pairs=Counter()
        for w,c in seqs.items():
            for i in range(len(w)-1): pairs[(w[i],w[i+1])]+=c
        if not pairs: break
        (a,b),_=pairs.most_common(1)[0]; merged.append(a+b)
        new=Counter()
        for w,c in seqs.items():
            out=[]; i=0
            while i<len(w):
                if i<len(w)-1 and w[i]==a and w[i+1]==b: out.append(a+b); i+=2
                else: out.append(w[i]); i+=1
            new[tuple(out)]+=c
        seqs=new
    return res, merged

L=parse('data/ZL3b-n.txt')
corp={'VMS':words_of(L,kind='P')}
for name,path in [('de','data/ref/de_faust.txt'),('it','data/ref/it_dante.txt'),('la','data/ref/la_caesar.txt')]:
    t=clean_gutenberg(path) if name!='la' else open(path).read()
    corp[name]=tokenize_natural(t)[:35000]
corp['he']=re.findall(r'[א-ת]+',open('data/ref/he_genesis.txt',encoding='utf-8').read())
for name,w in corp.items():
    res,merged=bpe_curve(w)
    print(f"\n== {name}  (first merges: {' '.join(merged[:25])})")
    print(f"{'merges':>6}{'units':>6}{'h1':>7}{'h2':>7}{'h2/h1':>7}{'u/word':>8}")
    for r in res: print(f"{r[0]:>6}{r[1]:>6}{r[2]:>7.2f}{r[3]:>7.2f}{r[4]:>7.2f}{r[5]:>8.2f}")
