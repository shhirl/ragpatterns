# Project ladders: books and disruption

Handoff document. Written 9 Sep 2026 after a planning session with Shirley.
Purpose: let the next session pick up either ladder and begin without re-deriving the decisions.

## The frame

Three yearly "bars" for AI engineering, each ladder has one project per bar:

- 2024, RAG and chatbots: vector DB and embeddings, chunking and retrieval pipelines, a custom chatbot app.
- 2025, agents: function and tool calling, agent loops, memory.
- 2026, production: multi-agent workflows, multimodal (vision, audio, text), context engineering, token and latency budgets, evals. "Demos are easy, real systems are not."

Each ladder shares one corpus, so each year builds on the last:
2024 answers questions about the data, 2025 acts on it, 2026 runs it in production.

The seven-RAG-patterns essay (naive, rerank, multimodal, graph, hybrid, agentic router, multi-agent) is the argument that
the 2024 rung makes: the pattern, not the model, is what breaks. The 2024 rung must therefore include at least one
question type that naive RAG visibly fails on (numbers, tables, filters) and one that needs relationships (graph).

## What already exists

- `/Users/shirley/Developer/fable_5.1/rag_website`: "Seven RAGs, one coach", v0. Handstand-coaching corpus, hand-traced
  worked examples, two pages, plain HTML. Read `CLAUDE.md` and `how-its-built.html#versions` first.
- House conventions: one site per project (Miessler style), cream palette, serif body, § sections, a "how it's built"
  page written as a lab notebook with versions, hand-labelled evals, trade-off tables, honest numbers.
- Honesty rule: never present an estimate as a measurement. Label worked examples until a pipeline produced the number.
- Shirley's working rule: present the plan, let her decide, then build. Do not start files off an open brief.

## Decisions made

- Personal ladder: **books**. Chosen over lifting and wine because the corpus is hers, she can populate it from an
  export in an afternoon, she can grade every answer, and "it invented a book I never read" is the most legible failure.
- Enterprise ladder: **airline disruption**, built on Lufthansa's public developer API and published rules.
  Never branded as Lufthansa. Chosen over contact centre, loyalty, operations, transfer navigator, and baggage
  because it has the most public data, exact answers to grade against (EU261), and a 2026 problem that is
  genuinely multi-agent and multimodal.

## Decisions still open (ask Shirley before building)

- Whether the handstand v0 is swapped for the books corpus (one domain, cleaner story) or kept as the standalone
  essay with books as the live app. Recommendation: swap.
- Books data sources she actually has: Kindle highlights, Goodreads or StoryGraph CSV, notes app.
- Highlights and metadata only, or book full text too. Recommendation: highlights only (smaller, personal, no
  copyright problem on a public site).
- Shared backend across the three rungs, or three separate sites. Recommendation: one backend, one site per rung.
- Whether she works at Lufthansa and could ever use internal data. Assume public only.
- Which ladder to build first. They are independent.

---

## Ladder A: Books

Corpus: Shirley's reading life. Reading log (title, author, dates, rating, pages, status incl. abandoned),
highlights and notes, cover and page photos. Book metadata from Open Library (free) or Google Books (better).

### A-2024: The Librarian (RAG, seven patterns)

**What it is.** A chatbot over her library, with a side panel that shows the trace: which pattern answered,
what was retrieved, what reranking removed. A toggle forces a pattern so a visitor can ask the same question
through naive vs router and watch naive invent a book.

**Fixed question set (five, one per failure mode), used for the scorecard on every version:**
1. "Where did I read that line about ..." (semantic over highlights; naive is fine, rerank helps).
2. "Which of my books cite or argue with each other?" (relationships; graph only).
3. "What did I read in 2024, rated five stars, under 300 pages?" (structured filter; tool call; naive hallucinates).
4. "What should I read next after X?" (needs history + themes + dislikes; router combines retrievers).
5. A question about a photographed page or cover (multimodal).

**Build.**
- Ingest: export -> normalise -> chunk. Highlights chunked per highlight with book metadata prepended.
  Log rows kept as rows in SQLite, not embedded. Photos captioned once at ingest.
- Retrievers: vector (Voyage embeddings), reranker (local cross-encoder), SQL tool for the log, NetworkX graph
  of author/book/theme/"cites" edges, image captions in the vector index.
- Seven pipelines behind one interface, selected by a router (Haiku 4.5) or forced by the toggle.
  Generation with Claude Opus 5.
- Site: reuse the v0 explorer renderer. Replace hand-traced cells with measured ones version by version.

**Evals.** Shirley grades each answer good/partial/wrong. Hard check: any title returned that is not in the log
is a hallucination, counted automatically. Cost and latency per question per pattern.

**Done when.** All five questions answered by all seven pipelines with measured numbers on the site,
worked-example labels removed.

### A-2025: The Acquisition Agent (tools, loop, memory)

**What it is.** "Get me this book." The agent checks whether she owns it (librarian as a tool), checks the public
library catalogue, and if no copy, searches used sellers under her price ceiling. It stops and asks before
anything is bought. It never spends money itself.

**Build.**
- Tools: `library_lookup` (the librarian's SQL), `catalogue_search` (public library, scrape if no API),
  `seller_search` (AbeBooks and eBay have APIs; Bookshop.org and local shops mostly do not), `ask_user`.
- Loop: plan -> call -> observe -> decide stop or continue, with a hard cap on tool calls and a stop rule.
- Memory, two layers, documented as a design argument: long-term preferences (paperback, price cap, no
  ex-library stamps, editions she dislikes) and per-task state (sellers tried, candidates rejected and why).
- Modes: "report only" (what it would buy) for the public site, "confirm to buy" for her own use.
- Site: a replayable run showing every tool call, the branch taken, and the moment it stopped to ask.

**Evals.** Did it find a copy she would accept. Tool calls per task. Did it ever act without asking (must be zero).
Cost per task.

**Done when.** Ten real requests replayed on the site with those numbers.

### A-2026: The Shelf Scanner (production, multimodal, multi-agent)

**What it is.** Photograph a bookshelf, get a verified inventory. Confirmed books flow into the librarian's
corpus; a found book cancels any pending acquisition search for it.

**Pipeline of agents, with an orchestrator:**
1. Spine detector: boxes around each spine.
2. Reader: text on each spine (sideways, partial, glared).
3. Matcher: partial text -> candidate books via Open Library or Google Books.
4. Context checker: against what she owns and the other spines on the shelf (a shelf of Tolstoy makes an
   unclear spine more likely Tolstoy).
5. Decider: add automatically above a confidence threshold, otherwise queue for a yes/no tap.

**Production concerns to publish.** Cost per shelf photo (budget, and what was cut to meet it). Latency while
she is standing there. Context engineering: what each agent is shown and what is withheld. Failure list: shelves
in bad light, thin spines, series volumes.

**Evals.** Hand-labelled shelves. Precision, recall, invented books, per shelf. A confusion table on the site.
Error propagation: show one scanner false match becoming a wrong "you already own this" answer downstream.

**Done when.** Five of her real shelves scanned, numbers published, review queue working.

---

## Ladder B: Airline disruption (Lufthansa public data)

Corpus: Lufthansa conditions of carriage, fare rules, baggage rules, EU261 regulation text and the EU's
passenger-rights guidance, Lufthansa Open API (developer.lufthansa.com: schedules, flight status, airports,
aircraft, lounges). Framing on every page: "built on Lufthansa's public API and published policies", not Lufthansa.

### B-2024: Passenger Rights Assistant (RAG, seven patterns)

**What it is.** A chatbot that answers "what am I owed and what can I do" from the published rules.

**Fixed question set:**
1. "My flight of 1,800 km was delayed 3h40, what compensation?" (distance band x delay table; naive gets the
   amount wrong).
2. "Can I change this fare class, and what does it cost?" (conditional fare rules; graph).
3. "Which lounges can I use with my status on this route?" (structured lookup; tool).
4. "Cancelled due to strike, what are my rights?" (cause-dependent; router must combine regulation + policy).
5. A question about a photographed delay notice or boarding pass (multimodal).

**Build.** Same architecture as A-2024, same explorer renderer. Tables (compensation bands, baggage allowances,
lounge access) kept as tables and queried, not embedded. Graph of fare class -> rule -> exception.

**Evals.** Regulation gives exact answers; grade against them. Any compensation amount not in the table is
counted as a hallucination automatically.

### B-2025: Disruption Agent (tools, loop, memory)

**What it is.** Given a booking, the agent watches the flight, and on delay or cancellation works out the
entitlement, finds rebooking options from the schedule feed, drafts the claim, and stops before submitting.

**Build.**
- Tools: `flight_status`, `schedule_search` (Lufthansa API), `rules_lookup` (B-2024 as a tool),
  `draft_claim`, `ask_user`.
- Loop branches on delay length and cause; re-plans on every status change.
- Memory: booking and traveller profile (long-term), this disruption's timeline (per-task).
- Public site runs in replay on recorded disruptions; never submits anything.

**Evals.** Correct entitlement on recorded cases. Rebooking found when one existed. Zero unrequested submissions.

### B-2026: Irregular Operations Desk (production, multimodal, multi-agent)

**What it is.** The airline side. One cancelled flight, all its passengers. An orchestrator runs: a status
watcher, a rights assessor, a rebooker, a message writer, with a human approving batches.

**Multimodal.** Photographed boarding passes, departure boards, hotel and meal receipts for expense claims.

**Production concerns to publish.** Cost per disrupted passenger. Latency while the flight is boarding.
Context engineering per agent. What breaks: same passenger on two records, partial cancellations, cause
reclassified mid-event.

**Evals.** Recorded or synthesised cancellations with known correct outcomes per passenger; accuracy,
cost, and time to first passenger message.

---

## Planned stack (both ladders)

Python service on Railway. Voyage embeddings. Local cross-encoder reranker. SQLite for tables.
NetworkX for graphs. Claude Opus 5 for generation, Haiku 4.5 for routing and cheap agents.
Static sites: plain HTML, inline CSS and JS, no build step, deployed via Cloudflare Pages from GitHub.

## First steps for the next session

1. Ask Shirley which ladder and which rung to start with, and settle the open decisions above.
2. For A-2024: get the export files, inspect them, propose the five questions with real examples from her data,
   then build ingest before anything else.
3. For B-2024: register for the Lufthansa Open API, pull the rules documents, confirm the compensation table
   values, then propose the five questions.

---

## Update, 9 Sep 2026 (later the same day)

- **Decided:** the handstand v0 is retired. The site is now "Seven RAGs, one shelf" on the books corpus (A-2024, the Librarian). `index.html` and `how-its-built.html` were rewritten; the explorer renderer was kept.
- **Decided:** data sources are the Goodreads export and Kindle highlights (`My Clippings.txt`), plus a hand-written `recommendations.csv` and a few photos. Highlights only, never full text. Private Notes never ingested. Recommenders as initials.
- **Decided:** six questions, not five. Q2 (a filter over the ledger) was added because "numbers" is the most common real-world RAG failure and the ledger-as-rows design makes it an honest test.
- **Written:** the full build plan with diagrams is `docs/plan.html` (also published as a Claude artifact). Its section 9 lists the decisions still open: retire vs keep handstand as a second corpus later, CSV vs shelf tags for recommendations, which books for Q3/Q5, the domain (ragpatterns.com parked at Cloudflare checkout, $10.46/yr), how abandoned books are tracked.
- **Next:** first session steps are in `docs/plan.html` section 10. Step 1 is copying the two exports into `corpus/` and inspecting them.
