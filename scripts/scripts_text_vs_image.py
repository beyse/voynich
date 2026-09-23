"""Does the text carry information about the illustration on its page?
Mantel test: text distance vs image-feature distance across herbal pages of one hand, permutation null,
folio distance controlled. Word level vs glyph-bigram level. Synthetic positive control for sensitivity."""
import sys, json, math, random, re
sys.path.insert(0,'.')
from voynich.ivtff import parse
from collections import Counter, defaultdict
import numpy as np
ok=lambda w: w and '?' not in w and '*' not in w
L=parse('data/ZL3b-n.txt',comma_is_space=False)
feats=json.load(open('results/page_colors.json'))
pages=defaultdict(list); meta={}
for ln in L:
    if ln.kind!='P': continue
    ws=[w for w in ln.words if ok(w)]
    if ws: pages[ln.page].extend(ws); meta[ln.page]=(ln.lang,ln.section,ln.hand)
def folio(p): m=re.match(r'f(\d+)([rv])',p); return int(m.group(1))*2+(m.group(2)=='v')
FKEYS=['green','blue','red','green_y','green_x','red_y','green_hue','blue_frac','red_frac','colour_total']
def image_matrix(ps):
    X=np.array([[feats[p][k] for k in FKEYS] for p in ps]); X=(X-X.mean(0))/(X.std(0)+1e-9)
    return np.sqrt(((X[:,None,:]-X[None,:,:])**2).sum(-1))
def word_dist(ps,extra=None):
    vocab={}; vecs=[]
    for p in ps:
        c=Counter(pages[p]);
        if extra: c.update(extra[p])
        vecs.append(c)
    keys=sorted({w for c in vecs for w in c}); idx={w:i for i,w in enumerate(keys)}
    M=np.zeros((len(ps),len(keys)))
    for i,c in enumerate(vecs):
        for w,n in c.items(): M[i,idx[w]]=n
    M=M/ M.sum(1,keepdims=True)                      # relative frequencies
    M=np.sqrt(M)                                     # Hellinger embedding
    D=np.sqrt(np.maximum(0,((M[:,None,:]-M[None,:,:])**2).sum(-1)))
    return D
def bigram_dist(ps):
    vecs=[]
    for p in ps:
        s=' '.join(pages[p]); vecs.append(Counter(zip(s,s[1:])))
    keys=sorted({k for c in vecs for k in c}); idx={k:i for i,k in enumerate(keys)}
    M=np.zeros((len(ps),len(keys)))
    for i,c in enumerate(vecs):
        for k,n in c.items(): M[i,idx[k]]=n
    M=np.sqrt(M/M.sum(1,keepdims=True)); return np.sqrt(np.maximum(0,((M[:,None,:]-M[None,:,:])**2).sum(-1)))
def mantel(A,B,mask,reps=3000,seed=0):
    """Spearman correlation between upper-triangle entries (masked) of A and B, permutation null over page identity of B."""
    iu=np.triu_indices(len(A),1); m=mask[iu]
    def sp(x,y):
        rx=np.argsort(np.argsort(x)); ry=np.argsort(np.argsort(y)); return np.corrcoef(rx,ry)[0,1]
    obs=sp(A[iu][m],B[iu][m]); rng=np.random.default_rng(seed); null=[]
    for _ in range(reps):
        perm=rng.permutation(len(A)); Bp=B[perm][:,perm]; null.append(sp(A[iu][m],Bp[iu][m]))
    null=np.array(null); p=(np.sum(null>=obs)+1)/(reps+1)
    return obs,p,null.std()
def run(ps,label,extra=None):
    ps=[p for p in ps if p in feats and len(pages[p])>=40]
    F=np.array([folio(p) for p in ps]); FD=np.abs(F[:,None]-F[None,:]); mask=FD>=6
    I=image_matrix(ps); W=word_dist(ps,extra); Bg=bigram_dist(ps)
    print(f"\n{label}: {len(ps)} pages, {mask[np.triu_indices(len(ps),1)].sum()} pairs with folio distance >= 3 folios")
    for name,T in [('words',W),('glyph bigrams',Bg)]:
        r,p,sd=mantel(T,I,mask); r_all,p_all,_=mantel(T,I,np.ones_like(mask,dtype=bool))
        rf,pf,_=mantel(T,FD.astype(float),np.ones_like(mask,dtype=bool))
        print(f"  text({name}) vs image: r={r:+.3f} (p={p:.3f}, null sd {sd:.3f}) | all pairs r={r_all:+.3f} (p={p_all:.3f}) | text vs folio distance r={rf:+.3f} (p={pf:.3f})")
    ri,pi,_=mantel(I,FD.astype(float),np.ones_like(mask,dtype=bool)); print(f"  image vs folio distance: r={ri:+.3f} (p={pi:.3f})")
    return ps
herbalA=[p for p in pages if meta[p]==('A','H','1') and folio(p)<=116]
herbalB=[p for p in pages if meta[p][1]=='H' and meta[p][0]=='B' and folio(p)<=116]
psA=run(herbalA,'Herbal-A, hand 1')
psB=run(herbalB,'Herbal-B (hands 2/3/5)')
# synthetic positive control: add k 'description' tokens per page determined by image features (colour bins)
print("\nPositive control (Herbal-A): add k content tokens per page derived from the image features")
rng=random.Random(0)
for k in (2,5,10,20):
    extra={}
    for p in psA:
        f=feats[p]; toks=[]
        toks.append('BLUE' if f['blue_frac']>0.05 else 'NOBLUE'); toks.append('BIGLEAF' if f['green']>0.06 else 'SMALLLEAF')
        toks.append('ROOTS' if f['red_frac']>0.4 else 'FEWROOTS'); toks.append('TOP' if f['green_y']<0.45 else 'LOW')
        extra[p]=Counter(rng.choices(toks,k=k))
    ps=[p for p in psA]; F=np.array([folio(p) for p in ps]); FD=np.abs(F[:,None]-F[None,:]); mask=FD>=6
    r,p,sd=mantel(word_dist(ps,extra),image_matrix(ps),mask,reps=1000)
    print(f"  k={k:>2} description tokens per page (of ~{int(np.mean([len(pages[p]) for p in ps]))} words): r={r:+.3f} (p={p:.3f})")
