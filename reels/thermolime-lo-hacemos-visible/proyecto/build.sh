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

# ---- V2 ----
REEL_SCENES=scenes_v2 python3 render.py build/video_v2.mp4
REEL_AUDIO=v2 python3 audio.py in/music.mp3 in/sfx build/audio_v2
ffmpeg -v error -y -i build/video_v2.mp4 -i build/audio_v2/master_mix.wav -map 0:v -map 1:a -c:v copy \
  -c:a aac -b:a 320k -ar 48000 -t 20 -movflags +faststart build/DIBURAMA_THERMOLINE_LO_HACEMOS_VISIBLE_V2_FINAL.mp4
ffmpeg -v error -y -i build/video_v2.mp4 -i build/audio_v2/sfx_only.wav -map 0:v -map 1:a -c:v copy \
  -c:a aac -b:a 320k -ar 48000 -t 20 -movflags +faststart build/DIBURAMA_THERMOLINE_LO_HACEMOS_VISIBLE_V2_SIN_MUSICA.mp4
python3 compare_sheets.py build/DIBURAMA_THERMOLINE_LO_HACEMOS_VISIBLE_FINAL.mp4 build/DIBURAMA_THERMOLINE_LO_HACEMOS_VISIBLE_V2_FINAL.mp4 build
echo "OK V2 -> build/"

# ---- V3 «Ventana a lo invisible» ----
REEL_SCENES=scenes_v3 REEL_CRF=17 python3 render.py build/video_v3.mp4
REEL_AUDIO=v3 python3 audio.py in/music.mp3 in/sfx build/audio_v3
ffmpeg -v error -y -i build/video_v3.mp4 -i build/audio_v3/master_mix.wav -map 0:v -map 1:a -c:v copy \
  -c:a aac -b:a 320k -ar 48000 -ac 2 -t 20 -movflags +faststart build/DIBURAMA_THERMOLINE_VENTANA_INVISIBLE_FINAL.mp4
python3 cover_v3.py build/DIBURAMA_THERMOLINE_PORTADA_V3.jpg

# ---- V4 «Visual Lab» multiventana ----
REEL_SCENES=scenes_v4 REEL_CRF=17 python3 render.py build/video_v4.mp4
REEL_AUDIO=v4 python3 audio.py in/music.mp3 in/sfx build/audio_v4
ffmpeg -v error -y -i build/video_v4.mp4 -i build/audio_v4/master_mix.wav -map 0:v -map 1:a -c:v copy \
  -c:a aac -b:a 320k -ar 48000 -ac 2 -t 20 -movflags +faststart build/DIBURAMA_THERMOLINE_VISUAL_LAB_V4.mp4
python3 deliver_v4.py portada build/DIBURAMA_THERMOLINE_PORTADA_V4.jpg
python3 deliver_v4.py hoja build/DIBURAMA_THERMOLINE_VISUAL_LAB_V4.mp4 build
python3 deliver_v4.py comparar build/DIBURAMA_THERMOLINE_VENTANA_INVISIBLE_FINAL.mp4 build/DIBURAMA_THERMOLINE_VISUAL_LAB_V4.mp4 build
echo "OK V4 -> build/"

# ---- V5 «Visual Lab» con logotipo oficial (assets/DIBURAMA_logo_original_transparente_recortado.png) ----
REEL_SCENES=scenes_v5 REEL_CRF=17 python3 render.py build/video_v5.mp4
REEL_AUDIO=v5 python3 audio.py in/music.mp3 in/sfx build/audio_v5
ffmpeg -v error -y -i build/video_v5.mp4 -i build/audio_v5/master_mix.wav -map 0:v -map 1:a -c:v copy \
  -c:a aac -b:a 320k -ar 48000 -ac 2 -t 20 -movflags +faststart build/DIBURAMA_THERMOLINE_VISUAL_LAB_V5_FINAL.mp4
python3 deliver_v5.py hoja build/DIBURAMA_THERMOLINE_VISUAL_LAB_V5_FINAL.mp4 build
python3 deliver_v5.py comparar build/DIBURAMA_THERMOLINE_VISUAL_LAB_V4.mp4 build/DIBURAMA_THERMOLINE_VISUAL_LAB_V5_FINAL.mp4 build
echo "OK V5 -> build/"
