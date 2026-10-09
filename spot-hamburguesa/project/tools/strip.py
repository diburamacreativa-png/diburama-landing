"""Render a strip of frames (30 fps) between two times for quick visual review.
usage: strip.py t0 t1 step out.jpg [width]"""
import sys, os, numpy as np, cv2
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import engine
t0, t1, step, out = float(sys.argv[1]), float(sys.argv[2]), float(sys.argv[3]), sys.argv[4]
w = int(sys.argv[5]) if len(sys.argv) > 5 else 216
ims = []
for t in np.arange(t0, t1 + 1e-6, step):
    n = int(round(t * 30)); im = engine.to8(engine.frame_at(n / 30, 30, n))
    im = cv2.cvtColor(cv2.resize(im, (w, int(w * 16 / 9)), interpolation=cv2.INTER_AREA), cv2.COLOR_RGB2BGR)
    cv2.putText(im, f"{n/30:.2f}", (4, 18), 0, 0.5, (0, 255, 255), 1); ims.append(im)
cols = 8; rows = [np.hstack(ims[i:i + cols] + [np.zeros_like(ims[0])] * (cols - len(ims[i:i + cols]))) for i in range(0, len(ims), cols)]
cv2.imwrite(out, np.vstack(rows))
