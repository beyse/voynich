"""Are Voynich 'words' more like natural-language syllables than words?"""
import sys, re, random
sys.path.insert(0,'.')
from voynich.ivtff import parse, words_of
from voynich.stats import *
def syllabify(word, vowels):
    # onset* nucleus+ (coda only if no following vowel)
    pat=re.compile(rf'[^{vowels}]*[{vowels}]+(?:[^{vowels}]+(?![{vowels}]))?')
    s=pat.findall(word)
    return s if s else [word]
L=parse('data/ZL3b-n.txt'); V=words_of(L,kind='P'); N=len(V)
print(HEADER)
print(fmt_row(summarize('VMS words',V)))
random.seed(0)
for name,path,vow in [('la',"data/ref/la_caesar.txt",'aeiouy'),('it',"data/ref/it_dante.txt",'aeiouàèéìòù'),('de',"data/ref/de_faust.txt",'aeiouäöüy')]:
    t=clean_gutenberg(path) if name!='la' else open(path).read()
    w=tokenize_natural(t)
    syl=[s for x in w for s in syllabify(x,vow)]
    st=random.randrange(0,len(syl)-N)
    print(fmt_row(summarize(f'{name} syllables',syl[st:st+N])))
    st=random.randrange(0,max(1,len(w)-N))
    print(fmt_row(summarize(f'{name} words',w[st:st+N])))
    if name=='la': print("   sample syllables:",syl[1000:1030])
# word-length distribution comparison
def ld(ws):
    c=Counter(len(x) for x in ws); n=len(ws); return [round(c.get(i,0)/n,3) for i in range(1,11)]
from collections import Counter
print("\nlength dist 1..10")
print("VMS      ",ld(V))
t=open('data/ref/la_caesar.txt').read(); w=tokenize_natural(t)
print("la syll  ",ld([s for x in w for s in syllabify(x,'aeiouy')]))
t=clean_gutenberg('data/ref/it_dante.txt'); w=tokenize_natural(t)
print("it syll  ",ld([s for x in w for s in syllabify(x,'aeiouàèéìòù')]))
# two-syllable chunks (bisyllables)
w=tokenize_natural(open('data/ref/la_caesar.txt').read())
syl=[s for x in w for s in syllabify(x,'aeiouy')]
bis=[syl[i]+syl[i+1] for i in range(0,len(syl)-1,2)]
print(fmt_row(summarize('la bisyllables',bis[:N])))
print("la bisyl ",ld(bis))
