#!/usr/bin/env bash
# Full reproducible pipeline: sources -> analysis -> render -> encode.
# Requirements: ffmpeg (libx264, prores_ks), python3 with numpy, opencv-python-headless, scipy.
set -euo pipefail
cd "$(dirname "$0")/.."
mkdir -p build/pano_frames build/frames
ffmpeg -y -v error -i assets/source/pano.mp4 -frames:v 256 -q:v 1 -qmin 1 build/pano_frames/f%03d.jpg
python3 tools/analyze_video_motion.py 252
python3 tools/reel.py --frames 0:70 & python3 tools/reel.py --frames 70:160 & wait
bash tools/encode.sh
