"""Single source of truth for every number in the paper: parse the analysis logs and result JSONs into paper/numbers.json."""
import re, json, sys, os
sys.path.insert(0,'.')
LOG='results/logs/'
def read(name): return open(LOG+name+'.txt').read()
N={}
# ---- basic stats table
rows={}
for line in read('basic_stats').splitlines():
    m=re.match(r'^(VMS all \(P\)|VMS Currier A|VMS Currier B|VMS labels|de_faust \(chunk\)|it_dante \(chunk\)|en_tolstoy \(chunk\)|la_caesar \(chunk\))\s+(\d+)\s+(\d+)\s+([\d.]+)\s+([\d.]+)\s+([\d.]+)\s+(\d+)\s+([\d.]+)\s+([\d.]+)\s+(-?[\d.]+)',line)
    if m: rows[m.group(1)]=dict(tokens=int(m.group(2)),types=int(m.group(3)),ttr=float(m.group(4)),hapax=float(m.group(5)),wlen=float(m.group(6)),alph=int(m.group(7)),h1=float(m.group(8)),h2=float(m.group(9)),zipf=float(m.group(10)))
N['basic']=rows
# Hebrew basic stats computed directly
from voynich.stats import summarize
he=re.findall(r'[א-ת]+',open('data/ref/he_genesis.txt',encoding='utf-8').read()); d=summarize('he',he)
N['basic']['he_genesis']=dict(tokens=d['tokens'],types=d['types'],ttr=d['ttr'],hapax=d['hapax_frac'],wlen=d['mean_len'],alph=d['alphabet'],h1=d['h1'],h2=d['h2'],zipf=d['zipf'])
# ---- BPE curves
bpe={}; cur=None
for line in read('bpe').splitlines():
    m=re.match(r'^== (\w+)',line)
    if m: cur=m.group(1); bpe[cur]=[]; continue
    m=re.match(r'^\s*(\d+)\s+(\d+)\s+([\d.]+)\s+([\d.]+)\s+([\d.]+)\s+([\d.]+)',line)
    if m and cur: bpe[cur].append(dict(merges=int(m.group(1)),units=int(m.group(2)),h1=float(m.group(3)),h2=float(m.group(4)),ratio=float(m.group(5)),upw=float(m.group(6))))
N['bpe']=bpe
# ---- boundary projections
proj={}
for line in read('boundary').splitlines():
    m=re.match(r'^(VMS[AB]? c=(?:jn|sp)|Latin|Italian|German|Hebrew)\s+word=\s*(-?[\d.]+) last1\|first1=\s*(-?[\d.]+) last2\|first2=\s*(-?[\d.]+) last1\|word_b=\s*(-?[\d.]+) word_a\|first1=\s*(-?[\d.]+) last2\|word_b=\s*(-?[\d.]+) word_a\|first2=\s*(-?[\d.]+) len_a\|len_b=\s*(-?[\d.]+)',line)
    if m: proj[m.group(1)]=dict(word=float(m.group(2)),l1f1=float(m.group(3)),l2f2=float(m.group(4)),l1w=float(m.group(5)),wf1=float(m.group(6)),l2w=float(m.group(7)),wf2=float(m.group(8)),len=float(m.group(9)))
N['proj']=proj
b=read('boundary'); m=re.search(r'ED=0:\s*(-?[\d.]+) ED=1:\s*(-?[\d.]+) ED=2:\s*(-?[\d.]+) ED>=3:\s*(-?[\d.]+)',b)
N['ed_buckets_withinline']=dict(ed0=float(m.group(1)),ed1=float(m.group(2)),ed2=float(m.group(3)),ed3=float(m.group(4)))
m=re.search(r'same line ([\d.]+), same page ([\d.]+), same language ([\d.]+)',b); N['psim']=dict(line=float(m.group(1)),page=float(m.group(2)),lang=float(m.group(3)))
# pmi by ED with global null
pm={}
for line in read('pmi_similarity').splitlines():
    m=re.match(r'^(VMS raw|VMS light|VMS heavy|VMS-A light|VMS-B light|Latin|Latin stem4|Italian|German)\s+total excess=\s*(-?[\d.]+) \| ED=0:\s*(-?[\d.]+) ED=1:\s*(-?[\d.]+) ED=2:\s*(-?[\d.]+) ED>=3:\s*(-?[\d.]+)',line)
    if m: pm[m.group(1)]=dict(total=float(m.group(2)),ed0=float(m.group(3)),ed1=float(m.group(4)),ed2=float(m.group(5)),ed3=float(m.group(6)))
N['pmi_global']=pm
# ---- line unit (subsampled)
lu={}
for src in ('lineunit','lineunit_nat'):
    for line in read(src).splitlines():
        m=re.match(r'^(VMS none|VMS light|VMS heavy|VMS-A light|VMS-B light|Latin|Latin stem4|Italian|German)\s+n=\s*(\d+) \| across=\s*(-?[\d.]+) \| within\(same n\)=\s*(-?[\d.]+)±([\d.]+) \| inner\(same n\)=\s*(-?[\d.]+)±([\d.]+) \| across-inner\(d3\)=\s*(-?[\d.]+) \| within d=3 \(same n\)=\s*(-?[\d.]+)±([\d.]+)',line)
        if m: lu[m.group(1)]=dict(n=int(m.group(2)),across=float(m.group(3)),within=float(m.group(4)),within_sd=float(m.group(5)),inner=float(m.group(6)),inner_sd=float(m.group(7)),across_d3=float(m.group(8)),within_d3=float(m.group(9)),within_d3_sd=float(m.group(10)))
N['lineunit']=lu
# ---- edges: I(word;page) by position and consecutive-line combos
ed={}; cur=None
for line in read('edges').splitlines():
    m=re.match(r'^(VMS raw|VMS light|Latin \(chunked\)|Italian \(chunked\)): I\(word;page\)',line)
    if m: cur=m.group(1); ed[cur]={'pos':{},'combo':{}}; continue
    m=re.match(r'^\s+(first|second|middle|penult|last)\s+I\(word;page\)=(-?[\d.]+)\s+types/n=([\d.]+)\s+H=([\d.]+)',line)
    if m and cur: ed[cur]['pos'][m.group(1)]=dict(mi=float(m.group(2)),ttr=float(m.group(3)),H=float(m.group(4))); continue
    m=re.match(r'^\s+(\S+ -> \S+)\s+n=\s*(\d+)\s+(-?[\d.]+)',line)
    if m and cur: ed[cur]['combo'][m.group(1)]=dict(n=int(m.group(2)),mi=float(m.group(3)))
N['edges']=ed
# ---- spaces
sp={}
for line in read('spaces').splitlines():
    m=re.match(r'^(VMS(?:-[AB])? c=(?:jn|sp)|Latin rule-spaced|Latin|Italian|German|Hebrew)\s+k=(\d)\s+boundary rate=([\d.]+)\s+H\(b\)=([\d.]+)\s+H\(b\|ctx\)=([\d.]+)\s+info gain=\s*([\d.]+)%\s+P=([\d.]+) R=([\d.]+) F1=([\d.]+)',line)
    if m: sp.setdefault(m.group(1),{})[int(m.group(2))]=dict(rate=float(m.group(3)),H=float(m.group(4)),Hc=float(m.group(5)),gain=float(m.group(6))/100,P=float(m.group(7)),R=float(m.group(8)),F1=float(m.group(9)))
N['spaces']=sp
# ---- lexicon
lx={}
for src in ('lexicon','lexicon_chunks'):
    for line in read(src).splitlines():
        m=re.match(r'^(.+?)\s+k=(\d)\s+bits/glyph: real=\s*([\d.]+) synth=\s*([\d.]+)\s+\| attested-in-train share: real tokens ([\d.]+), synth tokens ([\d.]+) \| types: real ([\d.]+), synth ([\d.]+) \| mean len real ([\d.]+) synth ([\d.]+)',line)
        if m: lx.setdefault(m.group(1).strip(),{})[int(m.group(2))]=dict(bits_real=float(m.group(3)),bits_synth=float(m.group(4)),tok_real=float(m.group(5)),tok_synth=float(m.group(6)),typ_real=float(m.group(7)),typ_synth=float(m.group(8)))
N['lexicon']=lx
# ---- entropy profiles
ep={}; cur=None
for line in read('entropy_rate').splitlines():
    m=re.match(r'^(VMS all|VMS A|VMS B|Latin rule-spaced|Latin|Italian|German|Hebrew)\s+h1=\s*([\d.]+) h2=\s*([\d.]+) h3=\s*([\d.]+) h4=\s*([\d.]+) h5=\s*([\d.]+)\s+lzma=\s*([\d.]+)',line)
    if m: cur=m.group(1); ep[cur]={'real':[float(m.group(i)) for i in range(2,7)],'lzma':float(m.group(7)),'twins':{}}; continue
    m=re.match(r'^\s+twin order-(\d)\s+h1=\s*([\d.]+) h2=\s*([\d.]+) h3=\s*([\d.]+) h4=\s*([\d.]+) h5=\s*([\d.]+)\s+lzma=\s*([\d.]+)',line)
    if m and cur: ep[cur]['twins'][int(m.group(1))]={'h':[float(m.group(i)) for i in range(2,7)],'lzma':float(m.group(7))}
N['entropy']=ep
# ---- agreement
ag={}
for line in read('agreement').splitlines():
    m=re.match(r'^(VMS[AB]? comma=(?:space|join)|Latin|Italian|German|Hebrew)\s+n=\s*(\d+)\s+(.*)$',line)
    if m:
        d={}
        for k,a,b,r in re.findall(r'(\w+): ([\d.]+)/([\d.]+)=\s*([\d.]+)',m.group(3)): d[k]=dict(obs=float(a),null=float(b),ratio=float(r))
        ag[m.group(1).strip()]=dict(n=int(m.group(2)),**d)
N['agreement']=ag
m=re.search(r"uncertain spaces ',' in file: (\d+) vs certain '\.': (\d+)",read('agreement')); N['comma_counts']=dict(comma=int(m.group(1)),dot=int(m.group(2)))
# ---- direction
dr=read('direction'); m=re.search(r'== VMS all: (\d+) adjacent inner pairs with ED=1',dr); N['direction']={'n_all':int(m.group(1))}
m=re.search(r'share of ED=1 pairs in strongly directional edits: ([\d.]+)',dr); N['direction']['share_directional']=float(m.group(1))
N['direction']['top']=re.findall(r'^(\w+ \S+ @\w+)\s+(\d+)\s+(\d+)\s+(-?[\d.]+)$',dr.split('== VMS A')[0],flags=re.M)
# ---- vertical
vt={}
for line in read('vertical').splitlines():
    m=re.match(r'^(prev word|word above \(i-1\.\.i\+1, min\)|word above \(same index\)|random same page|random same lang|2 lines above \(same index\)|min over 3 random same page)\s+(\d+)\s+([\d.]+)\s+([\d.]+)\s+([\d.]+)\s+([\d.]+)',line)
    if m: vt[m.group(1)]=dict(n=int(m.group(2)),meanED=float(m.group(3)),p0=float(m.group(4)),p1=float(m.group(5)),p2=float(m.group(6)))
N['vertical']=vt
# ---- selfcitation: immediate repeats
sc=read('selfcitation'); m=re.search(r'immediate exact repeats in VMS: (\d+)/(\d+) = ([\d.]+)',sc); N['repeats']={'vms':float(m.group(3)),'vms_n':int(m.group(2))}
for lang in ('de_faust','la_caesar','it_dante'):
    m=re.search(lang+r': (\d+)/(\d+) = ([\d.]+)',sc); N['repeats'][lang]=float(m.group(3))
# ---- mechanisms (JSON)
mech={}
for f in ('results_mechanisms_final','results_naibbe','results_naibbe_stateful','results_hier'):
    for r in json.load(open(f'results/{f}.json')): mech.setdefault(r['label'],r)
N['mech']=mech
# ---- oos / robustness
oo=read('oos'); rb={}
for line in oo.splitlines():
    m=re.match(r'^\s+order (\d): lzma real ([\d.]+) twin ([\d.]+) residual ([+-][\d.]+); h\(3\) residual ([+-][\d.]+)',line)
    if m: rb[f'oos_order{m.group(1)}']=dict(real=float(m.group(2)),twin=float(m.group(3)),resid=float(m.group(4)),h3=float(m.group(5)))
    m=re.match(r'^\s+order 3 reversed split: residual ([+-][\d.]+); h\(3\) residual ([+-][\d.]+)',line)
    if m: rb['oos_reversed']=dict(resid=float(m.group(1)),h3=float(m.group(2)))
    m=re.match(r'^(held-out real \(even pages\)|twin from odd-page model|hand \d \(\d+ pages\)|Currier [AB])\s+(-?[\d.]+)\s+(-?[\d.]+)\s+(-?[\d.]+)\s+([\d.]+)%\s+([\d.]+)\s+(-?[\d.]+)\s+([\d.]+)\s+([\d.]+)\s+([\d.]+)\s+([\d.]+)\s+([\d.]+)',line)
    if m: rb[m.group(1)]=dict(edge=float(m.group(2)),token=float(m.group(3)),brk=float(m.group(4)),space=float(m.group(5))/100,hapax=float(m.group(6)),zipf=float(m.group(7)),lex_real=float(m.group(8)),lex_synth=float(m.group(9)),h2=float(m.group(10)),h4=float(m.group(11)),page=float(m.group(12)))
N['robust']=rb
tk={}
for line in read('takahashi').splitlines():
    m=re.match(r'^(ZL3b|IT2a) c=(jn|sp)\s+(\d+)\s+(\d+)\s+(-?[\d.]+)\s+(-?[\d.]+)\s+(-?[\d.]+)\s+(-?[\d.]+)\s+([\d.]+)%\s+([\d.]+)\s+(-?[\d.]+)\s+([\d.]+)\s+([\d.]+)\s+([\d.]+)\s+([\d.]+)\s+([\d.]+)\s+([+-][\d.]+)\s+([\d.]+)',line)
    if m: tk[f'{m.group(1)} {m.group(2)}']=dict(tokens=int(m.group(3)),types=int(m.group(4)),edge=float(m.group(5)),token=float(m.group(6)),adj=float(m.group(7)),brk=float(m.group(8)),space=float(m.group(9))/100,hapax=float(m.group(10)),zipf=float(m.group(11)),wlen=float(m.group(12)),lex_real=float(m.group(13)),lex_synth=float(m.group(14)),h2=float(m.group(15)),h4=float(m.group(16)),resid=float(m.group(17)),page=float(m.group(18)))
N['transcriptions']=tk
# ---- drift
dft={}
for line in read('drift').splitlines():
    m=re.match(r'^(VMS|markov3\+drift|markov4\+drift|latin \(chunk\))\s+lang ([AB]) \((\d+) pages\): (.*)$',line)
    if m:
        d={k.strip():float(v) for k,v in re.findall(r'([^:]+?): ([\d.]+) \(n=\d+\)\s*',m.group(4))}
        dft[f'{m.group(1)} {m.group(2)}']=dict(pages=int(m.group(3)),**d)
N['drift']=dft
hv={}
for line in read('hand_vs_section').splitlines():
    m=re.match(r'^\s+lang ([AB]): (same sect|diff sect)\s+(same hand|diff hand)\s+([\d.]+) \(n=(\d+)\)',line)
    if m: hv[f'{m.group(1)} {m.group(2)} {m.group(3)}']=dict(jsd=float(m.group(4)),n=int(m.group(5)))
N['hand_vs_section']=hv
hd={}; cur=None
for line in read('hand_by_distance').splitlines():
    m=re.match(r'^([AB]-[HS]): (\d+) pages; hands Counter\((.*)\); folios (\d+)-(\d+)',line)
    if m: cur=m.group(1); hd[cur]={'pages':int(m.group(2)),'hands':m.group(3),'bins':{}}; continue
    m=re.match(r'^\s+(d<=6|d<=20|d>20)\s+(same hand|diff hand)\s+([\d.]+) \(n=(\d+) pairs\)',line)
    if m and cur: hd[cur]['bins'][f'{m.group(1)} {m.group(2)}']=dict(jsd=float(m.group(3)),n=int(m.group(4)))
m=re.search(r'hand 2 vs hand 3: (\[.*\])',read('hand_by_distance')); hd['bigrams_2_over_3']=m.group(1) if m else ''
m=re.search(r'hand 3 vs hand 2: (\[.*\])',read('hand_by_distance')); hd['bigrams_3_over_2']=m.group(1) if m else ''
N['hand_by_distance']=hd
# ---- labels
lb={}
for line in read('zodiac_labels').splitlines():
    m=re.match(r'^(\w+)\s+pages=\s*(\d+) label tokens=\s*(\d+) types=\s*(\d+)\s+recurrence across pages: ([\d.]+)\s+null \(text words of same pages/section\): ([\d.]+)',line)
    if m: lb[m.group(1)]=dict(pages=int(m.group(2)),tokens=int(m.group(3)),types=int(m.group(4)),rec=float(m.group(5)),null=float(m.group(6)))
m=re.search(r'zodiac labels on >=2 sign pages: (\[.*\])',read('zodiac_labels')); N['labels']={'table':lb,'zodiac_multi':m.group(1)}
lab=read('labels'); m=re.search(r"label first glyph overall: \[\('o', (\d+)\)",lab); m2=re.search(r'labels total: (\d+) distinct: (\d+)',lab)
N['labels']['o_initial']=int(m.group(1)) if m else None; N['labels']['total_L_only']=int(m2.group(1)) if m2 else None
from voynich.ivtff import parse as _parse
_L=_parse('data/ZL3b-n.txt',comma_is_space=False); _ok=lambda w: w and '?' not in w and '*' not in w
_zp={}
for _ln in _L:
    if _ln.kind=='L' and _ln.section=='Z':
        for _w in _ln.words:
            if _ok(_w): _zp.setdefault(_w,set()).add(_ln.page)
_cnt=[len(v) for v in _zp.values()]
N['labels']['zodiac_types']=len(_zp); N['labels']['zodiac_multi_n']=sum(1 for c in _cnt if c>=2); N['labels']['zodiac_multi_max']=max(_cnt); N['labels']['zodiac_pages']=len({p for v in _zp.values() for p in v})
# ---- text vs image
tvi={}; t=read('text_vs_image'); cur=None
for line in t.splitlines():
    m=re.match(r'^(Herbal-A, hand 1|Herbal-B \(hands 2/3/5\)): (\d+) pages, (\d+) pairs',line)
    if m: cur=m.group(1); tvi[cur]=dict(pages=int(m.group(2)),pairs=int(m.group(3))); continue
    if not cur: continue
    m=re.match(r'^\s+text\(words\) vs image: r=([+-][\d.]+) \(p=([\d.]+), null sd ([\d.]+)\) \| all pairs r=([+-][\d.]+) \(p=([\d.]+)\) \| text vs folio distance r=([+-][\d.]+) \(p=([\d.]+)\)',line)
    if m: tvi[cur].update(r_w=float(m.group(1)),p_w=float(m.group(2)),sd=float(m.group(3)),r_w_all=float(m.group(4)),p_w_all=float(m.group(5)),r_fol=float(m.group(6)),p_fol=float(m.group(7))); continue
    m=re.match(r'^\s+text\(glyph bigrams\) vs image: r=([+-][\d.]+) \(p=([\d.]+)',line)
    if m: tvi[cur].update(r_b=float(m.group(1)),p_b=float(m.group(2))); continue
    m=re.match(r'^\s+image vs folio distance: r=([+-][\d.]+) \(p=([\d.]+)\)',line)
    if m: tvi[cur].update(r_img_fol=float(m.group(1)),p_img_fol=float(m.group(2))); cur=None
tvi['positive_control']={int(k):dict(r=float(r),p=float(p)) for k,r,p in re.findall(r'k=\s*(\d+) description tokens per page \(of ~\d+ words\): r=([+-][\d.]+) \(p=([\d.]+)\)',t)}
m=re.search(r'\(of ~(\d+) words\)',t); tvi['mean_words']=int(m.group(1))
t2=read('text_vs_image2')
for key,pat in [('B_strat_w',r'permutation within hand: text\(words\) vs image r=([+-][\d.]+) p=([\d.]+)'),('B_strat_b',r'permutation within hand: text\(glyph bigrams\) vs image r=([+-][\d.]+) p=([\d.]+)'),('B_same_w',r'same-hand pairs only, within-hand permutation: text\(words\) vs image r=([+-][\d.]+) p=([\d.]+)'),('B_h2_w',r'hand 2 only \((\d+) pages\): text\(words\) vs image r=([+-][\d.]+) p=([\d.]+)'),('B_h2_b',r'hand 2 only \(\d+ pages\): text\(glyph bigrams\) vs image r=([+-][\d.]+) p=([\d.]+)'),('A_10000_w',r'Herbal-A \((\d+) pages, 10000 perms\): text\(words\) vs image r=([+-][\d.]+) p=([\d.]+)'),('A_10000_b',r'Herbal-A \(\d+ pages, 10000 perms\): text\(glyph bigrams\) vs image r=([+-][\d.]+) p=([\d.]+)')]:
    m=re.search(pat,t2); g=m.groups(); tvi[key]=dict(r=float(g[-2]),p=float(g[-1]),n=int(g[0]) if len(g)==3 else None)
tvi['features']={k:dict(r=float(r),p=float(p)) for k,r,p in re.findall(r'feature (\w+)\s+r=([+-][\d.]+) p=([\d.]+)',t2)}
N['text_vs_image']=tvi
# ---- section within hand
sw={}; cur=None
for line in read('section_within_hand').splitlines():
    m=re.match(r'^hand (\d): (\{.*\}) pages; majority baseline ([\d.]+)',line)
    if m: cur=m.group(1); sw[cur]={'counts':m.group(2),'majority':float(m.group(3)),'rows':{}}; continue
    m=re.match(r'^\s+exclude \|folio diff\|<=\s*(\d+) folios: words ([\d.]+)\s+glyph-bigrams ([\d.]+)\s+nearest-folio-only ([\d.]+)\s+\(n=(\d+)\)',line)
    if m and cur: sw[cur]['rows'][int(m.group(1))]=dict(words=float(m.group(2)),bigrams=float(m.group(3)),folio=float(m.group(4)),n=int(m.group(5)))
N['section_within_hand']=sw
# ---- jackknife (if present) and figure data
if os.path.exists('results/jackknife.json'): N['jack']=json.load(open('results/jackknife.json'))
for f in ('fig3_data','fig5_data','fig8_data'): N[f]=json.load(open(f'paper/figures/{f}.json'))
# ---- corpus facts
from voynich.ivtff import parse
from collections import Counter
L=parse('data/ZL3b-n.txt',comma_is_space=False); ok=lambda w: w and '?' not in w and '*' not in w
N['corpus']=dict(lines_P=sum(1 for l in L if l.kind=='P'),pages_P=len({l.page for l in L if l.kind=='P'}),tokens_P=sum(1 for l in L if l.kind=='P' for w in l.words if ok(w)),
                 lines_total=len(L),pages_total=len({l.page for l in L}),labels_L=sum(1 for l in L if l.kind=='L' for w in l.words if ok(w)),
                 hands=dict(Counter(l.hand for l in L if l.kind=='P')),langs=dict(Counter(l.lang for l in L if l.kind=='P')),sections=dict(Counter(l.section for l in L if l.kind=='P')))
json.dump(N,open('paper/numbers.json','w'),indent=1,ensure_ascii=False)
print("keys:",list(N)); print("basic rows:",list(N['basic'])); print("proj rows:",list(N['proj'])); print("spaces:",list(N['spaces'])); print("lexicon:",list(N['lexicon'])); print("entropy:",list(N['entropy']))
print("mech:",list(N['mech'])); print("robust:",list(N['robust'])); print("tvi keys:",list(N['text_vs_image'])); print("corpus:",N['corpus'])
