"""Run the question set through the live patterns and write the results the site publishes.

  python3 eval/run.py                       every ready question, naive + rerank, 5 runs
  python3 eval/run.py --runs 1 --q Q1,Q3    a quick check
  python3 eval/run.py --patterns naive

Rules this runner exists to keep (HANDOFF §3.8):
  - it calls the same answer() the site's panel calls; there is no eval-only code path;
  - it never grades. It records the answer, the trace, the cost and a set of automatic checks,
    and Shirley reads them. A verdict column is left empty for her.
  - every run is written, including the bad ones.

Outputs, into eval/results/:
  v1-<date>.csv          one row per run: the answer, the numbers, the automatic checks
  v1-<date>.json         full traces (retrieved chunks and scores), used to replay the panel
"""
import argparse, csv, datetime, json, os, re, sqlite3, sys, time

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from service import config
from service.answer import answer

HERE = os.path.dirname(os.path.abspath(__file__))
RESULTS = os.path.join(HERE, 'results')


def questions(path=None):
    import yaml
    rows = yaml.safe_load(open(path or os.path.join(HERE, 'questions.yaml'), encoding='utf-8'))
    return [q for q in rows if q.get('id')]


def ready(q):
    return str(q.get('status', '')).strip().lower().startswith(('ready', 'partially ready'))


# --- automatic checks --------------------------------------------------------------------
def _norm(t):
    t = re.sub(r'\s*\(.*?\)\s*$', '', t or '')          # drop "(The Lord of the Rings, #1)"
    return re.sub(r'[^a-z0-9 ]', '', t.lower()).strip()


def ledger_titles(db=None):
    con = sqlite3.connect(db or config.LEDGER_DB)
    out = [(r[0], _norm(r[0])) for r in con.execute('SELECT title FROM books')]
    con.close()
    return out


QUOTED = re.compile(r'[""“]([^""”]{4,80})[""”]|\*([^*\n]{4,80})\*')


def checks(text, context, expects, titles):
    """Three things a machine can settle, so Shirley only has to judge the answer itself."""
    low = ' ' + re.sub(r'[^a-z0-9 ]', ' ', (text or '').lower()) + ' '
    named = [orig for orig, n in titles if n and len(n) > 6 and (' ' + n + ' ') in low]
    in_context = {c.get('id') for c in (context or [])}
    outside = sorted(set(named) - set(in_context))
    hit = None
    if expects:
        want = [_norm(e) for e in expects]
        got = [_norm(c.get('id') or '') for c in (context or [])]
        hit = sum(1 for w in want if any(w and w in g for g in got))
    # a title-shaped phrase in quotes that matches nothing on the shelf: a candidate invention
    invented = []
    for m in QUOTED.finditer(text or ''):
        cand = _norm(m.group(1) or m.group(2) or '')
        if cand and len(cand.split()) <= 8 and not any(cand in n or n in cand for _, n in titles if n):
            invented.append((m.group(1) or m.group(2)).strip())
    abstained = bool(re.search(r"\b(not in the context|cannot answer|does not contain|no (?:ratings|dates|page)"
                               r"|isn't in the context|is not in the context|nothing (?:was )?retrieved)\b",
                               (text or '').lower()))
    return {'books_named': named, 'named_outside_context': outside,
            'retrieval_hit': hit, 'retrieval_expected': len(expects or []),
            'quoted_not_on_shelf': invented, 'abstained': abstained}


# --- the run -----------------------------------------------------------------------------
FIELDS = ['pattern', 'qid', 'run', 'ok', 'verdict', 'answer', 'route', 'calls', 'ms',
          'retrieve_ms', 'rerank_ms', 'gen_ms', 'input_tokens', 'output_tokens', 'usd',
          'embed_tokens', 'rerank_tokens', 'query_embedding_cached', 'retrieved', 'books_named', 'named_outside_context',
          'retrieval_hit', 'retrieval_expected', 'quoted_not_on_shelf', 'abstained', 'error']


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--runs', type=int, default=5)
    ap.add_argument('--patterns', default='naive,rerank')
    ap.add_argument('--q', default='')
    ap.add_argument('--tag', default='v1')
    ap.add_argument('--all-questions', action='store_true', help='include the ones still pending')
    a = ap.parse_args()

    qs = questions()
    if a.q:
        want = {x.strip().upper() for x in a.q.split(',')}
        qs = [q for q in qs if q['id'] in want]
    elif not a.all_questions:
        qs = [q for q in qs if ready(q)]
    patterns = [p.strip() for p in a.patterns.split(',') if p.strip()]
    titles = ledger_titles()

    stamp = datetime.date.today().isoformat()
    os.makedirs(RESULTS, exist_ok=True)
    csv_path = os.path.join(RESULTS, '%s-%s.csv' % (a.tag, stamp))
    json_path = os.path.join(RESULTS, '%s-%s.json' % (a.tag, stamp))
    total = len(patterns) * len(qs) * a.runs
    print('%d answers: %s x %s x %d runs' % (total, patterns, [q['id'] for q in qs], a.runs), flush=True)

    rows, traces, spend, t_start = [], [], 0.0, time.time()
    n = 0
    for pattern in patterns:
        for q in qs:
            for run in range(1, a.runs + 1):
                n += 1
                rec = {'pattern': pattern, 'qid': q['id'], 'run': run, 'verdict': '', 'error': ''}
                try:
                    r = answer(q['question'], pattern=pattern, cache_query=(run > 1))
                    ch = checks(r['answer'], r.get('context'), q.get('expects'), titles)
                    u = r.get('usage') or {}
                    rec.update({
                        'ok': 1, 'answer': r['answer'], 'route': r.get('route', ''),
                        'calls': r.get('calls', 0), 'ms': r.get('ms', 0),
                        'retrieve_ms': r.get('retrieve_ms', ''), 'rerank_ms': r.get('rerank_ms', ''),
                        'gen_ms': r.get('gen_ms', ''),
                        'input_tokens': u.get('input_tokens', 0), 'output_tokens': u.get('output_tokens', 0),
                        'usd': u.get('usd', 0.0), 'embed_tokens': r.get('embed_tokens', 0),
                        'rerank_tokens': r.get('rerank_tokens', 0),
                        'query_embedding_cached': int(bool(r.get('query_embedding_cached'))),
                        'retrieved': ' | '.join('%s (%s)' % (c.get('id'), c.get('score')) for c in r.get('context', [])),
                    })
                    rec.update({k: (json.dumps(v) if isinstance(v, list) else v) for k, v in ch.items()})
                    spend += u.get('usd', 0.0)
                    traces.append({'pattern': pattern, 'qid': q['id'], 'run': run,
                                   'question': q['question'], 'answer': r['answer'],
                                   'route': r.get('route'), 'calls': r.get('calls'), 'ms': r.get('ms'),
                                   'retrieve_ms': r.get('retrieve_ms'), 'rerank_ms': r.get('rerank_ms'),
                                   'gen_ms': r.get('gen_ms'), 'usage': u, 'checks': ch,
                                   'query_embedding_cached': bool(r.get('query_embedding_cached')),
                                   'context': r.get('context', [])})
                    flag = ''
                    if ch['named_outside_context']:
                        flag = '  !! named outside context: %s' % ch['named_outside_context']
                    print('  [%d/%d] %-7s %s run %d  %5d ms  $%0.4f%s' %
                          (n, total, pattern, q['id'], run, r.get('ms', 0), u.get('usd', 0), flag), flush=True)
                except Exception as e:                                    # noqa: BLE001
                    rec.update({'ok': 0, 'answer': '', 'error': '%s: %s' % (type(e).__name__, e)})
                    print('  [%d/%d] %-7s %s run %d  FAILED %s' % (n, total, pattern, q['id'], run, e), flush=True)
                rows.append(rec)

    with open(csv_path, 'w', newline='', encoding='utf-8') as f:
        w = csv.DictWriter(f, fieldnames=FIELDS, extrasaction='ignore')
        w.writeheader()
        for r in rows:
            w.writerow(r)
    json.dump({'tag': a.tag, 'date': stamp, 'model': config.GEN_MODEL,
               'embed_model': config.EMBED_MODEL, 'rerank_model': config.RERANK_MODEL,
               'runs': a.runs, 'traces': traces}, open(json_path, 'w', encoding='utf-8'),
              indent=1, ensure_ascii=False)
    print('\n%d rows -> %s' % (len(rows), csv_path))
    print('traces      -> %s' % json_path)
    print('spend $%0.2f, wall %d s' % (spend, int(time.time() - t_start)))


if __name__ == '__main__':
    main()
