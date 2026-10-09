"""FASE 1 · Analysis of the source clips.
Writes qa/analysis/<clip>_sheet.jpg (every Nth frame, numbered) and
qa/analysis/metrics.json (per-frame luma, sharpness, motion magnitude/direction)."""
import cv2, json, sys, os, numpy as np
from PIL import Image, ImageDraw, ImageFont
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
CLIPS = ["Plano 1A","Plano 1B","plano 2A","plano 3A","plano 4A","plano 5A","plano 6A",
         "plano 6B","plano 7A","plano 8A","plano 9A","plano 9B","plano 9C"]
OUT = os.path.join(ROOT, "qa", "analysis"); os.makedirs(OUT, exist_ok=True)
FONT = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 22)

def read(name):
    cap = cv2.VideoCapture(os.path.join(ROOT, "clips", name + ".mp4")); fr = []
    while True:
        ok, f = cap.read()
        if not ok: break
        fr.append(f)
    return fr

metrics = {}
step = int(sys.argv[1]) if len(sys.argv) > 1 else 4
for name in CLIPS:
    fr = read(name); m = []; prev = None
    for i, f in enumerate(fr):
        g = cv2.cvtColor(cv2.resize(f, (360, 640)), cv2.COLOR_BGR2GRAY)
        d = {"i": i, "luma": float(g.mean()), "sharp": float(cv2.Laplacian(g, cv2.CV_64F).var())}
        if prev is not None:
            fl = cv2.calcOpticalFlowFarneback(prev, g, None, 0.5, 3, 21, 3, 5, 1.1, 0)
            # radial component: + = zoom-in (expanding)
            h, w = g.shape; yy, xx = np.mgrid[0:h, 0:w]; rx, ry = xx - w/2, yy - h/2
            rn = np.sqrt(rx**2 + ry**2) + 1e-6
            d.update(dx=float(fl[...,0].mean()), dy=float(fl[...,1].mean()),
                     mag=float(np.linalg.norm(fl, axis=2).mean()),
                     zoom=float(((fl[...,0]*rx + fl[...,1]*ry)/rn).mean()),
                     diff=float(np.abs(g.astype(int) - prev.astype(int)).mean()))
        prev = g; m.append(d)
    metrics[name] = m
    idx = list(range(0, len(fr), step))
    if idx[-1] != len(fr) - 1: idx.append(len(fr) - 1)
    tw, th = 180, 320; cols = 8; rows = (len(idx) + cols - 1) // cols
    sheet = Image.new("RGB", (cols*tw, rows*th), (20, 20, 20)); dr = ImageDraw.Draw(sheet)
    for k, i in enumerate(idx):
        t = Image.fromarray(cv2.cvtColor(cv2.resize(fr[i], (tw, th), interpolation=cv2.INTER_AREA), cv2.COLOR_BGR2RGB))
        x, y = (k % cols)*tw, (k // cols)*th; sheet.paste(t, (x, y))
        dr.rectangle([x, y, x+70, y+28], fill=(0, 0, 0)); dr.text((x+4, y+2), f"{i}", fill=(255, 230, 0), font=FONT)
    sheet.save(os.path.join(OUT, name.replace(" ", "_") + "_sheet.jpg"), quality=85)
    print(name, len(fr), "frames")
json.dump(metrics, open(os.path.join(OUT, "metrics.json"), "w"), indent=0)
