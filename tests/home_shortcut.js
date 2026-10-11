// Run with playwright-cli run-code "$(cat tests/home_shortcut.js)" on a site page.
async (page) => {
  const base = new URL(page.url()).origin;
  const browser = page.context().browser();
  const results = [];
  const assert = (value, message) => { if (!value) throw new Error(message); };
  const android = await browser.newContext({viewport:{width:390,height:900},isMobile:true,hasTouch:true,
    userAgent:'Mozilla/5.0 (Linux; Android 14; Pixel 7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Mobile Safari/537.36'});
  await android.addInitScript(() => addEventListener('beforeinstallprompt', event => {
    if (!event.__sylMock) { event.preventDefault(); event.stopImmediatePropagation(); }
  }, true));
  try {
    const mobile = await android.newPage();
    const errors = [];
    mobile.on('pageerror', error => errors.push(error.message));
    await mobile.goto(base + '/portfolio/', {waitUntil:'domcontentloaded',timeout:90000});
    const button = mobile.locator('#syl-home-shortcut-button');
    const guide = mobile.locator('#syl-shortcut-guide');
    await button.waitFor({state:'visible'});
    await mobile.waitForFunction(() => !document.getElementById('syl-early'), null, {timeout:90000});
    const box = await button.boundingBox();
    assert(box.height >= 44 && box.y + box.height <= 880, 'Shortcut safe-area or touch size');
    assert(await mobile.locator('.portfolio-link').count() === 7, 'Works changed');
    await mobile.screenshot({path:'output/playwright/home-shortcut/mobile-390.png'});
    await button.click();
    assert((await guide.innerText()).includes('打开浏览器菜单'), 'Android instructions');
    await mobile.keyboard.press('Escape');
    assert(await guide.isHidden(), 'Escape did not close guide');
    assert(await button.getAttribute('aria-expanded') === 'false', 'Expanded state');
    await button.click();
    await guide.locator('button').click();
    assert(await guide.isHidden(), 'Close did not work');
    await mobile.setViewportSize({width:320,height:740});
    await button.click();
    const narrow = await guide.boundingBox();
    assert(narrow.x >= 0 && narrow.x + narrow.width <= 320 && narrow.y >= 0, 'Narrow-screen overflow');
    await mobile.screenshot({path:'output/playwright/home-shortcut/mobile-320-guide.png'});
    await mobile.mouse.click(8, 100);
    assert(await guide.isHidden(), 'Outside tap did not close');
    await mobile.setViewportSize({width:844,height:390});
    assert(await button.isVisible(), 'Phone landscape lost shortcut');
    await button.click();
    const landscape = await guide.boundingBox();
    assert(landscape.y >= 0 && landscape.y + landscape.height < 390, 'Landscape guide clipped');
    await mobile.keyboard.press('Escape');
    await mobile.setViewportSize({width:390,height:900});
    const mockPrompt = async outcome => mobile.evaluate(outcome => {
      window.__shortcutCalls = 0;
      const event = new Event('beforeinstallprompt', {cancelable:true});
      event.__sylMock = true;
      event.prompt = async () => { window.__shortcutCalls++; if (outcome === 'error') throw new Error('Unavailable'); };
      event.userChoice = Promise.resolve({outcome});
      window.dispatchEvent(event);
      if (!event.defaultPrevented) throw new Error('Prompt was not captured');
    }, outcome);
    await mockPrompt('dismissed');
    await button.click();
    await mobile.waitForFunction(() => window.__shortcutCalls === 1 && !document.getElementById('syl-home-shortcut-button').disabled);
    assert(await button.isVisible() && await guide.isHidden(), 'Dismissal hid shortcut or opened guide');
    await mockPrompt('error');
    await button.click();
    await guide.waitFor({state:'visible'});
    await mobile.keyboard.press('Escape');
    await mobile.locator('.portfolio-header a[href="/"]').click();
    await mobile.waitForURL(base + '/');
    assert(await button.isHidden(), 'Shortcut leaked onto homepage');
    await mobile.goBack();
    await mobile.waitForURL(base + '/portfolio/');
    await button.waitFor({state:'visible'});
    const cdp = await android.newCDPSession(mobile);
    const manifest = await cdp.send('Page.getAppManifest');
    assert(manifest.errors.length === 0 && JSON.parse(manifest.data).start_url === '/portfolio/', 'Invalid manifest');
    assert(await mobile.locator('meta[name="apple-mobile-web-app-title"]').getAttribute('content') === '以手予爱', 'Wrong iPhone home-screen name');
    await cdp.detach();
    await mockPrompt('accepted');
    await button.click();
    await button.waitFor({state:'hidden'});
    assert(errors.length === 0, errors.join('\n'));
    results.push({device:'Android',widths:[390,320,844],nativePrompt:'accepted/dismissed/error branches checked',history:true,manifest:true,errors});
  } finally { await android.close(); }
  for (const embedded of [false,true]) {
    const ios = await browser.newContext({viewport:{width:390,height:844},isMobile:true,hasTouch:true,
      userAgent:'Mozilla/5.0 (iPhone; CPU iPhone OS 18_0 like Mac OS X) AppleWebKit/605.1.15 Version/18.0 Mobile/15E148 Safari/604.1' + (embedded ? ' MicroMessenger/8.0.0' : '')});
    try {
      // Block the background: links and installation guidance remain usable.
      await ios.route('**/plaster.jpg', route => route.abort());
      const phone = await ios.newPage();
      await phone.goto(base + '/portfolio/', {waitUntil:'domcontentloaded',timeout:90000});
      const button = phone.locator('#syl-home-shortcut-button');
      await button.click();
      const text = await phone.locator('#syl-shortcut-guide').innerText();
      assert(text.includes(embedded ? '在浏览器中打开' : '用 Safari 打开本页'), 'iOS/embedded guidance');
      await phone.evaluate(() => { Object.defineProperty(navigator, 'standalone', {value:true}); dispatchEvent(new Event('pageshow')); });
      assert(await button.isHidden(), 'Installed iOS app shows shortcut');
      results.push({device:embedded ? 'WeChat iPhone guidance' : 'iPhone guidance',usableBeforeNativeStartup:true,standaloneHidden:true});
    } finally { await ios.close(); }
  }
  const desktop = await browser.newContext({viewport:{width:1440,height:900}});
  try {
    const wide = await desktop.newPage();
    await wide.goto(base + '/portfolio/', {waitUntil:'domcontentloaded',timeout:90000});
    await wide.waitForFunction(() => performance.getEntriesByName('syl-native-ready').length, null, {timeout:90000});
    assert(await wide.locator('#syl-home-shortcut').isHidden(), 'Shortcut visible on desktop');
    await wide.screenshot({path:'output/playwright/home-shortcut/desktop-1440.png'});
    results.push({device:'desktop',hidden:true});
  } finally { await desktop.close(); }
  return results;
}
