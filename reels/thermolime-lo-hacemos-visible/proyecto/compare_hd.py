# Comparación antes/después de la restauración HD, a la misma escala (recortes 1:1 de fotogramas renderizados)
# uso: python3 compare_hd.py dir_antes dir_despues out.jpg out.json
import sys, os, glob, json
import numpy as np, cv2
from PIL import Image, ImageDraw
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from deliver_v4 import font

# fotograma → (x, y) del recorte 1:1 de 560 × 315 y descripción
CROPS = {225: (560, 520, "Sistema multicapa (pantalla completa)"), 260: (280, 560, "Sistema multicapa (ventana editorial)"),
         310: (700, 380, "Rodillo macro (pantalla completa)"), 350: (330, 400, "Operario proyectando (ventana)"),
         375: (300, 420, "Rodillo sobre ladrillo (ventana)"), 392: (680, 380, "Spray (pantalla completa)"),
         405: (820, 420, "Edificio (pantalla completa)"), 430: (420, 460, "Edificio (ventana) + llana"),
         500: (1060, 300, "Clímax: sistema multicapa")}
CW, CH = 560, 315

def blockiness(g):
    g = g.astype(np.float32); dx = np.abs(np.diff(g, axis=1)); c = np.arange(dx.shape[1])
    dy = np.abs(np.diff(g, axis=0)); r = np.arange(dy.shape[0])
    return float((dx[:, c % 8 == 7].mean() + dy[r % 8 == 7].mean()) / (dx[:, c % 8 != 7].mean() + dy[r % 8 != 7].mean()))

def main(da, db, out, js):
    rows, rep = [], {}
    for n, (x, y, desc) in CROPS.items():
        a, b = cv2.imread(f"{da}/f{n:03d}.png"), cv2.imread(f"{db}/f{n:03d}.png")
        lo = lambda im: cv2.GaussianBlur(cv2.resize(im, (240, 135), interpolation=cv2.INTER_AREA).astype(np.float32), (0, 0), 1)
        layout = float(np.abs(lo(a) - lo(b)).mean())                      # 0 ≈ misma composición
        ca, cb = a[y:y + CH, x:x + CW], b[y:y + CH, x:x + CW]
        ga, gb = cv2.cvtColor(ca, cv2.COLOR_BGR2GRAY), cv2.cvtColor(cb, cv2.COLOR_BGR2GRAY)
        det = lambda g: float(np.abs(cv2.Laplacian(cv2.GaussianBlur(g, (0, 0), 0.6).astype(np.float32), cv2.CV_32F)).mean())
        # (la métrica de bloques se mide en las fuentes, alineada a su rejilla 8×8: ver README; aquí no sería fiable)
        rep[f"{n / 25:.2f} s · {desc}"] = dict(diferencia_composicion=round(layout, 2), detalle_antes=round(det(ga), 2), detalle_hd=round(det(gb), 2),
                                              mejora_detalle_pct=round(100 * (det(gb) / det(ga) - 1), 1))
        rows.append((n, desc, ca, cb))
    pad, lab = 16, 40
    sheet = Image.new('RGB', (2 * CW + 3 * pad, len(rows) * (CH + lab + pad) + 100), (13, 18, 25)); d = ImageDraw.Draw(sheet)
    d.text((pad, 20), "LinkedIn — restauración HD · antes / después (recortes 1:1 del vídeo renderizado)", font=font(28, 'InterDisplay-Bold.otf'), fill=(255, 255, 255))
    d.text((pad, 60), "Izquierda: fuente anterior (1 Mbps) · Derecha: fragmentos originales HD · mismo fotograma, misma escala, sin enfoque añadido", font=font(17), fill=(170, 176, 186))
    for k, (n, desc, ca, cb) in enumerate(rows):
        y0 = 100 + k * (CH + lab + pad)
        d.text((pad, y0 + 6), f"{n / 25:05.2f} s · f{n} · {desc}".replace('.', ',', 1), font=font(20, 'InterDisplay-Bold.otf'), fill=(229, 14, 119))
        sheet.paste(Image.fromarray(cv2.cvtColor(ca, cv2.COLOR_BGR2RGB)), (pad, y0 + lab))
        sheet.paste(Image.fromarray(cv2.cvtColor(cb, cv2.COLOR_BGR2RGB)), (2 * pad + CW, y0 + lab))
    sheet.save(out, quality=92)
    json.dump(rep, open(js, 'w'), indent=1, ensure_ascii=False); print(json.dumps(rep, indent=1, ensure_ascii=False))

if __name__ == '__main__': main(*sys.argv[1:5])
