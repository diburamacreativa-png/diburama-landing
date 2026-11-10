# DIBURAMA · THERMOLIME V6 — mezcla de 22 s con resolución musical
# El fragmento de 20 s está en re♯ menor y termina sobre do♯ (VII): no resuelve. Se construye un final con material
# de la propia canción:
#   17,69 s  golpe de marca (música + SFX 13, como en la V5)
#   18,02–18,69 s  la base rítmica se apaga con un filtro paso bajo que se cierra (reducción de intensidad, sin corte)
#   18,69 s  (golpe de compás) entra el acorde de TÓNICA: componente armónica (sin percusión) de los dos pasajes de la
#            canción que suenan en re♯ (0,02 s y 8,69 s), con una reverberación larga que se extingue sola hasta 22 s.
# No se añade silencio, no se congela el audio y no se repiten compases.
# uso: python3 audio_v6.py <music.mp3> <sfx_dir> <out_dir>
import os, sys, json
os.environ['REEL_AUDIO'] = 'v5'                      # mismo plan de SFX que la V5 (todos los eventos anteriores a 17,69 s)
import numpy as np, soundfile as sf
from scipy.signal import stft, istft, butter, sosfilt, sosfiltfilt, fftconvolve
from scipy.ndimage import median_filter
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import audio as A

SR = A.SR
DUR6 = 22.0; N6 = int(SR * DUR6)
T_DIM, T_RES = 18.02, 18.69                          # inicio de la bajada · golpe de compás de la resolución
TONIC_SRC = [(0.02, 1.30, 1.0), (8.69, 9.36, 0.8)]   # pasajes en re♯ (inicio y caída): (desde, hasta, peso)

def hpss_harmonic(x):
    """separación armónico/percusivo por filtros de mediana (Fitzgerald 2010) — devuelve la parte armónica estéreo"""
    out = []
    for ch in range(2):
        f, t, Z = stft(x[:, ch], SR, nperseg=4096, noverlap=4096 - 512)
        M = np.abs(Z)
        Hh = median_filter(M, size=(1, 31)); Pp = median_filter(M, size=(31, 1))
        mask = Hh ** 2 / (Hh ** 2 + Pp ** 2 + 1e-12)
        _, y = istft(Z * mask, SR, nperseg=4096, noverlap=4096 - 512)
        out.append(y[:len(x)])
    return np.stack(out, 1)

def reverb_ir(rt_low=4.6, rt_mid=3.8, rt_high=1.9, length=5.5, predelay=0.025, seed=3):
    """respuesta al impulso sintética estéreo: ruido decorrelado con caída dependiente de la frecuencia"""
    rng = np.random.default_rng(seed); n = int(length * SR); t = np.arange(n) / SR
    ir = np.zeros((n, 2))
    bands = [(butter(4, 250, 'low', fs=SR, output='sos'), rt_low),
             (butter(4, [250, 3000], 'band', fs=SR, output='sos'), rt_mid),
             (butter(4, 3000, 'high', fs=SR, output='sos'), rt_high)]
    for ch in range(2):
        nz = rng.normal(0, 1, n)
        for sos, rt in bands:
            ir[:, ch] += sosfilt(sos, nz) * np.exp(-6.91 * t / rt)
    ir[:int(predelay * SR)] = 0
    ir[:int(predelay * SR) + 240] *= np.linspace(0, 1, int(predelay * SR) + 240)[:, None]
    return ir / np.sqrt((ir ** 2).sum(0, keepdims=True))

def build_music(music_path):
    mus20 = A.load_music(music_path)                 # 20 s, recortado el relleno del MP3 (como en V1–V5)
    out = np.zeros((N6, 2)); out[:len(mus20)] = mus20
    # 1) bajada de intensidad: filtro paso bajo que se cierra 16 kHz → 500 Hz y ganancia hasta −12 dB en 18,69 s;
    #    la base se funde con el acorde de tónica en los 0,30 s siguientes (sin hueco entre ambos)
    i0, i1 = int(T_DIM * SR), int((T_RES + 0.30) * SR)
    seg = out[i0:i1].copy(); n = len(seg); blk = 960
    yseg = np.zeros_like(seg); zi = None
    for b in range(0, n, blk):
        u = min(1.0, b / (int((T_RES - T_DIM) * SR)))
        fc = 16000 * (500 / 16000) ** (u ** 1.3)
        sos = butter(2, fc, 'low', fs=SR, output='sos')
        if zi is None: zi = np.zeros((sos.shape[0], 2, 2))
        chunk, zi_new = [], []
        for ch in range(2):
            y, z = sosfilt(sos, seg[b:b + blk, ch], zi=zi[:, :, ch])
            chunk.append(y); zi_new.append(z)
        zi = np.stack(zi_new, 2)
        g = 10 ** (-12 * u ** 1.6 / 20)
        yseg[b:b + blk] = np.stack(chunk, 1) * g
    xf = int(0.30 * SR); yseg[-xf:] *= (np.linspace(1, 0, xf) ** 2)[:, None]   # fundido cruzado con la tónica
    out[i0:i1] = yseg; out[i1:] = 0
    # 2) acorde de tónica a partir de la propia canción
    harm = hpss_harmonic(mus20)
    chord = np.zeros((int(1.4 * SR), 2))
    for a, b, w in TONIC_SRC:
        s_ = harm[int(a * SR):int(b * SR)] * w
        env = np.ones(len(s_)); fi, fo = int(0.04 * SR), int(0.35 * SR)
        env[:fi] = np.linspace(0, 1, fi); env[-fo:] = np.linspace(1, 0, fo) ** 2
        chord[:len(s_)] += s_ * env[:, None]
    chord = sosfiltfilt(butter(2, 70, 'high', fs=SR, output='sos'), chord, axis=0)
    k0 = int(T_RES * SR); L = N6 - k0
    wet = np.stack([fftconvolve(chord[:, 0], reverb_ir(seed=3)[:, 0])[:L],
                    fftconvolve(chord[:, 1], reverb_ir(seed=7)[:, 1])[:L]], 1)
    # niveles: el acorde llega a −14 dB respecto a la música en su sección fuerte; la cola se extingue por sí sola
    ref = np.sqrt((mus20[int(16.0 * SR):int(17.6 * SR)] ** 2).mean())
    dry_g = 0.42 * ref / (np.sqrt((chord ** 2).mean()) + 1e-12)
    wet_g = 0.55 * ref / (np.sqrt((wet[:int(0.6 * SR)] ** 2).mean()) + 1e-12)
    out[k0:k0 + len(chord)] += chord[:N6 - k0] * dry_g
    out[k0:k0 + len(wet)] += wet * wet_g
    # últimos 0,35 s: la cola (ya muy baja) termina en silencio digital sin clic
    tail = int(0.35 * SR); out[-tail:] *= (np.linspace(1, 0, tail) ** 2)[:, None]
    return out

def main(music_path, sfx_dir, out_dir):
    os.makedirs(out_dir, exist_ok=True)
    M = build_music(music_path)
    A.N, A.DUR = N6, DUR6
    A.load_music = lambda p: M                       # el resto de la cadena (SFX por pico, ducking, limitador) es la de la V5
    A.main(music_path, sfx_dir, out_dir)
    # informe del cierre: nivel por 0,5 s y nota dominante de la cola
    x, _ = sf.read(os.path.join(out_dir, 'master_mix.wav'))
    m = x.mean(1); rms = [round(20 * np.log10(np.sqrt((m[int(t * SR):int((t + 0.5) * SR)] ** 2).mean()) + 1e-12), 1) for t in np.arange(16, 22, 0.5)]
    f, t, Z = stft(m[int(19.0 * SR):int(21.5 * SR)], SR, nperseg=16384)
    S = (np.abs(Z) ** 2).sum(1); band = (f > 60) & (f < 2000)
    names = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B']
    c = np.zeros(12); np.add.at(c, np.round(12 * np.log2(f[band] / 261.63)).astype(int) % 12, S[band]); c /= c.max()
    rep = json.load(open(os.path.join(out_dir, 'audio_report.json')))
    rep['cierre'] = dict(rms_db_cada_0_5s_desde_16s=rms, croma_cola_19_21_5s={names[i]: round(float(c[i]), 2) for i in np.argsort(-c)[:5]},
                         ultimo_pico_dbfs=round(20 * np.log10(np.abs(x[-int(0.05 * SR):]).max() + 1e-12), 1))
    json.dump(rep, open(os.path.join(out_dir, 'audio_report.json'), 'w'), indent=1)
    print(json.dumps(rep['cierre'], indent=1))
    print({k: rep[k] for k in ['master_true_peak_db', 'limiter_max_gain_reduction_db', 'mono_sum_loss_db']})

if __name__ == '__main__': main(*sys.argv[1:4])
