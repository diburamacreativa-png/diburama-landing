# DIBURAMA · THERMOLIME — «VENTANA A LO INVISIBLE» (V3)
# Sistema gráfico reutilizable: ventana panorámica 16:9 nítida (siempre REDUCIDA desde el original, nunca ampliada),
# fondo atmosférico derivado del plano o fondo limpio de diseño, y capa gráfica (lente, escáner, anotaciones).
import numpy as np, cv2
from lib import (W, H, FPS, SRC, TextBlock, fit_size, text_width, put, over, circle_mask, line_mask_x, line_mask_y,
                 vgrad, drop_shadow, eo, ei, eio, qo, seg, lerp, clamp, pulse, hexbgr, WHITE)

# ------------------------------------------------------------------ identidad
GRAPHITE, PETROL = hexbgr('#101419'), hexbgr('#102A39')
FUCHSIA = hexbgr('#D64B96')            # provisional (sustituir por el del logotipo oficial)
GREY = np.array([0.74, 0.74, 0.74], np.float32)
SCAN = np.array([1.0, 0.95, 0.86], np.float32)
WIN, WIN_L = 1000, 1040                # anchos de ventana (px de lienzo)

# ------------------------------------------------------------------ cues (fotogramas sobre acentos medidos)
MICRO, PART, BURST, MERGED = 42, 83, 100, 117
PROP, CMP, CMP_SCAN, CMP_KICK, CMP_OUT = 133, 162, 175, 200, 208
TECH, TECH_RING, TECH_LINK, TECH_CLICK = 217, 233, 242, 250
ROLL, SPRAY, ARCH = 300, 321, 367
CLX = [408, 417, 425, 433]; BRAND, LAST, END = 442, 483, 500

# ------------------------------------------------------------------ fuentes del original
B_IDX, AFTER_IDX, PLAIN_IDX = 1440, 1590, 1733          # 57.60 antes · 63.60 después · 69.32 sistema liso
LENS = (883.0, 493.0, 405.0)
_c = {}

def setup():
    if _c: return
    B, C = SRC.frame(B_IDX), SRC.frame(AFTER_IDX)
    mk = np.full((1080, 1920), 255, np.uint8); cv2.circle(mk, (883, 495), 420, 0, -1); cv2.rectangle(mk, (1080, 120), (1720, 320), 0, -1)
    orb = cv2.ORB_create(6000)
    ka, da = orb.detectAndCompute(cv2.cvtColor(C, 6), mk); kb, db = orb.detectAndCompute(cv2.cvtColor(B, 6), mk)
    m = cv2.BFMatcher(cv2.NORM_HAMMING, crossCheck=True).match(db, da)
    pb = np.float32([kb[x.queryIdx].pt for x in m]); pa = np.float32([ka[x.trainIdx].pt for x in m])
    M, _ = cv2.estimateAffinePartial2D(pb, pa, ransacReprojThreshold=2.5)
    _c['after'] = cv2.warpAffine(C, M, (1920, 1080), flags=cv2.INTER_CUBIC | cv2.WARP_INVERSE_MAP)
    for i0, n in [(1424, 46), (180, 45), (907, 20), (953, 16), (985, 20), (425, 30), (1733, 4), (1760, 125),
                  (3317, 22), (4785, 50), (5515, 42), (1873, 14), (4245, 8), (5450, 3)]:
        SRC.load(i0, n)

def S(t): return SRC.at(t)

# ------------------------------------------------------------------ capas
def win_image(src, w):
    """el plano completo, reducido con filtro de área (máxima nitidez, sin halos)"""
    h = int(round(w * 9 / 16))
    return cv2.resize(src, (w, h), interpolation=cv2.INTER_AREA).astype(np.float32) / 255

def bg_atmos(src, f, dark=0.5, sat=0.78, zoom=1.0, drift=(0.0, 0.0)):
    """fondo atmosférico: copia del plano, ampliada, desenfoque fuerte (~70 px a resolución completa), oscurecida, desaturada"""
    small = cv2.resize(src, (240, 135), interpolation=cv2.INTER_AREA).astype(np.float32) / 255
    small = cv2.GaussianBlur(small, (0, 0), 5.0)
    s = H / 135 * 1.06 * zoom
    cx = 120 + drift[0] + 6 * np.sin(f / 60); cy = 67.5 + drift[1] + 3 * np.cos(f / 75)
    M = np.float32([[s, 0, W / 2 - s * cx], [0, s, H / 2 - s * cy]])
    bg = cv2.warpAffine(small, M, (W, H), flags=cv2.INTER_LINEAR, borderMode=cv2.BORDER_REFLECT)
    g = bg.mean(2, keepdims=True); bg = g + (bg - g) * sat
    return np.clip(bg * dark, 0, 1)

_GRAD = {}
def bg_clean(kind='graphite', grid=0.0, f=0):
    key = kind
    if key not in _GRAD:
        y = np.linspace(0, 1, H, dtype=np.float32)[:, None, None]
        top, bot = (PETROL, GRAPHITE) if kind == 'petrol' else (GRAPHITE * 1.25, GRAPHITE * 0.8)
        g = top * (1 - y) + bot * y
        yy, xx = np.mgrid[:H, :W].astype(np.float32)
        vig = 1 - 0.35 * np.clip(((xx - W / 2) / (W * 0.8)) ** 2 + ((yy - H / 2) / (H * 0.65)) ** 2, 0, 1.5)
        _GRAD[key] = np.clip(g * np.ones((1, W, 1), np.float32) * vig[..., None], 0, 1)
    img = _GRAD[key].copy()
    if grid > 0:
        gm = np.zeros((H, W), np.float32); step = 80; off = int(f * 0.5) % step
        gm[(np.arange(H) + off) % step == 0, :] = 1; gm[:, (np.arange(W) + off // 2) % step == 0] = 1
        img = np.clip(img + grid * gm[..., None], 0, 1)
    return img

def place_window(canvas, win, cx, cy, alpha=1.0, frame=True, ticks=1.0, clip=None):
    """coloca la ventana en posición entera (sin re-muestreo: nitidez intacta) con sombra, filo fino y marcas de esquina"""
    h, w = win.shape[:2]
    x0, y0 = int(round(cx - w / 2)), int(round(cy - h / 2))
    m = np.zeros((H, W), np.float32)
    xa, ya, xb, yb = max(0, x0), max(0, y0), min(W, x0 + w), min(H, y0 + h)
    if xb <= xa or yb <= ya: return canvas, (x0, y0, w, h)
    m[ya:yb, xa:xb] = 1
    if clip is not None: m *= clip
    if frame:
        sh = drop_shadow(m, 0, 26, 36, 0.6 * alpha)
        canvas = canvas * (1 - sh[..., None])
    lay = canvas.copy(); lay[ya:yb, xa:xb] = win[ya - y0:yb - y0, xa - x0:xb - x0]
    canvas = over(canvas, lay, m * alpha)
    if frame and alpha > 0.05:
        e = cv2.morphologyEx(m, cv2.MORPH_GRADIENT, np.ones((2, 2), np.uint8)) * 0.22 * alpha
        canvas = np.clip(canvas + e[..., None], 0, 1)
        if ticks > 0: canvas = corner_ticks(canvas, x0, y0, w, h, ticks * alpha)
    return canvas, (x0, y0, w, h)

def corner_ticks(canvas, x0, y0, w, h, a, L=22, off=12):
    m = np.zeros((H, W), np.float32)
    for (cx, cy, sx, sy) in [(x0 - off, y0 - off, 1, 1), (x0 + w + off, y0 - off, -1, 1), (x0 - off, y0 + h + off, 1, -1), (x0 + w + off, y0 + h + off, -1, -1)]:
        cv2.line(m, (cx, cy), (cx + sx * L, cy), 1.0, 2, cv2.LINE_AA); cv2.line(m, (cx, cy), (cx, cy + sy * L), 1.0, 2, cv2.LINE_AA)
    return over(canvas, np.broadcast_to(WHITE, canvas.shape), m * 0.55 * a)

def ring(canvas, cx, cy, r, a=1.0, prog=1.0, width=1.6, color=WHITE, start=-np.pi / 2):
    if a <= 0 or prog <= 0: return canvas
    x0, x1 = int(max(0, cx - r - 4)), int(min(W, cx + r + 4)); y0, y1 = int(max(0, cy - r - 4)), int(min(H, cy + r + 4))
    if x1 <= x0 or y1 <= y0: return canvas
    yy, xx = np.mgrid[y0:y1, x0:x1].astype(np.float32)
    d = np.abs(np.sqrt((xx - cx) ** 2 + (yy - cy) ** 2) - r)
    ang = (np.arctan2(yy - cy, xx - cx) - start) % (2 * np.pi)
    m = np.clip(width / 2 - d + 0.5, 0, 1) * (ang <= prog * 2 * np.pi) * a
    sub = canvas[y0:y1, x0:x1]; canvas[y0:y1, x0:x1] = sub * (1 - m[..., None]) + np.asarray(color, np.float32) * m[..., None]
    return canvas

def dot(canvas, x, y, r, color=FUCHSIA, a=1.0):
    return over(canvas, np.broadcast_to(np.asarray(color, np.float32), canvas.shape), circle_mask(x, y, r, 1.2) * a)

def seg_line(canvas, p0, p1, a=0.8, w=1.6, color=WHITE, prog=1.0):
    if prog <= 0 or a <= 0: return canvas
    p0 = np.asarray(p0, np.float32); p1 = np.asarray(p1, np.float32); q = p0 + (p1 - p0) * prog
    m = np.zeros((H, W), np.float32)
    cv2.line(m, (int(p0[0] * 8), int(p0[1] * 8)), (int(q[0] * 8), int(q[1] * 8)), 1.0, max(1, int(round(w))), cv2.LINE_AA, shift=3)
    return over(canvas, np.broadcast_to(np.asarray(color, np.float32), canvas.shape), m * a)

def vscan(canvas, x, y0, y1, a=1.0):
    """línea de escáner vertical (núcleo + halo), puede salir de la ventana"""
    if a <= 0: return canvas
    xx = np.arange(W, dtype=np.float32)[None, :]
    band = (np.clip(1.6 - np.abs(xx - x), 0, 1) + 0.32 * np.exp(-((xx - x) / 18) ** 2)) * line_mask_y(y0, y1, 6) * a
    return np.clip(canvas + band[..., None] * SCAN, 0, 1)

def hscan(canvas, y, x0, x1, a=1.0):
    if a <= 0: return canvas
    yy = np.arange(H, dtype=np.float32)[:, None]
    band = (np.clip(1.6 - np.abs(yy - y), 0, 1) + 0.32 * np.exp(-((yy - y) / 18) ** 2)) * line_mask_x(x0, x1, 6) * a
    return np.clip(canvas + band[..., None] * SCAN, 0, 1)

def to_win(box, sx, sy):
    x0, y0, w, h = box; return x0 + sx * w / 1920, y0 + sy * h / 1080

# ------------------------------------------------------------------ tipografía
T = {}
def build_text():
    if T: return
    s = min(fit_size("¿CÓMO MUESTRAS", 'black', 840, 112), fit_size("LO QUE NO SE VE?", 'black', 840, 112)); T['s1'] = s
    T['q1'] = TextBlock("¿CÓMO MUESTRAS", 'black', s); T['q2'] = TextBlock("LO QUE NO SE VE?", 'black', s)
    s = min(fit_size("LA TECNOLOGÍA,", 'black', 840, 112), fit_size("AL DESCUBIERTO.", 'black', 840, 112)); T['s2'] = s
    T['t1'] = TextBlock("LA TECNOLOGÍA,", 'black', s); T['t2'] = TextBlock("AL DESCUBIERTO", 'black', s); T['t2dot'] = TextBlock(".", 'black', s)
    T['dib'] = TextBlock("DIBURAMA", 'brand', fit_size("DIBURAMA", 'brand', 760, 150, 0.06), tracking=0.06)
    T['sub'] = TextBlock("LO DIFÍCIL DE EXPLICAR,", 'semi', fit_size("LO DIFÍCIL DE EXPLICAR,", 'semi', 640, 46), tracking=0.04)
    sm = fit_size("LO HACEMOS VISIBLE", 'black', 840, 96); T['sm'] = sm
    T['main'] = TextBlock("LO HACEMOS VISIBLE", 'black', sm); T['maindot'] = TextBlock(".", 'black', sm)
    T['antes'] = TextBlock("ANTES", 'semi', 26, tracking=0.2); T['despues'] = TextBlock("DESPUÉS", 'semi', 26, tracking=0.2)

_ID = {}
def ident(canvas, f, f0, num, label, y, x=80, a_out=1.0):
    """identificador editorial: número fucsia + etiqueta gris, con filete fino"""
    p = eo(seg(f, f0, f0 + 8)) * a_out
    if p <= 0: return canvas
    key = (num, label)
    if key not in _ID: _ID[key] = (TextBlock(num, 'bold', 26, tracking=0.12), TextBlock(label, 'semi', 26, tracking=0.2))
    n, l = _ID[key]
    canvas = seg_line(canvas, (x, y + 9), (x + 34, y + 9), a=0.9 * p, w=2, color=FUCHSIA, prog=p)
    canvas = n.draw(canvas, x + 48 + 10 * (1 - p), y, color=FUCHSIA, opacity=p)
    return l.draw(canvas, x + 48 + n.w + 16 + 10 * (1 - p), y, color=GREY, opacity=p)

def title_lines(canvas, f, lines, y, f_out=None):
    """titular: cada línea aparece con máscara ascendente (no subtítulo: forma parte de la composición)"""
    out = eo(seg(f, f_out, f_out + 5)) if f_out is not None else 0.0
    for t, fi, dy, extra in lines:
        p = eo(seg(f, fi - 1, fi + 6))
        if p <= 0: continue
        yy = y + dy
        clip = line_mask_y(yy - 40, yy + t.caph + 10, 2)
        canvas = t.draw(canvas, 80, yy + 48 * (1 - p) - 30 * out, mask=clip, opacity=1 - out)
        if extra is not None:
            canvas = extra[0].draw(canvas, 80 + t.w + 2, yy + 48 * (1 - p) - 30 * out, mask=clip, opacity=1 - out, color=FUCHSIA)
    return canvas

# ================================================================== 0–41 · EL MISTERIO (Composición A)
WCY = 1010
def s_mystery(f):
    src = S(57.40 + f / FPS * 0.8)          # rótulo ya legible («Puente térmico»)
    bg = bg_atmos(src, f, dark=0.42)
    k = 1 + 0.05 * (1 - eo(seg(f, -1, 6)))
    win = win_image(src, int(WIN * k) // 2 * 2)
    img, box = place_window(bg, win, W / 2, WCY - 10 * seg(f, 0, MICRO))
    lx, ly = to_win(box, LENS[0], LENS[1]); lr = LENS[2] * box[2] / 1920
    # lente de exploración: anillo que se dibuja + línea de exploración dentro del círculo
    img = ring(img, lx, ly, lr + 12, a=0.85, prog=eo(seg(f, 2, 16)))
    for a_ in range(4):
        th = a_ * np.pi / 2; p = eo(seg(f, 10, 18))
        img = seg_line(img, (lx + (lr + 18) * np.cos(th), ly + (lr + 18) * np.sin(th)), (lx + (lr + 30) * np.cos(th), ly + (lr + 30) * np.sin(th)), a=0.85 * p, w=2)
    img = dot(img, lx + (lr + 12) * np.cos(-np.pi / 2 + eo(seg(f, 2, 16)) * 2 * np.pi), ly + (lr + 12) * np.sin(-np.pi / 2 + eo(seg(f, 2, 16)) * 2 * np.pi), 5, a=eo(seg(f, 2, 5)))
    if 14 <= f <= 36:
        ys = lerp(ly - lr, ly + lr, eio(seg(f, 14, 34)))
        dx = np.sqrt(max(0, lr ** 2 - (ys - ly) ** 2))
        img = hscan(img, ys, lx - dx, lx + dx, a=0.8 * (1 - seg(f, 32, 36)))
    if f >= 34:   # la lente crece: anticipa el cambio de mundo
        img = ring(img, lx, ly, (lr + 12) * (1 + 0.18 * eio(seg(f, 34, MICRO))), a=0.9, width=2.0)
    img = title_lines(img, f, [(T['q1'], -1, 0, None)], 455)
    img = ident(img, f, 6, "01", "TERMOGRAFÍA", box[1] + box[3] + 44)
    return img, box, (lx, ly, lr)

# ================================================================== 42–82 · DESCUBRIR OTRO MUNDO (lente → microscópico)
def s_micro_scene(f):
    src = S(7.20 + (f - MICRO) / FPS)
    bg = bg_atmos(src, f, dark=0.5, sat=0.9, zoom=1.15, drift=(-8 * seg(f, MICRO, PART), 0))
    win = win_image(src, WIN)
    img, box = place_window(bg, win, W / 2, WCY - 10 - 8 * seg(f, MICRO, PART))
    return img, box

def s_micro(f):
    new, box = s_micro_scene(f)
    q2 = T['q2']; s = T['s1']
    if f < MICRO + 9:     # la lente se abre como un iris y contiene el nuevo mundo
        old, obox, (lx, ly, lr) = s_mystery(MICRO - 1)
        x = seg(f, MICRO - 1, MICRO + 8); k = 1 - (1 - x) ** 2.4
        R = lerp((lr + 12) * 1.18, 1300, k)
        img = over(old, new, circle_mask(lx, ly, R, 2.0))
        img = ring(img, lx, ly, R, a=0.9 * (1 - x), width=2.0)
        img = dot(img, lx, ly - R, 6, a=1 - x)
    else:
        img = new
    out = 78
    img = title_lines(img, f, [(T['q1'], -10, 0, None), (q2, MICRO, s * 0.98, None)], 455, f_out=out)
    img = ident(img, f, MICRO + 4, "02", "MICROESTRUCTURA", box[1] + box[3] + 44, a_out=1 - seg(f, out, out + 5))
    return img

# ================================================================== 83–132 · VIAJE MICROSCÓPICO (Composición C: la partícula sale del marco)
def s_particles(f):
    if f < BURST:
        src = S(36.30 + (f - PART) / FPS)
    elif f < MERGED:
        src = S(38.12 + (f - BURST) / FPS * 0.7)
    else:
        src = S(39.40 + (f - MERGED) / FPS)
    glow = 0.42 + (0.16 * (1 - seg(f, BURST, MERGED)) if f >= BURST and f < MERGED else 0)
    bg = over(bg_clean('graphite'), bg_atmos(src, f, dark=glow, sat=0.9, zoom=1.25), 0.8)   # el fondo responde a la luz del plano
    cy = 820 - 20 * seg(f, PART, MERGED)
    win = win_image(src, WIN)
    img, box = place_window(bg, win, W / 2, cy)
    if f >= BURST:   # la esfera atraviesa los límites de la ventana (máscara circular 2.5D)
        if f < MERGED:
            pc, pr = (1000.0, 530.0), 330.0
            sc_ = lerp(1.0, 1.85, eo(seg(f, BURST - 1, BURST + 7)))
        else:
            pc, pr = (760.0, 525.0), 345.0
            sc_ = 1.62 * (1 + 0.06 * (1 - eo(seg(f, MERGED - 1, MERGED + 5)))) + sum(pulse(f, q, 0.04, 2.5) for q in (121, 125, 129))
        px, py = to_win(box, *pc)
        s_abs = box[2] / 1920 * sc_                                   # sigue siendo < 1: reducción, no ampliación
        M = np.float32([[s_abs, 0, px - s_abs * pc[0]], [0, s_abs, py - s_abs * pc[1]]])
        lay = cv2.warpAffine(src, M, (W, H), flags=cv2.INTER_AREA).astype(np.float32) / 255
        m = circle_mask(px, py, pr * s_abs, 1.5)
        img = img * (1 - drop_shadow(m, 0, 24, 30, 0.55)[..., None])
        img = over(img, lay, m)
        img = ring(img, px, py, pr * s_abs + 8, a=0.6, width=1.4)
    return img

# ================================================================== 133–161 · PROPIEDAD VISIBLE (Composición B sobre fondo petróleo)
def s_property(f):
    src = S(17.00 + (f - PROP) / FPS)
    img = bg_clean('petrol', grid=0.025, f=f)
    k = 1 + 0.04 * (1 - eo(seg(f, PROP - 1, PROP + 5)))
    img, box = place_window(img, win_image(src, int(WIN * k) // 2 * 2), W / 2, 820)
    # corchetes que destacan el edificio cuyo color revela la propiedad
    p = eo(seg(f, PROP + 3, PROP + 12))
    x0, y0 = to_win(box, 560, 60); x1, y1 = to_win(box, 1310, 1010)
    for (ax, ay, sx, sy) in [(x0, y0, 1, 1), (x1, y0, -1, 1), (x0, y1, 1, -1), (x1, y1, -1, -1)]:
        img = seg_line(img, (ax, ay), (ax + sx * 30, ay), a=0.9 * p, w=2); img = seg_line(img, (ax, ay), (ax, ay + sy * 30), a=0.9 * p, w=2)
    img = ident(img, f, PROP + 2, "03", "AISLAMIENTO TÉRMICO", box[1] + box[3] + 44)
    return img

# ================================================================== 162–216 · REVELACIÓN TÉRMICA (escáner antes / después)
def cmp_line(f):
    if f < CMP_SCAN: return None
    if f < CMP_KICK: return lerp(1.0, 0.0, eio(seg(f, CMP_SCAN, CMP_KICK - 2)))      # recorre: derecha → izquierda
    if f < CMP_OUT: return lerp(0.0, 0.5, eo(seg(f, CMP_KICK - 1, CMP_KICK + 6)))    # vuelve al centro: comparación
    return lerp(0.5, 1.6, ei(seg(f, CMP_OUT, TECH)))                                  # sale de la ventana: prepara el golpe

def s_compare(f):
    before, after = SRC.frame(B_IDX), _c['after']
    img = bg_clean('graphite', grid=0.018, f=f)
    img = over(img, bg_atmos(before, f, dark=0.5), 0.35)
    cy = 960 - 10 * seg(f, CMP, TECH)
    wb, wa = win_image(before, WIN), win_image(after, WIN)
    u = cmp_line(f)
    win = wb if u is None else over(wb, wa, _xmask(wb, u))     # a la derecha de la línea: «después»
    img, box = place_window(img, win, W / 2, cy)
    x0, y0, w, h = box
    if u is not None:
        xl = x0 + u * w
        img = vscan(img, xl, y0 - 70, y0 + h + 70, a=1.0)
        if u <= 1.0:
            img = dot(img, xl, y0 - 70, 5); img = dot(img, xl, y0 + h + 70, 5)
        pa = eo(seg(f, CMP_KICK, CMP_KICK + 7)) * (1 - seg(f, CMP_OUT, CMP_OUT + 4))
        if pa > 0:
            img = T['antes'].draw(img, xl - 24 - T['antes'].w, y0 - 62, color=GREY, opacity=pa)
            img = T['despues'].draw(img, xl + 24, y0 - 62, color=WHITE, opacity=pa)
    img = ident(img, f, CMP + 3, "04", "PUENTE TÉRMICO", y0 + h + 44, a_out=1 - seg(f, CMP_OUT, CMP_OUT + 4))
    return img

def _xmask(win, u):
    h, w = win.shape[:2]; xx = np.arange(w, dtype=np.float32)[None, :]
    return np.repeat(np.clip((xx - u * w) / 2 + 0.5, 0, 1), h, 0)

# ================================================================== 217–299 · LA GRAN REVELACIÓN (sistema multicapa)
def s_tech(f):
    t_open = 70.40 + max(0, f - TECH - 8) / FPS * 1.79
    opened = S(min(t_open, 75.3))
    img = bg_clean('petrol', grid=0.03, f=f)
    img = over(img, bg_atmos(opened, f, dark=0.55), 0.25)
    k = 1 + 0.06 * (1 - eo(seg(f, TECH - 1, TECH + 6)))
    w = int(WIN_L * k) // 2 * 2
    cy = 1050 - 16 * seg(f, TECH, ROLL)
    if f < TECH + 8:   # 1-2: primera representación → la línea recorre y revela la comparación
        u = lerp(1.04, -0.04, eio(seg(f, TECH - 1, TECH + 7)))
        wp, wo = win_image(SRC.frame(PLAIN_IDX), w), win_image(S(70.40), w)
        win = over(wp, wo, _xmask(wp, u))
        img, box = place_window(img, win, W / 2, cy)
        img = vscan(img, box[0] + u * box[2], box[1] - 90, box[1] + box[3] + 90, a=1.0)
    else:
        img, box = place_window(img, win_image(opened, w), W / 2, cy)
    # 3: círculos sobre los dos componentes revelados + conexión
    pr = eo(seg(f, TECH_RING - 1, TECH_RING + 10))
    if pr > 0:
        (ax, ay), (bx, by) = to_win(box, 323, 745), to_win(box, 1313, 740)
        ra, rb = 330 * box[2] / 1920, 300 * box[2] / 1920
        img = ring(img, ax, ay, ra, a=0.85, prog=pr, width=1.8)
        img = ring(img, bx, by, rb, a=0.85, prog=pr, width=1.8, start=np.pi / 2)
        pl = eo(seg(f, TECH_LINK - 1, TECH_CLICK + 2))
        if pl > 0:
            p0 = (ax + ra * 0.7071, ay + ra * 0.7071); p1 = (bx - rb * 0.7071, by + rb * 0.7071)
            img = seg_line(img, p0, p1, a=0.9, w=2, prog=pl)
            img = dot(img, *p0, 5)
            if f >= TECH_CLICK: img = dot(img, *p1, 5 * (1 + 0.5 * pulse(f, TECH_CLICK, 1.0, 2)))
    s = T['s2']
    img = title_lines(img, f, [(T['t1'], TECH, 0, None), (T['t2'], TECH + 4, s * 0.98, (T['t2dot'],))], box[1] - 70 - s * 0.727 * 2 - s * 0.25, f_out=ROLL - 5)
    img = ident(img, f, TECH + 6, "05", "SISTEMA MULTICAPA", box[1] + box[3] + 44, a_out=1 - seg(f, ROLL - 5, ROLL))
    return img

# ================================================================== 300–320 · DEL DISEÑO A LA REALIDAD (rodillo)
def s_roller(f):
    # díptico editorial: dos ventanas desplazadas (macro sobre ladrillo + macro del rodillo cargado)
    a, b = S(132.70 + (f - ROLL) / FPS), S(130.00 + (f - ROLL) / FPS)
    img = bg_atmos(a, f, dark=0.4, sat=0.7)
    k = 1 + 0.05 * (1 - eo(seg(f, ROLL - 1, ROLL + 5)))
    img, ba = place_window(img, win_image(a, int(880 * k) // 2 * 2), 60 + 440 + 8 * seg(f, ROLL, SPRAY), 700)
    pb = eo(seg(f, ROLL + 3, ROLL + 9))
    if pb > 0:
        img, bb = place_window(img, win_image(b, 880), W - 60 - 440 + 120 * (1 - pb), 700 + 248 + 24 + 248, alpha=pb)
        img = seg_line(img, (ba[0] + 40, ba[1] + ba[3] + 12), (ba[0] + 40, bb[1] + bb[3] - 40), a=0.5 * pb, w=1.5)
        img = dot(img, ba[0] + 40, ba[1] + ba[3] + 12, 4, a=pb)
    return ident(img, f, ROLL + 2, "06", "APLICACIÓN", 700 + 248 + 24 + 496 + 44)

# ================================================================== 321–366 · APLICACIÓN DEL MATERIAL (proyección) → arquitectura
def spray_scene(f):
    src = S(191.40 + (f - SPRAY) / FPS)
    bg = over(bg_clean('graphite', grid=0.015, f=f), bg_atmos(src, f, dark=0.5, sat=0.75, zoom=1.2, drift=(10 * seg(f, SPRAY, ARCH), 0)), 0.45)
    k = 1 + 0.04 * (1 - eo(seg(f, SPRAY - 1, SPRAY + 5)))
    img, box = place_window(bg, win_image(src, int(WIN_L * k) // 2 * 2), W / 2, 760 - 14 * seg(f, SPRAY, ARCH))
    return ident(img, f, SPRAY + 2, "07", "PROYECCIÓN", box[1] + box[3] + 44)

def arch_scene(f):
    src = SRC.frame(5515 + max(0, f - ARCH))
    bg = bg_atmos(src, f, dark=0.42, sat=0.75, zoom=1.1)
    w = int(WIN_L * (1 + 0.015 * seg(f, ARCH, CLX[0]))) // 2 * 2
    img, box = place_window(bg, win_image(src, w), W / 2, 1120)
    return ident(img, f, ARCH + 3, "08", "RESULTADO", box[1] - 70)

def s_spray(f):
    if f < ARCH - 6: return spray_scene(f)
    # barrido motivado por la niebla del spray (izquierda → derecha, dirección del chorro)
    a, b = spray_scene(f), arch_scene(f)
    p = eio(seg(f, ARCH - 6, ARCH + 3)); xw = lerp(-200, W + 200, p)
    img = over(b, a, line_mask_x(xw, 1e5, 180))
    xx = np.arange(W, dtype=np.float32)[None, :]
    return np.clip(img + (np.exp(-((xx - xw) / 110) ** 2) * 0.5)[..., None] * SCAN, 0, 1)

# ================================================================== 367–407 · RESULTADO
def s_arch(f): return arch_scene(f)

# ================================================================== 408–441 · CLÍMAX (ventanas que se sustituyen)
CLX_SRC = [(1440, None), (None, 38.20), (1880, None), (4245, None)]
CLX_POS = [(540, 900, -1), (540, 1020, 1), (540, 930, -1), (540, 1000, 1)]
def s_climax(f):
    i = max(j for j in range(4) if f >= CLX[j])
    fi, ti = CLX_SRC[i]
    src = SRC.frame(fi + (f - CLX[i]) // 2) if fi is not None else S(ti + (f - CLX[i]) / FPS * 0.6)
    img = over(bg_clean('graphite'), bg_atmos(src, f, dark=0.5), 0.5)
    x, y, d = CLX_POS[i]
    p = eo(seg(f, CLX[i] - 1, CLX[i] + 3))
    img, box = place_window(img, win_image(src, WIN), x + d * 70 * (1 - p), y)
    # filete de escáner que barre la ventana entrante
    xl = box[0] + (box[2] if d < 0 else 0) - d * box[2] * p
    if p < 0.98: img = vscan(img, xl, box[1] - 40, box[1] + box[3] + 40, a=0.9)
    return img

# ================================================================== 442–499 · DIBURAMA
THERMAL = np.array([[0.55, 0.10, 0.75], [0.15, 0.25, 0.95], [0.10, 0.80, 0.35], [0.98, 0.92, 0.10], [0.95, 0.15, 0.10]], np.float32)[:, ::-1]
def thermal_col(y_line, width=110):
    yy = np.arange(H, dtype=np.float32)
    u = np.clip((y_line - yy) / width, 0, 1) * (len(THERMAL) - 1)
    i = np.clip(u.astype(int), 0, len(THERMAL) - 2); fr = (u - i)[:, None]
    return (THERMAL[i] * (1 - fr) + THERMAL[i + 1] * fr)[:, None, :]

def s_brand(f, fold=None):
    img = bg_clean('petrol', grid=0.02 * seg(f, BRAND + 8, BRAND + 22), f=f)
    # la última ventana se pliega en una línea: esa línea es el escáner que revela la marca
    if f < BRAND + 6 and fold is not None:      # V4: pliegue conjunto de varias ventanas
        img = fold(img, f)
    elif f < BRAND + 6:
        last = SRC.frame(4245 + (BRAND - 1 - CLX[3]) // 2)
        k = 1 - eo(seg(f, BRAND - 1, BRAND + 4))
        win = win_image(last, WIN)
        h = max(2, int(win.shape[0] * k))
        win = cv2.resize(win, (WIN, h), interpolation=cv2.INTER_AREA)
        img, _ = place_window(img, win, W / 2, 1000, frame=k > 0.3, ticks=0)
    d = T['dib']; xd = (W - d.w) / 2; yd = 640
    ys = lerp(1000, yd + d.caph + 120, eio(seg(f, BRAND + 2, BRAND + 14))) if f < BRAND + 2 else None
    if f < BRAND + 2:
        img = hscan(img, 1000, 40, W - 40, a=1.0)
    else:
        ys = lerp(yd - 30, yd + d.caph + 120, eio(seg(f, BRAND + 2, BRAND + 14)))
        img = d.draw(img, xd, yd, mask=line_mask_y(-1e5, ys - 110, 4))
        if ys < yd + d.caph + 118:
            img = d.draw(img, xd, yd, mask=line_mask_y(ys - 110, ys, 3), color=thermal_col(ys))
            img = hscan(img, ys, 80, W - 80, a=1.0)
    # lente: anillo que rodea la firma (rima visual de todo el Reel)
    img = ring(img, W / 2, 860, 450, a=0.22, prog=eo(seg(f, BRAND + 4, BRAND + 28)), width=1.4)
    rw = 170 * eo(seg(f, BRAND + 10, BRAND + 18)) + 30 * eo(seg(f, LAST - 1, LAST + 7))
    if rw > 1:
        m = line_mask_x(W / 2 - rw / 2, W / 2 + rw / 2, 1.5) * line_mask_y(yd + d.caph + 44, yd + d.caph + 50, 1.2)
        img = over(img, np.broadcast_to(FUCHSIA, img.shape), m)
    sb = T['sub']; p1 = eo(seg(f, 455, 462)); y1 = yd + d.caph + 104
    img = sb.draw(img, (W - sb.w) / 2, y1 + 14 * (1 - p1), color=GREY, opacity=p1)
    mn, md = T['main'], T['maindot']; p2 = eo(seg(f, 460, 468)); y2 = y1 + sb.caph + 40
    if p2 > 0:
        x2 = (W - mn.w - md.w) / 2; clip = line_mask_y(-1e5, y2 + mn.caph + 6, 2)
        img = mn.draw(img, x2, y2 + 40 * (1 - p2), opacity=p2, mask=clip)
        img = md.draw(img, x2 + mn.w + 2, y2 + 40 * (1 - p2), opacity=p2, mask=clip, color=FUCHSIA)
    return img

# ================================================================== router
def render_frame(f):
    setup(); build_text()
    if f < MICRO: return s_mystery(f)[0]
    if f < PART: return s_micro(f)
    if f < PROP: return s_particles(f)
    if f < CMP: return s_property(f)
    if f < TECH: return s_compare(f)
    if f < ROLL: return s_tech(f)
    if f < SPRAY: return s_roller(f)
    if f < ARCH + 4: return s_spray(f)
    if f < CLX[0]: return s_arch(f)
    if f < BRAND: return s_climax(f)
    return s_brand(f)

CLIPS = [  # (inicio, fin, clip/origen, tiempo en el original, uso)
    (0, 41, "03_TERMOGRAFIA", "00:57,40–00:58,71 (0,8x)", "Ventana + lente de exploración"),
    (42, 82, "01_MACRO_AZUL", "00:07,20–00:08,80", "La lente se abre en iris al mundo microscópico"),
    (83, 99, "02_PARTICULAS", "00:36,30–00:36,96", "Tres componentes"),
    (100, 116, "02_PARTICULAS", "00:38,12–00:38,58 (0,7x)", "Transformación luminosa; la esfera sale del marco"),
    (117, 132, "02_PARTICULAS", "00:39,40–00:40,00", "Partícula resultante, pulsos en semicorcheas"),
    (133, 161, "Propiedades (00:17)", "00:17,00–00:18,12", "Edificio: cambio de color «Aislamiento térmico»"),
    (162, 216, "03_TERMOGRAFIA", "00:57,60 / 01:03,60", "Escáner antes / después (registrado)"),
    (217, 299, "04_SISTEMA_MULTICAPA", "01:09,32 → 01:10,40–01:15,30 (1,79x)", "Revelación por línea + círculos + conexión"),
    (300, 320, "05_RODILLO", "02:12,70–02:13,50", "Aplicación con rodillo"),
    (321, 366, "06/07 PROYECCION", "03:11,40–03:13,24", "Proyección; la niebla barre hacia el resultado"),
    (367, 407, "08_FACHADAS", "03:40,60–03:42,20", "Vivienda completa"),
    (408, 416, "03_TERMOGRAFIA", "00:57,60", "Clímax 1"),
    (417, 424, "02_PARTICULAS", "00:38,20", "Clímax 2"),
    (425, 432, "04_SISTEMA_MULTICAPA", "01:15,20", "Clímax 3"),
    (433, 441, "06_PROYECCION", "02:49,80", "Clímax 4"),
    (442, 499, "—", "—", "Cierre DIBURAMA"),
]
