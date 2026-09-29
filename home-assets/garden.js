import { gsap } from 'gsap';
import { ScrollTrigger } from 'gsap/ScrollTrigger';
import Lenis from 'lenis';

gsap.registerPlugin(ScrollTrigger);
const root=document.documentElement, body=document.body;
const canvas=document.querySelector('#garden'), footer=document.querySelector('.site-footer');
const reduced=matchMedia('(prefers-reduced-motion: reduce)'), touch=matchMedia('(pointer: coarse)');
const cursor=document.querySelector('.cursor'), media=[...document.querySelectorAll('.project-media')];
let lenis, scene, animationContext, bootId=0;
let lastScroll=scrollY, velocity=0, fast=0, dark=0, footerAmount=0, disposed=false, lastFrame=0;
let sceneQueue=Promise.resolve(), previousScene={scroll:-1,fast:-1,dark:-1};
let pointer={x:-100,y:-100}, currentPointer={x:-100,y:-100}, hoverMedia=null;
const runtime={ready:false,errors:[],mode:'loading',scene:null,scroll:0,fast:0,dark:0};
window.__garden=runtime;
const clamp=(v,min=0,max=1)=>Math.max(min,Math.min(max,v));
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
  const fastTarget=(!reduced.matches&&!touch.matches&&velocity>75)?clamp((velocity-75)/200):0;
  fast+=(fastTarget-fast)*(fastTarget>fast?.035:.06);
  measure();
  dark+=(footerAmount-dark)*(reduced.matches?1:.045);
  if(scene){
    if(previousScene.scroll!==scrollY){scene.setScroll(scrollY);previousScene.scroll=scrollY;}
    if(Math.abs(previousScene.fast-fast)>.001){scene.setFast(fast);previousScene.fast=fast;}
    if(Math.abs(previousScene.dark-dark)>.001){scene.setDark(dark);previousScene.dark=dark;}
  }
  runtime.fast=fast;runtime.dark=dark;
  root.style.setProperty('--overview-scale',String(1/(1+3*fast)));
  root.style.setProperty('--overview-title',String(clamp((fast-.15)*1.5)));
  root.style.setProperty('--overview-copy',String(1-fast*.85));
  if(!reduced.matches&&!touch.matches){
    currentPointer.x+=(pointer.x-currentPointer.x)*.24;
    currentPointer.y+=(pointer.y-currentPointer.y)*.24;
    cursor.style.left=currentPointer.x+'px';cursor.style.top=currentPointer.y+'px';
  }
}
async function start(){
  const id=++bootId;runtime.ready=false;
  lenis?.destroy();lenis=undefined;animationContext?.revert();animationContext=undefined;
  scene?.dispose();scene=undefined;runtime.scene=null;
  body.classList.remove('has-motion','scene-ready');
  const motion=!reduced.matches;
  runtime.mode=motion?'motion':'reduced';
  if(motion){
    body.classList.add('has-motion');
    lenis=new Lenis({lerp:.05,smoothWheel:true,syncTouch:false,anchors:false});
    animationContext=gsap.context(()=>{
      if(document.querySelector('.intro'))gsap.from('.intro-brand, .intro-identity, .scroll-cue',{opacity:0,y:16,duration:1.25,stagger:.12,ease:'sine.out',delay:.15,clearProps:'transform,opacity'});
      document.querySelectorAll('[data-reveal]').forEach(el=>{
        const display=el.classList.contains('display');
        gsap.fromTo(el,{opacity:display?.15:1,filter:display?'blur(5px)':'none',y:display?36:16},{opacity:1,filter:display?'blur(0px)':'none',y:0,ease:'none',scrollTrigger:{trigger:el,start:'top 100%',end:display?'top 75%':'top 87%',scrub:.45}});
      });
      if(!touch.matches){
        document.querySelectorAll('.project-media').forEach(el=>gsap.fromTo(el,{y:innerWidth*.027},{y:-innerWidth*.027,ease:'none',scrollTrigger:{trigger:el.parentElement,start:'top bottom',end:'bottom top',scrub:.8}}));
        if(document.querySelector('.intro'))gsap.to('.intro-brand, .intro-identity, .scroll-cue',{y:innerHeight*.17,ease:'none',scrollTrigger:{trigger:'.intro',start:'top top',end:'bottom top',scrub:true}});
      }
    });
  }
  try{
    const {createRelief}=await import('./reference-relief.bundle.js?v=garden-18');
    if(id!==bootId||disposed)return;
    const task=sceneQueue.then(async()=>{
      if(id!==bootId||disposed)return;
      const bundleScript=document.querySelector('script[type="module"][src*="garden.bundle"]');
      const bundleUrl=bundleScript?.src||new URL('./home-assets/garden.bundle.js',document.baseURI).href;
      const assetBase=new URL('relief-assets/',bundleUrl).href;
      const mobileQuality=touch.matches||innerWidth<768||/Android|iPhone|iPad|iPod/i.test(navigator.userAgent);
      const next=await createRelief({canvas,reducedMotion:!motion,quality:mobileQuality?'low':'high',randomSeed:42,assetBase});
      if(id!==bootId||disposed){next.dispose();return;}
      previousScene={scroll:-1,fast:-1,dark:-1};scene=next;
      scene.setScroll(scrollY);scene.setDark(footerAmount);
      runtime.scene=scene.stats;body.classList.add('scene-ready');
    });
    sceneQueue=task.catch(()=>{});await task;
  }catch(error){if(id===bootId&&!disposed){runtime.errors.push(String(error));runtime.mode='static-fallback';}}
  if(id===bootId){runtime.ready=true;ScrollTrigger.refresh();measure();}
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
window.addEventListener('pagehide',event=>{if(event.persisted)return;disposed=true;++bootId;lenis?.destroy();animationContext?.revert();scene?.dispose();gsap.ticker.remove(frame);});
measure();gsap.ticker.add(frame);gsap.ticker.lagSmoothing(0);
if(document.fonts?.ready)document.fonts.ready.then(()=>ScrollTrigger.refresh());
start();
