"""Motion analysis of 'Plano inicio zoom out' (1512x2688, 29.97 fps, 106 frames):
 - frame-to-frame similarity (scale / rotation / translation)            -> build/inicio_motion.json
 - registration of each late frame against frame 240 of pano.mp4 (same flight, same camera)
   so the new opening lives in the same coordinate system as the panorama handoff."""
import numpy as np, cv2, json
sift = cv2.SIFT_create(4000); bf = cv2.BFMatcher()
SC = 0.5
def feat_img(img, sc):
    g = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    g = cv2.resize(g, None, fx=sc, fy=sc, interpolation=cv2.INTER_AREA)
    k, d = sift.detectAndCompute(g, None); return k, d, sc
def match(a, b, ratio=0.72, thr=3.0):
    m = bf.knnMatch(a[1], b[1], k=2); good = [x for x, y in m if x.distance < ratio * y.distance]
    s = np.float32([a[0][x.queryIdx].pt for x in good]) / a[2]; d = np.float32([b[0][x.trainIdx].pt for x in good]) / b[2]
    A, inl = cv2.estimateAffinePartial2D(s, d, method=cv2.RANSAC, ransacReprojThreshold=thr)
    return A, int(inl.sum())
nf = 106
F = [feat_img(cv2.imread('build/inicio_frames/f%03d.jpg' % (n + 1)), SC) for n in range(nf)]
rows = []
for n in range(1, nf):
    A, inl = match(F[n - 1], F[n])
    rows.append(dict(n=n, A=A.tolist(), inl=inl, scale=float(np.sqrt(abs(np.linalg.det(A[:, :2])))), rot=float(np.arctan2(A[1, 0], A[0, 0]))))
old240 = feat_img(cv2.imread('build/pano_frames/f241.jpg'), 0.8)
reg = {}
for n in list(range(70, nf, 3)) + [nf - 1]:
    A, inl = match(F[n], old240, 0.75, 4.0)
    reg[n] = dict(A=A.tolist(), inl=inl, scale=float(np.sqrt(abs(np.linalg.det(A[:, :2])))), rot=float(np.degrees(np.arctan2(A[1, 0], A[0, 0]))))
    print('new f%d -> old f240: scale %.4f rot %.2f t=(%.1f,%.1f) inl %d' % (n, reg[n]['scale'], reg[n]['rot'], A[0, 2], A[1, 2], inl))
json.dump(dict(frames=rows, reg240=reg), open('build/inicio_motion.json', 'w'))
ls = np.log([r['scale'] for r in rows]); print('total log-scale', ls.sum(), 'min inliers', min(r['inl'] for r in rows))
