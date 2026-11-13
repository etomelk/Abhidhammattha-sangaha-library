"""Build data/mendis.json: N. K. G. Mendis, The Abhidhamma in Practice (BPS, The Wheel No. 322/323,
1985, reprinted 2005), from the pages proofread against the page images in ocr/mendis/p001.md …
p080.md (see AUTOPILOT_LOG.md for how they were made and their conventions):

python3 scripts/mendis/convert.py && python3 scripts/build.py mendis

- Each page file starts with "<!-- page NNN, book page X -->"; "<!-- cont -->" means the page's first
  paragraph (or verse) continues the last one of the page before, and it is joined to it.
- "## TITLE" opens a part (the chapter titles of the book's contents: The Cittas, The Cetasikas …);
  "### …" is a heading; "> …" lines are verse; the one fenced block (the ditto table of
  p034) is a table of two columns: each term, and what it qualifies or the printed ditto marks.
- Footnotes "[^n]: …" at the foot of a page are set under the paragraph that cites them and numbered
  anew in each part.
- Front matter: the cover (p001), the title page (p002) and the contents (p004) are left out (the
  reader has its own title and contents); the imprint (p003) and the Preface (p005) are kept.
  The book title over the Introduction (p006) is left out; the homage lines under it are kept.
- The text is as proofread, misprints and ⟨?⟩ marks included; nothing is corrected here."""
import glob
import json
import os
import re

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..')
SRC = os.path.join(ROOT, 'ocr', 'mendis')
SKIP_PAGES = {1, 2, 4}
LIST_ITEM = re.compile(r'^(\([a-z0-9]+\)|[a-z]\)|[ivx]+\.|\d+(-\d+)?\.)\s')
TITLES = {           # the heading on the page -> the part's title (as the contents give it), Saṅgaha chapter
    'PREFACE': ('Preface', None),
    'THE CITTAS': ('The Cittas', 1),
    'THE CETASIKAS': ('The Cetasikas', 2),
    'RŪPA': ('Rūpa', 6),
    'PLANES OF EXISTENCE': ('Planes of Existence', 5),
    'CAUSALITY': ('Causality', 8),
    'NIBBĀNA': ('Nibbāna', None),
    'About the Author': ('About the Author', None),
}


def page_blocks(text):
    """the blocks of one page: (kind, payload)"""
    lines = [l for l in text.split('\n') if not re.fullmatch(r'\s*<!--.*-->\s*', l)]
    out, i = [], 0
    while i < len(lines):
        l = lines[i]
        if not l.strip():
            i += 1
            continue
        if l.startswith('```'):
            j = i + 1
            while not lines[j].startswith('```'):
                j += 1
            out.append(('pre', '\n'.join(lines[i + 1:j])))
            i = j + 1
            continue
        j = i
        while j < len(lines) and lines[j].strip():
            j += 1
        blk = lines[i:j]
        i = j
        first = blk[0]
        if first.startswith('# '):
            out.append(('title', first[2:].strip()))
        elif first.startswith('## '):
            out.append(('part', first[3:].strip()))
        elif first.startswith('### '):
            out.append(('h', first[4:].strip()))
        elif first.startswith('|'):
            out.append(('table', blk))
        elif first.startswith('>'):
            out.append(('verse', [re.sub(r'^>\s?', '', x) for x in blk]))
        elif first.startswith('[^'):
            for x in blk:
                m = re.match(r'\[\^(\d+)\]:\s*(.*)$', x)
                if m:
                    out.append(('fn', (m.group(1), m.group(2))))
                else:
                    out[-1] = ('fn', (out[-1][1][0], out[-1][1][1] + ' ' + x.strip()))
        elif len(blk) > 1 and any(x.startswith('    ') for x in blk):
            out.append(('verse', [x.strip() for x in blk]))         # the homage lines (p006)
        elif len(blk) > 1:
            out.extend(('line', x.strip()) for x in blk)            # imprint, address: one line each
        else:
            out.append(('p', first.strip()))
    return out


def main():
    parts = [dict(num='0', label='Front matter', title='Preface', blocks=[])]
    nfn = 0
    files = sorted(glob.glob(os.path.join(SRC, 'p[0-9][0-9][0-9].md')))
    assert len(files) == 80, len(files)
    for f in files:
        pno = int(re.search(r'p(\d+)\.md$', f).group(1))
        if pno in SKIP_PAGES:
            continue
        text = open(f, encoding='utf-8').read()
        cont = '<!-- cont -->' in text
        notes = []
        for k, (kind, x) in enumerate(page_blocks(text)):
            blocks = parts[-1]['blocks']
            last = blocks[-1] if blocks else None
            if k == 0 and cont and (kind == 'pre' or kind == 'p' and LIST_ITEM.match(x)):
                pass                  # a list (or the ditto table) going on over the page: its next item is a block of its own
            elif k == 0 and cont:
                if kind == 'p' and last and last['type'] == 'p' and not last.get('note'):
                    last['text'] += ' ' + x
                    continue
                if kind == 'verse' and last and last['type'] == 'lines':
                    last['items'] += x
                    continue
                raise SystemExit(f'p{pno:03d}: "cont" but nothing to continue ({kind})')
            if kind == 'title':
                if pno == 6:          # the book's title over the Introduction
                    parts.append(dict(num='1', label='Introduction', title='Introduction', blocks=[]))
                continue
            if kind == 'part':
                title, ch = TITLES[x]
                if title == 'Preface':
                    continue
                p = dict(num=str(len(parts)), label=title, title=title, blocks=[])
                if ch:
                    p['sangaha_ch'] = ch
                parts.append(p)
                nfn = 0
            elif kind == 'h':
                blocks.append(dict(type='h', text=x))
            elif kind == 'pre':
                # the ditto table of the six pairs (p034): the term, then what it qualifies or the ditto marks
                rows = [list(m.groups()) for m in (re.match(r'^(.*?\([^)]*\))\s+(.*)$', l) for l in x.split('\n'))]
                assert all(rows) and len(rows) == 6, x
                blocks.append(dict(type='table', rows=[[a, re.sub(r'\s+', ' ', b)] for a, b in rows]))
            elif kind == 'verse':
                blocks.append(dict(type='lines', verse=True, items=x))
            elif kind in ('p', 'line'):
                blocks.append(dict(type='p', text=x))
            elif kind == 'fn':
                notes.append(x)
            elif kind == 'table':
                raise SystemExit(f'p{pno:03d}: unexpected table')
        # the page's footnotes: under the paragraph that cites them (searched back through the parts)
        for n, body in notes:
            for part in reversed(parts):
                hit = next((i for i in range(len(part['blocks']) - 1, -1, -1)
                            if f'[^{n}]' in part['blocks'][i].get('text', '') and not part['blocks'][i].get('note')), None)
                if hit is not None:
                    num = 1 + sum(1 for b in part['blocks'] if b.get('note'))
                    b = part['blocks'][hit]
                    b['text'] = b['text'].replace(f'[^{n}]', f'[^{num}]', 1)
                    part['blocks'].insert(hit + 1, dict(type='p', note=num, text=body))
                    break
            else:
                raise SystemExit(f'p{pno:03d}: note {n} not cited')
    for p in parts:
        assert p['blocks'], p['title']
    out = dict(chapters=parts, glossary=[])
    with open(os.path.join(ROOT, 'data', 'mendis.json'), 'w', encoding='utf-8') as fh:
        json.dump(out, fh, ensure_ascii=False, indent=1)
    for p in parts:
        print(p['num'], p['title'], len(p['blocks']), p.get('sangaha_ch', ''))
    doubt = [(p['title'], m) for p in parts for b in p['blocks'] for t in [b.get('text', '')] + b.get('items', [])
             for m in re.findall(r'\S+⟨\?⟩', t)]
    print('⟨?⟩:', doubt)


if __name__ == '__main__':
    main()
