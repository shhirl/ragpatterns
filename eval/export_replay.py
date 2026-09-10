"""Turn a graded run into service/data/replay.json, which the live panel serves.

  python3 eval/export_replay.py eval/results/v1-2026-09-10.json

Why replay and not a live model call: the panel is on a public page. A live naive or rerank call
would spend Shirley's money on every stranger's click, and the answer could differ from the trace
printed above it. What ships is the measured run, labelled as the measured run, with its date.
The forced SQL path stays genuinely live, because a query costs nothing.

Copyright: a retrieved chunk is shortened to a quotable excerpt before it leaves this file.
Highlights are the book's words (HANDOFF §3.4: short excerpts with attribution, never the
passage); her own notes are hers, and get more room.
"""
import argparse, csv, json, os, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, 'service', 'data', 'replay.json')
EXCERPT = {'highlight': 180, 'note': 400}


def excerpt(text, kind):
    n = EXCERPT.get(kind, 180)
    t = ' '.join((text or '').split())
    if len(t) <= n:
        return t, False
    cut = t.rfind(' ', 0, n)
    return t[:cut if cut > n // 2 else n].rstrip(' ,;:.') + '…', True


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('run_json')
    ap.add_argument('--run', type=int, default=1, help='which of the N runs the panel shows')
    ap.add_argument('--out', default=OUT)
    a = ap.parse_args()
    data = json.load(open(a.run_json, encoding='utf-8'))

    verdicts = {}
    vpath = a.run_json[:-5] + '-verdicts.csv'
    if os.path.exists(vpath):
        for r in csv.DictReader(open(vpath, encoding='utf-8')):
            v = (r.get('final') or '').strip()
            if v:
                verdicts[(r['pattern'], r['qid'])] = v

    cells, runs_by_cell = {}, {}
    for t in data['traces']:
        runs_by_cell.setdefault((t['pattern'], t['qid']), []).append(t)
    for key, ts in runs_by_cell.items():
        ts.sort(key=lambda x: x['run'])
        t = next((x for x in ts if x['run'] == a.run), ts[0])
        ctx, truncated = [], False
        for c in t['context']:
            text, cut = excerpt(c.get('text'), c.get('source'))
            truncated = truncated or cut
            ctx.append({'id': c.get('id'), 'author': c.get('author'), 'kind': c.get('source'),
                        'score': c.get('score'), 'cosine': c.get('cosine'),
                        'vector_rank': c.get('vector_rank'), 'location': c.get('location'),
                        'excerpt': text})
        cells['%s/%s' % key] = {
            'pattern': key[0], 'qid': key[1], 'question': t['question'], 'answer': t['answer'],
            'route': t['route'], 'calls': t['calls'], 'ms': t['ms'],
            'retrieve_ms': t.get('retrieve_ms'), 'rerank_ms': t.get('rerank_ms'), 'gen_ms': t.get('gen_ms'),
            'usd': round(t['usage'].get('usd', 0.0), 4),
            'input_tokens': t['usage'].get('input_tokens'), 'output_tokens': t['usage'].get('output_tokens'),
            'context': ctx, 'excerpts_truncated': truncated,
            'verdict': verdicts.get(key, ''),
            'runs': len(ts), 'shown_run': t['run'],
            'ms_all': [x['ms'] for x in ts],
            'agree': len({tuple(sorted(x['checks']['books_named'])) for x in ts}) == 1,
        }
    out = {'measured': data['date'], 'tag': data['tag'], 'model': data['model'],
           'embed_model': data['embed_model'], 'rerank_model': data['rerank_model'],
           'runs': data['runs'], 'graded': bool(verdicts), 'cells': cells}
    json.dump(out, open(a.out, 'w', encoding='utf-8'), indent=1, ensure_ascii=False)
    print('%d cells -> %s' % (len(cells), a.out))
    print('graded: %s' % ('yes' if verdicts else 'not yet - run eval/grade.py and fill `final`'))


if __name__ == '__main__':
    main()
