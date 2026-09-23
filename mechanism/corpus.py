"""Corpora for the mechanism-identification battery (see mechanism/PREREG.md, Sections 4 and 5).

Every corpus is a list of pages; a page is a list of lines; a line holds its tokens plus the
flags the line-level tests need. Voynich glyphs are segmented into units with the multigraphs
cth ckh cph cfh ch sh as single units; Latin-alphabet corpora use letters as units.
"""
import glob
import os
import re
from collections import defaultdict
from dataclasses import dataclass, field
from functools import lru_cache
from typing import List, Optional

from voynich.ivtff import parse
from voynich.stats import clean_gutenberg, tokenize_natural

UNIT_RE = re.compile(r'cth|ckh|cph|cfh|ch|sh|.')


@lru_cache(maxsize=None)
def eva_units(tok):
    return tuple(UNIT_RE.findall(tok))


@lru_cache(maxsize=None)
def letter_units(tok):
    return tuple(tok)


def certain(tok):
    return '?' not in tok and '*' not in tok


@dataclass
class Ln:
    toks: List[str]
    para_final: Optional[bool] = None   # True: paragraph-final; False: margin-bound; None: unknown
    eligible: bool = False              # usable for line-length tests (T2b)
    dc: Optional[List[bool]] = None     # double-coded flags aligned with toks (Voynich only)
    hyph: bool = False                  # line ends with a hyphenated fragment (gibberish only)
    locus: str = ''


@dataclass
class Pg:
    id: str
    lines: List[Ln]
    hand: Optional[str] = None
    quire: Optional[str] = None
    section: Optional[str] = None
    lang: Optional[str] = None


@dataclass
class Corpus:
    name: str
    pages: List[Pg]
    kind: str            # 'eva' or 'letters'
    gclass: str          # P, I, C, V (Voynich) or C-lang
    note: str = ''

    def units(self, tok):
        return eva_units(tok) if self.kind == 'eva' else letter_units(tok)

    def ntok(self):
        return sum(len(l.toks) for p in self.pages for l in p.lines)


# ------------------------------------------------------------------ Voynich
ZL = 'data/ZL3b-n.txt'
IT = 'data/IT2a-n.txt'


def load_voynich():
    zl = parse(ZL, comma_is_space=False)
    it = {(l.page, l.num): l.words for l in parse(IT, comma_is_space=False) if l.kind == 'P'}
    pages, order = {}, []
    for ln in zl:
        if ln.kind != 'P':
            continue
        raw = ln.words
        other = it.get((ln.page, ln.num))
        if other is not None and len(other) == len(raw):
            dc_raw = [a == b and certain(a) for a, b in zip(raw, other)]
        else:
            dc_raw = [False] * len(raw)
        toks = [w for w in raw if certain(w)]
        dc = [d for w, d in zip(raw, dc_raw) if certain(w)]
        if not toks:
            continue
        gap = '<->' in ln.raw or '<~>' in ln.raw
        line = Ln(toks=toks, para_final='<$>' in ln.raw,
                  eligible=(len(toks) == len(raw) and not gap), dc=dc, locus=ln.locus)
        if ln.page not in pages:
            m = ln.meta
            pages[ln.page] = Pg(id=ln.page, lines=[], hand=m.get('H'), quire=m.get('Q'),
                                section=m.get('I'), lang=m.get('L'))
            order.append(ln.page)
        pages[ln.page].lines.append(line)
    return Corpus('VOYNICH', [pages[p] for p in order], 'eva', 'V')


_VMETA = None


def vmeta():
    global _VMETA
    if _VMETA is None:
        _VMETA = {p.id: p for p in load_voynich().pages}
    return _VMETA


def with_vmeta(name, page_ids, gen_pages, kind, gclass, note=''):
    """Wrap generated pages (list of list of token lists) with Voynich page metadata."""
    meta = vmeta()
    out = []
    for pid, pg in zip(page_ids, gen_pages):
        m = meta.get(pid)
        lines = [Ln(toks=list(l)) for l in pg if l]
        if not lines:
            continue
        out.append(Pg(id=pid, lines=lines, hand=m.hand if m else None, quire=m.quire if m else None,
                      section=m.section if m else None, lang=m.lang if m else None))
    return Corpus(name, out, kind, gclass, note)


# ------------------------------------------------------------------ human gibberish (Gaskell & Bowern 2022)
SEP_RE = re.compile(r'^\s*_{3,}\s*$')
BULLET_RE = re.compile(r'^\s*[-*]+\s*')
WORD_RE = re.compile(r"[^\W\d_]+")


def load_gibberish():
    pages = []
    for f in sorted(glob.glob('data/gibberish/Gibberish - *.txt')):
        doc = os.path.basename(f)[len('Gibberish - '):-4]
        items = []
        for raw in open(f, encoding='utf-8', errors='replace').read().splitlines():
            if SEP_RE.match(raw):
                items.append(('sep', None))
            elif not raw.strip():
                items.append(('blank', None))
            else:
                items.append(('line', raw))
        lines = []
        for i, (kind, raw) in enumerate(items):
            if kind != 'line':
                continue
            nxt = next((k for k, _ in items[i + 1:] if k != 'sep'), None)
            # paragraph-final if followed by a blank line or the end of the document
            nxt_any = items[i + 1][0] if i + 1 < len(items) else None
            para_final = nxt_any == 'blank' or nxt is None
            text = BULLET_RE.sub('', raw).lower()
            hyph = text.rstrip().endswith('-')
            toks = WORD_RE.findall(text)
            if toks:
                lines.append(Ln(toks=toks, para_final=para_final, eligible=True, hyph=hyph))
        if lines:
            pages.append(Pg(id=doc, lines=lines, hand=doc, quire=doc, section='GIB', lang='GIB'))
    return Corpus('GIB', pages, 'letters', 'I', 'Gaskell & Bowern 2022, handwritten gibberish')


# ------------------------------------------------------------------ natural-language controls
LANGS = {'LAT': 'data/ref/la_caesar.txt', 'LATV': 'data/ref/la_vulgate.txt',
         'ITA': 'data/ref/it_dante.txt', 'GER': 'data/ref/de_faust.txt',
         'ENG': 'data/ref/en_war_and_peace.txt'}


def lang_words(name):
    return tokenize_natural(clean_gutenberg(LANGS[name]))


def load_lang_chunked(name):
    """Running text cut into the Voynich page/line token shape (a reflowed text)."""
    from voynich import generators as G
    pages = G.chunk(lang_words(name))
    return with_vmeta(name, list(G.pages.keys()), pages, 'letters', 'C-lang', 'natural language, V shape')


def load_lang_wrapped(name='LAT', width=55, lines_per_page=30, npages=60):
    """Running text wrapped greedily at a fixed width in letters (K-reflow calibration for T1/T2)."""
    words = lang_words(name)
    lines, cur, cur_len = [], [], 0
    for w in words:
        add = len(w) if not cur else len(w) + 1
        if cur and cur_len + add > width:
            lines.append(cur)
            cur, cur_len = [w], len(w)
        else:
            cur.append(w)
            cur_len += add
        if len(lines) >= lines_per_page * npages:
            break
    pages = []
    for i in range(npages):
        chunk = lines[i * lines_per_page:(i + 1) * lines_per_page]
        if not chunk:
            break
        pages.append(Pg(id=f'{name}W{i}', lines=[Ln(toks=l, para_final=False, eligible=True) for l in chunk],
                        hand='W', quire=str(i // 8), section='W', lang=name))
    return Corpus(name + 'W', pages, 'letters', 'C-lang', f'greedy wrap at {width} letters')
