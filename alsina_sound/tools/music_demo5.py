#!/usr/bin/env python3
"""Reedicion musical de «Groovy Good Vibes» para VIDEO REEL CHILE_DEMO 5 (38,68 s).

Sin cambios de tempo ni de tono en la musica ritmica. Edicion por compases sobre
transitorios del propio tema, mas una prolongacion del acorde sostenido final
(«fermata») para que el boton del tema muera con el fundido a negro.
"""
import numpy as np

SR = 48000
DUR = 38.68
N = int(round(DUR * SR))  # 1 856 640 muestras = 967 fotogramas exactos

# (inicio_video_s, inicio_fuente_s, fin_fuente_s) - fuente = segundos del MP3 original
# 1) 106,899 -> 133,979 : groove (video 0,000 - 27,080)
# 2) salto de 2 compases (8 beats, 4,404 s) sobre dos golpes de bateria equivalentes
# 3) 138,383 -> 145,000 : final del tema; el golpe de 144,713 cae en f835 (33,410 s)
# 4) fermata: acorde sostenido 145,00-145,92 prolongado +2 beats (1,102 s)
# 5) 145,920 -> fin   : stabs, boton final (147,06 -> 36,86 s) y cola
SPLICE_A = (133.979, 138.383)   # salida / entrada del salto de 2 compases (fuente)
SRC_START = SPLICE_A[0] - 27.080  # 106,899 en t = 0
SUSTAIN = (145.00, 145.92)
SUSTAIN_ADD = 2 * 60 / 108.9    # 2 beats = 1,102 s
VIDEO_FADE = (38.24, 0.38)      # fundido a negro del video f956-f965


def equal_power(n):
    u = np.linspace(0, 1, n)
    return np.sin(u * np.pi / 2), np.cos(u * np.pi / 2)


def best_lag(a, b, max_lag):
    """Desfase (muestras) que maximiza la correlacion de b respecto a a."""
    best, bl = -1e9, 0
    for lag in range(-max_lag, max_lag + 1):
        if lag >= 0:
            c = np.dot(a[lag:], b[:len(b) - lag])
        else:
            c = np.dot(a[:lag], b[-lag:])
        if c > best:
            best, bl = c, lag
    return bl


def join(a, b, xf):
    """Encadena a y b solapando las ultimas xf muestras de a con las primeras de b
    (fundido de igual potencia). a y b deben incluir ese solape."""
    fin, fout = equal_power(xf)
    return np.vstack([a[:-xf], a[-xf:] * fout[:, None] + b[:xf] * fin[:, None], b[xf:]])


def stretch_sustain(full, ffmpeg_filter, r0, r1, add):
    """Prolonga un acorde sostenido (sin transitorios) con rubberband en ventana
    larga; solo afecta a [r0, r1]. Devuelve el tramo prolongado."""
    pad = 0.12
    k = (r1 - r0 + add) / (r1 - r0)
    seg = full[int((r0 - pad) * SR):int((r1 + pad) * SR)]
    st = ffmpeg_filter(seg, f"rubberband=tempo={1 / k:.6f}:transients=smooth:detector=soft:phase=independent:"
                            "window=long:pitchq=quality:channels=together")
    a = int(round(pad * k * SR))
    L = int(round((r1 - r0 + add) * SR))
    return st[a:a + L]


def build(full, ffmpeg_filter):
    """full: MP3 original decodificado (estereo, 48 kHz, float64)."""
    xf_cut = int(0.012 * SR)   # empalme de compases: 12 ms
    xf_sus = int(0.030 * SR)   # entradas/salidas de la fermata: 30 ms
    pre = int(0.006 * SR)      # se empalma 6 ms antes del golpe: el transitorio nuevo enmascara la union
    s0 = int(round(SRC_START * SR))
    a_end = int(round(SPLICE_A[0] * SR)) - pre
    b0 = int(round(SPLICE_A[1] * SR)) - pre
    # entrada afinada por correlacion (+-3 ms) para que los dos golpes coincidan
    lag = best_lag(full[a_end - 2400:a_end + 2400].mean(1), full[b0 - 2400:b0 + 2400].mean(1), 144)
    b0 += lag
    h = xf_cut // 2
    # 1) groove 106,899 -> 133,979  +  2) 138,383 -> 145,00
    sus0 = int(round(SUSTAIN[0] * SR))
    out = join(full[s0:a_end + h], full[b0 - h:sus0 + xf_sus // 2], xf_cut)
    # 3) fermata (acorde sostenido prolongado), entrando y saliendo con fundidos de 30 ms
    sus = stretch_sustain(full, ffmpeg_filter, SUSTAIN[0] - xf_sus / 2 / SR, SUSTAIN[1] + xf_sus / 2 / SR,
                          SUSTAIN_ADD)
    out = join(out, sus, xf_sus)
    # 4) stabs finales, boton y cola original
    c0 = int(round(SUSTAIN[1] * SR))
    out = join(out, full[c0 - xf_sus // 2:], xf_sus)
    m = out[:N].copy()
    if len(m) < N:
        m = np.vstack([m, np.zeros((N - len(m), 2))])
    fi = int(0.004 * SR)
    m[:fi] *= (0.5 * (1 - np.cos(np.linspace(0, np.pi, fi))))[:, None]
    info = dict(src_start=SRC_START, splice_a=SPLICE_A, splice_lag_ms=lag / SR * 1000,
                splice_video_s=(a_end - s0) / SR, sustain=SUSTAIN, sustain_add_s=SUSTAIN_ADD,
                sustain_video_s=(sus0 - s0 - (b0 - a_end)) / SR)
    return m, info
