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


def is_diagram(l):
    """a line of a thought-process diagram: rows of one- and two-letter marks ("P C SP ST V J J J"), or a rule of dashes"""
    w = l.split()
    return bool(re.search(r'-{6,}|_{6,}', l)) or (len(w) >= 5 and sum(1 for x in w if re.fullmatch(r'\(?[A-Z]{1,2}\)?|\(\d\)', x)) >= 0.7 * len(w))


def is_table(l):
    if is_diagram(l):
        return True
    t = re.sub(r'^(•|\d{1,2}\.?|[A-H]\.|[ivx]{1,4}\.?|\([a-z0-9]+\)|' + SPEAKER + r')\s+', '', l.strip())
    t = re.sub(r'^[A-Za-z](-[a-z])?\s{2,}(?=[A-Z])', '', t)                 # "A   In the first …", "b-f   In the next …"
    if len(re.findall(r'\S {3,}\S', t)) == 1 and re.search(r'[.;:]\s{3,}[A-Z‘“]', t) and len(t.split()) >= 6:
        return False                     # two sentences with a wide space between them     # the gap after a list number or a speaker
    if not re.search(r'\S {3,}\S', t):
        return False
    gaps = [len(g) for g in re.findall(r'(?<=\S) +(?=\S)', t)]
    words = t.split()
    # a justified line of prose: many words, the gaps spread evenly and none very wide
    if (len(l.rstrip()) >= 55 and 3 <= len(words) <= 9 and min(gaps) >= 2 and max(gaps) <= 9 and all(re.search(r'[a-zāīūṃñ]', w) for w in words)
            and any(w[0].islower() or w[-1] in ',.;:' for w in words)):
        return False                     # a short justified line, its few words spread across the measure
    if JUSTIFIED[0] and len(t) >= 45 and len(words) >= 6 and max(gaps) <= 6 and sum(1 for g in gaps if g >= 3) * 2 >= len(gaps) - 1:
        return False
    return True


def key(t):
    return re.sub(r'[^a-z0-9]', '', t.lower())


def guide_fixes(text):
    """The Guide sets two lists beside braces with their labels on the right; pdftotext scatters the labels
    among the items. Those two lists are written out here as they read in the book."""
    def li(xs):
        return '\n'.join('⟦li⟧' + x for x in xs)
    fac = [('The 6 kinds of organs', ['1. eye', '2. ear', '3. nose', '4. tongue', '5. body', '6. mind']),
           (None, ['7. femininity (itthindriya)', '8. virility (purisindriya)', '9. vitality (jīvitindriya)']),
           ('The 5 kinds of feelings', ['10. bodily ease (sukha)', '11. bodily pain (dukkha)', '12. glad-mindedness (somanassa)',
                                        '13. sad-mindedness (domanassa)', '14. equanimity (upekkhā)']),
           ('The 5 spiritual faculties', ['15. faith (saddhā)', '16. energy (viriya)', '17. mindfulness (sati)',
                                          '18. concentration (samādhi)', '19. wisdom (paññā)']),
           ('The 3 supramundane faculties', ['20. the thought: “I shall come to know the unknown” (anaññātaññassāmītindriya)',
                                             '21. the faculty of understanding (aññindriya)',
                                             '22. the faculty of ‘one who has understood’ (aññātāvindriya)'])]
    new = '\n\n'.join(('⟦h4⟧' + h + '\n' if h else '') + li(xs) for h, xs in fac) + '\n'
    text, n1 = re.subn(r'\n[ \t]*\}[ \t]*\n[ \t]*1\. eye\n.*?\(aññātāvindriya\)[^\n]*faculties\)\n', '\n' + new, text, count=1, flags=re.S)
    schools = [('4th century BCE', ['Vajjiputtakas 12', 'Mahiṃsāsakas (Mahiṃs.) 21, 55, 59, 82, 98, 106, 161, 181, 192, 197',
                                    'Mahāsaṅghikas (Mahās.) 98–103, 105, 107–09, 112, 116–19, 135, 144, 145, 149, 155–56, 184, 201, 204',
                                    'Gokulikas 18', 'Sabbatthivādins (Sabb.) 2, 6, 7, 19, 113',
                                    'Sammitiyas (Samm.) 1–5, 19, 26, 28, 29, 66, 75, 80, 82–84, 98, 106, 141, 142, 154, 161, 162, 182']),
               ('3rd century BCE', ['Bhadrayānikas 19', 'Kassapikas 8']),
               ('Later schools', ['Hetuvādins (Het.) 148, 150–51, 153, 157, 168–69, 192, 194, 219',
                                  'Uttarāpathakas (Uttar.) 34–37, 39, 40, 45, 47, 58, 59, 74, 87, 88, 90–91, 113, 120–21, 123, 126–27, '
                                  '129–30, 132, 137–38, 159–60, 175, 178–80, 185, 189, 191, 193, 199, 205–06, 209–11, 213, 216, 219',
                                  'Andhakas (Andh.) 9, 10, 17, 19–24, 26, 28, 29, 32, 33, 41–44, 46, 48–54, 58, 60–63, 70–74, 78–81, 85, '
                                  '88, 89, 96, 97, 111, 114–15, 131, 139–42, 154, 162–65, 179–80, 182, 186, 190, 195–96, 202, 203, 205–08, 215, 217, 218',
                                  'Pubba-seliyas (Pubb.) 11–16, 55, 56, 75–77, 83, 84, 86, 93–95, 110, 122, 128, 133–34, 136, 143, 158, 183, 187–88, 198, 214',
                                  'Apara-seliyas (Apar.) 11, 128, 158, 214', 'Rājagirikas (Rāj.) 64–69, 125, 152, 166–67',
                                  'Siddhatthikas (Siddh.) 64–69, 166–67', 'Vetulyakas 170–74, 176, 177, 215'])]
    new = '\n\n'.join('⟦h4⟧' + h + '\n' + li(xs) for h, xs in schools) + '\n'
    text, n2 = re.subn(r'\n[ \t]*\{[ \t]*\n[ \t]*Vajjiputtakas 12\n.*?Vetulyakas 170–74, 176, 177, 215\n', '\n' + new, text, count=1, flags=re.S)
    if n1 + n2 < 2:
        print('guide_fixes: a list was not found', n1, n2, file=sys.stderr)
    return text


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
    # Nyanatiloka's Guide, BPS 2019 copy (Unicode Pāli); the 2007 copy needed FONTS['guide']
    'guide': dict(font=None, start=r'^\s*Publisher’s Preface\s*$', chapter=r'^\s{12,}([IVX]{1,4})\s*$', title_lines=2,
                  sangaha={}, front='Prefaces; Introduction', colon_heads=False, centred_caps=True, start_at=2,
                  extra_parts=[(r'^\s*THE MATRIX \(MĀTIKĀ\)\s*$', 'Mātikā', 'The Matrix (Mātikā)'),
                               (r'^\s*APPENDIX I\s*$', 'Appendix I', 'Paṭicca-samuppāda: the doctrine of dependent origination of all phenomena of existence'),
                               (r'^\s*APPENDIX II\s*$', 'Appendix II', 'Tables')],
                  running_head=r'^\s*(Guide [Tt]hrough the Abhidh?a?m+a Piṭaka|Paṭṭhāna|Kathāvatthu|Vibhaṅga|Yamaka|Paṭicca-samuppāda|Dhammasaṅgaṇī|The Abhidhamma Matrix|The Matrix \(Mātikā\)|Introduction|Dhātukathā|Puggalapaññatti|Appendix( II?)?)\s*$'),
}
FONTS = {'tinmon': FONT,
         # Nyanatiloka's Guide (BPS 2007): á ā, þ ṭ, ò ṅ, ó ṇ, ú ū, ì ī, í ṃ, ÿ ¿ ḷ, ð ḍ and their capitals;
         # ø is a stray mark inside words (reølationship) and is dropped
         'guide': str.maketrans({'á': 'ā', 'þ': 'ṭ', 'ò': 'ṅ', 'ó': 'ṇ', 'ú': 'ū', 'ì': 'ī', 'í': 'ṃ', 'ÿ': 'ḷ', '¿': 'ḷ',
                                 'ð': 'ḍ', 'Á': 'Ā', 'Þ': 'Ṭ', 'Ò': 'Ṅ', 'Ó': 'Ṇ', 'Ú': 'Ū', 'Ì': 'Ī', 'Í': 'Ṃ',
                                 'Ÿ': 'Ḷ', 'Ð': 'Ḍ', 'ø': None})}
NUMWORDS = {'One': 1, 'Two': 2, 'Three': 3, 'Four': 4, 'Five': 5, 'Six': 6, 'Seven': 7, 'Eight': 8, 'Nine': 9}
EQ = re.compile(r'^\s{0,2}(\S.{0,40}?)\s+=\s+([^\d\s].*[a-zāīū]{3}.*)$')     # "Jhāna        = Jhāna is so called …"


def eq_col(ls):
    """the column where the meanings of a list of terms start"""
    for x in reversed(ls):
        m = EQ.match(x)
        if m:
            return m.start(2)
    return -9


DEF = re.compile(r'^\S+(\s\S+)?\s+[:=]\s')     # a glossary line: "sampayuttaṃ : connected with"
SPEAKER = r'(Sayādaw|Student|Students|Yogi|Question|Answer|Q|A)\s*:'


def main(src, slug='tinmon'):
    cfg = BOOKS[slug]
    JUSTIFIED[0] = slug.startswith('handbook')
    text = open(src, encoding='utf-8').read()
    text = re.sub(r'(?m)^(\s*)([A-ZĀĪŪṬḌṆṄÑṂḶ ()-]+)$', lambda m: m.group(1) + re.sub(r'(?<=[A-ZĀĪŪṬḌṆṄÑṂḶ]) (?=[ṬḌṆṄ])|(?<=[ṬḌṆṄ]) (?=[A-ZĀĪŪṬḌṆṄ]{2})', '', m.group(2)), text)
    if slug == 'guide':
        text = text.replace('¿', 'ḷ')                   # the 2008 typesetting keeps a few of the old font's ¿ (sa¿āyatana)
        text = guide_fixes(text)
    text = re.sub(r'(?m)^[ \t]*[{}][ \t]*$', '', text)   # a brace drawn beside a group of lines comes out as a line of its own
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
    seen_start = 0
    for pg in pages:
        pl = pg.split('\n')
        if not started:
            if any(re.match(cfg['start'], l) for l in pl):
                seen_start += 1
                if seen_start < cfg.get('start_at', 1):
                    continue
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
            if cfg.get('font') is None:                  # the Guide (2019): a running head may stand at the foot too
                pl = [l for l in pl if not re.fullmatch(cfg['running_head'], l)]
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
        if cur['kind'] == 'pre' and EQ.match(cur['lines'][0]) and all(EQ.match(x) or indent(x) >= 8 for x in cur['lines']):
            # a list of terms and their meanings ("Jhāna   = Jhāna is so called …"): one paragraph each
            for x in cur['lines']:
                m = EQ.match(x)
                if m:
                    bl.append(dict(type='p', text=f'**{re.sub(r"\s+", " ", m.group(1).strip())}** = {m.group(2).strip()}', ind=1))
                else:
                    t = bl[-1]['text']
                    w = x.strip()
                    bl[-1]['text'] = t[:-1] + w if re.search(r'\w-$', t) and w[:1].islower() else t + ' ' + w
        elif cur['kind'] == 'pre':
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
                if cur.get('head') and len(cur['lines']) > 1:
                    h = re.sub(r'\s+', ' ', cur['lines'][0].strip())
                    t = f'**{h}** ' + t[len(h):].strip() if t.startswith(h) else t
                bl.append(dict(type='p', text=t, ind=1))
            else:
                bl.append(dict(type='p', text=t))
        cur = None

    def margin_item(s, nxt, i):
        """a numbered or lettered item set at the margin: with its lines hanging under it, in a run of items,
        or after a finished sentence ("A.   Lokiya = mundane (81),", "5.   What are …")"""
        if indent(lines[i]) > 1:
            return False
        if re.match(r'^[A-H]\.\s{2,}\S|^[A-Za-z](-[a-z])?\s{3,}[A-Z]', s) or (re.match(r'^\d{1,2}\.\s{2,}\S', s) and ended(i)):
            return True
        if not (indent(nxt) >= 3 or re.match(r'^\s?\d{1,3}\.\s+[*A-Z“‘(]', nxt)):
            return False
        return bool(re.match(r'^\d{1,2}\.?\s{2,}\S', s)
                    or (re.match(r'^(\d{1,3}|[ivx]{1,4})\.?\s+[*A-Z“‘(]', s) and (ended(i) or (cur and cur['kind'] == 'item'))))

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
        if re.fullmatch(r'\*\s?\*\s?\*', s):         # a break between sections
            flush()
            parts[-1]['blocks'].append(dict(type='p', text='* * *'))
            i += 1
            continue
        if s.startswith('⟦'):                       # a block written out by hand (guide_fixes)
            flush()
            kind, t = re.match(r'⟦(\w+)⟧\s*(.*)', s).groups()
            parts[-1]['blocks'].append(dict(type='h4', text=t) if kind == 'h4' else dict(type='p', text=t, ind=1))
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
        if cur and cur['kind'] == 'pre' and EQ.match(cur['lines'][-1] if not EQ.match(cur['lines'][0]) else cur['lines'][0]) \
                and ((indent(l) >= 8 and not EQ.match(l) and abs(indent(l) - eq_col(cur['lines'])) <= 3) or EQ.match(l)):
            cur['lines'].append(l)              # the meaning of a term goes on under itself
            i += 1
            continue
        nx0 = next((x for x in lines[i + 1:] if x != '\x00' and x.strip()), '')
        if (cur and cur['kind'] == 'pre' and indent(l) >= 5 and len(s.split()) <= 3 and len(s) <= 25
                and (is_diagram(nx0) or is_diagram(cur['lines'][-1]))):
            cur['lines'].append(l)              # a label of a diagram ("Eye-door", "Mind-door")
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
        if ind >= 10 and len(s) < 70 and (re.fullmatch(r'[A-Z][\w ’-]+ \(§§[\d–-]+\)', s)
                                           or (re.fullmatch(r'Section on [\w ’-]+', s) and re.match(r'\s?1\.\s', nxt))):
            flush()                    # a centred section title of the Matrix: "Section on Roots (§§1053–72)"
            parts[-1]['blocks'].append(dict(type='h4', text=s))
            i += 1
            continue
        if ind >= 10 and len(s) < 60 and key(s) in toc and heading_like(s) and ended(i) and not s.isupper() and not is_table(l):
            flush()                    # a centred title that the contents list ("Review Questions")
            j = i + 1
            while j < len(lines) and (not lines[j].strip() or lines[j] == '\x00'):
                j += 1
            if s.split()[-1] in ('and', 'of', 'the', 'in', 'to', '&') and j < len(lines) and indent(lines[j]) >= 10 and len(lines[j].strip()) < 50:
                s += ' ' + lines[j].strip()                         # the title goes on in a second line
                i = j
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
        if (re.match(r'^[A-Z][a-z]{0,3}:\s+\S+.*\s[–-]\s', s) and ended(i) and indent(nxt) > ind
                and not (cur and cur['kind'] == 'item' and ind > cur['ind'] + 1 and not cur.get('head'))):
            flush()                 # a term of a list with its explanation set in under it ("Na: bhavaṅga-calāna – …")
            cur = dict(kind='item', ind=1, lines=[s], hang=True, head=True)
            i += 1
            continue
        if re.match(SPEAKER + r'\s', s) and ind <= 1:                         # "Sayādaw: …" with a hanging indent
            flush()
            cur = dict(kind='speech', ind=0, lines=[s])
        elif cur and cur['kind'] == 'speech' and ind >= 4 and not re.match(SPEAKER, s):
            cur['lines'].append(s)
        elif (ind >= 2 and re.match(r'^(\d{1,2}\.?|[ivx]{1,4}\.?|\([a-z0-9ivx]+\)|•)\s|^[A-Za-z](-[a-z])?\s{2,}[A-Z]', s)) or margin_item(s, nxt, i):
            flush()
            cur = dict(kind='item', ind=ind, lines=[s])
        elif cur and cur['kind'] == 'item' and ind > cur['ind']:
            abbr = re.match(r'^[A-Z][a-z]{0,3}:\s', s)
            if ended(i) and (abbr or (cur.get('cont') and ind >= cur['cont'] + 4)):
                # inside an item: a new paragraph (set in further), or a term of a list ("Pa: Pañca-dvārāvajjana – …")
                flush()
                cur = dict(kind='item', ind=min(ind - 1, 3), lines=[s], hang=True, cont=ind, head=bool(abbr))
            else:
                cur['lines'].append(s)
                cur['hang'] = True
                cur.setdefault('cont', ind)
        elif (cur and cur['kind'] == 'para' and ind >= 2 and not DEF.match(s) and not DEF.match(cur['lines'][-1])
              and ((cur['ind'] >= 2 and ind > cur['ind'] + 1) or (ind == cur.get('cont') and ind > cur['ind'] + 1)
                   or (cur['ind'] >= 2 and not ended(i)) or (abs(ind - cur['ind']) <= 1 and not ended(i)))):
            cur['lines'].append(s)              # the paragraph goes on: a hanging indent, or a block set in from the margin
            cur['cont'] = ind
        elif ind >= 2:
            flush()
            cur = dict(kind='para', ind=ind, lines=[s])
        else:
            if cur is None:
                cur = dict(kind='para', ind=0, lines=[])
            elif cur['kind'] == 'item' and (ended(i) or (cur['ind'] <= 1 and cur.get('hang'))):     # a hanging item ends at the margin
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
