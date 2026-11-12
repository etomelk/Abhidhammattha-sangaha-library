#!/usr/bin/env python3
"""Render the library home page (index.html) and the references page (references/index.html)
from data/library.json and data/references.json."""
import json, html, os, re
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
lib = json.load(open(os.path.join(ROOT, 'data', 'library.json'), encoding='utf-8'))
refs = json.load(open(os.path.join(ROOT, 'data', 'references.json'), encoding='utf-8'))
e = lambda s: html.escape(s, quote=False)

# ---- books, on shelves: the text, then its commentaries (the translations to come)
SHELVES = [
    ('The Saṅgaha in Pāli', 'Ācariya Anuruddha’s text in the Sixth Council edition, whose paragraph numbers are the map of the library.', ('sangaha',)),
    ('The commentaries', 'Sumaṅgala’s Vibhāvinī, keyed to the Saṅgaha paragraph by paragraph, and Ledi Sayadaw’s Paramatthadīpanī with his Anudīpanī on it.', ('vibhavini', 'paramattha', 'anudipani')),
]
_shelf = {s: k for k, (_, _, ss) in enumerate(SHELVES) for s in ss}
assert set(_shelf) == {b['slug'] for b in lib['books']}, 'every book needs a shelf'
lib['books'].sort(key=lambda b: (_shelf[b['slug']], SHELVES[_shelf[b['slug']]][2].index(b['slug'])))
cards = []
nunits = nanchors = nentries = 0
for i, b in enumerate(lib['books'], 1):
    book = json.load(open(os.path.join(ROOT, 'data', f'{b["slug"]}.json'), encoding='utf-8'))
    chapters = [c for c in book['chapters'] if c['num'] != '0' and re.fullmatch(r'[\dIVXL]+', c['num'])]
    if any(c.get('sangaha_ch') for c in book['chapters']):      # the nine chapters of the Saṅgaha, not the opening and closing
        chapters = [c for c in book['chapters'] if c['label'].startswith('Chapter')]
    nunits += len(chapters)
    nanchors += sum(blk.get('pend', blk['pnum']) - blk['pnum'] + 1 for c in book['chapters'] for blk in c['blocks'] if blk.get('pnum') is not None)
    nentries += len(book.get('glossary', []))
    nsec = sum(1 for c in book['chapters'] for blk in c['blocks'] if blk.get('pnum') is not None)
    units = f'§{min(blk["pnum"] for c in book["chapters"] for blk in c["blocks"] if blk.get("pnum") is not None)}–{max(blk["pnum"] for c in book["chapters"] for blk in c["blocks"] if blk.get("pnum") is not None)}' if nsec and not b.get('sangaha_keys') else f'{len(chapters)} {b.get("unit", "Chapter").lower()}s'
    k = _shelf[b['slug']]
    if i == 1 or _shelf[lib['books'][i - 2]['slug']] != k:
        if i > 1:
            cards.append('      </div></div>')
        cards.append(f'      <div class="shelfgroup"><div class="shelfhead"><h3><span>{k + 1}</span>{e(SHELVES[k][0])}</h3><p>{e(SHELVES[k][1])}</p></div><div class="books">')
    cards.append(
        f'      <a class="book" href="{b["slug"]}/" data-slug="{b["slug"]}" style="--hue:{(i * 67) % 360}">'
        f'<span class="spine"><span class="bnum">{i}</span></span>'
        f'<span class="bbody">'
        f'<span class="btop"><span class="lvl">{e(b.get("level", ""))}</span><span class="bunits">{units}</span></span>'
        f'<span class="btitle">{e(b["title"])}</span><span class="bby">{e(b["by"])}</span>'
        f'<span class="bblurb">{e(b["blurb"])}</span>'
        f'<span class="bfoot"><span class="bed">{e(b["edition"])}</span><span class="bopen">Open →</span>'
        f'<span class="bresume" hidden></span></span></span></a>')

cards.append('      </div></div>')

# ---- references
by_area = {}
for r in refs['refs']:
    by_area.setdefault(r['area'], []).append(r)
chips = [f'<button type="button" data-area="all" aria-pressed="true">All <span>{len(refs["refs"])}</span></button>']
groups = []
for a in refs['areas']:
    rs = sorted(by_area.get(a['id'], []), key=lambda r: (r['authors'].lower().strip('“'), r['year']))
    chips.append(f'<button type="button" data-area="{a["id"]}" aria-pressed="false">{e(a["name"])} <span>{len(rs)}</span></button>')
    items = []
    for r in rs:
        where = f'<span class="rwhere">{e(r["where"])}</span>' if r['where'] else ''
        links = []
        if r.get('lib'):
            links.append(f'<a class="rlink lib" href="../{r["lib"]}">Read here</a>')
        for u, kind in ((r['url'], 'PDF' if r['url'].lower().endswith('.pdf') else 'Open'), (r.get('found', ''), r.get('label') or 'Open')):
            if u:
                host = re.sub(r'^www\.', '', re.sub(r'^https?://', '', u).split('/')[0])
                links.append(f'<a class="rlink" href="{e(u)}" target="_blank" rel="noopener">{kind} ↗ <span>{e(host)}</span></a>')
        link = ''.join(links) or '<span class="rlink none">Print</span>'
        added = ' <span class="radd" title="Not in the source list; added for this library">added</span>' if r.get('added') else ''
        items.append(f'<li class="ref"><span class="rmain"><span class="rauth">{e(r["authors"])}</span> <span class="ryear">({e(r["year"])})</span> '
                     f'<span class="rtitle">{e(r["title"])}</span>{added}{where}</span>{link}</li>')
    groups.append(f'<div class="refgroup" data-area="{a["id"]}" id="{a["id"]}"><h3>{e(a["name"])}<span>{len(rs)}</span></h3>'
                  f'<p class="rblurb">{e(a["blurb"])}</p><ol class="reflist">{"".join(items)}</ol></div>')

n = len(lib['books'])
stats = ''.join(f'<li><b>{v:,}</b><span>{k}</span></li>' for v, k in [
    (n, 'books' if n != 1 else 'book'), (nanchors, 'numbered sections'), (nentries, 'index entries')] if v)
nlinked = sum(1 for r in refs['refs'] if r['url'] or r.get('found') or r.get('lib'))
nlib = sum(1 for r in refs['refs'] if r.get('lib'))
nadded = sum(1 for r in refs['refs'] if r.get('added'))
WORDS = 'No One Two Three Four Five Six Seven Eight Nine Ten'.split()
subs = {'TITLE': e(lib['title']), 'TAGLINE': e(lib['tagline']), 'BOOKS': '\n'.join(cards),
        'NBOOKS': f'{n} book{"s" if n != 1 else ""}', 'STATS': stats, 'CHIPS': ''.join(chips),
        'REFS': '\n'.join(groups), 'NREFS': str(len(refs['refs'])), 'NAREAS': str(len(refs['areas'])), 'NLINKED': str(nlinked),
        'NLIB': WORDS[nlib] if nlib < len(WORDS) else str(nlib), 'ADDEDNOTE': (f' {len(refs["refs"]) - nadded} works come from the source list; the {nadded} marked <span class="radd">added</span> are standard works found and checked for this library.' if nadded else '')}
for tpl, out in (('home.html', os.path.join(ROOT, 'index.html')), ('references.html', os.path.join(ROOT, 'references', 'index.html'))):
    page = open(os.path.join(HERE, tpl), encoding='utf-8').read()
    for k, v in subs.items():
        page = page.replace('{{' + k + '}}', v)
    os.makedirs(os.path.dirname(out), exist_ok=True)
    open(out, 'w', encoding='utf-8').write(page)
    print('wrote', out, len(page), 'bytes')
