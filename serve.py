#!/usr/bin/env python3
"""静态镜像服务器,兼容 next/image 的 /_next/image?url=... 请求。"""
import http.server, urllib.parse, os, sys

ROOT = os.path.dirname(os.path.abspath(__file__))
PORT = int(sys.argv[1]) if len(sys.argv) > 1 else 8931

class Handler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *a, **kw):
        super().__init__(*a, directory=ROOT, **kw)

    def do_GET(self):
        parsed = urllib.parse.urlparse(self.path)
        if parsed.path == '/_next/image':
            qs = urllib.parse.parse_qs(parsed.query)
            url = qs.get('url', [''])[0]
            if url:
                self.path = urllib.parse.unquote(url)
        super().do_GET()

    def log_message(self, fmt, *args):
        pass

    def end_headers(self):
        self.send_header('Cache-Control', 'no-store')
        super().end_headers()

with http.server.ThreadingHTTPServer(('127.0.0.1', PORT), Handler) as srv:
    print(f'serving on http://127.0.0.1:{PORT}')
    srv.serve_forever()
