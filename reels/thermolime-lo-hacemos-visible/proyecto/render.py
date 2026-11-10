# Render del máster de vídeo (sin audio) directo a H.264 alta calidad (CRF 18, techo 16 Mbps)
# uso:  python3 render.py out_video.mp4            (500 fotogramas)
#       python3 render.py --frames 0,42,100 dir/   (PNG de control)
import sys, os, subprocess, time
import numpy as np, cv2
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from lib import W, H, FPS
import importlib
scenes = importlib.import_module(os.environ.get('REEL_SCENES', 'scenes'))

def to8(img): return (np.clip(img, 0, 1) * 255 + 0.5).astype(np.uint8)

def main():
    if sys.argv[1] == '--frames':
        out = sys.argv[3]; os.makedirs(out, exist_ok=True)
        for f in [int(x) for x in sys.argv[2].split(',')]:
            cv2.imwrite(f"{out}/f{f:03d}.png", to8(scenes.render_frame(f)))
        return
    out = sys.argv[1]
    n = int(os.environ.get('NFRAMES', 500))
    cmd = ["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "bgr24", "-s", f"{W}x{H}", "-r", str(FPS),
           "-i", "-", "-c:v", "libx264", "-preset", "slow", "-crf", os.environ.get("REEL_CRF", "18"), "-maxrate", "16M", "-bufsize", "32M", "-profile:v", "high", "-level", "4.2",
           "-pix_fmt", "yuv420p", "-color_primaries", "bt709", "-color_trc", "bt709", "-colorspace", "bt709",
           "-x264-params", "keyint=25:min-keyint=1", "-movflags", "+faststart", out]
    p = subprocess.Popen(cmd, stdin=subprocess.PIPE)
    t0 = time.time()
    for f in range(n):
        p.stdin.write(to8(scenes.render_frame(f)).tobytes())
        if f % 50 == 0: print(f"frame {f}  {time.time()-t0:.0f}s", flush=True)
    p.stdin.close(); p.wait()
    print("done", time.time() - t0)

if __name__ == '__main__': main()
