// A home-screen shortcut for the mobile works page, independent of WebGL readiness.
(() => {
  const wrapper = document.getElementById('syl-home-shortcut');
  const button = document.getElementById('syl-home-shortcut-button');
  const guide = document.getElementById('syl-shortcut-guide');
  const mobile = matchMedia('(max-width:640px), (max-width:960px) and (max-height:640px) and (pointer:coarse)');
  const standalone = matchMedia('(display-mode:standalone), (display-mode:fullscreen), (display-mode:minimal-ui)');
  let prompt = null;
  let installed = false;

  function closeGuide(focus = false) {
    guide.hidden = true;
    button.setAttribute('aria-expanded', 'false');
    if (focus && !wrapper.hidden) button.focus();
  }

  function update() {
    wrapper.hidden = !mobile.matches || !/^\/portfolio\/?$/.test(location.pathname) ||
      installed || standalone.matches || navigator.standalone === true;
    if (wrapper.hidden) closeGuide();
  }

  // Vue Router uses the History API; keep the shortcut scoped during client navigation.
  for (const name of ['pushState', 'replaceState']) {
    const original = history[name];
    history[name] = function (...args) {
      const result = original.apply(this, args);
      update();
      return result;
    };
  }
  addEventListener('popstate', update);
  addEventListener('pageshow', update);
  mobile.addEventListener('change', update);
  standalone.addEventListener('change', update);
  addEventListener('beforeinstallprompt', event => {
    event.preventDefault();
    prompt = event;
  });
  addEventListener('appinstalled', () => {
    installed = true;
    prompt = null;
    update();
  });

  button.addEventListener('click', async () => {
    if (prompt) {
      closeGuide();
      const request = prompt;
      prompt = null; // Browsers allow each installation event to be used only once.
      button.disabled = true;
      button.setAttribute('aria-busy', 'true');
      try {
        await request.prompt();
        installed = (await request.userChoice).outcome === 'accepted';
        return;
      } catch {
        // An unavailable native prompt falls back to the browser's own menu.
      } finally {
        button.disabled = false;
        button.removeAttribute('aria-busy');
        update();
      }
    }
    if (!guide.hidden) return closeGuide();
    const ios = /iPad|iPhone|iPod/.test(navigator.userAgent) ||
      (/Macintosh/.test(navigator.userAgent) && navigator.maxTouchPoints > 1);
    const embedded = /MicroMessenger|\bQQ\//.test(navigator.userAgent);
    guide.querySelector('p').textContent = guide.dataset[embedded ? 'embedded' : ios ? 'ios' : 'other'];
    guide.hidden = false;
    button.setAttribute('aria-expanded', 'true');
  });
  guide.querySelector('button').addEventListener('click', () => closeGuide(true));
  document.addEventListener('pointerdown', event => {
    if (!wrapper.contains(event.target)) closeGuide();
  });
  document.addEventListener('keydown', event => {
    if (event.key === 'Escape' && !guide.hidden) closeGuide(true);
  });
  update();
})();
