import http from 'node:http';
const body = Buffer.alloc(4096, 'x');
http.createServer((req, res) => {
  if (req.url === '/internal/content-access') {
    res.writeHead(req.headers['x-test-content-deny'] === '1' ? 403 : 204); res.end(); return;
  }
  const delay = req.url.includes('/hold/') ? 700 : req.url.includes('sign-image') ? 60 : 0;
  setTimeout(() => {
    res.writeHead(200, { 'Content-Type': req.url.includes('entries') ? 'text/html' : 'application/octet-stream' });
    res.end(body);
  }, delay);
}).listen(18991, '127.0.0.1');
