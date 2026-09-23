"""Do zodiac (and other) labels recur across pages more than automaton output would?"""
import sys, random
sys.path.insert(0,'.')
from voynich.ivtff import parse
from collections import Counter, defaultdict
ok=lambda w: w and '?' not in w and '*' not in w
L=parse('data/ZL3b-n.txt',comma_is_space=False)
labels=defaultdict(list)
for ln in L:
    if ln.kind!='L': continue
    for w in ln.words:
        if ok(w): labels[ln.page].append((ln.section,w))
def recurrence(pages_words):
    """share of tokens whose type occurs on at least one OTHER page of the set"""
    bypage={p:set(w for w in ws) for p,ws in pages_words.items()}
    tot=0; rec=0
    for p,ws in pages_words.items():
        others=set().union(*(bypage[q] for q in bypage if q!=p)) if len(bypage)>1 else set()
        for w in ws: tot+=1; rec+= w in others
    return rec/max(tot,1), tot, len({w for ws in pages_words.values() for w in ws})
for sec,name in [('Z','zodiac'),('A','astro'),('P','pharma'),('B','biological'),('C','cosmo'),('H','herbal')]:
    pw={p:[w for s,w in v if s==sec] for p,v in labels.items()}; pw={p:v for p,v in pw.items() if v}
    if len(pw)<2: continue
    r,tot,types=recurrence(pw)
    # null: text words from the same pages (paragraph text), same number per page, random sample
    rng=random.Random(0); textw=defaultdict(list)
    for ln in L:
        if ln.kind=='P' and ln.page in pw: textw[ln.page]+= [w for w in ln.words if ok(w)]
    # if pages have little text, take text from any page of the same section
    pool=[w for ln in L if ln.kind=='P' and ln.section==sec for w in ln.words if ok(w)]
    allpool=[w for ln in L if ln.kind=='P' for w in ln.words if ok(w)]
    nulls=[]
    for rep in range(20):
        sim={}
        for p,v in pw.items():
            src=textw[p] if len(textw[p])>=len(v) else (pool if len(pool)>=len(v)*3 else allpool)
            sim[p]=rng.sample(src,len(v))
        nulls.append(recurrence(sim)[0])
    print(f"{name:<11} pages={len(pw):>3} label tokens={tot:>4} types={types:>4}  recurrence across pages: {r:.3f}   null (text words of same pages/section): {sum(nulls)/len(nulls):.3f}")
# zodiac detail: which labels recur across signs
pw={p:[w for s,w in v if s=='Z'] for p,v in labels.items()}; pw={p:v for p,v in pw.items() if v}
c=Counter(w for v in pw.values() for w in set(v))
print("\nzodiac labels on >=2 sign pages:",[(w,n) for w,n in c.most_common() if n>=2][:25])
print("zodiac pages:",sorted(pw))
