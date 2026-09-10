"""Parse the Notion "Book Reviews" export (Markdown & CSV, subpages included) into rows.

Shirley's ratings, genre tags, notes and the "Related Books" / "How I Discovered It"
sections come from here. The export lands in corpus/notion/ (git-ignored):
  corpus/notion/<workspace>/Book Reviews <id>_all.csv     all properties, one row per page
  corpus/notion/<workspace>/Book Reviews/<Name> <id>.md   properties header + page body
  corpus/notion/<workspace>/Book Reviews/<Name>/          attachments for a few books
Rows without an author are template strays ("Fiction", "Book Review Ideas") and are dropped.
Rating text ("5-Star", "Lifechanging") becomes an integer 1..5; Lifechanging counts as 5 and
keeps a flag, because it is the strongest signal she has.
"""
import csv, difflib, glob, os, re
from dataclasses import dataclass, field, asdict
from typing import Optional

SECTIONS = ["What It's About", "Thoughts", "What I Liked About It", "What I Didn't Like About It",
            "Who Would Like It?", "How I Discovered It", "Themes, topics,", "Related Books"]
RATING = {'Lifechanging': 5, '5-Star': 5, '4-Star': 4, '3-Star': 3, '2-Star': 2, '1-Star': 1}


@dataclass
class Review:
    name: str
    authors: list
    rating: Optional[int]
    lifechanging: bool
    date_finished: Optional[str]
    kind: str                  # Fiction / Non-Fiction / Fiction-Series / Mystery / ''
    first_published: Optional[int]
    genres: list
    notes_status: str
    notes: str = ''            # free text at the top of the page, before the template headings
    sections: dict = field(default_factory=dict)   # heading -> text, her own words
    highlights: list = field(default_factory=list) # passages copied from the book: quote only short excerpts
    page_id: str = ''


def _find(root: str):
    csvs = glob.glob(os.path.join(root, '**', 'Book Reviews *_all.csv'), recursive=True)
    if not csvs:
        raise FileNotFoundError('no "Book Reviews *_all.csv" under ' + root)
    folder = os.path.join(os.path.dirname(csvs[0]), 'Book Reviews')
    return csvs[0], folder


def _split(v: str) -> list:
    return [x.strip() for x in v.split(',') if x.strip()] if v else []


def _body(md: str):
    """Drop the '# Title' line and the 'Key: value' header, split the rest into free notes + sections."""
    lines = md.split('\n')
    i = 0
    if lines and lines[0].startswith('# '):
        i = 1
    while i < len(lines) and (re.match(r'^[A-Za-z ?]+: ', lines[i]) or not lines[i].strip()):
        i += 1
    rest = '\n'.join(lines[i:])
    parts = re.split(r'\n(?=#{1,3} |🔍)', '\n' + rest)
    notes, sections = [], {}
    for p in parts:
        p = p.strip()
        if not p:
            continue
        if p.startswith('#') or p.startswith('🔍'):
            first, _, text = p.partition('\n')
            head = re.sub(r'^[#\s]*', '', first)
            head = re.sub(r'^[^A-Za-z]+', '', head).strip()      # drop the emoji
            if text.strip():
                sections[head] = text.strip()
        else:
            notes.append(p)
    return '\n\n'.join(notes).strip(), sections


QUOTE_HEADS = ('highlight', 'quote', 'my top 3 quotes')


def _classify(sections: dict):
    """Split page sections into her own notes and copied book text.
    A heading that is itself a long sentence is a pasted passage (Notion exports Kindle-synced
    highlights as headings); so is anything under a Highlights/Quotes heading. Those are
    copyrighted text: the site may quote short excerpts with attribution, never the passage."""
    notes, highlights = {}, []
    for head, text in sections.items():
        h = head.lower()
        if len(head.split()) > 12:
            highlights.append(head + ('\n' + text if text else ''))
        elif any(q in h for q in QUOTE_HEADS):
            highlights.extend([x.strip() for x in re.split(r'\n\s*\n', text) if x.strip()])
        else:
            notes[head] = text
    return notes, highlights


def _drop_boilerplate(rows):
    """A section whose heading AND text are identical on three or more pages is template text
    Shirley never edited (the 'Fiction' template's 'What to write notes on?' block). Drop it."""
    from collections import Counter
    seen = Counter((h, t) for r in rows for h, t in r.sections.items())
    dropped = 0
    for r in rows:
        for h, t in list(r.sections.items()):
            if seen[(h, t)] >= 3:
                del r.sections[h]; dropped += 1
    return dropped


def load(root: str = 'corpus/notion') -> list:
    csv_path, folder = _find(root)
    pages = {}
    for md in glob.glob(os.path.join(folder, '*.md')):
        base = os.path.basename(md)[:-3]
        m = re.match(r'^(.*) ([0-9a-f]{32})$', base)
        if not m:
            continue
        pages.setdefault(m.group(1), []).append((m.group(2), md))
    out = []
    with open(csv_path, encoding='utf-8-sig', newline='') as f:
        for r in csv.DictReader(f):
            name = r['Name'].strip()
            authors = _split(r.get('Author', ''))
            if not name or not authors:
                continue
            rating = RATING.get(r.get('Rating', '').strip())
            notes, sections, pid = '', {}, ''
            # match the md by the file-safe name Notion used (it strips ':' and a few others)
            key = name.replace(':', '').replace('/', '')
            cands = pages.get(key) or pages.get(name) or []
            if not cands:   # Notion strips accents and punctuation from file names; take the closest
                best = difflib.get_close_matches(key, list(pages), n=1, cutoff=0.8)
                cands = pages[best[0]] if best else []
            if cands:
                pid, md = cands[0]
                notes, sections = _body(open(md, encoding='utf-8').read())
            sections, highlights = _classify(sections)
            date = r.get('Date Finished', '').strip().replace('/', '-') or None
            fp = r.get('First Published', '').strip()
            out.append(Review(name=name, authors=authors, rating=rating,
                              lifechanging=r.get('Rating', '').strip() == 'Lifechanging',
                              date_finished=date, kind=r.get('Fiction?', '').strip(),
                              first_published=int(float(fp)) if fp else None,
                              genres=_split(r.get('Genres', '')), notes_status=r.get('Notes Status', '').strip(),
                              notes=notes, sections=sections, highlights=highlights, page_id=pid))
    load.dropped_boilerplate = _drop_boilerplate(out)
    return out


def to_dicts(rows): return [asdict(r) for r in rows]


if __name__ == '__main__':
    import sys, collections
    rows = load(sys.argv[1] if len(sys.argv) > 1 else 'corpus/notion')
    with_notes = [r for r in rows if r.notes or r.sections]
    print(f'{len(rows)} reviews with an author; {sum(1 for r in rows if r.rating)} rated; '
          f'{sum(1 for r in rows if r.date_finished)} dated; {sum(1 for r in rows if r.genres)} with tags; '
          f'{len(with_notes)} with her own notes; {sum(1 for r in rows if r.highlights)} with copied passages '
          f'({sum(len(r.highlights) for r in rows)} passages); {sum(1 for r in rows if r.page_id)} matched to a page file')
    print('template boilerplate sections dropped:', load.dropped_boilerplate)
    print('note sections used:', collections.Counter(h for r in rows for h in r.sections).most_common(12))
    print('ratings:', collections.Counter(r.rating for r in rows))
