"""DIBURAMA spot — V4 foley (client's original recordings only, one track per effect).

Same edit as the reviewed V3 foley: impact without saturation, single-hit metal, tamed cheese, natural bite.
The only non-recorded element is the short ring added under the metal lock (tuned resonators excited by the
real metal hit) — it is a treatment of the recording, not music.
"""
import os, sys, math
import numpy as np
from scipy import signal
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, os.path.join(ROOT, "audio", "v2"))
import mix_v2 as M
from mix_v2 import (SR, N, DUR, S, db, frag, onset, hp, lp, bp, notch, peq, pitch, fades, norm, rmsn, stereo, pan,
                    loop_to, autom, NOTE)
GB = M.GB; EV = M.EV

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
    bed = trmsn(loop_to(frag("02_sizzle_base.mp3", 9.0, 21.0), S(6.4)))
    bed = bed * autom(bed.shape[1], [(0, -5), (0.95, -4.5), (1.0, -2), (1.6, -3.5), (3.2, -5), (4.2, -7), (5.4, -12), (6.4, -40)])
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
    room = trmsn(loop_to(frag("14_plato.mp3", 0.1, 1.8), S(2.4)))
    b.put(AM, "tono_sala", fades(lp(room, 6000), 0.6, 0.35), EV["plate"] - 0.95, -30)
    for cue, a, at, g in (("miga_plato_1", 4.95, EV["crumb1"], -24), ("miga_plato_2", 6.95, EV["crumb2"], -20)):
        on = onset("14_plato.mp3", a, a + 0.2)
        po(F, cue, "14_plato.mp3", on - 0.02, on + 0.3, at, on, g, proc=lambda x: hp(x, 2000), fo=0.15)
    # brand drop + loop to the grill (end level = start level)
    on7 = onset("07_queso_elastico.mp3", 5.55, 5.70)
    po(X, "firma_gota", "07_queso_elastico.mp3", 5.55, 6.0, GB["drop_land"], on7, -10, proc=lambda x: hp(pitch(x, 1.6), 300), fo=0.12)
    tail = fades(trmsn(loop_to(frag("02_sizzle_base.mp3", 9.0, 12.0), S(1.2))), 1.0, 0.0) * db(-1)
    b.put(F, "sizzle_bucle", M.widen(tame(tail, 11), 1.25), DUR - 1.2, 0)
    firet = fades(norm(frag("04_fuego.mp3", 0.3, 1.5)), 1.0, 0.0)
    b.put(AM, "fuego_bucle", firet, DUR - 1.2, -6)


