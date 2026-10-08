// Fotogramas de control + hoja de contactos (out/stills/).
// Uso: node scripts/stills.mjs            → fotogramas por defecto
//      node scripts/stills.mjs 0,55,120   → fotogramas concretos
import {bundle} from '@remotion/bundler';
import {renderStill, selectComposition} from '@remotion/renderer';
import {execFileSync} from 'node:child_process';
import {existsSync, mkdirSync} from 'node:fs';
import path from 'node:path';

const DEFAULT = [3, 8, 14, 30, 53, 56, 75, 103, 106, 130, 153, 156, 180, 203, 206, 230, 260, 286, 292, 298, 303, 306, 350, 403, 406, 450, 503, 506, 530, 553, 556, 580, 603, 606, 612, 620, 649];
const frames = process.argv[2] ? process.argv[2].split(',').map(Number) : DEFAULT;
const chrome = '/opt/pw-browsers/chromium_headless_shell-1194/chrome-linux/headless_shell';
const browserExecutable = existsSync(chrome) ? chrome : null;

const outDir = path.resolve('out/stills');
mkdirSync(outDir, {recursive: true});
const serveUrl = await bundle({entryPoint: path.resolve('src/index.ts')});
const composition = await selectComposition({serveUrl, id: 'Reel', browserExecutable});
const files = [];
for (const f of frames) {
  const output = path.join(outDir, `f${String(f).padStart(3, '0')}.png`);
  await renderStill({composition, serveUrl, frame: f, output, scale: 0.5, browserExecutable});
  files.push(output);
  process.stdout.write(`${f} `);
}
// Hoja de contactos con número de fotograma.
const cols = 8;
execFileSync('ffmpeg', [
  '-v', 'error', '-y',
  ...files.flatMap((f) => ['-i', f]),
  '-filter_complex',
  files.map((_, i) => `[${i}]scale=270:-1,drawtext=text='${frames[i]}':x=8:y=8:fontsize=22:fontcolor=red[v${i}]`).join(';') +
    ';' + files.map((_, i) => `[v${i}]`).join('') +
    `xstack=inputs=${files.length}:layout=${files.map((_, i) => `${(i % cols) * 274}_${Math.floor(i / cols) * 484}`).join('|')}:fill=gray`,
  path.join(outDir, 'sheet.png'),
]);
console.log('\nOK', path.join(outDir, 'sheet.png'));
