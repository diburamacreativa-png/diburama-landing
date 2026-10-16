"""ALSINA — cinematic reel renderer (1080x1920, 25 fps, 160 frames).

One continuous virtual camera:
  real drone ascent (pano.mp4, rotated to portrait at native resolution)
  -> speed-matched handoff to the 360 panorama (DJI JPG) rendered with a general-perspective
     azimuthal projection (gnomonic -> stereographic tiny planet -> orthographic ball)
  -> the ball collapses on a curved path and is shape-morphed into the dot of the "i"
  -> the original white logo shapes are built from that dot -> clean hold on corporate red.

Usage:  python3 tools/reel.py [--frames a:b] [--preview] [--out build/frames]
Everything is rendered in linear light, float32, with true temporal supersampling
(180 degree shutter) for motion blur. Frames are written as 16-bit PNG.
"""
import os, sys, json, math, argparse
import numpy as np
import cv2
from scipy import ndimage

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, HERE)
from proj import srgb2lin, lin2srgb, theta_from_rho, directions

FPS = 25
NF = 160
W, H = 1080, 1920
SHUTTER = 0.5 / FPS                      # 180 degrees

# ---------------------------------------------------------------- brand constants (measured)
RED_SRGB = np.array([170, 25, 45], np.float32)          # #AA192D from LOGO VERTICAL.mp4
RED = srgb2lin(RED_SRGB[None, None, :])[0, 0]
LOGO_OFFSET = (189, 836)                                 # placement of the logo PNG (x, y), err 0.4%
R0 = 450.0                                               # reference screen radius for the speed curve

# ---------------------------------------------------------------- handoff alignment (video f240 <-> pano)
# Landmark similarity (crane base, green fence panel) between video frame 240 and the nadir gnomonic panorama:
#   video = 1.126 * Rot(+3.75deg) * pano  -> in portrait output: S = 292.8 px/rad, roll = +86.25deg,
#   panorama nadir lands at output (435.2, 1162.7). Focus of expansion of the drone ascent ~ video (930, 600).
HANDOFF_FRAME = 240
S_H = 292.8
ROLL_H = math.radians(86.25)
NADIR_H = np.array([435.2, 1162.7])
FOE_OUT = np.array([600.0, 1919.0 - 930.0])

# ---------------------------------------------------------------- composition
PLANET_C = np.array([540.0, 1000.0])     # tiny planet centre
S_PLANET_END = 132.0                      # stereographic scale at t=2.92 (ground disc = 4S ~ 50% width)
ROLL_FINAL = math.radians(30.0)          # crane pointing up out of the planet

# ---------------------------------------------------------------- easing helpers
def clamp01(x):
    return np.clip(x, 0.0, 1.0)

def smoothstep(a, b, x):
    t = clamp01((x - a) / (b - a))
    return t * t * (3 - 2 * t)

def smootherstep(a, b, x):
    t = clamp01((x - a) / (b - a))
    return t * t * t * (t * (6 * t - 15) + 10)

def cubic_bezier(p1x, p1y, p2x, p2y):
    """CSS-style cubic-bezier easing; returns f(x)."""
    def f(x):
        x = np.asarray(x, np.float64)
        t = x.copy()
        for _ in range(12):
            cx = 3 * p1x * t * (1 - t) ** 2 + 3 * p2x * t * t * (1 - t) + t ** 3
            dx = 3 * p1x * (1 - t) ** 2 + 6 * (p2x - p1x) * t * (1 - t) + 3 * (1 - p2x) * t * t
            t = np.clip(t - (cx - x) / np.maximum(dx, 1e-6), 0, 1)
        return 3 * p1y * t * (1 - t) ** 2 + 3 * p2y * t * t * (1 - t) + t ** 3
    return f

EXPO_OUT = cubic_bezier(0.16, 1.0, 0.3, 1.0)
QUINT_INOUT = cubic_bezier(0.83, 0.0, 0.17, 1.0)


# =====================================================================================
#  MASTER CAMERA CURVES
# =====================================================================================
class Curves:
    """Master speed curve.  lam(t) = log S(t), S = scale at the image centre (px per radian of the
    virtual camera; for the drone footage the equivalent scale of its content).  The camera speed is
    v(t) = -d lam/dt: one asymmetric speed-ramp (gaussian rise, long inertial tail) shared by the real
    footage and the panorama, so velocity is continuous through the handoff."""

    def __init__(self, video_Z):
        self.Z = video_Z                     # cumulative log-scale of video content per frame
        self.tt = np.linspace(-0.2, 7.0, 72001)
        dt = self.tt[1] - self.tt[0]
        s0 = 1.035
        self.lam0 = math.log(S_H * math.exp(self.Z[0] - self.Z[HANDOFF_FRAME]) * s0)
        lam_end = math.log(S_PLANET_END)
        target = self.lam0 - lam_end
        mask = self.tt >= 0
        base = np.where(mask, self._shape(self.tt), 0)
        drift = np.where(mask, 0.065 * smoothstep(-0.1, 0.25, self.tt) * (1 - smoothstep(1.9, 2.7, self.tt)), 0)
        i_end = np.searchsorted(self.tt, 2.92)
        cb = np.cumsum(base) * dt; cd = np.cumsum(drift) * dt
        self.A = (target - cd[i_end]) / cb[i_end]
        self.v = base * self.A + drift
        self.lam = self.lam0 - np.cumsum(self.v) * dt
        self.t_h = float(np.interp(-math.log(S_H), -self.lam, self.tt))
        # roll speed: starts after the handoff, peaks during the curvature, inertia tail into the collapse
        tr = 2.22
        w = np.where(self.tt < tr, np.exp(-((self.tt - tr) / 0.16) ** 2), 1 / (1 + ((self.tt - tr) / 0.26) ** 2) ** 2)
        w *= smoothstep(self.t_h - 0.02, self.t_h + 0.14, self.tt)
        cw = np.cumsum(w) * dt
        i_r = np.searchsorted(self.tt, 2.80)
        self.roll = ROLL_H + (ROLL_FINAL - ROLL_H) * cw / cw[i_r]

    @staticmethod
    def _shape(t):
        tp, s1, s2 = 1.97, 0.42, 0.20
        rise = np.exp(-((t - tp) / s1) ** 2)
        fall = 1 / (1 + ((t - tp) / s2) ** 2) ** 2
        return np.where(t < tp, rise, fall)

    def speed(self, t):
        return float(np.interp(t, self.tt, self.v))

    def roll_at(self, t):
        return float(np.interp(t, self.tt, self.roll))

    def S_at(self, t):
        return math.exp(float(np.interp(t, self.tt, self.lam)))

    # ---- video phase
    def micro(self, t):
        e = smootherstep(0.0, 1.1, t)
        s = 1.035 + (1.0 - 1.035) * e
        rot = math.radians(1.0) * (1 - e)
        return s, rot

    def video_tau(self, t):
        s, _ = self.micro(t)
        z = self.Z[HANDOFF_FRAME] + math.log(self.S_at(t) / (S_H * s))
        return float(np.interp(-z, -self.Z, np.arange(len(self.Z))))

    # ---- panorama phase
    def d_at(self, t):
        return float(smootherstep(self.t_h, 2.60, t))

    def nadir_at(self, t, S):
        model = FOE_OUT + (S / S_H) * (NADIR_H - FOE_OUT)
        e = smootherstep(self.t_h, 2.78, t)
        return model * (1 - e) + PLANET_C * e


# =====================================================================================
#  COLLAPSE (ball -> dot of the i)
# =====================================================================================
T_SPH, T_COLL0, T_LOCK = 2.88, 3.00, 3.50
DOT = None   # filled from the logo PNG: centre and half sizes


def collapse_state(t, S_planet):
    """Returns dict with sphere centre, ground radius G, ratio R_vis/G, morph mu, whiten p, scale sigma."""
    G_planet = 2.0 * S_planet
    cx, cy, hx, hy = DOT
    Gdot = math.sqrt(hx * hy * 4 / math.pi)              # area-equivalent radius
    total = math.log(G_planet / Gdot)
    u = (t - T_COLL0) / (T_LOCK - T_COLL0)
    # collapse progress: slow start (continuing the drift), violent acceleration, precise deceleration,
    # minimal overshoot (dot 4% smaller) settling 2 frames after the lock
    if u <= 0:
        prog = 0.0
    elif u < 1:
        prog = float(cubic_bezier(0.60, 0.0, 0.34, 1.0)(u))
    else:
        prog = 1.0
    over = 0.04 * math.sin(math.pi * clamp01((t - (T_LOCK - 0.08)) / 0.12)) if t > T_LOCK - 0.08 else 0.0
    logG = math.log(G_planet) - total * prog - over
    G = math.exp(logG)
    sigma = G / Gdot
    # path: cubic bezier from planet centre to the dot, swinging left then into place
    P0 = PLANET_C; P3 = np.array([cx, cy])
    P1 = P0 + np.array([-70.0, -40.0]); P2 = P3 + np.array([-120.0, 30.0])
    pu = float(cubic_bezier(0.55, 0.0, 0.25, 1.0)(clamp01(u))) if u > 0 else 0.0
    b = (1 - pu) ** 3 * P0 + 3 * (1 - pu) ** 2 * pu * P1 + 3 * (1 - pu) * pu ** 2 * P2 + pu ** 3 * P3
    # position overshoot: 2.5 px past the target along the arrival direction, settling
    arr = (P3 - P2) / np.linalg.norm(P3 - P2)
    b = b + arr * 2.5 * math.sin(math.pi * clamp01((t - (T_LOCK - 0.07)) / 0.11)) * (t > T_LOCK - 0.07)
    # sky wraps behind the ball: visible-disc / ground-disc ratio
    # red sweep: the visible-disc edge enters from the corners and decelerates onto the ball
    k = 1 - (1 - clamp01((t - T_SPH) / 0.42)) ** 3
    ratio = (3000.0 / G) ** (1 - k)
    ratio = max(ratio, 1.0005)
    mu = float(smootherstep(0.0, 1.0, (math.log(max(sigma, 1.0)) - math.log(4.5)) / (0 - math.log(4.5)))) if sigma < 4.5 else 0.0
    if t >= T_LOCK:
        mu = 1.0
    wp = float(smoothstep(math.log(8.0), math.log(1.15), math.log(max(sigma, 1e-3))))
    return dict(c=b, G=G, ratio=ratio, mu=mu, white=wp, sigma=sigma, spin=math.radians(28.0) * prog)


# =====================================================================================
#  SOURCES
# =====================================================================================
class Video:
    def __init__(self, n_frames=253):
        self.frames = []
        for n in range(n_frames):
            f = cv2.imread(os.path.join(ROOT, 'build/pano_frames/f%03d.jpg' % (n + 1)))
            self.frames.append(cv2.rotate(f, cv2.ROTATE_90_COUNTERCLOCKWISE))   # 1080x1920, native res
        self.flow_cache = {}
        self.dis = cv2.DISOpticalFlow_create(cv2.DISOPTICAL_FLOW_PRESET_MEDIUM)

    def _flow(self, a, b):
        key = (a, b)
        if key not in self.flow_cache:
            ga = cv2.cvtColor(cv2.resize(self.frames[a], (540, 960), interpolation=cv2.INTER_AREA), cv2.COLOR_BGR2GRAY)
            gb = cv2.cvtColor(cv2.resize(self.frames[b], (540, 960), interpolation=cv2.INTER_AREA), cv2.COLOR_BGR2GRAY)
            f = self.dis.calc(ga, gb, None)
            f = cv2.resize(f, (W, H), interpolation=cv2.INTER_LINEAR) * 2.0
            self.flow_cache[key] = f.astype(np.float16)
            if len(self.flow_cache) > 120:
                self.flow_cache.pop(next(iter(self.flow_cache)))
        return self.flow_cache[key].astype(np.float32)

    def at(self, tau):
        """Frame at fractional time tau (video frames), flow-interpolated, linear RGB float32."""
        tau = min(max(tau, 0.0), len(self.frames) - 1.0001)
        i = int(math.floor(tau)); f = tau - i
        if f < 0.02:
            return srgb2lin(self.frames[i][..., ::-1])
        if f > 0.98:
            return srgb2lin(self.frames[i + 1][..., ::-1])
        gx, gy = np.meshgrid(np.arange(W, dtype=np.float32), np.arange(H, dtype=np.float32))
        Fab = self._flow(i, i + 1); Fba = self._flow(i + 1, i)
        A = cv2.remap(self.frames[i], gx - f * Fab[..., 0], gy - f * Fab[..., 1], cv2.INTER_LINEAR, borderMode=cv2.BORDER_REFLECT)
        B = cv2.remap(self.frames[i + 1], gx - (1 - f) * Fba[..., 0], gy - (1 - f) * Fba[..., 1], cv2.INTER_LINEAR, borderMode=cv2.BORDER_REFLECT)
        return srgb2lin(A[..., ::-1]) * (1 - f) + srgb2lin(B[..., ::-1]) * f


class Pano:
    PAD = 160

    def __init__(self, path):
        img = srgb2lin(cv2.imread(path)[..., ::-1])
        self.Hs, self.Ws = img.shape[:2]
        P = self.PAD
        # pad across the poles (row mirrored + half-turn in longitude) and horizontally (wrap)
        top = np.roll(img[:P][::-1], self.Ws // 2, axis=1)
        bot = np.roll(img[-P:][::-1], self.Ws // 2, axis=1)
        v = np.concatenate([top, img, bot], 0)
        v = np.concatenate([v[:, -P:], v, v[:, :P]], 1)
        self.levels = []
        for l in range(8):
            if l == 0:
                lv = v
            else:
                sig = 0.5 * math.sqrt(4 ** l - 1)
                lv = cv2.GaussianBlur(v, (0, 0), sig)
            self.levels.append(np.ascontiguousarray(lv))
        self.pxrad = self.Hs / math.pi

    def sample(self, dirs, foot):
        """dirs: (h,w,3) unit vectors; foot: angular footprint (rad) per output pixel."""
        lon = np.arctan2(dirs[..., 1], dirs[..., 0])
        lat = np.arcsin(np.clip(dirs[..., 2], -1, 1))
        P = self.PAD
        mx = (((lon / (2 * np.pi) + 0.5) * self.Ws) % self.Ws - 0.5 + P).astype(np.float32)
        my = ((0.5 - lat / np.pi) * self.Hs - 0.5 + P).astype(np.float32)
        lod = np.clip(np.log2(np.maximum(foot * self.pxrad, 1e-6)), 0, 7.0)
        out = np.zeros(dirs.shape[:2] + (3,), np.float32)
        lmin, lmax = int(math.floor(lod.min())), int(math.ceil(lod.max()))
        for l in range(lmin, lmax + 1):
            wgt = np.clip(1 - np.abs(lod - l), 0, 1)
            if wgt.max() <= 0:
                continue
            interp = cv2.INTER_CUBIC if l == 0 else cv2.INTER_LINEAR
            out += cv2.remap(self.levels[l], mx, my, interp, borderMode=cv2.BORDER_REFLECT) * wgt[..., None]
        return np.maximum(out, 0)


def footprint(dirs):
    dx = np.zeros(dirs.shape[:2], np.float32); dy = np.zeros_like(dx)
    dx[:, :-1] = np.linalg.norm(dirs[:, 1:] - dirs[:, :-1], axis=-1); dx[:, -1] = dx[:, -2]
    dy[:-1] = np.linalg.norm(dirs[1:] - dirs[:-1], axis=-1); dy[-1] = dy[-2]
    return np.maximum(dx, dy)


# =====================================================================================
#  LOGO
# =====================================================================================
class Logo:
    def __init__(self):
        png = cv2.imread(os.path.join(ROOT, 'assets/source/alsina_logo_blanco_transparente.png'), cv2.IMREAD_UNCHANGED)
        a = png[..., 3].astype(np.float32) / 255.0
        full = np.zeros((H, W), np.float32)
        ox, oy = LOGO_OFFSET
        full[oy:oy + a.shape[0], ox:ox + a.shape[1]] = a
        self.alpha = full
        lab, n = ndimage.label(full > 0.5)
        # extend labels to anti-aliased fringe pixels (nearest core pixel)
        idx = ndimage.distance_transform_edt(lab == 0, return_distances=False, return_indices=True)
        lab_full = lab[idx[0], idx[1]] * (full > 0)
        objs = ndimage.find_objects(lab)
        comps = {}
        for i, sl in enumerate(objs):
            ys, xs = sl
            comps[i + 1] = dict(x0=xs.start, x1=xs.stop, y0=ys.start, y1=ys.stop)
        # identify components by position
        def find(x0, y0):
            for k, c in comps.items():
                if abs(c['x0'] - x0) <= 2 and abs(c['y0'] - y0) <= 2:
                    return k
            raise KeyError((x0, y0))
        names = dict(A_diag=find(262, 844), l=find(382, 845), dot=find(554, 845), s=find(429, 891),
                     n=find(608, 891), a=find(746, 891), i_stem=find(554, 893), A_leg=find(196, 935))
        self.parts = {}
        for nm, k in names.items():
            self.parts[nm] = dict(alpha=(full * (lab_full == k)).astype(np.float32), **comps[k])
        # exact dot geometry from alpha moments
        da = self.parts['dot']['alpha']
        ys, xs = np.nonzero(da > 0)
        y0, y1, x0, x1 = ys.min(), ys.max() + 1, xs.min(), xs.max() + 1
        sub = da[y0:y1, x0:x1]
        wcol = sub.max(0).sum(); hrow = sub.max(1).sum()
        cx = (sub.sum(0) * (np.arange(x0, x1) + 0.5)).sum() / sub.sum()
        cy = (sub.sum(1) * (np.arange(y0, y1) + 0.5)).sum() / sub.sum()
        self.dot = (float(cx), float(cy), float(wcol / 2), float(hrow / 2))
        # stroke axes for the A (PCA)
        for nm in ('A_diag', 'A_leg'):
            ys, xs = np.nonzero(self.parts[nm]['alpha'] > 0.5)
            pts = np.stack([xs, ys], 1).astype(np.float64)
            m = pts.mean(0); cov = np.cov((pts - m).T); ev, evec = np.linalg.eigh(cov)
            ax = evec[:, 1]
            if ax[1] < 0:
                ax = -ax                      # pointing downwards
            self.parts[nm]['axis'] = ax; self.parts[nm]['centroid'] = m
            proj = (pts - m) @ ax
            self.parts[nm]['span'] = (proj.min(), proj.max())
        # left edge line of the long stroke (for clipping the short leg as it slides out from behind it)
        self.crop = (150, 790, 940, 1070)    # x0,y0,x1,y1 working window


def shift_alpha(a, dx, dy, crop):
    x0, y0, x1, y1 = crop
    sub = a[y0:y1, x0:x1]
    M = np.float32([[1, 0, dx], [0, 1, dy]])
    out = np.zeros_like(a)
    out[y0:y1, x0:x1] = cv2.warpAffine(sub, M, (x1 - x0, y1 - y0), flags=cv2.INTER_CUBIC, borderMode=cv2.BORDER_CONSTANT)
    return np.clip(out, 0, 1)


def soft_half(coord, edge, sign=1.0, soft=1.0):
    """1 where sign*(coord-edge) >= 0, anti-aliased."""
    return np.clip(sign * (coord - edge) / soft + 0.5, 0, 1)


GX, GY = np.meshgrid(np.arange(W, dtype=np.float32) + 0.5, np.arange(H, dtype=np.float32) + 0.5)

T_BUILD0 = T_LOCK + 0.04


def ease_part(t, t0, dur, f=EXPO_OUT):
    return float(f(clamp01((t - t0) / dur))) if t > t0 else 0.0


def logo_alpha(t, logo):
    """White coverage of the logo build at time t (after lock)."""
    fr = 1.0 / FPS
    L = T_BUILD0
    out = np.zeros((H, W), np.float32)
    P = logo.parts
    crop = logo.crop
    # dot: exact logo dot (the ball has become it)
    out = np.maximum(out, P['dot']['alpha'])
    # i stem: extrudes downward out of the dot
    e = ease_part(t, L + 0 * fr, 7 * fr)
    if e > 0:
        a = shift_alpha(P['i_stem']['alpha'], 0, -(1 - e) * 120, crop)
        a *= soft_half(GY, P['dot']['y1'] + 0.5, 1)
        out = np.maximum(out, a)
    # l: rises from the baseline
    e = ease_part(t, L + 2 * fr, 8 * fr)
    if e > 0:
        a = shift_alpha(P['l']['alpha'], 0, (1 - e) * 185, crop)
        a *= soft_half(GY, P['l']['y1'], -1)
        out = np.maximum(out, a)
    # n: slides out from behind the stem of the i
    e = ease_part(t, L + 3 * fr, 8 * fr)
    if e > 0:
        a = shift_alpha(P['n']['alpha'], -(1 - e) * 70, 0, crop)
        a *= soft_half(GX, P['i_stem']['x1'] + 3, 1)
        out = np.maximum(out, a)
    # s: drops from the x-height line
    e = ease_part(t, L + 4 * fr, 8 * fr)
    if e > 0:
        a = shift_alpha(P['s']['alpha'], 0, -(1 - e) * 140, crop)
        a *= soft_half(GY, P['s']['y0'] - 0.5, 1)
        out = np.maximum(out, a)
    # a: slides out from behind the n
    e = ease_part(t, L + 5 * fr, 8 * fr)
    if e > 0:
        a = shift_alpha(P['a']['alpha'], -(1 - e) * 80, 0, crop)
        a *= soft_half(GX, P['n']['x1'] + 4, 1)
        out = np.maximum(out, a)
    # A long stroke: drawn along its own axis from the apex
    e = ease_part(t, L + 6 * fr, 8 * fr)
    if e > 0:
        p = P['A_diag']; ax = p['axis']; c = p['centroid']
        proj = (GX - c[0]) * ax[0] + (GY - c[1]) * ax[1]
        lo, hi = p['span']
        front = lo - 2 + (hi - lo + 4) * e
        a = shift_alpha(p['alpha'], -ax[0] * (1 - e) * 40, -ax[1] * (1 - e) * 40, crop)
        a *= np.clip((front - proj) / 1.5 + 0.5, 0, 1)
        out = np.maximum(out, a)
    # A short leg: slides out from behind the long stroke and closes the A (final beat)
    e = ease_part(t, L + 11 * fr, 6 * fr, cubic_bezier(0.2, 1.0, 0.3, 1.04))
    if e > 0:
        p = P['A_leg']; ax = p['axis']
        k = (1 - e) * 95
        a = shift_alpha(p['alpha'], -ax[0] * k, -ax[1] * k, crop)
        # visible only left of the long stroke's left edge
        q = P['A_diag']; qa = q['axis']; nrm = np.array([qa[1], -qa[0]])
        if nrm[0] > 0:
            nrm = -nrm
        # left edge: max extent of the stroke along -normal
        ys, xs = np.nonzero(q['alpha'] > 0.5)
        dist = (xs - q['centroid'][0]) * nrm[0] + (ys - q['centroid'][1]) * nrm[1]
        edge = dist.max()
        dd = (GX - q['centroid'][0]) * nrm[0] + (GY - q['centroid'][1]) * nrm[1]
        a *= np.clip((dd - edge + 1.0), 0, 1) if e < 0.999 else 1.0
        out = np.maximum(out, a)
    if t >= L + 20 * fr:
        return logo.alpha.copy()
    return np.clip(out, 0, 1)


def guides(t):
    """Fleeting construction guides (x-height and baseline), 2 px, low opacity, gone before the hold."""
    fr = 1.0 / FPS
    L = T_BUILD0
    g = np.zeros((H, W), np.float32)
    e = ease_part(t, L - 1 * fr, 9 * fr)
    fade = 1 - smoothstep(L + 8 * fr, L + 15 * fr, t)
    if e <= 0 or fade <= 0:
        return g
    cx = DOT[0]
    half_l = (cx - 176) * e; half_r = (903 - cx) * e
    for y in (891.0, 1027.0, 844.0):
        band = np.clip(1.0 - np.abs(GY - y) / 1.0, 0, 1)
        span = np.clip((GX - (cx - half_l)) + 0.5, 0, 1) * np.clip(((cx + half_r) - GX) + 0.5, 0, 1)
        g = np.maximum(g, band * span)
    # vertical through the i
    ev = ease_part(t, L - 1 * fr, 7 * fr)
    band = np.clip(1.0 - np.abs(GX - cx) / 1.0, 0, 1)
    span = np.clip(GY - 840, 0, 1) * np.clip((840 + 190 * ev) - GY, 0, 1)
    g = np.maximum(g, band * span)
    return g * 0.32 * fade


# =====================================================================================
#  FRAME COMPOSITION
# =====================================================================================
class Renderer:
    def __init__(self):
        rows = json.load(open(os.path.join(ROOT, 'build/video_motion.json')))
        ls = np.log([r['scale'] for r in rows])
        ls = np.minimum(ls, -1e-4)                 # strictly monotonic zoom-out
        ls = ndimage.uniform_filter1d(ls, 5, mode='nearest')
        self.Z = np.concatenate([[0.0], np.cumsum(ls)])
        self.C = Curves(self.Z)
        self.video = Video(len(self.Z))
        self.pano = Pano(os.path.join(ROOT, 'assets/source/DJI_20260617130023_0031_D.jpg'))
        self.logo = Logo()
        global DOT
        DOT = self.logo.dot
        self.t_blend0 = self.C.t_h - 0.12
        self.t_blend1 = self.C.t_h + 0.08
        self.dis_morph = cv2.DISOpticalFlow_create(cv2.DISOPTICAL_FLOW_PRESET_MEDIUM)

    # ----- video layer
    def video_layer(self, t, tau=None):
        if tau is None:
            tau = self.C.video_tau(t)
        img = self.video.at(tau)
        s, rot = self.C.micro(t)
        if abs(s - 1) > 1e-4 or abs(rot) > 1e-5:
            M = cv2.getRotationMatrix2D((W / 2, H / 2), math.degrees(rot), s)
            img = cv2.warpAffine(img, M, (W, H), flags=cv2.INTER_CUBIC, borderMode=cv2.BORDER_REFLECT)
        return img

    # ----- panorama / planet / ball layer; returns (rgb, coverage)
    def pano_layer(self, t):
        C = self.C
        if t < T_SPH:
            S = C.S_at(t); d = C.d_at(t); roll = C.roll_at(t)
            cen = C.nadir_at(t, S)
            st = None
        else:
            st = collapse_state(t, C.S_at(t))
            roll = C.roll_at(t) - st['spin']
            G = st['G']; ratio = st['ratio']
            d = math.sqrt(ratio ** 2 / (ratio ** 2 - 1.0)) if ratio > 1.0 else 1e6
            d = min(max(d, 1.0), 400.0)
            S = G * d / (d + 1.0)              # ground disc radius = S (d+1)/d = G
            cen = st['c']
        x = (GX - cen[0]); y = (GY - cen[1])
        cover = np.ones((H, W), np.float32)
        if st is not None and st['mu'] > 0:
            # true shape morph: radial remap of the disc onto a superellipse that becomes the dot rectangle
            mu = st['mu']; sig = st['sigma']
            _, _, hx, hy = DOT
            Rvis = S * math.sqrt((d + 1) / (d - 1)) if d > 1.0001 else 1e9
            a_ = Rvis * (1 - mu) + hx * sig * mu
            b_ = Rvis * (1 - mu) + hy * sig * mu
            m = 2.0 + 58.0 * mu ** 2
            r = np.sqrt(x * x + y * y) + 1e-6
            cph = np.abs(x) / r; sph = np.abs(y) / r
            rb = 1.0 / ((cph / a_) ** m + (sph / b_) ** m) ** (1.0 / m)
            cover = np.clip(rb - r + 0.5, 0, 1).astype(np.float32)
            if mu > 0.6:   # crisp rectangle AA for the final frames
                box = np.clip(a_ - np.abs(x) + 0.5, 0, 1) * np.clip(b_ - np.abs(y) + 0.5, 0, 1)
                wbox = smoothstep(0.6, 1.0, mu)
                cover = cover * (1 - wbox) + box * wbox
            scale_tex = Rvis / rb
            x = x * scale_tex; y = y * scale_tex
        c, s_ = math.cos(roll), math.sin(roll)
        u = (c * x - s_ * y) / S; v = (s_ * x + c * y) / S
        dirs, q = directions(u.astype(np.float32), v.astype(np.float32), d)
        foot = footprint(dirs)
        rgb = self.pano.sample(dirs, foot)
        if st is not None:
            if d > 1.0001 and st['mu'] <= 0:
                Rvis = S * math.sqrt((d + 1) / (d - 1))
                r = np.sqrt((GX - cen[0]) ** 2 + (GY - cen[1]) ** 2)
                cover = np.clip(Rvis - r + 0.5, 0, 1).astype(np.float32)
                # subtle limb shading so it reads as a ball, fades as it whitens
                rn = np.clip(r / Rvis, 0, 1)
                k = 0.22 * smoothstep(1.02, 3.0, d) * (1 - st['white'])
                rgb *= (1 - k * (1 - np.sqrt(1 - rn * rn)))[..., None]
            elif st['mu'] > 0:
                cover = cover * (q < 1.0000001)
            wp = st['white']
            if wp > 0:
                p = 1.0 + 80.0 * wp ** 2.2
                rgb = 1.0 - np.power(np.clip(1.0 - rgb, 0, 1), p)
                rgb = rgb * (1 - wp ** 6) + wp ** 6
        return rgb, cover, st

    def subframe(self, t):
        C = self.C
        if t < self.t_blend0:
            return self.video_layer(t)
        if t < self.t_blend1:
            a = float(smoothstep(self.t_blend0, self.t_blend1, t))
            vid = self.video_layer(t)
            pan, _, _ = self.pano_layer(t)
            return self.morph(vid, pan, a)
        if t < T_LOCK + 0.10:
            rgb, cover, st = self.pano_layer(t)
            out = RED[None, None, :] * (1 - cover[..., None]) + rgb * cover[..., None]
            if t >= T_LOCK:
                # hand over to the exact logo dot alpha (geometrically identical rectangle)
                k = smoothstep(T_LOCK, T_LOCK + 0.08, t)
                da = self.logo.parts['dot']['alpha']
                out_l = RED[None, None, :] * (1 - da[..., None]) + da[..., None]
                out = out * (1 - k) + out_l * k
            if t >= T_BUILD0 - 1.0 / FPS:
                la = np.maximum(logo_alpha(t, self.logo) if t >= T_BUILD0 else 0, guides(t))
                out = out * (1 - la[..., None]) + la[..., None]
            return out
        la = logo_alpha(t, self.logo)
        g = guides(t)
        cov = np.maximum(la, g)
        return RED[None, None, :] * (1 - cov[..., None]) + cov[..., None]

    def morph(self, vid, pan, a):
        """Large-scale optical-flow morph between the real footage and the panorama at the handoff:
        structures slide into each other instead of double-exposing."""
        sm = (480, 854)
        g = lambda im: cv2.cvtColor((lin2srgb(cv2.resize(im, sm, interpolation=cv2.INTER_AREA)) * 255).astype(np.uint8), cv2.COLOR_RGB2GRAY)
        F = self.dis_morph.calc(g(pan), g(vid), None)            # pan(x) ~ vid(x + F)
        F = cv2.GaussianBlur(F, (0, 0), 14)
        F = cv2.resize(F, (W, H), interpolation=cv2.INTER_LINEAR) * (W / sm[0])
        Iv = cv2.remap(vid, GX - 0.5 + a * F[..., 0], GY - 0.5 + a * F[..., 1], cv2.INTER_LINEAR, borderMode=cv2.BORDER_REFLECT)
        Ip = cv2.remap(pan, GX - 0.5 - (1 - a) * F[..., 0], GY - 0.5 - (1 - a) * F[..., 1], cv2.INTER_LINEAR, borderMode=cv2.BORDER_REFLECT)
        return Iv * (1 - a) + Ip * a

    def n_sub(self, t):
        if t < 0.6:
            return 3
        if t < self.C.t_h - 0.6:
            return 8
        if t < 2.9:
            return 20
        if t < T_LOCK + 0.1:
            return 20
        if t < T_BUILD0 + 0.75:
            return 12
        return 1

    def frame(self, k, nsub_scale=1.0):
        t = k / FPS
        n = max(1, int(round(self.n_sub(t) * nsub_scale)))
        if n == 1:
            return self.subframe(t)
        acc = np.zeros((H, W, 3), np.float32)
        for j in range(n):
            ts = t - SHUTTER / 2 + SHUTTER * (j + 0.5) / n
            acc += self.subframe(ts)
        return acc / n


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--frames', default='0:%d' % NF)
    ap.add_argument('--list', default=None, help='comma separated frame list')
    ap.add_argument('--preview', action='store_true')
    ap.add_argument('--out', default=os.path.join(ROOT, 'build/frames'))
    ap.add_argument('--curves', action='store_true')
    args = ap.parse_args()
    os.makedirs(args.out, exist_ok=True)
    R = Renderer()
    C = R.C
    print('A=%.3f  handoff t_h=%.3f s (frame %.1f)' % (C.A, C.t_h, C.t_h * FPS))
    if args.curves:
        for k in range(0, 90):
            t = k / FPS
            line = 't=%.2f v=%.3f S=%.1f' % (t, C.speed(t), C.S_at(t))
            if t < C.t_h + 0.1:
                line += ' tau=%.1f' % C.video_tau(t)
            if t > C.t_h - 0.1 and t < 2.95:
                S = C.S_at(t); line += ' S=%.1f d=%.3f roll=%.1f nad=%s' % (S, C.d_at(t), math.degrees(C.roll_at(t)), np.round(C.nadir_at(t, S), 0))
            if t > T_SPH:
                st = collapse_state(t, C.S_at(t))
                line += ' G=%.1f ratio=%.3f mu=%.2f wh=%.2f c=%s' % (st['G'], st['ratio'], st['mu'], st['white'], np.round(st['c'], 1))
            print(line)
        return
    if args.list:
        ks = [int(a) for a in args.list.split(',')]
    else:
        a, b = [int(x) for x in args.frames.split(':')]
        ks = range(a, b)
    for k in ks:
        img = R.frame(k, 0.25 if args.preview else 1.0)
        srgb = lin2srgb(img)
        out16 = np.clip(np.round(srgb * 65535), 0, 65535).astype(np.uint16)[..., ::-1]
        cv2.imwrite(os.path.join(args.out, 'f%03d.png' % k), out16)
        print('frame', k, flush=True)


if __name__ == '__main__':
    main()
