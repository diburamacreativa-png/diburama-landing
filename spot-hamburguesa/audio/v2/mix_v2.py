"""DIBURAMA spot — V2 sound: two mixes over the V2 picture (30 fps, 25.0 s).

  A · ASMR CINEMATOGRÁFICO  — the food is the protagonist; the music is born from the real foley
                              (sizzle → hi-hats, cutlery → snare, gel squish → percussion, foley through
                              tuned resonators → notes). Sparse, wide dynamics, real silences.
  B · ELECTRÓNICA PREMIUM   — same foley edit; the central block (7.5–15.7 s) is driven by a full
                              electronic production: punchy kick, layered clap, sidechained rolling bass,
                              supersaw stabs, arpeggios, risers.

ALL food / foley / ambience sounds are the client's original recordings (audio/foley/originales,
SHA-256 verified against MAPEO_ORIGINALES.csv). Nothing gastronomic is synthesised. The music is
original and generated here (synthesis + the same foley recordings used as instruments).

Outputs (per mix, under audio/v2/<A_ASMR|B_ELECTRONIC>/):
  tracks/<BUS>__<cue>.flac   one track per effect / instrument (24-bit, 48 kHz, post-fader, pre-master)
  stems/<BUS>.wav            MUSICA, FOLEY, SFX, AMBIENTES (24-bit WAV, post-bus processing, pre-master)
  DIBURAMA_V2_<MIX>_MIX_48k24.wav   final master (-14 LUFS integrated, ≤ -1.5 dBTP before AAC)
and audio/v2/CUE_SHEET_V2.md (every cue: source file, source in/out, master time, both mixes' gains).

usage: python3 audio/v2/mix_v2.py [A|B|both]
"""
import os, sys, json, math, subprocess
from fractions import Fraction
import numpy as np, soundfile as sf
from scipy import signal
from scipy.ndimage import minimum_filter1d
import pyloudnorm as pyln

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
SRC = os.path.join(ROOT, "audio", "foley", "originales")
SR = 48000; DUR = 25.0; N = int(DUR * SR)
BPM = 120.0; BEAT = 60 / BPM; S16 = BEAT / 4
GB = json.load(open(os.path.join(ROOT, "project", "edit_decisions.json")))["graphics"]["beats"]
# key picture events (V2 edit)
EV = dict(impact=1.0, t1=3.43, t2=7.5, t3=10.66, lock=10.74, t4=13.62, ret=15.75, bite=17.115, plate=18.5,
          gfx=19.792, crumb1=18.69, crumb2=19.51)

def S(t): return int(round(t * SR))
def db(x): return 10 ** (x / 20)
def rng(seed): return np.random.default_rng(seed)


# ------------------------------------------------------------------ source handling
_CACHE = {}
def load(name):
    if name not in _CACHE:
        raw = subprocess.run(["ffmpeg", "-v", "quiet", "-i", os.path.join(SRC, name), "-ar", str(SR), "-ac", "2",
                              "-f", "f32le", "-"], capture_output=True, check=True).stdout
        _CACHE[name] = np.frombuffer(raw, np.float32).reshape(-1, 2).T.astype(np.float64)
    return _CACHE[name]

def frag(name, a, b):
    x = load(name); return x[:, S(a):S(b)].copy()

def sos(kind, f, order=2): return signal.butter(order, f, btype=kind, fs=SR, output="sos")
def hp(x, f, o=2): return signal.sosfilt(sos("highpass", f, o), x, axis=-1)
def lp(x, f, o=2): return signal.sosfilt(sos("lowpass", f, o), x, axis=-1)
def bp(x, lo, hi, o=2): return signal.sosfilt(sos("bandpass", [lo, hi], o), x, axis=-1)
def notch(x, f, q=8):
    b, a = signal.iirnotch(f, q, fs=SR); return signal.lfilter(b, a, x, axis=-1)
def peq(x, f, gain_db, q=1.0):
    A = 10 ** (gain_db / 40); w = 2 * math.pi * f / SR; al = math.sin(w) / (2 * q)
    b = [1 + al * A, -2 * math.cos(w), 1 - al * A]; a = [1 + al / A, -2 * math.cos(w), 1 - al / A]
    return signal.lfilter(b, a, x, axis=-1)
def pitch(x, ratio):
    """resample-based pitch/speed change (tape style): ratio > 1 = higher & shorter"""
    fr = Fraction(1 / ratio).limit_denominator(48)
    return signal.resample_poly(x, fr.numerator, fr.denominator, axis=-1)
def fades(x, fi=0.003, fo=0.02, shape=2.0):
    n = x.shape[-1]; e = np.ones(n)
    a, b = min(S(fi), n), min(S(fo), n)
    if a: e[:a] = np.linspace(0, 1, a) ** shape
    if b: e[n - b:] *= np.linspace(1, 0, b) ** shape
    return x * e
def onset(name, a, b, hop=96):
    """time (s, in the source) of the strongest attack in [a, b]"""
    m = np.abs(load(name)[:, S(a):S(b)]).mean(0)
    e = np.sqrt(np.convolve(m ** 2, np.ones(hop) / hop, "same"))[::hop] + 1e-7
    fl = np.diff(20 * np.log10(e), prepend=-140)
    return a + int(np.argmax(fl)) * hop / SR
def norm(x, peak=0.89):
    m = np.abs(x).max(); return x * (peak / m) if m > 0 else x
def rmsn(x, rms_db=-20.0):
    """normalise a bed/texture to an RMS reference (dBFS) so its fader gain is meaningful"""
    r = np.sqrt(np.mean(x ** 2)) + 1e-12; return x * (db(rms_db) / r)
def stereo(x):
    return np.vstack([x, x]) if x.ndim == 1 else x
def pan(x, p):
    x = stereo(x); a = (p + 1) * math.pi / 4
    return np.vstack([x[0] * math.cos(a) * math.sqrt(2), x[1] * math.sin(a) * math.sqrt(2)])
def widen(x, w):
    m, s = (x[0] + x[1]) / 2, (x[0] - x[1]) / 2; return np.vstack([m + s * w, m - s * w])
def loop_to(x, n, xf=0.12):
    L = S(xf); out = x.copy()
    while out.shape[1] < n:
        r = np.linspace(0, 1, L)
        mid = out[:, -L:] * np.sqrt(1 - r) + x[:, :L] * np.sqrt(r)
        out = np.concatenate([out[:, :-L], mid, x[:, L:]], axis=1)
    return out[:, :n]
def autom(n, pts):
    """gain automation (dB) from [(t_rel, dB), ...]"""
    t = np.arange(n) / SR; k = np.array(pts, float)
    return db(np.interp(t, k[:, 0], k[:, 1]))


# ------------------------------------------------------------------ tracks
CUES = []          # for the cue sheet
class Mix:
    def __init__(self, name):
        self.name = name; self.tracks = {}
    def track(self, bus, cue):
        k = (bus, cue)
        if k not in self.tracks: self.tracks[k] = np.zeros((2, N))
        return self.tracks[k]
    def put(self, bus, cue, sig, t, gain_db=0.0, src=None):
        buf = self.track(bus, cue); sig = stereo(np.asarray(sig, float)) * db(gain_db)
        i = S(t)
        if i < 0: sig = sig[:, -i:]; i = 0
        j = min(N, i + sig.shape[1])
        if j > i: buf[:, i:j] += sig[:, :j - i]
        if src: CUES.append(dict(mix=self.name, bus=bus, cue=cue, t=round(t, 3), src=src, gain=gain_db))

def dense(x, drive):
    """parallel soft saturation: raises the body of a transient without dulling its attack"""
    if drive <= 0: return x
    sat = np.tanh(drive * x / (np.abs(x).max() + 1e-9)) / np.tanh(drive)
    return norm(0.5 * norm(x) + 0.5 * sat)

def place_onset(mx, bus, cue, name, a, b, at, align, gain, proc=None, fi=0.002, fo=0.05, drive=0.0):
    """take source [a, b], put its attack `align` (source time) exactly on master time `at`"""
    x = fades(frag(name, a, b), fi, fo)
    if proc: x = proc(x)
    x = dense(norm(x), drive)                     # transients: peak-normalised, gain = level below full scale
    mx.put(bus, cue, x, at - (align - a), gain, src=f"{name} {a:.3f}–{b:.3f} (attack {align:.3f} → {at:.3f}s)")


# ------------------------------------------------------------------ FOLEY / SFX / AMBIENTES (both mixes)
def foley(mx, mode):
    A = mode == "A"
    F, X, AM = "FOLEY", "SFX", "AMBIENTES"
    g = lambda a_, b_: a_ if A else b_

    # ---------- 0 – 3.4  GRILL: pure ASMR
    bed = rmsn(loop_to(frag("02_sizzle_base.mp3", 9.0, 21.0), S(3.95)))
    bed = bed * autom(bed.shape[1], [(0, -7), (0.95, -6), (1.0, -1), (1.6, 0), (3.0, -3), (3.95, -30)])
    mx.put(F, "sizzle_base", fades(bed, 0.004, 0.3), 0.0, g(0, -1), src="02_sizzle_base.mp3 9.0–21.0 loop")
    fire = rmsn(loop_to(frag("04_fuego.mp3", 0.3, 7.9), S(3.9)))
    mx.put(AM, "fuego", fades(peq(fire, 120, 4, 0.8), 0.004, 0.6), 0.0, g(-9, -10), src="04_fuego.mp3 0.3–7.9")
    # the fall: air of the patty passing the camera (low-passed, not a generic swish)
    place_onset(mx, X, "caida_carne", "10_whoosh.mp3", 0.15, 1.2, 0.93, 0.522, -17, proc=lambda x: lp(x, 2600), fo=0.25)
    # THE IMPACT — four layers on the same frame
    on16 = onset("16_impacto_humedo.mp3", 0.30, 0.50)
    place_onset(mx, F, "impacto_carne_golpe", "16_impacto_humedo.mp3", 0.37, 1.45, EV["impact"], on16, 2.0, fo=0.35, drive=3.0)
    place_onset(mx, F, "impacto_carne_cuerpo", "16_impacto_humedo.mp3", 0.37, 1.45, EV["impact"], on16, 0.5,
                proc=lambda x: peq(lp(x, 150, 4), 60, 5, 0.9), fo=0.4, drive=2.0)          # weight / body
    place_onset(mx, F, "grasa_estalla", "03_sizzle_detalle.mp3", 3.80, 6.40, EV["impact"] + 0.035, 3.892, -4, fo=0.6, drive=2.0)
    carne = rmsn(fades(lp(frag("01_carne_parrilla.mp3", 15.10, 18.0), 9500), 0.006, 0.9))
    carne = carne * autom(carne.shape[1], [(0, 0), (0.6, -1), (2.9, -6)])
    mx.put(F, "carne_parrilla", carne, EV["impact"] + 0.01, g(-2, -4), src="01_carne_parrilla.mp3 15.10–18.0")
    st = rmsn(fades(hp(frag("05_vapor.mp3", 7.0, 8.9), 700), 0.25, 0.7))
    mx.put(F, "vapor_hero", st, 1.85, g(-5, -7), src="05_vapor.mp3 7.0–8.9")

    # ---------- T1 3.43  into the crust
    place_onset(mx, X, "t1_rush", "10_whoosh.mp3", 0.0, 1.6, EV["t1"], 0.522, -5, fo=0.6)
    place_onset(mx, F, "t1_pan_textura", "07_queso_elastico.mp3", 0.40, 1.30, EV["t1"] + 0.02, 0.582, -10,
                proc=lambda x: hp(x, 250), fo=0.3)
    tail = rmsn(fades(lp(frag("11_transicion.mp3", 1.8, 4.5), 900), 0.2, 1.2))
    mx.put(AM, "t1_tunel", tail, EV["t1"] + 0.1, -9, src="11_transicion.mp3 1.8–4.5 (LP 900)")

    # ---------- T2 7.5  practical light flare → cheese
    riser = rmsn(fades(frag("05_vapor.mp3", 6.05, 7.40), 0.05, 0.03))
    mx.put(X, "t2_succion_vapor", riser, EV["t2"] - riser.shape[1] / SR, -5, src="05_vapor.mp3 6.05–7.40 (riser)")
    rw = norm(fades(frag("10_whoosh.mp3", 0.05, 0.56)[:, ::-1], 0.1, 0.01))
    mx.put(X, "t2_succion_inversa", rw, EV["t2"] - rw.shape[1] / SR, -9, src="10_whoosh.mp3 0.05–0.56 reversed")
    ch = rmsn(fades(frag("06_queso_textura.mp3", 5.4, 7.7), 0.04, 0.5))
    mx.put(F, "queso_textura", peq(ch, 3000, 2, 0.8), EV["t2"] + 0.05, g(-4, -7), src="06_queso_textura.mp3 5.4–7.7")
    for k, (a, b, al, at, gg) in enumerate([(0.40, 1.10, 0.582, 7.62, -9), (5.40, 6.10, 5.628, 8.55, -12), (0.40, 1.10, 0.582, 9.30, -14)]):
        place_onset(mx, F, "queso_elastico", "07_queso_elastico.mp3", a, b, at, al, g(gg, gg - 3), fo=0.3)

    # ---------- T3 10.66 vortex → gear lock 10.74
    place_onset(mx, X, "t3_vortice", "11_transicion.mp3", 0.0, 1.6, EV["t3"], 0.795, -5, fo=0.6)
    on9 = onset("09_impacto_metalico.mp3", 0.0, 0.08)
    place_onset(mx, X, "t3_impacto_metal", "09_impacto_metalico.mp3", 0.0, 1.32, EV["lock"], on9, -1.5, fo=0.5)
    place_onset(mx, X, "t3_impacto_metal_sub", "09_impacto_metalico.mp3", 0.0, 1.32, EV["lock"], on9, -4,
                proc=lambda x: lp(pitch(x, 0.5), 220, 4), fo=0.6)
    gears = rmsn(fades(frag("08_engranajes.mp3", 3.0, 6.05), 0.06, 0.6))
    mx.put(F, "engranajes", peq(gears, 250, -3, 0.7), EV["lock"] + 0.02, g(-7, -10), src="08_engranajes.mp3 3.0–6.05")

    # ---------- T4 13.62  metal → air → leaves (no generic whoosh)
    m = frag("08_engranajes.mp3", 6.0, 7.4)
    parts = np.array_split(m, 7, axis=1); slow = []
    for i, p in enumerate(parts):
        slow.append(lp(pitch(p, 1.0 - 0.07 * i), 6000 - 700 * i))
    slow = rmsn(fades(np.concatenate(slow, axis=1), 0.03, 0.35))
    mx.put(X, "t4_metal_se_ablanda", slow, EV["t4"] - 0.62, -6, src="08_engranajes.mp3 6.0–7.4 (pitch/LP glide down)")
    air = rmsn(fades(hp(frag("05_vapor.mp3", 9.0, 10.3), 1200), 0.35, 0.5))
    mx.put(X, "t4_aire", air, EV["t4"] - 0.35, -7, src="05_vapor.mp3 9.0–10.3 (HP 1.2k)")
    veg = rmsn(fades(hp(frag("06_queso_textura.mp3", 9.0, 11.6), 1800), 0.15, 0.6))
    mx.put(F, "t4_textura_vegetal", veg, EV["t4"] - 0.05, g(-5, -8), src="06_queso_textura.mp3 9.0–11.6 (HP 1.8k)")
    org = rmsn(fades(hp(frag("06_queso_textura.mp3", 14.0, 16.0), 2500), 0.2, 0.5))
    mx.put(F, "ilustracion_textura", org, 14.2, g(-10, -13), src="06_queso_textura.mp3 14.0–16.0 (HP 2.5k)")

    # ---------- 15.75 back to the real burger
    fire2 = rmsn(fades(frag("04_fuego.mp3", 3.9, 5.6), 0.15, 0.4))
    mx.put(AM, "fuego_regreso", fire2, 15.62, g(-11, -13), src="04_fuego.mp3 3.9–5.6")
    sz = rmsn(fades(frag("02_sizzle_base.mp3", 30.0, 31.5), 0.12, 0.45))
    mx.put(F, "sizzle_regreso", sz, 15.70, g(-7, -9), src="02_sizzle_base.mp3 30.0–31.5")
    st2 = rmsn(fades(hp(frag("05_vapor.mp3", 9.6, 10.8), 900), 0.3, 0.5))
    mx.put(F, "vapor_regreso", st2, 15.85, -10, src="05_vapor.mp3 9.6–10.8")
    ant = norm(fades(lp(frag("10_whoosh.mp3", 0.30, 0.56)[:, ::-1], 2400), 0.12, 0.004))
    mx.put(X, "anticipacion_mordisco", ant, EV["bite"] - ant.shape[1] / SR, -14, src="10_whoosh.mp3 reversed (LP)")

    # ---------- THE BITE 17.115 — dominates the mix for an instant
    on12 = onset("12_mordisco.mp3", 0.66, 0.80)
    place_onset(mx, F, "mordisco_pan", "12_mordisco.mp3", 0.55, 1.62, EV["bite"], on12, 9.0,
                proc=lambda x: peq(peq(x, 180, 3, 0.9), 4200, 2.5, 1.2), fi=0.004, fo=0.35, drive=6.0)
    hum = 1000.0
    on13 = onset("13_crunch_asmr.mp3", 24.45, 24.55)
    place_onset(mx, F, "mordisco_crack", "13_crunch_asmr.mp3", 24.40, 24.98, EV["bite"], on13, 8.0,
                proc=lambda x: notch(notch(x, hum, 6), hum * 2, 6), fo=0.25, drive=5.0)
    on13b = onset("13_crunch_asmr.mp3", 11.30, 11.42)
    place_onset(mx, F, "mordisco_desmenuza", "13_crunch_asmr.mp3", 11.30, 11.62, EV["bite"] + 0.045, on13b, 4.0,
                proc=lambda x: notch(hp(x, 600), hum, 6), fo=0.12, drive=2.5)
    place_onset(mx, F, "mordisco_peso", "16_impacto_humedo.mp3", 0.37, 0.9, EV["bite"], on16, 0.0,
                proc=lambda x: lp(x, 110, 4), fo=0.2, drive=2.0)

    # ---------- 18.5 – 19.8 empty plate: near silence
    room = rmsn(loop_to(frag("14_plato.mp3", 0.1, 1.8), S(1.45)))
    mx.put(AM, "tono_sala", fades(lp(room, 6000), 0.06, 0.35), EV["plate"], -30, src="14_plato.mp3 0.1–1.8 (room noise)")
    on14a = onset("14_plato.mp3", 4.95, 5.15); on14b = onset("14_plato.mp3", 6.95, 7.15)
    place_onset(mx, F, "miga_plato_1", "14_plato.mp3", 4.98, 5.30, EV["crumb1"], on14a, -24, proc=lambda x: hp(x, 2200), fo=0.15)
    place_onset(mx, F, "miga_plato_2", "14_plato.mp3", 6.98, 7.30, EV["crumb2"], on14b, -20, proc=lambda x: hp(x, 1800), fo=0.2)

    # ---------- brand: the drop lands (a real wet droplet, pitched), and the loop back to the grill
    on7 = onset("07_queso_elastico.mp3", 5.55, 5.70)
    place_onset(mx, X, "firma_gota", "07_queso_elastico.mp3", 5.55, 6.0, GB["drop_land"], on7, -7,
                proc=lambda x: hp(pitch(x, 1.6), 300), fo=0.12)
    tailb = fades(rmsn(loop_to(frag("02_sizzle_base.mp3", 9.0, 12.0), S(1.0))), 0.75, 0.0) * db(-7)
    mx.put(F, "sizzle_bucle", tailb, DUR - 1.0, g(0, 0.5), src="02_sizzle_base.mp3 9.0–12.0 (loop → t=0)")
    firet = fades(rmsn(frag("04_fuego.mp3", 0.3, 1.3)), 0.8, 0.0)
    mx.put(AM, "fuego_bucle", firet, DUR - 1.0, g(-9, -10), src="04_fuego.mp3 0.3–1.3 (loop → t=0)")


# ------------------------------------------------------------------ instruments
NOTE = {n: 440 * 2 ** ((i - 57) / 12) for i, n in enumerate(
    [f"{p}{o}" for o in range(0, 8) for p in ["C", "C#", "D", "Eb", "E", "F", "F#", "G", "Ab", "A", "Bb", "B"]])}
def hz(*n): return [NOTE[x] for x in n]

def ks(excite, f, decay=0.996, bright=0.5, length=None):
    """Karplus–Strong string excited by any signal (mono) — used to tune real foley into notes"""
    L = max(2, int(round(SR / f)))
    n = length or excite.shape[-1]
    x = np.zeros(n); x[:min(n, excite.shape[-1])] = excite[:n]
    a = np.zeros(L + 2); a[0] = 1; a[L] = -decay * (1 - bright); a[L + 1] = -decay * bright
    return signal.lfilter([1.0], a, x)

def resonate(x, freqs, decay=0.996, bright=0.5, tail=1.6):
    """foley → chord: the recording excites a bank of tuned strings"""
    m = stereo(x).mean(0); n = m.shape[0] + S(tail)
    out = np.zeros((2, n))
    for i, f in enumerate(freqs):
        y = ks(hp(m, f * 0.8), f, decay, bright, n)
        out += pan(y / len(freqs), 0.5 * math.sin(i * 2.1))
    return norm(lp(out, 9000))

def kick(tone=50, punch=1.0, length=0.45):
    n = S(length); t = np.arange(n) / SR
    f = tone + 110 * punch * np.exp(-t / 0.03)
    x = np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t / 0.22) * (1 - np.exp(-t / 0.0008))
    click = hp(rng(3).standard_normal(n), 2500) * np.exp(-t / 0.004) * 0.35
    return np.tanh(2.4 * (x + click)) / np.tanh(2.4)

def sub(f, length, att=0.004, rel=0.05):
    n = S(length); t = np.arange(n) / SR
    x = np.sin(2 * np.pi * f * t) + 0.18 * np.sin(4 * np.pi * f * t)
    e = np.clip(t / att, 0, 1) * np.clip((length - t) / rel, 0, 1)
    return np.tanh(1.6 * x * e) / np.tanh(1.6)

def saw(f, n, voices=1, det=0.0, seed=0, oversample=4):
    """band-limited-ish saw: oversampled naive saw + decimation"""
    t = np.arange(n * oversample) / (SR * oversample); r = rng(seed); out = 0
    for v in range(voices):
        fv = f * (1 + det * (v - (voices - 1) / 2))
        out = out + signal.sawtooth(2 * np.pi * fv * t + r.uniform(0, 6.28))
    return signal.decimate(out / voices, oversample, ftype="fir")

def sweep_lp(x, f0, f1, q_db=0.0, block=256, curve=1.0):
    y = np.zeros_like(x); zi = np.zeros((2, 2)) if False else None; n = x.shape[-1]
    sos_z = None
    for i in range(0, n, block):
        u = (i / max(1, n - 1)) ** curve; f = min(f0 * (f1 / f0) ** u, SR * 0.45)
        s_ = sos("lowpass", f, 2)
        if sos_z is None: sos_z = np.zeros((s_.shape[0], 2))
        y[i:i + block], sos_z = signal.sosfilt(s_, x[i:i + block], zi=sos_z)
    return y

def env_ar(n, att, rel):
    t = np.arange(n) / SR; return np.clip(t / max(att, 1e-4), 0, 1) * np.exp(-np.maximum(t - att, 0) / rel)

def pluck_synth(f, length=0.5, cutoff=(4500, 600), seed=0, det=0.004):
    n = S(length); x = saw(f, n, 3, det, seed)
    e = env_ar(n, 0.002, length * 0.35)
    return sweep_lp(x * e, cutoff[0], cutoff[1], curve=0.5)

def supersaw(freqs, length, cutoff=(800, 3000), att=0.02, rel=0.3, seed=1):
    n = S(length); out = np.zeros((2, n))
    for c in range(2):
        x = sum(saw(f, n, 5, 0.012 + 0.003 * c, seed + 7 * i + c) for i, f in enumerate(freqs))
        out[c] = sweep_lp(x, cutoff[0], cutoff[1])
    t = np.arange(n) / SR
    return norm(out) * (np.clip(t / att, 0, 1) * np.clip((length - t) / rel, 0, 1))

def bass_synth(f, length, cutoff=900, drive=2.0):
    n = S(length); t = np.arange(n) / SR
    x = saw(f, n, 2, 0.003, 9)
    e = np.exp(-t / 0.12)
    y = sweep_lp(x, cutoff, 120, curve=0.6) + 0.8 * np.sin(2 * np.pi * f * t)
    y = y * np.clip(t / 0.003, 0, 1) * np.clip((length - t) / 0.015, 0, 1)
    return np.tanh(drive * y) / np.tanh(drive)

def clap(seed=4):
    n = S(0.35); r = rng(seed); t = np.arange(n) / SR; x = np.zeros(n)
    for off in (0.0, 0.009, 0.017):
        i = S(off); L = n - i; b = r.standard_normal(L) * np.exp(-np.arange(L) / SR / (0.006 if off < 0.017 else 0.09))
        x[i:] += b
    return norm(bp(x, 900, 7000))

def reverb_ir(rt60, length, seed, bright=6500, pre=0.015):
    n = S(length); r = rng(seed); t = np.arange(n) / SR; ir = np.zeros((2, n + S(pre)))
    for c in range(2):
        nz = r.standard_normal(n) * np.exp(-6.9 * t / rt60)
        ir[c, S(pre):] = lp(nz, bright) * (1 - np.clip(t / (rt60 * 0.7), 0, 1)) + lp(nz, 1600) * np.clip(t / (rt60 * 0.3), 0, 1)
    return ir / np.sqrt((ir ** 2).sum(axis=1, keepdims=True))

def convolve(x, ir, wet):
    y = np.vstack([signal.fftconvolve(x[c], ir[c])[:N] for c in range(2)])
    return x + y * wet


# ------------------------------------------------------------------ foley-born instruments
def sizzle_hats(t0, t1, accent=(1.0, 0.35, 0.65, 0.4), dec=(0.03, 0.06), gain=1.0, seed_src=(20.0, 40.0)):
    """the real sizzle, high-passed and gated on the 16th grid → hi-hats"""
    n0, n1 = S(t0), S(t1); src = loop_to(frag("02_sizzle_base.mp3", *seed_src), n1 - n0)
    src = hp(src, 5200, 2)
    t = (np.arange(n0, n1)) / SR; k = np.floor(t / S16 + 1e-9).astype(int); ph = t - k * S16
    acc = np.array(accent)[k % 4]; d = np.where(k % 4 == 2, dec[1], dec[0])
    g = np.exp(-ph / d) * acc * gain
    return src * g, t0

def cutlery_snare(which=0):
    a, al = [(5.95, 6.004), (8.60, 8.642)][which]
    x = fades(frag("15_cubiertos.mp3", a, a + 0.32), 0.0005, 0.12)
    return norm(peq(hp(x, 180), 2500, 3, 1.0)), al - a

def gel_perc(semitones=0, which=0):
    a, al = [(0.55, 0.582), (5.60, 5.628)][which]
    x = fades(frag("07_queso_elastico.mp3", a, a + 0.28), 0.0005, 0.1)
    return norm(pitch(x, 2 ** (semitones / 12))), (al - a) / 2 ** (semitones / 12)

def gear_tick(i):
    a = 3.0 + (i * 0.173) % 2.5
    x = fades(hp(frag("08_engranajes.mp3", a, a + 0.07), 2500), 0.0005, 0.04)
    return norm(x)

def foley_kick():
    """kick built from the real wet impact (low-passed) + a sine sub for definition on phones"""
    on = onset("16_impacto_humedo.mp3", 0.30, 0.50)
    x = fades(lp(frag("16_impacto_humedo.mp3", on - 0.002, on + 0.35), 300, 4), 0.0005, 0.12).mean(0)
    k = kick(46, 0.7, 0.35)
    n = max(len(x), len(k)); y = np.zeros(n); y[:len(x)] += norm(x) * 0.8; y[:len(k)] += k * 0.6
    return np.tanh(1.5 * y) / np.tanh(1.5)


# ------------------------------------------------------------------ MUSIC A — ASMR cinematográfico
def music_A(mx):
    M = "MUSICA"
    # T1: the first musical element is born from the crust itself (gel squish through tuned strings, D minor)
    seed, _ = gel_perc(0, 0)
    mx.put(M, "A_resonador_nacimiento", resonate(seed, hz("D3", "A3", "F4"), 0.997, 0.45, 2.2), EV["t1"] + 0.02, -14)
    mx.put(M, "A_sub_drone", fades(sub(NOTE["D1"] * 2, 3.9, 0.9, 0.6), 0.6, 0.6), 3.55, -17)
    # pulse of sizzle, slowly gating in (3.6 – 7.5)
    hats, t0 = sizzle_hats(3.6, 7.5, accent=(0.9, 0.15, 0.5, 0.15), dec=(0.018, 0.035))
    hats = hats * np.clip((np.arange(hats.shape[1]) / SR) / 3.4, 0, 1) ** 2
    mx.put(M, "A_hats_chisporroteo", hats, t0, -9)
    # film world opens (6.0): soft resonant chord from the steam
    stx = frag("05_vapor.mp3", 7.0, 7.6)
    mx.put(M, "A_resonador_vapor", resonate(stx * 0.6, hz("Bb2", "F3", "D4", "A4"), 0.998, 0.6, 2.4), 5.95, -19)
    mx.put(M, "A_kick_foley", foley_kick(), 6.0, -10)
    # ---- 7.5 – 10.66 motion: half-time groove from foley
    fk = foley_kick()
    for b0 in np.arange(7.5, 10.6, 2.0):
        for p in (0.0, 1.25):
            if b0 + p < 10.6: mx.put(M, "A_kick_foley", fk, b0 + p, -7)
        sn, al = cutlery_snare(int(b0) % 2)
        mx.put(M, "A_caja_cubiertos", sn, b0 + 1.0 - al, -10)
    hats, t0 = sizzle_hats(7.5, 10.62, accent=(1.0, 0.3, 0.7, 0.35))
    mx.put(M, "A_hats_chisporroteo", hats, t0, -8)
    for k, tt in enumerate(np.arange(7.5 + S16 * 3, 10.55, S16 * 6)):
        g, al = gel_perc([0, 3, 7, 5][k % 4], k % 2)
        mx.put(M, "A_perc_queso", pan(g, 0.4 * math.sin(k * 1.3)), tt - al, -15)
    for b0, ch in [(7.5, hz("D3", "A3", "C4", "F4")), (9.5, hz("Bb2", "F3", "A3", "D4"))]:
        s, al = cutlery_snare(1)
        mx.put(M, "A_acordes_resonados", resonate(s * 0.5, ch, 0.9975, 0.5, 1.8), b0, -16)
    for b0 in np.arange(7.5, 10.6, 2.0):
        for nt, o, d in (("D2", 0, 0.7), ("D2", 1.25, 0.3), ("F2", 1.5, 0.45)):
            if b0 + o < 10.6: mx.put(M, "A_sub", sub(NOTE[nt], d), b0 + o, -12)
    # ---- 10.74 – 13.62 3D: precision metal
    for k, tt in enumerate(np.arange(10.75, 13.55, S16)):
        if k % 4 in (1, 3) or k % 8 == 6:
            mx.put(M, "A_ticks_engranaje", pan(gear_tick(k), 0.5 if k % 2 else -0.5), tt, -15 + (3 if k % 4 == 3 else 0))
    for k, b0 in enumerate(np.arange(10.75, 13.55, 1.0)):
        mx.put(M, "A_kick_foley", fk, b0, -8)
        tom = fades(lp(pitch(frag("09_impacto_metalico.mp3", 0.0, 0.6), 0.6 - 0.05 * (k % 3)), 900), 0.0005, 0.3)
        mx.put(M, "A_tom_metal", tom, b0 + 0.75, -15)
    for b0 in np.arange(10.75, 13.55, 2.0):
        for nt, o, d in (("Bb1", 0, 0.8), ("C2", 1.0, 0.6), ("A1", 1.5, 0.4)):
            mx.put(M, "A_sub", sub(NOTE[nt] * 2, d), b0 + o, -12)
    # ---- 13.62 – 15.7 organic: drums fall away, foley plucked in F major
    arp = hz("F3", "A3", "C4", "E4", "G4", "E4", "C4", "A3")
    for k, tt in enumerate(np.arange(13.62, 15.6, S16 * 2)):
        ex = fades(hp(frag("06_queso_textura.mp3", 12.88 + 0.01 * (k % 3), 12.98 + 0.01 * (k % 3)), 400), 0.0005, 0.03)
        mx.put(M, "A_arpegio_foley", pan(resonate(ex, [arp[k % 8]], 0.996, 0.4, 0.9), 0.35 * math.cos(k)), tt, -13)
    mx.put(M, "A_pad_organico", supersaw(hz("F2", "C3", "A3", "E4"), 2.1, (500, 1800), 0.4, 0.4, 5), 13.62, -24)
    # ---- 15.75 return: resolution, then the score withdraws
    mx.put(M, "A_kick_foley", fk, EV["ret"], -13)
    sn, _ = cutlery_snare(0)
    mx.put(M, "A_resolucion", resonate(sn, hz("F2", "C3", "A3", "E4", "G4"), 0.9985, 0.55, 2.4), EV["ret"], -17)
    mx.put(M, "A_sub", sub(NOTE["F1"] * 2, 1.0, 0.004, 0.6), EV["ret"], -14)
    # ---- brand: minimal resolution + signature
    sn0, _ = cutlery_snare(0); sn1, _ = cutlery_snare(1)
    mx.put(M, "A_golpe_copy", resonate(sn0 * 0.6, hz("D3", "A3"), 0.997, 0.5, 1.0), GB["line1"], -7)
    mx.put(M, "A_golpe_copy", resonate(sn1 * 0.6, hz("F3", "C4"), 0.997, 0.5, 1.0), GB["line2"], -7)
    mx.put(M, "A_kick_foley", fk, GB["line1"], -16); mx.put(M, "A_kick_foley", fk, GB["line2"], -16)
    mx.put(M, "A_cama_copy", supersaw(hz("D2", "A2", "F3", "C4"), GB["drop_land"] - GB["line1"] + 0.3, (350, 900), 0.5, 0.5, 21), GB["line1"], -17)
    mx.put(M, "A_kick_foley", fk, GB["drop_land"], -12)
    mx.put(M, "A_firma_acorde", resonate(seed, hz("F2", "C3", "G3", "A3", "E4", "C5"), 0.9992, 0.55, 2.2), GB["drop_land"], -12)
    mx.put(M, "A_pad_final", supersaw(hz("F2", "C3", "A3", "E4"), DUR - GB["drop_land"], (400, 1400), 0.5, 1.2, 8), GB["drop_land"], -24)


# ------------------------------------------------------------------ MUSIC B — electrónica premium
def music_B(mx):
    M = "MUSICA"
    K = kick(50, 1.0); CL = clap()
    # 2.6 – 3.43 tension under the ASMR (very low) → T1 hit
    mx.put(M, "B_sub_tension", fades(sub(NOTE["D1"] * 2, 0.9, 0.7, 0.05), 0.6, 0.02), 2.55, -18)
    mx.put(M, "B_kick", K, EV["t1"], -7)
    mx.put(M, "B_sub", sub(NOTE["D1"] * 2, 0.9, 0.004, 0.5), EV["t1"], -10)
    # build 3.5 – 7.5: filtered arp opening, hats from sizzle join at 6.0
    arp = hz("D4", "A4", "F4", "C5", "D5", "A4", "F4", "E4")
    for k, tt in enumerate(np.arange(3.5, 7.5, S16)):
        u = (tt - 3.5) / 4.0
        p = pluck_synth(arp[k % 8], 0.22, (700 + 5000 * u ** 1.6, 300), seed=k)
        mx.put(M, "B_arpegio", pan(p, 0.25 * math.sin(k * 0.9)), tt, -19 + 5 * u)
    for b0 in np.arange(4.5, 7.4, 1.0):
        mx.put(M, "B_kick", K, b0, -13 + 3 * (b0 - 4.5) / 3)
    hats, t0 = sizzle_hats(6.0, 7.5, accent=(0.7, 0.3, 0.9, 0.3))
    mx.put(M, "B_hats_chisporroteo", hats, t0, -11)
    rs = fades(hp(frag("05_vapor.mp3", 6.05, 7.40), 400), 0.05, 0.02)
    mx.put(M, "B_riser", rs, EV["t2"] - rs.shape[1] / SR, -16)
    # ---- 7.5 – 13.62 the drop: four-on-the-floor, clap+cutlery, rolling sidechained bass
    for b0 in np.arange(7.5, 13.6, BEAT):
        mx.put(M, "B_kick", K, b0, -5)
    for b0 in np.arange(7.5 + BEAT, 13.6, 2 * BEAT):
        sn, al = cutlery_snare(int(b0 * 2) % 2)
        mx.put(M, "B_clap", CL, b0, -11)
        mx.put(M, "B_clap_cubiertos", sn, b0 - al, -14)
    hats, t0 = sizzle_hats(7.5, 13.62, accent=(0.5, 0.35, 1.0, 0.35), dec=(0.025, 0.07))
    mx.put(M, "B_hats_chisporroteo", hats, t0, -7)
    prog = [("D2", hz("D3", "F3", "A3", "C4")), ("Bb1", hz("Bb2", "D3", "F3", "A3")),
            ("F1", hz("F2", "A2", "C3", "E3")), ("C2", hz("C3", "E3", "G3", "Bb3"))]
    for bar, b0 in enumerate(np.arange(7.5, 13.6, 2.0)):
        root, chord = prog[bar % 4]
        for k in range(16):
            tt = b0 + k * S16 * 2
            if tt >= 13.6: break
            if k % 2 == 0: continue                                         # offbeat rolling bass
            mx.put(M, "B_bajo", bass_synth(NOTE[root] * (2 if k % 4 == 3 else 1), S16 * 1.7, 1100), tt, -11)
        mx.put(M, "B_stabs", supersaw([c * 2 for c in chord], 0.32, (5000, 900), 0.004, 0.12, bar), b0 + BEAT * 1.5, -16)
        mx.put(M, "B_stabs", supersaw([c * 2 for c in chord], 0.22, (4000, 900), 0.004, 0.1, bar + 9), b0 + BEAT * 3.5, -18)
    for k, tt in enumerate(np.arange(7.5 + S16 * 3, 10.6, S16 * 6)):
        g, al = gel_perc([0, 5, 7, 12][k % 4], k % 2)
        mx.put(M, "B_perc_queso", pan(g, 0.5 * math.sin(k)), tt - al, -18)
    for k, tt in enumerate(np.arange(10.75, 13.55, S16)):
        if k % 2 == 1:
            mx.put(M, "B_ticks_engranaje", pan(gear_tick(k), 0.6 if k % 4 == 1 else -0.6), tt, -17)
    mx.put(M, "B_crash_vortice", fades(hp(frag("11_transicion.mp3", 0.6, 2.6), 1500), 0.002, 1.2), EV["t3"], -16)
    # ---- 13.62 break: kick halftime, filter closes, F major arp
    arp2 = hz("F4", "A4", "C5", "E5", "G5", "E5", "C5", "A4")
    for k, tt in enumerate(np.arange(13.62, 15.6, S16)):
        u = (tt - 13.62) / 2.0
        mx.put(M, "B_arpegio", pan(pluck_synth(arp2[k % 8], 0.2, (5200 - 3000 * u, 400), seed=40 + k), 0.3 * math.cos(k)), tt, -17)
    for b0 in (13.62, 14.62):
        mx.put(M, "B_kick", K, b0, -8); mx.put(M, "B_sub", sub(NOTE["F1"] * 2, 0.9), b0, -12)
    mx.put(M, "B_pad", supersaw(hz("F2", "C3", "A3", "E4"), 2.1, (600, 2600), 0.3, 0.3, 4), 13.62, -20)
    # ---- 15.75 final hit, then cut before the bite
    mx.put(M, "B_kick", K, EV["ret"], -10)
    mx.put(M, "B_sub", sub(NOTE["F1"] * 2, 1.0, 0.004, 0.5), EV["ret"], -13)
    mx.put(M, "B_acorde_final", supersaw(hz("F2", "C3", "A3", "E4", "G4"), 1.15, (6000, 700), 0.004, 0.5, 12), EV["ret"], -19)
    # ---- brand
    mx.put(M, "B_golpe_copy", pluck_synth(NOTE["D4"], 0.6, (3500, 500), 50), GB["line1"], -7)
    mx.put(M, "B_golpe_copy", pluck_synth(NOTE["F4"], 0.6, (3500, 500), 51), GB["line2"], -7)
    mx.put(M, "B_kick", kick(46, 0.5), GB["line1"], -14); mx.put(M, "B_kick", kick(46, 0.5), GB["line2"], -14)
    mx.put(M, "B_cama_copy", supersaw(hz("D2", "A2", "F3", "C4"), GB["drop_land"] - GB["line1"] + 0.3, (400, 1200), 0.4, 0.5, 22), GB["line1"], -15)
    mx.put(M, "B_kick", kick(46, 0.6), GB["drop_land"], -9)
    for k, f in enumerate(hz("F3", "C4", "G4", "A4", "E5")):
        mx.put(M, "B_firma_acorde", pan(pluck_synth(f, 1.4, (4200, 900), 60 + k, 0.006), -0.4 + 0.2 * k), GB["drop_land"] + 0.02 * k, -14)
    mx.put(M, "B_pad_final", supersaw(hz("F2", "C3", "A3", "E4"), DUR - GB["drop_land"], (500, 1600), 0.4, 1.2, 9), GB["drop_land"], -22)


# ------------------------------------------------------------------ mastering
def limiter(x, ceiling, look=0.003, rel=0.08):
    up = signal.resample_poly(x, 4, 1, axis=1)
    pk = np.abs(up).max(axis=0)[: 4 * x.shape[1]].reshape(-1, 4).max(axis=1)
    need = np.minimum(1.0, ceiling / np.maximum(pk, 1e-9)); L = S(look)
    mn = minimum_filter1d(need, size=2 * L + 1, mode="nearest")
    a = math.exp(-1 / (rel * SR)); g = np.empty_like(mn); v = 1.0
    for i, m in enumerate(mn):
        v = m if m < v else a * v + (1 - a) * m; g[i] = v
    g = np.minimum(np.convolve(g, np.ones(L) / L, mode="same"), mn)
    return x * g[None]

def kick_times(mx):
    k = mx.tracks.get(("MUSICA", "B_kick"));
    if k is None: k = mx.tracks.get(("MUSICA", "A_kick_foley"))
    return k

def sidechain(x, key, depth, rel=0.12):
    """duck x with the envelope of key (peak follower)"""
    a = np.abs(key).max(axis=0)
    a = a / (a.max() + 1e-9)
    e = signal.lfilter([1 - math.exp(-1 / (rel * SR))], [1, -math.exp(-1 / (rel * SR))], a)
    e = np.maximum(e, minimum_filter1d(a, 1))
    return x * (1 - depth * np.clip(e * 1.6, 0, 1))[None]

def master(mx, mode):
    buses = {}
    for (bus, cue), buf in mx.tracks.items():
        buses[bus] = buses.get(bus, 0) + buf
    for b in ("MUSICA", "FOLEY", "SFX", "AMBIENTES"):
        buses.setdefault(b, np.zeros((2, N)))
    t = np.arange(N) / SR
    # music: sidechain the bass/pads to the kick in B; duck under the impact; out before the bite
    if mode == "B":
        mus_keys = [k for k in mx.tracks if k[0] == "MUSICA" and k[1] in ("B_bajo", "B_stabs", "B_pad", "B_arpegio", "B_hats_chisporroteo")]
        key = mx.tracks[("MUSICA", "B_kick")]
        side = sum(mx.tracks[k] for k in mus_keys)
        buses["MUSICA"] = buses["MUSICA"] - side + sidechain(side, key, 0.55)
    gate = np.ones(N)
    cut0, cut1 = (16.95, GB["line1"] - 0.03) if mode == "A" else (16.85, GB["line1"] - 0.03)
    gate[(t > cut0) & (t < cut1)] = 0.0
    gate = np.convolve(gate, np.ones(S(0.06)) / S(0.06), mode="same")
    buses["MUSICA"] = buses["MUSICA"] * gate[None]
    # spaces
    hall = reverb_ir(1.8 if mode == "A" else 1.4, 2.4, 10, 5500, 0.02)
    room = reverb_ir(0.4, 0.6, 9, 7000, 0.005)
    buses["MUSICA"] = convolve(buses["MUSICA"], hall, 0.22 if mode == "A" else 0.14)
    buses["SFX"] = convolve(buses["SFX"], hall, 0.18)
    buses["FOLEY"] = convolve(buses["FOLEY"], room, 0.06)
    # bus balance (the two directions)
    bal = dict(A=dict(MUSICA=-6.0, FOLEY=0.0, SFX=-1.0, AMBIENTES=0.0),
               B=dict(MUSICA=-2.0, FOLEY=0.0, SFX=-1.0, AMBIENTES=-0.5))[mode]
    for b in buses: buses[b] = buses[b] * db(bal[b])
    mix = sum(buses.values())
    mix = hp(mix, 30, 2)
    mix = peq(mix, 300, -1.5, 0.8)                                     # low-mid clean-up
    mix = peq(mix, 3200, 1.0, 0.9)                                     # presence for phone speakers
    meter = pyln.Meter(SR); target = -14.0
    g = db(target - meter.integrated_loudness(mix.T)); mix *= g
    for b in buses: buses[b] = buses[b] * g
    for _ in range(4):
        out = limiter(mix, db(-3.0))
        d = target - meter.integrated_loudness(out.T)
        if abs(d) < 0.1: break
        mix *= db(d)
        for b in buses: buses[b] = buses[b] * db(d)
    return out, buses, g, meter.integrated_loudness(out.T)


def render(mode):
    name = dict(A="A_ASMR", B="B_ELECTRONIC")[mode]
    out_dir = os.path.join(HERE, name); os.makedirs(os.path.join(out_dir, "tracks"), exist_ok=True)
    os.makedirs(os.path.join(out_dir, "stems"), exist_ok=True)
    mx = Mix(name)
    foley(mx, mode)
    (music_A if mode == "A" else music_B)(mx)
    mix, buses, g, lufs = master(mx, mode)
    for (bus, cue), buf in sorted(mx.tracks.items()):
        sf.write(os.path.join(out_dir, "tracks", f"{bus}__{cue}.flac"), (buf * g).T.astype(np.float32), SR, subtype="PCM_24")
    for b, buf in buses.items():
        sf.write(os.path.join(out_dir, "stems", f"{b}.wav"), buf.T.astype(np.float32), SR, subtype="PCM_24")
    path = os.path.join(out_dir, f"DIBURAMA_V2_{name}_MIX_48k24.wav")
    sf.write(path, mix.T.astype(np.float32), SR, subtype="PCM_24")
    print(f"{name}: {len(mx.tracks)} tracks, integrated {lufs:.2f} LUFS, sample peak {20 * np.log10(np.abs(mix).max()):.2f} dBFS")
    return mx

def cue_sheet():
    with open(os.path.join(HERE, "CUE_SHEET_V2.md"), "w") as f:
        f.write("# Cue sheet V2 — foley original del cliente (sin sustituciones sintéticas)\n\n"
                "Tiempo de máster a 30 fps. `ataque → t` = el transitorio del archivo cae exactamente en ese instante.\n\n"
                "| TC (s) | Frame @30 | Mezcla | Bus | Pista | Origen (archivo, in–out en la fuente) | Ganancia (dB) |\n|---|---|---|---|---|---|---|\n")
        for c in sorted(CUES, key=lambda c: (c["t"], c["mix"])):
            f.write(f"| {c['t']:.3f} | {int(round(c['t'] * 30))} | {c['mix']} | {c['bus']} | {c['cue']} | {c['src']} | {c['gain']:+.1f} |\n")


if __name__ == "__main__":
    which = sys.argv[1] if len(sys.argv) > 1 else "both"
    if which in ("A", "both"): render("A")
    if which in ("B", "both"): render("B")
    cue_sheet()
