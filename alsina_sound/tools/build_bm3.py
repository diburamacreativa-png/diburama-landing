#!/usr/bin/env python3
"""Correccion del primer montaje de «Build Momentum» (tema de 21,24 s) sobre VIDEO REEL CHILE_DEMO 6.
Misma musica hasta 28,23 s; acentos movidos/sustituidos; cierre reconstruido con la resolucion
en el punto blanco (f738). El video NO se toca: el flujo de imagen se copia sin recodificar.

Uso:
  python3 -I build_bm3.py --music "Build Momentum.mp3" --pack <pack_dir> \
      --video "VIDEO REEL CHILE_DEMO 6.mp4" --out <out_dir>
"""
import argparse, json, math, os, subprocess, sys
import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import build_audio as B  # noqa: E402
import music_bm as M1  # noqa: E402
import music_bm3 as M  # noqa: E402
from cues_bm3 import CUES, DUCKS  # noqa: E402

SR = M.SR
N = M.N
B.N = N
TARGET_LUFS = -14.0
CEILING_DBTP = -1.0
MAX_LIMIT_GR_DB = 2.0   # solo actua en el ataque del impacto final (se verifica)
IMPACT_BUS_GR_DB = 3.0
MUSIC_BODY_DB = -1.8
BODY_RAMP = (26.8, 28.5)
VIDEO_FADE = (874 / 25, 0.36)   # fundido a negro del video f874-f883


def accent_curve(x):
    """Flujo espectral por bandas (2 ms), normalizado: el mismo analisis usado sobre el tema."""
    m = x.mean(1)
    h, n = 96, 1024
    win = np.hanning(n)
    f = np.fft.rfftfreq(n, 1 / SR)
    bands = [(30, 150), (150, 1000), (1000, 4000), (4000, 16000)]
    nfr = (len(m) - n) // h
    out = []
    for c0 in range(0, nfr, 20000):
        idx = np.arange(c0, min(nfr, c0 + 20000))
        S = np.log1p(10 * np.abs(np.fft.rfft(m[idx[:, None] * h + np.arange(n)] * win, axis=1)))
        out.append(np.stack([S[:, (f >= a) & (f < b)].mean(1) for a, b in bands], 1))
    Bm = np.concatenate(out)
    D = np.maximum(0, Bm[2:] - Bm[:-2])
    D = np.r_[np.zeros((2, 4)), D] / np.percentile(D, 99, axis=0)
    acc = D @ np.array([1.2, 1.0, 0.8, 0.6])
    t = (np.arange(len(acc)) * h + n / 2) / SR
    return t, acc


def onset_near(curve, t, win, min_strength=1.5):
    """Transitorio musical mas fuerte en t +- win (s), o None si no hay ninguno claro."""
    tt, acc = curve
    i0, i1 = np.searchsorted(tt, [t - win, t + win])
    if i1 <= i0:
        return None
    j = i0 + int(np.argmax(acc[i0:i1]))
    return float(tt[j]) if acc[j] >= min_strength else None


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--music", required=True)
    ap.add_argument("--pack", required=True)
    ap.add_argument("--video", required=True)
    ap.add_argument("--out", required=True)
    a = ap.parse_args()
    os.makedirs(a.out, exist_ok=True)

    print("[1] reedicion de la musica")
    music, blocks, minfo = M.build(B.decode(a.music), M1.BAR_ONSETS, B)

    print("[2] percusion complementaria y transiciones")
    curve = accent_curve(music)
    sfx = np.zeros((N + 2 * SR, 2))
    send = np.zeros((N + 2 * SR, 2))
    log = []
    for c in CUES:
        x = B.render_cue(a.pack, c)
        k = B.anchor_offset(x, c["mode"])
        t = c["t"]
        snapped = None
        if c.get("snap"):
            o = onset_near(curve, t, c["snap"])
            if o is not None and o < c["t"] - c.get("early", 0.025):
                o = None   # nunca adelantar el golpe a la imagen mas de lo permitido
            if o is not None:
                snapped = o
                t = o if c["mode"] == "attack" else c["t"] + (o - c["t"])
        start = int(round(t * SR)) - k
        if c["mode"] == "attack" or len(x) < int(0.3 * SR):
            lm = B.music_level_db(music, t)
        else:
            lm = B.music_level_span(music, start, start + len(x))
        g = lm + c["rel"] - B.sfx_level_db(x)
        gl, gr = B.pan_gains(c["pan"])
        y = x * 10 ** (g / 20)
        y[:, 0] *= gl
        y[:, 1] *= gr
        s0 = max(0, start)
        y = y[s0 - start:]
        e0 = min(len(sfx), s0 + len(y))
        sfx[s0:e0] += y[:e0 - s0]
        if c.get("verb") is not None:
            send[s0:e0] += y[:e0 - s0] * 10 ** (c["verb"] / 20)
        log.append(dict(id=c["id"], frame=round(c["t"] * 25, 2), event_s=round(t, 4), nominal_s=round(c["t"], 4),
                        snapped_to_music=snapped is not None, start_s=round(start / SR, 4), file=c["file"],
                        mode=c["mode"], rel_db=c["rel"], gain_db=round(g, 2), tier=c.get("tier"),
                        accion=c.get("accion"), note=c["note"]))
        print(f"  {c['id']} t={t:7.4f}{' (fundido con la musica)' if snapped is not None else ''}  {os.path.basename(c['file'])}")
    sfx += B.convolve(send, B.resonance_ir())
    sfx = sfx[:N]
    # limitador solo en el bus del impacto final: recorta 3 dB del pico de ataque (unos ms)
    # sin tocar el cuerpo ni la musica, para que el golpe no obligue a bajar todo el master
    ia, ib = int((M.ANCH_V - 0.08) * SR), int((M.ANCH_V + 0.6) * SR)
    seg = sfx[ia:ib]
    pk = np.abs(seg).max()
    lim, gr_imp = B.true_peak_limit(seg, 20 * math.log10(pk) - IMPACT_BUS_GR_DB)
    sfx[ia:ib] = lim
    print(f"    bus del impacto: reduccion maxima {gr_imp:.1f} dB")

    print("[3] ducking por bandas")
    low, mid, high = B.split3(music)
    music_d = (low * B.duck_env(DUCKS, 0)[:, None] + mid * B.duck_env(DUCKS, 1)[:, None]
               + high * B.duck_env(DUCKS, 2)[:, None])
    fade = np.ones(N)
    f0 = int(VIDEO_FADE[0] * SR)
    f1 = int((VIDEO_FADE[0] + VIDEO_FADE[1]) * SR)
    fade[f0:f1] = 0.5 * (1 + np.cos(np.linspace(0, np.pi, f1 - f0)))
    fade[f1:] = 0
    # automatizacion de volumen: el cuerpo 1,2 dB por debajo y subida durante el break hasta el
    # climax, para que el golpe del punto sea el acento mas concluyente de la pieza
    tt = np.arange(N) / SR
    ramp = np.clip((tt - BODY_RAMP[0]) / (BODY_RAMP[1] - BODY_RAMP[0]), 0, 1)
    body = 10 ** (MUSIC_BODY_DB * (1 - 0.5 * (1 - np.cos(np.pi * ramp))) / 20)
    music_d *= (fade * body)[:, None]
    sfx *= fade[:, None]
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
    res = np.abs(mix_g - (music_stem + sfx_stem)).max(1)
    act = np.where(res > 10 ** (-60 / 20))[0] / SR
    lim_span = (float(act.min()), float(act.max())) if len(act) else None

    print("[5] exportar")
    o = a.out
    pre = "ALSINA_BM3"
    wav = os.path.join(o, f"{pre}_MEZCLA_FINAL_48k24.wav")
    B.write_wav(wav, mix_g)
    B.write_wav(os.path.join(o, f"{pre}_MUSICA_STEM_48k24.wav"), music_stem)
    B.write_wav(os.path.join(o, f"{pre}_EFECTOS_48k24.wav"), sfx_stem)
    mp4 = os.path.join(o, "ALSINA_REEL_CHILE_DEMO6_BUILD_MOMENTUM_CORREGIDO.mp4")
    # imagen copiada sin recodificar; AAC codificado desde el WAV de 24 bits entregado
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", a.video, "-i", wav, "-map", "0:v:0", "-map", "1:a:0",
                    "-c:v", "copy", "-c:a", "aac", "-b:a", "320k", "-ar", "48000", "-movflags", "+faststart", mp4],
                   check=True)
    stats = dict(music=minfo, pre_gain_lufs=I0, master_gain_db=gain, after_gain=dict(I=I1, LRA=LRA1, TP=TP1),
                 final=dict(I=I2, LRA=LRA2, TP=TP2), limiter_max_gr_db=round(gr, 2), limiter_activo_s=lim_span,
                 music_stem=B.loudness(music_stem), sfx_stem=B.loudness(sfx_stem))
    with open(os.path.join(o, "build_stats_bm3.json"), "w") as f:
        json.dump(dict(stats=stats, cues=log, ducks=DUCKS), f, ensure_ascii=False, indent=1)
    print(json.dumps(stats, indent=1))


if __name__ == "__main__":
    main()
