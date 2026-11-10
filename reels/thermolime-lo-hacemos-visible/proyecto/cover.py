# Portada vertical 1080x1920 · «¿CÓMO MUESTRAS LO QUE NO SE VE?» · CASO REAL · THERMOLIME · Diburama
# El titular y la lupa quedan dentro del cuadrado central (y 420–1500) para el recorte de la cuadrícula.
import sys, os
import numpy as np, cv2
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from lib import *
import scenes as S

CLIENT = os.environ.get("CLIENT_NAME", "THERMOLIME")   # el producto del vídeo se llama «thermolime»

def main(out):
    S.setup()
    A = SRC.frame(S.A_IDX); B = SRC.frame(S.B_IDX); Bn = S._cache['Bn']; ax_, ay_ = S._cache['lensA']
    LYc, sl = 760, 0.80
    bg = src_layer_c(A, ax_, ay_, 2.0, LYc)
    bg = cv2.GaussianBlur(bg, (0, 0), 3.0) * 0.62
    th = src_layer_c(B, *S.LENS_C, sl, LYc); no = src_layer_c(Bn, *S.LENS_C, sl, LYc)
    inner = circle_mask(W / 2, LYc, S.LENS_RI * sl, 1.5); outer = circle_mask(W / 2, LYc, S.LENS_RO * sl, 1.5)
    ys = LYc - S.LENS_RI * sl * 0.45                       # línea de escaneo: arriba pared «normal», abajo lo invisible
    lens = over(th, over(no, th, line_mask_y(ys, 1e5, 4)), circle_mask(W / 2, LYc, (S.LENS_RI + 3.5) * sl, 1.2))
    sh = drop_shadow(outer, 0, 30, 40, 0.65)
    img = bg * (1 - sh[..., None]); img = over(img, sharpen(lens, 0.3), outer)
    # línea de escaneo limitada a la lupa (+ leve extensión)
    yy = np.arange(H, dtype=np.float32)[:, None]; xx = np.arange(W, dtype=np.float32)[None, :]
    span = np.clip(1 - np.abs(xx - W / 2) / (S.LENS_RO * sl + 120), 0, 1) ** 0.6
    core = np.clip(1.6 - np.abs(yy - ys), 0, 1) + np.exp(-((yy - ys) / 18) ** 2) * 0.35
    img = np.clip(img + (core * span)[..., None] * np.array([1.0, 0.93, 0.78], np.float32), 0, 1)
    img = over(img, np.broadcast_to(NAVY_D, img.shape), vgrad(1000, 1500, 0, 0.85))
    img = over(img, np.broadcast_to(NAVY_D, img.shape), vgrad(0, 420, 0.7, 0))
    img = grain(img, 1, 0.012)
    # titular
    l1, l2 = "¿CÓMO MUESTRAS", "LO QUE NO SE VE?"
    s = min(fit_size(l1, 'black', 940, 120), fit_size(l2, 'black', 940, 120))
    t1, t2 = TextBlock(l1, 'black', s), TextBlock(l2, 'black', s)
    y1 = 1135; y2 = y1 + s * 0.727 + s * 0.26
    img = t1.draw(img, (W - t1.w) / 2, y1, shadow=0.4)
    img = t2.draw(img, (W - t2.w) / 2, y2, shadow=0.4)
    tag = TextBlock(f"CASO REAL · {CLIENT}", 'semi', 34, tracking=0.24)
    yt = y2 + s * 0.727 + 62
    img = tag.draw(img, (W - tag.w) / 2, yt, opacity=0.85)
    # marca
    d = TextBlock("DIBURAMA", 'brand', 64, tracking=0.08)
    img = d.draw(img, (W - d.w) / 2, 1610)
    m = line_mask_x(W / 2 - 50, W / 2 + 50, 1.5) * line_mask_y(1580, 1585, 1.2)
    img = over(img, np.broadcast_to(FUCHSIA, img.shape), m)
    out8 = (np.clip(img, 0, 1) * 255 + .5).astype(np.uint8)
    cv2.imwrite(out, out8, [cv2.IMWRITE_JPEG_QUALITY, 95])

def src_layer_c(img, cx, cy, s, ay):
    return f32(warp(img, cam_M(cx, cy, s, W / 2, ay)))

if __name__ == '__main__': main(sys.argv[1])
