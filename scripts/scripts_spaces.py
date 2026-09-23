"""Are spaces real word boundaries? Predict boundary positions from local glyph context only.
Model: P(boundary | left k glyphs, right k glyphs), trained on half the lines, tested on the other half.
Report H(boundary|context) and F1 of predicting boundaries, VMS vs natural languages (with spaces removed)."""
import sys, re, random, math
sys.path.insert(0,'.')
from voynich.ivtff import parse
from voynich.stats import clean_gutenberg, tokenize_natural
from collections import Counter, defaultdict
ok=lambda w: w and '?' not in w and '*' not in w
def positions(line, k):
    """yield (context, is_boundary) for each between-glyph slot in the line"""
    s='#'*k+''.join(line)+'#'*k; b=set(); pos=k
    for w in line[:-1]: pos+=len(w); b.add(pos)
    for i in range(k+1, len(s)-k):
        yield (s[i-k:i], s[i:i+k]), (i in b)
def evaluate(lines, k, label):
    rng=random.Random(0); ls=list(lines); rng.shuffle(ls); half=len(ls)//2; train,test=ls[:half],ls[half:]
    c=defaultdict(Counter)
    for l in train:
        for ctx,b in positions(l,k): c[ctx][b]+=1
    # conditional entropy on test with add-0.5 smoothing; prediction = argmax
    H=0; n=0; tp=fp=fn=0
    prior=sum(v[True] for v in c.values())/sum(sum(v.values()) for v in c.values())
    for l in test:
        for ctx,b in positions(l,k):
            cc=c.get(ctx,Counter()); p=(cc[True]+0.5*prior*2)/(sum(cc.values())+1.0)
            H+=-math.log2(p if b else 1-p); n+=1
            pred=p>=0.5
            tp+=pred and b; fp+=pred and not b; fn+=(not pred) and b
    prec=tp/max(tp+fp,1); rec=tp/max(tp+fn,1); f1=2*prec*rec/max(prec+rec,1e-9)
    H0=-(prior*math.log2(prior)+(1-prior)*math.log2(1-prior))
    print(f"{label:<16} k={k}  boundary rate={prior:.3f}  H(b)={H0:.3f}  H(b|ctx)={H/n:.3f}  info gain={1-H/n/H0:5.1%}  P={prec:.2f} R={rec:.2f} F1={f1:.2f}")
for comma in (False,True):
    L=parse('data/ZL3b-n.txt',comma_is_space=comma)
    lines=[[w for w in ln.words if ok(w)] for ln in L if ln.kind=='P']; lines=[l for l in lines if len(l)>=2]
    for k in (1,2,3): evaluate(lines,k,f"VMS {'c=sp' if comma else 'c=jn'}")
    for lang in 'AB':
        ll=[[w for w in ln.words if ok(w)] for ln in L if ln.kind=='P' and ln.lang==lang]; ll=[l for l in ll if len(l)>=2]
        evaluate(ll,2,f"VMS-{lang} {'c=sp' if comma else 'c=jn'}")
L=parse('data/ZL3b-n.txt'); lens=[len([w for w in ln.words if ok(w)]) for ln in L if ln.kind=='P']
def chunk(words):
    rng=random.Random(2); out=[]; i=0
    while i<len(words)-12:
        k=rng.choice(lens); out.append(words[i:i+k]); i+=k
    return out
la=tokenize_natural(open('data/ref/la_caesar.txt').read())[:35000]; it=tokenize_natural(clean_gutenberg('data/ref/it_dante.txt'))[:35000]; de=tokenize_natural(clean_gutenberg('data/ref/de_faust.txt'))[:35000]
he=re.findall(r'[א-ת]+',open('data/ref/he_genesis.txt',encoding='utf-8').read())
for name,w in [('Latin',la),('Italian',it),('German',de),('Hebrew',he)]:
    for k in (1,2,3): evaluate(chunk(w),k,name)
# Control: a verbose cipher of Latin where spaces are REMOVED and re-inserted by a glyph rule (after vowels+'s', say)
# -> shows what a rule-inserted-space text looks like under this test
def rule_spaces(words):
    s=''.join(words); out=[]; cur=''
    for ch in s:
        cur+=ch
        if ch in 'msty' and len(cur)>=3: out.append(cur); cur=''
    if cur: out.append(cur)
    return out
rl=rule_spaces(la); print(f"(rule-spaced Latin: {len(rl)} 'words', mean len {sum(map(len,rl))/len(rl):.2f})")
for k in (1,2,3): evaluate(chunk(rl),k,'Latin rule-spaced')
