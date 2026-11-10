# DIBURAMA · THERMOLIME · "LO HACEMOS VISIBLE" — escenas
# Línea de tiempo en fotogramas (25 fps). Los cortes caen en el fotograma que contiene el transitorio
# real de la música (MP3 recortado 40 ms de relleno de codificador, ver audio.py).
import numpy as np, cv2
from lib import *

# ------------------------------------------------------------------ cues (fotogramas)
HOOK, PROB, SCAN_END, DIVE, MICRO = 0, 42, 67, 83, 100
TENS, P1, P2, P3, PRE, TECH = 150, 163, 175, 188, 200, 217        # 6.02 / 6.52 / 7.02 / 7.52 / 8.02 / 8.68
TECH2, TECH3, APP, CLARO, NOZ, RES = 233, 250, 300, 333, 350, 367   # 9.35 / 10.02 / 12.02 / 13.35 / 14.02 / 14.69
MONT = [400, 417, 425, 433]; BRAND, LAST, END = 442, 483, 500     # 16.02 … 17.69 / 19.355 / 20.00

LY = 760          # centro vertical del "objeto circular" (lupa térmica / partículas) en lienzo
TX = 80           # margen izquierdo de la tipografía (zona segura Instagram)

# ------------------------------------------------------------------ fuentes del original (índices de fotograma)
A_IDX, B_IDX = 1393, 1440      # 55.72 s pared sin lupa · 57.60 s lupa termográfica estable
FIELD_IDX = 812                # 32.48 s campo de partículas sin rótulos
LENS_C, LENS_RI, LENS_RO = (883.0, 493.0), 360.0, 405.0           # lupa en coordenadas de B
_cache = {}

def setup():
    """registro geométrico pared normal (A) ↔ lectura termográfica (B), calculado del propio material"""
    if 'Bn' in _cache: return
    A = SRC.frame(A_IDX); B = SRC.frame(B_IDX)
    ga, gb = cv2.cvtColor(A, cv2.COLOR_BGR2GRAY), cv2.cvtColor(B, cv2.COLOR_BGR2GRAY)
    mask = np.full(gb.shape, 255, np.uint8)
    cv2.circle(mask, (883, 495), 420, 0, -1); cv2.rectangle(mask, (1080, 140), (1720, 310), 0, -1)
    orb = cv2.ORB_create(6000)
    ka, da = orb.detectAndCompute(ga, None); kb, db = orb.detectAndCompute(gb, mask)
    m = cv2.BFMatcher(cv2.NORM_HAMMING, crossCheck=True).match(db, da)
    pb = np.float32([kb[x.queryIdx].pt for x in m]); pa = np.float32([ka[x.trainIdx].pt for x in m])
    M, _ = cv2.estimateAffinePartial2D(pb, pa, ransacReprojThreshold=2.0)
    _cache['M_ba'] = M
    _cache['Bn'] = cv2.warpAffine(A, M, (1920, 1080), flags=cv2.INTER_CUBIC | cv2.WARP_INVERSE_MAP)
    c = M @ np.array([LENS_C[0], LENS_C[1], 1.0]); _cache['lensA'] = (float(c[0]), float(c[1]))
    # preparar fuentes
    for i0, n in [(838, 52), (980, 70), (1734, 68), (4238, 34), (4302, 48), (5515, 36),
                  (1025, 10), (1873, 12), (5450, 25)]:
        SRC.load(i0, n)

# ------------------------------------------------------------------ textos (pre-maquetados)
def T(txt, name, size, **kw): return TextBlock(txt, name, size, **kw)

S1 = fit_size("MUESTRAS", 'black', 860, 178)
TXT = {}
def build_text():
    if TXT: return
    TXT['como'] = T("¿CÓMO", 'black', S1); TXT['muestras'] = T("MUESTRAS", 'black', S1)
    TXT['loque'] = T("LO QUE", 'black', S1); TXT['nosevee'] = T("NO SE VE?", 'black', fit_size("NO SE VE?", 'black', 860, S1))
    s3 = fit_size("PUDIERAS…", 'light', 860, 150, 0.01)
    TXT['s3'] = s3; TXT['y'] = T("¿Y", 'light', s3, tracking=0.01); TXT['si'] = T("SI", 'light', s3, tracking=0.01)
    TXT['pud'] = T("PUDIERAS…", 'light', s3, tracking=0.01)
    TXT['s4'] = fit_size("MOSTRARLO?", 'black', 820, 190)
    TXT['hacemos'] = T("HACEMOS", 'semi', 56, tracking=0.22)
    sv = fit_size("VISIBLE", 'black', 860, 150); TXT['visible'] = T("VISIBLE", 'black', sv)
    TXT['su'] = T("SU", 'semi', 56, tracking=0.22); TXT['tecno'] = T("TECNOLOGÍA", 'black', fit_size("TECNOLOGÍA", 'black', 760, 116))
    s6a = fit_size("DE LO COMPLEJO…", 'black', 860, 104, 0.025)
    TXT['complejo'] = T("DE LO COMPLEJO…", 'black', s6a, outline=True, stroke=4, tracking=0.025)
    s6b = fit_size("…A LO CLARO.", 'black', 860, 132); TXT['claro'] = T("…A LO CLARO.", 'black', s6b)
    s7 = fit_size("ENTIENDE.", 'bold', 860, 150); TXT['ahora'] = T("AHORA SE", 'bold', s7); TXT['entiende'] = T("ENTIENDE.", 'bold', s7)
    TXT['s7'] = s7
    TXT['diburama'] = T("DIBURAMA", 'brand', 124, tracking=0.08)
    TXT['dificil'] = T("LO DIFÍCIL DE EXPLICAR,", 'semi', fit_size("LO DIFÍCIL DE EXPLICAR,", 'semi', 780, 58))
    sh = fit_size("LO HACEMOS", 'black', 800, 136)
    TXT['lohacemos'] = T("LO HACEMOS", 'black', sh); TXT['visible2'] = T("VISIBLE", 'black', sh); TXT['sh'] = sh
    TXT['dot'] = T(".", 'black', sh)
    TXT['que'] = T("¿Qué necesitas explicar?", 'medium', 50)

def lines_y(top, size, gap=0.24):
    return top, top + size * 0.727 + size * gap

# ------------------------------------------------------------------ utilidades de escena
def src_layer(img, cx, cy, s, ax=W / 2, ay=H / 2, blur_from=None, n=11):
    """capa de vídeo encuadrada; blur_from=(cx0,cy0,s0) activa desenfoque de movimiento entre ambas cámaras"""
    if blur_from is None: return f32(warp(img, cam_M(cx, cy, s, ax, ay)))
    cx0, cy0, s0 = blur_from
    Ms = [cam_M(lerp(cx0, cx, k / (n - 1)), lerp(cy0, cy, k / (n - 1)), lerp(s0, s, k / (n - 1)), ax, ay) for k in range(n)]
    return warp_blur(img, Ms)

def scanline(canvas, y, a, color=np.array([1.0, 0.93, 0.78], np.float32)):
    if a <= 0: return canvas
    yy = np.arange(H, dtype=np.float32)[:, None]
    core = np.clip(1.6 - np.abs(yy - y), 0, 1)
    glow = np.exp(-((yy - y) / 22) ** 2) * 0.38
    trail = np.where(yy < y, np.exp(-(y - yy) / 90), 0) * 0.07
    add = (core + glow + trail) * a
    return np.clip(canvas + add[..., None] * color, 0, 1)

def card(canvas, img, rect, M, border=0.28, shadow=0.55):
    """panel flotante 2.5D con la imagen real recortada a 'rect' (x0,y0,x1,y1 en fuente)"""
    x0, y0, x1, y1 = rect
    m = np.zeros((1080, 1920), np.float32); m[y0:y1, x0:x1] = 1
    mk = cv2.warpAffine(m, M, (W, H), flags=cv2.INTER_LINEAR)
    lay = f32(cv2.warpAffine(img, M, (W, H), flags=cv2.INTER_LANCZOS4, borderMode=cv2.BORDER_REFLECT))
    lay = sharpen(lay, 0.3)
    sh = drop_shadow(mk, 0, 28, 38, shadow)
    canvas = canvas * (1 - sh[..., None])
    canvas = over(canvas, lay, mk)
    # filo de luz
    e = cv2.morphologyEx(mk, cv2.MORPH_GRADIENT, np.ones((3, 3), np.uint8)) * 0.5
    return np.clip(canvas + e[..., None] * border, 0, 1)

def pt(M, x, y): return M @ np.array([x, y, 1.0], np.float32)

def hline(canvas, p0, p1, prog, a=0.9, w=2.0, color=WHITE):
    if prog <= 0: return canvas
    q = p0 + (p1 - p0) * prog
    m = np.zeros((H, W), np.float32)
    cv2.line(m, (int(p0[0] * 4), int(p0[1] * 4)), (int(q[0] * 4), int(q[1] * 4)), 1.0, int(w * 4), cv2.LINE_AA, shift=2)
    return over(canvas, np.broadcast_to(color, canvas.shape), m * a)

def node(canvas, p, r, color, a=1.0):
    m = circle_mask(p[0], p[1], r, 1.5) * a
    return over(canvas, np.broadcast_to(color, canvas.shape), m)

# ================================================================== ESCENA 1+2 · lupa termográfica (0–99)
def lens_params(f):
    if f < PROB:
        sb = 2.0 + 0.10 * eo(f / 28)
        sl = 1.03 + 0.07 * eo(f / 8) + 0.02 * f / 41
    else:
        sb = 2.10 + 0.07 * seg(f, PROB, DIVE)
        sl = 1.12 + 0.03 * seg(f, PROB, DIVE) - 0.03 * np.exp(-(f - PROB) / 3)
        if f > DIVE:
            k = seg(f, DIVE, MICRO) ** 3
            sl83 = 1.15; sb83 = 2.17
            sl = sl83 * (1 + 0.62 * k); sb = sb83 * (1 + 0.38 * k)
    return sb, sl

def scene_lens(f):
    setup()
    A = SRC.frame(A_IDX); B = SRC.frame(B_IDX); Bn = _cache['Bn']; ax_, ay_ = _cache['lensA']
    sb, sl = lens_params(f)
    nb = 5 if f >= 90 else 1
    prev = lens_params(f - 0.8) if nb > 1 else None
    # fondo: pared real sin lupa, ligeramente desenfocada (profundidad)
    bg = src_layer(A, ax_, ay_, sb, W / 2, LY, blur_from=(ax_, ay_, prev[0]) if prev else None)
    bg = cv2.GaussianBlur(bg, (0, 0), 2.2) * 0.80
    # lupa
    th = src_layer(B, LENS_C[0], LENS_C[1], sl, W / 2, LY, blur_from=(LENS_C[0], LENS_C[1], prev[1]) if prev else None)
    if PROB <= f < SCAN_END + 1 or (f >= PROB and f < SCAN_END):
        pass
    inner = circle_mask(W / 2, LY, LENS_RI * sl, 1.5); outer = circle_mask(W / 2, LY, LENS_RO * sl, 1.5)
    lens = th
    if f >= PROB:
        y = scan_y(f)
        if y < LY + LENS_RI * sl + 5:
            no = src_layer(Bn, LENS_C[0], LENS_C[1], sl, W / 2, LY)
            rev = line_mask_y(-1e5, y, 6)
            lens = over(no, th, rev)
            lens = over(th, lens, circle_mask(W / 2, LY, (LENS_RI + 3.5) * sl, 1.2))  # anillo siempre del original
    sh = drop_shadow(outer, 0, 34, 42, 0.6)
    img = bg * (1 - sh[..., None])
    img = over(img, sharpen(lens, 0.3), outer)
    img = grain(img, f)
    img = over(img, np.broadcast_to(NAVY_D, img.shape), vgrad(1080, 1660, 0, 0.72) * (1 - eo(seg(f, DIVE, DIVE + 8))))
    # tipografía
    if f < PROB:
        c1, c2 = lines_y(1262, S1)
        for k, (t, cy) in enumerate([(TXT['como'], c1), (TXT['muestras'], c2)]):
            p = eo(seg(f, k * 2, k * 2 + 7))
            img = t.draw(img, TX, cy + 26 * (1 - p), opacity=1.0, shadow=0.35)
    else:
        y = scan_y(f)
        c1, c2 = lines_y(1262, S1)
        out = eo(seg(f, DIVE, DIVE + 7))
        m = line_mask_y(-1e5, y, 10)
        for t, cy in [(TXT['loque'], c1), (TXT['nosevee'], c2)]:
            img = t.draw(img, TX, cy + 70 * out, opacity=1 - out, shadow=0.35, mask=m, blur=6 * out)
        a = seg(f, PROB, PROB + 2) * (1 - seg(f, SCAN_END - 1, SCAN_END + 4))
        img = scanline(img, y, a)
    return img

def scan_y(f):
    return lerp(LY - LENS_RO * 1.1 - 20, 1600, eio(seg(f, PROB + 1, SCAN_END)))

# ================================================================== ESCENA 3 · inmersión microscópica (100–149)
CRY_C, CRY_R, CRY_MASK = (1402.0, 348.0), 240.0, 345.0
def cry_scale(f):
    s0 = LENS_RO * 0.95 * lens_params(MICRO - 1)[1] / CRY_R      # anillo ↔ anillo en el corte
    return 1.55 + (s0 - 1.55) * (1 - eo(seg(f, MICRO, MICRO + 13))) + 0.14 * seg(f, MICRO, TENS)

def field_bg(f, s, cx=960, cy=540, dim=0.8, blur=2.0):
    fl = SRC.frame(FIELD_IDX)
    b = src_layer(fl, cx, cy, s)
    return cv2.GaussianBlur(b, (0, 0), blur) * dim

def scene_micro(f):
    setup()
    sbf = 1.9 + 0.5 * eo(seg(f, MICRO, 140))
    bg = field_bg(f, sbf)
    fr = SRC.frame(838 + (f - MICRO))
    s = cry_scale(f)
    blur_from = (CRY_C[0], CRY_C[1], cry_scale(f - 0.8)) if f < MICRO + 4 else None
    fg = src_layer(fr, CRY_C[0], CRY_C[1], s, W / 2, LY, blur_from=blur_from)
    m = circle_mask(W / 2, LY, CRY_MASK * s, 30 * s / 1.55)
    img = over(bg, sharpen(fg, 0.25), m)
    img = grain(img, f)
    # ¿Y SI / PUDIERAS… — palabra a palabra sobre las semicorcheas
    s3 = TXT['s3']; c1, c2 = lines_y(1300, s3, 0.30)
    xs = TX + text_width("¿Y ", 'light', s3, 0.01)
    for t, x, cy, t0 in [(TXT['y'], TX, c1, 105), (TXT['si'], xs, c1, 113), (TXT['pud'], TX, c2, 121)]:
        p = eo(seg(f, t0, t0 + 7))
        if p > 0: img = t.draw(img, x, cy + 16 * (1 - p), opacity=p, blur=7 * (1 - p), shadow=0.3)
    return img

# ================================================================== ESCENA 4 · tensión (150–216)
PAR_C, PAR_R = (760.0, 525.0), 352.0
def par_params(f):
    s = lerp(1.12, 1.40, eio(seg(f, TENS, PRE)))
    s += pulse(f, P1, 0.035) + pulse(f, P2, 0.04) + pulse(f, P3, 0.045) + pulse(f, PRE, 0.08, 4.5)
    k = seg(f, PRE + 1, TECH) ** 2.4
    s *= 1 + 6.0 * k
    cx = lerp(PAR_C[0], 805, k); cy = lerp(PAR_C[1], 560, k)
    return cx, cy, s

def scene_tension(f):
    setup()
    k = seg(f, PRE + 1, TECH) ** 2.4
    bg = field_bg(f, 2.0 + 0.25 * seg(f, TENS, PRE) + 2.0 * k, dim=0.75)
    fr = SRC.frame(980 + (f - TENS))
    cx, cy, s = par_params(f)
    bf = par_params(f - 0.8)[2] if f >= 205 else None
    fg = src_layer(fr, cx, cy, s, W / 2, LY, blur_from=(par_params(f - 0.8)[0], par_params(f - 0.8)[1], bf) if bf else None)
    img = grain(bg, f)
    # MOSTRARLO? por detrás de la partícula (capas 2.5D)
    s4 = TXT['s4']; p = eo(seg(f, TENS - 1, TENS + 8))
    tr = round(0.10 * (1 - p), 3)
    t = T("MOSTRARLO?", 'black', s4, tracking=tr) if tr > 0 else TXT.setdefault('mostrarlo', T("MOSTRARLO?", 'black', s4))
    beat = 1 + 0.4 * (pulse(f, P1, 0.035) + pulse(f, P2, 0.04) + pulse(f, P3, 0.045) + pulse(f, PRE, 0.05))
    x = (W - t.w) / 2
    img = t.draw(img, x, 1335, opacity=p, shadow=0.3, scale=beat)
    pm = circle_mask(W / 2 + (PAR_C[0] - cx) * s, LY + (PAR_C[1] - cy) * s, PAR_R * s, 2.0)
    sh = drop_shadow(pm, 0, 30, 40, 0.5)
    img = img * (1 - sh[..., None])
    img = over(img, sharpen(fg, 0.25), pm)
    img = ring_draw(img, W / 2 + (PAR_C[0] - cx) * s, LY + (PAR_C[1] - cy) * s, (PAR_R + 5) * s, 2.0, WHITE, 0.35 * (1 - k))
    img = img * lerp(1, 0.62, seg(f, 208, TECH))
    return img

# ================================================================== ESCENA 5 · revelación tecnológica (217–299)
RA = (64, 157, 583, 1080)         # panel izquierdo: esquina con ventana de ladrillo (sistema multicapa)
RB = (1050, 360, 1580, 1080)      # panel derecho: segunda vista del sistema
BRICK_A, BRICK_B = (323.0, 745.0), (1313.0, 740.0)
def tech_M(f):
    ca = ((RA[0] + RA[2]) / 2, (RA[1] + RA[3]) / 2); cb = ((RB[0] + RB[2]) / 2, (RB[1] + RB[3]) / 2)
    s1 = 2.081 + 0.09 * (1 - eo(seg(f, TECH, TECH + 7))) + 0.05 * seg(f, TECH + 7, TECH2)
    p = eo(seg(f, TECH2, TECH2 + 15))
    drift = seg(f, TECH3, APP)
    sA = lerp(s1, 0.92, p) * (1 + 0.025 * drift)
    axA = lerp(W / 2, 290, p); ayA = lerp(H / 2, 640, p) - 16 * drift
    MA = cam_M(ca[0], ca[1], sA, axA, ayA)
    pb = eo(seg(f, TECH2 + 3, TECH3))
    sB = 0.92 * (1 + 0.03 * drift)
    MB = cam_M(cb[0], cb[1], sB, lerp(1180, 800, pb), 905 - 34 * drift)
    return MA, MB, p, pb

def scene_tech(f):
    setup()
    fr = SRC.frame(1734 + (f - TECH))
    MA, MB, p, pb = tech_M(f)
    img = tech_bg(f)
    img = card(img, fr, RA, MA, border=0.28 * p, shadow=0.55 * p)
    if pb > 0:
        tmp = card(img.copy(), fr, RB, MB)
        img = over(img, tmp, pb)
        # línea gráfica que conecta ambas visualizaciones
        a0 = pt(MA, *BRICK_A); b0 = pt(MB, *BRICK_B)
        prog = eo(seg(f, TECH2 + 9, TECH3 + 1))
        img = hline(img, a0, b0, prog, 0.9, 2.0)
        if prog > 0: img = node(img, a0, 7, FUCHSIA)
        if f >= TECH3: img = node(img, b0, 7 * (1 + 0.5 * pulse(f, TECH3, 1.0, 2)), FUCHSIA)
    img = grain(img, f, 0.014)
    # velo inferior para la tipografía
    img = over(img, np.broadcast_to(NAVY_D, img.shape), vgrad(1050, 1650, 0, 0.78))
    # HACEMOS (secundaria) / VISIBLE (principal, revelado por luz) / SU TECNOLOGÍA
    ph = eo(seg(f, TECH - 1, TECH + 6))
    up = 70 * eo(seg(f, TECH3 - 1, TECH3 + 6))
    img = TXT['hacemos'].draw(img, TX + 3 - 40 * (1 - ph), 1260 - up, opacity=ph, shadow=0.3)
    v = TXT['visible']; pv = eo(seg(f, TECH - 1, TECH + 9))
    xr = TX + (v.w + 30) * pv
    img = v.draw(img, TX, 1322 - up, mask=line_mask_x(-1e5, xr, 24), shadow=0.35)
    if 0 < pv < 0.999:   # borde de luz que revela la palabra (sólo dentro de las letras + halo suave)
        xx = np.arange(W, dtype=np.float32)[None, :]
        band = np.repeat(np.exp(-((xx - xr) / 60) ** 2), H, 0)
        img = v.draw(img, TX, 1322 - up, color=np.array([1.0, 0.97, 0.9], np.float32), opacity=0.9, mask=band, blur=10)
    ps = eo(seg(f, TECH3 - 1, TECH3 + 6))
    if ps > 0:
        cy = 1322 - 70 + v.caph + 36
        tc = TXT['tecno']
        img = TXT['su'].draw(img, TX + 3, cy + 24 * (1 - ps), opacity=0.8 * ps, shadow=0.3)
        img = tc.draw(img, TX, cy + TXT['su'].caph + 22 + 30 * (1 - ps), opacity=ps, shadow=0.35,
                      mask=line_mask_y(-1e5, cy + TXT['su'].caph + 22 + tc.caph + 8, 2))
    return img

# ================================================================== ESCENA 6 · aplicación real (300–366)
def closeup(f):  # 02:52 primer plano boquilla + chorro (ralentí 0.86x con mezcla de fotogramas)
    t = 172.15 + (f - APP) / FPS * 0.86
    fr = SRC.at(t)
    s = 1.82 + 0.07 * (1 - eo(seg(f, APP, APP + 5))) + 0.05 * seg(f, APP, NOZ)
    return sharpen(src_layer(fr, 1920 - 540 / s, 540, s), 0.3)

def operator(f):  # 02:49 operario proyectando sobre fachada en obra (encuadre sin rótulos)
    fr = SRC.at(169.60 + (f - NOZ) / FPS)
    s = 1.80 + 0.06 * (1 - eo(seg(f, NOZ, NOZ + 5))) + 0.04 * seg(f, NOZ, RES)
    return sharpen(src_layer(fr, 1040, 540, s), 0.3)

def scene_app(f):
    setup()
    if f < NOZ - 4:
        img = closeup(f)
    elif f >= NOZ + 4:
        img = operator(f)
    else:  # barrido con el propio chorro (derecha → izquierda, dirección del aerosol)
        p = eio(seg(f, NOZ - 4, NOZ + 4))
        xw = lerp(W + 160, -160, p)
        a = cv2.blur(closeup(f), (41, 1)); b = cv2.blur(operator(f), (41, 1))
        a = over(closeup(f), a, min(1, 2 * p)); b = over(operator(f), b, min(1, 2 * (1 - p)))
        mk = line_mask_x(xw, 1e5, 150)
        img = over(a, b, mk)
        xx = np.arange(W, dtype=np.float32)[None, :]
        mist = np.exp(-((xx - xw) / 90) ** 2) * (0.55 + 0.2 * GRAIN[f % 6][:, :] * 0.5)
        img = np.clip(img + mist[..., None] * 0.6, 0, 1)
    img = grain(img, f)
    img = over(img, np.broadcast_to(NAVY_D, img.shape), vgrad(0, 860, 0.80, 0))
    # DE LO COMPLEJO… (contorno) → …A LO CLARO. (macizo)
    c = TXT['complejo']; k = TXT['claro']
    out = eo(seg(f, RES - 6, RES))
    y1 = 330 - 40 * out
    pr = eo(seg(f, APP - 1, APP + 8))
    dim = lerp(1, 0.55, eo(seg(f, CLARO - 1, CLARO + 4)))
    img = c.draw(img, TX, y1, mask=line_mask_x(-1e5, TX + (c.w + 40) * pr, 30), opacity=dim * (1 - out), shadow=0.45)
    pk = eo(seg(f, CLARO - 1, CLARO + 4))
    if pk > 0:
        img = k.draw(img, TX, y1 + c.caph + 46, opacity=pk * (1 - out), scale=lerp(1.07, 1, pk), shadow=0.45)
    return img

# ================================================================== ESCENA 7 · resultado (367–399)
def scene_result(f):
    setup()
    fr = SRC.frame(5515 + (f - RES))
    s = 1.80 + 0.05 * (1 - eo(seg(f, RES, RES + 5))) + 0.05 * seg(f, RES, MONT[0])
    cx = 636 + 26 * seg(f, RES, MONT[0])
    img = sharpen(src_layer(fr, cx, 540, s), 0.3)
    img = grain(img, f)
    img = over(img, np.broadcast_to(NAVY_D, img.shape), vgrad(80, 760, 0.78, 0))
    s7 = TXT['s7']; c1, c2 = lines_y(300, s7, 0.2)
    p = eo(seg(f, RES + 2, RES + 10))
    img = TXT['ahora'].draw(img, TX, c1 + 24 * (1 - p), opacity=p, shadow=0.35)
    p2 = eo(seg(f, RES + 5, RES + 13))
    img = TXT['entiende'].draw(img, TX, c2 + 24 * (1 - p2), opacity=p2, shadow=0.35)
    return img

# ================================================================== ESCENA 8 · micro‑montaje (400–441)
def montage_img(f):
    if f < MONT[1]:
        s = 2.42 * (1 + 0.07 * (1 - eo(seg(f, MONT[0], MONT[0] + 4)))) - 0.06 * seg(f, MONT[0], MONT[1])
        return src_layer(SRC.frame(B_IDX), LENS_C[0], LENS_C[1], s)
    if f < MONT[2]:
        s = 2.64 * (1 + 0.07 * (1 - eo(seg(f, MONT[1], MONT[1] + 3)))) + 0.10 * seg(f, MONT[1], MONT[2])
        return src_layer(SRC.frame(1027 + f - MONT[1]), 730, 525, s)
    if f < MONT[3]:
        s = 2.68 * (1 + 0.07 * (1 - eo(seg(f, MONT[2], MONT[2] + 3)))) + 0.08 * seg(f, MONT[2], MONT[3])
        return src_layer(SRC.frame(1875 + f - MONT[2]), 1313, 720, s)
    s = 1.92 * (1 + 0.06 * (1 - eo(seg(f, MONT[3], MONT[3] + 3)))) + 0.03 * seg(f, MONT[3], BRAND)
    return src_layer(SRC.frame(5450 + min(f, BRAND) - MONT[3]), 614, 575, s)

def scene_montage(f):
    setup()
    img = sharpen(montage_img(f), 0.3)
    return grain(img, f)

# ================================================================== ESCENA 9 · DIBURAMA (442–499)
def scene_brand(f):
    setup()
    p = eo(seg(f, BRAND - 1, BRAND + 9))
    fr = SRC.at((5450 + (BRAND - MONT[3])) / FPS + (f - BRAND) / FPS * 0.5)
    s = 1.95 + 0.10 * seg(f, BRAND, END)
    base = src_layer(fr, 614, 575, s)
    base = cv2.GaussianBlur(base, (0, 0), 0.1 + 24 * p)
    img = over(base, tech_bg(f, grid=False), 0.93 * p)
    # retícula técnica que aparece tras el oscurecido
    g = tech_bg(f) - tech_bg(f, grid=False)
    img = np.clip(img + g * 0.8 * seg(f, BRAND + 6, BRAND + 20), 0, 1)
    img = grain(img, f, 0.012)
    # círculo: rima visual con la lupa térmica y la partícula
    pc = eo(seg(f, BRAND + 2, BRAND + 26))
    if pc > 0:
        yy, xx = np.mgrid[:H, :W].astype(np.float32)
        ang = (np.arctan2(yy - 960, xx - W / 2) + np.pi / 2) % (2 * np.pi)
        arc = (ang <= pc * 2 * np.pi).astype(np.float32)
        d = np.abs(np.sqrt((xx - W / 2) ** 2 + (yy - 960) ** 2) - 470 * lerp(0.94, 1, pc))
        m = np.clip(1.2 - d, 0, 1) * arc * 0.16
        img = np.clip(img + m[..., None], 0, 1)
    # composición tipográfica
    d = TXT['diburama']
    pd = eo(seg(f, BRAND - 1, BRAND + 6))
    xd = (W - d.w) / 2
    img = d.draw(img, xd, 600, opacity=pd, scale=lerp(1.05, 1, pd))
    if 0 < seg(f, BRAND - 1, BRAND + 8) < 1:      # destello de luz que recorre la marca (sólo en las letras)
        xr = lerp(xd - 80, xd + d.w + 80, eio(seg(f, BRAND - 1, BRAND + 8)))
        xx = np.arange(W, dtype=np.float32)[None, :]
        band = np.repeat(np.exp(-((xx - xr) / 50) ** 2), H, 0)
        img = d.draw(img, xd, 600, opacity=0.8 * pd, scale=lerp(1.05, 1, pd), blur=8, mask=band)
    # acento fucsia
    pr = eo(seg(f, BRAND + 4, BRAND + 12))
    rw = 150 * pr + 40 * eo(seg(f, LAST, LAST + 8))
    if rw > 1:
        m = line_mask_x(W / 2 - rw / 2, W / 2 + rw / 2, 1.5) * line_mask_y(744, 750, 1.2)
        img = over(img, np.broadcast_to(FUCHSIA, img.shape), m)
    # LO DIFÍCIL DE EXPLICAR, / LO HACEMOS / VISIBLE.
    t1 = TXT['dificil']; p1 = eo(seg(f, 451, 458))
    img = t1.draw(img, (W - t1.w) / 2, 830 + 18 * (1 - p1), opacity=0.86 * p1)
    sh = TXT['sh']; y2 = 830 + t1.caph + 44
    for k, (t, y, t0) in enumerate([(TXT['lohacemos'], y2, 456), (TXT['visible2'], y2 + sh * 0.727 + sh * 0.22, 460)]):
        pp = eo(seg(f, t0, t0 + 7))
        if pp <= 0: continue
        tw = t.w + (TXT['dot'].w if k == 1 else 0)
        x = (W - tw) / 2
        clip = line_mask_y(-1e5, y + sh * 0.727 + 6, 2)
        img = t.draw(img, x, y + 40 * (1 - pp), opacity=pp, mask=clip)
        if k == 1:
            img = TXT['dot'].draw(img, x + t.w + 2, y + 40 * (1 - pp), opacity=pp, color=FUCHSIA, mask=clip)
    q = TXT['que']; pq = eo(seg(f, 474, 482))
    if pq > 0:
        img = q.draw(img, (W - q.w) / 2, 1290 + 12 * (1 - pq), opacity=0.78 * pq)
    return img

# ================================================================== router
def render_frame(f):
    build_text()
    if f < MICRO: return scene_lens(f)
    if f < TENS: return scene_micro(f)
    if f < TECH: return scene_tension(f)
    if f < APP: return scene_tech(f)
    if f < RES: return scene_app(f)
    if f < MONT[0]: return scene_result(f)
    if f < BRAND: return scene_montage(f)
    return scene_brand(f)
