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

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from checks import abstained as _abstained, hedged as _hedged, named_outside, norm as _norm  # noqa: E402
from run import ledger_titles                                              # noqa: E402

_TITLES = None


def _titles():
    global _TITLES
    if _TITLES is None:
        _TITLES = ledger_titles()
    return _TITLES


def outside(trace):
    """Books named that were not in the context, recomputed from the recorded answer.

    Recomputed rather than read back, because a check that turns out to be wrong has to reach the
    runs measured before the fix. See eval/checks.py."""
    _, out = named_outside(trace.get('answer'), trace.get('context'), _titles(), trace.get('question'))
    return out


def refused(trace):
    """Did this run say plainly that it could not answer? Recomputed, for the same reason."""
    return _abstained(trace.get('answer'))


def hedge(trace):
    """A refusal that then answers a nearby question - still a refusal, a different shape."""
    return _hedged(trace.get('answer'), trace.get('context'))


def consistent(answers):
    """Do the five runs say the same thing? Compared on the set of books each names."""
    sets = [tuple(sorted(a['checks']['books_named'])) for a in answers]
    return len(set(sets)) == 1, sets


def propose(qid, answers, ref):
    """A proposed verdict from the automatic checks alone, plus the reason, in Shirley's terms.
    Deliberately conservative: anything that needs a judgement about meaning is left to her."""
    ch = [a['checks'] for a in answers]
    # Naming a book that was not in the context is an invention. Quoting a phrase that matches no
    # title is not: the quoted-phrase check fires on any short quotation, including the exact
    # highlight a correct answer is supposed to quote. It stays in the sheet as something to read.
    invented = any(outside(a) for a in answers)
    abstained = sum(1 for a in answers if refused(a))
    hits = [c['retrieval_hit'] for c in ch if c['retrieval_hit'] is not None]
    want = ch[0]['retrieval_expected']
    same, _ = consistent(answers)

    if invented:
        return 'wrong', 'names a book that was not in its context: %s' % ', '.join(
            sorted({b for a in answers for b in outside(a)}))
    # Shirley's ruling, 10 Sep 2026: "I can't answer that" is partial. It sits above the
    # retrieval-miss rule on purpose. A pattern that never retrieved the book and then said so
    # plainly has failed at retrieval and been honest about it, and honest is not wrong. A
    # pattern that never retrieved the book and answered anyway is the one that is wrong.
    if abstained == len(ch):
        h = sum(1 for a in answers if hedge(a))
        if h:
            return 'partial', ('says in all %d runs that the context cannot answer as asked; %d of them then '
                               'offer what the notes do hold. Partial by your ruling - read whether the '
                               'substitute answer is any good' % (len(ch), h))
        return 'partial', ('refuses flatly in all %d runs: says the context cannot answer, and names nothing '
                           'outside it. Partial by your ruling - honest, but not the answer' % len(ch))
    if want and hits and max(hits) == 0:
        return 'wrong', ('answered without the source: the book the reference names never reached the context '
                         'in any run, and %d of %d runs answered anyway' % (len(ch) - abstained, len(ch)))
    if abstained:
        return '', ('%d of %d runs refuse and the rest answer, so the cell is not one thing: read whether the '
                    'answers are right and whether the refusals should have been' % (abstained, len(ch)))
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
          'Scale: `good` answers the question · `partial` right in part, or right to refuse · `wrong`.', '',
          'Two caveats on the automatic checks. A title the question itself names is not counted as '
          'named-outside-context. And "quoted a title not on the shelf" flags any short quoted phrase '
          'that matches no book, so an ordinary quotation from a note lands there too: read it, do not '
          'trust it.', '', '---', '']
    rows = []
    for (pattern, qid), answers in by.items():
        q = qs.get(qid, {})
        verdict, why = propose(qid, answers, q.get('reference', ''))
        same, sets = consistent(answers)
        usd = sum(a['usage'].get('usd', 0) for a in answers)

        def med(key):
            vals = sorted(v for v in (a.get(key) for a in answers) if v)
            return vals[len(vals) // 2] if vals else 0

        # Wall clock is not latency here: Voyage's free tier allows three requests a minute, so a
        # cell can sit for fifty seconds doing nothing. Generation and rerank are the honest
        # numbers, and they are the ones the site publishes.
        ms = sorted(a['ms'] for a in answers)
        md += ['## %s - %s' % (pattern, qid), '',
               '**Question.** %s' % q.get('question', ''), '',
               '**Reference.** %s' % (q.get('reference', '') or '').strip().replace('\n', ' '), '',
               '**Proposed: `%s`** - %s' % (verdict or '(needs reading)', why), '',
               '| | |', '|---|---|',
               '| runs agree on the books named | %s |' % ('yes' if same else 'no - %s' % (set(sets),)),
               '| median generation | %d ms |' % med('gen_ms'),
               '| median rerank | %s |' % ('%d ms' % med('rerank_ms') if med('rerank_ms') else 'n/a'),
               '| median retrieval | %d ms %s|' % (med('retrieve_ms'),
                                                   '(throttled: Voyage allows 3 requests a minute) ' if med('retrieve_ms') > 2000 else ''),
               '| median wall clock | %d ms - not latency, see above |' % ms[len(ms) // 2],
               '| cost for %d runs | $%0.4f |' % (len(answers), usd),
               '| retrieval hit | %s of %s expected books |' % (answers[0]['checks']['retrieval_hit'],
                                                                answers[0]['checks']['retrieval_expected']),
               '| named outside its context | %s |' % (sorted({b for a in answers for b in outside(a)}) or 'none'),
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
