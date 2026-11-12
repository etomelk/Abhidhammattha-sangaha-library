"""Study-friendly markup applied to the running text of the grammar.

- Formulas such as "a+a=ā" or "√lag+na=lagna=lagga" become chips that never
  break across lines: parts joined by "+", an arrow, and the result in bold.
- Three or more formulas in a row (only punctuation between them) become a
  grid, one row per sentence, e.g. the a-, i- and u-groups of §22.
- Roots (√gam) get their own style.
- Paragraphs beginning "(a)", "(ii)", "(3)" get a hanging label; inline
  enumerations "(1) … (2) …" are split into separate items.
- "Remarks." / "Exception." / "Note." lead-ins are set as labels.
"""
import html
import re

_TC = r"[^\s+=,;:()\[\]<>\x00]"          # token character
_TOK = rf"{_TC}*[^\s+=,;:()\[\]<>\x00.!?]"  # token, never ending in . ! ?
_SEG = rf"{_TOK}(?: {_TOK}(?=\s?[+=]))?"     # a step may be two words if more steps follow
FORMULA = re.compile(rf"(?<![^\s(\"“‘'—–-])({_TOK}(?:\s?[+=]\s?{_SEG})*\s?[+=]\s?{_TOK})")
ROOT = re.compile(r"√([^\s,.;:()=+<>\x00]+)")

ROMAN = ['i', 'ii', 'iii', 'iv', 'v', 'vi', 'vii', 'viii', 'ix', 'x', 'xi', 'xii', 'xiii', 'xiv', 'xv']
LEAD = re.compile(r"^(Remarks?|Exceptions?|Notes?|N\.B|Obs)\.?(?=\s|$)")
ITEM = re.compile(r"^\((?:[a-h]|[ivx]{1,5}|\d{1,2})\)(?=\s)")


def _is_formula(s):
    return '+' in s and '=' in s


def formula_html(s):
    """a+b=c -> a + b → c (result bold).  c=a+b (analysis) -> c = a + b (word bold)."""
    parts = re.split(r"\s?([+=])\s?", s)
    analysis = parts.index('=') < parts.index('+')
    out = []
    for k, p in enumerate(parts):
        if p == '+':
            out.append('<span class="op">+</span>')
        elif p == '=':
            out.append('<span class="op">=</span>' if analysis else '<span class="op to">→</span>')
        else:
            bold = (k == 0) if analysis else (k == len(parts) - 1)
            out.append(f'<span class="{"res" if bold else "pt"}">{p}</span>')
    return '<span class="eq">' + ''.join(out) + '</span>'


def formulas(escaped):
    """Mark formulas in already-escaped text. Runs of 3+ formulas separated only by
    punctuation are replaced by a placeholder \\x00Gn\\x00; returns (text, grids)."""
    ms = [m for m in FORMULA.finditer(escaped) if _is_formula(m.group(1))]
    if not ms:
        return escaped, []
    # group consecutive formulas separated only by punctuation / "and"
    runs, cur = [], [ms[0]]
    for a, b in zip(ms, ms[1:]):
        between = escaped[a.end():b.start()]
        if re.fullmatch(r"[\s,.;]*(?:and\s*)?", between):
            cur.append(b)
        else:
            runs.append(cur)
            cur = [b]
    runs.append(cur)

    out, pos, grids = [], 0, []
    for run in runs:
        if len(run) >= 3:
            out.append(escaped[pos:run[0].start()])
            rows, row = [], [run[0]]
            for a, b in zip(run, run[1:]):
                if '.' in escaped[a.end():b.start()]:
                    rows.append(row)
                    row = [b]
                else:
                    row.append(b)
            rows.append(row)
            g = ''.join('<div class="eqrow">' + ''.join(formula_html(m.group(1)) for m in r) + '</div>' for r in rows)
            out.append(f'\x00G{len(grids)}\x00')
            grids.append(f'<div class="eqgrid">{g}</div>')
            tail = escaped[run[-1].end():]
            pos = run[-1].end() + len(tail) - len(tail.lstrip(' ,.;'))
        else:
            for m in run:
                out.append(escaped[pos:m.start(1)])
                out.append(formula_html(m.group(1)))
                pos = m.end(1)
                # swallow sentence punctuation straight after a chip (it would wrap alone)
                tail = re.match(r"[.,;](?=\s|$)", escaped[pos:])
                if tail:
                    pos += 1
    out.append(escaped[pos:])
    return ''.join(out), grids


def roots(h):
    return ROOT.sub(lambda m: f'<span class="root">√{m.group(1)}</span>', h)


def lead_label(h):
    """Bold 'Remarks.' etc. and hang an '(a)' label at the start of a paragraph."""
    cls = []
    m = LEAD.match(h)
    if m:
        h = f'<b class="lead">{m.group(0)}</b>' + h[m.end():]
        cls.append('remark')
    m = ITEM.match(h)
    if m:
        h = f'<span class="ix">{m.group(0)}</span>' + h[m.end():].lstrip()
        cls.append('item')
    return h, cls


def _seq(kind):
    if kind == 'roman':
        return ROMAN
    if kind == 'num':
        return [str(i) for i in range(1, 30)]
    return list('abcdefgh')


def split_enum(text):
    """Split 'lead: (1) aaa (2) bbb' into [lead, '(1) aaa', '(2) bbb'] when the
    markers run in order and follow sentence punctuation (not '27 (i) a')."""
    for kind, pat in (('num', r'\d{1,2}'), ('roman', r'[ivx]{1,5}'), ('alpha', r'[a-h]')):
        marks = [m for m in re.finditer(rf"(?:(?<=^)|(?<=[:.;!?]\s)|(?<=[:.;]))\s*\(({pat})\)\s", text)]
        seq = _seq(kind)
        chosen, want = [], 0
        for m in marks:
            if want < len(seq) and m.group(1) == seq[want]:
                chosen.append(m)
                want += 1
        if len(chosen) >= 2 and chosen[0].start() > 0:
            pieces = [text[:chosen[0].start()].strip()]
            for a, b in zip(chosen, chosen[1:] + [None]):
                pieces.append(text[a.start():b.start() if b else len(text)].strip())
            return pieces
    return [text]


def enrich(text, linkify):
    """raw text -> (html, grids). Escape, mark formulas, link references, style roots."""
    h, grids = formulas(html.escape(text, quote=False))
    h = roots(linkify(h))
    return h, grids
