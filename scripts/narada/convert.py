"""Build data/narada.json: Nārada Thera, A Manual of Abhidhamma (Abhidhammattha-Saṅgaha of
Anuruddhācariya, edited in the original Pāli text with English translation and explanatory notes),
from the palikanon.com web edition as a PDF (Word, 2010; the Preface is dated 14.7.1978):

pdftotext -layout Abhidhammattha-Sangaha-Narada.pdf work/narada.txt
python3 scripts/narada/convert.py work/narada.txt

- One part per chapter, the Preface first. Chapter VIII (Paccaya) is missing from this PDF: its
  contents list it, but the text runs from Chapter VII to Chapter IX.
- Nārada numbers his sections § 1, § 2 … anew in each chapter, once before the Pāli and again
  before his English. The first is the anchor: key chapter × 1000 + n (#p1003 and #p1-3), shown
  as "§ 3"; the second "§ 3." is left out of the English, which follows.
- Each § is tied to the paragraph of the Sixth Council Saṅgaha whose Pāli it gives
  (data/narada-key.json, made by match()), so a chip opens the same place in the Saṅgaha and the
  Vibhāvinī; places where the match is not certain get no chip.
- The diagrams are the PDF's text tables, shown as preformatted text with their columns.
- A short line standing alone, without end punctuation, is a heading; "Notes:" a sub-heading."""
import difflib
import json
import os
import re
import sys
import unicodedata

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..')
ROMAN = {'I': 1, 'II': 2, 'III': 3, 'IV': 4, 'V': 5, 'VI': 6, 'VII': 7, 'VIII': 8, 'IX': 9}
RN = ['', 'I', 'II', 'III', 'IV', 'V', 'VI', 'VII', 'VIII', 'IX']
SEC = re.compile(r'^§\s*(\d+)\s*\.?\s*')


def fold(s):
    s = unicodedata.normalize('NFD', s.lower())
    s = ''.join(c for c in s if unicodedata.category(c) != 'Mn')
    return re.sub(r'[^a-z]', '', s)


def is_table(lines):
    wide = sum(1 for l in lines if re.search(r'\S {3,}\S', l.strip()))
    return len(lines) >= 2 and wide * 2 >= len(lines) or (len(lines) == 1 and re.search(r'\S {6,}\S', lines[0].strip()))


ENGLISH = set('''of the and in on to with for a an by from as or is are its his section summary consciousness
mental states matter process processes analysis different types kinds classes sphere moral immoral rootless
beautiful supra mundane form formless sense door doors object objects base bases feeling roots functions
planes plane rebirth death kamma relations culture method purification emancipation individuals attainments
diagram diagrams introductory verse subject introduction contents definition combinations notes four five
twofold threefold fourfold sixfold great essentials material phenomena groups arising occurrence nibbāna
aspirations stages signs knowledge temperaments subjects suitability supernormal path paths fruits'''.split())


def is_heading(t):
    words = set(re.findall(r"[a-zāīūṃṅñṭḍṇḷ]+", t.lower()))
    if not (t.startswith('(') or t.isupper() or words & ENGLISH):
        return False          # a line of Pāli verse standing alone
    if re.search(r"\b(is|are|was|were|deal|deals|termed|rooted|purified)\b", t) or re.search(r"[.:;!?-]['\"’”]?$", t):
        return False          # a sentence
    return (len(t) <= 90 and len(t.split()) <= 12 and ',' not in t and not re.search(r'[.:;!?-]$', t)
            and not re.match(r'^[\d(§*•]', t) and t[0].isupper() or re.match(r'^\(.*\)$', t) and len(t) < 70
            and not re.match(r'^\(\d', t))


def blocks_of(text):
    """paragraphs (lines between blank lines), with page breaks dropped and a lone page number left out"""
    text = text.replace('\f', '\n')
    out, cur = [], []
    for line in text.split('\n'):
        if line.strip():
            cur.append(line.rstrip())
        elif cur:
            out.append(cur)
            cur = []
    if cur:
        out.append(cur)
    # a chapter title stands in a block of its own (the web page sets the running title
    # "Abhidhammattha-Sangaha" just above it, which is left out)
    res = []
    for b in out:
        k = next((i for i, l in enumerate(b) if re.match(r'^\s*CHAPTER [IVX]+ - ', l)), None)
        if k is None:
            res.append(b)
            continue
        before = [l for l in b[:k] if l.strip() != 'Abhidhammattha-Sangaha']
        res += [x for x in (before, [b[k]], b[k + 1:]) if x]
    return res


def main(src):
    text = open(src, encoding='utf-8').read()
    starts = [m.start() for m in re.finditer(r'(?m)^\s*CHAPTER [IVX]+ - ', text)]
    body_from = starts[9] if len(starts) > 9 else starts[len(starts) // 2]   # after the contents (they list the 9 chapters)
    pref = text.find('PREFACE')
    parts = [dict(label='Preface', title='Preface', ch=None, blocks=[])]
    seen = set()
    ch = None
    for raw in blocks_of(text[pref:]):
        raw = [re.sub(r'^\s*•\s+', '', l) for l in raw]          # list bullets of the web page
        first = raw[0].strip()
        m = re.match(r'^CHAPTER ([IVX]+) - (.*)$', first)
        if m and len(raw) > 1:
            # the chapter title is followed by the book's running title, or by text
            raw = raw[1:]
            raw_is_title = False
        else:
            raw_is_title = bool(m)
        if m:
            ch = ROMAN[m.group(1)]
            title = m.group(2).strip()
            parts.append(dict(label=f'Chapter {m.group(1)}', title=title[0].upper() + title[1:].lower() if title.isupper() else title, ch=ch, blocks=[]))
            if raw_is_title:
                continue
            first = raw[0].strip()
        part = parts[-1]
        if is_table(raw):
            part['blocks'].append(dict(type='pre', text='\n'.join(raw)))
            continue
        t = re.sub(r'\s+', ' ', ' '.join(l.strip() for l in raw)).strip()
        if re.fullmatch(r'\d{1,3}|_+', t):
            continue
        if t in ('Notes:', 'Notes', 'Note:'):
            part['blocks'].append(dict(type='h4', text='Notes'))
            continue
        if t == 'Diagrams:':
            part['blocks'].append(dict(type='h', text='Diagrams'))
            continue
        sm = SEC.match(t)
        if sm and ch:
            n = int(sm.group(1))
            rest = t[sm.end():].strip()
            key = ch * 1000 + n
            if key not in seen:
                seen.add(key)
                part['blocks'].append(dict(type='p', pnum=key, label=f'§ {n}', alias=[f'p{ch}-{n}'], text=rest or '', pali=True))
            elif rest:
                part['blocks'].append(dict(type='p', text=rest))
            continue
        if len(raw) == 1 and is_heading(t) and part['label'] != 'Preface' or (part['label'] == 'Preface' and t.isupper() and len(t) < 40):
            part['blocks'].append(dict(type='h', text=t.title() if t.isupper() else t))
            continue
        part['blocks'].append(dict(type='p', text=t))
    # a list number standing alone ("1.") joins the line that follows it
    for p in parts:
        bl, res = p['blocks'], []
        i = 0
        while i < len(bl):
            b = bl[i]
            if (b['type'] == 'p' and not b.get('pnum') and re.fullmatch(r'\(?\d{1,2}[.)]', b['text'] or '')
                    and i + 1 < len(bl) and bl[i + 1]['type'] == 'p' and not bl[i + 1].get('pnum')):
                bl[i + 1]['text'] = b['text'] + ' ' + bl[i + 1]['text']
                i += 1
                continue
            res.append(b)
            i += 1
        p['blocks'] = res
    # a § with no text of its own takes the Pāli that follows it
    for p in parts:
        bl = p['blocks']
        for i, b in enumerate(bl):
            if b.get('pnum') and not b['text'] and i + 1 < len(bl) and bl[i + 1]['type'] == 'p' and not bl[i + 1].get('pnum'):
                b['text'] = bl[i + 1]['text']
                bl[i + 1]['_drop'] = True
        p['blocks'] = [b for b in bl if not b.get('_drop')]
    # Chapter VIII, missing from the web edition, from the transcription of the 1956–57 edition (scripts/narada/ch8/)
    ch8 = chapter8()
    k = next(i for i, p in enumerate(parts) if p['ch'] == 9)
    parts.insert(k, ch8)
    chapters = [dict(num=str(i), label=p['label'], title=p['title'], blocks=p['blocks'], **({'sangaha_ch': p['ch']} if p['ch'] else {}))
                for i, p in enumerate(parts)]
    for c in chapters:
        for b in c['blocks']:
            b.pop('pali', None)
        diagram14(c['blocks'])
        c['blocks'] = note_heads(c['blocks'])
    json.dump(dict(chapters=chapters, glossary=[]), open(os.path.join(ROOT, 'data', 'narada.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=0)
    match(chapters)
    for c in chapters:
        ks = [b['pnum'] % 1000 for b in c['blocks'] if b.get('pnum')]
        print(f'  {c["label"]:12} {c["title"][:44]:44} §§ {len(ks):3} {ks[:3]}…{ks[-2:]}  tables {sum(1 for b in c["blocks"] if b["type"] == "pre")}', file=sys.stderr)


def note_heads(bl):
    """The notes give each term a line of its own that ends in a dash ("13. Vicikicchā-") with the note in the
    next paragraph: the two are set as one, the term in bold; a line "Notes-" is a heading."""
    out = []
    i = 0
    while i < len(bl):
        b = bl[i]
        t = b.get('text', '') if b['type'] == 'p' else ''
        nx = bl[i + 1] if i + 1 < len(bl) else None
        if re.fullmatch(r'Notes\s*:?\s*-?\s*', t) and not b.get('pnum'):
            out.append(dict(type='h4', text='Notes'))
            i += 1
            continue
        if (re.search(r'\w-$', t) and not b.get('pnum') and nx and nx['type'] == 'p' and not nx.get('pnum')
                and re.match(r'[a-zāīū(]', nx['text'])):
            bl[i + 1] = dict(b, text=t + nx['text'])          # a word broken over two paragraphs
            i += 1
            continue
        if (len(t) > 80 and re.search(r'[a-zāīū,]$', t) and not b.get('pnum') and nx and nx['type'] == 'p' and not nx.get('pnum')
                and re.match(r'[a-zāīū]', nx['text']) and not re.match(r'[ivx]{1,4} ?\.\s', nx['text'])):
            bl[i + 1] = dict(b, text=t + ' ' + nx['text'])    # a paragraph broken in two (at a page of the web edition)
            i += 1
            continue
        m = re.fullmatch(r'(\d{1,3}\.\s+\S.{0,70}?|[A-Z][\wāīūṃñ]+(?: [\wāīūṃñ]+)?)\s*-\s*', t)
        if m and not b.get('pnum') and nx and nx['type'] == 'p' and not nx.get('pnum') and not re.match(r'\d{1,3}\.\s', nx['text']):
            out.append(dict(b, text=f'**{m.group(1)}** — {nx["text"]}'))
            i += 2
            continue
        out.append(b)
        i += 1
    return out


def diagram14(bl):
    """Diagram XIV (the immoral states in the nine categories of evil): its column heads are set upright in the
    web edition and come out as rows of single letters; the chart is rebuilt here as a table."""
    k = next((i for i, b in enumerate(bl) if b['type'] == 'h' and b['text'] == 'Diagram XIV'), None)
    if k is None:
        return
    j = k + 1
    while j < len(bl) and not (bl[j]['type'] == 'pre' and bl[j]['text'].startswith('1. lobha')):
        j += 1
    e = j
    while e < len(bl) and bl[e]['type'] == 'pre' and re.match(r'\d{1,2}\. ', bl[e]['text']):
        e += 1
    rows = [bl[n]['text'] for n in range(j, e)]
    cols = [m.start() for m in re.finditer(r'\+', rows[0])]
    out = []
    for r in rows:
        out.append([r[:cols[0] - 4].strip(), r[cols[0] - 4:cols[0]].strip()] + ['+' if len(r) > c and r[c] == '+' else '' for c in cols])
    # the web edition's last rows have their marks shifted; set as the counts in its own "In" column
    # and the lists of Ch. VII §§3–13 have them (middha: a hindrance only; ahirika, anottappa: defilements;
    # issā, macchariya: fetters of the Abhidhamma list)
    fix = {'10': 5, '11': 8, '12': 8, '13': 7, '14': 7}
    for r in out:
        n = r[0].split('.')[0]
        if n in fix:
            r[2:] = ['+' if c == fix[n] else '' for c in range(len(cols))]
    head = ['Immoral state', 'In', 'āsava', 'ogha', 'yoga', 'gantha', 'upādāna', 'nīvaraṇa', 'anusaya', 'saṃyojana', 'kilesa']
    bl[k + 1:e] = [dict(type='table', head=head, rows=out, vhead=True)]


def chapter8():
    """Chapter VIII from scripts/narada/ch8/*.md, transcribed from the page images of the 1956–57 edition
    (Buddha Sāsana Council reprint, Rangoon 1970, pp. 73–103). The markup: '# ' the chapter's Pāli title,
    '## ' a heading, '### ' a sub-heading, '§ n' before the paragraph that opens Nārada's section n
    (the first one, the Pāli, is the anchor), '> ' a line of verse, '- ' a list item, '[fig N: caption]'
    a diagram kept as an image (narada/fig/ch8-N.png), '[^1]' and '[^1]: …' a footnote, '@page n' the
    printed page (not shown). A paragraph broken at the end of a file runs on into the next."""
    d = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'ch8')
    text = '\n\n'.join(open(os.path.join(d, f), encoding='utf-8').read() for f in sorted(os.listdir(d)) if f.endswith('.md'))
    text = re.sub(r'<!--.*?-->', '', text, flags=re.S)
    text = re.sub(r'⟨pg:\d+⟩', '', text)
    text = re.sub(r'(?m)^@page \d+\s*$', '', text)
    paras = [x.strip() for x in re.split(r'\n\s*\n', text) if x.strip()]
    joined = []
    for x in paras:
        if joined and not re.match(r'^(#|§|>|-|\[|\d+\.)', x) and not re.match(r'^(#|§|>|\[)', joined[-1]) and (
                joined[-1].endswith('-') or x[:1].islower()):
            joined[-1] = joined[-1][:-1] + x if joined[-1].endswith('-') and x[:1].islower() else joined[-1] + ' ' + x
        else:
            joined.append(x)
    blocks, seen, pending, notes = [], set(), None, {}
    for x in joined:
        m = re.match(r'^\[\^(\d+)\]:\s*(.*)$', x, flags=re.S)
        if m:
            blocks.append(dict(type='p', note=int(m.group(1)), text=m.group(2)))
            continue
        if x.startswith('# '):
            blocks.append(dict(type='h', text=x[2:]))
        elif x.startswith('## '):
            blocks.append(dict(type='h', text=x[3:]))
        elif x.startswith('### '):
            blocks.append(dict(type='h4', text=x[4:]))
        elif re.match(r'^§ \d+$', x.split('\n')[0]):
            n = int(x.split()[1])
            rest = '\n'.join(x.split('\n')[1:]).strip()
            pending = n if 8000 + n not in seen else None
            if rest:
                x = rest
            else:
                continue
        m = re.match(r'^\[fig (\d+): (.*)\]$', x)
        if m:
            blocks.append(dict(type='img', src=f'fig/ch8-{m.group(1)}.png', alt=m.group(2)))
            continue
        if x.startswith('#'):
            continue
        lines = x.split('\n')
        if lines[0].startswith('> '):
            for i, l in enumerate(lines):
                b = dict(type='p', text=l[2:].strip(), ind=2)
                if i == 0 and pending:
                    b.update(pnum=8000 + pending, label=f'§ {pending}', alias=[f'p8-{pending}'])
                    seen.add(8000 + pending)
                    pending = None
                blocks.append(b)
            continue
        if lines[0].startswith('- '):
            items = re.split(r'\n(?=- )', x)
            for i, it in enumerate(items):
                b = dict(type='p', text=re.sub(r'\s+', ' ', it[2:]).strip(), ind=1)
                if i == 0 and pending:
                    b.update(pnum=8000 + pending, label=f'§ {pending}', alias=[f'p8-{pending}'])
                    seen.add(8000 + pending)
                    pending = None
                blocks.append(b)
            continue
        b = dict(type='p', text=re.sub(r'\s+', ' ', x).strip())
        if pending:
            b.update(pnum=8000 + pending, label=f'§ {pending}', alias=[f'p8-{pending}'])
            seen.add(8000 + pending)
            pending = None
        blocks.append(b)
    return dict(label='Chapter VIII', title='The Compendium of Relations (Paccaya-saṅgaha-vibhāga)', ch=8, blocks=blocks)


def match(chapters):
    """Tie each § of Nārada to the Saṅgaha paragraph whose Pāli it gives: the paragraph of the same chapter
    whose opening (folded: no diacritics, spaces or punctuation) is most like the opening of Nārada's Pāli,
    in order through the chapter, only above a clear likeness."""
    sg = json.load(open(os.path.join(ROOT, 'data', 'sangaha.json'), encoding='utf-8'))
    vri = {}
    for c in sg['chapters']:
        for b in c['blocks']:
            if b.get('pnum'):
                vri.setdefault(b['pnum'] // 1000, []).append((b['pnum'], fold(re.sub(r'⟨[^⟩]*⟩|\*\*', '', b['text']))[:60]))
    out, weak = {}, []
    lead = re.compile(r'^(\s*(\([ivx]+\)|\(\d+\)|\d+\.)\s*)+')
    for c in chapters:
        ch = c.get('sangaha_ch')
        if not ch:
            continue
        cand = vri.get(ch, [])
        secs = [b for b in c['blocks'] if b.get('pnum')]
        qs = [fold(lead.sub('', b['text']))[:50] for b in secs]
        S = [[(difflib.SequenceMatcher(None, q, v[:len(q)]).ratio() if len(q) >= 8 else 0) for _, v in cand] for q in qs]
        # the best order-keeping alignment of Nārada's sections to the edition's paragraphs (pairs >= 0.6)
        n, m = len(qs), len(cand)
        best = [[0.0] * (m + 1) for _ in range(n + 1)]
        for a in range(n - 1, -1, -1):
            for b_ in range(m - 1, -1, -1):
                take = S[a][b_] + best[a + 1][b_ + 1] if S[a][b_] >= 0.6 else -1
                best[a][b_] = max(take, best[a + 1][b_], best[a][b_ + 1])
        a = b_ = 0
        while a < n and b_ < m:
            if S[a][b_] >= 0.6 and best[a][b_] == S[a][b_] + best[a + 1][b_ + 1]:
                out[str(secs[a]['pnum'])] = cand[b_][0]
                a += 1
                b_ += 1
            elif best[a][b_] == best[a + 1][b_]:
                weak.append(f'{RN[ch]} § {secs[a]["pnum"] % 1000}')
                a += 1
            else:
                b_ += 1
        weak += [f'{RN[ch]} § {x["pnum"] % 1000}' for x in secs[a:]]
    json.dump(out, open(os.path.join(ROOT, 'data', 'narada-key.json'), 'w'), indent=0)
    print(f'narada-key.json: {len(out)} sections tied to the Saṅgaha; not tied: {", ".join(weak)}', file=sys.stderr)


if __name__ == '__main__':
    main(sys.argv[1])
