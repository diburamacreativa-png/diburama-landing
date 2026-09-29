// Render por lotes: N navegadores headless en paralelo → PNG por fotograma.
// Uso: node tools/render.mjs --out frames --from 0 --to 810 --workers 3 [--scale 0.5] [--animatic] [--step 1] [--list 0,24,60]
import { chromium } from 'playwright-core';
import http from 'node:http';
import fs from 'node:fs';
import path from 'node:path';
const args = Object.fromEntries(process.argv.slice(2).reduce((a, v, i, arr) => { if (v.startsWith('--')) a.push([v.slice(2), arr[i + 1] && !arr[i + 1].startsWith('--') ? arr[i + 1] : true]); return a; }, []));
const ROOT = path.resolve(path.dirname(new URL(import.meta.url).pathname), '..');
const OUT = path.resolve(ROOT, args.out || 'frames');
const FROM = Number(args.from ?? 0), TO = Number(args.to ?? 810), WORKERS = Number(args.workers ?? 3), SCALE = Number(args.scale ?? 1), STEP = Number(args.step ?? 1);
fs.mkdirSync(OUT, { recursive: true });
const types = { '.html': 'text/html', '.js': 'text/javascript', '.woff2': 'font/woff2', '.png': 'image/png', '.jpg': 'image/jpeg', '.json': 'application/json' };
const server = http.createServer((req, res) => {
  const p = path.join(ROOT, decodeURIComponent(req.url.split('?')[0]));
  fs.readFile(p, (err, data) => { if (err) { res.writeHead(404); res.end(); return; } res.writeHead(200, { 'Content-Type': types[path.extname(p)] || 'application/octet-stream' }); res.end(data); });
}).listen(0);
const port = server.address().port;
let frames = [];
if (args.list) frames = String(args.list).split(',').map(Number); else for (let f = FROM; f < TO; f += STEP) frames.push(f);
const queue = [...frames];
const t0 = Date.now(); let done = 0;
async function worker(id) {
  const browser = await chromium.launch({ executablePath: '/opt/pw-browsers/chromium-1194/chrome-linux/chrome', args: ['--use-angle=swiftshader', '--enable-unsafe-swiftshader', '--ignore-gpu-blocklist', '--disable-gpu-vsync'] });
  const page = await browser.newPage({ viewport: { width: 1080, height: 1920 }, deviceScaleFactor: SCALE });
  page.on('console', m => { if (m.type() === 'error' || m.type() === 'warning') console.log(`[w${id}]`, m.text()); });
  page.on('pageerror', e => console.log(`[w${id}] PAGEERROR`, e.message));
  await page.goto(`http://localhost:${port}/index.html${args.animatic ? '?animatic' : ''}`);
  await page.evaluate(() => window.__ready);
  const canvas = await page.$('#out');
  while (queue.length) {
    const f = queue.shift();
    await page.evaluate((f) => window.renderFrame(f), f);
    await canvas.screenshot({ path: path.join(OUT, `f${String(f).padStart(4, '0')}.png`), type: 'png' });
    done++;
    if (done % 20 === 0) console.log(`${done}/${frames.length}  ${((Date.now() - t0) / 1000).toFixed(0)}s`);
  }
  await browser.close();
}
await Promise.all(Array.from({ length: Math.min(WORKERS, frames.length) }, (_, i) => worker(i)));
server.close();
console.log(`OK ${frames.length} fotogramas en ${((Date.now() - t0) / 1000).toFixed(1)}s → ${OUT}`);
