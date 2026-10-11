// The document and all project links work before any scene resources are requested.
requestAnimationFrame(() => requestAnimationFrame(() => {
  performance.mark('syl-portfolio-readable');
  const background = document.querySelector('.portfolio-background');
  let started = false;
  const script = (src, type) => new Promise((resolve, reject) => {
    const node = document.createElement('script');
    node.src = src;
    if (type) node.type = type;
    node.onload = resolve;
    node.onerror = reject;
    document.head.append(node);
  });
  const load = async () => {
    if (started || document.hidden) return;
    started = true;
    performance.mark('syl-portfolio-scene-start');
    try {
      const response = await fetch(background.dataset.scene, {priority:'low'});
      if (!response.ok) throw new Error('Scene boot data unavailable');
      const scene = await response.json();
      // Reuse the original scene, shaders and inputs; never replace the readable list.
      window.__sylPortfolio = {
        ready(app, view) {
          this.app = app;
          this.view = view;
          document.getElementById('__nuxt').classList.add('scene-ready');
          performance.mark('syl-portfolio-background-ready');
        }
      };
      window.__IG_LOCAL_PAGES__ = scene.pages;
      window.__NUXT__ = {config:scene.config};
      const data = document.createElement('script');
      data.id = '__NUXT_DATA__';
      data.type = 'application/json';
      data.dataset.ssr = 'false';
      data.textContent = scene.data;
      document.body.append(data);
      const root = document.createElement('div');
      root.id = '__nuxt';
      root.inert = true;
      root.setAttribute('aria-hidden', 'true');
      document.body.append(root);
      await Promise.all(scene.styles.map(href => new Promise((resolve, reject) => {
        const url = new URL(href, location.href).href;
        if ([...document.querySelectorAll('link[rel="stylesheet"]')].some(link => link.href === url)) {
          resolve();
          return;
        }
        const link = document.createElement('link');
        link.rel = 'stylesheet';
        link.href = href;
        link.onload = resolve;
        link.onerror = reject;
        document.head.append(link);
      })));
      await script(scene.entry, 'module');
    } catch (error) {
      // An unavailable enhancement must not cover or disable the directory.
      performance.mark('syl-portfolio-scene-error');
      console.warn('Portfolio scene unavailable', error);
    }
  };
  setTimeout(() => {
    const schedule = () => {
      if (document.hidden) return;
      if (window.requestIdleCallback) requestIdleCallback(load, {timeout:5000});
      else load();
    };
    document.addEventListener('visibilitychange', schedule);
    schedule();
  }, 2000);
}));
