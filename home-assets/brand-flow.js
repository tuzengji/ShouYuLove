import { Vector2, WebGLRenderTarget, RGBAFormat, LinearFilter, RawShaderMaterial, Scene, Camera, Mesh, Color } from 'three';
import { fullscreenTriangle } from './brand-fluid.js';
import { extrusionFlowVertex, extrusionFlowFragment } from './brand-shaders.js';
const clamp01 = value => Math.max(0, Math.min(1, Number(value) || 0));
export function seededRandom(seed) {
  let state = Number(seed) >>> 0;
  return () => {
    state += 0x6D2B79F5;
    let x = state;
    x = Math.imul(x ^ x >>> 15, x | 1);
    x ^= x + Math.imul(x ^ x >>> 7, x | 61);
    return ((x ^ x >>> 14) >>> 0) / 4294967296;
  };
}

// Seeded GSAP RoughEase interpolation for the exact taper:none/clamp:true settings.
function roughEase(random, duration, strong) {
  const points = [[0, 0], [1, 1]], bump = (strong ? 3 : 2) * .4;
  for (let i = 0; i < Math.floor(duration * 12); i++) {
    const x = random(), template = strong ? 1 - (1 - x) ** 3 : x;
    points.push([x, clamp01(template + random() * bump - bump * .5)]);
  }
  points.sort((a, b) => a[0] - b[0]);
  return progress => {
    if (progress <= 0) return 0;
    if (progress >= 1) return 1;
    let i = 1;
    while (points[i][0] < progress) i++;
    const [x0, y0] = points[i - 1], [x1, y1] = points[i];
    return y0 + (y1 - y0) * (progress - x0) / (x1 - x0);
  };
}

export function idlePointer(seed, mouse) {
  const random = seededRandom(seed);
  let steps = [], stepIndex = 0, stepTime = 0;
  function nextLoop() {
    steps = []; stepIndex = 0; stepTime = 0;
    const count = 1 + Math.floor(random() * 3);
    let start = null;
    for (let i = 0; i < count; i++) {
      const strong = i !== count - 1 && random() < .7;
      const duration = strong ? .8 + random() * .2 : .7 + random() * .1;
      start ||= new Vector2((random() - .5) * 2, (random() - .5) * 2);
      const angle = Math.PI / 2 + (random() - .5) * 2 * Math.PI * .8;
      const radius = .7 + random() * .2;
      const end = new Vector2(Math.cos(angle) * radius, Math.sin(angle) * radius);
      for (const axis of ['x', 'y']) steps.push({
        axis, from: start[axis] / 2 + .5, to: end[axis] / 2 + .5, duration,
        ease: roughEase(random, duration, strong),
      });
      start = end;
    }
    steps.push({ axis: null, duration: Math.round((1 + random() * 2) * 100) / 100 });
  }
  nextLoop();
  return delta => {
    stepTime += delta;
    while (stepTime >= steps[stepIndex].duration) {
      const step = steps[stepIndex];
      if (step.axis) mouse[step.axis] = step.to;
      stepTime -= step.duration; stepIndex++;
      if (stepIndex === steps.length) { nextLoop(); break; }
    }
    const step = steps[stepIndex];
    if (step.axis) mouse[step.axis] = step.from + (step.to - step.from) * step.ease(stepTime / step.duration);
    else mouse.set(-1, -1);
  };
}

export function createExtrusion(renderer, maskNoise, time, type) {
  const options = { type, format: RGBAFormat, minFilter: LinearFilter, magFilter: LinearFilter, depthBuffer: false };
  let read = new WebGLRenderTarget(256, 256, options), write = read.clone();
  const uniform = { value: read.texture };
  const mouse = new Vector2(), velocity = new Vector2(), mouse2 = new Vector2(), velocity2 = new Vector2(1, 1);
  const material = new RawShaderMaterial({
    vertexShader: extrusionFlowVertex, fragmentShader: extrusionFlowFragment, depthTest: false, depthWrite: false,
    uniforms: {
      tMap: uniform, uFalloff: { value: .19 }, uAlpha: { value: 1 }, uDissipation: { value: .953 },
      uDeltaMult: { value: 1 }, tNoise: { value: maskNoise }, uTime: time,
      uAspect: { value: 1 }, uMouse: { value: mouse }, uVelocity: { value: velocity },
      uMouse2: { value: mouse2 }, uVelocity2: { value: velocity2 }, uOffset: { value: 0 },
    },
  });
  const geometry = fullscreenTriangle(), scene = new Scene(), camera = new Camera();
  const mesh = new Mesh(geometry, material); mesh.frustumCulled = false; scene.add(mesh);
  function reset() {
    const priorTarget = renderer.getRenderTarget(), priorColor = renderer.getClearColor(new Color());
    const priorAlpha = renderer.getClearAlpha();
    renderer.setClearColor(0, 0);
    for (const item of [read, write]) { renderer.setRenderTarget(item); renderer.clear(); }
    renderer.setRenderTarget(priorTarget); renderer.setClearColor(priorColor, priorAlpha);
    uniform.value = read.texture;
  }
  reset();
  return {
    uniform, mouse, velocity, mouse2, velocity2, reset,
    setAspect(value) { material.uniforms.uAspect.value = value; },
    update(offset, dtMult) {
      material.uniforms.uOffset.value = offset; material.uniforms.uDeltaMult.value = dtMult;
      const previousTarget = renderer.getRenderTarget();
      renderer.setRenderTarget(write); renderer.render(scene, camera); renderer.setRenderTarget(previousTarget);
      [read, write] = [write, read]; uniform.value = read.texture;
    },
    dispose() { read.dispose(); write.dispose(); geometry.dispose(); material.dispose(); },
  };
}

