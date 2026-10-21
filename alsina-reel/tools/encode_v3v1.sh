#!/usr/bin/env bash
# v3 opening + v1 finale: frames 0..43 = v3 opening (footage only, identical for both finales),
# 44..70 = new render with the v1 curves (ALSINA_BASE=v1), 71..159 = untouched v1 frames.
set -euo pipefail
cd "$(dirname "$0")/.."
D=build/frames_v3v1_full; rm -rf $D; mkdir -p $D
for k in $(seq 0 159); do
  f=$(printf 'f%03d.png' $k)
  if [ $k -le 43 ]; then ln -s ../frames_v3/$f $D/$f
  elif [ $k -le 70 ]; then ln -s ../frames_v3v1/$f $D/$f
  else ln -s ../frames_v1/$f $D/$f; fi
done
ffmpeg -y -v error -framerate 25 -i $D/f%03d.png \
  -vf "scale=out_color_matrix=bt709:out_range=tv:flags=accurate_rnd+full_chroma_int+bicubic,format=yuv420p" \
  -c:v libx264 -preset veryslow -crf 12 -profile:v high -level 4.2 -x264-params "aq-mode=3:deblock=-1,-1" \
  -color_primaries bt709 -color_trc bt709 -colorspace bt709 -color_range tv \
  -movflags +faststart -an out/Alsina_Reel_v3_final_v1_1080x1920.mp4
ls -la out/Alsina_Reel_v3_final_v1_1080x1920.mp4
