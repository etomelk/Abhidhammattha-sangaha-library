"""Build data/<slug>.json for the Pāli books of the library from the VRI (Chaṭṭha Saṅgāyana) files
in sources/ (github.com/VipassanaTech/tipitaka-xml, romn/):

python3 scripts/pali/convert.py sangaha       # Abhidhammatthasaṅgaha      (abh07t.nrf.xml, first book)
python3 scripts/pali/convert.py vibhavini     # Abhidhammatthavibhāvinī    (abh07t.nrf.xml, second book)
python3 scripts/pali/convert.py paramattha    # Paramatthadīpanī           (e0301n.nrf.xml)
python3 scripts/pali/convert.py anudipani     # Anudīpanī                  (e0401n.nrf.xml)

The common map of the library is the Saṅgaha's own numbering: VRI numbers the paragraphs of the
Saṅgaha from 1 in each chapter (pariccheda), and numbers the Vibhāvinī by the paragraph of the
Saṅgaha it explains. A paragraph's key is chapter × 1000 + number (pnum 1011 = I.11), shown as
"I.11", anchored #p1011 and #p1-11 (the § box takes "1.11"). The Paramatthadīpanī runs one
numbering 1–174 through the book and the Anudīpanī explains it by the same numbers, so those two
are keyed by that number (pnum = n), and tied to the Saṅgaha by chapter.

One part per chapter; the opening (ganthārambha) and the closing (nigamana) are parts of their own.
Bold is kept, verses are indented lines, the variant readings (<note>) are footnotes numbered by
part, the pages of the Myanmar edition (pb ed="M") are page anchors #pg<n>."""
import html
import json
import os
import re
import sys

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..')
ROMAN = ['', 'I', 'II', 'III', 'IV', 'V', 'VI', 'VII', 'VIII', 'IX']
CHAPTERS = ['', 'Citta', 'Cetasika', 'Pakiṇṇaka', 'Vīthi', 'Vīthimutta', 'Rūpa', 'Samuccaya', 'Paccaya', 'Kammaṭṭhāna']
ENGLISH = ['', 'Consciousness', 'Mental factors', 'Miscellaneous', 'The cognitive process', 'Process-freed consciousness',
           'Matter', 'Categories', 'Conditionality', 'Meditation subjects']


def text_of(inner, notes):
    def note(m):
        v = html.unescape(re.sub(r'<[^>]+>', '', m.group(1))).strip()
        if notes is None:
            return f'({v})'
        notes.append(v)
        return '[^%d]' % len(notes)
    t = re.sub(r'<hi rend="paranum">\d+</hi><hi rend="dot">\.</hi>\s*', '', inner)
    t = re.sub(r'<note>(.*?)</note>', note, t)
    t = re.sub(r'<pb ed="M" n="\d+\.0*(\d+)"\s*/>', r'⟨pg:\1⟩', t)
    t = re.sub(r'<hi rend="bold">(.*?)</hi>', r'**\1**', t)
    t = re.sub(r'<[^>]+>', '', t)
    t = re.sub(r'\*\*\s*\*\*', ' ', t)
    return re.sub(r'\s+', ' ', html.unescape(t)).strip()


def read(name):
    raw = open(os.path.join(ROOT, 'sources', name), 'rb').read()
    try:
        x = raw.decode('utf-16')
    except UnicodeDecodeError:
        x = raw.decode('utf-8')
    return x[x.index('<body'):]


def paras(body):
    return [(m.group(1), m.group(2), m.group(3)) for m in re.finditer(r'<p rend="(\w+)"(?: n="(\d+)")?>(.*?)</p>', body, flags=re.S)]


def chapter_of(title):
    """the Saṅgaha chapter (1–9) a chapter heading of a commentary names"""
    m = re.match(r'(\d)\.', title)
    if m:
        return int(m.group(1))
    t = title.replace(' ', '').lower()
    for k in range(9, 0, -1):          # Vīthimutta before Vīthi
        if t.startswith(CHAPTERS[k].lower()):
            return k
    return None


def lis(seq):
    """indices of a longest strictly increasing subsequence of seq"""
    import bisect
    tails, tidx, prev = [], [], [None] * len(seq)
    for i, v in enumerate(seq):
        j = bisect.bisect_left(tails, v)
        if j == len(tails):
            tails.append(v); tidx.append(i)
        else:
            tails[j] = v; tidx[j] = i
        prev[i] = tidx[j - 1] if j else None
    out, i = [], tidx[-1] if tidx else None
    while i is not None:
        out.append(i); i = prev[i]
    return set(out)


def accepted(ps, keyed):
    """The paragraph numbers that make the map: the longest run of numbers that goes up through the
    book. VRI's files have a few slips (a number repeated, 169 for 159, 197 for 157, "14. 147");
    those stay in the text as printed, unnumbered, and are listed by this script."""
    ch, cand = 1, []
    for i, (rend, n, inner) in enumerate(ps):
        if rend == 'chapter':
            k = chapter_of(text_of(inner, None))
            if k:
                ch = k
        elif n and rend not in ('title', 'subhead', 'subsubhead'):
            cand.append((i, ch * 1000 + int(n) if keyed == 'chapter' else int(n)))
    keep = lis([k for _, k in cand])
    prev = 0                     # a jump far ahead (Anudīpanī "262" for 172) is a slip too
    for j in sorted(keep):
        k = cand[j][1]
        if keyed == 'running' and k - prev > 25:
            keep.discard(j)
        else:
            prev = k
    return {cand[j][0] for j in keep}, [(cand[j][1]) for j in range(len(cand)) if j not in keep]


def convert(ps, keyed):
    """keyed: 'chapter' (pnum = chapter × 1000 + n) or 'running' (pnum = n)"""
    ok, dropped = accepted(ps, keyed)
    if dropped:
        print('numbers left in the text as printed (out of order or repeated):', dropped, file=sys.stderr)
    parts = []
    seen = set()
    state = dict(ch=1, last=0)

    def new_part(label, title, ch):
        parts.append(dict(label=label, title=title, ch=ch, blocks=[], notes=[]))

    new_part('Ganthārambha', 'The opening', 1)
    heads = []
    for i, (rend, n, inner) in enumerate(ps):
        if rend in ('book', 'nikaya'):
            continue
        if rend == 'chapter':
            t = text_of(inner, None)
            k = chapter_of(t)
            if k:
                state['ch'] = k
                if keyed == 'chapter':
                    state['last'] = 0
                new_part(f'Chapter {ROMAN[k]}', f'{re.sub(r"^\\d+\\.\\s*", "", t)} — {ENGLISH[k]}', k)
            elif re.search(r'nigama', t, re.I):
                new_part('Nigamana', t, None)
            parts[-1]['blocks'].append(dict(type='h', text=t))
            continue
        if rend in ('title', 'subhead', 'subsubhead'):
            t = text_of(inner, None)
            if re.match(r'nigamana', t, re.I) and parts[-1]['label'] != 'Nigamana':
                new_part('Nigamana', 'The closing', None)
            parts[-1]['blocks'].append(dict(type='h' if rend != 'subsubhead' else 'h4', text=t))
            continue
        part = parts[-1]
        notes = part['notes']
        before = len(notes)
        t = text_of(inner, notes)
        b = None
        if n and part['label'] != 'Nigamana':
            k = int(n)
            key = state['ch'] * 1000 + k if keyed == 'chapter' else k
            if i in ok and key not in seen:
                seen.add(key)
                state['last'] = k
                if keyed == 'chapter':
                    b = dict(type='p', pnum=key, label=f'{ROMAN[state["ch"]]}.{k}', alias=[f'p{state["ch"]}-{k}'], text=t)
                else:
                    b = dict(type='p', pnum=key, text=t)
                if rend.startswith('gatha'):
                    b['ind'] = 2
        if b is None:
            if n:                                # a number outside the map (the closing verses): kept in the text
                t = f'{n}. {t}'
            if rend == 'centre':
                b = dict(type='p', text=t, ctr=True)
            elif rend.startswith('gatha'):
                b = dict(type='p', text=t, ind=2)
            elif rend == 'indent':
                b = dict(type='p', text=t, ind=1)
            else:
                b = dict(type='p', text=t)
        part['blocks'].append(b)
        for j in range(before + 1, len(notes) + 1):
            part['blocks'].append(dict(type='p', note=j, text=notes[j - 1]))
    parts = [p for p in parts if any(b['type'] == 'p' for b in p['blocks'])]
    return parts


def main(slug):
    if slug in ('sangaha', 'vibhavini'):
        body = read('abh07t.nrf.xml')
        cut = body.index('Abhidhammatthavibhāvinīṭīkā')
        cut = body.rfind('<p ', 0, cut)
        # the 'Namo tassa' that heads the Vibhāvinī belongs to it
        namo = body.rfind('<p rend="centre"', 0, cut)
        if 'Namo tassa' in body[namo:cut]:
            cut = namo
        ps = paras(body[:cut] if slug == 'sangaha' else body[cut:])
        parts = convert(ps, 'chapter')
    else:
        ps = paras(read('e0301n.nrf.xml' if slug == 'paramattha' else 'e0401n.nrf.xml'))
        parts = convert(ps, 'running')
    chapters = []
    for i, p in enumerate(parts):
        chapters.append(dict(num=str(i), label=p['label'], title=p['title'], blocks=p['blocks'],
                             **({'sangaha_ch': p['ch']} if p['ch'] else {})))
    out = os.path.join(ROOT, 'data', f'{slug}.json')
    json.dump(dict(chapters=chapters, glossary=[]), open(out, 'w', encoding='utf-8'), ensure_ascii=False, indent=0)
    ps_ = [b['pnum'] for c in chapters for b in c['blocks'] if b.get('pnum')]
    print(f'wrote {out}: {len(chapters)} parts, {len(ps_)} numbered paragraphs, '
          f'{sum(1 for c in chapters for b in c["blocks"] if b.get("note"))} variant notes', file=sys.stderr)
    for c in chapters:
        nums = [b['pnum'] for b in c['blocks'] if b.get('pnum')]
        print(f'  {c["num"]:>2} {c["label"]:14} {c["title"][:50]:50} {len(nums):4} {nums[:1]}…{nums[-1:]}', file=sys.stderr)


if __name__ == '__main__':
    main(sys.argv[1])
