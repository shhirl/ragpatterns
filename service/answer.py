"""The one interface. The eval, the site's demo box and the trace panel all call this.

answer(question, pattern, image=None, force_route=None) -> {
  answer, context: [{source, id, score, stage}], route, calls, ms, usage: {input_tokens, output_tokens, usd}
}
v1 status: only the forced SQL diagnostic path exists (no model call). It measures the tool,
not a pattern, and is labelled as such in every result it produces.
"""
import time
from service.patterns import sql_forced

PATTERNS = {}  # filled as patterns arrive: naive, rerank, multimodal, graph, hybrid, agentic, multiagent


def answer(question, pattern=None, image=None, force_route=None, qid='Q2'):
    t0 = time.time()
    if force_route == 'sql':
        out = sql_forced.run(question, qid)
    elif pattern in PATTERNS:
        out = PATTERNS[pattern](question, image)
    else:
        raise NotImplementedError(f'pattern {pattern!r} is not built yet (v1 has only force_route="sql")')
    out.setdefault('calls', 0)
    out.setdefault('usage', {'input_tokens': 0, 'output_tokens': 0, 'usd': 0.0})
    out['ms'] = int((time.time() - t0) * 1000)
    return out
