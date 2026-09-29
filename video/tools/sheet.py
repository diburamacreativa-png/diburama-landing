# Hoja de contactos para QA: python3 tools/sheet.py carpeta salida.png [ancho_miniatura]
import sys, glob, os
from PIL import Image, ImageDraw
files = sorted(glob.glob(os.path.join(sys.argv[1], '*.png')))
tw = int(sys.argv[3]) if len(sys.argv) > 3 else 360
th = tw * 16 // 9
cols = min(5, len(files)); rows = (len(files) + cols - 1) // cols
sheet = Image.new('RGB', (cols * tw, rows * (th + 24)), (30, 30, 30))
d = ImageDraw.Draw(sheet)
for i, f in enumerate(files):
    im = Image.open(f).convert('RGB').resize((tw, th), Image.LANCZOS)
    x, y = (i % cols) * tw, (i // cols) * (th + 24)
    sheet.paste(im, (x, y + 24)); d.text((x + 6, y + 5), os.path.basename(f), fill=(255, 255, 255))
sheet.save(sys.argv[2])
