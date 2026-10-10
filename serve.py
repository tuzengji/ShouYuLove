#!/usr/bin/env python3
"""Preview the exported Astra frontend without changing its files."""

import argparse
from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
import re
from urllib.parse import urlsplit

VERSIONED_RESOURCE = re.compile(r'\.(?:syl-v[0-9A-Za-z._-]+|[A-Za-z0-9_-]{8,})\.(?:js|css|woff2?|png|webp|ktx2|glb|json|mp3)$', re.I)


class Server(ThreadingHTTPServer):
    request_queue_size = 256


class Handler(SimpleHTTPRequestHandler):
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
        super().end_headers()

    def do_POST(self):
        if self.path.split("?", 1)[0] != "/api/local-newsletter":
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
