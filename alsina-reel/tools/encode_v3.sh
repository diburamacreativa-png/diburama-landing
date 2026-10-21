#!/usr/bin/env bash
# v3: frames 0..68 from the new opening render, 69..159 are the untouched v2 frames (white dot onwards).
set -euo pipefail
cd "$(dirname "$0")/.."
D=build/frames_v3_full; rm -rf $D; mkdir -p $D
for k in $(seq 0 159); do
  f=$(printf 'f%03d.png' $k)
  if [ $k -le 68 ]; then ln -s ../frames_v3/$f $D/$f; else ln -s ../frames/$f $D/$f; fi
done
IN=$D/f%03d.png
ffmpeg -y -v error -framerate 25 -i "$IN" \
  -vf "scale=out_color_matrix=bt709:out_range=tv:flags=accurate_rnd+full_chroma_int+bicubic,format=yuv420p" \
  -c:v libx264 -preset veryslow -crf 12 -profile:v high -level 4.2 -x264-params "aq-mode=3:deblock=-1,-1" \
  -color_primaries bt709 -color_trc bt709 -colorspace bt709 -color_range tv \
  -movflags +faststart -an out/Alsina_Reel_v3_1080x1920.mp4
ffmpeg -y -v error -framerate 25 -i "$IN" \
  -vf "scale=out_color_matrix=bt709:out_range=tv:flags=accurate_rnd+full_chroma_int+bicubic,format=yuv422p10le" \
  -c:v prores_ks -profile:v 3 -vendor apl0 -color_primaries bt709 -color_trc bt709 -colorspace bt709 -color_range tv \
  -an build/Alsina_Reel_v3_Master.mov
ls -la out/Alsina_Reel_v3_1080x1920.mp4 build/Alsina_Reel_v3_Master.mov
