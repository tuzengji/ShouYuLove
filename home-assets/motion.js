import { gsap } from 'gsap';
import { ScrollTrigger } from 'gsap/ScrollTrigger';
import Lenis from 'lenis';
import { createDaylightScene } from './daylight-scene.js';

gsap.registerPlugin(ScrollTrigger);

// Reference timing measurements are documented in docs/research/daylight/MOTION.md.
export function startMotion() {
  const root = document.documentElement;
  const originals = new Map();
  const sourceText = document.querySelectorAll('[data-split]');
  sourceText.forEach(element => {
    originals.set(element, element.innerHTML);
    element.setAttribute('aria-label', element.innerText);
    const walker = document.createTreeWalker(element, NodeFilter.SHOW_TEXT);
    const nodes = [];
    while (walker.nextNode()) nodes.push(walker.currentNode);
    nodes.forEach(node => {
      const fragment = document.createDocumentFragment();
      [...node.textContent].forEach(letter => {
        const span = document.createElement('span');
        span.className = 'char'; span.textContent = letter; span.setAttribute('aria-hidden', 'true');
        fragment.append(span);
      });
      node.replaceWith(fragment);
    });
  });
  root.classList.add('motion-active');
  const daylight = createDaylightScene();
  let lenis;
  let horizontal;
  let geometry;
  const media = gsap.matchMedia();
  const controls = document.querySelector('.journey-controls');
  const stage = document.querySelector('.journey');
  const track = document.querySelector('.journey-track');
  const panels = [...document.querySelectorAll('.journey-panel')];
  const previous = document.querySelector('.journey-previous');
  const next = document.querySelector('.journey-next');
  const position = document.querySelector('.journey-position');
  let currentPanel = 0;

  const absoluteTop = element => element.getBoundingClientRect().top + window.scrollY;
  function panelY(panel) {
    const travel = track.scrollWidth - innerWidth;
    const x = panel.offsetLeft - Math.max(0, (innerWidth - panel.offsetWidth) / 2);
    return absoluteTop(stage) + Math.max(0, Math.min(1, x / travel)) * (stage.offsetHeight - innerHeight);
  }
  function scrollToHash(hash, immediate = false, focus = false) {
    let target;
    try { target = document.querySelector(hash || '#top'); } catch (_) { return false; }
    if (!target) return false;
    let y = absoluteTop(target) - 108;
    if (hash === '#projects') y = absoluteTop(target);
    if (hash === '#teamwork') y = absoluteTop(target) - 60;
    if (hash === '#top' || hash === '#welcome') y = 0;
    if (hash === '#about') y = absoluteTop(target) + (target.offsetHeight - innerHeight) * .72;
    if (target.matches('.journey-panel') && root.classList.contains('motion-desktop')) y = panelY(target);
    const finish = () => {
      if (!focus) return;
      if (!target.hasAttribute('tabindex')) target.setAttribute('tabindex', '-1');
      target.focus({ preventScroll: true });
    };
    if (lenis) {
      // A deep link can run before Lenis observes the expanded animation layout.
      lenis.resize();
      lenis.scrollTo(Math.max(0, y), { immediate, duration: 1.1, onComplete: finish });
    }
    else { window.scrollTo({ top: Math.max(0, y), behavior: 'instant' }); finish(); }
    return true;
  }

  media.add({ desktop: '(min-width: 1024px)', mobile: '(max-width: 1023px)' }, context => {
    const { desktop } = context.conditions;
    root.classList.toggle('motion-desktop', desktop);
    const instance = new Lenis({ lerp: .145, wheelMultiplier: 1, syncTouch: false, autoRaf: false });
    lenis = instance;
    instance.on('scroll', ScrollTrigger.update);
    const tick = time => instance.raf(time * 1000);
    gsap.ticker.add(tick);
    gsap.ticker.lagSmoothing(0);

    const daylightFrame = { value: 0 };
    gsap.to(daylightFrame, {
      value: 169, duration: 1, ease: 'power1.out',
      onUpdate: () => daylight.draw(daylightFrame.value),
      scrollTrigger: { id: 'daylight-hero', trigger: '.hero', start: 'top top', end: 'bottom bottom', scrub: true },
    });
    gsap.from('.hero-copy', { y: 18, duration: .9, ease: 'power3.out', clearProps: 'transform' });
    gsap.from('.quick-start', { y: 18, duration: .9, delay: .15, ease: 'power3.out', clearProps: 'transform' });

    // Reveal the short heading first, then its one supporting paragraph.
    const attention = gsap.timeline({ scrollTrigger: { id: 'daylight-attention', trigger: '.attention', start: 'top top', end: 'bottom bottom', scrub: true } });
    attention.fromTo('.attention-statement .char', { opacity: 0, y: -10, z: 25, rotationX: 10 }, { opacity: 1, y: 0, z: 0, rotationX: 0, duration: 20 * 2 / 6, stagger: { amount: 20 * 4 / 6 }, ease: 'power3.out' }, 15)
      .fromTo('.attention-statement p', { opacity: 0, y: 12 }, { opacity: 1, y: 0, duration: 12, ease: 'power3.out' }, 28)
      .to('.attention-statement', { opacity: 0, duration: 10, ease: 'none' }, 76)
      .fromTo('.attention-shadow', { xPercent: 4 }, { xPercent: -4, duration: 100, ease: 'none' }, 0)
      .fromTo('.attention-pin', { clipPath: 'inset(0 0% 0 0)' }, { clipPath: 'inset(0 100% 0 0)', duration: 21, ease: 'none' }, 78)
      .to({}, { duration: 1 }, 99);

    function updateControls() {
      const center = innerWidth / 2;
      let distance = Infinity;
      panels.forEach((panel, index) => {
        const bounds = panel.getBoundingClientRect();
        const candidate = Math.abs(bounds.left + bounds.width / 2 - center);
        if (candidate < distance) { distance = candidate; currentPanel = index; }
      });
      controls.style.visibility = distance > innerWidth * .65 ? 'hidden' : 'visible';
      position.textContent = `${currentPanel + 1} / ${panels.length}`;
      previous.disabled = currentPanel === 0;
      next.disabled = currentPanel === panels.length - 1;
    }
    const move = direction => lenis.scrollTo(panelY(panels[Math.max(0, Math.min(panels.length - 1, currentPanel + direction))]), { duration: .9 });
    const prevClick = () => move(-1);
    const nextClick = () => move(1);
    const focusPanel = event => {
      const panel = event.target.closest('.project-slide');
      if (!panel) return;
      const rect = panel.getBoundingClientRect();
      if (rect.left < -40 || rect.right > innerWidth + 40) lenis.scrollTo(panelY(panel), { immediate: true });
    };
    if (desktop) {
      // Original maps total strip width in vw to the same numeric height in vh.
      geometry = () => { stage.style.height = `${track.scrollWidth / innerWidth * 100}svh`; };
      geometry();
      ScrollTrigger.addEventListener('refreshInit', geometry);
      horizontal = gsap.to(track, { x: () => -(track.scrollWidth - innerWidth), ease: 'none', scrollTrigger: { id: 'daylight-horizontal', trigger: stage, start: 'top top', end: 'bottom bottom', scrub: true, invalidateOnRefresh: true, onUpdate: updateControls } });
      document.querySelectorAll('.project-art').forEach(art => gsap.fromTo(art, { x: 45 }, { x: -45, ease: 'none', scrollTrigger: { trigger: art.closest('.project-slide'), containerAnimation: horizontal, start: 'left right', end: 'right left', scrub: true } }));
      controls.hidden = false;
      previous.addEventListener('click', prevClick); next.addEventListener('click', nextClick);
      track.addEventListener('focusin', focusPanel);
      updateControls();
    }

    const light = gsap.timeline({ scrollTrigger: { id: 'daylight-light', trigger: '.light-story', start: 'top top', end: 'bottom bottom', scrub: true, invalidateOnRefresh: true } });
    light.fromTo('.light-message .char', { opacity: 0, y: -10, z: 25, rotationX: 10 }, { opacity: 1, y: 0, z: 0, rotationX: 0, duration: 20 * 4 / 6, stagger: { amount: 20 * 2 / 6 }, ease: 'power3.out' }, 5)
      .fromTo('.light-sheet', { backgroundColor: 'var(--paper)' }, { backgroundColor: '#ff9d00', duration: 10, ease: 'power1.inOut' }, 40)
      .fromTo('.light-message', { color: 'var(--ink)' }, { color: '#24291f', duration: 10, ease: 'power1.inOut' }, 40)
      .fromTo('.light-stage', { scale: 1 }, { scale: desktop ? .52 : .5, duration: 15, ease: 'power2.inOut' }, 50)
      .to('.light-sheet', { borderRadius: 28, rotationY: desktop ? -7 : 0, rotationX: 4, duration: 15, ease: 'power2.inOut' }, 50)
      .to('.light-message', { scale: desktop ? .52 : .5, duration: 15, ease: 'power2.inOut' }, 50)
      .to('.light-message', { opacity: 0, duration: 7.5, ease: 'power2.inOut' }, 65)
      .to('.light-stage', { x: () => desktop ? -innerWidth * .23 : 0, y: () => desktop ? 0 : -innerHeight * .24, duration: 22.5, ease: 'power2.inOut' }, 70)
      .to('.light-message', { x: () => desktop ? innerWidth * .255 : 0, y: () => desktop ? 0 : innerHeight * .29, scale: desktop ? .67 : .9, color: 'var(--ink)', duration: 22.5, ease: 'power2.inOut' }, 70)
      .to('.light-message', { opacity: 1, duration: 15, ease: 'power2.out' }, 85);

    // The reference reveal responds to the pointer by ±0.025π radians.
    // An independent layer lets the scroll timeline reverse without losing its transforms.
    const tilt = document.querySelector('.light-tilt');
    const tiltX = gsap.quickTo(tilt, 'rotationX', { duration: .35, ease: 'power2.out' });
    const tiltY = gsap.quickTo(tilt, 'rotationY', { duration: .35, ease: 'power2.out' });
    const pointerTilt = event => {
      const progress = light.scrollTrigger.progress;
      if (!desktop || event.pointerType === 'touch' || progress < .5 || progress > .93) return;
      tiltX((event.clientY / innerHeight - .5) * -9);
      tiltY((event.clientX / innerWidth - .5) * 9);
    };
    const resetTilt = () => { tiltX(0); tiltY(0); };
    document.querySelector('.light-pin').addEventListener('pointermove', pointerTilt);
    document.querySelector('.light-pin').addEventListener('pointerleave', resetTilt);

    document.querySelectorAll('.reveal').forEach(element => gsap.fromTo(element, { opacity: 0, y: 24 }, { opacity: 1, y: 0, duration: .75, ease: 'power3.out', scrollTrigger: { trigger: element, start: 'top 92%', once: true } }));
    gsap.fromTo('.footer-wordmark', { y: 28 }, { y: 0, ease: 'none', scrollTrigger: { trigger: '.site-footer', start: 'top bottom', end: 'bottom bottom', scrub: true } });
    ScrollTrigger.refresh();
    return () => {
      gsap.ticker.remove(tick);
      instance.destroy();
      if (lenis === instance) lenis = undefined;
      previous.removeEventListener('click', prevClick); next.removeEventListener('click', nextClick);
      track.removeEventListener('focusin', focusPanel);
      document.querySelector('.light-pin').removeEventListener('pointermove', pointerTilt);
      document.querySelector('.light-pin').removeEventListener('pointerleave', resetTilt);
      if (geometry) ScrollTrigger.removeEventListener('refreshInit', geometry);
      stage.style.removeProperty('height');
      controls.hidden = true; controls.style.removeProperty('visibility');
      root.classList.remove('motion-desktop');
    };
  });

  let disposed = false;
  document.fonts.ready.then(() => { if (!disposed) ScrollTrigger.refresh(); });
  return {
    scrollToHash,
    refresh: () => ScrollTrigger.refresh(),
    destroy() {
      disposed = true;
      media.revert();
      daylight.destroy();
      root.classList.remove('motion-active', 'motion-desktop');
      [...root.classList].filter(name => name.startsWith('lenis')).forEach(name => root.classList.remove(name));
      originals.forEach((html, element) => { element.innerHTML = html; element.removeAttribute('aria-label'); });
    },
  };
}
