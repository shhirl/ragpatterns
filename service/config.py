"""Keys, model names and prices in one place, so a version's cost is reproducible.

Keys live in .env (git-ignored, never committed). Nothing here is imported by the deployed
service: the live panel replays the recorded run, so Railway needs no model keys at all.
"""
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA = os.path.join(ROOT, 'service', 'data')
LEDGER_DB = os.environ.get('LEDGER_DB') or os.path.join(DATA, 'library.sqlite')
INDEX_DB = os.environ.get('INDEX_DB') or os.path.join(DATA, 'index.sqlite')


def load_env(path=None):
    """Minimal .env reader. No dependency, and it never overwrites a real environment variable."""
    path = path or os.path.join(ROOT, '.env')
    if not os.path.exists(path):
        return
    for line in open(path, encoding='utf-8'):
        line = line.strip()
        if not line or line.startswith('#') or '=' not in line:
            continue
        k, _, v = line.partition('=')
        os.environ.setdefault(k.strip(), v.strip())


load_env()

# One generation model for every pattern (HANDOFF §3.10): different models per pattern would
# mean comparing models, not architectures.
GEN_MODEL = os.environ.get('GEN_MODEL', 'claude-opus-5')
EMBED_MODEL = os.environ.get('EMBED_MODEL', 'voyage-4')
RERANK_MODEL = os.environ.get('RERANK_MODEL', 'rerank-3')

# USD per million tokens. Voyage's current generation gives the first 200M tokens free, and this
# corpus is six orders of magnitude smaller than that, so retrieval genuinely costs nothing here.
PRICES = {
    'claude-opus-5': (5.00, 25.00),
    'claude-sonnet-5': (2.00, 10.00),
    'claude-haiku-4-5': (1.00, 5.00),
}
VOYAGE_FREE_ALLOWANCE = True


def usd(model, input_tokens, output_tokens):
    rate = PRICES.get(model)
    if not rate:
        return 0.0
    return round(input_tokens / 1e6 * rate[0] + output_tokens / 1e6 * rate[1], 6)


class Limiter(object):
    """Voyage holds an account with no payment method to 3 requests and 10,000 tokens a minute.
    One limiter per endpoint; it sleeps only as long as the window actually requires."""

    def __init__(self, rpm=3, tpm=10000):
        self.rpm, self.tpm, self.calls = rpm, tpm, []

    def wait(self, est_tokens):
        import time
        while True:
            now = time.time()
            self.calls = [(t, n) for t, n in self.calls if now - t < 60]
            if len(self.calls) < self.rpm and sum(n for _, n in self.calls) + est_tokens <= self.tpm:
                return
            time.sleep(min(21.0, 61 - (now - self.calls[0][0])))

    def record(self, tokens):
        import time
        self.calls.append((time.time(), tokens))
