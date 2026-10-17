// Run with Playwright CLI; read-only public browsing, no AI calls or login.
async (page) => {
  const results = [];
  for (const width of [1440, 390]) {
    const context = await page.context().browser().newContext({
      viewport: { width, height: 900 }, isMobile: width < 500, hasTouch: width < 500,
      userAgent: width < 500
        ? 'Mozilla/5.0 (Linux; Android 14) AppleWebKit/537.36 Chrome/140.0.0.0 Mobile Safari/537.36 ShouYuLove-QA'
        : 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 Chrome/140.0.0.0 Safari/537.36 ShouYuLove-QA',
    });
    try {
      const p = await context.newPage(), failures = [], errors = [];
      let responses = 0;
      p.on('response', r => {
        responses++;
        if (r.status() === 429 || r.status() >= 500) failures.push({ path: new URL(r.url()).pathname, status: r.status() });
      });
      p.on('pageerror', e => errors.push(e.message));
      await p.goto('https://shouyulove.cn/dict/entries', { waitUntil: 'domcontentloaded', timeout: 60000 });
      await p.waitForLoadState('networkidle', { timeout: 60000 });
      const cookies = await context.cookies('https://shouyulove.cn/dict/entries');
      const session = cookies.find(c => c.name === 'syl_dict_session');
      if (!session?.httpOnly || !session.secure || session.path !== '/dict/') throw new Error('Signed browser session missing');
      if (!cookies.some(c => c.name === 'action_device')) throw new Error('Existing dictionary device cookie was lost');
      const images = await p.locator('img').evaluateAll(imgs => imgs.map(i => ({ loaded: i.complete && i.naturalWidth > 0, visible: i.getBoundingClientRect().top < innerHeight })));
      if (!images.some(i => i.loaded) || images.some(i => i.visible && !i.loaded)) throw new Error('Visible images did not load');
      const next = await p.locator('a[href*="page=2"]').first().getAttribute('href');
      await p.goto(new URL(next, p.url()).href, { waitUntil: 'domcontentloaded', timeout: 60000 });
      await p.waitForLoadState('networkidle', { timeout: 60000 });
      const entry = await p.locator('a[href*="/entry/"]').first().getAttribute('href');
      await p.goto(new URL(entry, p.url()).href, { waitUntil: 'domcontentloaded', timeout: 60000 });
      await p.waitForLoadState('networkidle', { timeout: 60000 });
      await p.reload({ waitUntil: 'domcontentloaded', timeout: 60000 });
      await p.waitForLoadState('networkidle', { timeout: 60000 });
      if (failures.length || errors.length) throw new Error(JSON.stringify({ failures, errors }));
      results.push({ width, responses, images: images.length, signedSession: true, existingCookiePreserved: true, pagination: true, entryAndReload: true, failures, errors });
    } finally { await context.close(); }
  }
  return { passed: true, results };
}
