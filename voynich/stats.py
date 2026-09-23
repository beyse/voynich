"""Basic statistical measures for comparing Voynichese with natural-language texts."""
import math, re
from collections import Counter

def clean_gutenberg(path: str) -> str:
    t = open(path, encoding='utf-8', errors='replace').read()
    m = re.search(r'\*\*\* START OF [^\n]*\*\*\*', t)
    if m: t = t[m.end():]
    m = re.search(r'\*\*\* END OF [^\n]*\*\*\*', t)
    if m: t = t[:m.start()]
    return t

def tokenize_natural(t: str):
    t = t.lower()
    # keep letters incl. umlauts/accents, drop digits and punctuation
    return re.findall(r"[^\W\d_]+", t)

def entropy(counter: Counter) -> float:
    n = sum(counter.values())
    return -sum(c/n*math.log2(c/n) for c in counter.values())

def char_entropies(words, include_space=True):
    """h0 (log2 alphabet), h1 (unigram), h2 (conditional bigram) over the character stream."""
    sep = ' ' if include_space else ''
    s = sep.join(words)
    uni = Counter(s)
    bi = Counter(zip(s, s[1:]))
    h0 = math.log2(len(uni))
    h1 = entropy(uni)
    n = sum(bi.values())
    # H(X2|X1) = H(X1,X2) - H(X1)
    h12 = -sum(c/n*math.log2(c/n) for c in bi.values())
    h1_first = entropy(Counter(s[:-1]))
    h2 = h12 - h1_first
    return h0, h1, h2, len(uni)

def word_stats(words):
    c = Counter(words)
    n = len(words); v = len(c)
    lens = Counter(len(w) for w in words)
    mean_len = sum(len(w) for w in words)/n
    hapax = sum(1 for w,k in c.items() if k==1)
    return dict(tokens=n, types=v, ttr=v/n, hapax_frac=hapax/v, mean_len=mean_len,
                word_entropy=entropy(c), top=c.most_common(15), lens=lens)

def zipf_slope(words, top=200):
    c = Counter(words)
    freqs = sorted(c.values(), reverse=True)[:top]
    xs = [math.log(i+1) for i in range(len(freqs))]
    ys = [math.log(f) for f in freqs]
    n = len(xs); mx = sum(xs)/n; my = sum(ys)/n
    sxx = sum((x-mx)**2 for x in xs); sxy = sum((x-mx)*(y-my) for x,y in zip(xs,ys))
    return sxy/sxx

def summarize(name, words):
    h0,h1,h2,alpha = char_entropies(words)
    ws = word_stats(words)
    z = zipf_slope(words)
    return dict(name=name, alphabet=alpha, h0=h0, h1=h1, h2=h2, zipf=z, **ws)

def fmt_row(d):
    return (f"{d['name']:<22}{d['tokens']:>8}{d['types']:>7}{d['ttr']:>7.3f}{d['hapax_frac']:>7.2f}"
            f"{d['mean_len']:>7.2f}{d['alphabet']:>6}{d['h1']:>7.2f}{d['h2']:>7.2f}{d['zipf']:>7.2f}")

HEADER = f"{'corpus':<22}{'tokens':>8}{'types':>7}{'TTR':>7}{'hapax':>7}{'wlen':>7}{'alph':>6}{'h1':>7}{'h2':>7}{'zipf':>7}"
