"""Exercise the production log format with an isolated loopback-only Nginx."""
from http.client import HTTPConnection
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import importlib.util
import json
from pathlib import Path
import shutil
import socket
import subprocess
import tempfile
from threading import Thread
import time
import unittest

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('visits', ROOT / 'deploy/private_stats/visits.py')
visits = importlib.util.module_from_spec(spec)
spec.loader.exec_module(visits)
NGINX = shutil.which('nginx')


class Upstream(BaseHTTPRequestHandler):
    def do_GET(self):
        content_type = 'application/json' if self.path.startswith('/api/') else 'text/html'
        self.send_response(200)
        self.send_header('Content-Type', content_type)
        self.end_headers()
        self.wfile.write(b'{}' if content_type == 'application/json' else b'<html>Upstream page</html>')

    def log_message(self, *args):
        pass


@unittest.skipUnless(NGINX, 'Nginx is required for the integration test')
class NginxStatisticsTests(unittest.TestCase):
    def test_all_routes_original_paths_and_document_filter(self):
        with tempfile.TemporaryDirectory(prefix='syl-stats-test-') as folder:
            root = Path(folder)
            root.chmod(0o755)
            web = root / 'www'
            web.mkdir()
            for name, body in [('index.html', '<html>Home</html>'), ('future/new/index.html', '<html>Future</html>'),
                               ('static.css', 'body{}'), ('data.json', '{}')]:
                path = web / name
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_text(body)
            upstream = ThreadingHTTPServer(('127.0.0.1', 0), Upstream)
            thread = Thread(target=upstream.serve_forever, daemon=True)
            thread.start()
            self.addCleanup(thread.join)
            self.addCleanup(upstream.server_close)
            self.addCleanup(upstream.shutdown)
            with socket.socket() as port_finder:
                port_finder.bind(('127.0.0.1', 0))
                port = port_finder.getsockname()[1]
            config = root / 'nginx.conf'
            config.write_text('''worker_processes 1;
error_log "''' + str(root/'error.log') + '''";
pid "''' + str(root/'nginx.pid') + '''";
events { worker_connections 64; }
http {
    types { text/html html; text/css css; application/json json; }
    include "''' + str(ROOT/'deploy/private_stats/nginx-format.conf') + '''";
    server {
        listen 127.0.0.1:''' + str(port) + ''';
        server_name shouyulove.cn;
        root "''' + str(web) + '''";
        access_log "''' + str(root/'events.log') + '''" syl_private_visits if=$syl_visit_html;
        location /rewrite/ { try_files $uri /index.html; }
        location /proxy/ { proxy_pass http://127.0.0.1:''' + str(upstream.server_port) + '''/; }
        location = /xhtml { default_type application/xhtml+xml; return 200 '<html>XHTML</html>'; }
        location / { index index.html; }
    }
}''')
            subprocess.run([NGINX, '-t', '-p', folder, '-c', str(config)], check=True, capture_output=True)
            process = subprocess.Popen([NGINX, '-p', folder, '-c', str(config), '-g', 'daemon off;'], stdout=subprocess.DEVNULL, stderr=subprocess.PIPE)
            try:
                for _ in range(60):
                    if process.poll() is not None:
                        self.fail(process.stderr.read().decode())
                    try:
                        with socket.create_connection(('127.0.0.1', port), timeout=.1):
                            break
                    except OSError:
                        time.sleep(.05)
                else:
                    self.fail('Isolated Nginx did not start')

                def request(path, extra=None, method='GET'):
                    client = HTTPConnection('127.0.0.1', port, timeout=5)
                    headers = {'Host':'shouyulove.cn','User-Agent':'Browser','Sec-Fetch-Dest':'document','Accept':'text/html'}
                    headers.update(extra or {})
                    try:
                        client.request(method,path,headers=headers)
                        response = client.getresponse()
                        status, etag = response.status, response.getheader('ETag')
                        response.read()
                        return status, etag
                    finally:
                        client.close()

                status, etag = request('/')
                self.assertEqual(status,200)
                for path in ['/future/new/', '/rewrite/deep/page?token=must-not-be-logged', '/proxy/new/page', '/xhtml']:
                    self.assertEqual(request(path)[0],200)
                self.assertEqual(request('/',{'If-None-Match':etag})[0],304)
                css_status, css_etag = request('/static.css',{'Sec-Fetch-Dest':'style'})
                self.assertEqual(css_status,200)
                self.assertEqual(request('/static.css',{'Sec-Fetch-Dest':'style','If-None-Match':css_etag})[0],304)
                self.assertEqual(request('/proxy/api/items',{'Sec-Fetch-Dest':'empty'})[0],200)
                request('/future/new/',{'Purpose':'prefetch'})
                request('/future/new/',{'Sec-Purpose':'prefetch;prerender'})
                request('/future/new/',{'Sec-Fetch-Dest':'empty'})
                request('/future/new/',{'User-Agent':'ShouYuLove-QA'})
                self.assertEqual(request('/missing')[0],404)
                request('/',method='HEAD')
                # New files need neither a code change nor a configuration reload.
                (web/'brand-new.html').write_text('<html>Added after startup</html>')
                self.assertEqual(request('/brand-new.html')[0],200)
            finally:
                process.terminate()
                process.communicate(timeout=10)
            raw = (root/'events.log').read_text()
            self.assertNotIn('must-not-be-logged',raw)
            events = [json.loads(line) for line in raw.splitlines()]
            connection,key = visits.open_database(root/'private')
            accepted = [event['path'] for event in events if visits.record(connection,key,event)]
            connection.close()
            self.assertCountEqual(accepted,['/','/future/new/','/rewrite/deep/page','/proxy/new/page','/xhtml','/','/brand-new.html'])
            result = visits.report(root/'private/visits.sqlite')
            self.assertEqual(result['period'],dict(views=7,visitors=1))
            self.assertEqual(len(result['pages']),6)
            self.assertNotIn('/static.css', [p['path'] for p in result['pages']])


if __name__ == '__main__':
    unittest.main()
