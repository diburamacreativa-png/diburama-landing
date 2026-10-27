# Apertura nueva de VIDEO REEL CHILE_DEMO 6 (0 - 5,24 s). SOLO AUDIO.
# Desde f131 (5,24 s) el DEMO 6 es el DEMO 5 desde f213 adelantado 82 fotogramas (3,28 s):
# ahi se conserva la mezcla aprobada del DEMO 5 sin tocarla.
#
# Golpes de zoom medidos (alejamientos bruscos de escala):
#   f7  (0,28 s) escala 0,70  -> golpe 1
#   f23 (0,92 s) escala 0,84  -> golpe 2a (aparece «SIN»)
#   f31 (1,24 s) escala 0,84  -> golpe 2b (aparece «NECESIDAD»), el mas contundente
# Cada golpe se funde con el transitorio de la propia musica en ese fotograma:
H1 = 0.2613    # musica 0,2613 s (f7 visual 0,28)
H2A = 0.9376   # musica 0,9376 s (f23 visual 0,92)
H2B = 1.2069   # musica 1,2069 s (f31 visual 1,24)
MUSIC_IN = H1 - 0.004   # la musica entra con el primer zoom; antes, solo la subida de tension

F = 1 / 25.0
SHIFT = 3.28            # DEMO 6 = DEMO 5 - 3,28 s a partir de f131

CUES = [
    # ---------------- GOLPE 1 (f7) ----------------
    dict(id="O01", t=H1, file="04_RISERS_REVERSE/REVERSE_01_PREIMPACTO.wav", mode="end", rel=-11, pan=0.0, st=0, eq="air",
         width_env=[(0, 0.3), (1, 1.1)], note="f0-6 subida de tension: aire invertido que desemboca en el primer zoom"),
    dict(id="O02", t=H1 + 0.008, file="01_WHOOSHES/WHOOSH_01_MICRO_SECO.wav", mode="peak", rel=-9, pan=0.0, st=-1, eq="air",
         width_env=[(0, 1.2), (1, 0.6)], note="f7 whoosh corto y rapido del zoom"),
    dict(id="O03", t=H1, file="02_IMPACTS/HIT_02_PUNCH_CON_CUERPO.wav", mode="attack", rel=-6.5, pan=0.0, st=0, eq="hit",
         note="f7 golpe grave y seco del primer zoom (fundido con el golpe musical)"),
    dict(id="O04", t=H1, file="02_IMPACTS/HIT_04_METAL_MATE_SUTIL.wav", mode="attack", rel=-13, pan=0.0, st=0, eq="metal",
         note="f7 contacto metalico discreto (caracter industrial)"),
    # ---------------- GOLPE 2 (f23 -> f31) ----------------
    dict(id="O05", t=H2A, file="04_RISERS_REVERSE/RISER_01_MICRO.wav", mode="end", rel=-13, pan=0.0, st=0, eq="air",
         hp_env=[(0, 600), (1, 2200)], width_env=[(0, 0.4), (1, 1.1)],
         note="f12-23 micro-riser: tension hacia el segundo zoom"),
    dict(id="O06", t=H2A + 0.006, file="01_WHOOSHES/WHOOSH_01_MICRO_SECO.wav", mode="peak", rel=-10, pan=0.0, st=0, eq="air",
         note="f23 whoosh corto del zoom 2a"),
    dict(id="O07", t=H2A, file="02_IMPACTS/HIT_01_PUNCH_TEXTO_SECO.wav", mode="attack", rel=-8, pan=0.0, st=0, eq="hit",
         note="f23 golpe seco del zoom 2a: aparece «SIN»"),
    dict(id="O08", t=H2A, file="03_UI_POPS_CLICKS/UI_04_POP_TEXTO_PUNCH.wav", mode="attack", rel=-12, pan=-0.1, st=-2, eq="pop",
         note="f23 capa de ataque de «SIN»"),
    dict(id="O09", t=H2B, file="04_RISERS_REVERSE/REVERSE_01_PREIMPACTO.wav", mode="end", rel=-10, pan=0.0, st=1, eq="air",
         stretch=0.25, width_env=[(0, 0.3), (1, 1.2)],
         note="f25-31 aire invertido entre los dos zooms: la tension se tensa hacia el remate"),
    dict(id="O10", t=H2B + 0.008, file="01_WHOOSHES/WHOOSH_02_RAPIDO_LATERAL.wav", mode="peak", rel=-8, pan=0.0, st=-1, eq="air",
         width_env=[(0, 1.3), (1, 0.6)], note="f31 whoosh rapido del zoom 2b"),
    dict(id="O11", t=H2B, file="02_IMPACTS/HIT_03_GRUA_PROTAGONISTA.wav", mode="attack", rel=-1.5, pan=0.0, st=0, eq="hit_sub", fade=(0.28, 0.17),
         note="f31 GOLPE 2b: el mas contundente de la apertura (mismo golpe heroe que «SIN» en el DEMO 5)"),
    dict(id="O12", t=H2B, file="02_IMPACTS/HIT_04_METAL_MATE_SUTIL.wav", mode="attack", rel=-10, pan=0.0, st=0, eq="metal",
         note="f31 capa metalica del remate"),
    dict(id="O13", t=H2B, file="03_UI_POPS_CLICKS/UI_05_SNAP_PALABRA.wav", mode="attack", rel=-13, pan=0.1, st=0, eq="click",
         note="f31 aparece «NECESIDAD»"),
    # ---------------- LINEA, BARRIDO Y DE GRUA (f46 - f130) ----------------
    dict(id="O14", t=46 * F, file="01_WHOOSHES/WHOOSH_07_TRAZO_LINEA.wav", mode="start", rel=-19, pan=-0.15, st=0, eq="air",
         note="f46-78 linea roja rodea el texto (motivo de linea)"),
    dict(id="O15", t=83 * F, file="04_RISERS_REVERSE/REVERSE_02_PRE_CORTE.wav", mode="end", rel=-14, pan=0.0, st=0, eq="air",
         width_env=[(0, 0.3), (1, 1.1)], note="f78-82 barrido de camara: aire aspirado hacia el corte"),
    dict(id="O16", t=82.5 * F, file="01_WHOOSHES/WHOOSH_04_MOTION_MEDIO.wav", mode="peak", rel=-9, pan=0.0, st=-1, eq="air",
         pan_env=[(0, -0.3), (1, 0.3)], width_env=[(0, 1.2), (1, 0.6)], note="f78-83 barrido con desenfoque hacia DE GRUA"),
    dict(id="O17", t=83 * F, file="02_IMPACTS/HIT_02_PUNCH_CON_CUERPO.wav", mode="attack", rel=-6.5, pan=0.0, st=0, eq="hit",
         note="f83 «DE GRUA» llega con el corte (mismo tratamiento que en el DEMO 5)"),
    dict(id="O18", t=83 * F, file="03_UI_POPS_CLICKS/UI_05_SNAP_PALABRA.wav", mode="attack", rel=-13, pan=0.1, st=0, eq="click",
         note="f83 capa de ataque de «GRUA»"),
    dict(id="O19", t=83 * F, file="02_IMPACTS/HIT_04_METAL_MATE_SUTIL.wav", mode="attack", rel=-9, pan=0.0, st=0, eq="metal",
         note="f83 capa metalica de «GRUA»"),
]


def _d(t0, t1, att, rel, g, m, a, why):
    return dict(t0=t0, t1=t1, att=att, rel=rel, db=(g, m, a), why=why)


DUCKS = [
    _d(H1, H1 + 0.09, 0.003, 0.28, -3.0, -2.0, -1.5, "golpe 1"),
    _d(H2A, H2A + 0.08, 0.004, 0.22, -2.0, -1.0, -0.5, "golpe 2a"),
    _d(H2B, H2B + 0.10, 0.004, 0.32, -3.5, -2.5, -1.5, "golpe 2b"),
    _d(83 * F - 0.10, 83 * F - 0.004, 0.08, 0.004, 0.0, -1.0, -2.0, "barrido hacia DE GRUA"),
    _d(83 * F, 83 * F + 0.09, 0.004, 0.28, -3.0, -1.5, -1.0, "DE GRUA"),
]
