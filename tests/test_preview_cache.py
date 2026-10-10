"""Exercise actual HTTP responses for versioned, mutable and missing files."""
from functools import partial
from http.client import HTTPConnection
from pathlib import Path
import tempfile
from threading import Thread
import unittest

from serve import Handler, Server


class CachePolicyTests(unittest.TestCase):
    def test_versioned_assets_html_and_errors(self):
        with tempfile.TemporaryDirectory() as folder:
            for name in ['index.html', 'entry.syl-v1-1-fast.js', 'entry.AbCdEf12.js', 'plain.json']:
                (Path(folder) / name).write_text('test')
            class QuietHandler(Handler):
                def log_message(self, *args):
                    pass
            server = Server(('127.0.0.1', 0), partial(QuietHandler, directory=folder))
            thread = Thread(target=server.serve_forever, daemon=True)
            thread.start()
            try:
                for name, age in [('index.html', 'no-cache'), ('entry.syl-v1-1-fast.js', 'public, max-age=31536000, immutable'), ('entry.AbCdEf12.js', 'public, max-age=31536000, immutable'), ('plain.json', 'public, max-age=3600'), ('missing.syl-v1-1-fast.js', 'no-store')]:
                    with self.subTest(name=name):
                        client = HTTPConnection('127.0.0.1', server.server_port)
                        client.request('GET', '/' + name)
                        response = client.getresponse()
                        self.assertEqual(response.status, 404 if name.startswith('missing') else 200)
                        self.assertEqual(response.getheader('Cache-Control'), age)
                        response.read()
                        client.close()
            finally:
                server.shutdown()
                server.server_close()
                thread.join()
