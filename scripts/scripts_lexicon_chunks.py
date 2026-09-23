"""Does chopping a real language into short chunks reproduce the VMS 'no lexicon' property and its word statistics?"""
import sys, re, random, math
sys.path.insert(0,'.')
from voynich.ivtff import parse
from voynich.stats import clean_gutenberg, tokenize_natural, summarize, fmt_row, HEADER
exec(open('scripts/scripts_lexicon.py').read().split("L=parse")[0])
ok=lambda w: w and '?' not in w and '*' not in w
L=parse('data/ZL3b-n.txt',comma_is_space=False)
V=[w for ln in L if ln.kind=='P' for w in ln.words if ok(w)]
la=tokenize_natural(open('data/ref/la_caesar.txt').read())
it=tokenize_natural(clean_gutenberg('data/ref/it_dante.txt'))
def fixed_chunks(words,n):
    s=''.join(words); return [s[i:i+n] for i in range(0,len(s)-n,n)]
def var_chunks(words,lo,hi,seed=0):
    rng=random.Random(seed); s=''.join(words); out=[]; i=0
    while i<len(s)-hi: k=rng.randint(lo,hi); out.append(s[i:i+k]); i+=k
    return out
def rule_spaces(words,after='msty',minlen=3):
    s=''.join(words); out=[]; cur=''
    for ch in s:
        cur+=ch
        if ch in after and len(cur)>=minlen: out.append(cur); cur=''
    if cur: out.append(cur)
    return out
def syllabify(word, vowels='aeiouy'):
    pat=re.compile(rf'[^{vowels}]*[{vowels}]+(?:[^{vowels}]+(?![{vowels}]))?'); s=pat.findall(word); return s if s else [word]
syl=[s for x in la for s in syllabify(x)]
bisyl=[syl[i]+syl[i+1] for i in range(0,len(syl)-1,2)]
trisyl=[syl[i]+syl[i+1]+syl[i+2] for i in range(0,len(syl)-2,3)]
N=len(V)
cands=[('VMS',V),('Latin words',la[:N]),('Latin 3-chunks',fixed_chunks(la,3)[:N]),('Latin 4-chunks',fixed_chunks(la,4)[:N]),('Latin 5-chunks',fixed_chunks(la,5)[:N]),
       ('Latin 3-7 var',var_chunks(la,3,7)[:N]),('Latin rule msty',rule_spaces(la)[:N]),('Latin rule vowels',rule_spaces(la,'aeiou',4)[:N]),
       ('Latin bisyl',bisyl[:N]),('Latin trisyl',trisyl[:N]),('Italian bisyl',[s for s in (lambda sy:[sy[i]+sy[i+1] for i in range(0,len(sy)-1,2)])([s for x in it for s in syllabify(x,'aeiouàèéìòù')])][:N])]
print(HEADER)
for name,w in cands: print(fmt_row(summarize(name,w)))
print("\nlexicon test (k=2 glyph context): attested share of synthetic vs real held-out")
for name,w in cands: run(w,name,2)
