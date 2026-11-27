// 首页：首屏那只手递出的爱心，随滚动沿手画的虚线飘过整页，最后落进页尾另一只手里。
// 没有脚本或系统要求减少动态时，两只手各自托着一颗静止的爱心。
(() => {
  const { pointer, onFrame, wake, still, touch } = SylNext;
  const root = document.documentElement, id = (name) => document.getElementById(name);
  const from = id('heart-from'), to = id('heart-to'), route = id('route'), heart = id('heart');
  const hands = document.querySelectorAll('.hand');
  if (!from || !to || !route.querySelector('path').getPointAtLength) return;
  const [ahead, done] = route.querySelectorAll('path');
  const clip = route.querySelector('clipPath rect');
  const HEART_RATIO = 90 / 104;
  let table = [], start, end, firstLeg, lastLeg, transit, current = null;

  // Offsets ignore transforms, so entrance animations do not skew the measurement.
  const centre = (element) => {
    let x = element.offsetWidth / 2, y = element.offsetHeight / 2;
    for (let node = element; node; node = node.offsetParent) { x += node.offsetLeft; y += node.offsetTop; }
    return { x, y, size: element.offsetWidth };
  };
  const ease = (t) => { t = Math.min(1, Math.max(0, t)); return t * t * (3 - 2 * t); };

  function build() {
    const width = root.clientWidth, height = root.scrollHeight;
    start = centre(from); end = centre(to);
    const gutter = document.querySelector('[data-stop] .wrap').getBoundingClientRect().left;
    const weave = gutter >= 110;
    const offset = weave ? Math.min(gutter / 2, 100) : gutter * .4;
    transit = weave ? 46 : gutter > 50 ? 28 : 23;
    const points = [];
    let left = true;
    for (const stop of document.querySelectorAll('[data-stop]')) {
      const top = stop.offsetTop, inset = Math.min(90, stop.offsetHeight * .25);
      const a = top + inset, b = top + stop.offsetHeight - inset;
      const x = left || !weave ? gutter - offset : width - gutter + offset;
      const steps = Math.max(1, Math.round((b - a) / 380));
      const sway = weave ? 16 : 2;
      for (let i = 0; i <= steps; i++) points.push({ x: x + (i % 2 ? sway : -sway) * (left ? 1 : -1), y: a + (b - a) * i / steps });
      left = !left;
    }
    const first = points[0], last = points[points.length - 1];
    const r = (n) => Math.round(n * 10) / 10;
    // Leave the palm sideways, toward the reader; arrive in the other palm from above.
    let d = `M${r(start.x)} ${r(start.y)}C${r(start.x - (start.x - first.x) * .5)} ${r(start.y + (first.y - start.y) * .12)} ${r(first.x)} ${r(start.y + (first.y - start.y) * .5)} ${r(first.x)} ${r(first.y)}`;
    for (let i = 1; i < points.length; i++) {
      const p = points[i - 1], q = points[i], m = r((p.y + q.y) / 2);
      d += `C${r(p.x)} ${m} ${r(q.x)} ${m} ${r(q.x)} ${r(q.y)}`;
    }
    d += `C${r(last.x)} ${r(last.y + (end.y - last.y) * .35)} ${r(end.x)} ${r(end.y - (end.y - last.y) * .8)} ${r(end.x)} ${r(end.y)}`;
    route.setAttribute('viewBox', `0 0 ${width} ${height}`);
    route.style.height = height + 'px';
    ahead.setAttribute('d', d); done.setAttribute('d', d);
    clip.setAttribute('width', width);
    firstLeg = Math.min(first.y - start.y, 320); lastLeg = Math.min(end.y - last.y, 320);
    table = [];
    const length = ahead.getTotalLength();
    for (let at = 0; at <= length; at += 4) { const p = ahead.getPointAtLength(at); table.push(p.x, p.y); }
    table.push(end.x, end.y);
  }

  const target = () => {
    const range = root.scrollHeight - innerHeight;
    return start.y + (end.y - start.y) * (range > 0 ? Math.min(1, Math.max(0, scrollY / range)) : 0);
  };

  function place(y, now) {
    // The route never climbs, so its samples can be searched by height.
    let low = 0, high = table.length / 2 - 1;
    while (high - low > 1) { const middle = (low + high) >> 1; if (table[middle * 2 + 1] <= y) low = middle; else high = middle; }
    const x0 = table[low * 2], y0 = table[low * 2 + 1], x1 = table[high * 2], y1 = table[high * 2 + 1];
    const t = y1 > y0 ? Math.min(1, Math.max(0, (y - y0) / (y1 - y0))) : 0;
    const x = x0 + (x1 - x0) * t;
    const leaving = ease((y - start.y) / firstLeg), arriving = ease((end.y - y) / lastLeg);
    const flying = Math.min(leaving, arriving), rest = 1 - flying;
    const size = transit + (start.size - transit) * (1 - leaving) + (end.size - transit) * (1 - arriving);
    // In flight it leans into its path and rocks like a falling leaf; at rest it tips toward the pointer.
    const lean = Math.max(-16, Math.min(16, (x1 - x0) / Math.max(1, y1 - y0) * 12)) * flying
               + Math.sin(y / 90) * 9 * flying + (pointer.x * 7 + Math.sin(now * 1.1) * 2.5) * rest;
    const bob = Math.sin(now * 1.25) * size * .022 * rest;
    heart.style.width = size.toFixed(1) + 'px';
    heart.style.setProperty('--rest', rest.toFixed(2));
    heart.style.transform = `translate3d(${(x - size / 2).toFixed(1)}px,${(y - size * HEART_RATIO / 2 + bob).toFixed(1)}px,0) rotate(${lean.toFixed(1)}deg)`;
    clip.setAttribute('height', Math.max(0, y).toFixed(1));
  }

  function refresh() {
    build();
    if (still.matches) {
      current = null;
      root.classList.remove('route-on'); root.classList.add('route-still');
      clip.setAttribute('height', 0);
    } else {
      root.classList.remove('route-still'); root.classList.add('route-on');
      current = target();
    }
    wake();
  }

  // Small hearts scatter when the heart lands.
  const sparkArt = id('spark').innerHTML;
  let armed = false;
  function arrive() {
    if (current < end.y - 260) armed = true;
    if (!armed || current < end.y - 1.5) return;
    armed = false;
    for (let i = 0; i < 9; i++) {
      const spark = document.createElement('div'), angle = -Math.PI / 2 + (i / 8 - .5) * 2.6 + (Math.random() - .5) * .3;
      const reach = end.size * (.8 + Math.random() * .6);
      // On a narrow screen a spark must not fly past the page edge, or the page would scroll sideways for a moment.
      const edge = root.clientWidth - 22, drift = Math.max(22 - end.x, Math.min(edge - end.x, Math.cos(angle) * reach));
      spark.className = 'spark heart-art';
      spark.style.cssText = `left:${end.x}px;top:${end.y}px;--s:${(end.size * (.1 + Math.random() * .1)).toFixed(0)}px;--x:${drift.toFixed(0)}px;--y:${(Math.sin(angle) * reach).toFixed(0)}px;--r:${(Math.random() * 90 - 45).toFixed(0)}deg;--d:${(Math.random() * .18).toFixed(2)}s`;
      spark.innerHTML = sparkArt;
      spark.addEventListener('animationend', () => spark.remove());
      document.body.appendChild(spark);
    }
  }

  // The dream lights up character by character as it crosses the middle of the screen.
  const dream = document.querySelector('.dream'), letters = dream ? [...dream.querySelectorAll('i')] : [];
  let lit = -1;
  function light() {
    if (!dream) return;
    const box = dream.getBoundingClientRect();
    const progress = Math.min(1, Math.max(0, (innerHeight * .86 - box.top) / (box.height + innerHeight * .34)));
    const count = Math.round(progress * letters.length);
    if (count === lit) return;
    letters.forEach((letter, index) => letter.classList.toggle('on', index < count));
    lit = count;
  }

  onFrame((now, delta) => {
    if (!start) return;
    if (current !== null) {
      const goal = target();
      current += (goal - current) * Math.min(1, delta * 10);
      if (Math.abs(goal - current) < .3) current = goal;
      place(current, now);
      arrive();
    }
    light();
    // The hands shift a few pixels against the pointer, like paper on a second layer. A touch screen has no
    // pointer to follow, so there they float slowly on their own, and the first hand lags a little behind the scroll.
    hands.forEach((hand, index) => {
      let x = -pointer.x * 7, y = -pointer.y * 5;
      if (touch.matches) {
        x = Math.sin(now * .7 + index * 2) * 4;
        y = Math.sin(now * .95 + index * 2) * 5 + (index ? 0 : Math.min(scrollY, 320) * .06);
      }
      hand.style.setProperty('--px', x.toFixed(1)); hand.style.setProperty('--py', y.toFixed(1));
    });
  });

  let pending = 0;
  const schedule = () => { cancelAnimationFrame(pending); pending = requestAnimationFrame(refresh); };
  if (scrollY < 8 && !still.matches) heart.classList.add('is-arriving');
  refresh();
  addEventListener('resize', schedule);
  addEventListener('load', schedule);
  addEventListener('scroll', wake, { passive: true });
  still.addEventListener?.('change', schedule);
  document.fonts?.ready.then(schedule);
  if (window.ResizeObserver) new ResizeObserver(schedule).observe(document.querySelector('main'));
})();
