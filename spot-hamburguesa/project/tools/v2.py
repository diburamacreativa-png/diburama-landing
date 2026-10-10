"""DIBURAMA spot — V2 transitions (rebuilt joins T1–T4).

Each join has its own virtual camera (cam) and its own compositor (window). Cameras feed
the engine's shutter sampling, so every digital move gets physically consistent motion blur.

  T1  2A → 3A   single travelling: matched-point zoom (2A crust point ↔ 3A macro, ×6.5),
                progressive log-space acceleration, macro focus hand-off, 3A injected at
                matched scale inside the bun, then 3A's own push takes the velocity over.
  T2  4A → 5A   motivated flare: the soft-box on the left passes close to the lens, its
                bloom floods the frame, the material swaps at peak exposure, the flare
                recedes into the light already present in 5A.
  T3  6A → 6B   a cheese loop turns to face camera while the camera rolls; its material
                goes cheese → translucent → chrome; the chrome ring becomes the gear; the
                mechanism assembles (speed ramp) with a metallic impact and microshake.
  T4  7A → 8A   the camera dives through the bore of a bearing; the rim loses rigidity, its
                machined edges turn into glowing structure lines, then into leaf veins; the
                illustrated world is seen through the ring, and its veins grow out of it.
"""
import math
import numpy as np, cv2

CTX = {}           # filled by engine: source, SEG, shot_grade, W, H, LUMA, kf_interp
_CACHE = {}


def smooth(x):
    x = min(max(x, 0.0), 1.0); return x * x * (3 - 2 * x)
def ease_in(x, p=2.0):
    x = min(max(x, 0.0), 1.0); return x ** p
def ease_out(x, p=2.0):
    x = min(max(x, 0.0), 1.0); return 1 - (1 - x) ** p
def lerp(a, b, k): return a + (b - a) * k
def clamp_dest(s, ax, ay, bx, by):
    """keep the displayed crop inside the source frame (no borders) for scale s ≥ 1"""
    if s < 1: return bx, by
    bx = min(max(bx, 1 - (1 - ax) * s), ax * s)
    by = min(max(by, 1 - (1 - ay) * s), ay * s)
    return bx, by


# ------------------------------------------------------------------ tracking helpers
def _track(clip, f0, pt, f_from, f_to):
    """Lucas–Kanade track of one point (normalised) from frame f0, over unique-frame range"""
    key = ("track", clip, f0, pt)
    if key in _CACHE: return _CACHE[key]
    src = CTX["source"](clip)
    g = [cv2.cvtColor(f, cv2.COLOR_RGB2GRAY) for f in src.frames]
    pos = {f0: np.float32([[pt[0] * src.w, pt[1] * src.h]])}
    lk = dict(winSize=(61, 61), maxLevel=4, criteria=(cv2.TERM_CRITERIA_EPS | cv2.TERM_CRITERIA_COUNT, 30, 0.01))
    for rng_, step in ((range(f0, f_to), 1), (range(f0, f_from, -1), -1)):
        for i in rng_:
            j = i + step
            if j < 0 or j >= len(g): break
            p, st, _ = cv2.calcOpticalFlowPyrLK(g[i], g[j], pos[i].reshape(-1, 1, 2), None, **lk)
            pos[j] = p.reshape(-1, 2) if st[0][0] else pos[i]
    idx = sorted(pos)
    arr = np.array([[pos[i][0][0] / src.w, pos[i][0][1] / src.h] for i in idx])
    _CACHE[key] = (np.array(idx, float), arr)
    return _CACHE[key]

def tracked(clip, seg_id, t, f0, pt, f_from, f_to):
    idx, arr = _track(clip, f0, pt, f_from, f_to)
    seg = CTX["SEG"][seg_id]; src = CTX["source"](clip)
    u = src.pos(float(seg.remap(t)))
    return float(np.interp(u, idx, arr[:, 0])), float(np.interp(u, idx, arr[:, 1]))

def lamp_track():
    """brightest soft-box on the left of 4A, per unique frame (normalised centroid)"""
    if "lamp" in _CACHE: return _CACHE["lamp"]
    src = CTX["source"]("plano 4A"); out = []
    for f in src.frames:
        y = cv2.GaussianBlur(cv2.cvtColor(f, cv2.COLOR_RGB2GRAY).astype(np.float32), (0, 0), 3)
        x0, x1, y0, y1 = 0, int(0.32 * src.w), int(0.18 * src.h), int(0.5 * src.h)
        roi = y[y0:y1, x0:x1]; thr = roi.max() * 0.93
        ys, xs = np.where(roi >= thr)
        out.append(((xs.mean() + x0) / src.w, (ys.mean() + y0) / src.h))
    _CACHE["lamp"] = np.array(out)
    return _CACHE["lamp"]

def lamp_at(t):
    arr = lamp_track(); src = CTX["source"]("plano 4A")
    u = src.pos(float(CTX["SEG"]["S05"].remap(t)))
    i = np.arange(len(arr))
    return float(np.interp(u, i, arr[:, 0])), float(np.interp(u, i, arr[:, 1]))


# ------------------------------------------------------------------ image helpers
def blur(img, sigma):
    if sigma < 0.3: return img
    return cv2.GaussianBlur(img, (0, 0), sigma)

def edges(img, gamma=1.3):
    """normalised structure map (gradient magnitude) at half resolution"""
    W, H = CTX["W"], CTX["H"]
    y = cv2.resize(img @ CTX["LUMA"], (W // 2, H // 2), interpolation=cv2.INTER_AREA)
    y = cv2.GaussianBlur(y, (0, 0), 1.2)
    gx = cv2.Sobel(y, cv2.CV_32F, 1, 0, ksize=3); gy = cv2.Sobel(y, cv2.CV_32F, 0, 1, ksize=3)
    m = np.sqrt(gx * gx + gy * gy)
    m = np.clip(m / (np.percentile(m, 98.5) + 1e-6), 0, 1) ** gamma
    return cv2.resize(m, (W, H), interpolation=cv2.INTER_LINEAR)

def noise_field(seed, scale=8):
    key = ("nf", seed, scale)
    if key not in _CACHE:
        W, H = CTX["W"], CTX["H"]; r = np.random.default_rng(seed); acc = np.zeros((H, W, 2), np.float32)
        for k, oc in enumerate([scale, scale * 2, scale * 4]):
            g = r.standard_normal((int(oc * H / W) + 1, oc, 2)).astype(np.float32)
            acc += cv2.resize(g, (W, H), interpolation=cv2.INTER_CUBIC) / (k + 1)
        _CACHE[key] = acc / acc.std()
    return _CACHE[key]

def displace(img, field, amp):
    if amp < 0.2: return img
    W, H = CTX["W"], CTX["H"]
    gx, gy = np.meshgrid(np.arange(W, dtype=np.float32), np.arange(H, dtype=np.float32))
    return cv2.remap(img, gx + field[..., 0] * amp, gy + field[..., 1] * amp, cv2.INTER_LINEAR, borderMode=cv2.BORDER_REFLECT)

def radial(cx, cy, r):
    W, H = CTX["W"], CTX["H"]
    xx, yy = _grid()
    return np.sqrt((xx - cx) ** 2 + (yy - cy) ** 2) / max(r, 1e-3)

def chroma_aberration(img, k):
    """radial lateral CA: R scaled out, B scaled in by k (fraction)"""
    if k < 1e-4: return img
    W, H = CTX["W"], CTX["H"]; out = img.copy()
    for c, f in ((0, 1 + k), (2, 1 - k)):
        M = np.float32([[f, 0, (1 - f) * W / 2], [0, f, (1 - f) * H / 2]])
        out[..., c] = cv2.warpAffine(img[..., c], M, (W, H), flags=cv2.INTER_LINEAR, borderMode=cv2.BORDER_REFLECT)
    return out


def zoom_blur(img, cx, cy, amount, n=None):
    """radial (zoom) motion blur about (cx, cy) px: average of scalings 1 … 1+amount, computed at half res;
    the centre stays sharp, as with a real push-in"""
    if amount < 0.01: return img
    W, H = CTX["W"], CTX["H"]; h2, w2 = H // 2, W // 2
    small = cv2.resize(img, (w2, h2), interpolation=cv2.INTER_AREA)
    n = n or int(np.clip(amount * 70, 3, 18)); acc = np.zeros_like(small)
    for k in range(n):
        f = 1 + amount * k / (n - 1)
        M = np.float32([[f, 0, (1 - f) * cx / 2], [0, f, (1 - f) * cy / 2]])
        acc += cv2.warpAffine(small, M, (w2, h2), flags=cv2.INTER_LINEAR, borderMode=cv2.BORDER_REFLECT)
    bl = cv2.resize(acc / n, (W, H), interpolation=cv2.INTER_LINEAR)
    d = radial(cx, cy, 0.5 * math.hypot(W, H))[..., None]
    w = np.clip(d * 2.2, 0, 1)
    return img * (1 - w) + bl * w

def bulge(img, cx, cy, k):
    """lens deformation about (cx, cy): k > 0 magnifies the centre and compresses the edges (rush-in warp)"""
    if abs(k) < 1e-3: return img
    W, H = CTX["W"], CTX["H"]; xx, yy = _grid()
    R = 0.5 * math.hypot(W, H); dx, dy = (xx - cx) / R, (yy - cy) / R
    r2 = dx * dx + dy * dy
    f = 1 - k * np.exp(-r2 / 0.35)
    return cv2.remap(img, (cx + dx * f * R).astype(np.float32), (cy + dy * f * R).astype(np.float32),
                     cv2.INTER_LINEAR, borderMode=cv2.BORDER_REFLECT)

def twirl(img, cx, cy, ang, radius, blur_ang=0.0, n=1):
    """vortex: rotation that falls off with radius; optional angular motion blur (n samples over blur_ang)"""
    xx, yy = _grid()
    dx, dy = xx - cx, yy - cy; d = np.sqrt(dx * dx + dy * dy)
    fall = np.clip(1 - d / radius, 0, 1) ** 2
    acc = np.zeros_like(img)
    for k in range(n):
        a = (ang + (blur_ang * (k / (n - 1) - 0.5) if n > 1 else 0.0)) * fall
        c, s_ = np.cos(a), np.sin(a)
        mx = (cx + dx * c - dy * s_).astype(np.float32); my = (cy + dx * s_ + dy * c).astype(np.float32)
        acc += cv2.remap(img, mx, my, cv2.INTER_LINEAR, borderMode=cv2.BORDER_REFLECT)
    return acc / n

def own_light(img, thr=0.55, sigma=(6, 22, 60)):
    """bloom built from the frame's own highlights: the light carries the colours of the scene"""
    W, H = CTX["W"], CTX["H"]
    hi = np.clip(img - thr, 0, None)
    small = cv2.resize(hi, (W // 4, H // 4), interpolation=cv2.INTER_AREA)
    b = sum(cv2.GaussianBlur(small, (0, 0), s_) * w for s_, w in zip(sigma, (0.5, 0.35, 0.3)))
    return cv2.resize(b, (W, H), interpolation=cv2.INTER_LINEAR)


# ------------------------------------------------------------------ cameras
# ---- T1  (r2: faster accelerating push, swap at peak velocity under zoom blur + lens warp)
T1 = dict(T0=2.9, TH=3.45, S3=6.5, C=(0.778, 0.252), SW=(3.40, 3.48), WIN=(3.0, 3.85), P=2.6)
def L1(t):
    x = (t - T1["T0"]) / (T1["TH"] - T1["T0"])
    return math.log(T1["S3"]) * min(max(x, 0.0), 1.0) ** T1["P"]
def vel1(t):
    """log-zoom velocity (1/s) of the travelling, continued after the swap with an exponential decay"""
    D = T1["TH"] - T1["T0"]; vh = T1["P"] * math.log(T1["S3"]) / D
    if t <= T1["TH"]:
        x = min(max((t - T1["T0"]) / D, 0.0), 1.0); return vh * x ** (T1["P"] - 1)
    return vh * math.exp(-(t - T1["TH"]) / 0.07)
def cam_2A(t):
    L = L1(t); s = math.exp(L); u = L / math.log(T1["S3"])
    ax, ay = T1["C"]
    bx, by = clamp_dest(s, ax, ay, lerp(ax, 0.5, u), lerp(ay, 0.5, u))
    return dict(s=s, ax=ax, ay=ay, bx=bx, by=by)
def cam_3A(t):
    TH, S3 = T1["TH"], T1["S3"]
    if t <= TH:
        c2 = cam_2A(t)
        return dict(s=math.exp(L1(t)) / S3, ax=0.5, ay=0.5, bx=c2["bx"], by=c2["by"])
    vh = vel1(TH); tau = 0.07
    extra = min(vh * tau, math.log(1.45)) * (1 - math.exp(-(t - TH) / tau))
    extra *= 1 - smooth((t - 4.1) / 1.6)                      # slow hand-over to 3A's own push
    sd = math.exp(extra)
    sp, apx, apy = CTX["kf_interp"]([[3.417, 1.0, 0.5, 0.5], [5.7, 1.0, 0.62, 0.38], [6.083, 1.28, 0.62, 0.38]], t, (1, 2, 3))
    bx, by = apx + sp * (0.5 - apx), apy + sp * (0.5 - apy)
    return dict(s=sd * sp, ax=0.5, ay=0.5, bx=bx, by=by)

# ---- T2
T2 = dict(PUSH0=7.0, PEAK=7.5, SW0=7.46, SW1=7.54, END=7.9, LIGHT5A=(0.45, 0.38), WIN=(7.0, 7.9))
def cam_4A(t):
    if t < T2["PUSH0"]:
        s_, ax, ay, bx, by = CTX["kf_interp"]([[5.9, 1.0, 0.58, 0.36, 0.58, 0.36], [6.4, 1.0, 0.58, 0.36, 0.58, 0.36]], t, (1, 2, 3, 4, 5))
        return dict(s=s_, ax=ax, ay=ay, bx=bx, by=by)
    x = (t - T2["PUSH0"]) / (T2["SW1"] - T2["PUSH0"])
    lx, ly = lamp_at(t)
    s = 1 + 0.8 * ease_in(x, 2.2)
    bx, by = lerp(lx, 0.10, ease_in(x, 1.6)), lerp(ly, 0.38, ease_in(x, 1.6))
    bx, by = clamp_dest(s, lx, ly, bx, by)
    return dict(s=s, ax=lx, ay=ly, bx=bx, by=by)
def flare_state(t):
    """intensity, centre (normalised), for the T2 flare"""
    if t < T2["PEAK"]:
        I = ease_in((t - 7.08) / (T2["PEAK"] - 7.08), 2.4)
        c = cam_4A(t); return I, (c["bx"], c["by"])
    I = 1 - ease_out((t - T2["PEAK"]) / (T2["END"] - T2["PEAK"]), 1.7)
    c = cam_4A(T2["SW1"]); k = smooth((t - T2["PEAK"]) / (T2["END"] - T2["PEAK"]))
    return I, (lerp(c["bx"], T2["LIGHT5A"][0], k), lerp(c["by"], T2["LIGHT5A"][1], k))

# ---- T3  (r2: vortex + light built from the scene's own colours; swap at peak spin)
T3 = dict(A0=10.38, SW=10.66, B1=10.95, G=(0.51, 0.43), PEAK=math.radians(230), IMPACT=10.74, WIN=(10.38, 10.95))
def cam_6A(t):
    s = 1 + 0.22 * ease_in((t - T3["A0"]) / (T3["SW"] - T3["A0"]), 2.0)
    gx, gy = T3["G"]
    return dict(s=s, ax=gx, ay=gy, bx=gx, by=gy)
def cam_6B(t):
    s_, ax, ay, bx, by = CTX["kf_interp"]([[10.625, 1.0, 0.5, 0.5, 0.5, 0.5], [11.85, 1.0, 0.5, 0.5, 0.5, 0.5], [12.313, 1.3, 0.42, 0.45, 0.42, 0.45]], t, (1, 2, 3, 4, 5))
    dx = dy = 0.0
    if t >= T3["IMPACT"]:
        u = t - T3["IMPACT"]; e = 9 * math.exp(-u / 0.045)
        dx, dy = e * math.sin(u * 2 * math.pi * 29), e * math.sin(u * 2 * math.pi * 21 + 1.1)
    return dict(s=s_, ax=ax, ay=ay, bx=bx, by=by, dx=dx, dy=dy)
def spin(t):
    """vortex angle (rad, same sense throughout): winds up on 6A, unwinds on 6B"""
    if t < T3["SW"]:
        return T3["PEAK"] * ease_in((t - T3["A0"]) / (T3["SW"] - T3["A0"]), 2.6)
    return -T3["PEAK"] * (1 - ease_out((t - T3["SW"]) / (T3["B1"] - T3["SW"]), 2.2))
def spin_vel(t, h=1 / 120):
    if abs(t - T3["SW"]) > 2 * h:
        return (spin(t + h) - spin(t - h)) / (2 * h)
    return (spin(T3["SW"] - h) - spin(T3["SW"] - 2 * h)) / h

# ---- T4  (r2: push into the lettuce visible at the back of 7A; swap inside it at peak speed)
T4 = dict(D0=13.12, SW=13.62, SMAX=3.6, P=2.4, WIN=(13.2, 14.05))
def lettuce_at(t):
    return tracked("plano 7A", "S09", t, 44, (0.66, 0.42), 20, 70)
def L4(t):
    x = (t - T4["D0"]) / (T4["SW"] - T4["D0"])
    return math.log(T4["SMAX"]) * min(max(x, 0.0), 1.0) ** T4["P"]
def vel4(t):
    D = T4["SW"] - T4["D0"]; vh = T4["P"] * math.log(T4["SMAX"]) / D
    if t <= T4["SW"]:
        x = min(max((t - T4["D0"]) / D, 0.0), 1.0); return vh * x ** (T4["P"] - 1)
    return vh * math.exp(-(t - T4["SW"]) / 0.09)
def cam_7A(t):
    L = L4(t); s = math.exp(L); u = L / math.log(T4["SMAX"])
    ax, ay = lettuce_at(t)
    bx, by = clamp_dest(s, ax, ay, lerp(ax, 0.5, smooth(min(u * 1.2, 1))), lerp(ay, 0.5, smooth(min(u * 1.2, 1))))
    return dict(s=s, ax=ax, ay=ay, bx=bx, by=by)
def cam_8A(t):
    # full frame; forward energy is carried by blur + warp, then by 8A's own drift
    return dict(s=1.0, ax=0.5, ay=0.5, bx=0.5, by=0.5)

CAMS = dict(t1_2A=cam_2A, t1_3A=cam_3A, t2_4A=cam_4A, t3_6A=cam_6A, t3_6B=cam_6B, t4_7A=cam_7A, t4_8A=cam_8A)
def cam(name, t): return CAMS[name](t)


# ------------------------------------------------------------------ material looks
def color_gain_3A():
    if "g3" in _CACHE: return _CACHE["g3"]
    s2 = CTX["source"]("plano 2A"); s3 = CTX["source"]("plano 3A")
    a = s2.frames[int(s2.pos(2.9))].astype(np.float32); b = s3.frames[0].astype(np.float32)
    cx, cy = T1["C"]; w, h = int(s2.w / T1["S3"]), int(s2.h / T1["S3"])
    x0, y0 = int(cx * s2.w - w / 2), int(cy * s2.h - h / 2)
    ma = np.median(a[y0:y0 + h, x0:x0 + w].reshape(-1, 3), 0); mb = np.median(b[int(b.shape[0] * .25):, :].reshape(-1, 3), 0)
    r = ma / mb; lum = float(r @ np.float32([0.2126, 0.7152, 0.0722]))
    g = np.clip(lum + 0.3 * (r - lum), 0.75, 1.25).astype(np.float32)
    _CACHE["g3"] = g
    return g

def glassy(img, k):
    """cheese → translucent: desaturate, deepen transmission, sharpen speculars, refract"""
    if k <= 0: return img
    L = CTX["LUMA"]; y = img @ L
    gy, gx = np.gradient(cv2.GaussianBlur(y, (0, 0), 6))
    W, H = CTX["W"], CTX["H"]
    X, Y = np.meshgrid(np.arange(W, dtype=np.float32), np.arange(H, dtype=np.float32))
    ref = cv2.remap(img, X + gx * 260 * k, Y + gy * 260 * k, cv2.INTER_LINEAR, borderMode=cv2.BORDER_REFLECT)
    yr = ref @ L
    glass = yr[..., None] * np.float32([0.92, 0.95, 1.02]) * 0.75 + np.clip(yr - 0.65, 0, None)[..., None] * 1.6
    glass = glass + (ref - yr[..., None]) * 0.35
    return img * (1 - k) + glass * k

def chrome(img, k, sweep):
    """translucent → metal: luminance remapped through a chrome ramp, anisotropic highlight, moving specular"""
    if k <= 0: return img
    L = CTX["LUMA"]; y = np.clip(img @ L, 0, 1.2)
    band = 0.5 + 0.5 * np.cos(math.pi * (y * 2.4 + 0.15))
    steel = (0.05 + 0.8 * band ** 1.4)[..., None] * np.float32([1.0, 0.88, 0.74])     # warm gunmetal like 6B
    steel = steel + np.clip(y - 0.75, 0, None)[..., None] * 2.0
    edge = edges(img, 1.0)[..., None]
    steel = steel * (0.75 + 0.5 * edge)
    out = img * (1 - k) + steel * k
    return out + sweep[..., None] * np.clip(y, 0.2, 1)[..., None] * 1.4 * k

def leaf_colorize(y):
    stops = np.float32([[0.03, 0.08, 0.02], [0.13, 0.30, 0.06], [0.36, 0.60, 0.14], [0.78, 0.92, 0.48]])
    x = np.clip(y, 0, 1) * 3
    i = np.clip(x.astype(int), 0, 2); f = (x - i)[..., None]
    return stops[i] * (1 - f) + stops[i + 1] * f


# ------------------------------------------------------------------ flare
def flare(img, I, cx, cy, seed=3):
    """warm flare from a practical lamp passing near the lens: local exposure, out-of-focus disc,
    veiling glare that enters from the lamp side, restrained streak, faint ghosts, subtle CA"""
    if I <= 1e-3: return img
    W, H = CTX["W"], CTX["H"]; X, Y = cx * W, cy * H
    warm = np.float32([1.0, 0.82, 0.58]); cream = np.float32([1.0, 0.92, 0.78])
    d = radial(X, Y, 1.0)
    near = np.exp(-(d / (0.55 * W)) ** 2)[..., None]
    img = img * (1 + 0.3 * I + 1.1 * I * near)                               # exposure: global + local to the lamp
    hi = np.clip(img - 0.62, 0, None) * np.exp(-(d / (0.9 * W)) ** 2)[..., None]
    small = cv2.resize(hi, (W // 4, H // 4), interpolation=cv2.INTER_AREA)
    bloom = sum(w * cv2.GaussianBlur(small, (0, 0), s_) for s_, w in ((4, .5), (14, .35), (40, .3)))
    img = img + cv2.resize(bloom, (W, H)) * warm * (1.4 * I)
    veil = np.exp(-(d / (0.2 * W + 0.62 * W * I)) ** 2) * I
    img = img * (1 - 0.48 * veil[..., None]) + veil[..., None] * cream * 0.85
    disc = np.exp(-(d / (0.06 * W * (1 + 4.0 * I))) ** 4) * I ** 1.2          # defocused lamp = big soft bokeh
    img = img + disc[..., None] * cream * 0.9
    xx, yy = _grid()
    streak = np.exp(-((yy - Y) / (4 + 10 * I)) ** 2) * np.exp(-np.abs(xx - X) / (0.45 * W)) * 0.22 * I
    img = img + streak[..., None] * np.float32([1.0, 0.72, 0.42])
    vx, vy = W / 2 - X, H / 2 - Y
    for tpos, rad, col, a in ((0.55, 0.035, (1.0, 0.75, 0.45), .06), (1.25, 0.08, (0.95, 0.35, 0.6), .04), (1.7, 0.13, (1.0, 0.8, 0.5), .025)):
        gd = radial(X + vx * tpos * 2, Y + vy * tpos * 2, rad * W)
        img = img + (np.exp(-(gd ** 6)) * a * I)[..., None] * np.float32(col)
    img = img + 0.045 * I * warm                                             # veiling lift of blacks
    return chroma_aberration(img, 0.0035 * I)


# ------------------------------------------------------------------ windows
def window(name, t, fps):
    return np.asarray(dict(T1=win_T1, T2=win_T2, T3=win_T3, T4=win_T4)[name](t, fps), dtype=np.float32)

def win_T1(t, fps):
    """single accelerating push into the crust; the cut happens inside 2 frames at peak velocity,
    hidden by zoom blur and a lens rush-warp that both peak on the swap"""
    SEG = CTX["SEG"]; W, H = CTX["W"], CTX["H"]
    g3 = color_gain_3A()
    k = vel1(t) / vel1(T1["TH"])
    a = smooth((t - T1["SW"][0]) / (T1["SW"][1] - T1["SW"][0]))
    out = 0; cx = cy = None
    if a < 1:
        c = cam_2A(t); out = SEG["S03"].render(t, fps, max_n=24) * (1 - a)
        cx, cy = c["bx"] * W, c["by"] * H
    if a > 0:
        c3 = cam_3A(t); img3 = SEG["S04"].render(t, fps, max_n=24)
        gk = smooth((t - T1["TH"]) / 0.4)
        out = out + img3 * (g3 * (1 - gk) + gk) * a
        x3, y3 = c3["bx"] * W, c3["by"] * H
        cx, cy = (x3, y3) if cx is None else (lerp(cx, x3, a), lerp(cy, y3, a))
    out = zoom_blur(out, cx, cy, 0.22 * k ** 1.5)
    out = bulge(out, cx, cy, 0.22 * k ** 2)
    return out * (1 + 0.12 * k ** 3)

def _grid():
    if ("grid",) not in _CACHE:
        W, H = CTX["W"], CTX["H"]; yy, xx = np.mgrid[0:H, 0:W].astype(np.float32); _CACHE[("grid",)] = (xx, yy)
    return _CACHE[("grid",)]

def win_T2(t, fps):
    SEG = CTX["SEG"]; I, (fx, fy) = flare_state(t)
    a = smooth((t - T2["SW0"]) / (T2["SW1"] - T2["SW0"]))
    out = 0
    if a < 1:
        img4 = SEG["S05"].render(t, fps, max_n=24)
        img4 = blur(img4, 9.0 * ease_in((t - 7.15) / (T2["SW1"] - 7.15), 2.0))   # the lamp is now too close to focus
        out = img4 * (1 - a)
    if a > 0:
        img5 = SEG["S06"].render(t, fps)
        img5 = blur(img5, 6.0 * (1 - smooth((t - T2["SW0"]) / 0.3)))
        out = out + img5 * a
    return flare(out, I, fx, fy)

def win_T3(t, fps):
    """cheese ribbons wind into a vortex that drags their own amber/magenta light into spiral streaks;
    at peak spin the material changes; the gear world unwinds out of the same vortex and locks with an impact"""
    SEG = CTX["SEG"]; W, H = CTX["W"], CTX["H"]
    gx, gy = T3["G"][0] * W, T3["G"][1] * H
    ang = spin(t); w = abs(spin_vel(t)) / fps * 0.5
    e = min(1.0, abs(ang) / T3["PEAK"])
    a = smooth((t - (T3["SW"] - 0.035)) / 0.07)
    radius = 0.95 * H; nb = int(np.clip(w * 30, 1, 12))
    out = 0
    if a < 1:
        out = twirl(SEG["S07"].render(t, fps, max_n=16), gx, gy, ang, radius, w, nb) * (1 - a)
    if a > 0:
        out = out + twirl(SEG["S08"].render(t, fps, max_n=16), gx, gy, ang, radius, w, nb) * a
    L = own_light(out, 0.5)
    L = twirl(L, gx, gy, 0.0, radius, 0.9 * e + 0.1, n=10)
    out = out + L * (2.0 * e ** 1.6)
    core = np.exp(-(radial(gx, gy, 0.16 * W + 0.25 * W * e) ** 2))[..., None]
    out = out + core * np.float32([1.0, 0.62, 0.30]) * 0.55 * e ** 2
    out = chroma_aberration(out, 0.004 * e)
    if T3["IMPACT"] - 0.01 <= t < T3["IMPACT"] + 0.18:
        u = (t - T3["IMPACT"] + 0.01) / 0.19
        g = np.exp(-(radial(gx + (u - 0.5) * 0.35 * W, gy - 0.1 * W, 0.045 * W) ** 2))
        out = out + g[..., None] * np.float32([1.0, 0.95, 0.88]) * 0.7 * math.sin(math.pi * min(u, 1))
    return out

def veins(cx, cy, r0, grow, seed=5):
    """procedural leaf venation radiating from the opening: primary veins with secondary branches"""
    W, H = CTX["W"], CTX["H"]; xx, yy = _grid()
    dx, dy = xx - cx, yy - cy
    d = np.sqrt(dx * dx + dy * dy) + 1e-3; th = np.arctan2(dy, dx)
    nf = noise_field(seed, 5)
    wob = nf[..., 0] * 0.12 + 0.0006 * d
    prim = np.exp(-(np.sin(9 * (th + wob)) / 0.07) ** 2)                       # 18 primary veins
    sec = np.exp(-(np.sin(9 * (th + wob) * 3 + d / 45.0) / 0.10) ** 2) * 0.5   # oblique secondaries
    reach = r0 + grow
    front = np.clip((reach - d) / (0.12 * W), 0, 1) * (d > r0 * 0.98)
    fade = np.exp(-np.maximum(d - r0, 0) / (0.9 * W))
    return np.clip(prim + sec * (1 - prim), 0, 1) * front * fade

def win_T4(t, fps):
    """accelerating push into the lettuce at the back of 7A; organic melt + rush-warp grow with speed;
    at peak the illustration takes over inside the same green, then the blur releases"""
    SEG = CTX["SEG"]; W, H = CTX["W"], CTX["H"]
    k = vel4(t) / vel4(T4["SW"])
    a = smooth((t - (T4["SW"] - 0.05)) / 0.09)
    cx, cy = W * 0.5, H * 0.5
    out = 0
    if a < 1:
        c = cam_7A(t); cx, cy = c["bx"] * W, c["by"] * H
        img = displace(SEG["S09"].render(t, fps, max_n=24), noise_field(31, 3), 22 * k ** 2)
        out = img * (1 - a)
    if a > 0:
        img8 = displace(SEG["S10"].render(t, fps, max_n=24), noise_field(31, 3), 22 * k ** 2)
        out = out + img8 * a
        cx, cy = lerp(cx, 0.5 * W, a), lerp(cy, 0.5 * H, a)
    out = zoom_blur(out, cx, cy, 0.22 * k ** 1.4)
    out = bulge(out, cx, cy, 0.26 * k ** 2)
    return out + own_light(out, 0.6) * (0.6 * k ** 2)


# ------------------------------------------------------------------ T1.5 r2  (3A tunnel → 4A film set)
# Geometry: the tunnel mouth in 3A IS the arch in 4A (mouth ≈ 0.54 W wide at (0.63, 0.37); arch ≈ 0.83 W at
# (0.55, 0.40) → ratio 1.55). Camera = one push F(t) (beta-shaped velocity, peak inside the max-speed zone).
# 4A is locked to the same camera: s4 = s3 / 1.55, its arch centre on the mouth's current position, so both
# layers share scale AND vanishing point at every frame. 4A first appears INSIDE the mouth (the bread walls of 3A
# occlude its borders and fly out of frame), then takes the whole frame when s4 ≈ 1. Radial streaks converge on
# the vanishing point, peak while both layers are visible and fade out slowly with the deceleration.
from scipy.special import betainc
T15 = dict(P0=5.68, P1=6.24, A=(0.63, 0.37), DEST=(0.55, 0.40), RATIO=1.55, BA=3.0, BB=2.3,
           M0=5.86, M1=5.95, F0=6.04, F1=6.12, WIN=(5.55, 6.47))
def F15(t):
    x = min(max((t - T15["P0"]) / (T15["P1"] - T15["P0"]), 0.0), 1.0); return float(betainc(T15["BA"], T15["BB"], x))
def vel15(t, h=1 / 240):
    """normalised push speed (1 = peak)"""
    if not hasattr(vel15, "pk"):
        vel15.pk = max((F15(x + h) - F15(x - h)) for x in np.linspace(T15["P0"], T15["P1"], 400))
    return (F15(t + h) - F15(t - h)) / vel15.pk
def s3_15(t): return T15["RATIO"] ** F15(t)
def mouth_pos(t):
    u = F15(t); return lerp(T15["A"][0], T15["DEST"][0], u), lerp(T15["A"][1], T15["DEST"][1], u)
def cam_3A_15(t):
    if t <= T15["P0"]:
        return cam_3A(t)
    bx, by = mouth_pos(t)
    return dict(s=s3_15(t), ax=T15["A"][0], ay=T15["A"][1], bx=bx, by=by)
def cam_4A_15(t):
    if t >= T15["P1"]:
        return cam_4A(t)
    bx, by = mouth_pos(t)
    return dict(s=s3_15(t) / T15["RATIO"], ax=T15["DEST"][0], ay=T15["DEST"][1], bx=bx, by=by)
CAMS["t15_3A"] = cam_3A_15
CAMS["t15_4A"] = cam_4A_15

def blur15(t):
    """streak amount: rises with the push, plateau in the max-speed zone, slow release (gradual detail)"""
    up = smooth((t - 5.74) / (5.92 - 5.74))
    down = math.exp(-max(t - 6.04, 0.0) / 0.095)                  # deceleration: detail comes back gradually
    return up * down

def radial_streak(img, cx, cy, amount, center_keep=0.22):
    """camera-advance blur: samples along rays from the vanishing point (outward), stronger towards the edges"""
    if amount < 0.005: return img
    W, H = CTX["W"], CTX["H"]; h2, w2 = H // 2, W // 2
    small = cv2.resize(img, (w2, h2), interpolation=cv2.INTER_AREA)
    n = int(np.clip(amount * 90, 4, 28)); acc = np.zeros_like(small)
    for k in range(n):
        f = math.exp(amount * (k / (n - 1) - 0.5))       # symmetric in log-scale: streaks without shifting geometry
        M = np.float32([[1 / f, 0, (1 - 1 / f) * cx / 2], [0, 1 / f, (1 - 1 / f) * cy / 2]])
        acc += cv2.warpAffine(small, M, (w2, h2), flags=cv2.INTER_LINEAR, borderMode=cv2.BORDER_REFLECT)
    bl = cv2.resize(acc / n, (W, H), interpolation=cv2.INTER_LINEAR)
    d = radial(cx, cy, 0.5 * math.hypot(W, H))
    w = np.clip(center_keep + (1 - center_keep) * np.clip(d * 2.4, 0, 1), 0, 1)[..., None]
    return img * (1 - w) + bl * w

def win_T15(t, fps):
    SEG = CTX["SEG"]; W, H = CTX["W"], CTX["H"]
    mx, my = mouth_pos(t); cx, cy = mx * W, my * H; s3 = s3_15(t)
    # 4A visibility: first through the mouth (occluded by the 3A bread walls), then full frame
    a_in = smooth((t - T15["M0"]) / (T15["M1"] - T15["M0"]))
    a_full = smooth((t - T15["F0"]) / (T15["F1"] - T15["F0"]))
    img3 = SEG["S04"].render(t, fps, max_n=24) if a_full < 1 else None
    img4 = SEG["S05"].render(t, fps, max_n=24) if a_in > 0 else None
    if img4 is None:
        out = img3
    elif img3 is None:
        out = img4
    else:
        xx, yy = _grid()
        rx, ry = 0.27 * s3 * W, 0.14 * s3 * H
        e = np.sqrt(((xx - cx) / rx) ** 2 + ((yy - cy) / ry) ** 2)
        mouth = 1 - np.clip((e - 0.55) / 0.6, 0, 1); mouth = mouth * mouth * (3 - 2 * mouth)
        m = np.maximum(mouth * a_in, a_full)[..., None]
        out = img3 * (1 - m) + img4 * m
    k = blur15(t)
    out = radial_streak(out, cx, cy, 0.42 * k)
    # the set's real light beam blooms through the mouth for a few frames (warm, local, never a white frame)
    v = max(0.0, vel15(t))
    L = own_light(out, 0.6)
    wloc = np.exp(-(radial(cx, cy - 0.06 * H, 0.30 * W * s3) ** 2))[..., None]
    out = out + L * wloc * (1.3 * v ** 3)
    return out
_WINDOWS_EXTRA = dict(T15=win_T15)
_window_orig = window
def window(name, t, fps):
    if name in _WINDOWS_EXTRA:
        return np.asarray(_WINDOWS_EXTRA[name](t, fps), dtype=np.float32)
    return _window_orig(name, t, fps)
