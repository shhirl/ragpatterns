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
# They live in eval/checks.py so that grade.py computes exactly the same thing from a recorded
# run. See that file for why the filters are what they are.
from checks import checks, norm as _norm       # noqa: E402


def ledger_titles(db=None):
    con = sqlite3.connect(db or config.LEDGER_DB)
    out = [(r[0], _norm(r[0])) for r in con.execute('SELECT title FROM books')]
    con.close()
    return out


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
    ap.add_argument('--merge', action='store_true',
                    help='keep the rows already in this tag\'s files and replace only the cells re-run now')
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
                    ch = checks(r['answer'], r.get('context'), q.get('expects'), titles, q['question'])
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

    if not rows:
        # An empty run must never touch the files: `--runs 0` once wrote a 0-row CSV over a
        # measurement that had cost an hour and a dollar. It was in git; that was luck.
        print('nothing was run, so nothing was written')
        return

    if a.merge and os.path.exists(json_path):
        # Voyage's free tier can take a cell out mid-run. Re-running just that cell and merging
        # keeps the rest of the measurement, which cost real money, instead of paying for it
        # twice. A cell present in this run replaces the old one entirely; everything else stays.
        redone = {(r['pattern'], r['qid']) for r in rows}
        old_json = json.load(open(json_path, encoding='utf-8'))
        kept_traces = [t for t in old_json.get('traces', []) if (t['pattern'], t['qid']) not in redone]
        kept_rows = []
        if os.path.exists(csv_path):
            kept_rows = [r for r in csv.DictReader(open(csv_path, encoding='utf-8'))
                         if (r['pattern'], r['qid']) not in redone]
        print('merging: %d rows kept, %d cells replaced' % (len(kept_rows), len(redone)))
        rows = kept_rows + rows
        traces = kept_traces + traces
        rows.sort(key=lambda r: (r['pattern'], r['qid'], int(r['run'])))
        traces.sort(key=lambda t: (t['pattern'], t['qid'], t['run']))

    with open(csv_path, 'w', newline='', encoding='utf-8') as f:
        w = csv.DictWriter(f, fieldnames=FIELDS, extrasaction='ignore')
        w.writeheader()
        for r in rows:
            w.writerow(r)
    # The traces are committed to a public repo, so a chunk leaves this file as an excerpt, not
    # as the passage. Same limits and the same reason as export_replay.py: highlights are the
    # book's words under the short-excerpt rule, notes are Shirley's and get more room. Grading
    # never needed the full text - the sheet prints titles and scores - and the panel publishes
    # excerpts anyway, so nothing downstream loses anything.
    from export_replay import excerpt
    for t in traces:
        for c in t.get('context', []):
            if c.get('text'):
                c['text'], c['text_truncated'] = excerpt(c['text'], c.get('source'))

    json.dump({'tag': a.tag, 'date': stamp, 'model': config.GEN_MODEL,
               'embed_model': config.EMBED_MODEL, 'rerank_model': config.RERANK_MODEL,
               'runs': a.runs, 'traces': traces}, open(json_path, 'w', encoding='utf-8'),
              indent=1, ensure_ascii=False)
    print('\n%d rows -> %s' % (len(rows), csv_path))
    print('traces      -> %s' % json_path)
    print('spend $%0.2f, wall %d s' % (spend, int(time.time() - t_start)))


if __name__ == '__main__':
    main()
