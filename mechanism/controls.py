"""Generated control corpora (PREREG.md, Section 5). All reproduce the Voynich page/line shape."""
import random
from collections import Counter, defaultdict

from mechanism.corpus import Corpus, Ln, Pg, eva_units, load_voynich, with_vmeta


def _G():
    from voynich import generators as G
    return G


def mk_sec(seed=3):
    G = _G()
    return with_vmeta('MK-sec', list(G.pages.keys()), G.markov_pages(3, True, seed=seed), 'eva', 'P',
                      'order-3 automaton per (language, section)')


def mk_page(seed=0):
    G = _G()
    return with_vmeta('MK-page', list(G.pages.keys()), G.markov_pages_hier(3, 0.5, seed=seed), 'eva', 'P',
                      'order-3 automaton, page/section interpolation lambda=0.5')


def rugg(seed=0):
    G = _G()
    return with_vmeta('RUGG', list(G.pages.keys()), G.rugg_pages(seed=seed), 'eva', 'P', 'table and grille')


def ts(seed=0):
    G = _G()
    return with_vmeta('TS', list(G.pages.keys()), G.ts_pages(seed=seed), 'eva', 'I',
                      'copy-and-modify after Timm & Schinner 2020')


def naib(independent_lines=True, seed=0):
    G = _G()
    name = 'NAIB-lines' if independent_lines else 'NAIB-run'
    return with_vmeta(name, list(G.pages.keys()), G.naibbe_pages(seed=seed, independent_lines=independent_lines),
                      'eva', 'C', 'Naibbe cipher on Latin (Greshko 2025)')


# ------------------------------------------------------------------ periodic device (positive control for T4)
def dev(w, seed=0, period=5, cycle=4):
    """Token for (row r, column c) drawn from (1-2w)*global + w*Final_c + w*Initial_r.

    Final_c: global distribution restricted to tokens whose final unit is in group c (of `period` groups);
    Initial_r: restricted to tokens whose initial unit is in group r (of `cycle` groups).
    Line i of a page uses row (offset + i) mod cycle; token j uses column j mod period.
    """
    rng = random.Random(seed)
    V = load_voynich()
    freq = Counter(t for p in V.pages for l in p.lines for t in l.toks)
    toks = list(freq)
    finals = [u for u, _ in Counter(eva_units(t)[-1] for t in toks for _ in range(freq[t])).most_common()]
    inits = [u for u, _ in Counter(eva_units(t)[0] for t in toks for _ in range(freq[t])).most_common()]
    fgroup = {u: i % period for i, u in enumerate(finals)}
    igroup = {u: i % cycle for i, u in enumerate(inits)}
    gw = [freq[t] for t in toks]
    fw = [[freq[t] if fgroup[eva_units(t)[-1]] == c else 0 for t in toks] for c in range(period)]
    iw = [[freq[t] if igroup[eva_units(t)[0]] == r else 0 for t in toks] for r in range(cycle)]
    norm = lambda v: [x / sum(v) for x in v]
    gw, fw, iw = norm(gw), [norm(v) for v in fw], [norm(v) for v in iw]
    from itertools import accumulate
    mix = {}
    for r in range(cycle):
        for c in range(period):
            mix[r, c] = list(accumulate((1 - 2 * w) * g + w * f + w * i for g, f, i in zip(gw, fw[c], iw[r])))
    pages = []
    for p in V.pages:
        off = rng.randrange(cycle)
        lines = []
        for i, l in enumerate(p.lines):
            r = (off + i) % cycle
            lines.append(Ln(toks=[rng.choices(toks, cum_weights=mix[r, j % period])[0] for j in range(len(l.toks))]))
        pages.append(Pg(id=p.id, lines=lines, hand=p.hand, quire=p.quire, section=p.section, lang=p.lang))
    return Corpus(f'DEV-{w}', pages, 'eva', 'P', f'periodic device, period {period}, cycle {cycle}, w={w}')


# ------------------------------------------------------------------ drift-shape calibration (T5)
def drift(shape, seed=0, order=2):
    """Per hand, an order-2 automaton moving from the Currier-A model to the Currier-B model across the
    hand's pages, either linearly (smooth) or in one jump at the midpoint (step)."""
    G = _G()
    rng = random.Random(seed)
    V = load_voynich()
    strA = [' '.join(l.toks) for p in V.pages if p.lang == 'A' for l in p.lines]
    strB = [' '.join(l.toks) for p in V.pages if p.lang == 'B' for l in p.lines]
    mA, mB = G.fit(strA, order), G.fit(strB, order)

    class Mix(dict):
        def __init__(self, a):
            super().__init__()
            self.a = a

        def get(self, ctx, default=None):
            x, y = mA.get(ctx), mB.get(ctx)
            if not x and not y:
                return None
            nx = sum((x or {}).values()) or 1
            ny = sum((y or {}).values()) or 1
            syms = set(x or {}) | set(y or {})
            out = Counter({s: ((1 - self.a) * ((x or {}).get(s, 0) / nx) + self.a * ((y or {}).get(s, 0) / ny)) * 1000
                           for s in syms})
            out = Counter({k: v for k, v in out.items() if v > 0})
            return out if out else Counter(x or y)   # context seen only in the model with weight 0

    byhand = defaultdict(list)
    for p in V.pages:
        byhand[p.hand].append(p)
    pages = {}
    for h, ps in byhand.items():
        n = len(ps)
        for k, p in enumerate(ps):
            a = k / (n - 1) if n > 1 else 0.0
            if shape == 'step':
                a = 0.0 if k < n / 2 else 1.0
            m = Mix(a)
            lines = []
            for l in p.lines:
                gen = G.sample_line(m, order, len(' '.join(l.toks)), rng)
                if gen:
                    lines.append(Ln(toks=gen))
            pages[p.id] = Pg(id=p.id, lines=lines, hand=p.hand, quire=p.quire, section=p.section, lang=p.lang)
    out = [pages[p.id] for p in V.pages if pages[p.id].lines]
    return Corpus(f'DRIFT-{shape}', out, 'eva', 'P' if shape == 'step' else 'I', f'{shape} drift A->B per hand')
