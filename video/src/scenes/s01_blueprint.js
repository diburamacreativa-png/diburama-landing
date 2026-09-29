// ESCENA 01 · 0,0–3,0 s · Plano técnico gris → cae la gota → ES → ERA → la tinta viaja por las líneas.
import { W, H, C, FONT_HEAD, FONT_MONO, clamp, lerp, inv, seg, E, smooth, mulberry32, fbm1, noise1, hexA, makeCanvas, drawDrop } from '../lib.js';

// ---------- Geometría compartida de la máquina (se reutiliza en la escena 3D) ----------
export const MACHINE = {
  cx: 540, axisY: 640, len: 586,
  // perfil (s a lo largo del eje, r radio). Pieza a pieza.
  parts: [
    { id: 'flange', s0: 0, s1: 34, r: 170 },
    { id: 'housing', s0: 34, s1: 300, r: 118, fins: [70, 118, 166, 214, 262], finR: 134, finW: 12, bore: 96 },
    { id: 'cover', s0: 300, s1: 332, r: 138 },
    { id: 'hub', s0: 332, s1: 392, r: 78 },
    { id: 'shaft', s0: 392, s1: 540, r: 30 },
    { id: 'nut', s0: 540, s1: 586, r: 52, hex: true },
  ],
};
export const machineX = (s) => MACHINE.cx - MACHINE.len / 2 + s;

// ---------- Construcción procedural del plano ----------
const SHEET_TOP = -2400, SHEET_BOTTOM = 1900;
const OX = 300, OY = -SHEET_TOP + 40; // desplazamiento del lienzo horneado
function build() {
  const rnd = mulberry32(412);
  const lines = []; // {pts, kind, w, dash, part}
  const texts = []; // {x,y,s,size,font,align,rot,color}
  const L = (pts, kind = 'main', extra = {}) => lines.push({ pts, kind, ...extra });
  const T = (x, y, s, size = 20, extra = {}) => texts.push({ x, y, s, size, font: FONT_MONO, align: 'left', ...extra });
  const rect = (x0, y0, x1, y1, kind = 'frame', extra) => L([[x0, y0], [x1, y0], [x1, y1], [x0, y1], [x0, y0]], kind, extra);
  const circle = (cx, cy, r, kind = 'thin', n = 64, extra = {}) => {
    const pts = []; for (let i = 0; i <= n; i++) { const a = (i / n) * Math.PI * 2; pts.push([cx + Math.cos(a) * r, cy + Math.sin(a) * r]); }
    L(pts, kind, extra);
  };

  // Marco de hoja
  rect(40, SHEET_TOP + 30, 1040, SHEET_BOTTOM - 30, 'frame');
  for (let y = SHEET_TOP + 30; y < SHEET_BOTTOM - 30; y += 240) { L([[40, y], [26, y]], 'thin'); }

  // --- Alzado en semi-sección de la máquina ---
  const ay = MACHINE.axisY;
  const prof = []; // perfil superior (s, r)
  const P = MACHINE.parts;
  prof.push([0, 0]);
  for (const p of P) {
    if (p.fins) {
      prof.push([p.s0, p.r]);
      for (const f of p.fins) { prof.push([f - p.finW / 2, p.r], [f - p.finW / 2, p.finR], [f + p.finW / 2, p.finR], [f + p.finW / 2, p.r]); }
      prof.push([p.s1, p.r]);
    } else { prof.push([p.s0, p.r], [p.s1, p.r]); }
  }
  prof.push([MACHINE.len, 0]);
  const up = prof.map(([s, r]) => [machineX(s), ay - r]);
  const dn = prof.map(([s, r]) => [machineX(s), ay + r]);
  L(up, 'main', { part: true }); L(dn, 'main', { part: true });
  // aristas verticales de cada escalón
  for (let i = 0; i < P.length; i++) {
    const p = P[i];
    L([[machineX(p.s0), ay - p.r], [machineX(p.s0), ay + p.r]], 'main', { part: true });
    if (p.hex) { L([[machineX(p.s0), ay - p.r * 0.5], [machineX(p.s1), ay - p.r * 0.5]], 'main', { part: true }); L([[machineX(p.s0), ay + p.r * 0.5], [machineX(p.s1), ay + p.r * 0.5]], 'main', { part: true }); }
    if (p.fins) for (const f of p.fins) { L([[machineX(f - p.finW / 2), ay + p.r], [machineX(f - p.finW / 2), ay - p.r]], 'thin', { part: true }); }
  }
  // eje
  L([[machineX(-50), ay], [machineX(MACHINE.len + 50), ay]], 'axis', { dash: [26, 6, 4, 6] });
  // taladro interior (oculto) y rayado de sección en la mitad superior
  const hatch = (x0, x1, yTop, yBot) => {
    const step = 11;
    for (let k = -(yBot - yTop); k < x1 - x0; k += step) {
      let xa = x0 + k, ya = yBot, xb = x0 + k + (yBot - yTop), yb = yTop;
      // recorte al rectángulo
      if (xa < x0) { ya -= (x0 - xa); xa = x0; }
      if (xb > x1) { yb += (xb - x1); xb = x1; }
      if (ya > yTop && yb < yBot && xb > xa) L([[xa, ya], [xb, yb]], 'hatch', { part: true });
    }
  };
  const hs = P[1];
  hatch(machineX(hs.s0), machineX(hs.s1), ay - hs.r, ay - hs.bore);
  hatch(machineX(P[0].s0), machineX(P[0].s1), ay - P[0].r, ay - 30);
  hatch(machineX(P[2].s0), machineX(P[2].s1), ay - P[2].r, ay - 30);
  hatch(machineX(P[3].s0), machineX(P[3].s1), ay - P[3].r, ay - 30);
  L([[machineX(hs.s0), ay - hs.bore], [machineX(hs.s1), ay - hs.bore]], 'main', { part: true });
  L([[machineX(hs.s0), ay + hs.bore], [machineX(hs.s1), ay + hs.bore]], 'thin', { dash: [10, 7], part: true });
  L([[machineX(0), ay - 30], [machineX(392), ay - 30]], 'main', { part: true });
  // tornillos de brida (ocultos)
  for (const sg of [-1, 1]) for (const d of [131, 149]) L([[machineX(-6), ay + sg * d], [machineX(40), ay + sg * d]], 'thin', { dash: [8, 5], part: true });

  // cotas en cadena superior
  const chainY = ay - 214;
  const cuts = [0, 34, 300, 332, 392, 540, 586];
  L([[machineX(0), chainY], [machineX(586), chainY]], 'dim');
  cuts.forEach((s, i) => {
    const r = i === 0 ? 170 : (P[Math.min(i, P.length - 1)] || P[5]).r;
    L([[machineX(s), chainY - 14], [machineX(s), ay - Math.max(r, 30) - 8]], 'dim');
    L([[machineX(s) - 7, chainY + 7], [machineX(s) + 7, chainY - 7]], 'dim');
    if (i > 0) T((machineX(cuts[i - 1]) + machineX(s)) / 2, chainY - 12, String(s - cuts[i - 1]), 18, { align: 'center' });
  });
  // cota total inferior
  const botY = ay + 232;
  L([[machineX(0), botY], [machineX(586), botY]], 'dim');
  L([[machineX(0), ay + 178], [machineX(0), botY + 14]], 'dim'); L([[machineX(586), ay + 60], [machineX(586), botY + 14]], 'dim');
  L([[machineX(0), botY], [machineX(0) + 16, botY - 6]], 'dim'); L([[machineX(0), botY], [machineX(0) + 16, botY + 6]], 'dim');
  L([[machineX(586), botY], [machineX(586) - 16, botY - 6]], 'dim'); L([[machineX(586), botY], [machineX(586) - 16, botY + 6]], 'dim');
  T(540, botY - 10, '586 ±0,2', 20, { align: 'center' });
  // cota diámetro brida
  const dx = machineX(0) - 52;
  L([[dx, ay - 170], [dx, ay + 170]], 'dim'); L([[dx - 14, ay - 170], [machineX(0) - 6, ay - 170]], 'dim'); L([[dx - 14, ay + 170], [machineX(0) - 6, ay + 170]], 'dim');
  T(dx - 12, ay, 'Ø340 H7', 19, { align: 'center', rot: -Math.PI / 2 });
  // globos de referencia
  const balloons = [[1, 0, -1], [2, 150, -1], [3, 316, 1], [4, 362, -1], [5, 470, 1], [6, 563, -1]];
  for (const [n, s, side] of balloons) {
    const bx = machineX(s) + (side < 0 ? -18 : 22), by = ay + side * 300;
    const px = machineX(s), py = ay + side * Math.max(28, (P.find(p => s >= p.s0 && s <= p.s1) || P[0]).r * 0.7);
    L([[px, py], [bx, by - side * 22]], 'dim');
    circle(bx, by, 22, 'dim', 40);
    T(bx, by + 7, String(n), 20, { align: 'center', bold: true });
  }
  T(machineX(470) + 44, ay + 64, 'Ø60 h6', 18); T(machineX(150), ay - 150, 'Ra 0,8', 16);
  T(machineX(-40), ay - 252, 'SECCIÓN A–A', 20, { bold: true });
  T(machineX(400), ay - 252, 'DET. 04 · ESC 1:5', 18);

  // --- Bloque superior: fórmulas y código ---
  rect(70, 90, 520, 330, 'frame'); rect(560, 90, 1010, 330, 'frame');
  L([[70, 130], [520, 130]], 'frame'); L([[560, 130], [1010, 130]], 'frame');
  T(86, 118, 'CÁLCULO TÉRMICO / 07', 18, { bold: true }); T(576, 118, 'solver.rs', 18, { bold: true });
  const formulas = ['Q = ṁ · cₚ · ΔT', 'q = −λ ∇T', 'λ = 0,034 W/m·K', '∂T/∂t = α ∇²T', 'σ = F / A ≤ 235 MPa', 'Re = ρ·v·D / μ'];
  formulas.forEach((f, i) => T(90, 170 + i * 30, f, 21));
  const code = ['fn solve(k: &Mesh, t0: f64) {', '  for i in 1..k.n {', '    T[i] = T[i-1]', '      + α*dt*lap(&T, i);', '  }', '  clamp(T, 0.0, T_MAX)', '} // rev.07 — sin validar'];
  code.forEach((c, i) => T(578, 164 + i * 24, c, 17));
  // conectores del bloque superior al alzado
  L([[295, 330], [295, 356], [machineX(0), 356]], 'pipe');
  L([[785, 330], [785, 356], [machineX(586), 356]], 'pipe');
  L([[machineX(0), 356], [machineX(0), chainY - 14]], 'pipe');
  L([[machineX(586), 356], [machineX(586), chainY - 14]], 'pipe');

  // --- Cajetín con el titular ---
  const tb = { x0: 40, x1: 1040, y0: 960, y1: 1382 };
  rect(tb.x0, tb.y0, tb.x1, tb.y1, 'frame');
  L([[tb.x0, 1330], [tb.x1, 1330]], 'frame');
  const cells = [40, 300, 470, 610, 790, 1040];
  const labels = ['PLANO Nº 0412-B', 'ESC. 1:5', 'REV. 07', 'HOJA 3/48', 'NO APROBADO'];
  for (let i = 1; i < cells.length - 1; i++) L([[cells[i], 1330], [cells[i], 1382]], 'frame');
  labels.forEach((l, i) => T(cells[i] + 14, 1364, l, 17));
  T(56, 988, 'TÍTULO', 15);
  // conectores desde las cotas al cajetín
  L([[machineX(0), botY + 14], [machineX(0), tb.y0]], 'pipe');
  L([[machineX(586), botY + 14], [machineX(586), tb.y0]], 'pipe');
  L([[machineX(293), botY], [machineX(293), tb.y0]], 'pipe', { dash: [6, 6] });

  // --- Zona inferior: vista frontal, tabla de datos, gráfica ---
  const vx = 245, vy = 1625;
  L([[vx, 1382], [vx, vy - 210]], 'pipe');
  [170, 138, 118, 96, 78, 30].forEach((r, i) => circle(vx, vy, r, i === 0 || i === 2 ? 'main' : 'thin', 72));
  circle(vx, vy, 150, 'axis', 72, { dash: [18, 5, 3, 5] });
  for (let i = 0; i < 8; i++) { const a = (i / 8) * Math.PI * 2 + Math.PI / 8; circle(vx + Math.cos(a) * 150, vy + Math.sin(a) * 150, 9, 'thin', 20); }
  { const hx = []; for (let i = 0; i <= 6; i++) { const a = (i / 6) * Math.PI * 2; hx.push([vx + Math.cos(a) * 52, vy + Math.sin(a) * 52]); } L(hx, 'main'); }
  L([[vx - 200, vy], [vx + 200, vy]], 'axis', { dash: [26, 6, 4, 6] }); L([[vx, vy - 200], [vx, vy + 200]], 'axis', { dash: [26, 6, 4, 6] });
  T(vx + 200, vy - 190, 'VISTA B', 20, { align: 'center', bold: true });
  // tabla
  const tx0 = 470, tx1 = 1010, ty0 = 1420, rows = 7, rh = 30;
  rect(tx0, ty0, tx1, ty0 + rows * rh, 'frame');
  for (let r = 1; r < rows; r++) L([[tx0, ty0 + r * rh], [tx1, ty0 + r * rh]], 'thin');
  [600, 720, 860].forEach(x => L([[x, ty0], [x, ty0 + rows * rh]], 'thin'));
  L([[tx0 + 270, 1382], [tx0 + 270, ty0]], 'pipe');
  const hdr = ['POS', 'Ø / mm', 'MAT.', 'TOL.'];
  [tx0, 600, 720, 860].forEach((x, i) => T(x + 10, ty0 + 21, hdr[i], 16, { bold: true }));
  const mats = ['S235', 'AISI 316', 'EN-GJL', 'PA66', '42CrMo4', 'C45E', 'AlSi10'];
  for (let r = 1; r < rows; r++) {
    T(tx0 + 10, ty0 + r * rh + 21, String(r).padStart(2, '0'), 16);
    T(610, ty0 + r * rh + 21, (rnd() * 300 + 20).toFixed(1), 16);
    T(730, ty0 + r * rh + 21, mats[r - 1], 16);
    T(870, ty0 + r * rh + 21, ['h6', 'H7', '±0,1', 'js5', 'g6', 'k6', '±0,05'][r - 1], 16);
  }
  // gráfica
  const gx0 = 470, gx1 = 1010, gy0 = 1668, gy1 = 1850;
  rect(gx0, gy0, gx1, gy1, 'frame');
  const gpts = []; for (let i = 0; i <= 80; i++) { const x = gx0 + (i / 80) * (gx1 - gx0); gpts.push([x, gy1 - 30 - (Math.sin(i * 0.23) * 0.5 + 0.5) * 60 - fbm1(i * 0.2, 4) * 40 - i * 0.9]); }
  L(gpts, 'thin');
  for (let i = 1; i < 6; i++) L([[gx0 + i * 90, gy0], [gx0 + i * 90, gy1]], 'thin', { dash: [3, 6] });
  T(gx0 + 12, gy0 + 24, 'ΔT (K) / t (s)', 16);
  L([[vx, vy + 250], [vx, 1880], [40, 1880]], 'pipe');

  // --- Hoja superior (se descubre en el barrido del loop) ---
  const rng = mulberry32(99);
  for (let blk = 0; blk < 8; blk++) {
    const y0 = SHEET_TOP + 120 + blk * 300;
    if (y0 > 60) break;
    const kind = blk % 3;
    if (kind === 0) { // esquema de tuberías
      const nodes = [];
      for (let i = 0; i < 5; i++) nodes.push([110 + i * 205 + (rng() - 0.5) * 40, y0 + 60 + rng() * 150]);
      nodes.forEach(([x, y], i) => {
        if (i % 2) circle(x, y, 34, 'main', 40); else rect(x - 44, y - 60, x + 44, y + 60, 'main');
        T(x, y + 96, `T-${10 + blk}${i}`, 16, { align: 'center' });
        if (i > 0) { const [px, py] = nodes[i - 1]; const mx = (px + x) / 2; L([[px, py], [mx, py], [mx, y], [x, y]], 'pipe'); }
      });
    } else if (kind === 1) { // tabla + texto
      rect(70, y0 + 20, 1010, y0 + 250, 'frame');
      for (let r = 1; r < 7; r++) L([[70, y0 + 20 + r * 33], [1010, y0 + 20 + r * 33]], 'thin');
      for (let c = 1; c < 6; c++) L([[70 + c * 156, y0 + 20], [70 + c * 156, y0 + 250]], 'thin');
      for (let r = 0; r < 7; r++) for (let c = 0; c < 6; c++) T(82 + c * 156, y0 + 44 + r * 33, (rng() * 999).toFixed(r % 2 ? 2 : 0), 15);
    } else { // sección secundaria
      const cy = y0 + 140;
      for (let i = 0; i < 4; i++) circle(300, cy, 110 - i * 24, i ? 'thin' : 'main', 56);
      rect(470, cy - 90, 1000, cy + 90, 'main');
      hatch(470, 1000, cy - 90, cy - 60);
      L([[410, cy], [470, cy]], 'pipe');
      T(480, cy + 120, 'Fig. ' + (blk + 3) + ' — detalle de montaje', 16);
    }
    L([[40, y0 + 290], [1040, y0 + 290]], 'thin', { dash: [4, 8] });
  }
  return { lines, texts };
}

// ---------- Grafo para que la tinta viaje por las líneas ----------
function buildGraph(lines) {
  const segs = [];
  lines.forEach((l, li) => {
    if (l.kind === 'axis' && false) return;
    for (let i = 0; i < l.pts.length - 1; i++) {
      const [x1, y1] = l.pts[i], [x2, y2] = l.pts[i + 1];
      if (Math.hypot(x2 - x1, y2 - y1) < 0.01) continue;
      segs.push({ x1, y1, x2, y2, li, ts: [0, 1] });
    }
  });
  // intersecciones (con tolerancia en extremos)
  const n = segs.length, EPS = 1.2;
  const bb = segs.map(s => [Math.min(s.x1, s.x2) - EPS, Math.max(s.x1, s.x2) + EPS, Math.min(s.y1, s.y2) - EPS, Math.max(s.y1, s.y2) + EPS]);
  // rejilla espacial
  const G = 80, cells = new Map();
  segs.forEach((s, i) => {
    const b = bb[i];
    for (let gx = Math.floor(b[0] / G); gx <= Math.floor(b[1] / G); gx++) for (let gy = Math.floor(b[2] / G); gy <= Math.floor(b[3] / G); gy++) {
      const k = gx + ',' + gy; if (!cells.has(k)) cells.set(k, []); cells.get(k).push(i);
    }
  });
  const tested = new Set();
  for (const arr of cells.values()) {
    for (let a = 0; a < arr.length; a++) for (let b = a + 1; b < arr.length; b++) {
      const i = arr[a], j = arr[b]; const key = i < j ? i * n + j : j * n + i;
      if (tested.has(key)) continue; tested.add(key);
      const A = segs[i], B = segs[j];
      if (bb[i][1] < bb[j][0] || bb[j][1] < bb[i][0] || bb[i][3] < bb[j][2] || bb[j][3] < bb[i][2]) continue;
      const rx = A.x2 - A.x1, ry = A.y2 - A.y1, sx = B.x2 - B.x1, sy = B.y2 - B.y1;
      const den = rx * sy - ry * sx; if (Math.abs(den) < 1e-9) continue;
      const qx = B.x1 - A.x1, qy = B.y1 - A.y1;
      const t = (qx * sy - qy * sx) / den, u = (qx * ry - qy * rx) / den;
      const la = Math.hypot(rx, ry), lb = Math.hypot(sx, sy);
      const ea = EPS / la, eb = EPS / lb;
      if (t >= -ea && t <= 1 + ea && u >= -eb && u <= 1 + eb) { A.ts.push(clamp(t)); B.ts.push(clamp(u)); }
    }
  }
  // nodos y aristas
  const nodeMap = new Map(), nodes = [];
  const nid = (x, y) => { const k = Math.round(x * 2) + ':' + Math.round(y * 2); let id = nodeMap.get(k); if (id === undefined) { id = nodes.length; nodes.push({ x, y, adj: [] }); nodeMap.set(k, id); } return id; };
  const edges = [];
  for (const s of segs) {
    const ts = [...new Set(s.ts.map(v => Math.round(v * 1e5) / 1e5))].sort((a, b) => a - b);
    for (let k = 0; k < ts.length - 1; k++) {
      const x1 = lerp(s.x1, s.x2, ts[k]), y1 = lerp(s.y1, s.y2, ts[k]), x2 = lerp(s.x1, s.x2, ts[k + 1]), y2 = lerp(s.y1, s.y2, ts[k + 1]);
      const len = Math.hypot(x2 - x1, y2 - y1); if (len < 0.05) continue;
      const a = nid(x1, y1), b = nid(x2, y2);
      const e = { a, b, len, li: s.li, x1, y1, x2, y2 };
      edges.push(e); nodes[a].adj.push([b, len]); nodes[b].adj.push([a, len]);
    }
  }
  return { nodes, edges };
}

function dijkstra(nodes, seeds) {
  const dist = new Float64Array(nodes.length).fill(Infinity);
  const heap = []; // [d, i]
  const push = (d, i) => { heap.push([d, i]); let c = heap.length - 1; while (c > 0) { const p = (c - 1) >> 1; if (heap[p][0] <= heap[c][0]) break; [heap[p], heap[c]] = [heap[c], heap[p]]; c = p; } };
  const pop = () => { const top = heap[0], last = heap.pop(); if (heap.length) { heap[0] = last; let c = 0; for (;;) { const l = 2 * c + 1, r = l + 1; let m = c; if (l < heap.length && heap[l][0] < heap[m][0]) m = l; if (r < heap.length && heap[r][0] < heap[m][0]) m = r; if (m === c) break; [heap[m], heap[c]] = [heap[c], heap[m]]; c = m; } } return top; };
  for (const [i, d] of seeds) { if (d < dist[i]) { dist[i] = d; push(d, i); } }
  while (heap.length) {
    const [d, i] = pop(); if (d > dist[i]) continue;
    for (const [j, w] of nodes[i].adj) { const nd = d + w; if (nd < dist[j]) { dist[j] = nd; push(nd, j); } }
  }
  return dist;
}

// ---------- Estado global de la escena ----------
let S = null;
export const HEAD = { y1: 1128, y2: 1282, size1: 150, size2: 118 };
export const IMPACT_T = 0.8;
export const INK_T0 = 0.92;

function headlineLayout(ctx) {
  ctx.font = `700 ${HEAD.size1}px ${FONT_HEAD}`;
  const wES = ctx.measureText('ES').width, wERA = ctx.measureText('ERA').width;
  ctx.font = `700 ${HEAD.size2}px ${FONT_HEAD}`;
  const wC = ctx.measureText('COMPLICADO.').width;
  return { wES, wERA, wC, esX: 540 - wES / 2, eraX: 540 - wERA / 2, cX: 540 - wC / 2 };
}

// velocidad del frente de tinta con empujes en cada tiempo (120 BPM)
function buildFront() {
  const dt = 1 / 600, tab = [];
  let f = 0;
  for (let t = 0; t <= 4.5; t += dt) {
    tab.push(f);
    if (t < INK_T0) continue;
    const u = t - INK_T0;
    const beatPhase = ((t - 0.5) % 0.5) / 0.5; // tiempos en 1.0, 1.5, 2.0...
    const pulse = 0.35 + 0.65 * Math.pow(1 - beatPhase, 2.2) * 1.6;
    f += (380 + 2100 * u) * pulse * dt;
  }
  return { tab, dt };
}
const frontAt = (t) => { const { tab, dt } = S.front; const i = clamp(Math.floor(t / dt), 0, tab.length - 1); return tab[i]; };
function timeAtDist(d) { const { tab, dt } = S.front; let lo = 0, hi = tab.length - 1; if (tab[hi] < d) return 99; while (hi - lo > 1) { const m = (lo + hi) >> 1; if (tab[m] < d) lo = m; else hi = m; } return hi * dt; }

export function init() {
  if (S) return S;
  const { lines, texts } = build();
  const ctx0 = makeCanvas(10, 10).getContext('2d');
  const hl = headlineLayout(ctx0);
  const impact = { x: 540, y: HEAD.y1 - HEAD.size1 * 0.36 };
  const g = buildGraph(lines);
  S = { lines, texts, hl, impact, g, front: buildFront() };
  // semillas: nodos cerca del charco de tinta
  const seeds = [];
  g.nodes.forEach((nd, i) => { const d = Math.hypot(nd.x - impact.x, nd.y - impact.y); if (d < 190) seeds.push([i, d * 0.8]); });
  S.dist = dijkstra(g.nodes, seeds);
  // distancia de cada texto
  texts.forEach(tx => {
    let best = Infinity;
    for (let i = 0; i < g.nodes.length; i++) { const nd = g.nodes[i]; const e = Math.hypot(nd.x - tx.x, nd.y - tx.y); if (e < 120) best = Math.min(best, S.dist[i] + e); }
    tx.d = best; tx.tInk = timeAtDist(best);
  });
  g.edges.forEach(e => { const da = S.dist[e.a], db = S.dist[e.b]; e.d0 = Math.min(da, db); e.d1 = Math.max(da, db); e.rev = db < da; e.t0 = timeAtDist(e.d0); e.kind = lines[e.li].kind; e.part = !!lines[e.li].part; e.dash = lines[e.li].dash; });
  // papel horneado
  const pc = makeCanvas(W + OX * 2, OY + SHEET_BOTTOM + 80);
  const p = pc.getContext('2d');
  p.fillStyle = '#0D0E14'; p.fillRect(0, 0, pc.width, pc.height);
  p.save(); p.translate(OX, OY);
  p.fillStyle = C.PAPER; p.fillRect(-OX, SHEET_TOP, W + OX * 2, SHEET_BOTTOM - SHEET_TOP + 80);
  // borde superior de la hoja con sombra
  const sh = p.createLinearGradient(0, SHEET_TOP - 40, 0, SHEET_TOP); sh.addColorStop(0, 'rgba(0,0,0,0)'); sh.addColorStop(1, 'rgba(0,0,0,0.5)');
  p.fillStyle = sh; p.fillRect(-OX, SHEET_TOP - 40, W + OX * 2, 40);
  const rnd = mulberry32(7);
  for (let i = 0; i < 26000; i++) { // fibra
    const x = rnd() * (W + OX * 2) - OX, y = SHEET_TOP + rnd() * (SHEET_BOTTOM - SHEET_TOP + 80);
    p.fillStyle = rnd() < 0.5 ? 'rgba(0,0,0,0.035)' : 'rgba(255,255,255,0.08)';
    p.fillRect(x, y, 1 + rnd() * 2.5, 1);
  }
  for (let x = -OX; x < W + OX; x += 24) { p.fillStyle = x % 120 === 0 ? C.GRID_MAJOR : C.GRID; p.fillRect(x, SHEET_TOP, 1, SHEET_BOTTOM - SHEET_TOP + 80); }
  for (let y = SHEET_TOP; y < SHEET_BOTTOM + 80; y += 24) { p.fillStyle = (y - SHEET_TOP) % 120 === 0 ? C.GRID_MAJOR : C.GRID; p.fillRect(-OX, y, W + OX * 2, 1); }
  p.restore();
  S.paper = pc;
  S.layer = makeCanvas();
  return S;
}

const KIND = {
  main: { w: 2.4, c: C.LINE_DARK }, thin: { w: 1.3, c: C.LINE }, hatch: { w: 1, c: C.LINE }, dim: { w: 1.1, c: C.LINE },
  frame: { w: 1.8, c: C.LINE_DARK }, pipe: { w: 1.5, c: C.LINE }, axis: { w: 1.1, c: C.LINE },
};

// Cámara: devuelve {camY, z, shx, shy}
export const CAM0 = { dy: -400, dx: 0, T: 1.0 };
export function camera01(t) {
  const q = Math.pow(1 - clamp(t / CAM0.T), 3);
  const camY = CAM0.dy * q, camX = CAM0.dx * q;
  const z = 1 + 0.045 * smooth(clamp(t / 3));
  let shx = 0, shy = 0;
  const k = t - IMPACT_T;
  if (k >= 0 && k < 0.12) { const a = (1 - k / 0.12) * 9; shx = Math.sin(k * 190) * a; shy = Math.cos(k * 230) * a; }
  return { camX, camY, z, shx, shy };
}
export const w2s = (cam, x, y) => [(x - (cam.camX || 0) - 540) * cam.z + 540 + cam.shx, (y - cam.camY - 960) * cam.z + 960 + cam.shy];
function applyCam(ctx, cam) { ctx.save(); ctx.translate(540 + cam.shx, 960 + cam.shy); ctx.scale(cam.z, cam.z); ctx.translate(-540 - (cam.camX || 0), -cam.camY - 960); }

// Posición de la gota cayendo (pantalla) — compartida con el loop final.
export const DROP_Y0 = -14;
export function dropFallY(t, iy) { const u = t / IMPACT_T; return DROP_Y0 + (iy - DROP_Y0) * (0.86 * u + 0.14 * u * u); }

/**
 * Dibuja el plano. opts: { t, cam (override), inkOn, liftParts (ocultar líneas de la máquina), noDrop }
 */
export function drawBlueprint(ctx, t, opts = {}) {
  init();
  const cam = opts.cam || camera01(t);
  const inkOn = opts.inkOn !== false;
  applyCam(ctx, cam);
  // papel
  ctx.drawImage(S.paper, -OX, -OY);
  const front = inkOn ? frontAt(t) : -1;
  // --- líneas grises (las que aún no ha tocado la tinta) ---
  const greyPaths = {};
  const inkPaths = []; const heads = [];
  const view0 = cam.camY - 200 / cam.z, view1 = cam.camY + (1920 + 200) / cam.z;
  for (const e of S.g.edges) {
    if (Math.max(e.y1, e.y2) < view0 || Math.min(e.y1, e.y2) > view1) continue;
    if (opts.liftParts && e.part) continue;
    const inked = front > e.d0;
    const kd = KIND[e.kind];
    if (!inked) {
      (greyPaths[e.kind] ||= new Path2D());
      greyPaths[e.kind].moveTo(e.x1, e.y1); greyPaths[e.kind].lineTo(e.x2, e.y2);
      continue;
    }
    const age = t - e.t0;
    const k = clamp((front - e.d0) / Math.max(0.001, e.d1 - e.d0));
    const [sx, sy, ex, ey] = e.rev ? [e.x2, e.y2, e.x1, e.y1] : [e.x1, e.y1, e.x2, e.y2];
    const px = lerp(sx, ex, k), py = lerp(sy, ey, k);
    // parte no alcanzada sigue gris
    if (k < 1) { (greyPaths[e.kind] ||= new Path2D()); greyPaths[e.kind].moveTo(px, py); greyPaths[e.kind].lineTo(ex, ey); heads.push([px, py]); }
    // simplificación: rayados, cotas y auxiliares desaparecen tras entintarse
    const fades = e.kind === 'hatch' || e.kind === 'dim' || e.kind === 'thin' || e.kind === 'axis';
    const a = fades ? 1 - smooth(inv(0.25, 0.7, age)) : 1;
    if (a <= 0.01) continue;
    inkPaths.push({ sx, sy, px, py, a, w: kd.w + (e.kind === 'main' || e.kind === 'frame' ? 1.2 : 0.4), lift: e.kind === 'main' || e.kind === 'frame' || e.kind === 'pipe' });
  }
  for (const kd in greyPaths) { ctx.strokeStyle = KIND[kd].c; ctx.lineWidth = KIND[kd].w; ctx.setLineDash([]); ctx.stroke(greyPaths[kd]); }
  // --- textos (se desvanecen cuando llega la tinta: el plano se simplifica) ---
  for (const tx of S.texts) {
    if (tx.y < view0 || tx.y > view1) continue;
    const a = inkOn ? 1 - smooth(inv(tx.tInk - 0.05, tx.tInk + 0.35, t)) : 1;
    if (a <= 0.01) continue;
    ctx.save(); ctx.globalAlpha = a;
    ctx.font = `${tx.bold ? 700 : 400} ${tx.size}px ${tx.font}`; ctx.textAlign = tx.align; ctx.fillStyle = C.TEXT_SOFT;
    if (tx.rot) { ctx.translate(tx.x, tx.y); ctx.rotate(tx.rot); ctx.fillText(tx.s, 0, 0); } else ctx.fillText(tx.s, tx.x, tx.y);
    ctx.restore();
  }
  ctx.restore();

  // --- capa de tinta (pantalla) con elevación ---
  if (inkPaths.length) {
    const L = S.layer, lc = L.getContext('2d');
    lc.setTransform(1, 0, 0, 1, 0, 0); lc.clearRect(0, 0, W, H);
    lc.translate(540 + cam.shx, 960 + cam.shy); lc.scale(cam.z, cam.z); lc.translate(-540 - (cam.camX || 0), -cam.camY - 960);
    lc.lineCap = 'round';
    // agrupar por alfa
    const buckets = new Map();
    for (const p of inkPaths) { const key = Math.round(p.a * 8) + '|' + p.w.toFixed(1); if (!buckets.has(key)) buckets.set(key, { a: Math.round(p.a * 8) / 8, w: p.w, path: new Path2D() }); const b = buckets.get(key); b.path.moveTo(p.sx, p.sy); b.path.lineTo(p.px, p.py); }
    lc.strokeStyle = C.MAG;
    for (const b of buckets.values()) { lc.globalAlpha = b.a; lc.lineWidth = b.w; lc.stroke(b.path); }
    lc.globalAlpha = 1;
    // cabezas de energía
    for (const [x, y] of heads) {
      const g = lc.createRadialGradient(x, y, 0, x, y, 14); g.addColorStop(0, 'rgba(255,235,245,1)'); g.addColorStop(0.3, hexA(C.MAG_LIGHT, 0.8)); g.addColorStop(1, hexA(C.MAG, 0));
      lc.fillStyle = g; lc.fillRect(x - 14, y - 14, 28, 28);
    }
    const lift = seg(t, 1.2, 3.0);
    ctx.save();
    ctx.shadowColor = 'rgba(70,0,35,0.35)'; ctx.shadowBlur = 6 + 10 * lift; ctx.shadowOffsetY = 2 + 9 * lift; ctx.shadowOffsetX = 1 + 3 * lift;
    ctx.drawImage(L, 0, 0);
    ctx.restore();
    ctx.save(); ctx.globalCompositeOperation = 'lighter'; ctx.globalAlpha = 0.18; ctx.filter = 'blur(8px)'; ctx.drawImage(L, 0, 0); ctx.restore();
  }
  // --- titular ES / ERA ---
  drawHeadline(ctx, t, cam, opts);
  // --- gota cayendo e impacto ---
  if (!opts.noDrop) drawDropAndSplash(ctx, t, cam);
  return cam;
}

function blobPath(ctx, cx, cy, R, t, seed = 1, amp = 0.16) {
  ctx.beginPath();
  const n = 90;
  for (let i = 0; i <= n; i++) {
    const a = (i / n) * Math.PI * 2;
    const r = R * (1 + amp * fbm1(a * 2.2 + seed, seed) + amp * 0.5 * noise1(a * 7 + t * 3, seed + 2));
    const x = cx + Math.cos(a) * r * 1.12, y = cy + Math.sin(a) * r * 0.88;
    i ? ctx.lineTo(x, y) : ctx.moveTo(x, y);
  }
  ctx.closePath();
}

function drawHeadline(ctx, t, cam, opts) {
  const hl = S.hl, y1 = HEAD.y1, y2 = HEAD.y2, F1 = HEAD.size1;
  applyCam(ctx, cam);
  ctx.textBaseline = 'alphabetic'; ctx.textAlign = 'left';
  ctx.font = `700 ${HEAD.size2}px ${FONT_HEAD}`;
  ctx.fillStyle = C.TEXT;
  ctx.fillText('COMPLICADO.', hl.cX, y2);
  ctx.font = `700 ${F1}px ${FONT_HEAD}`;
  const imp = opts.inkOn === false ? 99 : IMPACT_T;
  if (t < imp) { ctx.fillText('ES', hl.esX, y1); ctx.restore(); return; }
  const k = t - imp;
  const ix = S.impact.x, iy = S.impact.y;
  // ES bajo la tinta: se disuelve
  if (k < 0.1) { ctx.globalAlpha = 1 - k / 0.1; ctx.fillText('ES', hl.esX, y1); ctx.globalAlpha = 1; }
  const grow = E.outExpo(clamp(k / 0.3));
  const shrink = seg(t, imp + 0.5, imp + 0.95, E.inOutCubic);
  const R = (16 + 138 * grow) * (1 - shrink);
  // ERA emerge del charco
  const eraP = seg(t, imp + 0.42, imp + 0.92, E.outCubic);
  if (eraP > 0) {
    const sc = lerp(0.8, 1, E.outBack(eraP, 2.4));
    const cy = y1 - F1 * 0.36;
    ctx.save();
    ctx.translate(540, cy); ctx.scale(sc, sc); ctx.translate(-540, -cy);
    const g = ctx.createLinearGradient(0, y1 - F1 * 0.75, 0, y1);
    g.addColorStop(0, '#FF3E98'); g.addColorStop(0.55, C.MAG); g.addColorStop(1, '#C0106A');
    ctx.fillStyle = g;
    ctx.shadowColor = 'rgba(90,0,40,0.32)'; ctx.shadowBlur = 12 * eraP; ctx.shadowOffsetY = 8 * eraP;
    ctx.fillText('ERA', hl.eraX, y1);
    ctx.shadowColor = 'transparent';
    const wet = 1 - seg(t, imp + 1.0, imp + 2.0);
    if (wet > 0) { // brillo húmedo que recorre las letras
      ctx.globalCompositeOperation = 'source-atop'; ctx.globalAlpha = 0.55 * wet;
      const sx = hl.eraX - 160 + (hl.wERA + 320) * seg(t, imp + 0.62, imp + 1.3);
      const sh = ctx.createLinearGradient(sx - 70, 0, sx + 70, 0);
      sh.addColorStop(0, 'rgba(255,255,255,0)'); sh.addColorStop(0.5, 'rgba(255,255,255,0.95)'); sh.addColorStop(1, 'rgba(255,255,255,0)');
      ctx.fillStyle = sh; ctx.fillRect(hl.eraX - 20, y1 - F1, hl.wERA + 40, F1 * 1.1);
    }
    ctx.restore();
    // goteos bajo las letras
    const drips = [[0.1, 40, 0.1], [0.5, 70, 0.0], [0.86, 30, 0.2]];
    ctx.fillStyle = C.MAG;
    for (const [fx, len, dl] of drips) {
      const dp = E.outCubic(seg(t, imp + 0.8 + dl, imp + 1.9 + dl, (x) => x));
      if (dp <= 0) continue;
      const dx = hl.eraX + hl.wERA * fx, L = len * dp, w = 8;
      ctx.beginPath(); ctx.moveTo(dx - w, y1 - 6); ctx.lineTo(dx - w * 0.55, y1 + L); ctx.arc(dx, y1 + L, w * 0.55, Math.PI, 0, true); ctx.lineTo(dx + w, y1 - 6); ctx.closePath(); ctx.fill();
      ctx.beginPath(); ctx.arc(dx, y1 + L + 2, w, 0, Math.PI * 2); ctx.fill();
    }
  }
  if (R > 1) {
    blobPath(ctx, ix, iy, R, t, 3);
    const bg = ctx.createRadialGradient(ix - R * 0.3, iy - R * 0.3, R * 0.1, ix, iy, R * 1.2);
    bg.addColorStop(0, '#FF4FA0'); bg.addColorStop(0.7, C.MAG); bg.addColorStop(1, '#B40E60');
    ctx.fillStyle = bg; ctx.fill();
    ctx.strokeStyle = hexA('#8E0B4C', 0.5); ctx.lineWidth = 3; ctx.stroke();
    ctx.save(); ctx.globalAlpha = 0.55 * (1 - shrink);
    ctx.beginPath(); ctx.ellipse(ix - R * 0.35, iy - R * 0.35, R * 0.28, R * 0.12, -0.5, 0, Math.PI * 2); ctx.fillStyle = 'rgba(255,255,255,0.7)'; ctx.fill(); ctx.restore();
  }
  ctx.restore();
}

function drawDropAndSplash(ctx, t, cam) {
  const [ix, iy] = w2s(cam, S.impact.x, S.impact.y);
  if (t < IMPACT_T) {
    const y = dropFallY(t, iy);
    // sombra en el papel
    const pa = seg(t, 0.2, IMPACT_T);
    ctx.save(); ctx.globalAlpha = 0.35 * pa;
    const sr = lerp(90, 28, pa);
    const g = ctx.createRadialGradient(ix + 10, iy + 12, 0, ix + 10, iy + 12, sr); g.addColorStop(0, 'rgba(60,0,30,0.7)'); g.addColorStop(1, 'rgba(60,0,30,0)');
    ctx.fillStyle = g; ctx.fillRect(ix - sr + 10, iy - sr + 12, sr * 2, sr * 2); ctx.restore();
    // estela de movimiento
    for (let i = 3; i >= 1; i--) drawDrop(ctx, ix, y - i * 15, 28, { stretch: 1.35, squash: 1.12, alpha: 0.12 * (4 - i), glow: 0 });
    drawDrop(ctx, ix, y, 28, { stretch: 1.35, squash: 1.12, glow: 0.6 });
    return;
  }
  // corona de salpicadura vista desde arriba
  const k = t - IMPACT_T;
  const rnd = mulberry32(23);
  const N = 30;
  for (let i = 0; i < N; i++) {
    const a = (i / N) * Math.PI * 2 + rnd() * 0.2;
    const far = 150 + rnd() * 230, sz = 4 + rnd() * 11;
    const p = E.outExpo(clamp(k / (0.35 + rnd() * 0.2)));
    const r = 40 + far * p;
    const x = ix + Math.cos(a) * r * 1.1, y = iy + Math.sin(a) * r * 0.85;
    const fly = 1 - p; // estirados mientras vuelan
    ctx.save(); ctx.fillStyle = C.MAG; ctx.translate(x, y); ctx.rotate(a);
    ctx.beginPath(); ctx.ellipse(0, 0, sz * (1 + fly * 2.5), sz * (1 - fly * 0.3), 0, 0, Math.PI * 2); ctx.fill(); ctx.restore();
  }
  // anillo de choque
  if (k < 0.3) {
    ctx.save(); ctx.strokeStyle = hexA(C.MAG, 0.45 * (1 - k / 0.3)); ctx.lineWidth = 6 * (1 - k / 0.3);
    ctx.beginPath(); ctx.ellipse(ix, iy, 40 + 500 * E.outCubic(k / 0.3), (40 + 500 * E.outCubic(k / 0.3)) * 0.8, 0, 0, Math.PI * 2); ctx.stroke(); ctx.restore();
  }
  // columna central (primeros fotogramas)
  if (k < 0.1) drawDrop(ctx, ix, iy - 20 * (1 - k / 0.1), 30 * (1 - k / 0.1) + 8, { squash: 0.5 + k * 3, glow: 0.8 });
}

export const scene01 = {
  name: '01 PLANO → ES/ERA', start: 0, end: 3.0,
  draw(ctx, t) { ctx.fillStyle = C.PAPER; ctx.fillRect(0, 0, W, H); drawBlueprint(ctx, t); },
};
