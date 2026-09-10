"""Naive RAG: embed the question, take the nearest chunks, put them in the prompt.

Three steps and one model call. It is the baseline every other pattern is measured against, and
on a question whose answer sits verbatim in one chunk it is the right answer at the lowest price.
It has no tool, so the ledger is invisible to it: dates, ratings and page counts are rows, and
rows were never embedded (HANDOFF §3.5).
"""
import os, sys, time

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from service.retrievers import vector
from service.patterns import _generate

K = 4


def run(question, image=None, k=K, cache_query=False):
    t0 = time.time()
    chunks, embed_tokens, cached = vector.search(question, k=k, cache_query=cache_query)
    retrieve_ms = int((time.time() - t0) * 1000)
    out = _generate.generate(question, chunks)
    out.update({
        'route': 'embed -> top-%d by cosine -> generate' % k,
        'context': [{'source': c['kind'], 'id': c['title'], 'score': c['score'], 'stage': 'retrieved',
                     'text': c['text'], 'author': c['author'], 'location': c.get('location'),
                     'book_id': c['book_id']} for c in chunks],
        'retrieve_ms': retrieve_ms, 'embed_tokens': embed_tokens, 'rerank_tokens': 0,
        'query_embedding_cached': cached,
    })
    return out
