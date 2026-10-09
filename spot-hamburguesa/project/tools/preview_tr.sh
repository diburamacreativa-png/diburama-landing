#!/usr/bin/env bash
# FASE A previews: each rebuilt join rendered at 30 fps, then shown  V2 1× → V2 0.4× → V1 1× (for comparison).
set -euo pipefail
cd "$(dirname "$0")/../.."
W=renders/work; OUT=renders/V2_FASE_A; mkdir -p $W $OUT
FONT=/usr/share/fonts/truetype/dejavu/DejaVuSansMono-Bold.ttf
declare -A WIN=( [T1]="2.3 4.5" [T2]="6.6 8.4" [T3]="9.9 11.5" [T4]="12.7 14.6" )
declare -A NAME=( [T1]="T1_HAMBURGUESA_A_CORTEZA" [T2]="T2_RODAJE_A_QUESO" [T3]="T3_QUESO_A_MECANISMO" [T4]="T4_METAL_A_ILUSTRACION" )
for T in ${ONLY:-T1 T2 T3 T4}; do
  read A B <<< "${WIN[$T]}"
  python3 project/tools/engine.py --fps 30 --start $A --end $B --workers 4 --out $W/prev_$T.mkv
  LBL="drawtext=fontfile=$FONT:fontsize=26:fontcolor=white@0.9:box=1:boxcolor=black@0.5:boxborderw=8:x=24:y=24"
  ffmpeg -y -v error -i $W/prev_$T.mkv -i $W/V1_LOCK_pic_30.mkv -filter_complex "
    [0:v]scale=out_color_matrix=bt709:out_range=tv,split=2[a][b];
    [a]$LBL:text='V2  $T  1x   %{pts\:hms}',setpts=PTS-STARTPTS[v1];
    [b]setpts=2.5*(PTS-STARTPTS),$LBL:text='V2  $T  0.4x',fps=30[v2];
    [1:v]trim=start=$A:end=$B,setpts=PTS-STARTPTS,scale=out_color_matrix=bt709:out_range=tv,$LBL:text='V1 (anterior)  1x'[v3];
    [v1][v2][v3]concat=n=3:v=1:a=0,scale=720:1280:flags=lanczos,format=yuv420p[o]" -map "[o]" \
    -c:v libx264 -preset slow -crf 17 -r 30 -movflags +faststart $OUT/DIBURAMA_V2_PREVIEW_${NAME[$T]}.mp4
done
ls -la $OUT
