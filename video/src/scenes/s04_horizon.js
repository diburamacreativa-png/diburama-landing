// ESCENA 04 · 10,5–13,0 s · Zoom a la gráfica → la línea magenta se convierte en el HORIZONTE de un paisaje.
import { makeCanvas, W, H, C, FONT_MONO, clamp, lerp, inv, seg, E, smooth, fbm1, noise1, hexA, mixHex, callout, mulberry32 } from '../lib.js';
import { drawUI, chartY, CHART } from './s03_software.js';

let LAYER = null;
export const HZ = { y: 900, pivotX: 620, S: 4.2 };
const pivotY = () => chartY(HZ.pivotX);
// Horizonte en pantalla (misma curva que la gráfica, ampliada)
export function ridgeY(x) { return (chartY((x - 540) / HZ.S + HZ.pivotX) - pivotY()) * HZ.S + HZ.y; }
export function backRidgeY(x) { return HZ.y - 70 - 90 * (fbm1(x * 0.0045, 11) * 0.5 + 0.5) - 40 * Math.sin(x * 0.004 + 1); }

const TURBINES = [[150, 0.8], [270, 1], [395, 0.7], [835, 0.9], [965, 1.1]];
const PYLONS = [[-40, 1.5], [230, 1.05], [440, 0.75], [610, 0.55], [745, 0.42]];
export const VP = { x: 600 };
const pylonBase = (x, s) => [x, HZ.y + 40 + 330 * (s - 0.42) / 1.08 + 60 * s];

function sky(ctx, t, a = 1) {
  const g = ctx.createLinearGradient(0, 0, 0, HZ.y + 40);
  g.addColorStop(0, '#0D0E14'); g.addColorStop(0.35, '#1A1A2A'); g.addColorStop(0.62, '#3C2E4A'); g.addColorStop(0.82, '#8C5A6E'); g.addColorStop(0.95, '#E7A488'); g.addColorStop(1, '#F6C9A2');
  ctx.globalAlpha = a; ctx.fillStyle = g; ctx.fillRect(0, 0, W, HZ.y + 60);
  // sol tras la cresta
  const sx = 770, sy = HZ.y - 40;
  let sg = ctx.createRadialGradient(sx, sy, 0, sx, sy, 520);
  sg.addColorStop(0, 'rgba(255,226,196,0.95)'); sg.addColorStop(0.08, 'rgba(255,196,160,0.65)'); sg.addColorStop(0.35, 'rgba(230,120,130,0.18)'); sg.addColorStop(1, 'rgba(230,120,130,0)');
  ctx.fillStyle = sg; ctx.fillRect(0, 0, W, HZ.y + 80);
  // nubes finas
  ctx.globalAlpha = a * 0.35;
  for (let i = 0; i < 7; i++) {
    const y = 420 + i * 55, x0 = ((i * 211 + t * 12) % 1500) - 300;
    const cg = ctx.createLinearGradient(x0, 0, x0 + 700, 0); cg.addColorStop(0, 'rgba(255,190,190,0)'); cg.addColorStop(0.5, `rgba(255,${190 - i * 8},${190 - i * 6},${0.25 - i * 0.02})`); cg.addColorStop(1, 'rgba(255,190,190,0)');
    ctx.fillStyle = cg; ctx.fillRect(x0, y, 700, 5 + i);
  }
  ctx.globalAlpha = 1;
}

function turbine(ctx, x, yb, s, t, style) {
  const h = 150 * s, r = 62 * s;
  const hx = x, hy = yb - h;
  const rot = t * 2.2 + x;
  if (style === 'real') { ctx.strokeStyle = 'rgba(70,52,72,0.95)'; ctx.fillStyle = 'rgba(70,52,72,0.95)'; }
  else { ctx.strokeStyle = '#1A1A20'; ctx.fillStyle = '#1A1A20'; }
  ctx.lineWidth = Math.max(1.5, 4 * s); ctx.lineCap = 'round';
  ctx.beginPath(); ctx.moveTo(x - 2 * s, yb); ctx.lineTo(hx, hy); ctx.lineTo(x + 2 * s, yb); ctx.stroke();
  for (let k = 0; k < 3; k++) { const a = rot + (k * Math.PI * 2) / 3; ctx.lineWidth = Math.max(1.2, 3 * s); ctx.beginPath(); ctx.moveTo(hx, hy); ctx.lineTo(hx + Math.cos(a) * r, hy + Math.sin(a) * r); ctx.stroke(); }
  ctx.beginPath(); ctx.arc(hx, hy, 3.5 * s, 0, Math.PI * 2); ctx.fill();
}
function pylon(ctx, x, yb, s, style) {
  const h = 230 * s, w = 40 * s;
  ctx.lineWidth = Math.max(1.2, 3 * s);
  ctx.strokeStyle = style === 'real' ? 'rgba(18,18,24,0.95)' : '#1A1A20';
  const top = yb - h;
  ctx.beginPath();
  ctx.moveTo(x - w, yb); ctx.lineTo(x - w * 0.25, top); ctx.lineTo(x + w * 0.25, top); ctx.lineTo(x + w, yb);
  for (let k = 0; k < 5; k++) { const y1 = yb - (h * k) / 5, y2 = yb - (h * (k + 1)) / 5; const w1 = lerp(w, w * 0.25, k / 5), w2 = lerp(w, w * 0.25, (k + 1) / 5); ctx.moveTo(x - w1, y1); ctx.lineTo(x + w2, y2); ctx.moveTo(x + w1, y1); ctx.lineTo(x - w2, y2); }
  ctx.moveTo(x - w * 1.5, top + h * 0.12); ctx.lineTo(x + w * 1.5, top + h * 0.12);
  ctx.moveTo(x - w * 1.1, top + h * 0.3); ctx.lineTo(x + w * 1.1, top + h * 0.3);
  ctx.stroke();
  return [[x - w * 1.5, top + h * 0.12], [x + w * 1.5, top + h * 0.12], [x - w * 1.1, top + h * 0.3], [x + w * 1.1, top + h * 0.3]];
}

/** Paisaje completo. style: 'real' (placeholder fotográfico) | 'drawn' (ilustración). drive: avance del dron. */
export function landscape(ctx, t, { style = 'real', drive = 0, routeP = 0, glow = 1, simplify = 0, noHorizon = false } = {}) {
  const real = style === 'real';
  const boil = real ? 0 : Math.floor(t * 12);
  const jit = (x, k = 1) => (real ? 0 : noise1(x * 0.05 + boil * 3.1, 9) * 1.4 * k);
  const lineA = 1 - simplify;
  if (real) sky(ctx, t);
  else { ctx.fillStyle = '#EEEDE8'; ctx.fillRect(0, 0, W, H); }
  // cresta trasera
  if (real) {
    ctx.beginPath(); ctx.moveTo(0, H); for (let x = 0; x <= W; x += 6) ctx.lineTo(x, backRidgeY(x)); ctx.lineTo(W, H); ctx.closePath();
    const bg = ctx.createLinearGradient(0, HZ.y - 200, 0, HZ.y); bg.addColorStop(0, '#5B4058'); bg.addColorStop(1, '#6E4C62'); ctx.fillStyle = bg; ctx.fill();
  } else if (lineA > 0) {
    ctx.save(); ctx.globalAlpha = lineA; ctx.strokeStyle = '#1A1A20'; ctx.lineWidth = 2;
    ctx.beginPath(); for (let x = 0; x <= W; x += 8) { const y = backRidgeY(x) + jit(x); x ? ctx.lineTo(x, y) : ctx.moveTo(x, y); } ctx.stroke();
    // sol en línea
    ctx.beginPath(); ctx.arc(770, HZ.y - 40, 70 + jit(1), Math.PI, Math.PI * 2 + 0.0); ctx.stroke();
    for (let i = 0; i < 5; i++) { ctx.beginPath(); ctx.moveTo(60 + i * 30, 380 + i * 34); ctx.lineTo(360 + i * 40, 380 + i * 34 + jit(i, 2)); ctx.globalAlpha = lineA * 0.35; ctx.stroke(); }
    ctx.restore();
  }
  // aerogeneradores en la cresta trasera
  ctx.save(); ctx.globalAlpha = real ? 1 : lineA;
  TURBINES.forEach(([x, s]) => turbine(ctx, x, backRidgeY(x) + 6, s, t, style));
  ctx.restore();
  // tierra (cresta delantera = línea de la gráfica)
  ctx.beginPath(); ctx.moveTo(-10, H); for (let x = -10; x <= W + 10; x += 5) ctx.lineTo(x, ridgeY(x)); ctx.lineTo(W + 10, H); ctx.closePath();
  if (real) {
    const gg = ctx.createLinearGradient(0, HZ.y - 60, 0, H); gg.addColorStop(0, '#2A2130'); gg.addColorStop(0.18, '#15151C'); gg.addColorStop(1, '#0B0B10');
    ctx.fillStyle = gg; ctx.fill();
  } else { ctx.fillStyle = '#EEEDE8'; ctx.fill(); }
  // bruma en el horizonte
  if (real) { const hz = ctx.createLinearGradient(0, HZ.y - 120, 0, HZ.y + 140); hz.addColorStop(0, 'rgba(240,170,150,0)'); hz.addColorStop(0.5, 'rgba(240,170,150,0.16)'); hz.addColorStop(1, 'rgba(240,170,150,0)'); ctx.fillStyle = hz; ctx.fillRect(0, HZ.y - 120, W, 260); }
  // rejilla del suelo (hereda la rejilla de la gráfica)
  ctx.save();
  ctx.beginPath(); ctx.moveTo(-10, H); for (let x = -10; x <= W + 10; x += 5) ctx.lineTo(x, ridgeY(x) + 2); ctx.lineTo(W + 10, H); ctx.closePath(); ctx.clip();
  ctx.strokeStyle = real ? 'rgba(242,241,236,0.06)' : 'rgba(26,26,32,0.12)'; ctx.lineWidth = 1.5;
  ctx.globalAlpha = lineA;
  for (let k = 0; k < 14; k++) { const z = ((k + (drive % 1)) ); const y = HZ.y + 40 + 900 / Math.max(0.2, 12 - z) * 1.1; if (y > H) continue; ctx.beginPath(); ctx.moveTo(0, y); ctx.lineTo(W, y); ctx.stroke(); }
  for (let k = -8; k <= 8; k++) { ctx.beginPath(); ctx.moveTo(VP.x + k * 18, HZ.y + 40); ctx.lineTo(VP.x + k * 260, H + 200); ctx.stroke(); }
  ctx.restore();
  // luces de ciudad
  const rnd = mulberry32(31);
  ctx.save(); ctx.globalAlpha = real ? 1 : 0;
  for (let i = 0; i < 90; i++) {
    const x = 60 + rnd() * 420, y = ridgeY(x) + 8 + rnd() * 26 * (1 - (x - 60) / 520);
    const tw = 0.6 + 0.4 * Math.sin(t * (3 + rnd() * 4) + i);
    ctx.fillStyle = `rgba(255,${200 + rnd() * 40},${150 + rnd() * 60},${0.55 * tw})`; ctx.fillRect(x, y, 2 + rnd() * 2, 2);
  }
  ctx.restore();
  // carretera
  const roadTop = ridgeY(VP.x) + 30;
  ctx.save(); ctx.globalAlpha = real ? 1 : lineA;
  ctx.beginPath(); ctx.moveTo(VP.x - 6, roadTop); ctx.lineTo(VP.x + 6, roadTop); ctx.lineTo(VP.x + 230, H); ctx.lineTo(VP.x - 380, H); ctx.closePath();
  if (real) { const rg = ctx.createLinearGradient(0, roadTop, 0, H); rg.addColorStop(0, '#3A2C3A'); rg.addColorStop(1, '#1C1C24'); ctx.fillStyle = rg; ctx.fill(); }
  else { ctx.strokeStyle = '#1A1A20'; ctx.lineWidth = 3; ctx.beginPath(); ctx.moveTo(VP.x - 6, roadTop + jit(2)); ctx.lineTo(VP.x - 380, H); ctx.moveTo(VP.x + 6, roadTop); ctx.lineTo(VP.x + 230 + jit(4), H); ctx.stroke(); }
  // marcas viales
  ctx.strokeStyle = real ? 'rgba(242,241,236,0.35)' : 'rgba(26,26,32,0.6)'; ctx.lineWidth = 3;
  for (let k = 0; k < 12; k++) { const u = ((k + drive * 1.6) % 12) / 12; const u2 = u + 0.025; const p = (u) => [lerp(VP.x, VP.x - 70, u * u), lerp(roadTop, H, u * u)]; const a = p(u), b = p(Math.min(1, u2)); ctx.lineWidth = 1 + 6 * u * u; ctx.beginPath(); ctx.moveTo(a[0], a[1]); ctx.lineTo(b[0], b[1]); ctx.stroke(); }
  // tráfico: faros
  if (real) {
    for (let k = 0; k < 9; k++) {
      const dir = k % 2 ? 1 : -1; let u = ((k * 0.137 + t * (0.09 + 0.02 * (k % 3)) * (dir > 0 ? 1 : -0.7)) % 1 + 1) % 1; u = u * u;
      const lane = dir > 0 ? -0.45 : 0.25; const x = lerp(VP.x, VP.x + lane * 400, u), y = lerp(roadTop, H, u), s = 1 + 12 * u;
      const col = dir > 0 ? 'rgba(255,238,215,' : 'rgba(255,150,90,';
      const rr = 3.2 * s; const g = ctx.createRadialGradient(x, y, 0, x, y, rr); g.addColorStop(0, col + '0.95)'); g.addColorStop(0.35, col + '0.5)'); g.addColorStop(1, col + '0)'); ctx.fillStyle = g; ctx.fillRect(x - rr, y - rr, rr * 2, rr * 2);
    }
  }
  ctx.restore();
  // torres eléctricas + cables (la "red")
  ctx.save(); ctx.globalAlpha = real ? 1 : lineA;
  let prev = null;
  const tops = [];
  PYLONS.forEach(([x, s]) => { const [bx, by] = pylonBase(x, s); tops.push(pylon(ctx, bx, by, s, style)); });
  ctx.strokeStyle = real ? 'rgba(20,20,26,0.8)' : '#1A1A20'; ctx.lineWidth = 1.4;
  for (let i = 0; i < tops.length - 1; i++) for (let c = 0; c < 4; c++) {
    const [x1, y1] = tops[i][c], [x2, y2] = tops[i + 1][c];
    ctx.beginPath(); ctx.moveTo(x1, y1); ctx.quadraticCurveTo((x1 + x2) / 2, Math.max(y1, y2) + 40 * PYLONS[i][1], x2, y2); ctx.stroke();
  }
  ctx.restore();
  // horizonte magenta (la línea de la gráfica)
  if (!noHorizon) {
  ctx.save();
  ctx.beginPath(); for (let x = -10; x <= W + 10; x += 4) { const y = ridgeY(x) + (real ? 0 : jit(x, 0.6)); x > -10 ? ctx.lineTo(x, y) : ctx.moveTo(x, y); }
  ctx.strokeStyle = C.MAG; ctx.lineWidth = real ? 3.5 : 4; ctx.lineJoin = 'round';
  if (glow > 0) { ctx.shadowColor = C.MAG; ctx.shadowBlur = 22 * glow; }
  ctx.stroke(); ctx.restore();
  }
  // ruta magenta por la carretera hacia cámara
  if (routeP > 0) {
    ctx.save(); ctx.strokeStyle = C.MAG; ctx.lineCap = 'round'; ctx.shadowColor = C.MAG; ctx.shadowBlur = 18;
    const N = 60; const n = Math.round(N * routeP);
    for (let i = 0; i < n; i++) {
      const u0 = i / N, u1 = (i + 1) / N;
      const p = (u) => [lerp(VP.x, ROUTE_END[0], u) + Math.sin(u * 3) * 20 * u, lerp(roadTop, ROUTE_END[1], u * u * 0.6 + u * 0.4)];
      const a = p(u0), b = p(u1); ctx.lineWidth = 2 + 10 * u1;
      ctx.beginPath(); ctx.moveTo(a[0], a[1]); ctx.lineTo(b[0], b[1]); ctx.stroke();
    }
    ctx.restore();
  }
  return { tops, roadTop };
}
export const ROUTE_END = [520, 1740];

function drawZoom(ctx, t) {
  // 10,5–11,6: zoom a la gráfica, la interfaz desaparece
  const k = seg(t, 10.5, 11.5, E.inOutCubic);
  const S = lerp(1, HZ.S, k);
  const px = HZ.pivotX, py = pivotY();
  const tx = lerp(px, 540, k), ty = lerp(py, HZ.y, k);
  const fade = seg(t, 10.5, 10.95);
  ctx.save();
  ctx.translate(tx, ty); ctx.scale(S, S); ctx.translate(-px, -py);
  drawUI(ctx, Math.min(t, 10.49), { fadeOthers: fade, lineWidth: lerp(5, 3.6, k) / S * (1 + 0.3 * k), noCallout: true });
  ctx.restore();
}

export const scene04 = {
  name: '04 GRÁFICA → HORIZONTE', start: 10.5, end: 13.0,
  draw(ctx, t) {
    const land = seg(t, 11.15, 11.85, E.inOutCubic);
    if (land < 1) drawZoom(ctx, t);
    if (land > 0) {
      // el paisaje nace desde la línea: máscara suave que se abre desde el horizonte
      const L = LAYER || (LAYER = makeCanvas()), lc = L.getContext('2d');
      lc.setTransform(1, 0, 0, 1, 0, 0); lc.globalCompositeOperation = 'source-over'; lc.clearRect(0, 0, W, H);
      const dz = 1 + 0.05 * seg(t, 11.4, 13.0, (x) => x);
      lc.save(); lc.translate(540, HZ.y); lc.scale(dz, dz); lc.translate(-540, -HZ.y);
      landscape(lc, t, { style: 'real', drive: (t - 11) * 1.2, routeP: seg(t, 12.15, 13.0, E.inOutCubic) });
      lc.restore();
      if (land < 1) {
        const up = (HZ.y + 200) * land, dn = (H - HZ.y + 200) * land;
        const g = lc.createLinearGradient(0, HZ.y - up, 0, HZ.y + dn);
        const a = HZ.y - up, b = HZ.y + dn, span = b - a;
        g.addColorStop(0, 'rgba(0,0,0,0)'); g.addColorStop(clamp(160 / span), 'rgba(0,0,0,1)'); g.addColorStop(1 - clamp(160 / span), 'rgba(0,0,0,1)'); g.addColorStop(1, 'rgba(0,0,0,0)');
        lc.globalCompositeOperation = 'destination-in'; lc.fillStyle = g; lc.fillRect(0, 0, W, H);
      }
      ctx.drawImage(L, 0, 0);
      // callout anclado a la torre
      const [bx, by] = pylonBase(PYLONS[2][0], PYLONS[2][1]);
      const ax = 540 + (bx - 540) * dz, ay = HZ.y + (by - 230 * PYLONS[2][1] - HZ.y) * dz;
      callout(ctx, { ax, ay, tx: 80, ty: 1400, text: 'UNA RED.', fig: 'FIG. 04 — ENERGÍA · LOGÍSTICA', p: inv(11.75, 12.4, t), out: inv(12.8, 13.0, t), color: C.OFF });
    }
  },
};
