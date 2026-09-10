"""Local workbench: see and interact with what is built. Not deployed, never will be.

    python3 service/workbench.py        then open http://localhost:8790

One page: the nine questions, each with a button per route that can answer it - the ledger's
forced SQL path, naive, rerank - a free SQL box against the read-only tool, and the full
answer() result. Unlike the public panel, naive and rerank really run here: this is a local
page, the keys are Shirley's, and a click costs about half a cent.

Run it with the virtualenv's Python, which has the model SDKs:
    .venv/bin/python service/workbench.py        then open http://localhost:8790
"""
import json, os, sys, html
from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib.parse import parse_qs, urlparse

ROOT = os.path.join(os.path.dirname(__file__), '..')
sys.path.insert(0, ROOT)
from service.answer import answer
from service.retrievers import sql
from service.patterns.sql_forced import QUERIES

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

PAGE = """<!DOCTYPE html><html lang="en"><head><meta charset="utf-8"><title>Workbench · RAG patterns, side by side</title>
<style>
:root{--bg:#fbfaf7;--ink:#1a1a1a;--mute:#7a7568;--line:#e5e2da;--soft:#f3f1ea;--acc:#1f5e4e}
body{margin:0;font-family:"Iowan Old Style",Palatino,Georgia,serif;background:var(--bg);color:var(--ink);line-height:1.5}
.wrap{max-width:1100px;margin:0 auto;padding:28px 22px 60px}
.k{font-family:-apple-system,Inter,Arial,sans-serif;font-size:11.5px;letter-spacing:.12em;text-transform:uppercase;color:var(--mute)}
h1{font-weight:500;font-size:30px;margin:6px 0 4px}
p.sub{color:var(--mute);margin:0 0 22px;font-size:15px}
.grid{display:grid;grid-template-columns:360px minmax(0,1fr);gap:22px}
.q{display:block;width:100%;text-align:left;border:1px solid var(--line);background:#fff;padding:10px 12px;margin:0 0 8px;cursor:pointer;font:inherit;font-size:14px;line-height:1.35}
.q b{font-family:-apple-system,Inter,Arial,sans-serif;font-size:11px;letter-spacing:.1em;color:var(--acc);margin-right:8px}
.q.off{color:var(--mute);cursor:default}
.q .rs{margin-top:7px;display:flex;gap:6px;flex-wrap:wrap}
.q .r{font-family:var(--sans,system-ui);font-size:10.5px;letter-spacing:.09em;text-transform:uppercase;border:1px solid #1a1a1a;background:#fff;padding:4px 10px;cursor:pointer}
.q .r:hover{background:#1a1a1a;color:#fbfaf7}.q.off small{display:block;font-family:-apple-system,Inter,Arial,sans-serif;font-size:11.5px;margin-top:3px}
textarea{width:100%;min-height:90px;font-family:"SF Mono",Menlo,monospace;font-size:12.5px;padding:10px;border:1px solid var(--line);background:#fff;box-sizing:border-box}
button.run{font-family:-apple-system,Inter,Arial,sans-serif;font-size:12px;letter-spacing:.06em;text-transform:uppercase;font-weight:600;background:var(--ink);color:#fff;border:0;padding:9px 14px;cursor:pointer;margin-top:8px}
.out{border:1px solid var(--ink);background:#fff;padding:16px 18px;min-height:200px}
.out .route{font-family:"SF Mono",Menlo,monospace;font-size:11.5px;color:var(--mute);margin-bottom:10px}
.out .ans{white-space:pre-line;font-size:16px;line-height:1.5;padding:12px 14px;background:var(--soft);border-left:3px solid var(--acc);margin:10px 0}
pre{font-family:"SF Mono",Menlo,monospace;font-size:11.5px;background:var(--soft);padding:12px;overflow:auto;margin:10px 0 0}
table{border-collapse:collapse;width:100%;font-family:-apple-system,Inter,Arial,sans-serif;font-size:13px;margin-top:10px}
th{text-align:left;border-bottom:1px solid var(--ink);padding:6px 8px;font-size:10.5px;letter-spacing:.1em;text-transform:uppercase}
td{border-bottom:1px solid var(--line);padding:6px 8px;vertical-align:top}
.err{color:#9c2f2f;font-family:-apple-system,Inter,Arial,sans-serif;font-size:13px}
@media(max-width:800px){.grid{grid-template-columns:1fr}}
</style></head><body><div class="wrap">
<p class="k">Local workbench · v1 · not deployed</p>
<h1>Ask the ledger</h1>
<p class="sub">What exists today: the SQLite ledger, the read-only SQL tool and its forced path, the vector index over her highlights and notes, and two patterns - naive and retrieve-and-rerank. The ledger path calls no model. Naive and rerank each call Claude Opus 5 once, for real, and the result shows what it cost.</p>
<div class="grid">
<div>
<p class="k">The nine questions</p>
%QUESTIONS%
<p class="k" style="margin-top:22px">Free SQL against the tool</p>
<form method="post" action="/sql"><textarea name="sql">SELECT title, author, my_rating, avg_rating FROM read_books WHERE my_rating <= 2 AND avg_rating >= 4.2 ORDER BY avg_rating DESC</textarea>
<button class="run" type="submit">Run (read-only)</button></form>
<p class="k" style="margin-top:14px">Schema</p><pre>%SCHEMA%</pre>
</div>
<div class="out">%OUT%</div>
</div></div></body></html>"""


def render_out(result=None, rows=None, err=None, title=''):
    if err:
        return f'<p class="k">{html.escape(title)}</p><p class="err">{html.escape(err)}</p>'
    if rows is not None:
        if not rows:
            return f'<p class="k">{html.escape(title)}</p><p>No rows.</p>'
        cols = list(rows[0].keys())
        body = ''.join('<tr>' + ''.join(f'<td>{html.escape(str(r[c]))}</td>' for c in cols) + '</tr>' for r in rows)
        return f'<p class="k">{html.escape(title)} · {len(rows)} rows</p><table><tr>' + ''.join(f'<th>{html.escape(c)}</th>' for c in cols) + '</tr>' + body + '</table>'
    if result is not None:
        meta = json.dumps({k: v for k, v in result.items() if k not in ('answer', 'sql')}, indent=1, ensure_ascii=False)
        return (f'<p class="k">{html.escape(title)}</p><div class="route">route: {html.escape(result["route"])} · calls: {result["calls"]} · {result["ms"]} ms</div>'
                f'<div class="ans">{html.escape(result["answer"])}</div>'
                f'<p class="k">query the tool ran</p><pre>{html.escape(result.get("sql", ""))}</pre>'
                f'<p class="k">answer() result</p><pre>{html.escape(meta)}</pre>')
    return '<p class="k">Pick a question or run a query.</p>'


def routes_for(qid, waits):
    """Which routes can answer this question today. The ledger path only has a query for the
    numbers questions; naive and rerank can be asked anything, and failing is a result."""
    if waits:
        return []
    out = ['naive', 'rerank']
    if qid in QUERIES:
        out.insert(0, 'sql')
    return out


def page(out_html):
    qs = ''
    for qid, text, waits in QUESTIONS:
        routes = routes_for(qid, waits)
        if not routes:
            qs += f'<div class="q off"><b>{qid}</b>{html.escape(text)}<small>{html.escape(waits)}</small></div>'
            continue
        buttons = ''.join(
            f'<form method="post" action="/ask" style="margin:0;display:inline">'
            f'<input type="hidden" name="qid" value="{qid}"><input type="hidden" name="pattern" value="{r}">'
            f'<button class="r" type="submit">{"the ledger" if r == "sql" else r}</button></form>'
            for r in routes)
        qs += (f'<div class="q"><b>{qid}</b>{html.escape(text)}'
               f'<div class="rs">{buttons}</div></div>')
    return PAGE.replace('%QUESTIONS%', qs).replace('%SCHEMA%', html.escape(sql.SCHEMA)).replace('%OUT%', out_html)


class H(BaseHTTPRequestHandler):
    def _send(self, body):
        data = body.encode('utf-8')
        self.send_response(200); self.send_header('Content-Type', 'text/html; charset=utf-8'); self.send_header('Content-Length', str(len(data))); self.end_headers(); self.wfile.write(data)

    def do_GET(self):
        self._send(page(render_out()))

    def do_POST(self):
        n = int(self.headers.get('Content-Length', 0)); form = parse_qs(self.rfile.read(n).decode('utf-8'))
        path = urlparse(self.path).path
        try:
            if path == '/ask':
                qid = form.get('qid', ['Q2'])[0]
                pattern = form.get('pattern', ['sql'])[0]
                text = dict((q, t) for q, t, _ in QUESTIONS)[qid]
                if pattern == 'sql':
                    r = answer(text, force_route='sql', qid=qid)
                else:
                    r = answer(text, pattern=pattern, qid=qid)
                self._send(page(render_out(result=r, title=f'{qid} · {pattern} · {text}')))
            elif path == '/sql':
                q = form.get('sql', [''])[0]
                rows, truncated = sql.run(q)
                self._send(page(render_out(rows=rows, title='SQL' + (' (truncated at 50 rows)' if truncated else ''))))
            else:
                self._send(page(render_out(err='unknown action')))
        except Exception as e:  # noqa: BLE001
            self._send(page(render_out(err=str(e), title='refused')))

    def log_message(self, *a):
        pass


if __name__ == '__main__':
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 8790
    print(f'workbench on http://localhost:{port}  (ctrl-c to stop)')
    HTTPServer(('127.0.0.1', port), H).serve_forever()
