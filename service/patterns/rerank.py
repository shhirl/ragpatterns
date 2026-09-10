"""Retrieve-and-rerank: cast a wider net, then let a cross-encoder read the question and each
candidate together and keep the best four.

Same index, same prompt, same model as naive. The only difference is that thirty candidates are
scored a second time by a model that can see the question while it reads the chunk. That fixes
the failure where a question's words match what Shirley marked rather than what she thought.

It cannot fix a missing source. The reranker only reorders what the vector search already found,
so every ledger question fails here exactly as it fails for naive - more cheaply worded, no more
correct.
"""
import os, sys, time

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from service.retrievers import vector, rerank as rr
from service.patterns import _generate

CANDIDATES, K = 30, 4


def run(question, image=None, k=K, candidates=CANDIDATES, cache_query=False):
    t0 = time.time()
    wide, embed_tokens, cached = vector.search(question, k=candidates, cache_query=cache_query)
    retrieve_ms = int((time.time() - t0) * 1000)
    t1 = time.time()
    chunks, rerank_tokens = rr.rerank(question, wide, k=k)
    rerank_ms = int((time.time() - t1) * 1000)
    out = _generate.generate(question, chunks)
    out.update({
        'route': 'embed -> top-%d by cosine -> cross-encoder rerank -> top-%d -> generate' % (candidates, k),
        'context': [{'source': c['kind'], 'id': c['title'], 'score': c['rerank_score'],
                     'cosine': c['score'], 'vector_rank': c['vector_rank'], 'stage': 'reranked',
                     'text': c['text'], 'author': c['author'], 'location': c.get('location'),
                     'book_id': c['book_id']} for c in chunks],
        'retrieve_ms': retrieve_ms, 'rerank_ms': rerank_ms,
        'embed_tokens': embed_tokens, 'rerank_tokens': rerank_tokens,
        'query_embedding_cached': cached,
    })
    return out
