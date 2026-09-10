# Evals guide: how many questions, and what kind

Written 10 September 2026 for ragpatterns.com, kept as a reference for future projects. The short version: **there is no expert consensus on one number.** The people worth reading say two things: start small and diagnostic, grown from real failures; then, when you want numbers you can defend, have enough questions per failure mode that a comparison is not noise. Those are two different sets with two different jobs.

## 1. What the sources say

| source | what it recommends | number given? |
|---|---|---|
| Anthropic, *Demystifying evals for AI agents* (Jan 2026) | Treat evals as engineering infrastructure, like product tests. Agent behaviour is stochastic, so run multiple trials (pass@k vs pass^k answer different questions). Widely summarised as "start with 20–50 simple tasks from real failures; early changes have large effect sizes; a small suite running today beats a perfect one running never". | 20–50 (community reading; the primary page is about method) |
| Anthropic, *A statistical approach to model evaluations* (2024) | Size the set by power analysis, not feel. Report 95% CIs (mean ± 1.96 × SEM). **Compare systems on the same question list and analyse paired differences**: it removes the variance from question difficulty, a "free" variance reduction, because question scores correlate 0.3–0.7 across systems. | no fixed N; compute it |
| Hamel Husain, *How should I approach evaluating my RAG system?* | Do error analysis first; let failure modes emerge from your own data, not a predetermined taxonomy. Evaluate retrieval separately (recall@k, precision@k, MRR) from generation. Generate extra questions by reverse engineering: take documents, extract facts, write the questions those facts answer. Validate any LLM judge against human labels before trusting it. | none |
| Eugene Yan, *Task-specific LLM evals that do and don't work* | Build evals for your task, not generic benchmarks; classification-style checks with references beat open-ended judging where possible. | none |
| Golden-dataset guides (Langfuse, Maxim, Anyscale) | Every observed failure mode deserves at least a few items; scope the set so a failure points at a cause; grow it from production failures. | "a few per failure mode" |
| Statistical power notes (dev.to; `evalstats`) | 100 questions at 80% pass ≈ ±8 points CI. Detecting a 3-point difference needs far more than detecting a 10-point one. Small-sample tools exist but want ≥15 items. Do not lean on the central limit theorem under a few hundred items. | 100 is still coarse |

## 2. The two tiers

**Tier 1, the diagnostic panel.** One question per failure mode plus one control, hand-written with a reference answer before any pipeline runs, graded by hand, full trace shown. Its job is to explain *which* pattern breaks on *what*. Size: as many failure modes as the data really has; for ragpatterns.com that is nine (quote lookup as control; ledger filter; contradicting sources; a relationship between two items; an answer in a picture; a multi-source deliverable; a rating filter joined to a theme; an aggregate; an aggregate over time). More would blur the story, fewer would hide a failure mode.

**Tier 2, the scored set.** About four questions per failure mode, so roughly 36, generated from the corpus the way Hamel describes and checked once by the owner. This is what published numbers rest on. Run every pattern on the same questions, five runs each for consistency, and report **paired differences between patterns with confidence intervals**, not bare pass rates. Hand-grade each question once per pattern (36 × 7 ≈ 250 readings); let code check the repeats for invented items and retrieval hits.

Why not one big set: 36 questions is far too few to *explain* anything and nine is far too few to *count* anything. Keeping the jobs separate keeps both honest.

## 3. Rules that fell out of doing it

- Write the reference answer before the pipeline exists, and compute it from the data where you can (SQL for numbers questions). A reference you can recompute is a reference you can trust.
- Bake the data's honest gaps into the references: "the four unrated books can never appear", "2023–2024 have too few tags to rank; a confident answer is wrong even if the words sound right". Traps for confident wrong answers are the most valuable items in the set.
- Separate "what the user tagged" from "what the model extracted" and let the eval say which one answered.
- Every measurement is labelled predicted until a run replaces it, with the month it happened.
- One interface for the eval and the product (`answer()`), so what is measured is what a visitor gets.

## 4. Sources

- https://hamel.dev/blog/posts/evals-faq/how-should-i-approach-evaluating-my-rag-system.html
- https://hamel.dev/blog/posts/evals-faq/
- https://www.anthropic.com/research/statistical-approach-to-model-evals
- https://ai-eval.org/post/anthropic-demystifying-evals-for-ai-agents
- https://eugeneyan.com/writing/evals/
- https://dev.to/gabrielanhaia/eval-set-sizing-the-statistical-power-math-behind-llm-ab-tests-4gpc
- https://github.com/ianarawjo/evalstats
- https://langfuse.com/resources/engineering/golden-dataset-evaluation
- https://www.getmaxim.ai/articles/building-a-golden-dataset-for-ai-evaluation-a-step-by-step-guide/
