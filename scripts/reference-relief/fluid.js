import {
  BufferGeometry, Float32BufferAttribute, WebGLRenderTarget, HalfFloatType,
  RGBAFormat, LinearFilter, NearestFilter, RawShaderMaterial, Mesh, Scene,
  Camera, Vector2, Vector3, Color,
} from 'three';
import {
  fluidVertex, fluidClear, fluidSplat, fluidAdvect, fluidDivergence, fluidCurl,
  fluidVorticity, fluidPressure, fluidGradientSubtract,
} from './shaders.js';

export function fullscreenTriangle() {
  const geometry = new BufferGeometry();
  geometry.setAttribute('position', new Float32BufferAttribute([-1, -1, 0, 3, -1, 0, -1, 3, 0], 3));
  geometry.setAttribute('uv', new Float32BufferAttribute([0, 0, 2, 0, 0, 2], 2));
  return geometry;
}

// Independent Navier–Stokes dye/velocity field; this is not the extrusion mask.
export function createFluid(renderer) {
  const simSize = 128, dyeSize = 512;
  const target = (size, filter = LinearFilter) => new WebGLRenderTarget(size, size, {
    type: HalfFloatType, format: RGBAFormat, minFilter: filter, magFilter: filter,
    depthBuffer: false, stencilBuffer: false,
  });
  const pair = (size, filter) => ({
    read: target(size, filter), write: target(size, filter),
    swap() { [this.read, this.write] = [this.write, this.read]; },
  });
  const dye = pair(dyeSize), velocity = pair(simSize), pressure = pair(simSize, NearestFilter);
  const divergence = target(simSize, NearestFilter), curl = target(simSize, NearestFilter);
  const targets = [dye.read, dye.write, velocity.read, velocity.write, pressure.read, pressure.write, divergence, curl];
  const texelSize = { value: new Vector2(1 / simSize, 1 / simSize) };
  const make = (fragmentShader, uniforms) => new RawShaderMaterial({
    vertexShader: fluidVertex, fragmentShader, uniforms: { texelSize, ...uniforms },
    depthTest: false, depthWrite: false,
  });
  const clear = make(fluidClear, { uTexture: { value: null }, value: { value: .925 } });
  const splat = make(fluidSplat, {
    uTarget: { value: null }, aspectRatio: { value: 1 }, color: { value: new Vector3() },
    point: { value: new Vector2() }, radius: { value: .007 },
  });
  const advect = make(fluidAdvect, {
    dyeTexelSize: { value: new Vector2(1 / dyeSize, 1 / dyeSize) },
    uVelocity: { value: null }, uSource: { value: null }, dt: { value: .016 }, dissipation: { value: 1 },
  });
  const div = make(fluidDivergence, { uVelocity: { value: null } });
  const curlPass = make(fluidCurl, { uVelocity: { value: null } });
  const vorticity = make(fluidVorticity, {
    uVelocity: { value: null }, uCurl: { value: null }, curl: { value: .1 }, dt: { value: .016 },
  });
  const jacobi = make(fluidPressure, { uPressure: { value: null }, uDivergence: { value: null } });
  const gradient = make(fluidGradientSubtract, { uPressure: { value: null }, uVelocity: { value: null } });
  const materials = [clear, splat, advect, div, curlPass, vorticity, jacobi, gradient];
  const geometry = fullscreenTriangle(), scene = new Scene(), camera = new Camera();
  const mesh = new Mesh(geometry, clear); mesh.frustumCulled = false; scene.add(mesh);
  const uniform = { value: dye.read.texture }, queue = [];
  let aspect = 1;
  function pass(material, destination) {
    mesh.material = material;
    renderer.setRenderTarget(destination);
    renderer.render(scene, camera);
  }
  function reset() {
    queue.length = 0;
    const priorTarget = renderer.getRenderTarget(), priorColor = renderer.getClearColor(new Color());
    const priorAlpha = renderer.getClearAlpha();
    renderer.setClearColor(0, 0);
    for (const item of targets) { renderer.setRenderTarget(item); renderer.clear(); }
    renderer.setRenderTarget(priorTarget); renderer.setClearColor(priorColor, priorAlpha);
    uniform.value = dye.read.texture;
  }
  function update() {
    const priorTarget = renderer.getRenderTarget(), priorAuto = renderer.autoClear;
    renderer.autoClear = false;
    try {
      // The reference consumes coalesced pointer samples from most recent to oldest.
      while (queue.length) {
        const { x, y, dx, dy } = queue.pop();
        const strength = Math.max(0, Math.min(2, (Math.hypot(dx, dy) - 5) / (78 - 5) * 2));
        if (!strength) continue;
        splat.uniforms.aspectRatio.value = aspect;
        splat.uniforms.point.value.set(x, y); splat.uniforms.color.value.set(dx, dy, 1);
        splat.uniforms.radius.value = .7 / 100 * strength;
        splat.uniforms.uTarget.value = velocity.read.texture; pass(splat, velocity.write); velocity.swap();
        splat.uniforms.uTarget.value = dye.read.texture; pass(splat, dye.write); dye.swap();
      }
      curlPass.uniforms.uVelocity.value = velocity.read.texture; pass(curlPass, curl);
      vorticity.uniforms.uVelocity.value = velocity.read.texture; vorticity.uniforms.uCurl.value = curl.texture;
      pass(vorticity, velocity.write); velocity.swap();
      div.uniforms.uVelocity.value = velocity.read.texture; pass(div, divergence);
      clear.uniforms.uTexture.value = pressure.read.texture; pass(clear, pressure.write); pressure.swap();
      jacobi.uniforms.uDivergence.value = divergence.texture;
      for (let i = 0; i < 3; i++) {
        jacobi.uniforms.uPressure.value = pressure.read.texture; pass(jacobi, pressure.write); pressure.swap();
      }
      gradient.uniforms.uPressure.value = pressure.read.texture; gradient.uniforms.uVelocity.value = velocity.read.texture;
      pass(gradient, velocity.write); velocity.swap();
      advect.uniforms.dyeTexelSize.value.set(1 / simSize, 1 / simSize);
      advect.uniforms.uVelocity.value = velocity.read.texture; advect.uniforms.uSource.value = velocity.read.texture;
      advect.uniforms.dissipation.value = .8891; pass(advect, velocity.write); velocity.swap();
      advect.uniforms.dyeTexelSize.value.set(1 / dyeSize, 1 / dyeSize);
      advect.uniforms.uVelocity.value = velocity.read.texture; advect.uniforms.uSource.value = dye.read.texture;
      advect.uniforms.dissipation.value = .95; pass(advect, dye.write); dye.swap();
      uniform.value = dye.read.texture;
    } finally {
      renderer.setRenderTarget(priorTarget); renderer.autoClear = priorAuto;
    }
  }
  reset();
  return {
    uniform, update, reset,
    setAspect(value) { aspect = value; },
    addPointer(x, y, dx, dy) { queue.push({ x, y, dx, dy }); },
    dispose() { targets.forEach(t => t.dispose()); materials.forEach(m => m.dispose()); geometry.dispose(); queue.length = 0; },
  };
}
