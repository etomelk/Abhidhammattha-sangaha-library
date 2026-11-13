# Autopilot: the books that need OCR

A scheduled task runs every hour (minute 51 of every UTC hour; changed from every two hours on 2026-11-13 at the owner's request). Each run is a fresh session
with no memory: this file, `data/autopilot.json` (the position) and `AUTOPILOT_LOG.md` (what the
runs did) are all it knows. The owner (etomelk@gmail.com) asked on 2026-11-12 for the four books on
hold to be done **from the shortest to the longest**, one chunk per run.

## The rules

- **Branch.** Work on the branch `autopilot` (create it from `main` if it does not exist; merge
  `origin/main` into it at the start of each run). NEVER push to `main`, never force-push, never
  merge into main: the owner merges after reading the log. Commit as Claude
  (`git config user.name Claude; git config user.email noreply@anthropic.com`).
- **Lock.** At the start, read `data/autopilot.json`. If `status` is `paused`, `done` or `blocked`,
  stop with no changes. If `lock` holds a time less than 3 hours old, another run is working: stop.
  Otherwise set `lock` to the current UTC time, commit and push it before doing the work, and clear
  it at the end.
- **Accuracy first.** The site shows the authors' words. Never invent, smooth or modernise the text.
  Where a word cannot be read with confidence, keep the best reading and mark it `⟨?⟩` right after
  the word, and list it in the log. Pāli diacritics are restored only where the word is certain
  (the book's own spelling elsewhere, the PTS/CST form of a well-known term); otherwise keep what
  the page shows.
- **Sources.** The PDFs are in `ocr-sources/` (kept out of the published site by `netlify.toml`).
  Do not commit page images; commit the proofread text only.
- **Checks before every push** that touches the site: `python3 scripts/audit_format.py <slug>`
  (read what it reports and fix what is a conversion fault), the book's build, and
  `python3 scripts/check_site.py` with **0 problems**.

## The queue (shortest first)

Added on 2026-11-13 at the owner's request: Rewata Dhamma's *Process of Consciousness and Matter* (PCM,
which the Systematization charts cite page by page) and Rerukane Chandawimala's *Basic Facts of
Abhidhamma*, put in their place by length after Fundamental Part II. For PCM keep the book's own page
numbers in the first line of each page file (`book page X`) and give the built book page anchors
(`p113`), so that a chart's "PCM p113" can be found. Later the same day the owner added Ashin
Nandamālābhivaṃsa's English translation of the Paramatthadīpanī (his M.Phil. thesis), with the
author's permission.

| # | slug | Book | Source | Pages to do |
|---|---|---|---|---|
| 1 | `mendis` | N. K. G. Mendis, *The Abhidhamma in Practice* (BPS Wheel 322/323) | `ocr-sources/mendis.pdf`: Acrobat ClearScan text layer, full of OCR slips ("determiniflg") | 80 |
| 2 | `fundamental` (Part II added to the existing book) | Dr. Nandamālābhivaṃsa, *Fundamental Abhidhamma*, Part II | `ocr-sources/fundamental-2.pdf`, pp. 106–247 (1–105 are Part I, already on the site); its text layer is a broken font encoding, so OCR the page images | 142 |
| 3 | `pcm` | Bhaddanta Dr. Rewata Dhamma, *Process of Consciousness and Matter*, ed. Ven. Dr. Kumarabhivamsa (Triple Gem Publications 2004; © 2007 Birmingham Buddhist Vihara; its acknowledgement says it was sponsored “for free distribution”) | `ocr-sources/pcm.pdf`: made from Word, with a good Unicode text layer, so take the text from the layer (`pdftotext`) and proofread it against the page images like Mendis; about **40 pages a run** | 223 |
| 4 | `rerukane` | Rerukane Chandawimala Mahāthera, *Basic Facts of Abhidhamma* (*Abhidharmaye Mūlika Karuṇu*), translated by D. J. Percy Silva (every page: “Non-Commercial Distribution”) | `ocr-sources/rerukane.pdf`: page images at 96 dpi, no text layer; render at 300 dpi before tesseract. **The book was typeset in a legacy Pāli font**, so its Pāli prints as à ā, ã ī, å ū, ñ ṭ (“Diññhi”, “Pañhavi”), õ ṇ (“aõu§”), § ṃ, and a box □ for ñ (“dãgha□ca”): write the Pāli in Unicode by this mapping, which is the author's spelling, not a correction; where a letter does not follow it (e.g. “phåla§” in a quotation where the verse has *thūlaṃ*), keep the best reading and mark it ⟨?⟩ | 273 |
| 5 | `paramattha-en` | Ashin Nandamālābhivaṃsa, *Paramatthadīpanī (An Exposition of the True Meaning): A Sub-Commentary on the Abhidhammatthasaṅgaha — An Annotated Translation with a Critical Introduction*, M.Phil. thesis, Postgraduate Institute of Pali and Buddhist Studies, University of Kelaniya, July 1996 (the supervisor is named on the title page: take the name from the image). Chapters 1–4 of the Saṅgaha only. **Published with the author's permission**, given to the owner (his student at ITBMU), as the owner stated on 2026-11-13: say so on the book's first page and in README | `ocr-sources/paramattha-en.pdf`: a 150 dpi scan (281 pages = Introduction i–x and book pp. 1–268) with an Acrobat OCR layer whose Pāli diacritics are garbled: OCR the page images (300 dpi render) and take every Pāli word from the image. Footnotes as `[^n]` at the end of each page. On the shelf "The commentaries", next to the Pāli Paramatthadīpanī (`paramattha/`); tie its chapters with `sangaha_ch` (1–4) | 281 |
| 6 | `shwezanaung` | Shwe Zan Aung & C. A. F. Rhys Davids, *Compendium of Philosophy* (PTS 1910) | `ocr-sources/shwe-zan-aung.pdf`: a scan with a poor text layer (words split one per line) | 354 |
| 7 | `cma` | Bhikkhu Bodhi (Gen. Ed.), *A Comprehensive Manual of Abhidhamma* (BPS 1993) | `ocr-sources/cma.pdf`: a scan with no text layer. **The fold-out Tables 2.4 and 6.3 are missing from this copy**: say so on the book's first page and in README | 432 |

## One run = one chunk

1. **Proofread pages** (most runs): take the next pages of the current book, about **25 pages a
   run** (fewer if they are dense). For each page:
   - get the text: from the text layer where it is usable (Mendis), otherwise `tesseract` at 300 dpi
     (`pdftoppm -r 300 -f N -l N -png`, `tesseract page.png out -l eng --psm 4`; install with
     `apt-get install -y tesseract-ocr` if missing);
   - **look at the page image** (render it and read it) and correct the text against it line by line:
     OCR slips, broken hyphenation, running heads and page numbers removed, footnotes kept at the end
     of the page marked `[^n]`, italics as `*…*`, headings as `## …`, tables as Markdown tables or
     a fenced block keeping the columns;
   - write it to `ocr/<slug>/p<NNN>.md` (NNN = the PDF page number), with a first line
     `<!-- page NNN, book page X -->`.
   Record in `data/autopilot.json` the last page done.
2. **Build the book** (when every page of a book is proofread): write `scripts/<slug>/convert.py`
   that reads `ocr/<slug>/*.md` and writes `data/<slug>.json` in the library's block format (see
   `scripts/practical/convert.py` and the chapters/blocks of any `data/*.json`: `h`, `h4`, `p` with
   `ind`/`note`, `pre`, `table`, `img`). Tie chapters to the Saṅgaha with `sangaha_ch` where a
   chapter follows one. Add the book to `data/library.json` and to a shelf in
   `scripts/build_home.py` (Mendis, Fundamental, Rewata Dhamma and Rerukane: "Start here"; Shwe Zan Aung and Bodhi: "The
   Saṅgaha in English"; Bodhi's §§ are the Saṅgaha's own numbers, so give the book a `pts_map`/
   paragraph keys like Nārada's if the map can use them), write its README section (source, how it
   was made, what is missing), remove it from the "To come" rows, then build:
   `python3 scripts/build.py <slug>`, `build_map.py`, `build_home.py`, audit, `check_site.py`.
   For Fundamental Part II, add its chapters after Part I's in `data/fundamental.json` (keep Part I
   as it is; the converter of Part I is `scripts/tinmon/convert.py`; write Part II's own converter
   and join the two like `scripts/tinmon/handbook.py` joins the Handbook's volumes).
3. **Finish:** a dated entry at the top of `AUTOPILOT_LOG.md` (pages done, words marked `⟨?⟩`,
   anything the owner should look at, the next position), clear the lock, set the next position,
   commit and push `autopilot`. When the last book is built, set `status` to `done`.

## Notify the owner only when

- a book is built and ready to merge (say: merge `autopilot` into `main` to publish it);
- a run is blocked (say why);
- all the books in the queue are done.
