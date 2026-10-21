#!/usr/bin/env python3
"""Construye la banda sonora final del reel ALSINA CHILE.

Uso:
  python3 -I build_audio.py --music "Groovy Good Vibes.mp3" --pack <pack_dir> \
      --video Alsina_Reel_Chile_ref_01.mp4 --out <out_dir> [--work <tmp_dir>]

Requiere numpy y ffmpeg (con rubberband). Todo el procesado es determinista.
"""
import argparse, json, math, os, subprocess, sys
import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from cues import CUES, DUCKS  # noqa: E402

SR = 48000
DUR = 25.24
N = int(round(DUR * SR))  # 1 211 520 muestras = 631 fotogramas exactos

# ---- Edicion musical (ver informe) ----
MUSIC_IN = 122.128      # s en el MP3 original -> fotograma 0
TEMPO = 1.00552         # +0,55 % de tempo (rubberband, tono intacto)
PREROLL = 0.5           # s de pre-roll para que rubberband arranque estable
TAIL_FADE = (24.94, 0.30)  # fundido de la cola de reverb residual (-43 dBFS)
TARGET_LUFS = -14.0
CEILING_DBTP = -1.0


def run(cmd, **kw):  # noqa
    return subprocess.run(cmd, check=True, capture_output=True, text=True, **kw)


def decode(path, extra_af=None):
    cmd = ["ffmpeg", "-v", "error", "-i", path, "-map", "0:a:0"]
    if extra_af:
        cmd += ["-af", extra_af]
    cmd += ["-ar", str(SR), "-ac", "2", "-f", "f32le", "-"]
    out = subprocess.run(cmd, check=True, capture_output=True).stdout
    return np.frombuffer(out, np.float32).reshape(-1, 2).astype(np.float64)


def ffmpeg_filter(x, af):
    p = subprocess.run(["ffmpeg", "-v", "error", "-f", "f32le", "-ar", str(SR), "-ac", "2", "-i", "-",
                        "-af", af, "-f", "f32le", "-"], input=x.astype(np.float32).tobytes(),
                       check=True, capture_output=True)
    return np.frombuffer(p.stdout, np.float32).reshape(-1, 2).astype(np.float64)


def write_wav(path, x, codec="pcm_s24le"):
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-f", "f32le", "-ar", str(SR), "-ac", "2", "-i", "-",
                    "-c:a", codec, path], input=x.astype(np.float32).tobytes(), check=True)


# ---- Ponderacion K (ITU-R BS.1770, 48 kHz) ----
def biquad(x, b, a):
    y = np.empty_like(x)
    z1 = z2 = 0.0
    b0, b1, b2 = b
    _, a1, a2 = a
    for i, v in enumerate(x.tolist()):
        o = b0 * v + z1
        z1 = b1 * v - a1 * o + z2
        z2 = b2 * v - a2 * o
        y[i] = o
    return y


KB1, KA1 = (1.53512485958697, -2.69169618940638, 1.19839281085285), (1, -1.69065929318241, 0.73248077421585)
KB2, KA2 = (1.0, -2.0, 1.0), (1, -1.99004745483398, 0.99007225036621)


def kpower(x):
    """Potencia ponderada K sumada por canal (muestra a muestra)."""
    p = np.zeros(len(x))
    for c in range(2):
        y = biquad(biquad(x[:, c], KB1, KA1), KB2, KA2)
        p += y * y
    return p


def sfx_level_db(x):
    p = kpower(np.vstack([x, np.zeros((SR // 10, 2))]))
    w = SR // 10
    c = np.convolve(p, np.ones(w) / w, "valid")
    return 10 * math.log10(c.max() + 1e-20)


def music_level_db(music, t):
    a = max(0, int((t - 1.0) * SR))
    b = min(len(music), int((t + 0.25) * SR))
    p = kpower(music[a:b])
    i0 = int((t - 0.2) * SR) - a
    i1 = int((t + 0.2) * SR) - a
    i0 = max(i0, int(0.05 * SR))
    return 10 * math.log10(p[i0:i1].mean() + 1e-20)


# ---- Edicion musical ----
def build_music(mp3):
    full = decode(mp3)
    s = int(round((MUSIC_IN - PREROLL) * SR))
    e = int(round((MUSIC_IN + DUR * TEMPO + 1.0) * SR))
    seg = full[s:e]
    st = ffmpeg_filter(seg, f"rubberband=tempo={TEMPO}:transients=crisp:detector=compound:phase=laminar:"
                            "window=standard:pitchq=quality:channels=together")
    off = int(round(PREROLL / TEMPO * SR))
    m = st[off:off + N].copy()
    fi = int(0.003 * SR)
    m[:fi] *= np.linspace(0, 1, fi)[:, None]
    a = int(TAIL_FADE[0] * SR)
    m[a:] *= (0.5 * (1 + np.cos(np.linspace(0, np.pi, N - a))))[:, None]
    return m


def split_bands(x, fc=160.0, taps=4097):
    n = np.arange(taps) - (taps - 1) / 2
    h = 2 * fc / SR * np.sinc(2 * fc / SR * n) * np.blackman(taps)
    h /= h.sum()
    L = len(x) + taps - 1
    nf = 1 << (L - 1).bit_length()
    H = np.fft.rfft(h, nf)
    low = np.stack([np.fft.irfft(np.fft.rfft(x[:, c], nf) * H, nf)[(taps - 1) // 2:(taps - 1) // 2 + len(x)]
                    for c in range(2)], 1)
    return low, x - low


def duck_env(ducks, idx):
    g = np.zeros(N)
    t = np.arange(N) / SR
    for ev in ducks:
        t0, d = ev[0], ev[idx]
        att, hold, rel = 0.008, 0.09, 0.28
        env = np.zeros(N)
        a = (t >= t0 - 0.004) & (t < t0 - 0.004 + att)
        env[a] = (t[a] - (t0 - 0.004)) / att
        h = (t >= t0 - 0.004 + att) & (t < t0 + att + hold)
        env[h] = 1
        r = (t >= t0 + att + hold) & (t < t0 + att + hold + rel)
        env[r] = 0.5 * (1 + np.cos(np.pi * (t[r] - (t0 + att + hold)) / rel))
        g = np.minimum(g, d * env)
    return 10 ** (g / 20)


EQ = {
    # hits casi todo subgrave: limpiar el infra y abrir hueco al bajo funk
    "hit_sub": "highpass=f=42:poles=2,equalizer=f=70:t=q:w=1.0:g=-1.5,equalizer=f=200:t=q:w=1.0:g=3.5",
    "hit": "highpass=f=40:poles=2,equalizer=f=75:t=q:w=1.0:g=-1.0,equalizer=f=190:t=q:w=1.0:g=3",
    # pops: fuera graves que compiten con caja/guitarra
    "pop": "highpass=f=140:poles=2,equalizer=f=600:t=q:w=1.2:g=-2,equalizer=f=2800:t=q:w=1.0:g=3",
    "click": "highpass=f=300:poles=2",
    # aire: sin graves y un pelo menos de brillo para no tapar charles/guitarra
    "air": "highpass=f=180:poles=2,highshelf=f=9000:g=-1.5",
    "air_body": "highpass=f=90:poles=2,highshelf=f=9000:g=-1.5",
}


def render_cue(pack, c):
    path = os.path.join(pack, c["file"])
    af = []
    if c["st"]:
        r = 2 ** (c["st"] / 12)
        af.append(f"asetrate={SR * r:.3f},aresample={SR}")
    af.append(EQ[c["eq"]])
    x = decode(path, ",".join(af))
    if c["fade"]:
        fs, fd = c["fade"]
        a, b = int(fs * SR), int((fs + fd) * SR)
        if a < len(x):
            env = np.ones(len(x))
            env[a:b] = 0.5 * (1 + np.cos(np.linspace(0, np.pi, len(env[a:b]))))
            env[b:] = 0
            x = (x.T * env).T[:min(len(x), b)]
    return x


def anchor_offset(x, mode):
    m = np.abs(x).mean(1)
    if mode == "attack":
        w = int(0.002 * SR)
        e = np.convolve(m, np.ones(w) / w, "same")
        return int(np.argmax(e[: int(0.05 * SR)]))
    if mode == "peak":
        w = int(0.03 * SR)
        e = np.sqrt(np.convolve(m ** 2, np.ones(w) / w, "same"))
        return int(np.argmax(e))
    if mode == "end":
        return len(x)
    return 0


def pan_gains(p):
    th = (p + 1) * math.pi / 4
    return math.cos(th) * math.sqrt(2), math.sin(th) * math.sqrt(2)


def loudness(path_or_x):
    if isinstance(path_or_x, str):
        args = ["-i", path_or_x]
        inp = None
    else:
        args = ["-f", "f32le", "-ar", str(SR), "-ac", "2", "-i", "-"]
        inp = path_or_x.astype(np.float32).tobytes()
    p = subprocess.run(["ffmpeg", "-nostats", "-hide_banner"] + args + ["-af", "ebur128=peak=true", "-f", "null", "-"],
                       input=inp, capture_output=True)
    txt = p.stderr.decode(errors="ignore").split("Summary:")[-1]
    I = float(txt.split("I:")[1].split("LUFS")[0])
    LRA = float(txt.split("LRA:")[1].split("LU")[0])
    tp = txt.split("Peak:")[1].split("dBFS")[0].strip()
    TP = float(tp) if tp not in ("-inf",) else -200.0
    return I, LRA, TP


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--music", required=True)
    ap.add_argument("--pack", required=True)
    ap.add_argument("--video", required=True)
    ap.add_argument("--out", required=True)
    args = ap.parse_args()
    os.makedirs(args.out, exist_ok=True)

    print("[1] edicion musical")
    music = build_music(args.music)

    print("[2] SFX: render, alineacion y calibracion de nivel")
    sfx = np.zeros((N + SR, 2))
    log = []
    for c in CUES:
        x = render_cue(args.pack, c)
        k = anchor_offset(x, c["mode"])
        start = int(round(c["t"] * SR)) - k
        lm = music_level_db(music, c["t"])
        ls = sfx_level_db(x)
        gain_db = lm + c["rel"] - ls
        gl, gr = pan_gains(c["pan"])
        g = 10 ** (gain_db / 20)
        y = x * g
        y[:, 0] *= gl
        y[:, 1] *= gr
        a = max(0, start)
        y = y[a - start:]
        b = min(len(sfx), a + len(y))
        sfx[a:b] += y[: b - a]
        log.append(dict(id=c["id"], start_s=round(start / SR, 4), event_s=round(c["t"], 4),
                        frame=round(c["t"] * 25, 2), file=c["file"], mode=c["mode"], rel_db=c["rel"],
                        gain_db=round(gain_db, 2), pan=c["pan"], st=c["st"], eq=c["eq"], note=c["note"],
                        dur_s=round(len(x) / SR, 3)))
        print(f"  {c['id']} t={c['t']:6.3f} start={start / SR:6.3f} gain={gain_db:+6.1f} dB  {os.path.basename(c['file'])}")
    tail = np.abs(sfx[N:]).max()
    sfx = sfx[:N]

    print("[3] ducking por bandas y suma")
    low, high = split_bands(music)
    music_d = low * duck_env(DUCKS, 1)[:, None] + high * duck_env(DUCKS, 2)[:, None]
    mix = music_d + sfx

    print("[4] master")
    I0, _, TP0 = loudness(mix)
    # objetivo -14 LUFS, pero sin limitar: si el pico verdadero no cabe, se baja
    # la ganancia en lugar de recortar transitorios
    gain = min(TARGET_LUFS - I0, CEILING_DBTP - 0.2 - TP0)
    mix_g = mix * 10 ** (gain / 20)
    I1, LRA1, TP1 = loudness(mix_g)
    limited = False
    if TP1 > CEILING_DBTP - 0.1:
        # limitador de picos verdaderos: sobremuestreo x4, techo -1,3 dBFS
        mix_g = ffmpeg_filter(mix_g, "aresample=192000,alimiter=limit=0.861:attack=1:release=60:level=disabled:asc=1,"
                                     "aresample=48000")[:N]
        limited = True
    I2, LRA2, TP2 = loudness(mix_g)
    music_stem = music_d * 10 ** (gain / 20)
    sfx_stem = sfx * 10 ** (gain / 20)
    res = mix_g - (music_stem + sfx_stem)
    lim_db = 20 * math.log10(np.abs(res).max() + 1e-12)

    print("[5] exportar")
    o = args.out
    write_wav(os.path.join(o, "ALSINA_REEL_MEZCLA_FINAL_48k24.wav"), mix_g)
    write_wav(os.path.join(o, "ALSINA_REEL_MUSICA_STEM_48k24.wav"), music_stem)
    write_wav(os.path.join(o, "ALSINA_REEL_SFX_STEM_48k24.wav"), sfx_stem)
    # edicion musical sin ducking (misma ganancia), para remezclar con libertad
    write_wav(os.path.join(o, "ALSINA_REEL_MUSICA_EDIT_SIN_DUCKING_48k24.wav"), music * 10 ** (gain / 20))
    mp4 = os.path.join(o, "ALSINA_REEL_CHILE_FINAL.mp4")
    # video copiado sin recodificar; la pista AAC muda original se sustituye
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", args.video, "-f", "f32le", "-ar", str(SR), "-ac", "2",
                    "-i", "-", "-map", "0:v:0", "-map", "1:a:0", "-c:v", "copy", "-c:a", "aac", "-b:a", "320k",
                    "-ar", "48000", "-movflags", "+faststart", mp4],
                   input=mix_g.astype(np.float32).tobytes(), check=True)

    stats = dict(music_in_s=MUSIC_IN, tempo=TEMPO, pre_gain_lufs=I0, master_gain_db=gain,
                 after_gain=dict(I=I1, LRA=LRA1, TP=TP1), final=dict(I=I2, LRA=LRA2, TP=TP2),
                 limiter_used=limited, limiter_max_change_dbfs=lim_db, sfx_tail_beyond_end_peak=float(tail),
                 music_stem=loudness(music_stem), sfx_stem=loudness(sfx_stem))
    with open(os.path.join(o, "build_stats.json"), "w") as f:
        json.dump(dict(stats=stats, cues=log), f, ensure_ascii=False, indent=1)
    print(json.dumps(stats, indent=1))


if __name__ == "__main__":
    main()
