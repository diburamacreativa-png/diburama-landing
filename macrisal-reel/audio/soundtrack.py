# DIBURAMA × MACRISAL · Música y efectos sintetizados en código.
# 120 BPM, La menor. 1 compás = 2 s = 1 tramo del reel: cada cambio de escena cae en un primer tiempo.
# Los efectos se colocan en los eventos exportados desde la coreografía (audio/events.json).
#
# Uso (desde macrisal-reel/):  npm run audio
#   1) npx tsx scripts/export-events.ts   → audio/events.json
#   2) python3 audio/soundtrack.py         → public/audio/soundtrack.wav (−14 LUFS, pico −1 dBTP)
import json, os, subprocess, sys
import numpy as np
from scipy.signal import butter, sosfilt, fftconvolve

SR = 48000
DUR = 26.0
N = int(SR * DUR)
BPM = 120
BEAT = 60 / BPM          # 0,5 s
BAR = 4 * BEAT           # 2 s
S16 = BEAT / 4           # semicorchea
rng = np.random.default_rng(20261008)

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
EVENTS = os.path.join(HERE, 'events.json')
OUT = os.path.join(ROOT, 'public', 'audio', 'soundtrack.wav')

# ───────────────────────── buses ─────────────────────────
class Bus:
    def __init__(self):
        self.L = np.zeros(N); self.R = np.zeros(N)
    def place(self, sig, at, gain=1.0, pan=0.0):
        """Coloca una señal mono (o (L,R)) en el segundo `at` con panorama −1…1."""
        i = int(round(at * SR))
        if isinstance(sig, tuple):
            l, r = sig
        else:
            th = (np.clip(pan, -1, 1) + 1) * np.pi / 4
            l, r = sig * np.cos(th) * 1.414, sig * np.sin(th) * 1.414
        if i < 0:
            l, r = l[-i:], r[-i:]; i = 0
        n = min(len(l), N - i)
        if n <= 0: return
        self.L[i:i + n] += l[:n] * gain; self.R[i:i + n] += r[:n] * gain

drums, bass, music, verb_send, sfx = Bus(), Bus(), Bus(), Bus(), Bus()

# ───────────────────────── utilidades ─────────────────────────
def T(d): return np.arange(int(d * SR)) / SR
def hz(m): return 440.0 * 2 ** ((m - 69) / 12)
def filt(x, kind, f, order=2):
    return sosfilt(butter(order, f, btype=kind, fs=SR, output='sos'), x)
def noise(d): return rng.standard_normal(int(d * SR))
def adsr(n, a=0.005, d=0.1, s=0.0, r=0.05, hold=None):
    t = np.arange(n) / SR
    hold = n / SR - r if hold is None else hold
    e = np.where(t < a, t / max(a, 1e-6), s + (1 - s) * np.exp(-(t - a) / max(d, 1e-6)))
    rel = np.clip((t - hold) / max(r, 1e-6), 0, 1)
    return e * (1 - rel)
def saw(f, d, phase=None):
    """Diente de sierra con polyBLEP (sin aliasing audible)."""
    n = int(d * SR); dt = f / SR
    ph = ((phase if phase is not None else rng.random()) + dt * np.arange(n)) % 1.0
    y = 2 * ph - 1
    m = ph < dt; x = ph[m] / dt; y[m] -= x + x - x * x - 1
    m = ph > 1 - dt; x = (ph[m] - 1) / dt; y[m] -= x * x + x + x + 1
    return y
def sweep_noise(d, f0, f1, q=1.2, steps=48):
    """Ruido filtrado con banda que se desplaza de f0 a f1 (solapado con ventanas Hann)."""
    n = int(d * SR); out = np.zeros(n)
    hop = max(1, n // steps); win = 2 * hop
    src = rng.standard_normal(n + win + 4096)
    w = np.hanning(win)
    for k in range(0, n, hop):
        p = k / max(1, n - 1)
        fc = f0 * (f1 / f0) ** p
        lo, hi = fc / (1 + 1 / q), min(fc * (1 + 1 / q), SR / 2 - 100)
        seg = sosfilt(butter(2, [max(lo, 20), hi], btype='band', fs=SR, output='sos'), src[k:k + win + 2048])[2048:2048 + win]
        e = min(win, n - k)
        out[k:k + e] += seg[:e] * w[:e]
    return out / (np.max(np.abs(out)) + 1e-9)

# ───────────────────────── instrumentos ─────────────────────────
def kick(big=False):
    t = T(0.6 if big else 0.42)
    f = 52 + (140 if big else 120) * np.exp(-t / 0.028)
    s = np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t / (0.3 if big else 0.17))
    click = filt(noise(0.008), 'highpass', 2500) * np.exp(-T(0.008) / 0.002) * 0.9
    s[:len(click)] += click
    return np.tanh(1.6 * s) / np.tanh(1.6)

def clap():
    d = 0.32; n = int(d * SR); s = np.zeros(n)
    src = filt(noise(d), 'band', [900, 3800])
    t = T(d)
    for off in (0.0, 0.011, 0.022):
        e = np.where(t >= off, np.exp(-(t - off) / 0.007), 0)
        s += src * e
    s += src * np.exp(-t / 0.11) * 0.55
    return s / np.max(np.abs(s))

def snare(vel=1.0):
    t = T(0.22)
    body = np.sin(2 * np.pi * (190 + 60 * np.exp(-t / 0.01)) * t) * np.exp(-t / 0.05)
    sn = filt(noise(0.22), 'highpass', 1800) * np.exp(-t / 0.07)
    s = 0.5 * body + 0.8 * sn
    return s / np.max(np.abs(s)) * vel

def hat(open_=False):
    d = 0.3 if open_ else 0.06
    t = T(d)
    s = filt(noise(d), 'highpass', 7500) * np.exp(-t / (0.12 if open_ else 0.018))
    return s / (np.max(np.abs(s)) + 1e-9)

def crash(d=1.8):
    t = T(d)
    s = filt(noise(d), 'highpass', 4200) * np.exp(-t / 0.65)
    s += filt(noise(d), 'band', [3000, 6000]) * np.exp(-t / 0.25) * 0.5
    return s / np.max(np.abs(s))

def bass_note(m, d, cutoff=700, accent=1.0):
    f = hz(m)
    s = 0.8 * saw(f, d, 0.0) + 0.3 * np.sin(2 * np.pi * f * T(d))  # sierra + algo de sub
    s = filt(s, 'lowpass', cutoff * accent, order=2)
    s = np.tanh(1.8 * s)
    return s * adsr(len(s), 0.003, 0.09, 0.55, 0.02)

def pad_chord(notes, d, cutoff=1600):
    L = np.zeros(int(d * SR)); R = np.zeros(int(d * SR))
    for m in notes:
        for det, side in ((-0.09, 'L'), (0.0, 'C'), (0.08, 'R')):
            v = saw(hz(m + det), d) * 0.33
            if side == 'L': L += v
            elif side == 'R': R += v
            else: L += v * 0.7; R += v * 0.7
    env = adsr(len(L), 0.18, 0.6, 0.75, 0.25)
    L = filt(L, 'lowpass', cutoff) * env; R = filt(R, 'lowpass', cutoff) * env
    k = max(np.max(np.abs(L)), np.max(np.abs(R))) + 1e-9
    return L / k, R / k

def pluck(m, d=0.32, bright=3600):
    f = hz(m); t = T(d)
    s = 0.6 * saw(f, d, 0.0) + 0.4 * np.sign(np.sin(2 * np.pi * f * t)) * 0.6 + 0.5 * np.sin(2 * np.pi * f * t)
    hi = filt(s, 'lowpass', bright); lo = filt(s, 'lowpass', 900)
    mix = np.exp(-t / 0.05)
    s = hi * mix + lo * (1 - mix)
    return s * adsr(len(s), 0.002, 0.12, 0.0, 0.03)

def stab(notes, d=0.45):
    s = sum(pluck(m, d, 5000) for m in notes)
    return s / (np.max(np.abs(s)) + 1e-9)

def riser(d):
    t = T(d); p = t / d
    nz = sweep_noise(d, 400, 9000, q=1.5)
    f = 180 * (2 ** (2.6 * p))
    tone = np.sin(2 * np.pi * np.cumsum(f) / SR) * 0.35 + np.sin(2 * np.pi * np.cumsum(f * 1.5) / SR) * 0.2
    s = (nz * 0.8 + tone) * (p ** 2.2)
    return s / np.max(np.abs(s))

def impact():
    d = 2.2; t = T(d)
    sub = np.sin(2 * np.pi * np.cumsum(32 + 60 * np.exp(-t / 0.08)) / SR) * np.exp(-t / 0.7)
    body = filt(noise(d), 'lowpass', 900) * np.exp(-t / 0.18)
    s = np.tanh(1.4 * (sub + 0.5 * body))
    return s / np.max(np.abs(s))

def bell(m, d=2.2):
    t = T(d); f = hz(m)
    s = sum(a * np.sin(2 * np.pi * f * r * t) * np.exp(-t / dec) for r, a, dec in
            [(1, 0.6, 1.4), (2.0, 0.22, 0.8), (3.01, 0.12, 0.5), (5.4, 0.05, 0.25)])
    return s * np.clip(t / 0.003, 0, 1)

# ───────────────────────── armonía ─────────────────────────
# Un acorde por compás (13 compases = 26 s).
CH = {
    'Am': ([57, 60, 64, 67], 33), 'F': ([53, 57, 60, 64], 29), 'C': ([55, 60, 64, 71], 36),
    'G': ([55, 59, 62, 67], 31), 'Dm': ([50, 57, 60, 65], 38), 'E': ([52, 56, 59, 62], 28),
    'Am9': ([57, 60, 64, 71], 33),
}
PROG = ['Am', 'F', 'C', 'G', 'Am', 'F', 'C', 'G', 'Am', 'F', 'Dm', 'E', 'Am9']

kicks = []
def K(at, big=False, g=0.42):
    drums.place(kick(big), at, g); kicks.append(at)

# ───────────────────────── arreglo ─────────────────────────
for b, name in enumerate(PROG):
    t0 = b * BAR
    notes, root = CH[name]
    drop = b in (4, 5)          # 8–12 s · fondo oscuro, "Con carácter."
    read = b in (6, 7, 8, 9)    # 12–20 s · comparaciones (lectura)
    grid = b == 10              # 20–22 s · cuadrícula
    tension = b == 11           # 22–24 s · pregunta
    final = b == 12             # 24–26 s · cierre

    # Bombo
    if b <= 10:
        for k in range(4): K(t0 + k * BEAT, big=(k == 0 and b in (0, 4, 8, 10)))
    elif tension:
        K(t0); K(t0 + BEAT)
    elif final:
        kicks.append(t0)  # el impacto ya lleva su propio sub

    # Palmas / caja
    if 1 <= b <= 10:
        for k in (1, 3):
            drums.place(clap(), t0 + k * BEAT, 0.6 if drop else 0.5, pan=0.05)
            verb_send.place(clap(), t0 + k * BEAT, 0.18)
    if b == 3:  # redoble hacia la caída (8 s)
        for i in range(8):
            drums.place(snare(0.35 + 0.08 * i), t0 + 3 * BEAT + i * S16 / 2, 0.38, pan=0.1)
    if tension:  # redoble con crescendo y un hueco antes del cierre
        for i in range(14):
            at = t0 + 2 * BEAT + i * S16 / 1.75
            if at < t0 + BAR - S16: drums.place(snare(0.25 + 0.05 * i), at, 0.4, pan=-0.1)

    # Charles
    if b <= 1:
        for k in range(4): drums.place(hat(), t0 + k * BEAT + BEAT / 2, 0.24, pan=0.3)
    elif b <= 10:
        for i in range(16):
            acc = 1.0 if i % 4 == 2 else (0.55 if i % 2 else 0.35)
            drums.place(hat(), t0 + i * S16, 0.22 * acc * (1.15 if drop or grid else 1), pan=0.3 if i % 2 else 0.18)
        if drop or grid or b in (2, 3):
            for k in range(4): drums.place(hat(True), t0 + k * BEAT + BEAT / 2, 0.13, pan=-0.25)

    # Bajo
    if b <= 3 or read:
        cut = 520 if b <= 1 else (760 if not read else 680)
        for k in range(4):
            bass.place(bass_note(root + 12, BEAT / 2 * 0.9, cut), t0 + k * BEAT + BEAT / 2, 0.55)
        if b in (2, 3, 8, 9):  # notas de paso
            bass.place(bass_note(root + 12, S16 * 0.9, cut), t0 + 3 * BEAT + 3 * S16, 0.4)
    elif drop or grid:
        for i in range(16):
            if i % 4 == 0: continue  # deja sitio al bombo
            acc = 1.25 if i % 4 == 2 else 1.0
            bass.place(bass_note(root + 12 + (12 if i in (7, 15) and drop else 0), S16 * 0.85, 1150, acc), t0 + i * S16, 0.5)
    elif tension:
        bass.place(bass_note(root + 12, BEAT * 0.9, 700), t0 + BEAT / 2, 0.5)
        n = bass_note(root + 12, BAR - BEAT - S16, 900)
        bass.place(n * np.linspace(1, 0.4, len(n)), t0 + BEAT, 0.45)
    elif final:
        bass.place(bass_note(root + 12, 1.9, 400) * np.linspace(1, 0, int(1.9 * SR)), t0, 0.5)

    # Pad (acordes)
    if b >= 2:
        L, R = pad_chord(notes, BAR + (0.3 if not final else 0), 1300 if read else (1900 if drop else 1600))
        g = 0.13 if read else 0.1
        if final: g = 0.16
        music.place((L, R), t0, g)
        verb_send.place((L, R), t0, 0.05)

    # Pluck / gancho
    hook_pos = [0, 3, 6, 10, 12, 14]
    hook_idx = [3, 2, 0, 1, 2, 3]
    if b <= 1 or drop:
        for p, ix in zip(hook_pos, hook_idx):
            m = notes[ix] + 12
            sig = pluck(m)
            music.place(sig, t0 + p * S16, 0.2 if drop else 0.17, pan=-0.2)
            music.place(sig, t0 + p * S16 + 0.375, 0.07, pan=0.6)   # eco de corchea con puntillo
            music.place(sig, t0 + p * S16 + 0.75, 0.03, pan=-0.6)
            if drop: music.place(pluck(m + 12, 0.2), t0 + p * S16, 0.06, pan=0.3)
    if read and b in (8, 9):
        for i in range(0, 16, 2):
            m = notes[(i // 2) % 4] + 12
            music.place(pluck(m, 0.25, 2400), t0 + i * S16, 0.07, pan=0.4 if i % 4 else -0.4)
    if grid or tension:
        seq = [0, 1, 2, 3, 2, 1, 2, 3] * 2
        for i in range(16):
            m = notes[seq[i]] + 12 + (12 if i % 8 == 7 else 0)
            br = 2600 + (i / 16) * 3000 if grid else 2000 + (i / 16) * 5000
            music.place(pluck(m, 0.2, br), t0 + i * S16, 0.11 if grid else 0.1, pan=0.35 if i % 2 else -0.35)

    # Golpes de acorde en los cambios grandes
    if b in (4, 6, 8, 10):
        music.place(stab([n + 12 for n in notes]), t0, 0.16)
        verb_send.place(stab([n + 12 for n in notes]), t0, 0.12)

# Platos e impactos
for at, g in ((0.0, 0.12), (8.0, 0.28), (12.0, 0.14), (16.0, 0.18), (20.0, 0.16)):
    drums.place(crash(), at, g, pan=0.2)
music.place(impact(), 8.0, 0.35)
music.place(impact(), 24.0, 0.6)
verb_send.place(impact(), 24.0, 0.25)
drums.place(crash(2.0), 24.0, 0.32)
# Subidas hacia la caída (8 s) y hacia el cierre (24 s)
music.place(riser(1.9), 8.0 - 1.9, 0.26)
music.place(riser(1.95), 24.0 - 2.0, 0.32)

# ───────────────────────── efectos sincronizados ─────────────────────────
def whoosh(d, rising=True, size=1.0):
    d = max(0.22, d + 0.12)
    nz = sweep_noise(d, 350, 5200, q=1.1) if rising else sweep_noise(d, 4200, 300, q=1.1)
    t = T(d); p = t / d
    env = np.sin(np.pi * np.clip(p ** 0.75, 0, 1)) ** 1.6
    body = filt(noise(d), 'lowpass', 260) * env * 0.4 * size
    return (nz * env + body)

def tock(f=300, d=0.07):
    t = T(d)
    s = np.sin(2 * np.pi * f * t) * np.exp(-t / 0.018)
    c = filt(noise(0.012), 'band', [2000, 5500]) * np.exp(-T(0.012) / 0.003)
    s[:len(c)] += c * 0.6
    return s

def blip(f=2400, d=0.06):
    t = T(d); return np.sin(2 * np.pi * f * t) * np.exp(-t / 0.012)

def pop():
    t = T(0.18)
    s = np.sin(2 * np.pi * np.cumsum(900 * np.exp(-t / 0.03) + 180) / SR) * np.exp(-t / 0.06)
    return s + 0.6 * np.sin(2 * np.pi * 70 * t) * np.exp(-t / 0.05)

def zip_(d=0.45):
    t = T(d); p = t / d
    s = sweep_noise(d, 2500, 9000, q=2.5) * (p ** 1.5) * np.exp(-np.clip(p - 0.85, 0, 1) * 30)
    return s

def sweep_low(d=0.7):
    t = T(d); p = t / d
    nz = sweep_noise(d, 180, 2800, q=0.9) * np.sin(np.pi * np.clip(p, 0, 1)) ** 1.2
    sub = np.sin(2 * np.pi * np.cumsum(90 * np.exp(-t / 0.25) + 38) / SR) * np.exp(-t / 0.3)
    return nz * 0.8 + sub * 0.6

def hit():
    t = T(0.9)
    s = np.sin(2 * np.pi * np.cumsum(140 * np.exp(-t / 0.04) + 45) / SR) * np.exp(-t / 0.25)
    s += filt(noise(0.9), 'band', [500, 3000]) * np.exp(-t / 0.05) * 0.5
    return np.tanh(1.5 * s)

with open(EVENTS) as fh:
    events = json.load(fh)['events']

# Agrupa eventos simultáneos del mismo tipo (mismo fotograma): uno solo, más grande.
groups = {}
for e in events:
    key = (e['type'], round(e['t'] * 25))
    groups.setdefault(key, []).append(e)

for (typ, _), es in sorted(groups.items(), key=lambda kv: kv[0][1]):
    e = max(es, key=lambda x: x['size'])
    n = len(es); t = e['t']; size = e['size']; pan = e['pan']
    boost = 1 + 0.25 * (n - 1)
    if typ in ('enter', 'exit', 'move'):
        d = e.get('dur', 0.4)
        w = whoosh(d, rising=(typ != 'exit'), size=size)
        # Panorama en movimiento: de la posición inicial al centro (entrada) o al revés (salida).
        p = np.linspace(pan, pan * 0.15, len(w)) if typ == 'enter' else np.linspace(pan * 0.15, pan, len(w)) if typ == 'exit' else np.full(len(w), pan * 0.4)
        th = (np.clip(p, -1, 1) + 1) * np.pi / 4
        g = 0.2 * (0.55 + 0.45 * size) * boost
        sfx.place((w * np.cos(th) * 1.414, w * np.sin(th) * 1.414), t - 0.03, g)
    elif typ == 'type':
        sfx.place(tock(260 + 40 * (len(es) > 1)), t + 0.02, 0.16, pan)
    elif typ == 'tick':
        sfx.place(blip(3200, 0.04), t, 0.05, pan)
    elif typ == 'blip':
        sfx.place(blip(2600), t, 0.05, pan); sfx.place(blip(3900), t + S16 / 2, 0.035, -pan)
    elif typ == 'cut':
        sfx.place(tock(520, 0.04), t, 0.07 * min(1.6, boost))
    elif typ == 'pop':
        sfx.place(pop(), t, 0.3, pan); verb_send.place(pop(), t, 0.1)
    elif typ == 'line':
        sfx.place(zip_(e.get('dur', 0.45)), t, 0.14, 0.2)
    elif typ == 'sweep':
        sfx.place(sweep_low(), t - 0.08, 0.4 * size)
    elif typ == 'hit':
        w = whoosh(0.45, True, 1.0)
        sfx.place(w, t - 0.42, 0.22); sfx.place(hit(), t, 0.45); verb_send.place(hit(), t, 0.15)
    elif typ == 'logo':
        for m, a, off in ((81, 0.5, 0.0), (76, 0.35, 0.0), (83, 0.25, 0.06), (88, 0.15, 0.12)):
            sfx.place(bell(m), t + off, 0.18 * a / 0.5, pan=(m - 82) / 12)
            verb_send.place(bell(m), t + off, 0.1)

# ───────────────────────── mezcla ─────────────────────────
# Sidechain: el bajo y el pad "respiran" con el bombo.
duck = np.ones(N)
tt = np.arange(N) / SR
last = np.full(N, -10.0)
for k in sorted(kicks):
    i = int(k * SR); last[i:] = k
since = tt - last
duck = 1 - 0.7 * np.exp(-since / 0.11) * (since >= 0)
duck_soft = 1 - 0.45 * np.exp(-since / 0.14) * (since >= 0)

def ir(d=1.8, seed=0):
    r = np.random.default_rng(seed)
    t = T(d); x = r.standard_normal(len(t)) * np.exp(-6.9 * t / d)
    x = filt(x, 'lowpass', 6000); x[:int(0.012 * SR)] = 0
    return x / np.sqrt(np.sum(x ** 2))

revL = fftconvolve(verb_send.L, ir(1.8, 1))[:N]
revR = fftconvolve(verb_send.R, ir(1.8, 2))[:N]

# Dinámica por secciones: la intro contenida, la caída (8 s) y la cuadrícula (20 s) al máximo.
SECTION_GAIN = [0.66, 0.72, 0.8, 0.86, 1.0, 1.0, 0.82, 0.82, 0.86, 0.88, 1.0, 0.92, 1.0]
sec_env = np.repeat(np.array(SECTION_GAIN), int(BAR * SR))[:N]
sec_env = np.convolve(sec_env, np.ones(960) / 960, mode='same')  # transiciones de 20 ms
sec_env[:480] = SECTION_GAIN[0]

def hp(x, f=35): return filt(x, 'highpass', f, order=4)
mix_drums_L = hp(drums.L); mix_drums_R = hp(drums.R)
mid_L = filt(music.L, 'highpass', 150); mid_R = filt(music.R, 'highpass', 150)

L = (mix_drums_L + hp(bass.L) * duck * 0.75 + mid_L * duck_soft * 2.6) * sec_env + sfx.L * 1.9 + revL * 0.6
R = (mix_drums_R + hp(bass.R) * duck * 0.75 + mid_R * duck_soft * 2.6) * sec_env + sfx.R * 1.9 + revR * 0.6

# Presencia para altavoces de móvil (realce suave 2–6 kHz) y final exacto en 26 s.
pres_L = filt(L, 'band', [2000, 6000]); pres_R = filt(R, 'band', [2000, 6000])
L = L + 0.6 * pres_L; R = R + 0.6 * pres_R
fade = np.ones(N); fl = int(0.5 * SR); fade[-fl:] = np.linspace(1, 0, fl) ** 2
L *= fade; R *= fade
k = max(np.max(np.abs(L)), np.max(np.abs(R)))
L, R = L / k * 0.7, R / k * 0.7

raw = os.path.join(HERE, 'soundtrack_raw.wav')
def write_wav(path, L, R):
    data = (np.stack([L, R], 1) * 32767).astype('<i2')
    import wave
    with wave.open(path, 'wb') as w:
        w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR); w.writeframes(data.tobytes())
write_wav(raw, L, R)

# Máster: compresión suave + normalización EBU R128 a −14 LUFS (dos pasadas) + limitador.
chain = 'acompressor=threshold=-20dB:ratio=2.5:attack=8:release=120:makeup=2'
m = subprocess.run(['ffmpeg', '-hide_banner', '-i', raw, '-af', chain + ',loudnorm=I=-14:TP=-1.2:LRA=9:print_format=json', '-f', 'null', '-'],
                   capture_output=True, text=True).stderr
js = json.loads(m[m.rindex('{'):m.rindex('}') + 1])
ln = (f"loudnorm=I=-14:TP=-1.2:LRA=9:measured_I={js['input_i']}:measured_TP={js['input_tp']}:"
      f"measured_LRA={js['input_lra']}:measured_thresh={js['input_thresh']}:offset={js['target_offset']}:linear=true")
os.makedirs(os.path.dirname(OUT), exist_ok=True)
subprocess.run(['ffmpeg', '-v', 'error', '-y', '-i', raw, '-af', f'{chain},{ln},alimiter=limit=0.87:level=false,aresample=48000',
                '-t', str(DUR), '-c:a', 'pcm_s16le', OUT], check=True)
os.remove(raw)
print('OK', OUT)
if '--report' in sys.argv:
    import wave
    w = wave.open(OUT); x = np.frombuffer(w.readframes(w.getnframes()), '<i2').reshape(-1, 2).mean(1) / 32768
    for lo, hi in ((None, 60), (60, 150), (150, 500), (500, 2000), (2000, 6000), (6000, None)):
        y = filt(x, 'lowpass' if lo is None else 'highpass' if hi is None else 'band', hi if lo is None else lo if hi is None else [lo, hi], 4)
        print(f'  banda {lo}-{hi} Hz: {20 * np.log10(np.sqrt(np.mean(y ** 2)) + 1e-12):6.1f} dB')
    print('  por compás:', ' '.join(f'{20 * np.log10(np.sqrt(np.mean(x[i * 96000:(i + 1) * 96000] ** 2))):.1f}' for i in range(13)))
