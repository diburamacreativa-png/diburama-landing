# Acentos percusivos y transiciones para «Build Momentum (1)» sobre VIDEO REEL CHILE_DEMO 6.
# Todos los eventos se comprobaron fotograma a fotograma (ver INFORME). Jerarquia:
#   FUERTE  golpes de camara del inicio, cortes con latigazo, punto de la «i»
#   MEDIO   cortes secundarios, llegada de los textos principales, barrido del cubo
#   LIGERO  textos secundarios (pop/tick discreto) o nada
# Familia unica: impactos del pack afinados a Sol (tonalidad del tema): las colas de HIT_02/03/06/07
# terminan en ~89 Hz (Fa+40c) -> +1,6 st = Sol 98 Hz; HIT_01 -> Re (quinta); metal HIT_04 -> Sol.
# 'snap': el ataque se funde con el transitorio musical mas cercano (+-snap s) si existe, para no
# producir doble ataque; 'early' limita cuanto puede adelantarse a la imagen (por defecto 25 ms).

F = 1 / 25.0
IMPACT = 753 * F + 0.010   # f753: el punto de la «i» se asienta en «Alsina» (30,120-30,160 s)
G = 1.6        # semitonos: impactos con cuerpo -> Sol
G_TXT = -0.8   # HIT_01 -> Re
G_MET = 1.39   # HIT_04 metal -> Sol

CUES = [
    # ================= INICIO: DOS IMPULSOS DE CAMARA (+ salto intermedio) =================
    # (niveles relativos a la musica de la intro, que suena con paso alto: sin bombo ni bajo)
    dict(id="Z1w", t=7 * F - 0.008, file="01_WHOOSHES/WHOOSH_01_MICRO_SECO.wav", mode="peak", rel=-8, pan=0.0, st=0, eq="air",
         note="f7 impulso 1: aire corto que desemboca en el golpe"),
    dict(id="Z1h", t=7 * F, file="02_IMPACTS/HIT_02_PUNCH_CON_CUERPO.wav", mode="attack", rel=2, pan=0.0, st=G, eq="hit",
         fade=(0.22, 0.12), level="hit", tier="FUERTE", note="f7 impulso de camara 1 (alejamiento brusco) + MONTAJES entra volando"),
    dict(id="Z1p", t=7 * F, file="02_IMPACTS/HIT_01_PUNCH_TEXTO_SECO.wav", mode="attack", rel=-5, pan=0.0, st=G_TXT, eq="pop",
         note="f7 capa de ataque en medios (se oye en movil)"),
    dict(id="Z2a", t=23 * F, file="02_IMPACTS/HIT_01_PUNCH_TEXTO_SECO.wav", mode="attack", rel=-2, pan=0.0, st=G_TXT, eq="hit", snap=0.04,
         level="hit", tier="MEDIO", note="f23 salto intermedio del zoom + entra «SIN» (mas ligero: prepara el segundo impulso)"),
    dict(id="Z2r", t=31 * F - 0.004, file="04_RISERS_REVERSE/REVERSE_01_PREIMPACTO.wav", mode="end", rel=-11, pan=0.0, st=1, eq="air",
         stretch=0.24, amp_env=[(0, -40), (0.4, -4), (1, 0)], width_env=[(0, 0.3), (1, 1.1)],
         note="f25-31 aspiracion breve hacia el impulso 2"),
    dict(id="Z2w", t=31 * F - 0.012, file="01_WHOOSHES/WHOOSH_02_RAPIDO_LATERAL.wav", mode="peak", rel=-8, pan=0.0, st=-1, eq="air",
         note="f31 impulso 2: aire rapido"),
    dict(id="Z2b", t=31 * F, file="02_IMPACTS/HIT_03_GRUA_PROTAGONISTA.wav", mode="attack", rel=3, pan=0.0, st=G, eq="hit_sub",
         fade=(0.26, 0.16), level="hit", tier="FUERTE", note="f31 impulso de camara 2 + entra «NECESIDAD» (el mas contundente del inicio)"),
    dict(id="Z2p", t=31 * F, file="02_IMPACTS/HIT_01_PUNCH_TEXTO_SECO.wav", mode="attack", rel=-4, pan=0.0, st=G_TXT, eq="pop",
         note="f31 capa de ataque en medios"),
    # ================= CORTES, TEXTOS Y MOVIMIENTOS =================
    dict(id="C1w", t=82.6 * F, file="01_WHOOSHES/WHOOSH_04_MOTION_MEDIO.wav", mode="peak", rel=-10, pan=0.0, st=-1, eq="air",
         pan_env=[(0, -0.3), (1, 0.3)], note="f79-82 latigazo con desenfoque hacia el corte"),
    dict(id="C1h", t=83 * F, file="02_IMPACTS/HIT_02_PUNCH_CON_CUERPO.wav", mode="attack", rel=-3, pan=0.0, st=G, eq="hit",
         fade=(0.2, 0.12), snap=0.025, level="hit", tier="FUERTE", note="f83 llegada al nuevo plano: «DE GRÚA»"),
    dict(id="C1p", t=83 * F, file="02_IMPACTS/HIT_01_PUNCH_TEXTO_SECO.wav", mode="attack", rel=-10, pan=0.0, st=G_TXT, eq="pop", snap=0.025,
         note="f83 capa de ataque en medios"),
    dict(id="C2w", t=130.7 * F, file="01_WHOOSHES/WHOOSH_02_RAPIDO_LATERAL.wav", mode="peak", rel=-11, pan=0.0, st=0, eq="air",
         pan_env=[(0, 0.35), (1, -0.35)], note="f127-130 paneo que acelera hacia el corte"),
    dict(id="C2h", t=131 * F, file="02_IMPACTS/HIT_05_ACENTO_LIGERO.wav", mode="attack", rel=-6, pan=0.0, st=0, eq="hit",
         level="hit", tier="MEDIO", note="f131 corte a ALISPLAY: la musica cae a la subida filtrada en el mismo instante"),
    dict(id="C3p", t=141 * F, file="03_UI_POPS_CLICKS/UI_04_POP_TEXTO_PUNCH.wav", mode="attack", rel=-2, pan=0.0, st=0, eq="click",
         level="hit", tier="LIGERO", note="f141 «ALISPLAY» se asienta"),
    dict(id="C4p", t=151 * F, file="03_UI_POPS_CLICKS/UI_05_SNAP_PALABRA.wav", mode="attack", rel=-7, pan=0.0, st=0, eq="click",
         level="hit", tier="LIGERO", note="f151 «MANUAL» se asienta"),
    dict(id="C5r", t=9.171, file="04_RISERS_REVERSE/REVERSE_02_PRE_CORTE.wav", mode="end", rel=-14, pan=0.0, st=0, eq="air",
         width_env=[(0, 0.3), (1, 1.1)], note="f224-229 aspiracion hacia el drop"),
    dict(id="C5w", t=229.6 * F, file="01_WHOOSHES/WHOOSH_05_GRAVE_CON_CUERPO.wav", mode="peak", rel=-10, pan=0.0, st=0, eq="air_body",
         note="f227-229 latigazo hacia 240 PLUS"),
    dict(id="C5h", t=230 * F, file="02_IMPACTS/HIT_03_GRUA_PROTAGONISTA.wav", mode="attack", rel=-6, pan=0.0, st=G, eq="hit_sub",
         fade=(0.25, 0.15), snap=0.04, early=0.030, level="hit", tier="FUERTE",
         note="f230 corte a 240 PLUS = drop del tema: el golpe refuerza el transitorio del drop (sin doble ataque)"),
    dict(id="C6p", t=243 * F, file="03_UI_POPS_CLICKS/UI_05_SNAP_PALABRA.wav", mode="attack", rel=-9, pan=0.0, st=0, eq="click",
         level="hit", tier="LIGERO", note="f243 «PLUS» completa su caida"),
    dict(id="C7w", t=297.7 * F, file="01_WHOOSHES/WHOOSH_03_AIRE_LIGERO.wav", mode="peak", rel=-12, pan=0.0, st=0, eq="air",
         note="f298 corte a DISEÑADO PARA (el texto sube y se asienta en f304)"),
    dict(id="C7h", t=298 * F, file="02_IMPACTS/HIT_05_ACENTO_LIGERO.wav", mode="attack", rel=-7, pan=0.0, st=0, eq="hit",
         level="hit", tier="MEDIO", note="f298 corte a «DISEÑADO PARA»"),
    dict(id="C8p", t=341 * F, file="03_UI_POPS_CLICKS/UI_04_POP_TEXTO_PUNCH.wav", mode="attack", rel=-4, pan=0.0, st=0, eq="click",
         level="hit", tier="LIGERO", note="f341 «EDIFICACIÓN» aparece"),
    dict(id="C9p", t=393 * F, file="03_UI_POPS_CLICKS/UI_01_CLICK_PRECISO.wav", mode="attack", rel=-13, pan=0.0, st=0, eq="click", snap=0.04,
         level="hit", tier="LIGERO", note="f393 el contador se detiene en 2,40 m"),
    dict(id="C10w", t=429 * F, file="01_WHOOSHES/WHOOSH_05_GRAVE_CON_CUERPO.wav", mode="peak", rel=-8, pan=0.0, st=-1, eq="air_body",
         pan_env=[(0, 0.4), (1, -0.4)], note="f425-433 el cubo de la grua barre el plano (der -> izq); corte oculto en f430"),
    dict(id="C10b", t=428 * F, file="01_WHOOSHES/WHOOSH_04_MOTION_MEDIO.wav", mode="peak", rel=-13, pan=0.0, st=1, eq="air",
         pan_env=[(0, 0.4), (1, -0.4)], note="f428 aire del barrido"),
    dict(id="C11m", t=503 * F, file="02_IMPACTS/HIT_04_METAL_MATE_SUTIL.wav", mode="attack", rel=-13, pan=0.0, st=G_MET, eq="metal",
         snap=0.012, level="hit", tier="LIGERO", note="f503 «GRÚA» destella en rojo (cae en el pulso)"),
    dict(id="C12w", t=544.7 * F, file="01_WHOOSHES/WHOOSH_03_AIRE_LIGERO.wav", mode="peak", rel=-12, pan=0.0, st=-1, eq="air",
         note="f545 corte a MONTAJE SIMPLE"),
    dict(id="C13h", t=563 * F, file="02_IMPACTS/HIT_01_PUNCH_TEXTO_SECO.wav", mode="attack", rel=-11, pan=0.0, st=G_TXT, eq="hit",
         snap=0.03, level="hit", tier="MEDIO", note="f563 «SIMPLE» aterriza = cambio a Do del tema"),
    dict(id="C14h", t=582 * F, file="02_IMPACTS/HIT_06_CALIDAD_CON_PESO.wav", mode="attack", rel=-6, pan=0.0, st=G, eq="hit",
         fade=(0.22, 0.14), level="hit", tier="MEDIO", note="f582 «CALIDAD.» aterriza"),
    dict(id="C15r", t=670 * F - 0.006, file="04_RISERS_REVERSE/REVERSE_02_PRE_CORTE.wav", mode="end", rel=-16, pan=0.0, st=0, eq="air",
         width_env=[(0, 0.3), (1, 1.1)], note="f664-669 aspiracion hacia el corte"),
    dict(id="C15w", t=669.6 * F, file="01_WHOOSHES/WHOOSH_02_RAPIDO_LATERAL.wav", mode="peak", rel=-12, pan=0.0, st=0, eq="air",
         note="f668-669 latigazo hacia la toma cenital"),
    dict(id="C15h", t=670 * F, file="02_IMPACTS/HIT_02_PUNCH_CON_CUERPO.wav", mode="attack", rel=-6, pan=0.0, st=G, eq="hit",
         fade=(0.2, 0.12), level="hit", tier="FUERTE", note="f670 corte a cenital: la bateria del tema se retira en el mismo instante"),
    # ================= CIERRE: ALEJAMIENTO, IRIS, PUNTO DE LA «i» =================
    dict(id="Z01", t=737.5 * F, file="04_RISERS_REVERSE/RISER_03_ZOOM_SPIN.wav", mode="end", rel=-10, pan=0.0, st=0, eq="air",
         stretch=1.25, lp_env=[(0, 2500), (0.6, 7000), (1, 14000)], amp_env=[(0, -30), (0.5, -8), (1, 0)],
         width_env=[(0, 0.5), (1, 1.4)], note="f708-737 alejamiento que acelera hasta el cierre del iris"),
    dict(id="Z02", t=738 * F, file="05_OUTRO_MARCA/LOGO_03_TICK_SIMBOLO.wav", mode="attack", rel=-9, pan=0.0, st=0, eq="click",
         level="hit", tier="LIGERO", note="f738 negro: nace el punto (cuadrado blanco)"),
    dict(id="Z03", t=IMPACT - 0.010, file="04_RISERS_REVERSE/REVERSE_01_PREIMPACTO.wav", mode="end", rel=-14, pan=0.0, st=0, eq="air",
         pitch_env=[(0, 3), (1, -2)], amp_env=[(0, -30), (0.5, -6), (1, 0)],
         note="f738-752 el punto cae y se encoge: aire invertido que termina justo antes del golpe"),
    dict(id="I01", t=IMPACT, file="02_IMPACTS/HIT_07_CIERRE_MARCA.wav", mode="attack", rel=-2, pan=0.0, st=G, eq="hit", verb=-12,
         snap=0.012, level="hit", tier="ANCLA", note="f753 PUNTO DE LA «i»: cuerpo del golpe final, fundido con el golpe del tema"),
    dict(id="I02", t=IMPACT, file="02_IMPACTS/HIT_03_GRUA_PROTAGONISTA.wav", mode="attack", rel=-5, pan=0.0, st=G, eq="hit_sub",
         fade=(0.4, 0.25), snap=0.012, note="f753 subgrave controlado (afinado con el Sol del acorde)"),
    dict(id="I03", t=IMPACT, file="02_IMPACTS/HIT_04_METAL_MATE_SUTIL.wav", mode="attack", rel=-12, pan=0.0, st=G_MET, eq="metal", verb=-8,
         snap=0.012, note="f753 contacto metalico en Sol: definicion en movil"),
    dict(id="I04", t=IMPACT, file="05_OUTRO_MARCA/LOGO_04_CLACK_IDENTIDAD.wav", mode="attack", rel=-15, pan=0.0, st=0, eq="click",
         snap=0.012, note="f753 ataque seco del golpe"),
    dict(id="I05", t=IMPACT + 0.012, file="05_OUTRO_MARCA/LOGO_02_AIRE_SALIDA.wav", mode="start", rel=-17, pan=0.0, st=-1, eq="air",
         lp_env=[(0, 8000), (1, 2000)], amp_env=[(0, -3), (0.3, 0), (1, -14)], width_env=[(0, 1.3), (1, 0.8)],
         note="f753+ aire que acompaña la cola, sin golpes nuevos"),
]


def _d(t0, t1, att, rel, g, m, a, why):
    return dict(t0=t0, t1=t1, att=att, rel=rel, db=(g, m, a), why=why)


# Bajadas breves de la musica por bandas (grave, medios, agudos) para dar sitio a los golpes
DUCKS = [
    _d(7 * F, 7 * F + 0.08, 0.004, 0.20, -3.0, -2.0, -1.0, "impulso 1"),
    _d(23 * F, 23 * F + 0.05, 0.004, 0.15, -1.5, -1.0, -0.5, "salto SIN"),
    _d(31 * F, 31 * F + 0.10, 0.004, 0.24, -3.0, -2.0, -1.0, "impulso 2"),
    _d(83 * F, 83 * F + 0.08, 0.004, 0.20, -2.0, -1.5, -1.0, "DE GRUA"),
    _d(429 * F - 0.12, 429 * F + 0.10, 0.08, 0.22, 0.0, -1.5, -2.5, "barrido del cubo"),
    _d(582 * F, 582 * F + 0.08, 0.004, 0.22, -2.0, -1.0, -0.5, "CALIDAD"),
    _d(670 * F, 670 * F + 0.08, 0.004, 0.22, -1.5, -1.0, -0.5, "corte a cenital"),
    # vacio antes del golpe final: al cerrarse el iris (f738, pantalla negra) la musica se retira
    # mientras cae el punto y vuelve entera justo antes del ataque (el golpe del tema queda intacto)
    _d(738 * F + 0.02, IMPACT - 0.010, 0.05, 0.006, -3.0, -6.0, -7.0, "vacio mientras cae el punto"),
    _d(IMPACT, IMPACT + 0.12, 0.002, 0.45, -2.5, -1.0, -0.5, "punto de la i"),
]
