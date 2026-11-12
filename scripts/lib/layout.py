"""Layout analysis shared by the PDF parsers: positioned rows of words ->
blocks (headings, paragraphs, word lists, exercises, tables, formula lines).

The caller (scripts/<book>/parse.py) drives the page loop: it calls
new_chapter(), appends segments() of each row to `region`, and flush()es the
region at headings. Everything else here is the heuristics that turn a region
of segments into blocks; the module variables at the top are the knobs."""
import re, os, collections

LABEL = re.compile(r'^(Nom|Acc|Ins|Instr|Abl|Dat|Gen|Loc|Voc|Masc|Neut|Fem)\.?$|^[123](st|nd|rd)\.?$')
ITEM = re.compile(r'^(\d{1,2})\.\s*(.*)$')
HEAD_SEC = re.compile(r'^(\d{1,2})\.\s*(.+)$')
SP = re.compile(r'^(Singular|Plural)$')
ENGLISH_FIRST = set('i we you he she it they me us him her them my our your his their the a an to of in on'.split())


def has_letters(w):
    return re.search(r'[A-Za-zāīūṃṅñṭḍṇḷ]', w['text'])


# ---------------------------------------------------------------- rows -> segments
def segments(row, L):
    """Split a row's words into column segments at a big gap in the right half.
    A meaning ('- speaks', '= I') or a bracketed note never starts a column."""
    segs, cur = [], [row['words'][0]]
    for a, b in zip(row['words'], row['words'][1:]):
        gap = b['x0'] - a['x1']
        note = b['text'].startswith('(') and not b['text'].endswith(')')   # "(by means of the man)"
        if (gap >= 9 and b['x0'] - L >= 118 and not re.match(r'^[-=–]', b['text']) and not note
                and not re.match(r'^[-=–]$', a['text'])):
            segs.append(cur)
            cur = [b]
        else:
            cur.append(b)
    segs.append(cur)
    out = []
    for ws in segs:
        letters = [w for w in ws if has_letters(w)] or ws
        out.append(dict(x0=ws[0]['x0'], x1=ws[-1]['x1'], top=row['top'], words=ws, L=L, rx=ws[0]['x0'] - L,
                        width=ws[-1]['x1'] - ws[0]['x0'],
                        text=' '.join(w['text'] for w in ws),
                        bold=sum(w['bold'] for w in letters) >= len(letters) * 0.8,
                        italic=sum(w['italic'] for w in letters) * 2 > len(letters),
                        first_bold=ws[0]['bold'], size=max(w['size'] for w in ws)))
    return out


def jl(texts):
    """Join the lines of a paragraph; a hyphen at a line end is a line break."""
    t = '\n'.join(texts)
    t = re.sub(r'(\w{2,})-\n(\w)', r'\1\2', t)
    return t.replace('\n', ' ')


def clean(t):
    t = re.sub(r'\s*-{3,}\s*', ' ', t)        # dot leaders in the verb list
    t = re.sub(r'\s+([,.;:?!])', r'\1', t)
    t = re.sub(r'\(\s+', '(', t)
    t = re.sub(r'\s+\)', ')', t)
    t = re.sub(r'\s*/\s*', ' / ', t)
    t = re.sub(r'\)(?=[A-Za-zāīū])', ') ', t)
    return re.sub(r'\s{2,}', ' ', t).strip()


def split_entry(text):
    """'word - meaning' / 'word = meaning' -> (word, meaning)."""
    m = re.match(r'^(.*?)\s+[-–=]\s*(.*)$', text)
    if m:
        return clean(m.group(1)), clean(m.group(2))
    m = re.match(r'^(.*?\S)[-–=](\s*[A-Z].*)$', text)   # "-The brahmin"
    if m:
        return clean(m.group(1)), clean(m.group(2))
    m = re.match(r'^(.*?[\w)])-\s+(.*)$', text)          # "mfn- Himalaya"
    if m:
        return clean(m.group(1)), clean(m.group(2))
    return clean(text), ''


def split_gloss(t):
    """'pac + i + tvā = pacitvā = having cooked' -> ['pac + i + tvā = pacitvā', 'having cooked'];
    a line without an English tail stays a plain string."""
    parts = re.split(r'\s*=\s*', t)
    if len(parts) >= 3 and is_english(parts[-1]) or (len(parts) >= 3 and not re.search(r'[āīūṃṅñṭḍṇḷ]', parts[-1].split()[0]) and parts[-1][:1].islower()):
        return [clean(' = '.join(parts[:-1])), clean(parts[-1])]
    return t


def is_english(s):
    s = s.strip()
    if not s:
        return False
    head = ' '.join(s.split()[:3])
    if re.search(r'[āīūṃṅñṭḍṇḷ]', head) and not re.match(r'^(the|a|an|to|of|in|by|with|for|from)\b', s, re.I):
        return False
    w = re.sub(r'[^A-Za-z]', '', s.split()[0]).lower()
    return s[0].isupper() or w in ENGLISH_FIRST


# ---------------------------------------------------------------- chapters
chapters = []
cur = None
region = []
REF_NUMS = ('verbs', 'words', 'glossary')   # chapters whose two-column lists are flushed per page


def new_chapter(num, title, label=None):
    global cur
    cur = dict(num=num, title=title, blocks=[])
    if label:
        cur['label'] = label
    chapters.append(cur)
    return cur


def col2_of(segs):
    xs = collections.Counter(round(s['rx']) for s in segs if s['rx'] >= 118)
    if not xs:
        return None
    x, n = xs.most_common(1)[0]
    near = [s for s in segs if s['rx'] >= 118 and abs(round(s['rx']) - x) <= 5]
    if len(near) >= 0.6 * sum(xs.values()) and (len(near) >= 3 or (len(near) == 2 and all(content_kind(s) in ('item', 'entry', 'hdr') for s in near))):
        return x
    return None


def content_kind(s):
    t = s['text']
    if s['bold'] and not ITEM.match(t):
        return 'hdr'
    w0 = s['words'][0]['text']
    if LABEL.match(w0):
        return 'label'
    m = ITEM.match(t)
    if m and not (s['first_bold'] and not s['bold']):
        return 'item'
    pre = re.split(r'\s[-–=]\s|(?<=\S)[-–=](?=[A-Z])|(?<=\w\w)-\s|(?<=\))-\s|\s-(?=[a-zāīū])', t)[0]
    if (re.search(r'\s[-–=]\s|\S[-–=][A-Z]|(\w{2,}|\))-\s\S', t) and s['width'] < 300
            and len(pre.split()) <= 6 and not re.match(r'^[A-Z][a-z]+ case', t)):
        return 'entry'
    if (re.search(r'\s-[a-zāīūṃṅñṭḍṇḷ]{4,}\s*(/.*)?$', t) and len(pre.split()) == 1 and len(pre) >= 4
            and t.count('-') == 1 and s['width'] < 300):
        return 'entry'      # "ārabhati -begins" 
    if re.fullmatch(r'[^\s-]+(\s*/\s*[^\s-]+)*\s*/', t):   # "Buddha / Tathāgata /" continues below
        return 'entry'
    return 'prose'


def flush():
    """Turn the pending region (segments in page order) into blocks."""
    global region
    segs = list(region)
    region.clear()
    if not segs:
        return
    # rows of the region, in page order
    rows = []
    for s in segs:
        if rows and abs(rows[-1][0]['top'] - s['top']) < 4 and rows[-1][0]['L'] == s['L']:
            rows[-1].append(s)
        else:
            rows.append([s])
    # sub-regions: paragraphs (full-width prose and the lines around them) are
    # never part of a column layout
    def prose_row(row):
        return (len(row) == 1 and (content_kind(row[0]) == 'prose' or (row[0]['first_bold'] and ITEM.match(row[0]['text']) and not row[0]['bold']))
                and not row[0]['bold'] and row[0]['rx'] < 40)
    def wide(row):
        return prose_row(row) and row[0]['x1'] - row[0]['L'] > 250 and row[0]['rx'] <= 4
    para = [wide(r) for r in rows]
    for k in range(1, len(rows)):
        prev = rows[k - 1]
        if (para[k] and not para[k - 1] and not re.search(r'[.!?:;]$', prev[-1]['text'])
                and content_kind(prev[0]) in ('item', 'entry', 'prose') and not prev[0]['bold']):
            para[k] = False      # the end of a sentence that began in a list item
    for k in range(len(rows)):
        if prose_row(rows[k]) and not para[k]:
            if (k > 0 and para[k - 1]) or (k + 1 < len(rows) and wide(rows[k + 1]) and rows[k]['rx'] > 4 if False else False):
                para[k] = True
            elif (k + 1 < len(rows) and wide(rows[k + 1]) and rows[k][0]['rx'] > 4
                  and (k == 0 or content_kind(rows[k - 1][0]) not in ('prose', 'item'))):
                para[k] = True       # a paragraph whose first line is indented
    subs, kind = [], None
    for row, pr in zip(rows, para):
        k = 'wide' if pr else 'cols'
        if k != kind:
            subs.append([])
            kind = k
        if k == 'wide':
            row[0]['_wide'] = True
        subs[-1].append(row)
    for sub in subs:
        flat = [s for row in sub for s in row]
        if sub[0][0].get('_wide'):
            for s in flat:
                s['rel'] = s['rx']
            cur['blocks'].extend(blocks_of(flat))
            continue
        cur['blocks'].extend(column_blocks(sub))


def header_anchors(row):
    """A bold row of 2+ short column titles -> their x positions, else None."""
    ws = [w for s in row for w in s['words']]
    if not all(w['bold'] for w in ws if has_letters(w)) or len(ws) < 2:
        return None
    parts, curp = [], [ws[0]]
    for a, b in zip(ws, ws[1:]):
        if b['x0'] - a['x1'] >= 12:
            parts.append(curp)
            curp = []
        curp.append(b)
    parts.append(curp)
    if len(parts) < 2 or any(len(p) > 4 for p in parts):
        return None
    texts = [clean(' '.join(w['text'] for w in p)) for p in parts]
    if any(ITEM.match(t) for t in texts) or all(len(t) == 1 for t in texts):
        return None
    return [p[0]['x0'] for p in parts], texts


def column_blocks(sub):
    """Rows that may be laid out in columns: a header-anchored table, a paired
    paradigm, or two independent columns read one after the other."""
    out = []
    i = 0
    while i < len(sub):
        hdr = header_anchors(sub[i])
        if hdr:
            anchors, texts = hdr
            j = i + 1
            # a second bold row of titles wrapped under the first ("Pronoun  Pronoun")
            if j < len(sub) and header_anchors(sub[j]) and sub[j][0]['top'] - sub[i][0]['top'] < 18:
                a2, t2 = header_anchors(sub[j])
                if len(a2) <= len(anchors):
                    for x, t in zip(a2, t2):
                        k = min(range(len(anchors)), key=lambda k: abs(anchors[k] - x))
                        texts[k] += ' ' + t
                    j += 1
            body = []
            while j < len(sub) and not header_anchors(sub[j]) and not any(s['bold'] and content_kind(s) == 'hdr' for s in sub[j]):
                row = sub[j]
                if (len(row) == 1 and len(row[0]['words']) >= 6 and content_kind(row[0]) == 'prose'
                        and not re.search(r'\s[-=]\s', row[0]['text'])):
                    break        # a sentence after the table
                body.append(row)
                j += 1
            if body:
                out.append(anchor_table(body, anchors, texts))
                LAST_HEAD[:] = texts
            else:
                out.append(dict(type='h5', text=' '.join(texts)))
            i = j
            continue
        # a run of rows without a header
        j = i
        run = []
        while j < len(sub) and not header_anchors(sub[j]):
            run.append(sub[j])
            j += 1
        out.extend(free_blocks(run))
        i = j
    return out


LAST_HEAD = []


def anchor_table(rows, anchors, head):
    """Rows under a bold header of column titles. The titles are centred, so the
    column starts come from the data: x positions that follow a gap in most rows."""
    ncol = len(anchors)
    prepped = []
    starts = collections.Counter()
    for row in rows:
        ws = [w for s in row for w in s['words']]
        lab = ''
        if LABEL.match(ws[0]['text']) or (ITEM.match(ws[0]['text']) and len(ws) > 1):
            lab = ws[0]['text'].rstrip('.') if LABEL.match(ws[0]['text']) else ws[0]['text']
            ws = ws[1:]
        if not ws:
            continue
        prepped.append((lab, ws))
        seen_eq = False
        for a, b in zip(ws, ws[1:]):
            seen_eq = seen_eq or a['text'] in ('=', '-') or a['text'].endswith('=')
            if b['x0'] - a['x1'] >= 7 and not re.match(r'^[-=–]', b['text']) and not re.match(r'^[-=–]$', a['text']):
                starts[round(b['x0'] / 6) * 6] += 1
            elif b['text'].startswith('(') and seen_eq and b['x0'] - a['x1'] >= 2:
                starts[round(b['x0'] / 6) * 6] += 1
    first = min(ws[0]['x0'] for _, ws in prepped)
    cands = sorted(((n, x) for x, n in starts.items() if x > first + 30 and n >= 2), reverse=True)
    if len(cands) < ncol - 1:
        cands += sorted(((n, x) for x, n in starts.items() if x > first + 30 and n == 1), reverse=True)
    cols = [first] + sorted(x for n, x in cands[:ncol - 1])
    trs = []
    for lab, ws in prepped:
        cells, curc = [], [ws[0]]
        for a, b in zip(ws, ws[1:]):
            gap = b['x0'] - a['x1']
            in_right = len(cols) > 1 and b['x0'] >= cols[1] - 9
            col_of = lambda x: max((k for k in range(len(cols)) if cols[k] <= x + 9), default=0)
            cur_text = ' '.join(w['text'] for w in curc)
            split = (gap >= 7 and in_right and col_of(b['x0']) > col_of(curc[0]['x0'])
                     and not re.match(r'^[-=–]$', a['text']) and not re.match(r'^[-=–]', b['text']))
            # cramped rows: "(So) pacati = He cooks (Te) pacanti = They cook"
            split = split or (b['text'].startswith('(') and '=' in cur_text and gap >= 2 and in_right)
            nxt = ws[ws.index(b) + 1]['text'] if ws.index(b) + 1 < len(ws) else ''
            split = split or ('=' in cur_text and gap >= 2 and in_right and nxt in ('=', '-') and not curc[-1]['text'] in ('=', '-', ','))
            if split:
                cells.append(curc)
                curc = []
            curc.append(b)
        cells.append(curc)
        texts = [''] * ncol
        for c in cells:
            x = c[0]['x0']
            col = max((k for k in range(len(cols)) if cols[k] <= x + 9), default=0)
            col = min(col, ncol - 1)
            t = clean(' '.join(w['text'] for w in c))
            texts[col] = (texts[col] + ' ' + t).strip()
        if not lab and trs and (ws[0]['x0'] > cols[0] + 9 or not texts[0] or any(r[0] for r in trs)):
            prev = trs[-1]
            for k, t in enumerate(texts):
                if t:
                    prev[k + 1] = (prev[k + 1] + (' ' if prev[k + 1].endswith(',') else ', ') + t) if prev[k + 1] else t
            continue
        trs.append([lab] + texts)
    labels = any(r[0] for r in trs)
    glossed = False
    for r in trs:
        for k in range(1, len(r)):
            c = r[k]
            m = re.match(r'^(.*?)\s*[-–=]\s*(.*)$', c)
            if m and (' - ' in c or (is_english(m.group(2)) and '+' not in m.group(1))):
                r[k] = [clean(m.group(1)), clean(m.group(2))]
                glossed = True
    if glossed:
        for r in trs:
            for k in range(1, len(r)):
                if isinstance(r[k], str):
                    r[k] = [r[k], '']
    return dict(type='table', rows=trs if labels else [r[1:] for r in trs], labels=labels, glossed=glossed,
                head=([''] if labels else []) + head)


def paired_rows(left, right):
    """Labelled rows (Nom. / 1st / 1.) in both columns without a header row:
    a paradigm whose two columns are read side by side."""
    if sum(1 for r in right if content_kind(r) == 'item') >= 2:
        return None          # numbered items in both columns: an exercise
    labelled = [l for l in left if content_kind(l) in ('label', 'item') and any(abs(l['top'] - r['top']) < 4 for r in right)]
    if len(labelled) < 2:
        return None
    rows = sorted(left + right, key=lambda s: s['top'])
    out, pending, trs = [], [], []

    def drain():
        if pending:
            for s in pending:
                s['rel'] = s['rx']
            out.extend(blocks_of(pending))
            pending.clear()

    def close():
        nonlocal trs
        if trs:
            glossed = False
            for r in trs:
                for k in (1, 2):
                    m = re.match(r'^(.*?)\s*[-–=]\s*(.*)$', r[k])
                    if m and (' - ' in r[k] or (is_english(m.group(2)) and '+' not in m.group(1))):
                        r[k] = [clean(m.group(1)), clean(m.group(2))]
                        glossed = True
            if glossed:
                for r in trs:
                    for k in (1, 2):
                        if isinstance(r[k], str):
                            r[k] = [r[k], '']
            out.append(dict(type='table', rows=trs, labels=True, glossed=glossed))
            trs = []

    i = 0
    while i < len(rows):
        same = [t for t in rows if abs(t['top'] - rows[i]['top']) < 4]
        i += len(same)
        l = sorted([t for t in same if t in left], key=lambda t: t['x0'])
        r = sorted([t for t in same if t in right], key=lambda t: t['x0'])
        ltxt = clean(' '.join(t['text'] for t in l))
        rtxt = clean(' '.join(t['text'] for t in r))
        if l and content_kind(l[0]) in ('label', 'item') and r:
            drain()
            m = re.match(r'^(\S+)\s*', ltxt)
            trs.append([m.group(1).rstrip('.'), ltxt[m.end():], rtxt])
        elif trs and not l and r:
            trs[-1][2] += ' ' + rtxt
        elif trs and l and l[0]['rel'] > 4 and content_kind(l[0]) == 'prose':
            trs[-1][1] += ' ' + ltxt
            if rtxt:
                trs[-1][2] += ' ' + rtxt
        else:
            close()
            pending.extend(same)
    close()
    drain()
    return out


def free_blocks(rows):
    """Rows without a column header: either one column, or two columns read in turn."""
    segs = []
    for row in rows:
        for s in row:
            if segs and s['rx'] >= 118 and re.fullmatch(r'\(.*\)', s['text']) and not s['bold']:
                prev = segs[-1]
                prev['text'] += ' ' + s['text']
                prev['words'] = prev['words'] + s['words']
                prev['x1'] = max(prev['x1'], s['x1'])
                continue
            segs.append(s)
    c2 = col2_of(segs)
    if c2 is None:
        for s in segs:
            s['rel'] = s['rx']
        return blocks_of(segs)
    left = [s for s in segs if s['rx'] < c2 - 5]
    right = [s for s in segs if s['rx'] >= c2 - 5]
    if all(len(s['words']) <= 2 and content_kind(s) not in ('item', 'entry') for s in right) and left:
        for r in right:
            l = min(left, key=lambda l: abs(l['top'] - r['top']))
            if abs(l['top'] - r['top']) < 4:
                l['text'] += ' ' + r['text']
                l['words'] = l['words'] + r['words']
                l['x1'] = r['x1']
        for s in left:
            s['rel'] = s['rx']
        return blocks_of(left)
    for s in left:
        s['rel'] = s['rx']
    for s in right:
        s['rel'] = s['rx'] - c2
    labelled = [s for s in left if content_kind(s) == 'label']
    if len(LAST_HEAD) >= 3 and len(labelled) >= 2 and not any(content_kind(s) == 'item' for s in right):
        trows = [row for row in rows if any(content_kind(s) == 'label' for s in row) or (row[0]['rx'] > 4 and len(row) <= 2 and len(row[0]['words']) <= 4)]
        rest = [row for row in rows if row not in trows]
        out = [anchor_table(trows, [0] * len(LAST_HEAD), list(LAST_HEAD))]
        flat = [s for row in rest for s in row]
        for s in flat:
            s['rel'] = s['rx']
        return out + blocks_of(flat)
    pairs = paired_rows(left, right)
    if pairs is not None:
        return pairs
    return blocks_of(left) + blocks_of(right)


DEBUG = os.environ.get('DEBUG_PAGE')


def blocks_of(segs):
    out = []
    n = len(segs)
    kinds = []
    for j, s in enumerate(segs):
        k = content_kind(s)
        if k == 'entry' and s['text'].startswith('-') and kinds and kinds[-1] in ('label', 'cont'):
            k = 'cont'
        if k == 'prose' and s['text'].startswith('- ') and kinds and kinds[-1] in ('prose', 'cont'):
            k = 'cont'
        if (k == 'prose' and kinds and kinds[-1] in ('item', 'cont') and s['rel'] <= 4
                and not re.search(r'[.!?;:]$', segs[j - 1]['text'])):
            k = 'cont'           # the rest of a sentence that began in a list item, set at the margin
        if (k == 'prose' and s['rel'] > 4 and j > 0 and kinds[-1] in ('item', 'entry', 'label', 'cont', 'prose')
                and not (s['x1'] - s['L'] > 262 and segs[j - 1]['x1'] - segs[j - 1]['L'] < 215 and kinds[-1] == 'entry')):
            k = 'cont'
        if (k == 'prose' and len(s['words']) <= 2 and j + 1 < n and content_kind(segs[j + 1]) == 'entry'
                and not re.search(r'[.;:]$', s['text']) and not s['bold']):
            k = 'entry'          # a term wrapped on to the line before its meaning
        kinds.append(k)
    if DEBUG and any(s.get('_page') == int(DEBUG) for s in segs):
        for s, k in zip(segs, kinds):
            print(f"   {k:6} rel={s['rel']:.0f} w={s['x1']-s['L']:.0f} {'B' if s['bold'] else '-'}{'I' if s['italic'] else '-'} {s['text'][:70]}")
    i = 0
    while i < n:
        k = kinds[i]
        if k == 'hdr':
            t = clean(segs[i]['text'])
            j = i + 1
            if re.match(r'^Exercise \d+$|^Translate into', t):
                out.append(dict(type='h', text=t))
            elif SP.match(t) or re.match(r'^Base ', t) or (j < n and kinds[j] == 'entry'):
                out.append(dict(type='h5', text=t))
            else:
                out.append(dict(type='h4', text=t))
            i += 1
            continue
        if k == 'label':
            j = i
            rows = []
            while j < n and kinds[j] in ('label', 'cont'):
                rows.append(segs[j])
                j += 1
            out.append(label_table(rows, out))
            i = j
            continue
        if k in ('item', 'entry'):
            j = i
            group = []
            mixed = k == 'item' and any(kinds[x] == 'entry' for x in range(i, min(n, i + 6))) and re.search(r'\s[-=]\s', segs[i]['text'])
            while j < n and (kinds[j] == k or kinds[j] == 'cont' or (mixed and kinds[j] == 'entry')):
                if kinds[j] == 'cont':
                    group[-1].append(segs[j])
                else:
                    group.append([segs[j]])
                j += 1
            if k == 'item' and len(group) == 1 and group[0][0]['x1'] - group[0][0]['L'] > 250 and not re.search(r'\s[-=]\s', group[0][0]['text']):
                text = clean(jl([s['text'] for s in group[0]]))
                m = ITEM.match(text)
                out.append(dict(type='p', text=m.group(2).strip(), pnum=int(m.group(1))))
            else:
                out.append(list_block(group, k, out))
            i = j
            continue
        j = i
        paras = []
        while j < n and kinds[j] in ('prose', 'cont'):
            s = segs[j]
            if kinds[j] == 'prose' and (j == i or paras[-1][-1]['x1'] < s['L'] + 235 or s['first_bold'] or (s['text'].startswith('*') and s['rel'] <= 4)):
                paras.append([s])
            else:
                paras[-1].append(s)
            j += 1
        for p in paras:
            text = clean(jl([s['text'] for s in p]))
            m = re.match(r'^(\S+(?: \S+){0,3})\s+[-–]\s+(.+)$', text)
            if m and len(text) < 60 and not p[0]['first_bold'] and not text.endswith(':') and (
                    re.search(r'[āīūṃṅñṭḍṇḷ]', m.group(1)) or re.search(r', (m|f|n|adj|ind|adv|pron)$', m.group(1))):
                out.append(dict(type='vocab', items=[[clean(m.group(1)), clean(m.group(2))]]))
                continue
            b = dict(type='p', text=text)
            m = re.match(r'^(\d{1,2})\.\s+', text)
            if m and p[0]['first_bold']:
                b['pnum'] = int(m.group(1))
                b['text'] = text[m.end():]
            if sum(1 for s in p if s['italic']) * 2 > len(p):
                b['pali'] = True
            out.append(b)
        i = j
    return out


def label_table(rows, out):
    """Rows labelled Nom./Acc./1st… in one column (Singular and Plural stacked)."""
    head = None
    if out and out[-1]['type'] == 'h5' and SP.match(out[-1]['text']):
        head = out.pop()['text']
    trs = []
    for s in rows:
        ws = s['words']
        if LABEL.match(ws[0]['text']):
            lab, ws = ws[0]['text'].rstrip('.'), ws[1:]
        else:
            lab = ''
        t = clean(' '.join(w['text'] for w in ws))
        if not lab and trs:
            trs[-1][1] = (trs[-1][1] + ' ' + t).strip()
        else:
            trs.append([lab, t])
    glossed = any(re.search(r'\s[-=]\s', r[1]) and is_english(re.split(r'\s[-=]\s', r[1], 1)[1]) for r in trs) and not any(r[1].count('=') > 1 for r in trs)
    rows_out = []
    for lab, c in trs:
        if glossed:
            m = re.match(r'^(.*?)\s*[-–=]\s*(.*)$', c)
            rows_out.append([lab, [clean(m.group(1)), clean(m.group(2))] if m and is_english(m.group(2)) else [c, '']])
        else:
            rows_out.append([lab, c])
    b = dict(type='table', rows=rows_out, labels=True, glossed=glossed)
    if head:
        b['head'] = ['', head]
    return b


def list_block(group, k, out):
    """group: list of [segment, continuation…]; k is 'item' or 'entry'."""
    if k == 'entry':
        texts = []
        for g in group:
            t = clean(jl([s['text'] for s in g]))
            if texts and texts[-1].endswith('/'):
                texts[-1] = texts[-1] + ' ' + t
            elif texts and texts[-1].endswith('-') and not re.search(r'\s[-=]\s', texts[-1]):
                texts[-1] = texts[-1] + t
            elif texts and not re.search(r'\s[-=]\s|\S[-=]\s|\s-\S', texts[-1]):
                texts[-1] = texts[-1] + ' ' + t          # a term wrapped before its dash
            else:
                texts.append(t)
        if sum(1 for t in texts if '=' in t and '+' in t.split('=')[0]) * 2 > len(texts):
            blk = dict(type='lines', items=[split_gloss(t) for t in texts])   # pac + i + tvā = pacitvā = having cooked
            if out and out[-1]['type'] == 'h5' and SP.match(out[-1]['text']):
                blk['note'] = out.pop()['text']
            return blk
        items = [list(split_entry(t)) for t in texts]
        blk = dict(type='vocab', items=items)
        if sum(1 for p, e in items if e and not re.search(r'[āīūṃṅñṭḍṇḷ]', e.split()[0])) * 2 < len(items):
            blk['glossed'] = False                           # Pāli forms on both sides
        return blk
    nums, pali, eng = [], [], []
    for g in group:
        t = clean(g[0]['text'])
        m = ITEM.match(t)
        nums.append(int(m.group(1)) if m else None)
        first = m.group(2).strip() if m else t
        p_parts, e_parts = [first], []
        for s in g[1:]:
            if g[0]['italic'] and not s['italic'] and not re.search(r'[āīūṃṅñṭḍṇḷ]', s['text']):
                e_parts.append(s['text'])
            elif e_parts:
                e_parts.append(s['text'])
            else:
                p_parts.append(s['text'])
        p, e = clean(jl(p_parts)), clean(jl(e_parts))
        m = re.match(r'^(.*?)\s*[-–=]\s*(.*)$', p)
        if m and not e and is_english(m.group(2)):
            p, e = clean(m.group(1)), clean(m.group(2))
            # "Ahaṃ dīpaṃ jālesiṃ / = I lit the lamp." + "jālayiṃ" on the next line
            mm = re.match(r'^(.*?)\s+(\S+)$', e)
            if p.endswith('/') and mm and re.search(r'[āīūṃṅñṭḍṇḷ]', mm.group(2)) and mm.group(1).endswith('.'):
                p, e = p + ' ' + mm.group(2), mm.group(1)
        pali.append(p)
        eng.append(e)
    if sum(1 for p in pali if '+' in p.split('=')[0] and '=' in p) * 2 > len(pali):
        blk = dict(type='lines', items=[split_gloss(p + ((' ' + e) if e else '')) for p, e in zip(pali, eng)], numbered=True)
        if out and out[-1]['type'] == 'h5' and SP.match(out[-1]['text']):
            blk['note'] = out.pop()['text']
        return blk
    if sum(1 for e in eng if e) >= len(eng) * 0.6:
        blk = dict(type='vocab', items=[[p, e] for p, e in zip(pali, eng)], numbered=True, wide=True)
        if any(n is None for n in nums):
            blk['nums'] = [n or '' for n in nums]
        if out and out[-1]['type'] == 'h5' and SP.match(out[-1]['text']):
            blk['note'] = out.pop()['text']
        return blk
    italic = sum(1 for g in group if g[0]['italic']) * 2 > len(group)
    is_pali = italic or sum(1 for b in pali if re.search(r'[āīūṃṅñṭḍṇḷ]', b)) * 2 > len(pali)
    blk = dict(type='ex', items=[p + ((' ' + e) if e else '') for p, e in zip(pali, eng)], pali=is_pali)
    nums = [n for n in nums if n is not None]
    if nums and nums[0] != 1:
        blk['start'] = nums[0]
    return blk


