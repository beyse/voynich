import sys, random
sys.path.insert(0, '.')
from voynich.ivtff import parse, words_of
from voynich.stats import *

L = parse('data/ZL3b-n.txt')
vms_all = words_of(L, kind='P')
vms_A = words_of(L, kind='P', lang='A')
vms_B = words_of(L, kind='P', lang='B')
labels = words_of(L, kind='L')

refs = {}
for name, path in [('de_faust','data/ref/de_faust.txt'), ('it_dante','data/ref/it_dante.txt'),
                   ('en_tolstoy','data/ref/en_war_and_peace.txt'), ('la_caesar','data/ref/la_caesar.txt')]:
    t = clean_gutenberg(path) if 'la_' not in name else open(path).read()
    refs[name] = tokenize_natural(t)

N = len(vms_all)
random.seed(1)
print(HEADER)
print(fmt_row(summarize('VMS all (P)', vms_all)))
print(fmt_row(summarize('VMS Currier A', vms_A)))
print(fmt_row(summarize('VMS Currier B', vms_B)))
print(fmt_row(summarize('VMS labels', labels)))
for k, w in refs.items():
    # same size sample as VMS, contiguous chunk, to make TTR/hapax comparable
    start = random.randrange(0, max(1, len(w)-N))
    print(fmt_row(summarize(k+' (chunk)', w[start:start+N])))
print()
print('Top words VMS:', word_stats(vms_all)['top'])
print('Top words A  :', word_stats(vms_A)['top'][:10])
print('Top words B  :', word_stats(vms_B)['top'][:10])
print()
print('Word length distribution (VMS vs Latin chunk):')
lv = word_stats(vms_all)['lens']; ll = word_stats(refs['la_caesar'][:N])['lens']
for i in range(1, 15):
    print(f"{i:>3} {lv.get(i,0)/N:>7.3f} {ll.get(i,0)/N:>7.3f}")
