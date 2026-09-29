// ESCENA 05 · 13,0–16,0 s · Persona "real" (placeholder: silueta a contraluz) → ilustración 2D siguiendo la tinta.
// ESCENA 06 · 16,0–18,6 s · El mundo ilustrado se simplifica; las líneas magenta vuelven a la mano → LA GOTA → silencio.
import { W, H, C, clamp, lerp, inv, seg, E, smooth, noise1, fbm1, hexA, callout, makeCanvas, drawDrop, mulberry32 } from '../lib.js';
import { landscape, ridgeY, HZ, VP, ROUTE_END } from './s04_horizon.js';

// ---------- Rig 2D (perfil, mirando a la derecha) ----------
const L = { thigh: 245, shin: 238, foot: 96, torso: 330, neck: 44, upper: 188, fore: 172 };
export const FREEZE = { x: 540, y: 960, r: 250 };

function pose(t) {
  // caminar 12,9–15,25; detenerse; levantar la mano 15,25–16,0
  const walkEnd = 15.25;
  const tw = Math.min(t, walkEnd);
  const phase = (tw - 12.9) * 2 * Math.PI * 0.95; // ~1 ciclo/seg
  const stopK = seg(t, walkEnd - 0.35, walkEnd + 0.2, smooth);
  const amp = 1 - stopK;
  const hipX = lerp(230, 520, E.outCubic(inv(12.9, walkEnd + 0.1, t)));
  const bob = -9 * Math.cos(2 * phase) * amp;
  const hip = [hipX, 1745 - (L.thigh + L.shin) - 8 + bob];
  const lean = 0.07 * amp + 0.02;
  const leg = (ph) => {
    const th = 0.4 * Math.sin(ph) * amp;
    const kn = (0.08 + 0.62 * Math.pow(Math.max(0, Math.sin(ph + 2.1)), 1.5)) * amp + 0.04;
    const fa = -0.1 * amp * Math.cos(ph);
    return { th, kn, fa };
  };
  const raise = seg(t, 15.3, 15.95, E.inOutCubic);
  const arm = (ph, near) => {
    let ua = -0.38 * Math.sin(ph) * amp + 0.05, el = 0.25 + 0.15 * (1 + Math.sin(ph)) * amp;
    if (near) { ua = lerp(ua, 1.05, raise); el = lerp(el, 0.95, raise); }
    return { ua, el };
  };
  return { hip, lean, legN: leg(phase), legF: leg(phase + Math.PI), armN: arm(phase + Math.PI, true), armF: arm(phase, false), phase, raise };
}
const dir = (a) => [Math.sin(a), Math.cos(a)];
const add = (p, a, l) => [p[0] + Math.sin(a) * l, p[1] + Math.cos(a) * l];

function skeleton(t, jitter = 0) {
  const P = pose(t);
  const j = (p, k) => jitter ? [p[0] + noise1(k * 13.1 + jitter, 3) * 1.6, p[1] + noise1(k * 7.7 + jitter, 5) * 1.6] : p;
  const hip = P.hip;
  const sh = [hip[0] + Math.sin(P.lean) * L.torso, hip[1] - Math.cos(P.lean) * L.torso];
  const neckTop = [sh[0] + Math.sin(P.lean + 0.15) * L.neck, sh[1] - Math.cos(P.lean + 0.15) * L.neck];
  const legPts = (lg) => { const knee = add(hip, lg.th, L.thigh), ank = add(knee, lg.th - lg.kn, L.shin); const toe = [ank[0] + Math.cos(lg.fa) * L.foot, ank[1] + Math.sin(lg.fa) * L.foot * 0.3 + 6]; return { knee: j(knee, 1), ank: j(ank, 2), toe: j(toe, 3) }; };
  const armPts = (ar) => { const elb = add(sh, ar.ua, L.upper), wr = add(elb, ar.ua + ar.el, L.fore); return { elb: j(elb, 4), wr: j(wr, 5), a: ar.ua + ar.el }; };
  return { P, hip: j(hip, 6), sh: j(sh, 7), neckTop: j(neckTop, 8), ln: legPts(P.legN), lf: legPts(P.legF), an: armPts(P.armN), af: armPts(P.armF) };
}

function taper(ctx, a, b, wa, wb) {
  const dx = b[0] - a[0], dy = b[1] - a[1], len = Math.hypot(dx, dy) || 1, nx = -dy / len, ny = dx / len;
  ctx.moveTo(a[0] + nx * wa / 2, a[1] + ny * wa / 2); ctx.lineTo(b[0] + nx * wb / 2, b[1] + ny * wb / 2);
  ctx.arc(b[0], b[1], wb / 2, Math.atan2(ny, nx), Math.atan2(ny, nx) + Math.PI, true);
  ctx.lineTo(a[0] - nx * wa / 2, a[1] - ny * wa / 2);
  ctx.arc(a[0], a[1], wa / 2, Math.atan2(-ny, -nx), Math.atan2(-ny, -nx) + Math.PI, true);
  ctx.closePath();
}
function bodyParts(sk) {
  // devuelve lista ordenada de partes: {name, path(ctx), fill}
  const { hip, sh, neckTop, ln, lf, an, af, P } = sk;
  const parts = [];
  const limb = (name, pts, ws) => parts.push({ name, segs: true, draw: (ctx, op) => { for (let i = 0; i < pts.length - 1; i++) { ctx.beginPath(); taper(ctx, pts[i], pts[i + 1], ws[i], ws[i + 1]); if (op) op(); } } });
  const foot = (name, ank, toe) => parts.push({ name, draw: (ctx) => { ctx.beginPath(); ctx.moveTo(ank[0] - 22, ank[1] - 18); ctx.lineTo(ank[0] + 10, ank[1] - 22); ctx.quadraticCurveTo(toe[0] + 20, toe[1] - 20, toe[0] + 16, toe[1] + 4); ctx.lineTo(ank[0] - 26, toe[1] + 6); ctx.closePath(); } });
  // lejanas
  limb('armF', [sh, af.elb, af.wr], [54, 44, 34]);
  parts.push({ name: 'handF', draw: (ctx) => { ctx.beginPath(); ctx.ellipse(...add(af.wr, af.a, 22), 17, 25, -af.a, 0, Math.PI * 2); } });
  limb('legF', [hip, lf.knee, lf.ank], [80, 58, 42]);
  foot('footF', lf.ank, lf.toe);
  // torso (chaqueta)
  parts.push({ name: 'torso', draw: (ctx) => {
    const c = Math.cos(P.lean), s = Math.sin(P.lean);
    const T = (x, y) => [hip[0] + x * c - y * s, hip[1] + x * s + y * c];
    const pts = [T(-62, 40), T(66, 40), T(78, -120), T(70, -250), T(52, -335), T(-42, -345), T(-72, -250), T(-78, -110)];
    ctx.beginPath(); ctx.moveTo(...pts[0]);
    for (let i = 1; i < pts.length; i++) { const p = pts[i], q = pts[(i + 1) % pts.length]; ctx.quadraticCurveTo(p[0], p[1], (p[0] + q[0]) / 2, (p[1] + q[1]) / 2); }
    ctx.closePath();
  } });
  limb('neck', [sh, neckTop], [42, 38]);
  // cabeza
  parts.push({ name: 'head', draw: (ctx) => {
    const cx = neckTop[0] + 14, cy = neckTop[1] - 58;
    ctx.beginPath(); ctx.ellipse(cx, cy, 58, 68, 0.12, 0, Math.PI * 2);
    ctx.moveTo(cx + 54, cy - 6); ctx.lineTo(cx + 72, cy + 14); ctx.lineTo(cx + 52, cy + 22); ctx.closePath();
  } });
  parts.push({ name: 'hair', draw: (ctx) => {
    const cx = neckTop[0] + 14, cy = neckTop[1] - 58;
    const sw = Math.sin(P.phase * 2) * 10 * (1 - P.raise);
    ctx.beginPath(); ctx.ellipse(cx - 6, cy - 22, 60, 50, 0.1, Math.PI * 0.95, Math.PI * 2.08);
    ctx.quadraticCurveTo(cx - 20, cy - 4, cx - 58, cy + 12); ctx.closePath();
    ctx.moveTo(cx - 52, cy - 10); ctx.quadraticCurveTo(cx - 118 + sw, cy + 10, cx - 104 + sw, cy + 84); ctx.quadraticCurveTo(cx - 88 + sw, cy + 30, cx - 44, cy + 6); ctx.closePath();
  } });
  // cercanas
  limb('legN', [hip, ln.knee, ln.ank], [86, 60, 44]);
  foot('footN', ln.ank, ln.toe);
  limb('armN', [sh, an.elb, an.wr], [58, 46, 36]);
  parts.push({ name: 'handN', draw: (ctx) => {
    const c = add(an.wr, an.a, 22);
    ctx.beginPath(); ctx.ellipse(c[0], c[1], 19, 27, -an.a, 0, Math.PI * 2);
  } });
  return parts;
}
export function palmPoint(t) { const sk = skeleton(t); const c = add(sk.an.wr, sk.an.a, 26); return [c[0] + 6, c[1] - 30]; }

const FILL = { armF: '#D9D8D2', handF: '#F4EFE8', legF: '#6A6A74', footF: '#1A1A20', torso: C.MAG, neck: '#F4EFE8', head: '#F4EFE8', hair: '#1A1A20', legN: '#8A8A94', footN: '#1A1A20', armN: C.MAG, handN: '#F4EFE8' };
const FILL_F = { armF: '#B01263' };

let BUF = null;
function drawPersonReal(ctx, t) {
  const sk = skeleton(t), parts = bodyParts(sk);
  const B = BUF || (BUF = { a: makeCanvas(), b: makeCanvas() });
  const a = B.a.getContext('2d'), b = B.b.getContext('2d');
  a.setTransform(1, 0, 0, 1, 0, 0); a.clearRect(0, 0, W, H); a.globalCompositeOperation = 'source-over';
  a.fillStyle = '#0F1015'; parts.forEach(p => { p.draw(a, () => a.fill()); if (!p.segs) a.fill(); });
  // volumen suave
  a.globalCompositeOperation = 'source-atop';
  const g = a.createLinearGradient(sk.hip[0] - 120, 0, sk.hip[0] + 120, 0); g.addColorStop(0, 'rgba(120,80,90,0.28)'); g.addColorStop(0.5, 'rgba(0,0,0,0)'); g.addColorStop(1, 'rgba(0,0,0,0.2)');
  a.fillStyle = g; a.fillRect(0, 0, W, H);
  // luz de recorte (contraluz del amanecer, por la izquierda-arriba)
  b.setTransform(1, 0, 0, 1, 0, 0); b.clearRect(0, 0, W, H); b.globalCompositeOperation = 'source-over';
  b.fillStyle = '#FFD2B0'; parts.forEach(p => { p.draw(b, () => b.fill()); if (!p.segs) b.fill(); });
  b.globalCompositeOperation = 'destination-out'; b.translate(6, 4); parts.forEach(p => { p.draw(b, () => b.fill()); if (!p.segs) b.fill(); }); b.setTransform(1, 0, 0, 1, 0, 0);
  a.globalCompositeOperation = 'source-atop'; a.globalAlpha = 0.85; a.filter = 'blur(1.5px)'; a.drawImage(B.b, 0, 0); a.filter = 'none'; a.globalAlpha = 1;
  a.globalCompositeOperation = 'source-over';
  // sombra en el suelo
  ctx.save(); ctx.globalAlpha = 0.5; const sg = ctx.createRadialGradient(sk.hip[0], 1750, 0, sk.hip[0], 1750, 160); sg.addColorStop(0, 'rgba(0,0,0,0.8)'); sg.addColorStop(1, 'rgba(0,0,0,0)'); ctx.fillStyle = sg; ctx.save(); ctx.translate(0, 1750); ctx.scale(1, 0.18); ctx.translate(0, -1750); ctx.fillRect(sk.hip[0] - 160, 1590, 320, 320); ctx.restore(); ctx.restore();
  ctx.save(); ctx.filter = 'blur(0.6px)'; ctx.drawImage(B.a, 0, 0); ctx.restore();
}
const GROUPS = [['armF', 'handF'], ['legF', 'footF'], ['torso', 'neck', 'head', 'hair'], ['legN', 'footN'], ['armN', 'handN']];
function drawPersonDrawn(ctx, t, { lineA = 1, fillA = 1 } = {}) {
  const boil = Math.floor(t * 12);
  const sk = skeleton(t, boil * 1.7), parts = bodyParts(sk);
  const byName = Object.fromEntries(parts.map(p => [p.name, p]));
  ctx.save(); ctx.lineJoin = 'round';
  for (const g of GROUPS) {
    ctx.globalAlpha = lineA; ctx.strokeStyle = '#16161C'; ctx.lineWidth = 10 + noise1(boil * 0.7 + g.length, 2) * 1.2;
    for (const n of g) { const p = byName[n]; p.draw(ctx, () => ctx.stroke()); if (!p.segs) ctx.stroke(); }
    ctx.globalAlpha = fillA;
    for (const n of g) { const p = byName[n]; ctx.fillStyle = FILL_F[n] || FILL[n]; p.draw(ctx, () => ctx.fill()); if (!p.segs) ctx.fill(); }
  }
  const { sh, hip, neckTop } = sk;
  ctx.globalAlpha = lineA; ctx.strokeStyle = '#16161C'; ctx.lineWidth = 3.5; ctx.lineCap = 'round';
  ctx.beginPath(); ctx.moveTo(sh[0] - 30, sh[1] + 10); ctx.lineTo(sh[0] + 10, sh[1] + 60); ctx.lineTo(sh[0] + 46, sh[1] + 4); ctx.stroke();
  ctx.beginPath(); ctx.moveTo(sh[0] + 30, sh[1] + 70); ctx.lineTo(hip[0] + 52, hip[1] + 30); ctx.stroke();
  ctx.fillStyle = '#16161C'; ctx.beginPath(); ctx.arc(neckTop[0] + 46, neckTop[1] - 72, 5, 0, Math.PI * 2); ctx.fill();
  ctx.restore();
}

// Frontera real → ilustrado (sube desde los pies siguiendo la tinta)
function boundaryY(t) {
  if (t < 14.25) return lerp(H + 60, 1265, seg(t, 13.7, 14.25, E.inOutQuad));
  if (t < 14.85) return lerp(1265, 1150, seg(t, 14.25, 14.85, (x) => x));
  return lerp(1150, -140, seg(t, 14.85, 15.55, E.inOutCubic));
}
function boundaryPath(ctx, t, below = true) {
  const yb = boundaryY(t);
  ctx.beginPath();
  for (let x = -10; x <= W + 10; x += 8) { const y = yb + 26 * Math.sin(x * 0.011 + t * 5) + 18 * fbm1(x * 0.02 + t * 2, 4); x === -10 ? ctx.moveTo(x, y) : ctx.lineTo(x, y); }
  if (below) { ctx.lineTo(W + 10, H + 10); ctx.lineTo(-10, H + 10); ctx.closePath(); }
}

// ---------- Escena 05 ----------
export const scene05 = {
  name: '05 PERSONA REAL → ILUSTRACIÓN', start: 13.0, end: 16.0,
  draw(ctx, t) {
    const drive = (t - 11) * 1.2;
    landscape(ctx, t, { style: 'real', drive, routeP: 1 });
    drawPersonReal(ctx, t);
    const yb = boundaryY(t);
    if (yb < H + 40) {
      ctx.save(); boundaryPath(ctx, t, true); ctx.clip();
      landscape(ctx, t, { style: 'drawn', drive, routeP: 1 });
      drawPersonDrawn(ctx, t);
      ctx.restore();
      // línea de tinta en la frontera
      ctx.save(); boundaryPath(ctx, t, false);
      ctx.strokeStyle = C.MAG; ctx.lineWidth = 7; ctx.shadowColor = C.MAG; ctx.shadowBlur = 26; ctx.stroke();
      ctx.lineWidth = 2; ctx.strokeStyle = '#FFD0E6'; ctx.shadowBlur = 0; ctx.stroke();
      ctx.restore();
      // chispas de tinta
      const rnd = mulberry32(Math.floor(t * 30));
      ctx.fillStyle = C.MAG;
      for (let i = 0; i < 26; i++) { const x = rnd() * W, y = yb + 26 * Math.sin(x * 0.011 + t * 5) - rnd() * 60; ctx.globalAlpha = rnd(); ctx.beginPath(); ctx.arc(x, y, 2 + rnd() * 4, 0, Math.PI * 2); ctx.fill(); }
      ctx.globalAlpha = 1;
    }
    // callout
    const sk = skeleton(t);
    callout(ctx, { ax: sk.neckTop[0] + 20, ay: sk.neckTop[1] - 70, tx: 80, ty: 470, text: 'UNA PERSONA.', fig: 'FIG. 05 — IMAGEN REAL + 2D', p: inv(13.9, 14.6, t), out: inv(15.6, 15.95, t), color: yb < 470 ? '#16161C' : C.OFF });
  },
};

// ---------- Escena 06: colapso de líneas → gota → silencio ----------
function ridgePts() { const a = []; for (let x = -10; x <= W + 10; x += 36) a.push([x, ridgeY(x)]); return a; }
function routePts() {
  const roadTop = ridgeY(VP.x) + 30, a = [];
  for (let i = 0; i <= 16; i++) { const u = i / 16; a.push([lerp(VP.x, ROUTE_END[0], u) + Math.sin(u * 3) * 20 * u, lerp(roadTop, ROUTE_END[1], u * u * 0.6 + u * 0.4)]); }
  return a;
}
function camPush(t) {
  // empuje final hacia la gota: la gota va al centro y crece hasta el tamaño del congelado
  const k = seg(t, 17.15, 18.0, E.inOutCubic);
  const palm = palmPoint(16.0);
  const dropC = [palm[0], palm[1] - 50];
  const s = lerp(1, FREEZE.r / 40, k);
  return { k, s, from: dropC, to: [FREEZE.x, FREEZE.y + 40 * (1 - k)] };
}
export const scene06 = {
  name: '06 COLAPSO → GOTA → SILENCIO', start: 16.0, end: 18.6,
  draw(ctx, t) {
    const tf = Math.min(t, 18.0); // 18,0–18,6: congelado
    const simplify = seg(tf, 16.05, 16.9);
    const cam = camPush(tf);
    ctx.save();
    // fondo papel → gris neutro
    ctx.fillStyle = C.PAPER; ctx.fillRect(0, 0, W, H);
    const cx = lerp(cam.from[0], cam.to[0], cam.k), cy = lerp(cam.from[1], cam.to[1], cam.k);
    ctx.translate(cx, cy); ctx.scale(cam.s, cam.s); ctx.translate(-cam.from[0], -cam.from[1]);
    // mundo ilustrado sin las líneas magenta (que ahora viajan)
    if (simplify < 1) {
      ctx.save(); ctx.globalAlpha = 1;
      landscape(ctx, tf, { style: 'drawn', drive: (16 - 11) * 1.2, routeP: 0, glow: 0, simplify, noHorizon: true });
      ctx.restore();
    }
    // ríos de tinta hacia la palma
    const palm = palmPoint(16.0);
    const target = [palm[0], palm[1] - 50];
    const src = [...ridgePts(), ...routePts()];
    const startT = (p, i) => 16.0 + 0.15 * ((i * 37) % 11) / 11 + Math.hypot(p[0] - target[0], p[1] - target[1]) / 2600;
    // tramos de la cresta que aún no han salido
    ctx.save(); ctx.strokeStyle = C.MAG; ctx.lineWidth = 4; ctx.lineCap = 'round';
    const rp = ridgePts();
    for (let i = 0; i < rp.length - 1; i++) { if (tf >= startT(rp[i], i) || tf >= startT(rp[i + 1], i + 1)) continue; ctx.beginPath(); ctx.moveTo(...rp[i]); ctx.lineTo(...rp[i + 1]); ctx.stroke(); }
    const ro = routePts(), off = rp.length;
    for (let i = 0; i < ro.length - 1; i++) { if (tf >= startT(ro[i], off + i) || tf >= startT(ro[i + 1], off + i + 1)) continue; ctx.lineWidth = 3 + 8 * i / ro.length; ctx.beginPath(); ctx.moveTo(...ro[i]); ctx.lineTo(...ro[i + 1]); ctx.stroke(); }
    ctx.restore();
    // la persona se desvanece línea a línea
    const pf = seg(tf, 16.7, 17.35);
    if (pf < 1) drawPersonDrawn(ctx, 16.0 + (tf - 16.0) * 0.15, { lineA: 1 - pf, fillA: 1 - pf });
    let arrived = 0;
    ctx.save(); ctx.lineCap = 'round'; ctx.strokeStyle = C.MAG; ctx.shadowColor = C.MAG; ctx.shadowBlur = 14;
    src.forEach((p, i) => {
      const st = startT(p, i);
      const u = clamp((tf - st) / 0.7);
      if (u <= 0) return;
      if (u >= 1) { arrived++; return; }
      const ctrl = [lerp(p[0], target[0], 0.5), Math.min(p[1], target[1]) - 120 - 0.25 * Math.abs(p[0] - target[0])];
      const bz = (v) => { const e = E.inOutCubic(v); return [(1 - e) ** 2 * p[0] + 2 * (1 - e) * e * ctrl[0] + e * e * target[0], (1 - e) ** 2 * p[1] + 2 * (1 - e) * e * ctrl[1] + e * e * target[1]]; };
      ctx.lineWidth = 3;
      ctx.beginPath();
      const tail = Math.max(0, u - 0.18);
      for (let k = 0; k <= 8; k++) { const q = bz(lerp(tail, u, k / 8)); k ? ctx.lineTo(q[0], q[1]) : ctx.moveTo(q[0], q[1]); }
      ctx.stroke();
    });
    ctx.restore();
    // la gota se forma
    const fr = arrived / src.length;
    const r = 40 * E.outBack(clamp(fr * 1.15), 1.8);
    const wob = Math.sin(tf * 22) * 0.06 * (1 - seg(tf, 17.2, 17.9));
    if (r > 0.5) drawDrop(ctx, target[0], target[1], r, { squash: 1 + wob, glow: 0.5 });
    ctx.restore();
    // fondo neutro en el congelado (sin elementos)
  },
};
