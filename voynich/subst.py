"""Homophonic/monoalphabetic substitution solver with a character 4-gram LM.

Usage: python3 voynich/subst.py <lang> <refpath> [--raw]
Runs: (a) plaintext LM score, (b) solve a random homophonic encipherment of held-out plaintext,
(c) solve Voynichese (retokenised units), (d) solve a shuffled-character control with VMS unit stats.
Reports bits/char under the LM: lower = more language-like.
"""
import sys, math, random, re
import numpy as np
sys.path.insert(0, '.')
from voynich.ivtff import parse, words_of
from voynich.stats import clean_gutenberg, tokenize_natural

GROUPS = ['ch','sh','ckh','cth','cph','cfh','qo','eee','ee','iiin','iin','ain','aiin','ar','or','ol','al','dy','am','an','ir','ey']

def retok(words, groups):
    groups = sorted(groups, key=len, reverse=True)
    sym = {g: chr(0xE000+i) for i, g in enumerate(groups)}
    out = []
    for w in words:
        for g in groups: w = w.replace(g, sym[g])
        out.append(w)
    return out

class LM:
    def __init__(self, text_words, letters):
        self.letters = [' '] + letters
        self.idx = {c: i for i, c in enumerate(self.letters)}
        A = len(self.letters); self.A = A
        seq = self.encode(text_words)
        c4 = np.zeros((A,A,A,A)); c3 = np.zeros((A,A,A)); c2 = np.zeros((A,A)); c1 = np.zeros(A)
        np.add.at(c4, (seq[:-3], seq[1:-2], seq[2:-1], seq[3:]), 1)
        np.add.at(c3, (seq[:-2], seq[1:-1], seq[2:]), 1)
        np.add.at(c2, (seq[:-1], seq[1:]), 1)
        np.add.at(c1, seq, 1)
        p1 = (c1+0.5)/(c1.sum()+0.5*A)
        p2 = (c2+0.1)/(c2.sum(1, keepdims=True)+0.1*A)
        p3 = (c3+0.1)/(c3.sum(2, keepdims=True)+0.1*A)
        p4 = (c4+0.1)/(c4.sum(3, keepdims=True)+0.1*A)
        p = 0.5*p4 + 0.3*p3[None, :, :, :] + 0.15*p2[None, None, :, :] + 0.05*p1[None, None, None, :]
        self.logp = np.log2(p)
    def encode(self, words):
        s = ' ' + ' '.join(words) + ' '
        return np.array([self.idx[c] for c in s if c in self.idx])
    def bits_per_char(self, words):
        seq = self.encode(words)
        return -self.logp[seq[:-3], seq[1:-2], seq[2:-1], seq[3:]].mean()

class Cipher:
    """cipher text as unit-id sequence with space = 0"""
    def __init__(self, words):
        units = sorted({u for w in words for u in w})
        self.units = [' '] + units
        self.idx = {u: i for i, u in enumerate(self.units)}
        s = ' ' + ' '.join(words) + ' '
        self.seq = np.array([self.idx[c] for c in s])
        self.U = len(self.units)
        # 4-gram type counts for fast scoring
        keys = self.seq[:-3]*self.U**3 + self.seq[1:-2]*self.U**2 + self.seq[2:-1]*self.U + self.seq[3:]
        uk, cnt = np.unique(keys, return_counts=True)
        self.g = np.stack([uk//self.U**3 % self.U, uk//self.U**2 % self.U, uk//self.U % self.U, uk % self.U], 1)
        self.cnt = cnt.astype(float)
        self.n = len(keys)
        self.unit_freq = np.bincount(self.seq, minlength=self.U)

def solve(cipher, lm, iters=40000, restarts=6, seed=0):
    rng = random.Random(seed)
    A = lm.A; U = cipher.U
    best_score = -1e18; best_map = None
    for r in range(restarts):
        m = np.array([0] + [rng.randrange(1, A) for _ in range(U-1)])
        def score(m):
            return (cipher.cnt * lm.logp[m[cipher.g[:,0]], m[cipher.g[:,1]], m[cipher.g[:,2]], m[cipher.g[:,3]]]).sum()
        cur = score(m); T0 = 2000.0
        for it in range(iters):
            T = T0 * (1 - it/iters) + 1e-3
            u = rng.randrange(1, U); old = m[u]
            if rng.random() < 0.15:  # swap two units' letters
                v = rng.randrange(1, U); m[u], m[v] = m[v], m[u]
                new = score(m)
                if new >= cur or rng.random() < math.exp((new-cur)/T): cur = new
                else: m[u], m[v] = m[v], m[u]
            else:
                m[u] = rng.randrange(1, A)
                new = score(m)
                if new >= cur or rng.random() < math.exp((new-cur)/T): cur = new
                else: m[u] = old
        if cur > best_score: best_score, best_map = cur, m.copy()
    return best_map, -best_score/cipher.n

def decode(cipher, lm, m, words, k=40):
    out = []
    for w in words[:k]:
        out.append(''.join(lm.letters[m[cipher.idx[u]]] for u in w))
    return ' '.join(out)

def homophonic_encipher(words, letters, n_units, rng):
    # each plaintext letter gets >=1 cipher units; extra units distributed proportional to frequency
    from collections import Counter
    freq = Counter(c for w in words for c in w)
    homos = {c: [chr(0xE100+i)] for i, c in enumerate(letters)}
    tot = sum(freq.values()); extra = n_units - len(letters); nxt = 0xE100+len(letters)
    for c in letters:
        k = round(extra*freq[c]/tot)
        for _ in range(k): homos[c].append(chr(nxt)); nxt += 1
    enc = [''.join(rng.choice(homos[c]) for c in w) for w in words]
    return enc

def main():
    lang, ref = sys.argv[1], sys.argv[2]
    raw = '--raw' in sys.argv
    L = parse('data/ZL3b-n.txt')
    V = words_of(L, kind='P')
    Vt = V if raw else retok(V, GROUPS)
    if lang == 'he':
        text = open(ref, encoding='utf-8').read()
        words = re.findall(r'[א-ת]+', text)
    else:
        t = clean_gutenberg(ref) if lang != 'la' else open(ref).read()
        words = tokenize_natural(t)
    from collections import Counter
    fc = Counter(c for w in words for c in w)
    letters = [c for c, _ in fc.most_common(30) if fc[c] > 0.001*sum(fc.values())]
    words = [w for w in words if all(c in letters for c in w)]
    n_test = len(Vt)
    test, train = words[:n_test], words[n_test:]
    lm = LM(train, letters)
    print(f"[{lang}] letters={len(letters)} train={len(train)} test={n_test} cipher units={'EVA raw' if raw else 'retokenised'}")
    print(f"(a) real plaintext (held-out):      {lm.bits_per_char(test):.3f} bits/char")
    rng = random.Random(0)
    cu = Cipher(Vt); U = cu.U
    enc = homophonic_encipher(test, letters, U, rng)
    ce = Cipher(enc); m, b = solve(ce, lm)
    # accuracy of recovered mapping
    truth = {}
    for w, e in zip(test, enc):
        for c, u in zip(w, e): truth[u] = c
    acc = np.mean([lm.letters[m[ce.idx[u]]] == truth[u] for u in ce.units[1:]])
    print(f"(b) solved homophonic cipher ({U} units) of held-out text: {b:.3f} bits/char; unit-accuracy {acc:.2f}")
    print("    decoded sample:", decode(ce, lm, m, enc, 15))
    m, b = solve(cu, lm)
    print(f"(c) solved Voynichese ({U} units):  {b:.3f} bits/char")
    print("    decoded sample:", decode(cu, lm, m, Vt, 25))
    # control d: random text with VMS unit unigram stats and word lengths
    units = cu.units[1:]; p = cu.unit_freq[1:]/cu.unit_freq[1:].sum()
    rnd = [''.join(rng.choices(units, weights=p, k=len(w))) for w in Vt]
    cr = Cipher(rnd); m, b = solve(cr, lm)
    print(f"(d) solved random-unit control:     {b:.3f} bits/char")
    # control e: VMS with words shuffled (keeps word-internal structure only)
    sh = list(Vt); rng.shuffle(sh)
    cs = Cipher(sh); m, b = solve(cs, lm)
    print(f"(e) solved VMS, words shuffled:     {b:.3f} bits/char")

if __name__ == '__main__':
    main()
