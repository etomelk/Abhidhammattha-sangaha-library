# Abhidhammattha-saṅgaha Library

Study editions of the Abhidhammatthasaṅgaha of Ācariya Anuruddha, the manual through which
the Abhidhamma is learned in the Theravāda world: its Pāli text, its commentaries and its
English translations, as a static website. There is a home page that lists the books, one reader
per book (all sharing the same template, stylesheet and script), a map of the Saṅgaha's paragraphs
that ties the books together, and a reference list.

This library is built like the Dhammasaṅgaṇī Library (etomelk/dhammasangani-library): the reader,
the build scripts and the checks were copied from it and adapted, not linked, and nothing here
changes that site.

**Status: in progress** (November 2026). The Pāli shelf is done (the Saṅgaha and three
commentaries), and Nārada's Manual (Chapter VIII transcribed from the 1956–57 edition), and Mehm Tin Mon's *Ultimate
Science*. and *Fundamental Abhidhamma* Part I, and N. K. G. Mendis's *The Abhidhamma in Practice* (proofread
from the scan). Part II of *Fundamental Abhidhamma* needs OCR and waits.

## The books

| Shelf | Folder | Book | Source of the text |
|---|---|---|---|
| 1. Start here: study guides | `mendis/` | Dr. N. K. G. Mendis, *The Abhidhamma in Practice* (BPS, The Wheel 322/323, 1985, repr. 2005) | scan: OCR proofread against the page images (`ocr/mendis/`) |
| | `fundamental/` | Dr. Nandamālābhivaṃsa, *Fundamental Abhidhamma*, Part I (CBS Sagaing 2005) | PDF text layer |
| | `tinmon/` | Dr. Mehm Tin Mon, *Buddha Abhidhamma: Ultimate Science* (BuddhaNet) | PDF text layer, old Pāli font mapped |
| | `handbook/` | Sayādaw U Sīlānanda, *Handbook of Abhidhamma Studies*, Vols. I–II (SBVMS 2012) | PDF text layer |
| | `practical/` | *Practical Abhidhamma Course*, v1.1 (2016), by “Rob” | PDF (LuaTeX) read with PyMuPDF; figures as images |
| | `lakkhana/` | *Characteristic, Function, Manifestation & Proximate Cause* (compiler not named, 2018) | PDF text layer, Mac “Norman” font mapped |
| 2. The Saṅgaha in Pāli | `sangaha/` | Abhidhammatthasaṅgaho, Sixth Council edition | VRI tipitaka-xml `abh07t.nrf.xml`, first book |
| 4. The commentaries | `vibhavini/` | Abhidhammatthavibhāvinīṭīkā (Sumaṅgala) | VRI `abh07t.nrf.xml`, second book |
| | `paramattha/` | Paramatthadīpanī, the Saṅgaha-mahāṭīkā (Ledi Sayadaw) | VRI `e0301n.nrf.xml` |
| | `anudipani/` | Anudīpanī (Ledi Sayadaw) | VRI `e0401n.nrf.xml` |
| 5. Background | `guide/` | Nyanatiloka, *Guide Through the Abhidhamma Piṭaka* (BPS, 4th ed. 2008, PDF 2019) | PDF text layer (Unicode) |
| 3. The Saṅgaha in English | `narada/` | Nārada Thera, *A Manual of Abhidhamma* (Vājirārāma; Preface 1978) | palikanon.com web edition, PDF (Word) |
| To come | | Bhaddanta Dr. Rewata Dhamma, *Process of Consciousness and Matter* (Triple Gem Publications 2004; © 2007 Birmingham Buddhist Vihara; sponsored for free distribution) | PDF text layer (Word) |
| | | Rerukane Chandawimala Mahāthera, *Basic Facts of Abhidhamma* (*Abhidharmaye Mūlika Karuṇu*), tr. D. J. Percy Silva (“Non-Commercial Distribution”) | scan (96 dpi), legacy Pāli font |
| | | Ashin Nandamālābhivaṃsa, *Paramatthadīpanī: An Annotated Translation* of chapters 1–4 (M.Phil. thesis, University of Kelaniya, 1996), published with the author's permission | scan (150 dpi), OCR from the page images |
| | | Bhikkhu Bodhi (Gen. Ed.), *A Comprehensive Manual of Abhidhamma* (BPS 1993) | PDF |
| | | Shwe Zan Aung & C. A. F. Rhys Davids, *Compendium of Philosophy* (PTS 1910) | scan |

The VRI source files are kept in `sources/` (UTF-16, as published at
github.com/VipassanaTech/tipitaka-xml, `romn/`). The order of the books and the shelves is set in
`scripts/build_home.py` (SHELVES) and `data/library.json`.

```
index.html              library home: the shelves, About this library, A note on rights
<slug>/                 one split reader per book: index.html + c/<part>.html, ids.json, search.json
map/index.html          the Saṅgaha map (scripts/build_map.py)
charts/                 the charts: index.html, svg/, thumb/, pdf/ (scripts/build_charts.py, scripts/charts.html)
references/index.html   the reference list (built from data/references.json)
shared/                 reader.css, reader.js, home.css: shared by every page
data/library.json       the books and their reader settings, in shelf order
data/<slug>.json        the structured text of each book
data/sangaha-key.json   the paragraph keys shared by the Saṅgaha and the Vibhāvinī (the chips between them)
data/pd-key.json        the paragraph numbers shared by the Paramatthadīpanī and the Anudīpanī
scripts/pali/convert.py the four Pāli books from sources/
scripts/build.py        renders one book:  python3 scripts/build.py <slug>
scripts/build_home.py   the home page and references/index.html
scripts/build_map.py    the Saṅgaha map
scripts/make_references.py   writes data/references.json
scripts/check_site.py   loads every page at 320, 400 and 1300 px: overflow, console errors, failed requests
scripts/check_phone.py  phone emulation of the sidebar and the "In this part" list
```

Rebuilding everything:

```sh
for s in sangaha vibhavini paramattha anudipani; do python3 scripts/pali/convert.py $s; done
for s in sangaha vibhavini paramattha anudipani; do python3 scripts/build.py $s; done
python3 scripts/build_map.py && python3 scripts/make_references.py && python3 scripts/build_home.py
python3 scripts/check_site.py
```

(`data/sangaha-key.json` and `data/pd-key.json` list every paragraph number the paired books have;
regenerate them after a conversion changes the numbers.)

## The map: the Saṅgaha's own paragraphs

The Dhammasaṅgaṇī Library uses the mātikā to tie its books together. This library uses the
Saṅgaha's paragraphs instead. The Sixth Council edition numbers the paragraphs of the Saṅgaha
from 1 in each of its nine chapters (paricchedas), and numbers the Vibhāvinī by the paragraph of
the Saṅgaha it explains. The library writes these numbers I.1 … IX.75:

- internally a paragraph's key is chapter × 1000 + number (`pnum` 4006 = IV.6); its anchors are
  `#p4006` and `#p4-6`, and the § box takes `4.6`;
- the number shown beside the paragraph is the label (`IV.6`), set by `pnum_span` in build.py;
- the Saṅgaha and the Vibhāvinī share `data/sangaha-key.json`, so each paragraph has a chip to the
  same paragraph in the other book, only where that book has it; both are marked `pts_sections`
  (numbered by the map), so a book with its own numbers and a `pts_map` to the keys (Nārada) gets
  chips to them, and they to it;
- `map/` lists every paragraph of the Saṅgaha with its opening words and the same place in each
  book keyed to it.

The opening verses (I.1–2, before the chapter heading) are a part of their own in the reader but
keep the chapter-I numbers they have in the edition. The closing verses (nigamana) are a part of
their own and are not numbered.

Ledi Sayadaw's **Paramatthadīpanī** runs one numbering through the whole book (1–174), and his
**Anudīpanī** explains it under the same numbers. Those two books are keyed by that number
(`data/pd-key.json`, with chips between them) and tied to the Saṅgaha chapter by chapter: each
part carries `sangaha_ch`, and the map links each chapter's part.

When the English translations come in, each will be matched to these keys by content, the way
Khine was matched to the PTS numbers in the Dhammasaṅgaṇī Library: Bodhi numbers his §§ within
each chapter, and how closely they follow the VRI's division will be checked paragraph by paragraph.

## The Pāli books (sangaha/, vibhavini/, paramattha/, anudipani/)

`scripts/pali/convert.py` reads the VRI XML: one part per chapter, with the opening and the
closing as parts of their own. Headings (chapter, subhead) become the part's contents; bold (in the
commentaries, the words of the text being explained) is kept; verses (gatha1…gathalast) are
indented lines; the pages of the Myanmar edition (`pb ed="M"`) are page anchors `#pg<n>`. None of
the three files has variant readings (`<note>`).

**The text is unchanged.** The paragraph numbers that make the map are chosen as the longest run of
numbers that goes up through the book (`accepted()`), so a slip in the file does not break the
sequence. The numbers outside that run stay in the text as printed and are not anchors:

- Saṅgaha: none. Chapter IV is numbered 1, 2, 4 in the edition (there is no IV.3); kept.
- Vibhāvinī: the seven verses of the Nigamanakathā, numbered 1–7 in the file.
- Paramatthadīpanī: 31 (out of order), 66 and 67 (repeated as "[66]" …). Paragraph 30 has no number in the file.
- Anudīpanī: 52, 66, 67, 136, 161 (repeated or out of order), "14. 147" (the file's own slip for 147),
  197 (for 157), 169 (for 159), 262 (for 172, the comment on the Paramatthadīpanī's closing paragraph), and the colophon verses 1–2. The Anudīpanī does not comment on every
  paragraph of the Paramatthadīpanī, so its numbers have gaps.

The script prints these lists each time it runs.

## Nārada Thera — A Manual of Abhidhamma (narada/)

*Abhidhammattha-Sangaha of Anuruddhācariya: A Manual of Abhidhamma, edited in the original Pali
text with English translation and explanatory notes* by Nārada Thera, Vājirārāma, Colombo (the
Preface is dated 14.7.1978), from the web edition of palikanon.com, as a PDF made from Word in 2010
(“for free distribution only”). The PDF has a text layer; no OCR was needed.

```sh
pdftotext -layout Abhidhammattha-Sangaha-Narada.pdf work/narada.txt
python3 scripts/narada/convert.py work/narada.txt      # data/narada.json and data/narada-key.json
python3 scripts/build.py narada && python3 scripts/build_map.py
```

**Chapter VIII (Paccaya)** is missing from this copy (the contents list it, but the text runs from
Chapter VII straight to Chapter IX). It is transcribed for this library from the first edition — *A
Manual of Abhidhamma*, Vols. I–II, Vājirārāma 1956–57, reprinted by the Buddha Sāsana Council,
Kaba-Aye, Rangoon, 1970 (a scan without text, 471 pages) — PDF pages 374–405, printed pp. 73–103:

```sh
pdftoppm -f 374 -l 405 -r 300 -gray -png Manual-Vol-I-II.pdf work/n8/pg      # the page images
for f in work/n8/pg-*.png; do tesseract $f ${f%.png} -l eng --psm 6; done      # OCR drafts
python3 scripts/narada/restore.py work/n8/pg-*.txt                            # drafts with the Pāli diacritics put back
#   … each page read against its image and written into scripts/narada/ch8/*.md …
```

- `restore.py` puts the diacritics back into the OCR (Tesseract reads ā as d/a/4, ṁ as m, ñ as fi/ii)
  by matching each word, without its diacritics, with the words of the Pāli books of the library; it
  only makes drafts. Every page was then read against its image (the Pāli at twice the size) and
  written out by hand in `scripts/narada/ch8/` (markup described in `chapter8()` of convert.py).
- The text is as printed: the print's ṁ is written ṃ (so this chapter's Pāli has its diacritics, where
  the web chapters have plain m and n); misprints are kept (*saṃhkārā*, *Anataraniruddhā*,
  *anantarasamanataranatthi-*, *nāmārupānaṃ*, *statess*, *continguity*, “Section 2” printed for
  Section 4 over the English of the 24 relations). The number of note 39 is smudged in the scan and is
  read from its place between notes 38 and 40.
- The two full-page diagrams — the Wheel of Life (p. 74) and Diagram 5, Paṭicca Samuppāda (between
  pp. 90 and 91, printed sideways and turned upright) — are images (`narada/fig/ch8-375.png`,
  `ch8-392.png`).
- Its four sections are tied to the Saṅgaha by the same matching (VIII.1, 2, 14, 38).

- Parts: the Preface and Chapters I–VII, IX. Nārada numbers his sections § 1 … anew in each chapter,
  once before the Pāli and again before the English; the first is the anchor (key chapter × 1000 + n,
  `#p4005` and `#p4-5`, the § box takes `4.5`), the second number is left out of the English.
- The ties to the Saṅgaha (`data/narada-key.json`, 87 of 101 sections) come from `match()`: the Pāli
  of each section, folded (no diacritics, spaces or punctuation, list markers left out), against the
  opening of each paragraph of the same chapter in the Sixth Council text, aligned in order, only where
  the likeness is at least 0.6. Each tie was looked over. Sections without a tie get no chip: those
  whose Pāli is set as a list or table (I § 7–9, II § 8–9), a question only (II § 11 “Katham?”), and
  the summaries in English (IV § 17, VII § 2, IX § 9).
- The Pāli is as the PDF has it, with plain m and n for ṃ and ṅ (*cittam*, *sangaha*); search folds
  them anyway.
- The diagrams are the PDF's text tables, shown with their columns (`pre`). In some of them the PDF
  breaks a cell over two lines (*Magg / a*); they are kept as they are.
- A short line standing alone is a heading when it is in English or in brackets; a line of Pāli verse
  standing alone stays text. A list number standing alone joins the line after it.

## Dr. Mehm Tin Mon — Buddha Abhidhamma: Ultimate Science (tinmon/)

*Buddha Abhidhamma: Ultimate Science* by Dr. Mehm Tin Mon (Buddha Dharma Education Association,
BuddhaNet), from the PDF (PageMaker, 2003; 448 pages), taken from its text layer.

```sh
pdftotext -layout Buddha-Abhidhamma-Ultimate-Science.pdf work/tinmon.txt
python3 scripts/tinmon/convert.py work/tinmon.txt && python3 scripts/build.py tinmon
```

- **The font.** The PDF is set in an old Pāli font that puts accented Latin letters where the Pāli
  ones belong. `FONT` turns them back: à ā, ã ī, å ū, ¤ ñ, ñ ṭ, õ ṇ, ü ṃ, ï ṅ, ë ḷ, ó ṭ, ò Ṭ,
  â/À/Ã Ā, ä Ī, æ Ū, ö Ṇ, ¥ Ñ. The map was read from the words (*pañisandhi* = *paṭisandhi*,
  *bhavaïga* = *bhavaṅga*, *KAMMAòòHâNA* = *KAMMAṬṬHĀNA*) and the chapter titles were checked against
  the page images. The script reports any old-font letter left (none).
- **Parts:** the Preface and Introduction, the nine chapters (the Saṅgaha's own, each marked
  `sangaha_ch` and listed on the map), and the Conclusion with About the Author. Chapter 5 keeps its
  printed title, *VĪTHIMUT or BHŪMI*.
- **Paragraphs** from the layout: a first-line indent starts a paragraph; an indented numbered line
  is a list item; a line with a gap of three spaces or more inside it is a table row, kept with its
  columns (`pre`); page numbers are dropped and paragraphs run on over page breaks; a drop capital
  is joined to its word.
- **Headings** are the section titles of the book's own contents (matched letter for letter, with
  or without their number, "1 Four Āsavas …"; contents lines with dot leaders are read wherever they
  stand), and other short Title-Case lines after the end of a paragraph that have no comma, semicolon
  or colon inside; a bracketed line under a heading is a sub-heading.
- **Line-end hyphens:** kept where the book writes the same word with the hyphen inside a line
  (*sense-sphere*, *Lobha-mūla*), joined otherwise.
- **Not in the PDF:** the charts the book refers to as "attached at the back" (Charts 1–10).

## Dr. N. K. G. Mendis — The Abhidhamma in Practice (mendis/)

Dr. N. K. G. Mendis, *The Abhidhamma in Practice*, Buddhist Publication Society, Kandy, The Wheel
Publication No. 322/323, first edition 1985, reprinted 2005, from a scanned PDF (80 pages;
`ocr-sources/mendis.pdf`, kept out of the site). Its text layer (Acrobat ClearScan) was too scrambled to
use, so each page was read with `tesseract` at 300 dpi and proofread line by line against the page image
by the autopilot runs (see `AUTOPILOT_LOG.md`, 12–13 November 2026), into `ocr/mendis/p001.md` …
`p080.md` (one file per PDF page; PDF page N = book page N − 5 from p006 on).

```sh
python3 scripts/mendis/convert.py && python3 scripts/build.py mendis
```

- **The text is as printed.** The book's own misprints are kept (*presense*, *orgination*,
  *spheer*, "hed him" for "led him" …; the log lists them page by page). Two readings that the scan
  leaves in doubt are marked ⟨?⟩: "were not⟨?⟩ uttered" (Introduction) and "(c)⟨?⟩ to clench the teeth"
  (The Cetasikas: the fifth of five methods, where (e) is surely meant). The Pāli diacritics are the
  book's own; "Pali" and "Sangha" are printed without them.
- **Parts:** the imprint and the Preface, the Introduction (with the homage under the book's title),
  The Cittas, The Cetasikas, Rūpa, Planes of Existence, Causality, Nibbāna and About the Author. The
  cover, the title page and the contents page are left out (the reader has its own). On the Saṅgaha map:
  The Cittas → I, The Cetasikas → II, Rūpa → VI, Planes of Existence → V, Causality → VIII.
- `<!-- cont -->` in a page file joins its first paragraph (or verse) to the page before, except where a
  list goes on over the page (its next item stays a paragraph of its own). The book's italic sub-heads
  are headings; verse (Dhammapada 288–289, the formula "When THIS is present …", the Visuddhimagga verse)
  is set in lines; the ditto table of the six pairs of beautiful factors is a table of two columns. The
  two footnotes are set under the paragraphs that cite them, numbered in each part.
- No printed page numbers are carried into the reader.

## Dr. Nandamālābhivaṃsa — Fundamental Abhidhamma, Part I (fundamental/)

*Fundamental Abhidhamma, Part I*, 2nd extended edition (January 2005, revised November 2005),
© Centre for Buddhist Studies, Mahāsubodhayon Monastery, Sagaing, from the PDF (Acrobat from Word,
2006; 104 pages), taken from its text layer, which is in Unicode.

```sh
pdftotext -layout Fundamental-Abhidhamma.pdf work/fundamental.txt
python3 scripts/tinmon/convert.py work/fundamental.txt fundamental && python3 scripts/build.py fundamental
```

The converter is the one of *Ultimate Science* (`BOOKS['fundamental']`: no font map, the body from
the Editorial Preface, one title line under "CHAPTER n"). This book's headings are also centred lines
(a title of its contents, or a count such as "Akusala – 12") and short lines ending in a colon
("Abhidhamma:"); both are taken as headings.

- **Parts:** the Editorial Preface, About the Author and The History of Abhidhamma, then the five
  chapters of Part I. They are in the book's own order, and each is tied to the Saṅgaha's chapter on
  the map: 1 Citta (I), 2 Cetasika (II), 3 Rūpa (VI), 4 Pakiṇṇaka (III), 5 Vīthi (IV).
- **The diagrams** are the PDF's text tables, kept with their columns. The large classification charts
  (e.g. "Citta 89/121") are set in the PDF as loose text boxes and come out in pieces; they are kept
  as they are.
- **Part II** (247-page copy, pp. 106–247: from Chapter 5 Vīthi to Paccaya and Kammaṭṭhāna) has a text
  layer in a broken font encoding (the words come out as symbols), so it needs OCR and proofreading
  from the page images, with the diacritics put back by hand. That is on hold. The first 105 pages of
  that copy are the same Part I.

## Sayādaw U Sīlānanda — Handbook of Abhidhamma Studies, Vols. I–II (handbook/)

U Sīlānanda's lectures on the Saṅgaha, edited from his American courses: *Handbook of Abhidhamma
Studies*, Volumes I and II, first edition October 2012, © SBVMS (Selangor), printed for free
distribution, from the PDFs (OpenOffice, 2012), taken from their text layer (Unicode).

```sh
pdftotext -layout Handbook-I.pdf work/handbook-1.txt && pdftotext -layout Handbook-II.pdf work/handbook-2.txt
python3 scripts/tinmon/convert.py work/handbook-1.txt handbook1
python3 scripts/tinmon/convert.py work/handbook-2.txt handbook2
python3 scripts/tinmon/handbook.py && python3 scripts/build.py handbook
```

- Volume I: Editorial Preface, Editor's Note, Introduction, Chapters One–Three (Three only Vedanā,
  Hetu and Kicca). Volume II: front matter, Chapters Four–Six. A third volume (Seven–Nine) is not here.
  `handbook.py` joins the volumes into one reader; each part's label names its volume.
- The converter is the shared one (`BOOKS['handbook1']`, `['handbook2']`): the running head at the top
  of each page ("Chapter One") and the page numbers are dropped, and so are the contents lines with dot
  leaders (Volume II prints its contents after the preface); the chapter titles are "Chapter One" …
  in words. The question-and-answer passages ("Sayādaw: … / Student: …", with a hanging indent) are
  paragraphs of their own. The prose is justified with wide gaps, so for this book only a long line of
  six words or more with even gaps is prose, not a table row (`JUSTIFIED`); bullets are list items.
- The lectures cite Bhikkhu Bodhi's *Comprehensive Manual* ("CMA, I, Guide to §7, p.39"); those
  references are left as text until the CMA is in the library.

## Practical Abhidhamma Course (practical/)

*Practical Abhidhamma Course*, version 1.1 (April 2016), practicalabhidhamma.com. The course names its
author only as “Rob” (rob.abhidhamma@gmail.com); the library credits it so. The PDF was made with
LuaTeX and is read with PyMuPDF (`pip install pymupdf`), which gives each span's size and style:

```sh
python3 scripts/practical/convert.py Practical-Abhidhamma.pdf && python3 scripts/build.py practical
```

- 20.7 pt opens a part (Lessons 1–8, the Postscript, Appendices 1–3), 17.2 pt is a heading, 14.3 pt a
  sub-heading, 12 pt the text; bold and italic are kept as `**…**` and `*…*`.
- **Footnotes** (about 650): a 7 pt number at the foot of a page opens a note, an 8 pt number in the
  text is its reference; notes are renumbered in each part and set under the paragraph that cites them.
- **Figures** (102): drawn as vector graphics with words laid over them, so each is cropped from the
  page, from the end of the text above it to the end of its caption, and kept as an image
  (`practical/fig/NNN.png`, 1.6×, 48 colours, 2.2 MB in all); the caption is its alt text, and the
  words inside a figure are left out of the text.
- On the Saṅgaha map: Lesson 3 (Citta) → I, 4 (Cetasika) → II, 5 (Rūpa) → VI, 6 (Realms) → V,
  8 (Processes) → IV; Lesson 7 (Kamma and Natural Decisive Support) spans V and VIII and is not tied.

## Nyanatiloka — Guide Through the Abhidhamma Piṭaka (guide/)

Nyanatiloka Mahāthera, *Guide Through the Abhidhamma Piṭaka*, fourth edition, newly typeset (BPS, Kandy,
2008; Bhikkhu Bodhi made minor changes to the first four chapters), from the PDF of 2019
(`sources/guide-2019.pdf`), taken from its text layer, which is in Unicode, with the shared converter
(`BOOKS['guide']`):

```sh
pdftotext -layout sources/guide-2019.pdf work/guide.txt
python3 scripts/tinmon/convert.py work/guide.txt guide && python3 scripts/build.py guide
```

- This copy replaced an earlier one (the 2007 PDF of the 2nd–3rd edition text), whose Pāli was in an old
  font and had to be mapped letter by letter (`FONTS['guide']` is kept for it). The 4th edition is the
  better text: Unicode Pāli, revised terms, and the Appendix II tables. It does not have the prefaces of
  the earlier editions.
- Parts: the publisher's preface and the introduction (the body starts at the second "Publisher's
  Preface", the first being the contents), the Mātikā, the seven books (a centred roman numeral and the
  book's title in capitals), Appendix I (Dependent Origination) and Appendix II (Tables). The running
  heads (the book's title on one page, the chapter's on the other) are dropped wherever they stand; a
  title in capitals set with spaces around a dotted letter (PAṬ Ṭ HĀNA) is closed up; the few ¿ left from
  the old font in the typesetting are ḷ (*saḷāyatana*).
- It is a guide to the canonical books, not to the Saṅgaha, so it sits on a shelf of its own and is not
  on the Saṅgaha map.

## Characteristic, Function, Manifestation & Proximate Cause (lakkhana/)

*Characteristic, Function, Manifestation & Proximate Cause (lakkhaṇa-rasa-paccupaṭṭhāna-padaṭṭhāna)*,
22 pages, PDF from Word (Mac, 2018); the compiler is not named. Each ultimate reality — the 28 kinds of
matter, the types of consciousness, feeling, perception and the cetasikas by their groups — with its
four defining devices in English and the Pāli of the commentaries (DhsA, Vism).

```sh
python3 scripts/lakkhana/convert.py sources/lakkhana.pdf && python3 scripts/build.py lakkhana
```

- Read from `pdftotext -layout` (the PDF draws its diacritics and some words twice as separate pieces,
  so its spans are not usable); each line is split at the gap before the Pāli column (column 60 on).
- The Pāli font "Norman": å ā, ˆ ṇ, Ë ū, ¥ ī, ∫ ṅ, ¬ ḷ, ∂ ḍ, ◊ ṃ; its ṭ is a no-break space, which the
  text layer gives as a plain space (*paccupa håna*): a space between two Pāli letters in the Pāli column
  is put back as ṭṭ or ṭ, whichever gives a word of the Sixth Council texts (ṭṭ before h otherwise).
- Each reality is a heading and a table (Characteristic, Function, Manifestation, Proximate cause ×
  English, Pāli), its references under it; the groups of cetasikas ("The Universals - 7") are
  sub-headings; the notes on abbreviations at the feet of the pages are gathered at the end.
- In item (1) the document sets the Pāli in two lines (the device's name above, the compound below,
  *sampaṭicchana-paccupa…*); it is kept as it reads.

## The charts (charts/)

Seventeen charts (23 pages) from the course of *Fundamental Abhidhamma* and its teachers: Aggañāṇī
(© 2005, with the Centre for Buddhist Studies, Sagaing; updated 2008) and Dr. Rewata Dhamma (the 31
realms, the eye-door process). The PDFs are in `sources/charts/`; `python3 scripts/build_charts.py`
writes the page.

- **Vector, not pictures.** Every page is converted to SVG with `pdftocairo -svg` (the text becomes
  outlines, the colours and lines are kept), and its viewBox is cropped to the printed area (found
  from a 72-dpi render, 1 px = 1 pt), so the chart fills the viewer and stays sharp at any zoom. A
  small PNG of the first page is the card's thumbnail; the original PDF can be downloaded.
- **Heavy charts.** A chart whose SVG would weigh more than 2 MB (Hanh Thuong's tree, with its colour
  gradients: 7 MB) is drawn from its PDF with pdf.js instead, like the Systematization.
- **The text** of each page (`pdftotext -layout`) is kept under its card ("Text of this chart"), so
  that the charts can be found with the browser's search and read by a screen reader.
- **The viewer** opens a chart full-screen: fitted to the screen; zoom with the wheel, + and −, the
  buttons, a double click or two fingers; drag to move; ← → through the pages and the charts; ⟳ or r
  turns a wide chart, and on a phone held upright a wide chart is turned to fill the screen; Esc closes.
  Every chart page has an address (`charts/#rupa_pali`, `#material_phenomena-3`).
- **Grouped by the Saṅgaha's chapters** (`CHARTS` in build_charts.py): the four realities (with Hanh
  Thuong's tree of them, 2015); I the 89/121
  cittas; II the 52 cetasikas, their combination with the cittas, the aggregate of feeling; III feeling,
  roots, functions, doors, objects, bases; IV the eye-door process; V the 31 realms; VI the 28 rūpas.
  The Saṅgaha map lists each chapter's charts.
- **The Systematization.** Bhikkhu Vietnam Dhammadhaja, *Systematization of Abhidhammaṭṭha Saṅgaha*
  (Na Uyana Forest Monastery, Sri Lanka, 2025–26; `sources/systematization.pdf`, 255 landscape pages):
  tables and process diagrams citing the pages of CMA, PCM (Revatadhamma, *Process of Consciousness and
  Matter*) and HOA (Sīlānanda's *Handbook*). The PDF is a run of documents each numbered "Page 1 of n";
  `SYS` in build_charts.py splits it into its 28 documents (`charts/sys/*.pdf`), each a card in the
  chapter it belongs to (I–VI, VIII, IX). The book gives them no titles: the titles are the library's,
  from what each document sets out. As SVG the 255 pages would weigh 71 MB against the PDF's 3.3 MB, so
  these pages are drawn from the PDF in the browser with pdf.js (`shared/pdfjs/`, pdfjs-dist 4.10.38,
  legacy build, Apache-2.0), cropped to the printed area and drawn again after each zoom, so they too stay
  sharp. Their text is kept under each card. In two documents the tables run on over the page breaks
  (*jāti* … *dhātu*, the 89 cittas by class; the twelve links of dependent origination): a table begun
  at the foot of a page goes on at the head of the next, with no column heads repeated. For these
  (`STITCH` in build_charts.py) the viewer shows one table at a time, whole: `table_views` finds the
  blocks of each page (bands of print between blank gaps, below the running head) and joins a block
  that reaches the foot of a page to the block at the head of the next page of the same document
  ("Page 2 of n" and on), and the viewer draws the pieces one under the other from the PDF, unchanged
  ("table 4 of 8"). The other documents are shown page by page: their long tables repeat their heads on
  every page, or each page is a sheet of notes and diagrams.

## Changes to the shared reader

- `scripts/build.py`: a numbered paragraph does not hang an opening “(1)” in the margin, which holds its
  number and chips; `pnum_span` shows a block's `label` and its `alias` anchors when it has them;
  `num_label()` writes a key of 1000 or more as I.11 (card ranges, chip titles);
  `goto_text` makes the § box a text field that takes `4.6`.
- `shared/reader.css`: the four Pāli books wrap their long compounds anywhere (as the Pāli books of
  the Dhammasaṅgaṇī Library do), so nothing scrolls sideways at 320 px.
- `scripts/build_home.py`: a book tied to the Saṅgaha by chapter, or keyed by chapter × 1000, shows its
  number of chapters on its card; empty stats are left out.
- `scripts/check_site.py` checks `map/` instead of `matika/` and `terms/`.

## Checks

`python3 scripts/check_site.py`: 134 pages × 3 widths, no problems (13 November 2026).

## Checking the formatting

`python3 scripts/audit_format.py [book]` looks through the converted books for the faults that text taken from
PDFs is prone to: lone braces or punctuation, paragraphs cut in two, lines of a table or a diagram set as text,
headings that are sentences, words broken into letters. What is left after the fixes is mostly the books' own
layout (lists of terms, Pāli verse lines, `namely:-`).

- The shared converter (`scripts/tinmon/convert.py`) joins hanging indents and items set at the margin, turns
  "term = meaning" lists into one paragraph per term, keeps thought-process diagrams (`P C SP ST V J J …`)
  together as preformatted blocks, and drops lone `{` / `}` lines. The Guide's two lists drawn beside braces
  (the 22 faculties, the schools of the Kathāvatthu) are written out in `guide_fixes()`.
- Nārada: the notes' "13. Vicikicchā-" lines are joined to their notes; Diagram XIV is rebuilt as a table with
  upright column heads (the last rows' marks follow the book's counts).
- Practical Course: figures are bounded by running text only (so whole tables are cropped), and heading and
  caption lines keep their spaces.
