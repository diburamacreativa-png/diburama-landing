"""DIBURAMA spot — V5 music edit: «Luxury in Motion» as ONE continuous section (no drop-hopping).

Both tests share: the same foley (audio/v4/foley_v4.py, untouched), the same sound-design transitions, the
same closing, and light ducking (max 2 dB, foreground foley only). The difference is the continuous section
used for the journey 3.43 → 16.03 s (exactly 4 beats of build + 16 beats from the drop, at the song's own
112.5 BPM — no time-stretch):

  A  source 105.14 → 117.74   its drop 109.21 lands on 7.5 s (T2); a steady, rising groove
  B  source  17.71 →  30.31   the song's own opening: filter-opening build → first drop on 7.5 s → the first
                              groove with its built-in stops (one of them falls on the T4 rush)

  Exit (both): the phrase ends at 16.03 s; the next downbeat is played as a short "button" with a natural
  reverb tail, gone by 16.75 s, while fire and sizzle bring the burger back (return dissolve 15.67–15.83).
  Closing (both): the song's real ending, 151.88 → 156.14 (starts on its own phrase boundary, ends on the
  song's stop), entering with the first copy line at 19.95 s. The logo drop keeps the foley signature only.

usage: python3 audio/v5/mix_v5.py A|B
"""
import os, sys
import numpy as np, soundfile as sf

HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, os.path.join(ROOT, "audio", "v4"))
import mix_v4 as V4
from mix_v4 import M, FV, SR, N, S, db, fades, Bus, load_music, region, tail_reverb, EV, GB

BEAT = 60 / 112.5
SECTIONS = dict(A=dict(drop=109.21, label="105.14–117.74 (drop 109.21 → 7.5 s)"),
                B=dict(drop=21.78, label="17.71–30.31 (apertura de la canción, drop 21.78 → 7.5 s)"))
T_IN, T_DROP = 3.43, 7.5
END = T_DROP + 16 * BEAT                    # 16.033 s: end of the 16-beat phrase from the drop
CLOSE_SRC = (151.877, 156.14)                # song outro: phrase start → the song's stop
CLOSE_AT = GB["line1"]
EDIT = []

def music(b, test):
    src = load_music()
    d = SECTIONS[test]["drop"]
    s_in = d - (T_DROP - T_IN)
    s_end = d + 16 * BEAT
    # the journey: one continuous take
    x = region(src, s_in, s_end)
    x = fades(x, 0.004, 0.004)
    x = x * M.autom(x.shape[1], [(0, -24), (0.12, -10), (0.45, -3), (0.9, 0),                  # swells in with the T1 rush
                                 (END - T_IN - 3 * BEAT, 0), (END - T_IN, -7)])               # breathes out on the last 2 beats
    b.put("MUSICA", "seccion_continua", x, T_IN); EDIT.append(("seccion_continua", s_in, s_end, T_IN))
    # exit: the next downbeat as a button, ringing out naturally
    btn = region(src, s_end, s_end + 0.5 * BEAT)
    btn = fades(btn, 0.003, 0.12) * M.autom(btn.shape[1], [(0, -6), (0.08, -7), (0.5 * BEAT, -18)])
    btn = tail_reverb(btn, 1.5, 0.5, 41)
    btn = btn * M.autom(btn.shape[1], [(0, 0), (0.45, -6), (0.7, -60)])
    b.put("MUSICA", "salida_boton", btn, END - 0.003); EDIT.append(("salida_boton", s_end, s_end + 0.5 * BEAT, END))
    # closing: the song's real ending
    c = region(src, *CLOSE_SRC)
    c = fades(c, 0.03, 0.02)
    c = tail_reverb(c, 2.0, 0.18, 42)
    c = c * M.autom(c.shape[1], [(0, -5), (CLOSE_SRC[1] - CLOSE_SRC[0], -5), (CLOSE_SRC[1] - CLOSE_SRC[0] + 0.6, -60)])
    b.put("MUSICA", "cierre_final_cancion", c, CLOSE_AT); EDIT.append(("cierre_final_cancion", *CLOSE_SRC, CLOSE_AT))

T15_CUT = 6.0
def t15_sfx(b):
    """V6 · tunnel → film set: a progressive rush built from the client's recordings, peaking on the cut.
    build = 11_transicion reversed (its swell rises into its own attack) + a sweep that opens as speed grows;
    arrival = the decaying air of 10_whoosh after its peak, low-passed for depth, panned slightly wide."""
    from foley_v4 import frag, lp, hp, norm
    widen = M.widen
    build = frag("11_transicion.mp3", 0.62, 1.55)[:, ::-1]                   # 0.93 s, ends on the attack at 0.795
    build = V4.sweep(build, "lowpass", 900, 14000, T15_CUT - 0.93, T15_CUT, T15_CUT - 0.93)
    build = norm(fades(hp(build, 90), 0.25, 0.006))
    build = build * M.autom(build.shape[1], [(0, -18), (0.45, -9), (0.80, -2), (0.93, 0)])
    b.put("SFX", "t15_rush_subida", build, T15_CUT - build.shape[1] / SR, -9)
    air = frag("10_whoosh.mp3", 0.50, 1.45)
    air = norm(fades(lp(air, 3800), 0.004, 0.45))
    b.put("SFX", "t15_llegada_aire", widen(air, 1.3), T15_CUT - 0.006, -13)

def light_duck(music_bus, key, max_db=2.0, thr_db=-24):
    return V4.__dict__["_duck_orig"](music_bus, key, max_db, thr_db)


if __name__ == "__main__":
    test = sys.argv[1].upper()
    V4._duck_orig = V4.duck_music
    V4.duck_music = light_duck                             # V5: the foley lives WITH the music
    b = Bus()
    FV.foley_c(b)
    V4.signature_foley(b)
    if os.environ.get("T15") == "1": t15_sfx(b)
    music(b, test)
    mix, buses, gain, info = V4.master(b)
    out = os.path.join(HERE, f"out_{test}" + ("_T15" if os.environ.get("T15") == "1" else "")); os.makedirs(os.path.join(out, "tracks"), exist_ok=True)
    os.makedirs(os.path.join(out, "stems"), exist_ok=True)
    for (bus, name), buf in sorted(b.tr.items()):
        sf.write(os.path.join(out, "tracks", f"{bus}__{name}.flac"), (buf * gain).T.astype(np.float32), SR, subtype="PCM_24")
    for k, buf in buses.items():
        sf.write(os.path.join(out, "stems", f"{k}.wav"), buf.T.astype(np.float32), SR, subtype="PCM_24")
    sf.write(os.path.join(out, f"DIBURAMA_V5_{test}_MIX_48k24.wav"), mix.T.astype(np.float32), SR, subtype="PCM_24")
    with open(os.path.join(HERE, f"EDL_MUSICA_V5_{test}.md"), "w") as f:
        f.write(f"# EDL música V5 · prueba {test} — {SECTIONS[test]['label']}\n\n"
                "Sin cambio de tempo. Una sola toma continua para todo el viaje; el resto de transiciones las resuelve el diseño sonoro.\n\n"
                "| Región | Fuente in | Fuente out | Máster in | Máster out |\n|---|---|---|---|---|\n")
        for n, a, b_, at in EDIT:
            f.write(f"| {n} | {a:.3f} | {b_:.3f} | {at:.3f} | {at + b_ - a:.3f} |\n")
    print(test, {k: (round(float(v), 2)) for k, v in info.items()})
