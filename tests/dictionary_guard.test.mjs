import test from 'node:test';
import assert from 'node:assert/strict';
import { Guard, COOKIE, POLICY, issue, verify } from '../deploy/dictionary_guard/guard.mjs';

const secret = 'a'.repeat(64);
const start = 1792240000;
const page = { 'x-original-uri': '/dict/entries', 'x-original-method': 'GET',
  'x-real-ip': '192.0.2.1', 'x-forwarded-proto': 'https', accept: 'text/html' };
function headers(token, path = '/dict/sign-image/1') {
  return { ...page, accept: 'image/avif,image/*', cookie: `${COOKIE}=${token}`, 'x-original-uri': path };
}
function bootstrap(guard) {
  const r = guard.check(page);
  assert.equal(r.status, 204);
  assert.match(r.setCookie, /HttpOnly; SameSite=Lax; Secure$/);
  return r.setCookie.split(';')[0].slice(COOKIE.length + 1);
}

test('100 identical browsers behind one IP get independent signed sessions', () => {
  const guard = new Guard(secret, () => start);
  const tokens = Array.from({ length: 100 }, () => bootstrap(guard));
  assert.equal(new Set(tokens).size, 100);
  for (const token of tokens) for (let i = 0; i < 100; i++)
    assert.equal(guard.check(headers(token, `/dict/sign-image/${i}`)).status, 204);
});
test('forged, expired, duplicate and cross-scope cookies cannot authorize content', () => {
  const guard = new Guard(secret, () => start);
  const token = bootstrap(guard);
  const forged = token.slice(0, -1) + (token.endsWith('a') ? 'b' : 'a');
  assert.equal(verify(secret, forged, start), null);
  assert.equal(guard.check(headers(forged)).status, 401);
  assert.equal(guard.check(headers(issue(secret, start - POLICY.ttl - 1))).status, 401);
  assert.equal(guard.check({ ...headers(token), cookie: `${COOKIE}=${token}; ${COOKIE}=${token}` }).status, 401);
  assert.equal(guard.check(headers(token, '/signtrace/')).status, 403);
  assert.equal(guard.check({ ...page, 'x-original-method': 'POST' }).status, 401);
});
test('session rotation is bounded without blocking existing classmates', () => {
  let now = start;
  const guard = new Guard(secret, () => now);
  const existing = bootstrap(guard);
  for (let i = 1; i < POLICY.mintBurst; i++) bootstrap(guard);
  assert.equal(guard.check(page).reason, 'session_rotation');
  assert.equal(guard.check(headers(existing)).status, 204);
  now += 1;
  bootstrap(guard);
});
test('sustained distinct-item scraping is stopped, repeated study and peers still work', () => {
  let now = start;
  const guard = new Guard(secret, () => now);
  const token = bootstrap(guard), peer = bootstrap(guard);
  for (let i = 0; i < POLICY.distinct; i++) {
    now += 0.25; // 4 r/s is below the ordinary 10 r/s limit.
    assert.equal(guard.check(headers(token, `/dict/sign-image/${i}`)).status, 204);
  }
  const denied = guard.check(headers(token, '/dict/sign-image/99999'));
  assert.equal(denied.reason, 'bulk_enumeration');
  assert.ok(denied.retry > 0);
  assert.equal(guard.check(headers(token, '/dict/sign-image/0')).status, 204);
  assert.equal(guard.check(headers(peer, '/dict/sign-image/99999')).status, 204);
  now = start + POLICY.window + 1;
  assert.equal(guard.check(headers(token, '/dict/sign-image/99999')).status, 204);
});
