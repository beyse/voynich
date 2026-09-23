"""A common test battery for the Voynich text and for candidate generating mechanisms.
Input: pages = list of pages, each a list of lines, each a list of word strings (glyph strings)."""
import math, random, re, lzma
from collections import Counter, defaultdict

def _mi(pairs):
    pa=Counter(a for a,b in pairs); pb=Counter(b for a,b in pairs); pab=Counter(pairs); n=len(pairs)
    return sum(c/n*math.log2((c/n)/((pa[a]/n)*(pb[b]/n))) for (a,b),c in pab.items())
def _excess_b(pairs,reps=5):
    if len(pairs)<50: return float('nan')
    obs=_mi(pairs); base=0
    for r in range(reps):
        bs=[b for a,b in pairs]; random.Random(r).shuffle(bs); base+=_mi(list(zip([a for a,b in pairs],bs)))/reps
    return obs-base
def _excess_line(inner,f,reps=5):
    adj=lambda segs:[f(s[i],s[i+1]) for s in segs for i in range(len(s)-1)]
    obs=_mi(adj(inner)); base=0
    for r in range(reps):
        rng=random.Random(r); base+=_mi(adj([rng.sample(s,len(s)) for s in inner]))/reps
    return obs-base
def _cond_entropy(strings,k):
    ctx=Counter(); joint=Counter()
    for s in strings:
        t='^'*k+s+'$'
        for i in range(k,len(t)): joint[t[i-k:i+1]]+=1; ctx[t[i-k:i]]+=1
    n=sum(joint.values()); return -sum(c/n*math.log2(c/ctx[j[:-1]]) for j,c in joint.items())
def _space_gain(lines,k=1):
    rng=random.Random(0); ls=list(lines); rng.shuffle(ls); half=len(ls)//2
    def positions(line):
        s='#'*k+''.join(line)+'#'*k; b=set(); pos=k
        for w in line[:-1]: pos+=len(w); b.add(pos)
        for i in range(k+1,len(s)-k): yield (s[i-k:i],s[i:i+k]),(i in b)
    c=defaultdict(Counter)
    for l in ls[:half]:
        for ctx,b in positions(l): c[ctx][b]+=1
    tot=sum(sum(v.values()) for v in c.values()); prior=sum(v[True] for v in c.values())/tot
    H=0;n=0
    for l in ls[half:]:
        for ctx,b in positions(l):
            cc=c.get(ctx,Counter()); p=(cc[True]+prior)/(sum(cc.values())+1.0); H+=-math.log2(p if b else 1-p); n+=1
    H0=-(prior*math.log2(prior)+(1-prior)*math.log2(1-prior)); return 1-H/n/H0
def _lexicon(words,k=2):
    S,E='^','$'; rng=random.Random(0); w=list(words); rng.shuffle(w); half=len(w)//2; train,test=w[:half],w[half:]
    m=defaultdict(Counter)
    for x in train:
        t=S*k+x+E
        for i in range(k,len(t)): m[t[i-k:i]][t[i]]+=1
    def sample():
        t=S*k; s=''
        while len(s)<15:
            c=m.get(t[-k:])
            if not c: break
            syms=list(c); x=rng.choices(syms,[c[y] for y in syms])[0]
            if x==E: break
            s+=x; t+=x
        return s
    synth=[s for s in (sample() for _ in range(len(test))) if s]; trainset=set(train)
    return sum(x in trainset for x in test)/len(test), sum(x in trainset for x in synth)/len(synth)
def _zipf(words,top=200):
    c=Counter(words); f=sorted(c.values(),reverse=True)[:top]; xs=[math.log(i+1) for i in range(len(f))]; ys=[math.log(v) for v in f]
    n=len(xs); mx=sum(xs)/n; my=sum(ys)/n; return sum((x-mx)*(y-my) for x,y in zip(xs,ys))/sum((x-mx)**2 for x in xs)

def battery(pages, label):
    lines=[l for pg in pages for l in pg if len(l)>=2]
    words=[w for l in lines for w in l]
    inner=[l[1:-1] for l in lines if len(l)>=5]
    r={'label':label,'tokens':len(words),'types':len(set(words))}
    c=Counter(words); r['hapax']=sum(1 for v in c.values() if v==1)/len(c); r['ttr']=len(c)/len(words); r['zipf']=_zipf(words); r['wlen']=sum(map(len,words))/len(words)
    r['edge_mi']=_excess_line(inner,lambda a,b:(a[-1],b[0]))
    r['token_mi']=_excess_line(inner,lambda a,b:(a,b))
    r['d2_mi']=_excess_b([(s[i],s[i+2]) for s in inner for i in range(len(s)-2)])
    # line break: (last_k, first_k+1) within page vs adjacent inner pairs subsampled to same n
    brk=[(pg[k][-1],pg[k+1][0]) for pg in pages for k in range(len(pg)-1) if len(pg[k])>=2 and len(pg[k+1])>=2]
    adjp=[(s[i],s[i+1]) for s in inner for i in range(len(s)-1)]; rng=random.Random(1)
    n=min(len(brk),len(adjp)); r['break_mi']=_excess_b(rng.sample(brk,n)); r['adj_mi_same_n']=sum(_excess_b(rng.sample(adjp,n)) for _ in range(3))/3
    r['break_edge']=_excess_b([(a[-1],b[0]) for a,b in brk]); r['adj_edge_same_n']=_excess_b([(a[-1],b[0]) for a,b in rng.sample(adjp,n)])
    r['space_gain']=_space_gain(lines,1)
    r['lex_real'],r['lex_synth']=_lexicon(words,2)
    strings=[' '.join(l) for l in lines]; r['h2']=_cond_entropy(strings,2); r['h3']=_cond_entropy(strings,3); r['h4']=_cond_entropy(strings,4)
    r['lzma']=len(lzma.compress('\n'.join(strings).encode(),preset=9))*8/sum(map(len,strings))
    pp=[(i,w) for i,pg in enumerate(pages) for l in pg for w in l]; r['page_mi']=_excess_b(rng.sample(pp,min(len(pp),20000)))
    # positional: share of line-final words ending in the two most line-final-specific glyphs is data-specific; instead report H(first glyph | line-initial) vs mid
    return r

COLS=[('tokens','{:>7d}'),('types','{:>6d}'),('hapax','{:>6.2f}'),('zipf','{:>6.2f}'),('wlen','{:>5.2f}'),('edge_mi','{:>7.3f}'),('token_mi','{:>8.3f}'),('d2_mi','{:>6.3f}'),
      ('break_mi','{:>8.3f}'),('adj_mi_same_n','{:>8.3f}'),('break_edge','{:>8.3f}'),('adj_edge_same_n','{:>8.3f}'),('space_gain','{:>6.1%}'),('lex_real','{:>6.2f}'),('lex_synth','{:>6.2f}'),('h2','{:>5.2f}'),('h3','{:>5.2f}'),('h4','{:>5.2f}'),('lzma','{:>5.2f}'),('page_mi','{:>7.3f}')]
def header():
    return f"{'mechanism':<18}"+"".join(f"{k:>{len(f.format(0) if 'd' in f or '%' not in f else '000000')}}" if False else f" {k[:8]:>8}" for k,f in COLS)
def row(r):
    return f"{r['label']:<18}"+"".join(f" {f.format(r[k]).strip():>8}" for k,f in COLS)

# ---- redundancy beyond a drifting order-3 automaton: lzma(real) - lzma(twin fitted per group on the mechanism's own output)
def twin_residual(pages, groups, order=3, seed=0):
    rng=random.Random(seed); strings_by_group=defaultdict(list)
    for pg,g in zip(pages,groups):
        for l in pg:
            if len(l)>=2: strings_by_group[g].append(' '.join(l))
    def fit(strings,k):
        m=defaultdict(Counter)
        for s in strings:
            t='^'*k+s+'$'
            for i in range(k,len(t)): m[t[i-k:i]][t[i]]+=1
        return m
    allstr=[s for v in strings_by_group.values() for s in v]; glob=fit(allstr,order)
    models={g:fit(v,order) for g,v in strings_by_group.items() if len(v)>=30}
    real=[]; twin=[]
    for pg,g in zip(pages,groups):
        m=models.get(g,glob)
        for l in pg:
            if len(l)<2: continue
            s=' '.join(l); real.append(s); t='^'*order; out=''
            while True:
                c=m.get(t[-order:])
                if not c: break
                syms=list(c); w=[c[x] for x in syms]
                if len(out)<len(s)*0.6 and len(syms)>1: w=[0 if x=='$' else v for x,v in zip(syms,w)]
                x=rng.choices(syms,w)[0]
                if x=='$' or len(out)>=len(s)*1.4: break
                out+=x; t+=x
            twin.append(out)
    lz=lambda ss: len(lzma.compress('\n'.join(ss).encode(),preset=9))*8/sum(map(len,ss))
    return lz(real)-lz(twin), _cond_entropy(real,3)-_cond_entropy(twin,3)
