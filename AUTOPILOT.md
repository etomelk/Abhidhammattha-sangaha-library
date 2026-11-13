# Autopilot: the books that need OCR

A scheduled task runs every two hours (minute 51 of every odd UTC hour). Each run is a fresh session
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

| # | slug | Book | Source | Pages to do |
|---|---|---|---|---|
| 1 | `mendis` | N. K. G. Mendis, *The Abhidhamma in Practice* (BPS Wheel 322/323) | `ocr-sources/mendis.pdf`: Acrobat ClearScan text layer, full of OCR slips ("determiniflg") | 80 |
| 2 | `fundamental` (Part II added to the existing book) | Dr. Nandamālābhivaṃsa, *Fundamental Abhidhamma*, Part II | `ocr-sources/fundamental-2.pdf`, pp. 106–247 (1–105 are Part I, already on the site); its text layer is a broken font encoding, so OCR the page images | 142 |
| 3 | `shwezanaung` | Shwe Zan Aung & C. A. F. Rhys Davids, *Compendium of Philosophy* (PTS 1910) | `ocr-sources/shwe-zan-aung.pdf`: a scan with a poor text layer (words split one per line) | 354 |
| 4 | `cma` | Bhikkhu Bodhi (Gen. Ed.), *A Comprehensive Manual of Abhidhamma* (BPS 1993) | `ocr-sources/cma.pdf`: a scan with no text layer. **The fold-out Tables 2.4 and 6.3 are missing from this copy**: say so on the book's first page and in README | 432 |

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
   `scripts/build_home.py` (Mendis and Fundamental: "Start here"; Shwe Zan Aung and Bodhi: "The
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
- all four books are done.
