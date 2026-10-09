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


# ------------------------------------------------------------------ cameras
# ---- T1
T1 = dict(T0=2.45, TH=3.55, S3=6.5, C=(0.778, 0.252), WIN=(3.15, 3.95))
def L1(t):
    x = (t - T1["T0"]) / (T1["TH"] - T1["T0"])
    return math.log(T1["S3"]) * min(max(x, 0.0), 1.0) ** 2
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
    vh = 2 * math.log(S3) / (TH - T1["T0"]); tau = 0.09
    extra = vh * tau * (1 - math.exp(-(t - TH) / tau))
    extra *= 1 - smooth((t - 4.3) / 1.2)                      # hand the velocity over to 3A's own push
    sd = math.exp(extra)
    sp, apx, apy = CTX["kf_interp"]([[3.417, 1.0, 0.5, 0.5], [5.7, 1.0, 0.62, 0.38], [6.083, 1.28, 0.62, 0.38]], t, (1, 2, 3))
    bx, by = apx + sp * (0.5 - apx), apy + sp * (0.5 - apy)   # compose centred digital push with V1's end push
    return dict(s=sd * sp, ax=0.5, ay=0.5, bx=bx, by=by)

# ---- T2
T2 = dict(PUSH0=7.0, PEAK=7.5, SW0=7.46, SW1=7.54, END=7.9, LIGHT5A=(0.45, 0.38), WIN=(7.0, 7.9))
def cam_4A(t):
    if t < T2["PUSH0"]:
        s_, ax, ay, bx, by = CTX["kf_interp"]([[5.917, 1.06, 0.58, 0.36, 0.58, 0.36], [6.4, 1.0, 0.58, 0.36, 0.58, 0.36]], t, (1, 2, 3, 4, 5))
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

# ---- T3
T3 = dict(A0=10.2, A1=10.98, G=(0.51, 0.43), B0=10.6, B1=11.05, BL0=10.62, BL1=10.95, IMPACT=10.84, WIN=(10.2, 11.05))
def loop_at(t):
    return tracked("plano 6A", "S07", t, 76, (0.49, 0.35), 60, 98)
def cam_6A(t):
    p = (t - T3["A0"]) / (T3["A1"] - T3["A0"])
    cx, cy = loop_at(t); e = ease_in(p, 2.0)
    bx, by = lerp(cx, T3["G"][0], smooth(p)), lerp(cy, T3["G"][1], smooth(p))
    return dict(s=1 + 0.3 * e, sx=1 + 0.35 * e, rot=40 * ease_in(p, 1.6), ax=cx, ay=cy, bx=bx, by=by)
def cam_6B(t):
    if t >= T3["B1"]:
        s_, ax, ay, bx, by = CTX["kf_interp"]([[10.625, 1.0, 0.5, 0.5, 0.5, 0.5], [11.85, 1.0, 0.5, 0.5, 0.5, 0.5], [12.313, 1.3, 0.42, 0.45, 0.42, 0.45]], t, (1, 2, 3, 4, 5))
        return dict(s=s_, ax=ax, ay=ay, bx=bx, by=by)
    q = ease_out((t - T3["B0"]) / (T3["B1"] - T3["B0"]), 2.0)
    gx, gy = T3["G"]
    sh = 0.0
    if t >= T3["IMPACT"]:
        u = t - T3["IMPACT"]; sh = 7 * math.exp(-u / 0.05)
    return dict(s=lerp(1.18, 1.0, q), sx=lerp(1.15, 1.0, q), rot=lerp(-24, 0, q), ax=gx, ay=gy, bx=gx, by=gy,
                dx=sh * math.sin(u * 2 * math.pi * 31) if sh else 0.0, dy=sh * math.sin(u * 2 * math.pi * 23 + 1) if sh else 0.0)

# ---- T4
# bearing of 7A (unique frames 37–44): centre ≈ (0.065, 0.789) of the source, inner race radius ≈ 0.13 × width
T4 = dict(D0=13.15, D1=13.92, SMAX=4.2, C=(0.065, 0.789), R=0.13, O0=13.42, WIN=(13.25, 14.35))
def L4(t):
    x = (t - T4["D0"]) / (T4["D1"] - T4["D0"])
    return math.log(T4["SMAX"]) * min(max(x, 0.0), 1.0) ** 2.0
def cam_7A(t):
    L = L4(t); s = math.exp(L); u = L / math.log(T4["SMAX"])
    ax, ay = T4["C"]
    bx, by = clamp_dest(s, ax, ay, lerp(ax, 0.5, u), lerp(ay, 0.52, u))
    return dict(s=s, ax=ax, ay=ay, bx=bx, by=by)
def hole(t):
    """hole centre (px), physical inner-race radius (px) and organic opening factor"""
    c = cam_7A(min(t, T4["D1"])); W = CTX["W"]
    o = ease_in((t - T4["O0"]) / (T4["D1"] - T4["O0"]), 2.2)
    return c["bx"] * W, c["by"] * CTX["H"], T4["R"] * c["s"] * W, o
def cam_8A(t):
    # full frame from the start of the opening (no mirrored borders); 8A's own forward drift gives depth
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
    SEG = CTX["SEG"]; TH, S3 = T1["TH"], T1["S3"]
    g3 = color_gain_3A()
    if t >= TH:
        img3 = SEG["S04"].render(t, fps, max_n=24)
        k = smooth((t - TH) / 0.4)
        return img3 * (g3 * (1 - k) + k)
    L = L1(t)
    img2 = SEG["S03"].render(t, fps, max_n=24)
    defocus = 7.0 * smooth((L - math.log(2.2)) / (math.log(S3) - math.log(2.2)))
    img2 = blur(img2, defocus)
    img3 = SEG["S04"].render(t, fps, max_n=24)            # reflect-padded; the mask below hides the padding
    img3 = blur(img3, 4.5 * (1 - smooth((L - math.log(3.0)) / (math.log(S3) - math.log(3.0))))) * g3
    W, H = CTX["W"], CTX["H"]; c3 = cam_3A(t); k = c3["s"]
    xx, yy = _grid()
    r = np.sqrt(((xx - c3["bx"] * W) / (0.5 * k * W)) ** 2 + ((yy - c3["by"] * H) / (0.5 * k * H)) ** 2)
    m = 1 - np.clip((r - 0.35) / 0.6, 0, 1); m = m * m * (3 - 2 * m)
    m = np.maximum(m, smooth((L - math.log(4.6)) / (math.log(S3) - math.log(4.6))))
    m = (m * smooth((L - math.log(2.0)) / (math.log(3.4) - math.log(2.0))))[..., None]
    return img2 * (1 - m) + img3 * m

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
    SEG = CTX["SEG"]; W, H = CTX["W"], CTX["H"]
    p = (t - T3["A0"]) / (T3["A1"] - T3["A0"])
    pb = (t - T3["BL0"]) / (T3["BL1"] - T3["BL0"])
    out = None
    if t < T3["A1"]:
        img6 = SEG["S07"].render(t, fps, max_n=24)
        c = cam_6A(t); cx, cy = c["bx"] * W, c["by"] * H
        spread = np.clip(1.25 - radial(cx, cy, 0.18 * W + 0.75 * W * smooth(p / 0.85)), 0, 1)[..., None]
        kg = smooth(p / 0.38) * (1 - smooth((p - 0.45) / 0.3))
        km = smooth((p - 0.3) / 0.35)
        sw_pos = (t - 10.62) / 0.26
        xx, yy = _grid()
        diag = (xx / W * 0.8 + yy / H * 0.45) - (-0.2 + 1.6 * sw_pos)
        sweep = np.exp(-(diag / 0.06) ** 2) * (0 < sw_pos < 1.2)
        m = glassy(img6, kg)
        m = chrome(m, km, sweep.astype(np.float32))
        out = img6 * (1 - spread) + m * spread
    if t >= T3["B0"]:
        img6b = SEG["S08"].render(t, fps, max_n=24)
        if out is None or pb >= 1:
            out = img6b
        else:
            y = cv2.GaussianBlur(cv2.resize(img6b @ CTX["LUMA"], (W // 4, H // 4)), (0, 0), 2)
            y = cv2.resize((y - y.min()) / (np.ptp(y) + 1e-6), (W, H))
            thr = 1.1 - 1.45 * smooth(pb)
            a = np.clip((y - thr) / 0.45, 0, 1)
            a = np.maximum(a, smooth((pb - 0.55) / 0.45))[..., None]
            out = out * (1 - a) + img6b * a
        # specular glint on the gear as it locks in
        if T3["IMPACT"] - 0.02 <= t < T3["IMPACT"] + 0.2:
            u = (t - T3["IMPACT"] + 0.02) / 0.22
            c = cam_6B(t)
            g = np.exp(-(radial(c["bx"] * W + (u - 0.5) * 0.4 * W, c["by"] * H - 0.12 * W, 0.05 * W) ** 2))
            out = out + g[..., None] * np.float32([1.0, 0.97, 0.92]) * 0.8 * math.sin(math.pi * min(u, 1))
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
    SEG = CTX["SEG"]; W, H = CTX["W"], CTX["H"]
    hx, hy, r, o = hole(t)
    img8 = SEG["S10"].render(t, fps, max_n=24)
    q8 = smooth((t - T4["O0"]) / 0.35)
    img8 = blur(img8, 6.0 * (1 - q8))                                        # world beyond: defocused, then sharp
    if t >= T4["D1"]:
        k = smooth((t - T4["D1"]) / (T4["WIN"][1] - T4["D1"]))
        e8 = edges(img8, 1.2)
        return img8 + e8[..., None] * np.float32([0.62, 0.95, 0.35]) * 0.55 * (1 - k) ** 1.6
    img7 = SEG["S09"].render(t, fps, max_n=24)
    p = smooth((t - 13.3) / (T4["D1"] - 13.3))
    xx, yy = _grid(); d = np.sqrt((xx - hx) ** 2 + (yy - hy) ** 2)
    th = np.arctan2(yy - hy, xx - hx)
    # organic opening: the inner race softens and dilates with an irregular, living edge
    edge_r = r * (0.92 + 2.4 * o) * (1 + 0.07 * o * np.sin(5 * th + 7 * t) + 0.05 * o * noise_field(21, 4)[..., 0])
    zone = np.clip(1 - (d - edge_r) / (1.3 * r + 0.25 * W), 0, 1)               # metal near the opening
    img7 = displace(img7, noise_field(11, 3), 10 * p) * zone[..., None] + img7 * (1 - zone[..., None])
    # metal → organic: around the opening the bronze takes chlorophyll, its machined lines glow as veins
    y = img7 @ CTX["LUMA"]
    leaf = leaf_colorize(cv2.GaussianBlur(y, (0, 0), 1.5) * 1.05)
    km = (zone * smooth((p - 0.15) / 0.6))[..., None] * 0.85
    base = img7 * (1 - km) + leaf * km
    e7 = edges(img7, 1.4)
    v = veins(hx, hy, edge_r.mean(), (0.15 + 1.1 * smooth((p - 0.2) / 0.7)) * W)
    lines = np.maximum(0.25 * e7 * zone * smooth((p - 0.1) / 0.4), 0.9 * v * smooth((p - 0.25) / 0.5))
    base = base * (1 - 0.35 * lines[..., None]) + lines[..., None] * np.float32([0.66, 0.95, 0.32]) * 0.9
    # backlit membrane rim + the illustrated world seen through the opening
    a = np.clip((edge_r - d) / (0.05 * r + 3), 0, 1)
    rim = np.exp(-((d - edge_r) / (0.03 * r + 4)) ** 2) * smooth(o / 0.3)
    comp = base * (1 - a[..., None]) + img8 * a[..., None]
    return comp + rim[..., None] * np.float32([0.85, 1.0, 0.45]) * 0.6
