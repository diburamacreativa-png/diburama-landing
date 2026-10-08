// Exporta a audio/events.json todos los momentos visuales que llevan sonido:
// movimientos de ventanas, cortes dentro de ventanas, revelados de texto,
// números, líneas, cambios de fondo y cierre. Lo lee audio/soundtrack.py.
// Uso: npx tsx scripts/export-events.ts
import {writeFileSync, mkdirSync} from 'node:fs';
import {CLIPS, FPS, SEGMENTS, TIMING, WIDTH, sec} from '../src/config';
import {ACCENTS, CARDS, DARK_RANGES, LABEL_RANGES, NUMBERS, RULES} from '../src/choreography';

type Ev = {t: number; type: string; pan: number; size: number; dur?: number; note?: string};
const ev: Ev[] = [];
const f2s = (f: number) => f / FPS;
const panOf = (cx: number) => Math.max(-1, Math.min(1, (cx - WIDTH / 2) / (WIDTH / 2)));

// Ventanas: entrada, salida o reorganización.
for (const c of CARDS) {
  let cur = {...c.start};
  for (const m of c.moves) {
    const next = {x: m.x ?? cur.x, y: m.y ?? cur.y, w: m.w ?? cur.w};
    const dur = m.dur ?? TIMING.card;
    const off = (r: typeof cur) => r.x >= WIDTH - 10 || r.x + r.w <= 10;
    const type = off(cur) && !off(next) ? 'enter' : !off(cur) && off(next) ? 'exit' : 'move';
    const dist = Math.hypot(next.x - cur.x, next.y - cur.y) + Math.abs(next.w - cur.w) * 1.5;
    if (dist > 20) {
      ev.push({
        t: f2s(sec(m.at)),
        type,
        pan: panOf(type === 'exit' ? next.x + next.w / 2 : cur.x + cur.w / 2),
        size: Math.min(1, (next.w / 1000) * 0.6 + Math.min(1, dist / 1200) * 0.4),
        dur: f2s(dur),
      });
    }
    cur = next;
  }
  // Cambio de fragmento dentro de una ventana ya visible.
  c.content.slice(1).forEach((k) => {
    ev.push({t: f2s(sec(k.at)), type: 'cut', pan: 0, size: 0.5, note: CLIPS[k.clip].src});
  });
}

// Títulos (misma lógica que components/Type.tsx).
let prev = '';
let bi = 0;
for (const s of SEGMENTS) {
  const key = s.title.join('|');
  if (key !== prev && s.title.length) {
    const enter = sec(s.from) + (bi === 0 ? -3 : 3);
    s.title.forEach((_, i) => ev.push({t: Math.max(0, f2s(enter + i * TIMING.lineStagger)), type: 'type', pan: -0.3, size: 1}));
    bi++;
  }
  prev = key;
}
// Etiquetas mono.
let prevK = '';
for (const s of SEGMENTS) {
  if (s.kicker && s.kicker !== prevK) ev.push({t: s.from + 1 / FPS, type: 'tick', pan: -0.5, size: 0.6});
  prevK = s.kicker;
}
for (const [a] of LABEL_RANGES) ev.push({t: f2s(sec(a) + 4), type: 'blip', pan: -0.4, size: 0.5});
for (const n of NUMBERS) ev.push({t: n.from, type: 'pop', pan: n.align === 'left' ? -0.5 : 0.5, size: 1});
for (const r of RULES) ev.push({t: r.from, type: 'line', pan: 0, size: 1, dur: 0.45});
for (const [a, b] of DARK_RANGES) {
  ev.push({t: a, type: 'sweep', pan: 0, size: 1});
  if (b < 26) ev.push({t: b, type: 'sweep', pan: 0, size: 0.6});
}
ev.push({t: ACCENTS.gesture, type: 'hit', pan: 0, size: 1});
ev.push({t: 24 + 2 / FPS, type: 'logo', pan: 0, size: 1});

ev.sort((a, b) => a.t - b.t);
mkdirSync('audio', {recursive: true});
writeFileSync('audio/events.json', JSON.stringify({fps: FPS, duration: 26, events: ev}, null, 1));
console.log(`audio/events.json · ${ev.length} eventos`);
