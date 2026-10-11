// Keep document navigation to the independent portfolio.
// The lightweight directory owns a document, so entering it also stops homepage audio.
document.addEventListener('click', event => {
  const anchor = event.target.closest?.('a[href]');
  if (!anchor || event.defaultPrevented || event.button !== 0 || event.metaKey || event.ctrlKey || event.shiftKey || event.altKey || anchor.target === '_blank') return;
  const url = new URL(anchor.href, location.href);
  if (url.origin !== location.origin || !/^\/(projects|portfolio)\/?$/.test(url.pathname)) return;
  event.preventDefault();
  event.stopImmediatePropagation();
  location.assign('/portfolio/' + url.search + url.hash);
}, true);
window.__sylFast = {
  ready(scroll, isReady) {
    const timer = setInterval(() => {
      if (!isReady()) return;
      const page = document.querySelector('#__nuxt .page');
      if (page && Number(getComputedStyle(page).opacity) < .95) return;
      clearInterval(timer);
      performance.mark('syl-native-ready');
    }, 50);
  }
};
