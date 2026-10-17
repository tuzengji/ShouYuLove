import test from 'node:test';
import assert from 'node:assert/strict';
import {readFileSync} from 'node:fs';
import vm from 'node:vm';

function setup(hidden = false) {
  const document = new EventTarget();
  document.hidden = hidden;
  const window = {};
  vm.runInNewContext(readFileSync(new URL('../scripts/background_resources.js', import.meta.url), 'utf8'), {document, window, Promise});
  return {queue: window.__sylSceneDownloads, setHidden(value) {
    document.hidden = value;
    document.dispatchEvent(new Event('visibilitychange'));
  }};
}
const tick = () => new Promise(resolve => setImmediate(resolve));

test('two body downloads at a time; hidden pages drain but do not start queued work', async () => {
  const {queue, setHidden} = setup();
  const started = [], releases = [];
  const requests = Array.from({length: 6}, (_, i) => queue.run(() => {
    started.push(i);
    return new Promise(resolve => { releases[i] = () => resolve(i); });
  }));
  await tick();
  assert.deepEqual(started, [0, 1]);
  setHidden(true);
  releases[0](); releases[1]();
  await tick();
  assert.deepEqual(started, [0, 1]);
  assert.equal(queue.active, 0);
  assert.equal(queue.pending, 4);
  setHidden(false);
  await tick();
  assert.deepEqual(started, [0, 1, 2, 3]);
  releases[2](); releases[3]();
  await tick();
  releases[4](); releases[5]();
  assert.deepEqual(await Promise.all(requests), [0, 1, 2, 3, 4, 5]);
  assert.equal(queue.active, 0);
});

test('rejected and synchronously throwing downloads release slots', async () => {
  const {queue} = setup();
  const results = await Promise.allSettled([
    queue.run(() => { throw new Error('network'); }),
    queue.run(() => Promise.reject(new Error('decode'))),
    queue.run(() => 'next')
  ]);
  assert.deepEqual(results.map(r => r.status), ['rejected', 'rejected', 'fulfilled']);
  assert.equal(results[2].value, 'next');
  assert.equal(queue.active, 0);
});

test('initially hidden pages wait; embedded model images do not deadlock downloads', async () => {
  const {queue, setHidden} = setup(true);
  let started = false;
  const request = queue.run(() => { started = true; return 'network'; });
  assert.equal(await queue.run(() => 'embedded', 'blob:local-image'), 'embedded');
  await tick();
  assert.equal(started, false);
  setHidden(false);
  assert.equal(await request, 'network');
});

test('decoders can enqueue dependencies after a model download releases its slot', async () => {
  const {queue} = setup();
  const models = Array.from({length: 3}, () => queue.run(() => 'model')
    .then(() => queue.run(() => 'decoder')));
  assert.deepEqual(await Promise.all(models), ['decoder', 'decoder', 'decoder']);
  assert.equal(queue.active, 0);
});
