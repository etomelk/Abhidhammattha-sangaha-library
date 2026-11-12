"""Turn the column-aligned text blocks of the PDF into HTML that wraps to the screen.

Each block is split on blank lines into segments. A segment whose lines have
several columns (separated by 2+ spaces) becomes a <table>; a single-column
segment becomes a list of lines. Nothing relies on fixed-width layout, so no
horizontal scrolling is needed.
"""
import html
import re

CASE = r'(?:Nom|Gen|Dat|Acc|Ins|Instr|Abl|Loc|Voc)\.?'
HEADER_WORDS = {
    'singular', 'plural', 'sing', 'plur', 'masculine', 'feminine', 'neuter', 'masc', 'fem', 'neut',
    'active', 'reflective', 'present', 'past', 'future', 'aorist', 'imperative', 'optative',
    'conditional', 'perfect', 'imperfect', 'stem', 'base', 'bases', 'roots', 'root', 'positive',
    'comparative', 'superlative', 'cardinals', 'ordinals', 'syllables', 'pali', 'pāli', 'english',
    'noun', 'nouns', 'adj', 'adjective', 'adjectives', 'adverb', 'substantives', 'simple',
    'reduplicated', 'person', 'persons', 'number', 'suffix', 'suffixes', 'examples', 'verbs',
    'causative', 'passive', 'gerund', 'infinitive', 'meaning', 'derivative', 'derivatives',
    'nom', 'gen', 'dat', 'acc', 'ins', 'abl', 'loc', 'voc', 'case', 'cases', 'and', 'of', 'in',
    'sanskrit', 'sansk', 'form', 'forms', 'word', 'words', 'compound', 'compounds', 'quarter', 'verses',
    'free', 'seat', '|', 'st', 'nd', 'rd', 'th', 'metre', 'metres', 'name', 'pāda', 'pādas', 'odd', 'even',
}


def _cells(line):
    """Split a line on runs of 2+ spaces; return [(start, text)]."""
    out = []
    for m in re.finditer(r'\S(?:\S| (?=\S))*', line):
        out.append((m.start(), m.group(0)))
    return out


def _is_headerish(texts):
    if not texts:
        return False
    for t in texts:
        words = re.findall(r'[A-Za-zāīū]+', t.lower())
        if 'seat' in words and 'free' in words:
            continue
        if not words or any(w not in HEADER_WORDS for w in words):
            return False
    return True


def _anchors(rows):
    starts = sorted(s for r in rows for s, _ in r)
    if not starts:
        return [0]
    groups = [[starts[0]]]
    for s in starts[1:]:
        if s - groups[-1][-1] <= 3:
            groups[-1].append(s)
        else:
            groups.append([s])
    need = 2 if len(rows) >= 3 else 1
    anchors = [min(g) for g in groups if len(g) >= need]
    if not anchors or anchors[0] > min(starts):
        anchors = [min(starts)] + anchors
    return anchors


def _col(anchors, start):
    idx = 0
    for i, a in enumerate(anchors):
        if start + 2 >= a:
            idx = i
    return idx


# Words that begin an English meaning after the Pāli form(s), e.g. "devo, a god."
GLOSS_START = set("""a an the by with to for from in on upon at of o oh thou thee thy thine you your yours
i my mine we us our ours he him his she her it its they them their this that these those who whom whose
which what one let may gods gods' god's""".split())
GLOSS_LATER = {"ye"}  # English only after a form ("tumhe, ye"); as a first word it is Pāli


def _word(w):
    return w.lower().strip(",.;:!?()")


def _split_line(line, cont):
    """-> (forms, gloss). The first word is always a form unless this is a
    continuation line that starts with an English word."""
    words = line.split()
    for i, w in enumerate(words):
        if ((i > 0 or cont) and _word(w) in GLOSS_START) or (i > 0 and _word(w) in GLOSS_LATER):
            return ' '.join(words[:i]), ' '.join(words[i:])
    return line, ''


def _clean_forms(t):
    return [f.strip(' .;') for f in re.split(r'[,.;]\s+|,', t.strip(' ,.;')) if f.strip(' .;')]


def _split_cell(text):
    forms, glosses = [], []
    for k, line in enumerate(text.split('\n')):
        f, g = _split_line(line.strip(), cont=k > 0)
        if not f and g and glosses and not glosses[-1].endswith(('.', '!')):
            glosses[-1] = glosses[-1].rstrip(',') + ' ' + g
            continue
        for x in _clean_forms(f):
            if x not in forms:
                forms.append(x)
        if g:
            glosses.append(g)
    out = []
    for g in glosses:
        g = g.strip(' ,;')
        g = g[:-1] if g.endswith('.') else g
        key = ' '.join(re.sub(r"[^a-z' ]", ' ', g.lower()).split())
        if any(key in k for _, k in out):
            continue
        out = [(x, k) for x, k in out if k not in key]
        out.append((g, key))
    return forms, [g for g, _ in out]


LABEL = r'(?:' + CASE + r'|[1-3]\.|[1-3](?:st|nd|rd)\.)'


def _gaps(lines):
    """Column gaps: runs (2+ wide) blank in nearly every line, where any line that
    is not blank there still has a space inside the run (a word boundary)."""
    n = len(lines)
    width = max(len(l) for l in lines)
    need = n if n < 7 else -(-n * 85 // 100)
    def blank(l, i):
        return i >= len(l) or l[i] == ' '
    cnt = [sum(blank(l, i) for l in lines) for i in range(width)]
    first = min(len(l) - len(l.lstrip()) for l in lines if l.strip())
    gaps, i = [], first
    while i < width:
        if cnt[i] < need:
            i += 1
            continue
        j = i
        while j < width and cnt[j] >= need:
            j += 1
        if j < width and j - i >= 2 and all(
                all(blank(l, k) for k in range(i, j)) or any(blank(l, k) for k in range(i, j))
                and not all(not blank(l, k) for k in range(i, j)) for l in lines):
            # every line has at least one space in the run
            if all(any(blank(l, k) for k in range(i, j)) for l in lines):
                gaps.append((i, j))
        i = j
    return gaps


def _slice(line, gaps):
    cells, pos = [], 0
    for n, (s, e) in enumerate(gaps):
        seg = line[s:e]
        if seg.strip() and not line[e:].strip():
            # text overhangs into the gap and the line ends there: keep it whole
            cells.append(line[pos:].strip())
            return cells + [''] * (len(gaps) - n)
        if seg.strip() == '':
            cut, nxt = s, e
        else:
            k = s + seg.rfind(' ')
            cut, nxt = k, k + 1
        cells.append(line[pos:cut].strip())
        pos = nxt
    cells.append(line[pos:].strip())
    return cells


def _segment_table(lines, esc):
    # 1. pull leading row labels (Nom., Gen., 1., 2nd ...) into their own column
    nlab = sum(1 for l in lines if re.match(r'^ {0,3}' + LABEL + r'\s+\S', l))
    use_labels = nlab >= 2
    # numbered lists (1 eka, 2. dve, ... 19.) are not person labels
    if use_labels and any(re.match(r'^(?:[4-9]|\d\d)\b', l.strip()) for l in lines):
        LBL = CASE
        use_labels = sum(1 for l in lines if re.match(r'^ {0,3}' + CASE + r'\s+\S', l)) >= 2
    else:
        LBL = LABEL
    labels, body = [], []
    for l in lines:
        m = re.match(r'^ {0,3}(' + LBL + r')(\s+)', l) if use_labels else None
        if m:
            labels.append(m.group(1))
            body.append(' ' * m.end() + l[m.end():])
        elif use_labels and re.fullmatch(LBL, l.strip()):
            labels.append(l.strip())
            body.append('')
        else:
            labels.append('')
            body.append(l)

    # 2. column intervals from the ordinary rows (not headers or long captions)
    def special(l):
        cs = _cells(l)
        return (_is_headerish([t for _, t in cs]) or (len(cs) == 1 and len(l.strip()) > 34)
                or not l.strip())
    core = [b for b in body if not special(b)] or [b for b in body if b.strip()] or ['x']
    gaps = _gaps(core)
    ncols = len(gaps) + 1
    starts = [0] + [e for _, e in gaps]

    grid = []
    for lab, b in zip(labels, body):
        cells = [''] * ncols
        if b.strip() and not special(b):
            cells = _slice(b, gaps)
        elif b.strip():
            for st, t in _cells(b):
                c = 0
                for k, a in enumerate(starts):
                    if st + 3 >= a:
                        c = k
                cells[c] = (cells[c] + ' ' + t).strip()
        grid.append(([lab] if use_labels else []) + cells)
    if use_labels:
        ncols += 1

    # Drop columns that are empty everywhere.
    keep = [i for i in range(ncols) if any(g[i] for g in grid)]
    grid = [[g[i] for i in keep] for g in grid]
    ncols = len(keep)

    has_label = use_labels and ncols > 1

    # Merge continuation lines (no label) into the labelled row above.
    if has_label:
        merged = []
        for g in grid:
            texts = [c for c in g if c]
            if (merged and not g[0] and merged[-1][0] and not _is_headerish(texts)):
                prev = merged[-1]
                for i in range(1, ncols):
                    if g[i]:
                        prev[i] = (prev[i] + '\n' + g[i]) if prev[i] else g[i]
            else:
                merged.append(list(g))
        grid = merged

    # Declension/conjugation tables whose cells carry English meanings:
    # put the Pāli forms first and the meaning on its own line.
    glossed = False
    if has_label:
        split = {}
        for r, g in enumerate(grid):
            if not g[0] or _is_headerish([c for c in g if c]):
                continue
            for i in range(1, ncols):
                if g[i]:
                    split[(r, i)] = _split_cell(g[i])
        ng = sum(1 for f, gl in split.values() if gl)
        glossed = ng >= 3 and ng >= 0.4 * len(split)

    def cell_html(r, i, c):
        if glossed and (r, i) in split:
            forms, gl = split[(r, i)]
            h = f'<span class="pf">{esc(", ".join(forms))}</span>'
            if gl:
                h += f'<span class="gl">{esc("; ".join(gl))}</span>'
            return h
        if re.fullmatch(r'[◡–×| ]+', c) and '|' in c:
            segs = c.split(' | ')
            return '<span class="scheme">' + '<span class="bar"> | </span>'.join(
                f'<span class="seg">{s}</span>' for s in segs) + '</span>'
        return esc(c).replace(chr(10), "<br>")

    out = ['<button class="gltoggle" type="button" aria-pressed="true">Hide English</button>' if glossed else '',
           '<table class="gt glossed">' if glossed else '<table class="gt">']
    for r, g in enumerate(grid):
        texts = [c for c in g if c]
        if not texts:
            continue
        if len(texts) == 1 and len(texts[0]) > 34 and ncols > 2:
            out.append(f'<tr><td class="span" colspan="{ncols}">{esc(texts[0])}</td></tr>')
            continue
        head = _is_headerish(texts)
        tag = 'th' if head else 'td'
        tr = ['<tr class="hd">' if head else '<tr>']
        for i, c in enumerate(g):
            cls = ' class="lbl"' if (i == 0 and has_label and not head) else ''
            tr.append(f'<{tag}{cls}>{cell_html(r, i, c) if not head else esc(c)}</{tag}>')
        tr.append('</tr>')
        out.append(''.join(tr))
    out.append('</table>')
    return ''.join(out)


def _li(h):
    m = re.match(r"^\((?:[a-h]|[ivx]{1,5}|\d{1,2})\)(?=\s)", h)
    if m:
        return f'<li class="it"><span class="ix">{m.group(0)}</span><span>{h[m.end():].strip()}</span></li>'
    return f'<li>{h}</li>'


def render_pre(text, esc):
    """esc(str) -> escaped + linkified HTML for a cell."""
    segs = [s for s in re.split(r'\n\s*\n', text) if s.strip()]
    # fold header-only segments into the following one
    folded = []
    pending = ''
    for s in segs:
        lines = [l for l in s.split('\n') if l.strip()]
        if all(_is_headerish([t for _, t in _cells(l)]) for l in lines):
            pending += s + '\n'
            continue
        folded.append(pending + s)
        pending = ''
    if pending:
        folded.append(pending)

    parts = []
    for s in folded:
        lines = [l.rstrip() for l in s.split('\n') if l.strip()]
        ind = min(len(l) - len(l.lstrip()) for l in lines)
        lines = [l[ind:] for l in lines]
        multi = sum(1 for l in lines if len(_cells(l)) > 1)
        if multi >= max(1, len(lines) // 2) or (multi >= 1 and len(lines) <= 3 and len(_cells(lines[0])) > 1):
            # caption lines above the table (single cell, long)
            cap = []
            while len(lines) > 1 and len(_cells(lines[0])) == 1 and len(lines[0]) > 34:
                cap.append(lines.pop(0))
            for c in cap:
                parts.append(f'<p class="cap">{esc(c.strip())}</p>')
            parts.append(_segment_table(lines, esc))
        else:
            items = ''.join(_li(esc(re.sub(r" {2,}", "   ", l.strip()))) for l in lines)
            parts.append(f'<ul class="lines">{items}</ul>')
    return ''.join(parts)


def _h(full, short):
    return f'<span class="full">{full}</span><span class="short">{short}</span>'


CONSONANT_CHART = (
    '<table class="gt chart">'
    '<tr class="hd"><th></th><th colspan="5">Mutes</th>'
    f'<th rowspan="2">{_h("Semi-<br>vowels", "Semi-v.")}</th>'
    f'<th rowspan="2">{_h("Spirant", "Spir.")}</th>'
    f'<th rowspan="2">{_h("Sibilant", "Sib.")}</th>'
    f'<th rowspan="2">{_h("Vowels", "Vow.")}</th>'
    f'<th rowspan="2">{_h("Diph&shy;thongs", "Diph.")}</th></tr>'
    '<tr class="hd"><th></th>'
    f'<th>{_h("Surd", "Surd")}</th><th>{_h("Surd<br>aspirate", "+h")}</th>'
    f'<th>{_h("Sonant", "Son.")}</th><th>{_h("Sonant<br>aspirate", "+h")}</th>'
    f'<th>{_h("Nasal", "Nas.")}</th></tr>'
    f'<tr><td class="lbl">{_h("Gutturals", "Gutt.")}</td><td>k</td><td>kh</td><td>g</td><td>gh</td><td>ṅ</td><td></td><td>h</td><td></td><td>a, ā</td><td rowspan="2">e</td></tr>'
    f'<tr><td class="lbl">{_h("Palatals", "Pal.")}</td><td>c</td><td>ch</td><td>j</td><td>jh</td><td>ñ</td><td>y</td><td></td><td></td><td>i, ī</td></tr>'
    f'<tr><td class="lbl">{_h("Linguals", "Ling.")}</td><td>ṭ</td><td>ṭh</td><td>ḍ</td><td>ḍh</td><td>ṇ</td><td>r, ḷ</td><td></td><td></td><td></td><td rowspan="3">o</td></tr>'
    f'<tr><td class="lbl">{_h("Dentals", "Dent.")}</td><td>t</td><td>th</td><td>d</td><td>dh</td><td>n</td><td></td><td></td><td>s</td><td></td></tr>'
    f'<tr><td class="lbl">{_h("Labials", "Lab.")}</td><td>p</td><td>ph</td><td>b</td><td>bh</td><td>m</td><td>v</td><td></td><td></td><td>u, ū</td></tr>'
    '<tr><td class="span" colspan="11">ṃ (niggahīta) is a sonant nasal breathing outside the classes (§8).</td></tr>'
    '</table>'
)
