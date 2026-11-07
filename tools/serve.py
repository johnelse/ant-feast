#!/usr/bin/env python3
"""Dev server for headless runs: serves the repo and saves POST bodies.

    python3 tools/serve.py [port]      (default 8766)

Test pages called with ?post=/name POST their output here; it is written to
tools/out/name. Plain `python3 -m http.server` is enough for playing.
"""
import http.server, os, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, 'tools', 'out')
os.makedirs(OUT, exist_ok=True)


class Handler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *a, **k):
        super().__init__(*a, directory=ROOT, **k)

    def do_POST(self):
        body = self.rfile.read(int(self.headers.get('Content-Length', 0)))
        name = self.path.strip('/').replace('/', '_') or 'post'
        with open(os.path.join(OUT, name), 'wb') as f:
            f.write(body)
        self.send_response(200)
        self.end_headers()

    def log_message(self, *a):
        pass


port = int(sys.argv[1]) if len(sys.argv) > 1 else 8766
http.server.ThreadingHTTPServer(('127.0.0.1', port), Handler).serve_forever()
