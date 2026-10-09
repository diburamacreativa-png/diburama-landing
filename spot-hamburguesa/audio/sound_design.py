"""DIBURAMA spot — sound design, music and mix (48 kHz stereo).

IMPORTANT — PROVISIONAL FOLEY. This environment had no access to recorded foley or
licensed sound libraries. Every food / ASMR sound here (sizzle, impact, steam, crunch,
crumbs...) is SYNTHESISED procedurally (stochastic micro-impulse models, resonant
filters, modal synthesis). They are placeholders built to the exact timing and
dynamics of the cut; each one is listed in audio/CUE_SHEET.md with its time code to be
replaced by close-miked recorded foley. The music is original and generated here.

Concept: the burger writes its own score. The sizzle becomes the hi-hats (the very
same signal, gated to the 16th grid), utensil hits become the backbeat, drops become
low hits, steam becomes the risers. Back at the real burger, the music withdraws and
the physical sounds return.

usage: python3 audio/sound_design.py      → audio/stems/*.wav, audio/DIBURAMA_HAMBURGUESA_MIX_48k.wav
"""
import os, json, math, numpy as np, soundfile as sf
from scipy import signal
import pyloudnorm as pyln

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
EDL = json.load(open(os.path.join(ROOT, "project", "edit_decisions.json")))
SR = 48000
DUR = EDL["format"]["duration"]
N = int(round(DUR * SR))
BPM = 120.0; BEAT = 60 / BPM; S16 = BEAT / 4
GB = EDL["graphics"]["beats"]
CUES = []   # (time, stem, name, provisional?)

def S(t): return int(round(t * SR))
def db(x): return 10 ** (x / 20)
def rng(seed): return np.random.default_rng(seed)

# ------------------------------------------------------------------ dsp helpers
def sos(kind, f, order=2):
    return signal.butter(order, f, btype=kind, fs=SR, output="sos")
def hp(x, f, o=2): return signal.sosfilt(sos("highpass", f, o), x, axis=-1)
def lp(x, f, o=2): return signal.sosfilt(sos("lowpass", f, o), x, axis=-1)
def bp(x, lo, hi, o=2): return signal.sosfilt(sos("bandpass", [lo, hi], o), x, axis=-1)

def reso(x, f, q):
    """RBJ constant-peak band-pass resonator"""
    w = 2 * math.pi * f / SR; al = math.sin(w) / (2 * q)
    b = [al, 0, -al]; a = [1 + al, -2 * math.cos(w), 1 - al]
    return signal.lfilter(b, a, x)

def sweep_bp(x, f0, f1, q, curve=1.0, block=256):
    """band-pass with a time-varying centre frequency (exponential sweep)"""
    y = np.zeros_like(x); zi = np.zeros(2); n = len(x)
    for i in range(0, n, block):
        u = (i / max(1, n - 1)) ** curve
        f = f0 * (f1 / f0) ** u
        w = 2 * math.pi * min(f, SR * 0.45) / SR; al = math.sin(w) / (2 * q)
        b = np.array([al, 0, -al]) / (1 + al); a = np.array([1, -2 * math.cos(w) / (1 + al), (1 - al) / (1 + al)])
        y[i:i + block], zi = signal.lfilter(b, a, x[i:i + block], zi=zi)
    return y

def smooth_noise(n, rate_hz, seed):
    r = rng(seed); k = max(2, int(n * rate_hz / SR) + 2)
    pts = r.standard_normal(k)
    return np.interp(np.linspace(0, k - 1, n), np.arange(k), pts)

def expenv(n, tau, attack=0.0):
    t = np.arange(n) / SR
    e = np.exp(-t / tau)
    if attack > 0: e *= 1 - np.exp(-t / attack)
    return e

def pan2(x, pan):
    """equal-power pan, pan in [-1, 1]; accepts mono or (2, n)"""
    if x.ndim == 2: return x
    a = (pan + 1) * math.pi / 4
    return np.vstack([x * math.cos(a), x * math.sin(a)])

def norm(x):
    m = np.abs(x).max(); return x / m if m > 0 else x

class Bus:
    def __init__(self, name): self.name = name; self.x = np.zeros((2, N))
    def add(self, sig, t, gain_db=0.0, pan=0.0, cue=None, prov=False):
        s = pan2(np.asarray(sig, dtype=np.float64), pan) * db(gain_db)
        i = S(t)
        if i < 0: s = s[:, -i:]; i = 0
        j = min(N, i + s.shape[1])
        if j > i: self.x[:, i:j] += s[:, : j - i]
        if cue: CUES.append((t, self.name, cue, prov))

def reverb_ir(rt60, length, seed, bright=6000, pre=0.012):
    n = S(length); r = rng(seed); t = np.arange(n) / SR
    ir = np.zeros((2, n + S(pre)))
    for c in range(2):
        nz = r.standard_normal(n) * np.exp(-6.9 * t / rt60)
        dark = lp(nz, 1800) * np.clip(t / (rt60 * 0.4), 0, 1)
        ir[c, S(pre):] = lp(nz, bright) * (1 - np.clip(t / (rt60 * 0.6), 0, 1)) + dark
    return ir / np.sqrt((ir ** 2).sum(axis=1, keepdims=True))

def convolve(x, ir, wet):
    y = np.vstack([signal.fftconvolve(x[c], ir[c])[:N] for c in range(2)])
    return x * (1 - wet * 0.3) + y * wet

def env_follow(x, att, rel):
    """peak envelope (mono) with attack/release in seconds"""
    a = np.abs(x).max(axis=0) if x.ndim == 2 else np.abs(x)
    a = signal.decimate(a, 16, ftype="fir", zero_phase=True) if len(a) > 64 else a
    ga, gr = math.exp(-1 / (att * SR / 16)), math.exp(-1 / (rel * SR / 16))
    e = np.zeros_like(a); v = 0.0
    for i, s in enumerate(a):
        v = ga * v + (1 - ga) * s if s > v else gr * v + (1 - gr) * s
        e[i] = v
    return np.interp(np.arange(N), np.arange(len(e)) * 16, e)

# ------------------------------------------------------------------ provisional foley models
def sizzle(dur, rate_fn, seed, level_fn=None, fat=1.0):
    """Stochastic sizzle: dense micro-bubble bursts in several resonant bands, sparse fat
    pops, grease spits and a modulated hiss. rate_fn(t) → events/s; level_fn(t) → gain."""
    n = S(dur); t = np.arange(n) / SR
    rate = rate_fn(t); lvl = level_fn(t) if level_fn else np.ones(n)
    out = np.zeros((2, n))
    for c in range(2):
        r = rng(seed * 10 + c)
        pops = np.zeros(n)
        for k, (fc, q, share) in enumerate([(2600, 2.2, .25), (4700, 2.6, .35), (7600, 2.4, .28), (11000, 1.8, .12)]):
            ev = r.random(n) < rate * share / SR
            amp = np.minimum(r.pareto(2.4, n) + 0.25, 7) * r.choice([-1.0, 1.0], n) * ev
            pops += reso(amp, fc * (1 + 0.08 * r.standard_normal()), q)
        # fat pops (larger bubbles bursting) — individually shaped
        fatn = int(dur * 9 * fat)
        for _ in range(fatn):
            i = r.integers(0, n - 2000); f = r.uniform(900, 2600); L = r.integers(150, 700)
            b = r.standard_normal(L) * expenv(L, r.uniform(0.001, 0.004))
            pops[i:i + L] += reso(b, f, r.uniform(4, 9)) * r.uniform(1.5, 4.5) * np.interp(t[i], t, rate) / 2500
        # grease spits: short dense clusters
        for _ in range(int(dur * 1.6)):
            i = r.integers(0, n - S(0.12)); L = S(r.uniform(0.03, 0.09))
            cl = (r.random(L) < 9000 / SR) * r.standard_normal(L) * np.hanning(L)
            pops[i:i + L] += hp(cl, 2500) * r.uniform(1, 2.2)
        hiss = lp(hp(r.standard_normal(n), 2800, 2), 13000, 2)
        am = 1 + 0.3 * smooth_noise(n, 9, seed * 7 + c) + 0.15 * smooth_noise(n, 31, seed * 9 + c)
        out[c] = (pops * 0.06 + hiss * 0.055 * am * np.sqrt(rate / 2500)) * lvl
    mid = out.mean(axis=0)
    return 0.72 * out + 0.28 * mid  # keep it wide but with a solid centre (close mic)

def impact_meat():
    """patty slapping onto hot grates: low body + wet slap + grate ring"""
    n = S(0.7); t = np.arange(n) / SR; r = rng(11)
    f = 52 + 70 * np.exp(-t / 0.035)
    body = np.sin(2 * np.pi * np.cumsum(f) / SR) * expenv(n, 0.16, 0.0015)
    slap = lp(r.standard_normal(n), 2400, 2) * expenv(n, 0.035, 0.0008)
    slap = slap + 0.6 * reso(r.standard_normal(n) * expenv(n, 0.02), 330, 3)
    grate = sum(reso(r.standard_normal(n) * expenv(n, 0.004), fr, 40) * a for fr, a in [(1830, .5), (2710, .35), (4120, .2)])
    x = 0.9 * np.tanh(1.6 * body) + 0.55 * norm(slap) + 0.25 * norm(grate)
    return norm(x)

def fire_bed(dur, seed):
    n = S(dur); r = rng(seed)
    roar = lp(np.cumsum(r.standard_normal((2, n)), axis=1) * 0.02, 380, 2)
    roar = hp(roar, 40) * (1 + 0.35 * smooth_noise(n, 3, seed))
    lick = bp(r.standard_normal((2, n)), 350, 1400) * (0.5 + 0.5 * np.abs(smooth_noise(n, 2.2, seed + 3)))
    cr = (r.random((2, n)) < 25 / SR) * r.standard_normal((2, n))
    cr = bp(cr, 900, 4200) * 4
    return norm(roar) * 0.6 + norm(lick) * 0.18 + cr * 0.2

def flame_whoosh(dur, seed):
    n = S(dur); r = rng(seed); t = np.arange(n) / SR
    x = np.vstack([sweep_bp(r.standard_normal(n), 260, 900, 0.9, 0.7) for _ in range(2)])
    e = np.clip(t / 0.06, 0, 1) * np.exp(-np.maximum(t - 0.06, 0) / (dur * 0.35))
    return norm(x * e)

def steam(dur, seed, f0=1500, f1=3800):
    n = S(dur); r = rng(seed); t = np.arange(n) / SR
    x = np.vstack([sweep_bp(r.standard_normal(n), f0, f1, 0.7, 1.0) for _ in range(2)])
    x += 0.4 * hp(r.standard_normal((2, n)), 5000)
    e = np.sin(np.pi * np.clip(t / dur, 0, 1)) ** 1.5 * (1 + 0.25 * smooth_noise(n, 5, seed))
    return norm(x * e)

def suction(dur, seed):
    """entering the bread: air pulled in, resonant sweep down, soft 'thoomp' at the end"""
    n = S(dur); r = rng(seed); t = np.arange(n) / SR
    air = np.vstack([sweep_bp(r.standard_normal(n), 5200, 240, 1.6, 0.6) for _ in range(2)])
    e = (t / dur) ** 2.2 * np.exp(-np.maximum(t - dur * 0.85, 0) / 0.05)
    th_n = S(0.5); tt = np.arange(th_n) / SR
    th = np.sin(2 * np.pi * np.cumsum(45 + 60 * np.exp(-tt / 0.05)) / SR) * expenv(th_n, 0.18, 0.004)
    x = norm(air * e) * 0.8
    i = S(dur * 0.86); x[:, i:i + th_n] += th[: n - i] * 0.7
    return x

def crunch(seed=21):
    """THE BITE: crust fracture (clustered micro-cracks), airy crumble, soft body, crumb tail.
    No chewing."""
    n = S(0.9); r = rng(seed); x = np.zeros(n)
    # clustered fracture times: accelerating burst then sparse
    times = np.sort(np.concatenate([r.gamma(1.8, 0.022, 120), 0.02 + r.gamma(2.5, 0.035, 60), 0.12 + r.exponential(0.07, 25)]))
    for k, tc in enumerate(times):
        i = S(tc)
        if i >= n - 600: continue
        big = r.random() < 0.18
        f = r.uniform(700, 1700) if big else r.uniform(1500, 7500)
        L = r.integers(120, 700 if big else 380)
        imp = r.standard_normal(L) * expenv(L, r.uniform(0.0006, 0.003 if big else 0.0018))
        g = (r.uniform(1.5, 3.2) if big else r.uniform(0.4, 1.4)) * math.exp(-tc / 0.24)
        x[i:i + L] += reso(imp, f, r.uniform(2, 6)) * g
    air = hp(r.standard_normal(n), 2200) * expenv(n, 0.11, 0.002)
    air *= (r.random(n) < 0.12) * 2 + 0.25  # grainy texture
    body = lp(r.standard_normal(n), 380, 2) * expenv(n, 0.06, 0.004)
    tail = np.zeros(n)
    for _ in range(26):
        tc = 0.12 + r.exponential(0.16)
        i = S(tc)
        if i >= n - 300: continue
        L = r.integers(80, 260); imp = r.standard_normal(L) * expenv(L, 0.0009)
        tail[i:i + L] += reso(imp, r.uniform(2500, 8000), 3) * 0.5 * math.exp(-tc / 0.3)
    m = norm(x) * 1.0 + norm(air) * 0.32 + norm(body) * 0.45 + norm(tail) * 0.28
    m = m + 0.35 * reso(m, 3600, 0.8)          # close-mic presence
    m = np.tanh(2.6 * norm(m)) / np.tanh(2.6)  # density: parallel-style saturation
    st = np.vstack([m + 0.08 * norm(tail), m + 0.08 * norm(np.roll(tail, 37))])
    return norm(st)

def ceramic_tick(seed, f0=2300, g=1.0):
    n = S(0.35); r = rng(seed); x = np.zeros(n)
    for ratio, tau, a in [(1, .09, 1), (1.78, .06, .6), (2.86, .045, .45), (4.2, .03, .3)]:
        x += a * np.sin(2 * np.pi * f0 * ratio * np.arange(n) / SR + r.uniform(0, 6)) * expenv(n, tau, 0.0002)
    x += hp(r.standard_normal(n), 4000) * expenv(n, 0.002) * 0.5
    return norm(x) * g

def slate_clap(seed=5):
    n = S(0.3); r = rng(seed); x = np.zeros(n)
    for off, g in [(0.0, 0.6), (0.006, 1.0)]:
        i = S(off); L = n - i
        b = r.standard_normal(L) * expenv(L, 0.012, 0.0003)
        x[i:] += g * (reso(b, 1150, 6) + 0.7 * reso(b, 2350, 5) + 0.4 * bp(b, 900, 5000))
    return norm(x)

def pencil(dur, seed):
    n = S(dur); r = rng(seed); t = np.arange(n) / SR
    x = bp(r.standard_normal(n), 1800, 7000)
    jitter = np.clip(1 + 0.9 * smooth_noise(n, 90, seed), 0, None)
    e = np.sin(np.pi * np.clip(t / dur, 0, 1)) ** 0.7
    return norm(x * jitter * e)

def leaves(dur, seed):
    n = S(dur); r = rng(seed); t = np.arange(n) / SR
    ev = (r.random(n) < 700 / SR) * r.standard_normal(n)
    x = bp(ev, 1200, 6500) + 0.3 * bp(r.standard_normal(n), 2000, 9000) * 0.05
    return norm(x * np.sin(np.pi * np.clip(t / dur, 0, 1)))

def whoosh(dur, seed, f0=400, f1=4000, q=0.8):
    n = S(dur); r = rng(seed); t = np.arange(n) / SR
    x = np.vstack([sweep_bp(r.standard_normal(n), f0, f1, q, 1.0) for _ in range(2)])
    e = np.sin(np.pi * np.clip(t / dur, 0, 1)) ** 2
    return norm(x * e)

def reverse_swell(dur, seed, f=3000):
    n = S(dur); r = rng(seed)
    x = bp(r.standard_normal((2, n)), f * 0.4, min(f * 2.5, 20000)) * expenv(n, dur * 0.35)[None]
    ir = reverb_ir(1.2, 1.4, seed + 1)
    y = np.vstack([signal.fftconvolve(x[c], ir[c])[:n] for c in range(2)])
    return norm(y[:, ::-1])

# ------------------------------------------------------------------ instruments
def kick(g=1.0, tone=52):
    n = S(0.45); t = np.arange(n) / SR
    f = tone + 95 * np.exp(-t / 0.028)
    x = np.sin(2 * np.pi * np.cumsum(f) / SR) * expenv(n, 0.2, 0.0008)
    x += 0.25 * hp(rng(3).standard_normal(n), 3000) * expenv(n, 0.0025)
    return np.tanh(2.2 * x) / np.tanh(2.2) * g        # harmonics for phone speakers

def utensil_hit(seed=8, f0=640):
    """spatula on grill → backbeat"""
    n = S(0.5); r = rng(seed); t = np.arange(n) / SR; x = np.zeros(n)
    for ratio, tau, a in [(1, .14, 1), (2.32, .09, .7), (4.25, .05, .5), (6.63, .03, .35), (9.38, .02, .25)]:
        x += a * np.sin(2 * np.pi * f0 * ratio * t + r.uniform(0, 6)) * expenv(n, tau, 0.0003)
    snap = bp(r.standard_normal(n), 1300, 7000) * expenv(n, 0.045, 0.0005)
    body = lp(r.standard_normal(n), 900) * expenv(n, 0.03)
    return norm(0.45 * norm(x) + 0.9 * norm(snap) + 0.3 * norm(body))

def drop_low(f=95, seed=0):
    """a drop, pitched low: short up-glide 'bloop'"""
    n = S(0.35); t = np.arange(n) / SR
    fr = f * (1 + 0.9 * (1 - np.exp(-t / 0.03)))
    x = np.sin(2 * np.pi * np.cumsum(fr) / SR) * expenv(n, 0.09, 0.001)
    return np.tanh(1.5 * x)

def plip(f=1175, tau=0.12):
    n = S(0.4); t = np.arange(n) / SR
    fr = f * (0.75 + 0.5 * (1 - np.exp(-t / 0.012)))
    return np.sin(2 * np.pi * np.cumsum(fr) / SR) * expenv(n, tau, 0.0007)

def elastic(f, seed=0):
    """cheese pluck: rubbery pitch drop"""
    n = S(0.3); t = np.arange(n) / SR
    fr = f * (1 + 0.6 * np.exp(-t / 0.04))
    ph = 2 * np.pi * np.cumsum(fr) / SR
    x = (np.sin(ph) + 0.35 * np.sin(2 * ph) + 0.12 * np.sin(3 * ph)) * expenv(n, 0.09, 0.002)
    return lp(x, 2500)

def metal_tick(seed, f0=None):
    r = rng(seed); f0 = f0 or r.uniform(2400, 4200); n = S(0.12); t = np.arange(n) / SR
    x = sum(a * np.sin(2 * np.pi * f0 * k * t + r.uniform(0, 6)) * expenv(n, tau, 0.0002)
            for k, tau, a in [(1, .03, 1), (1.47, .02, .6), (2.09, .014, .4), (2.94, .009, .3)])
    return norm(x)

def saw(f, n, voices=3, det=0.006, seed=0, harmonics=24):
    t = np.arange(n) / SR; r = rng(seed); x = np.zeros(n)
    for v in range(voices):
        fv = f * (1 + det * (v - (voices - 1) / 2)); ph = r.uniform(0, 6)
        for k in range(1, harmonics + 1):
            if fv * k > 16000: break
            x += np.sin(2 * np.pi * fv * k * t + ph * k) / k
    return x / voices

def pad(freqs, dur, seed, att=0.8, rel=0.8, cutoff=(500, 2400)):
    n = S(dur); t = np.arange(n) / SR; out = np.zeros((2, n))
    for c in range(2):
        x = sum(saw(f, n, 3, 0.007 + 0.002 * c, seed + 13 * i + c, 14) for i, f in enumerate(freqs))
        x = sweep_lp(x, cutoff[0], cutoff[1])
        out[c] = x
    e = np.clip(t / att, 0, 1) ** 2 * np.clip((dur - t) / rel, 0, 1)
    return norm(out) * e

def sweep_lp(x, f0, f1, block=512):
    y = np.zeros_like(x); zi = None; n = len(x)
    for i in range(0, n, block):
        u = i / max(1, n - 1); f = f0 * (f1 / f0) ** u
        b, a = signal.butter(2, min(f, SR * 0.45), "low", fs=SR)
        if zi is None: zi = signal.lfilter_zi(b, a) * 0
        y[i:i + block], zi = signal.lfilter(b, a, x[i:i + block], zi=zi)
    return y

def bass(f, dur, g=1.0):
    n = S(dur); t = np.arange(n) / SR
    x = saw(f, n, 2, 0.003, 9, 10)
    env = np.exp(-t / 0.09)
    y = np.zeros(n); zi = None
    for i in range(0, n, 256):
        fc = 140 + 1300 * env[i]
        b, a = signal.butter(2, fc, "low", fs=SR)
        if zi is None: zi = np.zeros(2)
        y[i:i + 256], zi = signal.lfilter(b, a, x[i:i + 256], zi=zi)
    y += 0.6 * np.sin(2 * np.pi * f * t)
    e = np.clip(t / 0.004, 0, 1) * np.clip((dur - t) / 0.02, 0, 1)
    return np.tanh(1.8 * y * e) * g

def kalimba(f, seed=0):
    n = S(0.9); t = np.arange(n) / SR
    x = np.sin(2 * np.pi * f * t) * expenv(n, 0.35, 0.001) + 0.25 * np.sin(2 * np.pi * f * 5.4 * t) * expenv(n, 0.03)
    x += 0.15 * np.sin(2 * np.pi * f * 2 * t) * expenv(n, 0.12)
    return x


# ------------------------------------------------------------------ notes
NOTE = {n: 440 * 2 ** ((i - 57) / 12) for i, n in enumerate(
    [f"{p}{o}" for o in range(0, 8) for p in ["C", "C#", "D", "Eb", "E", "F", "F#", "G", "Ab", "A", "Bb", "B"]])}
def hz(*names): return [NOTE[n] for n in names]


def build():
    foley, sfx, music, sig = Bus("PROV_FOLEY_ASMR"), Bus("SFX_TRANSICIONES"), Bus("MUSICA"), Bus("FIRMA_SONORA")

    # ======== 0 – 3.5  GRILL ASMR (no music) ========================================
    # one continuous sizzle "voice" for the whole film; its level follows the story
    def siz_rate(t):
        r = 2200 + 5200 * np.exp(-np.maximum(t - 1.0, 0) / 0.5) * (t >= 1.0)
        return np.where(t < 1.0, 1600 + 400 * t, r)
    def siz_level(t):
        k = np.interp(t, [0, 0.95, 1.0, 1.6, 3.0, 3.5, 7.0, 7.5, 13.75, 15.75, 16.2, 17.0, 17.3, 18.3, 18.5, 24.1, 25.0],
                         [1.0, 1.1, 1.7, 1.5, 0.95, 0.42, 0.3, 0.42, 0.42, 0.22, 0.75, 0.55, 0.2, 0.12, 0.0, 0.0, 1.0])
        return k
    SIZ = sizzle(DUR, siz_rate, 101, siz_level)
    # sizzle stays diegetic until 7.0, then morphs into the hi-hat (gated, 16ths) until 15.75
    t = np.arange(N) / SR
    grid = (t / S16) % 1.0
    acc = np.array([1.0, 0.45, 0.7, 0.5])[((t / S16).astype(int)) % 4]
    gate = np.exp(-grid * S16 / np.where(((t / S16).astype(int) % 4) == 2, 0.055, 0.028)) * acc
    morph = np.clip((t - 7.0) / 0.8, 0, 1) * (1 - np.clip((t - 15.6) / 0.3, 0, 1))
    hat_hp = hp(SIZ, 4500, 2)
    SIZ_DIEG = SIZ * (1 - morph)
    SIZ_HAT = hat_hp * gate[None] * morph * 2.4
    foley.add(SIZ_DIEG, 0, -0.5, cue="Chisporroteo de parrilla (cama continua; vuelve en 15,75 s y en el loop final)", prov=True)
    music.add(SIZ_HAT, 0, -3, cue="Hi-hat construido con el MISMO chisporroteo (gate a semicorcheas)")

    foley.add(fire_bed(3.8, 202) * np.clip(1 - (np.arange(S(3.8)) / SR - 3.0) / 0.8, 0, 1)[None], 0, -17, cue="Fuego / llama (cama)", prov=True)
    foley.add(whoosh(0.55, 31, 300, 1400, 0.7), 0.45, -24, cue="Aire de la caída de la carne", prov=True)
    foley.add(impact_meat(), 1.0, -2.5, cue="IMPACTO carne contra parrilla", prov=True)
    foley.add(flame_whoosh(1.1, 41), 0.98, -12, cue="Llamarada tras el impacto", prov=True)
    music.add(kick(0.9, 40), 1.0, -12)  # sub weight under the impact, felt more than heard
    foley.add(steam(1.6, 51, 1300, 3600), 1.85, -15, pan=0.0, cue="Vapor (hamburguesa hero)", prov=True)
    foley.add(fire_bed(2.2, 203), 3.4, -26)
    # tension: low swell
    n = S(1.6); tt = np.arange(n) / SR
    music.add(np.sin(2 * np.pi * NOTE["D1"] * 2 * tt) * (tt / 1.6) ** 2 * 0.5, 1.9, -14)

    # ======== 3.5 – 6.0  INTO THE BREAD =============================================
    sfx.add(reverse_swell(0.5, 61, 2500), 3.0, -15, cue="Pre-succión (swell invertido)")
    sfx.add(suction(0.75, 62), 3.05, -6, cue="SUCCIÓN: entrada en el pan")
    music.add(drop_low(NOTE["D2"] * 1.0), 3.5, -6, cue="Primer elemento musical: gota grave")
    music.add(pad(hz("D2", "A2", "F3", "C4", "E4"), 2.7, 71, att=1.0, rel=0.4, cutoff=(350, 1800)), 3.5, -15, cue="Pad Dm9")
    for k, (tt_, nt) in enumerate([(4.0, "D5"), (4.25, "A4"), (4.5, "F4"), (5.0, "C5"), (5.25, "A4"), (5.5, "E4")]):
        music.add(plip(NOTE[nt], 0.1), tt_, -17, pan=[-0.4, 0.3, -0.1, 0.4, -0.3, 0.1][k])
    for tt_ in (4.5, 5.5):
        music.add(drop_low(NOTE["D2"]), tt_, -10)
    sfx.add(whoosh(0.9, 63, 2000, 500, 1.2) * 0.6, 4.0, -18, cue="Travelling por el túnel")

    # ======== 6.0 – 7.5  FILM WORLD (space opens) ====================================
    sfx.add(slate_clap(), 6.0, -9, pan=0.15, cue="Claqueta (entramos en el rodaje)")
    music.add(pad(hz("Bb1", "F2", "D3", "A3", "C4", "F4"), 1.8, 72, att=0.25, rel=0.4, cutoff=(700, 3000)), 5.95, -14, cue="Pad Bbmaj9 (apertura espacial)")
    music.add(kick(0.8), 6.0, -10); music.add(kick(0.7), 7.0, -12)
    for tt_ in (6.5, 7.25):
        music.add(drop_low(NOTE["F2"]), tt_, -13)
    sfx.add(steam(0.7, 81, 900, 5200), 6.95, -14, cue="Vapor → transición luminosa al queso")

    # ======== 7.5 – 10.75  MOTION (cheese → graphics) ================================
    bar = 2.0
    kick_pat = [0, 0.75, 1.0, 1.5]          # in beats inside a 2-beat half-bar
    for b0 in np.arange(7.5, 15.75, 1.0):
        sec_ = "C" if b0 < 10.75 else ("D" if b0 < 13.75 else "E")
        if sec_ == "E":
            pat = [0]
        elif sec_ == "D":
            pat = [0, 0.5, 1.0, 1.5]
        else:
            pat = [0, 0.75, 1.5]
        for p_ in pat:
            tt_ = b0 + p_ * BEAT
            if tt_ < 15.75: music.add(kick(0.95), tt_, -6.5)
        # backbeat: utensil hit
        if sec_ != "E":
            music.add(utensil_hit(int(b0 * 10)), b0 + BEAT, -11, pan=0.05)
    CUES.append((7.5, "MUSICA", "Groove: bombo + 'utensilio' (espátula sobre parrilla) como caja", False))
    # elastic cheese plucks (syncopated)
    el_notes = ["D3", "F3", "A3", "D3", "C4", "A3", "F3", "A3"]
    for k, tt_ in enumerate(np.arange(7.5 + S16 * 3, 10.75, S16 * 3)):
        music.add(elastic(NOTE[el_notes[k % 8]]), tt_, -16, pan=0.35 * math.sin(k))
    CUES.append((7.5, "MUSICA", "Plucks elásticos (queso estirándose)", False))
    # bass line
    bl = [("D2", 0, .5), ("D2", .75, .25), ("F2", 1.5, .4), ("D2", 2, .5), ("C2", 2.75, .25), ("A1", 3.5, .5)]
    for b0 in np.arange(7.5, 15.75, 2.0):
        for nt, o, d in bl:
            tt_ = b0 + o * BEAT * 2 / 2
            root = {"D2": "D2", "F2": "F2", "C2": "C2", "A1": "A1"}[nt]
            if b0 >= 13.75: root = {"D2": "F2", "F2": "A2", "C2": "C2", "A1": "C2"}[nt]
            if tt_ < 15.7: music.add(bass(NOTE[root], d * BEAT * 1.6), tt_, -9)
    sfx.add(steam(0.5, 91, 2500, 6000), 9.0, -18, cue="Vapor → cintas (motion)")
    sfx.add(whoosh(0.35, 92, 600, 5000, 1.0), 9.1, -15, pan=-0.3, cue="Swish cinta motion")
    for k, tt_ in enumerate([9.6, 9.95, 10.3]):
        sfx.add(elastic(NOTE["A3"] * (1 + 0.25 * k)) , tt_, -19, pan=0.4 - 0.4 * k)
    music.add(pad(hz("D2", "A2", "D3", "F3", "C4", "E4"), 3.3, 73, att=0.3, rel=0.3, cutoff=(500, 1500)), 7.5, -20)

    # ======== 10.75 – 13.75  3D TECHNICAL ============================================
    sfx.add(utensil_hit(77, 820) * 0.8 + 0, 10.75, -10, cue="Impacto metálico: aparece la maquinaria")
    sfx.add(reverse_swell(0.35, 101, 5000), 10.4, -18)
    for k, tt_ in enumerate(np.arange(10.75, 13.75, S16)):
        if k % 4 in (1, 3) or (k % 8 == 6):
            music.add(metal_tick(500 + k), tt_, -21 + (3 if k % 4 == 3 else 0), pan=0.5 if k % 2 else -0.5)
    CUES.append((10.75, "MUSICA", "Percusión metálica de precisión (semicorcheas)", False))
    for k in range(10):   # ratchet into the bearings cut
        sfx.add(metal_tick(900 + k, 5200), 11.95 + k * 0.03, -24 + k, pan=-0.2)
    sfx.add(utensil_hit(78, 560) * 0.7, 12.25, -14, cue="Engranaje → rodamientos")
    sfx.add(whoosh(0.6, 111, 800, 3000, 1.4), 11.7, -20)
    music.add(pad(hz("Bb1", "F2", "D3", "F3", "A3", "C4"), 3.0, 74, att=0.2, rel=0.3, cutoff=(600, 2600)), 10.75, -19)

    # ======== 13.75 – 15.75  ILLUSTRATION (organic) ==================================
    sfx.add(leaves(0.6, 121), 13.55, -15, pan=-0.3, cue="Hojas: paso a la ilustración", prov=True)
    for k, tt_ in enumerate(np.arange(13.75, 15.6, BEAT / 2)):
        sfx.add(pencil(0.16 + 0.06 * (k % 3), 130 + k), tt_ + 0.02, -21 + (2 if k % 2 == 0 else 0), pan=0.45 * math.sin(k * 1.7), cue="Trazos de lápiz rítmicos" if k == 0 else None, prov=k == 0)
    arp = ["F4", "A4", "C5", "E5", "G5", "E5", "C5", "A4"]
    for k, tt_ in enumerate(np.arange(13.75, 15.7, S16 * 2)):
        music.add(kalimba(NOTE[arp[k % 8]]), tt_, -17, pan=0.3 * math.cos(k))
    CUES.append((13.75, "MUSICA", "Kalimba en Fa mayor (mundo orgánico)", False))
    music.add(pad(hz("F2", "C3", "A3", "E4", "G4"), 2.1, 75, att=0.4, rel=0.3, cutoff=(800, 3500)), 13.75, -17)
    sfx.add(leaves(0.5, 122), 14.7, -18, pan=0.4)

    # ======== 15.75 – 17.0  RETURN TO THE REAL BURGER ================================
    music.add(kick(1.0, 46), 15.75, -6)
    music.add(drop_low(NOTE["F1"] * 2), 15.75, -8)
    music.add(pad(hz("F1", "F2", "C3", "A3", "E4", "G4", "C5"), 1.5, 76, att=0.02, rel=1.2, cutoff=(2600, 500)), 15.75, -11, cue="Acorde de resolución (Fa add9)")
    foley.add(fire_bed(1.5, 204), 15.6, -19, cue="Regreso al sonido físico: fuego", prov=True)
    foley.add(steam(1.0, 141, 1600, 3200), 15.9, -19)
    foley.add(reverse_swell(0.42, 151, 4000), 16.6, -13, cue="Anticipación del mordisco (swell)", prov=True)

    # ======== 17.0 – 18.5  THE BITE ===================================================
    foley.add(crunch(), 17.115, 5.0, cue="CRUNCH del mordisco (domina la mezcla)", prov=True)
    foley.add(lp(rng(5).standard_normal((2, S(1.2))), 300) * expenv(S(1.2), 0.5)[None] * 0.3, 17.12, -30)

    # ======== 18.5 – 19.8  EMPTY PLATE ================================================
    room = lp(rng(161).standard_normal((2, S(1.4))), 700) * 0.02
    foley.add(room, 18.5, -18, cue="Tono de sala (casi silencio)", prov=True)
    foley.add(ceramic_tick(171, 2600, 0.35), 18.69, -26, pan=0.2, cue="Miga sobre el plato", prov=True)
    foley.add(ceramic_tick(172, 3100, 0.5), 19.51, -22, pan=-0.1, cue="Miga sobre el plato (la que cae en cuadro)", prov=True)

    # ======== 19.8 – 25.0  BRAND ======================================================
    sig.add(drop_low(NOTE["D2"]), GB["line1"], -9, cue="Golpe tipográfico 1")
    sig.add(metal_tick(181, 3300) * 0.5, GB["line1"], -20)
    sig.add(drop_low(NOTE["A2"]), GB["line2"], -9, cue="Golpe tipográfico 2")
    sig.add(metal_tick(182, 4400) * 0.5, GB["line2"], -19)
    sig.add(pad(hz("D3", "A3", "C4", "E4"), 2.0, 81, att=0.6, rel=0.5, cutoff=(400, 1400)), GB["line2"], -21)
    sig.add(whoosh(0.4, 191, 3000, 700, 0.9), GB["copy_out"] - 0.05, -21, cue="Salida del copy")
    for k, nt in enumerate(["F4", "A4", "C5", "E5"]):
        sig.add(kalimba(NOTE[nt]) * 0.6, GB["logo"] + k * 0.06, -19, pan=-0.3 + 0.2 * k)
    sig.add(whoosh(0.42, 192, 4500, 1500, 2.0) * 0.5, GB["drop_land"] - 0.42, -26)
    sig.add(plip(NOTE["D6"], 0.18), GB["drop_land"], -10, cue="FIRMA: la gota aterriza (plip + golpe cálido + tss)")
    sig.add(drop_low(NOTE["D2"]), GB["drop_land"], -7)
    sig.add(sizzle(0.7, lambda t: 2400 * np.exp(-t / 0.3) + 200, 777, lambda t: np.exp(-t / 0.25)), GB["drop_land"] + 0.01, -14, prov=True)
    sig.add(pad(hz("F2", "C3", "G3", "A3", "E4", "C5"), DUR - GB["drop_land"] + 0.1, 82, att=0.5, rel=1.2, cutoff=(600, 2200)), GB["drop_land"], -15, cue="Resolución musical minimalista (Fa add9)")
    sig.add(kalimba(NOTE["C5"]) * 0.5, GB["cta"], -20)
    sig.add(kalimba(NOTE["G5"]) * 0.35, GB["url"], -24)
    CUES.append((24.1, "PROV_FOLEY_ASMR", "Chisporroteo vuelve: enlaza con el inicio en reproducción en bucle", True))
    return foley, sfx, music, sig


def master(foley, sfx, music, sig):
    # glue: duck the music under the impact and the crunch (sidechain)
    key = np.zeros(N);
    for t0, depth, rel in [(1.0, 0.5, 0.25), (17.1, 0.97, 1.4)]:
        i = S(t0 - 0.03); n = N - i; tt = np.arange(n) / SR
        key[i:] = np.maximum(key[i:], depth * np.exp(-np.maximum(tt - 0.05, 0) / rel))
    duck = 1 - key
    # after the bite the score is gone until the brand
    t = np.arange(N) / SR
    duck *= np.where((t > 17.15) & (t < GB["line1"] - 0.02), 0.03, 1.0)
    music.x *= duck[None] * db(-9.0)
    sig.x *= db(-2.0)
    # spaces
    room_ir = reverb_ir(0.45, 0.6, 9, bright=7000, pre=0.006)
    hall_ir = reverb_ir(1.9, 2.4, 10, bright=5000, pre=0.02)
    foley.x = convolve(foley.x, room_ir, 0.12)
    sfx.x = convolve(sfx.x, hall_ir, 0.22)
    music.x = convolve(music.x, hall_ir, 0.18)
    sig.x = convolve(sig.x, hall_ir, 0.28)
    stems = {"01_PROV_FOLEY_ASMR": foley.x, "02_SFX_TRANSICIONES": sfx.x, "03_MUSICA": music.x, "04_FIRMA_SONORA": sig.x}
    mix = sum(stems.values())
    mix = hp(mix, 32, 2)
    # gentle low-mid cleanup + presence for small speakers
    mix = mix - 0.12 * bp(mix, 220, 420, 1) + 0.10 * bp(mix, 2500, 5000, 1)
    # loudness → -14 LUFS integrated, then true-peak-ish limiter at -1 dBTP
    meter = pyln.Meter(SR)
    g = db(-14.0 - meter.integrated_loudness(mix.T))
    mix *= g
    for k in stems: stems[k] = stems[k] * g
    for _ in range(3):   # converge: limiter costs loudness on the transient-heavy moments
        out, gr = limiter(mix, ceiling=db(-1.7))
        d = -14.0 - meter.integrated_loudness(out.T)
        if abs(d) < 0.15: break
        mix *= db(d)
        for k in stems: stems[k] = stems[k] * db(d)
    return out, stems, meter.integrated_loudness(out.T)

def limiter(x, ceiling, look=0.003, rel=0.08):
    """look-ahead peak limiter; 4x oversampled detection for an inter-sample-aware ceiling"""
    up = signal.resample_poly(x, 4, 1, axis=1)
    pk = np.abs(up).max(axis=0)[: 4 * x.shape[1]].reshape(-1, 4).max(axis=1)
    need = np.minimum(1.0, ceiling / np.maximum(pk, 1e-9))
    L = S(look)
    mn = _moving_min(need, L)
    a = math.exp(-1 / (rel * SR)); g = np.empty_like(mn); v = 1.0
    for i, m in enumerate(mn):
        v = m if m < v else a * v + (1 - a) * m
        g[i] = v
    g = np.convolve(g, np.ones(L) / L, mode="same")
    g = np.minimum(g, mn)
    return x * g[None], g

def _moving_min(x, L):
    from scipy.ndimage import minimum_filter1d
    return minimum_filter1d(x, size=2 * L + 1, mode="nearest")


if __name__ == "__main__":
    foley, sfx, music, sig = build()
    mix, stems, lufs = master(foley, sfx, music, sig)
    os.makedirs(os.path.join(HERE, "stems"), exist_ok=True)
    for k, v in stems.items():
        sf.write(os.path.join(HERE, "stems", k + ".wav"), v.T.astype(np.float32), SR, subtype="PCM_24")
    sf.write(os.path.join(HERE, "DIBURAMA_HAMBURGUESA_MIX_48k.wav"), mix.T.astype(np.float32), SR, subtype="PCM_24")
    with open(os.path.join(HERE, "CUE_SHEET.md"), "w") as f:
        f.write("# Cue sheet — DIBURAMA spot hamburguesa\n\n")
        f.write("`PROV` = sonido de comida/foley **sintetizado provisionalmente** (no es grabación real). "
                "Sustituir por foley grabado con micrófono cercano o librería con licencia comercial, respetando el timecode.\n\n")
        f.write("| TC (s) | Frame @24 | Frame @30 | Stem | Evento | Estado |\n|---|---|---|---|---|---|\n")
        for t_, st, name, prov in sorted(CUES, key=lambda c: c[0]):
            f.write(f"| {t_:6.3f} | {int(round(t_ * 24))} | {int(round(t_ * 30))} | {st} | {name} | {'PROV — sustituir' if prov else 'original'} |\n")
    print(f"mix written, integrated loudness {lufs:.2f} LUFS, peak {20 * np.log10(np.abs(mix).max()):.2f} dBFS")
