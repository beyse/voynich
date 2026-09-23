"""Herbal-B: stratified permutation within hand; hand 2 alone; plus higher-precision Herbal-A."""
import sys, json, re
sys.path.insert(0,'.')
exec(open('scripts/scripts_text_vs_image.py').read().split("herbalA=[p for p in pages")[0])
def mantel_strat(A,B,mask,strata,reps=5000,seed=0):
    iu=np.triu_indices(len(A),1); m=mask[iu]
    def sp(x,y):
        rx=np.argsort(np.argsort(x)); ry=np.argsort(np.argsort(y)); return np.corrcoef(rx,ry)[0,1]
    obs=sp(A[iu][m],B[iu][m]); rng=np.random.default_rng(seed); null=[]
    groups=defaultdict(list)
    for i,s in enumerate(strata): groups[s].append(i)
    for _ in range(reps):
        perm=np.arange(len(A))
        for g,idx in groups.items():
            idx=np.array(idx); perm[idx]=idx[rng.permutation(len(idx))]
        Bp=B[perm][:,perm]; null.append(sp(A[iu][m],Bp[iu][m]))
    null=np.array(null); return obs,(np.sum(null>=obs)+1)/(reps+1)
herbalB=[p for p in pages if meta[p][1]=='H' and meta[p][0]=='B' and folio(p)<=116 and p in feats and len(pages[p])>=40]
print("Herbal-B pages by hand:",Counter(meta[p][2] for p in herbalB))
ps=herbalB; F=np.array([folio(p) for p in ps]); FD=np.abs(F[:,None]-F[None,:]); mask=FD>=6
I=image_matrix(ps); W=word_dist(ps); Bg=bigram_dist(ps); strata=[meta[p][2] for p in ps]
for name,T in [('words',W),('glyph bigrams',Bg)]:
    r,p=mantel_strat(T,I,mask,strata); r2,p2=mantel_strat(T,I,np.ones_like(mask,dtype=bool),strata)
    print(f"  Herbal-B, permutation within hand: text({name}) vs image r={r:+.3f} p={p:.3f} | all pairs r={r2:+.3f} p={p2:.3f}")
# same-hand-only pairs
same=np.array([[meta[a][2]==meta[b][2] for b in ps] for a in ps])
for name,T in [('words',W),('glyph bigrams',Bg)]:
    r,p=mantel_strat(T,I,mask&same,strata); print(f"  Herbal-B, same-hand pairs only, within-hand permutation: text({name}) vs image r={r:+.3f} p={p:.3f}")
h2=[p for p in herbalB if meta[p][2]=='2']
if len(h2)>=8:
    ps=h2; F=np.array([folio(p) for p in ps]); FD=np.abs(F[:,None]-F[None,:]); mask=FD>=6
    I=image_matrix(ps); W=word_dist(ps); Bg=bigram_dist(ps)
    for name,T in [('words',W),('glyph bigrams',Bg)]:
        r,p,sd=mantel(T,I,mask,reps=5000); r2,p2,_=mantel(T,I,np.ones_like(mask,dtype=bool),reps=5000)
        print(f"  Herbal-B hand 2 only ({len(ps)} pages): text({name}) vs image r={r:+.3f} p={p:.3f} | all pairs r={r2:+.3f} p={p2:.3f}")
# Herbal-A with more permutations and with hand-1 pharma pages added as a second same-hand set
herbalA=[p for p in pages if meta[p]==('A','H','1') and folio(p)<=116 and p in feats and len(pages[p])>=40]
ps=herbalA; F=np.array([folio(p) for p in ps]); FD=np.abs(F[:,None]-F[None,:]); mask=FD>=6
I=image_matrix(ps); W=word_dist(ps); Bg=bigram_dist(ps)
for name,T in [('words',W),('glyph bigrams',Bg)]:
    r,p,sd=mantel(T,I,mask,reps=10000); print(f"  Herbal-A ({len(ps)} pages, 10000 perms): text({name}) vs image r={r:+.3f} p={p:.3f}")
# per-feature: does any single image feature correlate with text distance? (words)
iu=np.triu_indices(len(ps),1); m=mask[iu]
for k in FKEYS:
    x=np.array([feats[p][k] for p in ps]); D=np.abs(x[:,None]-x[None,:])
    r,p,_=mantel(W,D,mask,reps=2000); print(f"    feature {k:<13} r={r:+.3f} p={p:.3f}")
