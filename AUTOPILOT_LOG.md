# Autopilot log

Newest first. See AUTOPILOT.md for the standing instructions.

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
