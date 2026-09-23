"""Parser for IVTFF transliteration files (voynich.nu, EVA alphabet).

Produces a flat list of Line objects with page metadata and cleaned word lists.
"""
import re
from dataclasses import dataclass, field
from typing import List, Dict, Optional

PAGE_RE = re.compile(r'^<(f\d+[rv]\d?|f\d+[rv]|fRos|fRos\d)>\s*(<!([^>]*)>)?')
LOCUS_RE = re.compile(r'^<([^.>]+)\.(\d+),([^>]+)>\s*(.*)$')

# inline markup
ALT_RE = re.compile(r'\[([^\]:]*):[^\]]*\]')   # [a:o] -> a
HIGH_ASCII_RE = re.compile(r'@\d+;')            # @138; -> *
COMMENT_RE = re.compile(r'<![^>]*>')            # <! ... >
BRACE_RE = re.compile(r'\{[^}]*\}')             # {comment} or ligature indications
TAG_RE = re.compile(r'<[^>]*>')                 # remaining <%> <$> <-> <~> etc.

@dataclass
class Line:
    page: str
    num: int
    locus: str          # e.g. '@P0', '+P0', 'L0', 'Cc'
    raw: str
    words: List[str] = field(default_factory=list)
    meta: Dict[str, str] = field(default_factory=dict)

    @property
    def kind(self) -> str:
        """P = paragraph text, L = label, C = circular, R = radial, other."""
        t = self.locus.lstrip('@+*=~!/&')
        return t[:1] if t else '?'

    @property
    def lang(self) -> Optional[str]:
        return self.meta.get('L')

    @property
    def section(self) -> Optional[str]:
        return self.meta.get('I')

    @property
    def hand(self) -> Optional[str]:
        return self.meta.get('H')

    @property
    def quire(self) -> Optional[str]:
        return self.meta.get('Q')


def clean_text(s: str, comma_is_space: bool = True) -> str:
    s = ALT_RE.sub(r'\1', s)
    s = HIGH_ASCII_RE.sub('*', s)
    s = COMMENT_RE.sub('', s)
    s = BRACE_RE.sub('', s)
    s = s.replace('<->', '.').replace('<~>', '.')
    s = TAG_RE.sub('', s)
    s = s.replace('!', '')          # filler
    if comma_is_space:
        s = s.replace(',', '.')
    else:
        s = s.replace(',', '')
    s = re.sub(r'\s+', '', s)
    return s


def parse(path: str, comma_is_space: bool = True) -> List[Line]:
    lines: List[Line] = []
    meta: Dict[str, str] = {}
    page = None
    with open(path, encoding='utf-8', errors='replace') as fh:
        for raw in fh:
            raw = raw.rstrip('\n')
            if not raw or raw.startswith('#'):
                continue
            m = PAGE_RE.match(raw)
            if m and not LOCUS_RE.match(raw):
                page = m.group(1)
                meta = {}
                if m.group(3):
                    for kv in re.findall(r'\$(\w)=(\w+)', m.group(3)):
                        meta[kv[0]] = kv[1]
                continue
            m = LOCUS_RE.match(raw)
            if not m:
                continue
            pg, num, locus, text = m.groups()
            cleaned = clean_text(text, comma_is_space)
            words = [w for w in cleaned.split('.') if w]
            lines.append(Line(page=pg, num=int(num), locus=locus, raw=text,
                              words=words, meta=dict(meta)))
    return lines


def words_of(lines, kind='P', lang=None, section=None, drop_unclear=True):
    out = []
    for ln in lines:
        if kind and ln.kind != kind:
            continue
        if lang and ln.lang != lang:
            continue
        if section and ln.section != section:
            continue
        for w in ln.words:
            if drop_unclear and ('?' in w or '*' in w):
                continue
            out.append(w)
    return out


if __name__ == '__main__':
    import sys
    L = parse(sys.argv[1])
    print(len(L), 'lines;', sum(len(l.words) for l in L), 'tokens')
