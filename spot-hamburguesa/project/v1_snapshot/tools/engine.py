"""DIBURAMA spot — image engine.

Reads project/edit_decisions.json and renders the master timeline frame by frame:
  source decode (bt709) → duplicate-frame removal → time remap (speed ramps)
  → motion-compensated sampling (DIS optical flow) with a 180° shutter
  → spatial transform (fit 1080×1920, digital moves, shake) → per-shot grade
  → transitions → global look (tone curve, graphite shadows, orange restraint,
  magenta accent, glow, vignette) → film grain → end graphics.

usage:
  engine.py --fps 24 --out renders/x.mkv [--start 0 --end 25] [--workers 4] [--scale 1]
  engine.py --fps 24 --stills 3.5,6.0 --outdir qa/frames      (single frames, PNG)
"""
import argparse, json, os, subprocess, sys, math, multiprocessing as mp
import numpy as np, cv2
from scipy.interpolate import PchipInterpolator

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, HERE)
import graphics  # noqa: E402

W, H = 1080, 1920
EDL = json.load(open(os.path.join(ROOT, "project", "edit_decisions.json")))
LOOK = EDL["look"]
SHUTTER = 0.5  # 180°


# ---------------------------------------------------------------- sources
class Source:
    """Decoded clip with duplicate frames removed; unique frames are re-timed uniformly."""
    def __init__(self, name):
        path = os.path.join(ROOT, "clips", name + ".mp4")
        pr = subprocess.run(["ffprobe", "-v", "error", "-select_streams", "v:0", "-show_entries",
                             "stream=width,height,nb_frames", "-of", "json", path], capture_output=True, text=True)
        st = json.loads(pr.stdout)["streams"][0]
        w, h = st["width"], st["height"]
        raw = subprocess.run(["ffmpeg", "-v", "quiet", "-i", path, "-vf", "scale=in_color_matrix=bt709:in_range=tv",
                              "-f", "rawvideo", "-pix_fmt", "rgb24", "-"], capture_output=True).stdout
        n = len(raw) // (w * h * 3)
        fr = np.frombuffer(raw[: n * w * h * 3], np.uint8).reshape(n, h, w, 3)
        keep = [0]
        for i in range(1, n):
            if np.abs(fr[i].astype(np.int16) - fr[keep[-1]].astype(np.int16)).mean() > 0.6:
                keep.append(i)
        self.name, self.w, self.h, self.n = name, w, h, n
        self.frames = fr[keep]
        self.u = len(keep)
        self.duration = n / 24.0
        self.dups = n - self.u
        self._flow = {}
        self._dis = cv2.DISOpticalFlow_create(cv2.DISOPTICAL_FLOW_PRESET_MEDIUM)

    def pos(self, src_t):
        """seconds on the de-duplicated timeline → fractional unique-frame index"""
        return float(np.clip(src_t * self.u / self.duration, 0, self.u - 1))

    def flow(self, i):
        if i not in self._flow:
            if len(self._flow) > 24:
                self._flow.pop(next(iter(self._flow)))
            f = 360 / self.w
            a = cv2.cvtColor(cv2.resize(self.frames[i], None, fx=f, fy=f, interpolation=cv2.INTER_AREA), cv2.COLOR_RGB2GRAY)
            b = cv2.cvtColor(cv2.resize(self.frames[i + 1], None, fx=f, fy=f, interpolation=cv2.INTER_AREA), cv2.COLOR_RGB2GRAY)
            f01 = self._dis.calc(a, b, None)
            f10 = self._dis.calc(b, a, None)
            up = lambda fl: cv2.resize(fl, (self.w, self.h), interpolation=cv2.INTER_LINEAR) / f
            self._flow[i] = (up(f01), up(f10))
        return self._flow[i]

    def sample(self, p, interp="flow"):
        i = int(math.floor(p)); a = p - i
        if i >= self.u - 1:
            return self.frames[-1].astype(np.float32)
        if a < 0.03 or interp == "nearest":
            return self.frames[i if a < 0.5 else i + 1].astype(np.float32)
        if a > 0.97:
            return self.frames[i + 1].astype(np.float32)
        f01, f10 = self.flow(i)
        ft0 = -(1 - a) * a * f01 + a * a * f10
        ft1 = (1 - a) ** 2 * f01 - a * (1 - a) * f10
        gx, gy = np.meshgrid(np.arange(self.w, dtype=np.float32), np.arange(self.h, dtype=np.float32))
        w0 = cv2.remap(self.frames[i], gx + ft0[..., 0], gy + ft0[..., 1], cv2.INTER_LINEAR, borderMode=cv2.BORDER_REFLECT)
        w1 = cv2.remap(self.frames[i + 1], gx + ft1[..., 0], gy + ft1[..., 1], cv2.INTER_LINEAR, borderMode=cv2.BORDER_REFLECT)
        return (1 - a) * w0.astype(np.float32) + a * w1.astype(np.float32)


_SOURCES = {}
def source(name):
    if name not in _SOURCES:
        # keep memory bounded: at most 3 decoded clips per process
        if len(_SOURCES) >= 3:
            _SOURCES.pop(next(iter(_SOURCES)))
        _SOURCES[name] = Source(name)
    return _SOURCES[name]


# ---------------------------------------------------------------- curves
def kf_interp(keys, t, cols):
    """piecewise smooth (smoothstep-eased) interpolation of keyframe columns"""
    ks = sorted(keys, key=lambda k: k[0])
    if t <= ks[0][0]: return [ks[0][c] for c in cols]
    if t >= ks[-1][0]: return [ks[-1][c] for c in cols]
    for a, b in zip(ks, ks[1:]):
        if a[0] <= t <= b[0]:
            x = (t - a[0]) / (b[0] - a[0]); x = x * x * (3 - 2 * x)
            return [a[c] + (b[c] - a[c]) * x for c in cols]

class Segment:
    def __init__(self, d):
        self.d = d; self.id = d["id"]; self.clip = d["clip"]
        self.t_in, self.t_out = d["in"], d["out"]
        k = np.array(d["speed"], dtype=float)
        self.remap = PchipInterpolator(k[:, 0], k[:, 1], extrapolate=True)
        self.grade = d.get("grade", {})
        self.interp = d.get("interp", "flow")

    def xform(self, t):
        """scale, anchor (normalised source position in the fitted frame), destination of the anchor"""
        if "transform" not in self.d: return 1.0, 0.5, 0.5, 0.5, 0.5
        keys = [k if len(k) == 6 else list(k) + [k[2], k[3]] for k in self.d["transform"]]
        return kf_interp(keys, t, (1, 2, 3, 4, 5))

    def shake(self, t):
        dx = dy = 0.0
        for (t0, amp, dec) in self.d.get("shake", []):
            if t >= t0:
                e = math.exp(-(t - t0) / dec) * amp
                dx += e * math.sin((t - t0) * 2 * math.pi * 23 + 1.3)
                dy += e * math.sin((t - t0) * 2 * math.pi * 17 + 0.4)
        return dx, dy

    def matrix(self, src, t):
        base = max(W / src.w, H / src.h)
        s, ax, ay, bx, by = self.xform(t)
        dx, dy = self.shake(t)
        AX, AY, BX, BY = ax * W, ay * H, bx * W, by * H
        # base fit centred, then scale s about anchor
        cx0, cy0 = (W - src.w * base) / 2, (H - src.h * base) / 2
        a = base * s
        tx = BX + s * (cx0 - AX) + dx
        ty = BY + s * (cy0 - AY) + dy
        return np.float32([[a, 0, tx], [0, a, ty]])

    def render(self, t, fps):
        src = source(self.clip)
        e = SHUTTER / fps
        p0, p1 = src.pos(float(self.remap(t - e / 2))), src.pos(float(self.remap(t + e / 2)))
        m0, m1 = self.matrix(src, t - e / 2), self.matrix(src, t + e / 2)
        # pixel travel of the frame corners due to digital moves
        corners = np.float32([[0, 0, 1], [src.w, 0, 1], [0, src.h, 1], [src.w, src.h, 1]]).T
        xf_px = float(np.abs(m1 @ corners - m0 @ corners).max())
        n = int(np.clip(max(round(abs(p1 - p0) * 2) + 1, round(xf_px / 3) + 1), 1, 16))
        acc = np.zeros((H, W, 3), np.float32)
        for k in range(n):
            tk = t if n == 1 else t - e / 2 + e * (k + 0.5) / n
            img = src.sample(src.pos(float(self.remap(tk))), self.interp)
            acc += cv2.warpAffine(img, self.matrix(src, tk), (W, H), flags=cv2.INTER_LANCZOS4, borderMode=cv2.BORDER_REFLECT)
        img = acc / (n * 255.0)
        img = shot_grade(img, self.grade)
        if "fade_out" in self.d:
            a, b = self.d["fade_out"]
            if t > a: img *= max(0.0, 1 - (t - a) / (b - a)) ** 1.5
        return img


# ---------------------------------------------------------------- grade
LUMA = np.float32([0.2126, 0.7152, 0.0722])

def shot_grade(img, g):
    img = img * (2.0 ** g.get("ev", 0.0))
    if "wb" in g: img = img * np.float32(g["wb"])
    y = img @ LUMA
    img = y[..., None] + (img - y[..., None]) * g.get("sat", 1.0)
    return np.clip(img, 0, None)

_TONE = None
def tone_lut():
    global _TONE
    if _TONE is None:
        xs = [0.0, 0.05, 0.16, 0.42, 0.7, 0.86, 1.0, 1.25]
        ys = [0.008, 0.032, 0.135, 0.42, 0.715, 0.85, 0.93, 0.975]
        f = PchipInterpolator(xs, ys)
        _TONE = f(np.linspace(0, 1.25, 4096)).astype(np.float32)
    return _TONE

_VIG = None
def vignette():
    global _VIG
    if _VIG is None:
        yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
        r = np.sqrt(((xx - W / 2) / (W / 2)) ** 2 + ((yy - H / 2) / (H / 2)) ** 2) / math.sqrt(2)
        _VIG = (1 - LOOK["vignette"] * np.clip(r, 0, 1) ** 2.2)[..., None]
    return _VIG

def look(img):
    # hue-selective saturation: restrain saturated orange, keep Diburama magenta
    img = np.clip(img, 0, 1.25)
    hsv = cv2.cvtColor(img / 1.25, cv2.COLOR_RGB2HSV)
    h, s = hsv[..., 0], hsv[..., 1]
    d_or = np.minimum(np.abs(h - 30), 360 - np.abs(h - 30))
    d_mg = np.minimum(np.abs(h - 328), 360 - np.abs(h - 328))
    w_or = np.exp(-(d_or / 20) ** 2) * np.clip((s - 0.45) / 0.4, 0, 1)
    w_mg = np.exp(-(d_mg / 16) ** 2)
    s = s * (1 - LOOK["orange_restraint"] * w_or) * (1 + (LOOK["magenta_accent"] - 1) * w_mg)
    hsv[..., 1] = np.clip(s, 0, 1)
    img = cv2.cvtColor(hsv, cv2.COLOR_HSV2RGB) * 1.25
    # subtle highlight glow (warm), computed on a quarter-res image
    if LOOK["glow"] > 0:
        y = img @ LUMA
        hi = np.clip((y - 0.8) / 0.4, 0, 1)[..., None] * img
        small = cv2.resize(hi, (W // 4, H // 4), interpolation=cv2.INTER_AREA)
        small = cv2.GaussianBlur(small, (0, 0), 9)
        img = img + LOOK["glow"] * cv2.resize(small, (W, H), interpolation=cv2.INTER_LINEAR)
    # filmic tone curve (per channel)
    lut = tone_lut()
    idx = np.clip(img / 1.25 * 4095, 0, 4095).astype(np.int32)
    img = lut[idx]
    # graphite shadows: desaturate + neutral-cool the low end
    y = img @ LUMA
    ws = (1 - np.clip(y / 0.3, 0, 1)) ** 2
    img = img + (y[..., None] - img) * (0.45 * ws[..., None])
    img = img + ws[..., None] * np.float32([-0.004, 0.0, 0.007])
    img = img * vignette()
    return img

def sharpen(img, amt):
    if amt <= 0: return img
    bl = cv2.GaussianBlur(img, (0, 0), 1.1)
    return img + amt * (img - bl)

def grain(img, n, fps):
    rng = np.random.default_rng(1000 + int(round(n * 24 / fps * 7)))
    g = rng.standard_normal((H // 2, W // 2), dtype=np.float32)
    g = cv2.resize(g, (W, H), interpolation=cv2.INTER_CUBIC)
    g = cv2.GaussianBlur(g, (0, 0), 0.6)
    y = np.clip(img @ LUMA, 0, 1)
    amp = LOOK["grain"] * (0.35 + 2.6 * y * (1 - y))
    return img + (g * amp)[..., None]


# ---------------------------------------------------------------- timeline
SEGS = [Segment(d) for d in EDL["segments"]]
SEG = {s.id: s for s in SEGS}
TRANS = [tr for tr in EDL["transitions"] if tr["type"] != "cut"]
G0 = EDL["graphics"]["start"]

def smooth(x): x = min(max(x, 0.0), 1.0); return x * x * (3 - 2 * x)

_NOISE = None
def wipe_noise():
    global _NOISE
    if _NOISE is None:
        rng = np.random.default_rng(7); acc = np.zeros((H, W), np.float32)
        for k, oc in enumerate([8, 16, 32, 64]):
            g = rng.standard_normal((oc * 2, oc), dtype=np.float32)
            acc += cv2.resize(g, (W, H), interpolation=cv2.INTER_CUBIC) / (k + 1.5)
        _NOISE = acc / acc.std()
    return _NOISE

def combine(tr, a, b, t):
    p = (t - tr["t0"]) / (tr["t1"] - tr["t0"])
    if tr["type"] == "dissolve":
        return a + (b - a) * smooth(p)
    if tr["type"] == "luma":
        key = cv2.GaussianBlur(cv2.resize(a @ LUMA, (W // 4, H // 4)), (0, 0), 3)
        key = cv2.resize(key, (W, H))
        key = (key - key.min()) / max(1e-4, key.max() - key.min())
        thr = 1.05 - 1.5 * smooth(p)
        al = np.clip((key - thr) / 0.35, 0, 1)[..., None]
        return a + (b - a) * al
    if tr["type"] == "wipe_diag":
        dx, dy = tr.get("dir", [1, -1]); nrm = math.hypot(dx, dy); dx, dy = dx / nrm, dy / nrm
        yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
        g = (xx / W - 0.5) * dx + (yy / H - 0.5) * dy * (H / W) * 0.6
        g = (g - g.min()) / (g.max() - g.min()) + 0.12 * wipe_noise()
        soft = 0.22
        front = -0.35 - soft + (1.7 + soft) * smooth(p)
        al = np.clip((front - g) / soft, 0, 1)[..., None]
        return a + (b - a) * al
    raise ValueError(tr["type"])

def frame_at(t, fps, n):
    if t >= G0:
        return grain(graphics.render(t, EDL["graphics"]), n, fps)
    active = [s for s in SEGS if s.t_in - 1e-6 <= t < s.t_out - 1e-6]
    tr = next((x for x in TRANS if x["t0"] <= t < x["t1"]), None)
    if tr is not None:
        a = SEG[tr["from"]].render(t, fps); b = SEG[tr["to"]].render(t, fps)
        img = combine(tr, a, b, t)
    else:
        img = active[-1].render(t, fps)
    img = sharpen(img, LOOK["sharpen"])
    img = look(img)
    img = grain(img, n, fps)
    return img

def to8(img):
    return np.clip(img * 255 + 0.5, 0, 255).astype(np.uint8)


# ---------------------------------------------------------------- output
def ffmpeg_writer(path, fps, lossless=True):
    args = ["ffmpeg", "-y", "-v", "error", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(fps), "-i", "-"]
    if lossless:
        args += ["-c:v", "ffv1", "-level", "3", "-pix_fmt", "yuv444p",
                 "-vf", "scale=out_color_matrix=bt709:out_range=tv"]
    else:
        args += ["-c:v", "libx264", "-crf", "16", "-preset", "slow", "-pix_fmt", "yuv420p",
                 "-vf", "scale=out_color_matrix=bt709:out_range=tv"]
    args += ["-color_primaries", "bt709", "-color_trc", "bt709", "-colorspace", "bt709", path]
    return subprocess.Popen(args, stdin=subprocess.PIPE)

def render_range(job):
    fps, n0, n1, path = job
    w = ffmpeg_writer(path, fps)
    for n in range(n0, n1):
        w.stdin.write(to8(frame_at(n / fps, fps, n)).tobytes())
        if (n - n0) % 24 == 0:
            print(f"  [{os.path.basename(path)}] {n}/{n1}", flush=True)
    w.stdin.close(); w.wait()
    return path

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--fps", type=float, default=24)
    ap.add_argument("--out"); ap.add_argument("--start", type=float, default=0.0)
    ap.add_argument("--end", type=float, default=EDL["format"]["duration"])
    ap.add_argument("--workers", type=int, default=4)
    ap.add_argument("--stills"); ap.add_argument("--outdir", default=os.path.join(ROOT, "qa", "frames"))
    a = ap.parse_args()
    if a.stills:
        os.makedirs(a.outdir, exist_ok=True)
        for tok in a.stills.split(","):
            n = int(round(float(tok) * a.fps)); t = n / a.fps
            cv2.imwrite(os.path.join(a.outdir, f"f{a.fps:g}_{n:04d}.png"), cv2.cvtColor(to8(frame_at(t, a.fps, n)), cv2.COLOR_RGB2BGR))
        return
    n0, n1 = int(round(a.start * a.fps)), int(round(a.end * a.fps))
    # split at segment boundaries-ish: equal chunks; each worker decodes only what it needs
    k = max(1, a.workers); edges = np.linspace(n0, n1, k + 1).astype(int)
    tmp = a.out + ".parts"; os.makedirs(tmp, exist_ok=True)
    jobs = [(a.fps, edges[i], edges[i + 1], os.path.join(tmp, f"p{i:02d}.mkv")) for i in range(k) if edges[i + 1] > edges[i]]
    with mp.get_context("fork").Pool(len(jobs)) as pool:
        parts = pool.map(render_range, jobs)
    lst = os.path.join(tmp, "list.txt")
    open(lst, "w").write("".join(f"file '{os.path.abspath(p)}'\n" for p in parts))
    subprocess.run(["ffmpeg", "-y", "-v", "error", "-f", "concat", "-safe", "0", "-i", lst, "-c", "copy", a.out], check=True)
    for p in parts: os.remove(p)
    os.remove(lst); os.rmdir(tmp)
    print("wrote", a.out)

if __name__ == "__main__":
    main()
