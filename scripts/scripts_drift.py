"""Page locality: smooth drift with folio distance (habit) or page-specific offsets (topic)?
Jensen-Shannon divergence of glyph-bigram distributions between pages vs folio distance, within Currier language."""
import sys, re, math, random
sys.path.insert(0,'.')
from voynich.generators import pages, meta, P, markov_pages, chunk, la
from collections import Counter, defaultdict
def folio_num(p):
    m=re.match(r'f(\d+)([rv])',p); return int(m.group(1))*2+(m.group(2)=='v') if m else None
def bigrams(lines, n=450, rng=None):
    s=' '.join(' '.join(l) for l in lines)
    if rng and len(s)>n:
        st=rng.randrange(0,len(s)-n); s=s[st:st+n]
    c=Counter(zip(s,s[1:])); return c
def jsd(c1,c2,alpha=0.05):
    keys=set(c1)|set(c2); n1=sum(c1.values())+alpha*len(keys); n2=sum(c2.values())+alpha*len(keys)
    p=[(c1[k]+alpha)/n1 for k in keys]; q=[(c2[k]+alpha)/n2 for k in keys]
    m=[(a+b)/2 for a,b in zip(p,q)]
    return 0.5*sum(a*math.log2(a/mm) for a,mm in zip(p,m))+0.5*sum(b*math.log2(b/mm) for b,mm in zip(q,m))
def run(pagedict, label, glyphs_min=450):
    rng=random.Random(0)
    items=[(folio_num(pg),meta[pg],ls) for pg,ls in pagedict.items() if folio_num(pg) and len(' '.join(' '.join(l) for l in ls))>=glyphs_min]
    for lang in 'AB':
        it=[(f,m,ls) for f,m,ls in items if m[0]==lang]; it.sort()
        bins={'same page (halves)':[], 'd=1-2':[], 'd=3-6':[], 'd=7-14':[], 'd=15-40':[], 'd>40':[], 'other section':[]}
        for i,(f,m,ls) in enumerate(it):
            h=len(ls)//2
            if h>=2 and len(' '.join(' '.join(l) for l in ls[:h]))>=250: bins['same page (halves)'].append(jsd(bigrams(ls[:h],250,rng),bigrams(ls[h:],250,rng)))
            for j in range(i+1,len(it)):
                f2,m2,ls2=it[j]; d=f2-f
                b1=bigrams(ls,450,rng); b2=bigrams(ls2,450,rng); v=jsd(b1,b2)
                if m2[1]!=m[1]: bins['other section'].append(v); continue
                k='d=1-2' if d<=2 else 'd=3-6' if d<=6 else 'd=7-14' if d<=14 else 'd=15-40' if d<=40 else 'd>40'
                bins[k].append(v)
        print(f"{label:<16} lang {lang} ({len(it)} pages): "+"  ".join(f"{k}: {sum(v)/len(v):.4f} (n={len(v)})" for k,v in bins.items() if v))
run(pages,'VMS')
mk=markov_pages(3,True); run(dict(zip(pages.keys(),mk)),'markov3+drift')
mk=markov_pages(4,True); run(dict(zip(pages.keys(),mk)),'markov4+drift')
lc=chunk(la); run(dict(zip(list(pages.keys())[:len(lc)],lc)),'latin (chunk)')
