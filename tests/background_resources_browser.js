// Playwright CLI run-code, on a main-site preview or deployment.
async (page) => {
  const base = new URL(page.url()).origin, results = [];
  for (const width of [1440, 390]) {
    const context = await page.context().browser().newContext({
      viewport: {width, height: 900}, isMobile: width < 500, hasTouch: width < 500,
      userAgent: 'Mozilla/5.0 (Linux; Android 14) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/140.0.0.0 ' + (width < 500 ? 'Mobile ' : '') + 'Safari/537.36 ShouYuLove-QA'
    });
    let release;
    try {
      const p = await context.newPage(), errors = [], requests = [];
      // Chromium headless keeps all tabs visible. Exercise native visibility
      // listeners with a deterministic hidden document while real downloads run.
      await p.addInitScript(() => {
        window.__qaSetHidden = hidden => {
          Object.defineProperty(document, 'hidden', {configurable: true, value: hidden});
          document.dispatchEvent(new Event('visibilitychange'));
        };
        window.__qaSetHidden(true);
      });
      p.on('pageerror', error => errors.push(error.message));
      p.on('request', request => requests.push(request.url()));
      const held = new Promise(resolve => { release = resolve; });
      let started = 0;
      await p.route('**/webgl/**', async route => {
        started++;
        await held;
        await route.continue();
      });
      await p.goto(base + '/portfolio/', {waitUntil: 'domcontentloaded'});
      await p.waitForTimeout(2500);
      if (await p.locator('.portfolio-link').count() !== 10) throw new Error('Directory unavailable');
      if (requests.some(url => /entry\..*\.js|\/webgl\//.test(url))) throw new Error('Hidden scene booted');
      await p.evaluate(() => __qaSetHidden(false));
      await p.waitForFunction(() => window.__sylSceneDownloads?.active === 2 && __sylSceneDownloads.pending > 0);
      // Global images may precede the held WebGL requests in the shared queue.
      for (let i = 0; i < 100 && started < 2; i++) await p.waitForTimeout(50);
      await p.waitForTimeout(250);
      if (started !== 2) throw new Error('Expected two simultaneous WebGL downloads, got ' + started);
      await p.evaluate(() => __qaSetHidden(true));
      release();
      await p.waitForFunction(() => __sylSceneDownloads.active === 0);
      await p.waitForTimeout(400);
      if (started !== 2) throw new Error('Hidden page started additional downloads');
      const pending = await p.evaluate(() => __sylSceneDownloads.pending);
      if (!pending) throw new Error('Expected resources queued while hidden');
      await p.locator('.portfolio-link').last().scrollIntoViewIfNeeded();
      const scroll = await p.evaluate(() => scrollY);
      await p.evaluate(() => __qaSetHidden(false));
      await p.waitForFunction(() => performance.getEntriesByName('syl-portfolio-background-ready').length, null, {timeout: 90000});
      const ready = await p.evaluate(() => ({
        components: Object.keys(__sylPortfolio.view._components),
        frame: __sylPortfolio.app.renderer.instance.info.render.frame,
        active: __sylSceneDownloads.active, pending: __sylSceneDownloads.pending,
        scroll: scrollY, overflow: document.documentElement.scrollWidth > innerWidth
      }));
      await p.waitForTimeout(300);
      const laterFrame = await p.evaluate(() => __sylPortfolio.app.renderer.instance.info.render.frame);
      if (!ready.components.includes('fishScene') || !ready.components.includes('bgSimulation') || laterFrame <= ready.frame) throw new Error('Full native scene not animating');
      if (Math.abs(ready.scroll - scroll) > 2 || ready.overflow) throw new Error('Directory layout changed');
      if (requests.some(url => /\.mp3|\/sounds\//.test(url))) throw new Error('Portfolio downloaded audio');
      if (errors.length) throw new Error(errors.join('\n'));
      results.push({width, passed: true, visibility: 'simulated document.hidden', maxHeldDownloads: 2,
        queuedWhileHidden: pending, webglRequests: started, resumed: true, audioRequests: 0, ready});
    } finally {
      release?.();
      await context.close();
    }
  }
  return {base, passed: true, results};
}
