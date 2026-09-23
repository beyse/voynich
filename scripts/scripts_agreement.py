"""Do adjacent words share their ENDING (agreement-like) or their BEGINNING (copy/list-like)?
P(feature equal) for adjacent inner pairs vs within-line shuffle (marginal-preserving)."""
import sys, re, random
sys.path.insert(0,'.')
from voynich.ivtff import parse
from voynich.stats import clean_gutenberg, tokenize_natural
from collections import Counter
ok=lambda w: w and '?' not in w and '*' not in w
def gallows(w):
    m=re.search(r'c?[ktpf]h?',w); return m.group(0) if m else '-'
FEATS={'first1':lambda w:w[:1],'first2':lambda w:w[:2],'gallows':gallows,'last1':lambda w:w[-1:],'last2':lambda w:w[-2:],'last3':lambda w:w[-3:],'identical':lambda w:w}
def run(lines,label,reps=10):
    inner=[l[1:-1] for l in lines if len(l)>=5]
    obs={k:0 for k in FEATS}; n=0
    for s in inner:
        for i in range(len(s)-1):
            n+=1
            for k,f in FEATS.items(): obs[k]+= f(s[i])==f(s[i+1])
    base={k:0.0 for k in FEATS}
    for r in range(reps):
        rng=random.Random(r)
        for s in inner:
            t=rng.sample(s,len(s))
            for i in range(len(t)-1):
                for k,f in FEATS.items(): base[k]+= (f(t[i])==f(t[i+1]))/reps
    print(f"{label:<16} n={n:>6} "+" ".join(f"{k}: {obs[k]/n:.3f}/{base[k]/n:.3f}={obs[k]/max(base[k],1e-9):4.2f}" for k in FEATS))
print("format: feature: P(equal, adjacent)/P(equal, within-line shuffled) = ratio\n")
for comma in (True,False):
    L=parse('data/ZL3b-n.txt',comma_is_space=comma)
    tag='comma=space' if comma else 'comma=join '
    for lang in (None,'A','B'):
        lines=[[w for w in ln.words if ok(w)] for ln in L if ln.kind=='P' and (lang is None or ln.lang==lang)]
        run(lines,f'VMS{lang or ""} {tag}')
    if comma:
        # also report the frequency of uncertain spaces
        raw=open('data/ZL3b-n.txt').read(); print(f"   (uncertain spaces ',' in file: {raw.count(',')} vs certain '.': {raw.count('.')})")
print()
L=parse('data/ZL3b-n.txt'); lens=[len([w for w in ln.words if ok(w)]) for ln in L if ln.kind=='P']
def chunk(words):
    rng=random.Random(2); out=[]; i=0
    while i<len(words)-12:
        k=rng.choice(lens); out.append(words[i:i+k]); i+=k
    return out
la=tokenize_natural(open('data/ref/la_caesar.txt').read())[:35000]; it=tokenize_natural(clean_gutenberg('data/ref/it_dante.txt'))[:35000]; de=tokenize_natural(clean_gutenberg('data/ref/de_faust.txt'))[:35000]
he=re.findall(r'[א-ת]+',open('data/ref/he_genesis.txt',encoding='utf-8').read())
run(chunk(la),'Latin'); run(chunk(it),'Italian'); run(chunk(de),'German'); run(chunk(he),'Hebrew')
# Latin verse-like control with strong agreement? use the same Latin but only noun-phrase-rich text -> skip.
# Where exactly is the shared material? For adjacent VMS pairs that share last2 but differ: what differs?
print("\nVMS adjacent pairs sharing the last 2 glyphs but not identical: most common (onset_a -> onset_b) where onset = word minus shared suffix")
L=parse('data/ZL3b-n.txt',comma_is_space=False)
lines=[[w for w in ln.words if ok(w)] for ln in L if ln.kind=='P']
c=Counter()
for l in lines:
    s=l[1:-1]
    for i in range(len(s)-1):
        a,b=s[i],s[i+1]
        if a!=b and a[-2:]==b[-2:]:
            # longest common suffix
            k=0
            while k<min(len(a),len(b)) and a[-1-k]==b[-1-k]: k+=1
            c[(a[:-k] or '∅',b[:-k] or '∅',a[-k:])]+=1
for (x,y,suf),n in c.most_common(25): print(f"   {x:>6} -> {y:<6}  (+{suf})  {n}")
