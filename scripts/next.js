// 新版页面共用的动态：统一的帧循环、指针位置，以及进入视野时的出现。
const SylNext = (() => {
  const root = document.documentElement;
  root.classList.add('js');
  const still = matchMedia('(prefers-reduced-motion: reduce)');
  // x, y run from -1 to 1 across the viewport and ease toward the real pointer.
  const pointer = { x: 0, y: 0, goalX: 0, goalY: 0 };
  addEventListener('pointermove', (event) => {
    if (event.pointerType === 'touch') return;
    pointer.goalX = event.clientX / innerWidth * 2 - 1; pointer.goalY = event.clientY / innerHeight * 2 - 1;
  }, { passive: true });

  const tasks = new Set();
  let frame = 0, before = 0;
  function tick(now) {
    frame = 0;
    const delta = Math.min(.05, before ? (now - before) / 1000 : .016);
    before = now;
    const ease = still.matches ? 1 : Math.min(1, delta * 5);
    pointer.x += (pointer.goalX - pointer.x) * ease; pointer.y += (pointer.goalY - pointer.y) * ease;
    for (const task of tasks) task(now / 1000, delta);
    // With reduced motion each wake paints a single frame.
    if (!still.matches && !document.hidden) frame = requestAnimationFrame(tick);
  }
  const wake = () => { if (!frame) { before = 0; frame = requestAnimationFrame(tick); } };
  const onFrame = (task) => { tasks.add(task); wake(); };
  document.addEventListener('visibilitychange', wake);
  still.addEventListener?.('change', wake);
  addEventListener('resize', wake);

  // Reveal once, when the element first comes into view.
  const hidden = document.querySelectorAll('.pop, .rise');
  if (window.IntersectionObserver) {
    const seen = new IntersectionObserver((entries) => {
      // Anything already scrolled past (a restored position, a jump) is shown without waiting.
      for (const entry of entries) if (entry.isIntersecting || entry.boundingClientRect.bottom < 0) { entry.target.classList.add('is-in'); seen.unobserve(entry.target); }
    }, { rootMargin: '0px 0px -7% 0px', threshold: .12 });
    hidden.forEach((element) => seen.observe(element));
  } else hidden.forEach((element) => element.classList.add('is-in'));

  // A work lights up under a mouse or under keyboard focus, never from a touch (which would leave it stuck on).
  const fine = matchMedia('(hover: hover) and (pointer: fine)');
  for (const tile of document.querySelectorAll('.tile')) {
    const light = (on) => () => tile.classList.toggle('is-lit', on);
    tile.addEventListener('pointerenter', (event) => { if (event.pointerType !== 'touch' && fine.matches) light(true)(); });
    tile.addEventListener('pointerleave', light(false));
    tile.addEventListener('focusin', (event) => { if (event.target.matches(':focus-visible')) light(true)(); });
    tile.addEventListener('focusout', light(false));
  }

  return { pointer, onFrame, wake, still };
})();
