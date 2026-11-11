# Verificación del cierre musical V4: espectrogramas de los últimos 10 s (canción original · vídeo V3 · vídeo V4),
# fotogramas del cierre y estabilidad de los últimos 2,5 s.
# uso: python3 verify_v4_audio.py cancion.mp3 v3.mp4 v4.mp4 out.jpg
import sys, os, subprocess
import numpy as np, cv2
from scipy.signal import stft
from PIL import Image, ImageDraw
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from deliver_v4 import font

SR = 48000
def pcm(path, ss, t):
    raw = subprocess.run(["ffmpeg", "-v", "error", "-ss", str(ss), "-t", str(t), "-i", path, "-map", "0:a", "-ac", "1", "-ar", str(SR), "-f", "f32le", "-"],
                         capture_output=True, check=True).stdout
    return np.frombuffer(raw, np.float32).astype(np.float64)

def spec_img(x, w=1700, h=300):
    f, t, Z = stft(x, SR, nperseg=4096, noverlap=4096 - 512)
    S = np.clip((20 * np.log10(np.abs(Z) + 1e-9)[f < 8000][::-1] + 100) / 80, 0, 1)
    return cv2.cvtColor(cv2.resize(cv2.applyColorMap((S * 255).astype(np.uint8), cv2.COLORMAP_MAGMA), (w, h), interpolation=cv2.INTER_AREA), cv2.COLOR_BGR2RGB)

def frame(p, n, w, h):
    raw = subprocess.run(["ffmpeg", "-v", "error", "-i", p, "-vf", f"select=eq(n\\,{n}),scale={w}:{h}:flags=area", "-frames:v", "1", "-f", "rawvideo", "-pix_fmt", "rgb24", "-"],
                         capture_output=True, check=True).stdout
    return np.frombuffer(raw, np.uint8).reshape(h, w, 3)

def main(song, v3, v4, out):
    W, SH, pad = 1700, 300, 20
    rows = [("Canción original · últimos 10 s (02:46,28–02:56,28)", pcm(song, 166.28, 10.0), [(171.795 - 166.28, "último golpe"), (176.28 - 166.28, "fin")]),
            ("Vídeo V3 · 14–24 s (música editada)", pcm(v3, 14.0, 10.0), [(16.02 - 14, "compás repetido"), (18.69 - 14, "fin repetición"), (20.36 - 14, "marca"), (21.36 - 14, "acorde añadido")]),
            ("Vídeo V4 · 14–24 s (canción continua 02:45,77–02:55,77)", pcm(v4, 14.0, 10.0), [(20.03 - 14, "último golpe = marca (f500)"), (24.0 - 14, "fin")])]
    H = 120 + len(rows) * (SH + 70) + 330
    sheet = Image.new('RGB', (W + 2 * pad, H), (13, 18, 25)); d = ImageDraw.Draw(sheet)
    d.text((pad, 20), "LinkedIn V4 — verificación del cierre musical", font=font(32, 'InterDisplay-Bold.otf'), fill=(255, 255, 255))
    d.text((pad, 64), "Espectrogramas 0–8 kHz de 10 s. En la V4 la música es la canción original continua: su último golpe abre el logotipo y su cola natural cierra la pieza.", font=font(18), fill=(170, 176, 186))
    y = 120
    for title, x, marks in rows:
        d.text((pad, y), title, font=font(22, 'InterDisplay-Bold.otf'), fill=(229, 14, 119))
        img = spec_img(x, W, SH).copy()
        for tm, lab in marks:
            xx = int(tm / 10 * W) - (2 if tm >= 10 else 0); cv2.line(img, (xx, 0), (xx, SH), (255, 255, 255), 2)
            cv2.putText(img, lab, (min(xx + 6, W - 260), 26), 0, 0.7, (255, 255, 255), 2, cv2.LINE_AA)
        sheet.paste(Image.fromarray(img), (pad, y + 34)); y += SH + 70
    d.text((pad, y), "Vídeo V4 · fotogramas del cierre", font=font(22, 'InterDisplay-Bold.otf'), fill=(229, 14, 119))
    ns = [495, 500, 503, 512, 524, 599]; tw = (W - 5 * 10) // 6; th = tw * 9 // 16
    for k, n in enumerate(ns):
        sheet.paste(Image.fromarray(frame(v4, n, tw, th)), (pad + k * (tw + 10), y + 34))
        d.text((pad + k * (tw + 10), y + 40 + th), f"f{n} · {n / 25:.2f} s".replace('.', ','), font=font(16), fill=(200, 204, 212))
    sheet.save(out, quality=92)

if __name__ == '__main__': main(*sys.argv[1:5])
