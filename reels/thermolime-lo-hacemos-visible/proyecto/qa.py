# Control de calidad del máster final
# uso: python3 qa.py final.mp4 audio_report.json
import sys, json, subprocess, re
import numpy as np

def run(cmd): return subprocess.run(cmd, capture_output=True, text=True)

def main(mp4, rep_path):
    R = {}
    pr = json.loads(run(["ffprobe", "-v", "error", "-count_frames", "-show_streams", "-show_format", "-of", "json", mp4]).stdout)
    v = [s for s in pr['streams'] if s['codec_type'] == 'video'][0]; a = [s for s in pr['streams'] if s['codec_type'] == 'audio']
    R['video'] = dict(codec=v['codec_name'], profile=v.get('profile'), size=f"{v['width']}x{v['height']}", fps=v['r_frame_rate'],
                      pix_fmt=v['pix_fmt'], frames=int(v['nb_read_frames']), duration=float(v['duration']), start=float(v.get('start_time', 0)))
    if a:
        a = a[0]; R['audio'] = dict(codec=a['codec_name'], sr=a['sample_rate'], ch=a['channels'], duration=float(a['duration']),
                                    start=float(a.get('start_time', 0)), bitrate=a.get('bit_rate'))
    R['container_duration'] = float(pr['format']['duration'])
    # decodificación completa estricta
    e = run(["ffmpeg", "-v", "error", "-xerror", "-i", mp4, "-f", "null", "-"])
    R['decode_errors'] = e.stderr.strip() or "ninguno"
    # luminancia por fotograma + diferencias (detección de cortes)
    raw = subprocess.run(["ffmpeg", "-v", "error", "-i", mp4, "-vf", "scale=108:192", "-f", "rawvideo", "-pix_fmt", "gray", "-"],
                         capture_output=True).stdout
    fr = np.frombuffer(raw, np.uint8).reshape(-1, 192, 108).astype(np.float32)
    luma = fr.mean((1, 2)) / 255
    R['min_mean_luma'] = dict(value=round(float(luma.min()), 3), frame=int(luma.argmin()))
    R['frames_below_4pct_luma'] = [int(i) for i in np.where(luma < 0.04)[0]]
    d = np.abs(np.diff(fr, axis=0)).mean((1, 2))
    cuts = [int(i + 1) for i in np.where(d > 22)[0]]
    R['detected_cuts_frames'] = cuts
    if a:
        el = run(["ffmpeg", "-nostats", "-i", mp4, "-map", "0:a", "-af", "ebur128=peak=true", "-f", "null", "-"]).stderr
        summ = el[el.rfind('Summary'):]
        R['loudness'] = dict(I_LUFS=float(re.search(r'I:\s+(-?[\d.]+)', summ).group(1)),
                             LRA=float(re.search(r'LRA:\s+(-?[\d.]+)', summ).group(1)),
                             true_peak_dBTP=float(re.search(r'Peak:\s+(-?[\d.]+)', summ).group(1)))
        pcm = subprocess.run(["ffmpeg", "-v", "error", "-i", mp4, "-map", "0:a", "-f", "f32le", "-ac", "2", "-ar", "48000", "-"],
                             capture_output=True).stdout
        x = np.frombuffer(pcm, np.float32).reshape(-1, 2).astype(np.float64)
        R['audio_samples_s'] = len(x) / 48000
        R['stereo_corr'] = round(float(np.corrcoef(x[:, 0], x[:, 1])[0, 1]), 3)
        mono = x.mean(1)
        R['mono_vs_stereo_rms_db'] = round(10 * np.log10((mono ** 2).mean() / ((x ** 2).mean() + 1e-12)), 2)
        R['clipped_samples'] = int((np.abs(x) >= 0.999).sum())
    rep = json.load(open(rep_path)); cues = rep['cues']
    R['cue_vs_cut'] = {k: dict(audio_s=round(t, 3), frame=int(t * 25 + 1e-6)) for k, t in cues.items()}
    print(json.dumps(R, indent=1, ensure_ascii=False))

if __name__ == '__main__': main(*sys.argv[1:3])
