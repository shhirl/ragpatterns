# HANDOFF — RAG patterns, side by side

> **Newest first:** the latest session is **§10 (10 Sep 2026)** — v1 is built and wired but
> **nothing has been measured**. If you are picking this up, read §10 before anything else:
> it has the state, the decisions, what is verified, and the exact commands that finish v1.
> Then come back and read from §0 for the project's history and rules.
> (The working name "Seven RAGs, one shelf" was replaced on 10 Sep 2026.)

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

---

## 10. Session 4 (10 Sep 2026, afternoon): v1 built, not yet measured

**Read this section first if you are the next AI.** It says exactly what was built, what was
decided and why, what is verified, what is not, and the one command that finishes v1.

### 10.1 Where v1 stopped, precisely

Shirley's scope for this session (her words): *"Skip graph/hybrid/router/multi-agent for now.
Build vector + rerank retrievers, implement just the naive and rerank patterns (2 patterns,
9 questions, ~5 runs each), grade, ship dated traces. Ask the ledger panel shows real data for
two patterns + SQL forced path. Clean, minimal v1. Graph/hybrid come at v2."*

The session ended early, before the measurement run, because Shirley ran low on credits and asked
for records instead. **Everything is built and wired. Nothing has been measured.**

| state | what |
|---|---|
| done and verified | corpus cleaning, ingest rebuild, vector retriever, reranker, naive and rerank patterns, `answer()` wiring, eval runner, grading sheet, replay exporter, live-panel rewrite, workbench routes, API replay endpoint, method-page ingest numbers |
| verified end to end | **the pilot ran and all four answers succeeded** — see §10.1a. An earlier smoke test had died on a DNS failure, not a code fault. |
| not started | the full measurement run, grading, the site's `R` traces, the version table |

**The vector index is complete: 775 of 775 chunks embedded** (finished at the end of the session,
10 Sep 2026). 385 highlight chunks and 390 note chunks over 55 books, `voyage-4`, 1024 dimensions,
47,698 tokens billed against Voyage's free allowance, so it cost nothing. The build is resumable
and incremental, so re-running it is a no-op unless the ingest changed.

### 10.1a The pilot ran, and it changed three things (10 Sep 2026, 16:39)

Shirley ran `eval/run.py --runs 1 --q Q1,Q2` herself at the end of the session. **The pipeline
works end to end.** Results are in `eval/results/v1-2026-09-10.{csv,json}` — four answers, all
four succeeded, ungraded.

| | Q1 (control) | Q2 (ledger) |
|---|---|---|
| naive | **correct.** Such a Fun Age top-ranked at 0.560, quoted exactly with attribution | **abstained.** Said plainly there are no dates, ratings or page counts in the context |
| rerank | **correct.** Same answer; the cross-encoder pushed the right chunk from 0.560 to **0.922** | **abstained**, same reasoning |

Neither pattern named a book outside its context. Neither invented a title. The reranker did
visibly what it exists to do: it turned a 0.56/0.43 margin into 0.92/0.36.

**Three findings, all of which need a decision before anything is published:**

1. **The cost estimate was five times too high.** $0.0374 for four answers, about **$0.009 an
   answer**. The full 90-answer set is **roughly $0.85**, not the $4–5 estimated from the model's
   list price. Adaptive thinking produced far less output than assumed. v1 is comfortably
   affordable on the $6.79 balance.

2. **The measurement contradicts the v0 prediction, and the prompt may be why.** `index.html`
   predicts naive/Q2 as *"wrong, and invented … a confident list of five or six titles with
   dates"*. What actually happened is a clean, honest abstention. That is a genuinely interesting
   result — but the shared system prompt in `service/patterns/_generate.py` contains the line
   *"The context contains no ratings, dates, page counts or shelf information. If the question
   needs those, say that they are not in the context rather than estimating them."* **That
   sentence arguably hands the model the abstention**, so the run may be measuring the prompt
   rather than the pattern. This is Shirley's call, and it must be settled before the Q2 cell is
   published:
   - *Option A (recommended):* remove that sentence, keep only the general "use only the context
     / never name a book that is not in the context" rules, and re-run. That tests whether the
     pattern invents, which is what the site claims to measure.
   - *Option B:* keep it and **say so on the page** — publish the prompt, and frame the cell as
     "a well-prompted naive pipeline refuses; the failure the diagram predicts is a prompt away".
   - Either way the prompt is identical for both patterns, so the naive-vs-rerank comparison is
     unaffected. It is the "does RAG invent?" claim that is at stake.

3. **The published latency is contaminated.** rerank/Q2 reports 53,390 ms, of which **49,747 ms
   was `retrieve_ms` waiting on Voyage's 3-requests-per-minute free-tier limit**, not work. Do
   **not** publish `ms` as latency. Either report `gen_ms` + `rerank_ms` and state that embedding
   is throttled, or get the rate limit lifted and re-run. Honest figures from this pilot:
   generation 2.8–4.1 s, rerank 0.35–0.58 s, retrieval ~0.25 s when not throttled.

Minor: the `quoted_not_on_shelf` check produced one false positive — it flagged *"The book is not
that long,"*, a phrase from Shirley's own note, as a possible invented title. The check is a
prompt for a human, not a verdict; treat it that way, or tighten it to require title-case.

### 10.2 The command that finishes v1

```bash
set -a; . ./.env; set +a           # both keys are already in .env, git-ignored, chmod 600
.venv/bin/python eval/run.py --runs 1 --q Q1,Q2      # PILOT FIRST: 4 answers, ~$0.20
```

The index is already built, so start at the pilot. Only re-run `build_index.py` if you change the
ingest, which changes the chunk hashes and re-embeds everything.

Read the pilot's cost, multiply, and **only then** decide the full run:

```bash
.venv/bin/python eval/run.py --runs 5 --all-questions      # 90 answers, est. $4-5, ~45 min
.venv/bin/python eval/grade.py  eval/results/v1-<date>.json
#   -> v1-<date>-grading.md      Shirley reads this
#   -> v1-<date>-verdicts.csv    Shirley fills the `final` column
.venv/bin/python eval/export_replay.py eval/results/v1-<date>.json
#   -> service/data/replay.json  committed; the live panel serves it
```

**Cost is now measured, not estimated:** about **$0.009 an answer**, so the full 90-answer set is
**roughly $0.85**. The balance was $6.79 on 10 Sep 2026, so the five-run set is affordable.
(The earlier $4-5 estimate was wrong by five times; see §10.1a.)

### 10.3 Decisions taken this session

- **Keys.** `ANTHROPIC_API_KEY` and `VOYAGE_API_KEY` are in `.env` (git-ignored, `chmod 600`).
  Created through the browser with Shirley present; the values were piped from the clipboard
  straight into `.env` and never printed into a transcript. The Anthropic key is scoped to the
  Default workspace and **expires 10 Oct 2026**.
- **Python.** The system Python is 3.9 and the `anthropic` 1.x SDK needs 3.10+. There is now a
  **`.venv` on pyenv's 3.10.13** holding `anthropic` and `voyageai`. Use `.venv/bin/python` for
  anything that calls a model. `service/api.py` and the ingest still run on plain `python3`, and
  the 3.9 rules in `CLAUDE.md` still apply to them. `.claude/launch.json`'s `workbench` config now
  points at the venv.
- **Models.** `voyage-4` for embeddings, `rerank-3` for the reranker, `claude-opus-5` at its
  defaults for generation. Voyage's current generation carries 200M free tokens; this index is
  ~100k tokens, so **retrieval genuinely costs nothing** and the whole bill is the Opus calls.
- **Reranker: a remote cross-encoder, not a local one.** The plan (§3.10) said a local
  cross-encoder. Shirley chose Voyage's `rerank-3` instead: the same kind of model, no
  two-gigabyte torch dependency in the Railway image. Still not an LLM, so §3.10's reason for
  rejecting an LLM reranker is intact. The method page's stack table says so.
- **The live panel replays; it does not call a model.** Shirley's choice. A live naive or rerank
  call on a public page spends her money on every stranger's click and could disagree with the
  trace printed above it. `service/data/replay.json` holds the measured run, and the panel labels
  it "measured <date>, replayed, run N of 5". The forced SQL path stays genuinely live because a
  query is free. **Consequence: the deployed service needs no model keys at all** - do not add
  `anthropic` or `voyageai` to `requirements.txt`.
- **Grading.** Shirley chose "a sheet with my proposed verdicts". `eval/grade.py` proposes a
  verdict from the automatic checks only and labels it as the AI's; she writes `final`. §3.8 is
  unchanged: **nothing reaches the site under a verdict she has not written.**
- **Query-embedding cache.** Voyage allows 3 requests a minute on an account with no payment
  method. The eval therefore caches a question's vector after its first run (`cache_query=True`
  for runs 2+). Retrieval is deterministic, so this changes no answer, only wall-clock. Run 1 of
  every cell is a real uncached call and **its latency is the one to publish**; every row carries
  `query_embedding_cached`. Shirley declined to add a card; if that changes, the cache can go.

### 10.4 What ingest found, and the mistake it caught

- **The Kindle file never arrived, and it turned out not to be needed yet.** Ten Notion pages
  already held pasted highlights, five of them raw `My Clippings.txt` dumps with separators,
  locations and timestamps. `service/ingest/notion.py` now splits them out: **273 highlights, 256
  with a real Kindle location, across 10 books**. Q1, the control question, has a real target a
  version early.
- **The mistake.** Those dumps were sitting inside `my_notes`, the field the site prints.
  **236,000 of the 434,000 characters of "her notes" were verbatim book text.** Had v1 shipped
  without this, the site would have published pages of copyrighted prose as Shirley's writing and
  fed it to the index as her voice. Notes are now 243,000 characters of her own words, and the
  book's words live in `highlights`, under the short-excerpt rule.
- The splitter handles **three different shapes** Notion produced, which is why it looks
  over-engineered: clippings with `==========` separators, clippings without them, and clippings
  where Notion made the passage the *heading* and left only the metadata in the body. All three
  are in `_classify` / `split_clippings`. If a fourth shape appears, add it there.
- `MIN_HIGHLIGHT = 20` enforces §3.4's "clippings under 20 characters are dropped".
  `dedupe_highlights` keeps the longest of any pair where one contains the other, which is what
  Kindle produces when a highlight is extended.
- **Rebuild order matters:** `build_db.py` first, then `build_index.py`. Changing the ingest
  changes the chunk hashes, which re-embeds everything.

### 10.5 Q1 has a real question now

Q1 was a bracketed placeholder. It is now:

> "Where did I read the line about leaving a movie theatre and realising it had been dark outside
> for some time?"

Answer: **Such a Fun Age** (Kiley Reid), Kindle location 2290-2293. Chosen because the phrasing is
distinctive, it sits verbatim in exactly one chunk, and nothing else on the shelf is near it - a
control question that fails only if retrieval is genuinely broken. `eval/questions.yaml` carries
it with the passage as the reference. **Shirley has still not formally approved the question set**
(HANDOFF §6.3); she should read `eval/questions.yaml` before the numbers are published.

Every question now has an `expects:` list (the books that must reach the context) which is what
`eval/run.py` scores `retrieval_hit` against. Q4, Q5, Q6 have none: they stay pending.

### 10.6 New and changed files

```
service/config.py             NEW  keys, model names, prices, the Voyage rate limiter
service/retrievers/vector.py  NEW  chunking, embedding, cosine search. Resumable, throttled
service/retrievers/rerank.py  NEW  the cross-encoder call
service/patterns/_generate.py NEW  the ONE prompt template + the ONE Claude call, shared
service/patterns/naive.py     NEW  embed -> top-4 -> generate
service/patterns/rerank.py    NEW  embed -> top-30 -> rerank -> top-4 -> generate
service/ingest/build_index.py NEW  builds service/data/index.sqlite
eval/run.py                   NEW  the runner. Calls the same answer() the site calls
eval/grade.py                 NEW  the grading sheet + proposed verdicts
eval/export_replay.py         NEW  run -> service/data/replay.json, excerpts truncated
service/ingest/notion.py      CHG  the clippings splitter (see 10.4)
service/ingest/build_db.py    CHG  highlights carry source/location/page/added_on
service/answer.py             CHG  naive and rerank registered, imported lazily
service/api.py                CHG  /ask takes {qid, pattern}; replays naive and rerank
service/workbench.py          CHG  a button per route per question; runs patterns for real
index.html                    CHG  live panel: pattern selector, verdict, cost, retrieved chunks
how-its-built.html            CHG  §4 ingest numbers and the copyright find; stack table rows
eval/questions.yaml           CHG  Q1 real; expects: on every ready question
.claude/launch.json           CHG  workbench runs on .venv/bin/python
.gitignore                    CHG  !service/data/replay.json
```

**`_generate.py` is the file that makes the comparison mean anything.** Naive and rerank differ
only in which chunks reach it. Same model, same system prompt, same context format, same
settings. If a future pattern gets its own prompt, the site's whole claim collapses - do not.

### 10.7 What the index deliberately does not contain

Only the passage text is embedded. Title and author ride along as **metadata** and are shown to
the generator; no rating, date, page count or shelf is in any chunk. This is §3.5 made concrete,
and it is why Q2, Q8 and Q9 have nothing for a similarity search to match on. It is also why Q1
can be attributed: the chunk knows its book without the title being embedded.

### 10.8 What is still unverified - do not write it into the site as fact

1. ~~The pipeline has never produced a complete answer.~~ The pilot ran; see §10.1a. But **settle
   the prompt question in §10.1a finding 2 before publishing the Q2 cell.**
2. Every trace in `index.html`'s `R` for naive and rerank is **still a v0 prediction**. The
   "predicted" labels (kicker, the `.note` under the explorer, the scorecard legend and
   footnote) **must stay** until real traces replace them. §3.9 is non-negotiable.
3. The method page's §7 version table still lists v1 as `soon`. Do not mark it done until the
   run exists and Shirley has graded it.
4. `how-its-built.html` states the ingest numbers as fact - those **are** verified, from
   `build_db.py` and from the finished index (775 chunks, 55 books; the page says 55).
5. `api.ragpatterns.com` is **still not deployed**. Railway remains Shirley's login step
   (`DEPLOY.md`). The panel fails soft and says the service is unreachable, which is correct
   behaviour, and the local API on :8791 proves the contract.

### 10.9 Verified this session

- `build_db.py` rebuilds cleanly: 479 books, 205 read, 125 rated, 369 tags, 273 highlights,
  53 books with her own notes, 397 with a crowd average. **Zero verbatim book text left in
  `my_notes`** (checked by query).
- The local API answers `/health` and serves the SQL path live: Q2 returns exactly the three
  reference books in **1-3 ms with zero model calls**.
- The rewritten live panel renders, connects, greys out naive and rerank while no replay exists,
  greys out non-ledger questions under the ledger route, and returns the correct Q2 rows on
  click. No console errors.
- Both API keys authenticate; `voyage-4`, `rerank-3` and `claude-opus-5` all answered a probe.

### 10.10 Next session, in order

1. ~~Finish the index~~ — done, 775 of 775.
2. ~~Pilot~~ — done, 10 Sep 2026. Q1 correct on both patterns, Q2 abstained on both.
   **Decide the prompt question first** (§10.1a finding 2): re-running with a more neutral prompt
   is probably the honest version of this experiment, and it costs under a dollar.
3. Check the balance, then the full run at the largest number of runs it affords.
4. `eval/grade.py`, give Shirley the sheet, wait for her `final` column.
5. Rewrite `R.naive` and `R.rerank` in `index.html` from the real traces - trace rows, answer,
   verdict, why - dated **"September 2026"**, month and year only (§ honesty rule). Update the
   `.note` under the explorer to say which rows are measured and which are still predicted.
6. `export_replay.py`, commit `service/data/replay.json`.
7. Method page §7: v1 `done`, with the date and the real numbers.
8. Update the `v0` kicker on both pages only when Shirley says the version has shipped.
9. One PR, the template checklist, Shirley merges. **Never merge, never push to main.**

## 11. Session 5 (10 Sep 2026, evening): v1 measured

**Read §10 first for what was built. This section is what happened when it ran.**

### 11.1 The run

`eval/results/v1-2026-09-10.{csv,json}` — 16 cells (naive and rerank × Q1, Q2, Q3, Q4, Q6, Q7,
Q8, Q9), five runs each, **80 answers, $1.06, about 21 minutes of wall clock**. Q5 is not in it:
it needs a photograph and this pipeline takes text, so that cell stays a prediction until v3.
The pilot of §10.1a is preserved as `v1-pilot-2026-09-10.*`.

Shirley's decisions this session, both taken before anything was spent:

- **The prompt sentence came out** (§10.1a finding 2, option A). `_generate.py` no longer tells
  the model that the context holds no ratings, dates or page counts. The general grounding rules
  stayed — a baseline with no "use only the context" instruction would be a straw man. Checked on
  Q2 before the full run: both patterns still refuse. **The refusal is the pattern's, not the
  prompt's.** The prompt is now published verbatim on the method page, so a reader can check.
- **Eight questions, five runs.** Q5 excluded for the reason above.
- **"I can't answer that" is partial** (Shirley, 10 Sep 2026). This is now the rule `grade.py`
  proposes by, and it sits **above** the retrieval-miss rule: a pattern that never retrieved the
  book and then said so has failed at retrieval and been honest about it; one that never
  retrieved it and answered anyway is the one that is wrong.

### 11.2 What the run found

1. **Nothing invented a book, in any of the 80 answers.** The v0 page predicted naive/Q2 would
   produce "a confident list of five or six titles with dates". It refuses. This is the single
   biggest correction the measurement makes to the page.
2. **naive/Q3 never retrieved the book at all** — 0 of 1, every run, both patterns. Only passage
   text is embedded (§10.7), so naming a book in the question does not fetch that book. The v0
   prediction (retrieves the admiring highlights, speculates about the ending) was wrong about
   *where* the failure is, and reranking cannot fix it: the book is not among the thirty
   candidates, so there is nothing to promote.
3. **Reranking changed no verdict.** It bought margin (Q1: a 0.13 cosine gap became a 0.57
   cross-encoder gap), better chunks (Q7: A Different Drummer from 13th; Q8: the two notes that
   state a preference rather than the ones that list themes) and one real find (Q4: the note where
   Shirley records Pullman against Narnia — an ARGUES_WITH edge without a graph). Naive and rerank
   score **identically, 5.0 of 9**.
4. **The prediction most expected to fail held.** naive/Q1 did not misattribute: 0.560 against
   0.433, all five runs.

### 11.3 The grading regimes do not match, and the page says so

A measured refusal scores half a mark under Shirley's ruling. The five predicted rows were written
assuming invention, which scores nothing. So naive and rerank sit higher on the shelf than they may
once the others are actually run. `#scorecard` states this plainly; do not quietly drop it when v2
lands — restate it, or re-grade the predictions.

### 11.4 Bugs the run exposed, all fixed here

- **Two rate limiters, one budget.** `vector.py` and `rerank.py` each held their own, each stayed
  inside three requests a minute, and together they did six. Fourteen rerank answers died on 429s.
  There is now one `config.VOYAGE` limiter and both take their turn from it. The reranker also
  **retries** a 429 now; the embedder always did.
- **`--merge`.** A refilled cell replaces its old rows and the rest of the run survives. Both
  refills used it.
- **Rerank time included the queueing.** One cell reported 58 s for a model that takes a third of
  a second. `rerank()` now returns `api_ms` and `wait_ms` separately, and only `api_ms` is
  published. Same reasoning as §10.1a finding 3 for embedding.
- **The automatic checks were wrong in four ways** and each one turned an honest cell red: the
  abstention pattern missed "can't answer", "there's nothing about X in your library context",
  "I can't break your themes down by year" and "I'd need a note"; a title the question itself
  names counted as invented (Q3); "One Day" counted in any sentence about a day; and "Shirley"
  counted because it is a Brontë novel as well as the person being addressed.
- **`grade.py` proposed `wrong` for quoting.** The quoted-phrase check fires on any short
  quotation, including the exact highlight a correct Q1 answer must quote.
- **The checks now live in `eval/checks.py`**, imported by both scripts, and `grade.py`
  **recomputes them from the recorded answers**. That is what let all of the above be fixed
  without paying to measure anything again. Keep that property.
- **`run.py` refuses to write an empty run.** `--runs 0` wrote a 0-row CSV over the measurement;
  it was recoverable only because the results were already committed. Commit results immediately.

### 11.5 What is still open

1. **Shirley has confirmed the ruling, not the grid.** The 14 cells her rule settles carry it; Q1
   (good, both) is unchanged from v0 and agrees with the measurement; **Q4 (both patterns) is
   still hers to rule on** and carries its v0 `partial`. `eval/results/v1-2026-09-10-verdicts.csv`
   has an empty `final` column. §3.8 stands.
2. `service/data/replay.json` is exported and committed, ungraded — the panel says "measured, not
   yet graded" until `final` is filled and it is re-exported.
3. ~~`api.ragpatterns.com` does not exist yet.~~ **Deployed 10 Sep 2026**, Claude driving
   Shirley's browser, she was signed in to Railway and Cloudflare already. Project `ragpatterns`,
   service `web`, `main`, auto-deploy on push; CNAME + the TXT verification record Railway now
   also wants. `https://api.ragpatterns.com/health` answers 200 with the right CORS header.
   **Until PR #19 merges the service is serving `main`, which has no `replay.json`, so only the
   SQL route answers and naive/rerank return 404.** Merging fixes that by itself: Railway
   redeploys on push to main. Full record in `DEPLOY.md`.
4. ~~`eval/questions.yaml` still has not been formally approved~~ — **approved 11 Sep 2026**, and
   the file says so. Approved *after* v1 measured and shipped, which is the wrong order: §6.3 says
   the set is approved before anything is measured. Nothing in the file changed between the run
   and the approval, so the v1 numbers stand. The set is frozen now — adding a question is allowed
   and must be dated; editing or removing one invalidates the comparison with every published
   version.
5. The kicker on both pages now reads **v1**. Shirley has not said the word "shipped"; if she
   would rather it stayed v0 until she merges, that is a one-line revert.
