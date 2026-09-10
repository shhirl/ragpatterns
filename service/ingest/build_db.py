"""Build service/data/library.sqlite, the ledger, from the three sources on disk.

  Goodreads export  -> books (title, author, ISBN, pages, dates, shelves)        the ledger
  Open Library      -> books.avg_rating / ratings_count (fetched once, cached)    the crowd
  Notion export     -> books.my_rating / kind / my_notes, tags, highlights        Shirley's verdicts

Rules (HANDOFF.md §3.4, §5, §9):
  - Private Notes never reach this file (dropped in goodreads.py).
  - The ledger is rows, never embedded. Highlights are text; the ledger is not.
  - Crowd average: trust ISBN matches; keep a title-fallback match only when the normalised
    titles agree; otherwise store nothing and count the book as "no crowd figure".
  - Shelf: read / to-read / currently-reading / abandoned (the Goodreads `dnf` shelf).
Run:  python3 service/ingest/build_db.py   (prints the numbers that go on the method page)
"""
import json, os, sqlite3, sys
sys.path.insert(0, os.path.dirname(__file__))
from goodreads import load as load_goodreads
from notion import load as load_notion
from match import match, norm

ROOT = os.path.join(os.path.dirname(__file__), '..', '..')
DB = os.path.join(ROOT, 'service', 'data', 'library.sqlite')
CACHE = os.path.join(ROOT, 'service', 'data', 'ratings_cache.json')

SCHEMA = """
CREATE TABLE books (
  id INTEGER PRIMARY KEY, goodreads_id TEXT UNIQUE, title TEXT NOT NULL, author TEXT NOT NULL,
  isbn TEXT, isbn13 TEXT, pages INTEGER, pub_year INTEGER, orig_year INTEGER,
  date_read TEXT, date_added TEXT, shelf TEXT NOT NULL, shelves TEXT, read_count INTEGER,
  my_rating INTEGER, lifechanging INTEGER DEFAULT 0, kind TEXT,
  avg_rating REAL, ratings_count INTEGER, avg_source TEXT,
  notion_page_id TEXT, my_notes TEXT
);
CREATE TABLE tags (book_id INTEGER REFERENCES books(id), tag TEXT NOT NULL, source TEXT NOT NULL DEFAULT 'shirley');
CREATE TABLE highlights (
  id INTEGER PRIMARY KEY, book_id INTEGER REFERENCES books(id), source TEXT NOT NULL,
  text TEXT NOT NULL, location TEXT, page INTEGER, added_on TEXT, note TEXT
);
CREATE TABLE recommendations (book_id INTEGER REFERENCES books(id), by_initials TEXT, where_ TEXT, date TEXT);
CREATE TABLE images (id INTEGER PRIMARY KEY, book_id INTEGER, kind TEXT, path TEXT, caption TEXT);
CREATE VIEW read_books AS SELECT * FROM books WHERE shelf='read';
"""


def crowd(b, cache):
    r = cache.get(b.goodreads_id, {})
    if not r.get('avg'):
        return None, None, 'none'
    if r.get('source') == 'isbn':
        return r['avg'], r.get('count'), 'isbn'
    if r.get('source') == 'title' and r.get('ol_title') and norm(r['ol_title']) == norm(b.title):
        return r['avg'], r.get('count'), 'title-agreed'
    return None, None, 'title-disagreed'


def build(db_path=DB):
    books = load_goodreads(os.path.join(ROOT, 'corpus', 'goodreads_library_export.csv'))
    reviews = load_notion(os.path.join(ROOT, 'corpus', 'notion'))
    cache = json.load(open(CACHE)) if os.path.exists(CACHE) else {}
    pairs, unmatched, how = match(reviews, books)
    review_for = {b.goodreads_id: r for r, b in pairs}

    if os.path.exists(db_path):
        os.remove(db_path)
    con = sqlite3.connect(db_path)
    con.executescript(SCHEMA)
    counts = {'books': 0, 'read': 0, 'rated': 0, 'crowd_isbn': 0, 'crowd_title_agreed': 0, 'crowd_none': 0,
              'tags': 0, 'notion_highlights': 0, 'with_notes': 0}
    for b in books:
        r = review_for.get(b.goodreads_id)
        avg, cnt, src = crowd(b, cache)
        shelf = 'abandoned' if 'dnf' in b.shelves else b.exclusive_shelf
        my_notes = None
        if r:
            parts = [r.notes] + [f'{h}: {t}' for h, t in r.sections.items()]
            my_notes = '\n\n'.join(p for p in parts if p) or None
        cur = con.execute(
            'INSERT INTO books (goodreads_id,title,author,isbn,isbn13,pages,pub_year,orig_year,date_read,date_added,'
            'shelf,shelves,read_count,my_rating,lifechanging,kind,avg_rating,ratings_count,avg_source,notion_page_id,my_notes)'
            ' VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)',
            (b.goodreads_id, b.title, b.author, b.isbn or None, b.isbn13 or None, b.pages, b.year_published, b.original_year,
             b.date_read or (r.date_finished if r else None), b.date_added, shelf, ','.join(b.shelves) or None, b.read_count,
             r.rating if r else None, int(bool(r and r.lifechanging)), (r.kind or None) if r else None,
             avg, cnt, src, (r.page_id or None) if r else None, my_notes))
        bid = cur.lastrowid
        counts['books'] += 1
        counts['read'] += shelf == 'read'
        counts['rated'] += bool(r and r.rating)
        counts['with_notes'] += bool(my_notes)
        counts[{'isbn': 'crowd_isbn', 'title-agreed': 'crowd_title_agreed'}.get(src, 'crowd_none')] += 1
        if r:
            for t in r.genres:
                con.execute('INSERT INTO tags VALUES (?,?,?)', (bid, t, 'shirley')); counts['tags'] += 1
            for h in r.highlights:
                con.execute('INSERT INTO highlights (book_id,source,text) VALUES (?,?,?)', (bid, 'notion', h))
                counts['notion_highlights'] += 1
    con.commit(); con.close()
    counts['notion_reviews'] = len(reviews); counts['notion_matched'] = len(pairs); counts['notion_unmatched'] = len(unmatched)
    return counts


if __name__ == '__main__':
    c = build()
    print(json.dumps(c, indent=1))
