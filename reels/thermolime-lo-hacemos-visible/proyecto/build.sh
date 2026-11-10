#!/usr/bin/env bash
# Reconstruye todos los entregables desde los archivos de in/.
# Requisitos: ffmpeg, python3 con numpy, opencv-python-headless, pillow (con raqm), scipy, soundfile
set -euo pipefail
cd "$(dirname "$0")"
mkdir -p build
python3 render.py build/video.mp4                                   # 500 fotogramas 1080x1920 25 fps
python3 audio.py in/music.mp3 in/sfx build/audio                     # mezcla + versión sin música + informe
ffmpeg -v error -y -i build/video.mp4 -i build/audio/master_mix.wav -map 0:v -map 1:a -c:v copy \
  -c:a aac -b:a 320k -ar 48000 -t 20 -movflags +faststart build/DIBURAMA_THERMOLINE_LO_HACEMOS_VISIBLE_FINAL.mp4
ffmpeg -v error -y -i build/video.mp4 -i build/audio/sfx_only.wav -map 0:v -map 1:a -c:v copy \
  -c:a aac -b:a 320k -ar 48000 -t 20 -movflags +faststart build/DIBURAMA_THERMOLINE_LO_HACEMOS_VISIBLE_SIN_MUSICA.mp4
python3 cover.py build/DIBURAMA_THERMOLINE_PORTADA.jpg
python3 qa.py build/DIBURAMA_THERMOLINE_LO_HACEMOS_VISIBLE_FINAL.mp4 build/audio/audio_report.json > build/qa_report.json
echo "OK -> build/"
