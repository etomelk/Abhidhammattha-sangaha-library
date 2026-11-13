#!/usr/bin/env python3
"""Render one book of the library:  python3 scripts/build.py <slug>

Reads data/library.json (book metadata) and data/<slug>.json (the text), and
writes <slug>/index.html from scripts/template.html. The page loads
shared/reader.css and shared/reader.js, which every book has in common.

Block types in a book's JSON:
  h      section heading (numbered when it carries "pnum")
  h4     sub-heading
  p      paragraph ("pnum" = the book's own number for it)
  pre    column-aligned print table, rebuilt as a wrapping HTML table (tables.py)
  vocab  word list: "items": [[pali, english], ...]; "cols": optional group headings
  ex     exercise: "items": [sentence, ...] numbered from 1 (or "start")
  table  explicit table: "rows": [[cell, ...]], "head": [..], "labels": true; a row that is
         {"group": "Singular"} spans the table; "\n" in a cell is a line break
  tables several tables side by side: "parts": [{"title", "head", "rows", "labels"}, ...]
  list   numbered / lettered list: "items": [[marker, text], ...], "ind" nesting level
  cap    paradigm caption: "text" (Pāli word and gender), "gl" (its English, hideable)
Per-book settings used here: "split" (each chapter its own file under <slug>/c/, the drawer in
<slug>/gloss.html and the search index in <slug>/search.json, all loaded when first needed), "italics" (text carries *…* for the book's italics, and italic
Pāli is linked to the drawer), "sec_anchors" (section numbers 2.2.3 are anchors #s2-2-3).
"""
import json, re, html, sys, os
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, os.path.join(HERE, 'lib'))
from tables import render_pre, CONSONANT_CHART
from study import enrich, lead_label, split_enum

slug = sys.argv[1]
lib = json.load(open(os.path.join(ROOT, 'data', 'library.json'), encoding='utf-8'))
meta = next(b for b in lib['books'] if b['slug'] == slug)
book = json.load(open(os.path.join(ROOT, 'data', f'{slug}.json'), encoding='utf-8'))
OUT = os.path.join(ROOT, slug, 'index.html')
chapters = book['chapters']
ROMAN = ['', 'I', 'II', 'III', 'IV', 'V', 'VI', 'VII', 'VIII', 'IX']


def num_label(n):
    """§1011 -> I.11 for the books keyed by the Saṅgaha's chapter and paragraph"""
    return f'{ROMAN[n // 1000]}.{n % 1000}' if n >= 1000 else str(n)




def _eff(r):
    """a row's length without the merge marks that only run it to the table's right edge"""
    n = len(r)
    while n > 1 and r[n - 1] == '<':
        n -= 1
    return n


if meta.get('join_tables'):
    # A table the document broke at a page end comes as two or more tables: one table again, so that its
    # columns line up (only a table without headers of its own that has as many columns as the one before).
    for ch in chapters:
        out = []
        for b in ch['blocks']:
            prev = out[-1] if out else None
            if (prev and b.get('type') == 'table' and prev.get('type') == 'table' and b.get('spans') and prev.get('spans')
                    and not b.get('hrows') and not b.get('cap') and b.get('rows')
                    and abs(max(map(_eff, b['rows'])) - max(map(_eff, prev['rows']))) <= 1):
                ids = (prev.get('row_ids') or [None] * len(prev['rows'])) + (b.get('row_ids') or [None] * len(b['rows']))
                rows = prev['rows'] + b['rows']
                n = max(map(_eff, rows))
                # one more column in one part (a merged cell at the right): the other rows run their last cell into it
                prev['rows'] = [list(r[:_eff(r)]) + ['<'] * (n - _eff(r)) for r in rows]
                if any(ids):
                    prev['row_ids'] = ids
                continue
            out.append(b)
        ch['blocks'] = out
# library corrections to a finished book, checked against the Pāli (scripts/audit/<slug>.py, AUDIT = [...])
_af = os.path.join(ROOT, 'scripts', 'audit', f'{slug}.py')
if os.path.exists(_af):
    sys.path.insert(0, os.path.join(ROOT, 'scripts', 'lib'))
    from audit import apply_all, string_slots
    _ns = {}
    exec(open(_af, encoding='utf-8').read(), _ns)
    for fx in _ns.get('NUMBERS', []):        # a printed section number that is wrong: the block's number, corrected
        blk = next(b for c in chapters if c['num'] == fx['chapter'] for b in c['blocks']
                   if b.get('pnum') == fx['pnum'] and b.get('text', '').startswith(fx['starts']))
        for k in ('pnum', 'pend', 'label'):
            blk.pop(k, None)
        blk.update(fx.get('set', {}))
    apply_all(string_slots(chapters), _ns['AUDIT'], slug)
    for _get, _put in string_slots(chapters):     # the source ("Dhs §700") is not a reference in the text
        _put(re.sub(r'(⟦[^|⟧]*\|[^|⟧]*\|audit\|)([^⟧]*)(⟧)', lambda m: m.group(1) + m.group(2).replace('§', '\ue000') + m.group(3), _get()))
glossary = book.get('glossary', [])
CID = meta.get('cid', 'ch')
UNIT = meta.get('unit', 'Chapter')
SIGN = meta.get('sign', '§')

PAGE_IDS = {f'pg{b["n"]}' for c in chapters for b in c['blocks'] if b['type'] == 'pg'}
ALL_IDS = {b["id"] for c in chapters for b in c["blocks"] if b.get("id")}
PAGE_IDS |= {'pg' + x for c in chapters for b in c['blocks'] for t in [b.get('text', '')] + b.get('left', []) + b.get('right', [])
             for x in re.findall(r'⟨pg:([^⟩]+)⟩', t)}
UNIT_IDS = {CID + c['num'] for c in chapters} | {b['id'] for c in chapters for b in c['blocks'] if b.get('id')}
valid = {b['pnum'] for c in chapters for b in c['blocks'] if 'pnum' in b} if CID == 'ch' else set()
SECS = {'s' + str(b['pnum']).replace('.', '-') for c in chapters for b in c['blocks'] if b['type'] == 'h' and b.get('pnum')}
XREFS = meta.get('xrefs', True)
GLOBAL_TOGGLE = meta.get('global_toggle', False)
ITALICS = meta.get('italics', False)          # Bomhard: *…* marks the book's italics
STACK = meta.get('stack_tables', False)        # Maitreya: tables of 4+ columns stack as cards on a phone
FOOTNOTES = meta.get('footnotes', False)      # Warder: [^3] in the text is a link to note 3, set after its block
LESSON_LINKS = meta.get('lesson_links', False)  # Warder: "Lesson 13", "Exercises 17, 18" in the text are links
FORMULA_GT = meta.get('formula_gt', False)    # Warder: junction formulas "*ha* + *eva* > *heva*" are chips
SPLIT = meta.get('split', False)              # Warder, Maitreya: one file per chapter, drawer and search loaded on demand
SEC_ANCHORS = meta.get('sec_anchors', False)  # Bomhard: anchors are the book's section numbers   # one Hide English switch in the top bar instead of one per table
TOGGLE_BTN = '' if GLOBAL_TOGGLE else '<button class="gltoggle" type="button" aria-pressed="true">Hide English</button>'

# ---------- cross-reference linking (Duroiselle: "see 27", "(74, vi)") ----------
def link_num(m):
    n = int(m.group(0))
    if n in valid:
        return f'<a class="xref" href="#p{n}" data-p="{n}">{n}</a>'
    return m.group(0)

NUM = re.compile(r'(?<![\d.])\d{1,3}(?![\d])')

def sec_ref(m):
    n = m.group(1)
    sid = 's' + n.replace('.', '-')
    return f'<a class="xref" href="#{sid}" data-s="{sid}">§{n}</a>' if sid in SECS else m.group(0)

def linkify(escaped):
    """escaped: html-escaped text. Links paragraph references."""
    if SEC_ANCHORS:
        escaped = re.sub(r'§(\d+(?:\.\d+)+)', sec_ref, escaped)
        escaped = re.sub(r'\b(Chapter) (\d)\b', lambda m: f'<a class="xref" href="#{CID}{m.group(2)}">{m.group(1)} {m.group(2)}</a>', escaped)
    if LESSON_LINKS:
        def unit_links(m):
            word, nums = m.group(1), m.group(2)
            pre = 'l' if word.startswith('Lesson') else 'ex'
            return word + re.sub(r'\d{1,2}', lambda n: f'<a class="xref" href="#{pre}{n.group(0)}">{n.group(0)}</a>'
                                  if (pre + n.group(0)) in UNIT_IDS else n.group(0), nums)
        escaped = re.sub(r'\b(Lessons?|Exercises?)((?:\s+\d{1,2}(?![\d.]\d))(?:(?:\s*,\s*|\s+and\s+|\s*[–-]\s*)\d{1,2}(?!\d))*)', unit_links, escaped)
    if not XREFS:
        return escaped
    out = []
    pos = 0
    for m in re.finditer(r'\(([^()]*(?:\([^()]*\)[^()]*)*)\)', escaped):
        inner = m.group(1)
        words = re.findall(r'[A-Za-z]{3,}', inner)
        ok_words = {'see', 'See', 'SEE', 'Rule', 'Rules', 'rule', 'rules', 'para', 'paras', 'ibid', 'note', 'Note', 'Remark', 'Remarks', 'and', 'ff', 'below', 'above', 'cf', 'Cf', 'chapter', 'Chapter', 'page'}
        if not re.search(r'\d', inner) or re.search(r'\d{4}', inner):
            continue
        if any(w not in ok_words for w in words):
            continue
        before = escaped[:m.start()].rstrip()
        if re.fullmatch(r'\d{1,2}', inner) and (not before or before[-1] in ':.;'):
            continue  # an enumeration marker such as "(1) Whether ...", not a reference
        if re.search(r'[Pp]\.\s*\d', inner):
            continue
        out.append(escaped[pos:m.start(1)])
        out.append(NUM.sub(link_num, inner))
        pos = m.end(1)
    out.append(escaped[pos:])
    s = ''.join(out)
    def seeref(m):
        head, nums = m.group(1), m.group(2)
        return head + NUM.sub(link_num, nums)
    s = re.sub(r'((?:[Ss]ee|[Rr]ules?|[Pp]aras?\.?|cf\.)\s+)((?:\d{1,3})(?:\s*(?:,|and|-|–)\s*\d{1,3})*)(?!\d)', seeref, s)
    return s

# ---------- vocabulary linking (Primer: words in exercises -> drawer entries) ----------
VOCAB = {}            # normalised headword -> key
FOLD = str.maketrans({'â': 'ā', 'î': 'ī', 'û': 'ū', 'ṁ': 'ṃ'})
def vkey(s):
    """The lookup key of a Pāli word, the same for every book: lower case, ṁ = ṃ, and
    Müller's circumflexes (â î û) read as the macrons (ā ī ū)."""
    return re.sub(r'[^a-zāīūṃṅñṭḍṇḷ]', '', s.lower().translate(FOLD))
for g in glossary:
    if (g.get('key') or '').startswith('en-') and meta.get('en_lookup') is False:
        continue        # English headwords are not looked up (Maitreya: "he", "so" would catch the Pāli words)
    for hw in re.split(r'\s*/\s*' if not ITALICS else r'\s*(?:/|,|~| or )\s*', g['term']):
        hw = re.sub(r'\s*\(.*?\)', '', hw).strip()
        if hw and vkey(hw) not in VOCAB and (not ITALICS or len(vkey(hw)) > 1):
            VOCAB[vkey(hw)] = g.get('key') or vkey(g['term'])
# entries may list further lookup forms (Warder: the principal parts of a verb with its prefixes, noun stems)
for g in glossary:
    for f in g.get('forms', []):
        if vkey(f) not in VOCAB:
            VOCAB[vkey(f)] = g.get('key') or vkey(g['term'])
# the English–Pāli glossary gives forms the Pāli lists lack (tumhe, mayaṃ …)
for g in glossary:
    if (g.get('key') or '').startswith('en-'):
        for form in re.split(r'\s*/\s*', g['def']):
            form = re.sub(r'\s*\(.*?\)', '', form).strip()
            if form and ' ' not in form and vkey(form) not in VOCAB:
                VOCAB[vkey(form)] = g['key']
# Pāli -> Pāli lists in the lessons (gerunds, participles, future forms…): link each form to its verb
for c in chapters:
    for b in c['blocks']:
        if b['type'] == 'vocab' and b.get('glossed') is False:
            for p, e in b['items']:
                k = VOCAB.get(vkey(re.split(r'\s*/\s*', p)[0]))
                if not k:
                    continue
                for form in re.split(r'[,;/]\s*|\s+', re.sub(r'=.*', '', e.split(' but ')[0])):
                    f = vkey(form)
                    if len(f) >= 3 and f not in VOCAB and re.search(r'[āīūṃṅñṭḍṇḷ]|^[a-z]+$', f) and form.strip() == form and not re.search(r'[A-Z]', form):
                        VOCAB[f] = k

# the inflections the Primer teaches, longest first, so "narehi" -> "nara"
ENDINGS = sorted(set('''o ā ṃ e ena ehi ebhi ā asmā amhā āya assa ānaṃ e esu asmiṃ amhi āni ī ayo iṃ inā īhi ismā imhā īnaṃ ismiṃ imhi ino
 īni ū uṃ ūhi usmā umhā ūnaṃ usmiṃ umhi ūni uno avo ave uyo iyo iyā iyaṃ āyo āhi āsu āsaṃ ā uyā uyaṃ ūsu ūbhi
 ti nti si tha mi ma issati issanti issasi issatha issāmi issāma eyya eyyuṃ eyyāsi eyyātha eyyāmi eyyāma
 tu ntu hi tha i iṃsu o ttha iṃ imha mha a ā tvā itvā etvā tvāna ya tuṃ ituṃ etuṃ nto ntā ntaṃ ntassa ntena ntehi ntesu ntānaṃ anto antā antaṃ antena antehi antassa ta tā tāni to ito itā
 māno mānā mānaṃ mānena mānehi mānassa mānānaṃ māne amāno amānā amānaṃ etha ema esi emi enti eti essati essanti essāmi essāma issa
 ssati ssanti aṃ ūni ārā ārehi ārānaṃ ari āro āraṃ u ūsu unā antu āni ssa smā mhā smiṃ mhi'''.split()), key=len, reverse=True)

def link_vocab(escaped):
    """Link every Pāli word in an exercise sentence to its vocabulary entry, if we can
    find one by stripping the inflections taught in the book."""
    if not VOCAB:
        return escaped
    seen = set()
    def rep(m):
        w = m.group(0)
        k = vkey(w)
        if PALI_TEXT:           # Müller's text repeats its formulas: link a word once per paragraph
            if k in seen:
                return w
            seen.add(k)
        cands = [k]
        for e in ENDINGS:
            if k.endswith(e) and len(k) - len(e) >= 2:
                stem = k[:-len(e)]
                cands += [stem, stem + 'a', stem + 'i', stem + 'u', stem + 'ā', stem + 'ī', stem + 'ū', stem + 'ti', stem + 'ati', stem + 'eti', stem + 'āti', stem + 'oti', stem + 'āti']
        for c in cands:
            if c in VOCAB:
                return f'<a class="vw" href="#gloss" data-k="{VOCAB[c]}">{w}</a>'
        return w
    return re.sub(r'[A-Za-zāīūṃṅñṭḍṇḷĀĪŪâîûÂÎÛṄÑṬḌṆḶ]+', rep, escaped)

# ---------- the book's italics (Bomhard): *…* -> <i>…</i>, Pāli linked to the drawer ----------
def italics(escaped):
    if PALI_TEXT:
        escaped = text_marks(escaped)
        escaped = re.sub(r'\*\*([^*<>]+)\*\*', r'<b>\1</b>', escaped)
        return re.sub(r'(?<![\w*])\*([^*\s][^*]*)\*(?!\w)', r'<i>\1</i>', escaped)
    if not ITALICS:
        return escaped
    def run(m):
        t = m.group(1)
        k = vkey(t)
        if k in VOCAB:
            return f'<i><a class="vw" href="#gloss" data-k="{VOCAB[k]}">{t}</a></i>'
        if len(t.split()) > 4:          # a sentence or a title in italics, not a Pāli citation
            return '<i>' + t + '</i>'
        return '<i>' + link_vocab(t) + '</i>'
    escaped = re.sub(r'\*\*([^*<>]+)\*\*', r'<b>\1</b>', escaped)
    return re.sub(r'\*([^*]+)\*', run, escaped)


GT_FORMULA = re.compile(r'(\*[^*]+\*(?:\s?\+\s?\*[^*]+\*)+)\s?&gt;\s?(\*[^*]+\*)')

def gt_formulas(escaped):
    """Warder writes junction as "a + b > c": set it as a formula chip (parts, then the result in bold)."""
    if not FORMULA_GT:
        return escaped
    def chip(m):
        parts = re.split(r'\s?\+\s?', m.group(1))
        return ('<span class="eq">' + '<span class="op">+</span>'.join(f'<span class="pt">{p}</span>' for p in parts)
                + f'<span class="op to">&gt;</span><span class="res">{m.group(2)}</span></span>')
    return GT_FORMULA.sub(chip, escaped)


# ---------- Müller (pali_text): corrections, spaced letters, links to numbered sections ----------
PALI_TEXT = meta.get('pali_text', False)
KIND_TITLE = {'errata': 'Corrected from Müller’s List of Errata; printed', 'misprint': 'Misprint corrected; printed', 'sic': 'So printed; the slip is kept, as'}

AUDIT_TIPS = []


def text_marks(escaped):
    """⟦new|printed|kind⟧ -> the corrected text, marked, with the printed reading on hover;
    ~word~ -> letter-spaced (Müller's s p a c e d words)."""
    def corr(m):
        new, old, kind, ref = m.group(1), m.group(2), m.group(3), m.group(4)
        if meta.get('plain_corrections'):   # the study notes were drafts: the corrected text, unmarked
            return new
        if kind == 'audit':                  # a finished book: marked quietly, the note gives the print and the source
            old = re.sub(r'<[^>]+>', '', old)     # a word linked by an earlier pass: its text only
            ref = re.sub(r'<[^>]+>', '', ref or '')
            src = f' ({ref})'.replace('\ue000', '§') if ref else ''
            if not old:
                tip = f'Added by the library{src}; not printed'
            elif not new:
                tip = f'Removed by the library{src}; printed “{old.strip()}”'
            else:
                tip = f'Corrected by the library{src}; printed “{old.strip()}”'
            AUDIT_TIPS.append(tip)       # set as the title at the end, after every linking pass
            return f'<span class="corr audit{" del" if not new else ""}" data-ct="{len(AUDIT_TIPS) - 1}">{new or "[−]"}</span>'
        tip = f'{KIND_TITLE.get(kind, "Corrected; printed")} “{old}”'
        return f'<span class="corr {kind}" title="{tip}">{new}</span>'
    escaped = re.sub(r'⟦([^|⟧]*)\|([^|⟧]*)\|(\w+)(?:\|([^|⟧]*))?⟧', corr, escaped)
    escaped = re.sub(r'__(.+?)__', r'<u>\1</u>', escaped)              # Nhu Lien: underline
    escaped = re.sub(r'\^\{([^}]*)\}', r'<sup>\1</sup>', escaped)      # Nhu Lien: "2^{nd}"
    return re.sub(r'~([^~]+)~', r'<span class="spaced">\1</span>', escaped)

NSEC = {n for c in chapters for b in c['blocks'] if 'pnum' in b for n in range(b['pnum'], b.get('pend', b['pnum']) + 1)} if PALI_TEXT or meta.get('index_links') else set()

def sec_links(escaped):
    """Müller's references to his numbered sections: "No. 1018", "Nos. 59–63", "(528, 552)",
    "1014=1398", "See 63, 65", "282 and foll.", and the numbers of the index entries. A number
    is linked only after such a lead word (or in a run of numbers that follows one) and only
    when that section exists; page numbers ("p. 21"), roman-numbered chapters ("II. 9") and
    years are left alone."""
    if not PALI_TEXT:
        return escaped
    def one(n, to=None):
        k = int(to or n)
        return f'<a class="xref" href="#p{k}" data-p="{k}">{n}</a>' if k in NSEC else n
    def rng(m):
        a, b = m.group(1), m.group(3)
        full = a[:len(a) - len(b)] + b if len(b) < len(a) else b      # "968—69" is 968–969
        return one(a) + m.group(2) + one(b, full)
    num_run = r'\d{1,4}(?:\s*(?:,|and|&amp;|=|—|–|-|\(|\))\s*\d{1,4})*'
    lead = r'(?<![\w.])(Nos?\.|[Qq]uestions?|[Ss]ee|[Cc]ompare|[Cc]omp\.|[Cc]f\.|below,|above,|at|in|from|to|=)(\s*\(?)'
    def run(m):
        return m.group(1) + m.group(2) + re.sub(r'\d{1,4}', lambda k: one(k.group(0)), m.group(3))
    def on_text(h, fn):
        """apply fn to the text outside tags and outside links already made"""
        parts = re.split(r'(<a\b[^>]*>.*?</a>|<[^>]+>)', h)
        return ''.join(x if x.startswith('<') else fn(x) for x in parts)
    out = on_text(escaped, lambda t: re.sub(lead + '(' + num_run + r')(?![\d.]\d)', run, t))
    # ranges "59–63", "596—741"
    out = on_text(out, lambda t: re.sub(r'(?<![\d.])(\d{1,4})([–—])(\d{1,4})(?!\d)', rng, t))
    # any other number of three or four figures, unless it is a page ("p. 414"), follows a
    # roman chapter number ("xii. 555", "VII. 8"), is followed by "ff." of a page, or is a year
    out = on_text(out, lambda t: re.sub(r'((?<![\w.])(?<!p\. )(?<!pp\. )(?<![IVXLivxl]\. )(?<!ed\. ))(\d{3,4})(?![\d])(?!\s*ff)', lambda m: m.group(1) + one(m.group(2)), t))
    return out

def index_refs(escaped):
    """An index entry's numbers: every number is a section (Müller), or a printed page
    (Rhys Davids: "index_pages", roman numbers too, "lxivf" = lxiv and following)."""
    if '<' in escaped:                   # outside the tags (a correction's note is an attribute)
        return ''.join(x if x.startswith('<') else index_refs(x) for x in re.split(r'(<[^>]+>)', escaped))
    if INDEX_PAGES:
        def pg(m):
            n = m.group(1)
            return f'<a class="xref" href="#pg{n}" data-s="pg{n}">{n}</a>' if f'pg{n}' in PAGE_IDS else n
        return re.sub(r'(?<![\w.])(\d{1,3}|[ivxlc]{1,7})(?=f{0,2}\b|[,.;]|$)', pg, escaped)
    return re.sub(r'(?<![\w.])(?<!Du-)(?<!Ti-)(\d{1,4})(?![\d])', lambda m: f'<a class="xref" href="#p{int(m.group(1))}" data-p="{int(m.group(1))}">{m.group(1)}</a>'
                  if int(m.group(1)) in NSEC else m.group(1), escaped)

def matika_refs(h):
    """Khine's index: "Du-106" (the 106th duka of his Mātikā), "Ti-4" (the 4th tika) -> the item."""
    def one(m):
        kind, n = m.group(1), int(m.group(2))
        t = f't{n}' if kind == 'Ti' else (f'd{n}' if n <= 100 else f's{n - 100}')
        return f'<a class="xref" href="#m{t}">{m.group(0)}</a>' if f'm{t}' in ALL_IDS else m.group(0)
    return ''.join(x if x.startswith('<') else re.sub(r'(?<![\w-])(Du|Ti)-(\d{1,3})(?!\d)', one, x) for x in re.split(r'(<[^>]+>)', h))


# ---------- Rhys Davids: global notes, § / page / note / bibliography references, inline anchors ----------
NOTES_GLOBAL = meta.get('notes_global', False)   # notes numbered through the book: #n204
REF_LINKS = meta.get('ref_links', False)
INLINE = REF_LINKS or meta.get('inline_markup', False)     # the book's own *italics* / **bold** markup, rendered by rd_inline
SEE_PARA = meta.get('see_para', False)                     # Khine: "(See para 595)", "paras 2 to 15", the Mātikā's "(1003, 1402)"
INDEX_PAGES = meta.get('index_pages', False)
PTS = meta.get('pts_sections', False)
BIB_IDS = {b['id'] for c in chapters for b in c['blocks'] if b.get('bib')}
RD_SECS = set()
for c in chapters:
    for b in c['blocks']:
        if b.get('pnum') is not None:
            RD_SECS |= set(range(b['pnum'], b.get('pend', b['pnum']) + 1))
        for a in b.get('alias', []):
            RD_SECS.add(a[1:])
        for t in [b.get('text', '')] + b.get('left', []) + b.get('right', []):
            for a, z in re.findall(r'⟨sec:(\d+)(?:-(\d+))?⟩', t):
                RD_SECS |= set(range(int(a), int(z or a) + 1))
NOTE_IDS = {b['note'] for c in chapters for b in c['blocks'] if b.get('note')}


def ref_links(escaped):
    """§ 2, §§ 1003–6, § 498a; p. 245, pp. 230, 231; n. 1041; [37] (the bibliography)."""
    if not REF_LINKS:
        return escaped
    def on_text(h, fn):
        parts = re.split(r'(<a\b[^>]*>.*?</a>|<[^>]+>)', h)
        return ''.join(x if x.startswith('<') else fn(x) for x in parts)
    def sec(n, label=None):
        key = int(n) if n.isdigit() else n
        return f'<a class="xref" href="#p{n}" data-s="p{n}">{label or n}</a>' if key in RD_SECS else (label or n)
    def secs(m):
        def one(k):
            a, e = k.group(1), k.group(2)
            if e:
                full = a[:len(a) - len(e)] + e if len(e) < len(a) else e
                return sec(a) + k.group(0)[len(a):len(k.group(0)) - len(e)] + sec(full, e)
            return sec(a)
        return m.group(1) + re.sub(r'(\d{1,4}[a-z]?)(?:\s*[–-]\s*(\d{1,4}))?', one, m.group(2))
    def pages(m):
        return m.group(1) + re.sub(r'\b(\d{1,3}|[ivxlc]{1,7}|M\d)\b', lambda k: f'<a class="xref" href="#pg{k.group(1)}" data-s="pg{k.group(1)}">{k.group(1)}</a>'
                                   if f'pg{k.group(1)}' in PAGE_IDS else k.group(1), m.group(2))
    def note(m):
        n = int(m.group(2))
        return m.group(1) + (f'<a class="xref" href="#n{n}" data-s="n{n}">{n}</a>' if n in NOTE_IDS else m.group(2))
    def bib(m):
        return f'[<a class="xref" href="#b{m.group(1)}" data-s="b{m.group(1)}">{m.group(1)}</a>]' if f'b{m.group(1)}' in BIB_IDS else m.group(0)
    def fn(t):
        t = re.sub(r'(§§?\s*)(\d{1,4}[a-z]?(?:\s*[–-]\s*\d{1,4})?(?:(?:,\s*|\s+and\s+)\d{1,4}[a-z]?(?:\s*[–-]\s*\d{1,4})?)*)', secs, t)
        t = re.sub(r'(\bpp?\.\s*)((?:\d{1,3}|[ivxlc]{1,7}|M\d)(?:f{1,2}\.?)?(?:(?:,\s*|\s*[–-]\s*)(?:\d{1,3}|[ivxlc]{1,7})(?:f{1,2}\.?)?)*)', pages, t)
        t = re.sub(r'(\bnn?\.\s*)(\d{1,4})', note, t)
        t = re.sub(r'\[(\d{1,3})\]', bib, t)
        return t
    return on_text(escaped, fn)


PAGE_BOOKS = meta.get('page_books', {})      # a book made of two (Nhu Lien): page ids T12, D12 -> "Tika p. 12"


def page_no(n):
    n = str(n)
    if PAGE_BOOKS and n[:1] in PAGE_BOOKS:
        return n if meta.get('page_letter_visible') else n[1:]
    return n


def page_ref(n):
    n = str(n)
    return f'{PAGE_BOOKS[n[:1]]} p. {n[1:]}' if PAGE_BOOKS and n[:1] in PAGE_BOOKS else f'p. {n}'


# The Expositor prints the PTS pages of the Aṭṭhasālinī it translates, "[125]" (⟨pts:125⟩): an anchor #a125
# and a link to that page of the Pāli (#pgP125 in the Aṭṭhasālinī); the Aṭṭhasālinī's PTS pages link back.
PTS_PAGES = meta.get('pts_pages')             # the Expositor: "atthasalini"
PAGE_BACK = meta.get('page_back')             # the Aṭṭhasālinī: {"P": "expositor"}
_BACK = {}
if PAGE_BACK:
    for _l, _osl in PAGE_BACK.items():
        _od = json.dumps(json.load(open(os.path.join(ROOT, 'data', f'{_osl}.json'), encoding='utf-8')), ensure_ascii=False)
        _BACK[_l] = (_osl, set(re.findall(r'⟨pts:(\d+)⟩', _od)))
if PTS_PAGES:
    _PTS_HAVE = set(re.findall(r'⟨pg:P(\d+)⟩', open(os.path.join(ROOT, 'data', f'{PTS_PAGES}.json'), encoding='utf-8').read()))


def pg_mark(n):
    back = ''
    if n[:1] in _BACK and n[1:] in _BACK[n[:1]][1]:
        osl = _BACK[n[:1]][0]
        back = f'<a class="xb pgx" href="../{osl}/#a{n[1:]}" title="This page in English (Pe Maung Tin, The Expositor)">Eng</a>'
    return f'<span class="pgmark pgin" id="pg{n}" data-ref="{page_ref(n)}" title="Printed page {page_no(n)}">{page_no(n)}</span>{back}'


def pts_mark(m):
    n = m.group(1)
    if PTS_PAGES:       # a page the digital Pāli does not mark: the nearest page before it
        t = next((str(k) for k in range(int(n), 0, -1) if str(k) in _PTS_HAVE), None)
    if PTS_PAGES and t:
        return (f'<a class="ptsp" id="a{n}" data-ref="PTS p. {n}" href="../{PTS_PAGES}/#pgP{t}" '
                f'title="Page {n} of the PTS Aṭṭhasālinī: open the Pāli">[{n}]</a>')
    return f'<span class="ptsp" id="a{n}" data-ref="PTS p. {n}">[{n}]</span>'


def inline_marks(h):
    """⟨pg:12⟩ where a printed page begins inside a paragraph; ⟨sec:341⟩ a section number
    printed inside a paragraph; ⟨pts:125⟩ a page of the PTS Aṭṭhasālinī (the Expositor)."""
    h = re.sub(r'⟨pg:([^⟩]+)⟩', lambda m: pg_mark(m.group(1)), h)
    h = re.sub(r'⟨pts:(\d+)⟩', pts_mark, h)
    h = re.sub(r'⟨pgl:([^⟩]+)⟩', lambda m: f'<a class="xref" href="#pg{m.group(1)}">{m.group(1)}</a>', h)   # a page of this book
    def sec(m):
        a, z = int(m.group(1)), int(m.group(2) or m.group(1))
        lab = f'[{a}–{z}]' if z > a else f'[{a}]'
        extra = ''.join(f'<span class="sanchor" id="p{k}"></span>' for k in range(a + 1, z + 1))
        return f'<span class="isec" id="p{a}" data-ref="§{a}">{lab}</span>{extra}' + cross_links(a)
    return re.sub(r'⟨sec:(\d+)(?:-(\d+))?⟩', sec, h)


# the other books numbered by the PTS sections: a small link from each section to the same section there.
# A book with its own numbering (Khine: the Sixth Council's) maps its sections to the PTS ones
# ("pts_map", data/<slug>-pts.json, made by matching the sections by content); its chips, and
# the chips to it, go only where that map has the section.
def _have(slug_):
    od = json.load(open(os.path.join(ROOT, 'data', f'{slug_}.json'), encoding='utf-8'))
    have = set()
    for c in od['chapters']:
        for b in c['blocks']:
            if b.get('pnum') is not None:
                have |= set(range(b['pnum'], b.get('pend', b['pnum']) + 1))
            for t in [b.get('text', '')] + b.get('left', []) + b.get('right', []):
                for a, z in re.findall(r'⟨sec:(\d+)(?:-(\d+))?⟩', t):
                    have |= set(range(int(a), int(z or a) + 1))
    return have


def _pts_map(ob):
    f = os.path.join(ROOT, 'data', ob['pts_map'])
    return {int(k): v for k, v in json.load(open(f, encoding='utf-8')).items()} if os.path.exists(f) else {}


PTS_MAP = _pts_map(meta) if meta.get('pts_map') else {}      # this book's § -> the PTS §
XLINK = PTS or bool(PTS_MAP)
OTHER_PTS = []          # (slug, label, PTS § -> that book's §, title)
SAME_NUM = []           # books numbered like this one (the Sixth Council numbers: Khine, Nhu Lien): (slug, label, their §, title)
if XLINK:
    for ob in lib['books']:
        if ob['slug'] == slug:
            continue
        full = f'{ob["author"]}, {ob["short"]}'
        if PTS_MAP and ob.get('pts_map') == meta.get('pts_map'):
            SAME_NUM.append((ob['slug'], ob.get('pts_label', ob['short']), _have(ob['slug']), full))
            continue
        if ob.get('pts_sections'):
            have = _have(ob['slug'])
            OTHER_PTS.append((ob['slug'], ob.get('pts_label', ob['short']), {n: n for n in have}, full))
        elif ob.get('pts_map') and PTS:
            inv = {}
            ohave = _have(ob['slug'])             # only the sections that book has (Nhu Lien: the Aṭṭhakathā Kaṇḍa)
            for k, v in sorted(_pts_map(ob).items()):
                if k in ohave:
                    inv.setdefault(v, k)
            if inv:
                OTHER_PTS.append((ob['slug'], ob.get('pts_label', ob['short']), inv, full))


def cross_links(n, have_any=None):
    """A chip to the same section in the other books (§n, or the first number of a range they have)."""
    out = []
    for osl, lab, have, full in SAME_NUM:
        if n in have:
            out.append(f'<a class="xb" href="../{osl}/#p{n}" title="§{num_label(n)} in {html.escape(full, quote=True)}">{html.escape(lab, quote=False)}</a>')
    if PTS_MAP:
        n = PTS_MAP.get(n)
        have_any = None
        if n is None:
            return ''.join(out)
    for osl, lab, to, full in OTHER_PTS:
        k = n if n in to else next((x for x in (have_any or []) if x in to), None)
        if k is not None:
            t = to[k]
            out.append(f'<a class="xb" href="../{osl}/#p{t}" title="§{t} in {html.escape(full, quote=True)}">{html.escape(lab, quote=False)}</a>')
    return ''.join(out)


def bold_lookup(h):
    """Rhys Davids' bold (Pāli terms) and bold italic; a bold or a short italic Pāli word found
    in her Index of Pali Words opens it in the drawer."""
    def look(t, tag):
        k = vkey(re.sub(r'<[^>]+>', '', t))
        k = next((x for x in (k, k[:-1] if k.endswith('ṃ') else k + 'ṃ', k[:-1] + 'aṃ' if k.endswith('o') else k) if x in VOCAB), k)
        if k in VOCAB and len(t.split()) <= 3:
            return f'<{tag}><a class="vw" href="#gloss" data-k="{VOCAB[k]}">{t}</a></{tag}>'
        return f'<{tag}>{t}</{tag}>'
    h = re.sub(r'\*\*\*([^*]+)\*\*\*', lambda m: '<b>' + look(m.group(1), 'i') + '</b>', h)
    h = re.sub(r'\*\*([^*]+)\*\*', lambda m: look(m.group(1), 'b'), h)
    return re.sub(r'\*([^*]+)\*', lambda m: look(m.group(1), 'i'), h)


CUR = {}     # the block being rendered


def para_links(escaped):
    """Khine's references to his own paragraphs: "See para 595", "(see para 66)", "paras 2 to 15,
    16 and 54", "(See 604.)"; in the Mātikā, the paragraphs after each item "(1003, 1402)".
    Only the paragraphs this volume has are links."""
    def on_text(h, fn):
        parts = re.split(r'(<a\b[^>]*>.*?</a>|<[^>]+>)', h)
        return ''.join(x if x.startswith('<') else fn(x) for x in parts)
    def num(m):
        n = int(m.group(0))
        return f'<a class="xref" href="#p{n}" data-p="{n}">{m.group(0)}</a>' if n in valid else m.group(0)
    def run(m):
        return m.group(1) + re.sub(r'\d{1,4}', num, m.group(2))
    def fn(t):
        t = re.sub(r'(\b(?:[Pp]aras?\.?|[Ss]ee)\s+)(\d{1,4}(?:(?:\s*(?:,|and|to|-|–)\s*)\d{1,4})*)', run, t)
        if CUR.get('_cid') in [CID + x for x in meta.get('ref_parts', ['M'])]:     # the Mātikā, the Rūpa Mātikā: "(1003, 1402)", "(672)"
            t = re.sub(r'(\()(\d{1,4}(?:\s*[-–,]\s*\d{1,4})*)(?=[\s.]*\))', lambda m: run(m) if re.search(r'\d{3}', m.group(2)) else m.group(0), t)
        return t
    return on_text(escaped, fn)


def rd_inline(t, escaped=False):
    h = t if escaped else html.escape(t, quote=False)
    # a correction's source ("Dhs §700") is not a reference in the text: keep it out of the § links
    h = re.sub(r'(⟦[^|⟧]*\|[^|⟧]*\|audit\|)([^⟧]*)(⟧)', lambda m: m.group(1) + m.group(2).replace('§', '\ue000') + m.group(3), h)
    h = ref_links(h)
    if SEE_PARA:
        h = para_links(h)
    return inline_marks(bold_lookup(text_marks(h)))


# ---------- render ----------
def soft_breaks(h):
    """Nhu Lien's tables: a Pāli compound of 14 letters or more (cittasaṁsaṭṭhasamuṭṭhāna…) may break
    in a narrow column, with a hyphen, every 7 letters; shorter words never break."""
    def word(m):
        w = m.group(0)
        return '&shy;'.join(w[i:i + 7] for i in range(0, len(w), 7)) if len(w) >= 14 else w
    parts = re.split(r'(<[^>]+>|&[a-z]+;)', h)
    return ''.join(x if x.startswith('<') or x.startswith('&') else re.sub(r'[^\W\d_]{14,}', word, x) for x in parts)

def cell_html(text):
    """Table cells and list lines: formulas as chips (grids inline), roots styled."""
    if meta.get('rich_cells'):             # Nhu Lien: the book's own markup in cells, " // " a line break
        return soft_breaks(rd_inline(text).replace(' // ', '<br>'))
    h, grids = enrich(text, linkify)
    h = re.sub(r'\x00G(\d+)\x00', lambda m: grids[int(m.group(1))], h)
    if ITALICS:
        h = italics(h).replace('\n', '<br>')
        if '*' not in text and '<i>' not in h:
            h = link_vocab(h)      # a cell of Pāli forms: link each to the index when it has an entry
    elif PALI_TEXT:
        h = italics(sec_links(h))
    return h

def anchor_id(b):
    pn = b.get('pnum')
    if pn is None:
        return None
    if SEC_ANCHORS:
        return 's' + str(pn).replace('.', '-')
    return f'p{pn}' if CID == 'ch' else f'{b["_cid"]}-{pn}'

def pnum_span(b):
    pn = b.get('pnum')
    xb = cross_links(pn, range(pn, b.get('pend', pn) + 1)) if XLINK and pn is not None else ''
    if pn is not None and REF_LINKS:            # Rhys Davids: her label "[564a, 565]", "[1003–6]"
        lab = html.escape(b.get('label', str(pn)).strip('[]'), quote=False)
        extra = ''.join(f'<span class="sanchor" id="p{n}"></span>' for n in range(pn + 1, b.get('pend', pn) + 1))
        extra += ''.join(f'<span class="sanchor" id="{a}"></span>' for a in b.get('alias', []))
        return f'<span class="pnum">{lab}</span>{extra}{xb}'
    if pn is not None and b.get('pend'):        # Müller: one paragraph for §132–145; each number is an anchor
        return f'<span class="pnum">{pn}–{b["pend"]}</span>' + ''.join(f'<span class="sanchor" id="p{n}"></span>' for n in range(pn + 1, b['pend'] + 1)) + xb
    if pn is not None and b.get('pmoved'):     # Müller: a number his errata move
        return f'<span class="pnum corr errata" title="{html.escape(b["pmoved"], quote=True)}">{pn}</span>' + xb
    if pn is not None and b.get('label'):       # the Saṅgaha's numbers: "I.11" (key 1011), with the anchor #p1-11 beside #p1011
        alias = ''.join(f'<span class="sanchor" id="{a}"></span>' for a in b.get('alias', []))
        return f'<span class="pnum">{html.escape(b["label"], quote=False)}</span>{alias}{xb}'
    return f'<span class="pnum">{pn}</span>{xb}' if pn is not None else ''

def pali_html(x):
    """A Pāli form (or several, 'a / b'), each linked to its vocabulary entry when there is one."""
    return ' / '.join(f'<a class="vw" href="#gloss" data-k="{VOCAB[vkey(y)]}">{html.escape(y, quote=False)}</a>'
                      if vkey(y) in VOCAB else html.escape(y, quote=False) for y in re.split(r'\s*/\s*', x))


def render_vocab(b):
    items = b['items']
    glossed = b.get('glossed', True)
    out = ['<div class="vocab' + (' wide' if b.get('wide') else '') + (' plain' if not glossed else '') + '">']
    if b.get('note'):
        out.append(f'<p class="cap">{html.escape(b["note"], quote=False)}</p>')
    if glossed:
        out.append(TOGGLE_BTN)
    nums = b.get('nums')
    tag = 'ol' if b.get('numbered') else 'ul'
    out.append(f'<{tag} class="vl">')
    for i, (pali, eng) in enumerate(items):
        if b.get('numbered'):
            p = link_vocab(html.escape(pali, quote=False))
        else:
            p = pali_html(pali)
        attr = ''
        if nums is not None:
            attr = f' value="{nums[i]}"' if nums[i] != '' else ' class="unnum"'
        if ITALICS:
            gl = italics(html.escape(eng, quote=False))      # italic Pāli in the gloss is linked by italics()
        else:
            gl = html.escape(eng, quote=False) if glossed else link_vocab(html.escape(eng, quote=False))
        out.append(f'<li{attr}><span class="pf">{p}</span>' + (f'<span class="gl">{gl}</span>' if eng else '') + '</li>')
    out.append(f'</{tag}></div>')
    return ''.join(out)


def render_lines(b):
    tag = 'ol' if b.get('numbered') else 'ul'
    out = []
    if b.get('note'):
        out.append(f'<p class="cap">{html.escape(b["note"], quote=False)}</p>')
    def li(t):
        if isinstance(t, list):
            return f'<li><span class="pf">{cell_html(t[0])}</span> <span class="gl">= {html.escape(t[1], quote=False)}</span></li>'
        return f'<li>{cell_html(t)}</li>'
    cls = 'lines verse' if b.get('verse') else 'lines fl'
    if b.get('verse'):
        return ''.join(out) + '<ul class="lines verse">' + ''.join(f'<li>{link_vocab(html.escape(t, quote=False))}</li>' for t in b['items']) + '</ul>'
    out.append(f'<{tag} class="{cls}">' + ''.join(li(t) for t in b['items']) + f'</{tag}>')
    return ''.join(out)


def render_ex(b):
    start = b.get('start', 1)
    lis = []
    nums = b.get('nums')
    for i, s in enumerate(b['items']):
        h = html.escape(s, quote=False)
        if b.get('pali', True):
            h = link_vocab(h.replace('*', '') if ITALICS else h)   # a Pāli sentence is italic as a whole; its words are linked
        elif ITALICS:
            h = italics(h)
        lis.append(f'<li value="{nums[i]}">{h}</li>' if nums else f'<li>{h}</li>')
    cls = 'ex pali' if b.get('pali', True) else 'ex eng'
    return f'<ol class="{cls}" start="{start}">{"".join(lis)}</ol>'

def render_table(b):
    stack = STACK and b.get('head') and len(b['head']) >= 4 and max(sum(len(c[0] if isinstance(c, list) else c) for c in r) for r in b["rows"] if isinstance(r, list)) > 28
    out = ['<table class="gt' + (' glossed' if b.get('glossed') else '') + (' stack' if stack else '') + '">']
    if b.get('glossed'):
        out.insert(0, TOGGLE_BTN)
    if b.get('head'):
        out.append('<tr class="hd">' + ''.join(f'<th>{html.escape(c, quote=False)}</th>' for c in b['head']) + '</tr>')
    pali_cells = CID != 'ch'
    ncol = max(len(r) for r in b['rows'] if isinstance(r, list)) if b['rows'] else 1
    for row in b['rows']:
        tds = []
        if isinstance(row, dict):
            out.append(f'<tr class="grp"><td colspan="{ncol}">{html.escape(row["group"], quote=False)}</td></tr>')
            continue
        for i, c in enumerate(row):
            dh = f' data-h="{html.escape(b["head"][i], quote=True)}"' if stack and i < len(b['head']) and b['head'][i] else ''
            if i == 0 and b.get('labels'):
                tds.append(f'<td class="lbl"{dh}>{html.escape(c, quote=False)}</td>')
            elif isinstance(c, list):
                tds.append(f'<td{dh}><span class="pf">{cell_html(c[0])}</span>' + (f'<span class="gl">{html.escape(c[1], quote=False)}</span>' if len(c) > 1 and c[1] else '') + '</td>')
            else:
                if isinstance(c, str) and re.fullmatch(r'\d{1,3}\.?\s?[a-z]?\.?', c.strip()):
                    tds.append(f'<td class="num"{dh}>{cell_html(re.sub(r"^(\d+\.)\s+([a-z])", r"\1\2", c.strip()))}</td>')
                else:
                    tds.append(f'<td{dh}>{cell_html(c)}</td>')
        out.append('<tr>' + ''.join(tds) + '</tr>')
    out.append('</table>')
    return ''.join(out)

def _short_title(c):
    """a group's title ("5 khandha", "Magga sacca"), not a note that runs across the table"""
    t = re.sub(r'[*_]|⟦[^|]*\|[^⟧]*⟧', '', c if isinstance(c, str) else str(c[0])).strip()
    return 0 < len(t) <= 32 and not t.endswith('.') and t.count(' ') <= 4 and not re.search(r'\b(is|are)\b', t)


def render_span_table(b, narrow=True):
    """A table whose rows may hold '<' (the cell to the left extends here) and '^' (the cell above
    extends here); 'hrows' are header rows. Cells may be [pāli, english]."""
    rows = [('h', r) for r in b.get('hrows', [])] + [('b', r) for r in b['rows']]
    ncol = max(len(r) for _, r in rows)
    grid = [list(r) + [''] * (ncol - len(r)) for _, r in rows]
    owner, span = {}, {}
    for i, r in enumerate(grid):
        for j, c in enumerate(r):
            if c == '<' and j > 0:
                owner[(i, j)] = owner[(i, j - 1)]
            elif c == '^' and i > 0:
                owner[(i, j)] = owner[(i - 1, j)]
            else:
                owner[(i, j)] = (i, j)
                span[(i, j)] = [1, 1]
    for (i, j), o in owner.items():
        if o != (i, j):
            span[o] = [max(span[o][0], i - o[0] + 1), max(span[o][1], j - o[1] + 1)]
    out = [TOGGLE_BTN if b.get('glossed') else '', '<table class="gt span' + (' glossed' if b.get('glossed') else '') + '">']
    for i, (kind, _) in enumerate(rows):
        tds = []
        for j in range(ncol):
            if owner[(i, j)] != (i, j):
                continue
            c = grid[i][j]
            if c in ('<', '^') and meta.get('rich_cells'):
                c = ''                 # a merge mark with nothing to merge with (a phone part cut from a wider table)
            rs, cs = span[(i, j)]
            attr = (f' rowspan="{rs}"' if rs > 1 else '') + (f' colspan="{cs}"' if cs > 1 else '')
            if kind == 'h':
                tds.append(f'<th{attr}>{cell_html(c) if meta.get("rich_cells") else italics(html.escape(c, quote=False))}</th>')
            elif j == 0 and b.get('labels'):
                tds.append(f'<td class="lbl"{attr}>{italics(html.escape(c, quote=False))}</td>')
            elif isinstance(c, list):
                tds.append(f'<td{attr}><span class="pf">{cell_html(c[0])}</span>'
                           + (f'<span class="gl">{italics(html.escape(c[1], quote=False))}</span>' if len(c) > 1 and c[1] else '') + '</td>')
            else:
                no = ' class="no"' if meta.get('rich_cells') and c.strip() == 'No' else ''
                if isinstance(c, str) and re.fullmatch(r'\d{1,3}\.?\s?[a-z]?\.?', c.strip()):
                    c = re.sub(r'^(\d+\.)\s+([a-z])', r'\1\2', c.strip())     # "01. a" -> "01.a", kept on one line
                    no = ' class="num"'
                tds.append(f'<td{attr}{no}>{cell_html(c)}</td>')
        rid = ''
        if kind == 'b' and b.get('row_ids'):       # Dhammajeewa: a dyad's row is its Mātikā anchor (#md14)
            bi = i - len(b.get('hrows', []))
            if bi < len(b['row_ids']) and b['row_ids'][bi]:
                rid = f' id="{b["row_ids"][bi]}" data-ref="Mātikā {b["row_ids"][bi][1:]}"'
        cls = 'hd' if kind == 'h' else ''
        if kind == 'b' and meta.get('join_tables'):
            r = grid[i]
            real = [c for c in r if c not in ('<', '^', '')]
            if 1 <= len(real) <= 2 and r.count('<') >= ncol - len(real) - 1 and ncol >= 3 and (
                    len(real) == 1 or re.fullmatch(r'\d{1,2}\.?', str(r[0]).strip())) and _short_title(real[-1]):
                cls = 'grp'                # a group's heading inside the table: "1 · 5 khandha"
        out.append(f'<tr{" class=" + chr(34) + cls + chr(34) if cls else ""}{rid}>' + ''.join(tds) + '</tr>')
    out.append('</table>')
    if any('<tr class="grp"' in x for x in out):
        out[1] = out[1].replace('<table class="gt span', '<table class="gt span grouped', 1)
    if narrow and meta.get('rich_cells') and ncol >= 3:        # Nhu Lien: on a phone every table of three or more columns is a stack of cards
        return '<div class="tsplit-w">' + ''.join(out) + '</div>' + stack_span_table(b)
    if narrow and ncol >= 5:
        alt = split_span_table(b) or stack_span_table(b)
        if alt and ncol > 12 and meta.get('rich_cells'):     # Nhu Lien's 23-column chart: cards at every width
            return alt.replace('class="tsplit-n"', 'class="tsplit-n tsplit-all"', 1)
        if alt:
            return '<div class="tsplit-w">' + ''.join(out) + '</div>' + alt
    return ''.join(out)


def split_span_table(b, maxcols=4):
    """A narrow-screen version of a wide merged-cell table: one table per column group of a header row
    (Singular / Plural, or the groups of the alphabet chart), each with the row labels repeated.
    Returns None when no header row divides the columns into groups of at most maxcols."""
    hrows = b.get('hrows', [])
    ncol = max(len(r) for r in hrows + [r for r in b['rows']])
    def groups(row):
        row = list(row) + [''] * (ncol - len(row))
        out, j = [], 1
        while j < ncol:
            k = j + 1
            while k < ncol and row[k] == '<':
                k += 1
            out.append((row[j], j, k))
            j = k
        return out
    for lvl, hr in enumerate(hrows):
        gs = groups(hr)
        if len(gs) > 1 and all(k - j <= maxcols for _, j, k in gs) and not any(t in ('<', '^') for t, _, _ in gs):
            break
    else:
        return None
    parts = []
    for title, j, k in gs:
        def cut(r):
            r = list(r) + [''] * (ncol - len(r))
            cells = [r[0]] + r[j:k]
            if len(cells) > 1 and cells[1] == '<':        # a cell spanning in from the previous group
                i = j
                while i > 0 and r[i] == '<':
                    i -= 1
                cells[1] = r[i]
            return cells
        sub_h = [cut(r) for r in hrows[lvl + 1:]]
        sub_b = [cut(r) for r in b['rows']]
        sub_b = [r for r in sub_b if any(c not in ('', '^', '<') for c in r[1:])] or sub_b
        if sub_b and sub_b[0][1:] and all(c == '^' for c in sub_b[0][1:]):
            continue
        sub = dict(b, hrows=sub_h, rows=sub_b)
        tname = cell_html(title) if meta.get('rich_cells') else italics(html.escape(title, quote=False))
        parts.append(f'<div class="tname">{tname}</div>' + render_span_table(sub, narrow=False))
    return '<div class="tsplit-n">' + ''.join(parts) + '</div>'


def stack_span_table(b):
    """The last resort for a wide table on a phone: one card per row, each filled cell under the name
    of its column (the lowest header cell above it)."""
    hrows = b.get('hrows', [])
    ncol = max(len(r) for r in hrows + [r for r in b['rows']])
    def owner_text(rows, i, j):
        while True:
            r = list(rows[i]) + [''] * (ncol - len(rows[i]))
            c = r[j]
            if c == '<' and j > 0:
                j -= 1
            elif c == '^' and i > 0:
                i -= 1
            else:
                return c
    heads = []
    for j in range(ncol):
        heads.append(owner_text(hrows, len(hrows) - 1, j) if hrows else '')
    cards = []
    for r in b['rows']:
        r = list(r) + [''] * (ncol - len(r))
        if meta.get('join_tables'):
            real = [c for c in r if c not in ('<', '^', '')]
            NUM = r'\d{1,3}\.?'
            if 1 <= len(real) <= 2 and ncol >= 3 and r.count('<') >= ncol - len(real) - 1 and (
                    len(real) == 1 or re.fullmatch(NUM, str(r[0]).strip())) and _short_title(real[-1]):
                # a group's heading inside the table: a band, as on a wide screen
                no_ = f'<span class="gn">{html.escape(str(r[0]).strip())}</span>' if len(real) == 2 else ''
                cards.append(f'<div class="sgrp">{no_}{cell_html(real[-1])}</div>')
                continue
            if (ncol >= 4 and all(isinstance(x, str) for x in r[:3]) and re.fullmatch(NUM, r[0].strip())
                    and re.fullmatch(NUM, r[1].strip()) and r[2] not in ('', '<', '^')):
                # two numbers (through the pada, within the group) and the name: "1 · 1  Rūpakkhandhā"
                items = []
                for j in range(3, ncol):
                    c = r[j]
                    if c in ('', '<', '^') or not isinstance(c, str):
                        continue
                    hh = cell_html(heads[j]) if heads[j] else ''
                    items.append(f'<li><span class="sh">{hh}</span>{cell_html(c)}</li>' if hh else f'<li class="full">{cell_html(c)}</li>')
                cards.append(f'<div class="scard"><div class="slab"><span class="gn2">{html.escape(r[0].strip())}</span>'
                             f'<span class="gn3">{html.escape(r[1].strip())}</span> {cell_html(r[2])}</div><ul>{"".join(items)}</ul></div>')
                continue
        items = []
        # a first column of bare numbers ("1", "01. a"): the card is named by the number and the next cell
        last_lab = locals().get('last_lab', '')
        two = (meta.get('rich_cells') and ncol > 3 and isinstance(r[0], str) and isinstance(r[1], str)
               and re.fullmatch(r'[\d. a-b]{0,8}', re.sub(r'\*', '', r[0])) and r[1] not in ('', '<', '^') and '[^' not in heads[1])
        for j in range(2 if two else 1, ncol):
            c = r[j]
            if c in ('', '<', '^'):
                continue
            val = (f'<span class="pf">{cell_html(c[0])}</span>' + (f' <span class="gl">{italics(html.escape(c[1], quote=False))}</span>' if len(c) > 1 and c[1] else '')
                   if isinstance(c, list) else cell_html(c))
            hh = cell_html(heads[j]) if meta.get('rich_cells') else italics(html.escape(heads[j], quote=False))
            no = ' class="no"' if meta.get('rich_cells') and isinstance(c, str) and c.strip() == 'No' else ''
            items.append(f'<li{no}><span class="sh">{hh}</span>{val}</li>')
        lab = r[0] if isinstance(r[0], str) else r[0][0]
        if meta.get('rich_cells'):
            if lab.strip() in ('^', '<'):
                lab = last_lab                   # a row under a merged cell keeps the name of the row above
            last_lab = lab
        if two:
            lab = (lab.strip() + ' ' if lab.strip() not in ('^', '<') else '') + r[1]
        lab = cell_html(lab) if meta.get('rich_cells') else italics(html.escape(lab, quote=False))
        cards.append(f'<div class="scard"><div class="slab">{lab}</div><ul>{"".join(items)}</ul></div>')
    return '<div class="tsplit-n">' + ''.join(cards) + '</div>'


def render_tables(b):
    out = ['<div class="tgroup">']
    for part in b['parts']:
        out.append('<div class="tpart">' + (f'<div class="tname">{html.escape(part["title"], quote=False)}</div>' if part.get('title') else '')
                   + render_table(dict(part, head=part.get('head'))) + '</div>')
    out.append('</div>')
    return ''.join(out)


def render_list(b):
    lis = []
    for mk, t in b['items']:
        h, grids = enrich(html.escape(t, quote=False), linkify)
        h = re.sub(r'\x00G(\d+)\x00', lambda m: grids[int(m.group(1))], h)
        h, extra = lead_label(h)
        h = italics(h)
        lis.append(f'<li><span class="mk">{html.escape(mk, quote=False)}</span><span class="lt">{h}</span></li>')
    ind = f' style="--ind:{b["ind"]}"' if b.get('ind') else ''
    return f'<ol class="lst"{ind}>{"".join(lis)}</ol>'


def render_block(b):
    CUR.clear()
    CUR.update(b)
    t = html.escape(b.get('text', ''), quote=False)
    pn = b.get('pnum')
    aid = b.get('id') or anchor_id(b)
    anchor = f' id="{aid}"' if aid else ''
    if aid and b.get('ref'):
        anchor += f' data-ref="{html.escape(b["ref"], quote=True)}"'
    if FOOTNOTES and b.get('note'):
        n = b['note']
        nid, rid = (f'n{n}', f'r{n}') if NOTES_GLOBAL else (f'{b["_cid"]}-n{n}', f'{b["_cid"]}-r{n}')
        body = html.escape(b['text'], quote=False)
        if INLINE:
            body = ' </p><p class="para fnote cont">'.join(rd_inline(x, escaped=True) for x in body.split(' ¶ '))
        else:
            body = italics(sec_links(enrich(body, linkify)[0]))
        dref = f' data-ref="note {n}"' if NOTES_GLOBAL else ''
        return (f'<p class="para fnote" id="{nid}"{dref}><a class="fnback" href="#{rid}" title="Back to the text">{n}</a> {body}</p>')
    if b['type'] == 'pg':        # Warder: where a printed page begins (#pg23), shown in the margin on wide screens
        return f'<span class="pgmark" id="pg{b["n"]}" data-ref="{page_ref(b["n"])}" title="Printed page {page_no(b["n"])}">{page_no(b["n"])}</span>'
    if b['type'] == 'idx':       # Warder: index entries; printed page numbers link to their page (#pg23)
        def pages(t):
            t = html.escape(t, quote=False)
            t = re.sub(r'(?<![\d–-])(\d{1,3})(?![\d])', lambda m: f'<a class="xref" href="#pg{m.group(1)}">{m.group(1)}</a>'
                       if 'pg' + m.group(1) in PAGE_IDS else m.group(1), t)
            return re.sub(r'\*([^*]+)\*', r'<i>\1</i>', t)      # italic page numbers (the principal reference)
        return ('<ul class="idx">' + ''.join(f'<li class="lv{lv}"><span class="it">{rd_inline(t) if INLINE else italics(html.escape(t, quote=False))}</span> '
                f'<span class="ip">{pages(pg)}</span></li>' for t, pg, lv in b['items']) + '</ul>')
    if b['type'] == 'kidx':      # Khine: his index, "Bewilderment (moha) … 365, 390", references to his paragraphs and to the Mātikā ("Du-106", "Ti-4")
        return ('<ul class="idx">' + ''.join(f'<li class="lv{2 if re.match(r"^(–|--?|,|\()", t) else 1}"><span class="it">{rd_inline(t)}</span> '
                f'<span class="ip">{matika_refs(index_refs(rd_inline(r)))}</span></li>' for t, r in b['items']) + '</ul>')
    if b['type'] == 'verbs':     # Warder: the Principal Parts of Verbs, one entry per root
        head = b['head']
        lis = []
        for r in b['rows']:
            parts = [f'<span class="vk">{html.escape(head[i], quote=False)}</span> {link_vocab(html.escape(c.replace(" // ", "; "), quote=False))}'
                     for i, c in enumerate(r) if i >= 2 and c and c not in ('<', '^') and i < len(head)]
            lis.append(f'<li><span class="vr">{html.escape(r[0], quote=False)}</span> <span class="vc">{html.escape(r[1] if len(r) > 1 else "", quote=False)}</span>'
                       f'<span class="vp">{" · ".join(parts)}</span></li>')
        return '<div class="tbl"><ul class="verbs">' + ''.join(lis) + '</ul></div>'
    if b['type'] == 'img':       # Warder: a printed chart kept as an image
        img = f'<img src="{html.escape(b["src"], quote=True)}" alt="{html.escape(b["alt"], quote=True)}" loading="lazy">'
        if b.get('full'):        # Nhu Lien: a chart too wide for the page, the image opens at full size
            img = f'<a href="{html.escape(b["src"], quote=True)}" title="Open the chart at full size">{img}</a>'
        return f'<figure class="fig">{img}</figure>'
    if b['type'] == 'ctr':       # Müller: a centred line (titles, end-titles of the sections)
        return f'<p class="para ctr">{italics(t)}</p>'
    if b['type'] == 'ednote':    # an editorial note of this library (not the author's)
        return (f'<p class="para ednote"{anchor}><span class="mtag">{b["tag"]}</span> '
                f'<span class="edlabel">Library note</span> {html.escape(b["text"], quote=False)}</p>')
    if b['type'] == 'idxl':      # Müller: index entries, "Hîna, 269, 1025."
        def ent(x):
            sub = x.startswith('\t')
            x = x.lstrip('\t')
            m = re.match(r'^(.*?)(,\s*(?:\d|[ivxlc]+[,f .]|[ivxlc]+$|\*see).*)?$', x) if INDEX_PAGES else re.match(r'^(.*?)(,\s*\d.*)?$', x)
            term, refs = m.group(1), m.group(2) or ''
            return (f'<li{" class=" + chr(34) + "lv2" + chr(34) if sub else ""}><span class="it">{italics(html.escape(term, quote=False))}</span>'
                    f'{(bold_lookup if INDEX_PAGES else italics)(index_refs(html.escape(refs, quote=False)))}</li>')
        return '<ul class="idx mi">' + ''.join(ent(x) for x in b['items']) + '</ul>'
    if b['type'] == 'brace':     # Rhys Davids: a brace diagram — items on the left, what they share on the right
        L = ''.join(f'<li>{rd_inline(x)}</li>' for x in b['left'])
        tags = ''.join(f'<span class="mtag" id="m{t}">{t}</span>' for t in b.get('tags', []))
        R = ''.join(f'<p>{rd_inline(x)}</p>' for x in b['right'])
        if b.get('tags') and len(b.get('rsents', [])) == len(b['tags']):     # the Mātikā: one item per line, each with its label
            tags = ''
            R = ''.join(f'<p class="mitem" id="m{t}" data-ref="Mātikā {t}"><span class="mtag">{t}</span>{rd_inline(x)}</p>'
                        for t, x in zip(b['tags'], b['rsents']))
        return f'<div class="brace">{tags}<ul class="bl">{L}</ul><div class="br">{R}</div></div>'
    if b['type'] == 'link':
        return f'<p class="para plink"><a href="{html.escape(b["href"], quote=True)}">{html.escape(b["text"], quote=False)}</a></p>'
    if b['type'] == 'h':
        txt = re.sub(r'^\d{1,3}[.,]?\s*', '', t) if pn is not None and not SEC_ANCHORS else t
        lvl = f' l{str(pn).count(".") + 1}' if SEC_ANCHORS and pn is not None else ''
        if INLINE:
            return f'<h3 class="sec"{anchor}>{pnum_span(b)}{rd_inline(b["text"])}</h3>'
        return f'<h3 class="sec{lvl}"{anchor}>{pnum_span(b)}{italics(txt) if ITALICS or PALI_TEXT else (txt.title() if txt.isupper() else txt)}</h3>'
    if b['type'] == 'h4':
        if INLINE:
            return f'<h4 class="sub"{anchor}>{rd_inline(b["text"])}</h4>'
        return f'<h4 class="sub">{t}</h4>'
    if b['type'] == 'tables':
        return f'<div class="tbl"{anchor}>{pnum_span(b)}{render_tables(b)}</div>'
    if b['type'] == 'list':
        return render_list(b)
    if b['type'] == 'cap':
        gl = f' <span class="gl">‘{italics(html.escape(b["gl"], quote=False))}’</span>' if b.get('gl') else ''
        return f'<p class="pcap">{italics(t)}{gl}</p>'
    if b['type'] == 'vocab':
        ind = f' style="--ind:{b["ind"]}"' if b.get('ind') else ''
        return f'<div class="tbl"{anchor}{ind}>{pnum_span(b)}{render_vocab(b)}</div>'
    if b['type'] == 'ex':
        return f'<div class="exwrap"{anchor}>{pnum_span(b)}{render_ex(b)}</div>'
    if b['type'] == 'lines':
        return f'<div class="tbl"{anchor}>{pnum_span(b)}{render_lines(b)}</div>'
    if b['type'] == 'h5':
        return f'<h5 class="grp"{anchor if INLINE else ""}>{rd_inline(b["text"]) if INLINE else t}</h5>'
    if b['type'] == 'table':
        if b.get('details'):     # Nhu Lien: the text of a chart shown as an image above it
            return (f'<details class="tdet"><summary>{html.escape(b["details"], quote=False)}</summary>'
                    f'<div class="tbl tscroll">{render_span_table(b, narrow=False)}</div></details>')
        cap = f'<p class="cap">{html.escape(b["cap"], quote=False)}</p>' if b.get('cap') and b.get('spans') else ''
        return f'<div class="tbl"{anchor}>{pnum_span(b)}{cap}{render_span_table(b) if b.get("spans") else render_table(b)}</div>'
    if b['type'] == 'pre':
        raw = b['text']
        if pn is not None and CID == 'ch':
            raw = re.sub(r'^\s*\d{1,3}[.,]?\s', lambda m: ' ' * len(m.group(0)), raw, count=1)
        if 'gutterals' in raw and 'palatals' in raw and 'labials' in raw:
            body = CONSONANT_CHART
        else:
            body = render_pre(raw, cell_html)
        return f'<div class="tbl"{anchor}>{pnum_span(b)}{body}</div>'
    # paragraph
    raw = b['text']
    if INLINE:                   # Rhys Davids, Khine: their own markup only
        h = rd_inline(raw)
        if b.get('mrange'):
            h = f'<span class="mrng">{html.escape(b["mrange"], quote=False)}.</span> ' + (f'{b["mnum"]}. ' if b.get('mnum') else '') + h
        if b.get('tag'):
            h = f'<span class="mtag">{b["tag"]}</span>' + h
        if b.get('bib'):
            h = f'<span class="blab">{html.escape(b["label"], quote=False)}</span> ' + h
        cls = ' '.join(['para'] + (['ctr'] if b.get('ctr') else []) + (['q'] if b.get('q') else []) + (['mitem'] if b.get('tag') else []) + ([f'ind{b["ind"]}'] if b.get('ind') else [])
                       + (['big'] if b.get('big') else []) + (['bib'] if b.get('bib') else []))
        if aid:
            return f'<p{anchor} class="numbered {cls}">{pnum_span(b)}{h}</p>'
        return f'<p class="{cls}">{h}</p>'
    if pn is not None and CID == 'ch':
        raw = re.sub(r'^\d{1,3}[.,]?\s*', '', raw)
    examples = bool(re.match(r'^(EXAMPLES?|Examples?)\b', raw)) if not ITALICS else raw.rstrip(':') in ('Examples', 'Example', 'Notes', 'Note')
    parts = []
    for piece in (split_enum(raw) if not (ITALICS or PALI_TEXT) else [raw]):
        h, grids = enrich(piece, linkify)
        h = gt_formulas(h)
        h, extra = lead_label(h) if pn is None else (h, [])      # a numbered paragraph's margin holds its number and chips
        if ITALICS and not examples:
            h = re.sub(r'^(Notes?):\s+', lambda m: f'<b class="lead">{m.group(1)}</b> ', h)
        if b.get('pali'):
            h = link_vocab(h)
        elif PALI_TEXT:
            h = sec_links(h)
        h = italics(h)
        if b.get('tag'):
            h = f'<span class="mtag">{b["tag"]}</span>' + h
        cls = ' '.join(['para'] + extra + (['examples'] if examples else []) + (['pali'] if b.get('pali') else [])
                       + (['q'] if b.get('q') else []) + (['mitem'] if b.get('tag') else [])
                       + ([f'ind{b["ind"]}'] if b.get('ind') else []) + (['right'] if b.get('align') == 'right' else []))
        for seg in re.split(r'(\x00G\d+\x00)', h):
            g = re.fullmatch(r'\x00G(\d+)\x00', seg)
            if g:
                parts.append(grids[int(g.group(1))])
            elif seg.strip(' ,.;'):
                parts.append(f'<p class="{cls}">{seg.strip()}</p>')
                cls = 'para cont'
    num = pnum_span(b)
    if len(parts) == 1 and parts[0].startswith('<p '):
        if aid:
            return parts[0].replace('<p class="', f'<p{anchor} class="numbered ', 1).replace('">', '">' + num, 1)
        return parts[0]
    return f'<div class="pgroup{" numbered" if aid else ""}"{anchor}>{num}{"".join(parts)}</div>'

SEEN_REFS = set()
def fn_refs(h, cid):
    """[^3] -> a superscript link to note 3 of the chapter (hover shows it, tap goes to it)."""
    def one(m):
        n = m.group(1)
        rid, nid = (f'r{n}', f'n{n}') if NOTES_GLOBAL else (f'{cid}-r{n}', f'{cid}-n{n}')
        idattr = '' if rid in SEEN_REFS else f' id="{rid}"'
        SEEN_REFS.add(rid)
        return f'<sup class="fnref"><a class="xref" href="#{nid}" data-s="{nid}"{idattr}>{n}</a></sup>'
    return re.sub(r'\[\^(\d+|[A-Z]{2}\d+|[ivx]{1,4})\]', one, h)

# merge adjacent pre blocks (only blank lines separated them)
def merged(blocks):
    out = []
    for b in blocks:
        if b['type'] == 'pre' and out and out[-1]['type'] == 'pre' and 'pnum' not in b:
            sep = '\n' if ('\n' not in out[-1]['text'].strip() and '\n' not in b['text'].strip()) else '\n\n'
            out[-1] = dict(out[-1], text=out[-1]['text'] + sep + b['text'])
        else:
            out.append(dict(b))
    return out

def sec_title(t):
    if meta.get('plain_corrections'):
        t = re.sub(r'⟦([^|⟧]*)\|[^⟧]*⟧', r'\1', t)
    if not meta.get('keep_sec_numbers'):
        t = re.sub(r"^\d+[.,]?\s*", "", t)
    if ITALICS:
        t = t.replace('*', '')
    if PALI_TEXT:
        t = re.sub(r'⟦([^|⟧]*)\|[^⟧]*⟧', r'\1', t).rstrip('.')
        if t.isupper():
            t = ' '.join(w.lower() if w in ('OF', 'AND', 'THE') and i else w.capitalize() for i, w in enumerate(t.split()))
        return t
    if INLINE:                   # Rhys Davids, Khine: no note numbers, marks or markup in the contents
        t = re.sub(r'\[\^\w+\]|⟨[^⟩]*⟩|\*|__', '', re.sub(r'\^\{([^}]*)\}', r'\1', re.sub(r'⟦([^|⟧]*)\|[^⟧]*⟧', r'\1', t))).strip()
    return t.title() if t.isupper() else t

NAV_SKIP = re.compile(r'BH[AÂ]ṆAV[AÂ]R|^Ime dhamm|^Namo tassa', re.I)

def end_title_secs(blocks):
    """Müller's text names its sections at their end ("Catasso paṭipadâ.", "Hetu-gocchakaṃ."):
    each such centred line becomes an entry of the part's contents that leads to the first
    numbered section (or mātikā item) after the previous one, with the range it closes.
    Of several centred lines in a row only the first makes an entry (the later ones close
    larger units, or are the bhāṇavāra marks)."""
    out, start, end, prev_ctr = [], None, None, False
    for b in blocks:
        if b['type'] == 'ctr' and NAV_SKIP.search(b['text']):
            continue
        if b['type'] == 'ctr':
            if not prev_ctr and start is not None and not NAV_SKIP.search(b['text']):
                rng = (f'§{start[1]}' + (f'–{end[1]}' if end[1] != start[1] else '')) if start[0] == 'p' else (
                    start[1] + (f'–{end[1]}' if end[1] != start[1] else ''))
                title = re.sub(r'⟦([^|⟧]*)\|[^⟧]*⟧', r'\1', b['text']).rstrip('.').replace('*', '')
                title = title.title() if title.isupper() else title
                out.append((start[2], f'{rng} {title}'))
            if start is not None:
                start = None
            prev_ctr = True
            continue
        prev_ctr = False
        if b.get('pnum') is not None:
            ref = ('p', str(b['pnum']), f'p{b["pnum"]}')
        elif b.get('tag'):
            ref = ('m', b['tag'], b['id'])
        else:
            continue
        if start is None:
            start = ref
        end = ref
    return out

SKIP_SECS = ('EXAMPLES', 'EXAMPLE', 'EXERCISE', 'EXERCISES')

meta_ch = []
for c in chapters:
    cid = CID + c['num']
    blocks = merged(c['blocks'])
    for b in blocks:
        b['_cid'] = cid
    nums = [b['pnum'] for b in blocks if 'pnum' in b] if CID == 'ch' else []
    rng = (f'§{num_label(nums[0])}–{num_label(nums[-1])}' if nums[0] != nums[-1] else f'§{num_label(nums[0])}') if nums else c.get('rng', '')
    label = c.get('label') or ('Front matter' if c['num'] == '0' else f'{UNIT} {c["num"]}')
    secs = [(f'{cid}-s{i}', (f'{b["pnum"]} ' if SEC_ANCHORS and b.get('pnum') else '') + sec_title(b['text']))
            + ((' l3',) if SEC_ANCHORS and str(b.get('pnum', '')).count('.') >= 2 else ())
            for i, b in enumerate(blocks)
            if b['type'] == 'h' and b['text'] not in SKIP_SECS and b['text'] != 'MUTES']
    if PALI_TEXT:
        secs += end_title_secs(blocks)
    title_nb = re.sub(r'(?<=\s)-(?=[a-zāīūṃṇṭḍḷṅñ])', '\u2011', c['title'])   # keep "-a" on one line
    meta_ch.append(dict(cid=cid, label=label, title=title_nb, rng=rng, secs=secs, blocks=blocks, num=c['num']))

chap_html = []
split_parts = []      # split books: (cid, label, title, chapter body) written as separate files
nav_html = []
home_cards = []
for k, m in enumerate(meta_ch):
    cid, label, rng, secs, blocks = m['cid'], m['label'], m['rng'], m['secs'], m['blocks']
    title = html.escape(m['title'], quote=False)
    sub = ''.join(f'<li{" class=" + chr(34) + x[2].strip() + chr(34) if len(x) > 2 else ""}><a href="#{x[0]}">{html.escape(x[1], quote=False)}</a></li>' for x in secs)
    nav_html.append(f'<li class="chap"><button class="chbtn" data-ch="{cid}" aria-expanded="false"><span class="chlabel">{label}</span><span class="chtitle">{title}</span><span class="chrng">{rng}</span></button><ul class="secs" hidden>{sub}</ul></li>')

    peek = ', '.join(html.escape(x[1], quote=False) for x in secs[:4]) + (' …' if len(secs) > 4 else '')
    cnum = 'i' if m['num'] == '0' else (m['num'] if m['num'].isdigit() or m['num'].isupper() else '§')
    home_cards.append(f'<a class="card" href="#{cid}"><span class="cnum">{cnum}</span>'
                      f'<span class="ctitle">{title}</span><span class="crng">{rng}</span>'
                      f'<span class="cpeek">{peek}</span></a>')

    inner = []
    for i, b in enumerate(blocks):
        if b['type'] == 'h' and b['text'] == 'MUTES':
            continue
        h = render_block(b)
        if b['type'] == 'h':
            h = h.replace('<h3 class="sec"', f'<h3 class="sec" data-sid="{cid}-s{i}"', 1)
            if ' id="' not in h.split('>')[0]:
                h = h.replace('<h3 class="sec"', f'<h3 class="sec" id="{cid}-s{i}"', 1)
            else:
                h = f'<span id="{cid}-s{i}" class="sanchor"></span>' + h
        if FOOTNOTES:
            h = fn_refs(h, cid)
        inner.append(h)

    intoc = ''
    if len(secs) > 1:
        intoc = (f'<details class="intoc"><summary>In this {UNIT.lower() if m["num"] != "0" else "part"} <span>{len(secs)} sections</span></summary>'
                 f'<ol>{sub}</ol></details>')
    prev_m = meta_ch[k - 1] if k > 0 else None
    next_m = meta_ch[k + 1] if k + 1 < len(meta_ch) else None
    def pg(mm, cls, arrow):
        if not mm:
            return f'<a class="pg {cls}" href="#home"><span class="pgdir">{arrow} Contents</span><span class="pgt">All {UNIT.lower()}s</span></a>'
        return (f'<a class="pg {cls}" href="#{mm["cid"]}" data-go="{mm["cid"]}"><span class="pgdir">{"← Previous" if cls == "prev" else "Next →"}</span>'
                f'<span class="pgt">{mm["label"]}: {html.escape(mm["title"], quote=False)}</span></a>')
    pager = f'<nav class="pager" aria-label="{UNIT} navigation">{pg(prev_m, "prev", "←")}{pg(next_m, "next", "→")}</nav>'
    crumb = f'<span class="crumbs"><a class="crumb" href="../">{html.escape(lib["title"], quote=False)}</a><a class="crumb" href="#home">Contents</a></span>'
    open_tag = f'<section class="chapter" id="{cid}" data-label="{label}" data-title="{title}"'
    body = (f'<header class="chhead">{crumb}<span class="eyebrow">{label} {rng}</span><h2>{title}</h2></header>'
            f'{intoc}{"".join(inner)}{pager}')
    if SPLIT:
        chap_html.append(f'{open_tag} data-src="c/{cid}.html"></section>')
        split_parts.append((cid, label, m['title'], body))
    else:
        chap_html.append(f'{open_tag}>{body}</section>')

# drawer: glossary entries, optionally grouped
gl = []
last_group = None
for g in glossary:
    if g.get('group') != last_group and g.get('group'):
        gl.append(f'<div class="ghead">{html.escape(g["group"], quote=False)}</div>')
    last_group = g.get('group')
    key = g.get('key') or vkey(g['term'])
    gram = f' data-g="{html.escape(g["gram"], quote=True)}"' if g.get('gram') else ''
    gl.append(f'<dt data-k="{key}"{gram}>{html.escape(g["term"], quote=False)}'
              + (f' <i>{html.escape(g["gram"], quote=False)}</i>' if g.get('gram') else '') + '</dt>'
              f'<dd>{(bold_lookup if INDEX_PAGES else italics)(index_refs(html.escape(g["def"], quote=False))) if PALI_TEXT or INDEX_PAGES else matika_refs(index_refs(rd_inline(g["def"]))) if meta.get("index_links") else html.escape(g["def"], quote=False)}</dd>')
gloss_html = ''.join(gl)

howto = ''.join(f'<div><b>{t}</b><span>{s}</span></div>' for t, s in meta['howto'])
nunits = len(valid) if CID == 'ch' else (len(SECS) if SEC_ANCHORS else len(chapters) - 1)
page = open(os.path.join(HERE, 'template.html'), encoding='utf-8').read()
subs = {
    'LIBRARY': html.escape(lib['title'], quote=False),
    'SLUG': slug, 'ANCHOR': meta.get('anchor', '^p\\d+$'), 'SIGN': SIGN, 'MSIGN': meta.get('margin_sign', SIGN), 'GOTO': meta.get('goto', 'p'), 'GOTO_ROMAN': '1' if meta.get('goto_roman') else '',
    'TITLE': meta['short'] + ' · ' + meta['author'], 'DESC': meta['desc'],
    'BRAND': meta['short'], 'BRAND_SUB': meta.get('brand_sub', meta['author'].split()[-1] + ' · ' + meta['edition']),
    'GOTO_LABEL': meta.get('goto_label', '§'), 'GOTO_MAX': str(meta.get('goto_max', max(valid) if valid else len(chapters))),
    'GOTO_ARIA': meta.get('goto_aria', 'Go to'),
    'GOTO_INPUT': 'type="text" inputmode="decimal" size="6"' if SEC_ANCHORS or meta.get('goto_text') else f'type="number" min="1" max="{meta.get("goto_max", max(valid) if valid else len(chapters))}"',
    'DRAWER_BTN': meta.get('drawer_btn', 'Glossary'), 'DRAWER_TITLE': meta.get('drawer_title', 'Glossary'),
    'DRAWER_HINT': meta.get('drawer_hint', ''),
    'TOPTOGGLE': '<button class="iconbtn gltoggle" id="topgl" type="button" aria-pressed="true" title="Hide or show every English meaning">Hide English</button>' if GLOBAL_TOGGLE else '',
    'TOC_FOOT': meta.get('toc_foot', '').replace('{{NPARA}}', str(nunits)),
    'EYEBROW': meta['edition'], 'H1': meta['title'], 'BY': meta['by'], 'NOTE': meta['note'],
    'HOWTO': howto, 'SOURCE': meta['source'],
    'NAV': ''.join(nav_html), 'HOME': ''.join(home_cards), 'CHAPTERS': ''.join(chap_html), 'GLOSSARY': gloss_html,
}
subs['SPLIT'] = ' data-split="1"' if SPLIT else ''
if SPLIT:
    subs['GLOSSARY'] = ''
for k, v in subs.items():
    page = page.replace('{{' + k + '}}', v)


def audit_titles(h):
    return re.sub(r'data-ct="(\d+)"', lambda m: 'title="' + AUDIT_TIPS[int(m.group(1))].replace('"', '&quot;') + '"', h)


page = audit_titles(page)
split_parts = [(a, b, c, audit_titles(d)) for a, b, c, d in split_parts]
os.makedirs(os.path.dirname(OUT), exist_ok=True)
if SPLIT:
    from split import write_split
    write_split(os.path.dirname(OUT), split_parts, gloss_html, meta.get('anchor', '^p\\d+$'), SIGN)
open(OUT, 'w', encoding='utf-8').write(page)
print('wrote', OUT, len(page), 'bytes')
