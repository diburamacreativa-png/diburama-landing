#!/usr/bin/env python3
"""Reedicion de «Build Momentum (1)» (version completa: 173,23 s, 126 BPM, Sol) para
VIDEO REEL CHILE_DEMO 6 (35,40 s). Sin cambios de tempo ni de tono: solo bloques del tema
unidos en posiciones de su propia rejilla (compas, tiempo o semicorchea).

Ancla: el golpe final del tema (compas 90, 171,531 s: acorde de Sol con subgrave tras dos
compases de reduccion) cae en el punto de la «i» (f753). Todo se coloca hacia atras desde
ahi con la duracion nativa de cada bloque.

Tiempos de fuente medidos sobre los transitorios (mediana regional del flujo espectral).
Armonia de la seccion final: 80-83 Sol | 84-85 Fa | 86-87 Do | 88-90 Sol.
"""
import numpy as np

SR = 48000
DUR = 35.40
N = int(round(DUR * SR))      # 1 699 200 muestras = 885 fotogramas
HIT_SRC = 171.531             # ataque del golpe final del tema (medios; el subgrave llega +20 ms)
ANCH_V = 753 / 25 + 0.0143    # f753 (30,120-30,160 s): el ataque del golpe del tema queda en 30,130 s

# (inicio, fin) en segundos del tema. None = hasta el final del tema.
BLOCKS = [
    dict(name="A groove (compases 73-75)", src0=None, src1=144.731),          # termina en la ultima semicorchea del 75
    dict(name="B subida filtrada (77-79)", src0=148.541, src1=152.475),       # entra en la ultima semicorchea del 77
    dict(name="C1 drop (80-82)", src0=152.475, src1=158.188),
    dict(name="C2 (82-87) Sol-Fa-Do", src0=156.284, src1=167.723),            # repite el 82 (Sol) para cuadrar
    dict(name="F tiempo 1 del 87 (Do)", src0=165.815, src1=166.289),
    dict(name="E final (88 tiempo 2 -> golpe -> cola)", src0=168.201, src1=None),
]

# Intro: durante los impulsos de camara (f0-f31) el tema suena sin bombo ni bajo (paso alto de fase
# lineal) para que los golpes de zoom lleven solos el grave; el groove entero entra en el siguiente
# primer tiempo (compas 74), con el ritmo continuo en todo momento.
INTRO_HP_HZ = 230.0
INTRO_GAIN_DB = 2.0     # compensa el grave retirado para que la intro no caiga de nivel
INTRO_OPEN_SRC = 141.039

DRY_FADE_SRC = (172.95, 0.25)  # el tema decae solo tras el golpe; solo se suaviza el corte del final del archivo
TAIL_RT60 = 4.2
TAIL_WET_DB = -5.0


def plan():
    """Coloca los bloques hacia atras desde el ancla (duracion nativa de cada bloque)."""
    out = [None] * len(BLOCKS)
    last = BLOCKS[-1]
    v = ANCH_V - (HIT_SRC - last["src0"])
    out[-1] = dict(last, v0=v)
    for i in range(len(BLOCKS) - 2, -1, -1):
        b = BLOCKS[i]
        L = b["src1"] - (b["src0"] if b["src0"] is not None else 0)
        if b["src0"] is None:   # el primer bloque llega hasta t = 0
            out[i] = dict(b, src0=b["src1"] - v, v0=0.0)
        else:
            out[i] = dict(b, v0=v - L)
        v -= L
    return out


def tail_ir(B, rt60, length, seed=11):
    """Cola para el acorde final: decaimiento exponencial decorrelado, paso bajo 3,2 kHz,
    paso alto 70 Hz (conserva el subgrave del acorde), predelay 18 ms."""
    rng = np.random.default_rng(seed)
    n = int(length * SR)
    t = np.arange(n) / SR
    env = np.exp(-6.91 * t / rt60) * np.minimum(1, t / 0.006)
    ir = rng.standard_normal((n, 2)) * env[:, None]
    ir = B.fir_lowpass(ir, 3200.0, taps=1025)
    ir = ir - B.fir_lowpass(ir, 70.0, taps=4097)
    ir = np.vstack([np.zeros((int(0.018 * SR), 2)), ir])
    return ir / np.sqrt((ir ** 2).sum() / 2)


def build(full, B):
    """full: tema decodificado (48 kHz, estereo). Uniones con fundido de igual potencia de
    12 ms centrado 6 ms antes del transitorio entrante. Devuelve (musica, bloques, info)."""
    blocks = plan()
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
            # cola: el tema seco se apaga con un fundido suave y una reverberacion del acorde
            # final (enviada desde el golpe) prolonga la resolucion durante el logo
            f0 = int(round((DRY_FADE_SRC[0] - b["src0"]) * SR + (v0 - a)))
            f1 = f0 + int(DRY_FADE_SRC[1] * SR)
            env = np.ones(len(seg))
            env[f0:f1] = 0.5 * (1 + np.cos(np.linspace(0, np.pi, f1 - f0)))
            env[f1:] = 0
            dry = seg * env[:, None]
            r0 = int(round((HIT_SRC - 0.004 - b["src0"]) * SR + (v0 - a)))
            send = np.zeros_like(dry)
            send[r0:] = dry[r0:]
            ir = tail_ir(B, TAIL_RT60, 5.0)
            wet = B.convolve(np.vstack([send, np.zeros((len(ir), 2))]), ir)[:len(dry)]
            seg = dry + wet * 10 ** (TAIL_WET_DB / 20)
        out[a:a + len(seg)] += seg[:len(out) - a]
    m = out[:N]
    vo = src_to_video(blocks, INTRO_OPEN_SRC)
    k = int(round(vo * SR)) - pre - h          # mismo fundido de 12 ms que las uniones
    lp = B.fir_lowpass(m[:k + xf + SR // 10], INTRO_HP_HZ, taps=4097)
    hp = m[:k + xf + SR // 10] - lp
    w = np.zeros(k + xf + SR // 10)
    w[k:k + xf] = np.sin(np.linspace(0, np.pi / 2, xf)) ** 2
    w[k + xf:] = 1
    m[:len(w)] = hp * (10 ** (INTRO_GAIN_DB / 20)) * (1 - w)[:, None] + m[:len(w)] * w[:, None]
    fi = int(0.008 * SR)
    m[:fi] *= (0.5 * (1 - np.cos(np.linspace(0, np.pi, fi))))[:, None]
    info = [dict(bloque=b["name"], fuente_ini=round(b["src0"], 4),
                 fuente_fin=None if b["src1"] is None else round(b["src1"], 4), video_ini=round(b["v0"], 4))
            for b in blocks]
    return m, blocks, dict(bloques=info, golpe_fuente=HIT_SRC, golpe_video=ANCH_V,
                           intro_paso_alto_hz=INTRO_HP_HZ, groove_completo_desde_s=round(vo, 4))


def src_to_video(blocks, s):
    """Primer bloque que contiene el instante s de la fuente -> tiempo de video."""
    for b in blocks:
        s1 = b["src1"] if b["src1"] is not None else 1e9
        if b["src0"] <= s < s1:
            return b["v0"] + (s - b["src0"])
    return None


if __name__ == "__main__":
    for b in plan():
        print(f"{b['name']:42s} fuente {b['src0']:8.3f} -> video {b['v0']:7.3f}")
