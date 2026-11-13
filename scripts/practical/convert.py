"""Build data/practical.json and practical/fig/*.png: the Practical Abhidhamma Course (version 1.1,
April 2016; LaTeX/LuaTeX PDF, practicalabhidhamma.com), read with PyMuPDF, which gives each span's
font size and style:

python3 scripts/practical/convert.py Practical-Abhidhamma.pdf

- 20.7 pt "N Title" opens a part (the course's lessons and appendices); 17.2 pt is a heading,
  14.3 pt a sub-heading; 12 pt is the text; bold and italic spans keep their **…** and *…*.
- Footnotes: a 7 pt number at the foot of the page opens a note (10 pt text); an 8 pt number in the
  text is its reference. Notes are numbered anew in each part, set under the paragraph that cites them.
- Figures (102): the course draws its diagrams as vector graphics with words laid over them, which
  text cannot keep. Each is cropped from the page, from the end of the text above it to the end of its
  caption ("Figure n: …", 10.9 pt), and kept as an image (practical/fig/<n>.png); the caption is also
  the image's alt text. The words inside a figure are left out of the text.
- A paragraph starts where a line is indented (x ≈ 88) or after a heading, figure or list; a page's
  first line flush left continues the paragraph of the page before. Line-end hyphens are joined unless
  the course writes the word with the hyphen inside a line.
- Each lesson on a chapter of the Saṅgaha carries sangaha_ch (SANGAHA) for the Saṅgaha map."""
import json
import os
import re
import sys

import pymupdf
from PIL import Image

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..')
SANGAHA = {3: 1, 4: 2, 5: 6, 6: 5, 8: 4}
BODY, NOTE_MARK, SUP, NOTE, CAPTION, H4, H3, H2 = 12.0, 7.0, 8.0, 10.0, 10.9, 14.3, 17.2, 20.7


def prose(b):
    """a block of running text (its lines run across the measure), not the cells of a table"""
    ws = [l['bbox'][2] - l['bbox'][0] for l in b['lines']]
    return sum(ws) / len(ws) > 300


def near(a, b):
    return abs(a - b) < 0.25


def styled(spans):
    """spans -> text with **bold** and *italic*, and ⟨sup:n⟩ for an 8 pt note number"""
    out = []
    for s in spans:
        t = s['text']
        if near(s['size'], SUP) and t.strip().isdigit():
            out.append(f'⟨sup:{t.strip()}⟩')
            continue
        if not t.strip():
            out.append(t)
            continue
        lead, core, trail = re.match(r'^(\s*)(.*?)(\s*)$', t).groups()
        b, i = s['flags'] & 16, s['flags'] & 2
        if b:
            core = f'**{core}**'
        elif i:
            core = f'*{core}*'
        out.append(lead + core + trail)
    t = ''.join(out)
    t = re.sub(r'\*\*(\s*)\*\*', r'\1', t)                              # adjacent bold spans joined, their space kept
    t = re.sub(r'(?<!\*)\*(?!\*)(\s*)(?<!\*)\*(?!\*)', r'\1', t)      # adjacent italic spans joined
    return t


def main(src):
    doc = pymupdf.open(src)
    figdir = os.path.join(ROOT, 'practical', 'fig')
    os.makedirs(figdir, exist_ok=True)
    plain = ' '.join(pg.get_text() for pg in doc)
    hyph = {w.lower() for w in re.findall(r'\w+-\w+', re.sub(r'-\n', ' ', plain))}
    parts = [dict(num='0', label='Front matter', title='Preface and Acknowledgements', blocks=[], notes={})]
    para = None           # the paragraph being built (dict with 'text')
    note = None           # the footnote being built: [global number, text]
    nfig = 0

    def end_para():
        nonlocal para
        para = None

    def add_text(t, indent):
        nonlocal para
        if para is not None and not indent:
            if para['text'].endswith('-') and re.match(r'\w', t):
                a = re.search(r'(\w+)-$', para['text'])
                bword = re.match(r'\w+', t).group(0)
                para['text'] = para['text'] + t if a and f'{a.group(1)}-{bword}'.lower() in hyph else para['text'][:-1] + t
            else:
                para['text'] += ' ' + t
            return
        para = dict(type='p', text=t)
        parts[-1]['blocks'].append(para)

    for pno in range(1, len(doc)):            # page 1 is the contents
        pg = doc[pno]
        d = pg.get_text('dict')
        blocks = [b for b in d['blocks'] if b['type'] == 0]
        # figures: a caption block; the figure runs from the end of the prose above it
        caps = [b for b in blocks if b['lines'] and near(b['lines'][0]['spans'][0]['size'], CAPTION)
                and re.match(r'\s*Figure \d+:', ''.join(s['text'] for s in b['lines'][0]['spans']))]
        skip = set()
        figs = {}
        for cb in caps:
            top = 60
            for b in blocks:
                sz = b['lines'][0]['spans'][0]['size']
                if b['bbox'][3] <= cb['bbox'][1] + 1 and b is not cb and (
                        (near(sz, BODY) and prose(b)) or sz > 14):
                    top = max(top, b['bbox'][3])
            for c2 in caps:
                if c2 is not cb and c2['bbox'][3] <= cb['bbox'][1]:
                    top = max(top, c2['bbox'][3])
            clip = pymupdf.Rect(60, top + 2, 535, cb['bbox'][3] + 3)
            for b in blocks:
                if b is cb or (b['bbox'][1] >= top - 1 and b['bbox'][3] <= cb['bbox'][1] + 1):
                    skip.add(id(b))
            nfig += 1
            name = f'{nfig:03d}.png'
            pix = pg.get_pixmap(matrix=pymupdf.Matrix(1.6, 1.6), clip=clip)
            im = Image.frombytes('RGB', (pix.width, pix.height), pix.samples)
            im.quantize(colors=48, method=Image.Quantize.MEDIANCUT).save(os.path.join(figdir, name), optimize=True)
            cap = re.sub(r'\s+', ' ', ' '.join(''.join(s['text'] for s in l['spans']) for l in cb['lines'])).strip()
            figs[id(cb)] = dict(type='img', src=f'fig/{name}', alt=cap)
        for b in blocks:
            if id(b) in figs:
                end_para()
                parts[-1]['blocks'].append(figs[id(b)])
                continue
            if id(b) in skip:
                continue
            first = b['lines'][0]['spans'][0]
            text = re.sub(r'\s+', ' ', ''.join(s['text'] for l in b['lines'] for s in l['spans'])).strip()
            if b['bbox'][1] > 780 and re.fullmatch(r'\d{1,3}', text):
                continue                                  # page number
            if near(first['size'], H2):
                end_para()
                m = re.match(r'^(\d+)\s*(.*)$', text)
                k = int(m.group(1)) if m else None
                title = m.group(2) if m else text
                p = dict(num=str(len(parts)), label=(f'Lesson {k}' if k and k <= 8 else (title.split(' –')[0] if 'Appendix' in title else title)),
                         title=title, blocks=[], notes={})
                if k in SANGAHA:
                    p['sangaha_ch'] = SANGAHA[k]
                parts.append(p)
                continue
            if near(first['size'], H3) or near(first['size'], H4):
                end_para()
                # the lines of a heading: joined with a space, or closed up over a hyphen that only breaks the word
                text = ''
                for l in b['lines']:
                    x = ''.join(s['text'] for s in l['spans']).strip()
                    if re.search(r'[a-z]-$', text) and re.match(r'[a-z]', x):
                        text = text[:-1] + x
                    else:
                        text = (text + ' ' + x).strip()
                text = re.sub(r'\s+', ' ', text)
                if len(text) > 100:                       # a reader's question, set in bold: a paragraph, not a heading
                    parts[-1]['blocks'].append(dict(type='p', text=f'**{text}**'))
                else:
                    parts[-1]['blocks'].append(dict(type='h' if near(first['size'], H3) else 'h4', text=text))
                continue
            if near(first['size'], NOTE_MARK) or (near(first['size'], NOTE) and b['bbox'][1] > 450 and note is not None and not near(first['size'], BODY)):
                # footnotes: each line that starts with a 7 pt number opens a note
                for l in b['lines']:
                    sp = l['spans']
                    if sp and near(sp[0]['size'], NOTE_MARK) and sp[0]['text'].strip().isdigit():
                        note = [int(sp[0]['text']), styled(sp[1:]).strip()]
                        parts[-1]['notes'][note[0]] = note
                    elif note is not None:
                        t = styled(sp).strip()
                        note[1] = (note[1][:-1] + t) if note[1].endswith('-') and not note[1].endswith('--') else (note[1] + ' ' + t)
                continue
            # text (12 pt; smaller text outside the foot is a table or a list of the course)
            for li, l in enumerate(b['lines']):
                t = styled(l['spans']).strip()
                if not t:
                    continue
                x = l['bbox'][0]
                bullet = re.match(r'^(•|–|\d+\.|\([a-z0-9]+\))\s', re.sub(r'^\*+', '', t))
                if (li == 0 and not bullet and para is not None and para.get('text') and re.match(r'[a-z(“]', t)
                        and not re.search(r'[.:!?”]$', para['text'])):
                    add_text(t, False)                    # a list item or paragraph that goes on in a new block
                elif bullet or (li == 0 and x > 80):
                    if bullet:
                        para = dict(type='p', text=t, ind=1)
                        parts[-1]['blocks'].append(para)
                    else:
                        add_text(t, True)
                elif li == 0 and para is not None and para.get('ind') and x < 80:
                    add_text(t, True)                     # the text after a list
                else:
                    add_text(t, False)
    # footnotes: numbered anew in each part, set after the paragraph that cites them
    chapters = []
    for p in parts:
        loc, out = {}, []
        for b in p['blocks']:
            if b.get('text'):
                def ref(m):
                    g = int(m.group(1))
                    if g not in p['notes']:
                        return ''
                    loc.setdefault(g, len(loc) + 1)
                    return f'[^{loc[g]}]'
                b['text'] = re.sub(r'⟨sup:(\d+)⟩', ref, b['text'])
            out.append(b)
            cited = [g for g in re.findall(r'\[\^(\d+)\]', b.get('text', ''))]
            for k in cited:
                g = next(g for g, v in loc.items() if v == int(k))
                out.append(dict(type='p', note=int(k), text=p['notes'][g][1]))
        c = dict(num=p['num'], label=p['label'], title=p['title'], blocks=out)
        if p.get('sangaha_ch'):
            c['sangaha_ch'] = p['sangaha_ch']
        chapters.append(c)
    json.dump(dict(chapters=chapters, glossary=[]), open(os.path.join(ROOT, 'data', 'practical.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=0)
    for c in chapters:
        bl = c['blocks']
        print(f'  {c["label"]:12} {c["title"][:44]:44} paras {sum(1 for b in bl if b["type"] == "p" and not b.get("note")):4} '
              f'notes {sum(1 for b in bl if b.get("note")):3} figures {sum(1 for b in bl if b["type"] == "img"):3} headings {sum(1 for b in bl if b["type"] in ("h", "h4")):3}', file=sys.stderr)
    print(f'{nfig} figures cropped', file=sys.stderr)


if __name__ == '__main__':
    main(sys.argv[1])
