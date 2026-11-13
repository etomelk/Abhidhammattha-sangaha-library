#!/usr/bin/env python3
"""Render charts/index.html: the library's charts, one card each, grouped by the chapter of the
Saṅgaha they belong to, from the PDFs in sources/charts/ (vector PDFs from Word, OpenOffice Calc
and PostScript; see CHARTS for who made each).

python3 scripts/build_charts.py

For each page of each chart:
- charts/svg/<slug>-<n>.svg — the page as vector SVG (pdftocairo), its viewBox cropped to what is
  printed on it, so it fills the viewer and stays sharp at any zoom (the text is drawn as outlines);
- charts/thumb/<slug>.png — the first page, small, for the card;
- the page's words (pdftotext -layout), kept under the chart as "Text of this chart" so that the
  chart can be searched in the browser and read by a screen reader;
- charts/pdf/<slug>.pdf — the original, to download or print.
The viewer (in the page) opens a chart full-screen: fit to the screen, zoom with the wheel, the
buttons, + and −, or two fingers; drag to move; ← → for the pages of a chart and between charts;
Esc to close. Each chart has its own address (#rupa_pali, #material_phenomena-3)."""
import html
import json
import os
import re
import shutil
import subprocess
import sys

from PIL import Image, ImageOps

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
SRC = os.path.join(ROOT, 'sources', 'charts')
OUT = os.path.join(ROOT, 'charts')
e = lambda s: html.escape(s, quote=False)
AGG = 'Aggañāṇī'
CBS = 'Aggañāṇī & CBS, Sagaing (© 2005)'

# (group, title, slug, by, note)
GROUPS = [
    ('0', 'The four ultimate realities', 'The subject of the Saṅgaha: conventional and ultimate reality, and the four paramatthas.'),
    ('1', 'Chapter I — Consciousness (citta)', 'The 89 and 121 types of consciousness.'),
    ('2', 'Chapter II — Mental factors (cetasika)', 'The 52 mental factors and their combination with the types of consciousness.'),
    ('3', 'Chapter III — Miscellaneous (pakiṇṇaka)', 'Consciousness classified by feeling, roots, functions, doors, objects and bases.'),
    ('4', 'Chapter IV — The cognitive process (vīthi)', 'The seventeen mind-moments of a process at the eye-door.'),
    ('5', 'Chapter V — Process-freed (vīthimutta)', 'The thirty-one realms of existence.'),
    ('6', 'Chapter VI — Matter (rūpa)', 'The twenty-eight kinds of matter.'),
    ('8', 'Chapter VIII — Conditionality (paccaya)', 'Dependent origination and the twenty-four conditions.'),
    ('9', 'Chapter IX — Meditation subjects (kammaṭṭhāna)', 'Calm and insight, and the stages of purification.'),
]
DHD = 'Bhikkhu Vietnam Dhammadhaja · Systematization'
# Bhikkhu Vietnam Dhammadhaja, Systematization of Abhidhammaṭṭha Saṅgaha (Na Uyana, 2025–26): its documents,
# (first page, last page) of sources/systematization.pdf. The book gives them no titles; these are the library's.
SYS = [
    ('3', 'The 89 cittas: type, root, feeling, function, door, object, base', 'sys_citta_pakinnaka', 2, 27),
    ('2', 'The 52 cetasikas: characteristic, function, manifestation, proximate cause', 'sys_cetasika_lakkhana', 28, 34),
    ('2', 'The 89 cittas and their cetasikas (sampayoga- and saṅgaha-naya)', 'sys_citta_cetasika', 35, 54),
    ('3', 'The cittas grouped by function', 'sys_kicca', 55, 55),
    ('1', 'The cittas by class (jāti) and plane', 'sys_jati', 56, 62),
    ('4', 'The kinds of cognitive process (vāra)', 'sys_vara', 63, 63),
    ('4', 'The five-door process at the eye-door', 'sys_cakkhudvara', 64, 64),
    ('4', 'The five-door process: conditions, registration and javana', 'sys_pancadvara', 65, 73),
    ('4', 'The mind-door processes that follow a five-door process', 'sys_tadanuvattika', 74, 74),
    ('4', 'Clear and unclear objects at the mind-door', 'sys_vibhuta', 75, 75),
    ('4', 'The mind-door process with limited javana', 'sys_parittajavana', 76, 76),
    ('4', 'Javana: its objects and its course', 'sys_javana', 77, 83),
    ('4', 'The mind-door process with absorption javana', 'sys_appana', 84, 84),
    ('4', 'Absorption processes: jhāna, path, fruition, direct knowledge, cessation', 'sys_appana_vithi', 85, 103),
    ('4', 'The processes compared', 'sys_vithi_compared', 104, 104),
    ('5', 'The 31 realms: life-span, persons, rebirth-, life-continuum and death-consciousness', 'sys_bhumi', 105, 117),
    ('5', 'The death-proximate process at the five doors', 'sys_maranasanna_pancadvara', 118, 119),
    ('5', 'Kamma: by function, order, time and place of ripening', 'sys_kamma', 120, 132),
    ('5', 'The death-proximate process at the mind-door', 'sys_maranasanna_manodvara', 133, 137),
    ('5', 'Persons: rebirth-, life-continuum and death-consciousness', 'sys_puggala', 138, 144),
    ('5', 'The 89 cittas by root, feeling, function, door and plane of rebirth', 'sys_citta_patisandhi', 145, 172),
    ('6', 'The 28 rūpas: characteristic, function, manifestation, proximate cause', 'sys_rupa_lakkhana', 173, 178),
    ('6', 'Matter: its classification and origin', 'sys_rupa_vibhaga', 179, 185),
    ('6', 'The 28 rūpas: grouping, origin, classification, groups and occurrence', 'sys_rupa_sangaha', 186, 208),
    ('8', 'Dependent origination and the 24 conditions', 'sys_paticcasamuppada', 209, 226),
    ('8', 'The conditions: conditioning and conditioned states', 'sys_paccaya', 227, 241),
    ('9', 'Meditation subjects: calm (samatha)', 'sys_samatha', 242, 247),
    ('9', 'Meditation subjects: insight (vipassanā) and the purifications', 'sys_vipassana', 248, 255),
]
CHARTS = [
    ('0', 'Reality according to Abhidhamma', 'reality', AGG, 'Conventional and ultimate reality; the four ultimate realities and how they are counted (89/121 cittas, 52 cetasikas, 28 rūpas, Nibbāna); the aggregates.'),
    ('0', 'Abhidhamma: the four ultimate realities at a glance', 'abhidhamma_hanh_thuong', 'Hanh Thuong (2015)', 'One tree of everything the Saṅgaha counts: the 89/121 cittas by plane and kind, the 52 cetasikas by group, the 28 rūpas, and Nibbāna, each in its coloured box.'),
    ('1', 'Consciousness 89 / 121', 'citta_89_121_coloured', AGG, 'The 89 (or 121) types of consciousness as coloured dots: unwholesome, rootless, beautiful; sense-sphere, fine-material, immaterial, supramundane.'),
    ('1', 'Citta 89 / 121 (Pāli)', 'citta_89_121', CBS, 'The same classification with the Pāli names of each group.'),
    ('2', 'The 52 mental factors (cetasika)', 'cetasika_en', AGG, 'The 52 cetasikas in their groups: universals, occasionals, unwholesome, beautiful; two pages.'),
    ('2', 'Consciousness and mental factors', 'citta_cetasika_en', AGG, 'Which mental factors arise with which types of consciousness, in colour, with totals.'),
    ('2', 'Chart on the combination of citta and cetasika', 'citta_cetasika', CBS, 'The same combination with the Pāli names, and the totals of each row and column.'),
    ('2', 'The aggregate of feeling (vedanākkhandha)', 'vedanakkhandha', AGG, 'The five kinds of feeling by characteristic, function, manifestation and proximate cause.'),
    ('3', 'Consciousness and feeling', 'citta_feeling', AGG, 'Vedanā-saṅgaha: the types of consciousness by the feeling that goes with them.'),
    ('3', 'Consciousness and roots', 'citta_roots', AGG, 'Hetu-saṅgaha: the six roots and the types of consciousness without, with one, two or three roots.'),
    ('3', 'Consciousness and its functions', 'citta_functions', AGG, 'Kicca-saṅgaha: the fourteen functions and the types of consciousness that perform them.'),
    ('3', 'Consciousness and doors', 'citta_doors', AGG, 'Dvāra-saṅgaha: the six doors and the types of consciousness that arise at each.'),
    ('3', 'Consciousness and objects', 'citta_objects', AGG, 'Ālambaṇa-saṅgaha: the six objects and the objects of each type of consciousness.'),
    ('3', 'Consciousness and bases', 'citta_bases', AGG, 'Vatthu-saṅgaha: the six physical bases and the types of consciousness that depend on each.'),
    ('4', 'A complete eye-door process', 'eye_door_process', 'Dr. Rewata Dhamma', 'The seventeen mind-moments of a process at the eye-door, from past bhavaṅga to registration.'),
    ('5', 'The 31 realms of existence', 'realms_of_existence', 'Dr. Rewata Dhamma', 'The planes from the hells to the formless realms, with the life-span in each.'),
    ('6', 'Rūpa', 'rupa_pali', f'{AGG} (updated 09-2008)', 'The 28 kinds of matter against their groupings, in Pāli.'),
    ('6', 'Material phenomena (rūpa): definitions and information', 'material_phenomena', f'{AGG} (2008)', 'Each of the 28 kinds of matter: translation, class, characteristic, function, manifestation, proximate cause, origin; six pages.'),
]


def run(*a):
    return subprocess.run(a, capture_output=True, text=True, check=True).stdout


def crop_box(pdf, page):
    """the printed area of a page, in PDF points, from a render at 72 dpi (1 px = 1 pt)"""
    tmp = os.path.join(OUT, '_tmp')
    run('pdftoppm', '-f', str(page), '-l', str(page), '-r', '72', '-gray', '-png', '-singlefile', pdf, tmp)
    im = Image.open(tmp + '.png')
    bb = ImageOps.invert(im.convert('L')).point(lambda v: 255 if v > 24 else 0).getbbox()
    os.remove(tmp + '.png')
    w, h = im.size
    if not bb:
        return 0, 0, w, h
    m = 10
    return max(0, bb[0] - m), max(0, bb[1] - m), min(w, bb[2] + m) - max(0, bb[0] - m), min(h, bb[3] + m) - max(0, bb[1] - m)


def svg_page(pdf, page, out):
    run('pdftocairo', '-svg', '-f', str(page), '-l', str(page), pdf, out)
    x, y, w, h = crop_box(pdf, page)
    s = open(out, encoding='utf-8').read()
    s = re.sub(r'<svg([^>]*?)\swidth="[^"]*"\s+height="[^"]*"\s+viewBox="[^"]*"',
               lambda m: f'<svg{m.group(1)} viewBox="{x} {y} {w} {h}" preserveAspectRatio="xMidYMid meet"', s, count=1)
    open(out, 'w', encoding='utf-8').write(s)
    return w, h


def main():
    for d in ('svg', 'thumb', 'pdf'):
        os.makedirs(os.path.join(OUT, d), exist_ok=True)
    cards = {g: [] for g, _, _ in GROUPS}
    data = []
    total_pages = 0
    for g, title, slug, by, note in CHARTS:
        pdf = os.path.join(SRC, f'{slug}.pdf')
        n = int(re.search(r'Pages:\s+(\d+)', run('pdfinfo', pdf)).group(1))
        shutil.copy(pdf, os.path.join(OUT, 'pdf', f'{slug}.pdf'))
        pages = []
        heavy = False
        for p in range(1, n + 1):
            out = os.path.join(OUT, 'svg', f'{slug}-{p}.svg')
            w, h = svg_page(pdf, p, out)
            if os.path.getsize(out) > 2_000_000:       # gradients and many shapes: drawn from the PDF instead
                heavy = True
                os.remove(out)
            text = run('pdftotext', '-layout', '-f', str(p), '-l', str(p), pdf, '-')
            text = '\n'.join(l.rstrip() for l in text.split('\n')).strip('\n')
            pages.append(dict(src=f'svg/{slug}-{p}.svg', w=w, h=h, text=text, clip=list(crop_box(pdf, p))))
        total_pages += n
        run('pdftoppm', '-f', '1', '-l', '1', '-r', '60', '-png', '-singlefile', pdf, os.path.join(OUT, 'thumb', slug))
        im = Image.open(os.path.join(OUT, 'thumb', f'{slug}.png'))
        x, y, w, h = crop_box(pdf, 1)
        k = 60 / 72
        im = im.crop((int(x * k), int(y * k), int((x + w) * k), int((y + h) * k)))
        im.thumbnail((420, 300))
        im.save(os.path.join(OUT, 'thumb', f'{slug}.png'), optimize=True)
        if heavy:
            data.append(dict(slug=slug, title=title, by=by, pdf=f'pdf/{slug}.pdf', pages=[dict(clip=p['clip'], w=p['w'], h=p['h']) for p in pages]))
        else:
            data.append(dict(slug=slug, title=title, by=by, pages=[dict(src=p['src'], w=p['w'], h=p['h']) for p in pages]))
        texts = ''.join(f'<details class="ctext"><summary>Text of this chart{f" — page {i}" if n > 1 else ""}</summary><pre>{e(p["text"])}</pre></details>'
                        for i, p in enumerate(pages, 1))
        cards[g].append(
            f'<article class="chart" id="{slug}"><a class="cthumb" href="#{slug}" data-open="{slug}" aria-label="Open {html.escape(title, quote=True)}">'
            f'<img src="thumb/{slug}.png" alt="" loading="lazy"><span class="czoom">Open ⤢</span></a>'
            f'<div class="cbody"><h3><a href="#{slug}" data-open="{slug}">{e(title)}</a></h3><p class="cby">{e(by)}'
            f'{f" · {n} pages" if n > 1 else ""}</p><p class="cnote">{e(note)}</p>'
            f'<p class="clinks"><a href="#{slug}" data-open="{slug}">View</a> · <a href="pdf/{slug}.pdf" download>PDF</a></p>{texts}</div></article>')
    import pymupdf
    os.makedirs(os.path.join(OUT, 'sys'), exist_ok=True)
    book = pymupdf.open(os.path.join(ROOT, 'sources', 'systematization.pdf'))
    nsys = 0
    for g, title, slug, a, b in SYS:
        part = pymupdf.open()
        part.insert_pdf(book, from_page=a - 1, to_page=b - 1)
        pdf = os.path.join(OUT, 'sys', f'{slug}.pdf')
        part.save(pdf, garbage=4, deflate=True)
        n = b - a + 1
        nsys += n
        pages = []
        for p in range(1, n + 1):
            x, y, w, h = crop_box(pdf, p)
            pages.append(dict(clip=[x, y, w, h], w=w, h=h))
        run('pdftoppm', '-f', '1', '-l', '1', '-r', '60', '-png', '-singlefile', pdf, os.path.join(OUT, 'thumb', slug))
        im = Image.open(os.path.join(OUT, 'thumb', f'{slug}.png'))
        x, y, w, h = pages[0]['clip']
        k = 60 / 72
        im = im.crop((int(x * k), int(y * k), int((x + w) * k), int((y + h) * k)))
        im.thumbnail((420, 300))
        im.save(os.path.join(OUT, 'thumb', f'{slug}.png'), optimize=True)
        text = run('pdftotext', '-layout', pdf, '-')
        text = re.sub(r'(?m)^.*Compiled by Bhikkhu.*$\n?', '', text)
        text = re.sub(r'\n{3,}', '\n\n', '\n'.join(l.rstrip() for l in text.split('\n'))).strip('\n')
        data.append(dict(slug=slug, title=title, by=DHD, pdf=f'sys/{slug}.pdf', pages=pages))
        cards[g].append(
            f'<article class="chart sys" id="{slug}"><a class="cthumb" href="#{slug}" data-open="{slug}" aria-label="Open {html.escape(title, quote=True)}">'
            f'<img src="thumb/{slug}.png" alt="" loading="lazy"><span class="czoom">Open ⤢</span></a>'
            f'<div class="cbody"><h3><a href="#{slug}" data-open="{slug}">{e(title)}</a></h3><p class="cby">{e(DHD)} · '
            f'{"pp. " + str(a) + "–" + str(b) if n > 1 else "p. " + str(a)}</p>'
            f'<p class="clinks"><a href="#{slug}" data-open="{slug}">View</a> · <a href="sys/{slug}.pdf" download>PDF</a></p>'
            f'<details class="ctext"><summary>Text of these tables</summary><pre>{e(text)}</pre></details></div></article>')
    total_pages += nsys
    sections, chips = [], []
    for g, name, blurb in GROUPS:
        if not cards[g]:
            continue
        sections.append(f'<section class="cgroup" id="g{g}"><h2>{e(name)}</h2><p class="mgloss">{e(blurb)}</p>'
                        f'<div class="charts">{"".join(cards[g])}</div></section>')
        chips.append(f'<a class="mchip" href="#g{g}">{e(name.split(" — ")[0])}</a>')
    lib = json.load(open(os.path.join(ROOT, 'data', 'library.json'), encoding='utf-8'))
    page = open(os.path.join(HERE, 'charts.html'), encoding='utf-8').read()
    for k, v in {'TITLE': e(lib['title']), 'SECTIONS': '\n'.join(sections), 'CHIPS': ''.join(chips),
                 'NCHARTS': str(len(CHARTS) + len(SYS)), 'NPAGES': str(total_pages),
                 'DATA': json.dumps(data, ensure_ascii=False)}.items():
        page = page.replace('{{' + k + '}}', v)
    open(os.path.join(OUT, 'index.html'), 'w', encoding='utf-8').write(page)
    print(f'wrote charts/index.html: {len(CHARTS)} charts and {len(SYS)} documents of the Systematization, {total_pages} pages', file=sys.stderr)


if __name__ == '__main__':
    main()
