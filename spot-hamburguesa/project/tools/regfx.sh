#!/usr/bin/env bash
# Re-render only the end card (t >= graphics.start) and the audio, then re-mux masters.
set -euo pipefail
cd "$(dirname "$0")/../.."
W=renders/work
python3 audio/sound_design.py
AUDIO=audio/DIBURAMA_HAMBURGUESA_MIX_48k.wav
X264="$(grep '^X264=' project/tools/build.sh | sed 's/^X264=//; s/"//g')"
AAC="-c:a aac -b:a 320k -ar 48000 -ac 2"
for FPS in 24 30; do
  HEAD=$(python3 -c "import json;print(round(json.load(open('project/edit_decisions.json'))['graphics']['start']*$FPS))")
  for D in 0 1; do
    [[ $FPS == 24 && $D == 1 ]] && continue
    DIBURAMA_DESCRIPTOR=$D python3 project/tools/engine.py --fps $FPS --start $(python3 -c "print($HEAD/$FPS)") --end 25 --workers 4 --out $W/gfx_${FPS}_$D.mkv
  done
  ffmpeg -y -v error -i $W/pic_${FPS}.mkv -frames:v $HEAD -c copy $W/head_${FPS}.mkv
  printf "file '%s'\nfile '%s'\n" "$PWD/$W/head_${FPS}.mkv" "$PWD/$W/gfx_${FPS}_0.mkv" > $W/l_${FPS}.txt
  ffmpeg -y -v error -f concat -safe 0 -i $W/l_${FPS}.txt -c copy $W/pic_${FPS}_new.mkv && mv $W/pic_${FPS}_new.mkv $W/pic_${FPS}.mkv
  ffmpeg -y -v error -i $W/pic_${FPS}.mkv -i $AUDIO -map 0:v -map 1:a -vf "scale=out_color_matrix=bt709:out_range=tv,format=yuv420p" $X264 -r $FPS $AAC -shortest -movflags +faststart renders/DIBURAMA_HAMBURGUESA_MASTER_9x16_${FPS}FPS.mp4
done
printf "file '%s'\nfile '%s'\n" "$PWD/$W/head_30.mkv" "$PWD/$W/gfx_30_1.mkv" > $W/desc.txt
ffmpeg -y -v error -f concat -safe 0 -i $W/desc.txt -i $AUDIO -map 0:v -map 1:a $X264 $AAC -shortest -movflags +faststart renders/DIBURAMA_HAMBURGUESA_MASTER_9x16_30FPS_VARIANTE_DESCRIPTOR.mp4
ffmpeg -y -v error -i renders/DIBURAMA_HAMBURGUESA_MASTER_9x16_30FPS.mp4 \
  -vf "scale=720:1280:flags=lanczos,drawtext=fontfile=/usr/share/fonts/truetype/dejavu/DejaVuSansMono-Bold.ttf:text='PREVIEW  %{pts\:hms}  f%{frame_num}':x=16:y=16:fontsize=22:fontcolor=white@0.85:box=1:boxcolor=black@0.45:boxborderw=6" \
  -c:v libx264 -preset medium -crf 23 -pix_fmt yuv420p -c:a aac -b:a 160k -movflags +faststart renders/DIBURAMA_HAMBURGUESA_PREVIEW.mp4
python3 project/tools/qa_strips.py renders/DIBURAMA_HAMBURGUESA_MASTER_9x16_30FPS.mp4 qa/transitions_30fps --fps 30 --sheet renders/DIBURAMA_HAMBURGUESA_CONTACT_SHEET.jpg
python3 project/tools/qa_strips.py renders/DIBURAMA_HAMBURGUESA_MASTER_9x16_24FPS.mp4 qa/transitions_24fps --fps 24
python3 project/tools/audio_qa.py $AUDIO qa/audio_analysis.png
echo "regfx done"
