# DIBURAMA · THERMOLIME · «LO HACEMOS VISIBLE» — V2 (montaje con más ritmo y mejor selección)
# Cortes en fotogramas (25 fps) sobre acentos medidos de la música (corcheas cada ~0,333 s).
import numpy as np, cv2
from lib import *

# ------------------------------------------------------------------ cues (fotograma = transitorio real)
ZOOMOUT, IRIS, BLUE2, PART, BURST, MERGED = 17, 42, 67, 83, 100, 117
CMP, CMP_WIPE, CMP_P1, CMP_P2 = 133, 150, 162, 175
PLAIN, SLIT, TECH, TECH_ACC, PAN, SCAN, CLICK = 187, 200, 217, 225, 233, 242, 250
ROLL1, ROLL2, TROWEL = 263, 275, 283
SPR_WIDE, SPR_NOZ, SPR_MIST, SPR_OP = 300, 317, 333, 350
ARCH, ARCH2 = 363, 400
M_FIRE, M_BUILD, M_BURST, BRAND, END = 417, 425, 433, 442, 500

TX = 80
LY = 820                                   # centro de la lupa en el lienzo (plano B)
A_IDX, B_IDX = 1393, 1440                  # 55.72 pared sin lupa · 57.60 lupa térmica (antes)
AFTER_IDX = 1590                           # 63.60 lupa térmica (después: rotura del puente térmico)
FIELD_IDX = 812
LENS_C, LENS_RI, LENS_RO = (883.0, 493.0), 360.0, 405.0
RP_PLAIN_IDX = 1733                        # 69.32 panel derecho, enfoscado liso
_c = {}

def _reg(a, b, mask):
    orb = cv2.ORB_create(6000)
    ka, da = orb.detectAndCompute(cv2.cvtColor(a, cv2.COLOR_BGR2GRAY), mask)
    kb, db = orb.detectAndCompute(cv2.cvtColor(b, cv2.COLOR_BGR2GRAY), mask)
    m = cv2.BFMatcher(cv2.NORM_HAMMING, crossCheck=True).match(db, da)
    pb = np.float32([kb[x.queryIdx].pt for x in m]); pa = np.float32([ka[x.trainIdx].pt for x in m])
    M, _ = cv2.estimateAffinePartial2D(pb, pa, ransacReprojThreshold=2.5)
    return M          # lleva coordenadas de b -> a

def setup():
    if _c: return
    A, B, C = SRC.frame(A_IDX), SRC.frame(B_IDX), SRC.frame(AFTER_IDX)
    mk = np.full((1080, 1920), 255, np.uint8); cv2.circle(mk, (883, 495), 420, 0, -1); cv2.rectangle(mk, (1080, 140), (1720, 310), 0, -1)
    M = _reg(A, B, mk); _c['Bn'] = cv2.warpAffine(A, M, (1920, 1080), flags=cv2.INTER_CUBIC | cv2.WARP_INVERSE_MAP)
    c = M @ np.array([LENS_C[0], LENS_C[1], 1.0]); _c['lensA'] = (float(c[0]), float(c[1]))
    mk2 = np.full((1080, 1920), 255, np.uint8); cv2.circle(mk2, (883, 495), 420, 0, -1); cv2.rectangle(mk2, (1080, 120), (1720, 320), 0, -1)
    Mc = _reg(C, B, mk2)    # B -> C
    _c['after'] = cv2.warpAffine(C, Mc, (1920, 1080), flags=cv2.INTER_CUBIC | cv2.WARP_INVERSE_MAP)  # «después» en coords de «antes»
    P, Q = SRC.frame(RP_PLAIN_IDX), SRC.frame(1775)
    mk3 = np.zeros((1080, 1920), np.uint8); mk3[150:, 900:] = 255; mk3[400:1050, 1100:1500] = 0
    Mp = _reg(P, Q, mk3)    # Q(ladrillo) -> P(liso)
    _c['plainR'] = cv2.warpAffine(P, Mp, (1920, 1080), flags=cv2.INTER_CUBIC | cv2.WARP_INVERSE_MAP)  # liso en coords de ladrillo
    for i0, n in [(1424, 20), (1440, 30), (172, 45), (907, 18), (951, 12), (985, 18), (1733, 50), (1774, 22),
                  (3250, 14), (3325, 10), (3385, 20), (4667, 18), (4305, 18), (4787, 20), (4240, 16), (5515, 40),
                  (5622, 20), (572, 12), (435, 12), (953, 10)]:
        SRC.load(i0, n)

def S(t): return SRC.at(t)
def lay(img, cx, cy, s, **kw): return src_layer(img, cx, cy, s, **kw)

def src_layer(img, cx, cy, s, ax=W / 2, ay=H / 2, blur_from=None, n=11):
    if blur_from is None: return f32(warp(img, cam_M(cx, cy, s, ax, ay)))
    cx0, cy0, s0 = blur_from
    Ms = [cam_M(lerp(cx0, cx, k / (n - 1)), lerp(cy0, cy, k / (n - 1)), lerp(s0, s, k / (n - 1)), ax, ay) for k in range(n)]
    return warp_blur(img, Ms)

def punch(f, at, amt=0.06, n=4): return 1 + amt * (1 - eo(seg(f, at - 1, at - 1 + n)))
def scrim(img, y0=1050, y1=1660, a=0.8): return over(img, np.broadcast_to(NAVY_D, img.shape), vgrad(y0, y1, 0, a))

# ------------------------------------------------------------------ textos (3 bloques)
TXT = {}
def build_text():
    if TXT: return
    s1 = min(fit_size("¿CÓMO MUESTRAS", 'black', 860, 130), fit_size("LO QUE NO SE VE?", 'black', 860, 130))
    TXT['s1'] = s1; TXT['l1'] = TextBlock("¿CÓMO MUESTRAS", 'black', s1); TXT['l2'] = TextBlock("LO QUE NO SE VE?", 'black', s1)
    TXT['hacemos'] = TextBlock("HACEMOS", 'semi', 56, tracking=0.22)
    TXT['visible'] = TextBlock("VISIBLE", 'black', fit_size("VISIBLE", 'black', 860, 160))
    TXT['latec'] = TextBlock("LA TECNOLOGÍA", 'black', fit_size("LA TECNOLOGÍA", 'black', 760, 92))
    TXT['dib'] = TextBlock("DIBURAMA", 'brand', fit_size("DIBURAMA", 'brand', 800, 168, 0.06), tracking=0.06)
    TXT['dificil'] = TextBlock("LO DIFÍCIL DE EXPLICAR,", 'semi', fit_size("LO DIFÍCIL DE EXPLICAR,", 'semi', 760, 56))
    sh = fit_size("LO HACEMOS VISIBLE", 'black', 760, 90); TXT['sh'] = sh
    TXT['lhv'] = TextBlock("LO HACEMOS VISIBLE", 'black', sh); TXT['dot'] = TextBlock(".", 'black', sh)

def block1(img, f):
    s1 = TXT['s1']; c1 = 1300; c2 = c1 + s1 * 0.727 + s1 * 0.26
    out = eo(seg(f, 76, 82))
    p1 = eo(seg(f, -1, 5)); p2 = eo(seg(f, IRIS - 1, IRIS + 5))
    img = TXT['l1'].draw(img, TX, c1 + 26 * (1 - p1) - 40 * out, opacity=1 - out, shadow=0.4, blur=5 * out)
    if p2 > 0:
        m = line_mask_y(-1e5, c2 + s1 * 0.727 + 8, 2)
        img = TXT['l2'].draw(img, TX, c2 + 50 * (1 - p2) - 40 * out, opacity=p2 * (1 - out), shadow=0.4, mask=m, blur=5 * out)
    return img

def block2(img, f):
    if f < TECH - 1 or f >= ROLL1: return img
    out = eo(seg(f, ROLL1 - 5, ROLL1))
    ph = eo(seg(f, TECH - 1, TECH + 6)); pv = eo(seg(f, TECH - 1, TECH + 9)); pt_ = eo(seg(f, TECH_ACC - 1, TECH_ACC + 6))
    v = TXT['visible']; yv = 1300
    img = TXT['hacemos'].draw(img, TX + 3 - 40 * (1 - ph), yv - 62, opacity=ph * (1 - out), shadow=0.35)
    xr = TX + (v.w + 30) * pv
    img = v.draw(img, TX, yv, mask=line_mask_x(-1e5, xr, 24), opacity=1 - out, shadow=0.4, scale=lerp(1.08, 1, pv))
    if 0 < pv < 0.999:
        xx = np.arange(W, dtype=np.float32)[None, :]
        img = v.draw(img, TX, yv, color=np.array([1.0, 0.97, 0.9], np.float32), opacity=0.9,
                     mask=np.repeat(np.exp(-((xx - xr) / 60) ** 2), H, 0), blur=10)
    if pt_ > 0:
        t = TXT['latec']; y = yv + v.caph + 32
        img = t.draw(img, TX, y + 30 * (1 - pt_), opacity=pt_ * (1 - out), shadow=0.4, mask=line_mask_y(-1e5, y + t.caph + 8, 2))
    return img

# ------------------------------------------------------------------ 0–41 · termografía
def lens_comp(f, sl, sb, ly, blue=None, blue_R=None, nb=1, prev=None):
    """lupa térmica 2.5D sobre la pared real; si blue!=None, el interior de la lupa se abre a la textura azul"""
    A = SRC.frame(A_IDX); ax_, ay_ = _c['lensA']
    th_src = S(56.96 + min(f, 60) / FPS)
    bg = lay(A, ax_, ay_, sb, ay=ly, blur_from=(ax_, ay_, prev[1]) if prev else None)
    bg = cv2.GaussianBlur(bg, (0, 0), 2.4) * 0.78
    th = lay(th_src, LENS_C[0], LENS_C[1], sl, ay=ly, blur_from=(LENS_C[0], LENS_C[1], prev[0]) if prev else None)
    outer = circle_mask(W / 2, ly, LENS_RO * sl, 1.5)
    img = bg * (1 - drop_shadow(outer, 0, 34, 42, 0.6)[..., None])
    img = over(img, sharpen(th, 0.3), outer)
    if blue is not None:
        img = over(img, blue, circle_mask(W / 2, ly, blue_R, 2.0))
    return img

def scene_thermal(f):
    if f < ZOOMOUT:                 # impacto: termografía macro llenando el encuadre
        s = 2.48 * punch(f, 0, 0.07, 5) + 0.10 * seg(f, 0, ZOOMOUT)
        img = sharpen(lay(S(56.96 + f / FPS), LENS_C[0], LENS_C[1], s), 0.3)
        img = scrim(grain(img, f), 1050, 1700, 0.75)
        return block1(img, f)
    # salida de la lupa: la cámara retrocede y descubre la pared real
    def P(x):
        k = eo(seg(x, ZOOMOUT - 1, ZOOMOUT + 9))
        sl = lerp(2.58 * 1.0, 1.04, k) + 0.04 * seg(x, ZOOMOUT + 9, IRIS)
        if x > 34: sl *= 1 + 0.55 * seg(x, 34, IRIS) ** 2
        ly = lerp(960, LY, k)
        return sl, 2.0 + 0.12 * seg(x, ZOOMOUT, IRIS), ly
    sl, sb, ly = P(f)
    prev = P(f - 0.8) if (f < ZOOMOUT + 5 or f > 37) else None
    img = lens_comp(f, sl, sb, ly, nb=1, prev=(prev[0], prev[1]) if prev else None)
    img = scrim(grain(img, f), 1050, 1700, 0.75)
    return block1(img, f)

# ------------------------------------------------------------------ 42–82 · textura microscópica azul
def blue_a(f): return sharpen(lay(S(7.20 + (f - IRIS) / FPS), 820, 560, 1.85 + 0.12 * seg(f, IRIS, BLUE2)), 0.25)
def scene_blue(f):
    if f < BLUE2:
        bl = blue_a(f)
        if f < IRIS + 9:            # IRIS: el interior de la lupa se abre al mundo microscópico
            x = seg(f, IRIS - 1, IRIS + 8); k = 1 - (1 - x) ** 2.2
            sl = 1.08 * 1.55 * (1 + 0.5 * k)
            R = lerp(LENS_RI * sl, 1250, k)
            img = lens_comp(IRIS - 1, sl, 2.12 * (1 + 0.3 * k), LY, blue=bl, blue_R=R)
            # el anillo de la lupa acompaña la apertura
            ring_s = R / LENS_RI
            ring = lay(SRC.frame(B_IDX), LENS_C[0], LENS_C[1], ring_s, ay=LY)
            ann = circle_mask(W / 2, LY, LENS_RO * ring_s, 1.5) - circle_mask(W / 2, LY, (LENS_RI + 4) * ring_s, 1.5)
            img = over(img, ring, np.clip(ann, 0, 1))
        else:
            img = bl
    else:                           # macro de cristales (cambio de escala en el acento)
        s = 2.75 * punch(f, BLUE2, 0.07) + 0.15 * seg(f, BLUE2, PART)
        img = sharpen(lay(S(8.16 + (f - BLUE2) / FPS), 1420, 600, s), 0.3)
    img = scrim(grain(img, f), 1050, 1700, 0.7 * (1 - seg(f, 76, 83)))
    return block1(img, f)

# ------------------------------------------------------------------ 83–132 · transformación de partículas
PAR_C = (760.0, 525.0)
def scene_particles(f):
    if f < BURST:                   # recorrido por los tres componentes
        def C(x):
            k = eio(seg(x, PART - 1, BURST))
            return lerp(1480, 1010, k), lerp(360, 560, k), 2.05 + 0.25 * k
        cx, cy, s = C(f); px, py, ps = C(f - 0.9)
        img = sharpen(lay(S(36.30 + (f - PART) / FPS), cx, cy, s, blur_from=(px, py, ps)), 0.25)
    elif f < MERGED:                # destello de transformación (ralentí 0,6x)
        t = 38.12 + (f - BURST) / FPS * 0.6
        s = 1.95 * punch(f, BURST, 0.22, 7) + 0.08 * seg(f, BURST, MERGED)
        bf = (1000, 530, 1.95 * punch(f - 0.8, BURST, 0.22, 7)) if f < BURST + 4 else None
        img = sharpen(lay(S(t), 1000, 530, s, blur_from=bf), 0.2)
    else:                           # partícula resultante: pulsos en semicorcheas
        fl = SRC.frame(FIELD_IDX)
        bg = cv2.GaussianBlur(lay(fl, 960, 540, 2.0 + 0.3 * seg(f, MERGED, CMP)), (0, 0), 2.0) * 0.75
        sp = 1.30 * punch(f, MERGED, 0.12, 5) + sum(pulse(f, a, 0.035, 2.5) for a in (121, 125, 129))
        fg = lay(S(39.40 + (f - MERGED) / FPS), PAR_C[0], PAR_C[1], sp, ay=900)
        m = circle_mask(W / 2, 900, 352 * sp, 2.0)
        img = bg * (1 - drop_shadow(m, 0, 30, 40, 0.5)[..., None])
        img = over(img, sharpen(fg, 0.25), m)
        img = ring_draw(img, W / 2, 900, 357 * sp, 2.0, WHITE, 0.35)
    return grain(img, f)

# ------------------------------------------------------------------ 133–186 · comparación térmica antes / después
def scene_compare(f):
    s = 1.95 * punch(f, CMP, 0.06) + 0.12 * seg(f, CMP, PLAIN)
    cx, cy = 815, 540
    before = sharpen(lay(SRC.frame(B_IDX), cx, cy, s), 0.3)
    after = sharpen(lay(_c['after'], cx, cy, s), 0.3)
    if f < CMP_WIPE - 1:
        xw = W + 50
    elif f < CMP_P1:
        xw = lerp(W + 50, 150, eio(seg(f, CMP_WIPE - 1, CMP_P1 - 2)))
    elif f < CMP_P2:
        xw = lerp(150, 560, eo(seg(f, CMP_P1 - 1, CMP_P1 + 6)))
    else:
        xw = lerp(560, 420, eo(seg(f, CMP_P2 - 1, CMP_P2 + 6)))
    img = over(before, after, line_mask_x(xw, 1e5, 3))
    # línea de comparación (mismo lenguaje que el escaneo)
    xx = np.arange(W, dtype=np.float32)[None, :]
    a = 1.0 if CMP_WIPE - 1 <= f else 0.0
    band = (np.clip(1.8 - np.abs(xx - xw), 0, 1) + 0.35 * np.exp(-((xx - xw) / 20) ** 2)) * a
    img = np.clip(img + band[..., None] * np.array([1.0, 0.95, 0.85], np.float32), 0, 1)
    return grain(img, f)

# ------------------------------------------------------------------ 187–262 · sistema multicapa
RA_C = (323.0, 618.0)
def scene_multi(f):
    if f < SLIT:                    # enfoscado: nada a la vista
        k = eio(seg(f, PLAIN - 1, SLIT))       # desplazamiento lateral sobre el enfoscado
        s = 2.05 * punch(f, PLAIN, 0.05) + 0.10 * k
        img = sharpen(lay(SRC.frame(RP_PLAIN_IDX), lerp(1560, 1250, k), 600, s, blur_from=(lerp(1560, 1250, eio(seg(f - 0.8, PLAIN - 1, SLIT))), 600, s)), 0.3)
    elif f < TECH:                  # la rendija empieza a abrirse (ralentí, tensión)
        t = 69.36 + (f - SLIT) / FPS * 0.32
        s = 2.08 * punch(f, SLIT, 0.06) + 0.34 * seg(f, SLIT, TECH) ** 2.2
        img = sharpen(lay(S(t), RA_C[0], 618, s), 0.3)
    elif f < PAN:                   # GOLPE 8,69: las capas se abren de golpe + empujón
        k = seg(f, TECH - 1, TECH + 5)
        t = 69.58 + 0.52 * eo(k) + max(0, f - TECH - 5) / FPS
        s = 2.10 * punch(f, TECH, 0.16, 6) + 0.40 * eio(seg(f, TECH_ACC - 1, PAN))
        cy = lerp(618, 690, seg(f, TECH_ACC, PAN))
        bf = (RA_C[0], 618, 2.10 * punch(f - 0.8, TECH, 0.16, 6)) if f < TECH + 3 else None
        img = sharpen(lay(S(t), RA_C[0], cy, s, blur_from=bf), 0.3)
    elif f < SCAN:                  # barrido de cámara entre los dos componentes
        def C(x):
            k = eio(seg(x, PAN - 1, SCAN))
            return lerp(RA_C[0], 1313, k), lerp(690, 650, k), 2.6 + 0.3 * np.sin(np.pi * k)
        cx, cy, s = C(f); p = C(f - 1.0)
        img = sharpen(lay(S(70.62 + (f - PAN) / FPS), cx, cy, s, blur_from=p), 0.2)
    else:                           # comparación por escaneo: enfoscado ↔ capa interior
        s = 2.32 * punch(f, SCAN, 0.04) + 0.12 * seg(f, SCAN, ROLL1)
        brick = sharpen(lay(S(70.98 + (f - SCAN) / FPS), 1313, 650, s), 0.3)
        plain = sharpen(lay(_c['plainR'], 1313, 650, s), 0.3)
        y = lerp(-20, H + 20, eio(seg(f, SCAN, CLICK + 2)))
        img = over(plain, brick, line_mask_y(-1e5, y, 3))
        img = scanline(img, y, 1.0 if f < CLICK + 3 else 0.0)
    img = grain(img, f)
    if f >= TECH: img = scrim(img, 1000, 1660, 0.82 * lerp(0.6, 1, seg(f, TECH, TECH + 3)))
    return block2(img, f)

def scanline(canvas, y, a, color=np.array([1.0, 0.93, 0.78], np.float32)):
    if a <= 0: return canvas
    yy = np.arange(H, dtype=np.float32)[:, None]
    add = (np.clip(1.6 - np.abs(yy - y), 0, 1) + np.exp(-((yy - y) / 22) ** 2) * 0.38 + np.where(yy < y, np.exp(-(y - yy) / 90), 0) * 0.07) * a
    return np.clip(canvas + add[..., None] * color, 0, 1)

# ------------------------------------------------------------------ 263–299 · primeros planos de aplicación
def scene_closeups(f):
    if f < ROLL2:   img = lay(S(130.00 + (f - ROLL1) / FPS), 1150, 540, 1.80 * punch(f, ROLL1, 0.07) + 0.05 * seg(f, ROLL1, ROLL2))
    elif f < TROWEL: img = lay(S(133.00 + (f - ROLL2) / FPS), 1000, 540, 1.80 * punch(f, ROLL2, 0.07) + 0.05 * seg(f, ROLL2, TROWEL))
    else:           img = lay(S(135.40 + (f - TROWEL) / FPS), 1350, 540, 1.86 * punch(f, TROWEL, 0.06) + 0.06 * seg(f, TROWEL, SPR_WIDE))
    return grain(sharpen(img, 0.3), f)

# ------------------------------------------------------------------ 300–362 · proyección: general ↔ macro
def sp_nozzle(f):
    s = 1.82 * punch(f, SPR_NOZ, 0.06) + 0.05 * seg(f, SPR_NOZ, SPR_MIST)
    return sharpen(lay(S(172.20 + (f - SPR_NOZ) / FPS * 0.9), 1920 - 540 / s, 540, s), 0.3)
def sp_mist(f):
    s = 2.36 * punch(f, SPR_MIST, 0.05) + 0.06 * seg(f, SPR_MIST, SPR_OP)      # chorro de niebla (sin rótulos ni caja)
    return sharpen(lay(S(191.48 + (f - SPR_MIST) / FPS), 470 + 30 * seg(f, SPR_MIST, SPR_OP), 410, s), 0.3)
def sp_op(f):
    s = 1.80 * punch(f, SPR_OP, 0.05) + 0.05 * seg(f, SPR_OP, ARCH)
    return sharpen(lay(S(169.60 + (f - SPR_OP) / FPS), 1040, 540, s), 0.3)
def scene_spray(f):
    if f < SPR_NOZ:
        s = 1.80 * punch(f, SPR_WIDE, 0.06) + 0.06 * seg(f, SPR_WIDE, SPR_NOZ)
        img = sharpen(lay(S(186.70 + (f - SPR_WIDE) / FPS), 1180, 540, s), 0.3)
    elif f < SPR_MIST: img = sp_nozzle(f)
    elif f < SPR_OP - 4: img = sp_mist(f)
    elif f >= SPR_OP + 4: img = sp_op(f)
    else:                            # el propio chorro hace de barrido (derecha → izquierda)
        p = eio(seg(f, SPR_OP - 4, SPR_OP + 4)); xw = lerp(W + 160, -160, p)
        a, b = sp_mist(f), sp_op(f)
        a = over(a, cv2.blur(a, (41, 1)), min(1, 2 * p)); b = over(b, cv2.blur(b, (41, 1)), min(1, 2 * (1 - p)))
        img = over(a, b, line_mask_x(xw, 1e5, 150))
        xx = np.arange(W, dtype=np.float32)[None, :]
        img = np.clip(img + (np.exp(-((xx - xw) / 90) ** 2) * 0.55)[..., None] * 0.6, 0, 1)
    return grain(img, f)

# ------------------------------------------------------------------ 363–416 · resultado arquitectónico
def scene_arch(f):
    if f < ARCH2:
        s = 1.80 * punch(f, ARCH, 0.06) + 0.06 * seg(f, ARCH, ARCH2)
        img = lay(SRC.frame(5515 + (f - ARCH)), 600 + 70 * seg(f, ARCH, ARCH2), 540, s)
    else:
        s = 1.86 * punch(f, ARCH2, 0.06) + 0.08 * seg(f, ARCH2, M_FIRE)
        img = lay(S(224.90 + (f - ARCH2) / FPS), 900 - 40 * seg(f, ARCH2, M_FIRE), 540, s)
    return grain(sharpen(img, 0.3), f)

# ------------------------------------------------------------------ 417–441 · micro‑montaje (3 imágenes)
def burst_img(f):
    t = 38.12 + (f - M_BURST) / FPS * 0.8
    s = 2.05 * punch(f, M_BURST, 0.10) - 0.10 * seg(f, M_BURST, END)
    return lay(S(t), 1000, 530, s)
def scene_montage(f):
    if f < M_BUILD:
        s = 2.35 * punch(f, M_FIRE, 0.08) + 0.08 * seg(f, M_FIRE, M_BUILD)    # termografía: calor -> aislamiento
        a, b = lay(SRC.frame(B_IDX), 860, 520, s), lay(_c['after'], 860, 520, s)
        xw = lerp(W + 40, -40, eio(seg(f, M_FIRE + 1, M_BUILD - 1)))
        img = over(a, b, line_mask_x(xw, 1e5, 3))
        xx = np.arange(W, dtype=np.float32)[None, :]
        img = np.clip(img + ((np.clip(1.8 - np.abs(xx - xw), 0, 1) + 0.35 * np.exp(-((xx - xw) / 20) ** 2)))[..., None] * np.array([1.0, 0.95, 0.85], np.float32), 0, 1)
    elif f < M_BURST:  # el edificio pasa de rojo a azul en 8 fotogramas (2x)
        img = lay(S(17.36 + (f - M_BUILD) / FPS * 2.0), 930, 540, 1.85 * punch(f, M_BUILD, 0.08) + 0.05 * seg(f, M_BUILD, M_BURST))
    else:
        img = burst_img(f)
    return grain(sharpen(img, 0.25), f)

# ------------------------------------------------------------------ 442–499 · DIBURAMA
THERMAL = np.array([[0.55, 0.10, 0.75], [0.15, 0.25, 0.95], [0.10, 0.80, 0.35], [0.98, 0.92, 0.10], [0.95, 0.15, 0.10]], np.float32)[:, ::-1]
def thermal_colors(y_line, width=70):
    """columna de color (H,1,3) con la paleta de la propia termografía alrededor de la línea de escaneo"""
    yy = np.arange(H, dtype=np.float32)
    u = np.clip((y_line - yy) / width, 0, 1) * (len(THERMAL) - 1)
    i = np.clip(u.astype(int), 0, len(THERMAL) - 2); fr = (u - i)[:, None]
    col = THERMAL[i] * (1 - fr) + THERMAL[i + 1] * fr
    return col[:, None, :]

def scene_brand(f):
    p = eo(seg(f, BRAND - 1, BRAND + 9))
    base = burst_img(min(f, BRAND - 1))
    base = cv2.GaussianBlur(base, (0, 0), 0.1 + 26 * p)
    img = over(base, tech_bg(f, grid=False), 0.92 * p)
    g = tech_bg(f) - tech_bg(f, grid=False)
    img = np.clip(img + g * 0.7 * seg(f, BRAND + 6, BRAND + 20), 0, 1)
    img = grain(img, f, 0.012)
    # anillo: rima con la lupa y las partículas
    pc = eo(seg(f, BRAND + 2, BRAND + 26))
    if pc > 0:
        yy, xx = np.mgrid[:H, :W].astype(np.float32)
        ang = (np.arctan2(yy - 900, xx - W / 2) + np.pi / 2) % (2 * np.pi)
        d = np.abs(np.sqrt((xx - W / 2) ** 2 + (yy - 900) ** 2) - 470 * lerp(0.94, 1, pc))
        img = np.clip(img + (np.clip(1.2 - d, 0, 1) * (ang <= pc * 2 * np.pi) * 0.16)[..., None], 0, 1)
    # DIBURAMA revelado por la línea de escaneo: al pasar, las letras se leen en la paleta térmica
    d = TXT['dib']; xd = (W - d.w) / 2; yd = 690
    ys = lerp(yd - 20, yd + d.caph + 120, eio(seg(f, BRAND - 1, BRAND + 13)))
    sc = lerp(1.04, 1.0, eo(seg(f, BRAND - 1, BRAND + 12)))
    img = d.draw(img, xd, yd, mask=line_mask_y(-1e5, ys - 110, 4), scale=sc)
    if ys < yd + d.caph + 118:
        img = d.draw(img, xd, yd, mask=line_mask_y(ys - 110, ys, 3), color=thermal_colors(ys, 110), scale=sc)
        img = scanline(img, ys, 1.0)
    # acento fucsia
    rw = 180 * eo(seg(f, BRAND + 6, BRAND + 14))
    if rw > 1:
        m = line_mask_x(W / 2 - rw / 2, W / 2 + rw / 2, 1.5) * line_mask_y(yd + d.caph + 46, yd + d.caph + 52, 1.2)
        img = over(img, np.broadcast_to(FUCHSIA, img.shape), m)
    # LO DIFÍCIL DE EXPLICAR, / LO HACEMOS VISIBLE.
    t1 = TXT['dificil']; y1 = yd + d.caph + 110; p1 = eo(seg(f, 452, 459))
    img = t1.draw(img, (W - t1.w) / 2, y1 + 16 * (1 - p1), opacity=0.86 * p1)
    t2 = TXT['lhv']; dot = TXT['dot']; y2 = y1 + t1.caph + 40; p2 = eo(seg(f, 458, 466))
    if p2 > 0:
        x2 = (W - t2.w - dot.w) / 2; clip = line_mask_y(-1e5, y2 + t2.caph + 6, 2)
        img = t2.draw(img, x2, y2 + 36 * (1 - p2), opacity=p2, mask=clip)
        img = dot.draw(img, x2 + t2.w + 2, y2 + 36 * (1 - p2), opacity=p2, color=FUCHSIA, mask=clip)
    return img

# ------------------------------------------------------------------ router
def render_frame(f):
    setup(); build_text()
    if f < IRIS: return scene_thermal(f)
    if f < PART: return scene_blue(f)
    if f < CMP: return scene_particles(f)
    if f < PLAIN: return scene_compare(f)
    if f < ROLL1: return scene_multi(f)
    if f < SPR_WIDE: return scene_closeups(f)
    if f < ARCH: return scene_spray(f)
    if f < M_FIRE: return scene_arch(f)
    if f < BRAND: return scene_montage(f)
    return scene_brand(f)

# Mapa de planos usados (para la hoja de contactos de selección): (fotograma inicio, fin, tiempo origen, descripción)
SHOTS = [
    (0, 16, "00:56,96", "Termografía macro (impacto)"),
    (17, 41, "00:55,72 + 00:57,0", "Lupa térmica 2.5D sobre la pared real"),
    (42, 66, "00:07,20", "Textura microscópica azul (apertura en iris)"),
    (67, 82, "00:08,16", "Textura azul · macro cristales"),
    (83, 99, "00:36,30", "Recorrido por los tres componentes"),
    (100, 116, "00:38,12", "Destello de transformación (0,6x)"),
    (117, 132, "00:39,40", "Partícula resultante"),
    (133, 186, "00:57,60 / 01:03,60", "Termografía antes / después (cortinilla registrada)"),
    (187, 199, "01:09,32", "Sistema: enfoscado liso"),
    (200, 216, "01:09,36", "La rendija empieza a abrirse (0,32x)"),
    (217, 232, "01:09,58", "GOLPE: apertura de capas + empujón"),
    (233, 241, "01:10,62", "Barrido de cámara entre componentes"),
    (242, 262, "01:09,32 / 01:10,98", "Escaneo enfoscado ↔ ladrillo"),
    (263, 274, "02:10,00", "Rodillo macro"),
    (275, 282, "02:13,00", "Rodillo sobre ladrillo"),
    (283, 299, "02:15,40", "Llana macro"),
    (300, 316, "03:06,70", "Operario proyectando en techo (general)"),
    (317, 332, "02:52,20", "Boquilla y chorro (macro)"),
    (333, 349, "03:11,48", "Chorro de material hacia la superficie (macro)"),
    (350, 362, "02:49,60", "Operario en obra (general)"),
    (363, 399, "03:40,60", "Fachada terminada (aérea)"),
    (400, 416, "03:44,90", "Ventanal iluminado"),
    (417, 424, "00:57,60 / 01:03,60", "Termografía calor → aislamiento (8 fot.)"),
    (425, 432, "00:17,36", "Edificio rojo → azul (2x)"),
    (433, 441, "00:38,12", "Destello"),
    (442, 499, "—", "Cierre DIBURAMA"),
]
