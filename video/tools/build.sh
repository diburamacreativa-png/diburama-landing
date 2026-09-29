#!/usr/bin/env bash
# Encodes the master + animatic from frames/ and audio/score_raw.wav
set -euo pipefail
cd "$(dirname "$0")/.."
FF=${FFMPEG:-$(python3 -c "import imageio_ffmpeg;print(imageio_ffmpeg.get_ffmpeg_exe())")}
mkdir -p out
# 1) audio: normalized to -14 LUFS / -1 dBTP (Reels / LinkedIn)
$FF -y -loglevel error -i audio/score_raw.wav -af loudnorm=I=-14:TP=-1.0:LRA=11:linear=true -ar 48000 audio/score_master.wav
# 2) master
$FF -y -loglevel error -framerate 30 -i frames/f%04d.png -i audio/score_master.wav \
  -c:v libx264 -preset slow -crf 15 -profile:v high -pix_fmt yuv420p -colorspace bt709 -color_primaries bt709 -color_trc bt709 \
  -c:a aac -b:a 320k -t 27 -movflags +faststart out/DIBURAMA_LA_GOTA_9x16_MASTER.mp4
python3 tools/animatic.py
ls -la out/*.mp4
