"""QA: consecutive frames around each transition + full-film contact sheet.
usage: qa_strips.py video.mp4 outdir [--fps 24] [--sheet name.jpg]"""
import sys, os, json, subprocess, numpy as np, cv2
from PIL import Image, ImageDraw, ImageFont
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(os.path.dirname(HERE))
EDL = json.load(open(os.path.join(ROOT, "project", "edit_decisions.json")))
FONT = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSansMono-Bold.ttf", 18)
video, out = sys.argv[1], sys.argv[2]; os.makedirs(out, exist_ok=True)
fps = float(sys.argv[sys.argv.index("--fps") + 1]) if "--fps" in sys.argv else 24.0
raw = subprocess.run(["ffmpeg", "-v", "quiet", "-i", video, "-vf", "scale=270:480", "-f", "rawvideo", "-pix_fmt", "rgb24", "-"], capture_output=True).stdout
fr = np.frombuffer(raw, np.uint8).reshape(-1, 480, 270, 3)
print("frames", len(fr))
def lab(im, txt):
    im = Image.fromarray(im.copy()); d = ImageDraw.Draw(im); d.rectangle([0, 0, 120, 22], fill=(0, 0, 0)); d.text((3, 1), txt, fill=(255, 220, 0), font=FONT); return np.array(im)
cuts = [(tr.get("t", tr.get("t0", 0) / 2 + tr.get("t1", 0) / 2), tr["from"] + ">" + tr["to"]) for tr in EDL["transitions"]]
cuts += [(EDL["graphics"]["start"], "S13>GFX")]
for t, name in cuts:
    c = int(round(t * fps)); idx = [i for i in range(c - 4, c + 4) if 0 <= i < len(fr)]
    strip = np.hstack([lab(fr[i], f"{i} {i / fps:.2f}") for i in idx])
    Image.fromarray(strip).save(os.path.join(out, f"tr_{name.replace('>', '_')}.jpg"), quality=85)
if "--sheet" in sys.argv:
    step = max(1, int(round(fps / 4)))  # 4 frames per second
    idx = list(range(0, len(fr), step)); cols = 10
    th = [cv2.resize(fr[i], (162, 288), interpolation=cv2.INTER_AREA) for i in idx]
    th = [lab(x, f"{i / fps:5.2f}s") for x, i in zip(th, idx)]
    rows = [np.hstack(th[r:r + cols] + [np.zeros_like(th[0])] * (cols - len(th[r:r + cols]))) for r in range(0, len(th), cols)]
    Image.fromarray(np.vstack(rows)).save(sys.argv[sys.argv.index("--sheet") + 1], quality=88)
