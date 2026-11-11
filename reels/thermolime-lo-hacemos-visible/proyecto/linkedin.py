# DIBURAMA · VISUAL LAB — «LO HACEMOS VISIBLE» · versión horizontal LinkedIn (1920 × 1080 · 25 fps · 24 s · 600 fotogramas)
# Montaje propio para 16:9 (no derivado del vertical). Los planos a pantalla completa se muestran a resolución NATIVA
# (1:1, sin reescalar); las ventanas son reducciones del original. Fondos: grafito/petróleo e imagen original muy
# desenfocada, sin líneas, siluetas ni retículas. Márgenes de seguridad: 120 px laterales, 90 px arriba/abajo.
# Cortes sobre la edición musical de audio_linkedin.py (90 BPM; marca en 20,36 s; tónica en 21,36 s).
import lib
lib.W, lib.H = 1920, 1080                       # lienzo horizontal (antes de importar los módulos que leen W, H)
import numpy as np, cv2
from lib import SRC, FPS, TextBlock, fit_size, over, circle_mask, line_mask_x, line_mask_y, eo, ei, eio, seg, lerp, pulse, cam_M, warp, hexbgr, WHITE
import scenes_v3 as V
import scenes_v4 as V4
import scenes_v5 as V5
from scenes_v5 import wimg, hw, lerp_rect, _xm, _c

W, H = 1920, 1080
CANVAS = (W, H)
ML, MR, MT, MB = 120, 1800, 90, 990               # zona segura
FUCHSIA = hexbgr('#E50E77'); V.FUCHSIA = FUCHSIA
GREY = np.array([0.74, 0.75, 0.78], np.float32)
LENS = (883.0, 493.0, 405.0)
B_IDX, AF_IDX, PLAIN_IDX, MULTI_FULL, HOUSE, FIELD = 1440, 1590, 1733, 2000, 5515, 812

# ------------------------------------------------------------------ cues (fotogramas sobre la edición musical)
TITLE2, IMMERSE, IRIS, BURST, MERGED = 42, 67, 83, 100, 117
EXPL, SCAN_A, SEC_IN, SCAN_B, LINK, KICK, OUT = 133, 149, 163, 175, 188, 200, 206
TECH, EDIT_T, T2, DET = 217, 233, 242, 250
APP, SPLIT, SWAP, MIST = 300, 333, 367, 384
RES, RES_L, RES_D = 400, 417, 425
CL1, CL2, CL3, CL4, CONV = 467, 484, 492, 500, 502
BRAND, END = 509, 600
SLOGAN = (520, 523)
import os as _os
if _os.environ.get('REEL_END4'):
    # V4 audio final: la música es la canción continua 02:31,77–02:56,28; su último golpe (02:51,795) cae en 20,022 s.
    # El logotipo entra en ese golpe (f500, antes f509); la convergencia se comprime. f0–495 no cambian.
    CL4, CONV, BRAND, SLOGAN = 496, 497, 500, (511, 514)

import os
HD3 = bool(os.environ.get('REEL_HD3'))   # corrección HD V3 de los segundos 3, 4 y 19: fotogramas originales a 1:1, sin mezcla ni empujes de escala
def S_exact(t): return SRC.frame(int(round(t * FPS)))   # fotograma real más próximo (sin mezclar dos fotogramas)

def setup(): V5.setup()
def S(t): return SRC.at(t)
def f32(a): return a.astype(np.float32) / 255

# ------------------------------------------------------------------ utilidades
def native(src, s=1.0, cx=960, cy=540):
    """plano a pantalla completa: 1:1 nativo; s > 1 solo para empujes mínimos (anclados en cx, cy)"""
    return f32(src) if s <= 1.0001 else f32(warp(src, cam_M(cx, cy, s, cx, cy)))

def put(canvas, win, x0, y0, alpha=1.0, clip=None, frame=True):
    h, w = win.shape[:2]
    return V.place_window(canvas, win, x0 + w / 2, y0 + h / 2, alpha=alpha, frame=frame, ticks=0.0, clip=clip)

def bg(f, src, kind='graphite', amt=0.5, dark=0.42):
    """fondo limpio: gradiente + imagen original muy desenfocada; luminancia limitada (nunca compite con las ventanas)"""
    img = over(V.bg_clean(kind, grid=0.0, f=f), V.bg_atmos(src, f, dark=dark, sat=0.72, zoom=1.15), amt)
    lum = img.mean(2, keepdims=True); k = 0.22
    return img * (np.where(lum > k, k + (lum - k) * 0.35, lum) / np.maximum(lum, 1e-4))

def hgrad(x0, x1, a0, a1):
    x = np.arange(W, dtype=np.float32); t = np.clip((x - x0) / (x1 - x0), 0, 1); t = t * t * (3 - 2 * t)
    return np.repeat((a0 + (a1 - a0) * t)[None, :], H, 0)

def dot(c, x, y, r, a=1.0): return V.dot(c, x, y, r, color=FUCHSIA, a=a)

def rect_at(keys, f, n=6):
    r = keys[0][1]
    for i, (c, rr) in enumerate(keys[1:], 1):
        if f >= c - 1: r = lerp_rect(keys[i - 1][1], rr, eo(seg(f, c - 1, c - 1 + n)))
    return r

# ------------------------------------------------------------------ tipografía (un único sistema)
T = {}
def tb(key, txt, name, size, tr=0.0):
    if key not in T: T[key] = TextBlock(txt, name, int(size), tracking=tr)
    return T[key]

def build_text():
    if T: return
    lines = ["¿CÓMO", "MUESTRAS", "LO QUE", "NO SE VE?"]                 # titular de apertura (bloque de 4 líneas)
    s1 = min([fit_size(l, 'black', MR - 1320, 104) for l in lines]); T['s1'] = s1
    for i, l in enumerate(lines): tb(f'o{i + 1}', l, 'black', s1)
    s2 = min(80, fit_size("LA TECNOLOGÍA, AL DESCUBIERTO.", 'black', 1680, 80)); T['s2'] = s2     # titulares de escena
    tb('t1', "LA TECNOLOGÍA,", 'black', s2); tb('t2', "AL DESCUBIERTO", 'black', s2)
    tb('app', "LA APLICACIÓN", 'black', s2); tb('res', "EL RESULTADO", 'black', s2); tb('dot', ".", 'black', s2)
    tb('sp', " ", 'black', s2)

def title(canvas, f, parts, x, y, f_out=None):
    """titular con máscara ascendente; parts = [(TextBlock, fotograma de entrada, dx, punto fucsia?)]"""
    out = eo(seg(f, f_out, f_out + 5)) if f_out is not None else 0.0
    for t, fin, dx, dt in parts:
        p = eo(seg(f, fin - 1, fin + 6))
        if p <= 0: continue
        clip = line_mask_y(y - 40, y + t.caph + 12, 2)
        yy = y + 0.6 * t.size * (1 - p) - 24 * out
        canvas = t.draw(canvas, x + dx, yy, mask=clip, opacity=1 - out)
        if dt: canvas = T['dot'].draw(canvas, x + dx + t.w + 2, yy, mask=clip, opacity=1 - out, color=FUCHSIA)
    return canvas

_ID = {}
def ident(canvas, f, f0, num, label, x, y, a_out=1.0):
    """identificador «01 / LO INVISIBLE» (32 px)"""
    p = eo(seg(f, f0, f0 + 8)) * a_out
    if p <= 0: return canvas
    if (num, label) not in _ID: _ID[(num, label)] = (TextBlock(num, 'bold', 32, tracking=0.1), TextBlock("/", 'semi', 32), TextBlock(label, 'semi', 32, tracking=0.2))
    n, sl, lb = _ID[(num, label)]; dx = 14 * (1 - p)
    canvas = n.draw(canvas, x + dx, y, color=FUCHSIA, opacity=p)
    canvas = sl.draw(canvas, x + n.w + 14 + dx, y, color=GREY, opacity=p)
    return lb.draw(canvas, x + n.w + sl.w + 28 + dx, y, color=WHITE, opacity=p)

_LB = {}
def label(canvas, f, f0, text, x, y, a_out=1.0, color=WHITE):
    """cartela secundaria (30 px, versalitas espaciadas) con punto fucsia"""
    p = eo(seg(f, f0, f0 + 7)) * a_out
    if p <= 0: return canvas
    if text not in _LB: _LB[text] = TextBlock(text, 'semi', 30, tracking=0.18)
    canvas = dot(canvas, x + 6, y + 11, 5, a=p)
    return _LB[text].draw(canvas, x + 24 + 10 * (1 - p), y, color=color, opacity=p)

# ================================================================== 0–66 · IMPACTO (termografía a pantalla completa)
LP = ((883 - 175) * 1.10, (493 - 49) * 1.10)      # posición de la lente en el lienzo (encuadre 1,10 desplazado a la izquierda)
def s_open(f):
    s = 1.10 * (1 + 0.03 * eio(seg(f, 0, IMMERSE)))             # encuadre mínimo + empuje anclado en la lente (sin bordes)
    M = cam_M(LENS[0], LENS[1], s, LP[0], LP[1])
    plain, th = f32(warp(_c['plainB'], M)), f32(warp(SRC.frame(B_IDX), M))
    lx, ly, lr = LP[0], LP[1], LENS[2] * s
    r = (lr + 18) * eo(seg(f, -1, 7))                            # revelación circular en el golpe inicial
    img = over(plain, th, circle_mask(lx, ly, r, 2.0))
    img = over(img, th, eio(seg(f, 10, 18)) * (1 - circle_mask(lx, ly, r, 2.0)))   # aparece el rótulo original
    pr = eo(seg(f, 2, 16))
    img = V.ring(img, lx, ly, lr + 16, a=0.85, prog=pr, width=2.2)
    img = dot(img, lx + (lr + 16) * np.cos(-np.pi / 2 + pr * 2 * np.pi), ly + (lr + 16) * np.sin(-np.pi / 2 + pr * 2 * np.pi), 6, a=eo(seg(f, 2, 5)))
    if 16 <= f <= 40:
        ys = lerp(ly - lr * 0.85, ly + lr * 0.85, eio(seg(f, 16, 38))); dx = np.sqrt(max(0, (lr * 0.9) ** 2 - (ys - ly) ** 2))
        img = V.hscan(img, ys, lx - dx, lx + dx, a=0.8 * (1 - seg(f, 36, 40)))
    # titular en bloque de cuatro líneas, en la zona derecha libre (la lente termina en x ≈ 1260)
    img = over(img, np.broadcast_to(hexbgr('#0D1219'), img.shape), hgrad(1240, 1520, 0.0, 0.80))
    s1 = T['s1']; x = 1320; y0 = 540 - (3 * 0.98 * s1 + 0.727 * s1) / 2
    for i, (key, fin) in enumerate([('o1', 0), ('o2', 2), ('o3', TITLE2), ('o4', TITLE2 + 2)]):
        img = title(img, f, [(T[key], fin, 0, False)], x, y0 + i * 0.98 * s1, f_out=IMMERSE - 6)
    return img

# ================================================================== 67–132 · INMERSIÓN (textura → partícula · match cut circular)
def particles(f):
    if f < BURST: return S(36.30 + (f - IRIS) / FPS)
    if f < MERGED: return S_exact(38.16 + (f - BURST) / FPS * 0.7) if HD3 else S(38.12 + (f - BURST) / FPS * 0.7)
    return S(39.40 + (f - MERGED) / FPS)

def s_immerse(f):
    tex = native(S(7.20 + (f - IMMERSE) / FPS), 1.0 if HD3 else 1.0 + 0.04 * seg(f, IMMERSE, IRIS + 8), 1180, 560)
    if f < IRIS - 1: return tex
    par = native(particles(f), 1.0 if HD3 else 1.0 + (0.03 * (1 - eo(seg(f, BURST - 1, BURST + 6))) if BURST <= f < MERGED else 0.0))
    if f >= IRIS + 8: return par
    k = 1 - (1 - seg(f, IRIS - 1, IRIS + 7)) ** 2.4
    R = lerp(40, 1200, k)
    img = over(tex, par, circle_mask(W / 2, H / 2, R, 2.0))
    return V.ring(img, W / 2, H / 2, R, a=0.8 * (1 - k), width=2.0)

# ================================================================== 133–216 · EXPLICAR LO INVISIBLE (comparación técnica)
D_R = (ML, 170, 1200)                # dominante: 1200 × 675 (170–845)
C_R = (1360, 170 + (675 - 248) // 2, 440)   # complementaria: 440 × 248, centrada respecto a la dominante (x 1360–1800)
def s_explain(f):
    img = bg(f, SRC.frame(B_IDX), 'graphite', amt=0.5)
    ein = eo(seg(f, EXPL - 1, EXPL + 7)); out = ei(seg(f, OUT, TECH))
    dx, dy, dw = D_R; cx, cy, cw = C_R
    dx = dx - 1400 * out; cx = cx + 700 * out
    # dominante: pared → lectura térmica revelada por el escáner (mismo encuadre, registrado)
    u = eio(seg(f, SCAN_A - 1, SCAN_B - 2))
    a, b = wimg(_c['plainB'], dw), wimg(SRC.frame(B_IDX), dw)
    win = over(a, b, 1 - _xm(a, u)) if u > 0 else a
    sc = 1 + 0.05 * (1 - ein); dwin = cv2.resize(win, (int(dw * sc) // 2 * 2, hw(int(dw * sc) // 2 * 2)), interpolation=cv2.INTER_AREA) if sc > 1.001 else win
    img, bd = put(img, dwin, dx - (dwin.shape[1] - dw) / 2, dy - (dwin.shape[0] - hw(dw)) / 2, alpha=ein)
    if SCAN_A - 1 <= f <= SCAN_B:
        xs = bd[0] + bd[2] * u; img = V.vscan(img, xs, bd[1] - 26, bd[1] + bd[3] + 26); img = dot(img, xs, bd[1] - 26, 5); img = dot(img, xs, bd[1] + bd[3] + 26, 5)
    img = label(img, f, EXPL + 6, "ANTES", bd[0], bd[1] + bd[3] + 24, a_out=1 - seg(f, OUT, OUT + 3), color=GREY)
    # complementaria: la misma estancia tras la intervención, su lectura térmica revelada a continuación
    if f >= SEC_IN - 1:
        ci = eo(seg(f, SEC_IN - 1, SEC_IN + 7))
        u2 = eio(seg(f, SCAN_B - 1, LINK - 1))
        a2, b2 = wimg(_c['plainC'], cw), wimg(SRC.frame(AF_IDX), cw)
        win2 = over(a2, b2, 1 - _xm(a2, u2)) if u2 > 0 else a2
        img, bc = put(img, win2, cx + 80 * (1 - ci), cy, alpha=ci)
        if SCAN_B - 1 <= f <= LINK: img = V.vscan(img, bc[0] + bc[2] * u2, bc[1] - 20, bc[1] + bc[3] + 20)
        img = label(img, f, SEC_IN + 4, "DESPUÉS", bc[0], bc[1] + bc[3] + 24, a_out=1 - seg(f, OUT, OUT + 3))
        # las dos lentes, conectadas
        pr = eo(seg(f, LINK - 1, LINK + 9)) * (1 - out)
        if pr > 0:
            (ax, ay), (qx, qy) = V.to_win(bd, LENS[0], LENS[1]), V.to_win(bc, LENS[0], LENS[1])
            ra, rq = LENS[2] * bd[2] / 1920 + 14, LENS[2] * bc[2] / 1920 + 10
            kk = 1 + 0.08 * pulse(f, KICK, 1.0, 3)
            img = V.ring(img, ax, ay, ra * kk, a=0.85, prog=pr, width=2.0); img = V.ring(img, qx, qy, rq * kk, a=0.85, prog=pr, width=2.0)
            pl = eo(seg(f, LINK + 4, LINK + 14)) * (1 - out)
            p0, p1 = (ax + ra, ay), (qx - rq, qy)
            img = V.seg_line(img, p0, p1, a=0.8, w=2.0, prog=pl)
            if pl > 0: img = dot(img, *p0, 5); img = dot(img, *p1, 5, a=seg(f, LINK + 13, LINK + 15))
    img = ident(img, f, EXPL + 4, "01", "LO INVISIBLE", ML, 104, a_out=1 - seg(f, OUT, OUT + 4))
    if f >= OUT:   # la línea del escáner cruza el lienzo y anuncia la revelación
        g = eio(seg(f, OUT, TECH)); img = V.vscan(img, lerp(W + 20, -20, g), 0, H, a=0.9)
    return img

# ================================================================== 217–299 · LA TECNOLOGÍA, AL DESCUBIERTO
def tech_src(f): return S(min(70.40 + max(0, f - TECH - 8) / FPS * 1.79, 80.5))
M_KEYS = [(TECH, (0, 0, W)), (EDIT_T, (ML, 210, 1240))]
def s_tech(f):
    x, y, w = rect_at(M_KEYS, f, 7); w = int(w) // 2 * 2
    full = w >= W - 1
    if f < TECH + 8:                                             # en el golpe: el sistema se abre (transición original acelerada)
        uu = lerp(1.04, -0.04, eio(seg(f, TECH - 1, TECH + 7)))
        a, b = f32(SRC.frame(PLAIN_IDX)), f32(S(70.40))
        frame = over(a, b, _xm(a, uu))
        frame = V.vscan(frame, uu * W, 0, H)
    else:
        frame = f32(tech_src(f))
    if full: return frame
    img = bg(f, tech_src(f), 'petrol', amt=0.35)
    win = cv2.resize(frame, (w, hw(w)), interpolation=cv2.INTER_AREA)
    img, bm = put(img, win, x, y)
    # composición final: detalle nativo del componente, conectado con la representación completa
    if f >= DET - 1:
        k = eo(seg(f, DET - 1, DET + 7)); dw = 400; cw = 420
        det = wimg(SRC.frame(1800), dw, crop=(323, 745, cw))
        img, bdt = put(img, det, 1400 + 60 * (1 - k), bm[1] + bm[3] - hw(dw), alpha=k)
        ax, ay = V.to_win(bm, 323, 745); ra = 300 * bm[2] / 1920
        img = V.ring(img, ax, ay, ra, a=0.85, prog=eo(seg(f, DET, DET + 9)), width=2.0)
        pl = eo(seg(f, DET + 4, DET + 14))
        p0, p1 = (ax + ra, ay), (bdt[0] - 14, bdt[1] + bdt[3] / 2)
        img = V.seg_line(img, p0, p1, a=0.8, w=2.0, prog=pl)
        if pl > 0: img = dot(img, *p0, 5); img = dot(img, *p1, 5, a=seg(f, DET + 13, DET + 15))
        img = label(img, f, DET + 6, "DETALLE DEL SISTEMA", bdt[0], bdt[1] - 48, a_out=1 - seg(f, APP - 4, APP))
    s2 = T['s2']; t1 = T['t1']
    img = title(img, f, [(t1, EDIT_T, 0, False), (T['t2'], T2, t1.w + T['sp'].w, True)], ML, 104, f_out=APP - 5)
    return img

# ================================================================== 300–399 · LA APLICACIÓN
def roller(f): return S(131.00 + (f - APP) / FPS * 0.75)        # macro del rodillo (antes de 02:14,2)
def operator(f): return S(169.60 + (f - APP) / FPS * 0.9)       # operario proyectando (plano general)
A_DOM, A_SEC = (ML, 210, 1040), (1200, 210, 600)
R_KEYS = [(APP, (0, 0, W)), (SPLIT, A_SEC), (SWAP, A_DOM)]       # rodillo: pantalla completa → detalle → protagonista
O_KEYS = [(APP, (ML, 1200, 1040)), (SPLIT, A_DOM), (SWAP, A_SEC)]  # operario: entra como protagonista → pasa a detalle
def s_app(f):
    if f < SPLIT - 1: return native(roller(f))
    img = bg(f, operator(f), 'graphite', amt=0.5)
    rr, ro = rect_at(R_KEYS, f, 7), rect_at(O_KEYS, f, 7)
    big_r = f >= SWAP + 3
    for nm, (x, y, w) in ([('o', ro), ('r', rr)] if not big_r else [('r', rr), ('o', ro)]):
        w = int(w) // 2 * 2
        img, b = put(img, wimg(roller(f) if nm == 'r' else operator(f), w), x, y, alpha=(eo(seg(f, SPLIT - 1, SPLIT + 6)) if nm == 'o' else 1.0))
        if nm == 'r': br = b
        else: bo = b
    a_o = 1 - seg(f, MIST - 3, MIST)
    img = label(img, f, SPLIT + 6, "APLICACIÓN REAL", bo[0], bo[1] + bo[3] + 22, a_out=a_o)
    img = label(img, f, SPLIT + 10, "DETALLE DEL PROCESO", br[0], br[1] + br[3] + 22, a_out=a_o)
    img = title(img, f, [(T['app'], SPLIT, 0, True)], ML, 104, f_out=MIST - 5)
    return img

def mist(f): return native(S(191.40 + (f - MIST) / FPS))       # proyección sobre la superficie (pantalla completa)

def s_mist(f):
    img = mist(f)
    if f < MIST + 3:   # entra por corte con un breve barrido desde la composición anterior
        p = eio(seg(f, MIST - 1, MIST + 3)); img = over(s_app(MIST - 1), img, line_mask_x(-1e5, lerp(-100, W + 100, p), 120))
    return img

# ================================================================== 400–466 · EL RESULTADO
def house(f): return SRC.frame(HOUSE + max(0, f - RES))
H_KEYS = [(RES, (0, 0, W)), (RES_L, (ML, 210, 1240))]
def s_result(f):
    x, y, w = rect_at(H_KEYS, f, 7); w = int(w) // 2 * 2
    if w >= W - 1:
        img = native(house(f))
        if f < RES + 5:   # la niebla del spray barre hacia la arquitectura
            p = eio(seg(f, RES - 5, RES + 5)); xw = lerp(-260, W + 260, p)
            img = over(img, mist(min(f, RES - 1)), line_mask_x(xw, 1e5, 240))
            xx = np.arange(W, dtype=np.float32)[None, :]
            img = np.clip(img + (np.exp(-((xx - xw) / 150) ** 2) * 0.25)[..., None] * V.SCAN, 0, 1)
        return img
    img = bg(f, house(f), 'graphite', amt=0.5)
    img, bh = put(img, wimg(house(f), w), x, y)
    if f >= RES_D - 1:   # detalle del proceso: pequeño, abajo a la derecha; no compite con el edificio
        k = eo(seg(f, RES_D - 1, RES_D + 7)); dw = 400
        img, bd = put(img, wimg(S(135.40 + (f - RES_D) / FPS), dw), 1400 + 60 * (1 - k), bh[1] + bh[3] - hw(dw), alpha=k)
        img = label(img, f, RES_D + 5, "DETALLE DEL PROCESO", bd[0], bd[1] - 48)
    img = title(img, f, [(T['res'], RES_L, 0, True)], ML, 104)
    return img

# ================================================================== 467–508 · CLÍMAX (imágenes grandes sobre la percusión)
def c_part(f):
    if HD3:   # perspectiva posterior de la partícula (03_PARTICULA_FINAL), 1×, rótulos ya estables; distinta del segundo 4
        return S_exact(41.48 + min(max(f - CL1, 0), 14) / FPS)   # 41,48–42,04 s: la 3.ª cartela empieza en 42,08 s
    return S(38.30 + (f - CL1) / FPS * 0.5)
LS, RS = (ML, 271, 820), (980, 271, 820)          # dos ventanas grandes 820 × 461
LCY = 453                                         # eje del logotipo
L_KEYS = [(CL1, (0, 0, W)), (CL2, LS), (CONV, (ML + 140, LCY - hw(720) / 2, 720))]
R_KEYS2 = [(CL1, (W + 40, 271, 820)), (CL2, RS), (CONV, (980 + 20, LCY - hw(720) / 2, 720))]
def fold_k(f): return 1 - eio(seg(f, CONV + 2, BRAND + 1))

def s_climax(f):
    if f < CL2 - 1: return native(c_part(f), 1.0 if HD3 else 1.0 + 0.04 * eio(seg(f, CL1, CL2)))
    img = bg(f, SRC.frame(MULTI_FULL), 'graphite', amt=0.45)
    k = fold_k(f)
    for nm, keys in (('L', L_KEYS), ('R', R_KEYS2)):
        x, y, w = rect_at(keys, f, 5); w = int(w) // 2 * 2; h0 = hw(w)
        if nm == 'L':      # partícula → termografía (máscara en 19,69 s)
            a, b = wimg(c_part(f), w), wimg(SRC.frame(B_IDX), w); u = eio(seg(f, CL3 - 1, CL3 + 4))
            win = over(a, b, 1 - _xm(a, u)) if u > 0 else a
        else:              # sistema multicapa → aplicación real (máscara en 20,02 s)
            a, b = wimg(SRC.frame(MULTI_FULL), w), wimg(roller(APP + 40), w); u = eio(seg(f, CL4 - 1, CL4 + 4))
            win = over(a, b, _xm(a, 1 - u)) if u > 0 else a
        if k < 1:          # convergencia: las ventanas se pliegan en el eje del logotipo
            hh = max(2, int(h0 * k)); win = cv2.resize(win, (w, hh), interpolation=cv2.INTER_AREA); y = LCY - hh / 2
        img, b_ = put(img, win, x, y, frame=k > 0.25)
        if 0 < u < 1: img = V.vscan(img, b_[0] + b_[2] * (u if nm == 'L' else 1 - u), b_[1] - 22, b_[1] + b_[3] + 22)
    pl = eio(seg(f, CONV, BRAND))
    if pl > 0:     # una línea fucsia une las dos imágenes: se convierte en el eje de la marca
        half = 500 * pl
        img = over(img, np.broadcast_to(FUCHSIA, img.shape), line_mask_x(W / 2 - half, W / 2 + half, 1.5) * line_mask_y(LCY - 1.5, LCY + 1.5, 1.0))
        img = dot(img, W / 2 - half, LCY, 5); img = dot(img, W / 2 + half, LCY, 5)
    return img

# ================================================================== 509–599 · CIERRE DE MARCA (logotipo original)
LOGO_W = 960; LOGO_H = 406 * LOGO_W / 1065
_BG = {}
def brand_bg():
    if 'g' not in _BG:
        x = np.linspace(0, 1, W, dtype=np.float32)[None, :, None]; y = np.linspace(0, 1, H, dtype=np.float32)[:, None, None]
        g = hexbgr('#101A23') * (1 - 0.6 * y) + hexbgr('#0D1219') * (0.6 * y)
        g = g * np.ones((H, W, 1), np.float32)
        yy, xx = np.mgrid[:H, :W].astype(np.float32)
        vig = 1 - 0.32 * np.clip(((xx - W / 2) / (W * 0.62)) ** 2 + ((yy - LCY) / (H * 0.75)) ** 2, 0, 1.4)
        img = np.clip(g * vig[..., None], 0, 1)
        haze = V.bg_atmos(SRC.frame(B_IDX), 0, dark=0.35, sat=0.9, zoom=1.6)            # textura cromática muy oscura
        img = 1 - (1 - img) * (1 - 0.08 * haze)
        fx, fy = W / 2 - LOGO_W / 2 + 208 * LOGO_W / 1065, LCY - LOGO_H / 2 + 85 * LOGO_W / 1065
        glow = np.exp(-(((xx - fx) / 360) ** 2 + ((yy - fy) / 300) ** 2))[..., None].astype(np.float32) * 0.08
        _BG['g'] = np.clip(img + glow * FUCHSIA, 0, 1)
    return _BG['g'].copy()

def slogan():
    if 'l1' not in T:
        tb('l1', "LO DIFÍCIL DE EXPLICAR,", 'semi', 48, 0.03)
        s = fit_size("LO HACEMOS VISIBLE.", 'black', LOGO_W, 88); tb('l2', "LO HACEMOS VISIBLE", 'black', s); tb('dotl', ".", 'black', s)
    return T['l1'], T['l2'], T['dotl']

def s_brand(f):
    img = brand_bg()
    if f < BRAND + 3: img = over(img, s_climax(f), 1 - eio(seg(f, BRAND - 1, BRAND + 3)))
    sc = LOGO_W / 1065 * (1 + 0.04 * (1 - eo(seg(f, BRAND - 1, BRAND + 9))))     # 104 % → 100 %
    hh = (406 * sc / 2 + 12) * eio(seg(f, BRAND - 1, BRAND + 6))                # la línea se abre y revela el logotipo
    img, _ = V5.put_logo(img, sc, W / 2, LCY, mask=line_mask_y(LCY - hh, LCY + hh, 3))
    a_e = 1 - seg(f, BRAND + 4, BRAND + 8)
    if a_e > 0:
        for yy_ in (LCY - hh, LCY + hh):
            img = over(img, np.broadcast_to(FUCHSIA, img.shape), line_mask_x(W / 2 - 500, W / 2 + 500, 1.5) * line_mask_y(yy_ - 1.2, yy_ + 1.2, 1.0) * a_e)
    l1, l2, dt = slogan()
    y1 = LCY + LOGO_H / 2 + 52; y2 = y1 + l1.caph + 24
    p1, p2 = eo(seg(f, SLOGAN[0], SLOGAN[0] + 10)), eo(seg(f, SLOGAN[1], SLOGAN[1] + 10))   # después, composición estática
    if p1 > 0: img = l1.draw(img, (W - l1.w) / 2, y1 + 12 * (1 - p1), color=np.array([0.90, 0.91, 0.93], np.float32), opacity=p1)
    if p2 > 0:
        x2 = (W - l2.w - dt.w) / 2; clip = line_mask_y(-1e5, y2 + l2.caph + 8, 2)
        img = l2.draw(img, x2, y2 + 18 * (1 - p2), opacity=p2, mask=clip)
        img = dt.draw(img, x2 + l2.w + 2, y2 + 18 * (1 - p2), opacity=p2, mask=clip, color=FUCHSIA)
    return img

# ================================================================== router
def render_frame(f):
    setup(); build_text()
    if f < IMMERSE: return s_open(f)
    if f < EXPL: return s_immerse(f)
    if f < TECH: return s_explain(f)
    if f < APP: return s_tech(f)
    if f < MIST: return s_app(f)
    if f < RES: return s_mist(f)
    if f < CL1: return s_result(f)
    if f < BRAND: return s_climax(f)
    return s_brand(f)

CLIPS = [  # (inicio, fin, composición, clip, tiempo en el original, uso)
    (0, 66, "A · pantalla completa", "03_TERMOGRAFIA", "00:55,72 (registrada) → 00:57,60", "Revelación circular de la lente + titular"),
    (67, 82, "A", "01_MACRO_AZUL", "00:07,20–00:07,82", "Textura microscópica"),
    (83, 99, "D · match cut circular", "02_PARTICULAS", "00:36,30–00:36,96", "Iris desde el centro"),
    (100, 116, "A", "02_PARTICULAS", "00:38,12–00:38,58 (0,7x)", "Transformación luminosa"),
    (117, 132, "A", "02_PARTICULAS", "00:39,40–00:40,00", "Partícula resultante"),
    (133, 216, "B · comparación", "03_TERMOGRAFIA", "00:55,72→00:57,60 · 01:05,40→01:03,60", "Antes / después real (mismo encuadre) con escáner"),
    (217, 232, "A", "04_SISTEMA_MULTICAPA", "01:09,32 → 01:10,40", "El sistema se abre en el golpe"),
    (233, 299, "C · editorial", "04_SISTEMA_MULTICAPA", "01:10,40–01:15,70 (1,79x) + 01:12,00 (detalle nativo)", "Titular + detalle conectado"),
    (300, 332, "A", "05_RODILLO", "02:11,00–02:11,99", "Aplicación a pantalla completa"),
    (333, 383, "B/C · dos perspectivas", "05_RODILLO + 06_PROYECCION", "02:11,99–02:13,50 · 02:50,59–02:52,21", "Intercambio de protagonismo en 14,69 s"),
    (384, 399, "A", "07_SPRAY_DETALLE", "03:11,40–03:12,04", "Proyección; la niebla barre al resultado"),
    (400, 466, "A → C", "08_FACHADAS + llana", "03:40,60–03:43,24 · 02:15,40–02:16,88", "Arquitectura completa + detalle del proceso"),
    (467, 508, "Clímax", "02 · 03 · 04 · 05", "00:38,30 · 00:57,60 · 01:20,00 · 02:12,60", "Dos ventanas grandes, máscaras en la percusión"),
    (509, 599, "Cierre", "Logotipo oficial (PNG original)", "—", "Revelación desde la línea fucsia + eslogan"),
]
