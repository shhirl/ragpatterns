# Seven RAGs, one shelf

**New here? Read `HANDOFF.md` first.** It is the decision log and the starting point for building; this file is the day-to-day rules.

Static site comparing seven RAG design patterns on Shirley's own bookshelf (Goodreads export, Kindle highlights, recommendations CSV, a few photos) and six fixed questions. Two pages plus a plan, no build step. The build plan with diagrams is `docs/plan.html`; the three-year context is `LADDERS.md`.

## Constraints — keep it this simple

- **Plain HTML + inline CSS/JS. No framework, no npm, no external requests** (no CDN fonts, no analytics) unless the owner asks.
- One self-contained file per page. Styles and the explorer data live inside that page.
- Palette and voice match the owner's other sites (fixmybanana, shhirl.com): cream background with a faint ruled-paper line, serif body, small uppercase sans labels, monospace for numbers and verdicts, numbered "§" sections, honest version tags.
- Design direction chosen 9 Sep 2026: **option A "the shelf" with option C's explorer** (see `docs/design-options/`). Text sits in `.wrap` (900px); the explorer and scorecard sit in `.wide` (1180px). Verdicts are squares (`.vc`), not dots, everywhere.
- **Pipeline diagrams are drawn by `diagram()` from each pattern's `stages`.** Icons are chosen by stage kind (`k`) and by keywords in the label: `in` = open circle with "?", `out` = filled circle, `doc` = stacked pages, `store` = cylinder unless the label contains "graph" (linked nodes), "sql" (table) or "image" (frame); `model` = rect with a glyph for "embedding", "rerank", "router", "entity"/"linking", "planner", else a star. Stores are tinted with the pattern colour. A new stage label that matches none of these gets the default icon; add a keyword rather than a special case. Connectors animate slowly; `prefers-reduced-motion` turns that off.
- **The shelf hero is a chart.** `shelf()` in `index.html` builds the seven spines from `R` and `COST`: height = predicted score out of 6 (correct 1, partial ½), width = a flex share proportional to cost vs naive, so the seven fill the shelf. Do not hard-code spine sizes; change the data and the shelf follows. Same for the mini spines in the footer of `index.html`; the ones in `how-its-built.html` are static copies of the same numbers.

## Service (v1+)

- `service/ingest/` builds the ledger: `goodreads.py` (export → rows, Private Notes dropped), `ratings.py` (Open Library crowd average, cached), `notion.py` (Notion export → ratings, tags, notes, copied passages), `match.py` (Notion ↔ Goodreads), `build_db.py` → `service/data/library.sqlite`. Rebuild with `python3 service/ingest/build_db.py` after any export changes; it prints the numbers the method page publishes.
- `service/answer.py` is the one interface; `service/retrievers/sql.py` is the read-only SQL tool; `service/patterns/` holds the seven patterns as they arrive. `sql_forced.py` is a diagnostic, not a pattern: no model call, labelled as such in every result.
- `service/workbench.py` is the local page for seeing and interacting with what is built (`python3 service/workbench.py`, or the `workbench` launch config, then http://localhost:8790). Local only; it must never be deployed or linked from the pages.
- `eval/questions.yaml` is the question set with reference answers; Shirley approves it before anything is measured. The reasoning behind the set's size and shape is `docs/evals-guide.md` (two tiers: nine diagnostics now, ~36 scored questions at v5, paired differences with CIs).
- Python 3.9 on this machine: no `X | None` annotations, no `match` statements.

## Pages

- `index.html` — thesis + explorer. All explorer content is in the `<script>` at the bottom: `P` (patterns, with pipeline `stages` that drive the SVG), `Q` (six questions), `REF` (reference answers), `R[pattern][Qn]` (trace rows, answer, verdict `good|partial|wrong`, why), `COST`. Edit data there; do not fork the renderer.
- `how-its-built.html` — the method page. Section 7 (`#versions`) is the source of truth for what is measured vs. predicted. When a version ships, update it there **and** the `v0` kicker/footer on both pages.
- `docs/plan.html` — the build plan. Published as a Claude artifact too; republish after edits. The whole `docs/` folder is hidden on the live site by `_redirects` (`/docs/* → /`); it is for the repo.

## Names (use exactly these)

- **ragpatterns.com** — the site. Appears only as the nav brand.
- **Seven RAGs, one shelf** — the project and the main page. Every link back to the main page says "← Seven RAGs, one shelf".
- **How it's built** — the method page, in the nav, in body links, in the footer, in its own kicker and `<title>`. Never "the method page", "the comparison", "case study".
- **The Librarian** — reserved for the live ask box that ships at v5. Not used on the pages until then.

## Data and privacy rules (non-negotiable)

- The curated exports (`corpus/*.csv`, `corpus/*.txt`, `corpus/notion/`) are git-ignored and never committed. Shirley's ratings, tags and notes come from her Notion "Book Reviews" database via its Markdown & CSV export; Goodreads is the ledger. Photos, `graph.json`, `eval/questions.yaml` and `eval/results/*.csv` are committed.
- Goodreads "Private Notes" are never ingested. Recommenders are initials only; the initials-to-people mapping stays on Shirley's machine.
- Highlights only, never full text. The ledger (dates, ratings, pages) is stored as rows and queried by a tool; it is never embedded.

## Honesty rule

- **Dates on the pages are month and year only** (Shirley's instruction, 9 Sep 2026): "v0, September 2026", never a day. Repo docs and commits keep exact dates. When a cell becomes measured, date it on the pages as month and year.

v0 traces are predictions, not measurements. Keep the "predicted" labels (kicker, `.note` under the explorer, legend and footnote under the scorecard) until a live pipeline has produced the numbers. Never present an estimate as a result. When a cell becomes measured, say so with the month and year.

## Working on it

- Shirley's rule: present the plan, let her decide, then build. Do not start files off an open brief.
- **Git:** repo is https://github.com/shhirl/ragpatterns (public). **One open PR at a time when `HANDOFF.md` is touched:** every session appends to §9, so two open PRs conflict; wait for the merge, or branch the next PR from the open branch. `main` is protected; every change is a branch + pull request with the template checklist, and Shirley merges. An AI session never merges, never pushes to main, never force-pushes. Merging deploys ragpatterns.com through Cloudflare Pages; see `DEPLOY.md`.
- Preview: `python3 -m http.server 8787`, or the `static` launch config. The browser caches aggressively; add `?v=N` when checking a CSS change.
- Check desktop and ~375px mobile: the explorer collapses to one column under 700px; the pipeline diagram and the scorecard scroll horizontally inside their own containers.
- Deep links: `#compare/<patternId>/<Qn>` selects a cell on load.
