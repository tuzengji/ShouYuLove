import { gsap } from 'gsap';
import { ScrollTrigger } from 'gsap/ScrollTrigger';
import Lenis from 'lenis';

gsap.registerPlugin(ScrollTrigger);
const root=document.documentElement, body=document.body;
const canvas=document.querySelector('#garden'), footer=document.querySelector('.site-footer');
const reduced=matchMedia('(prefers-reduced-motion: reduce)'), touch=matchMedia('(pointer: coarse)');
const loader=document.querySelector('#site-loader'), loaderFill=document.querySelector('#site-loader-fill'), loaderValue=document.querySelector('#site-loader-value');
const cursor=document.querySelector('.cursor'), media=[...document.querySelectorAll('.project-media')], memberCards=[...document.querySelectorAll('.member-card')], inkLinks=[...document.querySelectorAll('.ink-hover')];
let lenis, scene, animationContext, bootId=0;
let lastScroll=scrollY, velocity=0, fast=0, dark=0, footerAmount=0, disposed=false, lastFrame=0;
let touchReveal=0, loaderValueState=0, loaderFinished=false, loaderStartedAt=0, loaderTween;
let sceneQueue=Promise.resolve(), previousScene={scroll:-1,fast:-1,dark:-1};
let pointer={x:-100,y:-100}, currentPointer={x:-100,y:-100}, hoverMedia=null;
const runtime={ready:false,errors:[],mode:'loading',scene:null,scroll:0,fast:0,dark:0};
window.__garden=runtime;
const clamp=(v,min=0,max=1)=>Math.max(min,Math.min(max,v));
function setLoaderProgress(value){
  if(!loader||loaderFinished)return;
  loaderValueState=Math.max(loaderValueState,clamp(value));
  if(loaderFill)loaderFill.style.transform=`scaleX(${loaderValueState})`;
  if(loaderValue)loaderValue.textContent=String(Math.round(loaderValueState*100));
}
function beginLoader(){
  if(!loader||loaderFinished)return;
  loaderStartedAt=performance.now();loader.classList.remove('is-done');body.classList.remove('loader-ready');loaderValueState=0;setLoaderProgress(0);
  loaderTween=gsap.to({value:0},{value:.72,duration:2.8,ease:'sine.inOut',onUpdate(){setLoaderProgress(this.targets()[0].value)}});
}
function finishLoader(){
  if(!loader||loaderFinished)return;
  const wait=Math.max(0,1100-(performance.now()-loaderStartedAt));
  if(wait>0){window.setTimeout(finishLoader,wait);return;}
  loaderTween&&loaderTween.kill();setLoaderProgress(1);loaderFinished=true;body.classList.add('loader-ready');
  loader.classList.add('is-done');
  if(!reduced.matches&&document.querySelector('.intro'))gsap.to('.intro-brand, .intro-identity, .scroll-cue',{autoAlpha:1,y:0,filter:'blur(0px)',duration:1.35,delay:.16,stagger:.15,ease:'power3.out',clearProps:'transform,opacity,filter,visibility'});
}
function measure(){
  footerAmount=clamp((innerHeight*.8-footer.getBoundingClientRect().top)/(innerHeight*.85));
  body.classList.toggle('past-intro',scrollY>Math.max(60,innerHeight*.5));
  body.classList.toggle('at-footer',footer.getBoundingClientRect().top<80);
  runtime.scroll=scrollY;
}
function frame(time){
  if(disposed||document.hidden)return;
  const dt=Math.min(50,lastFrame?(time-lastFrame)*1000:16.67);lastFrame=time;
  lenis?.raf(time*1000);
  const delta=scrollY-lastScroll;lastScroll=scrollY;
  velocity+=(Math.abs(delta)*16.67/Math.max(dt,1)-velocity)*.15;
  const fastTarget=(!reduced.matches&&velocity>75)?clamp((velocity-75)/200):0;
  fast+=(fastTarget-fast)*(fastTarget>fast?.035:.06);
  touchReveal+=(0-touchReveal)*(touchReveal>.01?.045:.16);
  const sceneFast=Math.max(fast,touchReveal);
  measure();
  dark+=(footerAmount-dark)*(reduced.matches?1:.045);
  if(scene){
    if(previousScene.scroll!==scrollY){scene.setScroll(scrollY);previousScene.scroll=scrollY;}
    if(Math.abs(previousScene.fast-sceneFast)>.001){scene.setFast(sceneFast);previousScene.fast=sceneFast;}
    if(Math.abs(previousScene.dark-dark)>.001){scene.setDark(dark);previousScene.dark=dark;}
  }
  runtime.fast=sceneFast;runtime.dark=dark;
  // Touch reveal belongs to the relief canvas only. Keep layout variables tied
  // to scroll velocity so a tap cannot scale the whole page on mobile.
  root.style.setProperty('--overview-scale',String(1/(1+3*fast)));
  root.style.setProperty('--overview-title',String(clamp((fast-.15)*1.5)));
  root.style.setProperty('--overview-copy',String(1-fast*.85));
  if(!reduced.matches&&!touch.matches){
    currentPointer.x+=(pointer.x-currentPointer.x)*.24;
    currentPointer.y+=(pointer.y-currentPointer.y)*.24;
    cursor.style.left=currentPointer.x+'px';cursor.style.top=currentPointer.y+'px';
  }
}
function prepareGlyphReveal(el){
  if(!el||el.dataset.glyphReveal==='true')return [...el.querySelectorAll('.reveal-glyph')];
  const text=el.textContent.trim();
  el.dataset.glyphReveal='true';
  el.setAttribute('aria-label',text);
  el.replaceChildren();
  for(const char of [...text]){
    const span=document.createElement('span');
    span.className='reveal-glyph';
    span.setAttribute('aria-hidden','true');
    span.textContent=char===' '?'\u00a0':char;
    el.append(span);
  }
  return [...el.querySelectorAll('.reveal-glyph')];
}
async function start(){
  const id=++bootId;runtime.ready=false;
  if(!loaderFinished)beginLoader();
  lenis?.destroy();lenis=undefined;animationContext?.revert();animationContext=undefined;
  scene?.dispose();scene=undefined;runtime.scene=null;
  body.classList.remove('has-motion','scene-ready');
  const motion=!reduced.matches;
  runtime.mode=motion?'motion':'reduced';
  if(motion){
    body.classList.add('has-motion');
    // Native touch scrolling is steadier on phones; keep Lenis for desktop wheels.
    lenis=touch.matches?null:new Lenis({lerp:.05,smoothWheel:true,syncTouch:false,anchors:false});
    const manifestoGlyphs=prepareGlyphReveal(document.querySelector('.manifesto'));
    animationContext=gsap.context(()=>{
      if(document.querySelector('.intro'))gsap.set('.intro-brand, .intro-identity, .scroll-cue',{autoAlpha:0,y:24,filter:'blur(14px)'});
      document.querySelectorAll('[data-reveal]:not(.manifesto)').forEach(el=>{
        const display=el.classList.contains('display');
        gsap.fromTo(el,{opacity:display?.15:1,filter:display?'blur(5px)':'none',y:display?36:16},{opacity:1,filter:display?'blur(0px)':'none',y:0,ease:'none',scrollTrigger:{trigger:el,start:'top 100%',end:display?'top 75%':'top 87%',scrub:.45}});
      });
      if(manifestoGlyphs.length){
        gsap.fromTo(manifestoGlyphs,
          {opacity:.15,filter:'blur(10px)',y:24,clipPath:'inset(-12% 100% -20% -10%)'},
          {opacity:1,filter:'blur(0px)',y:0,clipPath:'inset(-12% -10% -20% -10%)',stagger:.025,ease:'none',scrollTrigger:{trigger:'.manifesto',start:'top 96%',end:'top 42%',scrub:.65}});
      }
      memberCards.forEach(el=>gsap.fromTo(el,{opacity:.18,filter:'blur(10px)',y:100,scale:.78},{opacity:1,filter:'blur(0px)',y:0,scale:1.04,ease:'none',scrollTrigger:{trigger:el,start:'top 94%',end:'top 48%',scrub:.18}}));
      if(!touch.matches){
        document.querySelectorAll('.project-media').forEach(el=>gsap.fromTo(el,{y:innerWidth*.027},{y:-innerWidth*.027,ease:'none',scrollTrigger:{trigger:el.parentElement,start:'top bottom',end:'bottom top',scrub:.8}}));
        if(document.querySelector('.intro'))gsap.to('.intro-brand, .intro-identity, .scroll-cue',{y:innerHeight*.17,ease:'none',scrollTrigger:{trigger:'.intro',start:'top top',end:'bottom top',scrub:true}});
      }
    });
  }
  try{
    setLoaderProgress(.12);
    const {createRelief}=await import('./reference-relief.bundle.js?v=garden-21');
    if(id!==bootId||disposed)return;
    const task=sceneQueue.then(async()=>{
      if(id!==bootId||disposed)return;
      const bundleScript=document.querySelector('script[type="module"][src*="garden.bundle"]');
      const bundleUrl=bundleScript?.src||new URL('./home-assets/garden.bundle.js',document.baseURI).href;
      const assetBase=new URL('relief-assets/',bundleUrl).href;
      const mobileQuality=touch.matches||innerWidth<768||/Android|iPhone|iPad|iPod/i.test(navigator.userAgent);
      const next=await createRelief({canvas,reducedMotion:!motion,quality:mobileQuality?'low':'high',randomSeed:42,assetBase,onProgress:value=>setLoaderProgress(.16+value*.78)});
      if(id!==bootId||disposed){next.dispose();return;}
      previousScene={scroll:-1,fast:-1,dark:-1};scene=next;
      scene.setScroll(scrollY);scene.setDark(footerAmount);
      runtime.scene=scene.stats;body.classList.add('scene-ready');
    });
    sceneQueue=task.catch(()=>{});await task;
  }catch(error){if(id===bootId&&!disposed){runtime.errors.push(String(error));runtime.mode='static-fallback';}}
  if(id===bootId){runtime.ready=true;finishLoader();ScrollTrigger.refresh();measure();}
}
reduced.addEventListener('change',start);
window.addEventListener('resize',()=>{scene?.resize(innerWidth,innerHeight);ScrollTrigger.refresh();measure();});
document.addEventListener('visibilitychange',()=>{lastFrame=0;lastScroll=scrollY;});
document.querySelectorAll('a[href^="#"]').forEach(link=>link.addEventListener('click',event=>{
  const hash=link.getAttribute('href');if(hash==='#')return;const target=document.querySelector(hash);if(!target)return;
  if(lenis){event.preventDefault();lenis.scrollTo(target,{offset:hash==='#top'?0:-100,duration:1.6,onComplete:()=>{history.pushState(null,'',hash);target.focus?.({preventScroll:true});}});}
}));
window.addEventListener('pointermove',event=>{
  pointer.x=event.clientX;pointer.y=event.clientY;
  if(hoverMedia&&!touch.matches&&!reduced.matches){
    const r=hoverMedia.getBoundingClientRect();
    hoverMedia.style.setProperty('--mx',String((event.clientX-r.left)/r.width-.5));
    hoverMedia.style.setProperty('--my',String((event.clientY-r.top)/r.height-.5));
  }
},{passive:true});
window.addEventListener('pointerdown',event=>{
  if(touch.matches&&!reduced.matches){touchReveal=Math.max(touchReveal,.2);body.classList.add('touch-revealing');window.setTimeout(()=>body.classList.remove('touch-revealing'),360);}
},{passive:true});
window.addEventListener('pointerout',event=>{if(!event.relatedTarget){pointer.x=-100;pointer.y=-100;}});
media.forEach(el=>{
  el.addEventListener('pointerenter',()=>{
    hoverMedia=el;cursor.classList.add('is-media');
  if(!reduced.matches&&!touch.matches)gsap.to('#liquid feDisplacementMap',{attr:{scale:15},duration:1.4,ease:'sine.out'});
  });
  el.addEventListener('pointerleave',()=>{
    hoverMedia=null;cursor.classList.remove('is-media');
    gsap.to('#liquid feDisplacementMap',{attr:{scale:0},duration:.8});
    el.style.setProperty('--mx','0');el.style.setProperty('--my','0');
  });
});
inkLinks.forEach(el=>{
  el.addEventListener('pointerenter',()=>{if(!reduced.matches&&!touch.matches)gsap.to('#liquid feDisplacementMap',{attr:{scale:24},duration:.75,ease:'sine.out'});});
  el.addEventListener('pointerleave',()=>{gsap.to('#liquid feDisplacementMap',{attr:{scale:0},duration:.8,ease:'sine.out'});});
});
window.addEventListener('pagehide',event=>{if(event.persisted)return;disposed=true;++bootId;lenis?.destroy();animationContext?.revert();scene?.dispose();gsap.ticker.remove(frame);});
measure();gsap.ticker.add(frame);gsap.ticker.lagSmoothing(0);
if(document.fonts?.ready)document.fonts.ready.then(()=>ScrollTrigger.refresh());
start();
