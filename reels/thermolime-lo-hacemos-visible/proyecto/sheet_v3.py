# Hoja de contactos del máster V3 + relación de clips con tiempos de origen
# uso: python3 sheet_v3.py final.mp4 out_dir
import sys, os, subprocess
import numpy as np
from PIL import Image, ImageDraw, ImageFont
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from lib import FONTS
import scenes_v3 as V

TIMES = [0.0, 1.0, 2.0, 3.5, 4.2, 5.8, 7.2, 8.69, 9.6, 11.0, 12.4, 13.0, 14.0, 15.5, 16.9, 18.0, 19.96]

def frame_at(mp4, n, w, h):
    raw = subprocess.run(["ffmpeg", "-v", "error", "-i", mp4, "-vf", f"select=eq(n\\,{n}),scale={w}:{h}:flags=area", "-frames:v", "1",
                          "-f", "rawvideo", "-pix_fmt", "rgb24", "-"], capture_output=True, check=True).stdout
    return np.frombuffer(raw, np.uint8).reshape(h, w, 3)

def font(sz, n='InterDisplay-SemiBold.otf'): return ImageFont.truetype(os.path.join(FONTS, n), sz)

def scene_of(n):
    for f0, f1, clip, src, use in V.CLIPS:
        if f0 <= n <= f1: return clip, src, use
    return "", "", ""

def main(mp4, od):
    os.makedirs(od, exist_ok=True)
    cols, tw, th, pad = 6, 300, 533, 16
    rows = (len(TIMES) + cols - 1) // cols; ch = th + 96
    sheet = Image.new('RGB', (cols * (tw + pad) + pad, rows * ch + 120), (16, 20, 25)); d = ImageDraw.Draw(sheet)
    d.text((pad, 26), "DIBURAMA · «VENTANA A LO INVISIBLE» — hoja de contactos del máster final", font=font(36, 'InterDisplay-Bold.otf'), fill=(255, 255, 255))
    d.text((pad, 74), "Tiempo del Reel · clip y tiempo de origen en el vídeo Thermolime original", font=font(22), fill=(170, 176, 186))
    for k, t in enumerate(TIMES):
        n = min(499, int(round(t * 25)))
        r, c = divmod(k, cols); x = pad + c * (tw + pad); y = 120 + r * ch
        sheet.paste(Image.fromarray(frame_at(mp4, n, tw, th)), (x, y))
        clip, src, use = scene_of(n)
        d.text((x, y + th + 8), f"{t:05.2f} s · f{n}".replace('.', ','), font=font(21, 'InterDisplay-Bold.otf'), fill=(214, 75, 150))
        d.text((x, y + th + 36), clip, font=font(17), fill=(255, 255, 255))
        d.text((x, y + th + 58), src[:34], font=font(16), fill=(170, 176, 186))
    sheet.save(os.path.join(od, "DIBURAMA_THERMOLINE_VENTANA_INVISIBLE_HOJA_CONTACTOS.jpg"), quality=90)
    with open(os.path.join(od, "CLIPS_Y_TIEMPOS_DE_ORIGEN.md"), "w") as fh:
        fh.write("| Reel (s) | Fotogramas | Clip | Tiempo en el original | Uso |\n|---|---|---|---|---|\n")
        for f0, f1, clip, src, use in V.CLIPS:
            fh.write(f"| {f0/25:.2f}–{(f1+1)/25:.2f} | {f0}–{f1} | {clip} | {src} | {use} |\n".replace('.', ','))

if __name__ == '__main__': main(*sys.argv[1:3])
