# Comparativa V2 → V3 en 3,00 · 4,50 · 19,00 s, a partir de los MP4 exportados (misma resolución y escala)
# uso: python3 compare_hd3.py v2.mp4 v3.mp4 out.jpg out.json
import sys, os, json, subprocess
import numpy as np, cv2
from PIL import Image, ImageDraw
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from deliver_v4 import font

MOMENTS = [(75, (1060, 330), "00:03,00 · cristales azules"), (112, (700, 260), "00:04,50 · partícula (revelación)"),
           (475, (560, 300), "00:19,00 · partícula (clímax)")]
CW, CH = 760, 428

def frame(p, n):
    raw = subprocess.run(["ffmpeg", "-v", "error", "-i", p, "-vf", f"select=eq(n\\,{n})", "-frames:v", "1", "-f", "rawvideo", "-pix_fmt", "bgr24", "-"],
                         capture_output=True, check=True).stdout
    return np.frombuffer(raw, np.uint8).reshape(1080, 1920, 3)

def blockiness(g):
    """bloques 8×8 del códec, medidos en el MP4 exportado (rejilla alineada a 1920×1080): 1,0 = sin bloques"""
    g = g.astype(np.float32); dx = np.abs(np.diff(g, axis=1)); c = np.arange(dx.shape[1])
    dy = np.abs(np.diff(g, axis=0)); r = np.arange(dy.shape[0])
    return float((dx[:, c % 8 == 7].mean() + dy[r % 8 == 7].mean()) / (dx[:, c % 8 != 7].mean() + dy[r % 8 != 7].mean()))

def detail(g): return float(np.abs(cv2.Laplacian(cv2.GaussianBlur(g, (0, 0), 0.6).astype(np.float32), cv2.CV_32F)).mean())

def main(v2, v3, out, js):
    rep, rows = {}, []
    for n, (x, y), desc in MOMENTS:
        a, b = frame(v2, n), frame(v3, n)
        x8, y8 = x - x % 8, y - y % 8
        ga, gb = [cv2.cvtColor(im[y8:y8 + CH, x8:x8 + CW], cv2.COLOR_BGR2GRAY) for im in (a, b)]
        rep[desc] = dict(fotograma=n, bloques_v2=round(blockiness(ga), 3), bloques_v3=round(blockiness(gb), 3),
                         detalle_v2=round(detail(ga), 2), detalle_v3=round(detail(gb), 2),
                         mejora_detalle_pct=round(100 * (detail(gb) / detail(ga) - 1), 1))
        rows.append((n, desc, a, b, x8, y8))
    pad, lab, fw, fh = 16, 44, 760, 428
    H = 110 + len(rows) * (lab + fh + pad + CH + pad)
    sheet = Image.new('RGB', (2 * fw + 3 * pad, H), (13, 18, 25)); d = ImageDraw.Draw(sheet)
    d.text((pad, 20), "LinkedIn HD V3 — corrección de los segundos 3, 4 y 19 (V2 izquierda · V3 derecha)", font=font(28, 'InterDisplay-Bold.otf'), fill=(255, 255, 255))
    d.text((pad, 62), "Fotogramas extraídos de los MP4 exportados. Fila superior: fotograma completo reducido; fila inferior: recorte 1:1 (sin escalar)", font=font(17), fill=(170, 176, 186))
    y0 = 110
    for n, desc, a, b, x8, y8 in rows:
        m = rep[desc]
        d.text((pad, y0 + 8), f"{desc} · f{n} · detalle {m['detalle_v2']} → {m['detalle_v3']} ({m['mejora_detalle_pct']:+.0f} %) · bloques {m['bloques_v2']} → {m['bloques_v3']}",
               font=font(19, 'InterDisplay-Bold.otf'), fill=(229, 14, 119))
        for k, im in enumerate((a, b)):
            small = cv2.resize(im, (fw, fh), interpolation=cv2.INTER_AREA).copy()
            s = fw / 1920; cv2.rectangle(small, (int(x8 * s), int(y8 * s)), (int((x8 + CW) * s), int((y8 + CH) * s)), (0, 220, 255), 2)
            sheet.paste(Image.fromarray(cv2.cvtColor(small, cv2.COLOR_BGR2RGB)), (pad + k * (fw + pad), y0 + lab))
            sheet.paste(Image.fromarray(cv2.cvtColor(im[y8:y8 + CH, x8:x8 + CW], cv2.COLOR_BGR2RGB)), (pad + k * (fw + pad), y0 + lab + fh + pad))
        y0 += lab + fh + pad + CH + pad
    sheet.save(out, quality=93)
    json.dump(rep, open(js, 'w'), indent=1, ensure_ascii=False); print(json.dumps(rep, indent=1, ensure_ascii=False))

if __name__ == '__main__': main(*sys.argv[1:5])
