#!/usr/bin/env bash
# Automated QA of the master: duration, fps, resolution, black frames, silence, loudness, loop join.
cd "$(dirname "$0")/.."
FF=$(python3 -c "import imageio_ffmpeg;print(imageio_ffmpeg.get_ffmpeg_exe())")
M=out/DIBURAMA_LA_GOTA_9x16_MASTER.mp4
echo "== stream"; $FF -hide_banner -i $M 2>&1 | grep -E "Duration|Stream" | sed 's/^ *//'
echo "== frames"; $FF -hide_banner -i $M -map 0:v -f null - 2>&1 | grep -oE "frame= *[0-9]+" | tail -1
echo "== black frames (blackdetect)"; $FF -hide_banner -i $M -vf blackdetect=d=0.03:pix_th=0.04 -an -f null - 2>&1 | grep blackdetect || echo "no black frames"
echo "== silence (silencedetect -60dB)"; $FF -hide_banner -i $M -af silencedetect=n=-60dB:d=0.3 -vn -f null - 2>&1 | grep -E "silence_(start|end)"
echo "== loudness"; $FF -hide_banner -i $M -af ebur128=peak=true -vn -f null - 2>&1 | grep -A12 Summary | grep -E "I:|Peak:" 
echo "== loop join (f809 vs f0, frames)"; python3 - <<'PY'
from PIL import Image, ImageChops, ImageStat
a=Image.open('frames/f0809.png').convert('L'); b=Image.open('frames/f0000.png').convert('L'); c=Image.open('frames/f0001.png').convert('L')
d1=ImageStat.Stat(ImageChops.difference(a,b)).mean[0]; d2=ImageStat.Stat(ImageChops.difference(b,c)).mean[0]
print(f"mean diff f809->f0 = {d1:.2f}  | f0->f1 = {d2:.2f}  (similar = seamless loop)")
PY
