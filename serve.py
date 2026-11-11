#!/usr/bin/env python3
"""Preview the exported Astra frontend without changing its files."""

import argparse
import json
from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
import re
from urllib.parse import urlsplit

VERSIONED_RESOURCE = re.compile(r'\.(?:syl-v[0-9A-Za-z._-]+|[A-Za-z0-9_-]{8,})\.(?:js|css|woff2?|png|webp|ktx2|glb|json|mp3)$', re.I)
PORTFOLIO_CLICK = re.compile(r'^/__syl/portfolio-click/([a-z0-9][a-z0-9-]{0,79})$')
PROJECT_REDIRECTS = json.loads((Path(__file__).resolve().parent / 'deploy/project-redirects.json').read_text())


class Server(ThreadingHTTPServer):
    request_queue_size = 256


class Handler(SimpleHTTPRequestHandler):
    def redirect_directory(self):
        url = urlsplit(self.path)
        if url.path.startswith('/__syl/portfolio-click/'):
            self.send_error(405)
            return True
        if url.path in PROJECT_REDIRECTS:
            self.send_response(302)
            self.send_header('Location', PROJECT_REDIRECTS[url.path] + ('?' + url.query if url.query else ''))
            self.send_header('Content-Length', '0')
            self.end_headers()
            return True
        if url.path not in ('/projects', '/projects/', '/projects/index.html', '/portfolio'):
            return False
        self.send_response(308)
        self.send_header('Location', '/portfolio/' + ('?' + url.query if url.query else ''))
        self.send_header('Content-Length', '0')
        self.end_headers()
        return True

    def do_GET(self):
        if not self.redirect_directory():
            super().do_GET()

    def do_HEAD(self):
        if not self.redirect_directory():
            super().do_HEAD()

    def send_response(self, code, message=None):
        self.response_status = code
        super().send_response(code, message)

    def end_headers(self):
        path = urlsplit(self.path).path
        if self.response_status not in (200, 206, 304):
            cache = 'no-store'
        elif VERSIONED_RESOURCE.search(path):
            cache = 'public, max-age=31536000, immutable'
        elif path.endswith('.html') or path.endswith('/') or path.endswith('_payload.json'):
            cache = 'no-cache'
        else:
            cache = 'public, max-age=3600'
        self.send_header('Cache-Control', cache)
        self.send_header('X-Content-Type-Options', 'nosniff')
        if path.endswith('.html') or path.endswith('/'):
            self.send_header('Referrer-Policy', 'strict-origin-when-cross-origin')
        super().end_headers()

    def do_POST(self):
        route = urlsplit(self.path).path
        if PORTFOLIO_CLICK.fullmatch(route):
            try:
                length = int(self.headers.get('Content-Length', '0'))
            except ValueError:
                self.send_error(400)
                return
            if length < 0 or length > 1024:
                self.send_error(413 if length > 1024 else 400)
                return
            if length:
                self.rfile.read(length)
            host = self.headers.get('Host', '')
            origin = self.headers.get('Origin', '')
            referer = self.headers.get('Referer', '')
            expected_origins = {f'http://{host}', f'https://{host}'} if host else set()
            same_origin = origin in expected_origins
            from_portfolio = any(referer.startswith(base + '/portfolio/') for base in expected_origins)
            if not (same_origin and from_portfolio):
                self.send_error(403)
                return
            self.send_response(204)
            self.send_header('Content-Length', '0')
            self.end_headers()
            return
        if route.startswith('/__syl/portfolio-click/'):
            self.send_error(404)
            return
        if route != "/api/local-newsletter":
            self.send_error(405)
            return
        body = b'{"message":"Newsletter subscriptions are unavailable in this local preview."}'
        self.send_response(503)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--port", type=int, default=8038)
    parser.add_argument("--directory", default=str(Path(__file__).resolve().parent))
    args = parser.parse_args()
    with Server(("127.0.0.1", args.port), partial(Handler, directory=args.directory)) as server:
        print(f"Preview: http://127.0.0.1:{args.port}/", flush=True)
        server.serve_forever()
