#!/usr/bin/env bash
# Encode the 16-bit PNG frames (build/frames) into the delivery files.
set -euo pipefail
cd "$(dirname "$0")/.."
IN=build/frames/f%03d.png
mkdir -p out
# H.264 delivery (social): BT.709, limited range, 4:2:0, high quality, faststart
ffmpeg -y -v error -framerate 25 -i "$IN" \
  -vf "scale=out_color_matrix=bt709:out_range=tv:flags=accurate_rnd+full_chroma_int+bicubic,format=yuv420p" \
  -c:v libx264 -preset veryslow -crf 12 -profile:v high -level 4.2 -x264-params "aq-mode=3:deblock=-1,-1" \
  -color_primaries bt709 -color_trc bt709 -colorspace bt709 -color_range tv \
  -movflags +faststart -an out/Alsina_Reel_Final_1080x1920.mp4
# ProRes 422 HQ 10-bit master
ffmpeg -y -v error -framerate 25 -i "$IN" \
  -vf "scale=out_color_matrix=bt709:out_range=tv:flags=accurate_rnd+full_chroma_int+bicubic,format=yuv422p10le" \
  -c:v prores_ks -profile:v 3 -vendor apl0 -bits_per_mb 8000 \
  -color_primaries bt709 -color_trc bt709 -colorspace bt709 -color_range tv \
  -an build/Alsina_Reel_Master.mov
# control frames from the delivered MP4
mkdir -p out/control_frames
for t in 0.50 1.50 2.75 3.35 3.85 5.00; do
  ffmpeg -y -v error -i out/Alsina_Reel_Final_1080x1920.mp4 -vf "select='eq(n\,$(python3 -c "print(round($t*25))"))'" -frames:v 1 "out/control_frames/control_t${t}s.png"
done
ls -la out out/control_frames build/Alsina_Reel_Master.mov
