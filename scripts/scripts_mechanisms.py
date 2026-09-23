import sys, random, re, math
sys.path.insert(0,'.')
from voynich.ivtff import parse
from voynich.battery import battery, header, row
from voynich.stats import clean_gutenberg, tokenize_natural
from collections import Counter, defaultdict
ok=lambda w: w and '?' not in w and '*' not in w
L=parse('data/ZL3b-n.txt',comma_is_space=False)
pages=defaultdict(list); meta={}
for ln in L:
    if ln.kind!='P': continue
    ws=[w for w in ln.words if ok(w)]
    if len(ws)>=2: pages[ln.page].append(ws); meta[ln.page]=(ln.lang,ln.section)
P=list(pages.values()); shape=[[len(l) for l in pg] for pg in P]
results=[battery(P,'VMS')]
# --- G_markov: order-2 glyph model (space as symbol), lines sampled independently with VMS line lengths (in glyphs)
def fit(strings,k):
    m=defaultdict(Counter)
    for s in strings:
        t='^'*k+s+'$'
        for i in range(k,len(t)): m[t[i-k:i]][t[i]]+=1
    return m
def sample_line(m,k,target,rng):
    t='^'*k; s=''
    while True:
        c=m.get(t[-k:]); 
        if not c: break
        syms=list(c); w=[c[x] for x in syms]
        if len(s)<target*0.6 and len(syms)>1: w=[0 if x=='$' else v for x,v in zip(syms,w)]
        x=rng.choices(syms,w)[0]
        if x=='$': break
        s+=x; t+=x
        if len(s)>=target*1.4: break
    return [w for w in s.split(' ') if w]
def markov_pages(order,drift):
    rng=random.Random(order)
    if drift:   # one model per (language, section) group
        groups=defaultdict(list)
        for pg,ls in pages.items(): groups[meta[pg]].extend(' '.join(l) for l in ls)
        models={g:fit(v,order) for g,v in groups.items() if len(v)>=30}
    glob=fit([' '.join(l) for ls in P for l in ls],order)
    out=[]
    for pg,ls in pages.items():
        m=models.get(meta[pg],glob) if drift else glob
        out.append([sample_line(m,order,len(' '.join(l)),rng) for l in ls])
    return [[l for l in pg if len(l)>=2] for pg in out]
results.append(battery(markov_pages(2,False),'markov2'))
results.append(battery(markov_pages(2,True),'markov2+drift'))
results.append(battery(markov_pages(3,True),'markov3+drift'))
# --- Latin chunked into the same shapes (running text) and Latin with rule-inserted spaces
la=tokenize_natural(open('data/ref/la_caesar.txt').read())
def chunk(words):
    out=[]; i=0
    for pg in shape:
        npg=[]
        for k in pg:
            if i+k>len(words): break
            npg.append(words[i:i+k]); i+=k
        if npg: out.append(npg)
    return out
results.append(battery(chunk(la),'latin'))
def rule_spaces(words,after='msty',minlen=3):
    s=''.join(words); out=[]; cur=''
    for ch in s:
        cur+=ch
        if ch in after and len(cur)>=minlen: out.append(cur); cur=''
    if cur: out.append(cur)
    return out
results.append(battery(chunk(rule_spaces(la)),'latin rule-sp'))
print(header())
for r in results: print(row(r))
import json; json.dump(results,open('results/results_mechanisms.json','w'),indent=1)
