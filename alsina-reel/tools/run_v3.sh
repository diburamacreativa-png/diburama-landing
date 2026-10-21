#!/usr/bin/env bash
# v3 pipeline (new opening shot). Requires the v2 frames in build/frames (tools/run_all.sh).
set -euo pipefail
cd "$(dirname "$0")/.."
mkdir -p build/inicio_frames build/frames_v3
ffmpeg -y -v error -i assets/source/Plano_inicio_zoom_out.mp4 -vsync 0 -q:v 1 -qmin 1 build/inicio_frames/f%03d.jpg
python3 tools/analyze_inicio.py
python3 tools/analyze_v3_join.py
python3 tools/reel_v3.py --frames 0:44 --out build/frames_v3 & python3 tools/reel_v3.py --frames 44:69 --out build/frames_v3 & wait
bash tools/encode_v3.sh
