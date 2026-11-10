# V5 · hoja de contactos (incluye 12 · 14 · 16 · 16,5 · 17 · 17,5 · 17,8 · 18,5 · 19,5 s), relación de clips y comparación V4/V5
# uso: python3 deliver_v5.py hoja     final_v5.mp4 out_dir
#      python3 deliver_v5.py comparar v4.mp4 v5.mp4 out_dir
import sys, os, json, subprocess
import numpy as np, cv2
from PIL import Image, ImageDraw
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import scenes_v5 as V5
from deliver_v4 import frame_at, font, gray

TIMES = [0.0, 1.0, 2.4, 3.6, 4.2, 6.4, 7.6, 8.69, 10.4, 12.0, 13.0, 14.0, 15.4, 16.0, 16.2, 16.5, 17.0, 17.3, 17.5, 17.8, 18.0, 18.5, 19.0, 19.5, 19.96]

def hoja(mp4, od):
    cols, tw, th, pad = 5, 300, 533, 16; rows = (len(TIMES) + cols - 1) // cols; ch = th + 88
    sheet = Image.new('RGB', (cols * (tw + pad) + pad, rows * ch + 120), (13, 18, 25)); d = ImageDraw.Draw(sheet)
    d.text((pad, 24), "DIBURAMA · VISUAL LAB V5 — hoja de contactos", font=font(36, 'InterDisplay-Bold.otf'), fill=(255, 255, 255))
    d.text((pad, 72), "Tiempo del Reel · ventanas en pantalla y su origen en el vídeo Thermolime", font=font(21), fill=(170, 176, 186))
    for k, t in enumerate(TIMES):
        n = min(499, int(round(t * 25))); r, c = divmod(k, cols); x = pad + c * (tw + pad); y = 120 + r * ch
        sheet.paste(Image.fromarray(frame_at(mp4, n, tw, th)), (x, y))
        rows_ = [cl for cl in V5.CLIPS if cl[0] <= n <= cl[1]]
        d.text((x, y + th + 8), f"{t:05.2f} s · f{n}".replace('.', ','), font=font(21, 'InterDisplay-Bold.otf'), fill=(229, 14, 119))
        for i, cl in enumerate(rows_[:2]):
            d.text((x, y + th + 36 + i * 22), f"{cl[2]}: {cl[4]}"[:38], font=font(15), fill=(200, 204, 212))
    sheet.save(os.path.join(od, "DIBURAMA_THERMOLINE_VISUAL_LAB_V5_HOJA_CONTACTOS.jpg"), quality=90)
    with open(os.path.join(od, "CLIPS_Y_TIEMPOS_DE_ORIGEN_V5.md"), "w") as fh:
        fh.write("| Reel (s) | Ventana | Clip | Tiempo en el original | Uso |\n|---|---|---|---|---|\n")
        for f0, f1, win, clip, src, use in V5.CLIPS:
            fh.write(f"| {f0/25:.2f}–{(f1+1)/25:.2f} | {win} | {clip} | {src} | {use} |\n".replace('.', ',', 2))

def sharp_pct(g):
    occ = []
    for fr in g:
        lap = np.abs(cv2.Laplacian(fr, cv2.CV_32F, ksize=3))
        occ.append(float((cv2.resize(lap, (45, 80), interpolation=cv2.INTER_AREA) > 6.0).mean()))
    return round(100 * float(np.mean(occ)), 1)

def comparar(v4, v5, od):
    out = {}
    for name, mp4 in [('V4', v4), ('V5', v5)]:
        g = gray(mp4, 540, 960)
        small = gray(mp4, 108, 192); dd = np.abs(np.diff(small, axis=0)).mean((1, 2))
        bg_tex = []   # textura del fondo: desviación local en las franjas superior/inferior fuera de las ventanas de 0–16 s
        for fr in g[:400:10]:
            band = np.vstack([fr[0:90], fr[880:960]])
            bg_tex.append(float(np.std(cv2.GaussianBlur(band, (0, 0), 2))))
        out[name] = dict(lienzo_con_imagen_nitida_0_16s_pct=sharp_pct(g[:400:5]),
                         lienzo_con_imagen_nitida_climax_16_17_68s_pct=sharp_pct(g[400:442:2]),
                         movimiento_medio_climax=round(float(dd[400:441].mean()), 2),
                         textura_fondo_bordes=round(float(np.mean(bg_tex)), 2))
    json.dump(out, open(os.path.join(od, "comparacion_v4_v5.json"), "w"), indent=1, ensure_ascii=False)
    print(json.dumps(out, indent=1, ensure_ascii=False))
    idx = [300, 350, 400, 412, 425, 437, 445, 462, 487]
    a = [frame_at(v4, i, 216, 384) for i in idx]; b = [frame_at(v5, i, 216, 384) for i in idx]
    gap = np.full((384, 6, 3), 13, np.uint8)
    row = lambda fs: np.hstack(sum([[x, gap] for x in fs], [])[:-1])
    head = np.full((44, row(a).shape[1], 3), 13, np.uint8)
    im = Image.fromarray(np.vstack([head, row(a), head, row(b)])); dr = ImageDraw.Draw(im)
    dr.text((8, 8), "V4 — 12,0 · 14,0 · 16,0 · 16,5 · 17,0 · 17,5 · 17,8 · 18,5 · 19,5 s", font=font(26, 'InterDisplay-Bold.otf'), fill=(255, 255, 255))
    dr.text((8, 44 + 384 + 8), "V5 — mismos instantes", font=font(26, 'InterDisplay-Bold.otf'), fill=(229, 14, 119))
    im.save(os.path.join(od, "DIBURAMA_THERMOLINE_COMPARACION_V4_V5.jpg"), quality=88)

if __name__ == '__main__':
    cmd = sys.argv[1]
    if cmd == 'hoja': hoja(*sys.argv[2:4])
    elif cmd == 'comparar': comparar(*sys.argv[2:5])
