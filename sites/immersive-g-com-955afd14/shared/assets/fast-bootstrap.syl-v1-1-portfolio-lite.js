// Keep the approved HTML readable while the native scene is being prepared.
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
      const early = document.getElementById('syl-early');
      if (!early) return;
      const originalY = window.scrollY;
      const sections = [...early.querySelectorAll('[data-syl-key]')];
      const anchor = sections.filter(e => e.getBoundingClientRect().top <= innerHeight / 3).at(-1);
      const key = anchor?.dataset.sylKey;
      const y = anchor?.getBoundingClientRect().top;
      early.remove();
      document.documentElement.classList.remove('syl-fast-early');
      document.getElementById('__nuxt').removeAttribute('aria-hidden');
      window.scrollTo(0, 0);
      requestAnimationFrame(() => {
        const target = key && [...document.querySelectorAll('#__nuxt [id], #__nuxt .projectBlock')].find(e => (e.dataset.uri || e.id) === key);
        if (target && key !== 'brand') scroll.scrollTo(target.getBoundingClientRect().top - y, 0);
        else if (originalY) scroll.scrollTo(originalY, 0);
      });
      performance.mark('syl-native-ready');
    }, 50);
  }
};
