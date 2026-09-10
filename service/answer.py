"""The one interface. The eval, the site's demo box and the trace panel all call this.

answer(question, pattern, image=None, force_route=None) -> {
  answer, context: [{source, id, score, stage}], route, calls, ms, usage: {input_tokens, output_tokens, usd}
}
v1: naive and rerank are live. The forced SQL diagnostic still exists beside them; it measures
the tool, not a pattern, and is labelled as such in every result it produces.
Graph, hybrid, multimodal, agentic and multi-agent arrive at v2-v4 and are still predictions.
"""
import time
from service.patterns import sql_forced


def _load_patterns():
    """Imported lazily: the deployed service replays recorded runs and must not need model keys."""
    from service.patterns import naive as _naive, rerank as _rerank
    return {'naive': _naive.run, 'rerank': _rerank.run}


PATTERNS = {}   # naive and rerank at v1; multimodal, graph, hybrid, agentic, multiagent at v2-v4


def answer(question, pattern=None, image=None, force_route=None, qid='Q2', cache_query=False):
    t0 = time.time()
    if force_route == 'sql':
        out = sql_forced.run(question, qid)
    elif pattern in ('naive', 'rerank'):
        if not PATTERNS:
            PATTERNS.update(_load_patterns())
        out = PATTERNS[pattern](question, image, cache_query=cache_query)
    else:
        raise NotImplementedError(f'pattern {pattern!r} is not built yet (v1 has naive, rerank and force_route="sql")')
    out.setdefault('calls', 0)
    out.setdefault('usage', {'input_tokens': 0, 'output_tokens': 0, 'usd': 0.0})
    out['ms'] = int((time.time() - t0) * 1000)
    return out
