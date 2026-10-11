// Keep the approved HTML readable while the native scene is being prepared.
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
