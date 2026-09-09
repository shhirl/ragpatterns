"""Parse the Goodreads library export into ledger rows.

Rules (HANDOFF.md §3.4, §5): the Private Notes column is dropped at parse time and
never leaves this function; ISBNs arrive wrapped like ="0123456789" and are unwrapped;
dates are YYYY/MM/DD and become ISO YYYY-MM-DD; a rating of 0 means "not rated".
"""
import csv
from dataclasses import dataclass, asdict
from typing import Optional


@dataclass
class Book:
    goodreads_id: str
    title: str
    author: str
    additional_authors: str
    isbn: str
    isbn13: str
    my_rating: Optional[int]
    pages: Optional[int]
    year_published: Optional[int]
    original_year: Optional[int]
    date_read: Optional[str]
    date_added: Optional[str]
    shelves: list          # custom shelves, e.g. ["dnf"]
    exclusive_shelf: str   # read | currently-reading | to-read
    my_review: str
    read_count: int
    avg_rating: Optional[float] = None   # filled by ratings.py, never from this file
    ratings_count: Optional[int] = None


def _clean_isbn(v: str) -> str:
    return v.replace('="', '').replace('"', '').replace('=', '').strip()


def _int(v: str) -> Optional[int]:
    v = v.strip()
    return int(v) if v.isdigit() else None


def _date(v: str) -> Optional[str]:
    v = v.strip()
    return v.replace('/', '-') if v else None


def load(path: str) -> list:
    books = []
    with open(path, encoding='utf-8', newline='') as f:
        for r in csv.DictReader(f):
            r.pop('Private Notes', None)           # never ingested
            rating = int(float(r.get("My Rating", "0") or 0))
            books.append(Book(
                goodreads_id=r['Book Id'].strip(),
                title=r['Title'].strip(),
                author=r['Author'].strip(),
                additional_authors=r.get('Additional Authors', '').strip(),
                isbn=_clean_isbn(r.get('ISBN', '')),
                isbn13=_clean_isbn(r.get('ISBN13', '')),
                my_rating=rating if rating else None,
                pages=_int(r.get('Number of Pages', '')),
                year_published=_int(r.get('Year Published', '')),
                original_year=_int(r.get('Original Publication Year', '')),
                date_read=_date(r.get('Date Read', '')),
                date_added=_date(r.get('Date Added', '')),
                shelves=[s.strip() for s in r.get('Bookshelves', '').split(',')
                         if s.strip() and s.strip() not in ('read', 'to-read', 'currently-reading')],
                exclusive_shelf=r.get('Exclusive Shelf', '').strip(),
                my_review=r.get('My Review', '').strip(),
                read_count=_int(r.get('Read Count', '')) or 0,
            ))
    return books


def to_dicts(books: list) -> list:
    return [asdict(b) for b in books]


if __name__ == '__main__':
    import sys, collections
    bs = load(sys.argv[1] if len(sys.argv) > 1 else 'corpus/goodreads_library_export.csv')
    print(f'{len(bs)} books; {sum(1 for b in bs if b.isbn13 or b.isbn)} with an ISBN; '
          f'{sum(1 for b in bs if b.my_rating)} rated; {sum(1 for b in bs if b.my_review)} reviewed; '
          f'{sum(1 for b in bs if b.date_read)} with a date read')
    print(collections.Counter(b.exclusive_shelf for b in bs))
