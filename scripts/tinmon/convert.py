"""Build data/tinmon.json: Dr. Mehm Tin Mon, Buddha Abhidhamma — Ultimate Science (Buddha Dharma
Education Association / BuddhaNet, 1995 text; PDF of 2003 from PageMaker), from its text layer:

pdftotext -layout Buddha-Abhidhamma-Ultimate-Science.pdf work/tinmon.txt
python3 scripts/tinmon/convert.py work/tinmon.txt

The PDF is set in an old Pāli font that puts accented Latin letters where the Pāli letters should be
(à for ā, ñ for ṭ, ü for ṃ …); FONT turns them into Unicode. The map was read from the words
themselves (pañisandhi = paṭisandhi, bhavaïga = bhavaṅga, KAMMAòòHâNA = KAMMAṬṬHĀNA) and checked
against the page images.

- Parts: the Preface and Introduction, the nine chapters (the Saṅgaha's own, so each part carries
  sangaha_ch), the Conclusion with About the Author.
- Paragraphs: a first-line indent starts a paragraph; an indented line that begins with a number is
  a list item, and its deeper-indented lines continue it; a line with a gap of three spaces or more
  inside it is a table row (the book's tables and word lists), kept with its columns. Page numbers
  are left out, and a paragraph runs on over a page break.
- A short line flush left after the end of a paragraph, and in Title Case or in brackets, is a heading.
- The charts the book refers to as "attached at the back" (Charts 1–10) are not in this PDF."""
import json
import os
import re
import sys

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..')
FONT = str.maketrans({'à': 'ā', 'ã': 'ī', 'å': 'ū', '¤': 'ñ', 'ñ': 'ṭ', 'õ': 'ṇ', 'ü': 'ṃ', 'ï': 'ṅ', 'ë': 'ḷ',
                      'ó': 'ṭ', 'ò': 'Ṭ', 'â': 'Ā', 'À': 'Ā', 'Ã': 'Ā', 'ä': 'Ī', 'æ': 'Ū', 'ö': 'Ṇ', '¥': 'Ñ'})
HYPH = set()          # the hyphenated words the book writes inside a line


def indent(l):
    return len(l) - len(l.lstrip(' '))


def is_table(l):
    t = re.sub(r'^(\d{1,2}|[ivx]{1,4}|\([a-z0-9]+\))\s+', '', l.strip())     # the gap after a list number
    return bool(re.search(r'\S {3,}\S', t))


def key(t):
    return re.sub(r'[^a-z0-9]', '', t.lower())


def heading_like(t):
    if t.startswith('(') and t.endswith(')') and len(t) < 90:
        return True
    if len(t) > 70 or re.search(r'[.,;:!?’”"-]$', t) or not t[0].isupper():
        return False
    words = [w for w in re.findall(r"[^\s–—-]+", t) if w.isalpha()]
    small = {'of', 'and', 'the', 'in', 'to', 'a', 'an', 'or', 'with', 'by', 'for', 'on', 'as', 'at', 'from', 'into'}
    caps = sum(1 for w in words if w[0].isupper() or w.lower() in small)
    return len(t.split()) <= 9 and caps >= max(1, len(words) - 1)


def main(src, slug='tinmon'):
    text = open(src, encoding='utf-8').read().translate(FONT)
    pages = text.split('\f')
    HYPH.update(w.lower() for w in re.findall(r'\w+-\w+', re.sub(r'-\n', ' ', text)))
    # the section titles of the book's contents ("Kāmāvacara Cittas ........ 36"): the headings
    toc = set()
    for l in text[:text.find('Buddha’s Teachings', text.find('About the Author'))].split('\n'):
        m = re.match(r'^\s*(.+?)\s*\.{3,}\s*\d+\s*$', l) or re.match(r'^\s*(\S.*?)\s{8,}\d+\s*$', l)
        if m:
            toc.add(key(m.group(1)))
    # the body starts after the contents (the last contents line names About the Author)
    lines = []
    started = False
    for pg in pages:
        pl = pg.split('\n')
        if not started:
            if any(re.match(r'^\s*Buddha’s Teachings\s*$', l) for l in pl):
                started = True
                pl = pl[next(i for i, l in enumerate(pl) if re.match(r'^\s*Buddha’s Teachings\s*$', l)):]
            else:
                continue
        pl = [l.rstrip() for l in pl]
        pl = [l for l in pl if not re.fullmatch(r'\s*\d{1,3}\s*', l)]          # page numbers
        while pl and not pl[0].strip():
            pl.pop(0)
        while pl and not pl[-1].strip():
            pl.pop()
        lines += pl + ['\x00']                                                  # a page break
    parts = [dict(label='Preface', title='Preface and Introduction', ch=None, blocks=[])]
    cur = None          # the paragraph being built: dict(kind, ind, lines)

    def flush():
        nonlocal cur
        if not cur:
            return
        bl = parts[-1]['blocks']
        if cur['kind'] == 'pre':
            if bl and bl[-1]['type'] == 'pre':
                bl[-1]['text'] += '\n' + '\n'.join(cur['lines'])
            else:
                bl.append(dict(type='pre', text='\n'.join(cur['lines'])))
        else:
            t = ''
            for x in cur['lines']:
                x = x.strip()
                m = re.search(r'(\w+)-$', t)
                if m and x[:1].isalpha():
                    nxt = re.match(r'\w+', x).group(0)
                    # a line-end hyphen is the book's own where the book writes the word with it inside a line
                    t = t + x if f'{m.group(1)}-{nxt}'.lower() in HYPH else t[:-1] + x
                else:
                    t = (t + ' ' + x) if t else x
            t = re.sub(r'\s+', ' ', t).strip()
            t = re.sub(r'^([A-Z‘“]) {2,}(\w)', r'\1\2', t)                                  # a drop capital
            if cur['kind'] == 'item':
                bl.append(dict(type='p', text=t, ind=1))
            else:
                bl.append(dict(type='p', text=t))
        cur = None

    def ended(i):
        """did the line before i end a paragraph (or is it a break)?"""
        j = i - 1
        while j >= 0 and lines[j] == '\x00':
            j -= 1
        if j < 0 or not lines[j].strip():
            return True
        return bool(re.search(r'[.:?!”’)]$', lines[j].strip())) or (cur is None)

    i = 0
    while i < len(lines):
        l = lines[i]
        if l == '\x00':
            i += 1
            continue
        s = l.strip()
        if not s:
            flush()
            i += 1
            continue
        m = re.match(r'^\s*Chapter (\d)\s*$', l)
        if m:
            flush()
            k = int(m.group(1))
            j = i + 1
            heads = []
            while j < len(lines) and len(heads) < 2:
                if lines[j].strip() and lines[j] != '\x00':
                    heads.append(lines[j].strip())
                j += 1
            title = ' '.join(w.title() if w.isupper() and len(w) > 1 else w for w in heads[0].split())
            parts.append(dict(label=f'Chapter {k}', title=f'{title} — {heads[1]}', ch=k, blocks=[]))
            i = j
            continue
        if re.fullmatch(r'Conclusion', s) and indent(l) <= 1 and parts[-1]['ch'] == 9:
            flush()
            parts.append(dict(label='Conclusion', title='Conclusion; About the Author', ch=None, blocks=[]))
            i += 1
            continue
        if is_table(l) and not re.match(r'^\s*([A-Z‘“])\s{2,}[a-z]', l):
            if not cur or cur['kind'] != 'pre':
                flush()
                cur = dict(kind='pre', ind=0, lines=[])
            cur['lines'].append(l)
            i += 1
            continue
        if cur and cur['kind'] == 'pre':
            flush()
        ind = indent(l)
        nxt = next((x for x in lines[i + 1:] if x != '\x00'), '')
        numbered = re.match(r'^(\d{1,2}|[ivx]{1,4})\.?\s+(.*)$', s)
        if numbered and key(numbered.group(2)) in toc and ended(i):          # "1 Four Āsavas (…)": a numbered section
            flush()
            parts[-1]['blocks'].append(dict(type='h', text=s))
            i += 1
            continue
        if ind <= 1 and (key(s) in toc or heading_like(s)) and ended(i) and nxt.strip() and len(s) < 90:
            flush()
            parts[-1]['blocks'].append(dict(type='h4' if s.startswith('(') else 'h', text=s))
            i += 1
            continue
        if ind >= 2 and re.match(r'^(\d{1,2}|[ivx]{1,4}|\([a-z0-9ivx]+\)|•)\s', s):
            flush()
            cur = dict(kind='item', ind=ind, lines=[s])
        elif cur and cur['kind'] == 'item' and ind > cur['ind']:
            cur['lines'].append(s)
        elif ind >= 2:
            flush()
            cur = dict(kind='para', ind=ind, lines=[s])
        else:
            if cur is None:
                cur = dict(kind='para', ind=0, lines=[])
            elif cur['kind'] == 'item' and ended(i):
                flush()
                cur = dict(kind='para', ind=0, lines=[])
            cur['lines'].append(s)
        i += 1
    flush()
    chapters = [dict(num=str(n), label=p['label'], title=p['title'], blocks=p['blocks'], **({'sangaha_ch': p['ch']} if p['ch'] else {}))
                for n, p in enumerate(parts)]
    json.dump(dict(chapters=chapters, glossary=[]), open(os.path.join(ROOT, 'data', f'{slug}.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=0)
    left = sorted({c for ch in chapters for b in ch['blocks'] for c in b.get('text', '') if c in 'àãå¤õüïëóòâÀÃäæö¥'})
    for c in chapters:
        print(f'  {c["label"]:11} {c["title"][:46]:46} blocks {len(c["blocks"]):4}  headings {sum(1 for b in c["blocks"] if b["type"] in ("h", "h4")):3}  tables {sum(1 for b in c["blocks"] if b["type"] == "pre"):3}', file=sys.stderr)
    print('old-font letters left:', left, file=sys.stderr)


if __name__ == '__main__':
    main(*sys.argv[1:])
