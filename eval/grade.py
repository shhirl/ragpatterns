"""Turn a run into the sheet Shirley grades from.

  python3 eval/grade.py eval/results/v1-2026-09-10.json

Writes, beside the run:
  <run>-grading.md       one section per pattern x question: the reference, all five answers,
                         what the automatic checks found, and a proposed verdict with its reason
  <run>-verdicts.csv     pattern,qid,proposed,final,note  - she fills `final`

The proposal is mine and is labelled as mine. HANDOFF §3.8 says Shirley grades; the point of the
proposal is that she can agree in a second or overrule in a sentence, not that it counts as a
grade. Nothing reaches the site under `final` until she has written it.
"""
import argparse, collections, csv, json, os, re, sys


def consistent(answers):
    """Do the five runs say the same thing? Compared on the set of books each names."""
    sets = [tuple(sorted(a['checks']['books_named'])) for a in answers]
    return len(set(sets)) == 1, sets


def propose(qid, answers, ref):
    """A proposed verdict from the automatic checks alone, plus the reason, in Shirley's terms.
    Deliberately conservative: anything that needs a judgement about meaning is left to her."""
    ch = [a['checks'] for a in answers]
    invented = any(c['named_outside_context'] or c['quoted_not_on_shelf'] for c in ch)
    abstained = sum(1 for c in ch if c['abstained'])
    hits = [c['retrieval_hit'] for c in ch if c['retrieval_hit'] is not None]
    want = ch[0]['retrieval_expected']
    same, _ = consistent(answers)

    if invented:
        return 'wrong', 'names a book that was not in its context, or quotes a title that is not on the shelf'
    if want and hits and max(hits) == 0:
        return 'wrong', 'the book the reference names never reached the context: retrieval missed it in every run'
    if abstained == len(ch):
        return 'partial', ('says plainly that the context cannot answer. Right about itself, and no invention, '
                           'but it is not the answer: judge whether "I cannot" is the correct answer here')
    if want and hits and min(hits) == want:
        return 'good', 'every book the reference names was retrieved in every run, nothing outside the context is named'
    if want and hits and max(hits) > 0:
        return 'partial', 'retrieved %d of %d expected books (best run); read whether the answer is right about them' % (max(hits), want)
    if not same:
        return 'partial', 'the five runs do not name the same books, so at most one of them can be right'
    return '', 'no automatic check settles this one: it needs reading'


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('run_json')
    a = ap.parse_args()
    data = json.load(open(a.run_json, encoding='utf-8'))
    base = a.run_json[:-5]

    import yaml
    qs = {q['id']: q for q in yaml.safe_load(
        open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'questions.yaml'), encoding='utf-8')) if q.get('id')}

    by = collections.OrderedDict()
    for t in data['traces']:
        by.setdefault((t['pattern'], t['qid']), []).append(t)

    md = ['# Grading sheet - %s, %s' % (data['tag'], data['date']), '',
          'Generation: `%s`. Embeddings: `%s`. Reranker: `%s`. %d runs per cell.'
          % (data['model'], data['embed_model'], data['rerank_model'], data['runs']), '',
          'The **proposed** verdict is Claude\'s, from the automatic checks only. The **verdict** is '
          'Shirley\'s and is the one that ships. Write it in `%s-verdicts.csv`.' % os.path.basename(base), '',
          'Scale: `good` answers the question · `partial` right in part, or right to refuse · `wrong`.', '', '---', '']
    rows = []
    for (pattern, qid), answers in by.items():
        q = qs.get(qid, {})
        verdict, why = propose(qid, answers, q.get('reference', ''))
        same, sets = consistent(answers)
        usd = sum(a['usage'].get('usd', 0) for a in answers)
        ms = sorted(a['ms'] for a in answers)
        md += ['## %s - %s' % (pattern, qid), '',
               '**Question.** %s' % q.get('question', ''), '',
               '**Reference.** %s' % (q.get('reference', '') or '').strip().replace('\n', ' '), '',
               '**Proposed: `%s`** - %s' % (verdict or '(needs reading)', why), '',
               '| | |', '|---|---|',
               '| runs agree on the books named | %s |' % ('yes' if same else 'no - %s' % (set(sets),)),
               '| median latency | %d ms |' % ms[len(ms) // 2],
               '| cost for %d runs | $%0.4f |' % (len(answers), usd),
               '| retrieval hit | %s of %s expected books |' % (answers[0]['checks']['retrieval_hit'],
                                                                answers[0]['checks']['retrieval_expected']),
               '| named outside its context | %s |' % (sorted({b for a in answers for b in a['checks']['named_outside_context']}) or 'none'),
               '| quoted a title not on the shelf | %s |' % (sorted({b for a in answers for b in a['checks']['quoted_not_on_shelf']}) or 'none'),
               '']
        md += ['**Retrieved (run 1).**', '']
        for c in answers[0]['context']:
            md.append('- `%s` %s - *%s*%s' % (c.get('score'), c.get('id'), c.get('source'),
                                              (' loc %s' % c['location']) if c.get('location') else ''))
        md += ['']
        for t in answers:
            md += ['**Run %d** (%d ms, $%0.4f)' % (t['run'], t['ms'], t['usage'].get('usd', 0)), '',
                   '> ' + (t['answer'] or '(empty)').replace('\n', '\n> '), '']
        md += ['---', '']
        rows.append({'pattern': pattern, 'qid': qid, 'proposed': verdict, 'final': '', 'note': why})

    open(base + '-grading.md', 'w', encoding='utf-8').write('\n'.join(md))
    with open(base + '-verdicts.csv', 'w', newline='', encoding='utf-8') as f:
        w = csv.DictWriter(f, fieldnames=['pattern', 'qid', 'proposed', 'final', 'note'])
        w.writeheader()
        for r in rows:
            w.writerow(r)
    print('sheet    -> %s-grading.md  (%d cells)' % (base, len(rows)))
    print('verdicts -> %s-verdicts.csv  (fill the `final` column)' % base)


if __name__ == '__main__':
    main()
