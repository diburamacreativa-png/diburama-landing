"""Measure the drone video's frame-to-frame similarity motion (scale, rotation, focus of expansion).
Output: build/video_motion.json with cumulative log-scale Zv per frame (frames 0..N)."""
import numpy as np, cv2, json, sys
N=int(sys.argv[1]) if len(sys.argv)>1 else 252
sift=cv2.SIFT_create(2500); bf=cv2.BFMatcher()
def feat(n):
    g=cv2.cvtColor(cv2.imread('build/pano_frames/f%03d.jpg'%(n+1)),cv2.COLOR_BGR2GRAY)
    g=cv2.resize(g,(960,540),interpolation=cv2.INTER_AREA); return sift.detectAndCompute(g,None)
prev=feat(0); rows=[]
for n in range(1,N+1):
    cur=feat(n)
    m=bf.knnMatch(prev[1],cur[1],k=2); good=[a for a,b in m if a.distance<0.7*b.distance]
    src=np.float32([prev[0][a.queryIdx].pt for a in good])*2; dst=np.float32([cur[0][a.trainIdx].pt for a in good])*2
    A,inl=cv2.estimateAffinePartial2D(src,dst,method=cv2.RANSAC,ransacReprojThreshold=2)
    rows.append(dict(n=n,scale=float(np.sqrt(abs(np.linalg.det(A[:,:2])))),rot=float(np.arctan2(A[1,0],A[0,0])),A=A.tolist(),inl=int(inl.sum())))
    prev=cur
json.dump(rows,open('build/video_motion.json','w'))
ls=np.log([r['scale'] for r in rows]); print('total logscale',ls.sum(), 'min inliers',min(r['inl'] for r in rows))
