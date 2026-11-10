# DIBURAMA · THERMOLIME · "LO HACEMOS VISIBLE" — librería de composición
# Todo el trabajo se hace en BGR float32 [0..1] sobre un lienzo 1080x1920.
import os, subprocess, functools
import numpy as np, cv2
from PIL import Image, ImageDraw, ImageFont

W, H, FPS = 1080, 1920, 25
HERE = os.path.dirname(os.path.abspath(__file__))
FONTS = os.path.join(HERE, "fonts")
SRC_VIDEO = os.environ.get("THERMO_SRC", os.path.join(HERE, "in", "thermo.mp4"))

# Paleta (BGR)
def hexbgr(h):
    h = h.lstrip('#'); return np.array([int(h[4:6], 16), int(h[2:4], 16), int(h[0:2], 16)], np.float32) / 255
NAVY = hexbgr('#0A1222'); NAVY_D = hexbgr('#04070F'); WHITE = np.ones(3, np.float32)
FUCHSIA = hexbgr('#E6197D')  # fucsia de marca usado en las piezas Diburama del repositorio

# ---------------------------------------------------------------- easing
def clamp(x, a=0.0, b=1.0): return max(a, min(b, x))
def seg(f, a, b): return clamp((f - a) / float(b - a)) if b != a else float(f >= a)
def eo(x): x = clamp(x); return 1 - 2 ** (-10 * x) if x < 1 else 1.0          # expo out
def ei(x): x = clamp(x); return 2 ** (10 * (x - 1)) if x > 0 else 0.0           # expo in
def eio(x): x = clamp(x); return 4 * x ** 3 if x < .5 else 1 - (-2 * x + 2) ** 3 / 2
def qo(x): x = clamp(x); return 1 - (1 - x) ** 3
def lerp(a, b, t): return a + (b - a) * t
def pulse(f, at, amp, decay=3.5):
    """golpe de escala ligado a un acento: sube en 1 fotograma y decae exponencialmente"""
    if f < at: return 0.0
    return amp * np.exp(-(f - at) / decay)

# ---------------------------------------------------------------- fuente de vídeo
class Source:
    def __init__(self, path=SRC_VIDEO):
        self.path = path; self.cache = {}
    def load(self, i0, n):
        need = [i for i in range(i0, i0 + n) if i not in self.cache]
        if not need: return
        a, b = min(need), max(need)
        raw = subprocess.run(["ffmpeg", "-v", "error", "-ss", f"{a/FPS:.4f}", "-i", self.path,
                              "-frames:v", str(b - a + 1), "-f", "rawvideo", "-pix_fmt", "bgr24", "-"],
                             capture_output=True, check=True).stdout
        arr = np.frombuffer(raw, np.uint8).reshape(-1, 1080, 1920, 3)
        for k in range(arr.shape[0]): self.cache[a + k] = arr[k]
    def frame(self, i):
        if i not in self.cache: self.load(i, 1)
        return self.cache[i]
    def at(self, t):
        """fotograma a tiempo fraccionario (mezcla lineal entre vecinos, para ralentís suaves)"""
        x = t * FPS; i = int(np.floor(x + 1e-6)); fr = x - i
        a = self.frame(i)
        if fr < 0.02: return a
        b = self.frame(i + 1)
        return cv2.addWeighted(a, 1 - fr, b, fr, 0)

SRC = Source()

def f32(img): return img.astype(np.float32) / 255.0

# ---------------------------------------------------------------- cámara / capas
def cam_M(cx, cy, s, ax=W / 2, ay=H / 2, rot=0.0):
    """matriz que lleva el punto fuente (cx,cy) al punto de lienzo (ax,ay) con escala s"""
    c, sn = np.cos(rot), np.sin(rot)
    return np.array([[s * c, -s * sn, ax - s * (c * cx - sn * cy)],
                     [s * sn, s * c, ay - s * (sn * cx + c * cy)]], np.float32)

def warp(img, M, interp=cv2.INTER_LANCZOS4, border=cv2.BORDER_REFLECT):
    return cv2.warpAffine(img, M, (W, H), flags=interp, borderMode=border)

def warp_blur(img, Ms, interp=cv2.INTER_CUBIC):
    """desenfoque de movimiento real: promedio de varias posiciones de cámara dentro del obturador"""
    if len(Ms) == 1: return f32(warp(img, Ms[0]))
    acc = np.zeros((H, W, 3), np.float32)
    for M in Ms: acc += warp(img, M, interp).astype(np.float32)
    return acc / (255.0 * len(Ms))

def shutter(fn, f, n=1, span=0.6):
    """devuelve matrices muestreadas entre f-span y f (fn(f)->M)"""
    if n <= 1: return [fn(f)]
    return [fn(f - span + span * k / (n - 1)) for k in range(n)]

def sharpen(img, amt=0.35, sigma=1.2):
    b = cv2.GaussianBlur(img, (0, 0), sigma)
    return np.clip(img + amt * (img - b), 0, 1)

def circle_mask(cx, cy, r, feather=2.0):
    yy, xx = np.ogrid[:H, :W]
    d = np.sqrt((xx - cx) ** 2 + (yy - cy) ** 2)
    return np.clip((r - d) / max(feather, 1e-3) + 0.5, 0, 1).astype(np.float32)

def ring_draw(canvas, cx, cy, r, width, color, alpha):
    yy, xx = np.ogrid[:H, :W]
    d = np.abs(np.sqrt((xx - cx) ** 2 + (yy - cy) ** 2) - r)
    m = np.clip(width / 2 - d + 0.5, 0, 1)[..., None] * alpha
    return canvas * (1 - m) + color * m

def over(dst, src, a):
    """composición 'over' con alfa (H,W) o escalar"""
    if np.isscalar(a): return dst * (1 - a) + src * a
    a = a[..., None] if a.ndim == 2 else a
    return dst * (1 - a) + src * a

def vgrad(y0, y1, a0, a1):
    """máscara vertical de gradiente (para velos de legibilidad)"""
    y = np.arange(H, dtype=np.float32)
    t = np.clip((y - y0) / (y1 - y0), 0, 1); t = t * t * (3 - 2 * t)
    return np.repeat((a0 + (a1 - a0) * t)[:, None], W, 1)

def vignette(strength=0.35):
    yy, xx = np.mgrid[:H, :W].astype(np.float32)
    d = np.sqrt(((xx - W / 2) / (W * 0.75)) ** 2 + ((yy - H / 2) / (H * 0.62)) ** 2)
    return (1 - strength * np.clip(d, 0, 1.4) ** 2)[..., None].astype(np.float32)
VIG = None

def tech_bg(f, grid=True):
    """fondo tecnológico: degradado azul noche + retícula técnica muy tenue (diseño propio, sin stock)"""
    global VIG
    if VIG is None: VIG = vignette(0.55)
    y = np.linspace(0, 1, H, dtype=np.float32)[:, None, None]
    bg = (NAVY * (1 - y) * 1.15 + NAVY_D * y)[:, :, :] * np.ones((1, W, 1), np.float32)
    if grid:
        g = np.zeros((H, W), np.float32); step = 72; off = int((f * 0.6) % step)
        g[(np.arange(H) + off) % step == 0, :] = 1; g[:, (np.arange(W) + off // 2) % step == 0] = 1
        bg = bg + 0.035 * g[..., None]
    return np.clip(bg * VIG, 0, 1)

_rng = np.random.default_rng(7)
GRAIN = [cv2.GaussianBlur(_rng.normal(0, 1, (H, W)).astype(np.float32), (0, 0), 0.7) for _ in range(6)]
def grain(img, f, amt=0.018):
    g = GRAIN[f % 6][..., None]
    return np.clip(img + amt * g, 0, 1)

def drop_shadow(alpha, dx=0, dy=24, blur=40, opacity=0.55):
    s = cv2.GaussianBlur(alpha, (0, 0), blur)
    M = np.float32([[1, 0, dx], [0, 1, dy]])
    return cv2.warpAffine(s, M, (W, H)) * opacity

# ---------------------------------------------------------------- tipografía
FONT_FILES = {
    'black': 'InterDisplay-Black.otf', 'xbold': 'InterDisplay-ExtraBold.otf', 'bold': 'InterDisplay-Bold.otf',
    'semi': 'InterDisplay-SemiBold.otf', 'medium': 'InterDisplay-Medium.otf', 'light': 'InterDisplay-Light.otf',
    'xlight': 'InterDisplay-ExtraLight.otf', 'brand': 'SpaceGrotesk-700.ttf', 'brand5': 'SpaceGrotesk-500.ttf'}

@functools.lru_cache(None)
def font(name, size): return ImageFont.truetype(os.path.join(FONTS, FONT_FILES[name]), int(size))

def text_width(txt, name, size, tracking=0.0):
    f = font(name, size)
    return f.getlength(txt) + tracking * size * max(len(txt) - 1, 0)

def fit_size(txt, name, maxw, maxsize, tracking=0.0):
    s = maxsize
    while s > 10 and text_width(txt, name, s, tracking) > maxw: s -= 1
    return s

@functools.lru_cache(None)
def text_layer(txt, name, size, tracking=0.0, stroke=0, outline=False, pad=None):
    """capa RGBA (float32) de un texto, alineada a la caja de cuerpo (cap-height estable)"""
    f = font(name, size)
    pad = pad if pad is not None else int(size * 0.35) + stroke
    asc, desc = f.getmetrics()
    w = int(np.ceil(text_width(txt, name, size, tracking))) + 2 * pad
    h = asc + desc + 2 * pad
    img = Image.new('L', (w, h), 0); d = ImageDraw.Draw(img)
    x = pad
    if tracking == 0:
        kw = dict(stroke_width=stroke, stroke_fill=255) if stroke else {}
        d.text((x, pad), txt, font=f, fill=0 if outline else 255, **kw)
    else:
        for i, ch in enumerate(txt):
            px = pad + f.getlength(txt[:i]) + tracking * size * i
            kw = dict(stroke_width=stroke, stroke_fill=255) if stroke else {}
            d.text((px, pad), ch, font=f, fill=0 if outline else 255, **kw)
    a = np.asarray(img, np.float32) / 255
    if outline:  # sólo contorno: dibujar trazo y vaciar el interior
        inner = Image.new('L', (w, h), 0); di = ImageDraw.Draw(inner)
        if tracking == 0: di.text((x, pad), txt, font=f, fill=255)
        else:
            for i, ch in enumerate(txt):
                di.text((pad + f.getlength(txt[:i]) + tracking * size * i, pad), ch, font=f, fill=255)
        ai = np.asarray(inner, np.float32) / 255
        a = np.clip(a - ai, 0, 1)
    # metadatos útiles: desplazamiento hasta la línea de mayúsculas
    cap_top = pad + (asc - int(size * 0.727))  # Inter cap-height ≈ 0.727 em
    return a, pad, cap_top

def put(canvas, alpha_img, x, y, color=WHITE, opacity=1.0, mask=None, shadow=0.0, scale=1.0, blur=0.0):
    """pega una capa alfa en (x,y) (esquina sup-izq, puede ser fraccionaria) con escala opcional"""
    a = alpha_img
    if blur > 0.3: a = cv2.GaussianBlur(a, (0, 0), blur)
    h, w = a.shape
    M = np.float32([[scale, 0, x], [0, scale, y]])
    full = cv2.warpAffine(a, M, (W, H), flags=cv2.INTER_LINEAR)
    if mask is not None: full = full * mask
    full = full * opacity
    if shadow > 0 and opacity > 0:
        sh = drop_shadow(full, 0, 6, 14, shadow)
        canvas = canvas * (1 - sh[..., None])
    return canvas * (1 - full[..., None]) + np.asarray(color, np.float32) * full[..., None]

def line_mask_x(x0, x1, feather=8):
    xx = np.arange(W, dtype=np.float32)[None, :]
    m = np.clip((x1 - xx) / feather + 0.5, 0, 1) * np.clip((xx - x0) / feather + 0.5, 0, 1)
    return np.repeat(m, H, 0)

def line_mask_y(y0, y1, feather=8):
    yy = np.arange(H, dtype=np.float32)[:, None]
    m = np.clip((y1 - yy) / feather + 0.5, 0, 1) * np.clip((yy - y0) / feather + 0.5, 0, 1)
    return np.repeat(m, W, 1)

class TextBlock:
    """texto con posición por línea de mayúsculas: (x, cap_y) = esquina superior izquierda de las mayúsculas"""
    def __init__(self, txt, name, size, tracking=0.0, outline=False, stroke=0):
        self.a, self.pad, self.cap = text_layer(txt, name, int(size), tracking, stroke, outline)
        self.size = int(size); self.txt = txt
        self.w = text_width(txt, name, size, tracking)
        self.caph = size * 0.727
    def draw(self, canvas, x, cap_y, **kw):
        sc = kw.get('scale', 1.0)
        # escala alrededor del centro del texto
        cx = x + self.w / 2; cy = cap_y + self.caph / 2
        ox = cx - (self.pad + self.w / 2) * sc; oy = cy - (self.cap + self.caph / 2) * sc
        return put(canvas, self.a, ox, oy, **kw)
