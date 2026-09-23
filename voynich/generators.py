"""Candidate generating mechanisms, all producing pages in the exact line/word shape of the VMS paragraph text."""
import random, re
from collections import Counter, defaultdict
from voynich.ivtff import parse
from voynich.stats import tokenize_natural

ok=lambda w: w and '?' not in w and '*' not in w
L=parse('data/ZL3b-n.txt',comma_is_space=False)
pages=defaultdict(list); meta={}
for ln in L:
    if ln.kind!='P': continue
    ws=[w for w in ln.words if ok(w)]
    if len(ws)>=2: pages[ln.page].append(ws); meta[ln.page]=(ln.lang,ln.section)
P=list(pages.values()); shape=[[len(l) for l in pg] for pg in P]; groups=[meta[pg] for pg in pages]
V=[w for pg in P for l in pg for w in l]
la=tokenize_natural(open('data/ref/la_caesar.txt').read())
raw=open('data/ref/la_caesar.txt').read().lower()
sents=[tokenize_natural(s) for s in re.split(r'[.;:?!]',raw)]; sents=[s for s in sents if len(s)>=6]

def chunk(words):
    out=[]; i=0
    for pg in shape:
        npg=[]
        for k in pg:
            if i+k>len(words): break
            npg.append(words[i:i+k]); i+=k
        if npg: out.append(npg)
    return out
def rule_spaces(words,after='msty',minlen=3):
    s=''.join(words); out=[]; cur=''
    for ch in s:
        cur+=ch
        if ch in after and len(cur)>=minlen: out.append(cur); cur=''
    if cur: out.append(cur)
    return out

# ---- glyph Markov automaton, restarted per line, space as symbol
def fit(strings,k):
    m=defaultdict(Counter)
    for s in strings:
        t='^'*k+s+'$'
        for i in range(k,len(t)): m[t[i-k:i]][t[i]]+=1
    return m
def sample_line(m,k,target,rng):
    t='^'*k; s=''
    while True:
        c=m.get(t[-k:])
        if not c: break
        syms=list(c); w=[c[x] for x in syms]
        if len(s)<target*0.6 and len(syms)>1: w=[0 if x=='$' else v for x,v in zip(syms,w)]
        x=rng.choices(syms,w)[0]
        if x=='$': break
        s+=x; t+=x
        if len(s)>=target*1.4: break
    return [w for w in s.split(' ') if w]
def markov_pages(order,drift,seed=None):
    rng=random.Random(order if seed is None else seed)
    models={}
    if drift:
        gs=defaultdict(list)
        for pg,ls in pages.items(): gs[meta[pg]].extend(' '.join(l) for l in ls)
        models={g:fit(v,order) for g,v in gs.items() if len(v)>=30}
    glob=fit([' '.join(l) for ls in P for l in ls],order)
    out=[]
    for pg,ls in pages.items():
        m=models.get(meta[pg],glob) if drift else glob
        out.append([l for l in (sample_line(m,order,len(' '.join(x)),rng) for x in ls) if len(l)>=2])
    return out

# ---- Rugg table & grille
SLOT=re.compile(r'^(q?(?:o|y|d|s|ch|sh)?(?:k|t|p|f|ck|ct|cp|cf|ch|sh|ckh|cth|cph|cfh|l|r|d|s)?)(e{0,3}(?:o|a|y)?)((?:i{0,3}(?:n|r|l|m)|d|l|r|s|y|dy|ly|ry|dl|ol|al|or|ar|am|an)?y?)$')
pre=Counter(); mid=Counter(); suf=Counter()
for w in V:
    m=SLOT.match(w)
    if m and any(m.groups()): pre[m.group(1)]+=1; mid[m.group(2)]+=1; suf[m.group(3)]+=1
    else:
        k=len(w)//3; pre[w[:k]]+=1; mid[w[k:2*k]]+=1; suf[w[2*k:]]+=1
def draw(c,rng): syms=list(c); return rng.choices(syms,[c[s] for s in syms])[0]
def rugg_pages(cells_per_token=0.9,seed=0,cols=40):
    rng=random.Random(seed); gs=defaultdict(list)
    for pg in pages: gs[meta[pg]].append(pg)
    out={}
    for g,pgs in gs.items():
        ntok=sum(len(l) for pg in pgs for l in pages[pg]); C=cols; R=max(2,int(ntok*cells_per_token/C))
        table=[[draw(pre,rng)+draw(mid,rng)+draw(suf,rng) or 'o' for _ in range(C)] for _ in range(R)]
        for pg in pgs:
            r=rng.randrange(R); c=rng.randrange(C); npg=[]
            for l in pages[pg]:
                npg.append([table[r%R][(c+j)%C] for j in range(len(l))]); r+=1
            out[pg]=npg
    return [out[pg] for pg in pages]

# ---- Timm & Schinner style copy-and-modify (length-stable)
SIM=[('ch','sh'),('k','t'),('t','p'),('k','f'),('e','ee'),('ee','eee'),('i','ii'),('ii','iii'),('a','o'),('y','dy'),('r','l'),('n','m'),('ol','or'),('ar','al'),('ain','aiin'),('ey','edy')]
PREF=['q','o','d','s','y','l','ch','sh']; SUFF=['y','dy','n','in','iin','r','l','s','m']
def modify(w,rng):
    op=rng.random()
    if op<0.5:
        a,b=rng.choice(SIM)
        if rng.random()<0.5: a,b=b,a
        if a in w: return w.replace(a,b,1)
    grow=rng.random()<max(0.05,min(0.95,(6-len(w))/4+0.5))
    if op<0.75:
        if grow: return rng.choice(PREF)+w
        for p in PREF:
            if w.startswith(p) and len(w)>len(p)+1: return w[len(p):]
        return w
    if grow: return w+rng.choice(SUFF)
    for s in sorted(SUFF,key=len,reverse=True):
        if w.endswith(s) and len(w)>len(s)+1: return w[:-len(s)]
    return w
def ts_pages(seed=0,p_exact=0.15,p_two=0.25):
    rng=random.Random(seed); out=[]; seeds=[w for w,_ in Counter(V).most_common(300)]
    for pg,ls in pages.items():
        npg=[]
        for li,l in enumerate(ls):
            line=[]
            for j in range(len(l)):
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

# ---- verbose cipher of Latin (homophone chosen by previous glyph), rule-inserted spaces
UNITS=['ch','sh','k','t','p','f','ck','ct','cth','ckh','d','s','l','r','o','a','y','e','ee','i','ii','n','m','q','qo','ai','oi','ol','or','al','ar','dy','ey','ain','aiin']
LETTERS='abcdefghilmnopqrstuvxyz'
def make_cipher(seed):
    rng=random.Random(seed); return {x:rng.sample(UNITS,rng.choice([1,2,2,3])) for x in LETTERS}
def encipher(text_words,table):
    out=[]; prev='#'
    for w in text_words:
        for ch in w:
            if ch not in table: continue
            homs=table[ch]; u=homs[ord(prev)%len(homs)]; out.append(u); prev=u[-1]
    return ''.join(out)
def rule_space(stream,after='ynrlms',minlen=3,maxlen=9):
    out=[]; cur=''
    for ch in stream:
        cur+=ch
        if (ch in after and len(cur)>=minlen) or len(cur)>=maxlen: out.append(cur); cur=''
    if cur: out.append(cur)
    return out
def verbose_pages(seed=0,independent_lines=True):
    table=make_cipher(seed); out=[]; si=0; stream_words=[w for s in sents for w in s]; wi=0
    for pg in shape:
        npg=[]
        for k in pg:
            if independent_lines: s=sents[si%len(sents)]; si+=1; plain=s[:max(3,k//2+2)]
            else: plain=stream_words[wi:wi+max(3,k//2+2)]; wi+=len(plain)
            npg.append(rule_space(encipher(plain,table)))
        out.append(npg)
    return out

# ---- autokey (ciphertext-feedback) substitution: c_i = T[c_{i-1}][p_i]
GL='abcdefghijklmnopqrstuvwxyz*'; END=set('ynrlm')
def autokey_pages(seed=0,glyphs_per_letter=1,minl=3,maxl=9):
    rng=random.Random(seed)
    T=[{p:g for p,g in zip(LETTERS,rng.sample(GL,len(LETTERS)))} for _ in range(len(GL))]
    T2=[{p:g for p,g in zip(LETTERS,rng.sample(GL,len(LETTERS)))} for _ in range(len(GL))]
    out=[]; si=0
    for pg in shape:
        npg=[]
        for k in pg:
            s=sents[si%len(sents)]; si+=1; plain=''.join(s)[:max(8,int(k*5.3/glyphs_per_letter))]
            prev=rng.randrange(len(GL)); stream=''
            for ch in plain:
                if ch not in LETTERS: continue
                g=T[prev][ch]; stream+=g; prev=GL.index(g)
                if glyphs_per_letter==2: g=T2[prev][ch]; stream+=g; prev=GL.index(g)
            words=[]; cur=''
            for g in stream:
                cur+=g
                if (g in END and len(cur)>=minl) or len(cur)>=maxl: words.append(cur); cur=''
            if cur: words.append(cur)
            npg.append(words)
        out.append(npg)
    return out

# ---- hierarchical automaton: per-page counts interpolated with section counts (page-level drift)
def markov_pages_hier(order, lam, seed=0):
    rng=random.Random(seed)
    gs=defaultdict(list)
    for pg,ls in pages.items(): gs[meta[pg]].extend(' '.join(l) for l in ls)
    sec={g:fit(v,order) for g,v in gs.items() if len(v)>=30}
    glob=fit([' '.join(l) for ls in P for l in ls],order)
    out=[]
    for pg,ls in pages.items():
        pm=fit([' '.join(l) for l in ls],order); sm=sec.get(meta[pg],glob)
        class Mix(dict):
            def get(self,ctx,default=None):
                a=pm.get(ctx); b=sm.get(ctx)
                if not a and not b: return None
                syms=set(a or {})|set(b or {}); na=sum((a or {}).values()) or 1; nb=sum((b or {}).values()) or 1
                return Counter({x:(lam*(a[x]/na if a else 0)+(1-lam)*(b[x]/nb if b else 0))*1000 for x in syms})
        m=Mix()
        out.append([l for l in (sample_line(m,order,len(' '.join(x)),rng) for x in ls) if len(l)>=2])
    return out

# ---- Naibbe cipher (Greshko, Cryptologia 2025): reimplemented from the published tables and the repo's documented procedure.
# Plaintext: lowercase, w->uu, j->i, k->c, letters only, spaces removed. Tokens of 1 or 2 letters (P(unigram)=17/36).
# Table per letter chosen by drawing from a shuffled 52-card deck (alpha 20, beta1-3 8 each, gamma1-2 4 each; redeal when empty).
# Unigram token -> unigram glyph string; bigram token -> prefix(p)+suffix(s). Optionally 3% of ciphertext spaces removed.
import csv as _csv
NAIBBE={}
with open('data/naibbe/naibbe_tables.csv') as _fh:
    for row in _csv.DictReader(_fh): NAIBBE[row['code']]=row['glyphs']
NAIBBE_TABLES=['alpha','beta1','beta2','beta3','gamma1','gamma2']; NAIBBE_WEIGHTS={'alpha':20,'beta1':8,'beta2':8,'beta3':8,'gamma1':4,'gamma2':4}
def naibbe_clean(text):
    t=text.lower().replace('w','uu').replace('j','i').replace('k','c'); return re.sub(r'[^a-ilmnop-vxyz]','',t)
class _Deck:
    def __init__(self,rng): self.rng=rng; self.cards=[]
    def draw(self):
        if not self.cards:
            self.cards=[t for t,n in NAIBBE_WEIGHTS.items() for _ in range(n)]; self.rng.shuffle(self.cards)
        return self.cards.pop()
def naibbe_encipher(letters,rng,deck,card_per='letter',p_uni=17/36):
    out=[]; i=0
    while i<len(letters):
        if i==len(letters)-1 or rng.random()<p_uni:
            out.append(NAIBBE['unigram_%s_%s'%(deck.draw(),letters[i])]); i+=1
        else:
            t1=deck.draw(); t2=t1 if card_per=='token' else deck.draw()
            out.append(NAIBBE['prefix_%s_%s'%(t1,letters[i])]+NAIBBE['suffix_%s_%s'%(t2,letters[i+1])]); i+=2
    return out
def naibbe_pages(seed=0,independent_lines=True,card_per='letter',space_removal=0.03,text=None):
    rng=random.Random(seed); deck=_Deck(rng); out=[]; si=0
    stream=naibbe_clean(' '.join(la)) if text is None else naibbe_clean(text); pos=0
    for pg in shape:
        npg=[]
        for k in pg:
            words=[]
            if independent_lines:
                s=naibbe_clean(' '.join(sents[si%len(sents)])); si+=1; src=s; p=0
                while len(words)<k and p<len(src):
                    seg=naibbe_encipher(src[p:p+2],rng,deck,card_per); words+=seg; p+=2 if len(seg)==1 and len(src[p:p+2])==2 and False else 0
                    # simpler: encipher whole sentence then cut
                    break
                words=naibbe_encipher(src,rng,deck,card_per)[:k]
            else:
                need=k; letters=stream[pos:pos+2*need]; words=naibbe_encipher(letters,rng,deck,card_per)[:k]
                # advance by the number of plaintext letters consumed (approx: count letters of words) -> recompute exactly
                consumed=0; tmp=[]; j=0
                # re-derive consumption: encipher progressively
                rng2=random.Random(rng.random()); deck2=_Deck(rng2); words=[]; j=0
                while len(words)<k and pos+j<len(stream):
                    if pos+j==len(stream)-1 or rng2.random()<17/36:
                        words.append(NAIBBE['unigram_%s_%s'%(deck2.draw(),stream[pos+j])]); j+=1
                    else:
                        t1=deck2.draw(); t2=t1 if card_per=='token' else deck2.draw()
                        words.append(NAIBBE['prefix_%s_%s'%(t1,stream[pos+j])]+NAIBBE['suffix_%s_%s'%(t2,stream[pos+j+1])]); j+=2
                pos+=j
            if space_removal>0 and len(words)>2:
                merged=[words[0]]
                for w in words[1:]:
                    if rng.random()<space_removal: merged[-1]+=w
                    else: merged.append(w)
                words=merged
            if len(words)>=2: npg.append(words)
        out.append(npg)
    return out

# ---- stateful Naibbe: table choice depends on the previous ciphertext word's last glyph (random peaked 27x6 matrix) with mixing weight w
def naibbe_stateful_pages(seed=0,w=0.9,concentration=0.15,card_per='letter',space_removal=0.03):
    rng=random.Random(seed); deck=_Deck(rng); out=[]; si=0
    glyphs=sorted({g for s in NAIBBE.values() for g in s})
    def dirichlet(k):
        xs=[rng.gammavariate(concentration,1) for _ in range(k)]; s=sum(xs); return [x/s for x in xs]
    state_tab={g:dirichlet(len(NAIBBE_TABLES)) for g in glyphs}
    def draw(prev):
        if prev is None or rng.random()>w: return deck.draw()
        return rng.choices(NAIBBE_TABLES,state_tab[prev])[0]
    for pg in shape:
        npg=[]
        for k in pg:
            src=naibbe_clean(' '.join(sents[si%len(sents)])); si+=1; words=[]; i=0; prev=None
            while len(words)<k and i<len(src):
                if i==len(src)-1 or rng.random()<17/36:
                    wd=NAIBBE['unigram_%s_%s'%(draw(prev),src[i])]; i+=1
                else:
                    t1=draw(prev); t2=t1 if card_per=='token' else deck.draw()
                    wd=NAIBBE['prefix_%s_%s'%(t1,src[i])]+NAIBBE['suffix_%s_%s'%(t2,src[i+1])]; i+=2
                words.append(wd); prev=wd[-1]
            if space_removal>0 and len(words)>2:
                merged=[words[0]]
                for x in words[1:]:
                    if rng.random()<space_removal: merged[-1]+=x
                    else: merged.append(x)
                words=merged
            if len(words)>=2: npg.append(words)
        out.append(npg)
    return out


# ---- plain Latin, one independent sentence per line (no cipher): isolates the line-reset property from the cipher question
def latin_indep_pages():
    out=[]; si=0
    for pg in shape:
        npg=[]
        for k in pg:
            s=sents[si%len(sents)]; si+=1; npg.append(s[:k] if len(s)>=k else s)
        out.append(npg)
    return out
