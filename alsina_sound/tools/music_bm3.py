#!/usr/bin/env python3
"""Correccion del cierre de «Build Momentum» (tema de 21,24 s) en VIDEO REEL CHILE_DEMO 6.

Hasta 28,234 s la musica es la misma del primer montaje (music_bm, bloques identicos). Solo se
reconstruye el cierre desde el MP3 original para que la resolucion caiga en f738 (29,52 s), donde
el punto blanco aparece aislado sobre negro:

  26,816  break (compas 49, entero)                         = corte a cenital
  28,234  break (compas 49, solo tiempos 1-2)
  28,951  redoble en tresillos del tema (desde el compas 53, entra en el tiempo 3)
  29,425  la musica se detiene en el ultimo golpe del redoble: vacio breve mientras se cierra el iris
  29,522  resolucion del tema (acorde con subgrave) = PUNTO BLANCO (f738)
  ...     cola: acorde seco que se apaga + reverberacion del acorde + lecho ambiental muy discreto
"""
import numpy as np

import music_bm as M1

SR = M1.SR
DUR = M1.DUR
N = M1.N
ANCH_V = 738 / 25 + 0.004      # f738 = 29,520-29,560 s: ataque de la resolucion
RES_SRC = M1.ANCH_SRC          # 19,371 s: golpe de resolucion del tema
BREAK_SRC = 17.480             # compas 49 (break)
BREAK_B3_SRC = 18.197          # tiempo 3 del compas 49 (transitorio medido)
FILL_SRC = 18.897              # compas 53: redoble en tresillos
DRY_FADE_SRC = (19.90, 0.60)   # el acorde seco se apaga; la cola sigue con reverberacion y lecho
TAIL_RT60 = 3.0
TAIL_WET_DB = -8.0
PAD_DB = -29.0                 # lecho ambiental respecto al acorde (muy discreto)
PAD_SRC = (19.46, 19.90)       # tramo sostenido del acorde que se congela
VIDEO_FADE = (874 / 25, 0.36)


def freeze_pad(full, s0, s1, dur, B, seed=5):
    """Lecho ambiental: espectro medio del acorde con fases aleatorias (sin ataques ni ritmo),
    paso bajo 2,4 kHz y paso alto 60 Hz."""
    seg = full[int(s0 * SR):int(s1 * SR)]
    n, hop = 4096, 1024
    w = np.hanning(n)
    fr = np.arange(0, len(seg) - n, hop)
    mag = np.stack([np.abs(np.fft.rfft(seg[fr[:, None] + np.arange(n), c] * w, axis=1)).mean(0) for c in range(2)], 1)
    rng = np.random.default_rng(seed)
    L = int(dur * SR)
    out = np.zeros((L + n, 2))
    for k in range(0, L, hop):
        for c in range(2):
            ph = np.exp(2j * np.pi * rng.random(len(mag)))
            out[k:k + n, c] += np.fft.irfft(mag[:, c] * ph, n) * w
    out = out[:L]
    out = B.fir_lowpass(out, 2400.0, taps=2049)
    out = out - B.fir_lowpass(out, 60.0, taps=4097)
    ref = np.sqrt((seg ** 2).mean())
    return out / (np.sqrt((out ** 2).mean()) + 1e-12) * ref


def build(full, onsets, B):
    """Devuelve (musica, bloques, info). Bloques 1-5 identicos al primer montaje."""
    blocks1 = M1.plan(onsets)
    pre, xf = int(0.006 * SR), int(0.012 * SR)
    h = xf // 2
    v_b2 = blocks1[-1]["v0"]                       # 28,234: segunda pasada del break
    v_fill = v_b2 + (BREAK_B3_SRC - BREAK_SRC)     # 28,951
    v_stop = v_fill + (RES_SRC - FILL_SRC)         # 29,425: aqui caeria la resolucion sin vacio
    segs = [dict(src0=b["src0"], v0=b["v0"], name=f"bloque {i + 1} (primer montaje)") for i, b in enumerate(blocks1[:-1])]
    segs += [dict(src0=BREAK_SRC, v0=v_b2, name="break, tiempos 1-2"),
             dict(src0=FILL_SRC, v0=v_fill, name="redoble en tresillos"),
             dict(src0=RES_SRC, v0=ANCH_V, name="resolucion = punto blanco")]
    out = np.zeros((N + SR, 2))
    for i, s in enumerate(segs):
        v0 = int(round(s["v0"] * SR))
        s0 = int(round(s["src0"] * SR))
        last = i == len(segs) - 1
        if i == 0:
            a = 0
        elif last:
            a = v0 - int(0.004 * SR)               # entrada propia tras el vacio
        else:
            a = v0 - pre - h
        if last:
            e = N
        elif i == len(segs) - 2:                   # el redoble termina antes del golpe de resolucion
            e = int(round((v_stop - 0.008) * SR))
        else:
            e = int(round(segs[i + 1]["v0"] * SR)) - pre + h
        src = full[s0 + (a - v0):s0 + (e - v0)]
        seg = np.zeros((e - a, 2))
        seg[:len(src)] = src[:e - a]
        if last:
            k = int(0.003 * SR)
            seg[:k] *= np.sin(np.linspace(0, np.pi / 2, k))[:, None] ** 2
        elif i > 0:
            seg[:xf] *= np.sin(np.linspace(0, np.pi / 2, xf))[:, None]
        if i == len(segs) - 2:
            k = int(0.010 * SR)
            seg[-k:] *= np.cos(np.linspace(0, np.pi / 2, k))[:, None] ** 2
        elif not last:
            seg[-xf:] *= np.cos(np.linspace(0, np.pi / 2, xf))[:, None]
        else:
            # cola: acorde seco con fundido + reverberacion del acorde desde el golpe
            f0 = int(round((DRY_FADE_SRC[0] - s["src0"]) * SR + (v0 - a)))
            f1 = f0 + int(DRY_FADE_SRC[1] * SR)
            env = np.ones(len(seg))
            env[f0:f1] = 0.5 * (1 + np.cos(np.linspace(0, np.pi, f1 - f0)))
            env[f1:] = 0
            dry = seg * env[:, None]
            r0 = v0 - a
            send = np.zeros_like(dry)
            send[r0:] = dry[r0:]
            ir = M1.tail_ir(B, TAIL_RT60, 4.0)
            wet = B.convolve(np.vstack([send, np.zeros((len(ir), 2))]), ir)[:len(dry)]
            seg = dry + wet * 10 ** (TAIL_WET_DB / 20)
        out[a:a + len(seg)] += seg[:len(out) - a]
    m = out[:N]
    fi = int(0.004 * SR)
    m[:fi] *= (0.5 * (1 - np.cos(np.linspace(0, np.pi, fi))))[:, None]
    # lecho ambiental: entra por debajo de la cola y decae lentamente hasta la salida del video
    p0 = ANCH_V + 0.25
    pad = freeze_pad(full, PAD_SRC[0], PAD_SRC[1], DUR - p0, B)
    t = np.arange(len(pad)) / SR
    env = np.clip(t / 1.6, 0, 1) ** 1.5 * 10 ** (-11.0 * t / (DUR - p0) / 20)
    i0 = int(p0 * SR)
    m[i0:i0 + len(pad)] += pad[:N - i0] * (env * 10 ** (PAD_DB / 20))[:N - i0, None]
    info = dict(segmentos=[dict(nombre=s["name"], fuente=round(s["src0"], 4), video=round(s["v0"], 4)) for s in segs],
                redoble_termina=round(v_stop, 4), vacio_ms=round((ANCH_V - v_stop) * 1000, 1),
                resolucion_video=ANCH_V, lecho_db=PAD_DB)
    return m, segs, info
