# DIBURAMA — LA GOTA · Música y diseño sonoro sintetizados (120 BPM, Re menor → Re mayor).
# Uso: python3 audio/score.py  → audio/score_raw.wav (48 kHz estéreo float32, 27 s exactos, -14 LUFS / ≤ -1,5 dBTP)
# Dependencias: pip install -r requirements-audio.txt
import numpy as np
from scipy.signal import fftconvolve, butter, sosfilt, resample_poly
from scipy.io import wavfile
from pedalboard import Pedalboard, HighpassFilter, LowShelfFilter, PeakFilter, Compressor, Limiter
SR = 48000; DUR = 27.0; N = int(SR * DUR)
rng = np.random.default_rng(7)
L = np.zeros(N); R = np.zeros(N); REV = np.zeros(N)  # bus de reverb (mono)
BEAT = 0.5

def t_(d): return np.arange(int(d * SR)) / SR
def env(n, a=0.002, d=0.2):
    t = np.arange(n) / SR; e = np.exp(-t / d); att = np.clip(t / a, 0, 1) if a > 0 else 1; return e * att
def place(sig, at, gain=1.0, pan=0.0, rev=0.0):
    i = int(at * SR)
    if i >= N or i + len(sig) <= 0: return
    s = sig
    if i < 0: s = s[-i:]; i = 0
    s = s[: N - i]
    l = np.cos((pan + 1) * np.pi / 4); r = np.sin((pan + 1) * np.pi / 4)
    L[i:i + len(s)] += s * gain * l * 1.414; R[i:i + len(s)] += s * gain * r * 1.414
    REV[i:i + len(s)] += s * gain * rev
def filt(x, kind, f, order=2):
    sos = butter(order, f, btype=kind, fs=SR, output='sos'); return sosfilt(sos, x)
def noise(d): return rng.standard_normal(int(d * SR))
def hz(n): return 440 * 2 ** ((n - 69) / 12)  # MIDI → Hz
def silence(a, b): i, j = int(a * SR), int(b * SR); L[i:j] = 0; R[i:j] = 0

# ---------- instrumentos ----------
def plic(tuned=None, dur=0.35):
    t = t_(dur)
    f0, f1 = 700, (tuned or 1900)
    f = f0 * (f1 / f0) ** np.clip(t / 0.022, 0, 1)
    ph = 2 * np.pi * np.cumsum(f) / SR
    s = np.sin(ph) * env(len(t), 0.0005, 0.045)
    click = filt(noise(0.004), 'highpass', 3000) * 0.4
    s[:len(click)] += click
    if tuned:  # cola de campana (firma sonora)
        tb = t_(2.2); bell = sum(np.sin(2 * np.pi * tuned * k * tb) * a * np.exp(-tb / d) for k, a, d in [(1, 0.5, 1.2), (2.0, 0.18, 0.7), (2.76, 0.12, 0.45), (5.4, 0.05, 0.2)])
        out = np.zeros(len(tb)); out[:len(s)] += s; out += bell * np.clip(tb / 0.01, 0, 1); return out
    return s
def sub_boom(f0=48, f1=30, d=1.4):
    t = t_(d); f = f1 + (f0 - f1) * np.exp(-t / 0.25); s = np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t / (d / 3))
    return np.tanh(s * 2.2) * 0.7
def kick(g=1.0):
    t = t_(0.45); f = 48 + 110 * np.exp(-t / 0.035); s = np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t / 0.16)
    s[:200] += filt(noise(200 / SR), 'highpass', 1500) * np.linspace(0.5, 0, 200)
    return np.tanh(s * 1.6) * g
def soft_kick(): return filt(kick(0.8), 'lowpass', 400)
def hat(d=0.04, f=7000): return filt(noise(d), 'highpass', f) * env(int(d * SR), 0.0005, d / 4)
def clap():
    s = np.zeros(int(0.3 * SR))
    for k, o in enumerate([0, 0.011, 0.023]): n = filt(noise(0.25), 'bandpass', [900, 3500]) * env(int(0.25 * SR), 0.0005, 0.02 if k < 2 else 0.09); i = int(o * SR); s[i:i + len(n)] += n[: len(s) - i]
    return s * 0.8
def metal(f=520, d=0.8):
    t = t_(d); return sum(np.sin(2 * np.pi * f * r * t + r) * a for r, a in [(1, 1), (2.76, 0.6), (5.4, 0.4), (8.93, 0.25)]) * np.exp(-t / (d / 5)) * 0.35
def ink(d=0.18):
    n = filt(noise(d), 'bandpass', [300, 1800]); e = np.sin(np.linspace(0, np.pi, len(n))) ** 2; return n * e * 0.5
def servo(f0, f1, d):
    t = t_(d); f = f0 + (f1 - f0) * (t / d) ** 0.7 + 12 * np.sin(2 * np.pi * 30 * t)
    s = np.sin(2 * np.pi * np.cumsum(f) / SR) + 0.3 * np.sin(4 * np.pi * np.cumsum(f) / SR)
    return s * np.sin(np.linspace(0, np.pi, len(t))) * 0.18
def tick(): return filt(noise(0.012), 'bandpass', [2500, 6000]) * env(int(0.012 * SR), 0.0002, 0.003) * 1.2
def saw(f, d):
    t = t_(d); ph = (f * t) % 1; return 2 * ph - 1
def bass(n, d):
    s = saw(hz(n), d) + saw(hz(n) * 1.004, d); s = filt(s, 'lowpass', 380) * env(len(s), 0.004, d * 0.6); return np.tanh(s * 1.3) * 0.5
def pad(notes, d, bright=1200):
    t = t_(d); s = np.zeros(len(t))
    for n in notes:
        for det in (-0.08, 0, 0.08): s += saw(hz(n + det), d)
    s = filt(s, 'lowpass', bright) / (len(notes) * 3)
    fade = np.minimum(np.clip(t / 0.35, 0, 1), np.clip((d - t) / 0.5, 0, 1)); return s * fade
def bleep(n, d=0.09):
    t = t_(d); s = np.sign(np.sin(2 * np.pi * hz(n) * t)) * 0.3 + np.sin(2 * np.pi * hz(n) * t) * 0.7
    return filt(s, 'lowpass', 5000) * env(len(t), 0.001, d / 3) * 0.35
def marimba(n, d=0.6):
    t = t_(d); f = hz(n); s = np.sin(2 * np.pi * f * t) * np.exp(-t / 0.18) + 0.35 * np.sin(2 * np.pi * f * 3.93 * t) * np.exp(-t / 0.04)
    return s * 0.5
def choir(notes, d):
    t = t_(d); s = np.zeros(len(t))
    for n in notes:
        for k, a in [(1, 1), (2, 0.35), (3, 0.15)]: s += a * np.sin(2 * np.pi * hz(n) * k * t * (1 + 0.004 * np.sin(2 * np.pi * 5.2 * t + n)))
    s = filt(s, 'lowpass', 2500) / len(notes)
    return s * np.minimum(np.clip(t / 0.6, 0, 1), np.clip((d - t) / 1.0, 0, 1)) * 0.4
def whoosh(d, f0, f1, peak=0.6):
    n = noise(d); t = np.arange(len(n)) / SR; out = np.zeros(len(n)); seg = 2048
    for i in range(0, len(n), seg):
        u = i / len(n); f = f0 * (f1 / f0) ** u
        out[i:i + seg] = filt(n[max(0, i - 512):i + seg], 'bandpass', [f * 0.6, min(f * 1.6, 20000)])[-len(n[i:i + seg]):]
    e = np.exp(-((t / d - peak) ** 2) / 0.06); return out * e * 0.7
def pencil(): return filt(noise(0.09), 'bandpass', [1800, 5200]) * np.abs(np.sin(np.linspace(0, 9 * np.pi, int(0.09 * SR)))) * 0.25

# ---------- partitura ----------
# 0–0,8: tono de sala + zumbido fluorescente
tt = t_(0.95); room = filt(noise(0.95), 'lowpass', 900) * 0.02 + np.sin(2 * np.pi * 100 * tt) * 0.012 + np.sin(2 * np.pi * 200 * tt) * 0.006
place(room * np.clip((0.95 - tt) / 0.2, 0, 1), 0)
place(whoosh(0.25, 900, 300, peak=0.0) * 0.4, 0)  # cola del barrido final (loop)
# 0,8: PLIC + impacto grave
place(plic(), 0.8, 0.9, pan=0.0, rev=0.5); place(sub_boom(), 0.8, 1.0)
place(filt(noise(0.3), 'lowpass', 1500) * env(int(0.3 * SR), 0.001, 0.05) * 0.5, 0.8, 0.8)
# 1,0–6,0: pulso de tinta
for k in range(10):
    b = 1.0 + k * BEAT
    place(soft_kick(), b, 0.55 + 0.04 * k); place(ink(), b + 0.02, 0.5, pan=-0.3 + 0.06 * k, rev=0.2)
    place(tick(), b + 0.25, 0.35, pan=0.4); place(tick(), b + 0.375, 0.18, pan=-0.4)
# ES → ERA: pop + brillo
place(marimba(74, 0.5) * 0.8, 1.28, 0.6, rev=0.4); place(marimba(81, 0.5) * 0.6, 1.4, 0.5, pan=0.3, rev=0.4)
# 3,0–5,5: extrusión, servos, encajes metálicos
for i in range(6): place(metal(900 + 90 * i, 0.3) * 0.8, 3.02 + 0.07 * i, 0.5, pan=-0.5 + 0.2 * i, rev=0.2)
place(servo(220, 700, 0.9), 3.1, 1.0, pan=-0.2, rev=0.2); place(servo(300, 1100, 1.2), 4.05, 1.0, pan=0.2, rev=0.2)
place(whoosh(1.0, 400, 5000, peak=0.9) * 0.9, 5.0, 0.8, rev=0.3)
# 6,0–16,0: parte fuerte (Re menor)
prog = [(38, 38, 41, 33), (34, 34, 36, 41), (38, 38, 41, 33), (34, 36, 40, 45), (38, 41, 43, 45)]
for bar in range(5):
    t0 = 6.0 + bar * 2.0
    for q in range(4):
        b = t0 + q * BEAT
        half = t0 >= 10.5
        if not half or q % 2 == 0: place(kick(1.0 if not half else 0.8), b, 0.9)
        if q in (1, 3) and not half: place(clap(), b, 0.45, rev=0.25)
        for s16 in range(4):
            if t0 < 13.0: place(hat(0.03, 8000), b + s16 * 0.125, 0.12 if s16 % 2 else 0.2, pan=0.35 * (1 if s16 % 2 else -1))
        place(bass(prog[bar][q], 0.45), b, 0.8)
place(metal(520, 1.2), 6.0, 0.9, rev=0.5); place(clap(), 6.0, 0.5, rev=0.4)
for i, st in enumerate([6.0, 6.06, 6.18, 6.28, 6.38, 6.5]): place(metal(1300 + 150 * i, 0.25), st, 0.35, pan=-0.6 + 0.24 * i)
place(whoosh(0.6, 3000, 8000, peak=0.6) * 0.5, 6.7, 0.5)                 # giro de la tuerca
place(sub_boom(90, 60, 0.4) * 0.5, 7.35, 0.8); place(plic(2400, 0.2), 7.35, 0.5, rev=0.4)  # la cápsula se abre
for k in range(40): place(np.sin(2 * np.pi * hz(86 + (k % 5) * 2) * t_(0.05)) * env(int(0.05 * SR), 0.001, 0.015) * 0.12, 7.4 + k * 0.015, 1, pan=np.sin(k), rev=0.5)
# 8,0–10,5: interfaz — arpegios y glitches
arp = [74, 77, 81, 84, 81, 77]
for k in range(20): place(bleep(arp[k % 6]), 8.0 + k * 0.125, 0.8, pan=0.5 * np.sin(k), rev=0.15)
for g in (9.0, 9.5):
    chunk = bleep(96, 0.02)
    for r in range(4): place(chunk, g + r * 0.022, 0.6, pan=0.3)
place(tick() * 2, 9.98, 0.9); place(plic(1600, 0.15), 10.0, 0.4)  # clic del interruptor
# 10,5–13,0: apertura — pad amplio, viento
place(whoosh(1.0, 6000, 600, peak=0.4) * 0.8, 10.5, 0.7, rev=0.3)
place(pad([50, 53, 57, 62], 2.6, 1600), 10.9, 0.55, rev=0.5)
place(filt(noise(5.0), 'lowpass', 700) * 0.12 * np.sin(np.linspace(0, np.pi, int(5.0 * SR))), 10.8, 1, pan=0.2)
# 13,0–16,0: humano — motivo de marimba + lápiz
motif = [62, 65, 69, 72, 69, 65, 62, 60]
for k in range(12): place(marimba(motif[k % 8]), 13.0 + k * 0.25, 0.6, pan=-0.2 + 0.4 * (k % 2), rev=0.35)
place(pad([46, 50, 53, 58], 3.0, 1300), 13.0, 0.45, rev=0.5)
for k in range(6): place(pencil(), 13.75 + k * 0.28, 0.9, pan=0.1)
# 16,0–18,0: la música se reduce; tinta absorbida (reverse) hasta el silencio
rev_ink = whoosh(1.9, 300, 4000, peak=0.95)  # crece hasta el corte
place(rev_ink * 0.7, 16.05, 0.8, rev=0.4)
place(plic(1900)[::-1] * 0.8, 17.9 - 0.35, 0.6, rev=0.3)
place(pad([50, 53, 57], 2.0, 900), 16.0, 0.35, rev=0.6)

# ---------- reverb ----------
irt = t_(2.4); ir = rng.standard_normal(len(irt)) * np.exp(-irt / 0.55); ir = filt(ir, 'lowpass', 5000); ir /= np.sqrt(np.sum(ir ** 2))
wet = fftconvolve(REV, ir)[:N] * 0.35
L += wet; R += np.roll(wet, 331)
# fundido musical 16–18 y SILENCIO TOTAL 18,0–18,6 (corte seco, incluida la reverb)
fade = np.ones(N); i0, i1 = int(16.2 * SR), int(18.0 * SR); fade[i0:i1] = np.linspace(1, 0.55, i1 - i0) ** 1.5
L *= fade; R *= fade
silence(18.0, 18.6)

# ---------- 18,6–27: revelación, firma sonora, loop ----------
L2 = np.zeros(N); R2 = np.zeros(N); REV = np.zeros(N)
def place2(sig, at, gain=1.0, pan=0.0, rev=0.0):
    global L, R
    Lb, Rb = L.copy(), R.copy(); L[:] = 0; R[:] = 0
    place(sig, at, gain, pan, rev)
    L2[:] += L; R2[:] += R; L[:] = Lb; R[:] = Rb
place2(sub_boom(95, 26, 2.8) * 1.1, 18.6, 1.0)
place2(whoosh(2.5, 6000, 150, peak=0.12) * 1.0, 18.6, 0.8, rev=0.4)
place2(choir([62, 66, 69, 74], 3.9), 18.62, 0.8, rev=0.6)
motif2 = [62, 66, 69, 74, 69, 66, 69, 74]
for k in range(8): place2(marimba(motif2[k]), 19.6 + k * 0.25, 0.45, pan=-0.3 + 0.2 * (k % 4), rev=0.5)
place2(pad([50, 54, 57, 62], 4.0, 1800), 19.0, 0.35, rev=0.5)
place2(plic(hz(86)), 22.5, 1.0, rev=0.6)                        # FIRMA SONORA · Re6 afinado
place2(choir([50, 57, 62, 66], 4.4), 22.5, 0.5, rev=0.6)
place2(whoosh(0.5, 2000, 6000, peak=0.5) * 0.35, 23.1, 0.6, pan=0.3)
for k in range(17): place2(tick() * 0.7, 23.55 + k * 0.032, 0.5, pan=0.2)
place2(servo(600, 250, 0.3) * 1.2, 25.7, 0.7)                   # la gota se estira
place2(plic(1300, 0.2), 25.98, 0.7, rev=0.3)                    # se desprende
place2(whoosh(0.75, 300, 2500, peak=0.75) * 1.2, 26.25, 0.9)    # barrido de cámara → loop
irt = t_(2.4); ir = rng.standard_normal(len(irt)) * np.exp(-irt / 0.9); ir = filt(ir, 'lowpass', 6000); ir /= np.sqrt(np.sum(ir ** 2))
wet = fftconvolve(REV, ir)[:N] * 0.4
L2 += wet; R2 += np.roll(wet, 331)
L += L2; R += R2
# microfundidos en los extremos para el loop (sin clic)
k = int(0.004 * SR); ramp = np.linspace(0, 1, k)
L[:k] *= ramp; R[:k] *= ramp; L[-k:] *= ramp[::-1]; R[-k:] *= ramp[::-1]

# ---------- máster (pedalboard) ----------
# Objetivo: entregar a build.sh algo que loudnorm (-14 LUFS / -1 dBTP) solo tenga que mover con ganancia lineal.
# El tanh + normalización de pico anterior dejaba +0,9 dBTP y forzaba loudnorm a modo dinámico (ganancia variable).
LUFS, CEIL_TP = -14.0, -1.5
def lufs(x):  # ITU-R BS.1770-4 integrada (ponderación K + gating absoluto/relativo), coeficientes a 48 kHz
    k = np.array([[1.53512485958697, -2.69169618940638, 1.19839281085285, 1, -1.69065929318241, 0.73248077421585],
                  [1.0, -2.0, 1.0, 1, -1.99004745483398, 0.99007225036621]])
    y = sosfilt(k, x, axis=1); blk, hop = int(0.4 * SR), int(0.1 * SR)
    z = np.array([np.mean(y[:, i:i + blk] ** 2, axis=1).sum() for i in range(0, y.shape[1] - blk + 1, hop)])
    lk = lambda v: -0.691 + 10 * np.log10(v + 1e-20)
    z = z[lk(z) > -70]; z = z[lk(z) > lk(z.mean()) - 10]; return lk(z.mean())
def true_peak(x): return 20 * np.log10(np.abs(resample_poly(x, 4, 1, axis=1)).max())  # sobremuestreo x4
st = np.stack([L, R]).astype(np.float32); st *= 0.5 / np.abs(st).max()  # -6 dBFS de pico a la entrada del bus
bus = Pedalboard([
    HighpassFilter(28),                       # offset DC + subgraves inaudibles que solo consumen headroom
    LowShelfFilter(70, -2.0, 0.7),            # 25–150 Hz dominaban ~7 dB sobre los medios
    PeakFilter(3500, 1.5, 0.8),               # presencia: el destino es el altavoz del móvil (Reels)
    Compressor(threshold_db=-20, ratio=2, attack_ms=20, release_ms=150),  # pegamento suave; el ataque deja pasar el golpe del kick
])
st = bus(st, SR)
drive = 0.0  # entrada al Limiter de JUCE (lleva compensación propia: no es reducción de ganancia); solo sube si hace falta para llegar a LUFS con el pico en CEIL_TP
for _ in range(8):
    out = Limiter(threshold_db=-drive, release_ms=80)(st, SR) if drive > 0 else st.copy()
    out *= 10 ** ((CEIL_TP - true_peak(out)) / 20); d = LUFS - lufs(out)
    if d <= 0: out *= 10 ** (d / 20); break  # sobra loudness: basta con bajar ganancia
    if d < 0.05: break
    drive += d
# silencio total 18,0–18,6 y microfundidos del loop, de nuevo (los filtros IIR dejan colas)
out[:, int(18.0 * SR):int(18.6 * SR)] = 0
k = int(0.004 * SR); ramp = np.linspace(0, 1, k, dtype=np.float32); out[:, :k] *= ramp; out[:, -k:] *= ramp[::-1]
wavfile.write('audio/score_raw.wav', SR, out.T.astype(np.float32))
print(f'ok {out.T.shape}  {lufs(out):.2f} LUFS  {true_peak(out):.2f} dBTP  drive {drive:.2f} dB  '
      f'silencio 18,0–18,6: {np.abs(out[:, int(18.0 * SR):int(18.6 * SR)]).max()}')
