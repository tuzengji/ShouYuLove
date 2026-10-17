import { createHash, randomBytes, timingSafeEqual } from 'node:crypto';
import { createServer } from 'node:http';
import { readFileSync, chmodSync } from 'node:fs';
import { pathToFileURL } from 'node:url';

export const COOKIE = 'syl_dict_session';
export const POLICY = Object.freeze({
  ttl: 86400, mintBurst: 300, mintRate: 2,
  window: 600, distinct: 1200, maxSessions: 10000, maxItems: 100000,
});

// Matches Nginx secure_link_md5; fixed-width fields prevent ambiguous inputs.
export function signature(secret, sid, expires) {
  return createHash('md5').update(`${expires} ${sid} ${secret}`).digest('base64url');
}
export function issue(secret, now) {
  const sid = randomBytes(16).toString('hex');
  const expires = Math.floor(now) + POLICY.ttl;
  return `${sid}.${expires}.${signature(secret, sid, expires)}`;
}
export function verify(secret, token, now) {
  const match = /^([a-f0-9]{32})\.([0-9]{10})\.([A-Za-z0-9_-]{22})$/.exec(token);
  if (!match || +match[2] <= now || +match[2] > now + POLICY.ttl + 5) return null;
  const expected = signature(secret, match[1], match[2]);
  return timingSafeEqual(Buffer.from(expected), Buffer.from(match[3])) ? match[1] : null;
}
function cookieValue(header = '') {
  const values = header.split(';').map(s => s.trim()).filter(s => s.startsWith(`${COOKIE}=`));
  return values.length === 1 ? values[0].slice(COOKIE.length + 1) : '';
}
function contentKey(path) {
  const match = /^\/dict\/(entry|sign-image|inline-image|source-image|ai-video|ai-video-source)\/([0-9]+)(?:\/|$)/.exec(path);
  if (match) return `${match[1]}:${match[2]}`;
  if (path.startsWith('/dict/video-files/')) return path;
  return null;
}

export class Guard {
  constructor(secret, now = () => Date.now() / 1000) {
    this.secret = secret;
    this.now = now;
    this.sessions = new Map();
    this.issuers = new Map();
    this.items = 0;
    this.lastSweep = 0;
  }
  sweep(now) {
    if (now - this.lastSweep < 30) return;
    this.lastSweep = now;
    for (const [key, value] of this.sessions) {
      if (now - value.start >= POLICY.window) {
        this.items -= value.seen.size;
        this.sessions.delete(key);
      }
    }
    for (const [key, value] of this.issuers) {
      if (now - value.time >= POLICY.window) this.issuers.delete(key);
    }
  }
  check(headers) {
    const now = this.now();
    this.sweep(now);
    const path = String(headers['x-original-uri'] || '').split('?')[0];
    if (!path.startsWith('/dict/')) return { status: 403, reason: 'wrong_scope' };
    let token = cookieValue(headers.cookie);
    let sid = verify(this.secret, token, now);
    let setCookie;
    if (!sid) {
      // Only a document navigation bootstraps a new identity. Arbitrary cookies
      // and direct asset crawls cannot create fresh quota on every request.
      const method = headers['x-original-method'];
      const navigation = headers['sec-fetch-dest'] === 'document'
        || String(headers.accept || '').includes('text/html');
      if (!['GET', 'HEAD'].includes(method) || !navigation)
        return { status: 401, reason: 'session_required', retry: 1 };
      const ip = headers['x-real-ip'];
      if (!ip) return { status: 403, reason: 'missing_peer' };
      if (!this.issuers.has(ip) && this.issuers.size >= POLICY.maxSessions)
        return { status: 401, reason: 'issuer_capacity', retry: 30 };
      const bucket = this.issuers.get(ip) || { tokens: POLICY.mintBurst, time: now };
      bucket.tokens = Math.min(POLICY.mintBurst, bucket.tokens + (now - bucket.time) * POLICY.mintRate);
      bucket.time = now;
      this.issuers.set(ip, bucket);
      if (bucket.tokens < 1) return { status: 401, reason: 'session_rotation', retry: 1 };
      bucket.tokens -= 1;
      token = issue(this.secret, now);
      sid = verify(this.secret, token, now);
      const secure = headers['x-forwarded-proto'] === 'https' ? '; Secure' : '';
      setCookie = `${COOKIE}=${token}; Path=/dict/; Max-Age=${POLICY.ttl}; HttpOnly; SameSite=Lax${secure}`;
    }
    let state = this.sessions.get(sid);
    if (!state || now - state.start >= POLICY.window) {
      if (!state && this.sessions.size >= POLICY.maxSessions)
        return { status: 401, reason: 'session_capacity', retry: 30 };
      if (state) this.items -= state.seen.size;
      state = { start: now, seen: new Set() };
      this.sessions.set(sid, state);
    }
    const key = contentKey(path);
    if (key && !state.seen.has(key)) {
      if (state.seen.size >= POLICY.distinct)
        return { status: 401, reason: 'bulk_enumeration', retry: Math.ceil(POLICY.window - (now - state.start)) };
      if (this.items >= POLICY.maxItems)
        return { status: 401, reason: 'tracking_capacity', retry: 30 };
      state.seen.add(key);
      this.items += 1;
    }
    return { status: 204, reason: 'allowed', setCookie };
  }
}

export function start({ socket, secret }) {
  const guard = new Guard(secret);
  const server = createServer({ maxHeaderSize: 16384 }, (req, res) => {
    if (req.url === '/health') { res.writeHead(204); res.end(); return; }
    if (req.url !== '/check' || req.method !== 'GET') { res.writeHead(404); res.end(); return; }
    const result = guard.check(req.headers);
    const headers = { 'Cache-Control': 'no-store', 'X-Syl-Guard-Reason': result.reason };
    if (result.setCookie) headers['Set-Cookie'] = result.setCookie;
    if (result.retry) headers['Retry-After'] = String(result.retry);
    res.writeHead(result.status, headers);
    res.end();
  });
  server.headersTimeout = 5000;
  server.requestTimeout = 5000;
  server.keepAliveTimeout = 1000;
  server.listen({ path: socket, backlog: 4096 }, () => { chmodSync(socket, 0o600); console.log('Dictionary guard ready'); });
  process.on('SIGTERM', () => server.close(() => process.exit(0)));
  return server;
}
if (process.argv[1] && import.meta.url === pathToFileURL(process.argv[1]).href) {
  const keyPath = process.env.GUARD_SECRET_FILE || `${process.env.CREDENTIALS_DIRECTORY}/signing-key`;
  const secret = readFileSync(keyPath, 'utf8').trim();
  if (!/^[a-f0-9]{64}$/.test(secret)) throw new Error('Invalid signing key file');
  start({ socket: process.env.GUARD_SOCKET || '/run/shouyulove-dict-guard/guard.sock', secret });
}
