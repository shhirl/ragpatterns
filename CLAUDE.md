# Seven RAGs, one shelf

**New here? Read `HANDOFF.md` first.** It is the decision log and the starting point for building; this file is the day-to-day rules.

Static site comparing seven RAG design patterns on Shirley's own bookshelf (Goodreads export, Kindle highlights, recommendations CSV, a few photos) and six fixed questions. Two pages plus a plan, no build step. The build plan with diagrams is `docs/plan.html`; the three-year context is `LADDERS.md`.

## Constraints — keep it this simple

- **Plain HTML + inline CSS/JS. No framework, no npm, no external requests** (no CDN fonts, no analytics) unless the owner asks.
- One self-contained file per page. Styles and the explorer data live inside that page.
- Palette and voice match the owner's other sites (fixmybanana, shhirl.com): cream background, serif body, small uppercase sans labels, numbered "§" sections, honest version tags.

## Pages

- `index.html` — thesis + explorer. All explorer content is in the `<script>` at the bottom: `P` (patterns, with pipeline `stages` that drive the SVG), `Q` (six questions), `REF` (reference answers), `R[pattern][Qn]` (trace rows, answer, verdict `good|partial|wrong`, why), `COST`. Edit data there; do not fork the renderer.
- `how-its-built.html` — the method page. Section 7 (`#versions`) is the source of truth for what is measured vs. predicted. When a version ships, update it there **and** the `v0` kicker/footer on both pages.
- `docs/plan.html` — the build plan. Published as a Claude artifact too; republish after edits.

## Data and privacy rules (non-negotiable)

- The curated exports (`corpus/*.csv`, `corpus/*.txt`) are git-ignored and never committed. Photos, `graph.json`, `eval/questions.yaml` and `eval/results/*.csv` are committed.
- Goodreads "Private Notes" are never ingested. Recommenders are initials only; the initials-to-people mapping stays on Shirley's machine.
- Highlights only, never full text. The ledger (dates, ratings, pages) is stored as rows and queried by a tool; it is never embedded.

## Honesty rule

v0 traces are predictions, not measurements. Keep the "predicted" labels (kicker, `.note` under the explorer, legend and footnote under the scorecard) until a live pipeline has produced the numbers. Never present an estimate as a result. When a cell becomes measured, say so with the date.

## Working on it

- Shirley's rule: present the plan, let her decide, then build. Do not start files off an open brief.
- Preview: `python3 -m http.server 8787`, or the `static` launch config. The browser caches aggressively; add `?v=N` when checking a CSS change.
- Check desktop and ~375px mobile: the explorer collapses to one column under 700px; the pipeline diagram and the scorecard scroll horizontally inside their own containers.
- Deep links: `#compare/<patternId>/<Qn>` selects a cell on load.
