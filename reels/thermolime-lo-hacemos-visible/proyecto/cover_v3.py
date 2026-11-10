# Portada «Ventana a lo invisible» · 1080x1920 · titular y ventana dentro del recorte 1:1 de la cuadrícula (y 420–1500)
import sys, os
import numpy as np, cv2
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from lib import SRC, TextBlock, fit_size, W, H, over, line_mask_x, line_mask_y, eo
import scenes_v3 as V

CLIENT = os.environ.get("CLIENT_NAME", "THERMOLIME")

def main(out):
    V.setup(); V.build_text()
    src = SRC.frame(V.B_IDX)
    img = over(V.bg_clean('graphite'), V.bg_atmos(src, 0, dark=0.45), 0.7)
    img, box = V.place_window(img, V.win_image(src, V.WIN), W / 2, 1000)
    lx, ly = V.to_win(box, V.LENS[0], V.LENS[1]); lr = V.LENS[2] * box[2] / 1920
    img = V.ring(img, lx, ly, lr + 12, a=0.9, width=1.8)
    for k in range(4):
        th = k * np.pi / 2
        img = V.seg_line(img, (lx + (lr + 18) * np.cos(th), ly + (lr + 18) * np.sin(th)), (lx + (lr + 32) * np.cos(th), ly + (lr + 32) * np.sin(th)), a=0.85, w=2)
    img = V.dot(img, lx, ly - lr - 12, 6)
    ys = ly + lr * 0.15; dx = np.sqrt(lr ** 2 - (ys - ly) ** 2)
    img = V.hscan(img, ys, lx - dx, lx + dx, a=0.8)
    s = min(fit_size("¿CÓMO MUESTRAS", 'black', 900, 120), fit_size("LO QUE NO SE VE?", 'black', 900, 120))
    t1, t2 = TextBlock("¿CÓMO MUESTRAS", 'black', s), TextBlock("LO QUE NO SE VE?", 'black', s)
    img = t1.draw(img, (W - t1.w) / 2, 470); img = t2.draw(img, (W - t2.w) / 2, 470 + s * 0.98)
    tag = TextBlock(f"CASO REAL · {CLIENT}", 'semi', 30, tracking=0.24)
    img = tag.draw(img, (W - tag.w) / 2, box[1] + box[3] + 52, color=V.GREY)
    d = TextBlock("DIBURAMA", 'brand', 70, tracking=0.08)
    img = d.draw(img, (W - d.w) / 2, 1585)
    img = over(img, np.broadcast_to(V.FUCHSIA, img.shape), line_mask_x(W / 2 - 50, W / 2 + 50, 1.5) * line_mask_y(1550, 1556, 1.2))
    cv2.imwrite(out, (np.clip(img, 0, 1) * 255 + .5).astype(np.uint8), [cv2.IMWRITE_JPEG_QUALITY, 95])

if __name__ == '__main__': main(sys.argv[1])
