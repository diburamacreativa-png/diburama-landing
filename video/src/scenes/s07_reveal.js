// ESCENA 07 · 18,6–22,5 s · REVELACIÓN: todo el universo estaba dentro de la gota → la gota es la del logo.
// ESCENA 08 · 22,5–27,0 s · Cierre: DIBURAMA · PÁSANOS LO COMPLICADO. · la gota cae → LOOP al fotograma 0.
import * as THREE from 'three';
import { W, H, C, FONT_HEAD, FONT_MONO, FLAGS, clamp, lerp, inv, seg, E, smooth, hexA, makeCanvas, drawDrop, dropPath, drawLogoA, drawWordmark, LOGO_DROP, mulberry32 } from '../lib.js';
import { gl } from '../gl.js';
import { FREEZE } from './s05_person.js';
import { drawBlueprint, CAM0, IMPACT_T, dropFallY, init as initBP } from './s01_blueprint.js';

// Composición final del logo
export const LOGO = { cx: 540, cy: 800, s: 120 };
export const LOGO_DROP_POS = { x: LOGO.cx + LOGO_DROP.dx * LOGO.s, y: LOGO.cy + LOGO_DROP.dy * LOGO.s, r: LOGO_DROP.r * LOGO.s };

let R7 = null;
async function init() {
  if (R7) return;
  const { TIMELINE } = await import('../timeline.js');
  const byName = (n) => TIMELINE.find(s => s.name.startsWith(n));
  // instantáneas de las escenas anteriores → tira panorámica para el interior de la gota
  const shots = [['01', 2.9, 360], ['02', 5.45, 380], ['02', 7.95, 420], ['03', 10.3, 300], ['04', 12.7, 420], ['05', 14.55, 640]];
  const TS = 512;
  const strip = makeCanvas(TS * shots.length, TS), sc = strip.getContext('2d');
  const tmp = makeCanvas(), tc = tmp.getContext('2d');
  FLAGS.noCallouts = true;
  for (let i = 0; i < shots.length; i++) {
    const [n, t, y0] = shots[i];
    tc.setTransform(1, 0, 0, 1, 0, 0); tc.fillStyle = C.NIGHT; tc.fillRect(0, 0, W, H);
    tc.save(); await byName(n).draw(tc, t); tc.restore();
    sc.drawImage(tmp, 0, y0, W, W, i * TS, 0, TS, TS);
  }
  FLAGS.noCallouts = false;
  const { renderer } = gl();
  const tex = new THREE.CanvasTexture(strip); tex.colorSpace = THREE.SRGBColorSpace; tex.wrapS = THREE.RepeatWrapping; tex.minFilter = THREE.LinearMipmapLinearFilter; tex.anisotropy = 8;
  const mat = new THREE.ShaderMaterial({
    uniforms: { uTex: { value: tex }, uCenter: { value: new THREE.Vector2() }, uR: { value: 100 }, uRot: { value: 0 }, uRes: { value: new THREE.Vector2(W, H) } },
    vertexShader: `void main(){ gl_Position = vec4(position.xy, 0.0, 1.0); }`,
    fragmentShader: `
      uniform sampler2D uTex; uniform vec2 uCenter; uniform float uR; uniform float uRot; uniform vec2 uRes;
      vec3 look(vec3 n, float k){
        float lon = atan(n.x * k, n.z) + uRot;
        float lat = asin(clamp(n.y * k, -1.0, 1.0));
        vec2 uv = vec2(fract(lon / 6.2831853), clamp(0.5 + lat / 3.14159 * 0.95, 0.001, 0.999));
        return texture2D(uTex, uv).rgb;
      }
      void main(){
        vec2 px = vec2(gl_FragCoord.x, uRes.y - gl_FragCoord.y);
        vec2 q = (px - uCenter) / uR; float d = length(q);
        vec2 qq = d > 0.995 ? q / d * 0.995 : q;
        vec3 n = vec3(qq.x, -qq.y, sqrt(max(0.0, 1.0 - dot(qq, qq))));
        vec3 c;
        c.r = look(n, 0.985).r; c.g = look(n, 1.0).g; c.b = look(n, 1.015).b;
        c *= mix(1.0, 0.55, smoothstep(0.6, 1.0, d));
        gl_FragColor = vec4(c, 1.0);
      }`,
    depthTest: false, depthWrite: false,
  });
  mat.toneMapped = false;
  const quad = new THREE.Mesh(new THREE.PlaneGeometry(2, 2), mat);
  const scene = new THREE.Scene(); scene.add(quad);
  const cam = new THREE.OrthographicCamera(-1, 1, 1, -1, 0, 1);
  // campo de fragmentos (mundo alrededor de la gota)
  const rnd = mulberry32(77), frags = [];
  for (let i = 0; i < 260; i++) { const a = rnd() * Math.PI * 2, d = 40 + Math.pow(rnd(), 0.7) * 520; frags.push({ x: Math.cos(a) * d, y: Math.sin(a) * d * 1.2, k: Math.floor(rnd() * 5), s: 0.5 + rnd() * 1.4, rot: rnd() * 6, m: rnd() < 0.25 }); }
  R7 = { mat, scene, cam, frags, strip };
}

function renderInner(cx, cy, r, rot) {
  const { renderer, canvas } = gl();
  R7.mat.uniforms.uCenter.value.set(cx, cy); R7.mat.uniforms.uR.value = r; R7.mat.uniforms.uRot.value = rot;
  renderer.setClearColor(0x000000, 0); renderer.render(R7.scene, R7.cam);
  return canvas;
}

/** Gota de cristal con el universo dentro. world: 0..1 visibilidad del interior. */
function glassDrop(ctx, x, y, r, world, t) {
  if (world <= 0.001) { drawDrop(ctx, x, y, r, { glow: 0.5 }); return; }
  // halo
  const g0 = ctx.createRadialGradient(x, y, r * 0.3, x, y, r * 2.6); g0.addColorStop(0, hexA(C.MAG, 0.35)); g0.addColorStop(1, hexA(C.MAG, 0));
  ctx.fillStyle = g0; ctx.fillRect(x - r * 2.6, y - r * 2.6, r * 5.2, r * 5.2);
  ctx.save();
  dropPath(ctx, x, y, r); ctx.clip();
  const body = ctx.createRadialGradient(x - r * 0.35, y - r * 0.2, r * 0.1, x, y + r * 0.1, r * 1.35);
  body.addColorStop(0, '#FF6FB4'); body.addColorStop(0.45, C.MAG); body.addColorStop(1, '#7A0A41');
  ctx.fillStyle = body; ctx.fillRect(x - r * 2, y - r * 3, r * 4, r * 5);
  const inner = renderInner(x, y, r, 2.2 + t * 0.6);
  ctx.globalAlpha = world; ctx.drawImage(inner, 0, 0);
  // tinte magenta y lente
  ctx.globalAlpha = 0.35 * world; ctx.globalCompositeOperation = 'multiply'; ctx.fillStyle = '#FFA6CF'; ctx.fillRect(x - r * 2, y - r * 3, r * 4, r * 5);
  ctx.globalCompositeOperation = 'source-over'; ctx.globalAlpha = 1;
  const fr = ctx.createRadialGradient(x, y + r * 0.05, r * 0.55, x, y + r * 0.05, r * 1.05);
  fr.addColorStop(0, 'rgba(122,10,65,0)'); fr.addColorStop(0.8, 'rgba(160,12,80,0.25)'); fr.addColorStop(1, 'rgba(200,20,110,0.95)');
  ctx.fillStyle = fr; ctx.fillRect(x - r * 2, y - r * 3, r * 4, r * 5);
  // punta: siempre tinta sólida
  const tipG = ctx.createLinearGradient(0, y - r * 1.6, 0, y - r * 0.7); tipG.addColorStop(0, C.MAG); tipG.addColorStop(1, hexA(C.MAG, 0));
  ctx.fillStyle = tipG; ctx.fillRect(x - r, y - r * 1.6, r * 2, r * 0.9);
  ctx.restore();
  ctx.save(); ctx.globalAlpha = 0.9;
  ctx.beginPath(); ctx.ellipse(x - r * 0.38, y - r * 0.28, r * 0.2, r * 0.32, -0.5, 0, Math.PI * 2);
  const sp = ctx.createRadialGradient(x - r * 0.38, y - r * 0.28, 0, x - r * 0.38, y - r * 0.28, r * 0.32);
  sp.addColorStop(0, 'rgba(255,255,255,0.95)'); sp.addColorStop(1, 'rgba(255,255,255,0)'); ctx.fillStyle = sp; ctx.fill();
  ctx.restore();
}

function logoAPath(ctx, cx, cy, s) {
  ctx.beginPath();
  ctx.arc(cx, cy, s, 0, Math.PI * 2); ctx.moveTo(cx + s * 0.47, cy); ctx.arc(cx, cy, s * 0.47, 0, Math.PI * 2, true);
  const x0 = cx + s * 0.47, x1 = cx + s;
  ctx.moveTo(x0, cy); ctx.lineTo(x0, cy - s * 0.95); ctx.quadraticCurveTo(x0, cy - s * 1.06, x0 + s * 0.1, cy - s * 1.06);
  ctx.lineTo(x1, cy - s * 1.06); ctx.lineTo(x1, cy + s); ctx.lineTo(x0, cy + s); ctx.closePath();
}

function revealView(t) {
  const u = seg(t, 18.6, 22.35, E.inOutCubic);
  const Z0 = FREEZE.r / LOGO_DROP_POS.r;
  const Z = Math.pow(Z0, 1 - u);
  const D = [lerp(FREEZE.x, LOGO_DROP_POS.x, u), lerp(FREEZE.y, LOGO_DROP_POS.y, u)];
  const w2s = (x, y) => [(x - LOGO_DROP_POS.x) * Z + D[0], (y - LOGO_DROP_POS.y) * Z + D[1]];
  return { u, Z, D, w2s };
}

export const scene07 = {
  name: '07 REVELACIÓN: MUNDO EN LA GOTA → LOGO', start: 18.6, end: 22.5,
  init,
  async draw(ctx, t) {
    await init();
    const v = revealView(t);
    // fondo: gris del congelado → noche (onda desde la gota)
    ctx.fillStyle = C.PAPER; ctx.fillRect(0, 0, W, H);
    const bw = seg(t, 18.6, 18.95, E.inQuad);
    if (bw > 0) {
      const rr = 1 + 2400 * bw;
      const g = ctx.createRadialGradient(v.D[0], v.D[1], Math.max(0, rr - 120), v.D[0], v.D[1], rr);
      g.addColorStop(0, C.NIGHT); g.addColorStop(1, hexA(C.NIGHT, 0));
      ctx.fillStyle = g; ctx.fillRect(0, 0, W, H);
      ctx.fillStyle = C.NIGHT; ctx.beginPath(); ctx.arc(v.D[0], v.D[1], Math.max(0, rr - 120), 0, Math.PI * 2); ctx.fill();
    }
    // órbitas y fragmentos del universo (se contraen hacia la gota al alejarnos)
    const fa = seg(t, 18.75, 19.3) * (1 - seg(t, 21.3, 22.2));
    if (fa > 0) {
      ctx.save(); ctx.globalAlpha = fa;
      [60, 95, 150, 240, 380].forEach((r, i) => {
        const [x, y] = v.w2s(LOGO_DROP_POS.x, LOGO_DROP_POS.y);
        ctx.strokeStyle = i % 2 ? 'rgba(242,241,236,0.18)' : hexA(C.MAG, 0.35); ctx.lineWidth = 1.5;
        ctx.setLineDash([6 + i * 4, 10 + i * 6]); ctx.lineDashOffset = -t * (40 + i * 25);
        ctx.beginPath(); ctx.ellipse(x, y, r * v.Z, r * v.Z * 0.92, 0, 0, Math.PI * 2); ctx.stroke();
      });
      ctx.setLineDash([]);
      R7.frags.forEach(f => {
        const [x, y] = v.w2s(LOGO_DROP_POS.x + f.x, LOGO_DROP_POS.y + f.y);
        if (x < -40 || x > W + 40 || y < -40 || y > H + 40) return;
        const s = f.s * Math.min(3, 0.6 + v.Z * 0.4);
        ctx.strokeStyle = f.m ? C.MAG : 'rgba(242,241,236,0.55)'; ctx.fillStyle = ctx.strokeStyle; ctx.lineWidth = 1.5;
        ctx.save(); ctx.translate(x, y); ctx.rotate(f.rot + t * 0.3);
        if (f.k === 0) { ctx.beginPath(); ctx.arc(0, 0, 3 * s, 0, Math.PI * 2); ctx.fill(); }
        else if (f.k === 1) { ctx.beginPath(); ctx.moveTo(-8 * s, 0); ctx.lineTo(8 * s, 0); ctx.moveTo(0, -8 * s); ctx.lineTo(0, 8 * s); ctx.stroke(); }
        else if (f.k === 2) { ctx.strokeRect(-7 * s, -7 * s, 14 * s, 14 * s); }
        else if (f.k === 3) { ctx.beginPath(); ctx.arc(0, 0, 9 * s, 0, Math.PI * 1.3); ctx.stroke(); }
        else { ctx.beginPath(); ctx.moveTo(-14 * s, 4 * s); ctx.lineTo(-4 * s, -6 * s); ctx.lineTo(4 * s, 2 * s); ctx.lineTo(14 * s, -8 * s); ctx.stroke(); }
        ctx.restore();
      });
      ctx.restore();
    }
    // la "a" del logo aparece: primero trazo magenta, luego relleno
    const outline = seg(t, 19.7, 20.9, E.inOutCubic), fill = seg(t, 20.6, 21.5);
    if (outline > 0) {
      const [cx, cy] = v.w2s(LOGO.cx, LOGO.cy), s = LOGO.s * v.Z;
      ctx.save();
      if (fill > 0) { ctx.globalAlpha = fill; ctx.fillStyle = C.OFF; logoAPath(ctx, cx, cy, s); ctx.fill('evenodd'); ctx.globalAlpha = 1; }
      ctx.strokeStyle = C.MAG; ctx.lineWidth = 3; ctx.globalAlpha = 1 - fill * 0.9;
      const per = 2 * Math.PI * s * 1.47 + s * 6;
      ctx.setLineDash([per * outline, per]); logoAPath(ctx, cx, cy, s); ctx.stroke();
      ctx.restore();
    }
    // la gota
    const [dx, dy] = v.w2s(LOGO_DROP_POS.x, LOGO_DROP_POS.y);
    const world = seg(t, 18.62, 19.0) * (1 - seg(t, 21.2, 22.1));
    glassDrop(ctx, dx, dy, LOGO_DROP_POS.r * v.Z, world, t);
    // texto
    const ta = seg(t, 19.35, 19.8) * (1 - seg(t, 21.95, 22.4));
    if (ta > 0) {
      ctx.save(); ctx.globalAlpha = ta; ctx.textAlign = 'center'; ctx.textBaseline = 'alphabetic';
      ctx.font = `700 92px ${FONT_HEAD}`;
      const w1 = seg(t, 19.35, 19.85, E.outCubic), w2 = seg(t, 19.6, 20.1, E.outCubic);
      ctx.save(); ctx.beginPath(); ctx.rect(0, 1240, 90 + 900 * w1, 110); ctx.clip(); ctx.fillStyle = C.OFF; ctx.fillText('TODO SE PUEDE', 540, 1330); ctx.restore();
      ctx.save(); ctx.beginPath(); ctx.rect(0, 1340, 190 + 700 * w2, 120); ctx.clip(); ctx.fillStyle = C.MAG; ctx.fillText('EXPLICAR.', 540, 1430); ctx.restore();
      ctx.restore();
    }
  },
};

// ---------- ESCENA 08: cierre + loop ----------
const HOLD_CAMY = -4700;
const END_T = 27 - 1 / 30; // último fotograma
const camEndY = CAM0.dy * Math.pow(1 + 1 / 30, 3);            // cámara del fotograma "-1" de la escena 1
const camEndV = -3 * CAM0.dy * Math.pow(1 + 1 / 30, 2) / 1.0;  // px/s
const camEndX = CAM0.dx * Math.pow(1 + 1 / 30, 3);
function hermite(p0, v0, p1, v1, T, u) { const u2 = u * u, u3 = u2 * u; return (2 * u3 - 3 * u2 + 1) * p0 + (u3 - 2 * u2 + u) * T * v0 + (-2 * u3 + 3 * u2) * p1 + (u3 - u2) * T * v1; }
const WHIP0 = 26.3;
function endCamY(t) { if (t <= WHIP0) return HOLD_CAMY; const T = END_T - WHIP0; return hermite(HOLD_CAMY, 0, camEndY, camEndV, T, clamp((t - WHIP0) / T)); }
const FALL0 = 25.98;
function endDropY(t) {
  if (t <= FALL0) return LOGO_DROP_POS.y;
  const T = END_T - FALL0, u = clamp((t - FALL0) / T);
  // en el último fotograma la gota sale por abajo con la misma velocidad con la que entra en el fotograma 0
  const vIn = 0.86 * (1082 - dropY0()) / IMPACT_T;
  return hermite(LOGO_DROP_POS.y, 0, H + (-dropY0()) + vIn / 30, vIn, T, u);
}
const dropY0 = () => -14;

function drawEndcard(ctx, t, oy) {
  // logo
  drawLogoA(ctx, LOGO.cx, LOGO.cy + oy, LOGO.s, C.OFF);
  const wm = seg(t, 22.55, 23.2, E.outCubic);
  if (wm > 0) drawWordmark(ctx, 540, 1012 + oy + 24 * (1 - wm), 84, C.OFF, wm, lerp(0.5, 0.2, wm));
  // copy
  const cp = seg(t, 23.1, 23.65, E.inOutCubic);
  if (cp > 0) {
    ctx.save(); ctx.font = `700 60px ${FONT_HEAD}`; ctx.textBaseline = 'alphabetic';
    const a = 'PÁSANOS LO ', b = 'COMPLICADO.';
    const wa = ctx.measureText(a).width, wb = ctx.measureText(b).width, x0 = 540 - (wa + wb) / 2, y = 1206 + oy;
    ctx.beginPath(); ctx.rect(x0 - 10, y - 70, (wa + wb + 20) * cp, 100); ctx.clip();
    ctx.fillStyle = C.OFF; ctx.fillText(a, x0, y);
    ctx.fillStyle = C.GREY; ctx.fillText(b, x0 + wa, y);
    ctx.restore();
    if (cp < 1) { ctx.fillStyle = C.MAG; ctx.fillRect(x0 - 10 + (wa + wb + 20) * cp, y - 56, 8, 70); }
  }
  const url = 'videodiburama.com', up = seg(t, 23.55, 24.1);
  if (up > 0) {
    ctx.save(); ctx.font = `400 34px ${FONT_MONO}`; ctx.textAlign = 'center'; ctx.fillStyle = C.GREY;
    ctx.fillText(url.slice(0, Math.round(url.length * up)), 540, 1290 + oy); ctx.restore();
  }
}

export const scene08 = {
  name: '08 CIERRE → LOOP', start: 22.5, end: 27.0,
  draw(ctx, t) {
    initBP();
    const whip = t > WHIP0;
    // desenfoque de movimiento durante el barrido: promedio de sub-muestras
    const N = whip ? 14 : 1;
    const shutter = 1 / 30 * 0.8;
    const acc = N > 1 ? (ACC || (ACC = makeCanvas())) : null, tmp = N > 1 ? (TMP || (TMP = makeCanvas())) : null;
    if (acc) { const a = acc.getContext('2d'); a.setTransform(1, 0, 0, 1, 0, 0); a.globalAlpha = 1; a.globalCompositeOperation = 'source-over'; a.fillStyle = '#000'; a.fillRect(0, 0, W, H); }
    for (let k = 0; k < N; k++) {
      const ts = N > 1 ? t - shutter * (k / (N - 1) - 0.5) : t;
      const c = N > 1 ? tmp.getContext('2d') : ctx;
      c.save(); c.setTransform(1, 0, 0, 1, 0, 0);
      const camY = endCamY(ts);
      const oy = -(camY - HOLD_CAMY);
      c.fillStyle = C.NIGHT; c.fillRect(0, 0, W, H);
      // papel (hoja del plano) que sube desde abajo
      if (-2400 - camY < H) drawBlueprint(c, 0, { cam: { camX: camEndX, camY, z: 1, shx: 0, shy: 0 }, inkOn: false, noDrop: true });
      drawEndcard(c, t, oy);
      c.restore();
      if (N > 1) { const a = acc.getContext('2d'); a.globalCompositeOperation = 'lighter'; a.globalAlpha = 1 / N; a.drawImage(tmp, 0, 0); }
    }
    if (acc) { const a = acc.getContext('2d'); a.globalAlpha = 1; a.globalCompositeOperation = 'source-over'; ctx.drawImage(acc, 0, 0); }
    // la gota: asentamiento, desprendimiento y caída
    let y = endDropY(t), r = LOGO_DROP_POS.r, stretch = 1, squash = 1;
    const settle = t - 22.5;
    if (settle < 0.7) squash = 1 + 0.18 * Math.exp(-settle * 6) * Math.cos(settle * 34);
    const pre = seg(t, 25.7, FALL0, E.inQuad);
    if (t < FALL0) { stretch = 1 + 0.35 * pre; squash = 1 - 0.08 * pre; y += 6 * pre; }
    else { const k = seg(t, FALL0, FALL0 + 0.25); stretch = lerp(1.35, 1.35, k); squash = 1.12; r = lerp(r, 28, seg(t, FALL0, END_T)); }
    if (t > FALL0) for (let i = 3; i >= 1; i--) drawDrop(ctx, LOGO_DROP_POS.x, y - i * 15, r, { stretch: 1.35, squash: 1.12, alpha: 0.12 * (4 - i), glow: 0 });
    drawDrop(ctx, LOGO_DROP_POS.x, y, r, { stretch, squash, glow: 0.6 });
  },
};
let ACC = null, TMP = null;
