"""Verbose-cipher test: if plaintext letters map to glyph groups, merging the groups into
single units should raise conditional entropy h2 toward natural-language values (~3.0-3.5)."""
import sys, math
sys.path.insert(0,'.')
from voynich.ivtff import parse, words_of
from voynich.stats import char_entropies, clean_gutenberg, tokenize_natural
from collections import Counter

L=parse('data/ZL3b-n.txt')
W=words_of(L,kind='P')

def retok(words, groups):
    """replace multi-glyph groups by single private-use symbols (longest first)"""
    groups=sorted(groups,key=len,reverse=True)
    sym={g:chr(0xE000+i) for i,g in enumerate(groups)}
    out=[]
    for w in words:
        for g in groups: w=w.replace(g,sym[g])
        out.append(w)
    return out

levels=[
 ('EVA raw',[]),
 ('+ch sh',['ch','sh']),
 ('+benched gallows',['ch','sh','ckh','cth','cph','cfh']),
 ('+qo ee ii',['ch','sh','ckh','cth','cph','cfh','qo','ee','eee','ii','iii']),
 ('+aiin ain ar or ol al dy',['ch','sh','ckh','cth','cph','cfh','qo','eee','ee','iiin','iin','ain','aiin','ar','or','ol','al','dy','am','an','ir','ir','ey']),
]
print(f"{'tokenisation':<28}{'alph':>5}{'h1':>7}{'h2':>7}{'h2/h1':>7}{'chars/word':>11}")
for name,g in levels:
    ww=retok(W,g); h0,h1,h2,a=char_entropies(ww)
    print(f"{name:<28}{a:>5}{h1:>7.2f}{h2:>7.2f}{h2/h1:>7.2f}{sum(map(len,ww))/len(ww):>11.2f}")
print()
for name,path in [('de_faust','data/ref/de_faust.txt'),('la_caesar','data/ref/la_caesar.txt'),('it_dante','data/ref/it_dante.txt')]:
    t=clean_gutenberg(path) if name!='la_caesar' else open(path).read()
    w=tokenize_natural(t)[:35000]; h0,h1,h2,a=char_entropies(w)
    print(f"{name:<28}{a:>5}{h1:>7.2f}{h2:>7.2f}{h2/h1:>7.2f}{sum(map(len,w))/len(w):>11.2f}")
    # abjad-like: strip vowels
    wv=[''.join(ch for ch in x if ch not in 'aeiouäöüàèéìòù') for x in w]; wv=[x for x in wv if x]
    h0,h1,h2,a=char_entropies(wv)
    print(f"{name+' no vowels':<28}{a:>5}{h1:>7.2f}{h2:>7.2f}{h2/h1:>7.2f}{sum(map(len,wv))/len(wv):>11.2f}")

# Information content per word: word entropy vs. natural texts of equal size
from voynich.stats import word_stats
print("\nword-level entropy (bits/word):")
print(f"VMS {word_stats(W)['word_entropy']:.2f}")
for name,path in [('de_faust','data/ref/de_faust.txt'),('la_caesar','data/ref/la_caesar.txt'),('it_dante','data/ref/it_dante.txt')]:
    t=clean_gutenberg(path) if name!='la_caesar' else open(path).read()
    w=tokenize_natural(t)[:len(W)]
    print(f"{name} {word_stats(w)['word_entropy']:.2f}")
