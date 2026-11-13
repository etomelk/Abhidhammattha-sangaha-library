"""Build data/lakkhana.json: "Characteristic, Function, Manifestation & Proximate Cause
(lakkhaṇa-rasa-paccupaṭṭhāna-padaṭṭhāna)" — the four defining devices of every ultimate reality, aggregate
by aggregate (matter, consciousness, feeling, perception, formations), in English with the Pāli of the
commentaries (DhsA, Vism) beside it; 22 pages, PDF from Word (Mac, 2018). Read with PyMuPDF:

python3 scripts/lakkhana/convert.py Lakkhana-r-p-p.pdf

- The Pāli is set in the old Mac font "Norman", which puts other letters for the Pāli ones; NORMAN turns
  them into Unicode: å ā, ˆ ṇ, Ë ū, ¥ ī, ∫ ṅ, ¬ ḷ, ∂ ḍ, ◊ ṃ, and the no-break space ṭ (paccupa  håna =
  paccupaṭṭhāna). Only spans in that font are mapped.
- Each item, "(n) The earth-element   pathavī-dhātu", becomes a heading and a table with a row for each
  device — Characteristic (C), Function (F), Manifestation (M), Proximate cause (P) — the English on the
  left, the Pāli on the right (the Pāli column of the page, x ≥ 300, is matched to the row whose English
  starts at or above it), and the item's references under it.
- One part per aggregate; the running heads, page numbers and the notes on abbreviations at the feet of
  the pages are kept once, at the end."""
import json
import os
import re
import sys

import pymupdf

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..')
NORMAN = str.maketrans({'å': 'ā', 'ˆ': 'ṇ', 'Ë': 'ū', '¥': 'ī', '∫': 'ṅ', '¬': 'ḷ', '∂': 'ḍ', '◊': 'ṃ', '\xa0': 'ṭ',
                        'Å': 'Ā'})
ROWS = [(r'^\(C\)|^\(It has the characteristic of\)', 'Characteristic'),
        (r'^\(F\)|^\(Its function is\)', 'Function'),
        (r'^\(M\)|^\(It is manifested\)', 'Manifestation'),
        (r'^\(P\)|^\(Its proximate c\w+ is\)', 'Proximate cause')]
SPLIT = 300


def lexicon():
    words = set()
    for slug in ('sangaha', 'vibhavini', 'paramattha', 'anudipani'):
        d = json.load(open(os.path.join(ROOT, 'data', f'{slug}.json'), encoding='utf-8'))
        for c in d['chapters']:
            for b in c['blocks']:
                words |= set(w.lower() for w in re.findall(r'[a-zāīūṃṅñṭḍṇḷ]+', b.get('text', '') or ''))
    return words


LEX = None


def pali(t):
    """the Pāli column: the Norman letters, and the ṭ that pdftotext gives as a space (paccupa håna)"""
    global LEX
    t = t.translate(NORMAN)
    if LEX is None:
        LEX = lexicon()

    def join(m):
        a, b = m.group(1), m.group(2)
        for mid in ('ṭṭ', 'ṭ'):
            w = (a + mid + b).lower()
            if any(w in x for x in LEX if len(x) >= len(w)) if len(w) < 9 else w in LEX:
                return a + mid + b
        return a + ('ṭṭ' if b.startswith('h') else 'ṭ') + b
    # a letter, one space, a letter, inside a word of the Pāli column (the space was the ṭ)
    return re.sub(r'(\w*[aāiīuūeoṃ]) (h?[aāiīuūeo]\w*)', join, t)


def split_line(l):
    """a layout line -> (English, Pāli): the Pāli column starts after a gap at or beyond column 60"""
    m = None
    for g in re.finditer(r'\s{3,}(?=\S)', l):
        if g.end() >= 60:
            m = g
            break
    if m:
        return l[:m.start()].strip(), l[m.end():].strip()
    if len(l) - len(l.lstrip()) >= 60:
        return '', l.strip()
    return l.strip(), ''


def main(src):
    import subprocess
    text = subprocess.run(['pdftotext', '-layout', src, '-'], capture_output=True, text=True).stdout
    pages = text.split('\f')
    parts = [dict(label='Introduction', title='The four defining devices', blocks=[])]
    notes = []
    item = None

    def flush():
        nonlocal item
        if not item:
            return
        b = parts[-1]['blocks']
        b.append(dict(type='h', text=item['head'] + (f' — {item["pali"]}' if item['pali'] else '')))
        rows = [[name, re.sub(r'\s+', ' ', e).strip(), re.sub(r'\s+', ' ', p).strip()] for name, e, p in item['rows']]
        if rows:
            b.append(dict(type='table', head=['', 'English', 'Pāli'], rows=rows, labels=True))
        for t in item['extra']:
            b.append(dict(type='p', text=t))
        if item['ref']:
            b.append(dict(type='p', text=re.sub(r'\)\s*\d$', ')', item['ref']), ind=1))
        item = None

    for pno, pg in enumerate(pages):
        if pno == 0:
            continue
        lines = pg.split('\n')
        # the notes at the foot of a page: after a line that is a lone footnote number
        foot = next((i for i, l in enumerate(lines) if re.fullmatch(r'\s*\d\s*', l) and i > len(lines) * 0.6), None)
        if foot is not None:
            for l in lines[foot + 1:]:
                l = re.sub(r'\s+', ' ', l).strip()
                if l and l not in notes and not re.search(r'Characteristic, Function, Manifestation', l):
                    notes.append(l.translate(NORMAN))
            lines = lines[:foot]
        for l in lines:
            if not l.strip() or re.search(r'Characteristic, Function, Manifestation & Proximate [Cc]ause( of the|$)', l) and '!' in l:
                continue
            if re.fullmatch(r'\s*!?\d+!?\s*', l):
                continue
            en, pa = split_line(l)
            pa = pali(pa) if pa else ''
            en = en.translate(str.maketrans({'å': 'ā', 'ˆ': 'ṇ', 'Ë': 'ū', '¥': 'ī', '∫': 'ṅ', '¬': 'ḷ', '∂': 'ḍ', '◊': 'ṃ'}))
            m = re.match(r'^(\(\d+ of [A-Za-z ]+\) )?(The \w+ aggregate)\b(.*)$', en)
            if m:
                flush()
                parts.append(dict(label=m.group(2)[4:].capitalize(), title=en + (f' — {pa}' if pa else ''), blocks=[]))
                continue
            if en and re.match(r'^(The )?[A-Z][\w ()-]* - \d+$', en) and not re.match(r'^\(\d+\)', en):
                flush()                                       # a group of mental factors: "The Universals - 7"
                parts[-1]['blocks'].append(dict(type='h4', text=en + (f' — {pa}' if pa else '')))
                continue
            if en:
                mi = re.match(r'^\((\d+)\) (.*)$', en)
                if mi and parts[-1]['label'] != 'Introduction' and not re.match(r'^(its|the) ', mi.group(2)):
                    flush()
                    item = dict(head=f'({mi.group(1)}) {mi.group(2)}', pali=pa, rows=[], extra=[], ref='')
                    continue
                if item is not None:
                    k = next((name for pat, name in ROWS if re.match(pat, en)), None)
                    if k:
                        item['rows'].append([k, re.sub(r'^\([CFMP]\)\s*', '', en), ''])
                    elif item['rows']:
                        item['rows'][-1][1] += ' ' + en
                    else:
                        item['extra'].append(en)
                else:
                    pb = parts[-1]['blocks']
                    if pb and pb[-1]['type'] == 'p' and not pb[-1].get('ind') and not re.match(r'^\(\d\)', en) and not pb[-1]['text'].endswith(('.', ':', ')')):
                        pb[-1]['text'] += ' ' + en
                    else:
                        pb.append(dict(type='p', text=en))
            if pa:
                if item is None:
                    if parts[-1]['blocks'] or parts[-1]['label'] == 'Introduction':
                        parts[-1]['blocks'].append(dict(type='p', text=pa, ind=2))
                    continue
                if re.match(r'^\((DhsA|Vs|Vism|Dhs|Vbh|Abhi|As|Mil|Pts)\b', pa) or re.match(r'^\([A-Z][A-Za-z]*\.\d', pa):
                    item['ref'] = (item['ref'] + ' ' + pa).strip()
                elif not item['rows']:
                    item['pali'] = (item['pali'] + ' ' + pa).strip()
                else:
                    item['rows'][-1][2] += ' ' + pa
    flush()
    if notes:
        parts.append(dict(label='Notes', title='Abbreviations and notes at the foot of the pages',
                          blocks=[dict(type='p', text=n) for n in notes]))
    chapters = [dict(num=str(i), label=p['label'], title=p['title'], blocks=p['blocks']) for i, p in enumerate(parts)]
    for c in chapters:
        for b in c['blocks']:
            if 'text' in b:
                b['text'] = re.sub(r'(\w)- (\w)', r'\1-\2', b['text'])
            if 'rows' in b:
                b['rows'] = [[re.sub(r'(\w)- (\w)', r'\1\2' if i == 1 else r'\1-\2', x) for i, x in enumerate(r)] for r in b['rows']]
    json.dump(dict(chapters=chapters, glossary=[]), open(os.path.join(ROOT, 'data', 'lakkhana.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=0)
    for c in chapters:
        print(f'  {c["label"]:14} {c["title"][:60]:60} items {sum(1 for b in c["blocks"] if b["type"] == "h"):3} tables {sum(1 for b in c["blocks"] if b["type"] == "table"):3}', file=sys.stderr)


if __name__ == '__main__':
    main(sys.argv[1])
