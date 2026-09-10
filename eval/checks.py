"""The automatic checks, in one place, so the runner and the grading sheet cannot disagree.

These settle the three things a machine can settle - did it name a book that was not in front of
it, did the book the reference names reach the context, and did it refuse - so that Shirley only
has to judge the answer itself. None of them is a verdict.

They live here rather than in run.py because grade.py re-computes them from a recorded run: when
a check turns out to be wrong, the fix has to reach runs that were measured before the fix, and
re-running the models to re-measure a regex would be absurd.
"""
import re

# Titles that are also something else on this shelf. "Shirley" is Charlotte Bronte's novel and
# also the person the answer is addressing, so "Shirley, your notes say" is not naming a book.
# There is no clever rule for this; it is one book, listed by hand.
AMBIGUOUS = {'Shirley'}

QUOTED = re.compile(r'[""“]([^""”]{4,80})[""”]|\*([^*\n]{4,80})\*')

# What a refusal looks like. Broader than it first was: the first measured run produced "There's
# nothing about The Fellowship of the Ring in your library context", "I can't break your themes
# down by year" and "I'd need a note or highlight from the Tolkien", none of which the original
# pattern caught, and each miss turned an honest refusal into a proposed `wrong`.
ABSTAIN = re.compile(
    r"\b(?:i |it )?(?:can'?t|cannot|couldn'?t|can not|am unable to|unable to)\s+"
    r"(?:answer|tell|say|determine|break|build|rank|give|name|know|produce|list|make|do)"
    r"|\bthere(?:'s| is| are)?\s+(?:nothing|no \w+)\s+(?:about|in|on|from|here|that)"
    r"|\bi'?d need\b|\byou'?d need\b|\bi would need\b"
    r"|\b(?:is |are |it'?s )?not in (?:the |these |my |your )?(?:context|notes)"
    r"|\bdoes(?:n'?t| not) (?:contain|include|record|have|say|carry)"
    r"|\bdo(?:n'?t| not) (?:contain|include|record|have|say|carry|rank|name)"
    r"|\bno (?:ratings|dates|page|star|record|reading dates)"
    r"|\bisn'?t (?:in the context|here|recorded)"
    r"|\bnothing (?:was )?retrieved"
    r"|\bnot enough (?:information|context)"
    r"|\bthat judgement isn'?t\b|\bthat isn'?t (?:in|recorded)\b")


def norm(t):
    """A title reduced to comparable words: 'The Lord of the Rings, #1' parentheticals dropped."""
    t = re.sub(r'\s*\(.*?\)\s*$', '', t or '')
    return re.sub(r'[^a-z0-9 ]', '', t.lower()).strip()


def bare(title):
    return re.sub(r'\s*\(.*?\)\s*$', '', title or '').strip()


def really_named(orig, n, text):
    """Guard against short titles that are also ordinary English.

    "One Day" is a book on the shelf and also two words in any sentence about a day. For titles of
    three words or fewer, insist on the title's own capitalisation in the raw answer, so `One Day`
    counts and `one day the narrator` does not. A title in italics or quotes still counts.
    """
    b = bare(orig)
    if b in AMBIGUOUS:
        return False
    if len(n.split()) > 3:
        return True
    return re.search(r'(?<![A-Za-z])%s(?![A-Za-z])' % re.escape(b), text or '') is not None


def abstained(text):
    """Did it say plainly that it could not answer? Shirley's ruling of 10 Sep 2026 makes an
    all-runs refusal `partial`, so this pattern decides a verdict and is worth reading."""
    return bool(ABSTAIN.search((text or '').lower()))


def named_outside(text, context, titles, question=''):
    """Books named in the answer that were not in the context, and were not named by the question.

    Q3 asks about The Fellowship of the Ring by name; repeating it back invents nothing.
    """
    low = ' ' + re.sub(r'[^a-z0-9 ]', ' ', (text or '').lower()) + ' '
    named = [o for o, n in titles if n and len(n) > 6 and (' ' + n + ' ') in low and really_named(o, n, text)]
    in_context = {c.get('id') for c in (context or [])}
    qlow = ' ' + re.sub(r'[^a-z0-9 ]', ' ', (question or '').lower()) + ' '
    from_question = {o for o, n in titles if n and len(n) > 6 and (' ' + n + ' ') in qlow}
    return named, sorted(set(named) - set(in_context) - from_question)


def checks(text, context, expects, titles, question=''):
    named, outside = named_outside(text, context, titles, question)
    hit = None
    if expects:
        want = [norm(e) for e in expects]
        got = [norm(c.get('id') or '') for c in (context or [])]
        hit = sum(1 for w in want if any(w and w in g for g in got))
    # a title-shaped phrase in quotes that matches nothing on the shelf. A prompt for a human, not
    # a verdict: an ordinary quotation from a note lands here too.
    invented = []
    for m in QUOTED.finditer(text or ''):
        cand = norm(m.group(1) or m.group(2) or '')
        if cand and len(cand.split()) <= 8 and not any(cand in n or n in cand for _, n in titles if n):
            invented.append((m.group(1) or m.group(2)).strip())
    return {'books_named': named, 'named_outside_context': outside,
            'retrieval_hit': hit, 'retrieval_expected': len(expects or []),
            'quoted_not_on_shelf': invented, 'abstained': abstained(text)}


def hedged(text, context):
    """A refusal that then answers a nearby question.

    "Your notes don't say which themes you like most - so I can only point to what recurs", then
    four paragraphs about what recurs. It is not the flat "I can't answer that" the word refusal
    suggests, and Shirley's ruling still makes it partial, but the sheet should say which kind it
    is or she has to read every run to find out.
    """
    if not abstained(text):
        return False
    t = ' '.join((text or '').split())
    if len(t) < 350:
        return False
    ids = {(c.get('id') or '').lower() for c in (context or [])}
    lowered = t.lower()
    return sum(1 for i in ids if i and i[:24] in lowered) >= 2
