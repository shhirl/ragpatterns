# RAG patterns, side by side

Working name until 10 Sep 2026: "Seven RAGs, one shelf".

A one-project site that runs the seven common RAG design patterns (naive, retrieve-and-rerank, multimodal, graph, hybrid, agentic router, multi-agent) on **one** real knowledge base, Shirley's own bookshelf, and **the same nine questions**, so the only thing that changes between columns is the architecture.

- `index.html` — the thesis, the corpus, an interactive pattern × question explorer with pipeline diagrams and graded traces, the scorecard, and a decision guide.
- `how-its-built.html` — the method: why books, trade-offs, the corpus, the question set, how answers are judged, the version plan, the stack.
- `docs/plan.html` — the build plan with diagrams (ingest, graph schema, retriever matrix, versions, deployment) and the open decisions.
- `LADDERS.md` — the wider three-year plan this project is the first rung of.

No framework, no build step, no external requests. Each page is one self-contained HTML file with its CSS and JS inline.

## Status

**v0 (September 2026): predicted traces.** The nine questions are fixed and all 63 pattern × question cells are traced by prediction. Every cell is labelled as a prediction; `how-its-built.html#versions` says what becomes a measurement and when.

**v1 is built but not yet measured (10 Sep 2026).** The ledger, the read-only SQL tool, the vector index, the cross-encoder reranker and two patterns — naive and retrieve-and-rerank — all exist behind the same `answer()` interface. The measurement run has not been made, so **every trace on the site is still a prediction** and still says so. `HANDOFF.md` §10 is the full record: what was decided, what is verified, and the exact commands that finish v1.

The corpus itself (the curated exports) is not in the repo and never will be. The photos, the extracted graph, the question set and every result CSV will be.

## Build it (v1)

The ingest and the API run on the system Python. Anything that calls a model needs the
virtualenv, because the `anthropic` SDK requires Python 3.10+ and this machine's default is 3.9:

```bash
python3 -m venv .venv && .venv/bin/pip install anthropic voyageai
```

Put `ANTHROPIC_API_KEY` and `VOYAGE_API_KEY` in `.env` (git-ignored). Then:

```bash
python3 service/ingest/build_db.py            # corpus/ -> service/data/library.sqlite
.venv/bin/python service/ingest/build_index.py  # -> service/data/index.sqlite (resumable)
```

Both print the counts the method page publishes. Rebuild in that order: changing the ingest
changes the chunk hashes and re-embeds the index. `service/answer.py` is the one interface every
pattern, the eval and the site call.

## Measure it

```bash
.venv/bin/python eval/run.py --runs 1 --q Q1,Q2                  # pilot: 4 answers, cents
.venv/bin/python eval/run.py --runs 5 --all-questions            # the real run
.venv/bin/python eval/grade.py eval/results/v1-<date>.json       # the sheet Shirley grades
.venv/bin/python eval/export_replay.py eval/results/v1-<date>.json
```

The runner never grades and never hides a bad run: it writes every answer, its trace, its cost
and a set of automatic checks, and Shirley writes the verdicts. `export_replay.py` produces
`service/data/replay.json`, which is what the site's live panel serves — the measured run,
replayed with its date, rather than a model call charged to Shirley on every visitor's click.

## See and interact with the system (local workbench)

```bash
.venv/bin/python service/workbench.py
```

Then open http://localhost:8790. Each question gets a button per route that can answer it — the
ledger's SQL path, naive, rerank — plus a free SQL box against the read-only tool and the full
`answer()` result. Unlike the public panel, naive and rerank really run here: it is a local page
and a click costs about half a cent. Local only, never deployed, never linked from the pages.

## Run locally

```bash
python3 -m http.server 8787
```

Then open http://localhost:8787/. A `.claude/launch.json` config named `static` exists for the Claude Code browser preview.

## Deploy

Cloudflare Pages from the `main` branch of https://github.com/shhirl/ragpatterns, live at **https://ragpatterns.com** since 9 September 2026. `main` is protected: changes arrive as pull requests, each with its own preview URL, and merging deploys in about twenty seconds. The full story, including what happens when the v1 service arrives, is in `DEPLOY.md`.

## Design

Direction chosen 9 Sep 2026: "the shelf". The seven patterns stand on a shelf as book spines whose height is the predicted score and whose width is the cost; the explorer and scorecard are wide and square-gridded. The four directions that were considered are kept in `docs/design-options/`.
