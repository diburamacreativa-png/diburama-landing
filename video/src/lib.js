// Utilidades compartidas: matemáticas, easing, ruido, paleta, tipografía y dibujo de la gota.
export const W = 1080, H = 1920, FPS = 30, DURATION = 27, TOTAL_FRAMES = DURATION * FPS;

export const C = {
  PAPER: '#E4E3DE', PAPER_SHADE: '#D6D5CF', GRID: 'rgba(60,60,72,0.07)', GRID_MAJOR: 'rgba(60,60,72,0.13)',
  LINE: '#8C8C95', LINE_DARK: '#51515C', TEXT: '#3B3B45', TEXT_SOFT: '#7B7B85',
  MAG: '#E6197D', MAG_DARK: '#A80F5A', MAG_LIGHT: '#FF5AA8',
  NIGHT: '#0D0E14', NIGHT_2: '#161822', OFF: '#F2F1EC', GREY: '#9A9AA3',
};
export const FONT_HEAD = '"Space Grotesk"';
export const FONT_MONO = '"Space Mono"';

export const clamp = (x, a = 0, b = 1) => Math.min(b, Math.max(a, x));
export const lerp = (a, b, t) => a + (b - a) * t;
export const inv = (a, b, x) => clamp((x - a) / (b - a));
export const smooth = (t) => t * t * (3 - 2 * t);
export const smoother = (t) => t * t * t * (t * (t * 6 - 15) + 10);
export const E = {
  inQuad: (t) => t * t, outQuad: (t) => 1 - (1 - t) * (1 - t),
  inCubic: (t) => t * t * t, outCubic: (t) => 1 - Math.pow(1 - t, 3),
  inOutCubic: (t) => (t < 0.5 ? 4 * t * t * t : 1 - Math.pow(-2 * t + 2, 3) / 2),
  outQuart: (t) => 1 - Math.pow(1 - t, 4), inQuart: (t) => t ** 4,
  inOutQuart: (t) => (t < 0.5 ? 8 * t ** 4 : 1 - Math.pow(-2 * t + 2, 4) / 2),
  outExpo: (t) => (t >= 1 ? 1 : 1 - Math.pow(2, -10 * t)),
  inExpo: (t) => (t <= 0 ? 0 : Math.pow(2, 10 * t - 10)),
  inOutExpo: (t) => (t <= 0 ? 0 : t >= 1 ? 1 : t < 0.5 ? Math.pow(2, 20 * t - 10) / 2 : (2 - Math.pow(2, -20 * t + 10)) / 2),
  outBack: (t, s = 1.70158) => 1 + (s + 1) * Math.pow(t - 1, 3) + s * Math.pow(t - 1, 2),
  outElastic: (t) => (t <= 0 ? 0 : t >= 1 ? 1 : Math.pow(2, -10 * t) * Math.sin((t * 10 - 0.75) * (2 * Math.PI / 3)) + 1),
};
// Tramo animado: devuelve progreso 0..1 con easing entre a y b (segundos).
export const seg = (t, a, b, ease = smooth) => ease(inv(a, b, t));

export function mulberry32(seed) {
  return function () {
    seed |= 0; seed = (seed + 0x6d2b79f5) | 0;
    let t = Math.imul(seed ^ (seed >>> 15), 1 | seed);
    t = (t + Math.imul(t ^ (t >>> 7), 61 | t)) ^ t;
    return ((t ^ (t >>> 14)) >>> 0) / 4294967296;
  };
}
const hash = (n) => { const s = Math.sin(n * 127.1 + 311.7) * 43758.5453; return s - Math.floor(s); };
export function noise1(x, seed = 0) {
  const i = Math.floor(x), f = x - i, u = smooth(f);
  return lerp(hash(i + seed * 57), hash(i + 1 + seed * 57), u) * 2 - 1;
}
export function fbm1(x, seed = 0) { return noise1(x, seed) * 0.6 + noise1(x * 2.1, seed + 3) * 0.3 + noise1(x * 4.3, seed + 7) * 0.1; }

export function hexA(hex, a) {
  const n = parseInt(hex.slice(1), 16);
  return `rgba(${(n >> 16) & 255},${(n >> 8) & 255},${n & 255},${a})`;
}
export function mixHex(h1, h2, t) {
  const a = parseInt(h1.slice(1), 16), b = parseInt(h2.slice(1), 16);
  const r = Math.round(lerp((a >> 16) & 255, (b >> 16) & 255, t));
  const g = Math.round(lerp((a >> 8) & 255, (b >> 8) & 255, t));
  const bl = Math.round(lerp(a & 255, b & 255, t));
  return `rgb(${r},${g},${bl})`;
}

export function makeCanvas(w = W, h = H) {
  const c = document.createElement('canvas'); c.width = w; c.height = h; return c;
}

// Contorno de la gota (lágrima) centrada en (0,0): r = radio del cuerpo, stretch alarga la punta hacia arriba.
export function dropPath(ctx, x, y, r, stretch = 1, squash = 1, rot = 0) {
  ctx.save(); ctx.translate(x, y); ctx.rotate(rot); ctx.scale(1 / Math.sqrt(squash), squash);
  const tip = r * (1.55 * stretch);
  ctx.beginPath();
  ctx.moveTo(0, -tip);
  ctx.bezierCurveTo(r * 0.28, -tip * 0.62, r, -r * 0.55, r, 0.05 * r);
  ctx.arc(0, 0.05 * r, r, 0, Math.PI, false);
  ctx.bezierCurveTo(-r, -r * 0.55, -r * 0.28, -tip * 0.62, 0, -tip);
  ctx.closePath();
  ctx.restore();
}
// Gota física: cuerpo magenta con volumen, brillo especular y reflejo interno.
export function drawDrop(ctx, x, y, r, { stretch = 1, squash = 1, rot = 0, alpha = 1, glow = 0.35 } = {}) {
  if (r <= 0.2) return;
  ctx.save();
  ctx.globalAlpha = alpha;
  if (glow > 0) {
    const g = ctx.createRadialGradient(x, y, r * 0.2, x, y, r * 3.2);
    g.addColorStop(0, hexA(C.MAG, 0.35 * glow)); g.addColorStop(1, hexA(C.MAG, 0));
    ctx.fillStyle = g; ctx.fillRect(x - r * 3.2, y - r * 3.2, r * 6.4, r * 6.4);
  }
  dropPath(ctx, x, y, r, stretch, squash, rot);
  const body = ctx.createRadialGradient(x - r * 0.35, y - r * 0.2, r * 0.1, x, y + r * 0.1, r * 1.35);
  body.addColorStop(0, '#FF6FB4'); body.addColorStop(0.45, C.MAG); body.addColorStop(1, '#7A0A41');
  ctx.fillStyle = body; ctx.fill();
  ctx.clip();
  // reflejo inferior (luz transmitida)
  const tr = ctx.createRadialGradient(x + r * 0.2, y + r * 0.65, 0, x + r * 0.2, y + r * 0.65, r * 0.8);
  tr.addColorStop(0, 'rgba(255,170,210,0.55)'); tr.addColorStop(1, 'rgba(255,170,210,0)');
  ctx.fillStyle = tr; ctx.fillRect(x - r * 2, y - r * 3, r * 4, r * 5);
  ctx.restore();
  // especular
  ctx.save(); ctx.globalAlpha = alpha * 0.9;
  ctx.beginPath(); ctx.ellipse(x - r * 0.38, y - r * 0.28, r * 0.2, r * 0.32, -0.5, 0, Math.PI * 2);
  const sp = ctx.createRadialGradient(x - r * 0.38, y - r * 0.28, 0, x - r * 0.38, y - r * 0.28, r * 0.32);
  sp.addColorStop(0, 'rgba(255,255,255,0.95)'); sp.addColorStop(1, 'rgba(255,255,255,0)');
  ctx.fillStyle = sp; ctx.fill();
  ctx.restore();
}

export const FLAGS = { noCallouts: false };
// Callout técnico: punto ancla + línea guía + texto mono escrito carácter a carácter.
export function callout(ctx, { ax, ay, tx, ty, text, fig = '', p = 1, out = 0, color = C.OFF, lineColor = C.MAG, size = 50, align = 'left' }) {
  if (p <= 0 || out >= 1 || FLAGS.noCallouts) return;
  const a = 1 - out;
  ctx.save();
  ctx.globalAlpha = a;
  const pl = E.outCubic(clamp(p * 2.2));
  // punto
  ctx.fillStyle = lineColor;
  ctx.beginPath(); ctx.arc(ax, ay, 7 * E.outBack(clamp(p * 4)), 0, Math.PI * 2); ctx.fill();
  ctx.strokeStyle = lineColor; ctx.lineWidth = 2;
  ctx.beginPath(); ctx.arc(ax, ay, 16 * clamp(p * 3), 0, Math.PI * 2); ctx.globalAlpha = a * 0.5; ctx.stroke(); ctx.globalAlpha = a;
  // línea guía en codo
  const ex = tx + (align === 'left' ? -18 : 18), ey = ty - size * 0.35;
  const mx = ax + (ex - ax) * 0.5;
  const pts = [[ax, ay], [ax, ay + (ey - ay) * 0.0], [ex - (ex - ax) * 0.25, ey], [ex, ey]];
  const segs = [[ax, ay, pts[2][0], ey], [pts[2][0], ey, ex, ey]];
  const lens = segs.map(s => Math.hypot(s[2] - s[0], s[3] - s[1]));
  let rem = (lens[0] + lens[1]) * pl;
  ctx.beginPath(); ctx.moveTo(ax, ay);
  for (let i = 0; i < 2; i++) {
    const s = segs[i], L = lens[i], k = clamp(rem / L);
    ctx.lineTo(lerp(s[0], s[2], k), lerp(s[1], s[3], k)); rem -= L; if (rem <= 0) break;
  }
  ctx.stroke();
  // texto
  const tp = clamp((p - 0.3) / 0.7);
  const n = Math.round(text.length * tp);
  ctx.font = `700 ${size}px ${FONT_MONO}`; ctx.textAlign = align; ctx.textBaseline = 'alphabetic';
  ctx.fillStyle = color;
  const shown = text.slice(0, n);
  ctx.fillText(shown, tx, ty);
  if (n < text.length && n > 0) { // cursor
    const w = ctx.measureText(shown).width;
    ctx.fillStyle = lineColor; ctx.fillRect(align === 'left' ? tx + w + 4 : tx + 4, ty - size * 0.78, size * 0.55, size * 0.9);
  }
  if (fig) {
    ctx.font = `400 ${Math.round(size * 0.46)}px ${FONT_MONO}`; ctx.fillStyle = hexA(C.GREY, 1);
    ctx.globalAlpha = a * clamp(tp * 2);
    ctx.fillText(fig, tx, ty - size * 1.05);
  }
  ctx.restore();
}

// Logo Diburama provisional (reconstruido a partir de la web). Sustituir por el SVG oficial.
// La "a": cuenco circular + fuste vertical a la derecha. Unidad: s = radio exterior del cuenco.
export function logoMarkPath(ctx, cx, cy, s) {
  const R = s, r = s * 0.46, stemL = s * 0.08, stemR = s;
  ctx.beginPath();
  ctx.arc(cx, cy, R, 0, Math.PI * 2);
  ctx.moveTo(cx + r, cy); ctx.arc(cx, cy, r, 0, Math.PI * 2, true);
  ctx.rect(cx + stemL + s * 0.38, cy - R, stemR - stemL - s * 0.38, R * 2);
}
// Posición de la gota del logo respecto al centro de la "a".
export const LOGO_DROP = { dx: 0.73, dy: -1.62, r: 0.26 };
export function drawLogoMark(ctx, cx, cy, s, color = C.OFF) {
  ctx.save(); ctx.fillStyle = color; logoMarkPath(ctx, cx, cy, s); ctx.fill('nonzero'); ctx.restore();
  // cuenco hueco: rellenamos anillo con evenodd
}
export function drawLogoA(ctx, cx, cy, s, color = C.OFF) {
  ctx.save(); ctx.fillStyle = color;
  ctx.beginPath(); ctx.arc(cx, cy, s, 0, Math.PI * 2); ctx.arc(cx, cy, s * 0.47, 0, Math.PI * 2, true); ctx.fill();
  const x0 = cx + s * 0.47, x1 = cx + s;
  ctx.beginPath();
  ctx.moveTo(x0, cy); ctx.lineTo(x0, cy - s * 0.95); ctx.quadraticCurveTo(x0, cy - s * 1.06, x0 + s * 0.1, cy - s * 1.06);
  ctx.lineTo(x1, cy - s * 1.06); ctx.lineTo(x1, cy + s); ctx.lineTo(x0, cy + s); ctx.closePath(); ctx.fill();
  ctx.restore();
}
export function drawWordmark(ctx, cx, cy, size, color = C.OFF, alpha = 1, spacing = 0.18) {
  ctx.save(); ctx.globalAlpha = alpha; ctx.fillStyle = color;
  ctx.font = `400 ${size}px ${FONT_HEAD}`; ctx.textBaseline = 'middle'; ctx.textAlign = 'left';
  const txt = 'DIBURAMA';
  const sx = 0.82; // condensado
  let widths = [...txt].map(ch => ctx.measureText(ch).width * sx);
  const total = widths.reduce((a, b) => a + b, 0) + spacing * size * (txt.length - 1);
  let x = cx - total / 2;
  for (let i = 0; i < txt.length; i++) {
    ctx.save(); ctx.translate(x, cy); ctx.scale(sx, 1); ctx.fillText(txt[i], 0, 0); ctx.restore();
    x += widths[i] + spacing * size;
  }
  ctx.restore();
  return total;
}
