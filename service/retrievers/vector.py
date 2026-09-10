"""The vector index: the only text the patterns without a tool can see.

What is in it (and what deliberately is not):
  IN   her Kindle and Notion highlights (273 passages, 256 with a Kindle location)
       her own notes on 53 books, chunked
  OUT  the ledger. Dates, ratings, page counts and shelves stay as rows and are reached by the
       SQL tool (HANDOFF §3.5). Embedding a ledger is how a system invents a book.

Only the passage text is embedded. The book's title and author ride along as metadata and are
shown to the generator, which is what any real RAG system does and is what lets a quotation be
attributed. No rating, date or page count is ever in a chunk, so "what did I read in 2024,
five stars, under 300 pages" has nothing to match on. That is the point of the comparison.

Build:  python3 service/ingest/build_index.py      (re-embeds only what changed)
"""
import hashlib, os, sqlite3, struct, sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from service import config

SCHEMA = """
CREATE TABLE IF NOT EXISTS chunks (
  id INTEGER PRIMARY KEY,
  book_id INTEGER NOT NULL, title TEXT NOT NULL, author TEXT NOT NULL,
  kind TEXT NOT NULL,            -- 'highlight' | 'note'
  source TEXT,                   -- 'kindle' | 'notion' for highlights
  location TEXT, page TEXT, section TEXT,
  text TEXT NOT NULL, hash TEXT NOT NULL UNIQUE, vec BLOB
);
CREATE INDEX IF NOT EXISTS chunks_book ON chunks(book_id);
CREATE TABLE IF NOT EXISTS meta (key TEXT PRIMARY KEY, value TEXT);
"""

MAX_CHARS = 900          # a chunk a cross-encoder can read in one go
OVERLAP = 150


def split(text, max_chars=MAX_CHARS, overlap=OVERLAP):
    """Paragraph first, then sentence, then a hard cut. Short passages stay whole."""
    text = (text or '').strip()
    if len(text) <= max_chars:
        return [text] if text else []
    out, buf = [], ''
    for para in [p.strip() for p in text.split('\n\n') if p.strip()]:
        if len(buf) + len(para) + 2 <= max_chars:
            buf = (buf + '\n\n' + para).strip()
            continue
        if buf:
            out.append(buf)
        while len(para) > max_chars:
            cut = max(para.rfind('. ', 0, max_chars), para.rfind('? ', 0, max_chars),
                      para.rfind('! ', 0, max_chars), para.rfind('\n', 0, max_chars))
            cut = cut + 1 if cut > max_chars // 3 else max_chars
            out.append(para[:cut].strip())
            para = para[max(0, cut - overlap):].strip()
        buf = para
    if buf:
        out.append(buf)
    return [c for c in out if c]


def _h(*parts):
    return hashlib.sha256('\x00'.join(str(p) for p in parts).encode('utf-8')).hexdigest()[:32]


def collect(ledger_db=None):
    """Every chunk the index should hold, straight from the ledger's text columns."""
    con = sqlite3.connect(ledger_db or config.LEDGER_DB)
    con.row_factory = sqlite3.Row
    rows = []
    for h in con.execute('SELECT h.*, b.title, b.author FROM highlights h JOIN books b ON b.id=h.book_id'):
        for i, piece in enumerate(split(h['text'])):
            rows.append({'book_id': h['book_id'], 'title': h['title'], 'author': h['author'],
                         'kind': 'highlight', 'source': h['source'], 'location': h['location'],
                         'page': h['page'], 'section': None, 'text': piece,
                         'hash': _h('highlight', h['id'], i, piece)})
    for b in con.execute("SELECT id, title, author, my_notes FROM books WHERE my_notes IS NOT NULL AND length(my_notes) > 0"):
        for i, piece in enumerate(split(b['my_notes'])):
            rows.append({'book_id': b['id'], 'title': b['title'], 'author': b['author'],
                         'kind': 'note', 'source': 'notion', 'location': None, 'page': None,
                         'section': None, 'text': piece, 'hash': _h('note', b['id'], i, piece)})
    con.close()
    return rows


def pack(vec):
    return struct.pack('<%df' % len(vec), *vec)


def unpack(blob):
    return struct.unpack('<%df' % (len(blob) // 4), blob)


# An account with no payment method is held to 3 requests and 10,000 tokens a minute. That is
# plenty for a shelf this size; it just means the one-time index build paces itself. Token
# estimates from character counts run low on this text, so the batches are deliberately small
# and a rate-limit reply is retried rather than treated as a failure.
BATCH_TOKENS, MAX_INPUTS = 3200, 96   # bigger batches: the 3-per-minute request cap binds first
_limiter = config.Limiter()


def _embed_call(vo, batch, model, input_type, throttle):
    import time, voyageai
    est = sum(max(1, len(t) // 4) for t in batch)
    for attempt in range(6):
        if throttle:
            _limiter.wait(est)
        try:
            r = vo.embed(batch, model=model, input_type=input_type)
            _limiter.record(r.total_tokens)
            return r
        except voyageai.error.RateLimitError:
            _limiter.record(est)             # assume it counted against the window anyway
            time.sleep(20 * (attempt + 1))
        except (voyageai.error.APIConnectionError, voyageai.error.ServiceUnavailableError) as e:
            # a dropped connection or a DNS blip mid-build. The build commits batch by batch,
            # so the worst case is that this batch is done again.
            print('  network error (%s), retrying in %ds' % (type(e).__name__, 10 * (attempt + 1)), flush=True)
            time.sleep(10 * (attempt + 1))
    raise RuntimeError('Voyage would not answer after 6 attempts (rate limit or network)')


def _normalise(vecs):
    out = []
    for v in vecs:
        n = sum(x * x for x in v) ** 0.5 or 1.0
        out.append([x / n for x in v])
    return out


def embed(texts, input_type='document', model=None, throttle=True, on_batch=None):
    """Voyage embeddings, L2-normalised so cosine similarity is a plain dot product.

    `on_batch(offset, vectors, tokens)` is called after each batch so a long index build can
    commit as it goes and pick up where it stopped."""
    import voyageai
    model = model or config.EMBED_MODEL
    vo = voyageai.Client()
    batches, batch, batch_tokens = [], [], 0
    for t in texts:
        est = max(1, len(t) // 4)
        if batch and (batch_tokens + est > BATCH_TOKENS or len(batch) >= MAX_INPUTS):
            batches.append(batch); batch, batch_tokens = [], 0
        batch.append(t); batch_tokens += est
    if batch:
        batches.append(batch)
    out, tokens, offset = [], 0, 0
    for i, b in enumerate(batches):
        r = _embed_call(vo, b, model, input_type, throttle)
        vecs = _normalise(r.embeddings)
        tokens += r.total_tokens
        if on_batch:
            on_batch(offset, vecs, r.total_tokens)
        else:
            out.extend(vecs)
        offset += len(b)
        if throttle and len(batches) > 3:
            print('  embedded %d/%d batches, %d/%d chunks (%d tokens)'
                  % (i + 1, len(batches), offset, len(texts), tokens), flush=True)
    return out, tokens


def build(ledger_db=None, index_db=None, model=None):
    """Incremental: a chunk whose hash is already stored is not re-embedded."""
    index_db = index_db or config.INDEX_DB
    model = model or config.EMBED_MODEL
    con = sqlite3.connect(index_db)
    con.executescript(SCHEMA)
    have = {r[0] for r in con.execute('SELECT hash FROM chunks WHERE vec IS NOT NULL')}
    rows = collect(ledger_db)
    wanted = {r['hash'] for r in rows}
    for stale in have - wanted:                 # the corpus changed under a chunk: drop it
        con.execute('DELETE FROM chunks WHERE hash=?', (stale,))
    todo = [r for r in rows if r['hash'] not in have]
    tokens = 0
    if todo:
        def _store(offset, vecs, _tok):
            """Committed batch by batch: Voyage's free-tier pace makes this a long build, and a
            build that is interrupted should not have to start again."""
            for r, v in zip(todo[offset:offset + len(vecs)], vecs):
                con.execute('INSERT OR REPLACE INTO chunks (book_id,title,author,kind,source,location,page,section,text,hash,vec)'
                            ' VALUES (?,?,?,?,?,?,?,?,?,?,?)',
                            (r['book_id'], r['title'], r['author'], r['kind'], r['source'], r['location'],
                             r['page'], r['section'], r['text'], r['hash'], pack(v)))
            con.commit()

        _, tokens = embed([r['text'] for r in todo], 'document', model, on_batch=_store)
    con.execute('INSERT OR REPLACE INTO meta VALUES (?,?)', ('embed_model', model))
    con.commit()
    stats = {'chunks': con.execute('SELECT COUNT(*) FROM chunks').fetchone()[0],
             'books': con.execute('SELECT COUNT(DISTINCT book_id) FROM chunks').fetchone()[0],
             'highlights': con.execute("SELECT COUNT(*) FROM chunks WHERE kind='highlight'").fetchone()[0],
             'notes': con.execute("SELECT COUNT(*) FROM chunks WHERE kind='note'").fetchone()[0],
             'embedded_now': len(todo), 'embed_tokens': tokens, 'model': model}
    con.close()
    return stats


_CACHE = {}


def _load(index_db):
    """Held in memory as one matrix: 780 chunks is small, and the published latency should be a
    real system's latency, not the cost of a Python loop."""
    if index_db not in _CACHE:
        import numpy as np
        con = sqlite3.connect(index_db)
        con.row_factory = sqlite3.Row
        rows = list(con.execute('SELECT id,book_id,title,author,kind,source,location,page,text,vec'
                                ' FROM chunks WHERE vec IS NOT NULL ORDER BY id'))
        con.close()
        meta = [{k: r[k] for k in r.keys() if k != 'vec'} for r in rows]
        mat = np.frombuffer(b''.join(r['vec'] for r in rows), dtype='<f4').reshape(len(rows), -1) if rows else np.zeros((0, 1), dtype='<f4')
        _CACHE[index_db] = (meta, mat)
    return _CACHE[index_db]


_QCACHE = {}


def search(question, k=4, index_db=None, model=None, cache_query=False):
    """Top-k chunks by cosine similarity. This is the whole of naive retrieval.

    `cache_query` reuses a question's vector across repeated runs. Retrieval is deterministic -
    the same question gives the same vector and therefore the same chunks - so the cache changes
    no answer, only the wall clock, and it exists because Voyage's free tier allows three requests
    a minute. The eval leaves the first run of every cell uncached and publishes that latency;
    each result says which it was.
    """
    import numpy as np
    index_db = index_db or config.INDEX_DB
    rows, mat = _load(index_db)
    if not len(rows):
        raise RuntimeError('the index is empty: run python3 service/ingest/build_index.py')
    key = (question, model or config.EMBED_MODEL)
    cached = cache_query and key in _QCACHE
    if cached:
        q, tokens = _QCACHE[key], 0
    else:
        (q,), tokens = embed([question], 'query', model)
        if cache_query:
            _QCACHE[key] = q
    scores = mat @ np.asarray(q, dtype='<f4')      # both sides are normalised, so this is cosine
    out = []
    for i in np.argsort(-scores)[:k]:
        r = dict(rows[int(i)])
        r['score'] = round(float(scores[int(i)]), 4)
        out.append(r)
    return out, tokens, cached
