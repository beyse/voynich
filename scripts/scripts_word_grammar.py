import sys, re
sys.path.insert(0,'.')
from voynich.ivtff import parse, words_of
from collections import Counter, defaultdict
L=parse('data/ZL3b-n.txt')
W=words_of(L,kind='P')
c=Counter(W); N=len(W)

# 1. Positional glyph distribution: which glyphs occur word-initially / finally / medially
init=Counter(w[0] for w in W); fin=Counter(w[-1] for w in W)
med=Counter(ch for w in W for ch in w[1:-1])
allc=Counter(ch for w in W for ch in w)
print("glyph  total  %init  %final  %medial   (share of the glyph's occurrences by position)")
for g,n in allc.most_common():
    print(f"{g:>4} {n:>7} {init[g]/n:>7.2f} {fin[g]/n:>7.2f} {med[g]/n:>8.2f}")

# 2. Slot grammar: a compact regex that captures the usual 'word paradigm'
#   prefix: q? (o|y)? ; gallows/bench: (k|t|p|f|ck|ct|cp|cf|ch|sh|ckh|cth|cph|cfh)? ; e-group: e{0,3} ;
#   core: (o|a)? ; tail: (i{0,3}(n|r|l|m)|d|l|r|s|y|dy|ly|ry|...)?
SLOT = re.compile(r'^(q)?(o|y|d|s|ch|sh)?(k|t|p|f|ck|ct|cp|cf|ch|sh|ckh|cth|cph|cfh|l|r|d|s)?(e{0,3})?(o|a|y)?(i{0,3}(n|r|l|m)|d|l|r|s|y|dy|ly|ry|dl|ol|al|or|ar|am|an)?(y)?$')
m=sum(c[w] for w in c if SLOT.match(w)); print(f"\nslot-grammar coverage: {m/N:.3f} of tokens, {sum(1 for w in c if SLOT.match(w))/len(c):.3f} of types")
print("most frequent non-matching:",[w for w,_ in c.most_common(400) if not SLOT.match(w)][:30])

# 3. Glyph bigram transition table (top) and 'never' pairs
bi=Counter((w[i],w[i+1]) for w in W for i in range(len(w)-1))
gl=[g for g,_ in allc.most_common(20)]
print("\nwithin-word bigram counts (rows=first glyph, cols=second):")
print("    "+"".join(f"{g:>5}" for g in gl))
for a in gl:
    print(f"{a:>3} "+"".join(f"{bi[(a,b)]:>5}" for b in gl))

# 4. Line position effects
first=Counter(); last=Counter(); mid=Counter()
for ln in L:
    if ln.kind!='P' or len(ln.words)<3: continue
    ws=[w for w in ln.words if '?' not in w and '*' not in w]
    if len(ws)<3: continue
    first[ws[0][0]]+=1; last[ws[-1][-1]]+=1
    for w in ws[1:-1]: mid[w[0]]+=1
nf=sum(first.values()); nm=sum(mid.values()); nl=sum(last.values())
print("\nline-initial word's first glyph vs mid-line words' first glyph (share):")
for g,_ in (first+mid).most_common(12):
    print(f"{g:>3} first={first[g]/nf:.3f} mid={mid[g]/nm:.3f} ratio={ (first[g]/nf)/max(1e-9,mid[g]/nm):.2f}")
lastmid=Counter(w[-1] for ln in L if ln.kind=='P' for w in ln.words[1:-1] if w and '?' not in w)
nlm=sum(lastmid.values())
print("\nline-final word's last glyph vs mid-line words' last glyph:")
for g,_ in (last+lastmid).most_common(12):
    print(f"{g:>3} last={last[g]/nl:.3f} mid={lastmid[g]/nlm:.3f} ratio={(last[g]/nl)/max(1e-9,lastmid[g]/nlm):.2f}")

# 5. Paragraph-initial: gallows glyphs (p,f,t,k) at paragraph start
par_first=Counter(); other=Counter()
for ln in L:
    if ln.kind!='P' or not ln.words: continue
    w=ln.words[0]
    if ln.locus.startswith(('@','*')): par_first[w[0]]+=1
    else: other[w[0]]+=1
npf=sum(par_first.values()); no=sum(other.values())
print("\nparagraph-initial word's first glyph vs other line-initial words:")
for g in 'pftkqodsyc':
    print(f"{g:>3} par={par_first[g]/npf:.3f} other={other[g]/no:.3f}")
