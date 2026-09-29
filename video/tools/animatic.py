# Animatic 540x960 with timecode + scene labels (python3 tools/animatic.py)
import subprocess, imageio_ffmpeg
from PIL import Image, ImageDraw, ImageFont
FF = imageio_ffmpeg.get_ffmpeg_exe()
LAB = [(0, 3, '01 PLANO > ES/ERA'), (3, 5.5, '02a PLANO > MAQUINA 3D'), (5.5, 8, '02b EXPLOSIONADO > CAPSULA > MOLECULA'),
       (8, 10.5, '03 MOLECULA > SOFTWARE'), (10.5, 13, '04 GRAFICA > HORIZONTE  [KLING K01]'), (13, 16, '05 PERSONA REAL > 2D  [K02]'),
       (16, 18, '06 COLAPSO > GOTA'), (18, 18.6, '06b SILENCIO 0,6 s'), (18.6, 22.5, '07 MUNDO EN LA GOTA > LOGO'), (22.5, 27, '08 CIERRE > LOOP')]
font = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSansMono-Bold.ttf', 18)
p = subprocess.Popen([FF, '-y', '-loglevel', 'error', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-s', '540x960', '-r', '30', '-i', '-',
                      '-i', 'audio/score_master.wav', '-c:v', 'libx264', '-crf', '23', '-pix_fmt', 'yuv420p', '-c:a', 'aac', '-b:a', '160k',
                      '-t', '27', '-movflags', '+faststart', 'out/DIBURAMA_LA_GOTA_ANIMATIC.mp4'], stdin=subprocess.PIPE)
for f in range(810):
    t = f / 30
    im = Image.open(f'frames/f{f:04d}.png').convert('RGB').resize((540, 960), Image.BILINEAR)
    d = ImageDraw.Draw(im)
    lab = next(l for a, b, l in LAB if a <= t < b)
    d.rectangle([0, 0, 540, 52], fill=(0, 0, 0))
    d.text((8, 5), f'{t:05.2f}s  f{f:03d}', font=font, fill=(255, 255, 255)); d.text((8, 28), lab, font=font, fill=(230, 25, 125))
    p.stdin.write(im.tobytes())
p.stdin.close(); p.wait(); print('ok')
