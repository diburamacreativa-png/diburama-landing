#!/usr/bin/env python3
"""Construye la banda sonora final del reel ALSINA CHILE (v2).

Uso:
  python3 -I build_audio.py --music "Groovy Good Vibes.mp3" --pack <pack_dir> \
      --video Alsina_Reel_Chile_ref_01.mp4 --out <out_dir>

Requiere numpy y ffmpeg (con rubberband). Todo el procesado es determinista.
El video NUNCA se toca: se copia el flujo de video sin recodificar.
"""
import argparse, json, math, os, subprocess, sys
import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from cues import CUES, DUCKS  # noqa: E402

SR = 48000
DUR = 25.24
N = int(round(DUR * SR))  # 1 211 520 muestras = 631 fotogramas exactos

# ---- Edicion musical (ver informe) ----
# El golpe mas fuerte del tema (144,711 s del original) cae en el fotograma 553
# (22,12 s), llegada del punto de la «i» al logotipo. Tramo continuo, sin cortes.
MUSIC_IN = 122.022      # s en el MP3 original -> fotograma 0
TEMPO = 1.0255          # +2,55 % de tempo (rubberband, tono intacto; limite del brief +-3 %)
PREROLL = 0.5           # s de pre-roll para que rubberband arranque estable
FADE_IN = 0.006
TAIL_FADE = (24.94, 0.30)  # fundido de la cola residual del tema
TARGET_LUFS = -14.0
CEILING_DBTP = -1.0
MAX_LIMIT_GR_DB = 1.0   # el limitador solo puede tocar picos aislados


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
    fi = int(FADE_IN * SR)
    m[:fi] *= (0.5 * (1 - np.cos(np.linspace(0, np.pi, fi))))[:, None]
    a = int(TAIL_FADE[0] * SR)
    m[a:] *= (0.5 * (1 + np.cos(np.linspace(0, np.pi, N - a))))[:, None]
    return m


# ---- Division en 3 bandas (FIR de fase lineal, reconstruccion perfecta) ----
def fir_lowpass(x, fc, taps=4097):
    n = np.arange(taps) - (taps - 1) / 2
    h = 2 * fc / SR * np.sinc(2 * fc / SR * n) * np.blackman(taps)
    h /= h.sum()
    L = len(x) + taps - 1
    nf = 1 << (L - 1).bit_length()
    H = np.fft.rfft(h, nf)
    d = (taps - 1) // 2
    return np.stack([np.fft.irfft(np.fft.rfft(x[:, c], nf) * H, nf)[d:d + len(x)] for c in range(2)], 1)


def split3(x, f1=160.0, f2=2500.0):
    low = fir_lowpass(x, f1)
    lm = fir_lowpass(x, f2)
    return low, lm - low, x - lm


def duck_env(ducks, band):
    """band 0=grave, 1=medios, 2=agudos. Cada duck: dict(t0,t1,att,rel,db=(g,m,a))."""
    g = np.zeros(N)
    t = np.arange(N) / SR
    for d in ducks:
        depth = d["db"][band]
        if depth == 0:
            continue
        t0, t1, att, rel = d["t0"], d["t1"], d["att"], d["rel"]
        env = np.zeros(N)
        a = (t >= t0 - att) & (t < t0)
        env[a] = 0.5 * (1 - np.cos(np.pi * (t[a] - (t0 - att)) / att))
        env[(t >= t0) & (t < t1)] = 1
        r = (t >= t1) & (t < t1 + rel)
        env[r] = 0.5 * (1 + np.cos(np.pi * (t[r] - t1) / rel))
        g = np.minimum(g, depth * env)
    return 10 ** (g / 20)


EQ = {
    # hits casi todo subgrave: limpiar el infra y dar cuerpo audible en movil (~200 Hz)
    "hit_sub": "highpass=f=38:poles=2,equalizer=f=70:t=q:w=1.0:g=-1.5,equalizer=f=200:t=q:w=1.0:g=3.5",
    "hit": "highpass=f=40:poles=2,equalizer=f=75:t=q:w=1.0:g=-1.0,equalizer=f=190:t=q:w=1.0:g=3",
    # capa metalica: se queda con los parciales 350 Hz - 3 kHz de HIT_04
    "metal": "highpass=f=300:poles=2,equalizer=f=1800:t=q:w=1.0:g=4,equalizer=f=720:t=q:w=2:g=2",
    # boom lejano (corte a rojo visto desde la distancia)
    "boom_far": "highpass=f=35:poles=2,lowpass=f=420:poles=2",
    "pop": "highpass=f=140:poles=2,equalizer=f=600:t=q:w=1.2:g=-2,equalizer=f=2800:t=q:w=1.0:g=3",
    "click": "highpass=f=300:poles=2",
    "air": "highpass=f=180:poles=2,highshelf=f=9000:g=-1.5",
    "air_body": "highpass=f=70:poles=2,highshelf=f=9000:g=-1.5",
    "flat": "anull",
}


# ---- Herramientas de diseno ----
def env_curve(points, n, kind="lin"):
    """points: [(frac, valor)] -> curva de n muestras (interpolacion suave)."""
    fx = np.array([p[0] for p in points], float)
    fy = np.array([p[1] for p in points], float)
    u = np.linspace(0, 1, n)
    return np.interp(u, fx, fy)


def vari_pitch(x, points):
    """Remuestreo de velocidad variable (Doppler): semitonos en funcion de la
    posicion en el sonido de entrada. Cambia tono y duracion de forma continua."""
    n = len(x)
    st = env_curve(points, n)
    rate = 2 ** (st / 12)
    T = np.concatenate([[0], np.cumsum(1 / rate[:-1])])  # tiempo de salida de cada muestra de entrada
    m = int(T[-1])
    p = np.interp(np.arange(m), T, np.arange(n))
    i = np.floor(p).astype(int)
    fr = p - i
    i1 = np.minimum(i + 1, n - 1)
    return x[i] * (1 - fr)[:, None] + x[i1] * fr[:, None]


def stft_tv_filter(x, points, kind="lp", order=4):
    """Filtro paso bajo/alto variable en el tiempo (STFT, solape 75 %)."""
    nf, hop = 2048, 512
    win = np.hanning(nf)
    pad = np.vstack([np.zeros((nf, 2)), x, np.zeros((nf, 2))])
    frames = (len(pad) - nf) // hop + 1
    fc = np.exp(env_curve([(a, math.log(b)) for a, b in points], frames))
    f = np.fft.rfftfreq(nf, 1 / SR)
    out = np.zeros_like(pad)
    norm = np.zeros(len(pad))
    for k in range(frames):
        s = k * hop
        seg = pad[s:s + nf] * win[:, None]
        X = np.fft.rfft(seg, axis=0)
        if kind == "lp":
            g = 1 / np.sqrt(1 + (f / fc[k]) ** (2 * order))
        else:
            g = 1 / np.sqrt(1 + (fc[k] / np.maximum(f, 1)) ** (2 * order))
        out[s:s + nf] += np.fft.irfft(X * g[:, None], nf, axis=0) * win[:, None]
        norm[s:s + nf] += win ** 2
    out /= np.maximum(norm, 1e-9)[:, None]
    return out[nf:nf + len(x)]


def width_auto(x, points):
    """Anchura estereo compatible con mono: lado sintetico = medio retardado 13 ms
    y filtrado (se cancela al sumar a mono) escalado por la curva de anchura."""
    mid = x.mean(1)
    d = int(0.013 * SR)
    side = np.concatenate([np.zeros(d), mid[:-d]])
    side = side - fir_lowpass(np.stack([side, side], 1), 300.0, taps=1025)[:, 0]
    w = env_curve(points, len(x))
    s = 0.5 * side * w
    return np.stack([x[:, 0] + s, x[:, 1] - s], 1)


def pan_auto(x, points):
    p = env_curve(points, len(x))
    th = (p + 1) * math.pi / 4
    m = x.mean(1)
    return np.stack([m * np.cos(th) * math.sqrt(2), m * np.sin(th) * math.sqrt(2)], 1)


def amp_auto(x, points):
    g = 10 ** (env_curve(points, len(x)) / 20)
    return x * g[:, None]


def render_cue(pack, c):
    path = os.path.join(pack, c["file"])
    af = []
    if c.get("rev"):
        af.append("areverse")
    if c.get("stretch"):
        d0 = float(subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0",
                                   path], capture_output=True, text=True).stdout)
        af.append(f"rubberband=tempo={d0 / c['stretch']:.5f}:transients=smooth:window=long")
    if c["st"]:
        r = 2 ** (c["st"] / 12)
        af.append(f"asetrate={SR * r:.3f},aresample={SR}")
    af.append(EQ[c["eq"]])
    x = decode(path, ",".join(af))
    if c.get("pitch_env"):
        x = vari_pitch(x, c["pitch_env"])
    if c.get("lp_env"):
        x = stft_tv_filter(x, c["lp_env"], "lp")
    if c.get("hp_env"):
        x = stft_tv_filter(x, c["hp_env"], "hp", order=2)
    if c.get("amp_env"):
        x = amp_auto(x, c["amp_env"])
    if c.get("pan_env"):
        x = pan_auto(x, c["pan_env"])
    if c.get("width_env"):
        x = width_auto(x, c["width_env"])
    if c.get("fade"):
        fs, fd = c["fade"]
        a, b = int(fs * SR), int((fs + fd) * SR)
        if a < len(x):
            env = np.ones(len(x))
            env[a:b] = 0.5 * (1 + np.cos(np.linspace(0, np.pi, len(env[a:b]))))
            env[b:] = 0
            x = (x.T * env).T[:min(len(x), b)]
    # fundidos anticlic en los extremos (algunos WAV del pack terminan con energia residual)
    k_in = min(int(0.005 * SR), len(x) // 4)
    k_out = min(int(0.010 * SR), len(x) // 4)
    if c["mode"] != "attack":
        x[:k_in] *= (0.5 * (1 - np.cos(np.linspace(0, np.pi, k_in))))[:, None]
    x[-k_out:] *= (0.5 * (1 + np.cos(np.linspace(0, np.pi, k_out))))[:, None]
    return x


def music_level_span(music, a, b):
    """Media ponderada K de la musica a lo largo de todo el recorrido de un sonido largo."""
    a = max(0, a)
    b = min(len(music), b)
    lead = min(a, int(0.5 * SR))
    p = kpower(music[a - lead:b])[lead:]
    return 10 * math.log10(p.mean() + 1e-20)


def anchor_offset(x, mode):
    m = np.abs(x).mean(1)
    if mode == "attack":
        # inicio real del transitorio (no el maximo: en un hit subgrave el maximo
        # llega ~20 ms tarde y adelantaria el golpe respecto al fotograma)
        w = int(0.001 * SR)
        e = np.convolve(m, np.ones(w) / w, "same")[: int(0.06 * SR)]
        return int(np.argmax(e >= 0.25 * e.max()))
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


def resonance_ir(rt60=1.25, length=1.6, seed=7):
    """Resonancia corta y oscura (ruido decorrelado con caida exponencial)."""
    rng = np.random.default_rng(seed)
    n = int(length * SR)
    t = np.arange(n) / SR
    env = np.exp(-6.91 * t / rt60) * np.minimum(1, t / 0.004)
    ir = rng.standard_normal((n, 2)) * env[:, None]
    ir = fir_lowpass(ir, 3800.0, taps=1025)
    ir = ir - fir_lowpass(ir, 140.0, taps=2049)   # sin barro subgrave
    pre = int(0.014 * SR)
    ir = np.vstack([np.zeros((pre, 2)), ir])
    return ir / np.sqrt((ir ** 2).sum() / 2)


def convolve(x, ir):
    L = len(x) + len(ir) - 1
    nf = 1 << (L - 1).bit_length()
    return np.stack([np.fft.irfft(np.fft.rfft(x[:, c], nf) * np.fft.rfft(ir[:, c], nf), nf)[:len(x)]
                     for c in range(2)], 1)


def true_peak_limit(x, ceiling_db, look=0.0015, release=0.040, os_factor=4):
    """Limitador de pico verdadero SIN latencia (la sincronia no se mueve):
    pico sobremuestreado x4 por FFT, lookahead de 1,5 ms y liberacion de 40 ms.
    Devuelve la senal y la reduccion de ganancia maxima en dB."""
    n = len(x)
    nf = 1 << (n - 1).bit_length()
    up = []
    for c in range(2):
        X = np.fft.rfft(x[:, c], nf)
        Y = np.zeros(nf * os_factor // 2 + 1, complex)
        Y[:len(X)] = X
        up.append(np.fft.irfft(Y, nf * os_factor)[:n * os_factor] * os_factor)
    tp = np.max(np.abs(np.stack(up, 1)).reshape(n, os_factor, 2), axis=(1, 2))
    ceil = 10 ** (ceiling_db / 20)
    g_req = np.minimum(1.0, ceil / np.maximum(tp, 1e-12))
    if g_req.min() >= 1.0:
        return x, 0.0
    L = max(1, int(look * SR))
    # lookahead: gmin[n] = min(g_req[n .. n+L]); ataque = media de gmin[n-L .. n].
    # En cada pico p todos los terminos de la media son <= g_req[p] -> g <= g_req.
    pad = np.concatenate([g_req, np.ones(L)])
    gmin = np.min(np.lib.stride_tricks.sliding_window_view(pad, L + 1), axis=1)[:n]
    sm = np.convolve(np.concatenate([np.ones(L), gmin]), np.ones(L + 1) / (L + 1), "valid")[:n]
    sm = np.minimum(sm, g_req)
    # liberacion exponencial hacia 1, sin superar nunca la ganancia requerida
    coef = math.exp(-1 / (release * SR))
    g = np.empty(n)
    prev = 1.0
    for i, v in enumerate(sm.tolist()):
        prev = min(v, 1 - (1 - prev) * coef)
        g[i] = prev
    return x * g[:, None], -20 * math.log10(g.min())


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
    sfx = np.zeros((N + 2 * SR, 2))
    send = np.zeros((N + 2 * SR, 2))
    log = []
    for c in CUES:
        x = render_cue(args.pack, c)
        k = anchor_offset(x, c["mode"])
        start = int(round(c["t"] * SR)) - k
        if c["mode"] == "attack" or len(x) < int(0.3 * SR):
            lm = music_level_db(music, c["t"])
        else:
            lm = music_level_span(music, start, start + len(x))
        ls = sfx_level_db(x)
        gain_db = lm + c["rel"] - ls
        gl, gr = pan_gains(c["pan"])
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
    print("    resonancia del impacto")
    sfx += convolve(send, resonance_ir())
    tail = np.abs(sfx[N:]).max()
    sfx = sfx[:N]
    # la cola del bus de efectos se cierra con la misma curva que la musica
    a = int(TAIL_FADE[0] * SR)
    sfx[a:] *= (0.5 * (1 + np.cos(np.linspace(0, np.pi, N - a))))[:, None]

    print("[3] ducking por bandas y suma")
    low, mid, high = split3(music)
    music_d = (low * duck_env(DUCKS, 0)[:, None] + mid * duck_env(DUCKS, 1)[:, None]
               + high * duck_env(DUCKS, 2)[:, None])
    mix = music_d + sfx

    print("[4] master")
    I0, _, TP0 = loudness(mix)
    gain = TARGET_LUFS - I0
    mix_g = mix * 10 ** (gain / 20)
    I1, LRA1, TP1 = loudness(mix_g)
    limited = False
    gr = 0.0
    if TP1 > CEILING_DBTP - 0.15:
        need = TP1 - (CEILING_DBTP - 0.25)
        if need > MAX_LIMIT_GR_DB:
            # no se aplasta: se baja la ganancia hasta que el limitador solo roce picos
            gain -= need - MAX_LIMIT_GR_DB
            mix_g = mix * 10 ** (gain / 20)
        mix_g, gr = true_peak_limit(mix_g, CEILING_DBTP - 0.25)
        limited = True
    I2, LRA2, TP2 = loudness(mix_g)
    music_stem = music_d * 10 ** (gain / 20)
    sfx_stem = sfx * 10 ** (gain / 20)
    res = mix_g - (music_stem + sfx_stem)
    lim_db = 20 * math.log10(np.abs(res).max() + 1e-12)
    lim_time = float(np.argmax(np.abs(res).max(1)) / SR)

    print("[5] exportar")
    o = args.out
    write_wav(os.path.join(o, "ALSINA_REEL_MEZCLA_FINAL_48k24.wav"), mix_g)
    write_wav(os.path.join(o, "ALSINA_REEL_MUSICA_STEM_48k24.wav"), music_stem)
    write_wav(os.path.join(o, "ALSINA_REEL_SFX_STEM_48k24.wav"), sfx_stem)
    write_wav(os.path.join(o, "ALSINA_REEL_MUSICA_EDIT_SIN_DUCKING_48k24.wav"), music * 10 ** (gain / 20))
    mp4 = os.path.join(o, "ALSINA_REEL_CHILE_FINAL.mp4")
    # video copiado sin recodificar; la pista de audio se sustituye
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", args.video, "-f", "f32le", "-ar", str(SR), "-ac", "2",
                    "-i", "-", "-map", "0:v:0", "-map", "1:a:0", "-c:v", "copy", "-c:a", "aac", "-b:a", "320k",
                    "-ar", "48000", "-movflags", "+faststart", mp4],
                   input=mix_g.astype(np.float32).tobytes(), check=True)

    stats = dict(music_in_s=MUSIC_IN, tempo=TEMPO, pre_gain_lufs=I0, master_gain_db=gain,
                 after_gain=dict(I=I1, LRA=LRA1, TP=TP1), final=dict(I=I2, LRA=LRA2, TP=TP2),
                 limiter_used=limited, limiter_max_gr_db=round(gr, 2), limiter_max_change_dbfs=lim_db,
                 limiter_max_change_at_s=lim_time, sfx_tail_beyond_end_peak=float(tail),
                 music_stem=loudness(music_stem), sfx_stem=loudness(sfx_stem))
    with open(os.path.join(o, "build_stats.json"), "w") as f:
        json.dump(dict(stats=stats, cues=log, ducks=DUCKS), f, ensure_ascii=False, indent=1)
    print(json.dumps(stats, indent=1))


if __name__ == "__main__":
    main()
