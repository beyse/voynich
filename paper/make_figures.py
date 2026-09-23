"""Regenerate all paper figures directly from data (no numbers copied by hand). Output: paper/figures/fig*.png"""
import sys, json, math, random, re
sys.path.insert(0,'.')
import numpy as np, matplotlib
matplotlib.use('Agg'); import matplotlib.pyplot as plt
from collections import Counter, defaultdict
from voynich.ivtff import parse
from voynich.stats import clean_gutenberg, tokenize_natural, char_entropies
plt.rcParams.update({'font.size':8,'axes.titlesize':9,'axes.labelsize':8.5,'legend.fontsize':7.5,'figure.dpi':110})
OUT='paper/figures/'
ok=lambda w: w and '?' not in w and '*' not in w
L=parse('data/ZL3b-n.txt',comma_is_space=False)
V=[w for ln in L if ln.kind=='P' for w in ln.words if ok(w)]
refs={}
for name,path in [('German','data/ref/de_faust.txt'),('Italian','data/ref/it_dante.txt')]:
    refs[name]=tokenize_natural(clean_gutenberg(path))[:35000]
refs['Latin']=tokenize_natural(open('data/ref/la_caesar.txt').read())[:35000]
refs['Hebrew']=re.findall(r'[א-ת]+',open('data/ref/he_genesis.txt',encoding='utf-8').read())
COL={'Voynich':'#b2182b','Latin':'#2166ac','Italian':'#4393c3','German':'#5aae61','Hebrew':'#762a83','twin':'#999999'}

# ---------- Figure 1: BPE curve h2/h1 vs merges
def bpe_curve(words, merges=80, report=(0,5,10,15,20,25,30,40,50,60,80)):
    seqs=Counter(tuple(w) for w in words); res=[]
    for step in range(merges+1):
        if step in report:
            units={u for w in seqs for u in w}; uid={u:chr(0xE000+i) for i,u in enumerate(sorted(units))}
            ws=[''.join(uid[u] for u in w) for w,c in seqs.items() for _ in range(c)]
            h0,h1,h2,a=char_entropies(ws); res.append((step,a,h1,h2))
        pairs=Counter()
        for w,c in seqs.items():
            for i in range(len(w)-1): pairs[(w[i],w[i+1])]+=c
        if not pairs: break
        (a,b),_=pairs.most_common(1)[0]; new=Counter()
        for w,c in seqs.items():
            out=[]; i=0
            while i<len(w):
                if i<len(w)-1 and w[i]==a and w[i+1]==b: out.append(a+b); i+=2
                else: out.append(w[i]); i+=1
            new[tuple(out)]+=c
        seqs=new
    return res
fig,ax=plt.subplots(figsize=(3.4,2.6))
for name,words in [('Voynich',V)]+list(refs.items()):
    r=bpe_curve(words); ax.plot([x[1] for x in r],[x[3]/x[2] for x in r],'-o',ms=3,color=COL[name],label=name)
ax.set_xlabel('units in inventory after merges'); ax.set_ylabel('h2 / h1'); ax.set_ylim(0.5,0.9); ax.legend(frameon=False); ax.grid(alpha=.3)
fig.tight_layout(); fig.savefig(OUT+'fig1_bpe.png',dpi=300); plt.close(fig)
print('fig1 done',flush=True)

# ---------- Figure 2: entropy profile real vs order-3 twin (Voynich, Latin)
def cond_entropy(strings,k):
    ctx=Counter(); joint=Counter()
    for s in strings:
        t='^'*k+s+'$'
        for i in range(k,len(t)): joint[t[i-k:i+1]]+=1; ctx[t[i-k:i]]+=1
    n=sum(joint.values()); return -sum(c/n*math.log2(c/ctx[j[:-1]]) for j,c in joint.items())
def fit(strings,k):
    m=defaultdict(Counter)
    for s in strings:
        t='^'*k+s+'$'
        for i in range(k,len(t)): m[t[i-k:i]][t[i]]+=1
    return m
def sample(model,k,lengths,rng):
    out=[]
    for Ln in lengths:
        t='^'*k; s=''
        while True:
            c=model.get(t[-k:])
            if not c: break
            syms=list(c); w=[c[x] for x in syms]
            if len(s)<Ln*0.5 and len(syms)>1: w=[0 if x=='$' else v for x,v in zip(syms,w)]
            x=rng.choices(syms,w)[0]
            if x=='$': break
            s+=x; t+=x
            if len(s)>=Ln: break
        out.append(s)
    return out
vl=[' '.join(w for w in ln.words if ok(w)) for ln in L if ln.kind=='P']; vl=[l for l in vl if len(l)>=8]
lens=[len(l.split()) for l in vl]
def chunk(words):
    rng=random.Random(2); out=[]; i=0
    while i<len(words)-12:
        k=rng.choice(lens); out.append(' '.join(words[i:i+k])); i+=k
    return out
K=[1,2,3,4,5]
fig,axes=plt.subplots(1,2,figsize=(6.8,2.6),sharey=False)
for ax,(name,strings) in zip(axes,[('Voynich',vl),('Latin',chunk(refs['Latin']))]):
    h=[cond_entropy(strings,k) for k in K]; ax.plot(K,h,'-o',ms=3,color=COL[name],label=name+' (real)')
    for order,ls in [(1,':'),(2,'--'),(3,'-')]:
        tw=sample(fit(strings,order),order,[len(s) for s in strings],random.Random(order))
        ax.plot(K,[cond_entropy(tw,k) for k in K],ls,color=COL['twin'],label=f'order-{order} twin')
    ax.set_xlabel('context length k (glyphs)'); ax.set_ylabel('H(x | k previous) [bit]'); ax.set_title(name); ax.legend(frameon=False); ax.grid(alpha=.3)
fig.tight_layout(); fig.savefig(OUT+'fig2_entropy_profile.png',dpi=300); plt.close(fig)
print('fig2 done',flush=True)

# ---------- Figure 3: edge vs token MI (within-line shuffle null) for Voynich (all, A, B) and languages
def mi(pairs):
    pa=Counter(a for a,b in pairs); pb=Counter(b for a,b in pairs); pab=Counter(pairs); n=len(pairs)
    return sum(c/n*math.log2((c/n)/((pa[a]/n)*(pb[b]/n))) for (a,b),c in pab.items())
def excess_line(inner,f,reps=6):
    adj=lambda segs:[f(s[i],s[i+1]) for s in segs for i in range(len(s)-1)]
    obs=mi(adj(inner)); base=0
    for r in range(reps):
        rng=random.Random(r); base+=mi(adj([rng.sample(s,len(s)) for s in inner]))/reps
    return obs-base
def inner_of(lines): return [l[1:-1] for l in lines if len(l)>=5]
lines_all=[[w for w in ln.words if ok(w)] for ln in L if ln.kind=='P']
sets=[('Voynich',lines_all)]
for lang in 'AB': sets.append((f'Voynich {lang}',[[w for w in ln.words if ok(w)] for ln in L if ln.kind=='P' and ln.lang==lang]))
lens_w=[len(l) for l in lines_all if len(l)>=2]
def chunk_lines(words):
    rng=random.Random(2); out=[]; i=0
    while i<len(words)-12:
        k=rng.choice(lens_w); out.append(words[i:i+k]); i+=k
    return out
for name,w in refs.items(): sets.append((name,chunk_lines(w)))
labels=[]; edge=[]; tok=[]
for name,lines in sets:
    inner=inner_of(lines); labels.append(name); edge.append(excess_line(inner,lambda a,b:(a[-1],b[0]))); tok.append(excess_line(inner,lambda a,b:(a,b)))
fig,ax=plt.subplots(figsize=(4.8,2.7)); x=np.arange(len(labels)); wdt=0.38
ax.bar(x-wdt/2,edge,wdt,label='last glyph → first glyph',color='#b2182b'); ax.bar(x+wdt/2,tok,wdt,label='token → token',color='#2166ac')
ax.set_xticks(x); ax.set_xticklabels(labels,rotation=25,ha='right'); ax.set_ylabel('excess MI [bit]'); ax.legend(frameon=False); ax.grid(axis='y',alpha=.3)
fig.tight_layout(); fig.savefig(OUT+'fig3_edge_vs_token.png',dpi=300); plt.close(fig)
json.dump({'labels':labels,'edge':edge,'token':tok},open(OUT+'fig3_data.json','w'),indent=1)
print('fig3 done',flush=True)

# ---------- Figure 4: MI between words of consecutive lines by position pair (Voynich vs Latin, Italian)
def excess_b(pairs,reps=6):
    obs=mi(pairs); base=0
    for r in range(reps):
        bs=[b for a,b in pairs]; random.Random(r).shuffle(bs); base+=mi(list(zip([a for a,b in pairs],bs)))/reps
    return obs-base
pages=defaultdict(list)
for ln in L:
    if ln.kind!='P': continue
    ws=[w for w in ln.words if ok(w)]
    if len(ws)>=4: pages[ln.page].append(ws)
shape=[[len(l) for l in pg] for pg in pages.values()]
def chunk_pages(words):
    out={}; i=0
    for p,pg in enumerate(shape):
        npg=[]
        for k in pg:
            if i+k>len(words): break
            npg.append(words[i:i+k]); i+=k
        if npg: out[p]=npg
    return out
combos=['mid→mid','last→first','mid→first','last→mid','first→first','last→last']
def combo_mi(pgs):
    rng=random.Random(0); C={k:[] for k in combos}
    for ls in pgs.values():
        for k in range(len(ls)-1):
            a=ls[k]; b=ls[k+1]; ma=rng.choice(a[2:-2]) if len(a)>4 else a[2]; mb=rng.choice(b[2:-2]) if len(b)>4 else b[2]
            C['mid→mid'].append((ma,mb)); C['last→first'].append((a[-1],b[0])); C['mid→first'].append((ma,b[0])); C['last→mid'].append((a[-1],mb)); C['first→first'].append((a[0],b[0])); C['last→last'].append((a[-1],b[-1]))
    return [excess_b(C[k]) for k in combos]
fig,ax=plt.subplots(figsize=(4.6,2.6)); x=np.arange(len(combos)); wdt=0.27
for i,(name,pgs) in enumerate([('Voynich',pages),('Latin',chunk_pages(refs['Latin'])),('Italian',chunk_pages(refs['Italian']))]):
    ax.bar(x+(i-1)*wdt,combo_mi(pgs),wdt,label=name,color=COL[name])
ax.set_xticks(x); ax.set_xticklabels(combos,rotation=25,ha='right'); ax.set_ylabel('excess MI [bit]'); ax.legend(frameon=False); ax.grid(axis='y',alpha=.3)
fig.tight_layout(); fig.savefig(OUT+'fig4_linebreak.png',dpi=300); plt.close(fig)
print('fig4 done',flush=True)

# ---------- Figure 5: space predictability (info gain, k=1 and 2)
def space_gain(lines,k):
    rng=random.Random(0); ls=list(lines); rng.shuffle(ls); half=len(ls)//2
    def positions(line):
        s='#'*k+''.join(line)+'#'*k; b=set(); pos=k
        for w in line[:-1]: pos+=len(w); b.add(pos)
        for i in range(k+1,len(s)-k): yield (s[i-k:i],s[i:i+k]),(i in b)
    c=defaultdict(Counter)
    for l in ls[:half]:
        for ctx,b in positions(l): c[ctx][b]+=1
    tot=sum(sum(v.values()) for v in c.values()); prior=sum(v[True] for v in c.values())/tot; H=0;n=0
    for l in ls[half:]:
        for ctx,b in positions(l):
            cc=c.get(ctx,Counter()); p=(cc[True]+prior)/(sum(cc.values())+1.0); H+=-math.log2(p if b else 1-p); n+=1
    H0=-(prior*math.log2(prior)+(1-prior)*math.log2(1-prior)); return 1-H/n/H0
def rule_spaces(words,after='msty',minlen=3):
    s=''.join(words); out=[]; cur=''
    for ch in s:
        cur+=ch
        if ch in after and len(cur)>=minlen: out.append(cur); cur=''
    if cur: out.append(cur)
    return out
sp_sets=[('Voynich',[l for l in lines_all if len(l)>=2])]+[(n,chunk_lines(w)) for n,w in refs.items()]+[('Latin, rule-\nspaced',chunk_lines(rule_spaces(refs['Latin'])))]
fig,ax=plt.subplots(figsize=(4.2,2.5)); x=np.arange(len(sp_sets)); wdt=0.38
g1=[space_gain(l,1) for _,l in sp_sets]; g2=[space_gain(l,2) for _,l in sp_sets]
ax.bar(x-wdt/2,g1,wdt,label='1 glyph each side',color='#b2182b'); ax.bar(x+wdt/2,g2,wdt,label='2 glyphs each side',color='#ef8a62')
ax.set_xticks(x); ax.set_xticklabels([n for n,_ in sp_sets],rotation=25,ha='right'); ax.set_ylabel('information gain about boundaries'); ax.set_ylim(0,0.9); ax.legend(frameon=False); ax.grid(axis='y',alpha=.3)
fig.tight_layout(); fig.savefig(OUT+'fig5_spaces.png',dpi=300); plt.close(fig)
json.dump({'labels':[n for n,_ in sp_sets],'k1':g1,'k2':g2},open(OUT+'fig5_data.json','w'),indent=1)
print('fig5 done',flush=True)

# ---------- Figure 6: mechanism battery dot plot (from results JSON)
res=json.load(open('results/results_mechanisms_final.json'))+json.load(open('results/results_naibbe.json'))+json.load(open('results/results_naibbe_stateful.json'))
try: res+=json.load(open('results/results_hier.json'))
except Exception: pass
seen=set(); rows=[]
for r in res:
    if r['label'] in seen: continue
    seen.add(r['label']); rows.append(r)
metrics=[('edge_mi','edge MI'),('token_mi','token MI'),('break_mi','line-break MI'),('space_gain','space gain'),('hapax','hapax share'),('lex_synth','synth. attested'),('lzma_resid','residual (bit)'),('page_mi','I(word;page)')]
vms=[r for r in rows if r['label']=='VMS'][0]
fig,axes=plt.subplots(1,len(metrics),figsize=(10.5,4.4),sharey=True)
order=[r['label'] for r in rows]
for ax,(k,title) in zip(axes,metrics):
    for i,r in enumerate(rows):
        v=r.get(k,float('nan')); ax.plot(v,i,'o',color='#b2182b' if r['label']=='VMS' else ('#2166ac' if 'markov' in r['label'] or 'hier' in r['label'] else '#555'),ms=4)
    ax.axvline(vms.get(k,float('nan')),color='#b2182b',lw=0.8,alpha=.6); ax.set_title(title,fontsize=7.5); ax.grid(alpha=.3)
axes[0].set_yticks(range(len(rows))); axes[0].set_yticklabels(order,fontsize=7); axes[0].invert_yaxis()
fig.tight_layout(); fig.savefig(OUT+'fig6_battery.png',dpi=300); plt.close(fig)
print('fig6 done',flush=True)

# ---------- Figure 7: drift with folio distance (JSD), Voynich A/B vs section-drift twin vs Latin
def folio_num(p):
    m=re.match(r'f(\d+)([rv])',p); return int(m.group(1))*2+(m.group(2)=='v') if m else None
meta={ln.page:(ln.lang,ln.section) for ln in L if ln.kind=='P'}
def bigrams(lines,n,rng):
    s=' '.join(' '.join(l) for l in lines); st=rng.randrange(0,max(1,len(s)-n)); s=s[st:st+n]; return Counter(zip(s,s[1:]))
def jsd(c1,c2,alpha=0.05):
    keys=set(c1)|set(c2); n1=sum(c1.values())+alpha*len(keys); n2=sum(c2.values())+alpha*len(keys)
    p=[(c1[k]+alpha)/n1 for k in keys]; q=[(c2[k]+alpha)/n2 for k in keys]; m=[(a+b)/2 for a,b in zip(p,q)]
    return 0.5*sum(a*math.log2(a/mm) for a,mm in zip(p,m))+0.5*sum(b*math.log2(b/mm) for b,mm in zip(q,m))
from voynich.generators import markov_pages, pages as gpages
def drift_curve(pagedict,lang):
    rng=random.Random(0); items=[(folio_num(pg),meta[pg],ls) for pg,ls in pagedict.items() if folio_num(pg) and meta.get(pg,(None,))[0]==lang and len(' '.join(' '.join(l) for l in ls))>=450]
    items.sort(); bins=defaultdict(list); edges=[(1,2),(3,6),(7,14),(15,40),(41,999)]
    for i,(f,m,ls) in enumerate(items):
        for j in range(i+1,len(items)):
            f2,m2,ls2=items[j]
            if m2[1]!=m[1]: continue
            d=f2-f
            for lo,hi in edges:
                if lo<=d<=hi: bins[(lo,hi)].append(jsd(bigrams(ls,450,rng),bigrams(ls2,450,rng)))
    return [(f"{lo}–{hi if hi<999 else ''}",np.mean(bins[(lo,hi)])) for lo,hi in edges if bins[(lo,hi)]]
mk=dict(zip(gpages.keys(),markov_pages(3,True)))
fig,axes=plt.subplots(1,2,figsize=(6.8,2.6),sharey=True)
for ax,lang in zip(axes,'AB'):
    for name,pd,col,ls in [('Voynich',dict(gpages),COL['Voynich'],'-'),('section-drift twin',mk,COL['twin'],'--')]:
        c=drift_curve(pd,lang); ax.plot([x[0] for x in c],[x[1] for x in c],ls+'o',ms=3,color=col,label=name)
    ax.set_title(f'Currier {lang}'); ax.set_xlabel('folio distance (pages)'); ax.grid(alpha=.3)
axes[0].set_ylabel('JSD of glyph-bigram distributions'); axes[0].legend(frameon=False)
fig.tight_layout(); fig.savefig(OUT+'fig7_drift.png',dpi=300); plt.close(fig)
print('fig7 done',flush=True)

# ---------- Figure 8: text vs image Mantel (Herbal-A): null histogram + positive control
exec(open('scripts/scripts_text_vs_image.py').read().split("herbalA=[p for p in pages")[0].replace("L=parse('data/ZL3b-n.txt',comma_is_space=False)","L=parse('data/ZL3b-n.txt',comma_is_space=False)"))
herbalA=[p for p in pages if meta[p]==('A','H','1') and folio(p)<=116 and p in feats and len(pages[p])>=40]
ps=herbalA; F=np.array([folio(p) for p in ps]); FD=np.abs(F[:,None]-F[None,:]); mask=FD>=6
I=image_matrix(ps); W=word_dist(ps)
iu=np.triu_indices(len(ps),1); m=mask[iu]
def sp(x,y):
    rx=np.argsort(np.argsort(x)); ry=np.argsort(np.argsort(y)); return np.corrcoef(rx,ry)[0,1]
obs=sp(W[iu][m],I[iu][m]); rng=np.random.default_rng(0); null=[]
for _ in range(3000):
    perm=rng.permutation(len(ps)); Ip=I[perm][:,perm]; null.append(sp(W[iu][m],Ip[iu][m]))
ks=[0,2,5,10,20]; rs=[]; rr=random.Random(0)
for k in ks:
    extra={}
    for p in ps:
        f=feats[p]; toks=['BLUE' if f['blue_frac']>0.05 else 'NOBLUE','BIGLEAF' if f['green']>0.06 else 'SMALLLEAF','ROOTS' if f['red_frac']>0.4 else 'FEWROOTS','TOP' if f['green_y']<0.45 else 'LOW']
        extra[p]=Counter(rr.choices(toks,k=k)) if k else Counter()
    Wk=word_dist(ps,extra); rs.append(sp(Wk[iu][m],I[iu][m]))
fig,axes=plt.subplots(1,2,figsize=(6.8,2.6))
axes[0].hist(null,bins=40,color='#bbb'); axes[0].axvline(obs,color='#b2182b',lw=1.5,label=f'observed r = {obs:+.3f}'); axes[0].set_xlabel('Mantel r under permutation null'); axes[0].set_ylabel('count'); axes[0].legend(frameon=False); axes[0].set_title('Herbal-A, hand 1: words vs image')
axes[1].plot(ks,rs,'-o',ms=3,color='#2166ac'); axes[1].axhline(np.percentile(null,95),color='#999',ls='--',lw=0.8,label='95th percentile of null'); axes[1].set_xlabel('image-determined tokens added per page'); axes[1].set_ylabel('Mantel r'); axes[1].set_title('sensitivity (synthetic description)'); axes[1].legend(frameon=False); axes[1].grid(alpha=.3)
fig.tight_layout(); fig.savefig(OUT+'fig8_mantel.png',dpi=300); plt.close(fig)
json.dump({'obs':obs,'null_p95':float(np.percentile(null,95)),'null_sd':float(np.std(null)),'ks':ks,'rs':rs,'n_pages':len(ps)},open(OUT+'fig8_data.json','w'),indent=1)
print('fig8 done',flush=True)
