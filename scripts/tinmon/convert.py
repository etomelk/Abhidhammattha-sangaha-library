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


JUSTIFIED = [False]      # set per book: the book's prose is justified with wide gaps (the Handbook)


def is_table(l):
    t = re.sub(r'^(•|\d{1,2}|[ivx]{1,4}|\([a-z0-9]+\)|' + SPEAKER + r')\s+', '', l.strip())     # the gap after a list number or a speaker
    if not re.search(r'\S {3,}\S', t):
        return False
    gaps = [len(g) for g in re.findall(r'(?<=\S) +(?=\S)', t)]
    words = t.split()
    # a justified line of prose: many words, the gaps spread evenly and none very wide
    if JUSTIFIED[0] and len(t) >= 45 and len(words) >= 6 and max(gaps) <= 6 and sum(1 for g in gaps if g >= 3) * 2 >= len(gaps) - 1:
        return False
    return True


def key(t):
    return re.sub(r'[^a-z0-9]', '', t.lower())


def heading_like(t):
    if t.startswith('(') and t.endswith(')') and len(t) < 90:
        return True
    if len(t) > 70 or re.search(r'[.,;:!?’”"-]$|\.\)$', t) or not t[0].isupper() or re.search(r'[,;]|: ', t):
        return False
    words = [w for w in re.findall(r"[^\s–—-]+", t) if w.isalpha()]
    small = {'of', 'and', 'the', 'in', 'to', 'a', 'an', 'or', 'with', 'by', 'for', 'on', 'as', 'at', 'from', 'into'}
    caps = sum(1 for w in words if w[0].isupper() or w.lower() in small)
    return len(t.split()) <= 9 and caps >= max(1, len(words) - 1)


# per book: the old font or not, where the body starts, the chapter line, how many title lines it has,
# which chapter of the Saṅgaha each chapter is, and headings that end in a colon ("Abhidhamma:")
BOOKS = {
    'tinmon': dict(font='tinmon', start=r'^\s*Buddha’s Teachings\s*$', chapter=r'^\s*Chapter (\d)\s*$', title_lines=2,
                   sangaha={k: k for k in range(1, 10)}, front='Preface and Introduction', colon_heads=False),
    'fundamental': dict(font=False, start=r'^\s*Editorial preface\s*$', chapter=r'^\s*CHAPTER (\d)\s*$', title_lines=1,
                        sangaha={1: 1, 2: 2, 3: 6, 4: 3, 5: 4}, front='Editorial Preface; About the Author; The History of Abhidhamma',
                        colon_heads=True),
    'handbook1': dict(font=False, start=r'^\s*Editorial Preface\s*$', chapter=r'^\s*Chapter (One|Two|Three|Four|Five|Six)\s*$',
                      title_lines=1, sangaha={1: 1, 2: 2, 3: 3}, front='Editorial Preface; Editor’s Note; Introduction',
                      colon_heads=False, running_head=r'^\s*(Chapter (One|Two|Three|Four|Five|Six)|Introduction|Contents)\s*$'),
    'handbook2': dict(font=False, start=r'^\s*Editorial Preface\s*$', chapter=r'^\s*Chapter (One|Two|Three|Four|Five|Six)\s*$',
                      title_lines=1, sangaha={4: 4, 5: 5, 6: 6}, front='Editorial Preface; Editor’s Note',
                      colon_heads=False, running_head=r'^\s*(Chapter (One|Two|Three|Four|Five|Six)|Introduction|Contents)\s*$'),
    'guide': dict(font='guide', start=r'^\s*Publisher’s Preface\s*$', chapter=r'^\s{12,}([IVX]{1,4})\s*$', title_lines=2,
                  sangaha={}, front='Prefaces; Introduction', colon_heads=False, centred_caps=True,
                  extra_parts=[(r'^\s*THE MATRIX \(MĀTIKĀ\)\s*$', 'Mātikā', 'The Matrix (Mātikā)'),
                               (r'^\s*APPENDIX\s*$', 'Appendix', 'Dependent Origination')],
                  running_head=r'^\s*(([\dixvlc]+)\s{3,}Guide [Tt]hrough.*|\S.{0,40}?\s{8,}[\dixvlc]+)\s*$'),
}
FONTS = {'tinmon': FONT,
         # Nyanatiloka's Guide (BPS 2007): á ā, þ ṭ, ò ṅ, ó ṇ, ú ū, ì ī, í ṃ, ÿ ¿ ḷ, ð ḍ and their capitals;
         # ø is a stray mark inside words (reølationship) and is dropped
         'guide': str.maketrans({'á': 'ā', 'þ': 'ṭ', 'ò': 'ṅ', 'ó': 'ṇ', 'ú': 'ū', 'ì': 'ī', 'í': 'ṃ', 'ÿ': 'ḷ', '¿': 'ḷ',
                                 'ð': 'ḍ', 'Á': 'Ā', 'Þ': 'Ṭ', 'Ò': 'Ṅ', 'Ó': 'Ṇ', 'Ú': 'Ū', 'Ì': 'Ī', 'Í': 'Ṃ',
                                 'Ÿ': 'Ḷ', 'Ð': 'Ḍ', 'ø': None})}
NUMWORDS = {'One': 1, 'Two': 2, 'Three': 3, 'Four': 4, 'Five': 5, 'Six': 6, 'Seven': 7, 'Eight': 8, 'Nine': 9}
SPEAKER = r'(Sayādaw|Student|Students|Yogi|Question|Answer|Q|A)\s*:'


def main(src, slug='tinmon'):
    cfg = BOOKS[slug]
    JUSTIFIED[0] = slug.startswith('handbook')
    text = open(src, encoding='utf-8').read()
    if cfg['font']:
        text = text.translate(FONTS[cfg['font'] if isinstance(cfg['font'], str) else 'tinmon'])
    pages = text.split('\f')
    HYPH.update(w.lower() for w in re.findall(r'\w+-\w+', re.sub(r'-\n', ' ', text)))
    # the section titles of the book's contents ("Kāmāvacara Cittas ........ 36"): the headings
    toc = set()
    body_at = re.search(cfg['start'], text, flags=re.M).start()
    for n, l in enumerate(text.split('\n')):
        # a contents line: with dot leaders anywhere (the Handbook prints its contents after the preface),
        # or with a wide gap before the page number in the front of the book
        m = re.match(r'^\s*(.+?)\s*\.{3,}\s*[\divxlc]+\s*$', l) or (n < text[:body_at].count('\n') and re.match(r'^\s*(\S.*?)\s{8,}\d+\s*$', l))
        if m:
            toc.add(key(m.group(1)))
    # the body starts after the contents (the last contents line names About the Author)
    lines = []
    started = False
    for pg in pages:
        pl = pg.split('\n')
        if not started:
            if any(re.match(cfg['start'], l) for l in pl):
                started = True
                pl = pl[next(i for i, l in enumerate(pl) if re.match(cfg['start'], l)):]
            else:
                continue
        pl = [l.rstrip() for l in pl]
        pl = [l for l in pl if not re.search(r'\.{6,}\s*([\d]+|[ivxIVX]+)?\s*$', l)]   # contents lines with dot leaders
        pl = [l for l in pl if not re.fullmatch(r'\s*([\dl]{1,3}|[ivxlc]{1,6})\s*', l)]          # page numbers
        if cfg.get('running_head'):
            k = next((i for i, l in enumerate(pl) if l.strip()), None)
            if k is not None and re.match(cfg['running_head'], pl[k]):
                pl = pl[k + 1:]
        while pl and not pl[0].strip():
            pl.pop(0)
        while pl and not pl[-1].strip():
            pl.pop()
        lines += pl + ['\x00']                                                  # a page break
    parts = [dict(label='Front matter', title=cfg['front'], ch=None, blocks=[])]
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
        m = re.match(cfg['chapter'], l)
        if m:
            flush()
            g = m.group(1)
            k = int(g) if g.isdigit() else NUMWORDS.get(g, g)
            j = i + 1
            heads = []
            while j < len(lines) and len(heads) < cfg['title_lines']:
                if lines[j].strip() and lines[j] != '\x00':
                    heads.append(lines[j].strip())
                j += 1
            def tc(x):
                small = {'Of', 'To', 'The', 'And', 'In', 'On', 'With', 'For', 'Or', 'A', 'An', 'By'}
                ws = [w.title() if w.isupper() and len(w) > 1 else w for w in x.split()]
                return ' '.join(w.lower() if k and w in small else w for k, w in enumerate(ws))
            title = tc(heads[0]).rstrip(':')
            if len(heads) > 1:
                title = f'{title} — {tc(heads[1])}'
            parts.append(dict(label=f'Chapter {k}', title=title, ch=cfg['sangaha'].get(k), blocks=[]))
            i = j
            continue
        ex = next((e for e in cfg.get('extra_parts', []) if re.match(e[0], l)), None)
        if ex:
            flush()
            parts.append(dict(label=ex[1], title=ex[2], ch=None, blocks=[]))
            i += 1
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
        if (cfg.get('centred_caps') and ind >= 10 and len(s) < 70 and not is_table(l) and ended(i)
                and re.sub(r'[^A-Za-zĀĪŪṬḌṆṄÑṂḶāīūṭḍṇṅñṃḷ]', '', s).isupper()):
            flush()                    # a centred line in capitals ("CHAPTER XIV", "THE 24 CONDITIONS")
            t = ' '.join(w.title() if w.isupper() and len(w) > 1 and not re.fullmatch(r'[IVXL]+[.:]?', w) else w for w in s.split())
            t = ' '.join(w.lower() if k and w in ('Of', 'To', 'The', 'And', 'In', 'On', 'With', 'For', 'Or', 'By') else w for k, w in enumerate(t.split()))
            parts[-1]['blocks'].append(dict(type='h', text=t))
            i += 1
            continue
        if (cfg['colon_heads'] and ind >= 10 and not is_table(l) and len(s) < 60 and ended(i) and s[0].isupper() and '=' not in s
                and (any(k.startswith(key(s)) for k in toc if len(key(s)) >= 6) or re.search(r'\s[–-]\s*\d+$', s))):
            flush()                    # a centred heading: a title of the contents, or "Akusala – 12"
            parts[-1]['blocks'].append(dict(type='h', text=s))
            i += 1
            continue
        if (cfg['colon_heads'] and ind <= 1 and s.endswith(':') and len(s.split()) <= 8 and ended(i)
                and indent(nxt) >= 3 and not re.match(r'^\d', s)):
            flush()
            parts[-1]['blocks'].append(dict(type='h', text=s[:-1]))
            i += 1
            continue
        if ind <= 1 and (key(s) in toc or heading_like(s)) and ended(i) and nxt.strip() and len(s) < 90:
            flush()
            parts[-1]['blocks'].append(dict(type='h4' if s.startswith('(') else 'h', text=s))
            i += 1
            continue
        if re.match(SPEAKER + r'\s', s) and ind <= 1:                         # "Sayādaw: …" with a hanging indent
            flush()
            cur = dict(kind='speech', ind=0, lines=[s])
        elif cur and cur['kind'] == 'speech' and ind >= 4 and not re.match(SPEAKER, s):
            cur['lines'].append(s)
        elif ind >= 2 and re.match(r'^(\d{1,2}|[ivx]{1,4}|\([a-z0-9ivx]+\)|•)\s', s):
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
    left = sorted({c for ch in chapters for b in ch['blocks'] for c in b.get('text', '') if c in ('àãå¤õüïëóòâÀÃäæö¥' if slug == 'tinmon' else 'áþòóúìíÿ¿ðÁÞÒÓÚÌÍŸÐø' if slug == 'guide' else '')})
    for c in chapters:
        print(f'  {c["label"]:11} {c["title"][:46]:46} blocks {len(c["blocks"]):4}  headings {sum(1 for b in c["blocks"] if b["type"] in ("h", "h4")):3}  tables {sum(1 for b in c["blocks"] if b["type"] == "pre"):3}', file=sys.stderr)
    print('old-font letters left:', left, file=sys.stderr)


if __name__ == '__main__':
    main(*sys.argv[1:])
