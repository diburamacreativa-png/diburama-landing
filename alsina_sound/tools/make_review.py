#!/usr/bin/env python3
"""Genera versiones de REVISION (no master): video + n.º de fotograma + cue activo +
formas de onda de musica (gris) y SFX (naranja) con cursor, a 1x y al 50 %.

Uso: python3 -I make_review.py --video <mp4 original> --out <dir con los stems>
     [--dur 38.68 --prefix ALSINA_DEMO5 --stats build_stats_demo5.json --tag DEMO5]
"""
import argparse, json, os, subprocess

FONT = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
MONO = "/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf"
DUR = 25.24  # por defecto: reel de 25,24 s; --dur lo cambia


def esc(s):
    return (s.replace("\\", "\\\\").replace(":", "\\:").replace("'", "’")
            .replace(",", "\\,").replace("%", "\\%"))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--video", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--dur", type=float, default=DUR)
    ap.add_argument("--prefix", default="ALSINA_REEL")
    ap.add_argument("--stats", default="build_stats.json")
    ap.add_argument("--tag", default="ALSINA")
    a = ap.parse_args()
    o = a.out
    dur = a.dur
    cues = json.load(open(os.path.join(o, a.stats)))["cues"]
    W, H, P = 540, 960, 220
    labels = []
    for i, c in enumerate(cues):
        t = c["event_s"]
        name = os.path.basename(c["file"])[:-4]
        txt = esc(f"{c['id']} f{c['frame']:g}  {name}")
        y = H + 142 + (i % 4) * 19
        labels.append(f"drawtext=fontfile={MONO}:text='{txt}':x=8:y={y}:fontsize=15:fontcolor=white:"
                      f"enable='between(t,{t - 0.12:.3f},{t + 0.45:.3f})'")
    ticks = "".join(f",drawbox=x={c['event_s'] / dur * W:.1f}:y={H + 4}:w=1:h=8:color=yellow@0.9:t=fill"
                    for c in cues)
    fc = (
        f"[0:v]scale={W}:{H},pad={W}:{H + P}:0:0:color=0x111111[v];"
        f"[1:a]showwavespic=s={W}x60:colors=0x9a9a9a:scale=sqrt[wm];"
        f"[2:a]showwavespic=s={W}x60:colors=0xff8c1a:scale=sqrt[ws];"
        f"[v][wm]overlay=0:{H + 14}[v1];[v1][ws]overlay=0:{H + 78}{ticks}[v2];"
        f"color=c=white:s=2x128:r=25[ph];[v2][ph]overlay=x='t/{dur}*{W}':y={H + 12}:shortest=1[v3];"
        f"[v3]drawtext=fontfile={MONO}:text='f%{{eif\\:n\\:d}}  %{{pts\\:hms}}':x=8:y=8:fontsize=26:"
        f"fontcolor=yellow:box=1:boxcolor=black@0.6,"
        f"drawtext=fontfile={FONT}:text='REVISION - no es master':x=w-tw-8:y=8:fontsize=18:fontcolor=white:"
        f"box=1:boxcolor=red@0.7," + ",".join(labels) + "[vo]"
    )
    r1 = os.path.join(o, f"REVISION_1x_{a.tag}_sync.mp4")
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", a.video,
                    "-i", os.path.join(o, f"{a.prefix}_MUSICA_STEM_48k24.wav"),
                    "-i", os.path.join(o, f"{a.prefix}_SFX_STEM_48k24.wav"),
                    "-i", os.path.join(o, f"{a.prefix}_MEZCLA_FINAL_48k24.wav"),
                    "-filter_complex", fc, "-map", "[vo]", "-map", "3:a",
                    "-c:v", "libx264", "-preset", "medium", "-crf", "22", "-pix_fmt", "yuv420p",
                    "-c:a", "aac", "-b:a", "192k", "-t", str(dur), r1], check=True)
    r2 = os.path.join(o, f"REVISION_50pct_{a.tag}_sync.mp4")
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", r1, "-filter_complex",
                    "[0:v]setpts=2*PTS,fps=25[v];[0:a]rubberband=tempo=0.5:transients=crisp[a]",
                    "-map", "[v]", "-map", "[a]", "-c:v", "libx264", "-preset", "medium", "-crf", "22",
                    "-pix_fmt", "yuv420p", "-c:a", "aac", "-b:a", "192k", r2], check=True)
    print(r1, r2)


if __name__ == "__main__":
    main()
