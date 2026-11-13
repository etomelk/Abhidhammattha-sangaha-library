# Autopilot log

Newest first. See AUTOPILOT.md for the standing instructions.

## 2026-11-13 — Two books added to the queue (owner's request)

The owner sent three PDFs. Two are added: `ocr-sources/pcm.pdf` (Rewata Dhamma, *Process of
Consciousness and Matter*, 223 pages, Unicode text layer; © 2007 Birmingham Buddhist Vihara, sponsored
for free distribution) and `ocr-sources/rerukane.pdf` (Rerukane Chandawimala, *Basic Facts of
Abhidhamma*, tr. D. J. Percy Silva, 273 pages of 96 dpi images marked "Non-Commercial Distribution",
legacy Pāli font: the mapping is in AUTOPILOT.md). They go after Fundamental Part II, by length:
queue now Fundamental II (build) → PCM → Rerukane → Shwe Zan Aung → CMA.

Not added: Y. Karunadasa, *The Theravāda Abhidhamma* (HKU Centre of Buddhist Studies 2010): its
copyright page reads "© Y. Karunadasa. All Rights Reserved", so it cannot go on a public site without
the author's or publisher's permission.

Next: unchanged — build Fundamental Abhidhamma Part II (all its pages are proofread).

## 2026-11-13 — Fundamental Abhidhamma Part II pp. 231–247 proofread (all pages done)

Proofread PDF pages 231–247 of `ocr-sources/fundamental-2.pdf` (book pp. 126–142 of Part II): the rest of
Chapter 9 — 3. *Bodhipakkhiya Saṁgaha* (*Sammappadhāna*, *Iddhipāda*, *Indriya*, *Bala*, *Bojjhaṁga*,
*Maggaṁga*, Special Note, Way of Participation and its table), 4. *Sabba Saṁgaha* (*Khandha*,
*Upādānakkhanda*, *Āyatana*, *Dhātu*, *Ariyasacca*), "The End of chapter 9" (p238) — and the eight pages
of colour charts that close the PDF (pp. 239–247: "Mental Process", "Picture of Whole Life", the
"… and its conditions" wheels for each citta of the eye-door process, "Javana", "Sobhana cetasika - 25",
"Akusala cetasika - 14") into `ocr/fundamental-2/p231.md`–`p247.md`. Tesseract (300 dpi) for the English,
the page image (zoomed where small) for every word of Pāli and every chart label.

**Every page of Part II is now proofread.** The next run builds Part II into `data/fundamental.json`.

Notes for the build:
- Chapter 9 ends on p238; pp. 239–247 are an appendix of colour charts with no chapter head. Suggest a
  closing section (e.g. "Charts") after Chapter 9, or the page images as `img` blocks: the charts are
  in colour and only partly expressible as text. Each chart is transcribed as a fenced block (the
  wheel's neighbours above/left/right/below, then its rings "Centre / Inner ring / Middle ring / Outer
  ring", cells read clockwise from the top, blank cells left out) with a `<!-- figure … -->` note; the
  converter may keep the text, use images, or both (page images are not committed — render them from
  the PDF at build time if wanted).
- p239's "Mental Process" and "Picture of Whole Life", p243's "Javana" and p247's two titles are `###`;
  each wheel's title ("Bhavanga and its conditions") is a bold line.
- p247 has two braced groups; the brace text is a plain line followed by `<!-- braced to the four above -->`.
- p234's table has a header row ("14 *Dhamma* | Position").
- The charts' Pāli is printed without diacritics and abbreviated (Jvtdrya, Mnskra, Ekagta, S-vaca,
  S-kmta, S-ajva, Kukkca, Maccrya, Vicikcha); kept as printed.

Words marked ⟨?⟩: none.

Printed slips kept as printed (not corrected): p232 "*Sati sambojjhaṁga* - faith that is a factor of
enlightenment" ("faith" for mindfulness; comment added); p235 head "*Upādānakkhanda*" (no h) and
"cetasikas" in roman in (4); p237 "‘*Dhatu*’" (no macron) in the first line, (6) "Rūpa" in roman,
(7) "*Saddha dhātu*" (for *Sadda*), no space before the dash in (12), (14), (15); p238 "sati" in roman;
p240 the "Bhavanga and its conditions" wheel has "Bhavanga Upaccheda" in its centre; p247 "Ottapa",
"Kaya-mudita"/"Citta-mudita" (for -muduta), "Cittu-jukata".

The site was not touched (`ocr/` is not published), so check_site was not needed for this push.

Next: build Fundamental Abhidhamma Part II (pages 106–247 all in `ocr/fundamental-2/`) into the site.

## 2026-11-13 — Fundamental Abhidhamma Part II pp. 206–230 proofread

Proofread PDF pages 206–230 of `ocr-sources/fundamental-2.pdf` (book pp. 101–125 of Part II: the end of
Chapter 8 — Attainment of Path and Fruition with its process figure, Reviewing Knowledge, Analysis of
Emancipation, of Individuals and of Attainment (*Nirodha-samāpatti*), "The End of Chapter 8" — and
Chapter 9 *Samuccayasaṅgaha* from its opening through 1. *Akusalasaṅgaha* (the 9 categories, their
tables), 2. *Missaka saṁgaha* (*Hetu*, *Jhānaṁga*, *Maggaṁga*, 22 *Indriyas*, *Bala*, *Adhipati*,
*Āhāra*, the Special note, "*Dhamma* and Categories" and its table) and 3. *Bodhipakkhiya Saṁgaha* up to
*Satipaṭṭhāna*) into `ocr/fundamental-2/p206.md`–`p230.md`. Tesseract (300 dpi) for the English, the
page image for every word of Pāli and every table.

Note for the build: the book goes on past Chapter 8 — p211 opens a **Chapter 9** (`## CHAPTER 9`,
`## SAMUCCAYASAṄGAHA`, `## Compendium of Category`: three `##` lines to join into one title, as for
Chapters 7 and 8). Its `sangaha_ch` is 7 (the Saṅgaha's own chapter 7 is the Samuccaya), as Chapter 8
here follows the Saṅgaha's chapter 9 — the converter should map by content, not by number.

Conventions added this run (the converter should follow them):
- p206 and p207: the process rows are fenced blocks (as p114); p206's figure (circled S and N with
  arrows) is drawn in the block, with a figure comment.
- p210 ends Chapter 8 with "**The End of Chapter 8**" and a rule comment; the rest of the page is blank.
- Centred heads (bold or bold italic: "4 Compendiums", "1. *Akusalasaṅgaha*", "*Āsava*", "6 *Hetu*"…)
  are `###`; left-set bold heads ("**Reviewing Knowledge**", "**Special note**", "**Categories**") are
  bold lines; left-set bold italic run-in heads are written as on earlier pages.
- Two-column "*Term* - gloss" lists are one item per line, the column wraps joined (p216
  "*Sīlabbataparāmā*/*sa*" joined to *Sīlabbataparāmāsa*).
- Tables without a header row (p211, p214, p221, p225) have an empty header `| | |` (as p107);
  "altogether" rows are plain rows with a note that the sum is boxed.
- p220: the 14 × 9 table of *akusala cetasikas* marks cells with asterisks, written escaped `\*` —
  the converter must unescape them. p229's table marks cells with `/`, as printed.
- The book writes *saṁgaha*/*Saṁgha*/*-aṁga* with ṁ (m with dot above) in this chapter and
  *saṅgaha* in others; kept as printed page by page.

Words marked ⟨?⟩: none.

Printed slips kept as printed (not corrected): p207 "the contemplation of soul" (for non-soul) and
‘The contemplation of signlessness” (single opening quote); p208 "(appaṇihita)" in roman, "*vīcikicchā*"
(long ī, so throughout this chapter), heading "*Sakadāgāmi*" but text "*Sakadāgāmī*"; p209 "*Arūppa*"
and p210 "*Anāgāmi*"; p212 "*Nīvaraṇa*" (long ī, so throughout), "*Thina*" (no macron); p213 "*Bhavogha*
-Craving" (no space); p215 "*Sīlabbatupāda*" (for -*upādāna*), "*Byāpada*" in the list but "*Byāpāda*"
in the text; p216 "-Doubt", "-Ignorance" (no space); p218 "*Kilesa* mean", "*Upādana*" (short a);
p219 "*Kileasa*" and "*Ahirika* and *Anottappa* belong to 1, as *Saṁyojana*" (the table on p220 puts
them under *Kilesa*); p220 "*Ahīrika*" (long ī) in the table, list items (3)–(7) in roman; p224
"*Jīvindriya*" for the tongue faculty (for *Jivhindriya*; checked zoomed); p226 "sati" in roman,
"(*paṭisandh*i)" with a roman i; p227 "*Kabalīkāra*" (l, not ḷ); p228 "*Vīcāra*" (long ī), "Āhāra" in
roman; p229 the table heads "*Jhānañga*", "*Maggañga*" (ñ for ṅ; checked zoomed) and the "3 *Viratī*"
row marked under *Jhānañga* (p228 says *Maggaṁga*), noted in a comment.

The site was not touched (`ocr/` is not published), so check_site was not needed for this push.

Next: Fundamental Abhidhamma Part II, PDF page 231 (17 pages left, 231–247).

## 2026-11-13 — Fundamental Abhidhamma Part II pp. 181–205 proofread

Proofread PDF pages 181–205 of `ocr-sources/fundamental-2.pdf` (book pp. 76–100 of Part II: the rest of
Chapter 7 — conditions 4/5 *Anantara*/*Samanantara* to 24 *Avigata* with their *paccaya*/*paccayuppanna*,
the Analysis of Concepts (*atthapaññatti*, *saddapaññatti*), "The End of Chapter 7" — and Chapter 8
*Kammaṭṭhāna Saṅgaha* from its opening through *Samatha* (the 40 objects, temperaments, stages, signs,
*jhāna* attainment, *Abhiññā*) and *Vipassanā* (7 purifications, 10 insight knowledges, characteristics,
contemplations, emancipations) up to "*Vipassanā* Practice in brief" (4)) into
`ocr/fundamental-2/p181.md`–`p205.md`. Tesseract (300 dpi) for the English, the page image for every
word of Pāli and every table.

Conventions added this run (the converter should follow them):
- The condition heads continue as `####` (p181 "#### 4. *Anantara*/5. *Samanantarapaccayo*" covers two
  conditions in one head, as printed). Centred sub-heads "(A) **Mind to mind-matter**", "(B) ***Purejāta
  Nissaya***" are written as one bold line "**(A) …**", as p180 did; a second centred line under them
  ("**Mind to mind**") is its own bold line.
- p189 ends Chapter 7 with "**The End of Chapter 7**" and a rule comment (the rule is "=======").
- p190 opens `## CHAPTER 8`, `## *KAMMAṬṬHĀNA SAṄGAHA*` (italic small capitals), `## Meditation Subject`:
  three `##` lines to join into one chapter title, as for Chapter 7.
- p200: a short dashed rule closes the *Samatha* part (HTML comment) before "### (2) *Vipassanā*".
- Left-set bold italic heads (*Asubha*, *Sīlavisuddhi*…) are `***…***` lines; left-set bold heads
  ("**10 *Kasiṇa***", "**3 Contemplations**") are bold lines; centred heads are `###`.
- Two-column "*Term* - gloss" lists and "Attention (*āvajjana*)," lists are one item per line.
- Tables: p195, p196, p198, p204 as Markdown tables; p198 has merged cells (blank cells, with a note).
- Ordinals "1st", "2nd" (superscript in the book) are plain, as in earlier pages.

Words marked ⟨?⟩: none.

Printed slips kept as printed (not corrected): p183 "*appamañña*s" (no long ā; checked zoomed) and
"51 following *Javana citta*s" (capital J); p185 "(1)89" (no space); p186 "*Paccayupana*" (one p, one n),
"*vedanā, and*" with "and" in italics; p188 "*rupa*" (no macron), "kasina", "samatha" in roman;
p190 "*Pāḷi*" (ḷ); p194 "Appanā:" in roman; p195 the table has "8 M.O." where the text says 10 objects
(note added); p197 "*1Ānāpāna*" (no space); p198 "M.O." and "R.S." are defined in a note but no figure
using them is printed; p199 "*adiṭṭhāna*" (for *adhiṭṭhāna*; checked zoomed) and "*viññaṇa*" once (no
macron on the second a; checked zoomed); p200 "*Vipassanā nāṇa*" (n for ñ; checked zoomed); p201
"*Ñāṇadassa-visuddhi*" (for *-dassana-*); p202 "This knowledge overcome doubt"; p204 "*Suññānupassanā*";
p205 "fearlessness (*bhaya*)" (the sense wants fearfulness; printed so).

The site was not touched (`ocr/` is not published), so check_site was not needed for this push.

Next: Fundamental Abhidhamma Part II, PDF page 206 (42 pages left, 206–247).

## 2026-11-13 — Fundamental Abhidhamma Part II pp. 156–180 proofread

Proofread PDF pages 156–180 of `ocr-sources/fundamental-2.pdf` (book pp. 51–75 of Part II: the rest of
Chapter 6 — the death/rebirth processes (2)–(8), *Paṭisandhi* after *Cuti* and its table, "The end of
Chapter 6" — and Chapter 7 *Paccayasaṅgaha* from its opening through the way of *Paṭiccasamuppāda*
(the 12 factors one by one, their classification), the way of *Paṭṭhāna* (24 conditions, 9 groups,
7 ways of relation) up to *Adhipati paccayo* (B)(D)) into `ocr/fundamental-2/p156.md`–`p180.md`.
Tesseract (300 dpi) for the English, the page image for every word of Pāli and every table.

Conventions added this run (the converter should follow them):
- p161 opens `## CHAPTER 7`, `## PACCAYASAṄGAHA` (small capitals in the book), `## (Compendium of
  Causality)`: three `##` lines that the converter should join into one chapter title.
- p160 ends Chapter 6 with "**The end of Chapter 6**" and a rule comment, as p132 ended Chapter 5.
- The *paccayā* sub-heads ("*Avijjāpaccayā Saṅkhārā*" etc., left-set bold italic) are `***…***` lines;
  left-set bold heads ("**3 Periods**", "**(1) Mind to mind**") are bold lines; centred heads are `###`.
- From p179 the condition heads ("1. *Hetu paccayo*", "2. *Ārammaṇa paccayo*"…) are `####` (the first
  use of `####` in this book), each followed by its centred bold subtitle ("**Mind to mind and matter**").
- Numbered lists of conditions (p174–178) are written one item per line ("1. *Anantara*"); the book
  restarts or continues the numbers as printed (p174–175: 1–4, 5–8, 9–15 in one list).
- p173: the 9 groups with their numbers set as two columns are lines "(1) *Ārammaṇa* 8", with a note.
- Tables with headers spanning two columns (p160, p164, p171) have a note; merged cells are blank in the
  following rows.

Words marked ⟨?⟩: none.

Printed slips kept as printed (not corrected): p160 table "*Rūpa cuti* 4" (there are 5 *rūpa vipāka*s;
printed so); p163 "*viññāṅa*" twice (ṅ for ṇ, checked zoomed); p164 "*Sanṭīraṇa*" (ṭ, checked zoomed);
p162 "occuring"; p165 "*Phassa*;" (semicolon); p168 "*viñññāṇa*" (three ñ, checked zoomed); p172
"*Anantarapaccyao*"; p173 (17) no full stop after "object"; p174 and p178 "*Vipayutta*" (one p); p179
heading "*Paccayupanna*" and p180 "*Paccayupanna*:" (one p); p180 "*and*" set in italics; p162 "c*etanā*"
and "c*etanā*s" with a roman c (kept so).

The site was not touched (`ocr/` is not published), so check_site was not needed for this push.

Next: Fundamental Abhidhamma Part II, PDF page 181 (67 pages left, 181–247).

## 2026-11-13 — Fundamental Abhidhamma Part II pp. 131–155 proofread

Proofread PDF pages 131–155 of `ocr-sources/fundamental-2.pdf` (book pp. 26–50 of Part II: the end of
Chapter 5 — *Arahatta Phalaṭṭha*, *Tihetuka* in other planes, the tables of being/plane/*vīthicitta* —
and Chapter 6 *Vīthimutta*: the *Bhūmi* section, the *Paṭisandhi* section, the *Kamma* section, the
conditions of death and the death-and-rebirth processes up to the eye-door and mind-door diagrams)
into `ocr/fundamental-2/p131.md`–`p155.md`. As before, tesseract (300 dpi) for the English and the page
image for every word of Pāli and every table.

Conventions added this run (the converter should follow them):
- p132 ends Chapter 5 with "**The end of Chapter 5**" and a short dashed rule (kept as an HTML comment).
- p133 opens `## CHAPTER 6` / `## *VĪTHIMUTTA*: PASSIVE MENTAL PROCESS`; the section heads
  "(1) *BHŪMI* SECTION", "(2) *Paṭisandhi* Section", "(3) *KAMMA* SECTION" are `###` as printed (the
  book sets the first and third in small capitals).
- Left-set bold sub-heads that are not centred ("**3 *Kāya kamma***", "**1st *Jhāna* planes (3)**",
  "**(1) *Kāmāvacara kusala kamma***") are bold lines, not `###`.
- Lists set as "*Term* - gloss" in two columns are written as Markdown lists in one line each.
- Two small sums with an underlined last figure (p143, p146) are fenced blocks with a ‾ line and a note.
- Tables with a header spanning two columns (p137, p140) have the header in the first of the two and
  an HTML-comment note; merged cells are left blank in the following rows (p132, p147, with a note).
- p155: the death/rebirth process lines with J¹… as Unicode superscripts, as in Chapter 5.

Words marked ⟨?⟩: none.

Printed slips kept as printed (not corrected): p135 "*Viññāṇñcāyatana*" (an "a" missing; checked zoomed);
p137 table header "12 Indidivuals"; p140 the 3rd *arūpa vipāka* is said to be the *paṭisandhi* of the
"*ākāsānañcāyatana* plane" (the sense wants *ākiñcaññāyatana* — printed so, checked zoomed); p142 item 1
has no closing parenthesis; p147 the first "*patisandhi*" has no dot under the t (checked zoomed);
p148 "*parittāsubhā*"/"*appamāṇāsubhā*" (long ā, against p135 "*Parittasubhā*"/"*Appamāṇasubhā*");
p149 "*Upathambhaka*" in the list but p150 "*Upatthambhaka*"; p150 "*āsana kamma*" (one n);
p133 "*kāmasugati*" lower-case at the start of a sentence; p136 items 2–4 have "hetu", "paṭisandhi",
"hetus" in roman type.

The site was not touched (`ocr/` is not published), so check_site was not needed for this push.

Next: Fundamental Abhidhamma Part II, PDF page 156 (92 pages left, 156–247).

## 2026-11-13 — Fundamental Abhidhamma Part II pp. 106–130 proofread

Proofread PDF pages 106–130 of `ocr-sources/fundamental-2.pdf` (the Part II title page and book pp. 2–25
of Part II: Chapter 5 *Vīthi*, from the opening to the *Anāgāmi Phalaṭṭha* list) into
`ocr/fundamental-2/p106.md`–`p130.md`. The PDF's text layer is unusable (most glyphs lost), so each
page was read from `tesseract` at 300 dpi and, above all, from the page image itself: tesseract drops
every diacritic, so all Pāli was written from the image (the print is clean and its diacritics are clear).

Conventions (for this book; the converter should follow them):
- The comment line is `<!-- page NNN, book page X -->`; Part II restarts its page numbers (PDF p107 =
  book p. 2). p106 is the Part II title page (`# FUNDAMENTAL ABHIDHAMMA` / `# PART II`).
- `## CHAPTER 5` and `## *VĪTHI*: MENTAL PROCESS` are the chapter title; the centred bold heads are `###`.
- Bold run-in heads ("**Citta-vīthi**:", "**Manifestation:**") are `**…**`; the book sets them bold
  (often bold italic), so bold marks them and italics inside them are not kept.
- `<!-- cont -->` on p110 and p112 (the page begins mid-paragraph).
- Ruled tables are Markdown tables (a `<br>` where a cell has two lines; merged cells left blank in the
  following rows, p122); tables with spanning cells or columns that a Markdown table cannot hold (p109
  objects/doors, p111 objects per door, p116 the 15 processes) and the process diagrams (p114, p118,
  p121) are fenced blocks keeping the columns, the diagrams with an `<!-- figure: … -->` note of what
  the arrows and arcs show. J¹… superscripts kept as Unicode superscripts; "5th" for 5<sup>th</sup>.
- Ditto marks in the p108 table written “ as printed. "\#" (p125–126) is the book's own bullet sign.

Words marked ⟨?⟩: none.

Printed slips kept as printed (not corrected): p108 "*Arūpāvavara vipāka*s"; p109 "*Jīvha*-dvāra/-viññāṇa"
(the book's spelling); p112 "*sanṭīraṇa*" (ṭ); p113 "*Saṃpaṭicchana*"; p119 "**Kāma-jāvana:**"; p124 table:
the second row reads "4 *Kāma-kriya* with pleasant feeling" (the sense wants neutral feeling — printed so);
p125 "*nirodha-samapatti*" (no macrons); p127 "*viññāāṇa citta*s" (double ā, checked zoomed); p130 "1 *vicikiccha*".

For the owner: Part II opens with its own "Chapter 5 *Vīthi*: Mental Process" in a new, longer wording,
while the site's Part I (from the Part I PDF) already ends with a chapter 5 *Vīthi*. When Part II is
built, the two will need a decision (keep both, labelled by part, is the reading the build run should take
unless the owner says otherwise).

The site was not touched (`ocr/` is not published), so check_site was not needed for this push.

Next: Fundamental Abhidhamma Part II, PDF page 131 (117 pages left, 131–247).

## 2026-11-13 — Mendis built into the site (ready to merge)

Built *The Abhidhamma in Practice* from the 80 proofread pages:
- `scripts/mendis/convert.py` reads `ocr/mendis/p*.md` and writes `data/mendis.json` (9 parts: Front
  matter/Preface with the imprint, Introduction, The Cittas, The Cetasikas, Rūpa, Planes of Existence,
  Causality, Nibbāna, About the Author). Cover, title page and contents page (p001, p002, p004) left out.
  `<!-- cont -->` joins a page's first paragraph or verse to the page before, except where a list goes on
  over the page ((b)/(c)/(d) items on p028, p037, p038; "iii." on p027; the ditto table on p034), which
  stay blocks of their own. The ditto table (p034) is a two-column table; verse as lines; the two
  footnotes (p048, p057) under the paragraphs that cite them (the p057 note belongs to the last
  paragraph of Planes of Existence, before the CAUSALITY heading).
- Checked: every word of the proofread pages is in the JSON and nothing else (word counts compared; the
  only extras are the `###` headings, which the comparison left out of the pages).
- Saṅgaha map: The Cittas → I, The Cetasikas → II, Rūpa → VI, Planes of Existence → V, Causality → VIII.
- `data/library.json` (before Fundamental), shelf "Start here" in `scripts/build_home.py` (first), README
  section and status/table rows. Mendis was not among the README's "To come" rows, so none was removed.
- `python3 scripts/build.py mendis`, `build_map.py`, `build_home.py`; `audit_format.py mendis`: 6
  "broken", all list items ending "; and" before the next lettered item (the book's layout, not faults);
  `check_site.py`: **134 pages × 3 widths, 0 problems**.

Words marked ⟨?⟩ (shown on the site as marked): p007 "were not⟨?⟩ uttered"; p037 "(c)⟨?⟩ to clench the
teeth".

For the owner: merge `autopilot` into `main` to publish Mendis. The "Start here" shelf's blurb still says
"by teachers from Myanmar"; it was left as it is.

Next: Fundamental Abhidhamma Part II, PDF page 106 (`ocr-sources/fundamental-2.pdf`, pp. 106–247).

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
