// ESCENA 03 · 8,95–10,5 s · La molécula aplanada se convierte en una interfaz: nodos → grafo, puntos de datos, tarjetas.
import { W, H, C, FONT_HEAD, FONT_MONO, clamp, lerp, inv, seg, E, smooth, hexA, callout, mulberry32 } from '../lib.js';
import { MOL_SCREEN } from './s02_machine.js';

// Posición final (pantalla) de cada átomo → nodo. Índices = átomos de la molécula.
// Tipos: 0,3,12 magenta · 6,8,10 oscuros · resto blanco roto.
export const NODES2D = [
  { p: [720, 560], r: 20 }, { p: [540, 470], r: 15 }, { p: [540, 640], r: 15 }, { p: [880, 600], r: 20 }, { p: [720, 720], r: 15 }, { p: [540, 790], r: 15 },
  { p: [360, 430], r: 12 }, { p: [190, 470], r: 15 }, { p: [360, 600], r: 12 }, { p: [190, 620], r: 15 }, { p: [360, 770], r: 12 }, { p: [190, 770], r: 15 },
  { p: [880, 440], r: 20 }, { p: [190, 380], r: 15 },
];
const KIND = ['M', 'W', 'W', 'M', 'W', 'W', 'D', 'W', 'D', 'W', 'D', 'W', 'M', 'W'];
// Conexiones del grafo de flujo (izquierda compleja → derecha clara)
const EDGES = [[13, 6], [7, 6], [7, 8], [9, 8], [9, 10], [11, 10], [6, 1], [6, 2], [8, 1], [8, 2], [8, 5], [10, 2], [10, 5], [1, 0], [2, 0], [2, 4], [5, 4], [0, 12], [0, 3], [4, 3]];

// Gráfica
export const CHART = { x0: 130, x1: 950, y0: 1010, y1: 1230, vals: [0.2, 0.34, 0.28, 0.47, 0.4, 0.62, 0.55, 0.78, 0.72, 0.9] };
export function chartPt(i) { const { x0, x1, y0, y1, vals } = CHART; return [x0 + (i / (vals.length - 1)) * (x1 - x0), y1 - vals[i] * (y1 - y0)]; }
// Catmull-Rom en coordenadas de pantalla → función y(x)
export function chartY(x) {
  const { x0, x1, vals } = CHART, n = vals.length - 1;
  const u = clamp((x - x0) / (x1 - x0)) * n, i = Math.min(n - 1, Math.floor(u)), f = u - i;
  const p = (k) => chartPt(clamp(k, 0, n))[1];
  const p0 = p(i - 1), p1 = p(i), p2 = p(i + 1), p3 = p(i + 2);
  const f2 = f * f, f3 = f2 * f;
  let y = 0.5 * ((2 * p1) + (-p0 + p2) * f + (2 * p0 - 5 * p1 + 4 * p2 - p3) * f2 + (-p0 + 3 * p1 - 3 * p2 + p3) * f3);
  if (x < x0) y = p(0) + (x - x0) * ((p(1) - p(0)) / ((x1 - x0) / n)) * 0.5;
  if (x > x1) y = p(n) + (x - x1) * ((p(n) - p(n - 1)) / ((x1 - x0) / n)) * 0.3;
  return y;
}
// Qué nodos se convierten en puntos de la gráfica
const TO_CHART = { 0: 5, 3: 7, 12: 9 };

function rrect(ctx, x, y, w, h, r) { ctx.beginPath(); ctx.roundRect(x, y, w, h, r); }
function strokeProgress(ctx, x, y, w, h, r, p) {
  if (p <= 0) return;
  ctx.save(); ctx.setLineDash([(w + h) * 2 * p, 99999]); rrect(ctx, x, y, w, h, r); ctx.stroke(); ctx.restore();
}
function nodeColor(k) { return k === 'M' ? C.MAG : k === 'W' ? '#EFEEEA' : '#4A4B57'; }

/** Dibuja la interfaz completa en el instante t. opts.lineOnly: solo gráfica (para la escena 04). */
export function drawUI(ctx, t, opts = {}) {
  const fadeOthers = opts.fadeOthers ?? 0;
  const A = 1 - fadeOthers;
  ctx.fillStyle = C.NIGHT; ctx.fillRect(0, 0, W, H);
  // retícula de fondo
  const gridA = seg(t, 9.0, 9.5) * A;
  if (gridA > 0) {
    ctx.save(); ctx.globalAlpha = gridA * 0.5; ctx.strokeStyle = 'rgba(255,255,255,0.05)'; ctx.lineWidth = 1;
    for (let x = 0; x <= W; x += 30) { ctx.beginPath(); ctx.moveTo(x + 0.5, 0); ctx.lineTo(x + 0.5, H); ctx.stroke(); }
    for (let y = 0; y <= H; y += 30) { ctx.beginPath(); ctx.moveTo(0, y + 0.5); ctx.lineTo(W, y + 0.5); ctx.stroke(); }
    ctx.restore();
  }
  // --- paneles ---
  ctx.save(); ctx.globalAlpha = A;
  ctx.strokeStyle = 'rgba(242,241,236,0.28)'; ctx.lineWidth = 1.5;
  strokeProgress(ctx, 90, 330, 900, 540, 18, seg(t, 9.0, 9.45, E.outCubic));
  const chartPanel = seg(t, 9.12, 9.6, E.outCubic);
  ctx.save(); ctx.globalAlpha = A * chartPanel * 0.5; ctx.fillStyle = 'rgba(255,255,255,0.03)'; rrect(ctx, 90, 900, 900, 360, 18); ctx.fill(); ctx.restore();
  strokeProgress(ctx, 90, 900, 900, 360, 18, chartPanel);
  // cabecera
  const hd = seg(t, 9.0, 9.4);
  ctx.globalAlpha = A * hd;
  ctx.font = `700 24px ${FONT_MONO}`; ctx.fillStyle = C.OFF; ctx.textBaseline = 'middle';
  const title = 'DIBURAMA ─ MAPA DE LA IDEA';
  ctx.fillText(title.slice(0, Math.round(title.length * seg(t, 9.0, 9.4))), 110, 290);
  ctx.textAlign = 'right'; ctx.fillStyle = C.GREY; ctx.font = `400 22px ${FONT_MONO}`;
  ctx.fillText('v2.7 · EN VIVO', 940, 290);
  ctx.fillStyle = C.MAG; ctx.beginPath(); ctx.arc(962, 290, 7 * (0.7 + 0.3 * Math.sin(t * 12)), 0, Math.PI * 2); ctx.fill();
  ctx.textAlign = 'left';
  // etiquetas de columnas
  ctx.font = `400 19px ${FONT_MONO}`; ctx.fillStyle = C.GREY;
  const lb = seg(t, 9.2, 9.6);
  ctx.globalAlpha = A * lb;
  ctx.fillText('ENTRADA · COMPLEJA', 120, 364); ctx.textAlign = 'right'; ctx.fillText('SALIDA · CLARA', 960, 364); ctx.textAlign = 'left';
  // toggle con cursor
  const tg = seg(t, 9.3, 9.6);
  const on = seg(t, 9.98, 10.12, E.outCubic);
  if (tg > 0) {
    ctx.globalAlpha = A * tg;
    const tx = 800, ty = 820;
    ctx.fillStyle = on > 0.5 ? C.MAG : 'rgba(255,255,255,0.15)';
    rrect(ctx, tx, ty - 18, 76, 36, 18); ctx.fill();
    ctx.fillStyle = C.OFF; ctx.beginPath(); ctx.arc(tx + 18 + 40 * on, ty, 13, 0, Math.PI * 2); ctx.fill();
    ctx.font = `700 20px ${FONT_MONO}`; ctx.fillStyle = on > 0.5 ? C.OFF : C.GREY; ctx.textAlign = 'right';
    ctx.fillText(on > 0.5 ? 'MODO CLARO' : 'MODO COMPLEJO', tx - 16, ty); ctx.textAlign = 'left';
    if (on > 0 && on < 1) { ctx.strokeStyle = hexA(C.MAG, 1 - on); ctx.lineWidth = 3; ctx.beginPath(); ctx.arc(tx + 58, ty, 20 + 50 * on, 0, Math.PI * 2); ctx.stroke(); }
  }
  ctx.restore();

  // --- aristas del grafo ---
  const nodes = NODES2D.map((n, i) => ({ ...n, k: KIND[i] }));
  // posición de nodos: vienen de la molécula 3D; algunos viajan a la gráfica
  const toChart = seg(t, 9.35, 9.85, E.inOutCubic);
  nodes.forEach((n, i) => {
    n.x = n.p[0]; n.y = n.p[1];
    if (TO_CHART[i] !== undefined) { const [cx, cy] = chartPt(TO_CHART[i]); n.x = lerp(n.x, cx, toChart); n.y = lerp(n.y, cy, toChart); n.chart = true; }
  });
  const eg = seg(t, 9.05, 9.6, E.outCubic);
  ctx.save(); ctx.globalAlpha = A;
  EDGES.forEach(([a, b], k) => {
    const d = clamp(eg * 1.6 - k * 0.03);
    if (d <= 0) return;
    const na = nodes[a], nb = nodes[b];
    const pa = [NODES2D[a].p[0], NODES2D[a].p[1]], pb = [NODES2D[b].p[0], NODES2D[b].p[1]];
    const mx = (pa[0] + pb[0]) / 2;
    ctx.strokeStyle = (KIND[b] === 'M' || KIND[a] === 'M') ? hexA(C.MAG, 0.7 * on + 0.3) : 'rgba(242,241,236,0.35)';
    ctx.lineWidth = 2;
    ctx.save(); ctx.setLineDash([600 * d, 9999]);
    ctx.beginPath(); ctx.moveTo(pa[0], pa[1]); ctx.bezierCurveTo(mx, pa[1], mx, pb[1], pb[0], pb[1]); ctx.stroke(); ctx.restore();
    // pulsos de datos viajando
    if (d >= 1 && t > 9.4) {
      const u = ((t * 0.9 + k * 0.137) % 1);
      const bx = (1 - u) ** 3 * pa[0] + 3 * (1 - u) ** 2 * u * mx + 3 * (1 - u) * u * u * mx + u ** 3 * pb[0];
      const by = (1 - u) ** 3 * pa[1] + 3 * (1 - u) ** 2 * u * pa[1] + 3 * (1 - u) * u * u * pb[1] + u ** 3 * pb[1];
      ctx.fillStyle = C.MAG; ctx.beginPath(); ctx.arc(bx, by, 3.5, 0, Math.PI * 2); ctx.fill();
    }
  });
  // huecos que dejan los nodos que se van a la gráfica
  Object.keys(TO_CHART).forEach(i => {
    const n = NODES2D[i]; const a = seg(t, 9.5, 9.8);
    if (a <= 0) return;
    ctx.strokeStyle = hexA(C.MAG, 0.8 * a); ctx.lineWidth = 2; ctx.setLineDash([4, 5]);
    ctx.beginPath(); ctx.arc(n.p[0], n.p[1], n.r + 4, 0, Math.PI * 2); ctx.stroke(); ctx.setLineDash([]);
  });
  ctx.restore();

  // --- gráfica ---
  drawChart(ctx, t, { fadeOthers, lineWidth: opts.lineWidth });

  // --- nodos ---
  ctx.save();
  nodes.forEach((n, i) => {
    if (n.chart && fadeOthers > 0) return;
    ctx.globalAlpha = n.chart ? 1 : A;
    const r = n.chart ? lerp(n.r, 10, toChart) : n.r;
    ctx.fillStyle = nodeColor(n.k);
    ctx.beginPath(); ctx.arc(n.x, n.y, r, 0, Math.PI * 2); ctx.fill();
    if (n.k === 'M') { ctx.strokeStyle = hexA(C.MAG, 0.35); ctx.lineWidth = 2; ctx.beginPath(); ctx.arc(n.x, n.y, r + 8 + 3 * Math.sin(t * 6 + i), 0, Math.PI * 2); ctx.stroke(); }
    // etiqueta mono junto a algunos nodos
    const la = seg(t, 9.4 + i * 0.02, 9.7 + i * 0.02) * A;
    if (!n.chart && la > 0 && [7, 9, 11, 13, 4].includes(i)) {
      ctx.globalAlpha = la; ctx.font = `400 16px ${FONT_MONO}`; ctx.fillStyle = C.GREY; ctx.textBaseline = 'middle';
      const lbls = { 7: 'normativa', 9: 'datos', 11: 'procesos', 13: 'jerga', 4: 'mensaje' };
      ctx.fillText(lbls[i], n.x + n.r + 10, n.y - 20);
    }
  });
  ctx.restore();
  // cursor
  if (A > 0) {
    const cp = seg(t, 9.5, 9.95, E.inOutCubic);
    if (cp > 0) {
      const cx = lerp(1000, 858, cp), cy = lerp(1060, 826, cp);
      const press = t > 9.95 && t < 10.08 ? 0.85 : 1;
      ctx.save(); ctx.globalAlpha = A; ctx.translate(cx, cy); ctx.scale(1.25 * press, 1.25 * press);
      ctx.beginPath(); ctx.moveTo(0, 0); ctx.lineTo(0, 30); ctx.lineTo(8, 23); ctx.lineTo(14, 36); ctx.lineTo(19, 34); ctx.lineTo(13, 21); ctx.lineTo(23, 21); ctx.closePath();
      ctx.fillStyle = C.OFF; ctx.fill(); ctx.strokeStyle = C.NIGHT; ctx.lineWidth = 2; ctx.stroke();
      ctx.restore();
    }
  }
  // callout
  if (!opts.noCallout) callout(ctx, { ax: 90, ay: 1080, tx: 80, ty: 1400, text: 'UN SOFTWARE.', fig: 'FIG. 03 — INTERFAZ / DATOS', p: inv(9.25, 9.95, t), out: Math.max(inv(10.45, 10.7, t), fadeOthers), color: C.OFF });
}

export function drawChart(ctx, t, { fadeOthers = 0, lineWidth = 5 } = {}) {
  const A = 1 - fadeOthers;
  const { x0, x1, y0, y1, vals } = CHART;
  const lp = seg(t, 9.55, 10.25, E.inOutCubic);
  ctx.save();
  // ejes y rejilla
  ctx.globalAlpha = A * seg(t, 9.2, 9.6);
  ctx.strokeStyle = 'rgba(242,241,236,0.12)'; ctx.lineWidth = 1;
  for (let k = 0; k <= 4; k++) { const y = lerp(y1, y0, k / 4); ctx.beginPath(); ctx.moveTo(x0, y); ctx.lineTo(x1, y); ctx.stroke(); }
  // KPIs en la cabecera del panel
  ctx.font = `400 18px ${FONT_MONO}`; ctx.fillStyle = C.GREY; ctx.textBaseline = 'alphabetic';
  ctx.fillText('COMPRENSIÓN / TIEMPO', 120, 944);
  const kp = seg(t, 9.6, 10.3, E.outCubic);
  const kpis = [['COMPLEJIDAD', `−${Math.round(87 * kp)}%`, 530], ['CLARIDAD', `${Math.round(98 * kp)}%`, 760]];
  for (const [l, v, x] of kpis) {
    ctx.fillStyle = C.GREY; ctx.font = `400 16px ${FONT_MONO}`; ctx.fillText(l, x, 944);
    ctx.fillStyle = C.OFF; ctx.font = `700 34px ${FONT_HEAD}`; ctx.fillText(v, x, 984);
  }
  ctx.restore();
  // área + línea
  if (lp > 0) {
    const xe = lerp(x0, x1, lp);
    ctx.save();
    ctx.beginPath(); ctx.moveTo(x0, y1);
    for (let x = x0; x <= xe; x += 4) ctx.lineTo(x, chartY(x));
    ctx.lineTo(xe, y1); ctx.closePath();
    const g = ctx.createLinearGradient(0, y0, 0, y1); g.addColorStop(0, hexA(C.MAG, 0.35 * A)); g.addColorStop(1, hexA(C.MAG, 0));
    ctx.fillStyle = g; ctx.fill();
    ctx.beginPath();
    for (let x = x0; x <= xe; x += 3) x === x0 ? ctx.moveTo(x, chartY(x)) : ctx.lineTo(x, chartY(x));
    ctx.strokeStyle = C.MAG; ctx.lineWidth = lineWidth; ctx.lineJoin = 'round'; ctx.lineCap = 'round';
    ctx.shadowColor = C.MAG; ctx.shadowBlur = 16; ctx.stroke();
    ctx.restore();
    // puntos de datos
    ctx.save(); ctx.globalAlpha = A;
    vals.forEach((v, i) => {
      const [px, py] = chartPt(i); if (px > xe || Object.values(TO_CHART).includes(i)) return;
      ctx.fillStyle = C.NIGHT; ctx.strokeStyle = C.MAG; ctx.lineWidth = 3; ctx.beginPath(); ctx.arc(px, py, 7, 0, Math.PI * 2); ctx.fill(); ctx.stroke();
    });
    ctx.restore();
  }
}

export const scene03 = {
  name: '03 SOFTWARE', start: 8.867, end: 10.5,
  draw(ctx, t) { drawUI(ctx, t); },
};
