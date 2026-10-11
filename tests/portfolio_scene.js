// Actual-browser checks for progressive, original WebGL enhancement.
async (page) => {
 const base=new URL(page.url()).origin,results=[];
 for (const width of [1440,390,320]) {
  const c=await page.context().browser().newContext({viewport:{width,height:900},isMobile:width<500,hasTouch:width<500,userAgent:'Mozilla/5.0 (Linux; Android 14; Pixel 8) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/140.0.0.0 '+(width<500?'Mobile ':'')+'Safari/537.36 ShouYuLove-QA'});
  let release;
  try {
   const p=await c.newPage(),errors=[],requests=[];
   await p.bringToFront();p.on('pageerror',e=>errors.push(e.message));p.on('request',r=>requests.push({url:r.url(),time:Date.now()}));
   const hold=new Promise(r=>release=r);
   await p.route('**/webgl/projects/fish.glb',async r=>{await hold;await r.continue();});
   await p.goto(base+'/portfolio/',{waitUntil:'domcontentloaded',timeout:90000});
   await p.waitForFunction(()=>performance.getEntriesByName('syl-portfolio-readable').length);
   const initial=await p.locator('.portfolio-link').evaluateAll(nodes=>nodes.map(e=>({href:e.href,top:e.getBoundingClientRect().top,title:e.querySelector('h3').textContent})));
   if(initial.length!==8||initial[0].top>300)throw new Error('Initial links unavailable');
   const hierarchy=await p.evaluate(()=>({categories:[...document.querySelectorAll('.portfolio-section h2')].map(e=>e.textContent),headingSize:parseFloat(getComputedStyle(document.querySelector('.portfolio-section h2')).fontSize),primarySize:parseFloat(getComputedStyle(document.querySelector('.portfolio-link h3')).fontSize),secondarySize:parseFloat(getComputedStyle(document.querySelector('.portfolio-section--secondary h3')).fontSize),primaryRow:document.querySelector('.portfolio-link').getBoundingClientRect().height,secondaryRow:document.querySelector('.portfolio-section--secondary .portfolio-link').getBoundingClientRect().height}));
   if(hierarchy.categories.join(',')!=='核心创意,心创组内部使用,其他作品'||hierarchy.headingSize<=hierarchy.primarySize||hierarchy.secondarySize>=hierarchy.primarySize||hierarchy.secondaryRow>=hierarchy.primaryRow)throw new Error('Directory hierarchy');
   if(requests.some(r=>/entry\..*\.js|\/webgl\//.test(r.url)))throw new Error('Scene requested before content paint');
   await p.waitForFunction(()=>performance.getEntriesByName('syl-portfolio-scene-start').length);
   await p.waitForTimeout(1500);
   if(await p.evaluate(()=>!!window.__sylPortfolio?.view))throw new Error('Model was not blocked');
   // The lower entries and popup remain usable while the actual GLB is held.
   await p.locator('.portfolio-link').last().scrollIntoViewIfNeeded();
   const before=await p.locator('.portfolio-link').last().boundingBox();
   if(before.y>900||before.y<0)throw new Error('Scrolling blocked by scene loader');
   const popupPromise=p.waitForEvent('popup');await p.locator('.portfolio-link').last().click();const popup=await popupPromise;await popup.waitForURL(url=>{const expected=new URL(initial.at(-1).href);return url.host===expected.host&&url.pathname.replace(/\/$/,'')===expected.pathname.replace(/\/$/,'');},{waitUntil:'commit',timeout:60000});await popup.close();
   const y=await p.evaluate(()=>scrollY);
   release();await p.waitForFunction(()=>performance.getEntriesByName('syl-portfolio-background-ready').length,null,{timeout:90000});
   await p.waitForTimeout(1200);
   if(new URL(p.url()).pathname!=='/portfolio/')throw new Error('Scene changed canonical URL');
   if(Math.abs(await p.evaluate(()=>scrollY)-y)>2)throw new Error('Scene reset document scroll '+JSON.stringify({before:y,after:await p.evaluate(()=>scrollY)}));
   if(await p.locator('.portfolio-link').count()!==8)throw new Error('Scene replaced directory');
   await p.evaluate(()=>scrollTo(0,0));
   const geometry=await p.locator('.portfolio-link').evaluateAll(nodes=>nodes.map(e=>e.getBoundingClientRect().top));
   if(geometry.some((top,i)=>Math.abs(top-initial[i].top)>2))throw new Error('Scene shifted directory layout');
   if(await p.evaluate(()=>document.documentElement.scrollWidth>innerWidth))throw new Error('Horizontal overflow');
   await p.mouse.move(width*.7,350);await p.mouse.down();await p.mouse.move(width*.2,550,{steps:12});await p.mouse.up();
   if(width<500)await p.touchscreen.tap(width*.8,120);
   await p.waitForTimeout(300);
   const scene=await p.evaluate(()=>({marks:performance.getEntriesByType('mark').map(e=>({name:e.name,time:e.startTime})),frame:window.__sylPortfolio.app.renderer.instance.info.render.frame,components:Object.keys(window.__sylPortfolio.view._components),canvas:document.querySelector('#__nuxt canvas').getBoundingClientRect().toJSON(),font:getComputedStyle(document.body).fontFamily,visible:getComputedStyle(document.getElementById('__nuxt')).opacity,linkColor:getComputedStyle(document.querySelector('.portfolio-link')).color}));
   if(!scene.components.includes('fishScene')||!scene.components.includes('bgSimulation')||scene.frame<2||scene.visible!=='1')throw new Error('Original scene not rendering');
   if(requests.some(r=>/\.mp3|\/sounds\//.test(r.url)))throw new Error('Directory downloaded sound');
   await p.screenshot({path:'output/playwright/portfolio-3d/'+width+'.png'});
   if(errors.length)throw new Error(errors.join('\n'));
   results.push({width,links:8,blockedModelLinksUsable:true,scrollPreserved:true,geometryPreserved:true,audioRequests:0,hierarchy,scene,errors});
  }finally{release?.();await c.close();}
 }
 for(const mode of ['no-js','failed-scene']) {
  const c=await page.context().browser().newContext({viewport:{width:390,height:900},javaScriptEnabled:mode!=='no-js',userAgent:'Mozilla/5.0 ShouYuLove-QA'});
  try{const p=await c.newPage();if(mode==='failed-scene')await p.route('**/portfolio-scene.*.json',r=>r.abort());await p.goto(base+'/portfolio/');if(mode==='failed-scene')await p.waitForFunction(()=>performance.getEntriesByName('syl-portfolio-scene-error').length);if(await p.locator('.portfolio-link').count()!==8)throw new Error('Fallback links lost');await p.locator('.portfolio-link').last().scrollIntoViewIfNeeded();results.push({mode,links:8,scroll:true});}finally{await c.close();}
 }
 return {base,passed:true,results};
}
