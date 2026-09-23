import sys
sys.path.insert(0,'.')
from voynich.ivtff import parse, words_of
from collections import Counter
L=parse('data/ZL3b-n.txt')
text=Counter(words_of(L,kind='P'))
labels=[(ln.page,ln.section,w) for ln in L if ln.kind=='L' for w in ln.words if '?' not in w and '*' not in w]
print("labels total:",len(labels),"distinct:",len({w for _,_,w in labels}))
by_sec=Counter(s for _,s,_ in labels); print("by section:",by_sec)
# how many label words also occur in running text?
inText=sum(1 for _,_,w in labels if text[w]>0)
print(f"label tokens that also occur in paragraph text: {inText/len(labels):.3f}")
# per section
for s in by_sec:
    ls=[w for _,ss,w in labels if ss==s]
    print(f"  section {s}: {sum(1 for w in ls if text[w]>0)/len(ls):.2f} in text; mean len {sum(map(len,ls))/len(ls):.2f}; first-glyph {Counter(w[0] for w in ls).most_common(5)}")
# star labels (section S: 'stars/recipes' has labels? Actually A/Z have star labels)
print("\nlabel first glyph overall:",Counter(w[0] for _,_,w in labels).most_common(10))
print("text first glyph overall :",Counter(w[0] for w in text.elements()).most_common(10))
# labels starting with 'o': known phenomenon
print("\nlabel duplicates:",[(w,n) for w,n in Counter(w for _,_,w in labels).most_common(15)])
# Zodiac labels (nymphs) f70-f73 pages
zod=[(p,w) for p,s,w in labels if s=='Z']
print("\nZodiac labels sample:",zod[:30])
