"""v3 join analysis: 'Plano inicio zoom out' frame m == pano.mp4 frame 122+m (higher-res vertical crop).
Outputs build/v3_join.json:
  crop[m]   : similarity new-frame-m px -> old-frame-(122+m) px (exact inset placement)
  to240[tau]: similarity old-frame-tau px -> old-frame-240 px, tau in [200, 252] (direct registration)
  color     : per-channel linear map old -> new colours (to hide the source switch)"""
import numpy as np, cv2, json
sift = cv2.SIFT_create(6000); bf = cv2.BFMatcher()
def feat(img, sc):
    g = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY); g = cv2.resize(g, None, fx=sc, fy=sc, interpolation=cv2.INTER_AREA)
    k, d = sift.detectAndCompute(g, None); return k, d, sc
def match(a, b, ratio=0.75, thr=2.0):
    m = bf.knnMatch(a[1], b[1], k=2); good = [x for x, y in m if x.distance < ratio * y.distance]
    s = np.float32([a[0][x.queryIdx].pt for x in good]) / a[2]; d = np.float32([b[0][x.trainIdx].pt for x in good]) / b[2]
    A, inl = cv2.estimateAffinePartial2D(s, d, method=cv2.RANSAC, ransacReprojThreshold=thr, maxIters=5000, refineIters=50)
    return A, int(inl.sum())
old = lambda t: cv2.imread('build/pano_frames/f%03d.jpg' % (t + 1))
new = lambda m: cv2.imread('build/inicio_frames/f%03d.jpg' % (m + 1))
out = dict(crop={}, to240={}, color=None)
OF = {}
for m in range(0, 106):
    t = 122 + m
    if t not in OF: OF[t] = feat(old(t), 0.8)
    A, inl = match(feat(new(m), 0.45), OF[t])
    out['crop'][m] = dict(A=A.tolist(), inl=inl)
    if m % 15 == 0: print('crop m=%d inl %d scale %.4f ctr %s' % (m, inl, np.sqrt(abs(np.linalg.det(A[:, :2]))), np.round(cv2.transform(np.float32([[[756, 1344]]]), A)[0, 0], 1)))
F240 = feat(old(240), 0.8)
for t in range(200, 253):
    A, inl = match(feat(old(t), 0.8), F240)
    out['to240'][t] = dict(A=A.tolist(), inl=inl)
    if t % 4 == 0: print('to240 t=%d inl %d scale %.4f' % (t, inl, np.sqrt(abs(np.linalg.det(A[:, :2])))))
# colour: sample new frames and the matching old pixels
X = []; Y = []
for m in range(0, 106, 7):
    A = np.array(out['crop'][m]['A']); n = new(m).astype(np.float32); o = old(122 + m).astype(np.float32)
    Ai = cv2.invertAffineTransform(A)
    warped = cv2.warpAffine(o, A @ np.diag([1, 1, 1])[:, :3] if False else np.float32(np.linalg.inv(np.vstack([A, [0, 0, 1]]))[:2]), (n.shape[1], n.shape[0]))
    # warped = old resampled in new coords
    ok = warped.sum(2) > 0
    nb = cv2.GaussianBlur(n, (0, 0), 6); wb = cv2.GaussianBlur(warped, (0, 0), 2.5)
    idx = np.argwhere(ok[::16, ::16]) * 16
    X.append(wb[idx[:, 0], idx[:, 1]]); Y.append(nb[idx[:, 0], idx[:, 1]])
X = np.concatenate(X); Y = np.concatenate(Y)
coef = []
for c in range(3):
    M = np.column_stack([X[:, c], np.ones(len(X))]); sol, *_ = np.linalg.lstsq(M, Y[:, c], rcond=None); coef.append(sol.tolist())
    print('colour ch%d: new = %.3f*old + %.2f   (mean old %.1f new %.1f)' % (c, sol[0], sol[1], X[:, c].mean(), Y[:, c].mean()))
out['color'] = coef
json.dump(out, open('build/v3_join.json', 'w'))
