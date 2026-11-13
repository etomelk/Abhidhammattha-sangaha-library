"""Render map/index.html, the Saṅgaha map: every paragraph of the Abhidhammatthasaṅgaha (I.1 … IX.75),
with its opening words and the place of that paragraph in every book of the library that is keyed to it;
the books keyed by their own numbers (the Paramatthadīpanī, the Anudīpanī) are linked chapter by chapter."""
import html
import sys
import json
import os
import re

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
e = lambda s: html.escape(s, quote=False)
lib = json.load(open(os.path.join(ROOT, 'data', 'library.json'), encoding='utf-8'))
ROMAN = ['', 'I', 'II', 'III', 'IV', 'V', 'VI', 'VII', 'VIII', 'IX']
data = {b['slug']: json.load(open(os.path.join(ROOT, 'data', f'{b["slug"]}.json'), encoding='utf-8')) for b in lib['books']}
keyed = [b for b in lib['books'] if b.get('sangaha_keys') and b['slug'] != 'sangaha']
bychapter = [b for b in lib['books'] if not b.get('sangaha_keys')]


def plain(t, n=140):
    t = re.sub(r'⟨[^⟩]*⟩|\[\^\d+\]|\*\*', '', t)
    t = re.sub(r'\s+', ' ', t).strip()
    return t if len(t) <= n else t[:n].rsplit(' ', 1)[0] + ' …'


have = {b['slug']: {bl['pnum'] for c in data[b['slug']]['chapters'] for bl in c['blocks'] if bl.get('pnum')} for b in keyed}
# books with numbers of their own tied to the Saṅgaha's (Nārada: data/narada-key.json): Saṅgaha key -> (their key, label)
tied = []
for b in lib['books']:
    if b.get('pts_map') and b['pts_map'] not in ('sangaha-key.json', 'pd-key.json'):
        m = json.load(open(os.path.join(ROOT, 'data', b['pts_map']), encoding='utf-8'))
        lab = {bl['pnum']: bl.get('label', str(bl['pnum'])) for c in data[b['slug']]['chapters'] for bl in c['blocks'] if bl.get('pnum')}
        inv = {}
        for k, v in sorted(m.items(), key=lambda x: int(x[0])):
            inv.setdefault(v, (int(k), lab.get(int(k), k)))
        tied.append((b, inv))
bychapter = [b for b in bychapter if not any(b is t for t, _ in tied)]
sys.path.insert(0, HERE)
from build_charts import CHARTS
charts_of = {}
for g, title, slug, by, note in CHARTS:
    charts_of.setdefault(int(g), []).append((title, slug))
part_of = {b['slug']: {c.get('sangaha_ch'): c['num'] for c in data[b['slug']]['chapters'] if c.get('sangaha_ch')} for b in bychapter}
sections, chips = [], []
nplaces = 0
groups = {}
for c in data['sangaha']['chapters']:
    for bl in c['blocks']:
        if bl.get('pnum'):
            groups.setdefault(bl['pnum'] // 1000, []).append(bl)
CHTITLE = {c['sangaha_ch']: c['title'] for c in data['sangaha']['chapters'] if c.get('sangaha_ch') and c['label'].startswith('Chapter')}
for ch in sorted(groups):
    lis = []
    for bl in groups[ch]:
        k = bl['pnum']
        rows = [f'<li><span class="cb">Saṅgaha</span> <a href="../sangaha/#p{k}">§{bl["label"]}</a></li>']
        for b in keyed:
            if k in have[b['slug']]:
                rows.append(f'<li><span class="cb">{e(b["cite"])}</span> <a href="../{b["slug"]}/#p{k}">§{bl["label"]}</a></li>')
                nplaces += 1
        for b, inv in tied:
            if k in inv:
                ok, ol = inv[k]
                rows.append(f'<li><span class="cb">{e(b["cite"])}</span> <a href="../{b["slug"]}/#p{ok}">{e(ROMAN[ok // 1000])} {e(ol)}</a></li>')
                nplaces += 1
        lis.append(f'<li class="mi" id="s{ch}-{k % 1000}"><span class="mtag">{bl["label"]}</span><div class="mbody"><p class="mtext">{e(plain(bl["text"]))}</p>'
                   f'<ul class="cplaces">{"".join(rows)}</ul></div></li>')
    whole = ' · '.join(f'<a href="../{b["slug"]}/#ch{part_of[b["slug"]][ch]}">{e(b["cite"])}</a>' for b in bychapter if ch in part_of[b['slug']])
    gid = f'c{ch}'
    charts = ' · '.join(f'<a href="../charts/#{s}">{e(t)}</a>' for t, s in charts_of.get(ch, []))
    sections.append(f'<section class="mgroup" id="{gid}"><h2>{e(CHTITLE.get(ch, "Chapter " + ROMAN[ch]))} <span class="mrng">{ROMAN[ch]}.1–{groups[ch][-1]["label"]}</span></h2>'
                    + (f'<p class="mgloss">The whole chapter in {whole}.</p>' if whole else '')
                    + (f'<p class="mgloss">Charts: {charts}.</p>' if charts else '') + f'<ol class="mlist">{"".join(lis)}</ol></section>')
    chips.append(f'<a class="mchip" href="#{gid}">{ROMAN[ch]}</a>')
nitems = sum(len(v) for v in groups.values())

page = f'''<!doctype html>
<html lang="en" class="lib refpage">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover">
<title>Saṅgaha map · {e(lib["title"])}</title>
<meta name="description" content="Every paragraph of the Abhidhammatthasaṅgaha, with the same paragraph in each book of the library.">
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Gentium+Book+Plus:ital,wght@0,400;0,700;1,400;1,700&family=Figtree:wght@400;500;600;700&display=swap">
<link rel="stylesheet" href="../shared/reader.css">
<link rel="stylesheet" href="../shared/home.css">
</head>
<body>
<div class="topbar">
  <a class="iconbtn libbtn" href="../" title="{e(lib["title"])}"><svg width="16" height="16" viewBox="0 0 16 16" aria-hidden="true"><path d="M2 2.5h3v11H2zM6.5 2.5h3v11h-3zM11 3.2l2.9-.8 2.6 10.6-2.9.8z" fill="currentColor"/></svg><span>Library</span></a>
  <a class="brand" href="../">{e(lib["title"])}<small>Saṅgaha map</small></a>
  <nav class="topnav"><a href="../#books">Books</a><a href="./" aria-current="page">Map</a><a href="../charts/">Charts</a><a href="../references/">References</a></nav>
  <button class="iconbtn" id="themebtn" aria-label="Toggle theme" title="Toggle light / dark"><svg width="16" height="16" viewBox="0 0 16 16" aria-hidden="true"><circle cx="8" cy="8" r="6.5" fill="none" stroke="currentColor" stroke-width="1.5"/><path d="M8 1.5a6.5 6.5 0 0 1 0 13z" fill="currentColor"/></svg></button>
</div>
<main>
  <div class="col">
    <header class="hero small">
      <a class="crumb" href="../">{e(lib["title"])}</a>
      <p class="kicker">Between the books</p>
      <h1>The Saṅgaha map</h1>
      <p class="lede">The Abhidhammatthasaṅgaha numbers its paragraphs anew in each of its nine chapters, and the Vibhāvinī, as the Sixth Council edition prints it, numbers its comments by the paragraph they explain. Those numbers, written I.1 … IX.75, are the library’s common map: every paragraph of the Saṅgaha is listed here with its opening words and the same place in each book keyed to it. Nārada’s sections are tied to the paragraph whose Pāli they give, by comparing the Pāli (where the likeness is not clear, the section is left out). Ledi Sayadaw’s Paramatthadīpanī and Anudīpanī run numbers of their own, so they are linked chapter by chapter.</p>
      <ul class="stats"><li><b>{nitems}</b><span>paragraphs</span></li><li><b>{len(lib["books"])}</b><span>books mapped</span></li><li><b>{nplaces:,}</b><span>linked sections</span></li></ul>
    </header>
    <nav class="mchips" aria-label="Chapters">{"".join(chips)}</nav>
    {"".join(sections)}
    <footer class="source">
      <p class="note">The opening words are those of the Sixth Council text (VRI). In Chapter IV the edition has no paragraph 3; the numbers are kept as printed.</p>
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
}})();
</script>
</body>
</html>
'''
os.makedirs(os.path.join(ROOT, 'map'), exist_ok=True)
open(os.path.join(ROOT, 'map', 'index.html'), 'w', encoding='utf-8').write(page)
print('wrote map/index.html', len(page), 'bytes')
