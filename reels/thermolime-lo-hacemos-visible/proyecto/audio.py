# DIBURAMA · THERMOLIME — mezcla de audio
# Música (MP3 20 s entregado) + 13 SFX originales colocados por PICO sobre los transitorios reales.
# uso: python3 audio.py <music.mp3> <sfx_dir> <out_dir>
import sys, os, subprocess, json
import numpy as np, soundfile as sf
from scipy.signal import butter, sosfiltfilt, stft, resample_poly

SR, DUR = 48000, 20.0
N = int(SR * DUR)
ENCODER_PAD = 0.040   # relleno del MP3 antes del primer golpe (los cues del CSV quedan exactos tras recortarlo)

# ---------- cues musicales nominales (s, timeline final) -> se afinan al transitorio real ±50 ms
CUES = dict(hook=0.02, prob=1.687, scan_end=2.687, micro=4.02, tens=6.02, pre=8.02, tech=8.687, tech3=10.02,
            app=12.025, noz=14.025, res=14.69, m0=16.025, m1=16.69, m2=17.025, m3=17.355, brand=17.69, last=19.36)

# ---------- plan de SFX: (archivo, cue o tiempo, alineación del pico, ganancia dB, notas)
PLAN = [
    ("01_Impacto_inicial_HOOK_0s",              "hook",  "peak", -4.0),
    ("02_Whoosh_barrido_termico_2s",            2.30,    "peak", -8.5),   # máximo de velocidad del barrido
    ("03_Succion_entrada_particulas_4s",        "micro", "peak", -7.5),   # la succión culmina en el match cut
    ("04_Zoom_microscopico_6s",                 "tens",  "peak", -8.0),
    ("05_Riser_revelacion_acaba_en_8s",         "tech",  "end",  -9.0),   # la cola muere justo antes del golpe
    ("06_Impacto_revelacion_tecnica_8s",        "tech",  "peak", -4.0),
    ("07_Click_capas_tecnicas_10_5s",           "tech3", "peak", -10.0),   # nodo fucsia de conexión
    ("08_Corte_golpe_aplicacion_real_12s",      "app",   "peak", -5.5),
    ("09_Textura_proyeccion_revestimiento_12_3s", 12.20, "start", -12.0),
    ("10_Transicion_resultado_14s",             "noz",   "peak", -9.0),   # barrido con el chorro
    ("11_Triple_corte_montaje_16s#0",           "m1",    "peak", -8.0),
    ("11_Triple_corte_montaje_16s#1",           "m2",    "peak", -8.0),
    ("11_Triple_corte_montaje_16s#2",           "m3",    "peak", -8.0),
    ("12_Micro_riser_logo_desde_17_1s",         "brand", "peak-12ms", -8.5),
    ("13_Impacto_logo_final_18s",               "brand", "peak", -3.0),
]
# V2: el golpe 08 marca la entrada de los primeros planos de aplicación (10,52 s) y el barrido 02 acompaña al iris (1,69 s)
if os.environ.get('REEL_AUDIO', 'v1') == 'v2':
    CUES['app'] = 10.52
    PLAN = [(n, ('prob' if n.startswith('02_') else w), al, g) for n, w, al, g in PLAN]

# V3 («Ventana a lo invisible»): 04 en la lente → microscópico, 02 en el escáner térmico, 09 bajo la proyección, 10 en el barrido spray → resultado
if os.environ.get('REEL_AUDIO', 'v1') == 'v3':
    _m = {'02_': 7.48, '04_': 'prob', '09_': 12.86, '10_': 'res'}
    PLAN = [(n, next((v for k, v in _m.items() if n.startswith(k)), w), al, g) for n, w, al, g in PLAN]

# V4 (Visual Lab multiventana): 02 en la entrada de la segunda ventana, 07 en la revelación de la ventana inferior, 10 en el barrido al resultado
if os.environ.get('REEL_AUDIO', 'v1') == 'v4':
    _m = {'02_': 'prob', '07_': 9.69, '10_': 'res'}
    PLAN = [(n, next((v for k, v in _m.items() if n.startswith(k)), w), al, g) for n, w, al, g in PLAN]

# V5: como V4 + barrido 02 (segunda instancia) en la entrada de la segunda gran ventana del clímax (16,36 s)
if os.environ.get('REEL_AUDIO', 'v1') == 'v5':
    _m = {'02_': 'prob', '07_': 9.69, '10_': 'res'}
    PLAN = [(n, next((v for k, v in _m.items() if n.startswith(k)), w), al, g) for n, w, al, g in PLAN]
    PLAN.append(("02_Whoosh_barrido_termico_2s#clx", 16.36, "peak", -11.0))

SPLIT11 = [(0.0, 0.45), (0.45, 0.95), (0.95, None)]  # tres golpes internos (0.005 / 0.507 / 1.005 s)
DUCK = {"01_Impacto_inicial_HOOK_0s", "06_Impacto_revelacion_tecnica_8s", "13_Impacto_logo_final_18s",
        "08_Corte_golpe_aplicacion_real_12s"}

def db(x): return 10 ** (x / 20)

def load_music(path):
    raw = subprocess.run(["ffmpeg", "-v", "error", "-i", path, "-ar", str(SR), "-ac", "2", "-f", "f32le", "-"],
                         capture_output=True, check=True).stdout
    x = np.frombuffer(raw, np.float32).reshape(-1, 2).astype(np.float64)
    x = x[int(ENCODER_PAD * SR):]
    out = np.zeros((N, 2)); n = min(N, len(x)); out[:n] = x[:n]
    # salida natural: micro-fundido de 120 ms sólo en el último tramo (evita clic al final del máster)
    end = n; f0 = end - int(0.12 * SR)
    out[f0:end] *= np.linspace(1, 0, end - f0)[:, None] ** 1.5
    return out

def onsets(x):
    m = x.mean(1); hop = 120
    f, t, Z = stft(m, SR, nperseg=2048, noverlap=2048 - hop)
    M = np.log1p(np.abs(Z) * 100)
    flux = np.r_[0, np.maximum(0, np.diff(M, axis=1)).sum(0)]
    return t, flux

def refine(cues, x):
    t, flux = onsets(x); out = {}
    for k, c in cues.items():
        sel = (t > c - 0.05) & (t < c + 0.05)
        out[k] = float(t[sel][np.argmax(flux[sel])]) if sel.any() else c
    return out

def peak_time(y):
    m = np.abs(y).max(1); w = int(0.005 * SR)
    return np.argmax(np.convolve(m, np.ones(w) / w, 'same')) / SR

def mono_lows(y, fc=150):
    """graves en mono (compatibilidad con altavoz de móvil / suma mono)"""
    sos = butter(4, fc, 'low', fs=SR, output='sos')
    mid = (y[:, 0] + y[:, 1]) / 2; side = (y[:, 0] - y[:, 1]) / 2
    side = side - sosfiltfilt(sos, side)
    return np.stack([mid + side, mid - side], 1)

def hpf(y, fc=32):
    return sosfiltfilt(butter(2, fc, 'high', fs=SR, output='sos'), y, axis=0)

def true_peak_db(x):
    up = resample_poly(x, 4, 1, axis=0)
    return 20 * np.log10(np.abs(up).max() + 1e-12)

def limiter(x, ceiling_db=-1.5, look=0.003, release=0.08):
    """limitador con anticipación sobre señal sobremuestreada 4x (control de pico verdadero)"""
    up = resample_poly(x, 4, 1, axis=0); sr4 = SR * 4
    c = db(ceiling_db)
    need = np.minimum(1.0, c / (np.abs(up).max(1) + 1e-12))
    L = int(look * sr4)
    # mínimo en ventana de anticipación
    from scipy.ndimage import minimum_filter1d
    g = minimum_filter1d(need, size=2 * L + 1, mode='nearest')
    # liberación exponencial
    a = np.exp(-1 / (release * sr4)); out = np.empty_like(g); prev = 1.0
    for i in range(len(g)):  # bucle simple (20 s · 192 kHz = 3.8 M muestras) -> vectorizado por bloques abajo
        v = g[i]; prev = v if v < prev else v + (prev - v) * a; out[i] = prev
    y = up * out[:, None]
    return resample_poly(y, 1, 4, axis=0), 20 * np.log10(out.min())

def main(music_path, sfx_dir, out_dir):
    os.makedirs(out_dir, exist_ok=True)
    mus = load_music(music_path)
    cues = refine(CUES, mus)
    sfx = np.zeros((N, 2)); duck_env = np.zeros(N); report = []
    for name, when, align, gain in PLAN:
        base, _, part = name.partition('#')
        y, sr = sf.read(os.path.join(sfx_dir, base + '.wav'), always_2d=True); assert sr == SR
        if part.isdigit():
            a, b = SPLIT11[int(part)] if part.isdigit() else (0.0, None); y = y[int(a * SR): None if b is None else int(b * SR)].copy()
            fl = int(0.008 * SR); y[:fl] *= np.linspace(0, 1, fl)[:, None]; y[-fl:] *= np.linspace(1, 0, fl)[:, None]
        pk = peak_time(y)                      # pico del sonido original (antes de filtrar)
        y = hpf(mono_lows(y)) * db(gain)
        T = cues[when] if isinstance(when, str) else when
        if align.startswith('peak'):
            off = float(align[4:].replace('ms', '')) / 1000 if len(align) > 4 else 0.0
            start = T + off - pk
        elif align == 'end':
            start = T - 0.015 - len(y) / SR
        else:
            start = T
        i0 = int(round(start * SR)); s0 = max(0, -i0); i0 = max(0, i0)
        n = min(len(y) - s0, N - i0)
        sfx[i0:i0 + n] += y[s0:s0 + n]
        if base in DUCK:
            e = np.abs(y[s0:s0 + n]).max(1); duck_env[i0:i0 + n] = np.maximum(duck_env[i0:i0 + n], e / (e.max() + 1e-9))
        report.append(dict(sfx=name, start=round(start, 3), peak_at=round(start + pk, 3), gain_db=gain))
    # dip de graves de la música bajo los impactos (los subgraves del SFX no compiten con el bombo)
    from scipy.ndimage import maximum_filter1d, uniform_filter1d
    env = uniform_filter1d(maximum_filter1d(duck_env, int(0.12 * SR)), int(0.03 * SR))
    sos = butter(4, 140, 'low', fs=SR, output='sos')
    low = sosfiltfilt(sos, mus, axis=0); high = mus - low
    mus_d = high + low * (1 - (1 - db(-4.5)) * env)[:, None]
    mix = mus_d + sfx
    pre_tp = true_peak_db(mix)
    master, gr = limiter(mix, -1.5)
    # cola de 10 ms a cero exacto en los extremos
    master[:24] *= np.linspace(0, 1, 24)[:, None]
    # versión sin música: mismos niveles de SFX, sin limitar salvo seguridad
    sfx_only = sfx * min(1.0, db(-1.5) / db(true_peak_db(sfx))) if true_peak_db(sfx) > -1.5 else sfx
    sf.write(os.path.join(out_dir, 'master_mix.wav'), master.astype(np.float32), SR, subtype='PCM_24')
    sf.write(os.path.join(out_dir, 'sfx_only.wav'), sfx_only.astype(np.float32), SR, subtype='PCM_24')
    sf.write(os.path.join(out_dir, 'music_trimmed.wav'), mus.astype(np.float32), SR, subtype='PCM_24')
    info = dict(cues=cues, sfx=report, mix_true_peak_before_limiter_db=round(pre_tp, 2),
                limiter_max_gain_reduction_db=round(gr, 2), master_true_peak_db=round(true_peak_db(master), 2),
                sfx_only_true_peak_db=round(true_peak_db(sfx_only), 2),
                mono_corr=float(np.corrcoef(master[:, 0], master[:, 1])[0, 1]),
                mono_sum_loss_db=round(10 * np.log10(((master.mean(1)) ** 2).mean() / ((master ** 2).mean() + 1e-12)), 2))
    ev = {}
    for r in report:
        c = int(r['peak_at'] * SR); w = int(0.06 * SR)
        rm = lambda z: 10 * np.log10((z[max(0, c - w):c + w] ** 2).mean() + 1e-12)
        ev[r['sfx']] = round(rm(sfx) - rm(mus_d), 1)
    info['sfx_minus_music_db_at_event'] = ev
    json.dump(info, open(os.path.join(out_dir, 'audio_report.json'), 'w'), indent=1)
    print(json.dumps(info, indent=1))

if __name__ == '__main__':
    main(*sys.argv[1:4])
