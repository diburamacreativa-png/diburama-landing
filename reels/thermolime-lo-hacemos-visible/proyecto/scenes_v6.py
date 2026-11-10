# DIBURAMA · VISUAL LAB — Thermolime V6 (22 s · 550 fotogramas)
# Sobre la V5 (mismos planos, narrativa y transiciones). Cambios:
#  · Fondos limpios: sin retícula, sin contornos/siluetas, sin marcas de esquina; solo gradientes grafito/petróleo,
#    imagen original muy desenfocada y textura cromática del vídeo, con la luminancia limitada (nunca compite).
#  · Cuadrícula editorial: márgenes de 80 px, ventana principal 920 px (80–1000), secundaria 840 px alineada a la
#    derecha, titulares a x = 80 con 48 px hasta la ventana, identificadores siempre a x = 80 bajo la última ventana.
#  · «LA APLICACIÓN.» y «EL RESULTADO.» como titulares principales.
#  · Cierre de 4,3 s con el logotipo original; mensaje completo y estático desde 18,84 s hasta el último fotograma.
import numpy as np, cv2
from lib import W, H, FPS, SRC, TextBlock, fit_size, over, circle_mask, line_mask_x, line_mask_y, eo, ei, eio, seg, lerp, pulse, WHITE, hexbgr
import scenes_v3 as V
import scenes_v5 as V5
from scenes_v5 import (setup, S, hw, wimg, lerp_rect, thermo_src, part_src, tech_src, DET_C, LENS, FUCHSIA, dot,
                       ring, seg_line, vscan, hscan, to_win, bg_clean, bg_atmos, place_window, tag, label,
                       SEC_IN, PART, BURST, MERGED, CMP, CMP_SCAN, CMP_DONE, CMP_KICK, CMP_OUT, TECH, TECH_RING, TECH_DROP,
                       TECH_TAG, APP, SWAP, MIST, RES, RES_SEC, CLX0, CLX_PUSH, CLX_B, CLX_C, CLX_D, CLX_CONV, CLX_FOLD, BRAND,
                       B_IDX, AF_IDX, PLAIN_IDX, FIELD, MULTI_FULL, ROLL_REF, HOUSE, c_thermo, c_part, c_multi, c_roll)
from scenes_v5 import _xm, _c

END = 550
ML, MR = 80, 1000                 # márgenes laterales
GW, GS = 920, 840                 # ventana principal · secundaria
TY = 236                          # línea de mayúsculas de los titulares
WT2 = 455                         # arranque de ventana bajo titular de dos líneas (≈ 48 px de aire)
WT1 = 350                         # arranque de ventana bajo titular de una línea (≈ 50 px de aire)
SEC_Y = 1009                      # ventana secundaria (36 px bajo la principal de 455)
ID_GAP = 30                       # identificador: 30 px bajo la última ventana
LCY = 826                         # eje del logotipo en el cierre

# ------------------------------------------------------------------ fondos limpios
def bg6(f, src, kind='graphite', amt=0.55, dark=0.40, accent=None, acc_amt=0.16):
    """gradiente grafito/petróleo + imagen original muy desenfocada + textura cromática; sin líneas ni siluetas.
    La luminancia se comprime por encima de 0,24 para que el fondo nunca forme manchas claras."""
    img = over(bg_clean(kind, grid=0.0, f=f), bg_atmos(src, f, dark=dark, sat=0.72, zoom=1.2), amt)
    if accent is not None:
        acc = bg_atmos(SRC.frame(accent), f + 90, dark=0.5, sat=1.1, zoom=1.7, drift=(-20 * np.sin(f / 80), 14 * np.cos(f / 95)))
        img = 1 - (1 - img) * (1 - acc_amt * acc)
    lum = img.mean(2, keepdims=True); knee = 0.24
    comp = np.where(lum > knee, knee + (lum - knee) * 0.35, lum)
    return img * (comp / np.maximum(lum, 1e-4))

def put6(canvas, win, x0, y0, alpha=1.0, clip=None, frame=True):
    """ventana sin marcas de esquina (solo sombra suave y filo de 1 px)"""
    h, w = win.shape[:2]
    return place_window(canvas, win, x0 + w / 2, y0 + h / 2, alpha=alpha, frame=frame, ticks=0.0, clip=clip)

# ------------------------------------------------------------------ titulares
T = {}
def build_text():
    if T: return
    V5.build_text()
    s = min(fit_size("¿CÓMO MUESTRAS", 'black', 900, 100), fit_size("LO QUE NO SE VE?", 'black', 900, 100)); T['s1'] = s
    T['q1'], T['q2'] = TextBlock("¿CÓMO MUESTRAS", 'black', s), TextBlock("LO QUE NO SE VE?", 'black', s)
    s = min(fit_size("LA TECNOLOGÍA,", 'black', 900, 100), fit_size("AL DESCUBIERTO.", 'black', 900, 100)); T['s2'] = s
    T['t1'], T['t2'], T['dot2'] = TextBlock("LA TECNOLOGÍA,", 'black', s), TextBlock("AL DESCUBIERTO", 'black', s), TextBlock(".", 'black', s)
    s = min(fit_size("LA APLICACIÓN.", 'black', 860, 88), 88); T['s3'] = s       # titulares de escena (una línea)
    T['app'], T['res'], T['dot3'] = TextBlock("LA APLICACIÓN", 'black', s), TextBlock("EL RESULTADO", 'black', s), TextBlock(".", 'black', s)

# ================================================================== 0–82 · LO QUE NO SE VE
def s_open(f):
    src = thermo_src(f)
    img = bg6(f, src, 'graphite', accent=FIELD)
    w = int(GW * (1 + 0.04 * (1 - eo(seg(f, -1, 6))))) // 2 * 2
    x, y = 540 - w / 2 - 6 * seg(f, 0, PART), lerp(540, WT2, eo(seg(f, SEC_IN - 1, SEC_IN + 8)))
    img, box = put6(img, wimg(src, w), x, y)
    lx, ly = to_win(box, LENS[0], LENS[1]); lr = LENS[2] * box[2] / 1920
    pr = eo(seg(f, 2, 16))                                       # lente de exploración
    img = ring(img, lx, ly, lr + 12, a=0.85, prog=pr)
    img = dot(img, lx + (lr + 12) * np.cos(-np.pi / 2 + pr * 2 * np.pi), ly + (lr + 12) * np.sin(-np.pi / 2 + pr * 2 * np.pi), 5, a=eo(seg(f, 2, 5)))
    if 14 <= f <= 36:
        ys = lerp(ly - lr, ly + lr, eio(seg(f, 14, 34))); dx = np.sqrt(max(0, lr ** 2 - (ys - ly) ** 2))
        img = hscan(img, ys, lx - dx, lx + dx, a=0.8 * (1 - seg(f, 32, 36)))
    if f >= SEC_IN - 1:                                          # microestructura, revelada por el escáner
        sx, sy, sw = MR - GS + 6 * seg(f, SEC_IN, PART), SEC_Y, GS
        u = eio(seg(f, SEC_IN - 1, SEC_IN + 7)); xr = sx + sw * u
        img, sb = put6(img, wimg(S(7.20 + max(0, f - SEC_IN) / FPS), sw), sx, sy, clip=line_mask_x(-1e5, xr, 3))
        if u < 1: img = vscan(img, xr, sy - 30, sy + hw(sw) + 30)
        rx, ry = to_win(sb, 1180, 560)                           # círculo que une la lente con la estructura
        pl = eo(seg(f, SEC_IN + 4, SEC_IN + 14)); p0, p1 = (lx, ly + lr + 12), (rx, ry - 48)
        img = seg_line(img, p0, p1, a=0.75, w=1.6, prog=pl)
        if pl > 0: img = dot(img, *p0, 5)
        img = ring(img, rx, ry, 48, a=0.85, prog=eo(seg(f, SEC_IN + 10, SEC_IN + 20)), width=1.8)
        img = tag(img, f, SEC_IN + 6, "01", "LO INVISIBLE", ML, SEC_Y + hw(GS) + ID_GAP, a_out=1 - seg(f, 76, 82))
    img = V.title_lines(img, f, [(T['q1'], -1, 0, None), (T['q2'], SEC_IN, T['s1'] * 0.98, None)], TY, f_out=78)
    return img

# ================================================================== 83–132 · DENTRO DEL MATERIAL
def s_material(f):
    src = part_src(f)
    img = bg6(f, src, 'graphite', dark=0.36, accent=B_IDX, acc_amt=0.14)
    k = eo(seg(f, PART - 1, PART + 9)); sw = int(lerp(GS, 720, k)) // 2 * 2
    sx, sy = MR - sw + 6 * seg(f, PART, CMP), lerp(SEC_Y, 1040, k)
    img, sb = put6(img, wimg(S(6.60 + (f - PART) / FPS * 0.6), sw, crop=(1250, 600, 1300), gain=0.85), sx, sy)
    x, y, kw = 540 - GW / 2 - 6 - 4 * seg(f, PART, CMP), WT2, GW / 1920
    win = wimg(src, GW)
    if f < PART + 8:                                             # el círculo de la lente se abre a la partícula
        old = wimg(thermo_src(PART - 1), GW)
        kk = 1 - (1 - seg(f, PART - 1, PART + 7)) ** 2.4
        yy, xx = np.mgrid[:win.shape[0], :win.shape[1]].astype(np.float32)
        m = np.clip(lerp(LENS[2] * kw + 6, 1100, kk) - np.sqrt((xx - LENS[0] * kw) ** 2 + (yy - LENS[1] * kw) ** 2) + 0.5, 0, 1)[..., None]
        win = old * (1 - m) + win * m
    img, box = put6(img, win, x, y)
    if f >= BURST:                                               # la esfera atraviesa los límites de la ventana
        if f < MERGED: pc, pr, sc_ = (1000.0, 530.0), 330.0, lerp(1.0, 1.75, eo(seg(f, BURST - 1, BURST + 7)))
        else: pc, pr, sc_ = (760.0, 525.0), 345.0, 1.55 * (1 + 0.06 * (1 - eo(seg(f, MERGED - 1, MERGED + 5)))) + sum(pulse(f, q, 0.04, 2.5) for q in (121, 125, 129))
        px, py = to_win(box, *pc); s_abs = box[2] / 1920 * sc_
        M = np.float32([[s_abs, 0, px - s_abs * pc[0]], [0, s_abs, py - s_abs * pc[1]]])
        lay = cv2.warpAffine(src, M, (W, H), flags=cv2.INTER_AREA).astype(np.float32) / 255
        mm = circle_mask(px, py, pr * s_abs, 1.5)
        img = img * (1 - V.drop_shadow(mm, 0, 24, 30, 0.55)[..., None]); img = over(img, lay, mm)
        img = ring(img, px, py, pr * s_abs + 8, a=0.6, width=1.4)
    img = tag(img, f, PART + 4, "02", "EL MATERIAL", ML, sb[1] + sb[3] + ID_GAP, a_out=1 - seg(f, CMP - 5, CMP))
    return img

# ================================================================== 133–216 · ANTES / DESPUÉS
UP, LO = (ML, 340, GW), (ML, 930, GW)
def s_compare(f):
    img = bg6(f, SRC.frame(B_IDX), 'graphite', amt=0.45, accent=FIELD, acc_amt=0.12)
    ein = eo(seg(f, CMP - 1, CMP + 6)); out = ei(seg(f, CMP_OUT, TECH))
    ux, lx_ = UP[0] - 140 * (1 - ein), LO[0] + 140 * (1 - ein)
    uy, ly_ = UP[1] - 760 * out, LO[1] + 760 * out
    u = eio(seg(f, CMP_SCAN - 1, CMP_DONE)) if f >= CMP_SCAN - 1 else 0.0
    wins = []
    for (plain, th) in [(_c['plainB'], SRC.frame(B_IDX)), (_c['plainC'], SRC.frame(AF_IDX))]:
        a, b = wimg(plain, GW), wimg(th, GW)
        wins.append(over(a, b, 1 - _xm(a, u)) if u > 0 else a)
    img, bu = put6(img, wins[0], ux, uy, alpha=ein)
    img, bl = put6(img, wins[1], lx_, ly_, alpha=ein)
    if CMP_SCAN - 1 <= f <= CMP_DONE + 1:                         # un único escáner recorre ambas ventanas
        xs = UP[0] + GW * u
        img = vscan(img, xs, uy - 24, ly_ + hw(GW) + 24); img = dot(img, xs, uy - 24, 5); img = dot(img, xs, ly_ + hw(GW) + 24, 5)
    pr = eo(seg(f, CMP_DONE + 2, CMP_DONE + 12)) * (1 - out)
    if pr > 0:
        (ax, ay), (cx, cy) = to_win(bu, LENS[0], LENS[1]), to_win(bl, LENS[0], LENS[1]); rk = (LENS[2] * GW / 1920 + 14) * (1 + 0.08 * pulse(f, CMP_KICK, 1.0, 3))
        img = ring(img, ax, ay, rk, a=0.85, prog=pr, width=1.8); img = ring(img, cx, cy, rk, a=0.85, prog=pr, width=1.8, start=np.pi / 2)
        pl = eo(seg(f, CMP_DONE + 8, CMP_DONE + 18)) * (1 - out)
        img = seg_line(img, (ax, ay + rk), (cx, cy - rk), a=0.8, w=1.8, prog=pl)
        if pl > 0: img = dot(img, ax, ay + rk, 5); img = dot(img, cx, cy - rk, 5, a=seg(f, CMP_DONE + 17, CMP_DONE + 19))
    a_l = 1 - seg(f, CMP_OUT, CMP_OUT + 3)
    img = label(img, f, CMP + 4, "ANTES", ML, uy - 36, a_out=a_l)
    img = label(img, f, CMP + 8, "DESPUÉS", ML, ly_ - 36, a_out=a_l, color=WHITE)
    if f >= CMP_OUT:
        g = eio(seg(f, CMP_OUT, TECH)); img = hscan(img, (UP[1] + hw(GW) + LO[1]) / 2, W / 2 - 500 * g, W / 2 + 500 * g, a=g)
    return img

# ================================================================== 217–299 · LA TECNOLOGÍA, AL DESCUBIERTO
def det_cw(f): return lerp(940, 860, eio(seg(f, TECH_DROP, APP)))         # recorte ≥ 840 px: detalle nativo
def s_tech(f):
    src = tech_src(f)
    img = bg6(f, src, 'petrol', amt=0.3, accent=B_IDX, acc_amt=0.12)
    w = int(GW * (1 + 0.05 * (1 - eo(seg(f, TECH - 1, TECH + 6))))) // 2 * 2
    x, y = 540 - w / 2, WT2 + (hw(GW) - hw(w)) / 2 - 6 * seg(f, TECH, APP)
    if f < TECH + 8:
        uu = lerp(1.04, -0.04, eio(seg(f, TECH - 1, TECH + 7)))
        wp, wo = wimg(SRC.frame(PLAIN_IDX), w), wimg(S(70.40), w)
        img, box = put6(img, over(wp, wo, _xm(wp, uu)), x, y)
        img = vscan(img, box[0] + uu * box[2], box[1] - 60, box[1] + box[3] + 60)
    else:
        img, box = put6(img, wimg(src, w), x, y)
    ax, ay = to_win(box, 323, 745); ra = 330 * box[2] / 1920
    img = ring(img, ax, ay, ra, a=0.85, prog=eo(seg(f, TECH_RING - 1, TECH_RING + 9)), width=1.8)
    yb = SEC_Y; pd = eio(seg(f, TECH_RING + 3, TECH_DROP))
    if pd > 0:
        img = seg_line(img, (ax, ay + ra), (ax, lerp(ay + ra, yb + 60, pd)), a=0.85, w=1.8); img = dot(img, ax, ay + ra, 5)
    if f >= TECH_DROP - 1:
        cw = det_cw(f); dsrc = SRC.frame(1800); sx = MR - GS + 6 * seg(f, TECH_DROP, APP)
        yr = lerp(yb, yb + hw(GS) + 2, eio(seg(f, TECH_DROP - 1, TECH_DROP + 7)))
        img, lb = put6(img, wimg(dsrc, GS, crop=(DET_C[0], DET_C[1], cw)), sx, yb, clip=line_mask_y(-1e5, yr, 3))
        if yr < yb + hw(GS): img = hscan(img, yr, sx - 20, sx + GS + 20)
        s_ = GS / cw; cxs = min(max(DET_C[0], cw / 2), 1920 - cw / 2); cys = min(max(DET_C[1], cw * 9 / 32), 1080 - cw * 9 / 32)
        dx, dy = lb[0] + GS / 2 + (323 - cxs) * s_, lb[1] + hw(GS) / 2 + (745 - cys) * s_
        img = ring(img, dx, dy, 165 * s_, a=0.85, prog=eo(seg(f, TECH_DROP + 6, TECH_DROP + 16)), width=1.8, start=np.pi / 2)
        img = dot(img, ax, yb + 60, 5 * (1 + 0.5 * pulse(f, TECH_TAG, 1.0, 2)), a=seg(f, TECH_DROP, TECH_DROP + 2))
    img = tag(img, f, TECH_TAG, "03", "LA TECNOLOGÍA", ML, SEC_Y + hw(GS) + ID_GAP, a_out=1 - seg(f, APP - 5, APP))
    s = T['s2']
    img = V.title_lines(img, f, [(T['t1'], TECH, 0, None), (T['t2'], TECH + 4, s * 0.98, (T['dot2'],))], TY, f_out=APP - 5)
    return img

# ================================================================== 300–366 · LA APLICACIÓN (titular principal)
R0, S0 = (ML, WT1, GW), (MR - 760, 940, 760)         # rodillo dominante · spray secundario
R1, S1 = (ML, WT1, 760), (ML, 850, GW)               # 13,35 s: el spray pasa a dominante
def s_app(f):
    rsrc = S(131.00 + (f - APP) / FPS) if f < SWAP else S(134.20 + (f - SWAP) / FPS * 0.7)
    ssrc = S(191.40 + (f - APP) / FPS)
    img = bg6(f, ssrc if f >= SWAP else rsrc, 'graphite', amt=0.5, accent=ROLL_REF, acc_amt=0.12)
    k = eio(seg(f, SWAP - 1, SWAP + 8))
    (rx, ry, rw), (sx, sy, sw) = lerp_rect(R0, R1, k), lerp_rect(S0, S1, k)
    ein = eo(seg(f, APP + 3, APP + 10)); sx += 70 * (1 - ein)
    order = [('s', sx, sy, sw), ('r', rx, ry, rw)] if f < SWAP + 4 else [('r', rx, ry, rw), ('s', sx, sy, sw)]
    boxes = {}
    for nm, x, y, w in order:
        img, boxes[nm] = put6(img, wimg(rsrc if nm == 'r' else ssrc, w), x, y, alpha=(1.0 if nm == 'r' else ein))
    br, bs = boxes['r'], boxes['s']; a_o = 1 - seg(f, MIST - 2, MIST + 2)
    img = label(img, f, APP + 4, "APLICACIÓN REAL", br[0], br[1] + br[3] + 16, a_out=a_o)          # cartelas bajo su ventana
    img = label(img, f, APP + 9, "DETALLE DEL PROCESO", bs[0], bs[1] + bs[3] + 16, a_out=a_o, color=WHITE)
    img = V.title_lines(img, f, [(T['app'], APP, 0, (T['dot3'],))], TY, f_out=MIST)
    return img

def s_app_to_res(f):     # la niebla del spray barre la composición hacia el resultado (brillo contenido)
    a, b = s_app(f), s_result(f)
    p = eio(seg(f, MIST, RES)); xw = lerp(-220, W + 220, p)
    img = over(b, a, line_mask_x(xw, 1e5, 200))
    xx = np.arange(W, dtype=np.float32)[None, :]
    return np.clip(img + (np.exp(-((xx - xw) / 120) ** 2) * 0.22)[..., None] * V.SCAN, 0, 1)

# ================================================================== 367–399 · EL RESULTADO (titular principal)
def s_result(f):
    hsrc = SRC.frame(HOUSE + max(0, f - RES))
    img = bg6(f, hsrc, 'graphite', amt=0.5, accent=FIELD, acc_amt=0.10)
    img, box = put6(img, wimg(hsrc, GW), ML, WT1 - 8 * seg(f, RES, CLX0))
    if f >= RES_SEC - 1:     # detalle del proceso: menor y a la derecha, no compite con el edificio
        k = eo(seg(f, RES_SEC - 1, RES_SEC + 8)); sw = 720
        img, sb = put6(img, wimg(S(135.40 + (f - RES_SEC) / FPS), sw), MR - sw + 60 * (1 - k), 912, alpha=k)
        img = label(img, f, RES_SEC + 4, "DETALLE DEL PROCESO", sb[0], sb[1] + sb[3] + 16)
    img = V.title_lines(img, f, [(T['res'], RES - 1, 0, (T['dot3'],))], TY)
    return img

# ================================================================== 400–441 · CLÍMAX (cuadrícula de 920 px; expansiones de 960 en los golpes)
A_KEYS = [(CLX0, (ML, 700, GW)), (CLX_PUSH, (60, 689, 960)), (CLX_B, (ML, 380, GW)), (CLX_C, (60, 368, 960)),
          (CLX_D, (120, 392, 840)), (CLX_CONV, (120, LCY - 4 - hw(840), 840))]
B_KEYS = [(CLX0, (ML, 1930, GW)), (CLX_B, (ML, 938, GW)), (CLX_C, (120, 950, 840)),
          (CLX_D, (60, 926, 960)), (CLX_CONV, (120, LCY + 4, 840))]
def key_rect(keys, f):
    r = keys[0][1]
    for i, (c, rr) in enumerate(keys[1:], 1):
        if f >= c - 1: r = lerp_rect(keys[i - 1][1], rr, eo(seg(f, c - 1, c + 3)))
    return r

def fold_k(f): return 1 - eio(seg(f, CLX_FOLD, BRAND + 2))

def s_climax(f):
    big = c_multi(f) if f >= CLX_C else c_thermo(f)
    hit = min(1.0, sum(pulse(f, c, 1.0, 4.0) for c in (CLX0, CLX_PUSH, CLX_B, CLX_C, CLX_D, CLX_CONV)))
    img = bg6(f, big, 'graphite', amt=0.5, accent=(FIELD if f >= CLX_B else B_IDX), acc_amt=0.14 + 0.22 * hit)
    ra, rb = key_rect(A_KEYS, f), key_rect(B_KEYS, f); k = fold_k(f)
    for name, (x, y, w) in (('B', rb), ('A', ra)):
        w = int(w) // 2 * 2; h0 = hw(w)
        if name == 'A':
            a, b = wimg(c_thermo(f), w), wimg(c_multi(f), w); u = eio(seg(f, CLX_C - 1, CLX_C + 4))
            win = over(a, b, 1 - _xm(a, u)) if u > 0 else a
        else:
            a, b = wimg(c_part(f), w), wimg(c_roll(f), w); u = eio(seg(f, CLX_D - 1, CLX_D + 4))
            win = over(a, b, _xm(a, 1 - u)) if u > 0 else a
        if k < 1:
            h = max(2, int(h0 * k)); win = cv2.resize(win, (w, h), interpolation=cv2.INTER_AREA)
            y = (y + h0 - h) if name == 'A' else y
        img, box = put6(img, win, x, y, frame=k > 0.25)
        cue = CLX_C if name == 'A' else CLX_D; uu = eio(seg(f, cue - 1, cue + 4))
        if 0 < uu < 1: img = vscan(img, box[0] + box[2] * (uu if name == 'A' else 1 - uu), box[1] - 26, box[1] + box[3] + 26)
    pl = eio(seg(f, CLX_CONV + 1, CLX_FOLD + 1))
    if pl > 0:                                                   # la línea fucsia une las ventanas: eje del logotipo
        half = 420 * pl
        img = over(img, np.broadcast_to(FUCHSIA, img.shape), line_mask_x(W / 2 - half, W / 2 + half, 1.5) * line_mask_y(LCY - 1.5, LCY + 1.5, 1.0))
        img = dot(img, W / 2 - half, LCY, 4.5); img = dot(img, W / 2 + half, LCY, 4.5)
    return img

# ================================================================== 442–549 · CIERRE (logotipo original + eslogan, 4,3 s)
LOGO_W = 880; LOGO_H = 406 * LOGO_W / 1065
_BG = {}
def brand_bg(f):
    if 'g' not in _BG:
        y = np.linspace(0, 1, H, dtype=np.float32)[:, None, None]
        g = (hexbgr('#101A23') * (1 - y) + hexbgr('#0D1219') * y) * np.ones((1, W, 1), np.float32)
        yy, xx = np.mgrid[:H, :W].astype(np.float32)
        vig = 1 - 0.30 * np.clip(((xx - W / 2) / (W * 0.85)) ** 2 + ((yy - LCY) / (H * 0.6)) ** 2, 0, 1.4)
        _BG['g'] = np.clip(g * vig[..., None], 0, 1)
        fx, fy = W / 2 - LOGO_W / 2 + 208 * LOGO_W / 1065, LCY - LOGO_H / 2 + 85 * LOGO_W / 1065
        _BG['glow'] = np.exp(-(((xx - fx) / 320) ** 2 + ((yy - fy) / 280) ** 2))[..., None].astype(np.float32) * 0.09
        # textura cromática de la termografía, muy oscura y estática (profundidad sin formas)
        haze = bg_atmos(SRC.frame(B_IDX), 0, dark=0.35, sat=0.9, zoom=1.9)
        _BG['haze'] = haze
    img = _BG['g'].copy()
    img = 1 - (1 - img) * (1 - _BG['haze'] * lerp(0.16, 0.07, eo(seg(f, BRAND, 470))))
    return np.clip(img + _BG['glow'] * FUCHSIA, 0, 1)

ST = {}
def brand_text():
    if ST: return
    ST['l1'] = TextBlock("LO DIFÍCIL DE EXPLICAR,", 'semi', fit_size("LO DIFÍCIL DE EXPLICAR,", 'semi', 640, 46), tracking=0.03)
    s2 = fit_size("LO HACEMOS VISIBLE.", 'black', 840, 84)
    ST['l2'], ST['dot'] = TextBlock("LO HACEMOS VISIBLE", 'black', s2), TextBlock(".", 'black', s2)

def s_brand(f):
    brand_text()
    img = brand_bg(f)
    if f < BRAND + 3:                                            # las ventanas terminan de plegarse en la línea
        img = over(img, s_climax(f), 1 - eio(seg(f, BRAND - 1, BRAND + 3)))
    sc = LOGO_W / 1065 * (1 + 0.04 * (1 - eo(seg(f, BRAND - 1, BRAND + 9))))      # 104 % → 100 % en 0,4 s
    hh = (406 * sc / 2 + 12) * eio(seg(f, BRAND - 1, BRAND + 6))
    img, _ = V5.put_logo(img, sc, W / 2, LCY, mask=line_mask_y(LCY - hh, LCY + hh, 3))
    a_edge = 1 - seg(f, BRAND + 4, BRAND + 8)
    if a_edge > 0:
        for yy_ in (LCY - hh, LCY + hh):
            img = over(img, np.broadcast_to(FUCHSIA, img.shape), line_mask_x(W / 2 - 420, W / 2 + 420, 1.5) * line_mask_y(yy_ - 1.2, yy_ + 1.2, 1.0) * a_edge)
    l1, l2, dt = ST['l1'], ST['l2'], ST['dot']
    y1 = LCY + LOGO_H / 2 + 56; y2 = y1 + l1.caph + 22
    p1, p2 = eo(seg(f, 455, 466)), eo(seg(f, 459, 471))         # 18,2–18,84 s; después, todo estático
    if p1 > 0: img = l1.draw(img, (W - l1.w) / 2, y1 + 12 * (1 - p1), color=np.array([0.90, 0.91, 0.93], np.float32), opacity=p1)
    if p2 > 0:
        x2 = (W - l2.w - dt.w) / 2; clip = line_mask_y(-1e5, y2 + l2.caph + 8, 2)
        img = l2.draw(img, x2, y2 + 18 * (1 - p2), opacity=p2, mask=clip)
        img = dt.draw(img, x2 + l2.w + 2, y2 + 18 * (1 - p2), opacity=p2, mask=clip, color=FUCHSIA)
    return img

# ================================================================== router
def render_frame(f):
    setup(); build_text()
    if f < PART: return s_open(f)
    if f < CMP: return s_material(f)
    if f < TECH: return s_compare(f)
    if f < APP: return s_tech(f)
    if f < MIST: return s_app(f)
    if f < RES: return s_app_to_res(f)
    if f < CLX0: return s_result(f)
    if f < BRAND: return s_climax(f)
    return s_brand(f)

CLIPS = [c for c in V5.CLIPS if c[0] < 442] + [(442, 549, "—", "Logotipo oficial (PNG original)", "—", "Revelación desde la línea fucsia; eslogan estático desde 18,84 s")]
