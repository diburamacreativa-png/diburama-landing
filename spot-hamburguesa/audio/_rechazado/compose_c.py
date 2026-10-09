"""DIBURAMA spot — VERSIÓN C: ASMR cinematográfico + composición electrónica.

What is composed here (and exported as MIDI, so it can be produced with professional instruments):
  · MOTIVO DIBURAMA — 4 notes, "Di-bu-ra-MA": three short notes rising to a long one.
        D minor form  A4  D5  E5  F5   (5 – 1 – 2 – ♭3)   … tension, the world inside the burger
        F major form  C5  F5  G5  A5   (5 – 1 – 2 – 3)    … resolution, the brand
    3.5 s   born inside the bread: first 3 notes only, slow, from the plate (incomplete = curiosity)
    5.5 s   in the bass, under the dominant A: the motif becomes the preparation of T2
    7.5 s   hook of the motion world (full, + answer)              — Dm | B♭
    10.75 s metallic augmentation in the 3D world                  — B♭ | C (lift to F)
    13.5 s  organic, in F major, soft                               — F
    19.95 / 20.9 s  the two copy lines carry notes 1-2 and 3; the logo completes it:
    22.85 s the last note lands with the drop of the logo.
  · HARMONY  Dm – A (prep T2) ‖ Dm – B♭ – Gm/A (prep T3) ‖ B♭ – C – Csus4→C (prep T4) ‖ F – Fadd9
  · GROOVE   120 BPM, bars start at 3.5 s, 56 % swing on 16ths, velocity layers, round-robin
             foley percussion (different real hits every time), ghost notes, fills before T3.
  · Each of the four transformations is prepared musically (see arrangement comments).

What is NOT professional production here: the instruments of this render are a MAQUETA built in-house
(tuned resonators and plucked-string models excited by the client's real foley; sine sub). Every part
is a separate bus and can be replaced by external stems: drop WAVs (48 kHz, starting at t = 0 of the
spot, 120 BPM) into audio/v3/external/<part>.wav and re-run; the mockup part is then muted.
  parts: motivo, armonia, bajo, percusion, texturas

usage: python3 audio/v3/compose_c.py      → audio/v3/C/…, audio/v3/DIBURAMA_V3_C_COMPOSICION.mid
"""
import os, sys, math, json
import numpy as np, soundfile as sf
from scipy import signal
import pyloudnorm as pyln

HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, os.path.join(ROOT, "audio", "v2"))
import mix_v2 as M                                      # shared, verified DSP + foley loader
from mix_v2 import (SR, N, DUR, S, db, rng, frag, load, onset, hp, lp, bp, notch, peq, pitch, fades, norm,
                    rmsn, stereo, pan, loop_to, autom, ks, reverb_ir, NOTE, hz)

GB = M.GB; EV = M.EV
BPM = 120.0; BEAT = 0.5; S16 = 0.125; BAR0 = 3.5
def T(bar, beat=0.0, six=0.0):
    """musical position → seconds (bar 0 starts at 3.5 s; may be negative for pickups)"""
    return BAR0 + bar * 2.0 + beat * BEAT + six * S16

R = rng(2026)
MIDI = {}          # part -> list of (t, dur, midi_note, velocity)
def midi_note(name):
    names = ["C", "C#", "D", "Eb", "E", "F", "F#", "G", "Ab", "A", "Bb", "B"]
    p, o = name[:-1], int(name[-1]); return 12 * (o + 1) + names.index(p)
def log(part, t, dur, note, vel):
    MIDI.setdefault(part, []).append((t, dur, note if isinstance(note, int) else midi_note(note), int(np.clip(vel, 1, 127))))


# ------------------------------------------------------------------ buses
class Bus:
    def __init__(s): s.tr = {}
    def put(s, bus, name, sig, t, gain_db=0.0):
        k = (bus, name)
        if k not in s.tr: s.tr[k] = np.zeros((2, N))
        sig = stereo(np.asarray(sig, float)) * db(gain_db); i = S(t)
        if i < 0: sig = sig[:, -i:]; i = 0
        j = min(N, i + sig.shape[1])
        if j > i: s.tr[k][:, i:j] += sig[:, :j - i]


# ------------------------------------------------------------------ instruments (foley-excited)
def _exc(name, a, b, hpf=None):
    x = fades(frag(name, a, b), 0.0005, 0.02).mean(0)
    return hp(x, hpf) if hpf else x

EXC = {}
def excitations():
    """small real transients used to 'strike' the tuned instruments"""
    if EXC: return EXC
    o = lambda f, a, b: onset(f, a, b)
    EXC["plato"] = [_exc("14_plato.mp3", t - 0.001, t + 0.03, 1500) for t in
                    [o("14_plato.mp3", a, a + 0.25) for a in (1.75, 2.30, 4.62, 6.95, 8.80, 10.75)]]
    EXC["gel"] = [_exc("07_queso_elastico.mp3", t - 0.001, t + 0.05, 300) for t in
                  [o("07_queso_elastico.mp3", a, a + 0.3) for a in (0.35, 1.40, 3.60, 4.65, 5.45, 18.95)]]
    EXC["metal"] = [_exc("09_impacto_metalico.mp3", t - 0.001, t + 0.04, 400) for t in (0.005, 0.135, 0.28, 0.34, 0.405)]
    EXC["cubiertos"] = [_exc("15_cubiertos.mp3", t - 0.001, t + 0.03, 200) for t in
                        [o("15_cubiertos.mp3", a, a + 0.3) for a in (1.15, 1.95, 5.35, 5.85, 6.30, 8.55, 9.25, 10.45, 11.65, 13.10)]]
    return EXC

def celesta(note, vel=0.8, k=0, length=2.2):
    """plate-struck tuned string + octave partial: the 'celesta' of the motif"""
    f = NOTE[note]; e = excitations()["plato"][k % 6] * vel
    n = S(length)
    y = ks(e, f, 0.9986, 0.62, n) + 0.35 * ks(e, 2 * f, 0.9978, 0.7, n) + 0.08 * ks(e, 4.01 * f, 0.996, 0.7, n)
    y = lp(y, 7500) * np.exp(-np.arange(n) / SR / (length * 0.45))
    return norm(y) * vel

def kalimba(note, vel=0.8, k=0, length=1.4):
    f = NOTE[note]; e = excitations()["gel"][k % 6] * vel; n = S(length)
    y = ks(e, f, 0.9965, 0.3, n) + 0.2 * ks(e, 3.0 * f, 0.993, 0.4, n)
    return norm(lp(y, 6000) * np.exp(-np.arange(n) / SR / 0.45)) * vel

def bell_metal(note, vel=0.8, k=0, length=2.6):
    """metal-hit excited inharmonic resonators (bell partials)"""
    f = NOTE[note]; e = excitations()["metal"][k % 5] * vel; n = S(length); x = np.zeros(n); x[:len(e)] = e
    y = 0
    for ratio, q, a in ((1.0, 900, 1.0), (2.0, 700, 0.5), (2.76, 600, 0.45), (5.40, 400, 0.25), (8.93, 300, 0.12)):
        fr = f * ratio
        if fr > 16000: continue
        w = 2 * math.pi * fr / SR; al = math.sin(w) / (2 * q)
        y = y + a * signal.lfilter([al, 0, -al], [1 + al, -2 * math.cos(w), 1 - al], x)
    return norm(y * np.exp(-np.arange(n) / SR / (length * 0.4))) * vel

def pluck_bass(note, dur, vel=0.85, k=0):
    """cutlery-thump plucked string (picked bass) + clean sine sub on the same note"""
    f = NOTE[note]; n = S(dur + 0.15); e = lp(excitations()["cubiertos"][k % 10], 1500) * vel
    y = ks(e, f, 0.9975, 0.25, n)
    t = np.arange(n) / SR
    sub = np.sin(2 * np.pi * f * t) * np.clip(t / 0.006, 0, 1)
    env = np.clip((dur + 0.15 - t) / 0.08, 0, 1)
    out = (0.7 * norm(lp(y, 2200)) + 0.55 * sub) * env * vel
    return np.tanh(1.3 * out) / np.tanh(1.3)

def vapor_strings(notes, dur, att=0.6, rel=0.8, seed=0, src=("05_vapor.mp3", 7.0, 8.8), bright=4500):
    """sustained resonant chord: the real steam/sizzle continuously drives tuned strings (bowed-like)"""
    n = S(dur); noise = loop_to(frag(*src), n).mean(0); noise = hp(noise, 180)
    noise = noise / (np.sqrt(np.mean(noise ** 2)) + 1e-9) * 0.02
    out = np.zeros((2, n))
    for i, nt in enumerate(notes):
        f = NOTE[nt]
        for c, cents in ((0, -3), (1, +4)):
            fc = f * 2 ** (cents / 1200)
            out[c] += ks(np.roll(noise, 997 * i + 31 * c), fc, 0.9992, 0.5, n)
    t = np.arange(n) / SR
    e = np.clip(t / att, 0, 1) ** 1.5 * np.clip((dur - t) / rel, 0, 1)
    out = lp(out, bright) * e
    return norm(out)

def sub_note(note, dur, vel=0.8):
    f = NOTE[note]; n = S(dur); t = np.arange(n) / SR
    y = np.sin(2 * np.pi * f * t) * np.clip(t / 0.01, 0, 1) * np.clip((dur - t) / 0.12, 0, 1)
    return y * vel


# ------------------------------------------------------------------ percussion (round-robin, swing, humanised)
PERC = {}
def perc_pools():
    if PERC: return PERC
    kicks = []
    for f, a, b, cut in (("16_impacto_humedo.mp3", 0.30, 0.50, 260), ("16_impacto_humedo.mp3", 0.30, 0.50, 180),
                         ("14_plato.mp3", 1.80, 1.95, 220), ("14_plato.mp3", 7.00, 7.10, 240), ("14_plato.mp3", 2.35, 2.50, 200)):
        on = onset(f, a, b); x = fades(frag(f, on - 0.002, on + 0.32), 0.0008, 0.12).mean(0)
        x = norm(lp(x, cut, 4))
        t = np.arange(S(0.32)) / SR
        body = np.sin(2 * np.pi * np.cumsum(48 + 70 * np.exp(-t / 0.025)) / SR) * np.exp(-t / 0.16)   # tuned body under the real thud
        kicks.append(norm(0.75 * x[:len(body)] + 0.45 * body))
    snares = []
    for a in (1.15, 1.95, 5.35, 5.85, 6.30, 8.55, 9.25, 10.45, 11.65, 13.10):
        on = onset("15_cubiertos.mp3", a, a + 0.3)
        x = fades(frag("15_cubiertos.mp3", on - 0.001, on + 0.28), 0.0005, 0.1)
        snares.append(norm(peq(hp(x, 220), 2800, 3, 1.0)))
    gels = []
    for a in (0.35, 1.40, 3.60, 4.65, 5.45, 18.95, 20.0, 21.15):
        on = onset("07_queso_elastico.mp3", a, a + 0.3)
        gels.append(norm(hp(fades(frag("07_queso_elastico.mp3", on - 0.001, on + 0.18), 0.0005, 0.06), 300)))
    ticks = [norm(hp(fades(frag("08_engranajes.mp3", a, a + 0.06), 0.0005, 0.03), 2500)) for a in np.linspace(2.9, 9.4, 12)]
    PERC.update(kick=kicks, snare=snares, gel=gels, tick=ticks)
    return PERC

def swing(t, amount=0.56):
    """delay off-beat 16ths: position within the beat decides"""
    k = round((t - BAR0) / S16)
    return t + ((amount - 0.5) * 2 * S16 if k % 2 == 1 else 0.0)

def hit(bus, pool, t, vel, gain_db, part, note, pan_=0.0, jitter=0.004, sw=True):
    p = perc_pools()[pool]; x = p[R.integers(len(p))]                       # round-robin (random, never fixed)
    tt = (swing(t) if sw else t) + (R.normal(0, jitter) if jitter else 0.0)
    v = np.clip(vel * (1 + R.normal(0, 0.06)), 0.05, 1.0)
    y = lp(x, 3000 + 14000 * v) * v                                           # softer hits are darker
    bus.put("MUSICA", f"perc_{pool}", pan(y, pan_), tt, gain_db)
    log("percusion", tt, 0.1, note, v * 127)

def sizzle_hats(bus, t0, t1, density, gain_db, accent=(1.0, 0.35, 0.7, 0.4), dec=(0.022, 0.055), name="hats_chisporroteo"):
    """the real sizzle, gated on swung 16ths; density(t) 0…1 morphs continuous sizzle → rhythm"""
    n0, n1 = S(t0), S(t1); src = hp(loop_to(frag("02_sizzle_base.mp3", 20.0, 44.0), n1 - n0), 4800, 2)
    t = np.arange(n0, n1) / SR; g = np.zeros(len(t))
    k0 = int(math.floor((t0 - BAR0) / S16)); k1 = int(math.ceil((t1 - BAR0) / S16))
    for k in range(k0, k1 + 1):
        st = swing(BAR0 + k * S16) + R.normal(0, 0.003)
        a = accent[k % 4] * (0.85 + 0.3 * R.random())
        d = dec[1] if k % 4 == 2 else dec[0]
        i0 = int((st - t0) * SR)
        if i0 >= len(t) or i0 + S(0.25) < 0: continue
        seg = np.arange(max(i0, 0), min(len(t), i0 + S(0.25)))
        g[seg] = np.maximum(g[seg], a * np.exp(-(seg - i0) / SR / d))
        log("percusion", st, 0.05, 42, a * 110)
    dens = np.array([density(x) for x in t[::480]]); dens = np.interp(np.arange(len(t)), np.arange(len(dens)) * 480, dens)
    env = (1 - dens) * 0.55 + dens * g                                         # continuous sizzle → gated groove
    bus.put("MUSICA", name, src * env, t0, gain_db)


def tame(x, crest_db=12.0):
    """texture beds: hold isolated crackle peaks to RMS + crest_db (inaudible as compression, frees headroom)"""
    r = np.sqrt(np.mean(x ** 2)) + 1e-12
    return M.limiter(stereo(x), r * db(crest_db), look=0.002, rel=0.03)

def body(x, thr_below_peak=16.0, ratio=3.0, att=0.004, rel=0.07):
    """transient-friendly compression: slow-ish attack lets the first crack through, lifts the texture"""
    pk = np.abs(x).max() + 1e-12
    y, _ = compressor_(stereo(x), 20 * np.log10(pk) - thr_below_peak, ratio, att, rel)
    return norm(y)

def compressor_(x, thr_db, ratio, att, rel):
    e = np.abs(x).max(axis=0)
    a1, r1 = math.exp(-1 / (att * SR)), math.exp(-1 / (rel * SR))
    env = signal.lfilter([1 - a1], [1, -a1], e)                      # attack-smoothed detector
    env = np.maximum(env, signal.lfilter([1 - r1], [1, -r1], e) * 0)  # (release handled by smoothing below)
    env = signal.filtfilt([1 - r1], [1, -r1], env) if False else env
    lvl = 20 * np.log10(env + 1e-9)
    gr = np.minimum(0, (thr_db - lvl) * (1 - 1 / ratio))
    # release: gain recovers with time constant rel
    g = np.empty_like(gr); v = 0.0
    for i, q in enumerate(gr):
        v = q if q < v else r1 * v + (1 - r1) * q; g[i] = v
    return x * db(g)[None], g

# ------------------------------------------------------------------ FOLEY (revised one by one)
def trmsn(x, crest=12.0):
    """RMS-normalised texture with its isolated peaks held to RMS + crest (high-crest sources: fire, cheese, steam)"""
    return tame(rmsn(x), crest)

def foley_c(b):
    F, X, AM = "FOLEY", "SFX", "AMBIENTES"
    def po(bus, cue, name, a, bb, at, align, gain, proc=None, fi=0.002, fo=0.05):
        x = fades(frag(name, a, bb), fi, fo)
        if proc: x = proc(x)
        b.put(bus, cue, norm(x), at - (align - a), gain)
    # 0–3.4: ASMR protagonist (louder, closer, wider than A)
    bed = trmsn(loop_to(frag("02_sizzle_base.mp3", 9.0, 21.0), S(4.6)))
    bed = bed * autom(bed.shape[1], [(0, -5), (0.95, -4.5), (1.0, -2), (1.6, -3.5), (3.2, -5), (4.0, -8), (4.6, -30)])
    b.put(F, "sizzle_base", M.widen(fades(tame(bed, 11), 0.004, 0.5), 1.25), 0.0, 0)
    det = trmsn(fades(frag("03_sizzle_detalle.mp3", 12.0, 15.4), 0.004, 0.4))   # close-mic detail layer, panned
    b.put(F, "sizzle_detalle", pan(tame(det, 11), 0.35), 0.0, -9)
    fire = norm(loop_to(frag("04_fuego.mp3", 0.3, 7.9), S(3.9)))           # peak-based: its crackles have 40 dB crest
    b.put(AM, "fuego", fades(peq(fire, 140, 3, 0.8), 0.004, 0.6), 0.0, -9)
    po(X, "caida_carne", "10_whoosh.mp3", 0.15, 1.2, 0.93, 0.522, -18, proc=lambda x: lp(x, 2400), fo=0.25)
    # IMPACT — reviewed: no saturation, no 60 Hz boost (useless on phones); body = 80–180 Hz band + harmonics
    on16 = onset("16_impacto_humedo.mp3", 0.30, 0.50)
    po(F, "impacto_carne_golpe", "16_impacto_humedo.mp3", 0.385, 1.45, EV["impact"], on16, -12.0, fo=0.35)
    po(F, "impacto_carne_cuerpo", "16_impacto_humedo.mp3", 0.385, 1.0, EV["impact"], on16, -16,
       proc=lambda x: peq(bp(x, 70, 190, 2), 120, 3, 1.0), fo=0.25)
    po(F, "grasa_estalla", "03_sizzle_detalle.mp3", 3.80, 6.40, EV["impact"] + 0.03, 3.892, -13, fo=0.6)
    carne = trmsn(fades(lp(frag("01_carne_parrilla.mp3", 15.10, 18.0), 9500), 0.006, 0.9))
    carne = carne * autom(carne.shape[1], [(0, 0), (0.6, -1), (2.9, -7)])
    b.put(F, "carne_parrilla", tame(carne, 12), EV["impact"] + 0.01, -7)
    st = trmsn(fades(hp(frag("05_vapor.mp3", 7.0, 8.9), 700), 0.25, 0.7))
    b.put(F, "vapor_hero", pan(st, -0.2), 1.85, -6)
    # T1
    po(X, "t1_rush", "10_whoosh.mp3", 0.0, 1.6, EV["t1"], 0.522, -8, fo=0.6)
    po(F, "t1_pan_textura", "07_queso_elastico.mp3", 0.40, 1.30, EV["t1"] + 0.02, 0.582, -12, proc=lambda x: hp(x, 250), fo=0.3)
    # T2 (riser = real steam; reversed real whoosh as the suction)
    riser = trmsn(fades(frag("05_vapor.mp3", 6.05, 7.40), 0.05, 0.03))
    b.put(X, "t2_succion_vapor", riser, EV["t2"] - 0.15 - riser.shape[1] / SR, -8)        # ends 150 ms before the drop: a breath of silence
    rw = norm(fades(frag("10_whoosh.mp3", 0.05, 0.56)[:, ::-1], 0.1, 0.01))
    b.put(X, "t2_succion_inversa", rw, EV["t2"] - rw.shape[1] / SR, -12)
    # CHEESE — reviewed: wet squelch tamed (HP 150, -4 dB at 7 kHz), placed only where the cheese stretches
    ch = trmsn(fades(peq(hp(frag("06_queso_textura.mp3", 5.4, 7.7), 150), 7000, -4, 1.2), 0.04, 0.5))
    b.put(F, "queso_textura", ch, EV["t2"] + 0.05, -9)
    for a, al, at, g in ((0.40, 0.582, 7.62, -12), (5.40, 5.628, 8.55, -15)):
        po(F, "queso_elastico", "07_queso_elastico.mp3", a, a + 0.7, at, al, g, proc=lambda x: peq(hp(x, 150), 7000, -3, 1.2), fo=0.3)
    # T3 — METAL reviewed: the source has 8 hits in 1.3 s (machine-gun); use ONLY the first hit + its own ring
    po(X, "t3_vortice", "11_transicion.mp3", 0.0, 1.6, EV["t3"], 0.795, -14, fo=0.6)
    on9 = onset("09_impacto_metalico.mp3", 0.0, 0.08)
    hitm = fades(frag("09_impacto_metalico.mp3", 0.0, 0.125), 0.0005, 0.03)
    ring = bell_metal("D3", 0.9, 0, 1.6); ring = np.vstack([ring, ring])
    metal = np.zeros((2, S(1.6))); metal[:, :hitm.shape[1]] += norm(hitm); metal += 0.35 * ring
    b.put(X, "t3_impacto_metal", fades(metal, 0.0005, 0.5), EV["lock"] - on9, -14)
    po(X, "t3_impacto_metal_sub", "09_impacto_metalico.mp3", 0.0, 0.3, EV["lock"], on9, -14,
       proc=lambda x: lp(pitch(x, 0.5), 220, 4), fo=0.2)
    gears = trmsn(fades(frag("08_engranajes.mp3", 3.0, 6.05), 0.06, 0.6))
    b.put(F, "engranajes", peq(gears, 250, -3, 0.7), EV["lock"] + 0.02, -13)
    # T4 metal → air → vegetal
    m = frag("08_engranajes.mp3", 6.0, 7.4); parts = np.array_split(m, 7, axis=1)
    slow = trmsn(fades(np.concatenate([lp(pitch(p, 1.0 - 0.07 * i), 6000 - 700 * i) for i, p in enumerate(parts)], axis=1), 0.03, 0.35))
    b.put(X, "t4_metal_se_ablanda", slow, EV["t4"] - 0.62, -9)
    air = trmsn(fades(hp(frag("05_vapor.mp3", 9.0, 10.3), 1200), 0.35, 0.5))
    b.put(X, "t4_aire", air, EV["t4"] - 0.35, -10)
    veg = trmsn(fades(hp(frag("06_queso_textura.mp3", 9.0, 11.6), 1800), 0.15, 0.6))
    b.put(F, "t4_textura_vegetal", pan(veg, 0.25), EV["t4"] - 0.05, -9)
    # 15.75 return: the ASMR takes the foreground again
    fire2 = norm(fades(frag("04_fuego.mp3", 3.9, 5.6), 0.15, 0.4))
    b.put(AM, "fuego_regreso", fire2, 15.62, -13)
    sz = trmsn(fades(frag("02_sizzle_base.mp3", 30.0, 31.6), 0.15, 0.5))
    b.put(F, "sizzle_regreso", tame(sz, 11) * autom(sz.shape[1], [(0, 0), (0.9, -2), (1.6, -14)]), 15.62, -7)
    st2 = trmsn(fades(hp(frag("05_vapor.mp3", 9.6, 10.8), 900), 0.3, 0.5))
    b.put(F, "vapor_regreso", st2, 15.85, -11)
    # BITE — reviewed: natural, no saturation; teeth contact (12) → crack (13) → crumble (13) → a little weight
    on12 = onset("12_mordisco.mp3", 0.66, 0.80)
    po(F, "mordisco_pan", "12_mordisco.mp3", 0.55, 1.62, EV["bite"], on12, 4.0,
       proc=lambda x: body(peq(peq(x, 200, 2, 0.9), 4200, 2, 1.2), 22, 3.5), fi=0.004, fo=0.35)
    on13 = onset("13_crunch_asmr.mp3", 24.45, 24.55)
    po(F, "mordisco_crack", "13_crunch_asmr.mp3", 24.40, 24.98, EV["bite"], on13, 0.0,
       proc=lambda x: body(notch(notch(x, 1000.0, 6), 2000.0, 6), 22, 3.5), fo=0.25)
    on13b = onset("13_crunch_asmr.mp3", 11.30, 11.42)
    po(F, "mordisco_desmenuza", "13_crunch_asmr.mp3", 11.30, 11.62, EV["bite"] + 0.045, on13b, 2,
       proc=lambda x: body(notch(hp(x, 600), 1000.0, 6), 16, 2.5), fo=0.12)
    po(F, "mordisco_peso", "16_impacto_humedo.mp3", 0.385, 0.8, EV["bite"], on16, -8, proc=lambda x: bp(x, 80, 200, 2), fo=0.2)
    # plate
    room = trmsn(loop_to(frag("14_plato.mp3", 0.1, 1.8), S(1.45)))
    b.put(AM, "tono_sala", fades(lp(room, 6000), 0.06, 0.35), EV["plate"], -30)
    for cue, a, at, g in (("miga_plato_1", 4.95, EV["crumb1"], -24), ("miga_plato_2", 6.95, EV["crumb2"], -20)):
        on = onset("14_plato.mp3", a, a + 0.2)
        po(F, cue, "14_plato.mp3", on - 0.02, on + 0.3, at, on, g, proc=lambda x: hp(x, 2000), fo=0.15)
    # brand drop + loop to the grill (end level = start level)
    on7 = onset("07_queso_elastico.mp3", 5.55, 5.70)
    po(X, "firma_gota", "07_queso_elastico.mp3", 5.55, 6.0, GB["drop_land"], on7, -10, proc=lambda x: hp(pitch(x, 1.6), 300), fo=0.12)
    tail = fades(trmsn(loop_to(frag("02_sizzle_base.mp3", 9.0, 12.0), S(1.2))), 1.0, 0.0) * db(-4)
    b.put(F, "sizzle_bucle", M.widen(tame(tail, 11), 1.25), DUR - 1.2, 0)
    firet = fades(norm(frag("04_fuego.mp3", 0.3, 1.5)), 1.0, 0.0)
    b.put(AM, "fuego_bucle", firet, DUR - 1.2, -9)


# ------------------------------------------------------------------ COMPOSITION
MOTIF_Dm = ["A4", "D5", "E5", "F5"]
MOTIF_F = ["C5", "F5", "G5", "A5"]
RHY = [0.0, 0.5, 1.0, 1.5]                               # in 8ths: short-short-short-LONG
def motif(b, inst, notes, t0, step, gain_db, part="motivo", vel=(0.75, 0.7, 0.8, 0.95), last_len=2.0, panv=0.0, upto=4):
    for i in range(upto):
        tt = t0 + RHY[i] * step * 2; ln = last_len if i == 3 else step * 2.5
        y = inst(notes[i], vel[i], i, ln + 0.6)
        b.put("MUSICA", part, pan(y, panv + 0.12 * (i - 1.5)), tt, gain_db)
        log("motivo", tt, ln, notes[i], vel[i] * 127)

def chord(b, notes, t0, dur, gain_db, name="armonia", **kw):
    b.put("MUSICA", name, vapor_strings(notes, dur, **kw), t0, gain_db)
    for nt in notes: log("armonia", t0, dur, nt, 70)

def bass(b, line, gain_db):
    for k, (tt, nt, d, v) in enumerate(line):
        b.put("MUSICA", "bajo", pluck_bass(nt, d, v, k), swing(tt), gain_db)
        log("bajo", swing(tt), d, nt, v * 127)

def compose(b):
    # ---------------- I · 3.43–7.5  inside the bread: the motif is born, the sizzle becomes rhythm
    motif(b, celesta, MOTIF_Dm, T(0, 0) + 0.02, 0.5, -15, upto=3, vel=(0.55, 0.5, 0.6, 0.0))      # incomplete: A D E …
    chord(b, ["D3", "A3", "F4"], T(0), 2.2, -18, att=1.2, rel=0.6, seed=1)
    sizzle_hats(b, 3.6, 7.35, lambda t: np.clip((t - 4.2) / 3.0, 0, 1) ** 1.5, -8, accent=(0.9, 0.2, 0.55, 0.25))
    hit(b, "kick", T(1, 0), 0.55, -9, "musica", 36, sw=False)                                   # film world opens (5.5)
    hit(b, "kick", T(1, 2), 0.45, -11, "musica", 36, sw=False)
    # prep T2: dominant A, motif in the bass, steam riser (foley) — then a breath of silence and the drop
    chord(b, ["A2", "E3", "C#4", "E4"], T(1, 0), 2.0, -16, att=0.8, rel=0.15, seed=2, src=("02_sizzle_base.mp3", 30, 34))
    bass(b, [(T(1, 0), "A1", 0.45, 0.6), (T(1, 1), "D2", 0.45, 0.65), (T(1, 2), "E2", 0.45, 0.7), (T(1, 3), "F2", 0.3, 0.8)], -10)
    for k, s16 in enumerate((0, 2, 3)):
        hit(b, "gel", T(1, 3, s16), 0.35 + 0.15 * k, -16, "musica", 60, pan_=0.3 * (k - 1))
    # ---------------- II · 7.5–10.75  motion world: the hook, real groove, real harmony
    bars = [(T(2), ["D3", "F3", "A3", "C4"], "D2"), (T(3), ["Bb2", "D3", "F3", "A3"], "Bb1")]
    for t0, ch, root in bars:
        chord(b, ch, t0, 2.05, -15, att=0.04, rel=0.25, seed=int(t0 * 10), src=("02_sizzle_base.mp3", 40, 44), bright=6000)
    # bass line: syncopated, follows the motif rhythm
    line = []
    for bar, root, fifth, oct_ in ((2, "D2", "A1", "D3"), (3, "Bb1", "F1", "Bb2")):
        for beat, six, nt, d, v in ((0, 0, root, 0.32, 0.95), (0, 3, root, 0.12, 0.55), (1, 2, fifth, 0.2, 0.7),
                                    (2, 0, root, 0.3, 0.85), (2, 3, oct_, 0.12, 0.6), (3, 0, fifth, 0.2, 0.75), (3, 2, root, 0.2, 0.7)):
            line.append((T(bar, beat, six), nt, d, v))
    bass(b, line, -8)
    # drums: kick on 1 and the "and of 2", snare on 3 (half-time feel with 16th pushes), ghosts, round-robin
    for bar in (2, 3):
        for beat, six, v in ((0, 0, 1.0), (1, 2, 0.75), (2, 3, 0.5), (3, 1, 0.7)):
            hit(b, "kick", T(bar, beat, six), v, -6, "musica", 36)
        for beat, six, v in ((1, 0, 0.95), (3, 0, 1.0)):
            hit(b, "snare", T(bar, beat, six), v, -8, "musica", 38, pan_=0.05)
        for six in (3, 6, 11, 14):                                                          # ghosts
            hit(b, "snare", T(bar, 0, six), 0.28 + 0.1 * R.random(), -14, "musica", 37, pan_=-0.2)
        for six in (1, 5, 9, 13):
            hit(b, "gel", T(bar, 0, six), 0.4 + 0.25 * R.random(), -15, "musica", 62, pan_=0.35 * math.sin(six))
    sizzle_hats(b, T(2), T(4) - 0.25, lambda t: 1.0, -6)
    motif(b, celesta, MOTIF_Dm, T(2, 0), 0.5, -9, last_len=1.4)                                 # THE HOOK
    for i, (nt, bt) in enumerate((("C5", 2.5), ("A4", 3.0), ("G4", 3.5))):                     # answer
        b.put("MUSICA", "motivo", celesta(nt, 0.55, i + 2, 1.2), T(2, bt), -13); log("motivo", T(2, bt), 0.4, nt, 70)
    motif(b, celesta, ["Bb4", "D5", "F5", "G5"], T(3, 0), 0.5, -10, last_len=1.0)              # sequence over B♭
    # prep T3 (10.0–10.75): harmony to the dominant, cutlery roll accelerating, a frame of silence, HIT
    chord(b, ["G2", "Bb2", "D3", "E3", "A3"], T(3, 2), 1.08, -14, att=0.15, rel=0.05, seed=9, src=("05_vapor.mp3", 6.05, 7.4))
    roll = [T(3, 2) + x for x in np.cumsum([0.125, 0.11, 0.095, 0.08, 0.07, 0.06, 0.05, 0.045, 0.04])]
    for k, tt in enumerate(roll):
        if tt < EV["t3"] - 0.02: hit(b, "snare", tt, 0.35 + 0.07 * k, -11, "musica", 38, sw=False, jitter=0.002)
    # ---------------- III · 10.75–13.5  3D world: metal motif, augmented; B♭ → C, lift into F
    hit(b, "kick", EV["lock"], 1.0, -11, "musica", 36, sw=False)
    bass(b, [(EV["lock"], "Bb1", 0.7, 1.0)], -12)
    chord(b, ["Bb2", "F3", "D4", "A4"], EV["lock"], 1.8, -14, att=0.02, rel=0.3, seed=11, src=("08_engranajes.mp3", 3, 6), bright=5000)
    chord(b, ["C3", "G3", "E4", "G4"], T(4, 2), 1.3, -14, att=0.05, rel=0.2, seed=12, src=("08_engranajes.mp3", 6, 9), bright=5000)
    motif(b, bell_metal, ["F4", "Bb4", "C5", "D5"], T(3, 3, 2) + 0.25, 0.75, -13, last_len=1.6, panv=-0.1)   # augmented, starts on the lock
    line3 = [(T(4, 0), "Bb1", 0.3, 0.9), (T(4, 0, 3), "Bb1", 0.12, 0.55), (T(4, 1, 2), "F1", 0.2, 0.7),
             (T(4, 2), "C2", 0.3, 0.9), (T(4, 2, 3), "C2", 0.12, 0.55), (T(4, 3, 2), "G1", 0.2, 0.7)]
    bass(b, line3, -8)
    for beat, six, v in ((0, 0, 1.0), (0, 3, 0.55), (1, 2, 0.8), (2, 0, 0.95), (2, 3, 0.6)):
        hit(b, "kick", T(4, beat, six), v, -6, "musica", 36)
    for beat in (1, 3):
        hit(b, "snare", T(4, beat), 0.9, -8, "musica", 38)
    for k in range(16):
        hit(b, "tick", T(4, 0, k), (0.85 if k % 4 == 2 else 0.45) * (0.8 + 0.4 * R.random()), -13, "musica", 42, pan_=0.55 * (1 if k % 2 else -1))
    # prep T4 (13.0–13.5): drums fall away, Csus4 → C lifts, the motif's last note hangs
    chord(b, ["C3", "F3", "G3", "C4", "F4"], T(4, 3) + 0.02, 0.55, -13, att=0.25, rel=0.02, seed=13, src=("05_vapor.mp3", 9, 10.3))
    # ---------------- IV · 13.5–15.6  organic world: F major, the motif softens (kalimba of gel)
    chord(b, ["F2", "C3", "A3", "E4"], T(5), 2.25, -15, att=0.12, rel=0.5, seed=14, src=("06_queso_textura.mp3", 9.0, 11.6), bright=5200)
    motif(b, kalimba, MOTIF_F, T(5, 0, 1), 0.5, -11, last_len=1.2, panv=0.1)
    for i, (nt, bt) in enumerate((("E5", 2.5), ("C5", 3.0), ("A4", 3.5))):
        b.put("MUSICA", "motivo", kalimba(nt, 0.5, i, 1.0), T(5, bt), -15); log("motivo", T(5, bt), 0.4, nt, 64)
    bass(b, [(T(5, 0), "F1", 0.9, 0.7), (T(5, 2), "C2", 0.9, 0.6)], -11)
    for six in (2, 6, 10, 14):
        hit(b, "gel", T(5, 0, six), 0.3 + 0.2 * R.random(), -17, "musica", 62, pan_=0.4 * math.cos(six))
    # ---------------- V · 15.75 return: resolution, then the music leaves the burger alone
    hit(b, "kick", EV["ret"], 0.7, -9, "musica", 36, sw=False)
    chord(b, ["F2", "C3", "G3", "A3", "E4"], EV["ret"], 1.05, -14, att=0.01, rel=0.7, seed=15)
    bass(b, [(EV["ret"], "F1", 0.9, 0.7)], -11)
    # ---------------- VI · brand: the motif is completed by the copy and the logo
    b.put("MUSICA", "motivo", celesta("C5", 0.7, 0, 1.6), GB["line1"], -10); log("motivo", GB["line1"], 0.4, "C5", 90)
    b.put("MUSICA", "motivo", celesta("F5", 0.7, 1, 1.8), GB["line1"] + 0.25, -10); log("motivo", GB["line1"] + 0.25, 0.6, "F5", 90)
    b.put("MUSICA", "motivo", celesta("G5", 0.7, 2, 1.8), GB["line2"], -10); log("motivo", GB["line2"], 0.6, "G5", 90)
    chord(b, ["D3", "A3", "F4"], GB["line1"], GB["line2"] + 0.9 - GB["line1"], -20, att=0.5, rel=0.6, seed=16)
    chord(b, ["Bb2", "F3", "D4"], GB["line2"], GB["logo"] - GB["line2"] + 0.2, -20, att=0.3, rel=0.4, seed=17)
    motif(b, celesta, MOTIF_F, GB["drop_land"] - 0.75, 0.25, -7, vel=(0.6, 0.65, 0.7, 1.0), last_len=2.2)   # A lands on the drop
    chord(b, ["F2", "C3", "G3", "A3", "E4"], GB["drop_land"], DUR - GB["drop_land"], -15, att=0.05, rel=1.2, seed=18)
    bass(b, [(GB["drop_land"], "F1", 1.6, 0.75)], -10)
    hit(b, "kick", GB["drop_land"], 0.75, -10, "musica", 36, sw=False)


# ------------------------------------------------------------------ external stems hook
EXTERNAL = os.path.join(HERE, "external")
PART_OF = dict(motivo="motivo", armonia="armonia", bajo="bajo")
def part_of(name):
    if name.startswith("perc_") or name.startswith("hats"): return "percusion"
    return PART_OF.get(name, "texturas")

def apply_external(b):
    used = []
    for part in ("motivo", "armonia", "bajo", "percusion", "texturas"):
        p = os.path.join(EXTERNAL, part + ".wav")
        if not os.path.exists(p): continue
        x, sr = sf.read(p, always_2d=True)
        if sr != SR: x = signal.resample_poly(x, SR, sr, axis=0)
        for k in [k for k in b.tr if k[0] == "MUSICA" and part_of(k[1]) == part]: del b.tr[k]
        buf = np.zeros((2, N)); n = min(N, x.shape[0]); buf[:, :n] = x[:n].T
        b.tr[("MUSICA", f"EXTERNAL_{part}")] = buf; used.append(part)
    return used


# ------------------------------------------------------------------ mixing / mastering (transient-friendly)
def compressor(x, thr_db, ratio, att, rel, makeup=0.0):
    e = np.abs(x).max(axis=0)
    a1, r1 = math.exp(-1 / (att * SR)), math.exp(-1 / (rel * SR))
    env = np.empty_like(e); v = 0.0
    for i, s in enumerate(e):
        v = a1 * v + (1 - a1) * s if s > v else r1 * v + (1 - r1) * s; env[i] = v
    lvl = 20 * np.log10(env + 1e-9)
    gr = np.minimum(0, (thr_db - lvl) * (1 - 1 / ratio))
    return x * db(gr + makeup)[None], gr

def master(b):
    buses = {}
    for (bus, name), buf in b.tr.items(): buses[bus] = buses.get(bus, 0) + buf
    for k in ("MUSICA", "FOLEY", "SFX", "AMBIENTES"): buses.setdefault(k, np.zeros((2, N)))
    t = np.arange(N) / SR
    # the music leaves room for the physical hits (not a fader dip: a carved window)
    duck = np.ones(N)
    for t0, depth, rel in ((EV["impact"], 0.0, 0.0), (EV["lock"], 0.35, 0.18)):
        if depth: duck *= 1 - depth * np.exp(-np.maximum(t - t0, 0) / rel) * (t >= t0 - 0.005)
    gate = np.ones(N); gate[(t > 16.75) & (t < GB["line1"] - 0.03)] = 0.0             # silence before the bite
    gate = np.convolve(gate, np.ones(S(0.25)) / S(0.25), mode="same")
    buses["MUSICA"] = buses["MUSICA"] * (duck * gate)[None]
    # glue on the music only (gentle, slow attack keeps the transients)
    buses["MUSICA"], _ = compressor(buses["MUSICA"], -18, 2.0, 0.025, 0.2)
    hall = reverb_ir(1.9, 2.6, 10, 5500, 0.022); plate = reverb_ir(1.1, 1.6, 12, 8000, 0.01); room = reverb_ir(0.35, 0.5, 9, 7000, 0.004)
    buses["MUSICA"] = M.convolve(buses["MUSICA"], hall, 0.2)
    buses["SFX"] = M.convolve(buses["SFX"], plate, 0.16)
    buses["FOLEY"] = M.convolve(buses["FOLEY"], room, 0.05)
    bal = dict(MUSICA=-7.5, FOLEY=0.0, SFX=-1.5, AMBIENTES=-0.5)
    for k in buses: buses[k] = buses[k] * db(bal[k])
    # The bite gets its own fader. The rest of the film is mastered to TARGET; the bite is placed as high as
    # possible WITHOUT being squashed (limiter ≤ 3 dB on it, > 1 dB for ≤ 30 ms: only the tips of the cracks).
    bite_keys = [k for k in b.tr if k[1].startswith("mordisco")]
    bite_sig = M.convolve(sum(b.tr[k] for k in bite_keys), room, 0.05) * db(bal["FOLEY"])   # same path as FOLEY (linear)
    eq = lambda x: peq(peq(hp(x, 28, 2), 320, -1.2, 0.8), 3300, 0.8, 0.9)
    full = eq(sum(buses.values())); bite_eq = eq(bite_sig); rest = full - bite_eq
    # spike clipper on the bite only: 4 ms release, it shaves the needle-tips of the cracks and nothing else
    pk = np.abs(bite_eq).max()
    bite_cl = M.limiter(bite_eq, pk * db(-5.0), look=0.0005, rel=0.004)
    lv = np.abs(bite_eq).max(axis=0) > pk * db(-40)
    rr = np.abs(bite_cl).max(axis=0)[lv] / np.abs(bite_eq).max(axis=0)[lv]
    print(f"   bite spike clipper: >1 dB for {1000 * np.sum(rr < db(-1)) / SR:.1f} ms, >3 dB for {1000 * np.sum(rr < db(-3)) / SR:.1f} ms (bite ≈ 500 ms)")
    bite_sig = bite_sig * 0 + (bite_cl - bite_eq) * 0 + bite_sig      # (stems keep the unclipped bite; clip lives in the master)
    rest_bite = bite_cl
    meter = pyln.Meter(SR); TARGET = -16.0
    bite = slice(S(EV["bite"] - 0.02), S(EV["bite"] + 0.5))
    best = None
    for trim in np.arange(0.0, -12.01, -0.5):
        mix = rest + rest_bite * db(trim)
        g_ = db(TARGET - meter.integrated_loudness(mix.T))
        o_ = M.limiter(mix * g_, db(-1.5))
        r_ = np.abs(o_).max(axis=0) / np.maximum(np.abs(mix * g_).max(axis=0), 1e-9)
        live = np.abs(mix * g_).max(axis=0) > 0.05
        grmax = -20 * np.log10(max(r_[live].min(), 1e-9))
        lb = live[bite]
        grbite = -20 * np.log10(max(r_[bite][lb].min(), 1e-9)) if lb.any() else 0.0
        bite_ms = 1000 * np.sum(r_[bite][lb] < db(-1.0)) / SR
        spike_ms = 1000 * np.sum(r_[bite][lb] < db(-3.0)) / SR
        if grbite <= 2.0 and bite_ms <= 15:
            best = (trim, g_, o_, grmax, bite_ms, grbite); break
    trim, gain, out, gr, bite_ms, grbite = best
    buses["FOLEY"] = buses["FOLEY"] + bite_sig * (db(trim) - 1)          # stems keep summing to the mix
    for k in buses: buses[k] = buses[k] * gain
    for k in bite_keys: b.tr[k] = b.tr[k] * db(trim)
    r_ = np.abs(out).max(axis=0) / np.maximum(np.abs((rest + rest_bite * db(trim)) * gain).max(axis=0), 1e-9)
    spike_ms = 1000 * np.sum(r_[bite] < db(-3.0)) / SR
    print(f"   bite trim {trim:+.1f} dB | limiter max {gr:.2f} dB overall; on the bite max {grbite:.2f} dB, >1 dB for {bite_ms:.1f} ms, >3 dB for {spike_ms:.1f} ms")
    gr = -gr
    return out, buses, gain, meter.integrated_loudness(out.T), gr

# ------------------------------------------------------------------ MIDI export
def write_midi(path):
    import mido
    mf = mido.MidiFile(ticks_per_beat=480); tpb = 480
    sec2tick = lambda s: int(round(s / BEAT * tpb))
    tempo = mido.MidiTrack(); mf.tracks.append(tempo)
    tempo.append(mido.MetaMessage("set_tempo", tempo=mido.bpm2tempo(BPM), time=0))
    tempo.append(mido.MetaMessage("time_signature", numerator=4, denominator=4, time=0))
    marks = sorted([(0.0, "ASMR parrilla"), (EV["impact"], "IMPACTO carne"), (EV["t1"], "T1 entra en el pan"), (BAR0, "BAR 1 · nace el motivo"),
                    (EV["t2"], "T2 destello → queso · DROP"), (EV["t3"], "T3 vórtice"), (EV["lock"], "T3 engranaje bloquea"),
                    (EV["t4"], "T4 metal → ilustración"), (EV["ret"], "Regreso a la hamburguesa"), (EV["bite"], "MORDISCO"),
                    (EV["plate"], "Plato vacío · silencio"), (GB["line1"], "Copy 1"), (GB["line2"], "Copy 2"), (GB["drop_land"], "Gota / logo · motivo resuelto"),
                    (DUR, "FIN · bucle")])
    last = 0
    for s, txt in marks:
        tk = sec2tick(s); tempo.append(mido.MetaMessage("marker", text=f"{s:.3f}s {txt}".replace("→", "->").replace("·", "-"), time=tk - last)); last = tk
    chans = dict(motivo=0, armonia=1, bajo=2, percusion=9)
    for part, notes in MIDI.items():
        tr = mido.MidiTrack(); mf.tracks.append(tr); tr.append(mido.MetaMessage("track_name", name=part, time=0))
        ch = chans.get(part, 3); ev = []
        for t0, d, n, v in notes:
            ev.append((sec2tick(t0), 1, mido.Message("note_on", note=n, velocity=v, channel=ch)))
            ev.append((sec2tick(t0 + d), 0, mido.Message("note_off", note=n, velocity=0, channel=ch)))
        ev.sort(key=lambda e: (e[0], e[1])); last = 0
        for tk, _, msg in ev:
            msg.time = max(0, tk - last); tr.append(msg); last = max(last, tk)
    mf.save(path)


if __name__ == "__main__":
    b = Bus()
    foley_c(b)
    compose(b)
    used = apply_external(b)
    mix, buses, gain, lufs, gr = master(b)
    out = os.path.join(HERE, "C"); os.makedirs(os.path.join(out, "tracks"), exist_ok=True); os.makedirs(os.path.join(out, "stems"), exist_ok=True)
    for (bus, name), buf in sorted(b.tr.items()):
        sf.write(os.path.join(out, "tracks", f"{bus}__{name}.flac"), (buf * gain).T.astype(np.float32), SR, subtype="PCM_24")
    for k, buf in buses.items():
        sf.write(os.path.join(out, "stems", f"{k}.wav"), buf.T.astype(np.float32), SR, subtype="PCM_24")
    sf.write(os.path.join(out, "DIBURAMA_V3_C_MIX_48k24.wav"), mix.T.astype(np.float32), SR, subtype="PCM_24")
    write_midi(os.path.join(HERE, "DIBURAMA_V3_C_COMPOSICION.mid"))
    print(f"C: {len(b.tr)} tracks | integrated {lufs:.2f} LUFS | max limiter GR {gr:.2f} dB | external parts: {used or 'none'}")
