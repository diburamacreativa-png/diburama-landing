#!/usr/bin/env bash
# V2 picture: 0–15 s rendered with the V2 edit, 15 s → end spliced bit-exact from the approved V1 frames.
set -euo pipefail
cd "$(dirname "$0")/../.."
W=renders/work
python3 project/tools/engine.py --fps 30 --start 0 --end 15 --workers 4 --out $W/v2_head_30.mkv
ffmpeg -y -v error -i $W/V1_LOCK_pic_30.mkv -vf "select=gte(n\,450),setpts=PTS-STARTPTS" -c:v ffv1 -level 3 -pix_fmt yuv444p $W/v1_tail_30.mkv
printf "file '%s'\nfile '%s'\n" "$PWD/$W/v2_head_30.mkv" "$PWD/$W/v1_tail_30.mkv" > $W/v2.txt
ffmpeg -y -v error -f concat -safe 0 -i $W/v2.txt -c copy $W/V2_pic_30.mkv
ffprobe -v error -count_frames -show_entries stream=nb_read_frames -of csv=p=0 $W/V2_pic_30.mkv
