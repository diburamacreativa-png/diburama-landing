# DIBURAMA — LA GOTA · source project

9:16 · 1080×1920 · 30 fps · 27 s (810 frames) · perfect loop.

```
npm install
pip install numpy scipy pillow imageio-ffmpeg
python3 audio/score.py                                     # music + sound design → audio/score_raw.wav
node tools/render.mjs --out frames --workers 4             # PNG frames (headless Chromium + WebGL)
tools/build.sh                                             # MASTER.mp4 + ANIMATIC.mp4 in out/
tools/qa.sh                                                # duration, black frames, silence, LUFS, loop
```
Interactive preview: `npx http-server . -p 8080` → `http://localhost:8080/index.html?preview` (scrub bar).
Frame render: `node tools/render.mjs --out out/qa/x --list 24,90,240`.

| Scene | File | Time |
|---|---|---|
| 01 Blueprint → drop → ES/ERA → ink along the lines | `src/scenes/s01_blueprint.js` | 0–3.0 |
| 02 Lines → 3D machine → exploded view → nut → capsule → molecule | `src/scenes/s02_machine.js` | 3.0–9.0 |
| 03 Molecule → interface | `src/scenes/s03_software.js` | 8.95–10.5 |
| 04 Chart → horizon (landscape) | `src/scenes/s04_horizon.js` | 10.5–13.0 |
| 05/06 Real person → 2D · collapse → drop · silence | `src/scenes/s05_person.js` | 13.0–18.6 |
| 07/08 World inside the drop → logo · close · loop | `src/scenes/s07_reveal.js` | 18.6–27.0 |

Master timeline: `src/timeline.js`. Palette, easings, drop and logo: `src/lib.js`. External prompts: `prompts/`.
