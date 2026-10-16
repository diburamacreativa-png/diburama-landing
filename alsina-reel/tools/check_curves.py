"""Print per-frame geometry of the finale (debug aid)."""
import sys, math, json
sys.path.insert(0, __import__('os').path.dirname(__file__))
import numpy as np, reel
from scipy import ndimage
L = reel.VecLogo(); reel.DOTV = L.dot
rows = json.load(open('build/video_motion.json')); ls = np.log([r['scale'] for r in rows]); ls = np.minimum(ls, -1e-4)
ls = ndimage.gaussian_filter1d(ls, 7.0, mode='nearest'); Z = np.concatenate([[0], np.cumsum(ls)])
C = reel.Curves(Z, math.sqrt(L.dot[2] * L.dot[3] * 4 / math.pi) * reel.SG0)
for k in range(int(sys.argv[1]), int(sys.argv[2])):
    t = k / 25; st = reel.sphere_state(t, C); d = st['d']
    R = st['S'] * math.sqrt((d + 1) / (d - 1)) if d > 1.0001 else float('inf')
    print('%d t=%.2f d=%.3f G=%.0f Redge=%.0f sig=%.2f mu=%.2f wh=%.2f c=%s' % (k, t, d, st['G'], R, st['sigma'], st['mu'], st['white'], np.round(st['c'])))
