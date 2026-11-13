"""Add Part II of Dr. Nandamālābhivaṃsa's Fundamental Abhidhamma to data/fundamental.json, from the
pages proofread against the page images in ocr/fundamental-2/p106.md … p247.md (see AUTOPILOT_LOG.md,
13 November 2026, for how they were made and their conventions):

python3 scripts/tinmon/convert.py work/fundamental.txt fundamental     # Part I (optional: it is kept as it is)
python3 scripts/fundamental/part2.py                                  # Part II joined after it
python3 scripts/build.py fundamental

Like scripts/tinmon/handbook.py for the Handbook's two volumes, each part's label names its Part
("Part I · Chapter 5", "Part II · Chapter 5"); Part I's text is not touched. Running the script again
replaces Part II (the parts marked "part": 2).

- Each page file starts with "<!-- page NNN, book page X -->"; "<!-- cont -->" joins the page's first
  paragraph to the last one of the page before. Other HTML comments are the proofreaders' notes and
  are left out.
- "## CHAPTER n" and the "##" lines under it open a chapter (titles in TITLES, with the Saṅgaha chapter
  each follows: the book's 5–9 are the Saṅgaha's IV, V, VIII, IX, VII). p106 (the Part II title page)
  is left out. The colour charts after Chapter 9 (pp. 239–247) are a part of their own, "Charts": each
  page is shown as an image (rendered from ocr-sources/fundamental-2.pdf into fundamental/fig/) with
  its transcription under it.
- "###" is a heading, "####" a sub-heading (the 24 conditions), a line wholly in bold a minor heading;
  "**The end of Chapter n**" a centred line; Markdown tables are tables ("<br>" a line break in a
  cell, a header of empty cells no header); fenced blocks keep their columns; "> " lines are set as
  lines; every other line is a paragraph. "\\*" and "\\#" are the book's own asterisk and # signs.
- The text is as proofread, misprints included; nothing is corrected here."""
import glob
import json
import os
import re
import subprocess

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..')
SRC = os.path.join(ROOT, 'ocr', 'fundamental-2')
PDF = os.path.join(ROOT, 'ocr-sources', 'fundamental-2.pdf')
FIG = os.path.join(ROOT, 'fundamental', 'fig')
TITLES = {           # the book's chapter -> the part's title, the Saṅgaha chapter it follows
    '5': ('Vīthi: Mental Process', 4),
    '6': ('Vīthimutta: Passive Mental Process', 5),
    '7': ('Paccayasaṅgaha: Compendium of Causality', 8),
    '8': ('Kammaṭṭhāna Saṅgaha: Meditation Subject', 9),
    '9': ('Samuccayasaṅgaha: Compendium of Category', 7),
}
CHARTS_FROM = 239
COMMENT = re.compile(r'\s*<!--.*?-->')


LIT = ''
PUNCT = re.compile(r'[\s.,:;()\-–—/‘’“”"\']+')
PROBLEMS = []


def flatten(t):
    """The proofread pages nest bold and italics as Markdown does ("***Saṅkhāra*:**", "**10 *Kasiṇa***");
    the reader's markup takes flat runs only (*…*, **…**, ***…***). Split the text into runs by style,
    and write each run with its own marks, its spaces outside them; a run of punctuation only between
    two marked runs is left unmarked (the colon of "***Saṅkhāra*:**")."""
    runs, b, i = [], False, False
    for tok in re.split(r'(\*{1,3})', t):
        if tok and set(tok) == {'*'}:
            n = len(tok)
            if n == 3:
                b, i = not b, not i
            elif n == 2:
                b = not b
            else:
                i = not i
        elif tok:
            runs.append([tok, b, i])
    if b or i:
        PROBLEMS.append(('unbalanced', t))
        return t
    for k, r in enumerate(runs):
        if (r[1] or r[2]) and PUNCT.fullmatch(r[0]) and 0 < k < len(runs) - 1:
            r[1] = r[2] = False
    out = []
    for tok, b, i in runs:
        m = '***' if b and i else '**' if b else '*' if i else ''
        if not m or not tok.strip():
            out.append(tok)
            continue
        lead = tok[:len(tok) - len(tok.lstrip())]
        trail = tok[len(tok.rstrip()):]
        out.append(lead + m + tok.strip() + m + trail)
    return ''.join(out)       # runs that touch ("***Paccaya*****:**") are read right by the reader's markup: *** first, then **


def unescape(t):
    t = t.replace('\\*', LIT).replace('\\#', '#')
    return '\n'.join(flatten(x) for x in t.split('\n')).replace(LIT, '*')


def cells(line):
    return [unescape(c.strip()).replace('<br>', ' // ') for c in line.strip().strip('|').split('|')]


def whole_bold(t):
    """a line wholly in bold ("**Reviewing Knowledge**", "***Asubha***", "**10 *Kasiṇa***"): its text, else None"""
    if len(t) > 110 or not t.endswith('**'):
        return None
    if t.startswith('***') and t.endswith('***') and '**' not in t[3:-3]:
        return '*' + t[3:-3] + '*'
    if t.startswith('**') and not t.startswith('***') and '**' not in t[2:-2].replace('***', ''):
        inner = t[2:-2]
        return inner if inner.count('*') % 2 == 0 else None
    if t.startswith('**') and '**' not in t[2:-3] and t.endswith('***'):
        return t[2:-2]                 # "**10 *Kasiṇa***": bold, the last word italic too
    return None


def page_blocks(text):
    lines = text.split('\n')
    out, i = [], 0
    while i < len(lines):
        raw = lines[i]
        if raw.startswith('```'):
            j = i + 1
            while not lines[j].startswith('```'):
                j += 1
            body = [COMMENT.sub('', l).rstrip() for l in lines[i + 1:j]]
            out.append(('pre', unescape('\n'.join(body).strip('\n'))))
            i = j + 1
            continue
        l = COMMENT.sub('', raw).rstrip()
        if not l.strip():
            i += 1
            continue
        if l.startswith('|'):
            j = i
            rows = []
            while j < len(lines) and lines[j].startswith('|'):
                rows.append(lines[j])
                j += 1
            out.append(('table', rows))
            i = j
            continue
        if l.startswith('>'):
            j = i
            items = []
            while j < len(lines) and lines[j].startswith('>'):
                items.append(unescape(re.sub(r'^>\s?', '', lines[j]).strip()))
                j += 1
            out.append(('lines', items))
            i = j
            continue
        i += 1
        m = re.match(r'^(#{1,4}) (.*)$', l)
        if m:
            out.append(({1: 'title', 2: 'part', 3: 'h', 4: 'h4'}[len(m.group(1))], m.group(2).strip()))
            continue
        t = unescape(l.strip())
        wb = whole_bold(t)
        if wb is not None and re.fullmatch(r'The [Ee]nd of [Cc]hapter \d', wb):
            out.append(('ctr', wb))
        elif wb is not None:
            out.append(('h5', wb))
        else:
            out.append(('p', t))
    return out


def table_block(rows):
    rows = [r for r in rows if not re.fullmatch(r'\|(\s*:?-+:?\s*\|)+\s*', r.strip())]
    grid = [cells(r) for r in rows]
    head, body = grid[0], grid[1:]
    b = dict(type='table', spans=True, rows=body)
    if any(c for c in head):
        b['hrows'] = [head]
    else:
        assert body, rows
    for r in b.get('hrows', []) + body:
        assert not any(c in ('<', '^') for c in r), r
    return b


def chart_image(pno):
    """the chart page as an image: rendered at 200 dpi, cropped to the print, the page number left out"""
    from PIL import Image, ImageOps
    os.makedirs(FIG, exist_ok=True)
    dest = os.path.join(FIG, f'p{pno}.png')
    if not os.path.exists(dest):
        tmp = os.path.join(FIG, f'_p{pno}')
        subprocess.run(['pdftoppm', '-f', str(pno), '-l', str(pno), '-r', '200', '-png', '-singlefile', PDF, tmp], check=True)
        im = Image.open(tmp + '.png').convert('RGB')
        os.remove(tmp + '.png')
        w, h = im.size
        body = im.crop((0, 0, w, int(h * 0.90)))           # the page number sits in the last tenth
        box = ImageOps.invert(body.convert('L')).point(lambda v: 255 if v > 24 else 0).getbbox()
        pad = 12
        im = body.crop((max(0, box[0] - pad), max(0, box[1] - pad), min(w, box[2] + pad), min(body.size[1], box[3] + pad)))
        im.quantize(colors=64, method=Image.Quantize.MEDIANCUT).save(dest, optimize=True)
    return f'fig/p{pno}.png'


def part2():
    parts = []
    files = sorted(glob.glob(os.path.join(SRC, 'p[0-9][0-9][0-9].md')))
    assert len(files) == 142, len(files)
    for f in files:
        pno = int(re.search(r'p(\d+)\.md$', f).group(1))
        if pno == 106:
            continue                    # the Part II title page
        text = open(f, encoding='utf-8').read()
        cont = '<!-- cont -->' in text
        if pno == CHARTS_FROM:
            parts.append(dict(label='Part II · Charts', title='Charts', part=2, blocks=[]))
        if pno >= CHARTS_FROM:
            parts[-1]['blocks'].append(dict(type='img', src=chart_image(pno), full=True,
                                            alt=f'The colour charts of page {pno - 105} of Part II, as printed; their text follows'))
        in_title = False
        for k, (kind, x) in enumerate(page_blocks(text)):
            if kind == 'part':
                m = re.fullmatch(r'CHAPTER (\d)', x)
                if m:
                    title, ch = TITLES[m.group(1)]
                    parts.append(dict(label=f'Part II · Chapter {m.group(1)}', title=title, sangaha_ch=ch, part=2, blocks=[]))
                    in_title = True
                else:
                    assert in_title, (pno, x)       # the title lines under "CHAPTER n"
                continue
            in_title = False
            assert kind != 'title', (pno, x)
            blocks = parts[-1]['blocks']
            if k == 0 and cont:
                last = blocks[-1]
                assert kind == 'p' and last['type'] == 'p', (pno, kind)
                last['text'] += ('' if last['text'].endswith('-') else ' ') + x     # "tongue-" / "consciousness)": the hyphen of a compound
                continue
            if kind == 'pre':
                blocks.append(dict(type='pre', text=x))
            elif kind == 'table':
                blocks.append(table_block(x))
            elif kind == 'lines':
                blocks.append(dict(type='lines', items=x))
            else:
                blocks.append(dict(type=kind, text=x))
    return parts


def main():
    path = os.path.join(ROOT, 'data', 'fundamental.json')
    book = json.load(open(path, encoding='utf-8'))
    part1 = [c for c in book['chapters'] if c.get('part') != 2]
    for c in part1:
        if re.fullmatch(r'Chapter \d+', c['label']):
            c['label'] = 'Part I · ' + c['label']
    parts = part2()
    for c in parts:
        assert c['blocks'], c['title']
    chapters = part1 + parts
    for i, c in enumerate(chapters):
        c['num'] = str(i)
    book['chapters'] = [{k: c[k] for k in ('num', 'label', 'title', 'sangaha_ch', 'part', 'blocks') if k in c} for c in chapters]
    with open(path, 'w', encoding='utf-8') as fh:
        json.dump(book, fh, ensure_ascii=False, indent=0)
    for c in book['chapters']:
        print(c['num'], c['label'], '|', c['title'], len(c['blocks']), c.get('sangaha_ch', ''))
    doubt = [(c['title'], m) for c in parts for b in c['blocks'] for t in [b.get('text', '')] + b.get('items', [])
             for m in re.findall(r'\S+⟨\?⟩', t)]
    print('⟨?⟩:', doubt)
    for kind, t in PROBLEMS:
        print('markup', kind, t[:160])


if __name__ == '__main__':
    main()
