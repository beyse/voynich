"""Leave-one-quire-out jackknife standard errors for the core VMS metrics (no duplication of pages, unlike a bootstrap)."""
import sys, json, random, math
sys.path.insert(0,'.')
from voynich.ivtff import parse
from voynich.battery import _excess_line, _excess_b, _space_gain, _lexicon, _cond_entropy, _zipf
from collections import Counter, defaultdict
ok=lambda w: w and '?' not in w and '*' not in w
L=parse('data/ZL3b-n.txt',comma_is_space=False)
pages=defaultdict(list); quire={}
for ln in L:
    if ln.kind!='P': continue
    ws=[w for w in ln.words if ok(w)]
    if len(ws)>=2: pages[ln.page].append(ws); quire[ln.page]=ln.quire or '?'
def core(pgs,seed=0):
    lines=[l for pg in pgs for l in pg]; words=[w for l in lines for w in l]; inner=[l[1:-1] for l in lines if len(l)>=5]
    c=Counter(words); r={}
    r['edge_mi']=_excess_line(inner,lambda a,b:(a[-1],b[0]),reps=4); r['token_mi']=_excess_line(inner,lambda a,b:(a,b),reps=4)
    brk=[(pg[k][-1],pg[k+1][0]) for pg in pgs for k in range(len(pg)-1)]
    adjp=[(s[i],s[i+1]) for s in inner for i in range(len(s)-1)]; rng=random.Random(seed); n=min(len(brk),len(adjp))
    r['break_mi']=_excess_b(rng.sample(brk,n),reps=4); r['adj_mi_same_n']=sum(_excess_b(rng.sample(adjp,n),reps=4) for _ in range(3))/3
    r['space_gain']=_space_gain(lines,1); r['hapax']=sum(1 for v in c.values() if v==1)/len(c); r['zipf']=_zipf(words)
    lr,ls=_lexicon(words,2); r['lex_real']=lr; r['lex_synth']=ls; r['lex_gap']=lr-ls
    strings=[' '.join(l) for l in lines]; r['h2']=_cond_entropy(strings,2); r['h4']=_cond_entropy(strings,4)
    return r
P=list(pages.values()); Q=[quire[p] for p in pages]; quires=sorted(set(Q)); print("quires:",quires,flush=True)
point=core(P); reps=[]
for q in quires:
    sub=[pg for pg,qq in zip(P,Q) if qq!=q]; reps.append(core(sub)); print(q,flush=True)
n=len(quires); out={'point':point,'quires':quires,'reps':reps,'se':{},'ci95':{}}
for k in point:
    vals=[r[k] for r in reps]; m=sum(vals)/n; se=math.sqrt((n-1)/n*sum((v-m)**2 for v in vals)); out['se'][k]=se; out['ci95'][k]=(point[k]-1.96*se,point[k]+1.96*se)
    print(f"{k:<14} {point[k]:8.4f}  jackknife SE {se:.4f}  95% CI [{out['ci95'][k][0]:.4f}, {out['ci95'][k][1]:.4f}]")
json.dump(out,open('results/jackknife.json','w'),indent=1)
