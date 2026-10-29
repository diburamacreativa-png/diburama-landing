#!/usr/bin/env python3
"""Lista de acentos (analisis visual + tratamiento sonoro) para «Build Momentum (1)» / DEMO 6.
Los fotogramas y acciones se comprobaron a mano en hojas de contacto; los tiempos sonoros salen
del build (build_stats_bm2.json), no se escriben a mano.

Uso: python3 -I lista_acentos_bm2.py <out_dir>
"""
import csv, json, os, sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import music_bm2 as M  # noqa: E402

F = 25.0
# (fotograma, accion visual comprobada, fuerza, ids de cue que la acompanan o texto si no lleva golpe)
EVENTOS = [
    (7, "Impulso de camara 1: alejamiento brusco; «MONTAJES» entra volando", "FUERTE", ["Z1h", "Z1p", "Z1w"]),
    (23, "Salto intermedio del zoom; aparece «SIN»", "MEDIO", ["Z2a"]),
    (31, "Impulso de camara 2: alejamiento brusco; aparece «NECESIDAD»", "FUERTE", ["Z2b", "Z2p", "Z2w", "Z2r"]),
    (None, "Musica: entra el groove completo (primer tiempo del compas 74)", "ESTRUCTURA", "groove"),
    (83, "Latigazo con desenfoque (f79-82) y corte al plano «DE GRÚA» (el texto llega con el paneo)", "FUERTE", ["C1h", "C1p", "C1w"]),
    (89, "El paneo rapido frena (f84-89); linea roja se dibuja", "SECUNDARIO", "sin golpe"),
    (131, "Paneo que acelera (f127-130) y corte a ALISPLAY", "MEDIO", ["C2h", "C2w"]),
    (141, "«ALISPLAY» sube y se asienta", "LIGERO", ["C3p"]),
    (151, "«MANUAL» se asienta", "LIGERO", ["C4p"]),
    (230, "Latigazo (f227-229) y corte a 240 PLUS", "FUERTE", ["C5h", "C5w", "C5r"]),
    (243, "«PLUS» completa la caida de sus letras", "LIGERO", ["C6p"]),
    (298, "Corte a «DISEÑADO PARA» (el texto sube y se asienta en f304)", "MEDIO", ["C7h", "C7w"]),
    (341, "«EDIFICACIÓN» aparece", "LIGERO", ["C8p"]),
    (355, "«CHILENA» aparece", "SECUNDARIO", "sin golpe"),
    (393, "El contador (desde f360) se detiene en 2,40 m", "LIGERO", ["C9p"]),
    (429, "El cubo de la grua barre el plano (f425-433), corte oculto en f430", "MEDIO (movimiento)", ["C10w", "C10b"]),
    (453, "«MENOS DEPENDENCIA» se forma (f429-456)", "SECUNDARIO", "sin golpe (la musica pasa a Fa en el compas 84)"),
    (503, "«GRÚA» destella en rojo", "LIGERO", ["C11m"]),
    (545, "Corte a MONTAJE SIMPLE", "MEDIO", ["C12w"]),
    (563, "«SIMPLE» aterriza", "MEDIO", ["C13h"]),
    (582, "«CALIDAD.» aterriza", "MEDIO", ["C14h"]),
    (670, "Latigazo (f668-669) y corte a la toma cenital", "FUERTE", ["C15h", "C15w", "C15r"]),
    (737, "Alejamiento que acelera (f708-735) y cierre del iris (f735-737)", "ANTICIPACION", ["Z01"]),
    (738, "Negro: nace el punto (cuadrado blanco); la musica se retira", "LIGERO", ["Z02"]),
    (753, "PUNTO DE LA «i»: el punto cae (f738-752) y se asienta en la «i»; «Alsina» queda completo", "ANCLA", ["I01", "I02", "I03", "I04", "Z03"]),
    (766, "«x» y ALTIUS se ensamblan (f754-766); «ASÍ SE CONSTRUYE EN / CHILE | GRAN VÍA» aparece (f764-774)", "SIN GOLPE", "cola limpia del acorde final"),
    (874, "Fundido a negro del video (f874-883)", "FINAL", "la cola se apaga con la imagen"),
]


def tc(t):
    f = int(round(t * F))
    return f"00:00:{f // 25:02d}:{f % 25:02d}"


def main():
    o = sys.argv[1]
    st = json.load(open(os.path.join(o, "build_stats_bm2.json")))
    cues = {c["id"]: c for c in st["cues"]}
    groove = st["stats"]["music"]["groove_completo_desde_s"]
    rows = []
    for fr, accion, fuerza, cue_ids in EVENTOS:
        if cue_ids == "groove":
            rows.append(dict(fotograma="-", tiempo_imagen_s=f"{groove:.3f}".replace(".", ","), timecode=tc(groove),
                             accion_visual=accion, fuerza=fuerza, golpe_audio_s=f"{groove:.3f}".replace(".", ","),
                             desfase_ms="", que_suena="Bombo y bajo del tema entran (la intro sonaba con paso alto)"))
            continue
        t_img = fr / F
        if isinstance(cue_ids, str):
            rows.append(dict(fotograma=fr, tiempo_imagen_s=f"{t_img:.3f}".replace(".", ","), timecode=tc(t_img),
                             accion_visual=accion, fuerza=fuerza, golpe_audio_s="", desfase_ms="", que_suena=cue_ids))
            continue
        main_c = cues[cue_ids[0]]
        t_snd = main_c["event_s"]
        partes = []
        for cid in cue_ids:
            c = cues[cid]
            partes.append(f"{os.path.basename(c['file'])[:-4]}{' (fundido con el tema)' if c['snapped_to_music'] else ''}")
        rows.append(dict(fotograma=fr, tiempo_imagen_s=f"{t_img:.3f}".replace(".", ","), timecode=tc(t_img),
                         accion_visual=accion, fuerza=fuerza, golpe_audio_s=f"{t_snd:.3f}".replace(".", ","),
                         desfase_ms=f"{(t_snd - t_img) * 1000:+.0f}" if main_c["mode"] == "attack" else "",
                         que_suena=" + ".join(partes)))
    # eventos musicales de estructura (desde la reedicion)
    blocks = M.plan()
    # tiempos de estructura medidos sobre la pista de musica final (transitorio mas fuerte a +-15 ms)
    import build_audio as B
    import build_bm2 as BB
    import numpy as np
    curve = BB.accent_curve(B.decode(os.path.join(o, "ALSINA_BM2_MUSICA_STEM_48k24.wav")))

    def medido(t):
        tt, acc = curve
        i0, i1 = np.searchsorted(tt, [t - 0.015, t + 0.015])
        return float(tt[i0 + int(np.argmax(acc[i0:i1]))])

    extra = [
        (blocks[1]["v0"], "Musica: el groove se corta y entra la subida filtrada (compases 78-79) con el corte de f131"),
        (M.src_to_video(blocks, 152.475), "Musica: DROP del tema (compas 80) = corte a 240 PLUS"),
        (M.src_to_video(blocks, 160.0965), "Musica: cambio a Fa (compas 84) mientras se forma «MENOS DEPENDENCIA DE GRÚA»"),
        (M.src_to_video(blocks, 163.9095), "Musica: cambio a Do (compas 86) = «SIMPLE»"),
        (blocks[-1]["v0"], "Musica: la bateria se retira y empieza la resolucion (compas 88) = corte a cenital"),
    ]
    for t, txt in extra:
        t = medido(t) if "subida" not in txt else t
        rows.append(dict(fotograma="-", tiempo_imagen_s="", timecode=tc(t), accion_visual=txt, fuerza="ESTRUCTURA",
                         golpe_audio_s=f"{t:.3f}".replace(".", ","), desfase_ms="", que_suena="tema"))
    path = os.path.join(o, "LISTA_DE_ACENTOS.csv")
    with open(path, "w", newline="", encoding="utf-8-sig") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        w.writeheader()
        w.writerows(rows)
    print(path, len(rows))


if __name__ == "__main__":
    main()
