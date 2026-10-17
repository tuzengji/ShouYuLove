import http2 from 'node:http2';
import assert from 'node:assert/strict';
const base = 'https://127.0.0.1:18992';
const clients = new Set();
function connect() {
  const client = http2.connect(base, { rejectUnauthorized: false, servername: 'shouyulove.cn' });
  clients.add(client);
  return client;
}
function close(client) { client.close(); clients.delete(client); }
function request(client, path, cookie, extra = {}) {
  return new Promise((resolve, reject) => {
    const started = performance.now();
    const stream = client.request({ ':path': path, 'user-agent': 'ShouYuLove-QA CampusSimulation/1',
      ...(cookie ? { cookie } : {}), ...extra });
    let headers, bytes = 0;
    stream.on('response', h => { headers = h; });
    stream.on('data', b => { bytes += b.length; });
    stream.on('error', reject);
    stream.on('end', () => resolve({ status: headers[':status'], headers, bytes, ms: performance.now() - started }));
    stream.end();
  });
}
function token(response) {
  const cookies = response.headers['set-cookie'] || [];
  const cookie = cookies.find(c => c.startsWith('syl_dict_session='));
  assert.ok(cookie, 'server issues a signed session on navigation');
  return cookie.split(';')[0];
}
async function bootstrap(client) { return token(await request(client, '/dict/entries', null, { accept: 'text/html' })); }
function summary(results) {
  const times = results.map(r => r.ms).sort((a, b) => a - b);
  const counts = {};
  for (const r of results) counts[r.status] = (counts[r.status] || 0) + 1;
  return { requests: results.length, statuses: counts, p95_ms: Math.round(times[Math.floor(times.length * .95)]), max_ms: Math.round(times.at(-1)) };
}
try {
  const report = { scenarios: [] };
  const oldClients = [connect(), connect(), connect()];
  const old = await Promise.all(oldClients.flatMap(c => Array.from({ length: 32 }, (_, i) => request(c, `/baseline/${i}`))));
  assert.ok(old.some(r => r.status === 429), 'control reproduces the old shared-IP failure');
  for (const c of oldClients) close(c);
  report.old_limit = summary(old);
  for (const users of [30, 50, 100]) {
    const results = [];
    const group = await Promise.all(Array.from({ length: users }, async () => {
      const client = connect();
      const page = await request(client, '/dict/entries', null, { accept: 'text/html' });
      results.push(page);
      return { client, cookie: token(page) };
    }));
    for (const round of [0, 1]) {
      await Promise.all(group.flatMap(({ client, cookie }) => [
        ...Array.from({ length: 32 }, (_, i) => request(client, `/dict/sign-image/${round * 32 + i}`, cookie)),
        request(client, `/dict/entries?page=${round + 1}&q=qa`, cookie, { accept: 'text/html' }),
        request(client, '/dict/static/style.css', cookie),
        request(client, '/dict/static/app.js', cookie),
      ]).map(p => p.then(r => results.push(r))));
    }
    assert.ok(results.every(r => r.status === 200), JSON.stringify(summary(results)));
    for (const { client } of group) close(client);
    report.scenarios.push({ users, same_ip: true, same_user_agent: true, ...summary(results) });
    console.log(JSON.stringify(report.scenarios.at(-1)));
  }
  const client = connect(), cookie = await bootstrap(client);
  const a = connect(), b = connect();
  const concurrency = await Promise.all([client, a, b].flatMap(c => Array.from({ length: 32 }, (_, i) => request(c, `/dict/hold/${i}`, cookie))));
  assert.ok(concurrency.some(r => r.status === 429), 'one browser cannot exceed 64 active requests');
  assert.ok(concurrency.filter(r => r.status === 200).length <= 64);
  close(a); close(b);
  const peer = await bootstrap(client);
  assert.equal((await request(client, '/dict/sign-image/1', peer)).status, 200);
  const rateCookie = await bootstrap(client);
  const rates = [];
  for (let i = 0; i < 160; i++) rates.push(await request(client, '/dict/entry/1', rateCookie));
  assert.ok(rates.some(r => r.status === 429 && r.headers['retry-after']), 'rate rejection includes retry advice');
  const forged = await request(client, '/dict/sign-image/1', 'syl_dict_session=' + 'f'.repeat(32) + '.1999999999.' + 'A'.repeat(22));
  assert.equal(forged.status, 429);
  const deniedVideo = await request(client, '/dict/video-files/qa.mp4', peer, { 'x-test-content-deny': '1' });
  assert.equal(deniedVideo.status, 403, 'existing content restriction survives new guard');
  const video = await request(client, '/dict/video-files/qa.mp4', peer, { range: 'bytes=0-15' });
  assert.equal(video.status, 206);
  const fallbackVideo = await request(client, '/dict/video-files/missing.mp4', peer);
  assert.equal(fallbackVideo.status, 200);
  const fallbackDenied = await request(client, '/dict/video-files/missing.mp4', peer, { 'x-test-content-deny': '1' });
  assert.equal(fallbackDenied.status, 403);
  const queries = await Promise.all(Array.from({ length: 100 }, async () => {
    const c = connect(), ck = await bootstrap(c);
    const r = await request(c, '/dict/api/structured-action-search', ck, { ':method': 'POST' });
    close(c);
    return r;
  }));
  assert.ok(queries.every(r => r.status === 200), JSON.stringify(summary(queries)));
  const expensive = [];
  for (let i = 0; i < 10; i++) expensive.push(await request(client, '/dict/admin/login', peer, { ':method': 'POST' }));
  assert.ok(expensive.some(r => r.status === 429), 'sensitive routes have their own stricter limit');
  const rotation = [];
  for (let i = 0; i < 330; i++) rotation.push(await request(client, '/dict/entries', null, { accept: 'text/html' }));
  assert.ok(rotation.some(r => r.status === 429), 'fresh cookie rotation has a separate IP backstop');
  assert.equal((await request(client, '/dict/sign-image/2', peer)).status, 200);
  assert.equal((await request(client, '/dict/static/style.css')).status, 200);
  assert.equal((await request(client, '/unrelated/')).status, 200);
  report.protection = {
    concurrency: summary(concurrency), request_rate: summary(rates), cookie_rotation: summary(rotation),
    forged_cookie: forged.status, restricted_video: deniedVideo.status,
    video_range: video.status, fallback_video: fallbackVideo.status,
    fallback_restriction: fallbackDenied.status, unaffected_peer_and_public_assets: true,
    unrelated_project: true, simultaneous_query_starts: summary(queries), sensitive_abuse: summary(expensive),
  };
  console.log(JSON.stringify(report));
} finally { for (const client of clients) client.destroy(); }
