// Postproducción común: grano fílmico, viñeta y aberración mínima.
import { W, H, mulberry32, makeCanvas } from './lib.js';
let tiles = null;
function makeTiles() {
  tiles = [];
  for (let k = 0; k < 6; k++) {
    const c = makeCanvas(512, 512), x = c.getContext('2d'), img = x.createImageData(512, 512), r = mulberry32(1000 + k);
    for (let i = 0; i < img.data.length; i += 4) { const v = (r() + r() + r()) / 3 * 255; img.data[i] = img.data[i + 1] = img.data[i + 2] = v; img.data[i + 3] = 255; }
    x.putImageData(img, 0, 0); tiles.push(c);
  }
}
export function post(ctx, frame, { grain = 0.055, vignette = 0.28 } = {}) {
  if (!tiles) makeTiles();
  const r = mulberry32(frame * 7919 + 13);
  const tile = tiles[frame % tiles.length];
  ctx.save();
  ctx.globalCompositeOperation = 'overlay'; ctx.globalAlpha = grain;
  const ox = -Math.floor(r() * 512), oy = -Math.floor(r() * 512);
  for (let y = oy; y < H; y += 512) for (let x = ox; x < W; x += 512) ctx.drawImage(tile, x, y);
  ctx.restore();
  if (vignette > 0) {
    ctx.save();
    const g = ctx.createRadialGradient(W / 2, H * 0.47, H * 0.28, W / 2, H * 0.5, H * 0.72);
    g.addColorStop(0, 'rgba(0,0,0,0)'); g.addColorStop(1, `rgba(0,0,0,${vignette})`);
    ctx.fillStyle = g; ctx.fillRect(0, 0, W, H); ctx.restore();
  }
}
