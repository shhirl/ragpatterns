# HANDOFF — Seven RAGs, one shelf

Written 9 September 2026 at the end of the planning session with Shirley. This is the document the next AI reads first. It says what the project is, what has been decided (and what was rejected, and why), what exists on disk, what does not exist yet, and exactly where to start building. Nothing in this folder should be deleted.

---

## 0. Read in this order

1. `HANDOFF.md` — this file. The decision log and the starting point.
2. `docs/plan.html` — the build plan with diagrams: corpus, ingest, data model, graph schema, question set, retriever matrix, evals, versions, deployment, repo layout, stack, open decisions, first-session steps. Open it in a browser. Also published as a Claude artifact: https://claude.ai/code/artifact/40f88c01-0b8f-45bb-bfad-0b26a17d813f
3. `CLAUDE.md` — the working rules for anyone editing this repo (style, privacy, honesty).
4. `index.html` and `how-its-built.html` — the v0 site as it stands. The explorer's content is the JavaScript data object at the bottom of `index.html`.
5. `LADDERS.md` — the wider three-year plan (books ladder and airline-disruption ladder). This project is rung A-2024, "the Librarian". Read it for context, not for instructions; where it and this file disagree, this file wins because it is newer.

---

## 1. What the project is

A one-project website (Miessler style: one site, one idea) that demonstrates Shirley can *think* about RAG. The thesis: RAG systems break on the retrieval pattern, not the model. The proof: the seven common RAG patterns (naive, retrieve-and-rerank, multimodal, graph, hybrid, agentic router, multi-agent) run on **one real corpus** and **the same six questions**, so the only variable between columns is the architecture. A scorecard shows nobody wins every column and the cheapest pattern wins the easy one.

The corpus is Shirley's own bookshelf: her Goodreads export, her Kindle highlights, a short hand-written list of who recommended what, and a few photographed pages. She chose it because she can grade every answer in a second, the data exports in an afternoon, and "it invented a book I never read" is the most legible RAG failure there is.

Audience: hiring managers and peers for AI product / AI engineering roles, and readers of her LinkedIn. The site has to be honest to the point of publishing bad numbers; that is her house style (see fixmybanana.com/how-its-built).

Working name: **Seven RAGs, one shelf**. Intended domain: **ragpatterns.com** (not bought yet, see §7).

---

## 2. Status: v0, predicted, nothing has run

| exists | does not exist |
|---|---|
| Two static pages, fully written for the books corpus, verified in a browser at desktop and 375px mobile, no console errors | Any code that runs a pipeline |
| All 42 explorer cells (7 patterns × 6 questions) traced *by prediction*, labelled as predictions | Any measurement, latency, cost, or verdict from a real run |
| Six question *shapes* with reference-answer shapes | The real book titles in Q1, Q3, Q5 (bracketed placeholders until the export is inspected) |
| The build plan with diagrams | The corpus files in the repo (Shirley has them; they go in `corpus/`, git-ignored) |
| `.gitignore`, `README.md`, `CLAUDE.md`, `DEPLOY.md`, `.claude/launch.json`, the GitHub repo with protected `main`, the domain | Nothing on the hosting side. Everything from here is v1 work. |

---

## 3. Decision log

Each entry: what was decided, what was rejected, why. Dated 9 Sep 2026 unless noted.

### 3.1 The site's shape

- **Decided (9 Sep 2026, evening):** design direction **A "the shelf"**, blended with **C "the grid"** for the explorer. Shirley chose A ("I like the visual, the hovering") on condition the spine heights mean something, and took from C the wider, clearer explorer and question layout. Result: the spines are a chart (height = predicted score out of 6, width = cost vs naive, built from `R` and `COST` by `shelf()`), the explorer and scorecard sit in a 1180px `.wide` column with C's full-width tab strip, big rectangular pipeline diagram, question list with square verdict markers, trace as a headed table, boxed answer card, and a solid-square scorecard. Rejected: B "reading room" (dark; tables read worse), D "marginalia" (sidenotes collapse on mobile). Mockups kept in `docs/design-options/`.

- **Decided:** one site per project, Miessler format. Thesis headline, numbered "§" argument sections, the comparison in the middle, a "how it's built" method page written as a lab notebook with versions. Footer "Built by Shirley" (the "AI-assisted" tag was removed on Shirley's instruction, 9 Sep 2026 evening; the method page still says the site is AI-assisted in prose). The method link in the footer is named after the system: "The Librarian: how it's built", the name from `LADDERS.md`. Inspirations Shirley gave: danielmiessler.com/projects, thevulnequation.ai, oursafe.ai, ispalantirtrustworthy.io.
- **Decided:** plain HTML, inline CSS and JS, no build step, no external requests, one self-contained file per page. This is Shirley's house rule from shhirl.com and it is not negotiable.
- **Decided:** house palette and voice: cream `#fbfaf7`, ink `#1a1a1a`, accent `#1f5e4e`, serif body (Iowan Old Style / Palatino), small uppercase sans labels, `§01`-style section numbers, honest version kickers ("v0 · predicted, not yet measured").
- **Rejected:** a framework, a build step, hosted fonts, analytics. Reason: anyone should be able to clone the repo and open the file.

### 3.2 One use case for all seven patterns

- **Decided:** run all seven patterns on one corpus and one fixed question set. Reason: comparing patterns on different demos measures the demos. This was Shirley's own instinct at kickoff and it is the core of the site.
- **Rejected:** seven separate demos, one per pattern (the infographic's approach).

### 3.3 Which corpus — the history matters

1. **First draft (rejected by Shirley):** a handstand-coaching notebook, 34 documents I would have written, chosen for her personal-trainer background. Built fully as v0, then rejected: "I don't like using the handstand coach's notebook again." Also weaker on inspection: fabricated, and no structured-numbers failure mode.
2. **Assessed alternatives** (all rejected): a fictional product team's docs (would have to fabricate everything; can't grade); airline-disruption public rules (strong, but it is the *other* ladder's 2024 rung — see LADDERS.md; could become a second corpus on this site much later); travel journal (privacy-heavy, weak relationships); cooking log (fine for RAG, weak future rungs; rejected in the earlier ladders session); her own notes / meeting transcripts (can't publish work data); music or podcast log (no highlights, weak relationships).
3. **Decided: her own bookshelf.** Criteria used: (a) she can grade every answer; (b) the data has the failure modes that separate the seven patterns; (c) failures are legible to a stranger; (d) real, publishable, fast to populate; (e) has a future (2025 acquisition agent, 2026 shelf scanner in LADDERS.md). Books won on all five.
- **Decided:** retire the handstand version entirely; keep the explorer renderer (it is data-driven). Open decision 9.1 in `docs/plan.html` still formally asks Shirley to confirm this; my recommendation and the current state of the site both assume retire.

### 3.4 What goes into the corpus and what stays out

- **In:** Goodreads export CSV (title, author, additional authors, ISBN13, my rating, average rating, number of pages, original publication year, date read, date added, bookshelves, exclusive shelf, my review, read count). Kindle highlights (`My Clippings.txt`: highlight text, book, location/page, date, her notes). A hand-written `recommendations.csv` with columns `title, by, where, date` where `by` is initials. 5 to 10 photos: covers (Open Library by ISBN), a few photographed pages, one shelf.
- **Out, permanently:** Goodreads "Private Notes" (never ingested). Full text of any book (highlights only: short quotations with attribution are publishable, books are not). The mapping from recommender initials to real people (stays on her machine). Any title Shirley removes from the CSV before ingest (the site says the corpus is curated). Public reviews from Goodreads or elsewhere (copyright and noise; the crowd's opinion is represented by the Average Rating column, which is enough for the "why two stars" question). Bookmarks and clippings under 20 characters.
- **In the repo:** photos, the extracted `graph.json`, `eval/questions.yaml`, every `eval/results/*.csv` including bad ones.
- **Not in the repo, ever:** the curated exports (`corpus/*.csv`, `corpus/*.txt`), `.env`, the initials mapping. `.gitignore` already covers these.

### 3.5 The ledger is rows, never embedded

- **Decided:** dates, ratings, page counts and shelves stay in SQLite and are queried by a SQL tool. They are not chunked or embedded.
- **Why:** embedding a ledger is how a system invents a book. Keeping it as rows makes the "numbers" question an honest test of "does this pattern have a tool or not", which is the cleanest split on the scorecard.
- **Consequence:** the SQL tool is only reachable through the agentic router and multi-agent patterns. The first five patterns, as drawn in the infographic, have no tool call. That is deliberate and the site says so.

### 3.6 Six questions, not five

- **Decided:** six fixed questions, one per failure mode plus one control. Q2 (a filter over the ledger) was added relative to the handstand version because "numbers, dates, filters" is the most common real-world RAG failure.
- Q1 quote lookup (control). Q2 "What did I read in 2024, rated five stars, under 300 pages?" Q3 "Why did I give [book] two stars when everyone else loved it?" Q4 "Which of my books argue with each other?" Q5 photographed page: "Which book is this, and what did I highlight near it?" Q6 two-week holiday list from the to-read shelf with four constraints.
- **Rejected:** 50 random questions (averages out the diagnostics; more questions come at v5 once pipelines run).
- **Reference answers** are written before any pipeline runs. Their *shapes* are on the site now; the real titles get fixed after the export is inspected.

### 3.7 Graph

- **Decided:** fixed schema. Nodes: Book, Author, Person (recommender), Theme. Edges from the files: WROTE, RECOMMENDED(date), READ_AFTER. Edges extracted by Claude from highlights and reviews: ABOUT (theme), MENTIONS / ARGUES_WITH (book→book or book→author). Book nodes carry my_rating, date_read, pages as properties. NetworkX in memory, loaded from committed `graph.json`.
- **Rejected:** a hand-built graph (hides the real Graph RAG failure mode, which is the extractor missing an edge). A graph database (a fourth thing to run for under a thousand nodes).

### 3.8 Evaluation

- **Decided:** Shirley grades every answer correct / partial / wrong against the reference, by hand, before any metric. Automatic checks: invented books (any title in an answer that is not in `books`), retrieval hit, consistency over 5 runs, model calls, latency, token cost. 6 × 7 × 5 = 210 answers per version. A second reader grades a sample before v5 and the agreement rate is published as the ceiling.
- **Rejected:** an LLM judge (needs its own validation set; at 210 answers reading is cheaper).
- **Rule:** the eval calls the same `answer()` function the site's demo box will call.

### 3.9 v0 ships as labelled predictions

- **Decided:** publish v0 with every cell labelled "predicted" and replace cells with measurements version by version, with dates.
- **Rejected:** waiting for live pipelines before publishing anything.
- **Rule (non-negotiable):** never present an estimate as a measurement. The "predicted" labels (kicker, the `.note` under the explorer, the scorecard legend and footnote) stay until a real run replaces the cell.

### 3.10 Stack

- **Decided:** Python service on Railway (Cloudflare in front), same setup as fixmybanana. SQLite for the ledger and the vectors (one file). Voyage text embeddings; Voyage multimodal at v3. A local cross-encoder reranker (no API call, so its cost is milliseconds). NetworkX graph from JSON. Claude Opus 5 with adaptive thinking for generation, one prompt template for every pattern. Claude Haiku 4.5 for the router. Claude Opus 5 at ingest for graph extraction and image captions, once.
- **Rejected:** an LLM reranker (second LLM in the loop muddies attribution); a vector database; different models per pattern (then you are comparing models).
- **One interface for everything:** `answer(question, pattern, image) -> {answer, context, route, calls, ms, usage}`. See `docs/plan.html` §4.

### 3.11 Versions

- v0 (done, 9 Sep 2026): site rewritten for books, predictions.
- v1: ingest both exports, SQLite, embed highlights, cross-encoder, SQL tool; naive and rerank live; fix the real titles; run 2 × 6 × 5; first measured cells with dates. Q2 gets a real answer through a forced SQL path so the number exists early.
- v2: graph and hybrid; `graph.json` published.
- v3: multimodal (photos).
- v4: router and multi-agent; the cost column becomes real.
- v5: all 210 answers graded, consistency and invented-book counts, second reader, ten more questions, live "ask the librarian" box with trace panel, "predicted" labels removed.

### 3.12 Site structure across Shirley's projects, and the domain

- **Decided (direction):** www.shhirl.com becomes her personal home with a Miessler-style `/projects` index; each project lives at its own subdomain or domain and links back. The existing `/ai-pm-workflows/` product pages stay where they are (Stan redirects there). This is a separate piece of work in the shhirl.com repo, not this one.
- **Recommended, not yet done:** buy ragpatterns.com. It is parked at Cloudflare Registrar checkout under her account at $10.46/year, registrant prefilled, auto-renew on, **nothing charged**. The tab was left open. Only Shirley completes the purchase; an AI must not click "Continue to pay" without her explicit yes in chat. Fallback if she doesn't buy: `rag.shhirl.com` as a Cloudflare Pages custom domain.

---

## 4. Working rules for the builder

1. **Plan first, then Shirley decides, then build.** Present a short plan and the decisions she needs to make, and stop. Do not start files off an open brief. She said this explicitly.
2. **Honesty.** Predicted stays labelled predicted. Bad numbers get published. Dates on everything that becomes measured.
3. **Privacy.** See §3.4. If in doubt, leave it out of the repo.
4. **Style.** Match `CLAUDE.md`. Edit the explorer's data object; do not fork the renderer.
5. **Git.** Repo https://github.com/shhirl/ragpatterns (public, created 9 Sep 2026). `main` is protected: pull requests only, no force push, rules apply to admins. Every change is a branch + PR with the template checklist; Shirley merges; an AI never merges. Merging deploys ragpatterns.com through Cloudflare Pages (`DEPLOY.md`). The v1 service will follow the same rule.
6. **Verify before declaring done.** For the pages: open in a browser at desktop and 375px, no console errors, no horizontal page scroll (the browser preview caches hard; add `?v=N`). For the service: the eval runner runs end to end on the real corpus.

---

## 5. Data format notes for ingest

**Goodreads export** (`goodreads_library_export.csv`, from Goodreads → My Books → Import/Export). Columns as exported: `Book Id, Title, Author, Author l-f, Additional Authors, ISBN, ISBN13, My Rating, Average Rating, Publisher, Binding, Number of Pages, Year Published, Original Publication Year, Date Read, Date Added, Bookshelves, Bookshelves with positions, Exclusive Shelf, My Review, Spoiler, Private Notes, Read Count, Owned Copies`. Gotchas: ISBN fields come wrapped like `="0123456789"`; dates are `YYYY/MM/DD`; `Date Read` is often empty for older books; `Exclusive Shelf` is one of `read`, `currently-reading`, `to-read`; an abandoned book is usually a custom shelf (ask Shirley what hers is called, or accept five titles by name). Drop `Private Notes` at parse time, do not just skip it later.

**Kindle highlights** (`My Clippings.txt` from the device's `documents/` folder). Blocks separated by a line of ten `=`. Block: line 1 `Title (Author)`, line 2 `- Your Highlight on page N | Location A-B | Added on Weekday, D Month YYYY HH:MM:SS` (or `Your Note`, `Your Bookmark`), blank line, text. Gotchas: titles vary from Goodreads titles (subtitles, series names); match by fuzzy title + author, report the match rate; duplicates when a highlight is extended; keep notes attached to the highlight they follow.

**Recommendations** (`recommendations.csv`, written by Shirley): `title, by, where, date`. `by` is initials. Twenty rows is plenty.

**Photos:** `corpus/photos/` committed. Captions generated once at ingest and stored in `images.caption`.

---

## 6. Where to start (first build session)

1. Goodreads, Notion export and photos are in `corpus/` (see §9); the ledger builds with `python3 service/ingest/build_db.py`. Ask for the Kindle `My Clippings.txt` (expected week of 14 Sep 2026), `recommendations.csv`, and the photo-crop yes.
2. Done for Goodreads and Notion (numbers in §9). Remaining: Kindle highlights match rate once the file arrives.
3. `eval/questions.yaml` is drafted with real titles for Q2 and Q3. Shirley approves; Q1 gets its phrase from the Kindle file.
4. Build `service/ingest/` (goodreads.py, kindle.py, recommendations.py, photos.py) → `service/data/library.sqlite`.
5. Build retrievers `vector.py`, `rerank.py`, `sql.py`; patterns `naive.py`, `rerank.py`; `service/answer.py` (the one interface); `eval/run.py` and `eval/questions.yaml`.
6. Run 2 patterns × 6 questions × 5 runs. Shirley grades. Replace the naive and rerank rows in `index.html` with real traces, dated, and update `how-its-built.html#versions`. That is v1.

Repo layout to create is in `docs/plan.html` §7.

---

## 7. Open decisions (Shirley's, not the builder's)

1. Confirm: retire the handstand version entirely (recommended) vs keep it as a second corpus later.
2. Recommendations: hand-written CSV (recommended) vs Goodreads shelf tags like `rec-ab`.
3. Abandoned books: a Goodreads shelf (name?) or five titles she names.
4. Which low-rated-but-loved book for Q3; which pages she is happy to photograph for Q5. After the export is inspected.
5. ~~Domain: buy ragpatterns.com (recommended) or use rag.shhirl.com.~~ Bought, 9 Sep 2026.

---

## 8. File map

```
rag_website/
  HANDOFF.md            this file — read first
  docs/plan.html        the build plan with diagrams (also a Claude artifact)
  CLAUDE.md             working rules: style, privacy, honesty, preview, deep links
  README.md             public-facing summary and run instructions
  DEPLOY.md             GitHub + Cloudflare Pages setup, PR rule, rollback, what changes at v1
  .github/PULL_REQUEST_TEMPLATE.md   the PR checklist
  docs/design-options/  the four design mockups and index; A + C was chosen
  docs/evals-guide.md   eval-set research and the two-tier decision (reference for future projects)
  LADDERS.md            the three-year plan (books + airline ladders); this project is rung A-2024
  index.html            v0 site: thesis, corpus, explorer (data object at bottom), scorecard, decision guide
  how-its-built.html    v0 method page; #versions is the source of truth for measured vs predicted
  .gitignore            corpus exports, service data (except graph.json), .env
  .claude/launch.json   `static` preview server on :8787
```

Memory for the Claude sessions on this machine lives outside the repo (`~/.claude/projects/-Users-shirley-Developer-fable-5-1-rag-website/memory/`) and points here.

---

## 9. Session 3 (9 Sep 2026, evening): domain bought, design and hosting pending Shirley's decision

- **ragpatterns.com is bought** (Cloudflare Registrar). Open decision 7.5 is closed.
- **Design options** are in `docs/design-options/` with an `index.html` describing them: A the shelf (spines as hero and nav), B reading room (dark, amber), C the grid (Swiss, scorecard as hero), D marginalia (Tufte sidenotes, highlighter accent). All four keep the house rules and the "predicted" labels. Shirley picks one (or a blend); the chosen direction is then applied to `index.html` and `how-its-built.html` without forking the explorer renderer. Unchosen files stay as the record.
- **Hosting decided and set up:** public GitHub repo `shhirl/ragpatterns`, `main` protected, v0 pushed as the first commit. Cloudflare Pages is Shirley's one manual step (`DEPLOY.md`). Railway only from v1, for the service, at `api.ragpatterns.com`.
- **Design decided:** A + C blend, see §3.1. Applied to both pages on branch `design/shelf`, opened as the first pull request. Unchosen mockups stay in `docs/design-options/`.
- **Diagrams (later the same evening):** Shirley asked for option D's inked-icon naive diagram across all seven pipelines. `diagram()` now draws marginalia-style icons (see `CLAUDE.md`), numbered stages, mono labels, italic asides, a figure caption, and a slow ink-flow animation; stacked columns (hybrid, router, multi-agent) label to the right so a five-way fan-out stays short.
- **Docs added:** `DEPLOY.md`, `.github/PULL_REQUEST_TEMPLATE.md`; `CLAUDE.md`, `README.md` and this file updated.
- **Live (9 Sep 2026, ~18:20 UK):** PR #1 merged by Shirley; Cloudflare Pages project `ragpatterns` created from the repo; ragpatterns.com and www both serve the site. Go-live is the merge of PR #1. `DEPLOY.md` has the details and the clean-URL note.
- **Shelf fills the width (later):** spines now grow with `flex: var(--w) 1 0`, so width stays proportional to cost but the seven books span the whole shelf. Footer: "AI-assisted" removed, method link renamed "The Librarian: how it's built".
- **Naming settled (later still):** three names, one job each: ragpatterns.com (site, nav brand only), Seven RAGs, one shelf (project + main page, all back-links), How it's built (method page, everywhere). "The Librarian" is reserved for the v5 ask box and removed from the footer. `/docs/*` is hidden on the live site via `_redirects` (302 to `/`); the plan and mockups stay in the repo. The tool stays inside the main page's explorer (Shirley confirmed).
- **Dates and no Ops (later):** Shirley first asked for a 2025 frame, then reverted: 2026 stays, but the pages never show an exact day. Footers and the versions list now read "September 2026" / "Sep 2026" (rule in `CLAUDE.md`). The "Ops" subsection at the end of the stack section on the method page was removed; the PR flow is documented in `DEPLOY.md` instead.
- **Corpus status (9 Sep 2026, late evening):** Shirley dropped `corpus/goodreads_library_export.csv` (479 rows, git-ignored) and five photos into `corpus/photos/` (IMG_2386/2389/2390/2391.JPG, IMG_8279.jpeg; 3–4 MB each, not yet committed).
  - **Kindle highlights: still to do.** No `My Clippings.txt` yet; she did not have time to plug the Kindle in. v1 ingest can start on the ledger, the SQL tool and Q2; the vector index, naive and rerank, and Q1/Q3 need the highlights. Ask for the file at the start of the next session, or offer the read.amazon.com/notebook route if she reads in the app.
  - **The export has no `Average Rating` column** (header checked: `Book Id, Title, Author, Author l-f, Additional Authors, ISBN, ISBN13, My Rating, Publisher, Binding, Number of Pages, Year Published, Original Publication Year, Date Read, Date Added, Bookshelves, Bookshelves with positions, Exclusive Shelf, My Review, Spoiler, Private Notes, Read Count, Owned Copies`). §5 assumed it. Q3 ("why two stars when everyone else loved it") needs the crowd average from somewhere else: fetch it once at ingest by ISBN (Open Library has `ratings_average`) and store it in `books.avg_rating`, and say so on the method page. Decide in the first build session.
  - Photos must be downscaled (~1600 px long edge, ~300 KB) before they are committed; the originals stay out of git. `.DS_Store` added to `.gitignore`.
- **What the export actually contains (9 Sep 2026, late):** 479 rows: 205 read, 250 to-read, 24 currently reading. 372 have an ISBN. **13 rated, 0 reviewed** (Shirley: "I personally never rated books on Goodreads; I know which books I love, in my head"). 136 have a date read: 2018·3, 2019·12, 2020·12, 2021·39, 2022·36, 2023·12, 2024·15, 2025·4, 2026·3. 85 read books are under 300 pages. One book on a `dnf` shelf (In Ascension); `own-but-not-read` has 3.
  - **Consequence for the questions.** Q2 as written ("read in 2024, five stars, under 300 pages") returns nothing, and Q3 ("why two stars when everyone loved it") has no review to quote. Decision taken with Shirley: her ratings and one-line verdicts become a **hand-written file `corpus/verdicts.csv`** (`title, rating, why`; template in `corpus/verdicts.example.csv`), merged into the ledger at ingest by title, exactly like `recommendations.csv`. The site says so: "Goodreads holds what and when; the ratings and the one-line verdicts are mine, written for this project." 20–30 rows is enough; it must include a few 2024 reads for Q2 and at least one low rating on a crowd favourite for Q3. Q3's "review" becomes the one-line `why`.
  - **Crowd average:** fetched once from Open Library by ISBN (`service/ingest/ratings.py`, cache in `service/data/ratings_cache.json`, git-ignored). Approved by Shirley. Run completed 9 Sep 2026 ~21:10: **479 books → 350 matched by ISBN, 121 by title fallback, 8 unmatched; 412 have a crowd average, 198 with 20+ ratings, 73 with 100+.** 188 of the 205 read books have one. Two caveats for the method page: Open Library's crowd is small (the most-rated book here has 759 ratings, not Goodreads' millions), and the title fallback is unreliable (47 of the matches have a different title; some are translations of the same work, e.g. "Les années" for "The Years", but "None of This Is True" → "Untitled" and "A Storm of Swords" → "A Game of Thrones" are wrong). **Ingest rule for v1:** trust ISBN matches; keep a title-fallback match only when the normalised titles agree; otherwise store no average and count the book as "no crowd figure". Publish all three numbers.
  - **Q2 is feasible** once verdicts exist: 15 books read in 2024, 10 of them under 300 pages (Emergency Skin, A Little Luck, The Talented Mr. Ripley, Poverty by America, The Years, A Different Drummer, I Who Have Never Known Men, The Color Purple, The Dangers of Smoking in Bed, Medusa). **Q3 candidates** (read, crowd ≥ 4.2 with 100+ ratings): Howl's Moving Castle, The Fellowship of the Ring, Dune, The Song of Achilles, plus undated reads The Martian, A Thousand Splendid Suns, The Little Prince, 1984, The Help, Pride and Prejudice, The Fault in Our Stars. Shirley picks one she rates low.
  - `service/ingest/goodreads.py` parses the export and drops Private Notes at load. Note the export writes ratings as "5.0"; parse as float.
- **Theme vocabulary (10 Sep 2026):** Shirley asked for the theme list before v2. Draft of 28 themes with one-line definitions and example titles from her read shelf is committed at `service/ingest/themes.csv`; she edits it. Rule for the extractor: themes come only from this list (no free text); each ABOUT edge carries the evidence highlight; to-read books (no highlights) get themes marked `source: model-knowledge` and lower confidence; Shirley reviews the extraction table before `graph.json` is committed and corrections go in an overrides file whose count is published.
- **Verdicts come from Notion, not a CSV (10 Sep 2026).** Shirley has a Notion database **"📖 Book Reviews"** (https://app.notion.com/p/03c3f22bba3343e4bf1448369bbcedf2, data source `collection://41c251fb-ca97-451c-b2a1-fb883664e687`). Checked read-only through the Notion connector: 144 rows (132 real; the rest are template strays); her own Genres tags (about 80: Dystopia, Greek Mythology, Race, Feminism, Climate Change, Mental Health, …); Fiction? (Fiction / Non-Fiction / Fiction-Series / Mystery); First Published; Notes Status (Published 10, Notes In Progress 48). Each row is a page whose body holds her free-text notes under a template (What It's About / Thoughts / What I Liked / Didn't Like / Who Would Like It / How I Discovered It / Themes, topics / Related Books). Stray rows to drop at ingest: anything without an author (six named "Fiction", three "Book Review Ideas", one empty).
  - **Integration:** Notion is the source of her rating, her tags, her notes (the Q3 "review"), and the "Related Books" / "How I Discovered It" sections (hand-made ground truth for MENTIONS and RECOMMENDED edges). Goodreads stays the ledger (ISBN, pages, shelves, date read). Merge by normalised title + author surname; print the match rate. Her tags become `TAGGED_BY_SHIRLEY` edges, kept separate from the extractor's `ABOUT` edges so the site can compare the two.
  - **Export mechanism (offline, no API token):** in Notion, open the database → ⋯ → Export → format "Markdown & CSV", "Include subpages" on → unzip into `corpus/notion/` (git-ignored). The CSV carries the properties, one `.md` per book carries the notes. `service/ingest/notion.py` (to write) parses both. Re-export before each version.
  - **Ratings done (10 Sep 2026):** Shirley rated what she could; four stay unrated by her decision (Cold Enough for Snow, Medusa, The Dangers of Smoking in Bed, A Little Luck). 125 of 132 real rows rated; 2024: 11 of 14. **Q2 reference answer** ("read in 2024, five stars, under 300 pages", counting Lifechanging as five): **I Who Have Never Known Men (206 p), A Different Drummer (245 p), The Color Purple (287 p)**; nothing else. Unrated books can never appear, a useful trap for a pattern that guesses. **Q3 book: The Fellowship of the Ring** (her 2-Star vs 4.34 crowd); backups The Three-Body Problem and The Dark Forest (2-Star, crowd ≈ 4.4), Fahrenheit 451 and Dune Messiah (1-Star), Yellowface, The Midnight Library, Small Things Like These (2-Star).
  - `corpus/verdicts.csv` and its template are withdrawn. The theme list in `service/ingest/themes.csv` should be reconciled with her Notion tags before v2 (Dystopia → surveillance and control, Race → race and empire, Feminism → women's lives, Climate Change → ecology and the non-human, Mental Health → mind and madness, Greek Mythology → myth retold).
- **Photos and copyright (10 Sep 2026, proposed, awaiting her yes):** shelf photo publishable; full page photos stay local and git-ignored; the site gets downscaled crops of the highlighted sentence plus a line or two, which is quotation with attribution like the Kindle highlights. Add `corpus/photos/*` to `.gitignore` and commit crops under `corpus/photos/crops/` when done.
- **Notion export parsed (10 Sep 2026, later):** Shirley exported "Book Reviews" (Markdown & CSV, subpages) into `corpus/notion/` (git-ignored). Layout: `<workspace>/Book Reviews <id>_all.csv` (all eight properties, 143 rows) + `Book Reviews/<Name> <id>.md` per page (148) + four folders that only hold attached images. `service/ingest/notion.py` parses it: **132 real reviews (rows with an author), 125 rated, 128 dated, 102 with her tags, 54 with her own notes once template boilerplate is dropped, 131 page files matched (fuzzy, because Notion strips accents and punctuation from file names).** Template boilerplate (a "What to write notes on? / Prose? / Characters? …" block identical on 16 pages) is dropped automatically. **17 pages contain passages copied from the books themselves (80 passages, e.g. Little Fires Everywhere, Such a Fun Age, Kindle-synced highlights exported as headings).** The parser separates them into `highlights`; they are treated exactly like Kindle highlights: index them, quote short excerpts with attribution, never publish a passage. `service/ingest/match.py` joins Notion to Goodreads: **132 of 132 matched** (129 exact title, 1 title+author, 2 fuzzy for Notion typos "Farenheit"/"Perjudice", 2 by alias: Fermat's Last Theorem → Fermat's Enigma, Persepolis → The Complete Persepolis). These numbers go on the method page.
- **v1 step 1–2 built (10 Sep 2026):** `service/ingest/build_db.py` builds `service/data/library.sqlite` (git-ignored): **479 books, 205 read, 125 with Shirley's rating, 54 with her notes, 369 of her tags, 80 Notion-copied passages as highlights (source 'notion'); crowd average kept for 397 (311 by ISBN, 86 by title where the titles agree), none for 82.** `service/retrievers/sql.py` is the read-only SQL tool (SELECT only, one statement, 50 rows). `service/answer.py` is the interface; `service/patterns/sql_forced.py` is the forced SQL diagnostic: **Q2 answers exactly the three reference books in 3 ms with zero model calls.** That is the first real cell, and it is labelled "forced SQL path, not a pattern" wherever it appears. `eval/questions.yaml` drafts the six questions with real titles for Q2 and Q3 and marks Q1/Q4/Q5/Q6 pending (Kindle next week, graph at v2, photos at v3, recommendations.csv); **Shirley approves it before v1 measures anything.** Kindle file expected the week of 14 Sep.
- **Questions grew to nine (10 Sep 2026):** Shirley added Q7 "favourite books about race" (rating filter joined to a theme), Q8 "themes I like most" (aggregate over her tags), Q9 "top themes each year" (aggregate grouped by year). References computed from the ledger and written into `eval/questions.yaml`. Two honest findings baked into them: her Notion tags are genres more than themes (Fantasy, Classics), so the extracted-theme answer at v2 is the deeper one and the site shows both; and tag coverage collapses after 2022 (2023: 4 of 12 books tagged, 2024: 2 of 15), so a correct Q9 answer must say the later years are unknown. **The site still says six questions; a follow-up PR after #11 adds Q7–Q9 to `Q` and `R` in `index.html` (21 predicted traces), the copy, the stats and the method page.** Why six originally: one per failure mode plus a control; fifty random questions were rejected because averages hide which pattern fails on what; the three additions each add a failure mode.
- **Eval design researched and written up (10 Sep 2026):** `docs/evals-guide.md` records what Anthropic, Hamel Husain, Eugene Yan and the golden-dataset guides say about eval set size, and the decision it leads to: **two tiers**: the nine hand-graded diagnostic questions (the site's argument) and, at v5, a scored set of about four questions per failure mode (~36), same questions for every pattern, five runs, reported as paired differences with confidence intervals; hand-grade once per pattern (~250 readings), code checks the repeats. This replaces the plan's "ten more questions at v5". Also saved as the cross-project skill `~/.claude/skills/eval-design` so future projects start from it.
- **Site at nine questions (10 Sep 2026):** `index.html` `Q`, `REF` and `R` carry Q7–Q9 with 21 predicted traces; Q3 names The Fellowship of the Ring; `REF` Q2/Q3 are the real references; the shelf score is out of 9; copy says nine on both pages, README and the method page's question table. Predicted verdicts for the new columns: Q7 partial for naive/rerank/multimodal (right theme, cannot see the rating), good for graph/hybrid/agentic/multiagent; Q8 and Q9 wrong for the three text-only patterns, partial for graph/hybrid (can count, wrong vocabulary, no coverage caveat), good for agentic/multiagent (agentic Q9 depends on the coverage column reaching the prompt).
- **Local workbench (10 Sep 2026, PR #13):** Shirley asked how to see and interact with the system. `service/workbench.py` (stdlib http.server, port 8790, launch config `workbench`) shows the nine questions as buttons, runs the ledger ones (Q2, Q7, Q8, Q9) through `answer()` with the forced SQL path, has a free SQL box against the read-only tool, and prints the full result. `sql_forced.QUERIES` covers Q2, Q7, Q8, Q9; Q9's query carries a coverage column and the formatter says "too few tagged books to rank" for years under five tagged books. Local only.
- **Live panel on the main site (10 Sep 2026, PR #15):** Shirley wanted the workbench on the main site, not local. Decision: the **service** goes live now (planned for v1 anyway) with a **public copy of the ledger** (`service/data/library.public.sqlite`, committed: books, tags, recommendations; **no notes, no copied passages, no Notion ids**), a stdlib WSGI API (`service/api.py`: `/health`, `/questions`, `POST /ask {qid}`; CORS only for the site and localhost), gunicorn on Railway at `api.ragpatterns.com` (files: `requirements.txt`, `Procfile`, `railway.json`, `.python-version`; steps in `DEPLOY.md`), and an **"Ask the ledger, live" panel** in §03 of `index.html` under the explorer: the nine questions as buttons, the four ledger ones call the service and show route, calls, ms, the query and the answer, labelled "forced SQL path, no model call"; the panel says "service not reachable" until Railway is connected. **Free SQL stays local** (the workbench), never public. Railway connection is Shirley's login step, like Cloudflare was.
- **Title and kicker (10 Sep 2026):** Shirley found "Seven RAGs, one shelf. The pattern is the product." unclear and "predicted, not yet measured" like jargon. New h1: **"RAG patterns, side by side. Tested on my own bookshelf."**; site name **"RAG patterns, side by side"** in titles and back-links; kicker **"v0 · every result is a prediction until a version measures it"**. Applied to both pages, the workbench, README, CLAUDE.md and the GitHub description. "Seven RAGs, one shelf" survives only as the working name in older notes.
- **Placement of the live panel (10 Sep 2026):** Shirley asked whether "Ask the ledger" should be its own page or higher up. Decision: stays under the explorer in §03 for now; a nav item "ask" and a hero line "ask the ledger ↓" point to it. As patterns go live, the panel dissolves into the explorer: each cell gets a "run it live" button and the live answer appears beside the prediction. A separate /ask page only when it does things the explorer cannot (own questions, history, comparisons).
- **Next session starts at §6** (first build session: exports into `corpus/`, inspect, real titles, v1), after Shirley has merged the design PR and connected Pages.
