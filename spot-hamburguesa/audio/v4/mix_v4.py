"""DIBURAMA spot — V4 sound: the client's selected music ("Luxury in Motion") edited to the V2 picture,
with the client's original foley. No music is generated here: the score is the external track, cut on its
own beat grid (112.5 BPM, D minor) and shaped only with fades, filters, gain automation and a reverb tail.

MUSIC EDIT (source time → master time):
  m1 subida        17.710 – 21.780  → 3.430 – 7.500   the track's filter-opening build: the ASMR becomes music
  m2 drop motion   21.780 – 24.985  → 7.500 – 10.705  its first drop lands on T2 (light flare → cheese)
                                                       10.15–10.70: high-pass rises (tension), clean stop on the beat
  m3 drop 3D       109.210 – 111.885 → 10.750 – 13.425 its biggest drop lands on the gear lock (T3)
                                                       13.30–13.62: low-pass dive into the T4 rush
  m4 break         141.220 – 143.340 → 13.620 – 15.740 the filtered break, exactly 4 beats: organic world
  m5 golpe regreso 143.340 – 144.000 → 15.750 –        drop hit on the return to the real burger, rings out
  m6 final         152.000 – 156.200 → 19.950 – 24.150 the song's real ending under copy, logo and CTA
  m7 golpe firma   143.340 – 143.870 → 22.850 –        the same hit as the return: Diburama's sonic signature
                                                       (+ the foley drop and a sizzle "tss" — see foley)
  silence for the music: 0 – 3.43 (pure ASMR) and 16.75 – 19.95 (bite, empty plate)

usage: python3 audio/v4/mix_v4.py → audio/v4/out/…
"""
import os, sys, math, subprocess
import numpy as np, soundfile as sf
from scipy import signal
import pyloudnorm as pyln

HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, HERE)
import foley_v4 as FV
from foley_v4 import M, SR, N, DUR, S, db, hp, lp, peq, fades, norm, stereo, EV, GB

MUSIC = os.path.join(HERE, "music_src", "Luxury_in_Motion.mp3")
OUT = os.path.join(HERE, "out")

def load_music():
    raw = subprocess.run(["ffmpeg", "-v", "quiet", "-i", MUSIC, "-ar", str(SR), "-ac", "2", "-f", "f32le", "-"],
                         capture_output=True, check=True).stdout
    return np.frombuffer(raw, np.float32).reshape(-1, 2).T.astype(np.float64)

def sweep(x, kind, f0, f1, t0, t1, at, block=256):
    """time-varying 2nd-order filter; f0→f1 (exponential) between master times t0..t1; region starts at `at`"""
    y = np.zeros_like(x); zi = None; n = x.shape[1]
    for i in range(0, n, block):
        t = at + i / SR
        u = min(max((t - t0) / (t1 - t0), 0.0), 1.0)
        f = f0 * (f1 / f0) ** u
        s_ = signal.butter(2, min(f, SR * 0.45), btype=kind, fs=SR, output="sos")
        if zi is None: zi = np.zeros((s_.shape[0], 2, 2))
        for c in range(2):
            y[c, i:i + block], zi[:, c] = signal.sosfilt(s_, x[c, i:i + block], zi=zi[:, c])
    return y

def tail_reverb(x, rt60=2.2, wet=0.55, seed=31):
    """a reverb 'throw' so a hit rings out naturally instead of being cut"""
    ir = M.reverb_ir(rt60, rt60 * 1.3, seed, 5000, 0.02)
    y = np.vstack([signal.fftconvolve(x[c], ir[c]) for c in range(2)])
    n = y.shape[1]
    out = np.zeros((2, n)); out[:, :x.shape[1]] = x
    return out + y * wet

class Bus:
    def __init__(s): s.tr = {}
    def put(s, bus, name, sig, t, gain_db=0.0):
        k = (bus, name)
        if k not in s.tr: s.tr[k] = np.zeros((2, N))
        sig = stereo(np.asarray(sig, float)) * db(gain_db); i = S(t)
        if i < 0: sig = sig[:, -i:]; i = 0
        j = min(N, i + sig.shape[1])
        if j > i: s.tr[k][:, i:j] += sig[:, :j - i]

def region(src, a, b, pre=0.0, post=0.0):
    """slice the source with optional handles (pre/post seconds) for crossfades"""
    return src[:, S(a - pre):S(b + post)].copy()

EDIT = []
def music(b):
    src = load_music()
    # m1 — the build. Enters under the T1 rush, rises to the drop.
    m1 = region(src, 17.71, 21.78, post=0.012)
    m1 = m1 * M.autom(m1.shape[1], [(0, -30), (0.25, -10), (1.0, -5), (2.6, -2.5), (4.07, 0)])
    m1 = fades(m1, 0.01, 0.012)
    b.put("MUSICA", "m1_subida", m1, 3.43); EDIT.append(("m1_subida", 17.71, 21.78, 3.43))
    # m2 — drop on T2; tension filter before T3; clean stop on the beat
    m2 = region(src, 21.78, 24.985, pre=0.012, post=0.006)
    m2 = sweep(m2, "highpass", 25, 700, 10.15, 10.69, 7.5 - 0.012)
    m2 = m2 * M.autom(m2.shape[1], [(0, 0), (2.65, 0), (3.19, 1.5), (3.217, 1.5)])
    m2 = fades(m2, 0.012, 0.018)
    b.put("MUSICA", "m2_drop_motion", m2, 7.5 - 0.012); EDIT.append(("m2_drop_motion", 21.78, 24.985, 7.5))
    # m3 — the biggest drop on the gear lock; low-pass dive into T4
    m3 = region(src, 109.21, 111.885 + 0.2, pre=0.004)
    m3 = sweep(m3, "lowpass", 18000, 280, 13.28, 13.62, 10.75 - 0.004)
    m3 = m3 * M.autom(m3.shape[1], [(0, 0), (2.55, 0), (2.87, -14)])
    m3 = fades(m3, 0.004, 0.06)
    b.put("MUSICA", "m3_drop_3D", m3, 10.75 - 0.004); EDIT.append(("m3_drop_3D", 109.21, 112.085, 10.75))
    # m4 — the filtered break, 4 beats: organic world (rises from the rush)
    m4 = region(src, 141.22, 143.34, post=0.01)
    m4 = m4 * M.autom(m4.shape[1], [(0, -10), (0.25, -3), (0.6, -2), (2.12, -1)])
    m4 = fades(m4, 0.04, 0.01)
    b.put("MUSICA", "m4_break_organico", m4, 13.62); EDIT.append(("m4_break_organico", 141.22, 143.34, 13.62))
    # m5 — the return: one drop hit, then it rings out and leaves the burger alone before the bite
    m5 = region(src, 143.34, 144.00, pre=0.01)
    m5 = m5 * M.autom(m5.shape[1], [(0, 0), (0.25, 0), (0.67, -12)])
    m5 = tail_reverb(fades(m5, 0.01, 0.12), 1.6, 0.45, 32)
    m5 = m5 * M.autom(m5.shape[1], [(0, 0), (0.6, -3), (0.95, -30), (1.0, -80)])
    b.put("MUSICA", "m5_golpe_regreso", m5, 15.75 - 0.01, -9.0); EDIT.append(("m5_golpe_regreso", 143.34, 144.0, 15.75))
    # m6 — the song's real ending under the brand
    m6 = region(src, 152.0, 156.2)
    m6 = fades(m6, 0.06, 0.25)
    m6 = tail_reverb(m6, 2.4, 0.25, 33)
    m6 = m6 * M.autom(m6.shape[1], [(0, -6), (2.9, -5), (4.1, -6), (4.6, -18), (5.05, -60)])
    b.put("MUSICA", "m6_final_marca", m6, 19.95); EDIT.append(("m6_final_marca", 152.0, 156.2, 19.95))
    # m7 — the signature hit on the logo drop (same hit as the return)
    m7 = region(src, 143.34, 143.87, pre=0.004)
    m7 = tail_reverb(fades(m7, 0.004, 0.15), 2.0, 0.5, 34)
    m7 = m7 * M.autom(m7.shape[1], [(0, 0), (0.5, -2), (1.6, -18), (2.1, -60)])
    b.put("MUSICA", "m7_golpe_firma", m7, GB["drop_land"] - 0.004, -8); EDIT.append(("m7_golpe_firma", 143.34, 143.87, GB["drop_land"]))

def signature_foley(b):
    """the drop's "tss": a breath of real sizzle on the logo, so the brand closes with the burger's sound"""
    x = FV.trmsn(fades(M.frag("03_sizzle_detalle.mp3", 3.86, 4.6), 0.004, 0.45))
    b.put("SFX", "firma_tss", x * M.autom(x.shape[1], [(0, 0), (0.15, -4), (0.74, -30)]), GB["drop_land"] + 0.02, -14)


# ------------------------------------------------------------------ automation: music and foley don't compete
def foley_key(b):
    """envelope of the foreground foley events (not the beds) — the music makes room only when they speak"""
    beds = {"sizzle_base", "sizzle_detalle", "fuego", "fuego_regreso", "fuego_bucle", "sizzle_bucle", "tono_sala",
            "carne_parrilla", "engranajes", "sizzle_regreso"}
    keys = [k for k in b.tr if k[0] in ("FOLEY", "SFX") and k[1] not in beds]
    x = sum(b.tr[k] for k in keys)
    e = np.abs(x).max(axis=0)
    a1, r1 = math.exp(-1 / (0.008 * SR)), math.exp(-1 / (0.18 * SR))
    env = np.empty_like(e); v = 0.0
    for i, s_ in enumerate(e):
        v = a1 * v + (1 - a1) * s_ if s_ > v else r1 * v + (1 - r1) * s_; env[i] = v
    return env

def duck_music(music_bus, key, max_db=4.5, thr_db=-30):
    lvl = 20 * np.log10(key + 1e-9)
    amt = np.clip((lvl - thr_db) / 20, 0, 1) * max_db
    return music_bus * db(-amt)[None], amt


def master(b):
    buses = {}
    for (bus, name), buf in b.tr.items(): buses[bus] = buses.get(bus, 0) + buf
    for k in ("MUSICA", "FOLEY", "SFX", "AMBIENTES"): buses.setdefault(k, np.zeros((2, N)))
    key = foley_key(b)
    buses["MUSICA"], amt = duck_music(buses["MUSICA"], key)
    # a gentle dip where the foley textures live (2–5 kHz) only while the music plays over foley-rich moments
    buses["MUSICA"] = peq(buses["MUSICA"], 3500, -1.5, 0.9)
    room = M.reverb_ir(0.35, 0.5, 9, 7000, 0.004); plate = M.reverb_ir(1.1, 1.6, 12, 8000, 0.01)
    buses["FOLEY"] = M.convolve(buses["FOLEY"], room, 0.05)
    buses["SFX"] = M.convolve(buses["SFX"], plate, 0.14)
    bal = dict(MUSICA=-6.5, FOLEY=0.0, SFX=-1.5, AMBIENTES=-0.5)
    for k in buses: buses[k] = buses[k] * db(bal[k])
    # same transient-friendly logic as before: the bite on its own fader, the rest to TARGET
    bite_keys = [k for k in b.tr if k[1].startswith("mordisco")]
    bite_sig = M.convolve(sum(b.tr[k] for k in bite_keys), room, 0.05) * db(bal["FOLEY"])
    eq = lambda x: peq(peq(M.hp(x, 28, 2), 320, -1.0, 0.8), 3300, 0.6, 0.9)
    full = eq(sum(buses.values())); bite_eq = eq(bite_sig); rest = full - bite_eq
    pk = np.abs(bite_eq).max()
    bite_cl = M.limiter(bite_eq, pk * db(-5.0), look=0.0005, rel=0.004)              # shaves only the needle tips
    meter = pyln.Meter(SR); TARGET = -16.0
    bite = slice(S(EV["bite"] - 0.02), S(EV["bite"] + 0.5))
    best = None
    for trim in np.arange(3.0, -10.01, -0.5):
        mix = rest + bite_cl * db(trim)
        g_ = db(TARGET - meter.integrated_loudness(mix.T))
        o_ = M.limiter(mix * g_, db(-1.5))
        r_ = np.abs(o_).max(axis=0) / np.maximum(np.abs(mix * g_).max(axis=0), 1e-9)
        live = np.abs(mix * g_).max(axis=0) > 0.05; lb = live[bite]
        grbite = -20 * np.log10(max(r_[bite][lb].min(), 1e-9)) if lb.any() else 0.0
        bite_ms = 1000 * np.sum(r_[bite][lb] < db(-1.0)) / SR
        grmax = -20 * np.log10(max(r_[live].min(), 1e-9))
        if grbite <= 2.0 and bite_ms <= 15:
            best = (trim, g_, o_, grmax, grbite, bite_ms); break
    trim, gain, out, grmax, grbite, bite_ms = best
    buses["FOLEY"] = buses["FOLEY"] + bite_sig * (db(trim) - 1)
    for k in buses: buses[k] = buses[k] * gain
    for k in bite_keys: b.tr[k] = b.tr[k] * db(trim)
    info = dict(lufs=meter.integrated_loudness(out.T), limiter_max_db=grmax, bite_trim_db=trim,
                bite_limiter_db=grbite, bite_ms=bite_ms, duck_max_db=float(amt.max()))
    return out, buses, gain, info


if __name__ == "__main__":
    b = Bus()
    FV.foley_c(b)
    signature_foley(b)
    music(b)
    mix, buses, gain, info = master(b)
    os.makedirs(os.path.join(OUT, "tracks"), exist_ok=True); os.makedirs(os.path.join(OUT, "stems"), exist_ok=True)
    for (bus, name), buf in sorted(b.tr.items()):
        sf.write(os.path.join(OUT, "tracks", f"{bus}__{name}.flac"), (buf * gain).T.astype(np.float32), SR, subtype="PCM_24")
    for k, buf in buses.items():
        sf.write(os.path.join(OUT, "stems", f"{k}.wav"), buf.T.astype(np.float32), SR, subtype="PCM_24")
    sf.write(os.path.join(OUT, "DIBURAMA_V4_MIX_48k24.wav"), mix.T.astype(np.float32), SR, subtype="PCM_24")
    with open(os.path.join(HERE, "EDL_MUSICA_V4.md"), "w") as f:
        f.write("# EDL música V4 — «Luxury in Motion» editada a la imagen V2\n\n| Región | Fuente in | Fuente out | Máster in | Máster out |\n|---|---|---|---|---|\n")
        for n, a, b_, at in EDIT:
            f.write(f"| {n} | {a:.3f} | {b_:.3f} | {at:.3f} | {at + b_ - a:.3f} |\n")
    print("V4:", {k: (round(v, 2) if isinstance(v, float) else v) for k, v in info.items()})
