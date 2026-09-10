"""The one prompt template and the one generation call, shared by every pattern.

This file is the reason the comparison means anything. Naive and rerank differ only in which
chunks arrive here; the model, the system prompt, the context format and the settings are
identical. If a column wins, retrieval won it.

Claude Opus 5 at its defaults (adaptive thinking, effort high). No pattern gets a better prompt.
"""
import os, sys, time

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from service import config

SYSTEM = """You answer questions about Shirley's personal library, using only the CONTEXT below.

The context holds two kinds of text: passages she highlighted in a book (the book's words) and
notes she wrote about a book (her words). Each is labelled with its book and author.

Rules:
- Use only the CONTEXT. Do not use anything you know about these books from elsewhere.
- Never name a book that does not appear in the CONTEXT.
- If the CONTEXT cannot answer the question, say so plainly and say what is missing. Do not
  guess, and do not fill a gap with a plausible answer.
- The context contains no ratings, dates, page counts or shelf information. If the question
  needs those, say that they are not in the context rather than estimating them.
- When you quote, quote exactly and name the book.
- Answer in a few sentences. No preamble."""


def render(chunks):
    """The context block. Metadata (book, author, Kindle location) rides alongside the passage;
    only the passage itself was ever embedded."""
    out = []
    for i, c in enumerate(chunks, 1):
        kind = 'highlight I marked' if c['kind'] == 'highlight' else 'note I wrote'
        where = ''
        if c.get('location'):
            where = ', Kindle location %s' % c['location']
        elif c.get('page'):
            where = ', page %s' % c['page']
        out.append('[%d] %s - %s (%s%s)\n%s' % (i, kind.capitalize(), c['title'], c['author'], where, c['text']))
    return '\n\n'.join(out) if out else '(nothing was retrieved)'


def generate(question, chunks, model=None):
    import anthropic
    model = model or config.GEN_MODEL
    prompt = 'CONTEXT\n%s\n\nQUESTION\n%s' % (render(chunks), question)
    t0 = time.time()
    r = anthropic.Anthropic().messages.create(
        model=model, max_tokens=8000, system=SYSTEM,
        messages=[{'role': 'user', 'content': prompt}])
    ms = int((time.time() - t0) * 1000)
    text = '\n'.join(b.text for b in r.content if b.type == 'text').strip()
    u = r.usage
    return {'answer': text, 'calls': 1, 'gen_ms': ms, 'model': model,
            'stop_reason': r.stop_reason,
            'usage': {'input_tokens': u.input_tokens, 'output_tokens': u.output_tokens,
                      'usd': config.usd(model, u.input_tokens, u.output_tokens)}}
