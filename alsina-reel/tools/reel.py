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
PLANET_C = np.array([540.0, 850.0])      # tiny planet centre (upper half: the ball then falls)
IMPACT_C = np.array([540.0, 960.0])      # exact centre of the frame: the dot lands here
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

    def __init__(self, video_Z, G_target):
        self.Z = video_Z                     # cumulative log-scale of video content per frame
        self.tt = np.linspace(-0.2, 7.0, 72001)
        dt = self.tt[1] - self.tt[0]
        s0 = 1.02
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
        # second, continuous pull-back: the planet never stops; the camera keeps receding until the
        # ball has the size of the dot (G_target) at T_DOT. Smooth ease-in/out added on top of the tail.
        E2 = cubic_bezier(0.50, 0.0, 0.42, 1.0)(clamp01((self.tt - T_PULL0) / (T_DOT - T_PULL0)))
        S_old = math.exp(float(np.interp(T_DOT, self.tt, self.lam)))
        dd = self.d_at(T_DOT)
        self.L2 = math.log(S_old * (dd + 1) / dd / G_target)
        self.E2 = E2
        self.lam = self.lam - self.L2 * E2
        self.v = -np.gradient(self.lam, dt)
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
        spin = math.radians(30.0) * float(np.interp(t, self.tt, self.E2))
        return float(np.interp(t, self.tt, self.roll)) - spin

    def S_at(self, t):
        return math.exp(float(np.interp(t, self.tt, self.lam)))

    # ---- video phase
    def micro(self, t):
        e = smootherstep(0.0, 1.6, t)
        s = 1.02 + (1.0 - 1.02) * e
        rot = math.radians(0.6) * (1 - e)
        return s, rot

    def video_tau(self, t):
        s, _ = self.micro(t)
        z = self.Z[HANDOFF_FRAME] + math.log(self.S_at(t) / (S_H * s))
        return float(np.interp(-z, -self.Z, np.arange(len(self.Z))))

    # ---- panorama phase
    def d_at(self, t):
        """Camera distance from the sphere centre, continuous 0 -> 1 -> inf: gnomonic (inside the pano)
        -> stereographic tiny planet at T_ONE -> orthographic ball. One dolly-out, no hold.
        Past d=1 it is driven by rho = R_visible/G (visible-disc edge / ground-disc radius), so the sky
        wraps behind the ball as a gradual radial sweep revealing the red."""
        if t <= T_ONE:
            return float(smoothstep(T_CURVE0, T_ONE, t))
        # 1/d eased smoothly from 1 to 0: the ground disc G = S(1 + 1/d) stays smooth, and the visible-disc
        # ratio rho = 1/sqrt(1 - 1/d^2) starts at infinity (edge off-screen) and closes onto the ball.
        E = float(SWEEP_EASE(clamp01((t - T_ONE) / (T_ORTHO - T_ONE))))
        inv = 1.0 - E
        return min(1.0 / max(inv, 1e-6), 400.0)

    def nadir_at(self, t, S):
        """Centre of the projection on screen: from the handoff alignment to the planet position, then
        the ball falls (accelerating) into the exact centre of the frame, impact at T_IMPACT."""
        model = FOE_OUT + (S / S_H) * (NADIR_H - FOE_OUT)
        if t <= 2.40:
            e = smootherstep(self.t_h, 2.40, t)
            return model * (1 - e) + PLANET_C * e
        f = float(clamp01((t - 2.40) / (T_IMPACT - 2.40))) ** 2.6
        return PLANET_C + (IMPACT_C - PLANET_C) * f


# =====================================================================================
#  TIMELINE OF THE FINALE
# =====================================================================================
T_PULL0 = 2.22        # second pull-back starts (planet already transforming)
T_CURVE0 = 1.90       # the panorama starts to curve (inside the handoff blend)
T_ONE = 2.34          # stereographic tiny planet
T_ORTHO = 2.84        # projection reaches orthographic (sky fully wrapped behind the ball)
def SWEEP_EASE(u, a=2.6, u1=0.6):
    """Slow power start (the red edge enters the frame gently), cubic Hermite landing with zero slope."""
    u = float(u)
    if u <= u1:
        return u ** a
    y1, m1 = u1 ** a, a * u1 ** (a - 1)
    h = 1 - u1; x = (u - u1) / h
    # Hermite from (y1, slope m1*h) to (1, slope 0)
    return (2 * x ** 3 - 3 * x ** 2 + 1) * y1 + (x ** 3 - 2 * x ** 2 + x) * m1 * h + (-2 * x ** 3 + 3 * x ** 2) * 1.0
T_DOT = 2.94          # ball has become the white dot (vector dot takes over, identical geometry)
T_IMPACT = 3.00       # dot hits the centre of the frame
SG0 = 1.60            # logo-group scale at impact (the dot carries the frame); settles to 1.0
T_SETTLE0, T_SETTLE1 = 3.36, 4.30
DOTV = None           # (cx, cy, hx, hy) of the vector dot, logo space


def sphere_state(t, C):
    S = C.S_at(t); d = C.d_at(t)
    G = S * (d + 1) / d if d > 1e-6 else 1e9
    cx, cy, hx, hy = DOTV
    Gt = math.sqrt(hx * hy * 4 / math.pi) * SG0
    sigma = G / Gt
    ls = math.log(max(sigma, 1e-3))
    mu = float(smootherstep(math.log(3.5), math.log(1.04), ls)) if sigma < 3.5 else 0.0
    white = float(smoothstep(math.log(6.0), math.log(1.10), ls))
    return dict(S=S, d=d, G=G, sigma=sigma, mu=mu, white=white, c=C.nadir_at(t, S), roll=C.roll_at(t))


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
#  LOGO (vector reconstruction of the original white logo)
# =====================================================================================
from logo_vec import trace, raster

GX, GY = np.meshgrid(np.arange(W, dtype=np.float32) + 0.5, np.arange(H, dtype=np.float32) + 0.5)
QUINT_OUT = cubic_bezier(0.22, 1.0, 0.36, 1.0)
QUART_INOUT = cubic_bezier(0.55, 0.0, 0.15, 1.0)


class VecLogo:
    NAMES = dict(A_diag=(262, 844), l=(382, 845), dot=(554, 845), s=(429, 891), n=(608, 891),
                 a=(746, 891), i_stem=(554, 893), A_leg=(196, 935))

    def __init__(self):
        raw = trace()
        self.P = {}
        for nm, (x0, y0) in self.NAMES.items():
            k = [k for k, v in raw.items() if abs(v['x0'] - x0) <= 2 and abs(v['y0'] - y0) <= 2][0]
            self.P[nm] = raw[k]
        allp = np.concatenate(self.P['dot']['polys'])
        x0, y0 = allp.min(0); x1, y1 = allp.max(0)
        self.dot = ((x0 + x1) / 2, (y0 + y1) / 2, (x1 - x0) / 2, (y1 - y0) / 2)
        st = np.concatenate(self.P['i_stem']['polys'])
        self.stem_y0, self.stem_y1 = st[:, 1].min(), st[:, 1].max()
        # stroke axes of the A (PCA on the outline)
        for nm in ('A_diag', 'A_leg'):
            pts = np.concatenate(self.P[nm]['polys'])
            m = pts.mean(0); ev, evec = np.linalg.eigh(np.cov((pts - m).T))
            ax = evec[:, 1]
            if ax[1] < 0:
                ax = -ax
            self.P[nm]['axis'] = ax; self.P[nm]['centroid'] = m
        # clip half-plane for the short leg: left of the long stroke's left edge
        q = self.P['A_diag']; qa = q['axis']; nrm = np.array([qa[1], -qa[0]])
        if nrm[0] > 0:
            nrm = -nrm
        pts = np.concatenate(q['polys'])
        edge = ((pts - q['centroid']) @ nrm).max()
        p0 = q['centroid'] + nrm * (edge + 0.8)
        self.leg_clip = [np.array([p0 - qa * 2000, p0 + qa * 2000, p0 + qa * 2000 + nrm * 3000, p0 - qa * 2000 + nrm * 3000])]
        mid = lambda a_, b_: 0.5 * (a_ + b_)
        P = self.P
        R = lambda xc: [np.array([[xc, 0], [4000, 0], [4000, 4000], [xc, 4000]], float)]
        L = lambda xc: [np.array([[-4000, 0], [xc, 0], [xc, 4000], [-4000, 4000]], float)]
        # (name, start, duration, slide vector in logo px, clip)   -- cadence radiating out from the i
        wdt = lambda nm: P[nm]['x1'] - P[nm]['x0']
        self.reveals = [
            ('n',      3.40, 0.36, (-0.62 * wdt('n'), 0), R(mid(P['i_stem']['x1'], P['n']['x0']))),
            ('s',      3.46, 0.34, (+0.62 * wdt('s'), 0), L(mid(P['s']['x1'], P['i_stem']['x0']))),
            ('l',      3.76, 0.32, (+0.90 * wdt('l'), 0), L(mid(P['l']['x1'], P['s']['x0']))),
            ('a',      3.79, 0.33, (-0.62 * wdt('a'), 0), R(mid(P['n']['x1'], P['a']['x0']))),
            ('A_diag', 3.86, 0.32, (+0.50 * wdt('A_diag'), 0), L(mid(P['A_diag']['x1'], P['l']['x0']))),
            ('A_leg',  3.97, 0.28, tuple(-P['A_leg']['axis'] * 70.0), self.leg_clip),
        ]
        self._hold = None

    # ---- group motion: impact, bounce, settle
    def group(self, t, fall_pos):
        """Returns (T, s, sx, sy): screen position of the dot centre, group scale, dot squash."""
        sx = sy = 1.0
        if t < T_IMPACT:
            T = np.array(fall_pos, float)
        else:
            u = t - T_IMPACT
            b = -10.0 * math.exp(-u / 0.06) * math.sin(2 * math.pi * u / 0.17) if u < 0.4 else 0.0
            T = IMPACT_C + np.array([0.0, b])
            p = math.exp(-((u - 0.008) / 0.026) ** 2)
            sy = 1 - 0.07 * p; sx = 1 + 0.045 * p
        e = float(QUART_INOUT(clamp01((t - T_SETTLE0) / (T_SETTLE1 - T_SETTLE0))))
        dc = np.array(self.dot[:2])
        T = T * (1 - e) + dc * e
        s = SG0 + (1.0 - SG0) * e
        return T, s, sx, sy

    def _map(self, polys, T, s, sx=1.0, sy=1.0):
        dc = np.array(self.dot[:2])
        return [T + s * (p - dc) * [sx, sy] for p in polys]

    def coverage(self, t, fall_pos):
        if t >= T_SETTLE1 + 0.02:
            if self._hold is None:
                self._hold = self._cov_at(T_SETTLE1 + 0.02, fall_pos)
            return self._hold
        return self._cov_at(t, fall_pos)

    def _cov_at(self, t, fall_pos):
        T, s, sx, sy = self.group(t, fall_pos)
        out = np.zeros((H, W), np.float32)
        def put(screen_polys, clip=None):
            allp = np.concatenate(screen_polys)
            x0 = max(int(math.floor(allp[:, 0].min())) - 2, 0); y0 = max(int(math.floor(allp[:, 1].min())) - 2, 0)
            x1 = min(int(math.ceil(allp[:, 0].max())) + 2, W); y1 = min(int(math.ceil(allp[:, 1].max())) + 2, H)
            if x1 <= x0 or y1 <= y0:
                return
            c = raster(screen_polys, (x0, y0, x1, y1), clip)
            out[y0:y1, x0:x1] = np.maximum(out[y0:y1, x0:x1], c)
        P = self.P
        put(self._map(P['dot']['polys'], T, s, sx, sy))
        # i stem: pulled out of the dot -- bottom edge leads, top edge follows and opens the gap
        if t > 3.15:
            eb = float(QUINT_OUT(clamp01((t - 3.15) / 0.27)))
            et = float(cubic_bezier(0.5, 0.0, 0.2, 1.0)(clamp01((t - 3.17) / 0.25)))
            d_bot = self.dot[1] + self.dot[3]
            top = d_bot + (self.stem_y0 - d_bot) * et
            bot = d_bot + (self.stem_y1 - d_bot) * eb
            if bot - top > 0.05:
                k = (bot - top) / (self.stem_y1 - self.stem_y0)
                polys = [np.column_stack([p[:, 0], top + (p[:, 1] - self.stem_y0) * k]) for p in P['i_stem']['polys']]
                put(self._map(polys, T, s))
        for nm, t0, dur, slide, clip in self.reveals:
            if t <= t0:
                continue
            e = float(QUINT_OUT(clamp01((t - t0) / dur)))
            off = np.array(slide) * (1 - e)
            polys = [p + off for p in P[nm]['polys']]
            put(self._map(polys, T, s), self._map(clip, T, s) if e < 1 else None)
        return out


# =====================================================================================
#  FRAME COMPOSITION
# =====================================================================================
class Renderer:
    def __init__(self):
        rows = json.load(open(os.path.join(ROOT, 'build/video_motion.json')))
        ls = np.log([r['scale'] for r in rows])
        ls = np.minimum(ls, -1e-4)                 # strictly monotonic zoom-out
        ls = ndimage.gaussian_filter1d(ls, 7.0, mode='nearest')     # smooth zoom-rate -> even playback
        self.Z = np.concatenate([[0.0], np.cumsum(ls)])
        self.logo = VecLogo()
        global DOTV
        DOTV = self.logo.dot
        Gt = math.sqrt(DOTV[2] * DOTV[3] * 4 / math.pi) * SG0
        self.C = Curves(self.Z, Gt)
        self.video = Video(len(self.Z))
        self.pano = Pano(os.path.join(ROOT, 'assets/source/DJI_20260617130023_0031_D.jpg'))
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

    # ----- panorama -> tiny planet -> ball -> dot; returns (rgb, coverage, state)
    def pano_layer(self, t):
        st = sphere_state(t, self.C)
        S, d, cen, roll = st['S'], st['d'], st['c'], st['roll']
        x = (GX - cen[0]); y = (GY - cen[1])
        cover = np.ones((H, W), np.float32)
        Rvis = S * math.sqrt((d + 1) / (d - 1)) if d > 1.0001 else 1e9
        mu = st['mu']
        if mu > 0:
            # true shape morph: radial remap of the visible disc onto a superellipse -> the dot rectangle
            _, _, hx, hy = DOTV
            sig = st['sigma']
            a_ = Rvis * (1 - mu) + hx * SG0 * sig * mu
            b_ = Rvis * (1 - mu) + hy * SG0 * sig * mu
            m = 2.0 + 58.0 * mu ** 2
            r = np.sqrt(x * x + y * y) + 1e-6
            rb = 1.0 / ((np.abs(x) / r / a_) ** m + (np.abs(y) / r / b_) ** m) ** (1.0 / m)
            cover = np.clip(rb - r + 0.5, 0, 1).astype(np.float32)
            if mu > 0.6:
                box = np.clip(a_ - np.abs(x) + 0.5, 0, 1) * np.clip(b_ - np.abs(y) + 0.5, 0, 1)
                wbox = smoothstep(0.6, 1.0, mu)
                cover = cover * (1 - wbox) + box * wbox
            sc = Rvis / rb
            x = x * sc; y = y * sc
        elif d > 1.0001:
            r = np.sqrt(x * x + y * y)
            cover = np.clip(Rvis - r + 0.5, 0, 1).astype(np.float32)
        c, s_ = math.cos(roll), math.sin(roll)
        u = (c * x - s_ * y) / S; v = (s_ * x + c * y) / S
        dirs, q = directions(u.astype(np.float32), v.astype(np.float32), d)
        rgb = self.pano.sample(dirs, footprint(dirs))
        if d > 1.0001 and mu <= 0:
            # subtle limb shading so it reads as a ball; fades as it turns white
            rn = np.clip(np.sqrt((GX - cen[0]) ** 2 + (GY - cen[1]) ** 2) / Rvis, 0, 1)
            k = 0.22 * smoothstep(1.02, 3.0, d) * (1 - st['white'])
            rgb *= (1 - k * (1 - np.sqrt(1 - rn * rn)))[..., None]
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
        if t < T_DOT:
            rgb, cover, st = self.pano_layer(t)
            return RED[None, None, :] * (1 - cover[..., None]) + rgb * cover[..., None]
        # the white ball is now exactly the dot: continue with the vector logo group (same geometry)
        fall = C.nadir_at(min(t, T_IMPACT), C.S_at(min(t, T_IMPACT)))
        cov = self.logo.coverage(t, fall)
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
        if t < T_IMPACT + 0.06:
            return 20
        if t < T_SETTLE1 + 0.04:
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
        for k in range(40, 112):
            t = k / FPS
            line = 't=%.2f v=%.3f S=%.1f' % (t, C.speed(t), C.S_at(t))
            if t < C.t_h + 0.1:
                line += ' tau=%.1f' % C.video_tau(t)
            if t > C.t_h - 0.1 and t < T_DOT + 0.05:
                st = sphere_state(t, C)
                line += ' d=%.3f G=%.1f sig=%.2f mu=%.2f wh=%.2f roll=%.1f c=%s' % (st['d'], st['G'], st['sigma'], st['mu'], st['white'], math.degrees(st['roll']), np.round(st['c'], 1))
            if t >= T_DOT:
                T, sg, sx, sy = R.logo.group(t, C.nadir_at(min(t, T_IMPACT), 1.0))
                line += ' group T=%s s=%.3f squash=(%.3f,%.3f)' % (np.round(T, 1), sg, sx, sy)
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
