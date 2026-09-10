"""Forced SQL path: the diagnostic that gives Q2 a real answer before any pattern exists.

This is NOT a pattern. There is no router and no generation call; the question is mapped to a
hand-written query by the eval, the tool runs it, and the rows are formatted. It measures one
thing: whether the ledger and the tool can answer a numbers question at all. When the agentic
router exists, the same query is what a correct route should produce.
"""
from service.retrievers import sql

# question id -> the query a correct tool call would run. Q2 is the only one at v1.
QUERIES = {
    'Q2': ("SELECT title, author, pages, date_read, my_rating, lifechanging FROM read_books "
           "WHERE date_read BETWEEN '2024-01-01' AND '2024-12-31' AND my_rating = 5 AND pages < 300 "
           "ORDER BY date_read"),
}


def run(question: str, qid: str = 'Q2'):
    q = QUERIES[qid]
    rows, truncated = sql.run(q)
    if rows:
        lines = [f"{r['title']} ({r['author']}, {r['pages']} pages, read {r['date_read']}"
                 + (", lifechanging" if r['lifechanging'] else "") + ")" for r in rows]
        text = 'Exactly these ledger rows:\n' + '\n'.join(f'- {l}' for l in lines)
    else:
        text = 'No book in the ledger matches all three conditions.'
    return {'answer': text,
            'context': [{'source': 'sql', 'id': r['title'], 'score': None, 'stage': 'rows'} for r in rows],
            'route': 'sql (forced, no model call)', 'calls': 0, 'sql': q, 'truncated': truncated}
