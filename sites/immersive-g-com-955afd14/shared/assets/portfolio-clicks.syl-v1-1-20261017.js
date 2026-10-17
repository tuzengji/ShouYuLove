// Record activations without delaying the original link or its new tab.
(() => {
  const track = (event) => {
    if (!event.isTrusted || event.defaultPrevented ||
        event.button !== (event.type === 'auxclick' ? 1 : 0)) return;
    const link = event.target instanceof Element &&
      event.target.closest('#portfolio .portfolio-link[data-project]');
    if (!link) return;
    const endpoint = '/__syl/portfolio-click/' + encodeURIComponent(link.dataset.project);
    try {
      if (navigator.sendBeacon?.(endpoint)) return;
    } catch (_) { /* Navigation remains usable when tracking is blocked. */ }
    try {
      fetch(endpoint, { method: 'POST', keepalive: true, mode: 'same-origin', credentials: 'omit' })
        .catch(() => {});
    } catch (_) { /* Older browsers may not support keepalive. */ }
  };
  document.addEventListener('click', track);
  document.addEventListener('auxclick', track);
})();
