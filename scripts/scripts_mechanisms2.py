import sys, random, re, math, json
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
V=[w for pg in P for l in pg for w in l]
results=json.load(open('results/results_mechanisms.json'))

# ---------- markov4 + drift (from scripts_mechanisms) ----------
exec(open('scripts/scripts_mechanisms.py').read().split('results.append(battery(markov_pages(2,False)')[0].split("results=[battery(P,'VMS')]")[1])
results.append(battery(markov_pages(4,True),'markov4+drift'))

# ---------- Rugg: table and grille ----------
SLOT=re.compile(r'^(q?(?:o|y|d|s|ch|sh)?(?:k|t|p|f|ck|ct|cp|cf|ch|sh|ckh|cth|cph|cfh|l|r|d|s)?)(e{0,3}(?:o|a|y)?)((?:i{0,3}(?:n|r|l|m)|d|l|r|s|y|dy|ly|ry|dl|ol|al|or|ar|am|an)?y?)$')
pre=Counter(); mid=Counter(); suf=Counter()
for w in V:
    m=SLOT.match(w)
    if m and any(m.groups()): pre[m.group(1)]+=1; mid[m.group(2)]+=1; suf[m.group(3)]+=1
    else:
        k=len(w)//3; pre[w[:k]]+=1; mid[w[k:2*k]]+=1; suf[w[2*k:]]+=1
def draw(c,rng): syms=list(c); return rng.choices(syms,[c[s] for s in syms])[0]
def rugg_pages(cells_per_token=0.9,seed=0):
    rng=random.Random(seed); groups=defaultdict(list)
    for pg,ls in pages.items(): groups[meta[pg]].append(pg)
    out=[]
    for g,pgs in groups.items():
        ntok=sum(len(l) for pg in pgs for l in pages[pg]); C=40; R=max(2,int(ntok*cells_per_token/C))
        table=[[draw(pre,rng)+draw(mid,rng)+draw(suf,rng) or 'o' for _ in range(C)] for _ in range(R)]
        for pg in pgs:
            r=rng.randrange(R); c=rng.randrange(C); npg=[]
            for l in pages[pg]:
                npg.append([table[r%R][(c+j)%C] for j in range(len(l))]); r+=1     # grille moves one row down per line
            out.append(npg)
    return out
results.append(battery(rugg_pages(),'rugg grille'))

# ---------- Timm & Schinner: copy and modify ----------
SIM=[('ch','sh'),('k','t'),('t','p'),('k','f'),('e','ee'),('ee','eee'),('i','ii'),('ii','iii'),('a','o'),('y','dy'),('r','l'),('n','m'),('ol','or'),('ar','al'),('ain','aiin'),('ey','edy')]
PREF=['q','o','d','s','y','l','ch','sh']; SUFF=['y','dy','n','in','iin','r','l','s','m']
def modify(w,rng):
    op=rng.random()
    if op<0.5:
        a,b=rng.choice(SIM)
        if rng.random()<0.5: a,b=b,a
        if a in w: return w.replace(a,b,1)
    if op<0.7:
        p=rng.choice(PREF)
        return w[len(p):] if w.startswith(p) and len(w)>len(p)+1 else p+w
    if op<0.9:
        s=rng.choice(SUFF)
        return w[:-len(s)] if w.endswith(s) and len(w)>len(s)+1 else w+s
    return w
def ts_pages(seed=0,p_exact=0.15,p_two=0.25):
    rng=random.Random(seed); out=[]
    seeds=[w for w,_ in Counter(V).most_common(300)]
    for pg,ls in pages.items():
        npg=[]
        for li,l in enumerate(ls):
            line=[]
            for j in range(len(l)):
                # source: line above (same column +-1) with p=.6, previous word in line .2, random word on page .2, else seed
                src=None; r=rng.random()
                if li>0 and r<0.6:
                    above=npg[li-1]; jj=min(len(above)-1,max(0,j+rng.randint(-1,1))); src=above[jj]
                elif line and r<0.8: src=line[-1]
                elif npg and r<0.95: src=rng.choice(rng.choice(npg))
                if src is None: src=rng.choice(seeds)
                w=src; u=rng.random()
                if u>p_exact:
                    w=modify(w,rng)
                    if u>1-p_two: w=modify(w,rng)
                line.append(w or 'o')
            npg.append(line)
        out.append(npg)
    return out
results.append(battery(ts_pages(),'timm-schinner'))

# ---------- Verbose cipher of Latin, rule-inserted spaces, independent lines ----------
UNITS=['ch','sh','k','t','p','f','ck','ct','cth','ckh','d','s','l','r','o','a','y','e','ee','i','ii','n','m','q','qo','ai','oi','ol','or','al','ar','dy','ey','ain','aiin']
def make_cipher(seed):
    rng=random.Random(seed); letters='abcdefghilmnopqrstuvxyz'
    table={}
    for x in letters:
        k=rng.choice([1,2,2,3]); table[x]=rng.sample(UNITS,k)
    return table
def encipher(text_words,table):
    out=[]; prev='#'
    for w in text_words:
        for ch in w:
            if ch not in table: continue
            homs=table[ch]; u=homs[hash(prev)%len(homs)] if len(homs)>1 else homs[0]   # homophone chosen by previous glyph -> rigid transitions
            out.append(u); prev=u[-1]
    return ''.join(out)
def rule_space(stream,after='ynrlms',minlen=3,maxlen=9):
    out=[]; cur=''
    for ch in stream:
        cur+=ch
        if (ch in after and len(cur)>=minlen) or len(cur)>=maxlen: out.append(cur); cur=''
    if cur: out.append(cur)
    return out
raw=open('data/ref/la_caesar.txt').read().lower()
sents=[tokenize_natural(s) for s in re.split(r'[.;:?!]',raw)]; sents=[s for s in sents if len(s)>=6]
def verbose_pages(seed=0,independent_lines=True):
    rng=random.Random(seed); table=make_cipher(seed); out=[]; si=0; stream_words=[w for s in sents for w in s]; wi=0
    for pg in shape:
        npg=[]
        for k in pg:
            if independent_lines:
                s=sents[si%len(sents)]; si+=1; plain=s[:max(3,k//2+2)]
            else:
                plain=stream_words[wi:wi+max(3,k//2+2)]; wi+=len(plain)
            glyphs=encipher(plain,table); npg.append(rule_space(glyphs))
        out.append(npg)
    return out
results.append(battery(verbose_pages(0,True),'verbose+indep'))
results.append(battery(verbose_pages(0,False),'verbose+running'))
print(header())
for r in results: print(row(r))
json.dump(results,open('results/results_mechanisms.json','w'),indent=1)
print("\nsamples:")
print(" rugg:",' '.join(rugg_pages()[3][1][:10])); print(" T&S :",' '.join(ts_pages()[3][2][:10])); print(" verb:",' '.join(verbose_pages()[3][1][:10]))
