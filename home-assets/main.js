(() => {
  const root = document.documentElement;
  const reduced = matchMedia('(prefers-reduced-motion: reduce)');
  const themeToggle = document.querySelector('.theme-toggle');
  const motionToggle = document.querySelector('.motion-toggle');
  let motion;
  let motionRequest = 0;
  let simple = false;
  try { simple = localStorage.getItem('shouyulove-motion') === 'simple'; } catch (_) {}

  function applyTheme(theme, save = false) {
    const dark = theme === 'dark';
    root.dataset.theme = dark ? 'dark' : 'light';
    themeToggle.setAttribute('aria-label', dark ? '切换到浅色模式' : '切换到深色模式');
    themeToggle.setAttribute('aria-pressed', String(dark));
    themeToggle.querySelector('span').textContent = dark ? '切换到浅色' : '切换到深色';
    document.querySelector('meta[name="theme-color"]').content = dark ? '#1c211b' : '#faf5f2';
    if (save) { try { localStorage.setItem('signmate-theme', theme); } catch (_) {} }
  }
  themeToggle.hidden = false;
  applyTheme(root.dataset.theme);
  themeToggle.addEventListener('click', () => applyTheme(root.dataset.theme === 'dark' ? 'light' : 'dark', true));

  // A small catalog needs no extra controls. Search and categories appear as it grows.
  const items = [...document.querySelectorAll('.project-item')];
  const tools = document.querySelector('.project-tools');
  const input = document.querySelector('#project-search');
  const filters = document.querySelector('#project-filters');
  const count = document.querySelector('#project-count');
  const empty = document.querySelector('.project-empty');
  const normalize = value => value.toLocaleLowerCase().normalize('NFKC').replace(/\s+/g, ' ').trim();
  const searchable = new Map(items.map(item => [item, normalize(item.textContent)]));
  let category = '全部';
  const categories = ['全部', ...new Set(items.map(item => item.dataset.category))];
  function filterProjects() {
    const words = normalize(input.value).split(' ').filter(Boolean);
    let visible = 0;
    items.forEach(item => {
      const match = (category === '全部' || item.dataset.category === category) && words.every(word => searchable.get(item).includes(word));
      item.hidden = !match;
      if (match) visible++;
    });
    filters.querySelectorAll('button').forEach(button => button.setAttribute('aria-pressed', String(button.dataset.category === category)));
    empty.hidden = visible !== 0;
    count.textContent = tools.hidden ? '' : `显示 ${visible} 个项目，共 ${items.length} 个`;
    motion?.refresh();
  }
  categories.forEach(value => {
    const button = document.createElement('button');
    button.type = 'button'; button.className = 'project-filter'; button.dataset.category = value; button.textContent = value;
    button.addEventListener('click', () => { category = value; filterProjects(); });
    filters.append(button);
  });
  tools.hidden = items.length <= 6;
  input.addEventListener('input', filterProjects);
  document.querySelector('#clear-search').addEventListener('click', () => { input.value = ''; category = '全部'; filterProjects(); input.focus(); });
  filterProjects();

  async function applyMotion() {
    if (!document.querySelector('.hero')) { motionToggle.hidden = true; return; }
    const request = ++motionRequest;
    motion?.destroy(); motion = undefined;
    motionToggle.setAttribute('aria-pressed', String(simple));
    motionToggle.textContent = simple ? '沉浸浏览' : '简洁浏览';
    motionToggle.hidden = reduced.matches;
    if (simple || reduced.matches) return;
    try {
      const module = await import('./motion.bundle.js?v=collections-13');
      if (request !== motionRequest) return;
      motion = module.startMotion();
      if (location.hash) {
        // Native fragment scrolling can run after the animation layout initializes.
        const loaded = document.readyState === 'complete' ? Promise.resolve() : new Promise(resolve => window.addEventListener('load', resolve, { once: true }));
        Promise.all([loaded, document.fonts.ready]).then(() => {
          if (request === motionRequest) requestAnimationFrame(() => motion?.scrollToHash(location.hash, true));
        });
      }
    } catch (error) {
      root.classList.remove('motion-active', 'motion-desktop');
      console.warn('Motion unavailable; the complete static page remains available.', error);
    }
  }
  motionToggle.addEventListener('click', () => {
    simple = !simple;
    try { localStorage.setItem('shouyulove-motion', simple ? 'simple' : 'full'); } catch (_) {}
    applyMotion();
  });
  reduced.addEventListener('change', applyMotion);
  applyMotion();

  document.querySelectorAll('a[href^="#"]').forEach(link => link.addEventListener('click', event => {
    if (event.metaKey || event.ctrlKey || event.shiftKey || event.altKey || !motion) return;
    if (motion.scrollToHash(link.hash, false, event.detail === 0)) {
      event.preventDefault();
      history.pushState(null, '', link.hash);
    }
  }));
  const restoreHash = () => requestAnimationFrame(() => motion?.scrollToHash(location.hash || '#top', true));
  window.addEventListener('popstate', restoreHash);
  window.addEventListener('hashchange', restoreHash);
})();
