"""Vector reconstruction of the original Alsina logo (from the official white PNG extracted from
LOGO VERTICAL.mp4) and an anti-aliased rasteriser with arbitrary affine transforms and clip masks.

Each glyph component is traced at 8x (bicubic upsampling of the alpha, iso-line at 50%), giving
sub-pixel outlines that reproduce the original at 1:1 and stay crisp when the group is scaled."""
import os
import numpy as np
import cv2
from scipy import ndimage

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LOGO_OFFSET = (189, 836)
UP = 8
SS = 4          # rasteriser supersampling (per axis)


def trace():
    png = cv2.imread(os.path.join(ROOT, 'assets/source/alsina_logo_blanco_transparente.png'), cv2.IMREAD_UNCHANGED)
    a = png[..., 3].astype(np.float32) / 255.0
    lab, n = ndimage.label(a > 0.5)
    idx = ndimage.distance_transform_edt(lab == 0, return_distances=False, return_indices=True)
    lab_full = lab[idx[0], idx[1]] * (a > 0.01)
    parts = {}
    for k in range(1, n + 1):
        ak = a * (lab_full == k)
        big = cv2.resize(ak, None, fx=UP, fy=UP, interpolation=cv2.INTER_CUBIC)
        m = (big > 0.5).astype(np.uint8)
        cs, hier = cv2.findContours(m, cv2.RETR_CCOMP, cv2.CHAIN_APPROX_NONE)
        polys = []
        for c in cs:
            c = c[:, 0, :].astype(np.float64)
            c = cv2.approxPolyDP(c.astype(np.float32), 0.6, True)[:, 0, :].astype(np.float64)
            # pixel-centre convention: upsampled pixel i covers [i/UP, (i+1)/UP)
            p = (c + 0.5) / UP
            p[:, 0] += LOGO_OFFSET[0]; p[:, 1] += LOGO_OFFSET[1]
            polys.append(p)
        ys, xs = np.nonzero(lab == k)
        parts[k] = dict(polys=polys, x0=xs.min() + LOGO_OFFSET[0], x1=xs.max() + 1 + LOGO_OFFSET[0],
                        y0=ys.min() + LOGO_OFFSET[1], y1=ys.max() + 1 + LOGO_OFFSET[1])
    return parts


def raster(polys_list, roi, clip=None):
    """polys_list: list of polygon arrays in screen coords (even-odd fill across all).
    roi: (x0,y0,x1,y1) integer screen window. clip: optional list of polygons (screen coords) to AND with.
    Returns coverage float32 of roi size."""
    x0, y0, x1, y1 = roi
    w, h = (x1 - x0) * SS, (y1 - y0) * SS
    if w <= 0 or h <= 0:
        return np.zeros((max(y1 - y0, 0), max(x1 - x0, 0)), np.float32)
    SH = 4
    def fill(pl):
        c = np.zeros((h, w), np.uint8)
        pts = [np.round(((p - [x0, y0]) * SS) * (1 << SH)).astype(np.int32).reshape(-1, 1, 2) for p in pl]
        cv2.fillPoly(c, pts, 255, lineType=cv2.LINE_8, shift=SH)
        return c
    c = fill(polys_list)
    if clip is not None:
        c = cv2.bitwise_and(c, fill(clip))
    return cv2.resize(c.astype(np.float32) / 255.0, (x1 - x0, y1 - y0), interpolation=cv2.INTER_AREA)


if __name__ == '__main__':
    parts = trace()
    png = cv2.imread(os.path.join(ROOT, 'assets/source/alsina_logo_blanco_transparente.png'), cv2.IMREAD_UNCHANGED)
    a = png[..., 3].astype(np.float32) / 255.0
    full = np.zeros((1920, 1080), np.float32); full[836:1036, 189:890] = a
    roi = (180, 830, 900, 1040)
    cov = raster([p for k in parts for p in parts[k]['polys']], roi)
    ref = full[830:1040, 180:900]
    print('parts', len(parts), 'points', sum(len(p) for k in parts for p in parts[k]['polys']))
    print('mean |vector - png| = %.4f   max = %.3f   area ratio = %.4f' % (np.abs(cov - ref).mean(), np.abs(cov - ref).max(), cov.sum() / ref.sum()))
    vis = np.hstack([ref, cov, np.abs(cov - ref) * 4])
    cv2.imwrite(os.path.join(ROOT, 'build/vec_check.png'), (np.clip(vis, 0, 1) * 255).astype(np.uint8))
