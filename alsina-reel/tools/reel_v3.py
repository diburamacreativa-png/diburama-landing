"""ALSINA reel v3 — new opening shot ('Plano inicio zoom out.mp4') joined into the v2 film.

Facts measured by tools/analyze_v3_join.py:
  * the new shot is the same drone flight as pano.mp4: new frame m == pano.mp4 frame 122+m,
    a higher-resolution vertical crop (0.415 old px per new px, rotation 0, crop centre drifting
    from x=1589 to x=1301 in the old frame);
  * old frames 224..252 are registered directly to frame 240, the frame the panorama is aligned to.

So the new opening lives in exactly the same coordinate system as the v2 handoff. The camera:
  0 s      new shot, upright, native resolution (0.92 output px per source px), its own drone motion
           at 0.85x real time;
  ->       one speed ramp that merges (C1) into the v2 master curve at T_MERGE;
  ->       the frame is a 'virtual frame': the new high-res crop composited over the wider old frame
           (same instant, colour matched), so the framing can drift toward the site centre;
  ~1.86 s  frame 240 -> panorama handoff (optical-flow morph under motion blur), as in v2;
  after    identical v2 curves: tiny planet, red, dot, logo (only the planet's spin starts from the
           upright orientation instead of the 90-degree rotated one, and converges by 2.80 s).
"""
import os, sys, json, math, argparse
import numpy as np
import cv2
from scipy import ndimage

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import reel
reel.ROLL_H = math.radians(-3.75)          # upright footage: pano roll at the handoff (v2: +86.25 rotated)
from reel import (W, H, FPS, NF, SHUTTER, RED, srgb2lin, lin2srgb, smoothstep, smootherstep, clamp01,
                  cubic_bezier, Curves, Pano, VecLogo, sphere_state, PLANET_C, IMPACT_C, T_IMPACT, T_DOT,
                  SG0, T_SETTLE1, GX, GY, ROOT)

C_OUT = np.array([540.0, 960.0])
N240 = np.array([756.3, 435.2])            # panorama nadir in old frame-240 px (v2 landmark alignment)
S240 = 292.8                               # panorama px/rad per old frame-240 px
M0 = 122                                   # new frame 0 == old frame 122
NEW_C = np.array([756.0, 1344.0])          # centre of the new frame
K_END = 1.79                               # output px per old px once the old frame fills 9:16 (>= 1920/1080)
K_N0 = 0.92                                # output px per new px at the start (native, slight downscale)
V_START = 0.354                            # opening zoom speed (log/s) = new shot at 0.85x real time
T_MERGE = 1.75                             # merge into the v2 master curve (C1)
F_TARGET_X = 1040.0                        # framing drifts toward the site centre before the handoff
PAN = (1.50, 1.88)


# ------------------------------------------------------------------------------------ measurements
J = json.load(open(os.path.join(ROOT, 'build/v3_join.json')))
_crop = {int(k): np.array(v['A']) for k, v in J['crop'].items()}
_ms = np.array(sorted(_crop))
_cs = np.array([math.sqrt(abs(np.linalg.det(_crop[m][:, :2]))) for m in _ms])
_cc = np.array([cv2.transform(np.float32([[NEW_C]]), _crop[m])[0, 0] for m in _ms])
CROP_S = float(np.median(_cs))
_px = np.polyfit(_ms, _cc[:, 0], 2); _py = np.polyfit(_ms, _cc[:, 1], 1)


def crop_centre(m):
    """Old-frame coordinates of the new frame centre at new frame m (smooth fit; extrapolates)."""
    return np.array([np.polyval(_px, m), np.polyval(_py, m)])


_t2 = {int(k): (np.array(v['A']), v['inl']) for k, v in J['to240'].items()}
_tt = np.array([t for t in sorted(_t2) if _t2[t][1] >= 60 or t == 240])
_ts = np.array([math.sqrt(abs(np.linalg.det(_t2[t][0][:, :2]))) for t in _tt])
_tw = np.array([min(_t2[t][1], 600) for t in _tt], float)
_pl = np.polyfit(_tt, np.log(_ts), 3, w=np.sqrt(_tw))
_pl[-1] -= np.polyval(_pl, 240)            # exactly 1 at frame 240
fps_ = []
for t in _tt:
    A = _t2[t][0]
    if t == 240 or _t2[t][1] < 90:
        continue
    fps_.append(np.linalg.solve(np.eye(2) - A[:, :2], A[:, 2]))
FOE_OLD = np.median(np.array(fps_), 0)


def s_to240(tau):
    return math.exp(float(np.polyval(_pl, tau)))


# new-shot zoom (accurate per-frame measurement), anchored to the old frame at 227
_im = json.load(open(os.path.join(ROOT, 'build/inicio_motion.json')))['frames']
_ln = ndimage.gaussian_filter1d(np.log([r['scale'] for r in _im]), 2.0, mode='nearest')
ZN = np.concatenate([[0.0], np.cumsum(_ln)])          # ZN[m], m = 0..105
C_OLD227 = S240 / s_to240(227.0)
C_NEW105 = C_OLD227 / CROP_S


def C_old(tau):
    """Panorama px/rad per old-frame px at old frame tau (tau 122..252)."""
    if tau <= 227.0:
        m = tau - M0
        zn = float(np.interp(m, np.arange(len(ZN)), ZN))
        return C_NEW105 * math.exp(zn - ZN[105]) * CROP_S
    return S240 / s_to240(tau)


_tau_grid = np.linspace(M0, 252.0, 4000)
_logC = np.array([math.log(C_old(t)) for t in _tau_grid])     # decreasing


def tau_from_C(c):
    return float(np.interp(-math.log(c), -_logC, _tau_grid))


# footage -> panorama correction measured on ground landmarks at the handoff (build/v3_sim.npy):
# yellow-crane base, green-crane base, south fence, site-office fence. Eased in before the blend and
# folded into the speed curve (the footage advances to compensate), so perceived speed is unchanged.
_SIM = np.load(os.path.join(ROOT, 'build/v3_sim.npy'))
SIM_S = float(math.hypot(_SIM[0, 0], _SIM[1, 0])); SIM_R = float(math.atan2(_SIM[1, 0], _SIM[0, 0]))
SIM_T = _SIM[:, 2].copy()
CORR = (1.55, 1.76)


def corr(t):
    b = float(smootherstep(CORR[0], CORR[1], t))
    return 1.0 + b * (SIM_S - 1.0), b * SIM_R, b * SIM_T


# ------------------------------------------------------------------------------------ curves
def k_old(t):
    """Display scale, output px per old px."""
    k0 = K_N0 / CROP_S
    return k0 + (K_END - k0) * float(smootherstep(1.52, 1.78, t))


class Curves3(Curves):
    def __init__(self, video_Z, G_target):
        super().__init__(video_Z, G_target)
        tt = self.tt; dt = tt[1] - tt[0]
        v2 = self.v.copy(); lam2 = self.lam.copy()
        S0 = k_old(0.0) * C_old(float(M0))
        need = math.log(S0) - float(np.interp(T_MERGE, tt, lam2))
        mask = (tt >= 0) & (tt <= T_MERGE)
        def integral(ta):
            B = smootherstep(ta, T_MERGE, tt)
            v = V_START + np.maximum(0.0, v2 - V_START) * B      # monotonic: never slower than the footage
            return (v * mask).sum() * dt, v
        lo, hi = 0.0, T_MERGE - 0.05
        for _ in range(60):                       # later blend start -> less of the v2 ramp -> smaller integral
            mid = 0.5 * (lo + hi)
            I, _ = integral(mid)
            if I > need:
                lo = mid
            else:
                hi = mid
        self.t_a = 0.5 * (lo + hi)
        I, v3 = integral(self.t_a)
        self.need, self.got = need, I
        lam3 = math.log(S0) - np.cumsum(np.where(tt >= 0, v3, 0)) * dt
        self.lam = np.where(tt < T_MERGE, lam3, lam2)
        self.v = np.where(tt < T_MERGE, v3, v2)
        self.merge_err = float(np.interp(T_MERGE - 1e-3, tt, lam3) - np.interp(T_MERGE, tt, lam2))
        # handoff = old frame 240 reached
        ts = np.linspace(1.5, 2.1, 3001)
        taus = np.array([self.tau_at(t) for t in ts])
        self.t_h3 = float(np.interp(240.0, taus, ts))
        self.G_h = self.G_at(self.t_h3)

    def tau_at(self, t):
        return tau_from_C(self.S_at(t) / k_old(t))

    def tau_eff(self, t):
        """Footage time actually shown (includes the landmark correction zoom)."""
        return tau_from_C(self.S_at(t) / (k_old(t) * corr(t)[0]))

    def F_at(self, t):
        """Framing centre in the coordinates of the current old frame."""
        tau = self.tau_at(t)
        f = crop_centre(tau - M0)
        f[0] += (F_TARGET_X - crop_centre(240.0 - M0)[0]) * float(smootherstep(PAN[0], PAN[1], t))
        return f

    def G_at(self, t):
        """Framing centre expressed in old frame-240 coordinates."""
        tau = self.tau_at(t)
        return FOE_OLD + (S240 / C_old(tau)) * (self.F_at(t) - FOE_OLD)

    def nadir_at(self, t, S):
        if t <= self.t_h3:
            return C_OUT + (S / S240) * (N240 - self.G_at(t))
        model = C_OUT + (S / S240) * (N240 - self.G_h)
        if t <= 2.40:
            e = smootherstep(self.t_h3, 2.40, t)
            return model * (1 - e) + PLANET_C * e
        f = float(clamp01((t - 2.40) / (T_IMPACT - 2.40))) ** 2.6
        return PLANET_C + (IMPACT_C - PLANET_C) * f


# ------------------------------------------------------------------------------------ footage
class FlowClip:
    """Frames at native size, flow-interpolated fractional access, linear-light float32."""

    def __init__(self, paths, colour=None, flow_scale=0.25):
        self.paths = paths
        self.cache = {}
        self.flows = {}
        self.colour = colour
        self.fs = flow_scale
        self.dis = cv2.DISOpticalFlow_create(cv2.DISOPTICAL_FLOW_PRESET_MEDIUM)

    def raw(self, i):
        if i not in self.cache:
            f = cv2.imread(self.paths[i])
            if self.colour is not None:
                f = f.astype(np.float32)
                for c in range(3):
                    a, b = self.colour[c]          # measured on BGR images
                    f[..., c] = f[..., c] * a + b
                f = np.clip(f, 0, 255).astype(np.uint8)
            self.cache[i] = f
            if len(self.cache) > 40:
                self.cache.pop(next(iter(self.cache)))
        return self.cache[i]

    def flow(self, a, b):
        key = (a, b)
        if key not in self.flows:
            ga = cv2.cvtColor(cv2.resize(self.raw(a), None, fx=self.fs, fy=self.fs, interpolation=cv2.INTER_AREA), cv2.COLOR_BGR2GRAY)
            gb = cv2.cvtColor(cv2.resize(self.raw(b), None, fx=self.fs, fy=self.fs, interpolation=cv2.INTER_AREA), cv2.COLOR_BGR2GRAY)
            f = self.dis.calc(ga, gb, None)
            h, w = self.raw(a).shape[:2]
            self.flows[key] = (cv2.resize(f, (w, h), interpolation=cv2.INTER_LINEAR) / self.fs).astype(np.float16)
            if len(self.flows) > 30:
                self.flows.pop(next(iter(self.flows)))
        return self.flows[key].astype(np.float32)

    def at(self, x):
        n = len(self.paths)
        x = min(max(x, 0.0), n - 1.0001)
        i = int(math.floor(x)); f = x - i
        if f < 0.02:
            return srgb2lin(self.raw(i)[..., ::-1])
        if f > 0.98:
            return srgb2lin(self.raw(i + 1)[..., ::-1])
        A0, B0 = self.raw(i), self.raw(i + 1)
        h, w = A0.shape[:2]
        gx, gy = np.meshgrid(np.arange(w, dtype=np.float32), np.arange(h, dtype=np.float32))
        Fab = self.flow(i, i + 1); Fba = self.flow(i + 1, i)
        A = cv2.remap(A0, gx - f * Fab[..., 0], gy - f * Fab[..., 1], cv2.INTER_LINEAR, borderMode=cv2.BORDER_REFLECT)
        B = cv2.remap(B0, gx - (1 - f) * Fba[..., 0], gy - (1 - f) * Fba[..., 1], cv2.INTER_LINEAR, borderMode=cv2.BORDER_REFLECT)
        return srgb2lin(A[..., ::-1]) * (1 - f) + srgb2lin(B[..., ::-1]) * f


def feather(px, py, w, h, f):
    return (np.clip(px / f, 0, 1) * np.clip((w - 1 - px) / f, 0, 1) *
            np.clip(py / f, 0, 1) * np.clip((h - 1 - py) / f, 0, 1)).astype(np.float32)


# ------------------------------------------------------------------------------------ renderer
class Renderer3(reel.Renderer):
    def __init__(self):
        rows = json.load(open(os.path.join(ROOT, 'build/video_motion.json')))
        ls = np.log([r['scale'] for r in rows]); ls = np.minimum(ls, -1e-4)
        ls = ndimage.gaussian_filter1d(ls, 7.0, mode='nearest')
        self.Z = np.concatenate([[0.0], np.cumsum(ls)])
        self.logo = VecLogo()
        reel.DOTV = self.logo.dot
        Gt = math.sqrt(reel.DOTV[2] * reel.DOTV[3] * 4 / math.pi) * SG0
        self.C = Curves3(self.Z, Gt)
        self.pano = Pano(os.path.join(ROOT, 'assets/source/DJI_20260617130023_0031_D.jpg'))
        self.new = FlowClip([os.path.join(ROOT, 'build/inicio_frames/f%03d.jpg' % (i + 1)) for i in range(106)])
        self.old = FlowClip([os.path.join(ROOT, 'build/pano_frames/f%03d.jpg' % (i + 1)) for i in range(256)],
                            colour=J['color'], flow_scale=0.5)
        self.t_blend0 = self.C.t_h3 - 0.10
        self.t_blend1 = self.C.t_h3 + 0.07
        self.dis_morph = cv2.DISOpticalFlow_create(cv2.DISOPTICAL_FLOW_PRESET_MEDIUM)
        # pre-computed output grid offsets
        self.qx = (GX - 0.5 - C_OUT[0]).astype(np.float32)
        self.qy = (GY - 0.5 - C_OUT[1]).astype(np.float32)

    def video_layer(self, t, tau=None):
        """The 'virtual frame': new high-res crop over the wider old frame of the same instant."""
        C = self.C
        tau = C.tau_eff(t)
        k = k_old(t)
        F = C.F_at(t)
        cs, cr, ct = corr(t)                     # output q -> q' = S_b^-1(q), then old-frame coords
        qx = self.qx + C_OUT[0] - ct[0]; qy = self.qy + C_OUT[1] - ct[1]
        c_, s_ = math.cos(-cr), math.sin(-cr)
        qx2 = (c_ * qx - s_ * qy) / cs - C_OUT[0]; qy2 = (s_ * qx + c_ * qy) / cs - C_OUT[1]
        po_x = (F[0] + qx2 / k).astype(np.float32); po_y = (F[1] + qy2 / k).astype(np.float32)   # old-frame coords
        w = np.zeros((H, W), np.float32)
        out = None
        if tau <= 227.0:
            m = tau - M0
            cc = crop_centre(m)
            pn_x = (NEW_C[0] + (po_x - cc[0]) / CROP_S).astype(np.float32)
            pn_y = (NEW_C[1] + (po_y - cc[1]) / CROP_S).astype(np.float32)
            alpha = 1.0 - float(smoothstep(223.0, 227.0, tau))
            w = feather(pn_x, pn_y, 1512, 2688, 60.0) * alpha
            img = self.new.at(m)
            out = cv2.remap(img, pn_x, pn_y, cv2.INTER_CUBIC, borderMode=cv2.BORDER_REFLECT)
        if out is None or w.min() < 0.999:
            img = self.old.at(tau)
            old = cv2.remap(img, po_x - 0.0, po_y, cv2.INTER_CUBIC, borderMode=cv2.BORDER_REFLECT)
            out = old if out is None else out * w[..., None] + old * (1 - w[..., None])
        return np.maximum(out, 0)

    def n_sub(self, t):
        if t < 0.8:
            return 4
        if t < 1.3:
            return 8
        if t < 1.55:
            return 12
        return reel.Renderer.n_sub(self, t) if t >= self.C.t_h - 0.6 else 20


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--frames', default='0:%d' % NF)
    ap.add_argument('--list', default=None)
    ap.add_argument('--preview', action='store_true')
    ap.add_argument('--out', default=os.path.join(ROOT, 'build/frames_v3'))
    ap.add_argument('--curves', action='store_true')
    args = ap.parse_args()
    os.makedirs(args.out, exist_ok=True)
    R = Renderer3()
    C = R.C
    print('need %.3f got %.3f | crop scale %.4f  FOE_old %s  C_old(122)=%.0f C_old(227)=%.0f  S0=%.0f  t_a=%.3f  merge_err=%.2e  t_h3=%.3f  G_h=%s' % (
        C.need, C.got, CROP_S, np.round(FOE_OLD, 1), C_old(122.0), C_old(227.0), k_old(0) * C_old(122.0), C.t_a, C.merge_err, C.t_h3, np.round(C.G_h, 1)))
    if args.curves:
        for k in range(0, 60):
            t = k / FPS
            S = C.S_at(t)
            print('t=%.2f v=%.3f S=%.0f tau=%.2f (new m=%.2f, x%.2f rt) k_old=%.3f F=%s nadir=%s' % (
                t, C.speed(t), S, C.tau_at(t), C.tau_at(t) - M0,
                (C.tau_at(t + 0.02) - C.tau_at(t - 0.02)) / 0.04 / 29.97, k_old(t), np.round(C.F_at(t), 0),
                np.round(C.nadir_at(t, S), 0)))
        return
    ks = [int(a) for a in args.list.split(',')] if args.list else range(*[int(x) for x in args.frames.split(':')])
    for k in ks:
        img = R.frame(k, 0.25 if args.preview else 1.0)
        out16 = np.clip(np.round(lin2srgb(img) * 65535), 0, 65535).astype(np.uint16)[..., ::-1]
        cv2.imwrite(os.path.join(args.out, 'f%03d.png' % k), out16)
        print('frame', k, flush=True)


if __name__ == '__main__':
    main()
