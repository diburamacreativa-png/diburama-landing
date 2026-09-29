// MASTER · 1080×1920 · 30 fps · 27 s (810 fotogramas). Motor determinista: renderFrame(f) pinta el fotograma f.
import { W, H, FPS, TOTAL_FRAMES, C, FONT_HEAD, FONT_MONO } from './lib.js';
import { post } from './post.js';
import { TIMELINE } from './timeline.js';

const out = document.getElementById('out');
const ctx = out.getContext('2d');
const params = new URLSearchParams(location.search);
const ANIMATIC = params.has('animatic');

async function loadFonts() {
  const specs = [`700 40px ${FONT_HEAD}`, `400 40px ${FONT_HEAD}`, `500 40px ${FONT_HEAD}`, `400 40px ${FONT_MONO}`, `700 40px ${FONT_MONO}`];
  await Promise.all(specs.map(s => document.fonts.load(s, 'ÁÉÍÓÚÑ¿?abcABC0123')));
}

let ready = false;
export async function setup() {
  await loadFonts();
  for (const s of TIMELINE) if (s.init) await s.init();
  ready = true;
}

export async function renderFrame(f) {
  const t = f / FPS;
  ctx.setTransform(1, 0, 0, 1, 0, 0);
  ctx.globalAlpha = 1; ctx.globalCompositeOperation = 'source-over'; ctx.filter = 'none';
  ctx.fillStyle = C.NIGHT; ctx.fillRect(0, 0, W, H);
  const active = TIMELINE.filter(s => t >= s.start && t < s.end);
  for (const s of active) { ctx.save(); await s.draw(ctx, t, f); ctx.restore(); }
  post(ctx, f, active[active.length - 1]?.post || {});
  if (ANIMATIC) {
    ctx.save(); ctx.fillStyle = 'rgba(0,0,0,0.6)'; ctx.fillRect(0, 0, W, 64);
    ctx.font = `700 30px ${FONT_MONO}`; ctx.fillStyle = '#fff'; ctx.textBaseline = 'middle';
    ctx.fillText(`${t.toFixed(2)}s  f${String(f).padStart(3, '0')}  ${active.map(s => s.name).join(' + ')}`, 20, 32);
    ctx.restore();
  }
}
window.renderFrame = renderFrame;
window.TOTAL_FRAMES = TOTAL_FRAMES;
window.__ready = setup().then(() => true);

if (params.has('preview')) {
  document.body.classList.add('preview');
  const scrub = document.getElementById('scrub'), tc = document.getElementById('tc'), btn = document.getElementById('play');
  let playing = false, cur = Number(params.get('f') || 0);
  const show = async (f) => { cur = f; scrub.value = f; tc.textContent = (f / FPS).toFixed(2) + 's'; await renderFrame(f); };
  window.__ready.then(() => show(cur));
  scrub.oninput = () => show(Number(scrub.value));
  btn.onclick = async () => { playing = !playing; btn.textContent = playing ? '❚❚' : '▶'; while (playing) { const t0 = performance.now(); await show((cur + 1) % TOTAL_FRAMES); const dt = performance.now() - t0; await new Promise(r => setTimeout(r, Math.max(0, 1000 / FPS - dt))); } };
}
