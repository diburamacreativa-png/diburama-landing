# LinkedIn · portada, hoja de contactos, relación de fragmentos, espectrograma del cierre y vista de feed móvil
# uso: python3 deliver_linkedin.py portada out.jpg
#      python3 deliver_linkedin.py hoja    final.mp4 out_dir
#      python3 deliver_linkedin.py espectro master_mix.wav out.png
#      python3 deliver_linkedin.py movil   final.mp4 out.jpg
import sys, os, subprocess
import numpy as np, cv2
import linkedin as L                       # fija el lienzo a 1920 × 1080
from PIL import Image, ImageDraw
from lib import TextBlock, line_mask_x, line_mask_y, over
import scenes_v5 as V5
from deliver_v4 import font

def frame_at(mp4, n, w, h):
    raw = subprocess.run(["ffmpeg", "-v", "error", "-i", mp4, "-vf", f"select=eq(n\\,{n}),scale={w}:{h}:flags=area", "-frames:v", "1",
                          "-f", "rawvideo", "-pix_fmt", "rgb24", "-"], capture_output=True, check=True).stdout
    return np.frombuffer(raw, np.uint8).reshape(h, w, 3)

def portada(out):
    L.setup(); L.build_text()
    img = L.render_frame(60)                                   # termografía + titular completo
    s1 = L.T['s1']; y_end = 540 + (3 * 0.98 * s1 + 0.727 * s1) / 2
    cap = TextBlock("CASO REAL · THERMOLIME", 'semi', 30, tracking=0.22)
    img = cap.draw(img, 1320, y_end + 44, color=L.GREY)
    img = over(img, np.broadcast_to(L.FUCHSIA, img.shape), line_mask_x(1320, 1380, 1.2) * line_mask_y(y_end + 22, y_end + 27, 1.0))
    img, _ = V5.put_logo(img, 340 / 1065, L.MR - 170, L.MB - 65)   # logotipo original, abajo a la derecha
    cv2.imwrite(out, (np.clip(img, 0, 1) * 255 + .5).astype(np.uint8), [cv2.IMWRITE_JPEG_QUALITY, 95])

TIMES = [0.0, 1.0, 2.0, 3.0, 4.0, 4.8, 6.4, 7.6, 8.5, 9.0, 10.4, 11.6, 12.4, 13.0, 14.0, 15.0, 15.6, 16.2, 17.0, 18.4, 19.2,
         19.6, 20.2, 20.7, 21.2, 22.0, 23.0, 23.96]
def hoja(mp4, od):
    cols, tw, th, pad = 4, 420, 236, 14; rows = (len(TIMES) + cols - 1) // cols; ch = th + 64
    sheet = Image.new('RGB', (cols * (tw + pad) + pad, rows * ch + 104), (13, 18, 25)); d = ImageDraw.Draw(sheet)
    d.text((pad, 20), "DIBURAMA · VISUAL LAB — LINKEDIN 16:9 · hoja de contactos (24 s · 600 fotogramas)", font=font(30, 'InterDisplay-Bold.otf'), fill=(255, 255, 255))
    d.text((pad, 60), "Tiempo · composición · fragmento original. Recuadro amarillo: zona segura (120 px laterales, 90 px arriba/abajo)", font=font(18), fill=(170, 176, 186))
    for k, t in enumerate(TIMES):
        n = min(599, int(round(t * 25))); r, c = divmod(k, cols); x = pad + c * (tw + pad); y = 104 + r * ch
        im = frame_at(mp4, n, tw, th).copy(); s = tw / 1920
        cv2.rectangle(im, (int(120 * s), int(90 * s)), (int(1800 * s), int(990 * s)), (255, 220, 0), 1)
        sheet.paste(Image.fromarray(im), (x, y))
        cl = [c_ for c_ in L.CLIPS if c_[0] <= n <= c_[1]]
        d.text((x, y + th + 6), f"{t:05.2f} s · f{n}{' · último' if n == 599 else ''}".replace('.', ',', 1), font=font(18, 'InterDisplay-Bold.otf'), fill=(229, 14, 119))
        if cl: d.text((x, y + th + 30), f"{cl[0][2]} · {cl[0][3]}"[:52], font=font(14), fill=(200, 204, 212))
    sheet.save(os.path.join(od, "DIBURAMA_THERMOLINE_LINKEDIN_HOJA_CONTACTOS.jpg"), quality=90)
    with open(os.path.join(od, "FRAGMENTOS_Y_TIEMPOS_DE_ORIGEN_LINKEDIN.md"), "w") as fh:
        fh.write("| Vídeo (s) | Fotogramas | Composición | Clip | Tiempo en el original | Uso |\n|---|---|---|---|---|---|\n")
        for f0, f1, comp, clip, src, use in L.CLIPS:
            fh.write(f"| {f0/25:.2f}–{(f1+1)/25:.2f} | {f0}–{f1} | {comp} | {clip} | {src} | {use} |\n".replace('.', ',', 2))

def espectro(wav, out, t0=18.0, t1=24.0, marks=((20.357, "marca"), (20.69, "baja"), (21.357, "tonica"), (24.0, "fin"))):
    import soundfile as sf
    from scipy.signal import stft
    x, sr = sf.read(wav); m = x.mean(1)[int(t0 * sr):int(t1 * sr)]
    f, t, Z = stft(m, sr, nperseg=4096, noverlap=4096 - 512)
    S = np.clip((20 * np.log10(np.abs(Z) + 1e-9)[f < 8000][::-1] + 100) / 80, 0, 1)
    img = cv2.resize(cv2.applyColorMap((S * 255).astype(np.uint8), cv2.COLORMAP_MAGMA), (1500, 520), interpolation=cv2.INTER_AREA)
    pad = np.full((600, 1560, 3), 13, np.uint8); pad[40:560, 40:1540] = img
    for s_ in range(int(t0), int(t1) + 1):
        xx = 40 + int((s_ - t0) / (t1 - t0) * 1500); cv2.putText(pad, f"{s_}s", (xx - 12, 592), 0, 0.55, (255, 255, 255), 1, cv2.LINE_AA)
    for s_, txt in marks:
        xx = 40 + int((s_ - t0) / (t1 - t0) * 1500); cv2.line(pad, (xx, 40), (xx, 560), (119, 14, 229), 1)
        cv2.putText(pad, txt, (min(xx + 4, 1480), 30), 0, 0.55, (255, 255, 255), 1, cv2.LINE_AA)
    cv2.imwrite(out, pad)

def movil(mp4, out):
    """simulación del feed móvil: el vídeo a 390 px de ancho (pantalla de teléfono típica, en píxeles CSS)"""
    ns = [50, 260, 345, 430, 560]; tiles = [frame_at(mp4, n, 390, 219) for n in ns]
    gap = np.full((219, 10, 3), 13, np.uint8)
    cv2.imwrite(out, cv2.cvtColor(np.hstack(sum([[t_, gap] for t_ in tiles], [])[:-1]), cv2.COLOR_RGB2BGR), [cv2.IMWRITE_JPEG_QUALITY, 92])

if __name__ == '__main__':
    cmd = sys.argv[1]
    if cmd == 'portada': portada(sys.argv[2])
    elif cmd == 'hoja': hoja(*sys.argv[2:4])
    elif cmd == 'espectro': espectro(*sys.argv[2:4])
    elif cmd == 'movil': movil(*sys.argv[2:4])
