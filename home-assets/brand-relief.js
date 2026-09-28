import {
  WebGLRenderer, PerspectiveCamera, Scene, Mesh, ShaderMaterial, RawShaderMaterial,
  PlaneGeometry, Vector2, DataTexture, RGBAFormat, UnsignedByteType, FloatType,
  HalfFloatType, RepeatWrapping, LinearFilter, LinearToneMapping, LinearEncoding,
} from 'three';
import { fullscreenTriangle, createFluid } from './brand-fluid.js';
import { createExtrusion, seededRandom, idlePointer } from './brand-flow.js';
import { fullscreenVertex, surfaceVertex, surfaceFragment, backgroundFragment } from './brand-shaders.js';

const TILE_WIDTH = 13.25, TILE_HEIGHT = 9.995, PERIOD = TILE_HEIGHT * 6;
const clamp = (value, min = 0, max = 1) => Math.max(min, Math.min(max, value));
const nextFrame = () => new Promise(resolve => requestAnimationFrame(resolve));
const SCENE_COUNT = 6;

function hash(x, y, seed) {
  let n = Math.imul(x + seed, 374761393) ^ Math.imul(y, 668265263);
  n = Math.imul(n ^ n >>> 13, 1274126177);
  return ((n ^ n >>> 16) >>> 0) / 4294967295;
}
function noise(x, y, period, seed) {
  const ix = Math.floor(x), iy = Math.floor(y), fx = x - ix, fy = y - iy;
  const u = fx * fx * (3 - 2 * fx), v = fy * fy * (3 - 2 * fy);
  const wrap = n => (n % period + period) % period;
  const a = hash(wrap(ix), wrap(iy), seed), b = hash(wrap(ix + 1), wrap(iy), seed);
  const c = hash(wrap(ix), wrap(iy + 1), seed), d = hash(wrap(ix + 1), wrap(iy + 1), seed);
  return a + (b - a) * u + (c - a) * v + (a - b - c + d) * u * v;
}
function rgbaTexture(data, w, h, repeat = false) {
  const texture = new DataTexture(data, w, h, RGBAFormat, UnsignedByteType);
  texture.minFilter = texture.magFilter = LinearFilter;
  texture.generateMipmaps = false;
  if (repeat) texture.wrapS = texture.wrapT = RepeatWrapping;
  texture.needsUpdate = true;
  return texture;
}
function proceduralTexture(size, seed, plaster) {
  const data = new Uint8Array(size * size * 4);
  const frequencies = plaster ? [3, 11, 34, 100, 240] : [3, 9, 24];
  const weights = plaster ? [.36, .28, .19, .1, .07] : [.5, .3, .2];
  for (let y = 0; y < size; y++) for (let x = 0; x < size; x++) {
    const i = (y * size + x) * 4;
    for (let c = 0; c < (plaster ? 1 : 3); c++) {
      let value = 0;
      for (let k = 0; k < frequencies.length; k++) value += noise(x / size * frequencies[k], y / size * frequencies[k], frequencies[k], seed + c * 491 + k * 13) * weights[k];
      data[i + c] = Math.round(clamp(plaster ? .917 + (value - .5) * .22 + (hash(x, y, seed) - .5) * .035 : .24 + value * .76) * 255);
    }
    if (plaster) data[i + 1] = data[i + 2] = data[i];
    data[i + 3] = 255;
  }
  return rgbaTexture(data, size, size, true);
}

function makeField(nx, ny) {
  const w = nx + 1, h = ny + 1, values = new Float32Array(w * h);
  const dx = TILE_WIDTH / nx, dy = TILE_HEIGHT / ny;
  function stamp(cx, cy, radius, fn) {
    const x0 = clamp(Math.floor((cx - radius + TILE_WIDTH / 2) / dx), 0, nx), x1 = clamp(Math.ceil((cx + radius + TILE_WIDTH / 2) / dx), 0, nx);
    const y0 = clamp(Math.floor((cy - radius + TILE_HEIGHT / 2) / dy), 0, ny), y1 = clamp(Math.ceil((cy + radius + TILE_HEIGHT / 2) / dy), 0, ny);
    for (let iy = y0; iy <= y1; iy++) for (let ix = x0; ix <= x1; ix++) {
      const x = ix * dx - TILE_WIDTH / 2, y = iy * dy - TILE_HEIGHT / 2;
      const z = fn(x - cx, y - cy);
      if (z > 0) values[iy * w + ix] = Math.max(values[iy * w + ix], z);
    }
  }
  function lobe(x, y, angle, length, width, height, bend = 0, leaf = false, phase = 0) {
    const ca = Math.cos(angle), sa = Math.sin(angle);
    stamp(x, y, length + width, (px, py) => {
      const along = (px * ca + py * sa) / length;
      if (along <= 0 || along >= 1) return 0;
      const center = bend * Math.sin(Math.PI * along);
      const halfWidth = width * Math.pow(Math.sin(Math.PI * along), leaf ? .82 : .56) * (1 + .1 * Math.sin(along * 7 + phase));
      const across = (-px * sa + py * ca - center) / Math.max(.001, halfWidth);
      if (Math.abs(across) >= 1) return 0;
      const envelope = Math.pow(1 - across * across, leaf ? 1.1 : .72) * Math.pow(Math.sin(Math.PI * along), .64);
      if (leaf) {
        const midrib = .2 * Math.exp(-across * across * 48);
        const ribs = .055 * Math.pow(Math.max(0, Math.cos((along * 7 - Math.abs(across) * .58) * Math.PI * 2)), 12);
        return height * envelope * (.65 + midrib + ribs) * (1 - .16 * along);
      }
      const cup = .53 + .48 * along + .28 * across * across - .1 * Math.exp(-across * across * 35);
      const folds = .055 * Math.sin(across * 15 + along * 8 + phase) * Math.sin(Math.PI * along);
      return height * envelope * Math.max(.1, cup + folds);
    });
  }
  function branch(points, radius = .045, height = .07) {
    for (let i = 0; i < points.length - 1; i++) {
      const a = points[i], b = points[i + 1], vx = b[0] - a[0], vy = b[1] - a[1], length2 = vx * vx + vy * vy;
      stamp((a[0] + b[0]) / 2, (a[1] + b[1]) / 2, Math.sqrt(length2) / 2 + radius, (px, py) => {
        const x = px + (a[0] + b[0]) / 2, y = py + (a[1] + b[1]) / 2;
        const t = clamp(((x - a[0]) * vx + (y - a[1]) * vy) / Math.max(.0001, length2));
        const distance = Math.hypot(x - a[0] - t * vx, y - a[1] - t * vy) / radius;
        return distance < 1 ? height * (1 - distance * distance) ** .7 : 0;
      });
    }
  }
  function curve(a, control, b, count = 18) {
    const points = [];
    for (let i = 0; i <= count; i++) { const t = i / count, u = 1 - t; points.push([u * u * a[0] + 2 * u * t * control[0] + t * t * b[0], u * u * a[1] + 2 * u * t * control[1] + t * t * b[1]]); }
    return points;
  }
  function flower(cx, cy, scale, rotation, seed, layers = 2) {
    const random = seededRandom(seed), petalCount = 9;
    for (let layer = 0; layer < layers; layer++) for (let p = 0; p < petalCount - layer * 2; p++) {
      const angle = rotation + p / (petalCount - layer * 2) * Math.PI * 2 + layer * .36 + (random() - .5) * .16;
      const length = scale * (layer ? .92 : 1.38) * (.92 + random() * .16);
      lobe(cx + Math.cos(angle) * .055 * scale, cy + Math.sin(angle) * .055 * scale, angle, length, scale * (layer ? .35 : .44), scale * (layer ? .63 : .45), (random() - .5) * .12 * scale, false, random() * 5);
    }
    stamp(cx, cy, .26 * scale, (x, y) => { const r = Math.hypot(x, y) / (.25 * scale); return r < 1 ? .3 * scale * (1 - r * r) * (1 + .12 * Math.sin(x * 80) * Math.sin(y * 70)) : 0; });
  }
  function willow(a, control, b, side, seed) {
    const random = seededRandom(seed), points = curve(a, control, b);
    branch(points, .047, .07);
    for (let i = 2; i < points.length - 2; i += 2) {
      const [x, y] = points[i], flip = (i / 2 % 2 ? 1 : -1) * side;
      const angle = -Math.PI / 2 + flip * (.68 + random() * .35);
      lobe(x, y, angle, 1.1 + random() * .55, .13 + random() * .055, .24 + random() * .05, flip * .07, true, random() * 4);
    }
  }
  function finish() {
    const smoothed = new Float32Array(values.length);
    for (let y = 1; y < ny; y++) for (let x = 1; x < nx; x++) {
      const i = y * w + x;
      smoothed[i] = (values[i] * 4 + values[i - 1] + values[i + 1] + values[i - w] + values[i + w]) / 8;
      const edge = Math.min(x / 5, (nx - x) / 5, y / 7, (ny - y) / 7, 1);
      smoothed[i] *= edge * edge * (3 - 2 * edge);
    }
    return { data: smoothed, nx, ny, w, h, dx, dy };
  }
  return { lobe, branch, curve, flower, willow, stamp, finish };
}

function botanicalScene(index, nx, ny, seed) {
  const f = makeField(nx, ny);
  const ripples = (cx, cy, sx, sy, phase) => f.stamp(cx, cy, Math.max(sx, sy) * 1.2, (x, y) => {
    const angle = Math.atan2(y / sy, x / sx), r = Math.hypot(x / sx, y / sy);
    if (r > 1.15 || r < .08) return 0;
    const wave = Math.max(0, Math.sin((r * 6 + Math.sin(angle * 3 + phase) * .06) * Math.PI * 2));
    return .095 * wave ** 6 * Math.sin(Math.min(1, r / 1.15) * Math.PI) ** .6;
  });
  if (index === 0) {
    f.flower(3.8, 2.1, 1.04, .2, seed + 31);
    f.flower(-4.25, -2.1, .77, -.7, seed + 97);
    f.branch(f.curve([-5.8, -4.4], [-3.8, -2.8], [-3.8, -.6]), .06, .08);
    f.lobe(-4.6, -3.5, .7, 1.55, .38, .31, -.14, true);
    f.lobe(4.1, 1.5, -1.42, 1.6, .32, .32, .12, true);
    f.lobe(4.3, 1.6, -.2, 1.3, .3, .28, .09, true);
  } else if (index === 1) {
    f.willow([5.5, 4.7], [3.7, 1.5], [4.6, -3.9], 1, seed + 8);
    f.willow([-5.8, 4.6], [-3.9, 3.1], [-4.5, -.9], -1, seed + 25);
  } else if (index === 2) {
    for (let layer = 0; layer < 2; layer++) for (let p = 0; p < 7; p++) {
      const angle = Math.PI * (.08 + p / 6 * .84);
      f.lobe(-4.1 + (layer ? 0 : .1), -2.6, angle, (layer ? 1.05 : 1.7), layer ? .36 : .43, layer ? .57 : .41, (p - 3) * .04, false, p * .4);
    }
    f.lobe(-4.1, -2.7, -.22, 2.3, .5, .21, .14, true);
    ripples(-4, -2.5, 2.3, .95, 1);
    f.willow([5.4, 4.8], [4.1, 3.4], [4.8, .2], 1, seed + 35);
  } else if (index === 3) {
    ripples(4.1, 2.3, 2.05, 1.28, 2.2);
    ripples(-4.7, -2.5, 1.8, .88, .5);
    f.lobe(4.3, 2.4, 2.1, 1.5, .4, .22, .15, true);
    f.branch(f.curve([-6.1, 3.3], [-4.9, 1.4], [-4.5, -.4]), .047, .06);
    for (let i = 0; i < 5; i++) f.lobe(-5.4 + i * .17, 2.2 - i * .52, -.8 - (i % 2) * .7, 1.25, .15, .23, .12, true, i);
  } else if (index === 4) {
    f.willow([-5.7, 4.6], [-3.4, 3.5], [-4.1, -.7], -1, seed + 41);
    f.branch(f.curve([5.9, -4.5], [2.6, -3.8], [4.3, -.8]), .06, .09);
    for (let i = 0; i < 6; i++) f.lobe(4.6 - i * .15, -3.7 + i * .42, i % 2 ? .46 : 2.22, 1.3, .23, .3, .12, true, i * .6);
    f.flower(4.35, -1.15, .57, -.3, seed + 62, 1);
  } else {
    f.flower(-4.35, 2.05, .91, 1.1, seed + 52);
    f.flower(4.45, -2.1, .73, -.1, seed + 13, 1);
    f.branch(f.curve([-5.2, -1.1], [-4.8, 1.9], [-3.5, 3.8]), .05, .08);
    f.lobe(-4.7, .75, -1.9, 1.6, .29, .28, -.11, true);
    f.lobe(4.35, -2.4, -2.5, 1.55, .32, .25, -.1, true);
  }
  return f.finish();
}

async function buildSurface(field, subdivisionsX, subdivisionsY) {
  const { data, nx, ny, w, h, dx, dy } = field;
  const geometry = new PlaneGeometry(TILE_WIDTH, TILE_HEIGHT, subdivisionsX, subdivisionsY), vertices = geometry.attributes.position;
  const scale = nx / subdivisionsX;
  for (let row = 0; row <= subdivisionsY; row++) for (let col = 0; col <= subdivisionsX; col++) vertices.setZ(row * (subdivisionsX + 1) + col, data[(ny - row * scale) * w + col * scale]);
  geometry.computeVertexNormals(); geometry.computeBoundingBox(); geometry.computeBoundingSphere();
  const high = new Uint8Array(w * h * 4), low = new Uint8Array(w * h * 4);
  const get = (x, y) => data[clamp(y, 0, ny) * w + clamp(x, 0, nx)];
  const light = [-.47, .57, .674];
  const slope = Math.hypot(...light); light.forEach((_, i) => light[i] /= slope);
  const neighborSteps = [[2, 0], [-2, 0], [0, 2], [0, -2], [6, 6], [-6, 6], [6, -6], [-6, -6], [12, 0], [-12, 0], [0, 12], [0, -12]];
  for (let y = 0; y < h; y++) {
    if (y % 96 === 0) await nextFrame();
    for (let x = 0; x < w; x++) {
    const i = y * w + x, height = data[i], gx = (get(x + 1, y) - get(x - 1, y)) / (2 * dx), gy = (get(x, y + 1) - get(x, y - 1)) / (2 * dy);
    let concavity = 0, horizon = 0;
    for (const [ox, oy] of neighborSteps) concavity += Math.max(0, get(x + ox, y + oy) - height) / (Math.hypot(ox * dx, oy * dy) + .08);
    concavity /= neighborSteps.length;
    for (let k = 1; k <= 8; k++) horizon = Math.max(horizon, (get(x - k * 2, y + k * 2) - height) / (k * 2 * Math.hypot(dx, dy)));
    const levels = [];
    for (let level = 0; level < 6; level++) {
      const e = level / 5, length = Math.sqrt(1 + gx * gx * e * e + gy * gy * e * e);
      const lambert = Math.max(0, (-gx * e * light[0] - gy * e * light[1] + light[2]) / length);
      const shadow = clamp((horizon * e - .38) / .65);
      const shade = .54504 + (lambert - light[2]) * .63 - concavity * e * .25 - shadow * .13;
      levels.push(Math.round(clamp(shade, .06, .93) * 255));
    }
    const offset = i * 4;
    high.set([levels[5], levels[4], levels[3], 255], offset); low.set([levels[2], levels[1], levels[0], 255], offset);
    }
  }
  return { geometry, high: rgbaTexture(high, w, h), low: rgbaTexture(low, w, h), maxHeight: geometry.boundingBox.max.z, bytes: geometry.attributes.position.array.byteLength + geometry.attributes.normal.array.byteLength + geometry.attributes.uv.array.byteLength + geometry.index.array.byteLength + high.byteLength + low.byteLength };
}

function canvasFallback(canvas, stats) {
  const context = canvas.getContext('2d'); let dark = 0, disposed = false;
  stats.mode = 'canvas-static'; stats.ready = true; stats.fluidEnabled = false;
  const draw = () => { if (!context || disposed) return; context.fillStyle = dark ? '#202220' : '#c9cac7'; context.fillRect(0, 0, canvas.width, canvas.height); };
  const resize = (w = innerWidth, h = innerHeight) => { canvas.width = Math.max(1, w); canvas.height = Math.max(1, h); draw(); };
  resize(canvas.clientWidth || innerWidth, canvas.clientHeight || innerHeight);
  return { setScroll() {}, setFast() {}, setOpacity() {}, setDark(value) { dark = !!value; draw(); }, resize, dispose() { disposed = true; stats.disposed = true; stats.ready = false; }, stats };
}

export async function createBrandRelief({ canvas, reducedMotion = false, randomSeed = 42, quality = 'auto' } = {}) {
  if (!(canvas instanceof HTMLCanvasElement)) throw new TypeError('A canvas is required.');
  if (!['auto', 'low', 'high'].includes(quality)) throw new TypeError('quality must be auto, low, or high.');
  const began = performance.now();
  const touch = matchMedia('(pointer:coarse)').matches || navigator.maxTouchPoints > 1;
  const lowPerformance = (navigator.hardwareConcurrency || 8) <= 4 || (navigator.deviceMemory || 8) <= 2;
  const selected = quality === 'auto' ? touch || lowPerformance ? 'low' : 'high' : quality;
  const stats = { ready: false, disposed: false, contextLost: false, paused: false, mode: 'webgl', quality: selected, reducedMotion, frames: 0, time: 0, errors: [], assetRequests: 0, geometryBytes: 0, source: 'Original parameterized botanical heightfields and periodic noise; zero image or model assets.' };
  let renderer;
  try {
    const options = { antialias: false, premultipliedAlpha: false, alpha: false, powerPreference: 'high-performance' };
    const context = canvas.getContext('webgl2', options) || canvas.getContext('webgl', options);
    if (!context) return canvasFallback(canvas, stats);
    renderer = new WebGLRenderer({ canvas, context, ...options });
  }
  catch { return canvasFallback(canvas, stats); }
  renderer.outputEncoding = LinearEncoding; renderer.toneMapping = LinearToneMapping; renderer.setPixelRatio(1); renderer.setClearColor(0xc9cac7, 1);
  renderer.debug.onShaderError = (gl, program, vertex, fragment) => { const error = [gl.getProgramInfoLog(program), gl.getShaderInfoLog(vertex), gl.getShaderInfoLog(fragment)].filter(Boolean).join('\n'); stats.errors.push(error); console.error(error); };
  const floatSupported = renderer.capabilities.isWebGL2 ? renderer.extensions.has('EXT_color_buffer_float') : renderer.extensions.has('WEBGL_color_buffer_float');
  const halfSupported = floatSupported || renderer.extensions.has('EXT_color_buffer_half_float');
  const staticMode = reducedMotion || lowPerformance || !halfSupported;
  stats.mode = staticMode ? 'webgl-static' : 'webgl'; stats.fluidEnabled = !touch && !staticMode;
  stats.dpr = selected === 'low' ? 1 : Math.min(1.5, devicePixelRatio || 1);
  const scene = new Scene(), camera = new PerspectiveCamera(50, 1, 5, 20); camera.position.z = 15;
  const plaster = proceduralTexture(512, randomSeed + 513, true), mask = proceduralTexture(128, randomSeed + 814, false);
  const blank = rgbaTexture(new Uint8Array([0, 0, 0, 255]), 1, 1), still = rgbaTexture(new Uint8Array([0, 0, 55, 55]), 1, 1);
  const uniforms = {
    uResolution: { value: new Vector2() }, uBrightness: { value: new Vector2(touch ? .5 : .6, touch ? .6 : .4) },
    uCompact: { value: 0 }, uTime: { value: 0 }, uFast: { value: 0 }, uOpacity: { value: 1 }, uDark: { value: 0 }, uScreenScroll: { value: 0 }, uSceneY: { value: 0 },
    tNoise: { value: mask }, tPlaster: { value: plaster }, uWorldSize: { value: new Vector2() },
  };
  const flow = !staticMode ? createExtrusion(renderer, mask, uniforms.uTime, floatSupported && !touch ? FloatType : HalfFloatType) : null;
  const fluid = stats.fluidEnabled ? createFluid(renderer) : null;
  uniforms.tFlow = flow?.uniform || { value: still }; uniforms.tFluid = fluid?.uniform || { value: blank };
  const backgroundGeometry = fullscreenTriangle();
  const backgroundMaterial = new RawShaderMaterial({ vertexShader: fullscreenVertex, fragmentShader: backgroundFragment, uniforms, depthTest: false, depthWrite: false });
  const background = new Mesh(backgroundGeometry, backgroundMaterial); background.renderOrder = -1; background.frustumCulled = false; scene.add(background);
  const surfaces = [], meshes = [];
  const geometryStart = performance.now();
  const nx = selected === 'low' ? 192 : 256, ny = selected === 'low' ? 144 : 192;
  for (let i = 0; i < SCENE_COUNT; i++) {
    const bakeScale = selected === 'low' ? 2 : 3;
    const surface = await buildSurface(botanicalScene(i, nx * bakeScale, ny * bakeScale, randomSeed + i * 151), nx, ny); surfaces.push(surface); stats.geometryBytes += surface.bytes;
    const material = new ShaderMaterial({ vertexShader: surfaceVertex, fragmentShader: surfaceFragment, uniforms: { ...uniforms, tBakeHigh: { value: surface.high }, tBakeLow: { value: surface.low }, uBakeTexel: { value: new Vector2(1 / surface.high.image.width, 1 / surface.high.image.height) } } });
    surface.material = material;
    for (const col of [-1, 0, 1]) { const mesh = new Mesh(surface.geometry, material); mesh.position.set(col * TILE_WIDTH, -i * TILE_HEIGHT, 0); mesh.userData.baseY = mesh.position.y; mesh.userData.column = col; scene.add(mesh); meshes.push(mesh); }
    await nextFrame();
  }
  stats.geometryMs = performance.now() - geometryStart; stats.sceneCount = surfaces.length;
  stats.meshCount = meshes.length; stats.triangles = nx * ny * 2 * meshes.length;
  const pointer = new Vector2(-1, -1), lastPointer = new Vector2(-1, -1), velocity = new Vector2();
  const idle = flow ? idlePointer(randomSeed, flow.mouse2) : null;
  if (flow && touch) flow.velocity2.set(.35, .35);
  let width = 1, height = 1, viewportHeight = 1, scroll = 0, previousScreenScroll = 0, raf = 0, lastTime = 0, disposed = false, lost = false, pixelPointer = null;
  function projection() {
    const aspect = width / height;
    camera.aspect = aspect; camera.fov = Math.min(30, Math.atan(1.33 * (TILE_HEIGHT - .1) / aspect / 30) * 360 / Math.PI);
    camera.zoom = 1 - .4 * uniforms.uFast.value; camera.updateProjectionMatrix();
    const h = 2 * Math.tan(camera.fov * Math.PI / 360) * 15 / camera.zoom;
    uniforms.uWorldSize.value.set(h * aspect, h); stats.cameraZoom = camera.zoom;
  }
  function schedule() { if (!raf && !disposed && !lost && !document.hidden) raf = requestAnimationFrame(render); }
  function resize(w, h) {
    if (disposed) return;
    width = Math.max(1, Number(w) || canvas.clientWidth || innerWidth); height = Math.max(1, Number(h) || canvas.clientHeight || innerHeight);
    viewportHeight = 2 * Math.tan(camera.fov * Math.PI / 360) * 15;
    renderer.setSize(Math.round(width * stats.dpr), Math.round(height * stats.dpr), false);
    uniforms.uResolution.value.set(width * stats.dpr, height * stats.dpr); uniforms.uCompact.value = 1 - clamp((width - 650) / 200); flow?.setAspect(width / height); fluid?.setAspect(width / height); projection(); schedule();
  }
  function onPointer(event) {
    if (touch || staticMode || lost || disposed || document.hidden) return;
    const samples = event.getCoalescedEvents?.();
    for (const p of samples?.length ? samples : [event]) {
      const rect = canvas.getBoundingClientRect(), x = p.clientX - rect.left, y = p.clientY - rect.top;
      pointer.set(x / width, 1 - y / height);
      if (pixelPointer && fluid) { const dx = clamp(x - pixelPointer.x, -20, 20) * 5, dy = -clamp(y - pixelPointer.y, -20, 20) * 5; if (dx || dy) fluid.addPointer(pointer.x, pointer.y, dx, dy); }
      pixelPointer = { x, y };
    }
  }
  function leave(event) { if (event?.type === 'pointerout' && event.relatedTarget) return; pointer.set(-1, -1); lastPointer.copy(pointer); pixelPointer = null; }
  function render(now) {
    raf = 0; if (disposed || lost || document.hidden) return;
    const start = performance.now(), delta = staticMode ? 0 : lastTime ? Math.min(.05, (now - lastTime) / 1000) : 1 / 60; lastTime = now;
    uniforms.uTime.value += delta; scene.position.y = scroll / (height * stats.dpr) * .25 * TILE_HEIGHT; uniforms.uSceneY.value = scene.position.y;
    uniforms.uScreenScroll.value = scene.position.y * .6 / viewportHeight;
    const difference = uniforms.uScreenScroll.value - previousScreenScroll, offset = clamp(difference, -.2, .2); previousScreenScroll = uniforms.uScreenScroll.value;
    projection();
    const cellWidth = TILE_WIDTH - uniforms.uCompact.value * 5.2;
    for (const mesh of meshes) {
      const world = mesh.userData.baseY + scene.position.y;
      mesh.position.y = mesh.userData.baseY - Math.floor((world + PERIOD / 2) / PERIOD) * PERIOD;
      mesh.position.x = mesh.userData.column * cellWidth;
      mesh.visible = Math.abs(mesh.position.x) < uniforms.uWorldSize.value.x / 2 + cellWidth / 2 + .08 && Math.abs(mesh.position.y + scene.position.y) < uniforms.uWorldSize.value.y / 2 + TILE_HEIGHT / 2 + .08;
    }
    if (flow) {
      const dtMult = Math.min(delta * 1000, 32) / 16;
      if (lastPointer.x === -1) lastPointer.copy(pointer);
      velocity.copy(pointer).sub(lastPointer).multiplyScalar(dtMult); lastPointer.copy(pointer);
      flow.mouse.lerp(pointer, .4); flow.velocity.lerp(velocity, velocity.length() ? .1 : .04);
      idle(delta); flow.update(-offset, dtMult); fluid?.update();
    }
    renderer.setRenderTarget(null); renderer.render(scene, camera);
    stats.frames++; stats.time = uniforms.uTime.value; stats.scroll = scroll; stats.paused = false;
    const cpu = performance.now() - start; stats.frameCpuMs = cpu; stats.averageFrameCpuMs = stats.averageFrameCpuMs ? stats.averageFrameCpuMs * .95 + cpu * .05 : cpu;
    stats.visibleTriangles = renderer.info.render.triangles;
    if (!staticMode) schedule();
  }
  function visibility() { stats.paused = document.hidden; if (document.hidden) { cancelAnimationFrame(raf); raf = 0; leave(); } else { lastTime = 0; schedule(); } }
  function releaseGPUResources() {
    flow?.dispose(); fluid?.dispose();
    for (const surface of surfaces) { surface.geometry.dispose(); surface.material.dispose(); surface.high.dispose(); surface.low.dispose(); }
    [plaster, mask, blank, still].forEach(texture => texture.dispose()); backgroundGeometry.dispose(); backgroundMaterial.dispose();
  }
  function contextLost(event) {
    event.preventDefault(); lost = true; stats.contextLost = true; stats.paused = true; cancelAnimationFrame(raf); raf = 0;
    // Release r151's old-context disposal listeners while GL deletions are no-ops.
    // Typed geometry/texture data stays intact and is reuploaded on restoration.
    releaseGPUResources();
  }
  function contextRestored() { if (disposed) return; lost = false; stats.contextLost = false; lastTime = 0; flow?.reset(); fluid?.reset(); resize(width, height); }
  function dispose() {
    if (disposed) return; disposed = true; stats.disposed = true; stats.ready = false; stats.paused = true; cancelAnimationFrame(raf);
    window.removeEventListener('pointermove', onPointer); window.removeEventListener('pointerout', leave); window.removeEventListener('blur', leave);
    document.removeEventListener('visibilitychange', visibility); canvas.removeEventListener('webglcontextlost', contextLost); canvas.removeEventListener('webglcontextrestored', contextRestored);
    releaseGPUResources(); renderer.dispose();
  }
  window.addEventListener('pointermove', onPointer, { passive: true }); window.addEventListener('pointerout', leave, { passive: true }); window.addEventListener('blur', leave);
  document.addEventListener('visibilitychange', visibility); canvas.addEventListener('webglcontextlost', contextLost); canvas.addEventListener('webglcontextrestored', contextRestored);
  resize(canvas.clientWidth || innerWidth, canvas.clientHeight || innerHeight);
  // Two peripheral stamps establish the botanical scene while leaving the title quiet.
  if (flow) {
    for (const point of [[.795, .74], [.17, .26]]) {
      flow.mouse2.set(...point);
      for (let i = 0; i < 12; i++) flow.update(0, 1);
    }
    flow.mouse2.set(-1, -1);
  }
  renderer.compile(scene, camera);
  if (stats.errors.length) { dispose(); throw new Error(stats.errors.join('\n')); }
  stats.ready = true; stats.initMs = performance.now() - began;
  return {
    setScroll(value) { if (!disposed) { scroll = Math.max(0, Number(value) || 0); schedule(); } },
    setFast(value) { if (!disposed) { uniforms.uFast.value = clamp(Number(value) || 0); schedule(); } },
    setOpacity(value) { if (!disposed) { uniforms.uOpacity.value = clamp(Number(value) || 0); schedule(); } },
    setDark(value) { if (!disposed) { uniforms.uDark.value = clamp(Number(value) || 0); schedule(); } },
    resize, dispose, stats,
  };
}
