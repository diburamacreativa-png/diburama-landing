#!/usr/bin/env bash
# DIBURAMA spot hamburguesa — full reproducible build.
#   project/tools/build.sh            → audio + 24 fps + 30 fps masters + preview + QA
# Intermediates (lossless FFV1) go to renders/work/ (git-ignored).
set -euo pipefail
cd "$(dirname "$0")/../.."
W=renders/work; mkdir -p $W renders qa
python3 audio/sound_design.py
AUDIO=audio/DIBURAMA_HAMBURGUESA_MIX_48k.wav
X264="-c:v libx264 -preset slow -crf 18 -maxrate 25M -bufsize 50M -tune film -profile:v high -pix_fmt yuv420p -color_primaries bt709 -color_trc bt709 -colorspace bt709 -color_range tv"
AAC="-c:a aac -b:a 320k -ar 48000 -ac 2"
for FPS in 24 30; do
  python3 project/tools/engine.py --fps $FPS --out $W/pic_${FPS}.mkv
  ffmpeg -y -v error -i $W/pic_${FPS}.mkv -i $AUDIO -map 0:v -map 1:a \
    -vf "scale=out_color_matrix=bt709:out_range=tv,format=yuv420p" $X264 -r $FPS $AAC -shortest -movflags +faststart \
    renders/DIBURAMA_HAMBURGUESA_MASTER_9x16_${FPS}FPS.mp4
done
# variant with the micro-descriptor "Vídeos para empresas" (only the end card is re-rendered)
DIBURAMA_DESCRIPTOR=1 python3 project/tools/engine.py --fps 30 --start 19.792 --end 25 --workers 2 --out $W/gfx_desc_30.mkv
ffmpeg -y -v error -i $W/pic_30.mkv -frames:v 594 -c copy $W/head_30.mkv
printf "file '%s'\nfile '%s'\n" "$PWD/$W/head_30.mkv" "$PWD/$W/gfx_desc_30.mkv" > $W/desc.txt
ffmpeg -y -v error -f concat -safe 0 -i $W/desc.txt -i $AUDIO -map 0:v -map 1:a $X264 $AAC -shortest -movflags +faststart \
  renders/DIBURAMA_HAMBURGUESA_MASTER_9x16_30FPS_VARIANTE_DESCRIPTOR.mp4
# preview for human review: 720p, burnt-in timecode + frame number
ffmpeg -y -v error -i renders/DIBURAMA_HAMBURGUESA_MASTER_9x16_30FPS.mp4 \
  -vf "scale=720:1280:flags=lanczos,drawtext=fontfile=/usr/share/fonts/truetype/dejavu/DejaVuSansMono-Bold.ttf:text='PREVIEW  %{pts\:hms}  f%{frame_num}':x=16:y=16:fontsize=22:fontcolor=white@0.85:box=1:boxcolor=black@0.45:boxborderw=6" \
  -c:v libx264 -preset medium -crf 23 -pix_fmt yuv420p -c:a aac -b:a 160k -movflags +faststart renders/DIBURAMA_HAMBURGUESA_PREVIEW.mp4
python3 project/tools/qa_strips.py renders/DIBURAMA_HAMBURGUESA_MASTER_9x16_30FPS.mp4 qa/transitions_30fps --fps 30 \
  --sheet renders/DIBURAMA_HAMBURGUESA_CONTACT_SHEET.jpg
python3 project/tools/qa_strips.py renders/DIBURAMA_HAMBURGUESA_MASTER_9x16_24FPS.mp4 qa/transitions_24fps --fps 24
python3 project/tools/audio_qa.py $AUDIO qa/audio_analysis.png
echo "build done"
