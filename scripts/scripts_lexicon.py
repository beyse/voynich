"""Lexicon test. Train a within-word glyph n-gram model on half the tokens; compare held-out real tokens with
synthetic words sampled from the model: log-prob per glyph, and the share of tokens whose type is attested."""
import sys, re, random, math
sys.path.insert(0,'.')
from voynich.ivtff import parse
from voynich.stats import clean_gutenberg, tokenize_natural
from collections import Counter, defaultdict
ok=lambda w: w and '?' not in w and '*' not in w
S,E='^','$'
def fit(words,k):
    m=defaultdict(Counter)
    for w in words:
        t=S*k+w+E
        for i in range(k,len(t)): m[t[i-k:i]][t[i]]+=1
    return m
def logp(model,k,w,alpha=0.1,V=30):
    t=S*k+w+E; lp=0
    for i in range(k,len(t)):
        c=model.get(t[i-k:i],Counter()); lp+=math.log2((c[t[i]]+alpha)/(sum(c.values())+alpha*V))
    return lp
def sample(model,k,rng,maxlen=15):
    t=S*k; s=''
    while len(s)<maxlen:
        c=model.get(t[-k:]); 
        if not c: break
        syms=list(c); x=rng.choices(syms,[c[y] for y in syms])[0]
        if x==E: break
        s+=x; t+=x
    return s
def run(words,label,k=2):
    rng=random.Random(0); w=list(words); rng.shuffle(w); half=len(w)//2; train,test=w[:half],w[half:]
    m=fit(train,k); trainset=set(train); testc=Counter(test)
    synth=[sample(m,k,rng) for _ in range(len(test))]; synth=[s for s in synth if s]
    lp_real=sum(logp(m,k,x) for x in test)/sum(len(x)+1 for x in test)
    lp_syn=sum(logp(m,k,x) for x in synth)/sum(len(x)+1 for x in synth)
    att_real=sum(x in trainset for x in test)/len(test); att_syn=sum(x in trainset for x in synth)/len(synth)
    # type-level: share of distinct synthetic types attested
    st=set(synth); att_syn_types=sum(x in trainset for x in st)/len(st)
    tt=set(test); att_real_types=sum(x in trainset for x in tt)/len(tt)
    print(f"{label:<14} k={k}  bits/glyph: real={-lp_real:5.2f} synth={-lp_syn:5.2f}  | attested-in-train share: real tokens {att_real:.2f}, synth tokens {att_syn:.2f} | types: real {att_real_types:.2f}, synth {att_syn_types:.2f} | mean len real {sum(map(len,test))/len(test):.2f} synth {sum(map(len,synth))/len(synth):.2f}")
    return synth
L=parse('data/ZL3b-n.txt',comma_is_space=False)
V=[w for ln in L if ln.kind=='P' for w in ln.words if ok(w)]
for k in (1,2,3): s=run(V,'VMS',k)
print("   synthetic VMS words (k=2):",' '.join(run(V,'VMS',2)[:25]))
for lang in 'AB': run([w for ln in L if ln.kind=='P' and ln.lang==lang for w in ln.words if ok(w)],f'VMS {lang}',2)
la=tokenize_natural(open('data/ref/la_caesar.txt').read())[:35000]; it=tokenize_natural(clean_gutenberg('data/ref/it_dante.txt'))[:35000]
he=re.findall(r'[א-ת]+',open('data/ref/he_genesis.txt',encoding='utf-8').read()); de=tokenize_natural(clean_gutenberg('data/ref/de_faust.txt'))[:35000]
for name,w in [('Latin',la),('Italian',it),('German',de),('Hebrew',he)]:
    for k in (2,3): s=run(w,name,k)
print("   synthetic Latin words (k=2):",' '.join(run(la,'Latin',2)[:25]))
