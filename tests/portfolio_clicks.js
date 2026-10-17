// Run with Playwright CLI after opening the candidate or live portfolio.
async (page) => {
  const base = new URL(page.url()).origin;
  const live = base === 'https://shouyulove.cn';
  const results = [];
  for (const mode of ['desktop', 'mobile', 'narrow', 'fallback', 'blocked', 'no-js', 'full-scene']) {
    const width = mode === 'mobile' ? 390 : mode === 'narrow' ? 320 : 1440;
    const context = await page.context().browser().newContext({
      viewport: {width, height: 900}, isMobile: width < 500, hasTouch: width < 500,
      javaScriptEnabled: mode !== 'no-js',
      userAgent: 'Mozilla/5.0 ' + (width < 500 ? '(Linux; Android 14; Pixel 8)' : '(Macintosh; Intel Mac OS X 10_15_7)') +
        ' AppleWebKit/537.36 (KHTML, like Gecko) Chrome/140.0.0.0 Safari/537.36 ShouYuLove-QA'
    });
    try {
      if (mode === 'fallback') await context.addInitScript(() => { navigator.sendBeacon = () => false; });
      const requests = [], errors = [];
      await context.route('**/*', async route => {
        const request = route.request(), url = new URL(request.url());
        if (url.pathname.startsWith('/__syl/portfolio-click/')) {
          requests.push({path: url.pathname, method: request.method(), headers: await request.allHeaders()});
          if (mode === 'blocked') return route.abort();
          if (!live) return route.fulfill({status: 204});
          return route.continue();
        }
        // Open the original destination but avoid test traffic reaching other sites.
        if (request.isNavigationRequest() &&
            (url.origin !== base || url.pathname !== '/portfolio/')) {
          return route.fulfill({status: 200, contentType: 'text/html', body: '<p>Destination test</p>'});
        }
        if (url.pathname.includes('/portfolio-scene.') && mode !== 'full-scene') return route.abort();
        if (/\.mp3$|\/sounds\//.test(url.pathname)) throw new Error('Portfolio requested music');
        return route.continue();
      });
      const p = await context.newPage();
      await p.bringToFront();
      p.on('pageerror', e => errors.push(e.message));
      await p.goto(base + '/portfolio/', {waitUntil: 'domcontentloaded'});
      const links = p.locator('#portfolio .portfolio-link');
      if (await links.count() !== 10) throw new Error('Missing works');
      await p.evaluate(() => document.fonts.ready);
      if (mode === 'full-scene') {
        await p.waitForFunction(() => performance.getEntriesByName('syl-portfolio-background-ready').length, null, {timeout: 90000})
          .catch(error => { throw new Error('Scene: ' + error.message + '; ' + errors.join('; ')); });
        await p.waitForTimeout(500);
      }
      if (requests.length) throw new Error('Page load counted as a click');
      if (await p.evaluate(() => document.documentElement.scrollWidth > innerWidth)) throw new Error('Overflow');
      const indices = mode === 'desktop' ? [...Array(10).keys()] : mode === 'mobile' ? [0, 7, 8, 9] : [9];
      const activate = async (index, action) => {
        await p.bringToFront();
        const link = links.nth(index), href = await link.getAttribute('href');
        const id = await link.getAttribute('data-project');
        const before = requests.length;
        const receipt = mode !== 'no-js' && mode !== 'blocked' && p.waitForResponse(
          response => new URL(response.url()).pathname === '/__syl/portfolio-click/' + id,
          {timeout: 15000});
        const popupPromise = context.waitForEvent('page', {timeout: 10000});
        await action(link);
        const popup = await popupPromise.catch(error => { throw new Error(mode + ' index=' + index + ' count=' + before + ': ' + error.message); });
        await popup.waitForLoadState('domcontentloaded');
        if (popup.url() !== new URL(href).href) throw new Error('Destination was changed: ' + popup.url());
        await popup.close();
        if (receipt && (await receipt).status() !== 204) throw new Error('Collector rejected ' + id);
        if (mode !== 'no-js') {
          for (let i = 0; i < 40 && requests.length === before; i++) await p.waitForTimeout(50);
          if (requests.length !== before + 1 || requests.at(-1).path !== '/__syl/portfolio-click/' + id ||
              requests.at(-1).method !== 'POST') throw new Error('Expected exactly one activation for ' + id);
          if (live && mode !== 'blocked') {
            if (requests.at(-1).headers.origin !== base || !requests.at(-1).headers.referer.startsWith(base + '/portfolio/'))
              throw new Error('Origin or portfolio source missing');
          }
        } else if (requests.length) throw new Error('No-JS page counted clicks');
      };
      for (const index of indices) await activate(index, link => width < 500 ? link.tap() : link.click());
      if (mode === 'desktop') {
        await activate(8, async link => { await link.focus(); await p.keyboard.press('Enter'); });
        await activate(8, link => link.click({button: 'middle'}));
        const before = requests.length;
        await links.nth(8).click({button: 'right'});
        await p.keyboard.press('Escape');
        await p.waitForTimeout(100);
        if (requests.length !== before) throw new Error('Context menu counted as navigation');
      }
      if (errors.length) throw new Error(errors.join('\n'));
      if (['desktop', 'mobile', 'narrow'].includes(mode)) {
        await p.waitForFunction(() => [...document.querySelectorAll('.portfolio-icon')].every(img => img.complete && img.naturalWidth), null, {timeout: 15000});
        await p.evaluate(() => { window.getSelection()?.removeAllRanges(); document.activeElement?.blur(); });
        await p.evaluate(() => scrollTo(0, 0));
        await p.screenshot({path: 'output/playwright/portfolio-clicks/' + (live ? 'live-' : 'local-') + mode + '.png', fullPage: true});
      }
      results.push({mode, width, activations: requests.length, originalLinksPreserved: true, errors});
    } finally { await context.close(); }
  }
  return {base, results};
}
