// Background enhancement starts only after the fully usable directory has painted.
requestAnimationFrame(() => requestAnimationFrame(() => {
  performance.mark('syl-portfolio-readable');
  const background = document.querySelector('.portfolio-background');
  const connection = navigator.connection;
  if (matchMedia('(prefers-reduced-motion:reduce)').matches || connection?.saveData || /(^|-)2g$/.test(connection?.effectiveType || '')) return;
  const load = () => {
    if (document.hidden) return;
    const image = new Image();
    image.fetchPriority = 'low';
    image.onload = () => {
      background.style.backgroundImage = `url("${background.dataset.texture}")`;
      background.classList.add('ready');
      performance.mark('syl-portfolio-background-ready');
    };
    image.src = background.dataset.texture;
  };
  setTimeout(() => {
    if (window.requestIdleCallback) requestIdleCallback(load, {timeout:5000});
    else load();
  }, 2000);
}));
