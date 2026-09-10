"""The live service: the one interface over HTTP. Standard-library WSGI app, run by gunicorn.

  GET  /health            {ok, version, db, patterns, measured}
  GET  /questions         the nine questions with status
  POST /ask  {qid, pattern}
        pattern "sql"    -> runs the query now, against the public ledger. Costs nothing.
        pattern "naive" | "rerank" -> the measured run of September 2026, replayed from
                            service/data/replay.json, with its date and its verdict.

Why the two patterns replay rather than run: a live model call on a public page spends money on
every stranger's click and could disagree with the trace printed above it. What ships is the
measurement, labelled as a measurement. The service needs no model keys.

Serves the PUBLIC ledger (service/data/library.public.sqlite: no notes, no copied passages).
No free SQL in public: that stays in the local workbench. CORS is limited to the site.
"""
import json, os, sys, time
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
os.environ.setdefault('LEDGER_DB', os.path.join(os.path.dirname(__file__), 'data', 'library.public.sqlite'))
from service.answer import answer
from service.patterns.sql_forced import QUERIES

REPLAY_PATH = os.path.join(os.path.dirname(__file__), 'data', 'replay.json')
try:
    REPLAY = json.load(open(REPLAY_PATH, encoding='utf-8'))
except Exception:                                    # noqa: BLE001
    REPLAY = {'cells': {}, 'measured': None}

VERSION = ('v1 · ledger live + naive and rerank measured %s' % REPLAY['measured']) if REPLAY['cells'] \
    else 'v1 · ledger only · forced SQL path, no model call'
PATTERNS = ['sql'] + sorted({c['pattern'] for c in REPLAY['cells'].values()})
ORIGINS = {'https://ragpatterns.com', 'https://www.ragpatterns.com', 'http://localhost:8787', 'http://127.0.0.1:8787'}
QUESTIONS = [
    ('Q1', 'Where did I read the line about leaving a movie theatre and realising it had been dark outside for some time?', None),
    ('Q2', 'What did I read in 2024, rated five stars, under 300 pages?', None),
    ('Q3', 'Why did I give The Fellowship of the Ring two stars when everyone else loved it?', None),
    ('Q4', 'Which of my books argue with each other?', 'waits for the graph (v2)'),
    ('Q5', '[photo] Which book is this, and what did I highlight near it?', 'waits for photo crops and the multimodal index (v3)'),
    ('Q6', 'Two-week holiday list from my to-read shelf…', 'waits for recommendations.csv and the graph (v2)'),
    ('Q7', 'Give me my favourite books I have read about race.', None),
    ('Q8', 'What are the themes I like most?', None),
    ('Q9', 'What were my top themes each year?', None),
]


def _json(start, status, obj, origin):
    body = json.dumps(obj, ensure_ascii=False).encode('utf-8')
    headers = [('Content-Type', 'application/json; charset=utf-8'), ('Content-Length', str(len(body))), ('Cache-Control', 'no-store')]
    if origin in ORIGINS:
        headers += [('Access-Control-Allow-Origin', origin), ('Access-Control-Allow-Methods', 'GET, POST, OPTIONS'),
                    ('Access-Control-Allow-Headers', 'Content-Type'), ('Vary', 'Origin')]
    start(status, headers)
    return [body]


def app(environ, start):
    path = environ.get('PATH_INFO', '/'); method = environ.get('REQUEST_METHOD', 'GET'); origin = environ.get('HTTP_ORIGIN', '')
    if method == 'OPTIONS':
        return _json(start, '204 No Content', {}, origin)
    if path == '/health':
        return _json(start, '200 OK', {'ok': True, 'version': VERSION, 'db': os.path.basename(os.environ['LEDGER_DB']),
                                       'patterns': PATTERNS, 'measured': REPLAY.get('measured'),
                                       'model': REPLAY.get('model'), 'runs': REPLAY.get('runs'),
                                       'sql_answerable': [q for q in QUERIES],
                                       'answerable': [q for q, _, w in QUESTIONS if not w]}, origin)
    if path == '/questions':
        return _json(start, '200 OK', [{'id': q, 'text': t, 'waits_for': w} for q, t, w in QUESTIONS], origin)
    if path == '/ask' and method == 'POST':
        try:
            n = int(environ.get('CONTENT_LENGTH') or 0)
            data = json.loads(environ['wsgi.input'].read(n) or b'{}')
            qid = str(data.get('qid', ''))
            pattern = str(data.get('pattern') or 'sql')
            text = dict((q, t) for q, t, _ in QUESTIONS).get(qid)
            if not text:
                return _json(start, '400 Bad Request', {'error': f'{qid or "?"} is not one of the nine questions'}, origin)
            if pattern in ('naive', 'rerank'):
                cell = REPLAY['cells'].get('%s/%s' % (pattern, qid))
                if not cell:
                    return _json(start, '404 Not Found',
                                 {'error': f'{pattern} has no measured run for {qid} yet'}, origin)
                r = dict(cell)
                r.update({'live': False, 'measured': REPLAY.get('measured'), 'model': REPLAY.get('model'),
                          'source': 'the measured run, replayed', 'version': VERSION,
                          'served_at': int(time.time())})
                return _json(start, '200 OK', r, origin)
            if qid not in QUERIES:
                return _json(start, '400 Bad Request', {'error': f'{qid} is not a ledger question'}, origin)
            r = answer(text, force_route='sql', qid=qid)
            r.update({'question': text, 'live': True, 'source': 'run just now',
                      'version': VERSION, 'served_at': int(time.time())})
            return _json(start, '200 OK', r, origin)
        except Exception as e:  # noqa: BLE001
            return _json(start, '500 Internal Server Error', {'error': str(e)}, origin)
    return _json(start, '404 Not Found', {'error': 'not found'}, origin)


if __name__ == '__main__':   # local run without gunicorn
    from wsgiref.simple_server import make_server
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 8791
    print(f'api on http://localhost:{port}')
    make_server('127.0.0.1', port, app).serve_forever()
