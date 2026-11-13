# Autopilot log

Newest first. See AUTOPILOT.md for the standing instructions.

## 2026-11-13 — Mendis pp. 51–80 proofread (all pages done)

Proofread PDF pages 51–80 of `ocr-sources/mendis.pdf` (book pp. 46–74 plus the unnumbered
"About the Author": rest of "Planes of Existence", "Causality", "Nibbāna") into
`ocr/mendis/p051.md`–`p080.md`. The last 30 pages were taken in one run because pp. 79–80 are
short; every page was read from `tesseract` at 300 dpi and corrected line by line against the page
image (zoomed where letters were broken). Every page of Mendis is now proofread.

Conventions as in the earlier entries, plus:
- `## CAUSALITY` (p057), `## NIBBĀNA` (p074), `## About the Author` (p080) are chapter-level
  titles; `### The Natural Laws` (p057), `### Dependent Origination` (p058), `### Modes of
  Conditioning` (p064) are the centred sub-heads.
- The plane lists (p051–055) keep the book's A./B./C. groups and a)–f) items, one per paragraph;
  the plane number in brackets "(1)"…"(31)" kept as printed.
- "4 & 5." (p065) kept as the book prints it (one paragraph for two conditions).
- The "When THIS is present…" formula (p058–059) and the Visuddhimagga verse (p070) are `>` lines.
- Footnote p057 (Shattock) is `[^1]` on that page (footnote ids are per page; the converter should
  renumber).
- p080 has no book page number: its first line says "book page (unnumbered, back matter)".

Words marked ⟨?⟩: none.

Letters missing from the print (ink drop-out) but certain from the sense, written whole and not
marked: p054 "accessible", "lower five fetters", "rites and ceremonies", "They will destroy";
p057 "influencing" (printed "inf uencing"); p059 "saṁkhārapaccayā" (the r is a broken fragment);
p069 "continuous"; p052 "wholesome" (first letter broken). Punctuation read through specks:
p070 "first link, it must" (a faint mark, read as a comma); p072 "sensory stimuli. Security".

Printed slips kept as printed (not corrected): p051 "he 'perpetual wandering'" (for "the");
p052 "creations of other"; p055 "presense", "neither perception or non-perception", the odd quote
marks "'The Buddha then said:'"; p056 "at urbulent mass", "jhanās"; p057 "(*niyāma dhammā*):"
(colon); p058 "aotion"; p059 "When THIS is not present. there isn't THAT" (full stop), "soṁkhārā",
"taṇhāpoccayā"; p062 "also arise Contact" (no full stop); p063 the heading "Dependent on clinging
there is birth" (the series has "becoming"); p064 "orgination", "realationship"; p066
"(*purejāta paccaya*), This" (comma); p067 "āhāra paccya", "indriya paccya"; p069 "veriety";
p075 "sense spheer world"; p077 "our refuge, The present"; p080 "hed him" (for "led").
List markers printed "1," / "11," (p059) are written "1." / "11.".

The site was not touched (`ocr/` is not published), so check_site was not needed for this push.

Next: Mendis is fully proofread — the next run builds the book into the site (AUTOPILOT.md,
"Build the book"): `scripts/mendis/convert.py` → `data/mendis.json`, library/shelf/README, build,
audit, check_site.

## 2026-11-13 — Mendis pp. 26–50 proofread

Proofread PDF pages 26–50 of `ocr-sources/mendis.pdf` (book pp. 21–45: rest of "The Cetasikas",
"Rūpa", start of "Planes of Existence") into `ocr/mendis/p026.md`–`p050.md`. Text from `tesseract`
at 300 dpi, every page corrected line by line against the page image (zoomed where a letter was in
doubt). Conventions as in the previous entry, plus:
- `## RŪPA` (p038) and `## PLANES OF EXISTENCE` (p050) are chapter titles.
- `### …` for the italic sub-heads on a line of their own: Perception (p027), The Arising of
  Material Form (p043), Decay / Death of Material Form (p045), The Five Groups, Materiality and
  Meditation (p047). The smaller italic labels "*Five Kinds:*" / "*Six Kinds:*" (p026–027) are kept
  as italic paragraphs.
- Numbered and lettered lists keep the book's own markers (`1.`, `i.`, `(a)`, `a)`), one item per
  paragraph; sub-lists (p031 i–iii under item 6) are not indented. A paragraph that continues a
  list item (p035 "Compassion and sympathetic joy…") is a plain paragraph after it.
- The ditto table of the six pairs (p034) is a fenced block keeping the columns.
- First footnote of the book: p048, printed `*`, written `[^1]` with its text at the end of the page.

Words marked ⟨?⟩:
- p037: "(c)⟨?⟩ to clench the teeth…" — the fifth of five methods; the print shows "(c)", (e) is
  surely meant. Kept as printed.

Printed slips kept as printed (not corrected): p030 "adhimokka"; p032 "kukkkucca", "Ninteen";
p034 "sammā vacā"; p045 "brokeness", "parallelled"; p047 "(kāmāsava). desire" (full stop for comma).
Read through obvious print damage without marking: p043 "they probably" (a speck, not a comma);
p044 "smell and", "Pure Octad"; p049 "lovely" (printed like "lovelv").

The site was not touched (`ocr/` is not published), so check_site was not needed for this push.

Next: Mendis, page 51 (30 pages left, 51–80).

## 2026-11-13 — Mendis pp. 1–25 proofread

Proofread PDF pages 1–25 of `ocr-sources/mendis.pdf` (cover, title, imprint, contents, Preface,
Introduction = book pp. 1–4, "The Cittas" = book pp. 5–19, start of "The Cetasikas" = book p. 20)
into `ocr/mendis/p001.md`–`p025.md`. The ClearScan text layer was too scrambled to use (lines out of
order); the text was taken from `tesseract` at 300 dpi and every page corrected line by line against
the page image. Diacritics restored from the page (the print has them: ā ī ū ṭ ṇ ñ ṅ ṁ); "Pali" and
"Sangha" stay without diacritics as printed.

Conventions for the converter (to be written when the book is built):
- PDF page N = book page N − 5 from p006 on; pp. 1–5 are front matter.
- `<!-- cont -->` on line 2: the page's first paragraph continues the previous page's last one.
  A word hyphenated across a page break is written whole on the earlier page.
- `## …` chapter titles (THE CITTAS p010, THE CETASIKAS p025); `### …` for the book's own italic
  sub-heads on a line of their own (p017, p025); `*Run-in head.*` kept as italics in the paragraph.
- Dhammapada verse (p022) as `>` lines, one per printed line.

Words marked ⟨?⟩:
- p007: "were not⟨?⟩ uttered" — the print reads like "nut"; "not" is certainly meant.

Printed slips kept as printed (not corrected): p008 "spiritual development Ideally" (no full stop);
p011 "classified various ways", "according their nature", "coninuum"; p012 "vipāke citta";
p016 "intenions"; p019 "memories possible Since"; p023 "Buddhst"; p005 "who, with, devotion".

The site was not touched (`ocr/` is not published), so check_site was not needed for this push.

Next: Mendis, page 26.

## 2026-11-12 — set up

The owner asked for the four books on hold to be done from the shortest to the longest, every two
hours. Sources copied to `ocr-sources/`; queue: Mendis (80 pp.), Fundamental Abhidhamma Part II
(pp. 106–247), Shwe Zan Aung (354 pp.), Bodhi's CMA (432 pp.). Next: Mendis, page 1.
