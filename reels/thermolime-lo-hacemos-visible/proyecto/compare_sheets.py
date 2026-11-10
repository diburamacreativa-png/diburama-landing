# Hoja de contactos de la selección (V2) y comparación objetiva V1 ↔ V2
# uso: python3 compare_sheets.py v1.mp4 v2.mp4 out_dir
import sys, os, json, subprocess
import numpy as np, cv2
from PIL import Image, ImageDraw, ImageFont
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from lib import SRC, FONTS
import scenes_v2

def frames(mp4, w=108, h=192):
    raw = subprocess.run(["ffmpeg", "-v", "error", "-i", mp4, "-vf", f"scale={w}:{h}", "-f", "rawvideo", "-pix_fmt", "rgb24", "-"],
                         capture_output=True, check=True).stdout
    return np.frombuffer(raw, np.uint8).reshape(-1, h, w, 3)

def frame_at(mp4, n, w, h):
    raw = subprocess.run(["ffmpeg", "-v", "error", "-i", mp4, "-vf", f"select=eq(n\\,{n}),scale={w}:{h}", "-frames:v", "1",
                          "-f", "rawvideo", "-pix_fmt", "rgb24", "-"], capture_output=True, check=True).stdout
    return np.frombuffer(raw, np.uint8).reshape(h, w, 3)

def metrics(mp4):
    fr = frames(mp4).astype(np.float32)
    d = np.abs(np.diff(fr, axis=0)).mean((1, 2, 3))
    cuts = np.where(d > 22)[0] + 1
    # agrupar cortes consecutivos (transiciones de varios fotogramas) en un solo evento
    ev = [c for i, c in enumerate(cuts) if i == 0 or c - cuts[i - 1] > 2]
    bounds = [0] + ev + [len(fr)]
    lens = np.diff(bounds) / 25
    per_s = [float(d[i * 25:(i + 1) * 25].mean()) for i in range(20)]
    return dict(cortes=len(ev), plano_mas_largo_s=round(float(lens.max()), 2), duracion_media_plano_s=round(float(lens.mean()), 2),
                cortes_0_12s=int(sum(1 for c in ev if c < 300)),
                energia_movimiento_media=round(float(d.mean()), 2),
                energia_movimiento_0_12s=round(float(d[:300].mean()), 2),
                segundos_casi_estaticos=[i for i, v in enumerate(per_s) if v < 1.5],
                energia_por_segundo=[round(v, 1) for v in per_s])

def font(sz, w='InterDisplay-SemiBold.otf'): return ImageFont.truetype(os.path.join(FONTS, w), sz)

def selection_sheet(v2, out):
    shots = scenes_v2.SHOTS; cols = 7; tw, th = 230, 409; sh = 130; pad = 14
    cw, ch = tw + pad, th + sh + 92
    rows = (len(shots) + cols - 1) // cols
    sheet = Image.new('RGB', (cols * cw + pad, rows * ch + 110), (10, 18, 34)); d = ImageDraw.Draw(sheet)
    d.text((pad, 24), "DIBURAMA · THERMOLIME · V2 — planos utilizados y tiempos de origen", font=font(34, 'InterDisplay-Bold.otf'), fill=(255, 255, 255))
    d.text((pad, 68), "Arriba: fotograma del Reel (mitad del plano) · Abajo: fotograma del vídeo original · Reel s = fotogramas/25",
           font=font(20), fill=(170, 180, 200))
    for k, (f0, f1, src, desc) in enumerate(shots):
        r, c = divmod(k, cols); x = pad + c * cw; y = 110 + r * ch
        mid = (f0 + f1) // 2
        sheet.paste(Image.fromarray(frame_at(v2, mid, tw, th)), (x, y))
        # fotograma original correspondiente (primer tiempo citado)
        t = src.split(' ')[0].split('/')[0].strip()
        if t != '—':
            mm, ss = t.split(':'); ts = int(mm) * 60 + float(ss.replace(',', '.'))
            im = cv2.cvtColor(SRC.frame(int(round(ts * 25))), cv2.COLOR_BGR2RGB)
            sheet.paste(Image.fromarray(cv2.resize(im, (tw, sh), interpolation=cv2.INTER_AREA)), (x, y + th + 4))
        d.text((x, y + th + sh + 10), f"Reel {f0/25:05.2f}–{(f1+1)/25:05.2f} s".replace('.', ','), font=font(18, 'InterDisplay-Bold.otf'), fill=(230, 25, 125))
        d.text((x, y + th + sh + 32), f"Origen {src}", font=font(16), fill=(255, 255, 255))
        lines, cur = [], ""
        for wd in desc.split():
            if len(cur + wd) > 30: lines.append(cur.strip()); cur = ""
            cur += wd + " "
        lines.append(cur.strip())
        for i, ln in enumerate(lines[:2]): d.text((x, y + th + sh + 52 + i * 18), ln, font=font(15), fill=(170, 180, 200))
    sheet.save(out, quality=90)

def side_by_side(v1, v2, out):
    a, b = frames(v1, 135, 240), frames(v2, 135, 240)
    idx = list(range(0, 500, 12))
    pad = np.full((240, 4, 3), 20, np.uint8)
    row = lambda fr: np.hstack(sum([[fr[i], pad] for i in idx], [])[:-1])
    top, bot = row(a), row(b)
    lab = np.full((36, top.shape[1], 3), 10, np.uint8)
    img = np.vstack([lab, top, lab, bot])
    im = Image.fromarray(img); d = ImageDraw.Draw(im)
    d.text((8, 6), "V1 (anterior) — un fotograma cada 0,48 s", font=font(22, 'InterDisplay-Bold.otf'), fill=(255, 255, 255))
    d.text((8, 36 + 240 + 6), "V2 (nueva) — mismos instantes", font=font(22, 'InterDisplay-Bold.otf'), fill=(230, 25, 125))
    # partir en dos filas para que sea legible
    W2 = im.width // 2
    left, right = im.crop((0, 0, W2, im.height)), im.crop((W2, 0, im.width, im.height))
    out_im = Image.new('RGB', (W2 + 10, im.height * 2 + 10), (10, 18, 34))
    out_im.paste(left, (0, 0)); out_im.paste(right, (0, im.height + 10)); out_im.save(out, quality=88)

if __name__ == '__main__':
    v1, v2, od = sys.argv[1:4]; os.makedirs(od, exist_ok=True)
    m = {'V1': metrics(v1), 'V2': metrics(v2)}
    json.dump(m, open(os.path.join(od, 'comparacion_v1_v2.json'), 'w'), indent=1, ensure_ascii=False)
    print(json.dumps({k: {kk: vv for kk, vv in v.items() if kk != 'energia_por_segundo'} for k, v in m.items()}, indent=1, ensure_ascii=False))
    selection_sheet(v2, os.path.join(od, 'DIBURAMA_THERMOLINE_V2_HOJA_CONTACTOS_SELECCION.jpg'))
    side_by_side(v1, v2, os.path.join(od, 'DIBURAMA_THERMOLINE_COMPARACION_V1_V2.jpg'))
