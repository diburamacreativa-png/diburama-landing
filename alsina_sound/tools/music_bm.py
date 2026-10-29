#!/usr/bin/env python3
"""Reedicion de «Build Momentum» (21,24 s, 169,3 BPM) para VIDEO REEL CHILE_DEMO 6 (35,40 s).

Ancla: el golpe de resolucion del tema (19,371 s, ultimo tresillo del fill + entrada del
subgrave sostenido) cae en el punto de la «i» (f753). Se trabaja hacia atras con bloques
continuos del tema unidos en inicio de compas. Indices de beat del tema: beat k en
GRID0 + k * BEAT, con compases que empiezan en beats 1, 5, 9 ... 53.
"""
import numpy as np

SR = 48000
DUR = 35.40
N = int(round(DUR * SR))      # 1 699 200 muestras = 885 fotogramas
BEAT = 0.3544                 # 169,3 BPM
ANCH_SRC = 19.371             # golpe de resolucion del tema
ANCH_V = 753 / 25 + 0.005     # f753 (30,12 s): el punto de la «i» entra en «Alsina»


# Inicios de compas usados (indice de beat -> segundos del tema): rejilla de 169,3 BPM corregida con
# el desfase regional mediano de los transitorios (mas fiable que un unico transitorio)
BAR_ONSETS = {1: 0.436, 21: 7.564, 29: 10.403, 41: 14.647, 49: 17.480, 53: 18.898}


# Bloques (compas_inicio, compas_fin_exclusivo) en indices de beat del tema; el ultimo
# bloque llega hasta el final del tema.
BLOCKS = [(1, 21), (29, 49), (21, 49), (41, 49), (49, 53), (49, None)]


def plan(onsets, k_pre=1.0):
    """Coloca los bloques hacia atras desde el ancla. k_pre: factor de tempo opcional de
    los bloques anteriores al break (1.0 = sin cambio). Devuelve lista de bloques con
    (src0, src1, v0, v1)."""
    out = []
    last_src0 = onsets[49]
    v_end_block = ANCH_V - (ANCH_SRC - last_src0)   # inicio en video del ultimo bloque
    out.append(dict(src0=last_src0, src1=None, v0=v_end_block, k=1.0))
    v = v_end_block
    for b0, b1 in reversed(BLOCKS[:-1]):
        s0, s1 = onsets[b0], onsets[b1]
        k = 1.0 if b0 == 49 else k_pre
        L = (s1 - s0) / k
        out.append(dict(src0=s0, src1=s1, v0=v - L, k=k))
        v -= L
    return out[::-1]


def src_to_video(blocks, s, which):
    b = blocks[which]
    return b["v0"] + (s - b["src0"]) / b["k"]


END_FADE_SRC = (20.05, 0.75)   # el tema se apaga en 20,55-20,75 s; se sustituye por un fundido suave
TAIL_RT60 = 2.6                # cola de reverberacion del acorde final (s)


def tail_ir(B, rt60, length, seed=11):
    """Cola de reverberacion para el acorde final: decaimiento exponencial decorrelado,
    paso bajo 3,2 kHz y paso alto 70 Hz (el acorde final es casi todo subgrave)."""
    rng = np.random.default_rng(seed)
    n = int(length * SR)
    t = np.arange(n) / SR
    env = np.exp(-6.91 * t / rt60) * np.minimum(1, t / 0.006)
    ir = rng.standard_normal((n, 2)) * env[:, None]
    ir = B.fir_lowpass(ir, 3200.0, taps=1025)
    ir = ir - B.fir_lowpass(ir, 70.0, taps=4097)
    ir = np.vstack([np.zeros((int(0.018 * SR), 2)), ir])
    return ir / np.sqrt((ir ** 2).sum() / 2)


def build(full, onsets, B):
    """full: tema decodificado (48 kHz, estereo). B: modulo build_audio (motor comun).
    Devuelve (musica, bloques, info). Union de bloques: 6 ms antes del golpe entrante,
    fundido de igual potencia de 12 ms."""
    blocks = plan(onsets)
    pre, xf = int(0.006 * SR), int(0.012 * SR)
    h = xf // 2
    out = np.zeros((N + SR, 2))
    for i, b in enumerate(blocks):
        v0 = int(round(b["v0"] * SR))
        s0 = int(round(b["src0"] * SR))
        a = 0 if i == 0 else v0 - pre - h
        e = N if i == len(blocks) - 1 else int(round(blocks[i + 1]["v0"] * SR)) - pre + h
        src = full[s0 + (a - v0):s0 + (e - v0)]
        seg = np.zeros((e - a, 2))
        seg[:len(src)] = src[:e - a]
        if i > 0:
            seg[:xf] *= np.sin(np.linspace(0, np.pi / 2, xf))[:, None]
        if i < len(blocks) - 1:
            seg[-xf:] *= np.cos(np.linspace(0, np.pi / 2, xf))[:, None]
        else:
            # fundido del final del tema (en tiempo de fuente) y cola natural
            f0 = int(round((END_FADE_SRC[0] - b["src0"]) * SR + (v0 - a)))
            f1 = f0 + int(END_FADE_SRC[1] * SR)
            env = np.ones(len(seg))
            env[f0:f1] = 0.5 * (1 + np.cos(np.linspace(0, np.pi, f1 - f0)))
            env[f1:] = 0
            dry = seg * env[:, None]
            # envio de reverberacion solo del acorde final (desde el golpe de resolucion)
            r0 = int(round((ANCH_SRC - b["src0"]) * SR + (v0 - a)))
            send = np.zeros_like(dry)
            send[r0:] = dry[r0:]
            ir = tail_ir(B, TAIL_RT60, 3.2)
            wet = B.convolve(np.vstack([send, np.zeros((len(ir), 2))]), ir)[:len(dry)]
            wet *= 10 ** (-9 / 20)
            seg = dry + wet
        out[a:a + len(seg)] += seg[:len(out) - a]
    m = out[:N]
    fi = int(0.004 * SR)
    m[:fi] *= (0.5 * (1 - np.cos(np.linspace(0, np.pi, fi))))[:, None]
    info = dict(blocks=[dict(src0=round(b["src0"], 4), src1=None if b["src1"] is None else round(b["src1"], 4),
                             video0=round(b["v0"], 4)) for b in blocks],
                video0_src=round(blocks[0]["src0"] - blocks[0]["v0"], 4), anchor_src=ANCH_SRC, anchor_video=ANCH_V)
    return m, blocks, info
