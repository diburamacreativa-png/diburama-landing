// ESCENA 02 · 3,0–9,0 s · Las líneas del plano se levantan → máquina 3D → explosionado →
// tuerca → cápsula → molécula → la molécula se aplana (entrega a la interfaz 2D).
import * as THREE from 'three';
import { Line2 } from 'three/addons/lines/Line2.js';
import { LineSegments2 } from 'three/addons/lines/LineSegments2.js';
import { LineSegmentsGeometry } from 'three/addons/lines/LineSegmentsGeometry.js';
import { LineMaterial } from 'three/addons/lines/LineMaterial.js';
import { W, H, C, clamp, lerp, inv, seg, E, smooth, mulberry32, makeCanvas, callout, hexA } from '../lib.js';
import { gl, project } from '../gl.js';
import { drawBlueprint, MACHINE, machineX, camera01 } from './s01_blueprint.js';
import { NODES2D } from './s03_software.js';

const T0 = 3.0;
const Z0 = 1.045; // zoom de la cámara 2D en t=3.0
const FOV = 30, D0 = (H / 2) / Math.tan((FOV / 2) * Math.PI / 180);
const col = (h) => new THREE.Color(h);
let S = null;

function wireForLathe(profile, segs = 64, meridians = 8, hex = false) {
  // anillos en cada vértice del perfil + meridianos → líneas técnicas
  const pos = [];
  const ring = (r, y) => {
    const n = hex ? 6 : segs;
    for (let i = 0; i < n; i++) {
      const a0 = (i / n) * Math.PI * 2 + (hex ? Math.PI / 6 : 0), a1 = ((i + 1) / n) * Math.PI * 2 + (hex ? Math.PI / 6 : 0);
      pos.push(Math.cos(a0) * r, y, Math.sin(a0) * r, Math.cos(a1) * r, y, Math.sin(a1) * r);
    }
  };
  profile.forEach(([r, y]) => { if (r > 0.5) ring(r, y); });
  const mers = hex ? 6 : meridians;
  for (let m = 0; m < mers; m++) {
    const a = (m / mers) * Math.PI * 2 + (hex ? Math.PI / 6 : 0);
    for (let i = 0; i < profile.length - 1; i++) {
      const [r0, y0] = profile[i], [r1, y1] = profile[i + 1];
      pos.push(Math.cos(a) * r0, y0, Math.sin(a) * r0, Math.cos(a) * r1, y1, Math.sin(a) * r1);
    }
  }
  const g = new LineSegmentsGeometry(); g.setPositions(pos); return g;
}
function lineMat(color, width, opts = {}) {
  const m = new LineMaterial({ color, linewidth: width, worldUnits: false, transparent: true, depthTest: true, ...opts });
  m.resolution.set(W, H); return m;
}

// --- Superficie paramétrica: tuerca hexagonal ⇄ cápsula (misma topología) ---
function morphPoint(theta, v, m) {
  // tuerca
  const a = 50, ch = 24;
  const k = ((theta % (Math.PI / 3)) + Math.PI / 3) % (Math.PI / 3) - Math.PI / 6;
  const rHex = a / Math.cos(k);
  let yN, rN;
  if (v < 0.12) { yN = -ch; rN = rHex * (v / 0.12) * 0.92; }
  else if (v > 0.88) { yN = ch; rN = rHex * ((1 - v) / 0.12) * 0.92; }
  else { const u = (v - 0.12) / 0.76; yN = lerp(-ch, ch, u); const edge = Math.min(u, 1 - u); rN = rHex * (edge < 0.12 ? lerp(0.92, 1, edge / 0.12) : 1); }
  // cápsula
  const rc = 30, half = 48;
  let yC, rC;
  if (v < 0.3) { const f = (v / 0.3) * Math.PI / 2; yC = -half - rc * Math.cos(f); rC = rc * Math.sin(f); }
  else if (v > 0.7) { const f = ((1 - v) / 0.3) * Math.PI / 2; yC = half + rc * Math.cos(f); rC = rc * Math.sin(f); }
  else { yC = lerp(-half, half, (v - 0.3) / 0.4); rC = rc; }
  const y = lerp(yN, yC, m), r = lerp(rN, rC, m);
  return [Math.cos(theta) * r, y, Math.sin(theta) * r];
}
function makeMorphHalf(bottom) {
  const U = 60, rows = [];
  const V = 26;
  for (let j = 0; j <= V; j++) rows.push({ v: bottom ? (j / V) * 0.5 : 0.5 + (j / V) * 0.5, cap: 0 });
  // tapa interior en el corte
  for (let j = 1; j <= 4; j++) rows.push({ v: 0.5, cap: j / 4 });
  if (!bottom) rows.reverse();
  const geo = new THREE.BufferGeometry();
  const nV = (U + 1) * rows.length;
  geo.setAttribute('position', new THREE.BufferAttribute(new Float32Array(nV * 3), 3));
  const idx = [];
  for (let j = 0; j < rows.length - 1; j++) for (let i = 0; i < U; i++) {
    const a = j * (U + 1) + i, b = a + 1, c = a + (U + 1), d = c + 1;
    idx.push(a, c, b, b, c, d);
  }
  geo.setIndex(idx);
  geo.userData = { U, rows };
  return geo;
}
function updateMorph(geo, m, flip) {
  const { U, rows } = geo.userData, p = geo.attributes.position.array;
  let n = 0;
  for (const row of rows) for (let i = 0; i <= U; i++) {
    const th = (i / U) * Math.PI * 2;
    let [x, y, z] = morphPoint(th, row.v, m);
    if (row.cap) { x *= 1 - row.cap; z *= 1 - row.cap; }
    p[n++] = x; p[n++] = y; p[n++] = z;
  }
  geo.attributes.position.needsUpdate = true;
  geo.computeVertexNormals();
  if (flip) { const nr = geo.attributes.normal.array; }
}

// --- Molécula (coordenadas locales) ---
const MOL = (() => {
  const atoms = [];
  const R = 58; // anillo hexagonal
  for (let i = 0; i < 6; i++) { const a = (i / 6) * Math.PI * 2; atoms.push([Math.cos(a) * R, Math.sin(a) * R, (i % 2 ? 1 : -1) * 6, i % 3 === 0 ? 'M' : 'W']); }
  const sub = [[0, 118, 0], [2, 118, 30], [4, 118, -30], [1, 112, -60], [3, 110, 60], [5, 116, 20]];
  sub.forEach(([ai, d, zz], k) => { const a = (ai / 6) * Math.PI * 2 + (k % 2 ? 0.25 : -0.2); atoms.push([Math.cos(a) * d, Math.sin(a) * d, zz, k % 2 ? 'W' : 'D']); });
  atoms.push([168, 30, 40, 'M'], [-160, -60, -50, 'W']);
  const bonds = [];
  for (let i = 0; i < 6; i++) bonds.push([i, (i + 1) % 6]);
  sub.forEach(([ai], k) => bonds.push([ai, 6 + k]));
  bonds.push([6, 12], [9, 13]);
  const radius = { M: 22, W: 17, D: 13 };
  return { atoms, bonds, radius };
})();

export function init() {
  if (S) return;
  const { renderer, env } = gl();
  const scene = new THREE.Scene();
  scene.environment = env;
  scene.background = col(C.NIGHT);
  scene.fog = new THREE.Fog(col(C.NIGHT), 1e6, 2e6);
  const camera = new THREE.PerspectiveCamera(FOV, W / H, 10, 30000);

  // Papel: textura = último fotograma de la escena 1 (sin las líneas de la máquina, que ahora son 3D)
  const pc = makeCanvas();
  const pctx = pc.getContext('2d');
  drawBlueprint(pctx, T0, { liftParts: true });
  const tex = new THREE.CanvasTexture(pc); tex.colorSpace = THREE.SRGBColorSpace; tex.anisotropy = 8;
  const paperMat = new THREE.MeshBasicMaterial({ map: tex, fog: true });
  const paper = new THREE.Mesh(new THREE.PlaneGeometry(W, H), paperMat);
  paper.rotation.x = -Math.PI / 2; scene.add(paper);
  const floorMat = new THREE.MeshBasicMaterial({ color: col(C.PAPER), fog: true });
  const floor = new THREE.Mesh(new THREE.PlaneGeometry(40000, 40000), floorMat);
  floor.rotation.x = -Math.PI / 2; floor.position.y = -1; scene.add(floor);
  const shadowPlane = new THREE.Mesh(new THREE.PlaneGeometry(40000, 40000), new THREE.ShadowMaterial({ opacity: 0.28 }));
  shadowPlane.rotation.x = -Math.PI / 2; shadowPlane.position.y = 0.5; shadowPlane.receiveShadow = true; scene.add(shadowPlane);

  // Luces
  scene.add(new THREE.HemisphereLight(0xffffff, 0x30303a, 0.9));
  const key = new THREE.DirectionalLight(0xffffff, 2.4);
  key.position.set(-900, 2200, 1200); key.castShadow = true;
  key.shadow.mapSize.set(2048, 2048); Object.assign(key.shadow.camera, { left: -1400, right: 1400, top: 1400, bottom: -1400, near: 10, far: 6000 });
  key.shadow.bias = -0.0005; key.shadow.radius = 6;
  scene.add(key); scene.add(key.target);
  const rim = new THREE.DirectionalLight(col(C.MAG_LIGHT), 1.4); rim.position.set(800, 600, -1600); scene.add(rim);

  // --- Máquina ---
  const clip = new THREE.Plane(new THREE.Vector3(-1, 0, 0), 99999);
  const matWhite = new THREE.MeshStandardMaterial({ transparent: true, color: col('#ECEBE7'), roughness: 0.42, metalness: 0.05, clippingPlanes: [clip] });
  const matGrey = new THREE.MeshStandardMaterial({ transparent: true, color: col('#9E9EA6'), roughness: 0.3, metalness: 0.75, clippingPlanes: [clip] });
  const matBlack = new THREE.MeshStandardMaterial({ transparent: true, color: col('#1B1C23'), roughness: 0.32, metalness: 0.2, clippingPlanes: [clip] });
  const matSteel = new THREE.MeshStandardMaterial({ transparent: true, color: col('#D4D4DA'), roughness: 0.22, metalness: 0.9, clippingPlanes: [clip] });
  const partMats = { flange: matGrey, housing: matWhite, cover: matBlack, hub: matGrey, shaft: matSteel, nut: matSteel };

  const root = new THREE.Group(); scene.add(root); // posición/rotación de pie
  const parts = [];
  const lineMats = [];
  for (const p of MACHINE.parts) {
    let profile;
    if (p.fins) {
      profile = [[0, p.s0], [p.r, p.s0]];
      for (const f of p.fins) profile.push([p.r, f - p.finW / 2], [p.finR, f - p.finW / 2], [p.finR, f + p.finW / 2], [p.r, f + p.finW / 2]);
      profile.push([p.r, p.s1], [0, p.s1]);
    } else profile = [[0, p.s0], [p.r, p.s0], [p.r, p.s1], [0, p.s1]];
    const flat = new THREE.Group(); root.add(flat); // escala "hacia fuera del papel"
    const explode = new THREE.Group(); flat.add(explode);
    const lie = new THREE.Group(); explode.add(lie);
    lie.position.y = -MACHINE.len / 2; // eje centrado
    let mesh;
    if (p.hex) {
      const g = new THREE.CylinderGeometry(p.r / Math.cos(Math.PI / 6), p.r / Math.cos(Math.PI / 6), p.s1 - p.s0, 6, 1);
      g.rotateY(Math.PI / 6); g.translate(0, (p.s0 + p.s1) / 2, 0);
      mesh = new THREE.Mesh(g, partMats[p.id]);
    } else {
      const pts = profile.map(([r, y]) => new THREE.Vector2(Math.max(r, 0.01), y));
      mesh = new THREE.Mesh(new THREE.LatheGeometry(pts, 96), partMats[p.id]);
    }
    mesh.castShadow = true; mesh.receiveShadow = true;
    lie.add(mesh);
    const wm = lineMat(col(C.MAG), 3.6); lineMats.push(wm);
    const wire = new LineSegments2(wireForLathe(profile, 72, 8, !!p.hex), wm);
    wire.computeLineDistances();
    lie.add(wire);
    // energía: trazo discontinuo magenta que recorre algunas líneas
    const em = lineMat(col(C.MAG_LIGHT), 4.5, { dashed: true, dashSize: 40, gapSize: 260, opacity: 0 });
    const energy = new LineSegments2(wireForLathe(profile, 72, 4, !!p.hex), em); energy.computeLineDistances(); lie.add(energy);
    parts.push({ ...p, flat, explode, lie, mesh, wire, wm, em, energy });
  }
  // tornillos, junta y rodamiento (aparecen en el explosionado)
  const extras = new THREE.Group(); root.add(extras);
  const bolts = [];
  for (let i = 0; i < 8; i++) {
    const a = (i / 8) * Math.PI * 2 + Math.PI / 8;
    const b = new THREE.Mesh(new THREE.CylinderGeometry(13, 13, 16, 6), matSteel); b.castShadow = true;
    const sh = new THREE.Mesh(new THREE.CylinderGeometry(6, 6, 60, 16), matSteel); sh.position.y = -36; b.add(sh);
    b.userData.a = a; extras.add(b); bolts.push(b);
  }
  const gasket = new THREE.Mesh(new THREE.TorusGeometry(128, 4, 12, 96), matBlack); gasket.rotation.x = Math.PI / 2; extras.add(gasket);
  const bearing = new THREE.Mesh(new THREE.TorusGeometry(56, 11, 18, 72), matSteel); bearing.rotation.x = Math.PI / 2; extras.add(bearing);
  extras.visible = false;

  // --- Tuerca → cápsula ---
  const capTop = new THREE.MeshPhysicalMaterial({ color: col('#D4D4DA'), metalness: 0.9, roughness: 0.22, clearcoat: 0, clearcoatRoughness: 0.08, side: THREE.DoubleSide });
  const capBot = capTop.clone();
  const gTop = makeMorphHalf(false), gBot = makeMorphHalf(true);
  const capsule = new THREE.Group(); scene.add(capsule);
  const halfTop = new THREE.Mesh(gTop, capTop), halfBot = new THREE.Mesh(gBot, capBot);
  halfTop.castShadow = halfBot.castShadow = true;
  capsule.add(halfTop, halfBot); capsule.visible = false;

  // --- Molécula ---
  const mol = new THREE.Group(); scene.add(mol);
  const atomMeshes = MOL.atoms.map(([x, y, z, k]) => {
    const m = new THREE.MeshStandardMaterial({ color: col(k === 'M' ? C.MAG : k === 'W' ? '#EFEEEA' : '#3A3B45'), roughness: 0.28, metalness: 0.05, transparent: true });
    const s = new THREE.Mesh(new THREE.SphereGeometry(MOL.radius[k], 48, 32), m);
    s.userData = { k, base: new THREE.Vector3(x, y, z) }; mol.add(s); return s;
  });
  const bondMat = new THREE.MeshStandardMaterial({ color: col('#C9C8C4'), roughness: 0.4, metalness: 0.1, transparent: true });
  const bondMeshes = MOL.bonds.map(() => { const b = new THREE.Mesh(new THREE.CylinderGeometry(4.5, 4.5, 1, 16), bondMat); mol.add(b); return b; });
  mol.visible = false;
  // polvo / partículas
  const NP = 2200, rnd = mulberry32(5);
  const pGeo = new THREE.BufferGeometry();
  const pPos = new Float32Array(NP * 3), pCol = new Float32Array(NP * 3);
  const pData = [];
  for (let i = 0; i < NP; i++) {
    const ai = Math.floor(rnd() * MOL.atoms.length);
    const dir = new THREE.Vector3(rnd() - 0.5, rnd() - 0.5, rnd() - 0.5).normalize();
    const off = new THREE.Vector3(rnd() - 0.5, rnd() - 0.5, rnd() - 0.5).normalize().multiplyScalar(Math.cbrt(rnd()) * MOL.radius[MOL.atoms[ai][3]] * 0.9);
    pData.push({ ai, dir, off, sp: 90 + rnd() * 220, dl: rnd() * 0.18 });
    const c = MOL.atoms[ai][3] === 'M' ? col(C.MAG) : col('#F2F1EC'); pCol.set([c.r, c.g, c.b], i * 3);
  }
  pGeo.setAttribute('position', new THREE.BufferAttribute(pPos, 3)); pGeo.setAttribute('color', new THREE.BufferAttribute(pCol, 3));
  const spr = makeCanvas(64, 64), sx = spr.getContext('2d'); const sg = sx.createRadialGradient(32, 32, 0, 32, 32, 32); sg.addColorStop(0, 'rgba(255,255,255,1)'); sg.addColorStop(0.5, 'rgba(255,255,255,0.8)'); sg.addColorStop(1, 'rgba(255,255,255,0)'); sx.fillStyle = sg; sx.fillRect(0, 0, 64, 64);
  const pMat = new THREE.PointsMaterial({ size: 7, map: new THREE.CanvasTexture(spr), vertexColors: true, transparent: true, depthWrite: false, sizeAttenuation: true });
  const points = new THREE.Points(pGeo, pMat); scene.add(points); points.visible = false;

  S = { scene, camera, paper, paperMat, floorMat, shadowPlane, key, rim, root, parts, clip, extras, bolts, gasket, bearing, capsule, halfTop, halfBot, gTop, gBot, capTop, capBot, mol, atomMeshes, bondMeshes, points, pData, pGeo, lineMats };
  S.matAll = [matWhite, matGrey, matBlack, matSteel];
}

// ---------- Cámara ----------
function sph(target, dist, polar, azim) {
  return new THREE.Vector3(target.x + dist * Math.sin(polar) * Math.sin(azim), target.y + dist * Math.cos(polar), target.z + dist * Math.sin(polar) * Math.cos(azim));
}
// Posición de la molécula / final de la tuerca
const P1 = new THREE.Vector3(0, 1130, 0);
const CAM_END = { target: P1.clone(), dist: 1150, polar: 1.42, azim: -0.95 };
function camState(t) {
  const A = { target: new THREE.Vector3(0, 0, 0), dist: D0, polar: 0.0001, azim: 0 };
  const B = { target: new THREE.Vector3(0, 330, 0), dist: 2750, polar: 1.18, azim: -0.55 };
  const Cc = { target: new THREE.Vector3(0, 690, 0), dist: 3900, polar: 1.32, azim: -0.8 };
  const lerpS = (a, b, k) => ({ target: a.target.clone().lerp(b.target, k), dist: lerp(a.dist, b.dist, k), polar: lerp(a.polar, b.polar, k), azim: lerp(a.azim, b.azim, k) });
  let s = A;
  const k1 = seg(t, 3.55, 5.35, E.inOutCubic);
  s = lerpS(A, B, k1);
  const k2 = seg(t, 5.5, 6.9, E.inOutQuad);
  if (k2 > 0) s = lerpS(s, Cc, k2);
  const k3 = seg(t, 6.75, 7.55, E.inOutCubic);
  if (k3 > 0) s = lerpS(s, CAM_END, k3);
  // leve deriva orbital constante
  s.azim += 0.05 * Math.max(0, t - 7.6);
  s.dist *= 1 - 0.012 * (t - 3);
  return s;
}
function applyCam(t) {
  const s = camState(t);
  const cam = S.camera;
  cam.position.copy(sph(s.target, s.dist, s.polar, s.azim));
  const upBlend = clamp(s.polar / 0.5);
  cam.up.set(0, 0, -1).lerp(new THREE.Vector3(0, 1, 0), smooth(upBlend)).normalize();
  cam.lookAt(s.target);
  cam.updateMatrixWorld(); cam.updateProjectionMatrix();
  return s;
}

// Posiciones de pantalla finales de los nodos (entrega a la escena 03)
function nodeWorldTarget(i) {
  const cam = S.camera;
  const [sx, sy] = NODES2D[i].p;
  const fwd = new THREE.Vector3(); cam.getWorldDirection(fwd);
  const right = new THREE.Vector3().crossVectors(fwd, cam.up).normalize();
  const up = new THREE.Vector3().crossVectors(right, fwd).normalize();
  const dist = cam.position.distanceTo(CAM_END.target);
  const Hh = dist * Math.tan((FOV / 2) * Math.PI / 180);
  return cam.position.clone().add(fwd.multiplyScalar(dist)).add(right.multiplyScalar(((sx - 540) / 960) * Hh)).add(up.multiplyScalar(((960 - sy) / 960) * Hh));
}

export const MOL_SCREEN = { atoms: [], ready: false };

function update(t) {
  const s = applyCam(t);
  const T = (a, b, e = E.inOutCubic) => seg(t, a, b, e);
  // --- papel: se oscurece y se pierde en niebla ---
  const dark = T(4.5, 5.6);
  const paperC = new THREE.Color(1, 1, 1).lerp(col('#14151C'), dark);
  S.paperMat.color.copy(paperC);
  S.floorMat.color.copy(col(C.PAPER).lerp(col('#101118'), dark));
  const fogK = T(3.8, 5.5, smooth);
  S.scene.fog.near = lerp(1e6, 2600, fogK); S.scene.fog.far = lerp(2e6, 7000, fogK);
  S.shadowPlane.material.opacity = 0.3 * seg(t, 3.25, 3.9) * (1 - T(6.3, 7.0));
  // --- inflado pieza a pieza ---
  const stand = T(4.05, 5.25, E.inOutCubic);
  const lieY = 170, axisZ = (MACHINE.axisY - 960) * Z0;
  S.root.scale.setScalar(Z0);
  const infMax = seg(t, 3.02, 3.72, E.outCubic);
  S.root.position.set(0, lerp(2 + lieY * Z0 * infMax, (MACHINE.len / 2) * Z0 + 2, stand), lerp(axisZ, 0, stand));
  S.root.rotation.set(0, 0, lerp(-Math.PI / 2, 0, stand));
  // durante el tumbado el eje de la máquina es el X del mundo: aplicamos "inflado" en el Y del mundo a cada pieza
  const turn = 0.9 * Math.max(0, t - 5.0) + 0.25 * Math.max(0, t - 6.0);
  S.parts.forEach((p, i) => {
    const inf = seg(t, 3.02 + 0.07 * i, 3.72 + 0.07 * i, E.outCubic);
    // el grupo 'flat' está dentro de root (que está rotado -90° en Z mientras está tumbado): el Y del mundo = X local
    p.flat.scale.set(lerp(0.004, 1, inf), 1, 1);
    // explosionado
    const offs = [-50, 95, 250, 330, 450, 620];
    const st = [6.0, 6.06, 6.18, 6.28, 6.38, 6.5][i];
    const ek = seg(t, st, st + 0.42, (x) => E.outBack(x, 1.5));
    p.explode.position.y = offs[i] * ek;
    p.explode.rotation.y = turn * (1 + i * 0.03);
    // cables y energía
    const solid = T(3.35 + 0.05 * i, 4.1 + 0.05 * i, smooth);
    p.wm.color.copy(col(C.MAG).lerp(col('#2A2B33'), T(4.4, 5.2)));
    p.wm.opacity = 1 - 0.75 * T(5.4, 6.2);
    p.wm.linewidth = lerp(3.6, 1.6, T(4.2, 5.2));
    p.em.opacity = T(4.4, 4.9) * (1 - T(6.8, 7.2));
    p.em.dashOffset = -t * 900;
  });
  // revelado de sólidos por barrido (plano de corte que avanza a lo largo del eje)
  const rv = T(3.3, 4.3, E.inOutCubic);
  S.clip.constant = lerp(-400, 900, rv); // muestra x < constante (normal -X)
  S.clip.normal.set(-1, 0, 0);
  if (rv >= 1) S.clip.constant = 1e6;
  // extras del explosionado
  const ex = T(5.95, 6.4, (x) => E.outBack(x, 1.4));
  S.extras.visible = ex > 0.001 && t < 7.4;
  S.extras.rotation.y = turn;
  S.bolts.forEach((b) => { const a = b.userData.a; const r = 150 + 70 * ex; b.position.set(Math.cos(a) * r, (MACHINE.len / 2) * 0 - MACHINE.len / 2 + 34 + 8 + 150 * ex, Math.sin(a) * r); });
  S.gasket.position.y = -MACHINE.len / 2 + 300 + 170 * ex; S.gasket.scale.setScalar(Math.max(0.001, ex));
  S.bearing.position.y = -MACHINE.len / 2 + 360 + 330 * ex; S.bearing.scale.setScalar(Math.max(0.001, ex));
  // resto de piezas se desvanecen cuando la tuerca protagoniza
  const fadeRest = T(6.85, 7.45);
  S.matAll.forEach(m => { m.opacity = 1 - fadeRest; });
  S.root.visible = fadeRest < 0.999;
  // --- tuerca → cápsula ---
  const nutPart = S.parts[5];
  const tStart = 6.62;
  if (t >= tStart) {
    nutPart.mesh.visible = false; nutPart.wire.visible = false; nutPart.energy.visible = false;
    S.capsule.visible = t < 8.0;
    // posición inicial = posición mundial de la tuerca en el explosionado
    const n0 = new THREE.Vector3(0, (563) + 0, 0); // centro de la tuerca en coords locales de 'lie'
    nutPart.lie.updateMatrixWorld(true);
    const w0 = nutPart.lie.localToWorld(n0.clone());
    const k = T(tStart, 7.35, E.inOutCubic);
    S.capsule.position.copy(w0.clone().lerp(P1, k));
    const m = T(6.85, 7.3, E.inOutCubic);
    updateMorph(S.gTop, m); updateMorph(S.gBot, m);
    const sc = Z0 * lerp(1, 1.0, m);
    S.capsule.scale.setScalar(sc);
    // giro: rota sobre su eje y se inclina hacia cámara
    S.capsule.rotation.set(lerp(0, 0.5, k), turn + 9 * E.outCubic(inv(tStart, 7.5, t)), lerp(0, -0.95, k));
    // materiales: acero → cápsula brillante (magenta / blanco roto)
    S.capTop.color.copy(col('#D4D4DA').lerp(col(C.MAG), m)); S.capBot.color.copy(col('#D4D4DA').lerp(col('#F1F0EC'), m));
    for (const mt of [S.capTop, S.capBot]) { mt.metalness = lerp(0.9, 0.0, m); mt.roughness = lerp(0.22, 0.16, m); mt.clearcoat = m; }
    // apertura
    const open = T(7.32, 7.62, E.outCubic);
    S.halfTop.position.y = 70 * open; S.halfBot.position.y = -70 * open;
    S.halfTop.rotation.z = 0.35 * open; S.halfBot.rotation.z = -0.25 * open;
    const cfade = T(7.55, 7.85);
    S.capTop.transparent = S.capBot.transparent = true; S.capTop.opacity = S.capBot.opacity = 1 - cfade;
  } else { nutPart.mesh.visible = true; nutPart.wire.visible = true; nutPart.energy.visible = true; S.capsule.visible = false; }
  // --- partículas → molécula ---
  const pk = inv(7.36, 7.95, t);
  S.points.visible = t > 7.36 && t < 8.15;
  const molRot = new THREE.Euler(0.4 + 0.9 * (t - 7.4), 1.2 * (t - 7.4), 0.2);
  const flatK = T(8.2, 8.84, E.inOutCubic);
  const rotDamp = 1 - flatK;
  const molQ = new THREE.Quaternion().setFromEuler(new THREE.Euler(molRot.x * 1, molRot.y * 1, molRot.z));
  // quaternión "de cara a cámara" para el estado plano
  const camQ = S.camera.quaternion.clone();
  const atomWorld = (i) => {
    const b = S.atomMeshes[i].userData.base.clone().multiplyScalar(Z0).applyQuaternion(molQ).add(P1);
    return flatK > 0 ? b.lerp(nodeWorldTarget(i), flatK) : b;
  };
  if (S.points.visible) {
    const arr = S.pGeo.attributes.position.array;
    S.pData.forEach((d, i) => {
      const k = E.inOutCubic(clamp((pk - d.dl) / (1 - d.dl)));
      const start = P1.clone().add(d.dir.clone().multiplyScalar(8));
      const mid = P1.clone().add(d.dir.clone().multiplyScalar(d.sp));
      const end = atomWorld(d.ai).add(d.off.clone().multiplyScalar(Z0));
      // bezier cuadrática
      const a = start.clone().lerp(mid, k), b = mid.clone().lerp(end, k), p = a.lerp(b, k);
      arr[i * 3] = p.x; arr[i * 3 + 1] = p.y; arr[i * 3 + 2] = p.z;
    });
    S.pGeo.attributes.position.needsUpdate = true;
    S.points.material.opacity = 1 - T(7.85, 8.1);
  }
  const atomsIn = T(7.72, 8.0, E.outCubic);
  S.mol.visible = t > 7.72;
  const shots = [];
  S.atomMeshes.forEach((a, i) => {
    const wp = atomWorld(i);
    a.position.copy(wp);
    const Hh = S.camera.position.distanceTo(CAM_END.target) * Math.tan((FOV / 2) * Math.PI / 180);
    const rFlat = (NODES2D[i].r / MOL.radius[a.userData.k]) * (2 * Hh / H);
    a.scale.setScalar(Math.max(0.001, atomsIn) * lerp(Z0, rFlat, flatK));
    a.quaternion.copy(camQ);
    a.scale.z *= lerp(1, 0.04, flatK);
    // sombreado plano al aplanarse
    const k = a.userData.k, base = col(k === 'M' ? C.MAG : k === 'W' ? '#EFEEEA' : '#3A3B45');
    a.material.color.copy(base.clone().lerp(new THREE.Color(0, 0, 0), flatK));
    a.material.emissive.copy(new THREE.Color(0, 0, 0).lerp(base, flatK));
    const sp = project(wp, S.camera);
    shots.push({ x: sp[0], y: sp[1], k });
  });
  MOL_SCREEN.atoms = shots;
  MOL.bonds.forEach(([i, j], bi) => {
    const b = S.bondMeshes[bi];
    const A = S.atomMeshes[i].position, B = S.atomMeshes[j].position;
    const len = A.distanceTo(B);
    b.position.copy(A).add(B).multiplyScalar(0.5);
    b.scale.set(Z0 * lerp(1, 0.35, flatK) * atomsIn, len * atomsIn, Z0 * lerp(1, 0.35, flatK) * atomsIn);
    b.quaternion.setFromUnitVectors(new THREE.Vector3(0, 1, 0), B.clone().sub(A).normalize());
  });
  S.bondMeshes.forEach(b => { b.material.opacity = 1 - T(8.6, 8.95); });
  // luz clave sigue a la escena
  S.key.target.position.copy(s.target); S.key.position.copy(s.target.clone().add(new THREE.Vector3(-900, 2200, 1200)));
  return s;
}

export const scene02 = {
  name: '02 MÁQUINA → CÁPSULA → MOLÉCULA', start: 3.0, end: 9.0,
  init,
  draw(ctx, t) {
    init();
    const { renderer, canvas } = gl();
    update(t);
    renderer.setClearColor(col(C.NIGHT), 1);
    renderer.render(S.scene, S.camera);
    ctx.drawImage(canvas, 0, 0);
    // viñeta de profundidad al oscurecer
    // --- Callouts ---
    const cam = S.camera;
    if (t > 4.0 && t < 6.2) {
      const cover = S.parts[2].lie; cover.updateMatrixWorld(true);
      const [ax, ay] = project(cover.localToWorld(new THREE.Vector3(-138, 316, 0)), cam);
      callout(ctx, { ax, ay, tx: 80, ty: 1400, text: 'UNA MÁQUINA.', fig: 'FIG. 01 — SECCIÓN A–A', p: inv(4.35, 5.2, t), out: inv(5.85, 6.1, t), color: C.OFF });
    }
    if (t > 7.6 && t < 9.0) {
      const a = MOL_SCREEN.atoms[0];
      callout(ctx, { ax: a.x, ay: a.y, tx: 80, ty: 1400, text: 'UNA MOLÉCULA.', fig: 'FIG. 02 — C₁₄ · ESTRUCTURA', p: inv(7.75, 8.45, t), out: inv(8.75, 8.98, t), color: C.OFF });
    }
  },
};
