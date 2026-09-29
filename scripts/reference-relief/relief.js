import {
  WebGLRenderer, PerspectiveCamera, Camera, Scene, Mesh, ShaderMaterial, RawShaderMaterial,
  TextureLoader, DataTexture, WebGLRenderTarget, Vector2, Color, FloatType, HalfFloatType,
  RGBAFormat, LinearFilter, RepeatWrapping, MirroredRepeatWrapping,
  LinearToneMapping, LinearEncoding,
} from 'three';
import { GLTFLoader } from 'three/addons/loaders/GLTFLoader.js';
import { DRACOLoader } from 'three/addons/loaders/DRACOLoader.js';
import { fullscreenTriangle, createFluid } from './fluid.js';
import {
  reliefVertex, reliefFragment, plasterFragment, fullscreenVertex,
  extrusionFlowVertex, extrusionFlowFragment,
} from './shaders.js';

const RELIEF_HEIGHT = 9.995;
const clamp01 = value => Math.max(0, Math.min(1, Number(value) || 0));
const DEFINES = {
  EFFECT_AMPLITUDE: '.57', EFFECT_SHADOW_STRENGTH: '.3', EFFECT_FLUID_MAGNITUDE: '.15',
  EFFECT_FLUID_RED_COEF: '2.0', EFFECT_FLUID_GREEN_COEF: '1.0', EFFECT_FLUID_BLUE_COEF: '1.5',
  EFFECT_LINES_SPEED: '2.0', EFFECT_LINES_SCALE: '4.0', EFFECT_LINES_STRENGTH: '0.0',
  EFFECT_LINES_WAVE_LENGTH: '.15', EFFECT_BASE_COLOR: 'vec3(.478431,.749020,.772549)',
  EFFECT_BASE_THRESHOLD: '1.0', EFFECT_HUE_SHIFT: '-.52', EFFECT_COLOR_RANGE: '2.0',
  CHROMATIC_FRESNEL_SHARPNESS: '35.0', CHROMATIC_FRESNEL_OPACITY: '.98',
  CHROMATIC_SHADOW_RANGE: 'vec2(.2,.42)', CHROMATIC_SHADOW_OPACITY: '.25',
  SCROLL_EXTRUDE_NOISE_SIZE: '7.77', SCROLL_EXTRUDE_SPEED: '2.0',
  SCROLL_EXTRUDE_MASK: 'vec2(-1.0,1.0)', SCROLL_EXTRUDE_STRENGTH: '1.02',
};

function seededRandom(seed) {
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

function idlePointer(seed, mouse) {
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

function createExtrusion(renderer, maskNoise, time, type) {
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
    uniform, mouse, velocity, mouse2, reset,
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

/** A self-contained reference relief. All scroll values are positive CSS pixels. */
export async function createRelief({ canvas, assetBase = './assets/', quality = 'low', reducedMotion = false, randomSeed = 42 } = {}) {
  if (!(canvas instanceof HTMLCanvasElement)) throw new TypeError('createRelief requires a canvas.');
  if (!['low', 'high'].includes(quality)) throw new TypeError('quality must be low or high.');
  const base = new URL(assetBase.endsWith('/') ? assetBase : `${assetBase}/`, document.baseURI);
  const asset = name => new URL(name, base).href;
  const mobile = /Android|iPhone|iPod/i.test(navigator.userAgent);
  const touchDevice = mobile || /iPad/i.test(navigator.userAgent) || (navigator.platform === 'MacIntel' && navigator.maxTouchPoints > 1);
  const stats = {
    ready: false, disposed: false, contextLost: false, paused: document.hidden, quality,
    dpr: quality === 'low' ? 1 : Math.min(2, window.devicePixelRatio || 1),
    reducedMotion, fluidEnabled: !touchDevice && !reducedMotion,
    meshCount: 0, vertices: 0, triangles: 0, frames: 0, time: 0, errors: [],
  };
  const renderer = new WebGLRenderer({ canvas, antialias: false, premultipliedAlpha: false, powerPreference: 'high-performance' });
  renderer.outputEncoding = LinearEncoding; renderer.toneMapping = LinearToneMapping;
  renderer.setClearColor(0xffffff, 1); renderer.setPixelRatio(1);
  renderer.debug.onShaderError = (gl, program, vertex, fragment) => {
    const message = [gl.getProgramInfoLog(program), gl.getShaderInfoLog(vertex), gl.getShaderInfoLog(fragment)].filter(Boolean).join('\n');
    stats.errors.push(message); console.error('Relief shader compile failed:', message);
  };
  const hasFloat = renderer.capabilities.isWebGL2
    ? renderer.extensions.has('EXT_color_buffer_float')
    : renderer.extensions.has('WEBGL_color_buffer_float');
  const hasHalf = hasFloat || renderer.extensions.has('EXT_color_buffer_half_float');
  if (!hasHalf) { renderer.dispose(); throw new Error('Floating point WebGL render targets are unavailable.'); }
  const floatType = /iPad|iPhone|iPod/i.test(navigator.userAgent) || !hasFloat ? HalfFloatType : FloatType;
  const draco = new DRACOLoader().setDecoderPath(asset('draco/')).setWorkerLimit(2);
  const loader = new GLTFLoader().setDRACOLoader(draco), textureLoader = new TextureLoader();
  const loaded = await Promise.allSettled([
    loader.loadAsync(asset(`reliefs_${quality}_compressed.glb`)),
    textureLoader.loadAsync(asset('plaster.jpg')),
    textureLoader.loadAsync(asset('mask-noise.png')),
    textureLoader.loadAsync(asset('rgb-attenuation-0,9.png')),
  ]);
  draco.dispose();
  const failed = loaded.find(item => item.status === 'rejected');
  if (failed) {
    for (const item of loaded) if (item.status === 'fulfilled') {
      if (item.value.isTexture) item.value.dispose();
      else item.value.scene.traverse(node => { node.geometry?.dispose(); node.material?.map?.dispose(); node.material?.emissiveMap?.dispose(); node.material?.dispose(); });
    }
    renderer.dispose(); throw failed.reason;
  }
  const [model, plaster, maskNoise, fastNoise] = loaded.map(item => item.value);
  plaster.wrapS = plaster.wrapT = maskNoise.wrapS = maskNoise.wrapT = RepeatWrapping;
  fastNoise.wrapS = fastNoise.wrapT = MirroredRepeatWrapping;
  const textureSet = new Set([plaster, maskNoise, fastNoise]);
  const scene = new Scene(), camera = new PerspectiveCamera(50, 1, 5, 20); camera.position.z = 15;
  const emptyTexture = new DataTexture(new Float32Array([0, 0, 0, 0]), 1, 1, RGBAFormat, FloatType);
  emptyTexture.needsUpdate = true; textureSet.add(emptyTexture);
  const staticTexture = new DataTexture(new Float32Array([0, 0, .25, .25]), 1, 1, RGBAFormat, FloatType);
  staticTexture.needsUpdate = true; textureSet.add(staticTexture);
  const uniforms = {
    uResolution: { value: new Vector2() }, uAspect: { value: 1 }, uDPR: { value: stats.dpr },
    uTime: { value: 0 }, uScroll: { value: 0 }, uScreenScroll: { value: 0 }, uScrollSpeed: { value: 0 },
    uOpacity: { value: 1 }, uSwitchColorTransition: { value: 0 }, uTransition: { value: 0 },
    uTextureStrength: { value: 1 }, uGradientStrength: { value: .17 }, uFastScroll: { value: 0 },
    uSwitchColorFastScroll: { value: 0 }, tMaskNoise: { value: fastNoise }, tPlaster: { value: plaster },
    uBrightnessFactor: { value: mobile ? .5 : .6 }, uBrightnessOffset: { value: mobile ? .6 : .4 },
  };
  const flow = createExtrusion(renderer, maskNoise, uniforms.uTime, floatType);
  const fluid = stats.fluidEnabled ? createFluid(renderer) : null;
  uniforms.tFlow = reducedMotion ? { value: staticTexture } : flow.uniform;
  uniforms.tFluidFlowmap = fluid?.uniform || { value: emptyTexture };
  const backgroundGeometry = fullscreenTriangle();
  const backgroundMaterial = new RawShaderMaterial({
    vertexShader: fullscreenVertex, fragmentShader: plasterFragment,
    uniforms: { uGradientStrength: uniforms.uGradientStrength, tPlaster: uniforms.tPlaster, uTextureStrength: uniforms.uTextureStrength },
    depthTest: false, depthWrite: false,
  });
  const background = new Mesh(backgroundGeometry, backgroundMaterial); background.frustumCulled = false; background.renderOrder = -1; scene.add(background);
  const meshes = [], rows = new Map(), rowOrder = [];
  for (const source of model.scene.children) {
    if (!source.geometry) continue;
    const sourceMaterial = source.material;
    textureSet.add(sourceMaterial.map); textureSet.add(sourceMaterial.emissiveMap);
    const material = new ShaderMaterial({
      vertexShader: reliefVertex, fragmentShader: reliefFragment, defines: { ...DEFINES },
      extensions: { derivatives: true },
      uniforms: { ...uniforms, tBake1: { value: sourceMaterial.map }, tBake2: { value: sourceMaterial.emissiveMap } },
    });
    const mesh = new Mesh(source.geometry, material); mesh.name = source.name;
    mesh.position.copy(source.position); mesh.scale.copy(source.scale);
    const row = Math.round(source.position.y); rows.set(row, (rows.get(row) || 0) + 1);
    if (!rowOrder.includes(row)) rowOrder.push(row);
    mesh.renderOrder = rowOrder.indexOf(row); scene.add(mesh); meshes.push(mesh);
    stats.vertices += source.geometry.attributes.position.count;
    stats.triangles += (source.geometry.index?.count || source.geometry.attributes.position.count) / 3;
    sourceMaterial.dispose();
  }
  stats.meshCount = meshes.length;
  const period = meshes.length / Math.max(...rows.values()) * RELIEF_HEIGHT;
  const updateIdle = idlePointer(randomSeed, flow.mouse2);
  const pointer = new Vector2(-1, -1), lastPointer = new Vector2(-1, -1), pointerVelocity = new Vector2();
  let pixelPointer = null, width = 1, height = 1, viewportHeight = 1;
  let scroll = 0, lastScreenScroll = 0, disposed = false, contextLost = false, raf = 0, lastTime = 0;

  function projection() {
    const aspect = width / height, extent = 1.33 * (RELIEF_HEIGHT - .1) / aspect;
    camera.aspect = aspect; camera.fov = Math.min(30, 2 * Math.atan(extent / 30) * 180 / Math.PI);
    camera.zoom = 1 - .4 * uniforms.uFastScroll.value; camera.updateProjectionMatrix();
    stats.cameraFov = camera.fov; stats.cameraZoom = camera.zoom;
  }
  function requestFrame() {
    if (!raf && !disposed && !contextLost && !document.hidden) raf = requestAnimationFrame(renderFrame);
  }
  function resize(w, h) {
    if (disposed) return;
    width = Math.max(1, Number(w) || canvas.clientWidth || window.innerWidth);
    height = Math.max(1, Number(h) || canvas.clientHeight || window.innerHeight);
    viewportHeight = 2 * Math.tan(camera.fov * Math.PI / 360) * camera.position.z;
    renderer.setSize(Math.round(width * stats.dpr), Math.round(height * stats.dpr), false);
    uniforms.uResolution.value.set(width * stats.dpr, height * stats.dpr);
    uniforms.uAspect.value = width / height; flow.setAspect(width / height); fluid?.setAspect(width / height);
    projection(); requestFrame();
  }
  function handlePointer(event) {
    if (disposed || reducedMotion || contextLost || document.hidden) return;
    const samples = event.getCoalescedEvents?.();
    const events = samples?.length ? samples : [event];
    for (const sample of events) {
      const x = sample.clientX, y = sample.clientY;
      if (!Number.isFinite(x) || !Number.isFinite(y)) continue;
      const rect = canvas.getBoundingClientRect(), px = x - rect.left, py = y - rect.top;
      pointer.set(px / width, 1 - py / height);
      if (pixelPointer && fluid) {
        const dx = Math.max(-20, Math.min(20, px - pixelPointer.x)) * 5;
        const dy = -Math.max(-20, Math.min(20, py - pixelPointer.y)) * 5;
        if (dx || dy) fluid.addPointer(pointer.x, pointer.y, dx, dy);
      }
      pixelPointer = { x: px, y: py };
    }
  }
  function leavePointer(event) {
    if (event?.type === 'pointerout' && event.relatedTarget) return;
    pointer.set(-1, -1); lastPointer.copy(pointer); pointerVelocity.set(0, 0); pixelPointer = null;
  }
  function renderFrame(now) {
    raf = 0;
    if (disposed || contextLost || document.hidden) return;
    const delta = reducedMotion ? 0 : lastTime ? Math.min((now - lastTime) / 1000, .05) : 1 / 60;
    lastTime = now; uniforms.uTime.value += delta;
    uniforms.uScroll.value = -scroll / (height * stats.dpr) * .25;
    scene.position.y = -uniforms.uScroll.value * RELIEF_HEIGHT;
    uniforms.uScreenScroll.value = scene.position.y * .6 / viewportHeight;
    for (const mesh of meshes) {
      const worldY = mesh.position.y + scene.position.y;
      if (worldY < -period / 2 || worldY > period / 2) mesh.position.y -= Math.floor((worldY + period / 2) / period) * period;
    }
    const rawDelta = uniforms.uScreenScroll.value - lastScreenScroll;
    const scrollDelta = Math.min(.2, Math.abs(rawDelta)) * Math.sign(rawDelta); lastScreenScroll = uniforms.uScreenScroll.value;
    uniforms.uScrollSpeed.value += (scrollDelta * 5 - uniforms.uScrollSpeed.value) * .04;
    projection();
    if (!reducedMotion) {
      const dtMult = Math.min(delta * 1000, 32) / 16;
      if (lastPointer.x === -1) lastPointer.copy(pointer);
      pointerVelocity.copy(pointer).sub(lastPointer).multiplyScalar(dtMult); lastPointer.copy(pointer);
      flow.mouse.lerp(pointer, .4); flow.velocity.lerp(pointerVelocity, pointerVelocity.length() ? .1 : .04);
      updateIdle(delta); flow.update(-scrollDelta, dtMult); fluid?.update();
    }
    renderer.setRenderTarget(null); renderer.render(scene, camera);
    stats.frames++; stats.time = uniforms.uTime.value; stats.scroll = scroll;
    stats.visibleTriangles = renderer.info.render.triangles; stats.calls = renderer.info.render.calls;
    stats.paused = false;
    if (!reducedMotion) requestFrame();
  }
  function visibility() {
    stats.paused = document.hidden;
    if (document.hidden) { cancelAnimationFrame(raf); raf = 0; leavePointer(); }
    else { lastTime = 0; requestFrame(); }
  }
  function onContextLost(event) {
    event.preventDefault(); contextLost = true; stats.contextLost = true; stats.paused = true;
    cancelAnimationFrame(raf); raf = 0;
  }
  function onContextRestored() {
    if (disposed) return;
    contextLost = false; stats.contextLost = false; lastTime = 0;
    flow.reset(); fluid?.reset(); resize(width, height); requestFrame();
  }
  function dispose() {
    if (disposed) return;
    disposed = true; stats.disposed = true; stats.ready = false; stats.paused = true;
    cancelAnimationFrame(raf); raf = 0;
    window.removeEventListener('pointermove', handlePointer); window.removeEventListener('pointerdown', handlePointer);
    window.removeEventListener('pointerout', leavePointer); window.removeEventListener('blur', leavePointer);
    document.removeEventListener('visibilitychange', visibility);
    canvas.removeEventListener('webglcontextlost', onContextLost); canvas.removeEventListener('webglcontextrestored', onContextRestored);
    flow.dispose(); fluid?.dispose();
    for (const mesh of meshes) { mesh.geometry.dispose(); mesh.material.dispose(); }
    backgroundGeometry.dispose(); backgroundMaterial.dispose();
    for (const texture of textureSet) if (texture) { texture.dispose(); texture.source?.data?.close?.(); }
    renderer.dispose();
  }
  window.addEventListener('pointermove', handlePointer, { passive: true }); window.addEventListener('pointerdown', handlePointer, { passive: true });
  window.addEventListener('pointerout', leavePointer, { passive: true }); window.addEventListener('blur', leavePointer);
  document.addEventListener('visibilitychange', visibility);
  canvas.addEventListener('webglcontextlost', onContextLost); canvas.addEventListener('webglcontextrestored', onContextRestored);
  resize(canvas.clientWidth || window.innerWidth, canvas.clientHeight || window.innerHeight);
  renderer.compile(scene, camera);
  if (stats.errors.length) { dispose(); throw new Error(stats.errors.join('\n')); }
  stats.ready = true;
  return {
    setScroll(value) { if (!disposed) { scroll = Math.max(0, Number(value) || 0); requestFrame(); } },
    setFast(value) { if (!disposed) { uniforms.uFastScroll.value = clamp01(value); requestFrame(); } },
    setOpacity(value) { if (!disposed) { uniforms.uOpacity.value = clamp01(value); requestFrame(); } },
    setDark(value) { if (!disposed) { uniforms.uSwitchColorTransition.value = clamp01(value); requestFrame(); } },
    resize, dispose, stats,
  };
}
