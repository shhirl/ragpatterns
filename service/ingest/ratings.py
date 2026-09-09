"""Fetch the crowd average for each book from Open Library, once, by ISBN.

Why this exists: the Goodreads export no longer carries an Average Rating column
(checked 9 Sep 2026), and Q3 needs "what everyone else thought". Open Library's search
API returns ratings_average and ratings_count per work. Results are cached in
service/data/ratings_cache.json (git-ignored) so the network is hit once per ISBN.
Books without an ISBN fall back to a title + author search, flagged as such.
"""
import json, os, sys, time, urllib.parse, urllib.request
from concurrent.futures import ThreadPoolExecutor

UA = 'ragpatterns.com ingest (shirley.he09@gmail.com)'
CACHE = os.path.join(os.path.dirname(__file__), '..', 'data', 'ratings_cache.json')
FIELDS = 'key,title,author_name,ratings_average,ratings_count'


def _get(url: str):
    req = urllib.request.Request(url, headers={'User-Agent': UA})
    for attempt in range(3):
        try:
            with urllib.request.urlopen(req, timeout=20) as r:
                return json.load(r)
        except Exception as e:  # noqa: BLE001
            time.sleep(1.5 * (attempt + 1))
    return None


def lookup(isbn13: str, isbn: str, title: str, author: str) -> dict:
    """Returns {source, key, avg, count, ol_title} or {source: 'none'}."""
    for code in (isbn13, isbn):
        if code:
            d = _get(f'https://openlibrary.org/search.json?isbn={urllib.parse.quote(code)}&fields={FIELDS}&limit=1')
            if d and d.get('docs'):
                doc = d['docs'][0]
                return {'source': 'isbn', 'key': doc.get('key'), 'avg': doc.get('ratings_average'),
                        'count': doc.get('ratings_count'), 'ol_title': doc.get('title')}
    q = urllib.parse.quote(f'{title.split("(")[0].split(":")[0].strip()} {author}')
    d = _get(f'https://openlibrary.org/search.json?q={q}&fields={FIELDS}&limit=1')
    if d and d.get('docs'):
        doc = d['docs'][0]
        return {'source': 'title', 'key': doc.get('key'), 'avg': doc.get('ratings_average'),
                'count': doc.get('ratings_count'), 'ol_title': doc.get('title')}
    return {'source': 'none'}


def enrich(books: list, workers: int = 4) -> dict:
    cache = json.load(open(CACHE)) if os.path.exists(CACHE) else {}
    todo = [b for b in books if b.goodreads_id not in cache]

    def work(b):
        return b.goodreads_id, lookup(b.isbn13, b.isbn, b.title, b.author)

    with ThreadPoolExecutor(max_workers=workers) as ex:
        for i, (gid, res) in enumerate(ex.map(work, todo), 1):
            cache[gid] = res
            if i % 50 == 0:
                print(f'  {i}/{len(todo)} looked up', file=sys.stderr)
                json.dump(cache, open(CACHE, 'w'), indent=1)
    os.makedirs(os.path.dirname(CACHE), exist_ok=True)
    json.dump(cache, open(CACHE, 'w'), indent=1)
    for b in books:
        r = cache.get(b.goodreads_id, {})
        b.avg_rating = r.get('avg')
        b.ratings_count = r.get('count')
    return cache


if __name__ == '__main__':
    sys.path.insert(0, os.path.dirname(__file__))
    from goodreads import load
    books = load(sys.argv[1] if len(sys.argv) > 1 else 'corpus/goodreads_library_export.csv')
    cache = enrich(books)
    found = [b for b in books if b.avg_rating]
    by_isbn = sum(1 for b in books if cache[b.goodreads_id].get('source') == 'isbn')
    by_title = sum(1 for b in books if cache[b.goodreads_id].get('source') == 'title')
    print(f'{len(books)} books: matched {by_isbn} by ISBN, {by_title} by title, {len(books)-by_isbn-by_title} unmatched; '
          f'{len(found)} have a crowd average; {sum(1 for b in found if (b.ratings_count or 0) >= 20)} with 20+ ratings')
