"""Build data/pcm.json: Bhaddanta Dr. Rewata Dhamma, Process of Consciousness and Matter, ed. Ven. Dr.
Kumarabhivamsa (Triple Gem Publications 2004; © 2007 Birmingham Buddhist Vihara), from the pages
proofread against the page images in ocr/pcm/p001.md … p208.md and p222.md (see AUTOPILOT_LOG.md,
13–14 November 2026, for how they were made and their conventions):

python3 scripts/pcm/convert.py && python3 scripts/build.py pcm

- Each page file starts with "<!-- page NNN, book page X -->". The book's own page X is kept as a page
  anchor (#pgX, and #pX beside it, so that a chart's "PCM p113" can be found): a mark in the margin
  where a page begins between blocks, inline (⟨pg:X⟩) where it begins inside a paragraph or a table.
  Blank pages and the unnumbered front pages have no mark.
- "<!-- cont … -->" joins the page's first block to the last one of the page before: a paragraph to a
  paragraph (an indented passage to an indented passage), a table without a header row to the table
  before, a glossary or index entry to the entry before. Other comments are the proofreaders' notes.
- The parts: Front matter (title page, imprint, List of Tables, Abbreviations, Terms Used and Tables),
  Preface, Acknowledgement, the biography, Introduction, Chapters I–V, the Tables printed after
  Chapter V (pp. 144–159), Notes, Bibliography, Pāli-English Glossary, Index, and the opening statement
  of the sponsors' acknowledgement (p. 200). The half-title, a blank page and the Contents (pp. 1–2,
  5–10 of the PDF) are left out: the reader has its own contents.
- A table whose body is only "ooo" (and the ellipsis cells) is a process diagram ("diagram": shown
  compact, on a phone in rows of seven cells, not as cards).
- "##" is a heading, "###" a sub-heading (in the Tables, Notes: a heading); a line wholly in bold on
  its own a minor heading; "> " one line an indented passage, several lines a passage keeping its
  line breaks; "- " a list line (indented by its spaces); every other line a paragraph.
- The notes are the book's endnotes, numbered afresh in the Introduction and each chapter: the
  chapters' [^n] link to the note in the Notes part (the book setting "endnotes", scripts/build.py).
- The index's page numbers link to the page anchors.
- The text is as proofread, misprints included; nothing is corrected here."""
import glob
import json
import os
import re
import sys

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..')
SRC = os.path.join(ROOT, 'ocr', 'pcm')
SKIP_PAGES = {1, 2, 5, 6, 7, 8, 9, 10}
COMMENT = re.compile(r'\s*<!--.*?-->')
LIT = ''
ROMAN = {'I': 1, 'II': 2, 'III': 3, 'IV': 4, 'V': 5}
CHAPTERS = {         # the book's chapter -> its title (as the Contents give it), the Saṅgaha chapter it follows
    'I': ('Consciousness and its Factors', 1),
    'II': ('Process of Consciousness (Citta Vīthi)', 4),
    'III': ('Mind-Door Cognitive Process (Manodvāra Vīthi)', 4),
    'IV': ('Absorption Javana in the Mind-Door Process (Appanā Javanavāra-Manodvāra Vīthi)', 4),
    'V': ('Process of Matter', 6),
}
PARTS = {            # a "##" line that opens a part -> label, title, notes key
    'PREFACE': ('Preface', 'Preface', None),
    'ACKNOWLEDGEMENT': ('Acknowledgement', 'Acknowledgement', None),
    'DR REWATA DHAMMA': ('Biography', 'Dr Rewata Dhamma', None),
    'INTRODUCTION': ('Introduction', 'Introduction', 'intro'),
    'NOTES': ('Notes', 'Notes', None),
    'BIBLIOGRAPHY': ('Bibliography', 'Bibliography', None),
    'PĀLI-ENGLISH GLOSSARY': ('Glossary', 'Pāli-English Glossary', None),
    'INDEX': ('Index', 'Index', None),
    'Acknowledgement': ('Back matter', 'Acknowledgement', None),       # p222, the sponsors'
}
TABLES_FROM = 166
CAPS = {             # headings printed in capitals, in the case the Contents give them (the reader sets headings in capitals)
    'THE 89 AND 121 CITTAS AT A GLANCE[^3]': 'The 89 and 121 Cittas at a Glance[^3]',
    'THE 52 MENTAL FACTORS AT A GLANCE': 'The 52 Mental Factors at a Glance',
    'INTRODUCTION': 'Introduction',
}
NOTE_KEYS = {'INTRODUCTION': 'intro', 'CHAPTER I': '1', 'CHAPTER II': '2', 'CHAPTER III': '3', 'CHAPTER IV': '4', 'CHAPTER V': '5'}
IDX = re.compile(r'^(.*?)\s+((?:(?:[IVX]+|\d+(?:-\d+)?)(?:,\s*|\s+))*(?:[IVX]+|\d+(?:-\d+)?))$')


def unescape(t):
    return t.replace('\\*', LIT).replace(LIT, '*') if '\\' in t else t


def cells(line):
    return [unescape(c.strip()) for c in line.strip().strip('|').split('|')]


def whole_bold(t):
    if t.startswith('**') and t.endswith('**') and not t.startswith('***') and '**' not in t[2:-2]:
        return t[2:-2]
    return None


CENTRED = False


def page_blocks(text):
    """(kind, payload) for each block of one page"""
    lines = text.split('\n')
    out, i, gid = [], 0, 0
    while i < len(lines):
        raw = lines[i]
        if raw.startswith('```'):
            raise SystemExit('a fenced block: not expected in PCM')
        l = COMMENT.sub('', raw).rstrip()
        if not l.strip():
            i += 1
            continue
        j = i
        blk = []
        while j < len(lines) and COMMENT.sub('', lines[j]).strip():
            blk.append(COMMENT.sub('', lines[j]).rstrip())
            j += 1
        i = j
        gid += 1
        first = blk[0]
        if first.startswith('|'):
            rows = [r for r in blk if not re.fullmatch(r'\|(\s*:?-+:?\s*\|)+\s*', r.strip())]
            grid = [cells(r) for r in rows]
            out.append(('table', grid, gid))
            continue
        if first.startswith('>'):
            items = [unescape(re.sub(r'^>\s?', '', x).strip()) for x in blk]
            out.append(('quote', items, gid))
            continue
        for x in blk:
            m = re.match(r'^(#{1,3}) (.*)$', x)
            if m:
                out.append(({1: 'title', 2: 'h', 3: 'h4'}[len(m.group(1))], m.group(2).strip(), gid))
                continue
            ind = (len(x) - len(x.lstrip(' '))) // 4
            t = x.strip()
            if t.startswith('- '):
                out.append(('li', (ind, unescape(t[2:].strip())), gid))
            elif ind:
                out.append(('sub', unescape(t), gid))
            elif len(blk) == 1 and whole_bold(t) is not None and not CENTRED:
                out.append(('h5', whole_bold(t), gid))
            else:
                out.append(('line' if len(blk) > 1 else 'p', unescape(t), gid))
    return out


def initial(t):
    import unicodedata
    t = re.sub(r'[^\w]', '', unicodedata.normalize('NFD', t)).lower()
    return t[:1]


def main():
    parts = [dict(label='Front matter', title='Front matter', blocks=[])]
    files = sorted(glob.glob(os.path.join(SRC, 'p[0-9][0-9][0-9].md')))
    pages = [int(re.search(r'p(\d+)\.md$', f).group(1)) for f in files]
    assert pages == list(range(1, 209)) + [222], pages
    pending_title = None       # the title line under "CHAPTER n"
    notes_key = None
    for f, pno in zip(files, pages):
        if pno in SKIP_PAGES:
            continue
        text = open(f, encoding='utf-8').read()
        head = re.match(r'<!-- page (\d+), book page (\S+?)[ ,-]', text + ' ')
        assert int(head.group(1)) == pno, f
        bp = head.group(2)
        bp = None if bp == 'unnumbered' or 'blank page' in text else bp
        cont = bool(re.search(r'<!-- cont\b', text))
        mark = bp            # the page's anchor, set before its first block (or inline at a join)
        if pno == TABLES_FROM:
            parts.append(dict(label='Tables', title='Tables', blocks=[]))
        global CENTRED
        CENTRED = pno == 3          # the title page: every line centred
        blist = page_blocks(text)

        def add(b):
            nonlocal mark
            blocks = parts[-1]['blocks']
            if mark:
                blocks.append(dict(type='pg', n=mark))
                mark = None
            blocks.append(b)

        last_gid = None
        for k, (kind, x, gid) in enumerate(blist):
            blocks = parts[-1]['blocks']
            last = blocks[-1] if blocks else None
            title = parts[-1]['title']
            # ---- a page that goes on from the page before
            if k == 0 and cont:
                pgm = f'⟨pg:{mark}⟩' if mark else ''
                if kind == 'table' and not any(c for c in x[0]):
                    assert last['type'] == 'table', (pno, last['type'])
                    rows = x[1:]
                    if pgm:
                        rows[0][0] = pgm + rows[0][0]
                    last['rows'] += rows
                    mark = None
                    continue
                if kind == 'table':
                    pass                          # a new diagram under the heading of the page before
                elif title == 'Pāli-English Glossary' and kind in ('p', 'line'):
                    it = last['items']
                    it[-1] += ('' if it[-1].endswith('-') else ' ') + x      # the mark goes before the page's next entry
                    continue
                elif title == 'Index' and kind in ('p', 'line'):
                    t, pg, lv = last['items'][-1]
                    last['items'][-1] = idx_item(t + (' ' + pg if pg else '') + ' ' + x)
                    continue
                elif title == 'Notes' and kind == 'sub':
                    last['text'] += ' ¶ ' + pgm + x
                    mark = None
                    continue
                elif title == 'Notes':
                    pass                          # the next note
                elif kind == 'quote' and len(x) == 1:
                    assert last['type'] == 'p' and last.get('ind') == 1, (pno, last)
                    last['text'] += ' ' + pgm + x[0]
                    mark = None
                    continue
                elif kind in ('p', 'line'):
                    if last['type'] == 'list' or (last['type'] == 'p' and last.get('ind')):
                        pass
                    assert last['type'] == 'p' and not last.get('note'), (pno, last)
                    last['text'] += ('' if last['text'].endswith('-') else ' ') + pgm + x
                    mark = None
                    continue
                else:
                    raise SystemExit(f'p{pno:03d}: "cont" before {kind}')
            # ---- the parts
            if kind == 'title':
                assert pno == 3, pno
                add(dict(type='p', ctr=True, big=True, text=x))
                continue
            if kind == 'h':
                m = re.fullmatch(r'CHAPTER ([IV]+)', x)
                if m:
                    t, ch = CHAPTERS[m.group(1)]
                    parts.append(dict(label=f'Chapter {m.group(1)}', title=t, sangaha_ch=ch,
                                      notes_key=str(ROMAN[m.group(1)]), blocks=[]))
                    if pno == 31:            # the homage printed above "CHAPTER I": it opens the chapter
                        homage = [b for b in parts[-2]['blocks'][-3:] if b.get('ctr') or b['type'] == 'pg']
                        del parts[-2]['blocks'][-len(homage):]
                        parts[-1]['blocks'] += homage
                    pending_title = m.group(1)
                    continue
                if pending_title:
                    assert x.upper() == x and x.startswith(CHAPTERS[pending_title][0].upper().split(' (')[0][:12]), (pno, x)
                    pending_title = None
                    continue
                if x in PARTS:
                    lab, t, nk = PARTS[x]
                    p = dict(label=lab, title=t, blocks=[])
                    if nk:
                        p['notes_key'] = nk
                    parts.append(p)
                    continue
                if x in ('LIST OF TABLES', 'ABBREVIATIONS', 'TERMS USED AND TABLES'):
                    add(dict(type='h', text=x.title().replace(' And ', ' and ').replace(' Of ', ' of ').replace(' Used', ' Used')))
                    continue
                add(dict(type='h', text=CAPS.get(x, x)))
                continue
            pending_title = None
            if kind == 'h4':
                if title in ('Tables', 'Notes'):
                    if title == 'Notes':
                        notes_key = NOTE_KEYS[x]
                    add(dict(type='h', text=CAPS.get(x, 'Chapter ' + x.split()[1] if x.startswith('CHAPTER ') else x)))
                else:
                    add(dict(type='h4', text=x))
                continue
            if kind == 'h5':
                add(dict(type='h5', text=x))
                continue
            if kind == 'table':
                head, body = x[0], x[1:]
                b = dict(type='table', spans=True, rows=body)
                if any(c for c in head):
                    b['hrows'] = [head]
                for r in b.get('hrows', []) + body:
                    assert not any(c in ('<', '^') for c in r), r
                if all(re.fullmatch(r'ooo|\**[.…]+\**”?|', c) for r in body for c in r) and any('ooo' in c for r in body for c in r):
                    b['diagram'] = True      # a process drawn mind-moment by mind-moment: a row of codes over rows of ooo
                add(b)
                continue
            if kind == 'quote':
                if len(x) == 1:
                    add(dict(type='p', ind=1, text=x[0]))
                else:
                    add(dict(type='lines', items=x))
                continue
            if kind == 'li':
                ind, t = x
                add(dict(type='p', text=t, **({'ind': ind} if ind else {})))
                continue
            if title == 'Notes':
                if kind == 'sub':
                    last['text'] += ' ¶ ' + x
                    continue
                m = re.match(r'^(\d+)\.\s+(.*)$', x)
                assert m, (pno, x)
                back = next(c['num'] for c in parts_numbered(parts) if c.get('notes_key') == notes_key)
                add(dict(type='p', note=int(m.group(1)), nkey=notes_key, back=back, text=m.group(2)))
                continue
            assert kind != 'sub', (pno, x)
            if title in ('Pāli-English Glossary', 'Index'):
                typ = 'lines' if title != 'Index' else 'idx'
                item = x if typ == 'lines' else idx_item(x)
                if last and last['type'] == typ and not mark and gid == last_gid:
                    last['items'].append(item)
                else:
                    add(dict(type=typ, items=[item]))
                last_gid = gid
                continue
            if pno == 3 or (pno == 31 and kind == 'line'):
                add(dict(type='p', ctr=True, text=x))
                continue
            add(dict(type='p', text=x))
    chapters = parts_numbered(parts)
    for c in chapters:
        assert [b for b in c['blocks'] if b['type'] != 'pg'], c['title']
    check_notes(chapters)
    out = dict(chapters=[{k: c[k] for k in ('num', 'label', 'title', 'sangaha_ch', 'notes_key', 'blocks') if k in c} for c in chapters],
               glossary=[])
    with open(os.path.join(ROOT, 'data', 'pcm.json'), 'w', encoding='utf-8') as fh:
        json.dump(out, fh, ensure_ascii=False, indent=0)
    for c in chapters:
        print(c['num'], c['label'], '|', c['title'], len(c['blocks']), c.get('sangaha_ch', ''))
    doubt = [m for c in chapters for b in c['blocks'] for t in [b.get('text', '')] + [str(i) for i in b.get('items', [])]
             for m in re.findall(r'\S+⟨\?⟩', t)]
    print('⟨?⟩:', doubt)


def idx_item(line):
    m = IDX.match(line)
    if not m:
        return [line, '', 1]
    return [m.group(1), m.group(2), 1]


def parts_numbered(parts):
    for i, c in enumerate(parts):
        c['num'] = str(i)
    return parts


def check_notes(chapters):
    refs = {}
    for c in chapters:
        if c.get('notes_key'):
            for b in c['blocks']:
                for t in [b.get('text', '')] + [x for x in b.get('items', []) if isinstance(x, str)] + [y for r in b.get('rows', []) + b.get('hrows', []) for y in r]:
                    for n in re.findall(r'\[\^(\d+)\]', t):
                        refs.setdefault(c['notes_key'], []).append(int(n))
    notes = {}
    for c in chapters:
        for b in c['blocks']:
            if b.get('nkey'):
                notes.setdefault(b['nkey'], []).append(b['note'])
    ok = True
    for k in sorted(set(refs) | set(notes)):
        r, n = sorted(set(refs.get(k, []))), notes.get(k, [])
        if r != n:
            ok = False
            print('notes', k, 'cited', r, 'printed', n, file=sys.stderr)
    for c in chapters:
        if not c.get('notes_key'):
            for b in c['blocks']:
                assert '[^' not in b.get('text', ''), (c['title'], b['text'][:80])
    print('notes: every [^n] has its note' if ok else 'notes: MISMATCH (see above)')


if __name__ == '__main__':
    main()
