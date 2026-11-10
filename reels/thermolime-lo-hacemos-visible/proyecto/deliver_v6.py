# V6 · hoja de contactos (12, 13 … 21 s y último fotograma), relación de clips y espectrograma del cierre (16–22 s)
# uso: python3 deliver_v6.py hoja final_v6.mp4 out_dir
#      python3 deliver_v6.py espectro master_mix.wav out.png
import sys, os, subprocess
import numpy as np, cv2
from PIL import Image, ImageDraw
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import scenes_v6 as V6
from deliver_v4 import frame_at, font

TIMES = [0.0, 1.0, 2.4, 4.2, 6.4, 8.69, 10.4, 12.0, 13.0, 14.0, 15.0, 16.0, 16.5, 17.0, 17.5, 18.0, 18.5, 19.0, 20.0, 21.0, 21.96]

def hoja(mp4, od):
    cols, tw, th, pad = 7, 260, 462, 14; rows = (len(TIMES) + cols - 1) // cols; ch = th + 80
    sheet = Image.new('RGB', (cols * (tw + pad) + pad, rows * ch + 112), (13, 18, 25)); d = ImageDraw.Draw(sheet)
    d.text((pad, 22), "DIBURAMA · VISUAL LAB V6 — hoja de contactos (22 s · 550 fotogramas)", font=font(34, 'InterDisplay-Bold.otf'), fill=(255, 255, 255))
    d.text((pad, 66), "Tiempo del Reel · ventanas en pantalla y su origen en el vídeo Thermolime", font=font(20), fill=(170, 176, 186))
    for k, t in enumerate(TIMES):
        n = min(549, int(round(t * 25))); r, c = divmod(k, cols); x = pad + c * (tw + pad); y = 112 + r * ch
        sheet.paste(Image.fromarray(frame_at(mp4, n, tw, th)), (x, y))
        rows_ = [cl for cl in V6.CLIPS if cl[0] <= n <= cl[1]]
        lab = "último fotograma" if n == 549 else ""
        d.text((x, y + th + 8), f"{t:05.2f} s · f{n} {lab}".replace('.', ',', 1), font=font(19, 'InterDisplay-Bold.otf'), fill=(229, 14, 119))
        for i, cl in enumerate(rows_[:2]):
            d.text((x, y + th + 34 + i * 20), f"{cl[2]}: {cl[4]}"[:34], font=font(14), fill=(200, 204, 212))
    sheet.save(os.path.join(od, "DIBURAMA_THERMOLINE_VISUAL_LAB_V6_HOJA_CONTACTOS.jpg"), quality=90)
    with open(os.path.join(od, "CLIPS_Y_TIEMPOS_DE_ORIGEN_V6.md"), "w") as fh:
        fh.write("| Reel (s) | Ventana | Clip | Tiempo en el original | Uso |\n|---|---|---|---|---|\n")
        for f0, f1, win, clip, src, use in V6.CLIPS:
            fh.write(f"| {f0/25:.2f}–{(f1+1)/25:.2f} | {win} | {clip} | {src} | {use} |\n".replace('.', ',', 2))

def espectro(wav, out):
    import soundfile as sf
    from scipy.signal import stft
    x, sr = sf.read(wav); m = x.mean(1)[int(16 * sr):int(22 * sr)]
    f, t, Z = stft(m, sr, nperseg=4096, noverlap=4096 - 512)
    S = 20 * np.log10(np.abs(Z) + 1e-9); keep = f < 8000; S = S[keep][::-1]
    S = np.clip((S + 100) / 80, 0, 1)
    img = cv2.applyColorMap((S * 255).astype(np.uint8), cv2.COLORMAP_MAGMA)
    img = cv2.resize(img, (1500, 520), interpolation=cv2.INTER_AREA)
    pad = np.full((600, 1560, 3), 13, np.uint8); pad[40:560, 40:1540] = img
    for s_ in range(16, 23):
        xx = 40 + int((s_ - 16) / 6 * 1500); cv2.line(pad, (xx, 560), (xx, 572), (255, 255, 255), 1)
        cv2.putText(pad, f"{s_}s", (xx - 12, 592), 0, 0.55, (255, 255, 255), 1, cv2.LINE_AA)
    for s_, txt in [(17.69, "marca"), (18.02, "baja"), (18.69, "tonica"), (22.0, "fin")]:
        xx = 40 + int((s_ - 16) / 6 * 1500); cv2.line(pad, (xx, 40), (xx, 560), (229, 14, 119)[::-1], 1)
        cv2.putText(pad, txt, (min(xx + 4, 1480), 30), 0, 0.55, (255, 255, 255), 1, cv2.LINE_AA)
    cv2.imwrite(out, pad)

if __name__ == '__main__':
    if sys.argv[1] == 'hoja': hoja(*sys.argv[2:4])
    else: espectro(*sys.argv[2:4])
