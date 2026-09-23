import sys, json
sys.path.insert(0,'.')
from voynich.battery import battery, twin_residual
from voynich.generators import *
from collections import Counter
real_lines={' '.join(l) for pg in P for l in pg}
real_bigrams=Counter((l[i],l[i+1]) for pg in P for l in pg for i in range(len(l)-1))
# real text self-consistency: bigram attestation between halves of pages
import random
rng=random.Random(0); pg_ids=list(range(len(P))); rng.shuffle(pg_ids); A=set(pg_ids[:len(P)//2])
bgA=Counter((l[i],l[i+1]) for k,pg in enumerate(P) if k in A for l in pg for i in range(len(l)-1))
bgB=[(l[i],l[i+1]) for k,pg in enumerate(P) if k not in A for l in pg for i in range(len(l)-1)]
print(f"real: share of word bigrams in half B attested in half A: {sum(b in bgA for b in bgB)/len(bgB):.3f}")
cols=[('edge_mi','{:.3f}'),('token_mi','{:.3f}'),('adj_mi_same_n','{:.3f}'),('d2_mi','{:.3f}'),('hapax','{:.2f}'),('lex_real','{:.2f}'),('lex_synth','{:.2f}'),('lzma_resid','{:+.3f}'),('page_mi','{:.3f}')]
print(f"{'mechanism':<16}"+"".join(f" {k[:9]:>9}" for k,_ in cols)+"  lines_copied  bigrams_attested")
for order in (3,4,5,6):
    pg=markov_pages(order,True); r=battery(pg,f'markov{order}+drift'); r['lzma_resid'],_=twin_residual(pg,groups)
    lines=[' '.join(l) for x in pg for l in x]; copied=sum(l in real_lines for l in lines)/len(lines)
    bg=[(l[i],l[i+1]) for x in pg for l in x for i in range(len(l)-1)]; att=sum(b in real_bigrams for b in bg)/len(bg)
    print(f"{r['label']:<16}"+"".join(f" {f.format(r[k]):>9}" for k,f in cols)+f"  {copied:11.3f}  {att:16.3f}",flush=True)
