#!/usr/bin/env python3
"""Render terms/index.html: the Pāli words of the library, one list for every book.

Each book's own index of Pāli words is read from its data (Müller's index of words, with
the sections where a word occurs; Rhys Davids' Index of Pali Words, with her pages) and the
entries are put together by the library's lookup key (build.vkey: lower case, ṁ = ṃ,
Müller's â î û = ā ī ū, hyphens ignored). A word whose two spellings differ only in the
ending of the stem form (upādānaṃ / upâdâna, doso / dosa) is one entry; nothing else is
merged. The links go to the place in each book, in that book's own numbering.

    python3 scripts/build_terms.py
"""
import html
import json
import os
import re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
e = lambda s: html.escape(s, quote=False)
lib = json.load(open(os.path.join(ROOT, 'data', 'library.json'), encoding='utf-8'))
FOLD = str.maketrans({'â': 'ā', 'î': 'ī', 'û': 'ū', 'ṁ': 'ṃ'})


def vkey(s):
    return re.sub(r'[^a-zāīūṃṅñṭḍṇḷ]', '', s.lower().translate(FOLD))


def stem(k):
    """upādānaṃ -> upādāna, doso -> dosa: the citation forms the two indexes use."""
    if k.endswith('aṃ'):
        return k[:-1]
    if k.endswith('o'):
        return k[:-1] + 'a'
    return k


# the Pāli alphabet, for sorting
ORDER = 'a ā i ī u ū e o ṃ k kh g gh ṅ c ch j jh ñ ṭ ṭh ḍ ḍh ṇ t th d dh n p ph b bh m y r l v s h ḷ'.split()
RANK = {x: i for i, x in enumerate(ORDER)}


def pali_sort(k):
    out, i = [], 0
    while i < len(k):
        two = k[i:i + 2]
        if two in RANK and len(two) == 2:
            out.append(RANK[two])
            i += 2
        else:
            out.append(RANK.get(k[i], 99))
            i += 1
    return out


def numbers(defn, href, label):
    """'44, 45, 324.' -> links; anything that is not a number (see …) is kept as text."""
    def one(m):
        n = m.group(0)
        return f'<a href="{href(n)}">{label(n)}</a>'
    t = e(defn.rstrip('.'))
    t = re.sub(r'\*([^*]+)\*', r'<i>\1</i>', t)
    return re.sub(r'(?<![\w])(\d{1,4}|[ivxlc]{1,7})(?![\w])', one, t)


def khine_refs(defn, slug):
    """'Bewilderment: 365, 390; Bewilderment, non-: 1, 16' -> the English in plain text, the
    paragraphs and the Mātikā items (Du-106 = the 106th duka, Ti-4 = the 4th tika) as links."""
    out = []
    for part in re.split(r';\s+(?=[^\d\s])', defn):
        eng, _, refs = part.rpartition(': ')
        def mat(m):
            kind, n = m.group(1), int(m.group(2))
            t = f't{n}' if kind == 'Ti' else (f'd{n}' if n <= 100 else f's{n - 100}')
            return f'<a href="../{slug}/#m{t}">{m.group(0)}</a>'
        r = e(refs)
        r = re.sub(r'(?<![\w-])(Du|Ti)-(\d{1,3})(?!\d)', mat, r)
        r = re.sub(r'(?<![\w>-])(?<!Du-)(?<!Ti-)(\d{1,4})(?![\w<])', lambda m: f'<a href="../{slug}/#p{m.group(1)}">§{m.group(1)}</a>', r)
        out.append(f'<i>{e(eng)}</i> {r}' if eng else r)
    return '; '.join(out)


entries = {}          # key -> dict(forms={slug: term}, refs={slug: html})
books = []
for b in lib['books']:
    d = json.load(open(os.path.join(ROOT, 'data', f'{b["slug"]}.json'), encoding='utf-8'))
    g = d.get('glossary', [])
    if not g:
        continue
    slug = b['slug']
    if b.get('index_pages'):           # Rhys Davids: printed pages
        href = lambda n, s=slug: f'../{s}/#pg{n}'
        label = lambda n: n
        what = 'pages'
    else:                              # Müller: sections
        href = lambda n, s=slug: f'../{s}/#p{n}'
        label = lambda n: '§' + n
        what = 'sections'
    if b.get('index_links'):           # Khine: his index turned round, "English: 1, 16; English: Du-106, 1313"
        what = 'paragraphs (Du-, Ti- = the dukas and tikas of his Mātikā)'
    books.append((slug, b.get('cite', b['author']), what, len(g)))
    for x in g:
        k = vkey(x['term'])
        if not k:
            continue
        ent = entries.setdefault(stem(k), dict(forms={}, refs={}))
        ent['forms'].setdefault(slug, x['term'])
        ref = khine_refs(x['def'], slug) if b.get('index_links') else numbers(x['def'], href, label)
        ent['refs'][slug] = (ent['refs'][slug] + '; ' + ref) if slug in ent['refs'] else ref

order = [s for s, *_ in books]
cite = {s: c for s, c, *_ in books}
rows = []
letters = []
last = None
both = 0
for k in sorted(entries, key=pali_sort):
    ent = entries[k]
    first = ent['forms'][next(s for s in order if s in ent['forms'])]
    head = vkey(first)[:2] if vkey(first)[:2] in RANK else vkey(first)[:1]
    if head != last:
        letters.append(head)
        rows.append(f'<li class="tl" id="l-{head}">{e(head)}</li>')
        last = head
    forms = []
    for s in order:
        f = ent['forms'].get(s)
        if f and f not in forms:
            forms.append(f)
    if len(ent['forms']) > 1:
        both += 1
    refs = ''.join(f'<span class="tb"><b>{e(cite[s])}</b> {ent["refs"][s]}</span>' for s in order if s in ent['refs'])
    rows.append(f'<li class="tw" data-n="{e(" ".join(vkey(f) for f in forms))}"><span class="tt">{" · ".join(e(f) for f in forms)}</span>{refs}</li>')

stats = ''.join(f'<li><b>{n:,}</b><span>words in {e(c)}</span></li>' for s, c, w, n in books)
legend = '; '.join(f'{e(c)}’s index gives the {w}' for s, c, w, n in books)
jump = ''.join(f'<a class="mchip" href="#l-{x}">{e(x)}</a>' for x in letters)

page = f'''<!doctype html>
<html lang="en" class="lib refpage">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover">
<title>Pāli terms · {e(lib["title"])}</title>
<meta name="description" content="The Pāli words indexed in the books of the Dhammasaṅgaṇī Library, in one list, with links to the sections and pages of each book.">
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Gentium+Book+Plus:ital,wght@0,400;0,700;1,400;1,700&family=Figtree:wght@400;500;600;700&display=swap">
<link rel="stylesheet" href="../shared/reader.css">
<link rel="stylesheet" href="../shared/home.css">
</head>
<body>
<div class="topbar">
  <a class="iconbtn libbtn" href="../" title="{e(lib["title"])}"><svg width="16" height="16" viewBox="0 0 16 16" aria-hidden="true"><path d="M2 2.5h3v11H2zM6.5 2.5h3v11h-3zM11 3.2l2.9-.8 2.6 10.6-2.9.8z" fill="currentColor"/></svg><span>Library</span></a>
  <a class="brand" href="../">{e(lib["title"])}<small>Pāli terms</small></a>
  <nav class="topnav"><a href="../#books">Books</a><a href="../matika/">Mātikā</a><a href="./" aria-current="page">Terms</a><a href="../references/">References</a></nav>
  <button class="iconbtn" id="themebtn" aria-label="Toggle theme" title="Toggle light / dark"><svg width="16" height="16" viewBox="0 0 16 16" aria-hidden="true"><circle cx="8" cy="8" r="6.5" fill="none" stroke="currentColor" stroke-width="1.5"/><path d="M8 1.5a6.5 6.5 0 0 1 0 13z" fill="currentColor"/></svg></button>
</div>
<main>
  <div class="col">
    <header class="hero small">
      <a class="crumb" href="../">{e(lib["title"])}</a>
      <p class="kicker">Between the books</p>
      <h1>Pāli terms</h1>
      <p class="lede">The Pāli words that the books of the library index, in one list in the order of the Pāli alphabet. Each book keeps its own spelling (Müller writes â î û and ṃ, Rhys Davids ā ī ū and ṃ, Khine ā ī ū and ṁ) and its own numbering: {legend}. The same word in more than one book is one entry; {both:,} words are indexed by more than one.</p>
      <ul class="stats"><li><b>{len(entries):,}</b><span>words</span></li>{stats}</ul>
    </header>
    <div class="tfilter"><input id="tq" type="search" placeholder="Filter: e.g. vedana, rupa, citta" aria-label="Filter the terms" autocomplete="off" spellcheck="false"><span id="tn"></span></div>
    <nav class="mchips tjump" aria-label="Letters">{jump}</nav>
    <ul class="terms">{"".join(rows)}</ul>
    <footer class="source">
      <p class="note">How the list is made: the entries of each book’s index are matched by spelling, with Müller’s â î û read as ā ī ū, ṁ as ṃ, hyphens and capitals ignored, and a final -aṃ or -o read as the stem in -a (Rhys Davids indexes <i>upādānaṃ</i>, <i>doso</i>, Müller <i>upâdâna</i>, <i>dosa</i>). Nothing else is merged, so a word the two indexes give in different forms appears twice. Müller lists the first sections where a word occurs and a few more, not every passage; Rhys Davids gives the pages where she discusses it. Khine’s index is English first (“Bewilderment (moha)”); here it is turned round to its Pāli, with his English in italics.</p>
    <p class="rightsline">Offered freely as <i>Dhamma-dāna</i>, for study. All rights in these works belong to their authors, translators and publishers; this library claims none and cannot grant permission to reproduce them. <a href="../#rights">A note on rights</a></p>
    </footer>
  </div>
</main>
<script>
(function(){{
  const root=document.documentElement;
  try{{const t=localStorage.getItem('pg-theme'); if(t) root.setAttribute('data-theme',t);}}catch(e){{}}
  document.getElementById('themebtn').addEventListener('click',()=>{{
    const dark = root.getAttribute('data-theme')==='dark' || (!root.getAttribute('data-theme') && matchMedia('(prefers-color-scheme: dark)').matches);
    const next = dark?'light':'dark'; root.setAttribute('data-theme',next); try{{localStorage.setItem('pg-theme',next);}}catch(e){{}}
  }});
  const MAP={{'ā':'a','ī':'i','ū':'u','ṃ':'m','ṁ':'m','ṅ':'n','ñ':'n','ṭ':'t','ḍ':'d','ṇ':'n','ḷ':'l','â':'a','î':'i','û':'u'}};
  const norm=s=>s.toLowerCase().replace(/[āīūṃṁṅñṭḍṇḷâîû]/g,c=>MAP[c]).replace(/[^a-z ]/g,'');
  const q=document.getElementById('tq'), n=document.getElementById('tn');
  const items=[...document.querySelectorAll('li.tw')].map(li=>[li,norm(li.dataset.n)]);
  const heads=[...document.querySelectorAll('li.tl')];
  let t=null;
  q.addEventListener('input',()=>{{ clearTimeout(t); t=setTimeout(()=>{{
    const v=norm(q.value).replace(/ /g,''); let k=0;
    items.forEach(([li,s])=>{{ const ok=!v||s.replace(/ /g,'').includes(v)||s.split(' ').some(w=>w.startsWith(v)); li.hidden=!ok; if(ok) k++; }});
    heads.forEach(h=>h.hidden=!!v);
    n.textContent=v?k+' found':'';
  }},120); }});
}})();
</script>
</body>
</html>
'''
os.makedirs(os.path.join(ROOT, 'terms'), exist_ok=True)
open(os.path.join(ROOT, 'terms', 'index.html'), 'w', encoding='utf-8').write(page)
print(f'wrote terms/index.html: {len(entries)} words, {both} in more than one book', len(page), 'bytes')
