"""Check that every piece of text in the rendered HTML also appears in the PDF.

    python3 paper/check_pdf.py [paper|supplement] [path/to/file.pdf]

The PDF renderer (fitz.Story) has been seen to drop table rows and following content at page breaks,
so the build runs this check after rendering. Text is compared with all whitespace removed and
ligatures expanded; each HTML block is split into chunks of 6 words and every chunk must occur in the PDF.
"""
import html as H
import re
import sys

import fitz

LIG = {'ﬁ': 'fi', 'ﬂ': 'fl', 'ﬀ': 'ff', 'ﬃ': 'ffi', 'ﬄ': 'ffl', '­': ''}


def norm(s):
    for a, b in LIG.items():
        s = s.replace(a, b)
    return re.sub(r'\s+', '', s)


def html_chunks(html, n=6):
    body = html.split('<body>', 1)[-1]
    body = re.sub(r'<img[^>]*>', ' ', body)
    blocks = re.split(r'</(?:p|li|td|th|h1|h2|h3)>|<(?:ul|ol)>', body)
    out = []
    for b in blocks:
        t = H.unescape(re.sub(r'<[^>]+>', ' ', b))
        words = t.split()
        for i in range(0, len(words), n):
            chunk = ' '.join(words[i:i + n])
            if len(norm(chunk)) >= 4:
                out.append(chunk)
    return out


def missing(html_path, pdf_path):
    html = open(html_path, encoding='utf-8').read()
    doc = fitz.open(pdf_path)
    pdf = norm(''.join(p.get_text(clip=fitz.Rect(0, 52, p.rect.width, p.rect.height - 52)) for p in doc))   # skip running head and page number
    def present(c):
        if norm(c) in pdf:
            return True
        w = c.split()          # a chunk interrupted by a float (table or figure) placed at a page break
        return any(norm(' '.join(w[:k])) in pdf and norm(' '.join(w[k:])) in pdf for k in range(1, len(w)))
    return [c for c in html_chunks(html) if not present(c)]


if __name__ == '__main__':
    name = sys.argv[1] if len(sys.argv) > 1 else 'paper'
    pdf = sys.argv[2] if len(sys.argv) > 2 else f'paper/{name}.pdf'
    miss = missing(f'paper/{name}.html', pdf)
    print(f'{name}: {len(miss)} missing chunks')
    for c in miss[:40]:
        print('  ', c)
