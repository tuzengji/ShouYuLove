// Run with Playwright CLI on an open local preview or deployed main-site tab.
async(page)=>{
  const base=new URL(page.url()).origin,results=[];
  const state=async(p)=>p.evaluate(()=>{
    const g=document.querySelector('#__nuxt')?.__vue_app__?.config.globalProperties;
    const view=g?.$nuxt.$webglApp.viewManager.get('projects')?.instance;
    const node=document.querySelector('#__nuxt .projectsPage');
    let opacity=1;
    for(let e=node;e;e=e.parentElement)opacity*=Number(getComputedStyle(e).opacity);
    return {path:location.pathname,opacity:node?opacity:0,transition:g?.$pinia.state.value.transition.transitionState,loaded:view?._areResourcesLoaded(),active:g?.$nuxt.$webglApp.viewManager.active?.viewName,visible:view?.visible,links:[...document.querySelectorAll('.projectsPage .projectListItem .name')].map(a=>({title:a.textContent,url:a.href,target:a.target,line:getComputedStyle(a,'::after').content})),overflow:document.documentElement.scrollWidth>innerWidth};
  });
  const readyHome=async(p)=>p.waitForFunction(()=>{
    const g=document.querySelector('#__nuxt')?.__vue_app__?.config.globalProperties;
    return g?.$pinia.state.value.webgl.ready&&!document.getElementById('syl-early')&&document.querySelector('.homePage')&&g.$pinia.state.value.transition.transitionState==='none';
  },null,{timeout:90000});
  const readyProjects=async(p,timeout=12000)=>p.waitForFunction(()=>{
    const g=document.querySelector('#__nuxt')?.__vue_app__?.config.globalProperties,e=document.querySelector('.projectsPage');
    return e&&Number(getComputedStyle(e).opacity)>.95&&g.$pinia.state.value.transition.transitionState==='none';
  },null,{timeout});
  const clickWorks=async(p,width,context)=>{
    const fixed=p.locator('a.projectsBttn');
    if(await fixed.isVisible()){await fixed.click();return;}
    const target=p.locator('a.footer__projectsCta'),cdp=width<500?await context.newCDPSession(p):null;
    for(let i=0;i<50;i++){
      const delta=await target.evaluate(e=>e.getBoundingClientRect().top-300);
      if(Math.abs(delta)<60)break;
      if(cdp){const x=width/2,y=delta>0?740:150,travel=Math.sign(delta)*Math.min(Math.abs(delta),550);await cdp.send('Input.dispatchTouchEvent',{type:'touchStart',touchPoints:[{x,y}]});for(let j=1;j<=8;j++){await cdp.send('Input.dispatchTouchEvent',{type:'touchMove',touchPoints:[{x,y:y-travel*j/8}]});await p.waitForTimeout(20);}await cdp.send('Input.dispatchTouchEvent',{type:'touchEnd',touchPoints:[]});}
      else await p.mouse.wheel(0,Math.sign(delta)*Math.min(Math.abs(delta)/2,1500));
      await p.waitForTimeout(200);
    }
    await cdp?.detach();await target.click();
  };
  for(const [width,label] of [[1440,'desktop'],[390,'mobile']]){
    const context=await page.context().browser().newContext({viewport:{width,height:900},deviceScaleFactor:width<500?3:2,isMobile:width<500,hasTouch:width<500,...(width<500?{userAgent:'Mozilla/5.0 (Linux; Android 14; Pixel 8) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/154.0.0.0 Mobile Safari/537.36'}:{})});
    let release;
    try{
      const p=await context.newPage(),errors=[],badResponses=[];
      p.on('pageerror',e=>errors.push(String(e)));p.on('response',r=>{if(r.status()>=400)badResponses.push({url:r.url(),status:r.status()});});
      let fishRequests=0;const hold=new Promise(r=>release=r);
      await p.route('**/webgl/projects/fish.glb',async r=>{fishRequests++;await hold;await r.continue();});
      await p.goto(base+'/',{waitUntil:'domcontentloaded',timeout:90000});await readyHome(p);
      if((await state(p)).loaded||fishRequests)throw new Error('Works scene eagerly loaded '+label);
      await clickWorks(p,width,context);await readyProjects(p);
      const pending=await state(p);
      if(pending.loaded||pending.opacity<.95||pending.links.length!==7||pending.transition!=='none'||fishRequests!==1)throw new Error('Delayed works navigation failed '+label+JSON.stringify(pending));
      await p.screenshot({path:'output/playwright/project-navigation/pending-'+label+'.png'});
      await p.locator('.projectsPage a.prevNextBttn[href="/"]').click();await readyHome(p);
      release();
      await p.waitForFunction(()=>document.querySelector('#__nuxt').__vue_app__.config.globalProperties.$nuxt.$webglApp.viewManager.get('projects').instance._areResourcesLoaded(),null,{timeout:30000});
      const stale=await p.evaluate(()=>{const v=document.querySelector('#__nuxt').__vue_app__.config.globalProperties.$nuxt.$webglApp.viewManager;return {active:v.active?.viewName,worksVisible:v.get('projects').instance.visible};});
      if(stale.active!=='home'||stale.worksVisible)throw new Error('Late scene took over the home page '+label+JSON.stringify(stale));
      await clickWorks(p,width,context);await readyProjects(p);
      const loaded=await state(p);
      if(!loaded.loaded||loaded.opacity<.95||loaded.links.length!==7||loaded.links.some(l=>l.line!=='none'||l.target!=='_blank')||loaded.overflow||fishRequests!==1)throw new Error('Ready works navigation failed '+label+JSON.stringify(loaded));
      if(width>=500){await p.locator('.projectListItem .name').filter({hasText:'分社手语词典'}).hover();await p.waitForTimeout(350);}
      await p.screenshot({path:'output/playwright/project-navigation/ready-'+label+'.png'});
      await p.goBack();await readyHome(p);await p.goForward();await readyProjects(p);
      if(errors.length||badResponses.length)throw new Error(JSON.stringify({label,errors,badResponses}));
      results.push({label,width,pending,stale,loaded,fishRequests,errors,badResponses});
    }finally{release?.();await context.close();}
    const coldContext=await page.context().browser().newContext({viewport:{width,height:900},isMobile:width<500,hasTouch:width<500});
    try{
      const p=await coldContext.newPage();await p.goto(base+'/projects/',{waitUntil:'domcontentloaded',timeout:90000});await readyProjects(p,90000);
      const cold=await state(p);if(!cold.loaded||cold.opacity<.95||cold.links.length!==7||cold.overflow)throw new Error('Direct works entry failed '+label+JSON.stringify(cold));
      results.push({label:'cold-'+label,width,cold});
    }finally{await coldContext.close();}
  }
  return {base,passed:true,results};
}
