# Percusion complementaria y transiciones para «Build Momentum» sobre VIDEO REEL CHILE_DEMO 6.
# La musica es la protagonista: solo se refuerzan los momentos principales.
# 'snap': el ataque se funde con el transitorio musical mas cercano (+-snap s) si existe;
# si no, cae en el tiempo indicado (siempre dentro del fotograma del evento).

F = 1 / 25.0
IMPACT = 753 * F + 0.005   # f753 (30,12 s): el punto de la «i» entra en «Alsina»

CUES = [
    # ---------------- GOLPES DE ZOOM INICIALES ----------------
    dict(id="Z1a", t=0.290, file="01_WHOOSHES/WHOOSH_01_MICRO_SECO.wav", mode="peak", rel=-10, pan=0.0, st=-1, eq="air",
         width_env=[(0, 1.2), (1, 0.6)], note="f7 golpe de zoom 1: whoosh corto"),
    dict(id="Z1b", t=0.300, file="02_IMPACTS/HIT_02_PUNCH_CON_CUERPO.wav", mode="attack", rel=-5, pan=0.0, st=0, eq="hit",
         note="f7 golpe de zoom 1: percusion grave en la semicorchea que cae en el fotograma (la musica no tiene golpe ahi)"),
    dict(id="Z1c", t=0.300, file="02_IMPACTS/HIT_04_METAL_MATE_SUTIL.wav", mode="attack", rel=-14, pan=0.0, st=-1.14, eq="metal",
         note="f7 contacto metalico discreto (afinado a Mi)"),
    dict(id="Z2a", t=23 * F, file="01_WHOOSHES/WHOOSH_01_MICRO_SECO.wav", mode="peak", rel=-13, pan=0.0, st=0, eq="air", snap=0.03,
         note="f23 primer salto del zoom 2 (secundario: lo marca el beat de la musica)"),
    dict(id="Z2r", t=31 * F + 0.03, file="04_RISERS_REVERSE/REVERSE_01_PREIMPACTO.wav", mode="end", rel=-12, pan=0.0, st=1, eq="air",
         stretch=0.25, width_env=[(0, 0.3), (1, 1.2)], amp_env=[(0, -40), (0.35, -3), (1, 0)], snap=0.045,
         note="f25-31 subida breve hacia el golpe 2"),
    dict(id="Z2b", t=31 * F + 0.03, file="01_WHOOSHES/WHOOSH_02_RAPIDO_LATERAL.wav", mode="peak", rel=-10, pan=0.0, st=-1, eq="air", snap=0.045,
         note="f31 golpe de zoom 2: whoosh rapido"),
    dict(id="Z2c", t=31 * F + 0.03, file="02_IMPACTS/HIT_03_GRUA_PROTAGONISTA.wav", mode="attack", rel=-4, pan=0.0, st=0, eq="hit_sub",
         fade=(0.28, 0.17), snap=0.045, note="f31 golpe de zoom 2: grave fundido con el primer tiempo fuerte de la musica"),
    # ---------------- CORTES Y BLOQUES DE TEXTO PRINCIPALES ----------------
    dict(id="T01", t=83 * F, file="04_RISERS_REVERSE/REVERSE_02_PRE_CORTE.wav", mode="end", rel=-14, pan=0.0, st=0, eq="air",
         width_env=[(0, 0.3), (1, 1.1)], note="f78-82 barrido: aire aspirado hacia el corte"),
    dict(id="T02", t=82.5 * F, file="01_WHOOSHES/WHOOSH_04_MOTION_MEDIO.wav", mode="peak", rel=-10, pan=0.0, st=-1, eq="air",
         pan_env=[(0, -0.3), (1, 0.3)], note="f78-83 barrido hacia DE GRUA"),
    dict(id="T03", t=83 * F, file="02_IMPACTS/HIT_02_PUNCH_CON_CUERPO.wav", mode="attack", rel=-7, pan=0.0, st=0, eq="hit", snap=0.04,
         note="f83 «DE GRUA» llega con el corte"),
    dict(id="T04", t=130.5 * F, file="01_WHOOSHES/WHOOSH_02_RAPIDO_LATERAL.wav", mode="peak", rel=-12, pan=0.0, st=0, eq="air",
         pan_env=[(0, -0.35), (1, 0.35)], note="f126-131 paneo y corte a ALISPLAY MANUAL"),
    dict(id="T05", t=229.5 * F, file="01_WHOOSHES/WHOOSH_05_GRAVE_CON_CUERPO.wav", mode="peak", rel=-10, pan=0.0, st=0, eq="air_body",
         note="f224-230 latigazo y corte a 240 PLUS"),
    dict(id="T06", t=230 * F, file="02_IMPACTS/HIT_01_PUNCH_TEXTO_SECO.wav", mode="attack", rel=-9, pan=0.0, st=0, eq="hit", snap=0.04,
         note="f230 corte a 240 PLUS (fundido con el acento musical)"),
    dict(id="T07", t=243 * F, file="03_UI_POPS_CLICKS/UI_05_SNAP_PALABRA.wav", mode="attack", rel=-15, pan=0.0, st=0, eq="click",
         note="f243 «PLUS» aterriza (secundario)"),
    dict(id="T08", t=298 * F, file="01_WHOOSHES/WHOOSH_05_GRAVE_CON_CUERPO.wav", mode="peak", rel=-12, pan=0.0, st=-1, eq="air_body",
         note="f298 corte a DISEÑADO PARA"),
    dict(id="T09", t=298 * F, file="02_IMPACTS/HIT_05_ACENTO_LIGERO.wav", mode="attack", rel=-16, pan=0.0, st=0, eq="hit", snap=0.04,
         note="f298 «DISEÑADO PARA» se asienta"),
    dict(id="T10", t=427 * F, file="01_WHOOSHES/WHOOSH_04_MOTION_MEDIO.wav", mode="peak", rel=-8, pan=0.0, st=1, eq="air",
         pan_env=[(0, 0.35), (1, -0.35)], note="f424-433 el cubo de la grua cruza (der -> izq); la musica vuelve completa en 16,90 s"),
    dict(id="T11", t=430 * F, file="01_WHOOSHES/WHOOSH_05_GRAVE_CON_CUERPO.wav", mode="peak", rel=-11, pan=0.0, st=-3, eq="air_body",
         note="f430 masa de aire de la maquinaria y corte oculto"),
    dict(id="T12", t=503 * F, file="02_IMPACTS/HIT_04_METAL_MATE_SUTIL.wav", mode="attack", rel=-11, pan=0.0, st=-1.14, eq="metal", snap=0.04,
         note="f503 «GRUA» destella en rojo"),
    dict(id="T13", t=545 * F, file="01_WHOOSHES/WHOOSH_04_MOTION_MEDIO.wav", mode="peak", rel=-10, pan=0.0, st=-1, eq="air",
         note="f545 corte a MONTAJE SIMPLE"),
    dict(id="T14", t=563 * F, file="02_IMPACTS/HIT_01_PUNCH_TEXTO_SECO.wav", mode="attack", rel=-8, pan=0.0, st=1, eq="hit", snap=0.04,
         note="f563 «SIMPLE» aterriza"),
    dict(id="T15", t=582 * F, file="02_IMPACTS/HIT_06_CALIDAD_CON_PESO.wav", mode="attack", rel=-6, pan=0.0, st=0, eq="hit", snap=0.04,
         note="f582 «CALIDAD.» completo"),
    dict(id="T16", t=670 * F, file="04_RISERS_REVERSE/REVERSE_02_PRE_CORTE.wav", mode="end", rel=-13, pan=0.0, st=0, eq="air",
         width_env=[(0, 0.3), (1, 1.1)], note="f665-670 latigazo: aire aspirado; la musica entra en el break"),
    dict(id="T17", t=669.5 * F, file="01_WHOOSHES/WHOOSH_03_AIRE_LIGERO.wav", mode="peak", rel=-10, pan=0.0, st=0, eq="air",
         note="f670 corte a la toma cenital"),
    # ---------------- ALEJAMIENTO, CAIDA DEL PUNTO E IMPACTO ----------------
    dict(id="Z01", t=721 * F, file="04_RISERS_REVERSE/REVERSE_02_PRE_CORTE.wav", mode="end", rel=-12, pan=0.0, st=0, eq="air",
         width_env=[(0, 0.3), (1, 1.2)], note="succion hacia el arranque del alejamiento (f721)"),
    dict(id="Z02", t=723 * F, file="04_RISERS_REVERSE/RISER_03_ZOOM_SPIN.wav", mode="start", rel=-8, pan=0.0, st=0, eq="air",
         rev=True, stretch=0.80, pitch_env=[(0, 3), (0.25, 1.5), (0.6, -3), (1, -10)],
         lp_env=[(0, 16000), (0.35, 9000), (0.7, 2600), (1, 650)], amp_env=[(0, -90), (0.22, -4), (0.26, 0), (0.45, -1.5), (1, -16)],
         width_env=[(0, 1.6), (0.5, 0.9), (1, 0.1)], note="f723-743 alejamiento: Doppler descendente, el aire se oscurece y el estereo se cierra"),
    dict(id="Z03", t=IMPACT - 0.055, file="04_RISERS_REVERSE/REVERSE_01_PREIMPACTO.wav", mode="end", rel=-13, pan=0.0, st=0, eq="air",
         pitch_env=[(0, 4), (1, -2)], note="f747-752 caida del punto: aire invertido que se corta justo antes del golpe"),
    dict(id="I01", t=IMPACT, file="02_IMPACTS/HIT_03_GRUA_PROTAGONISTA.wav", mode="attack", rel=-2, pan=0.0, st=0, eq="hit_sub", verb=-9,
         snap=0.03, note="f753 IMPACTO: subgrave fundido con el golpe de resolucion del tema"),
    dict(id="I02", t=IMPACT, file="02_IMPACTS/HIT_07_CIERRE_MARCA.wav", mode="attack", rel=-1.5, pan=0.0, st=-1, eq="hit", verb=-9,
         fade=(0.45, 0.2), snap=0.03, note="f753 cuerpo del impacto"),
    dict(id="I03", t=IMPACT, file="02_IMPACTS/HIT_04_METAL_MATE_SUTIL.wav", mode="attack", rel=-9, pan=0.0, st=-1.14, eq="metal", verb=-3,
         snap=0.03, note="f753 contacto metalico afinado a Mi (tonica del acorde final)"),
    dict(id="I05", t=IMPACT, file="02_IMPACTS/HIT_02_PUNCH_CON_CUERPO.wav", mode="attack", rel=-5, pan=0.0, st=-2, eq="pop", snap=0.03,
         note="f753 capa de cuerpo en medios (presencia del golpe en movil)"),
    dict(id="I06", t=IMPACT + 0.01, file="05_OUTRO_MARCA/LOGO_02_AIRE_SALIDA.wav", mode="start", rel=-15, pan=0.0, st=-1, eq="air",
         lp_env=[(0, 9000), (1, 2200)], amp_env=[(0, 0), (1, -12)], width_env=[(0, 1.4), (1, 0.8)],
         note="f753+ soplo de aire que acompana la cola, sin golpes nuevos"),
    dict(id="I04", t=IMPACT, file="05_OUTRO_MARCA/LOGO_04_CLACK_IDENTIDAD.wav", mode="attack", rel=-13, pan=0.0, st=0, eq="click", verb=-12,
         snap=0.03, note="f753 ataque definido del impacto"),
]


def _d(t0, t1, att, rel, g, m, a, why):
    return dict(t0=t0, t1=t1, att=att, rel=rel, db=(g, m, a), why=why)


DUCKS = [
    _d(0.300, 0.380, 0.004, 0.22, -3.0, -2.0, -1.0, "golpe zoom 1"),
    _d(31 * F + 0.03, 31 * F + 0.11, 0.004, 0.25, -2.5, -1.5, -1.0, "golpe zoom 2"),
    _d(83 * F, 83 * F + 0.08, 0.004, 0.22, -2.0, -1.0, -1.0, "DE GRUA"),
    _d(229.5 * F - 0.1, 229.5 * F + 0.1, 0.06, 0.2, 0.0, -1.0, -2.0, "corte 240"),
    _d(427 * F - 0.12, 430 * F + 0.1, 0.08, 0.25, 0.0, -1.5, -2.5, "maquinaria"),
    _d(582 * F, 582 * F + 0.08, 0.004, 0.25, -2.5, -1.0, -0.5, "CALIDAD"),
    _d(721 * F, 738 * F, 0.15, 0.25, 0.0, -1.0, -2.0, "alejamiento"),
    _d(IMPACT, IMPACT + 0.12, 0.002, 0.5, -2.5, -1.0, -0.5, "IMPACTO"),
]
