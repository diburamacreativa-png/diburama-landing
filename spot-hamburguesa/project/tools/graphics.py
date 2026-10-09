"""DIBURAMA spot — end graphics (copy, official logo, CTA).

The logo is the client's file marca/logo_alfa.png, untouched in shape. For the dark
background its grey glyphs are re-coloured to the light grey (#F1F1F1) used by the
client's own dark-background variant marca/logo_diburama.png; the magenta drop
(with its face) and the magenta dot keep their original pixels. The drop is animated
by translation only.
"""
import os, math, numpy as np, cv2
from PIL import Image, ImageDraw, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
W, H = 1080, 1920
MAGENTA = (228, 14, 119)
WHITE = (241, 241, 241)
SUB = (196, 198, 204)
FONT_DIR = "/usr/share/fonts/opentype/inter"
F_COPY = os.path.join(FONT_DIR, "InterDisplay-Bold.otf")
F_CTA = os.path.join(FONT_DIR, "InterDisplay-SemiBold.otf")
F_URL = os.path.join(FONT_DIR, "InterDisplay-Medium.otf")
VARIANT_DESCRIPTOR = os.environ.get("DIBURAMA_DESCRIPTOR") == "1"   # "Vídeos para empresas" variant

def ease_out_expo(x):
    x = min(max(x, 0.0), 1.0); return 1.0 if x >= 1 else 1 - 2 ** (-10 * x)
def ease_in_cubic(x):
    x = min(max(x, 0.0), 1.0); return x ** 3
def ease_out_cubic(x):
    x = min(max(x, 0.0), 1.0); return 1 - (1 - x) ** 3


class Layer:
    """premultiplied float RGBA sprite placed at (x, y) in canvas pixels"""
    def __init__(self, rgba, x, y):
        a = rgba[..., 3:4].astype(np.float32) / 255.0
        self.rgb = rgba[..., :3].astype(np.float32) / 255.0 * a
        self.a = a; self.x, self.y = x, y
        self.h, self.w = rgba.shape[:2]


def text_layer(txt, font_path, size, color, tracking=0.0, accent_last=None):
    """render text with tracking; optional accent colour for the final character (Diburama's magenta dot)"""
    f = ImageFont.truetype(font_path, size)
    pad = int(size * 0.35)
    widths = [f.getlength(c) for c in txt]
    total = sum(widths) + tracking * size * (len(txt) - 1)
    im = Image.new("RGBA", (int(total + 2 * pad), int(size * 1.5 + 2 * pad)), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    x = pad
    for i, c in enumerate(txt):
        col = accent_last if (accent_last and i == len(txt) - 1) else color
        d.text((x, pad), c, font=f, fill=col + (255,))
        x += widths[i] + tracking * size
    arr = np.array(im)
    ys, xs = np.where(arr[..., 3] > 0)
    asc, _ = f.getmetrics()
    return arr, pad, pad + asc, total  # sprite, left pad, baseline y inside sprite, advance width


def load_logo():
    im = np.array(Image.open(os.path.join(ROOT, "marca", "logo_alfa.png")).convert("RGBA"))
    x0, x1, y0, y1 = 496, 1561, 272, 678          # alpha bbox of the official artwork
    im = im[y0 - 8:y1 + 8, x0 - 8:x1 + 8].copy()
    ox, oy = x0 - 8, y0 - 8
    rgb = im[..., :3].astype(int)
    grey = (np.abs(rgb[..., 0] - rgb[..., 1]) < 40) & (np.abs(rgb[..., 1] - rgb[..., 2]) < 40)
    # drop region (with its face lines) in original coordinates
    dbox = (628 - ox, 748 - ox, max(0, 262 - oy), 415 - oy)
    drop = np.zeros_like(im); drop[dbox[2]:dbox[3], dbox[0]:dbox[1]] = im[dbox[2]:dbox[3], dbox[0]:dbox[1]]
    body = im.copy(); body[dbox[2]:dbox[3], dbox[0]:dbox[1]] = 0
    body[..., :3][grey & (body[..., 3] > 0)] = WHITE
    return body, drop


class EndCard:
    def __init__(self, g):
        self.b = g["beats"]; self.t0 = g["start"]; self.t1 = g["end"]
        yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
        r = np.sqrt(((xx - W * 0.5) / W) ** 2 + ((yy - H * 0.45) / H) ** 2)
        c0, c1 = np.float32([0.115, 0.122, 0.138]), np.float32([0.045, 0.048, 0.056])   # graphite
        k = np.clip(r / 0.75, 0, 1)[..., None] ** 1.4
        self.bg = c0 * (1 - k) + c1 * k
        # copy block: left aligned editorial block, 4 lines, centred vertically in the safe area
        size = 126; lh = 1.02 * size; x = 104
        lines = [("QUE QUIERAN", None), ("VERLO ENTERO.", MAGENTA), ("Y QUE LO", None), ("ENTIENDAN.", MAGENTA)]
        top = 0.315 * H
        rendered = [text_layer(txt, F_COPY, size, WHITE, tracking=-0.012, accent_last=acc) for txt, acc in lines]
        x = (W - max(r[3] for r in rendered)) / 2      # left-aligned block, optically centred in frame
        self.copy = []
        for i, (arr, pad, base, adv) in enumerate(rendered):
            gap = 0.42 * size if i >= 2 else 0
            by = top + i * lh + gap + size  # baseline
            self.copy.append(dict(layer=Layer(arr, x - pad, by - base), clip=(by - size * 0.98, by + size * 0.26), group=0 if i < 2 else 1, idx=i % 2))
        # logo
        body, drop = load_logo()
        s = 860 / body.shape[1]
        bw, bh = int(round(body.shape[1] * s)), int(round(body.shape[0] * s))
        body = cv2.resize(body, (bw, bh), interpolation=cv2.INTER_AREA)
        drop = cv2.resize(drop, (bw, bh), interpolation=cv2.INTER_AREA)
        lx, ly = (W - bw) / 2, 0.40 * H - bh / 2
        self.logo = Layer(body, lx, ly); self.drop = Layer(drop, lx, ly)
        # CTA + URL
        arr, pad, base, adv = text_layer("¿COCINAMOS EL TUYO?", F_CTA, 74, WHITE, tracking=0.0)
        self.cta_by = 0.585 * H
        self.cta = Layer(arr, (W - adv) / 2 - pad, self.cta_by - base)
        arr, pad, base, adv = text_layer("videodiburama.com", F_URL, 46, SUB, tracking=0.03)
        self.url_by = 0.585 * H + 90
        self.url = Layer(arr, (W - adv) / 2 - pad, self.url_by - base)
        self.desc = None
        if VARIANT_DESCRIPTOR:
            arr, pad, base, adv = text_layer("VÍDEOS PARA EMPRESAS", F_URL, 34, SUB, tracking=0.16)
            self.desc = Layer(arr, (W - adv) / 2 - pad, 0.40 * H + bh / 2 + 52 - base)

    def put(self, img, L, dx=0.0, dy=0.0, alpha=1.0, clip=None, xclip=None):
        if alpha <= 0.001: return
        x, y = L.x + dx, L.y + dy
        ix, iy = int(math.floor(x)), int(math.floor(y)); fx, fy = x - ix, y - iy
        M = np.float32([[1, 0, fx], [0, 1, fy]])
        rgb = cv2.warpAffine(L.rgb, M, (L.w + 1, L.h + 1), flags=cv2.INTER_LINEAR)
        a = cv2.warpAffine(L.a, M, (L.w + 1, L.h + 1), flags=cv2.INTER_LINEAR)[..., None]
        x0, y0, x1, y1 = ix, iy, ix + L.w + 1, iy + L.h + 1
        cy0, cy1 = (clip if clip else (0, H))
        cx0, cx1 = (xclip if xclip else (0, W))
        X0, Y0 = max(x0, 0, int(math.ceil(cx0))), max(y0, 0, int(math.ceil(cy0)))
        X1, Y1 = min(x1, W, int(cx1)), min(y1, H, int(cy1))
        if X1 <= X0 or Y1 <= Y0: return
        sr, sa = rgb[Y0 - y0:Y1 - y0, X0 - x0:X1 - x0] * alpha, a[Y0 - y0:Y1 - y0, X0 - x0:X1 - x0] * alpha
        img[Y0:Y1, X0:X1] = img[Y0:Y1, X0:X1] * (1 - sa) + sr

    def render(self, t):
        b = self.b
        img = self.bg.copy()
        # fade up from black
        fin = ease_out_cubic((t - self.t0) / 0.25)
        # -- copy: masked rise per line, exit upwards
        for c in self.copy:
            L = c["layer"]; lh = c["clip"][1] - c["clip"][0]
            start = (b["line1"] if c["group"] == 0 else b["line2"]) + 0.07 * c["idx"]
            p = ease_out_expo((t - start) / 0.55)
            q = ease_in_cubic((t - (b["copy_out"] + 0.03 * (c["group"] * 2 + c["idx"]))) / 0.26)
            dy = (1 - p) * lh * 1.05 - q * lh * 1.1
            if p > 0 and q < 1:
                self.put(img, L, dy=dy, clip=c["clip"])
        # -- logo body: soft left→right reveal with slight drift
        if t >= b["logo"]:
            p = ease_out_cubic((t - b["logo"]) / 0.6)
            edge = self.logo.x - 60 + (self.logo.w + 120) * p
            self.put(img, self.logo, dx=(1 - p) * -18, alpha=min(1.0, p * 1.6), xclip=(0, edge))
            if self.desc is not None:
                self.put(img, self.desc, dy=(1 - ease_out_expo((t - b["logo"] - 0.5) / 0.5)) * 14,
                         alpha=ease_out_cubic((t - b["logo"] - 0.5) / 0.4))
        # -- drop: falls into place (translation only), small settle
        land = b["drop_land"]; fall = 0.42
        if t >= land - fall:
            if t < land:
                x = (t - (land - fall)) / fall
                dy = -330 * (1 - x * x); al = min(1.0, x * 3)
            else:
                u = t - land
                dy = -9 * math.exp(-u / 0.07) * math.sin(u * 2 * math.pi / 0.16) if u < 0.5 else 0.0; al = 1.0
            self.put(img, self.drop, dy=dy, alpha=al)
        # -- CTA + URL
        p = ease_out_expo((t - b["cta"]) / 0.55)
        if p > 0:
            self.put(img, self.cta, dy=(1 - p) * 84, clip=(self.cta_by - 76, self.cta_by + 26))
        p = ease_out_cubic((t - b["url"]) / 0.45)
        if p > 0:
            self.put(img, self.url, dy=(1 - p) * 12, alpha=p)
        return img * fin


_CARD = None
def render(t, g):
    global _CARD
    if _CARD is None: _CARD = EndCard(g)
    return _CARD.render(t)
