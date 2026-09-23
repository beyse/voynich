"""Entropy rate of the glyph stream (lines as strings, space as symbol) with growing context,
compared to synthetic twins sampled from fitted order-1 and order-2 models with identical line lengths."""
import sys, re, random, math, lzma
sys.path.insert(0,'.')
from voynich.ivtff import parse
from voynich.stats import clean_gutenberg, tokenize_natural
from collections import Counter, defaultdict
ok=lambda w: w and '?' not in w and '*' not in w
S,E='^','$'
def cond_entropy(strings,k):
    """H(x_i | x_{i-k..i-1}) plug-in over all strings (with start markers)"""
    ctx=Counter(); joint=Counter()
    for s in strings:
        t=S*k+s+E
        for i in range(k,len(t)):
            joint[t[i-k:i+1]]+=1; ctx[t[i-k:i]]+=1
    n=sum(joint.values())
    return -sum(c/n*math.log2(c/ctx[j[:-1]]) for j,c in joint.items())
def fit(strings,k):
    m=defaultdict(Counter)
    for s in strings:
        t=S*k+s+E
        for i in range(k,len(t)): m[t[i-k:i]][t[i]]+=1
    return m
def sample(model,k,lengths,rng):
    out=[]
    for L in lengths:
        t=S*k; s=''
        while True:
            c=model.get(t[-k:]);
            if not c: break
            syms=list(c); w=[c[x] for x in syms]
            if len(s)<L*0.5 and len(syms)>1:      # too short to end: resample among non-end symbols
                w=[0 if x==E else v for x,v in zip(syms,w)]
            x=rng.choices(syms,w)[0]
            if x==E: break
            s+=x; t+=x
            if len(s)>=L: break
        out.append(s)
    return out
def compress_bits(strings):
    b='\n'.join(strings).encode('utf-8'); return len(lzma.compress(b,preset=9|lzma.PRESET_EXTREME))*8/sum(len(s) for s in strings)
def profile(strings,label,twins=True,K=(1,2,3,4,5)):
    h=[cond_entropy(strings,k) for k in K]
    row=f"{label:<20} "+" ".join(f"h{k}={v:5.2f}" for k,v in zip(K,h))+f"  lzma={compress_bits(strings):5.2f}"
    print(row)
    if twins:
        lengths=[len(s) for s in strings]
        for order in (1,2,3):
            tw=sample(fit(strings,order),order,lengths,random.Random(order))
            ht=[cond_entropy(tw,k) for k in K]
            print(f"{'  twin order-'+str(order):<20} "+" ".join(f"h{k}={v:5.2f}" for k,v in zip(K,ht))+f"  lzma={compress_bits(tw):5.2f}   excess(real-twin): "+" ".join(f"{a-b:+.2f}" for a,b in zip(h,ht)))
L=parse('data/ZL3b-n.txt',comma_is_space=False)
lines=[' '.join(w for w in ln.words if ok(w)) for ln in L if ln.kind=='P']; lines=[l for l in lines if len(l)>=8]
print(f"VMS: {len(lines)} lines, {sum(map(len,lines))} glyphs incl. spaces")
profile(lines,'VMS all')
for lang in 'AB':
    ll=[' '.join(w for w in ln.words if ok(w)) for ln in L if ln.kind=='P' and ln.lang==lang]; ll=[l for l in ll if len(l)>=8]
    profile(ll,f'VMS {lang}')
lens=[len(l.split()) for l in lines]
def chunk(words):
    rng=random.Random(2); out=[]; i=0
    while i<len(words)-12:
        k=rng.choice(lens); out.append(' '.join(words[i:i+k])); i+=k
    return out
la=tokenize_natural(open('data/ref/la_caesar.txt').read())[:35000]; it=tokenize_natural(clean_gutenberg('data/ref/it_dante.txt'))[:35000]
he=re.findall(r'[א-ת]+',open('data/ref/he_genesis.txt',encoding='utf-8').read())
de=tokenize_natural(clean_gutenberg('data/ref/de_faust.txt'))[:35000]
profile(chunk(la),'Latin'); profile(chunk(it),'Italian'); profile(chunk(de),'German'); profile(chunk(he),'Hebrew')
def rule_spaces(words):
    s=''.join(words); out=[]; cur=''
    for ch in s:
        cur+=ch
        if ch in 'msty' and len(cur)>=3: out.append(cur); cur=''
    if cur: out.append(cur)
    return out
profile(chunk(rule_spaces(la)),'Latin rule-spaced')
