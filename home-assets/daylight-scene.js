// Re-light one fixed view across the reference's 170-frame scroll interval.
// The hero uses one real photograph; gentle color fields supply the time-of-day change.
export function createDaylightScene() {
  const frame = document.querySelector('.hero-frame');
  const picture = document.querySelector('.hero-picture');
  const morning = picture.querySelector('img');
  const canvas = document.createElement('canvas');
  canvas.className = 'hero-canvas';
  canvas.setAttribute('aria-hidden', 'true');
  picture.after(canvas);
  const context = canvas.getContext('2d', { alpha: false });
  if (!context) { canvas.remove(); return { draw() {}, destroy() {} }; }
  let ready = false;
  let disposed = false;
  let current = 0;

  function fit(image, alpha = 1) {
    const scale = Math.max(canvas.width / image.naturalWidth, canvas.height / image.naturalHeight);
    const width = image.naturalWidth * scale;
    const height = image.naturalHeight * scale;
    const horizontalPosition = innerWidth < 768 ? .68 : .5;
    context.globalAlpha = alpha;
    context.drawImage(image, (canvas.width - width) * horizontalPosition, (canvas.height - height) / 2, width, height);
  }
  function draw(index = current) {
    current = Math.max(0, Math.min(169, Math.round(index)));
    if (!ready || disposed) return;
    // The static high-priority image already represents frame zero. Keep it as
    // the first paint instead of replacing it with a second full-size raster.
    if (current === 0) {
      context.clearRect(0, 0, canvas.width, canvas.height);
      canvas.dataset.frame = '0';
      canvas.dataset.period = 'morning';
      canvas.style.visibility = 'hidden';
      return;
    }
    const progress = current / 169;
    const noon = Math.max(0, 1 - Math.abs(progress - .24) / .24);
    context.clearRect(0, 0, canvas.width, canvas.height);
    const dusk = Math.max(0, (progress - .62) / .38);
    context.filter = `brightness(${1 + noon * .10 - dusk * .10}) saturate(${1 - noon * .06 + dusk * .04})`;
    fit(morning);
    context.filter = 'none';
    context.globalAlpha = 1;
    // Sunlight travels from the upper left to the upper right before disappearing.
    // The warm fill preserves the photograph's existing shadows.
    if (progress < .8) {
      const sunX = canvas.width * (.08 + progress * 1.2);
      const sunY = canvas.height * (.08 - .12 * Math.sin(progress * Math.PI));
      const radius = canvas.width * .65;
      const strength = Math.sin(progress / .8 * Math.PI) * .10;
      const light = context.createRadialGradient(sunX, sunY, 0, sunX, sunY, radius);
      light.addColorStop(0, `rgba(255,232,179,${strength})`);
      light.addColorStop(1, 'rgba(255,232,179,0)');
      context.fillStyle = light;
      context.fillRect(0, 0, canvas.width, canvas.height);
    }
    if (dusk) {
      context.fillStyle = `rgba(26,48,92,${dusk * .30})`;
      context.fillRect(0, 0, canvas.width, canvas.height);
    }
    canvas.dataset.frame = String(current);
    canvas.dataset.period = progress < .24 ? 'morning' : progress < .48 ? 'noon' : progress < .82 ? 'sunset' : 'night';
    canvas.style.visibility = 'visible';
  }
  function resize() {
    const pixelRatio = Math.min(devicePixelRatio || 1, innerWidth < 768 ? 1.25 : 1.5);
    canvas.width = Math.round(frame.clientWidth * pixelRatio);
    canvas.height = Math.round(frame.clientHeight * pixelRatio);
    draw();
  }
  const observer = new ResizeObserver(resize);
  observer.observe(frame);
  morning.decode().then(() => {
    if (disposed) return;
    ready = true;
    resize();
  }).catch(() => { if (!disposed) canvas.remove(); });
  return {
    draw,
    destroy() { disposed = true; observer.disconnect(); canvas.remove(); },
  };
}
