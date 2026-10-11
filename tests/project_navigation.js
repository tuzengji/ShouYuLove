// Run with Playwright CLI on a local or deployed main-site page.
async (page) => {
 const base=new URL(page.url()).origin,results=[];
 for(const width of [1440,390]){
  const context=await page.context().browser().newContext({viewport:{width,height:900},isMobile:width<500,hasTouch:width<500,userAgent:width<500?'Mozilla/5.0 (Linux; Android 14; Pixel 8) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/140.0.0.0 Mobile Safari/537.36 ShouYuLove-QA':'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/140.0.0.0 Safari/537.36 ShouYuLove-QA'});
  try{
   const p=await context.newPage(),errors=[];p.on('pageerror',e=>errors.push(e.message));
   await p.route('**/webgl/**/*.glb',r=>r.abort());
   await p.goto(base+'/',{waitUntil:'domcontentloaded',timeout:90000});
   await p.locator('#syl-early a[href="/portfolio/"]').click();
   await p.waitForURL(base+'/portfolio/');
   if(await p.locator('.portfolio-link').count()!==7)throw new Error('Early home to lightweight directory');
   await p.locator('.portfolio-header a[href="/"]').click();await p.waitForURL(base+'/');
   await p.goBack();await p.waitForURL(base+'/portfolio/');await p.locator('.portfolio-link').first().waitFor();
   await p.goForward();await p.waitForURL(base+'/');
   // The deliberately aborted homepage models may reject; the directory did not load them.
   const blockedHomeErrors=errors.splice(0);
   await p.unroute('**/webgl/**/*.glb');
   await p.goto(base+'/',{waitUntil:'domcontentloaded',timeout:90000});
   await p.waitForFunction(()=>!document.getElementById('syl-early'),null,{timeout:90000});
   if(width>=500)await p.locator('a.projectsBttn').click();
   else{
    const target=p.locator('.footer__projectsCta');
    const cdp=await context.newCDPSession(p);
    for(let i=0;i<60;i++){
     const delta=await target.evaluate(e=>e.getBoundingClientRect().top-300);if(Math.abs(delta)<60)break;
     const x=width/2,y=delta>0?740:150,travel=Math.sign(delta)*Math.min(Math.abs(delta),550);
     await cdp.send('Input.dispatchTouchEvent',{type:'touchStart',touchPoints:[{x,y}]});
     for(let j=1;j<=8;j++){await cdp.send('Input.dispatchTouchEvent',{type:'touchMove',touchPoints:[{x,y:y-travel*j/8}]});await p.waitForTimeout(20);}
     await cdp.send('Input.dispatchTouchEvent',{type:'touchEnd',touchPoints:[]});await p.waitForTimeout(200);
    }
    await cdp.detach();await target.click();
   }
   await p.waitForURL(base+'/portfolio/');await p.locator('.portfolio-link').first().waitFor();
   if(new URL(p.url()).pathname!=='/portfolio/')throw new Error('Native home link changed address');
   if(errors.length)throw new Error(errors.join('\n'));
   results.push({width,earlyHome:true,nativeHome:true,history:true,links:7,blockedHomeErrors,errors});
  }finally{await context.close();}
 }
 return {base,passed:true,results};
}
