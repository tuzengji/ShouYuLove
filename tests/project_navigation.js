// Run with Playwright CLI on a local or deployed main-site page.
async (page) => {
 const base=new URL(page.url()).origin,results=[];
 for(const width of [1440,390]){
  const context=await page.context().browser().newContext({viewport:{width,height:900},isMobile:width<500,hasTouch:width<500,userAgent:width<500?'Mozilla/5.0 (Linux; Android 14; Pixel 8) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/140.0.0.0 Mobile Safari/537.36 ShouYuLove-QA':'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/140.0.0.0 Safari/537.36 ShouYuLove-QA'});
  try{
   const p=await context.newPage(),errors=[];p.on('pageerror',e=>errors.push(e.message));
   await p.goto(base+'/',{waitUntil:'domcontentloaded',timeout:90000});
   await p.bringToFront();
   await p.waitForFunction(()=>performance.getEntriesByName('syl-native-ready').length,null,{timeout:90000});
   if(await p.locator('#syl-early').count())throw new Error('Temporary page returned');
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
   await p.locator('.portfolio-header a[href="/"]').click();await p.waitForURL(base+'/');
   await p.goBack();await p.waitForURL(base+'/portfolio/');await p.locator('.portfolio-link').first().waitFor();
   await p.goForward();await p.waitForURL(base+'/');
   if(errors.length)throw new Error(errors.join('\n'));
   results.push({width,nativeHome:true,history:true,links:10,errors});
  }finally{await context.close();}
 }
 return {base,passed:true,results};
}
