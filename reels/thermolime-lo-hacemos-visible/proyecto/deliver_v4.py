# V4 · portada, hoja de contactos, relación de clips y comparación objetiva con la V3
# uso: python3 deliver_v4.py portada  out.jpg
#      python3 deliver_v4.py hoja     final_v4.mp4 out_dir
#      python3 deliver_v4.py comparar v3.mp4 v4.mp4 out_dir
import sys, os, json, subprocess
import numpy as np, cv2
from PIL import Image, ImageDraw, ImageFont
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from lib import FONTS, W, H, TextBlock, over, line_mask_x, line_mask_y
import scenes_v4 as V4
import scenes_v3 as V3

CLIENT = os.environ.get("CLIENT_NAME", "THERMOLIME")

def portada(out):
    """composición del arranque (dos ventanas + lente conectada) con firma y caso real"""
    V4.setup(); V4.build_text()
    full = V4.render_frame(66)
    # la composición (titular + dos ventanas) se reduce un 7 % y baja para caber en el recorte 3:4 de la cuadrícula (y 240–1680)
    comp = full[200:1560]; sc = 0.93
    comp = cv2.resize(comp, (int(W * sc), int(comp.shape[0] * sc)), interpolation=cv2.INTER_AREA)
    img = V4.bg(66, V4.thermo_src(66), 'graphite', amt=0.6)        # el mismo fondo de la escena, sin texto: sin costuras
    x0, y0 = (W - comp.shape[1]) // 2, 285
    hh, ww = comp.shape[:2]
    fx = np.clip(np.minimum(np.arange(ww), ww - 1 - np.arange(ww)) / 60, 0, 1)[None, :]
    fy = np.clip(np.minimum(np.arange(hh), hh - 1 - np.arange(hh)) / 60, 0, 1)[:, None]
    fade = (fx * fy)[..., None]
    img[y0:y0 + comp.shape[0], x0:x0 + comp.shape[1]] = img[y0:y0 + comp.shape[0], x0:x0 + comp.shape[1]] * (1 - fade) + comp * fade
    tag = TextBlock(f"CASO REAL · {CLIENT}", 'semi', 28, tracking=0.24)
    img = tag.draw(img, (W - tag.w) / 2, 1572, color=V3.GREY)
    d = TextBlock("DIBURAMA", 'brand', 60, tracking=0.08)
    img = d.draw(img, (W - d.w) / 2, 1630)
    img = over(img, np.broadcast_to(V3.FUCHSIA, img.shape), line_mask_x(W / 2 - 45, W / 2 + 45, 1.5) * line_mask_y(1612, 1617, 1.2))
    cv2.imwrite(out, (np.clip(img, 0, 1) * 255 + .5).astype(np.uint8), [cv2.IMWRITE_JPEG_QUALITY, 95])

def frame_at(mp4, n, w, h):
    raw = subprocess.run(["ffmpeg", "-v", "error", "-i", mp4, "-vf", f"select=eq(n\\,{n}),scale={w}:{h}:flags=area", "-frames:v", "1",
                          "-f", "rawvideo", "-pix_fmt", "rgb24", "-"], capture_output=True, check=True).stdout
    return np.frombuffer(raw, np.uint8).reshape(h, w, 3)

def font(sz, n='InterDisplay-SemiBold.otf'): return ImageFont.truetype(os.path.join(FONTS, n), sz)

TIMES = [0.0, 1.2, 2.4, 3.6, 4.2, 5.2, 6.4, 7.6, 8.69, 9.9, 11.0, 12.4, 13.8, 14.5, 15.6, 16.5, 17.1, 17.5, 18.4, 19.96]
def hoja(mp4, od):
    cols, tw, th, pad = 5, 300, 533, 16; rows = (len(TIMES) + cols - 1) // cols; ch = th + 88
    sheet = Image.new('RGB', (cols * (tw + pad) + pad, rows * ch + 120), (16, 20, 25)); d = ImageDraw.Draw(sheet)
    d.text((pad, 24), "DIBURAMA · VISUAL LAB V4 — hoja de contactos", font=font(36, 'InterDisplay-Bold.otf'), fill=(255, 255, 255))
    d.text((pad, 72), "Tiempo del Reel · ventanas en pantalla y su origen en el vídeo Thermolime", font=font(21), fill=(170, 176, 186))
    for k, t in enumerate(TIMES):
        n = min(499, int(round(t * 25))); r, c = divmod(k, cols); x = pad + c * (tw + pad); y = 120 + r * ch
        sheet.paste(Image.fromarray(frame_at(mp4, n, tw, th)), (x, y))
        rows_ = [cl for cl in V4.CLIPS if cl[0] <= n <= cl[1]]
        d.text((x, y + th + 8), f"{t:05.2f} s · f{n}".replace('.', ','), font=font(21, 'InterDisplay-Bold.otf'), fill=(214, 75, 150))
        for i, cl in enumerate(rows_[:2]):
            d.text((x, y + th + 36 + i * 22), f"{cl[2]}: {cl[4]}"[:38], font=font(15), fill=(200, 204, 212))
    sheet.save(os.path.join(od, "DIBURAMA_THERMOLINE_VISUAL_LAB_V4_HOJA_CONTACTOS.jpg"), quality=90)
    with open(os.path.join(od, "CLIPS_Y_TIEMPOS_DE_ORIGEN_V4.md"), "w") as fh:
        fh.write("| Reel (s) | Ventana | Clip | Tiempo en el original | Uso |\n|---|---|---|---|---|\n")
        for f0, f1, win, clip, src, use in V4.CLIPS:
            fh.write(f"| {f0/25:.2f}–{(f1+1)/25:.2f} | {win} | {clip} | {src} | {use} |\n".replace('.', ',', 2))

def gray(mp4, w, h):
    raw = subprocess.run(["ffmpeg", "-v", "error", "-i", mp4, "-vf", f"scale={w}:{h}:flags=area", "-f", "rawvideo", "-pix_fmt", "gray", "-"],
                         capture_output=True, check=True).stdout
    return np.frombuffer(raw, np.uint8).reshape(-1, h, w).astype(np.float32)

def comparar(v3, v4, od):
    out = {}
    for name, mp4 in [('V3', v3), ('V4', v4)]:
        g = gray(mp4, 540, 960)
        # % del lienzo con imagen nítida: bloques 12×12 con energía de Laplaciano alta (el fondo desenfocado no cuenta)
        occ = []
        for fr in g[::5]:
            lap = np.abs(cv2.Laplacian(fr, cv2.CV_32F, ksize=3))
            blk = cv2.resize(lap, (45, 80), interpolation=cv2.INTER_AREA)
            occ.append(float((blk > 6.0).mean()))
        small = gray(mp4, 108, 192); d = np.abs(np.diff(small, axis=0)).mean((1, 2))
        out[name] = dict(lienzo_con_imagen_nitida_pct=round(100 * np.mean(occ), 1),
                         movimiento_medio=round(float(d.mean()), 2),
                         fotogramas_casi_estaticos_pct=round(100 * float((d < 1.0).mean()), 1))
    json.dump(out, open(os.path.join(od, "comparacion_v3_v4.json"), "w"), indent=1, ensure_ascii=False)
    print(json.dumps(out, indent=1, ensure_ascii=False))
    # tira comparativa en los mismos instantes
    idx = list(range(0, 500, 25)); a = [frame_at(v3, i, 162, 288) for i in idx]; b = [frame_at(v4, i, 162, 288) for i in idx]
    gap = np.full((288, 4, 3), 16, np.uint8)
    row = lambda fs: np.hstack(sum([[x, gap] for x in fs], [])[:-1])
    im = Image.fromarray(np.vstack([np.full((40, row(a).shape[1], 3), 16, np.uint8), row(a), np.full((40, row(a).shape[1], 3), 16, np.uint8), row(b)]))
    dd = ImageDraw.Draw(im)
    dd.text((8, 8), "V3 — Ventana a lo invisible (un fotograma por segundo)", font=font(24, 'InterDisplay-Bold.otf'), fill=(255, 255, 255))
    dd.text((8, 40 + 288 + 8), "V4 — Visual Lab multiventana (mismos instantes)", font=font(24, 'InterDisplay-Bold.otf'), fill=(214, 75, 150))
    half = im.width // 2
    outim = Image.new('RGB', (half + 2, im.height * 2 + 12), (16, 20, 25))
    outim.paste(im.crop((0, 0, half + 2, im.height)), (0, 0)); outim.paste(im.crop((half - 2, 0, im.width, im.height)), (0, im.height + 12))
    outim.save(os.path.join(od, "DIBURAMA_THERMOLINE_COMPARACION_V3_V4.jpg"), quality=88)

if __name__ == '__main__':
    cmd = sys.argv[1]
    if cmd == 'portada': portada(sys.argv[2])
    elif cmd == 'hoja': hoja(*sys.argv[2:4])
    elif cmd == 'comparar': comparar(*sys.argv[2:5])
