"""Track the central walker (backlit dark silhouette) in 3A and 4A: head top, torso centre, feet, per unique frame.
Writes project/walker_track.json and a QA image with the detected boxes."""
import sys, os, json, numpy as np, cv2
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, HERE); import engine

def silhouette(f, cx, cy, half_w, half_h):
    h, w = f.shape[:2]
    x0, x1 = int(max(0, (cx - half_w) * w)), int(min(w, (cx + half_w) * w))
    y0, y1 = int(max(0, (cy - half_h) * h)), int(min(h, (cy + half_h) * h))
    roi = cv2.cvtColor(f[y0:y1, x0:x1], cv2.COLOR_RGB2GRAY).astype(np.float32)
    roi = cv2.GaussianBlur(roi, (0, 0), 1.5)
    bg = cv2.GaussianBlur(roi, (0, 0), 25)
    dark = (roi < bg * 0.62).astype(np.uint8)
    dark = cv2.morphologyEx(dark, cv2.MORPH_OPEN, np.ones((3, 3), np.uint8))
    dark = cv2.morphologyEx(dark, cv2.MORPH_CLOSE, np.ones((7, 3), np.uint8))
    n, lab, st, cen = cv2.connectedComponentsWithStats(dark)
    best, bs = None, -1
    for i in range(1, n):
        x, y, ww, hh, a = st[i]
        if hh < 0.02 * h or a < 40: continue
        ccx = (x0 + x + ww / 2) / w
        score = a * hh / (1 + 40 * abs(ccx - cx))          # tall, big, near the expected column
        if score > bs: bs, best = score, i
    if best is None: return None
    x, y, ww, hh, a = st[best]
    m = (lab == best)
    ys, xs = np.where(m)
    top = (y0 + ys.min()) / h; bot = (y0 + ys.max()) / h
    # torso centre: centroid of the upper 55 % of the body (legs swing, torso does not)
    up = ys < ys.min() + 0.55 * (ys.max() - ys.min())
    tx = (x0 + xs[up].mean()) / w; ty = (y0 + ys[up].mean()) / h
    return dict(head=top, feet=bot, x=tx, torso_y=ty, height=bot - top, box=[(x0 + x) / w, (y0 + y) / h, ww / w, hh / h])

def track(name, frames, start, half_w, half_h):
    src = engine.source(name); out = {}; cx, cy = start
    for i in frames:
        r = silhouette(src.frames[i], cx, cy, half_w, half_h)
        if r: out[i] = r; cx, cy = r["x"], r["torso_y"]
    return out

if __name__ == "__main__":
    t3 = track("plano 3A", range(119, 84, -1), (0.565, 0.52), 0.09, 0.12)
    t4 = track("plano 4A", range(0, 30), (0.56, 0.54), 0.14, 0.24)
    json.dump({"3A": t3, "4A": t4}, open(os.path.join(ROOT, "project", "walker_track.json"), "w"), indent=0)
    for k, d in (("3A", t3), ("4A", t4)):
        print(k)
        for i in sorted(d):
            r = d[i]; print(f"  {i:3d} head {r['head']:.3f} torso ({r['x']:.3f},{r['torso_y']:.3f}) feet {r['feet']:.3f} h {r['height']:.3f}")
    ims = []
    for name, d, idx in (("plano 3A", t3, [100, 110, 119]), ("plano 4A", t4, [0, 6, 12])):
        src = engine.source(name)
        for i in idx:
            f = cv2.cvtColor(src.frames[i], cv2.COLOR_RGB2BGR).copy(); h, w = f.shape[:2]
            if i in d:
                r = d[i]; bx, by, bw, bh = r["box"]
                cv2.rectangle(f, (int(bx * w), int(by * h)), (int((bx + bw) * w), int((by + bh) * h)), (0, 255, 0), 2)
                cv2.circle(f, (int(r["x"] * w), int(r["torso_y"] * h)), 6, (0, 0, 255), -1)
            ims.append(cv2.resize(f, (288, 512)))
    cv2.imwrite(sys.argv[1] if len(sys.argv) > 1 else "/tmp/walker.jpg", np.hstack(ims))
