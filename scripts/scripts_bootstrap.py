"""Page-level bootstrap confidence intervals for the core VMS metrics (ZL3b, comma joined)."""
import sys, json, random, math
sys.path.insert(0,'.')
from voynich.ivtff import parse
from voynich.battery import _excess_line, _excess_b, _space_gain, _lexicon, _cond_entropy, _zipf
from collections import Counter, defaultdict
ok=lambda w: w and '?' not in w and '*' not in w
L=parse('data/ZL3b-n.txt',comma_is_space=False)
pages=defaultdict(list)
for ln in L:
    if ln.kind!='P': continue
    ws=[w for w in ln.words if ok(w)]
    if len(ws)>=2: pages[ln.page].append(ws)
P=list(pages.values())
def core(pgs,seed=0):
    lines=[l for pg in pgs for l in pg]; words=[w for l in lines for w in l]; inner=[l[1:-1] for l in lines if len(l)>=5]
    c=Counter(words); r={}
    r['edge_mi']=_excess_line(inner,lambda a,b:(a[-1],b[0]),reps=3)
    r['token_mi']=_excess_line(inner,lambda a,b:(a,b),reps=3)
    brk=[(pg[k][-1],pg[k+1][0]) for pg in pgs for k in range(len(pg)-1)]
    adjp=[(s[i],s[i+1]) for s in inner for i in range(len(s)-1)]; rng=random.Random(seed); n=min(len(brk),len(adjp))
    r['break_mi']=_excess_b(rng.sample(brk,n),reps=3); r['adj_mi_same_n']=_excess_b(rng.sample(adjp,n),reps=3)
    r['space_gain']=_space_gain(lines,1); r['hapax']=sum(1 for v in c.values() if v==1)/len(c); r['zipf']=_zipf(words)
    lr,ls=_lexicon(words,2); r['lex_real']=lr; r['lex_synth']=ls; r['lex_gap']=lr-ls
    strings=[' '.join(l) for l in lines]; r['h2']=_cond_entropy(strings,2); r['h4']=_cond_entropy(strings,4)
    return r
REPS=int(sys.argv[1]) if len(sys.argv)>1 else 60
rng=random.Random(42); boots=[]
point=core(P); print("point estimates:",{k:round(v,4) for k,v in point.items()},flush=True)
for b in range(REPS):
    sample=[P[rng.randrange(len(P))] for _ in range(len(P))]
    boots.append(core(sample,seed=b)); print(b,flush=True)
out={'point':point,'boot':boots}
ci={k:(sorted(x[k] for x in boots)[int(0.025*REPS)],sorted(x[k] for x in boots)[int(0.975*REPS)-1]) for k in point}
out['ci95']=ci
json.dump(out,open('results/bootstrap.json','w'),indent=1)
for k,v in point.items(): print(f"{k:<14} {v:8.4f}  95% CI [{ci[k][0]:.4f}, {ci[k][1]:.4f}]")
