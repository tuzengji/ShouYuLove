// Shared by the native file, image and XHR loaders, including decoder dependencies.
// A slot lasts until the response body has been consumed, not just its headers.
function createSceneDownloadQueue(doc, limit = 2) {
  const pending = [];
  let active = 0;
  const pump = () => {
    while (!doc.hidden && active < limit && pending.length) {
      const {start, resolve, reject} = pending.shift();
      active++;
      const finish = () => { active--; pump(); };
      Promise.resolve().then(start).then(
        value => { finish(); resolve(value); },
        error => { finish(); reject(error); }
      );
    }
  };
  doc.addEventListener('visibilitychange', pump);
  return {
    run(start, url = '') {
      // Embedded model images have no network cost and must not wait for a slot.
      if (/^(data|blob):/.test(url)) return Promise.resolve().then(start);
      return new Promise((resolve, reject) => {
        pending.push({start, resolve, reject});
        pump();
      });
    },
    get active() { return active; },
    get pending() { return pending.length; },
    limit
  };
}
const __sylSceneDownloads = createSceneDownloadQueue(document);
window.__sylSceneDownloads = __sylSceneDownloads;

function __sylQueueImage(image, url) {
  __sylSceneDownloads.run(() => new Promise((resolve, reject) => {
    const cleanup = () => {
      image.removeEventListener('load', loaded);
      image.removeEventListener('error', failed);
    };
    const loaded = () => { cleanup(); resolve(); };
    const failed = () => { cleanup(); reject(new Error('Scene image unavailable')); };
    image.addEventListener('load', loaded);
    image.addEventListener('error', failed);
    image.fetchPriority = 'low';
    image.src = url;
  }), url).catch(() => {}); // The native loader retains its own error callback.
}

function __sylQueueXHR(request, url) {
  __sylSceneDownloads.run(() => new Promise((resolve, reject) => {
    request.addEventListener('loadend', resolve, {once: true});
    try { request.send(); } catch (error) { reject(error); }
  }), url).catch(() => {}); // Success/error handling remains in the native loader.
}
