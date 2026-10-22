#!/usr/bin/env python3
"""Banda sonora de VIDEO REEL CHILE_DEMO 5 (38,68 s). El video NO se toca.

Uso:
  python3 -I build_demo5.py --music "Groovy Good Vibes.mp3" --pack <pack_dir> \
      --video "VIDEO REEL CHILE_DEMO 5.mp4" --out <out_dir>
"""
import argparse, json, math, os, subprocess, sys
import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import build_audio as B  # noqa: E402  (motor comun: render, calibracion, ducking, limitador)
import music_demo5 as M  # noqa: E402
from cues_demo5 import CUES, DUCKS  # noqa: E402

SR = M.SR
N = M.N
B.N = N  # el motor comun dimensiona sus envolventes con N
TARGET_LUFS = -14.0
CEILING_DBTP = -1.0
MAX_LIMIT_GR_DB = 1.0


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--music", required=True)
    ap.add_argument("--pack", required=True)
    ap.add_argument("--video", required=True)
    ap.add_argument("--out", required=True)
    args = ap.parse_args()
    os.makedirs(args.out, exist_ok=True)

    print("[1] reedicion musical")
    music, minfo = M.build(B.decode(args.music), B.ffmpeg_filter)

    print("[2] SFX")
    sfx = np.zeros((N + 2 * SR, 2))
    send = np.zeros((N + 2 * SR, 2))
    log = []
    for c in CUES:
        x = B.render_cue(args.pack, c)
        k = B.anchor_offset(x, c["mode"])
        start = int(round(c["t"] * SR)) - k
        if c["mode"] == "attack" or len(x) < int(0.3 * SR):
            lm = B.music_level_db(music, c["t"])
        else:
            lm = B.music_level_span(music, start, start + len(x))
        gain_db = lm + c["rel"] - B.sfx_level_db(x)
        gl, gr = B.pan_gains(c["pan"])
        y = x * 10 ** (gain_db / 20)
        y[:, 0] *= gl
        y[:, 1] *= gr
        a = max(0, start)
        y = y[a - start:]
        b = min(len(sfx), a + len(y))
        sfx[a:b] += y[: b - a]
        if c.get("verb") is not None:
            send[a:b] += y[: b - a] * 10 ** (c["verb"] / 20)
        log.append(dict(id=c["id"], start_s=round(start / SR, 4), end_s=round((start + len(x)) / SR, 4),
                        event_s=round(c["t"], 4), frame=round(c["t"] * 25, 2), file=c["file"], mode=c["mode"],
                        rel_db=c["rel"], gain_db=round(gain_db, 2), pan=c["pan"], st=c["st"], eq=c["eq"],
                        design=",".join(k for k in ("rev", "stretch", "pitch_env", "lp_env", "hp_env", "amp_env",
                                                    "pan_env", "width_env", "verb") if c.get(k) is not None),
                        note=c["note"], dur_s=round(len(x) / SR, 3)))
        print(f"  {c['id']} t={c['t']:6.3f} start={start / SR:6.3f} gain={gain_db:+6.1f} dB  {os.path.basename(c['file'])}")
    sfx += B.convolve(send, B.resonance_ir())
    tail = float(np.abs(sfx[N:]).max())
    sfx = sfx[:N]

    print("[3] ducking por bandas")
    low, mid, high = B.split3(music)
    music_d = (low * B.duck_env(DUCKS, 0)[:, None] + mid * B.duck_env(DUCKS, 1)[:, None]
               + high * B.duck_env(DUCKS, 2)[:, None])

    # fundido final sincronizado con el fundido a negro del video (f956-f965)
    fade = np.ones(N)
    a = int(M.VIDEO_FADE[0] * SR)
    b = int((M.VIDEO_FADE[0] + M.VIDEO_FADE[1]) * SR)
    fade[a:b] = 0.5 * (1 + np.cos(np.linspace(0, np.pi, b - a)))
    fade[b:] = 0
    music_d *= fade[:, None]
    sfx *= fade[:, None]
    music_nd = music * fade[:, None]
    mix = music_d + sfx

    print("[4] master")
    I0, _, TP0 = B.loudness(mix)
    gain = TARGET_LUFS - I0
    mix_g = mix * 10 ** (gain / 20)
    I1, LRA1, TP1 = B.loudness(mix_g)
    gr = 0.0
    if TP1 > CEILING_DBTP - 0.15:
        need = TP1 - (CEILING_DBTP - 0.25)
        if need > MAX_LIMIT_GR_DB:
            gain -= need - MAX_LIMIT_GR_DB
            mix_g = mix * 10 ** (gain / 20)
        mix_g, gr = B.true_peak_limit(mix_g, CEILING_DBTP - 0.25)
    I2, LRA2, TP2 = B.loudness(mix_g)
    music_stem = music_d * 10 ** (gain / 20)
    sfx_stem = sfx * 10 ** (gain / 20)
    res = mix_g - (music_stem + sfx_stem)
    lim_time = float(np.argmax(np.abs(res).max(1)) / SR)

    print("[5] exportar")
    o = args.out
    pre = "ALSINA_DEMO5"
    B.write_wav(os.path.join(o, f"{pre}_MEZCLA_FINAL_48k24.wav"), mix_g)
    B.write_wav(os.path.join(o, f"{pre}_MUSICA_STEM_48k24.wav"), music_stem)
    B.write_wav(os.path.join(o, f"{pre}_SFX_STEM_48k24.wav"), sfx_stem)
    B.write_wav(os.path.join(o, f"{pre}_MUSICA_EDIT_SIN_DUCKING_48k24.wav"), music_nd * 10 ** (gain / 20))
    mp4 = os.path.join(o, "ALSINA_REEL_CHILE_DEMO5_FINAL.mp4")
    # imagen copiada sin recodificar
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", args.video, "-f", "f32le", "-ar", str(SR), "-ac", "2",
                    "-i", "-", "-map", "0:v:0", "-map", "1:a:0", "-c:v", "copy", "-c:a", "aac", "-b:a", "320k",
                    "-ar", "48000", "-movflags", "+faststart", mp4],
                   input=mix_g.astype(np.float32).tobytes(), check=True)

    stats = dict(music=minfo, pre_gain_lufs=I0, master_gain_db=gain, after_gain=dict(I=I1, LRA=LRA1, TP=TP1),
                 final=dict(I=I2, LRA=LRA2, TP=TP2), limiter_max_gr_db=round(gr, 2), limiter_max_change_at_s=lim_time,
                 limiter_max_change_dbfs=20 * math.log10(np.abs(res).max() + 1e-12),
                 sfx_tail_beyond_end_peak=tail, music_stem=B.loudness(music_stem), sfx_stem=B.loudness(sfx_stem))
    with open(os.path.join(o, "build_stats_demo5.json"), "w") as f:
        json.dump(dict(stats=stats, cues=log, ducks=DUCKS), f, ensure_ascii=False, indent=1)
    print(json.dumps(stats, indent=1))


if __name__ == "__main__":
    main()
