"""The SQL tool: read-only access to the ledger for the patterns that have a tool.

Only SELECT statements, one statement, capped rows. The schema text is what the router
and the agents are shown; keep it in sync with build_db.py.
"""
import os, re, sqlite3

DB = os.environ.get('LEDGER_DB') or os.path.join(os.path.dirname(__file__), '..', 'data', 'library.sqlite')
SCHEMA = """books(id, title, author, isbn13, pages, pub_year, orig_year, date_read 'YYYY-MM-DD', date_added,
      shelf in ('read','to-read','currently-reading','abandoned'), shelves, read_count,
      my_rating 1-5 or NULL if Shirley never rated it, lifechanging 0/1, kind 'Fiction'|'Non-Fiction'|...,
      avg_rating (Open Library crowd average, NULL if unknown), ratings_count, my_notes)
tags(book_id, tag, source)              -- Shirley's own genre tags
highlights(id, book_id, source, text)   -- short passages; source 'notion' or 'kindle'
recommendations(book_id, by_initials, where_, date)
view read_books = books where shelf='read'"""
MAX_ROWS = 50


class ToolError(ValueError):
    pass


def run(sql: str, db_path: str = DB, max_rows: int = MAX_ROWS):
    q = sql.strip().rstrip(';')
    if not re.match(r'^\s*(select|with)\b', q, re.I) or ';' in q:
        raise ToolError('read-only: one SELECT statement')
    if re.search(r'\b(insert|update|delete|drop|alter|attach|pragma|create)\b', q, re.I):
        raise ToolError('read-only: statement not allowed')
    con = sqlite3.connect(f'file:{db_path}?mode=ro', uri=True)
    con.row_factory = sqlite3.Row
    try:
        rows = con.execute(q).fetchmany(max_rows + 1)
    finally:
        con.close()
    truncated = len(rows) > max_rows
    return [dict(r) for r in rows[:max_rows]], truncated
