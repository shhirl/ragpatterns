# Seven RAGs, one shelf

A one-project site that runs the seven common RAG design patterns (naive, retrieve-and-rerank, multimodal, graph, hybrid, agentic router, multi-agent) on **one** real knowledge base, Shirley's own bookshelf, and **the same six questions**, so the only thing that changes between columns is the architecture.

- `index.html` — the thesis, the corpus, an interactive pattern × question explorer with pipeline diagrams and graded traces, the scorecard, and a decision guide.
- `how-its-built.html` — the method: why books, trade-offs, the corpus, the question set, how answers are judged, the version plan, the stack.
- `docs/plan.html` — the build plan with diagrams (ingest, graph schema, retriever matrix, versions, deployment) and the open decisions.
- `LADDERS.md` — the wider three-year plan this project is the first rung of.

No framework, no build step, no external requests. Each page is one self-contained HTML file with its CSS and JS inline.

## Status

**v0 (9 Sep 2026): predicted traces.** The corpus is chosen (Goodreads export + Kindle highlights + a hand-written recommendations list + a few photos), the six question shapes are fixed, and all 42 pattern × question cells are traced by prediction. No pipeline has run. Every cell is labelled as a prediction; `how-its-built.html#versions` says what becomes a measurement and when.

The corpus itself (the curated exports) is not in the repo and never will be. The photos, the extracted graph, the question set and every result CSV will be.

## Build the ledger (v1)

```bash
python3 service/ingest/build_db.py
```

Reads the git-ignored exports in `corpus/` and writes `service/data/library.sqlite`, printing the counts that the method page publishes. `service/answer.py` is the one interface every pattern and the eval call.

## Run locally

```bash
python3 -m http.server 8787
```

Then open http://localhost:8787/. A `.claude/launch.json` config named `static` exists for the Claude Code browser preview.

## Deploy

Cloudflare Pages from the `main` branch of https://github.com/shhirl/ragpatterns, live at **https://ragpatterns.com** since 9 September 2026. `main` is protected: changes arrive as pull requests, each with its own preview URL, and merging deploys in about twenty seconds. The full story, including what happens when the v1 service arrives, is in `DEPLOY.md`.

## Design

Direction chosen 9 Sep 2026: "the shelf". The seven patterns stand on a shelf as book spines whose height is the predicted score and whose width is the cost; the explorer and scorecard are wide and square-gridded. The four directions that were considered are kept in `docs/design-options/`.
