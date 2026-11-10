# DIBURAMA · VISUAL LAB — LO HACEMOS VISIBLE · Thermolime V5
# V5 = V4 con ventanas más grandes, fondos de varias capas derivados del propio material, clímax 16,02–17,68 s
# rediseñado (dos grandes ventanas que intercambian protagonismo) y cierre con el PNG ORIGINAL del logotipo.
# --- texto original de la V4 ---
# Base: sistema gráfico de la V3 (scenes_v3.py). Novedad: lienzo vertical con 2–3 ventanas que se complementan,
# rectángulos animados (desplazamiento, expansión, intercambio, división, mosaico), cartelas y líneas de conexión.
# Regla de nitidez: toda ventana es una REDUCCIÓN del original 1920×1080 (escala ≤ 1). Los detalles se obtienen
# recortando a resolución nativa (ancho de recorte ≥ ancho de ventana), nunca ampliando.
import numpy as np, cv2
from lib import (W, H, FPS, SRC, TextBlock, fit_size, over, circle_mask, line_mask_x, line_mask_y,
                 eo, ei, eio, seg, lerp, pulse, WHITE)
import scenes_v3 as V
from scenes_v3 import GREY, LENS, place_window, ring, seg_line, vscan, hscan, to_win, bg_clean, bg_atmos
from scenes_v3 import dot as _dot3
from lib import hexbgr
import os
FUCHSIA = hexbgr('#E50E77')          # rosa exacto del logotipo oficial (medido en el PNG)
V.FUCHSIA = FUCHSIA                  # también para los puntos de los titulares reutilizados de la V3
def dot(canvas, x, y, r, color=None, a=1.0): return _dot3(canvas, x, y, r, color=FUCHSIA if color is None else color, a=a)

# ------------------------------------------------------------------ cues (fotogramas sobre transitorios medidos)
SEC_IN, PART, BURST, MERGED = 42, 83, 100, 117                 # 1,69 · 3,32 · 4,02 · 4,69 s
CMP, CMP_SCAN, CMP_DONE, CMP_KICK, CMP_OUT = 133, 150, 175, 200, 206
TECH, TECH_RING, TECH_DROP, TECH_TAG = 217, 233, 242, 250       # 8,69 · 9,35 · 9,69 · 10,02 s
APP, SWAP, MIST, RES, RES_SEC = 300, 333, 360, 367, 375         # 12,02 · 13,35 · 14,69 · 15,02 s
CLX0, CLX_PUSH, CLX_B, CLX_C, CLX_D, CLX_CONV, CLX_FOLD = 400, 404, 408, 417, 425, 433, 439   # 16,02 … 17,36 s
BRAND, LAST, END = 442, 483, 500                                # 17,69 · 19,36 · 20,00 s

TY = 232                       # línea de mayúsculas del titular (zona superior 230–400)
MAIN = (40, 418, 1000)         # (x, y, ancho) · alto = ancho·9/16 → 418–980
SEC = (140, 1010, 900)         # 1010–1516, desplazada a la derecha (composición editorial)
KW = 1000 / 1920                # escala de la ventana principal respecto al original

# ------------------------------------------------------------------ fuentes
A_IDX, B_IDX = 1393, 1440            # 55,72 pared sin lente · 57,60 termografía (antes)
RN_IDX, AF_IDX = 1635, 1590          # 65,40 pared renovada sin lente · 63,60 termografía (después)
PLAIN_IDX = 1733                     # 69,32 sistema multicapa sin abrir
FIELD, MULTI_FULL, ROLL_REF, HOUSE = 812, 2000, 3300, 5515
_c = {}

def _reg(dst, src, mask):
    """matriz que lleva coordenadas de src -> dst (registro por características, RANSAC)"""
    orb = cv2.ORB_create(6000)
    ka, da = orb.detectAndCompute(cv2.cvtColor(dst, cv2.COLOR_BGR2GRAY), mask)
    kb, db = orb.detectAndCompute(cv2.cvtColor(src, cv2.COLOR_BGR2GRAY), mask)
    m = cv2.BFMatcher(cv2.NORM_HAMMING, crossCheck=True).match(db, da)
    pb = np.float32([kb[x.queryIdx].pt for x in m]); pa = np.float32([ka[x.trainIdx].pt for x in m])
    return cv2.estimateAffinePartial2D(pb, pa, ransacReprojThreshold=2.5)[0]

def setup():
    if _c: return
    V.setup(); V.build_text()
    mk = np.full((1080, 1920), 255, np.uint8); cv2.circle(mk, (883, 495), 420, 0, -1); cv2.rectangle(mk, (1080, 120), (1720, 320), 0, -1)
    A, B, R, C = SRC.frame(A_IDX), SRC.frame(B_IDX), SRC.frame(RN_IDX), SRC.frame(AF_IDX)
    # pared «normal» registrada sobre cada termografía (el escáner revela exactamente la misma pared)
    _c['plainB'] = cv2.warpAffine(A, _reg(A, B, mk), (1920, 1080), flags=cv2.INTER_CUBIC | cv2.WARP_INVERSE_MAP)
    _c['plainC'] = cv2.warpAffine(R, _reg(R, C, mk), (1920, 1080), flags=cv2.INTER_CUBIC | cv2.WARP_INVERSE_MAP)
    for i0, n in [(1435, 40), (165, 50), (907, 20), (953, 16), (985, 22), (1734, 4), (1760, 140), (1975, 4),
                  (3317, 70), (4785, 70), (5515, 45), (3385, 35), (958, 15), (1800, 3)]:
        SRC.load(i0, n)

def S(t): return SRC.at(t)

# ------------------------------------------------------------------ ventanas
def hw(w): return int(round(w * 9 / 16))

def wimg(src, w, crop=None, gain=1.0):
    """imagen de ventana: plano completo reducido (área) o recorte nativo (cx, cy, ancho_recorte ≥ w)"""
    w = int(w) // 2 * 2; h = hw(w)
    if crop is None:
        out = cv2.resize(src, (w, h), interpolation=cv2.INTER_AREA).astype(np.float32) / 255
    else:
        cx, cy, cw = crop; cw = max(cw, w); ch = cw * 9 / 16
        cx = min(max(cx, cw / 2), 1920 - cw / 2); cy = min(max(cy, ch / 2), 1080 - ch / 2)
        s = w / cw
        pre = cv2.GaussianBlur(src, (0, 0), 0.5 * (1 / s - 1)) if s < 0.85 else src   # antialias, sin enfoque artificial
        M = np.float32([[s, 0, w / 2 - s * cx], [0, s, h / 2 - s * cy]])
        out = cv2.warpAffine(pre, M, (w, h), flags=cv2.INTER_CUBIC, borderMode=cv2.BORDER_REFLECT).astype(np.float32) / 255
    return out * gain if gain != 1.0 else out

def put_win(canvas, win, x0, y0, alpha=1.0, ticks=0.0, clip=None, frame=True):
    h, w = win.shape[:2]
    return place_window(canvas, win, x0 + w / 2, y0 + h / 2, alpha=alpha, frame=frame, ticks=ticks, clip=clip)

def lerp_rect(a, b, k): return tuple(lerp(p, q, k) for p, q in zip(a, b))

def _xm(win, u):  # 1 a la derecha de la fracción u del ancho
    h, w = win.shape[:2]; xx = np.arange(w, dtype=np.float32)[None, :]
    return np.repeat(np.clip((xx - u * w) / 2 + 0.5, 0, 1), h, 0)

_EDGE = {}
def contours(key):
    """contornos del propio plano (silueta técnica), calculados una vez por fotograma de referencia"""
    if key not in _EDGE:
        g = cv2.cvtColor(cv2.resize(SRC.frame(key), (480, 270), interpolation=cv2.INTER_AREA), cv2.COLOR_BGR2GRAY)
        e = cv2.Canny(cv2.GaussianBlur(g, (0, 0), 1.2), 40, 110)
        # solo siluetas grandes: se descartan letras y cartelas del original (< 60 px, o < 25 px de alto/ancho)
        cs, _ = cv2.findContours(e, cv2.RETR_LIST, cv2.CHAIN_APPROX_NONE)
        keep = np.zeros_like(e)
        for c in cs:
            x, y, w, h = cv2.boundingRect(c)
            if max(w, h) >= 60 and min(w, h) >= 25: cv2.drawContours(keep, [c], -1, 255, 1, cv2.LINE_AA)
        _EDGE[key] = cv2.GaussianBlur(keep.astype(np.float32) / 255, (0, 0), 0.9)
    return _EDGE[key]

def bg(f, src, kind='graphite', amt=0.5, dark=0.34, grid=0.0, accent=None, acc_amt=0.22, lines=None):
    """fondo en capas: diseño limpio + atmósfera del plano + reflejo cromático de otra imagen del proyecto
    (paralaje opuesto) + contornos técnicos difusos del propio material. Movimiento lento e independiente."""
    img = over(bg_clean(kind, grid=grid, f=f), bg_atmos(src, f, dark=dark + 0.06, sat=0.72, zoom=1.15), min(1.0, amt + 0.1))
    if accent is not None:
        acc = bg_atmos(SRC.frame(accent), f + 90, dark=0.6, sat=1.15, zoom=1.7, drift=(-25 * np.sin(f / 70), 18 * np.cos(f / 90)))
        img = 1 - (1 - img) * (1 - acc_amt * acc)
    if lines is not None:
        s = H / 270 * 0.95; cx = 240 + 14 * np.sin(f / 80); cy = 135 + 7 * np.cos(f / 95)
        M = np.float32([[s, 0, W / 2 - s * cx], [0, s, H / 2 - s * cy]])
        em = cv2.warpAffine(contours(lines), M, (W, H), flags=cv2.INTER_LINEAR)
        img = np.clip(img + em[..., None] * 0.055, 0, 1)
    return img

# ------------------------------------------------------------------ cartelas
_TX = {}
def _tb(txt, name, size, tr=0.0):
    k = (txt, name, size, tr)
    if k not in _TX: _TX[k] = TextBlock(txt, name, size, tracking=tr)
    return _TX[k]

def tag(canvas, f, f0, num, label, x, y, a_out=1.0, line_to=None):
    """identificador «01 / LO INVISIBLE»: número fucsia, barra gris, etiqueta blanca; opcionalmente una línea que lo conecta"""
    p = eo(seg(f, f0, f0 + 8)) * a_out
    if p <= 0: return canvas
    n, sl, lb = _tb(num, 'bold', 24, 0.1), _tb("/", 'semi', 24), _tb(label, 'semi', 24, 0.2)
    dx = 12 * (1 - p)
    canvas = n.draw(canvas, x + dx, y, color=FUCHSIA, opacity=p)
    canvas = sl.draw(canvas, x + n.w + 12 + dx, y, color=GREY, opacity=p)
    canvas = lb.draw(canvas, x + n.w + sl.w + 24 + dx, y, color=WHITE, opacity=p)
    if line_to is not None:
        xe = x + n.w + sl.w + lb.w + 40
        canvas = seg_line(canvas, (xe, y + 9), (line_to, y + 9), a=0.5 * p, w=1.5, prog=eo(seg(f, f0 + 2, f0 + 12)))
    return canvas

def label(canvas, f, f0, text, x, y, a_out=1.0, color=GREY):
    p = eo(seg(f, f0, f0 + 7)) * a_out
    if p <= 0: return canvas
    t = _tb(text, 'semi', 22, 0.22)
    canvas = dot(canvas, x + 5, y + 8, 4, a=p)
    return t.draw(canvas, x + 20 + 10 * (1 - p), y, color=color, opacity=p)

# ------------------------------------------------------------------ titulares
T = {}
def build_text():
    if T: return
    s = min(fit_size("¿CÓMO MUESTRAS", 'black', 900, 100), fit_size("LO QUE NO SE VE?", 'black', 900, 100)); T['s1'] = s
    T['q1'], T['q2'] = TextBlock("¿CÓMO MUESTRAS", 'black', s), TextBlock("LO QUE NO SE VE?", 'black', s)
    s = min(fit_size("LA TECNOLOGÍA,", 'black', 900, 100), fit_size("AL DESCUBIERTO.", 'black', 900, 100)); T['s2'] = s
    T['t1'], T['t2'], T['dot'] = TextBlock("LA TECNOLOGÍA,", 'black', s), TextBlock("AL DESCUBIERTO", 'black', s), TextBlock(".", 'black', s)

# ================================================================== 0–82 · LO QUE NO SE VE (termografía + microestructura)
def thermo_src(f): return S(57.40 + min(f, 82) / FPS * 0.36)      # el original funde la lente desde 00:58,62
def main_rect_s1(f): return (40 - 8 * seg(f, 0, PART), lerp(500, 418, eo(seg(f, SEC_IN - 1, SEC_IN + 8))), 1000 * (1 + 0.04 * (1 - eo(seg(f, -1, 6)))))
def sec_rect_s1(f): return (140 + 10 * seg(f, SEC_IN, PART), 1010, 900)

def s_open(f):
    src = thermo_src(f)
    img = bg(f, src, 'graphite', amt=0.6, accent=FIELD, lines=B_IDX)
    x, y, w = main_rect_s1(f)
    img, box = put_win(img, wimg(src, w), x, y, ticks=1.0)
    lx, ly = to_win(box, LENS[0], LENS[1]); lr = LENS[2] * box[2] / 1920
    pr = eo(seg(f, 2, 16))                                  # lente de exploración
    img = ring(img, lx, ly, lr + 12, a=0.85, prog=pr)
    img = dot(img, lx + (lr + 12) * np.cos(-np.pi / 2 + pr * 2 * np.pi), ly + (lr + 12) * np.sin(-np.pi / 2 + pr * 2 * np.pi), 5, a=eo(seg(f, 2, 5)))
    if 14 <= f <= 36:
        ys = lerp(ly - lr, ly + lr, eio(seg(f, 14, 34))); dx = np.sqrt(max(0, lr ** 2 - (ys - ly) ** 2))
        img = hscan(img, ys, lx - dx, lx + dx, a=0.8 * (1 - seg(f, 32, 36)))
    if f >= SEC_IN - 1:                                     # segunda ventana: microestructura, revelada por el escáner
        sx, sy, sw = sec_rect_s1(f)
        bsrc = S(7.20 + max(0, f - SEC_IN) / FPS)
        u = eio(seg(f, SEC_IN - 1, SEC_IN + 7)); xr = sx + sw * u
        img, sb = put_win(img, wimg(bsrc, sw), sx, sy, clip=line_mask_x(-1e5, xr, 3))
        if u < 1: img = vscan(img, xr, sy - 30, sy + hw(sw) + 30)
        # círculo que conecta la lente térmica con la estructura microscópica
        rx, ry = to_win(sb, 1180, 560)
        pl = eo(seg(f, SEC_IN + 4, SEC_IN + 14))
        p0, p1 = (lx, ly + lr + 12), (rx, ry - 52)
        img = seg_line(img, p0, p1, a=0.75, w=1.6, prog=pl)
        if pl > 0: img = dot(img, *p0, 5)
        img = ring(img, rx, ry, 52, a=0.85, prog=eo(seg(f, SEC_IN + 10, SEC_IN + 20)), width=1.8)
    img = V.title_lines(img, f, [(T['q1'], -1, 0, None), (T['q2'], SEC_IN, T['s1'] * 0.98, None)], TY, f_out=78)
    img = tag(img, f, 8, "01", "LO INVISIBLE", 80, box[1] + box[3] + 7, a_out=1 - seg(f, 76, 82), line_to=box[0] + box[2])
    return img, box

# ================================================================== 83–132 · DENTRO DEL MATERIAL
def part_src(f):
    if f < BURST: return S(36.30 + (f - PART) / FPS)
    if f < MERGED: return S(38.12 + (f - BURST) / FPS * 0.7)
    return S(39.40 + (f - MERGED) / FPS)

def s_material(f):
    src = part_src(f)
    glow = 0.30 + (0.14 * (1 - seg(f, BURST, MERGED)) if BURST <= f < MERGED else 0)
    img = bg(f, src, 'graphite', amt=0.55, dark=glow, accent=B_IDX, acc_amt=0.18, lines=985)
    # ventana secundaria (detrás): textura azul, más pequeña, sin competir
    k = eo(seg(f, PART - 1, PART + 9)); sw = int(lerp(900, 720, k)) // 2 * 2
    sx, sy = 1040 - sw + 12 * seg(f, PART, CMP), lerp(1010, 1040, k)
    img, sb = put_win(img, wimg(S(6.60 + (f - PART) / FPS * 0.6), sw, crop=(1250, 600, 1300), gain=0.85), sx, sy)
    # ventana principal: el círculo de la lente se abre a la partícula (match cut circular)
    x, y = 40 - 8 - 6 * seg(f, PART, CMP), 418
    win = wimg(src, 1000)
    if f < PART + 8:
        old = wimg(thermo_src(PART - 1), 1000)
        kk = 1 - (1 - seg(f, PART - 1, PART + 7)) ** 2.4
        cx, cy, r0 = LENS[0] * KW, LENS[1] * KW, LENS[2] * KW
        yy, xx = np.mgrid[:win.shape[0], :win.shape[1]].astype(np.float32)
        m = np.clip(lerp(r0 + 6, 1150, kk) - np.sqrt((xx - cx) ** 2 + (yy - cy) ** 2) + 0.5, 0, 1)[..., None]
        win = old * (1 - m) + win * m
    img, box = put_win(img, win, x, y, ticks=1.0)
    if f >= BURST:   # la esfera atraviesa los límites de la ventana
        if f < MERGED: pc, pr, sc_ = (1000.0, 530.0), 330.0, lerp(1.0, 1.75, eo(seg(f, BURST - 1, BURST + 7)))
        else: pc, pr, sc_ = (760.0, 525.0), 345.0, 1.55 * (1 + 0.06 * (1 - eo(seg(f, MERGED - 1, MERGED + 5)))) + sum(pulse(f, q, 0.04, 2.5) for q in (121, 125, 129))
        px, py = to_win(box, *pc); s_abs = box[2] / 1920 * sc_            # < 1: sigue siendo reducción
        M = np.float32([[s_abs, 0, px - s_abs * pc[0]], [0, s_abs, py - s_abs * pc[1]]])
        lay = cv2.warpAffine(src, M, (W, H), flags=cv2.INTER_AREA).astype(np.float32) / 255
        mm = circle_mask(px, py, pr * s_abs, 1.5)
        img = img * (1 - V.drop_shadow(mm, 0, 24, 30, 0.55)[..., None]); img = over(img, lay, mm)
        img = ring(img, px, py, pr * s_abs + 8, a=0.6, width=1.4)
    img = tag(img, f, PART + 4, "02", "EL MATERIAL", 80, sb[1] + sb[3] + 22, a_out=1 - seg(f, CMP - 5, CMP))
    return img

# ================================================================== 133–216 · DESCUBRIR LO INVISIBLE (antes / después real)
UP, LO = (40, 330, 1000), (40, 940, 1000)
def s_compare(f):
    img = bg(f, SRC.frame(B_IDX), 'graphite', amt=0.4, grid=0.018, accent=FIELD, acc_amt=0.16, lines=AF_IDX)
    ein = eo(seg(f, CMP - 1, CMP + 6)); out = ei(seg(f, CMP_OUT, TECH))
    ux = UP[0] - 140 * (1 - ein); lx_ = LO[0] + 140 * (1 - ein)
    uy, ly_ = UP[1] - 760 * out, LO[1] + 760 * out                       # división: las ventanas se separan
    u = eio(seg(f, CMP_SCAN - 1, CMP_DONE)) if f >= CMP_SCAN - 1 else 0.0
    wins = []
    for (plain, th) in [(_c['plainB'], SRC.frame(B_IDX)), (_c['plainC'], SRC.frame(AF_IDX))]:
        a, b = wimg(plain, 1000), wimg(th, 1000)
        wins.append(over(a, b, 1 - _xm(a, u)) if u > 0 else a)           # a la izquierda del escáner: termografía
    img, bu = put_win(img, wins[0], ux, uy, alpha=ein, ticks=1.0)
    img, bl = put_win(img, wins[1], lx_, ly_, alpha=ein)
    # escáner único que recorre y conecta ambas ventanas
    if CMP_SCAN - 1 <= f <= CMP_DONE + 1:
        xs = UP[0] + 1000 * u
        img = vscan(img, xs, uy - 24, ly_ + 562 + 24); img = dot(img, xs, uy - 24, 5); img = dot(img, xs, ly_ + 586, 5)
    # lentes conectadas: misma posición, diferente lectura
    pr = eo(seg(f, CMP_DONE + 2, CMP_DONE + 12)) * (1 - out)
    if pr > 0:
        (ax, ay), (cx, cy) = to_win(bu, LENS[0], LENS[1]), to_win(bl, LENS[0], LENS[1]); rr = LENS[2] * KW + 14
        rk = rr * (1 + 0.08 * pulse(f, CMP_KICK, 1.0, 3))
        img = ring(img, ax, ay, rk, a=0.85, prog=pr, width=1.8); img = ring(img, cx, cy, rk, a=0.85, prog=pr, width=1.8, start=np.pi / 2)
        pl = eo(seg(f, CMP_DONE + 8, CMP_DONE + 18)) * (1 - out)
        img = seg_line(img, (ax, ay + rk), (cx, cy - rk), a=0.8, w=1.8, prog=pl)
        if pl > 0: img = dot(img, ax, ay + rk, 5); img = dot(img, cx, cy - rk, 5, a=seg(f, CMP_DONE + 17, CMP_DONE + 19))
    a_l = 1 - seg(f, CMP_OUT, CMP_OUT + 3)
    img = label(img, f, CMP + 4, "ANTES", 80, uy - 38, a_out=a_l)
    img = label(img, f, CMP + 8, "DESPUÉS", 80, ly_ - 35, a_out=a_l, color=WHITE)
    if f >= CMP_OUT:                                                      # la línea central anuncia el golpe
        g = eio(seg(f, CMP_OUT, TECH)); img = hscan(img, 916, W / 2 - 520 * g, W / 2 + 520 * g, a=g)
    return img

# ================================================================== 217–299 · LA GRAN REVELACIÓN (sistema multicapa)
def tech_src(f): return S(min(70.40 + max(0, f - TECH - 8) / FPS * 1.79, 80.5))
DET_C = (440.0, 745.0)
def det_cw(f): return lerp(1010, 920, eio(seg(f, TECH_DROP, APP)))      # recorte ≥ 900 px: detalle nativo
def s_tech(f):
    src = tech_src(f)
    img = bg(f, src, 'petrol', amt=0.25, grid=0.03, accent=B_IDX, acc_amt=0.14, lines=MULTI_FULL)
    w = int(1000 * (1 + 0.05 * (1 - eo(seg(f, TECH - 1, TECH + 6))))) // 2 * 2
    x, y = 540 - w / 2, 418 + (562 - hw(w)) / 2 - 8 * seg(f, TECH, APP)
    if f < TECH + 8:   # en el golpe: la línea revela el sistema abierto sobre el enfoscado
        uu = lerp(1.04, -0.04, eio(seg(f, TECH - 1, TECH + 7)))
        wp, wo = wimg(SRC.frame(PLAIN_IDX), w), wimg(S(70.40), w)
        img, box = put_win(img, over(wp, wo, _xm(wp, uu)), x, y, ticks=1.0)
        img = vscan(img, box[0] + uu * box[2], box[1] - 80, box[1] + box[3] + 80)
    else:
        img, box = put_win(img, wimg(src, w), x, y, ticks=1.0)
    # 2) círculo sobre el componente y línea que desciende al ritmo
    ax, ay = to_win(box, 323, 745); ra = 330 * box[2] / 1920
    img = ring(img, ax, ay, ra, a=0.85, prog=eo(seg(f, TECH_RING - 1, TECH_RING + 9)), width=1.8)
    yb = SEC[1]
    pd = eio(seg(f, TECH_RING + 3, TECH_DROP))
    if pd > 0:
        img = seg_line(img, (ax, ay + ra), (ax, lerp(ay + ra, yb + 60, pd)), a=0.85, w=1.8)
        img = dot(img, ax, ay + ra, 5)
    # 3) se revela la ventana inferior: detalle nativo de las capas (sin ampliar)
    if f >= TECH_DROP - 1:
        cw = det_cw(f); dsrc = SRC.frame(1800)
        yr = lerp(yb, yb + hw(900) + 2, eio(seg(f, TECH_DROP - 1, TECH_DROP + 7)))
        img, lb = put_win(img, wimg(dsrc, 900, crop=(DET_C[0], DET_C[1], cw)), SEC[0] + 10 * seg(f, TECH_DROP, APP), yb,
                          clip=line_mask_y(-1e5, yr, 3))
        if yr < yb + hw(900): img = hscan(img, yr, SEC[0] - 20, SEC[0] + 920)
        # el mismo componente, señalado en el detalle
        s_ = 900 / cw; cxs = min(max(DET_C[0], cw / 2), 1920 - cw / 2); cys = min(max(DET_C[1], cw * 9 / 32), 1080 - cw * 9 / 32)
        dx, dy = lb[0] + 450 + (323 - cxs) * s_, lb[1] + hw(900) / 2 + (745 - cys) * s_
        rd = 165 * s_
        img = ring(img, dx, dy, rd, a=0.85, prog=eo(seg(f, TECH_DROP + 6, TECH_DROP + 16)), width=1.8, start=np.pi / 2)
        img = dot(img, ax, yb + 60, 5 * (1 + 0.5 * pulse(f, TECH_TAG, 1.0, 2)), a=seg(f, TECH_DROP, TECH_DROP + 2))
    # 4) cartela técnica en la junta entre ventanas
    img = tag(img, f, TECH_TAG, "03", "LA TECNOLOGÍA", ax + 28, 986, a_out=1 - seg(f, APP - 5, APP), line_to=1040)
    s = T['s2']
    img = V.title_lines(img, f, [(T['t1'], TECH, 0, None), (T['t2'], TECH + 4, s * 0.98, (T['dot'],))], TY, f_out=APP - 5)
    return img

# ================================================================== 300–366 · DE LA TECNOLOGÍA A LA APLICACIÓN
R0, S0 = (40, 418, 1000), (240, 1024, 800)         # rodillo grande · spray menor
R1, S1 = (40, 420, 800), (40, 912, 1000)           # tras el golpe: el spray gana protagonismo
def app_layout(f):
    k = eio(seg(f, SWAP - 1, SWAP + 8))
    return lerp_rect(R0, R1, k), lerp_rect(S0, S1, k)

def s_app(f):
    # rodillo: macro hasta el intercambio; después, plano general del operario (contexto real)
    rsrc = S(131.00 + (f - APP) / FPS) if f < SWAP else S(134.20 + (f - SWAP) / FPS * 0.7)
    ssrc = S(191.40 + (f - APP) / FPS)
    img = bg(f, ssrc if f >= SWAP else rsrc, 'graphite', amt=0.45, grid=0.015, accent=ROLL_REF, acc_amt=0.16, lines=4785)
    (rx, ry, rw), (sx, sy, sw) = app_layout(f)
    ein = eo(seg(f, APP + 3, APP + 10))
    rx += -6 * seg(f, APP, MIST); sx += 70 * (1 - ein) + 6 * seg(f, APP, MIST)
    big_spray = f >= SWAP + 4
    order = [('s', sx, sy, sw), ('r', rx, ry, rw)] if not big_spray else [('r', rx, ry, rw), ('s', sx, sy, sw)]
    boxes = {}
    for nm, x, y, w in order:
        src = rsrc if nm == 'r' else ssrc
        img, boxes[nm] = put_win(img, wimg(src, w), x, y, alpha=(1.0 if nm == 'r' else ein), ticks=(1.0 if (nm == 'r') != big_spray else 0.0))
    br, bs = boxes['r'], boxes['s']
    img = label(img, f, APP + 2, "APLICACIÓN REAL", br[0], br[1] - 34, a_out=1 - seg(f, MIST - 2, MIST + 2))
    img = label(img, f, APP + 8, "DETALLE DEL PROCESO", bs[0], bs[1] - 34, a_out=1 - seg(f, MIST - 2, MIST + 2), color=WHITE)
    img = tag(img, f, APP + 2, "04", "LA APLICACIÓN", 80, 300, a_out=1 - seg(f, MIST - 2, MIST + 2))
    return img

def s_app_to_res(f):   # la niebla del spray barre la composición hacia el resultado
    a, b = s_app(f), s_result(f)
    p = eio(seg(f, MIST, RES)); xw = lerp(-220, W + 220, p)
    img = over(b, a, line_mask_x(xw, 1e5, 200))
    xx = np.arange(W, dtype=np.float32)[None, :]
    return np.clip(img + (np.exp(-((xx - xw) / 120) ** 2) * 0.45)[..., None] * V.SCAN, 0, 1)

# ================================================================== 367–399 · EL RESULTADO
def s_result(f):
    hsrc = SRC.frame(5515 + max(0, f - RES))
    img = bg(f, hsrc, 'graphite', amt=0.5, accent=FIELD, acc_amt=0.14, lines=HOUSE)
    img, box = put_win(img, wimg(hsrc, 1000), 40, 418 - 10 * seg(f, RES, CLX0), ticks=1.0)
    if f >= RES_SEC - 1:   # detalle del acabado (llana) entra desde la izquierda
        k = eo(seg(f, RES_SEC - 1, RES_SEC + 9))
        img, sb = put_win(img, wimg(S(135.40 + (f - RES_SEC) / FPS), 900), 40 - 90 * (1 - k) + 10 * seg(f, RES_SEC, CLX0), 1010, alpha=k)
        pl = eo(seg(f, RES_SEC + 4, RES_SEC + 14))
        img = seg_line(img, (sb[0] + sb[2] + 24, sb[1] + 40), (1040, sb[1] + 40), a=0.5, w=1.5, prog=pl)
        img = seg_line(img, (1040, sb[1] + 40), (1040, box[1] + box[3] + 12), a=0.5, w=1.5, prog=eo(seg(f, RES_SEC + 10, RES_SEC + 18)))
        if pl > 0: img = dot(img, 1040, box[1] + box[3] + 12, 4, a=seg(f, RES_SEC + 17, RES_SEC + 19))
    img = tag(img, f, RES + 2, "05", "EL RESULTADO", 80, 300, a_out=1 - seg(f, CLX0 - 4, CLX0))
    return img

# ================================================================== 400–441 · CLÍMAX — EXPANSIÓN CINEMATOGRÁFICA
# Dos grandes ventanas (≥ 880 px) que entran, cambian de contenido con máscaras e intercambian protagonismo en cada golpe;
# después convergen hacia la línea donde nacerá el logotipo.
LCY = 820                                    # centro vertical del logotipo en el cierre
def c_thermo(f): return SRC.frame(B_IDX)
def c_part(f): return S(38.30 + max(0, f - CLX_B) / FPS * 0.5)
def c_multi(f): return SRC.frame(MULTI_FULL)
def c_roll(f): return S(131.40 + max(0, f - CLX_D) / FPS)

A_KEYS = [(CLX0, (40, 680, 1000)), (CLX_PUSH, (20, 669, 1040)), (CLX_B, (40, 330, 1000)), (CLX_C, (20, 318, 1040)),
          (CLX_D, (80, 330, 920)), (CLX_CONV, (100, LCY - 4 - hw(880), 880))]
B_KEYS = [(CLX0, (40, 1930, 1000)), (CLX_B, (40, 930, 1000)), (CLX_C, (80, 945, 920)),
          (CLX_D, (20, 905, 1040)), (CLX_CONV, (100, LCY + 4, 880))]
def key_rect(keys, f):
    r = keys[0][1]
    for i, (c, rr) in enumerate(keys[1:], 1):
        if f >= c - 1: r = lerp_rect(keys[i - 1][1], rr, eo(seg(f, c - 1, c + 3)))
    return r

def climax_bg(f):
    big = c_multi(f) if f >= CLX_C else c_thermo(f)
    hit = sum(pulse(f, c, 1.0, 4.0) for c in (CLX0, CLX_PUSH, CLX_B, CLX_C, CLX_D, CLX_CONV))
    return bg(f, big, 'graphite', amt=0.5, accent=(FIELD if f >= CLX_B else B_IDX), acc_amt=0.20 + 0.30 * min(hit, 1.0), lines=MULTI_FULL)

def fold_k(f): return 1 - eio(seg(f, CLX_FOLD, BRAND + 2))

def s_climax(f):
    img = climax_bg(f)
    ra, rb = key_rect(A_KEYS, f), key_rect(B_KEYS, f)
    k = fold_k(f)
    out = {}
    for name, (x, y, w) in (('B', rb), ('A', ra)):
        w = int(w) // 2 * 2; h0 = hw(w)
        if name == 'A':   # termografía → sistema multicapa (máscara de izquierda a derecha en 16,69 s)
            a, b = wimg(c_thermo(f), w), wimg(c_multi(f), w); u = eio(seg(f, CLX_C - 1, CLX_C + 4))
            win = over(a, b, 1 - _xm(a, u)) if u > 0 else a
        else:             # partícula → aplicación real (máscara de derecha a izquierda en 17,02 s)
            a, b = wimg(c_part(f), w), wimg(c_roll(f), w); u = eio(seg(f, CLX_D - 1, CLX_D + 4))
            win = over(a, b, _xm(a, 1 - u)) if u > 0 else a
        if k < 1:         # pliegue hacia la línea central (A hacia abajo, B hacia arriba)
            h = max(2, int(h0 * k)); win = cv2.resize(win, (w, h), interpolation=cv2.INTER_AREA)
            y = (y + h0 - h) if name == 'A' else y
        img, box = put_win(img, win, x, y, ticks=(1.0 if w >= 1000 and k > 0.9 else 0.0), frame=k > 0.25)
        out[name] = box
        # escáner que acompaña cada máscara
        uu = eio(seg(f, (CLX_C if name == 'A' else CLX_D) - 1, (CLX_C if name == 'A' else CLX_D) + 4))
        if 0 < uu < 1:
            xs = box[0] + box[2] * (uu if name == 'A' else 1 - uu)
            img = vscan(img, xs, box[1] - 26, box[1] + box[3] + 26)
    # convergencia: una línea fucsia une las dos ventanas y se convierte en el eje del logotipo
    pl = eio(seg(f, CLX_CONV + 1, CLX_FOLD + 1))
    if pl > 0:
        half = 440 * pl
        img = over(img, np.broadcast_to(FUCHSIA, img.shape), line_mask_x(W / 2 - half, W / 2 + half, 1.5) * line_mask_y(LCY - 1.5, LCY + 1.5, 1.0))
        img = dot(img, W / 2 - half, LCY, 4.5); img = dot(img, W / 2 + half, LCY, 4.5)
    return img

# ================================================================== 442–499 · CIERRE — LOGOTIPO ORIGINAL
LOGO_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'assets', 'DIBURAMA_logo_original_transparente_recortado.png')
LOGO_W = 880                                  # 880 px (escala 0,826 del PNG original de 1065 px: reducción, nunca ampliación)
_L = {}
def logo_rgba():
    if 'rgba' not in _L:
        im = cv2.imread(LOGO_PATH, cv2.IMREAD_UNCHANGED).astype(np.float32) / 255     # BGRA, sin modificar
        a = im[..., 3:4]; _L['rgba'] = np.concatenate([im[..., :3] * a, a], 2)      # alfa premultiplicado (bordes limpios)
    return _L['rgba']

def put_logo(canvas, scale, cx, cy, mask=None):
    src = logo_rgba(); w = int(round(src.shape[1] * scale)); h = int(round(src.shape[0] * scale))
    lay = cv2.resize(src, (w, h), interpolation=cv2.INTER_AREA)
    x0, y0 = int(round(cx - w / 2)), int(round(cy - h / 2))
    rgb, a = lay[..., :3], lay[..., 3:4]
    if mask is not None:
        m = mask[y0:y0 + h, x0:x0 + w][..., None]; rgb, a = rgb * m, a * m
    sub = canvas[y0:y0 + h, x0:x0 + w]
    canvas[y0:y0 + h, x0:x0 + w] = sub * (1 - a) + rgb
    return canvas, (x0, y0, w, h)

_BG = {}
def brand_bg(f):
    if 'g' not in _BG:
        y = np.linspace(0, 1, H, dtype=np.float32)[:, None, None]
        top, bot = hexbgr('#101A23'), hexbgr('#0D1219')
        g = (top * (1 - y) + bot * y) * np.ones((1, W, 1), np.float32)
        yy, xx = np.mgrid[:H, :W].astype(np.float32)
        vig = 1 - 0.30 * np.clip(((xx - W / 2) / (W * 0.85)) ** 2 + ((yy - LCY) / (H * 0.6)) ** 2, 0, 1.4)
        _BG['g'] = np.clip(g * vig[..., None], 0, 1)
        # reflejo fucsia muy suave, anclado a la llama del logotipo
        fx, fy = W / 2 - LOGO_W / 2 + 208 * LOGO_W / 1065, LCY - 0.5 * 406 * LOGO_W / 1065 + 85 * LOGO_W / 1065
        _BG['glow'] = np.exp(-(((xx - fx) / 300) ** 2 + ((yy - fy) / 260) ** 2))[..., None].astype(np.float32)
        # textura técnica casi imperceptible: contornos del sistema multicapa
        _BG['lines'] = cv2.GaussianBlur(cv2.resize(contours(MULTI_FULL), (W * 2, H), interpolation=cv2.INTER_LINEAR)[:, W // 2:W // 2 + W], (0, 0), 1.2)
    img = _BG['g'].copy()
    # movimiento residual de las escenas anteriores: la luz de la partícula, muy desenfocada, se apaga lentamente
    res = bg_atmos(c_part(BRAND), f, dark=0.55, sat=0.9, zoom=1.8, drift=(10 * np.sin(f / 50), -8 * seg(f, BRAND, END)))
    img = 1 - (1 - img) * (1 - res * lerp(0.30, 0.10, eo(seg(f, BRAND, 470))))
    img = np.clip(img + _BG['lines'][..., None] * 0.03, 0, 1)
    breath = 0.10 + 0.02 * np.sin(f / 9) + 0.05 * pulse(f, LAST, 1.0, 6)
    img = np.clip(img + _BG['glow'] * FUCHSIA * breath, 0, 1)
    return img

ST = {}
def brand_text():
    if ST: return
    s1 = fit_size("LO DIFÍCIL DE EXPLICAR,", 'semi', 700, 50)
    ST['l1'] = TextBlock("LO DIFÍCIL DE EXPLICAR,", 'semi', s1, tracking=0.03)
    s2 = fit_size("LO HACEMOS VISIBLE.", 'black', 880, 88); ST['s2'] = s2
    ST['l2'], ST['dot'] = TextBlock("LO HACEMOS VISIBLE", 'black', s2), TextBlock(".", 'black', s2)

def s_brand(f):
    brand_text()
    img = brand_bg(f)
    sc = LOGO_W / 1065 * (1 + 0.04 * (1 - eo(seg(f, BRAND - 1, BRAND + 9))))      # 104 % → 100 %
    hh = (406 * sc / 2 + 12) * eio(seg(f, BRAND - 1, BRAND + 6))                # la línea se abre y revela el logotipo
    if f < BRAND + 3:   # las ventanas terminan de plegarse en la misma línea
        img = over(img, s_climax(f), 1 - eio(seg(f, BRAND - 1, BRAND + 3)))
    mask = line_mask_y(LCY - hh, LCY + hh, 3)
    img, lb = put_logo(img, sc, W / 2, LCY, mask=mask)
    a_edge = 1 - seg(f, BRAND + 4, BRAND + 9)
    if a_edge > 0:
        for yy_ in (LCY - hh, LCY + hh):
            img = over(img, np.broadcast_to(FUCHSIA, img.shape), line_mask_x(W / 2 - 440, W / 2 + 440, 1.5) * line_mask_y(yy_ - 1.2, yy_ + 1.2, 1.0) * a_edge)
    # eslogan: aparición más suave que la del logotipo
    l1, l2, dt = ST['l1'], ST['l2'], ST['dot']
    y1 = LCY + 406 * LOGO_W / 1065 / 2 + 74; y2 = y1 + l1.caph + 34
    p1 = eo(seg(f, 451, 461)); p2 = eo(seg(f, 455, 466))
    if p1 > 0: img = l1.draw(img, (W - l1.w) / 2, y1 + 14 * (1 - p1), color=np.array([0.86, 0.87, 0.89], np.float32), opacity=p1)
    if p2 > 0:
        x2 = (W - l2.w - dt.w) / 2; clip = line_mask_y(-1e5, y2 + l2.caph + 8, 2)
        img = l2.draw(img, x2, y2 + 22 * (1 - p2), opacity=p2, mask=clip)
        img = dt.draw(img, x2 + l2.w + 2, y2 + 22 * (1 - p2), opacity=p2, mask=clip, color=FUCHSIA)
    return img

# ================================================================== router
def render_frame(f):
    setup(); build_text()
    if f < PART: return s_open(f)[0]
    if f < CMP: return s_material(f)
    if f < TECH: return s_compare(f)
    if f < APP: return s_tech(f)
    if f < MIST: return s_app(f)
    if f < RES: return s_app_to_res(f)
    if f < CLX0: return s_result(f)
    if f < BRAND: return s_climax(f)
    return s_brand(f)

CLIPS = [  # (inicio, fin, ventana, origen, tiempo en el original, uso)
    (0, 82, "Principal", "03_TERMOGRAFIA", "00:57,40–00:58,58 (0,36x)", "Lente de exploración"),
    (42, 82, "Secundaria", "01_MACRO_AZUL", "00:07,20–00:08,80", "Microestructura revelada por escáner"),
    (83, 132, "Principal", "02_PARTICULAS", "00:36,30 · 00:38,12 · 00:39,40", "Iris desde la lente; esfera fuera del marco"),
    (83, 132, "Secundaria", "01_MACRO_AZUL", "00:06,60–00:07,78 (detalle nativo)", "Textura complementaria"),
    (133, 216, "Superior", "03_TERMOGRAFIA", "00:55,72 → 00:57,60", "ANTES"),
    (133, 216, "Inferior", "03_TERMOGRAFIA", "01:05,40 → 01:03,60", "DESPUÉS"),
    (217, 299, "Superior", "04_SISTEMA_MULTICAPA", "01:09,32 → 01:10,40–01:15,70", "Sistema completo"),
    (242, 299, "Inferior", "04_SISTEMA_MULTICAPA", "01:12,00 (recorte nativo)", "Detalle del componente"),
    (300, 366, "Rodillo", "05_RODILLO", "02:11,00 · 02:14,20", "Macro → plano general"),
    (300, 366, "Spray", "06_PROYECCION", "03:11,40–03:14,04", "Pasa a protagonista"),
    (367, 399, "Principal", "08_FACHADAS", "03:40,60–03:41,88", "Vivienda completa"),
    (375, 399, "Secundaria", "07_SPRAY_DETALLE (llana)", "02:15,40–02:16,36", "Detalle del acabado"),
    (400, 416, "Superior", "03_TERMOGRAFIA", "00:57,60", "Clímax: ventana grande con empujón en 16,19"),
    (408, 424, "Inferior", "02_PARTICULAS", "00:38,30–00:38,64", "Entra en 16,36"),
    (417, 441, "Superior", "04_SISTEMA_MULTICAPA", "01:20,00", "Máscara en 16,69"),
    (425, 441, "Inferior", "05_RODILLO", "02:11,40–02:12,04", "Máscara en 17,02; convergencia en 17,36"),
    (442, 499, "—", "Logotipo oficial (PNG original)", "—", "Revelación desde la línea fucsia + eslogan"),
]
