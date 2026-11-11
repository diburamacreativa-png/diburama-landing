# DIBURAMA · VISUAL LAB — versión horizontal LinkedIn (24 s) · edición musical y mezcla
# FUENTE: solo está disponible el fragmento de 20 s de «Digital Ascension» (la canción completa no llegó al entorno).
# Edición por compases (90 BPM · compás = 2,6667 s · re♯ menor), sin estirar ni cambiar el tempo:
#   salida 0,00–16,02 s  = fragmento 0,00–16,02 s
#   salida 16,02–18,69 s = fragmento 13,35–16,02 s  (se amplía un compás de la misma armonía; corte en el tiempo fuerte,
#                                                    alineado por correlación y con fundido de 20 ms)
#   salida 18,69–20,36 s = fragmento 16,02–17,69 s  (preparación del clímax)
#   20,36 s  golpe de marca (fragmento 17,69 s) + SFX 13
#   20,69–21,36 s  la base se apaga con un filtro que se cierra (los graves continúan)
#   21,36 s  acorde de TÓNICA (re♯–fa♯–la♯) extraído de la propia canción + resonancia que se extingue hasta 24,00 s
# Si llega la canción completa, basta con cambiar EDIT (lista de tramos) por tramos de la canción original.
# uso: python3 audio_linkedin.py <music.mp3> <sfx_dir> <out_dir>
import os, sys, json
import numpy as np, soundfile as sf
from scipy.signal import butter, sosfilt, sosfiltfilt, fftconvolve, stft
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import audio as A
from audio_v6 import hpss_harmonic, reverb_ir, TONIC_SRC

SR = A.SR; DUR = 24.0; N = int(SR * DUR)
BAR = 4 * 60 / 90
EDIT = [(0.0, 16.0225, 0.0), (13.355, 16.0225, 16.0225), (16.0225, 19.95, 16.0225 + BAR)]   # (desde, hasta, posición en salida)
HIT = 16.0225 + BAR + (17.69 - 16.0225)       # 20,357 s · golpe de marca
T_DIM, T_RES = HIT + 0.333, HIT + 1.0         # bajada y tónica (siguiente tiempo fuerte)

def onset_time(x, t0, win=0.030):
    """instante preciso del transitorio (envolvente de agudos > 2 kHz) cerca de t0"""
    seg = x[int((t0 - win) * SR):int((t0 + win) * SR)].mean(1)
    hf = sosfiltfilt(butter(4, 2000, 'high', fs=SR, output='sos'), seg)
    env = np.convolve(np.abs(hf), np.ones(48) / 48, 'same')
    d = np.diff(env, prepend=env[0])
    return t0 - win + np.argmax(d) / SR

def best_lag(x, a, b):
    """retardo (muestras) para que el transitorio del tramo nuevo caiga donde caería el del original"""
    ta, tb = onset_time(x, a), onset_time(x, b)
    return int(round(((tb - b) - (ta - a)) * SR)), (round(ta, 4), round(tb, 4))

def build_music(music_path):
    src = A.load_music(music_path)
    out = np.zeros((N, 2)); xf = int(0.020 * SR); report = []
    for i, (a, b, pos) in enumerate(EDIT):
        lag = 0
        if i > 0:   # alinear el tramo nuevo con el tiempo fuerte donde termina el anterior
            prev_end_src = EDIT[i - 1][1]
            lag, (ta, tb) = best_lag(src, prev_end_src, a); report.append(dict(corte_salida_s=round(pos, 3), transitorio_original_s=ta, transitorio_nuevo_s=tb, ajuste_ms=round(1000 * lag / SR, 2)))
        i0 = int(a * SR) + lag; i1 = int(b * SR) + lag; p = int(pos * SR) - (xf if i > 0 else 0)
        seg = src[i0 - (xf if i > 0 else 0):min(i1 + xf, len(src))].copy()
        n = min(len(seg), N - p)
        env = np.ones(n)
        if i > 0: env[:xf] = np.sin(np.linspace(0, np.pi / 2, xf)) ** 2               # fundido de potencia constante
        if i < len(EDIT) - 1 and n > xf: env[-xf:] = np.cos(np.linspace(0, np.pi / 2, xf)) ** 2
        out[p:p + n] += seg[:n] * env[:, None]
    # bajada de intensidad tras el golpe de marca (filtro 16 kHz → 500 Hz, hasta −12 dB) y fundido cruzado con la tónica
    i0, i1 = int(T_DIM * SR), int((T_RES + 0.30) * SR)
    seg = out[i0:i1].copy(); yseg = np.zeros_like(seg); blk = 960; zi = np.zeros((1, 2, 2))
    for bb in range(0, len(seg), blk):
        u = min(1.0, bb / int((T_RES - T_DIM) * SR))
        sos = butter(2, 16000 * (500 / 16000) ** (u ** 1.3), 'low', fs=SR, output='sos')
        ys = []
        for ch in range(2):
            y, z = sosfilt(sos, seg[bb:bb + blk, ch], zi=zi[:, :, ch]); ys.append(y); zi[:, :, ch] = z
        yseg[bb:bb + blk] = np.stack(ys, 1) * 10 ** (-12 * u ** 1.6 / 20)
    k = int(0.30 * SR); yseg[-k:] *= (np.linspace(1, 0, k) ** 2)[:, None]
    out[i0:i1] = yseg; out[i1:] = 0
    # acorde de tónica a partir de la propia canción (componente armónica de los pasajes en re♯) + resonancia
    harm = hpss_harmonic(src); chord = np.zeros((int(1.4 * SR), 2))
    for a, b, w in TONIC_SRC:
        s_ = harm[int(a * SR):int(b * SR)] * w; env = np.ones(len(s_)); fi, fo = int(0.04 * SR), int(0.35 * SR)
        env[:fi] = np.linspace(0, 1, fi); env[-fo:] = np.linspace(1, 0, fo) ** 2; chord[:len(s_)] += s_ * env[:, None]
    chord = sosfiltfilt(butter(2, 70, 'high', fs=SR, output='sos'), chord, axis=0)
    k0 = int(T_RES * SR); L = N - k0
    wet = np.stack([fftconvolve(chord[:, 0], reverb_ir(seed=3)[:, 0])[:L], fftconvolve(chord[:, 1], reverb_ir(seed=7)[:, 1])[:L]], 1)
    ref = np.sqrt((src[int(16.0 * SR):int(17.6 * SR)] ** 2).mean())
    out[k0:k0 + len(chord)] += chord[:L] * 0.42 * ref / (np.sqrt((chord ** 2).mean()) + 1e-12)
    out[k0:] += wet * 0.55 * ref / (np.sqrt((wet[:int(0.6 * SR)] ** 2).mean()) + 1e-12)
    t = int(0.35 * SR); out[-t:] *= (np.linspace(1, 0, t) ** 2)[:, None]
    return out, report

# SFX: (archivo, instante del pico en la salida, ganancia dB) — sincronizados con los cortes del montaje horizontal
def plan():
    return [("01_Impacto_inicial_HOOK_0s", 0.017, -4.0), ("02_Whoosh_barrido_termico_2s", 1.685, -10.0),
            ("03_Succion_entrada_particulas_4s", 3.355, -8.0), ("04_Zoom_microscopico_6s", 4.018, -9.0),
            ("02_Whoosh_barrido_termico_2s#scan", 6.40, -11.0), ("05_Riser_revelacion_acaba_en_8s", 8.633, -9.0),
            ("06_Impacto_revelacion_tecnica_8s", 8.688, -4.0), ("07_Click_capas_tecnicas_10_5s", 10.022, -10.0),
            ("08_Corte_golpe_aplicacion_real_12s", 12.022, -5.5), ("09_Textura_proyeccion_revestimiento_12_3s", 13.40, -13.0),
            ("10_Transicion_resultado_14s", 16.022, -9.0), ("11_Triple_corte_montaje_16s#0", 18.688, -8.0),
            ("11_Triple_corte_montaje_16s#1", 19.355, -8.0), ("11_Triple_corte_montaje_16s#2", 19.69, -8.0),
            ("12_Micro_riser_logo_desde_17_1s", HIT - 0.012, -8.5), ("13_Impacto_logo_final_18s", HIT, -3.0)]

def main(music_path, sfx_dir, out_dir):
    os.makedirs(out_dir, exist_ok=True)
    mus, cuts = build_music(music_path)
    sfx = np.zeros((N, 2)); duck = np.zeros(N); rep = []
    for name, tpk, gain in plan():
        base, _, part = name.partition('#')
        y, _ = sf.read(os.path.join(sfx_dir, base + '.wav'), always_2d=True)
        if part.isdigit():
            a, b = A.SPLIT11[int(part)]; y = y[int(a * SR): None if b is None else int(b * SR)].copy()
            fl = int(0.008 * SR); y[:fl] *= np.linspace(0, 1, fl)[:, None]; y[-fl:] *= np.linspace(1, 0, fl)[:, None]
        pk = A.peak_time(y); y = A.hpf(A.mono_lows(y)) * A.db(gain)
        i0 = int(round((tpk - pk) * SR)); s0 = max(0, -i0); i0 = max(0, i0); n = min(len(y) - s0, N - i0)
        sfx[i0:i0 + n] += y[s0:s0 + n]
        if base[:2] in ('01', '06', '08', '13'):
            e = np.abs(y[s0:s0 + n]).max(1); duck[i0:i0 + n] = np.maximum(duck[i0:i0 + n], e / (e.max() + 1e-9))
        rep.append(dict(sfx=name, pico_s=round(tpk, 3), ganancia_db=gain))
    from scipy.ndimage import maximum_filter1d, uniform_filter1d
    env = uniform_filter1d(maximum_filter1d(duck, int(0.12 * SR)), int(0.03 * SR))
    low = sosfiltfilt(butter(4, 140, 'low', fs=SR, output='sos'), mus, axis=0)
    mix = (mus - low) + low * (1 - (1 - A.db(-4.5)) * env)[:, None] + sfx
    master, gr = A.limiter(mix, -1.5); master[:24] *= np.linspace(0, 1, 24)[:, None]
    sfx_only = sfx * min(1.0, A.db(-1.5) / A.db(A.true_peak_db(sfx)))
    sf.write(os.path.join(out_dir, 'master_mix.wav'), master.astype(np.float32), SR, subtype='PCM_24')
    sf.write(os.path.join(out_dir, 'sfx_only.wav'), sfx_only.astype(np.float32), SR, subtype='PCM_24')
    m = master.mean(1)
    f, t, Z = stft(m[int(21.6 * SR):int(23.6 * SR)], SR, nperseg=16384); S = (np.abs(Z) ** 2).sum(1); band = (f > 60) & (f < 2000)
    names = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B']
    c = np.zeros(12); np.add.at(c, np.round(12 * np.log2(f[band] / 261.63)).astype(int) % 12, S[band]); c /= c.max()
    info = dict(edicion=dict(tramos=[dict(fragmento_desde_s=a, fragmento_hasta_s=b, salida_desde_s=round(p, 3)) for a, b, p in EDIT],
                             cortes=cuts, golpe_marca_s=round(HIT, 3), bajada_s=round(T_DIM, 3), tonica_s=round(T_RES, 3)),
                sfx=rep, master_true_peak_db=round(A.true_peak_db(master), 2), limitador_reduccion_max_db=round(gr, 2),
                rms_db_cada_0_5s_desde_18s=[round(float(20 * np.log10(np.sqrt((m[int(x * SR):int((x + .5) * SR)] ** 2).mean()) + 1e-12)), 1) for x in np.arange(18, 24, .5)],
                croma_cola_21_6_23_6s={names[i]: round(float(c[i]), 2) for i in np.argsort(-c)[:4]},
                ultimo_pico_dbfs=round(float(20 * np.log10(np.abs(master[-int(0.05 * SR):]).max() + 1e-12)), 1),
                perdida_suma_mono_db=round(float(10 * np.log10((m ** 2).mean() / ((master ** 2).mean() + 1e-12))), 2))
    json.dump(info, open(os.path.join(out_dir, 'audio_report.json'), 'w'), indent=1, ensure_ascii=False)
    print(json.dumps({k: v for k, v in info.items() if k != 'sfx'}, indent=1, ensure_ascii=False))

if __name__ == '__main__': main(*sys.argv[1:4])
