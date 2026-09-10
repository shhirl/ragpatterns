"""The reranker: a cross-encoder that reads the question and one chunk together.

The difference from the vector search is what it sees. The embedder turns the question into a
vector once and compares it to vectors made without knowing the question. The cross-encoder
reads the pair, so it can tell "a passage I marked in that book" from "the sentence that answers
why I disliked it" - the failure the whole rerank column exists to test.

It is not a second LLM (HANDOFF §3.10 rejected that: a second LLM muddies attribution). It is a
scoring model, and the only thing it can do is reorder a list it is handed. It cannot add a
candidate the vector search never retrieved, which is why reranking never rescues the ledger
questions.
"""
import os, sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from service import config

_limiter = config.VOYAGE          # the account's budget, shared with every other Voyage call


def rerank(question, chunks, k=4, model=None):
    """-> (top-k chunks with a `rerank_score` and their old rank, tokens billed)."""
    import time, voyageai
    if not chunks:
        return [], 0
    model = model or config.RERANK_MODEL
    docs = [c['text'] for c in chunks]
    # Thirty chunks and a question is most of the free tier's 10,000 tokens a minute, and a
    # character-count estimate runs low on this text, so the reply that matters is 429. The
    # embedder has retried since it was written; this call did not, and fourteen cells of the
    # first measured run died on it. Retrieval is deterministic, so a retry costs wall clock
    # and changes no answer.
    est = sum(max(1, len(d) // 4) for d in docs) + max(1, len(question) // 4)
    r = None
    for attempt in range(6):
        _limiter.wait(est)
        try:
            r = voyageai.Client().rerank(question, docs, model=model, top_k=min(k, len(docs)))
            break
        except voyageai.error.RateLimitError:
            _limiter.record(est)             # it counted against the window even though it failed
            time.sleep(20 * (attempt + 1))
    if r is None:
        raise RuntimeError('the reranker was rate-limited six times in a row')
    _limiter.record(r.total_tokens)
    out = []
    for res in r.results:
        c = dict(chunks[res.index])
        c['rerank_score'] = round(float(res.relevance_score), 4)
        c['vector_rank'] = res.index + 1
        out.append(c)
    return out, r.total_tokens
