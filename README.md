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
commentaries), and Nārada's Manual (without Chapter VIII, missing from the copy). More English
translations and the study guides are next.

## The books

| Shelf | Folder | Book | Source of the text |
|---|---|---|---|
| 1. The Saṅgaha in Pāli | `sangaha/` | Abhidhammatthasaṅgaho, Sixth Council edition | VRI tipitaka-xml `abh07t.nrf.xml`, first book |
| 3. The commentaries | `vibhavini/` | Abhidhammatthavibhāvinīṭīkā (Sumaṅgala) | VRI `abh07t.nrf.xml`, second book |
| | `paramattha/` | Paramatthadīpanī, the Saṅgaha-mahāṭīkā (Ledi Sayadaw) | VRI `e0301n.nrf.xml` |
| | `anudipani/` | Anudīpanī (Ledi Sayadaw) | VRI `e0401n.nrf.xml` |
| 2. The Saṅgaha in English | `narada/` | Nārada Thera, *A Manual of Abhidhamma* (Vājirārāma; Preface 1978) | palikanon.com web edition, PDF (Word) |
| To come | | Bhikkhu Bodhi (Gen. Ed.), *A Comprehensive Manual of Abhidhamma* (BPS 1993) | PDF |
| | | Shwe Zan Aung & C. A. F. Rhys Davids, *Compendium of Philosophy* (PTS 1910) | scan |

The VRI source files are kept in `sources/` (UTF-16, as published at
github.com/VipassanaTech/tipitaka-xml, `romn/`). The order of the books and the shelves is set in
`scripts/build_home.py` (SHELVES) and `data/library.json`.

```
index.html              library home: the shelves, About this library, A note on rights
<slug>/                 one split reader per book: index.html + c/<part>.html, ids.json, search.json
map/index.html          the Saṅgaha map (scripts/build_map.py)
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

**Chapter VIII (Paccaya) is missing from this copy**: the contents list it, but the text runs from
Chapter VII straight to Chapter IX. A complete copy is wanted.

- Parts: the Preface and Chapters I–VII, IX. Nārada numbers his sections § 1 … anew in each chapter,
  once before the Pāli and again before the English; the first is the anchor (key chapter × 1000 + n,
  `#p4005` and `#p4-5`, the § box takes `4.5`), the second number is left out of the English.
- The ties to the Saṅgaha (`data/narada-key.json`, 83 of 97 sections) come from `match()`: the Pāli
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

## Changes to the shared reader

- `scripts/build.py`: `pnum_span` shows a block's `label` and its `alias` anchors when it has them;
  `num_label()` writes a key of 1000 or more as I.11 (card ranges, chip titles);
  `goto_text` makes the § box a text field that takes `4.6`.
- `shared/reader.css`: the four Pāli books wrap their long compounds anywhere (as the Pāli books of
  the Dhammasaṅgaṇī Library do), so nothing scrolls sideways at 320 px.
- `scripts/build_home.py`: the cards of the Saṅgaha and the Vibhāvinī count the nine chapters; empty
  stats are left out.
- `scripts/check_site.py` checks `map/` instead of `matika/` and `terms/`.

## Checks

`python3 scripts/check_site.py`: 60 pages × 3 widths, no problems (November 2026).
