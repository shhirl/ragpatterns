"""Match Notion reviews to Goodreads ledger rows by title and author.

Order: exact normalised title (unique) -> normalised title + author surname -> fuzzy title
(difflib >= 0.85) + author surname -> alias table. Everything else is reported as unmatched;
the count is published on the method page.
"""
import difflib, re

ALIASES = {  # Notion name -> Goodreads title, for cases fuzzy matching cannot see
    "Fermat's Last Theorem": "Fermat's Enigma",
    "Persepolis": "The Complete Persepolis",
}


def norm(t: str) -> str:
    t = t.lower().split(' (')[0].split(':')[0]
    t = re.sub(r"[^a-z0-9 ]", "", t)
    t = re.sub(r"^(the|a|an) ", "", t.strip())
    return re.sub(r"\s+", " ", t).strip()


def surname(a: str) -> str:
    return a.split()[-1].lower() if a else ''


def match(reviews, books):
    """Returns (pairs, unmatched, how) where pairs = [(review, book)], how = Counter of match kinds."""
    from collections import Counter
    idx = {}
    for b in books:
        idx.setdefault(norm(b.title), []).append(b)
    keys = list(idx)
    pairs, unmatched, how = [], [], Counter()
    for r in reviews:
        name = ALIASES.get(r.name, r.name)
        key = norm(name)
        c = idx.get(key, [])
        if len(c) == 1:
            pairs.append((r, c[0])); how['title'] += 1; continue
        if len(c) > 1:
            c2 = [b for b in c if any(surname(a) == surname(b.author) for a in r.authors)]
            if c2:
                pairs.append((r, c2[0])); how['title+author'] += 1; continue
        close = difflib.get_close_matches(key, keys, n=3, cutoff=0.85)
        c3 = [b for k in close for b in idx[k] if any(surname(a)[:4] == surname(b.author)[:4] for a in r.authors)]
        if c3:
            pairs.append((r, c3[0])); how['fuzzy+author'] += 1; continue
        unmatched.append(r)
    return pairs, unmatched, how


if __name__ == '__main__':
    import sys, os
    sys.path.insert(0, os.path.dirname(__file__))
    from goodreads import load as load_gr
    from notion import load as load_notion
    pairs, unmatched, how = match(load_notion('corpus/notion'), load_gr('corpus/goodreads_library_export.csv'))
    print(f'{len(pairs)} matched {dict(how)}; {len(unmatched)} unmatched: {[r.name for r in unmatched]}')
