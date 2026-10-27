#!/usr/bin/env python3
"""Banda sonora de VIDEO REEL CHILE_DEMO 6 (35,40 s). El video NO se toca.

Desde la union (J) el audio ES la mezcla aprobada del DEMO 5 adelantada 3,28 s
(mismas muestras: sin remezcla ni re-master). Antes de J se renderiza la apertura
nueva con el mismo motor, la misma musica (continua, desplazada) y la misma
ganancia de master del DEMO 5, y se comprueba que en J ambas senales coinciden.

Uso:
  python3 -I build_demo6.py --music "Groovy Good Vibes.mp3" --pack <pack_dir> \
      --demo5 <out_demo5> --video "VIDEO REEL CHILE_DEMO 6.mp4" --out <out_dir>
"""
import argparse, json, math, os, subprocess, sys
import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import build_audio as B  # noqa: E402
import music_demo5 as M  # noqa: E402
import cues_demo5 as C5  # noqa: E402
import cues_demo6 as C6  # noqa: E402

SR = 48000
DUR = 35.40
N = int(round(DUR * SR))          # 1 699 200 muestras = 885 fotogramas
SHIFT = int(round(C6.SHIFT * SR))  # 3,28 s = 82 fotogramas
J = 6.0                            # union con la mezcla aprobada (entre eventos)
WIN = 8.0                          # ventana renderizada de la apertura
XF = int(0.010 * SR)
P5 = "ALSINA_DEMO5"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--music", required=True)
    ap.add_argument("--pack", required=True)
    ap.add_argument("--demo5", required=True)
    ap.add_argument("--video", required=True)
    ap.add_argument("--out", required=True)
    a = ap.parse_args()
    os.makedirs(a.out, exist_ok=True)

    st5 = json.load(open(os.path.join(a.demo5, "build_stats_demo5.json")))["stats"]
    gain = st5["master_gain_db"]
    mix5 = B.decode(os.path.join(a.demo5, f"{P5}_MEZCLA_FINAL_48k24.wav"))
    mus5 = B.decode(os.path.join(a.demo5, f"{P5}_MUSICA_STEM_48k24.wav"))
    sfx5 = B.decode(os.path.join(a.demo5, f"{P5}_SFX_STEM_48k24.wav"))

    print("[1] musica: la misma del DEMO 5, continua y adelantada 3,28 s")
    music5, _ = M.build(B.decode(a.music), B.ffmpeg_filter)
    W = int(WIN * SR)
    m6 = music5[SHIFT:SHIFT + W].copy()
    i0 = int(round(C6.MUSIC_IN * SR))
    fi = int(0.003 * SR)
    m6[:i0] = 0
    m6[i0:i0 + fi] *= (0.5 * (1 - np.cos(np.linspace(0, np.pi, fi))))[:, None]

    print("[2] efectos de la apertura + efectos del DEMO 5 que caen en la ventana")
    sfx = np.zeros((W + SR, 2))
    log = []
    keep5 = [c for c in C5.CUES if c["t"] >= 8.4 and c["t"] - C6.SHIFT < WIN + 1]
    for c, src in [(c, "DEMO6") for c in C6.CUES] + [(c, "DEMO5") for c in keep5]:
        dt = 0.0 if src == "DEMO6" else C6.SHIFT
        t6 = c["t"] - dt
        x = B.render_cue(a.pack, c)
        k = B.anchor_offset(x, c["mode"])
        start = int(round(t6 * SR)) - k
        # calibracion contra la musica continua (tiempo del DEMO 5), como en el DEMO 5
        if c["mode"] == "attack" or len(x) < int(0.3 * SR):
            lm = B.music_level_db(music5, t6 + C6.SHIFT)
        else:
            lm = B.music_level_span(music5, start + SHIFT, start + SHIFT + len(x))
        g = lm + c["rel"] - B.sfx_level_db(x)
        gl, gr = B.pan_gains(c["pan"])
        y = x * 10 ** (g / 20)
        y[:, 0] *= gl
        y[:, 1] *= gr
        s0 = max(0, start)
        y = y[s0 - start:]
        e0 = min(len(sfx), s0 + len(y))
        sfx[s0:e0] += y[:e0 - s0]
        log.append(dict(id=c["id"], origen=src, frame=round(t6 * 25, 2), event_s=round(t6, 4),
                        start_s=round(start / SR, 4), file=c["file"], rel_db=c["rel"], gain_db=round(g, 2),
                        note=c["note"]))
    sfx = sfx[:W]
    k0 = int(0.030 * SR)  # la subida de tension recortada en t=0 entra con 30 ms de fundido, sin clic
    sfx[:k0] *= (0.5 * (1 - np.cos(np.linspace(0, np.pi, k0))))[:, None]

    print("[3] ducking: el de la apertura + el del DEMO 5 desplazado")
    ducks = list(C6.DUCKS)
    for d in C5.DUCKS:
        if d["t0"] >= 8.2:
            dd = dict(d)
            dd["t0"] -= C6.SHIFT
            dd["t1"] -= C6.SHIFT
            ducks.append(dd)
    B.N = W
    low, mid, high = B.split3(m6)
    m6d = (low * B.duck_env(ducks, 0)[:, None] + mid * B.duck_env(ducks, 1)[:, None]
           + high * B.duck_env(ducks, 2)[:, None])
    g = 10 ** (gain / 20)
    open_mus = m6d * g
    open_sfx = sfx * g
    open_mix = open_mus + open_sfx

    print("[4] union con la mezcla aprobada en J = %.2f s" % J)
    ref = mix5[SHIFT:SHIFT + W]
    a_, b_ = int((J - 0.5) * SR), int((J + 1.5) * SR)
    diff_db = 20 * math.log10(np.abs(open_mix[a_:b_] - ref[a_:b_]).max() + 1e-12)
    print("    diferencia maxima apertura vs mezcla aprobada en [J-0,5 ; J+1,5]: %.1f dBFS" % diff_db)
    j = int(J * SR)
    fin = np.sin(np.linspace(0, np.pi / 2, XF))[:, None]
    fout = np.cos(np.linspace(0, np.pi / 2, XF))[:, None]

    def joined(op, appr):
        tail = appr[SHIFT + j:SHIFT + N]
        mixz = op[j - XF:j] * fout + appr[SHIFT + j - XF:SHIFT + j] * fin
        return np.vstack([op[:j - XF], mixz, tail])

    mix6 = joined(open_mix, mix5)
    mus6 = joined(open_mus, mus5)
    sfx6 = joined(open_sfx, sfx5)
    assert len(mix6) == N

    o = a.out
    pre = "ALSINA_DEMO6"
    B.write_wav(os.path.join(o, f"{pre}_MEZCLA_FINAL_48k24.wav"), mix6)
    B.write_wav(os.path.join(o, f"{pre}_MUSICA_STEM_48k24.wav"), mus6)
    B.write_wav(os.path.join(o, f"{pre}_SFX_STEM_48k24.wav"), sfx6)
    mp4 = os.path.join(o, "ALSINA_REEL_CHILE_DEMO6_FINAL.mp4")
    # el AAC se codifica desde el WAV de 24 bits entregado: codificando la senal en coma
    # flotante, el AAC rebotaba a -0,15 dBTP en el impacto del logo; desde el WAV queda en -1,3
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", a.video, "-i", os.path.join(o, f"{pre}_MEZCLA_FINAL_48k24.wav"),
                    "-map", "0:v:0", "-map", "1:a:0", "-c:v", "copy", "-c:a", "aac", "-b:a", "320k",
                    "-ar", "48000", "-movflags", "+faststart", mp4], check=True)
    op_loud = B.loudness(mix6[:j])
    stats = dict(union_s=J, master_gain_db_demo5=gain, diferencia_union_dbfs=diff_db,
                 apertura_0_J=dict(I=op_loud[0], TP=op_loud[2]), final=dict(zip(("I", "LRA", "TP"), B.loudness(mix6))),
                 cuerpo_identico_a_demo5_desde_s=J)
    with open(os.path.join(o, "build_stats_demo6.json"), "w") as f:
        json.dump(dict(stats=stats, cues=log, ducks=ducks), f, ensure_ascii=False, indent=1)
    print(json.dumps(stats, indent=1))


if __name__ == "__main__":
    main()
