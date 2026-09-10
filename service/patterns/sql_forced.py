"""Forced SQL path: the diagnostic that gives Q2 a real answer before any pattern exists.

This is NOT a pattern. There is no router and no generation call; the question is mapped to a
hand-written query by the eval, the tool runs it, and the rows are formatted. It measures one
thing: whether the ledger and the tool can answer a numbers question at all. When the agentic
router exists, the same query is what a correct route should produce.
"""
from service.retrievers import sql

# question id -> the query a correct tool call would run. Only the ledger questions have one.
QUERIES = {
    'Q2': ("SELECT title, author, pages, date_read, my_rating, lifechanging FROM read_books "
           "WHERE date_read BETWEEN '2024-01-01' AND '2024-12-31' AND my_rating = 5 AND pages < 300 "
           "ORDER BY date_read"),
    'Q7': ("SELECT b.title, b.author, b.my_rating, b.lifechanging FROM books b JOIN tags t ON t.book_id = b.id "
           "WHERE t.tag = 'Race' AND b.my_rating = 5 AND b.shelf = 'read' ORDER BY b.date_read"),
    'Q8': ("SELECT t.tag, COUNT(*) AS books_read, SUM(CASE WHEN b.my_rating = 5 THEN 1 ELSE 0 END) AS five_star "
           "FROM tags t JOIN books b ON b.id = t.book_id WHERE b.shelf = 'read' GROUP BY t.tag ORDER BY books_read DESC LIMIT 10"),
    'Q9': ("WITH c AS (SELECT substr(b.date_read,1,4) AS year, t.tag, COUNT(*) AS n FROM tags t JOIN books b ON b.id = t.book_id "
           "WHERE b.shelf = 'read' AND b.date_read IS NOT NULL GROUP BY year, t.tag), "
           "r AS (SELECT *, ROW_NUMBER() OVER (PARTITION BY year ORDER BY n DESC, tag) AS rk FROM c), "
           "cov AS (SELECT substr(date_read,1,4) AS year, COUNT(*) AS books, SUM(CASE WHEN EXISTS(SELECT 1 FROM tags t WHERE t.book_id = b.id) THEN 1 ELSE 0 END) AS tagged "
           "FROM books b WHERE shelf = 'read' AND date_read IS NOT NULL GROUP BY year) "
           "SELECT r.year, r.tag, r.n, cov.tagged, cov.books FROM r JOIN cov ON cov.year = r.year WHERE rk <= 3 ORDER BY r.year, rk"),
}


def run(question: str, qid: str = 'Q2'):
    if qid not in QUERIES:
        raise KeyError(f'{qid} has no ledger query; it is not a numbers question')
    q = QUERIES[qid]
    rows, truncated = sql.run(q)
    if not rows:
        text = 'No ledger row matches.'
    elif 'title' in rows[0]:
        lines = [f"{r['title']} ({r['author']}" + (f", {r['pages']} pages" if r.get('pages') else '')
                 + (f", read {r['date_read']}" if r.get('date_read') else '') + (", lifechanging" if r.get('lifechanging') else "") + ")" for r in rows]
        text = 'Exactly these ledger rows:\n' + '\n'.join(f'- {l}' for l in lines)
    elif 'year' in rows[0]:
        by = {}
        for r in rows:
            by.setdefault((r['year'], r['tagged'], r['books']), []).append(f"{r['tag']} ({r['n']})")
        lines = [f"{y}: " + (', '.join(tags) if tagged >= 5 else f"too few tagged books to rank ({tagged} of {books} tagged)")
                 for (y, tagged, books), tags in by.items()]
        text = 'Top tags per year, by my own tags:\n' + '\n'.join(f'- {l}' for l in lines)
    else:
        lines = [f"{r['tag']}: {r['books_read']} read, {r['five_star']} five-star" for r in rows]
        text = 'My tags across the read shelf:\n' + '\n'.join(f'- {l}' for l in lines)
    return {'answer': text,
            'context': [{'source': 'sql', 'id': r.get('title') or r.get('tag'), 'score': None, 'stage': 'rows'} for r in rows],
            'route': 'sql (forced, no model call)', 'calls': 0, 'sql': q, 'truncated': truncated}
