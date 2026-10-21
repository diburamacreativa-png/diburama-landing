# Hoja de cues v2 - ALSINA CHILE reel (25 fps, 25,24 s). SOLO AUDIO: la imagen no se toca.
# Tiempos verificados fotograma a fotograma sobre Alsina_Reel_Chile_ref_01.mp4.
#
# Campos basicos:
#   t      evento en segundos de VIDEO (fotograma / 25)
#   file   WAV del pack (ruta relativa a la raiz del pack)
#   mode   'attack' -> el pico del transitorio cae en t
#          'peak'   -> el maximo de la envolvente (whoosh) cae en t
#          'end'    -> el sonido termina en t (reverse / riser hacia el corte)
#          'start'  -> el sonido arranca en t
#   rel    nivel objetivo en dB relativo a la musica en ese instante
#          (pico de 100 ms ponderado K del SFX frente a la media ponderada K de
#          la musica en +-200 ms alrededor del evento)
#   pan    -1..+1 (equal power)            st   pitch fijo en semitonos
#   eq     preset de EQ correctiva         fade (inicio, duracion) de salida
# Campos de diseno (opcionales; listas de (fraccion 0..1, valor)):
#   rev      invierte el sonido            stretch  duracion objetivo (time-stretch)
#   pitch_env  semitonos variables (Doppler; cambia duracion)
#   lp_env / hp_env  corte del filtro en Hz   amp_env  dB
#   pan_env    paneo dinamico              width_env anchura estereo (mono-compatible)
#   verb       envio en dB al bus de resonancia del impacto

F = 1 / 25.0
IMPACT = 553 * F + 0.007   # f553 (22,12 s): el punto de la «i» llega al logotipo; ataque musical medido en 22,126 s

CUES = [
    # ---------------- 00:00 - 04:28  GANCHO ----------------
    dict(id="G01", t=0.22, file="01_WHOOSHES/WHOOSH_03_AIRE_LIGERO.wav", mode="peak", rel=-15, pan=0.0, st=0, eq="air",
         note="f0-5 apertura sobre la grua; arranca en f0 y culmina en la entrada de ¿Y"),
    dict(id="G02", t=6 * F, file="03_UI_POPS_CLICKS/UI_03_POP_TEXTO_SUAVE.wav", mode="attack", rel=-13, pan=-0.2, st=0, eq="pop",
         note="f6 «¿Y» aparece (izquierda)"),
    dict(id="G03", t=12 * F, file="03_UI_POPS_CLICKS/UI_03_POP_TEXTO_SUAVE.wav", mode="attack", rel=-14.5, pan=0.2, st=2, eq="pop",
         note="f12 «SI» aparece (derecha), mismo pop +2 st"),
    dict(id="G04", t=12 * F, file="01_WHOOSHES/WHOOSH_07_TRAZO_LINEA.wav", mode="start", rel=-19, pan=0.1, st=0, eq="air",
         note="f12-19 linea grafica curva se dibuja"),
    dict(id="G05", t=20 * F, file="02_IMPACTS/HIT_03_GRUA_PROTAGONISTA.wav", mode="attack", rel=-3, pan=0.0, st=0, eq="hit_sub", fade=(0.28, 0.17),
         note="f20 «NO» + fondo a blanco: golpe heroe del gancho"),
    dict(id="G06", t=20 * F, file="03_UI_POPS_CLICKS/UI_04_POP_TEXTO_PUNCH.wav", mode="attack", rel=-11.5, pan=0.0, st=-2, eq="pop",
         note="f20 capa de ataque del «NO»"),
    dict(id="G07", t=30 * F, file="03_UI_POPS_CLICKS/UI_02_TICK_MINIMO.wav", mode="attack", rel=-17.5, pan=0.1, st=0, eq="click",
         note="f30 «NECE»"),
    dict(id="G08", t=34 * F, file="03_UI_POPS_CLICKS/UI_02_TICK_MINIMO.wav", mode="attack", rel=-17, pan=0.1, st=1, eq="click",
         note="f34 «SITA» (acumulacion +1 st)"),
    dict(id="G09", t=38 * F, file="03_UI_POPS_CLICKS/UI_02_TICK_MINIMO.wav", mode="attack", rel=-16.5, pan=0.1, st=2, eq="click",
         note="f38 «RAS» (acumulacion +2 st)"),
    dict(id="G10", t=46 * F, file="02_IMPACTS/HIT_02_PUNCH_CON_CUERPO.wav", mode="attack", rel=-3, pan=0.0, st=0, eq="hit",
         note="f46 «GRUA» + fondo rojo"),
    dict(id="G11", t=46 * F, file="03_UI_POPS_CLICKS/UI_05_SNAP_PALABRA.wav", mode="attack", rel=-13, pan=0.0, st=0, eq="click",
         note="f46 capa de ataque de «GRUA»"),
    dict(id="G16", t=46 * F, file="02_IMPACTS/HIT_04_METAL_MATE_SUTIL.wav", mode="attack", rel=-9, pan=0.0, st=0, eq="metal",
         note="f46 capa metalica corta: «GRUA» con caracter industrial"),
    dict(id="G12", t=66 * F, file="01_WHOOSHES/WHOOSH_02_RAPIDO_LATERAL.wav", mode="peak", rel=-13.5, pan=0.0, st=-1, eq="air",
         note="f59-66 barrido vertical del panel; la musica remata «EN CADA MONTAJE?»"),
    dict(id="G13", t=72 * F, file="01_WHOOSHES/WHOOSH_07_TRAZO_LINEA.wav", mode="start", rel=-20, pan=-0.15, st=-2, eq="air",
         note="f72-80 linea alrededor del simbolo (motivo de linea, -2 st)"),
    dict(id="G14", t=107 * F, file="04_RISERS_REVERSE/REVERSE_02_PRE_CORTE.wav", mode="end", rel=-14, pan=0.0, st=0, eq="air",
         width_env=[(0, 0.3), (1, 1.1)], note="aire invertido que termina en el gran cambio de escena f107"),
    dict(id="G15", t=107 * F, file="01_WHOOSHES/WHOOSH_04_MOTION_MEDIO.wav", mode="peak", rel=-10, pan=0.0, st=0, eq="air",
         width_env=[(0, 1.2), (1, 0.6)], note="f107 corte a obra aerea: pico del whoosh en el corte"),
    dict(id="G17", t=107 * F, file="01_WHOOSHES/WHOOSH_05_GRAVE_CON_CUERPO.wav", mode="peak", rel=-14, pan=0.0, st=-2, eq="air_body",
         note="f107 cuerpo de aire grave bajo el whoosh (gran cambio de escena)"),
    # ---------------- 04:28 - 07:40  ALISPLAY MANUAL ----------------
    dict(id="P01", t=115 * F, file="01_WHOOSHES/WHOOSH_01_MICRO_SECO.wav", mode="peak", rel=-15, pan=0.0, st=0, eq="air",
         note="f113-117 «ALISPLAY» sube y se asienta"),
    dict(id="P02", t=124 * F, file="01_WHOOSHES/WHOOSH_01_MICRO_SECO.wav", mode="peak", rel=-16, pan=0.0, st=-1.5, eq="air",
         note="f122-127 «MANUAL» sube (mismo swish -1,5 st)"),
    # ---------------- 07:40 - 09:68  240 PLUS ----------------
    dict(id="P03", t=185 * F, file="01_WHOOSHES/WHOOSH_02_RAPIDO_LATERAL.wav", mode="peak", rel=-11, pan=0.0, st=0, eq="air",
         pan_env=[(0, -0.35), (1, 0.35)], note="f185 cambio de toma con barrido lateral"),
    dict(id="P04", t=189 * F, file="01_WHOOSHES/WHOOSH_01_MICRO_SECO.wav", mode="peak", rel=-16, pan=0.2, st=1, eq="air",
         note="f187-191 «240» entra desde la derecha"),
    dict(id="P05", t=197 * F, file="02_IMPACTS/HIT_01_PUNCH_TEXTO_SECO.wav", mode="attack", rel=-9.5, pan=0.0, st=0, eq="hit",
         note="f197 «PLUS» consolidado: hit seco"),
    dict(id="P06", t=197 * F, file="02_IMPACTS/HIT_04_METAL_MATE_SUTIL.wav", mode="attack", rel=-14, pan=0.0, st=2, eq="metal",
         note="f197 capa metalica del nombre de producto"),
    # ---------------- 09:68 - 12:92  DISEÑADO PARA / EDIFICACION CHILENA / 2,40 m ----------------
    dict(id="D01", t=242 * F, file="01_WHOOSHES/WHOOSH_05_GRAVE_CON_CUERPO.wav", mode="peak", rel=-6, pan=0.0, st=0, eq="air_body",
         width_env=[(0, 1.2), (1, 0.5)], note="f242 corte principal"),
    dict(id="D02", t=245 * F, file="03_UI_POPS_CLICKS/UI_03_POP_TEXTO_SUAVE.wav", mode="attack", rel=-14, pan=0.0, st=-1, eq="pop",
         note="f245 «DISEÑADO» se materializa"),
    dict(id="D03", t=251 * F, file="03_UI_POPS_CLICKS/UI_07_GLITCH_SUTIL.wav", mode="peak", rel=-17.5, pan=0.1, st=0, eq="click",
         note="f250-253 «PARA» entra en rojo con desenfoque glitch"),
    dict(id="D04", t=263 * F, file="03_UI_POPS_CLICKS/UI_05_SNAP_PALABRA.wav", mode="attack", rel=-16.5, pan=-0.1, st=0, eq="click",
         note="f263 «EDIFICACION»"),
    dict(id="D05", t=268 * F, file="03_UI_POPS_CLICKS/UI_04_POP_TEXTO_PUNCH.wav", mode="attack", rel=-14, pan=0.0, st=0, eq="pop",
         note="f268 «CHILENA»"),
    dict(id="D06", t=271 * F, file="03_UI_POPS_CLICKS/UI_01_CLICK_PRECISO.wav", mode="attack", rel=-19.5, pan=-0.1, st=0, eq="click",
         note="f271 contador 0,01 m arranca"),
    dict(id="D07", t=274 * F, file="03_UI_POPS_CLICKS/UI_01_CLICK_PRECISO.wav", mode="attack", rel=-19.5, pan=-0.1, st=0.5, eq="click",
         note="f274 contador 0,25 m"),
    dict(id="D08", t=277 * F, file="03_UI_POPS_CLICKS/UI_01_CLICK_PRECISO.wav", mode="attack", rel=-18.5, pan=-0.1, st=1, eq="click",
         note="f277 contador 0,91 m"),
    dict(id="D09", t=280 * F, file="03_UI_POPS_CLICKS/UI_01_CLICK_PRECISO.wav", mode="attack", rel=-18.5, pan=-0.1, st=1.5, eq="click",
         note="f280 contador 1,77 m"),
    dict(id="D10", t=283 * F, file="03_UI_POPS_CLICKS/UI_01_CLICK_PRECISO.wav", mode="attack", rel=-18.5, pan=-0.1, st=2, eq="click",
         note="f283 contador 2,27 m (desacelera)"),
    dict(id="D11", t=286 * F, file="02_IMPACTS/HIT_05_ACENTO_LIGERO.wav", mode="attack", rel=-10.5, pan=0.0, st=0, eq="hit",
         note="f286 la cota se fija en 2,40 m"),
    dict(id="D12", t=286 * F, file="02_IMPACTS/HIT_04_METAL_MATE_SUTIL.wav", mode="attack", rel=-15, pan=-0.1, st=5, eq="metal",
         note="f286 tope metalico de la medida (agudo, corto)"),
    # ---------------- 12:92 - 16:00  MENOS DEPENDENCIA DE GRUA ----------------
    dict(id="M01", t=323 * F, file="01_WHOOSHES/WHOOSH_04_MOTION_MEDIO.wav", mode="peak", rel=-6, pan=0.0, st=1, eq="air",
         pan_env=[(0, 0.3), (1, -0.3)], note="f320-329 barrido del brazo de grua en primer plano (pico f323)"),
    dict(id="M07", t=324 * F, file="01_WHOOSHES/WHOOSH_05_GRAVE_CON_CUERPO.wav", mode="peak", rel=-10, pan=0.0, st=-3, eq="air_body",
         note="f320-329 masa de aire de la maquinaria pasando por delante"),
    dict(id="M02", t=338 * F, file="03_UI_POPS_CLICKS/UI_02_TICK_MINIMO.wav", mode="attack", rel=-17.5, pan=0.15, st=0, eq="click",
         note="f338 «ME» entra"),
    dict(id="M03", t=348 * F, file="03_UI_POPS_CLICKS/UI_02_TICK_MINIMO.wav", mode="attack", rel=-18, pan=0.15, st=1, eq="click",
         note="f348 «NOS»"),
    dict(id="M04", t=352 * F, file="03_UI_POPS_CLICKS/UI_02_TICK_MINIMO.wav", mode="attack", rel=-17.5, pan=0.15, st=2, eq="click",
         note="f352 «DEPEN / DE»"),
    dict(id="M05", t=374 * F, file="02_IMPACTS/HIT_02_PUNCH_CON_CUERPO.wav", mode="attack", rel=-7, pan=0.0, st=-1, eq="hit",
         note="f374 «GRUA» parpadea a rojo: golpe mediano (misma familia que el GRUA del gancho)"),
    dict(id="M08", t=374 * F, file="02_IMPACTS/HIT_04_METAL_MATE_SUTIL.wav", mode="attack", rel=-13, pan=0.0, st=-2, eq="metal",
         note="f374 capa metalica de «GRUA» (eco del gancho, mas grave)"),
    dict(id="M06", t=382 * F, file="03_UI_POPS_CLICKS/UI_01_CLICK_PRECISO.wav", mode="attack", rel=-20, pan=0.0, st=-1, eq="click",
         note="f382 segundo parpadeo rojo"),
    # ---------------- 16:00 - 19:16  MONTAJE SIMPLE / ACABADOS DE CALIDAD ----------------
    dict(id="S01", t=400 * F, file="01_WHOOSHES/WHOOSH_04_MOTION_MEDIO.wav", mode="peak", rel=-11, pan=0.0, st=-1, eq="air",
         width_env=[(0, 1.2), (1, 0.6)], note="f400 corte a montaje"),
    dict(id="S02", t=406 * F, file="03_UI_POPS_CLICKS/UI_03_POP_TEXTO_SUAVE.wav", mode="attack", rel=-14.5, pan=-0.1, st=0, eq="pop",
         note="f406 «MONTAJE» aparece"),
    dict(id="S03", t=425 * F, file="02_IMPACTS/HIT_01_PUNCH_TEXTO_SECO.wav", mode="attack", rel=-9.5, pan=0.0, st=1, eq="hit",
         note="f425 «SIMPLE» completo: acento seco y corto"),
    dict(id="S04", t=425 * F, file="03_UI_POPS_CLICKS/UI_05_SNAP_PALABRA.wav", mode="attack", rel=-16.5, pan=0.0, st=1, eq="click",
         note="f425 capa snap de «SIMPLE»"),
    dict(id="S05", t=431 * F, file="03_UI_POPS_CLICKS/UI_05_SNAP_PALABRA.wav", mode="attack", rel=-19.5, pan=0.1, st=-1, eq="click",
         note="f431 «ACABADOS DE» empieza"),
    dict(id="S06", t=455 * F, file="02_IMPACTS/HIT_06_CALIDAD_CON_PESO.wav", mode="attack", rel=-1.5, pan=0.0, st=0, eq="hit",
         note="f455 «CALIDAD.» completo: acento con peso"),
    dict(id="S07", t=455 * F, file="03_UI_POPS_CLICKS/UI_04_POP_TEXTO_PUNCH.wav", mode="attack", rel=-14, pan=0.0, st=-2, eq="pop",
         note="f455 capa pop de «CALIDAD»"),
    dict(id="S08", t=478.5 * F, file="01_WHOOSHES/WHOOSH_03_AIRE_LIGERO.wav", mode="peak", rel=-11.5, pan=0.0, st=0, eq="air",
         width_env=[(0, 1.2), (1, 0.5)], note="f476-479 latigazo con desenfoque y corte a toma vertical"),
    # ---------------- 19:16 - 22:12  VIAJE DE CAMARA: giro -> alejamiento -> tension -> vacio ----------------
    dict(id="Z01", t=510 * F, file="04_RISERS_REVERSE/REVERSE_02_PRE_CORTE.wav", mode="end", rel=-10, pan=0.0, st=0, eq="air",
         width_env=[(0, 0.3), (1, 1.2)], note="succion de aire hacia el arranque del giro (f510)"),
    dict(id="Z02", t=516 * F, file="01_WHOOSHES/WHOOSH_06_SPIN_DRON.wav", mode="peak", rel=-5, pan=0.0, st=0, eq="air",
         pan_env=[(0, -0.45), (0.5, 0.0), (1, 0.45)], width_env=[(0, 0.8), (1, 1.2)],
         note="f509-520 giro acelerado: rotacion que barre de izquierda a derecha (pico f516)"),
    dict(id="Z03", t=519 * F, file="04_RISERS_REVERSE/RISER_03_ZOOM_SPIN.wav", mode="start", rel=-5, pan=0.0, st=0, eq="air",
         rev=True, stretch=0.80,
         pitch_env=[(0, 3), (0.25, 1.5), (0.6, -3), (1, -10)],
         lp_env=[(0, 16000), (0.35, 9000), (0.7, 2600), (1, 650)],
         amp_env=[(0, -8), (0.07, 0), (0.45, -1.5), (1, -16)],
         width_env=[(0, 1.6), (0.5, 0.9), (1, 0.1)],
         note="f519-537 ALEJAMIENTO: desplazamiento aereo con Doppler (+3 -> -10 st), el aire se oscurece y el estereo se cierra hacia la distancia"),
    dict(id="Z04", t=527 * F, file="01_WHOOSHES/WHOOSH_05_GRAVE_CON_CUERPO.wav", mode="peak", rel=-9, pan=0.0, st=-5, eq="air_body",
         pitch_env=[(0, 0), (1, -3)], note="f520-527 masa de aire grave mientras se forma el planeta (profundidad)"),
    dict(id="Z05", t=533.5 * F, file="01_WHOOSHES/WHOOSH_04_MOTION_MEDIO.wav", mode="peak", rel=-9, pan=0.0, st=-2, eq="air",
         pitch_env=[(0, 1), (1, -5)], lp_env=[(0, 12000), (1, 1500)], width_env=[(0, 1.2), (1, 0.2)],
         note="f533 ultimo tiron hacia atras antes del corte a rojo (Doppler descendente)"),
    dict(id="C01", t=534 * F, file="02_IMPACTS/HIT_07_CIERRE_MARCA.wav", mode="attack", rel=-10, pan=0.0, st=-2, eq="boom_far", fade=(0.35, 0.2),
         note="f534 corte a rojo: boom lejano y oscuro (se reserva la intensidad para el impacto del punto)"),
    dict(id="Z06", t=IMPACT - 0.07, file="04_RISERS_REVERSE/RISER_02_BUILD_CORTO.wav", mode="end", rel=-3, pan=0.0, st=0, eq="air",
         stretch=0.62, pitch_env=[(0, -2), (1, 4)], hp_env=[(0, 500), (1, 2400)], width_env=[(0, 0.4), (1, 1.3)],
         amp_env=[(0, -30), (0.11, 0), (1, 0)],
         note="f538-552 tension: riser ascendente del punto blanco hasta 70 ms antes del impacto (vacio)"),
    dict(id="Z07", t=IMPACT - 0.055, file="04_RISERS_REVERSE/REVERSE_01_PREIMPACTO.wav", mode="end", rel=-10, pan=0.0, st=0, eq="air",
         pitch_env=[(0, 4), (1, -2)], note="f547-552 caida acelerada del punto: aire invertido que se corta justo antes del golpe"),
    # ---------------- 22:12  IMPACTO DEL PUNTO DE LA «i» (maxima intensidad) ----------------
    dict(id="I01", t=IMPACT, file="02_IMPACTS/HIT_03_GRUA_PROTAGONISTA.wav", mode="attack", rel=-1, pan=0.0, st=0, eq="hit_sub", verb=-9,
         note="f553 IMPACTO: subgrave cinematografico, integrado con el golpe musical"),
    dict(id="I02", t=IMPACT, file="02_IMPACTS/HIT_07_CIERRE_MARCA.wav", mode="attack", rel=-4, pan=0.0, st=-1, eq="hit", verb=-9,
         fade=(0.45, 0.2), note="f553 cuerpo del impacto (150-300 Hz, se oye en movil)"),
    dict(id="I03", t=IMPACT, file="02_IMPACTS/HIT_04_METAL_MATE_SUTIL.wav", mode="attack", rel=-5, pan=0.0, st=-0.14, eq="metal", verb=-3,
         note="f553 capa metalica de precision, afinada a F (fundamental del acorde final)"),
    dict(id="I04", t=IMPACT, file="05_OUTRO_MARCA/LOGO_04_CLACK_IDENTIDAD.wav", mode="attack", rel=-8, pan=0.0, st=0, eq="click", verb=-12,
         note="f553 ataque definido del impacto"),
    dict(id="I05", t=IMPACT + 0.01, file="05_OUTRO_MARCA/LOGO_02_AIRE_SALIDA.wav", mode="start", rel=-16, pan=0.0, st=-1, eq="air",
         lp_env=[(0, 9000), (1, 2500)], amp_env=[(0, 0), (1, -10)], width_env=[(0, 1.4), (1, 0.8)],
         note="f553+ soplo de aire posterior: resonancia breve y elegante junto al bus de resonancia"),
    # ---------------- 22:28 - 25:24  DETALLES DEL LOGOTIPO ----------------
    dict(id="L01", t=557 * F, file="05_OUTRO_MARCA/LOGO_03_TICK_SIMBOLO.wav", mode="attack", rel=-15, pan=0.0, st=0, eq="click",
         note="f557 «x» + icono ALTIUS + «ASI SE CONSTRUYE EN» aparecen"),
    dict(id="L02", t=561 * F, file="03_UI_POPS_CLICKS/UI_09_BRUSH_TRAZO.wav", mode="start", rel=-19, pan=0.0, st=0, eq="air",
         lp_env=[(0, 6000), (1, 12000)], note="f561-566 «GRAN VIA» se revela: trazo de aire suave"),
    dict(id="L03", t=567 * F, file="05_OUTRO_MARCA/LOGO_01_CONFIRMACION_LIGERA.wav", mode="attack", rel=-16, pan=0.0, st=2.61, eq="pop",
         note="f567 icono ALTIUS completo y composicion asentada: confirmacion afinada a C (quinta del Fmaj7)"),
]

# Ducking SUAVE de la musica por bandas (grave <160 Hz, medios, agudos >2,5 kHz), en dB.
# t0..t1 meseta, att / rel en s.
def _d(t0, t1, att, rel, g, m, a, why):
    return dict(t0=t0, t1=t1, att=att, rel=rel, db=(g, m, a), why=why)


DUCKS = [
    _d(20 * F, 20 * F + 0.09, 0.006, 0.30, -3.0, -2.0, -1.5, "NO"),
    _d(46 * F, 46 * F + 0.09, 0.006, 0.28, -2.5, -1.5, -1.0, "GRUA"),
    _d(107 * F - 0.12, 107 * F + 0.12, 0.10, 0.30, 0.0, -1.5, -2.5, "whoosh 4,28"),
    _d(185 * F - 0.10, 185 * F + 0.10, 0.08, 0.25, 0.0, -1.0, -2.0, "whoosh 7,40"),
    _d(197 * F, 197 * F + 0.08, 0.006, 0.25, -2.0, -1.0, -0.5, "PLUS"),
    _d(242 * F - 0.12, 242 * F + 0.12, 0.10, 0.30, -1.0, -1.5, -3.0, "whoosh 9,68"),
    _d(286 * F, 286 * F + 0.06, 0.006, 0.22, -1.0, -0.5, -0.3, "2,40 m"),
    _d(323 * F - 0.12, 323 * F + 0.12, 0.10, 0.30, -1.0, -1.5, -3.0, "brazo de grua 12,92"),
    _d(374 * F, 374 * F + 0.08, 0.006, 0.25, -2.0, -1.0, -0.5, "GRUA roja"),
    _d(400 * F - 0.10, 400 * F + 0.10, 0.08, 0.25, 0.0, -1.0, -2.0, "whoosh 16,00"),
    _d(425 * F, 425 * F + 0.08, 0.006, 0.25, -2.0, -1.0, -0.5, "SIMPLE"),
    _d(455 * F, 455 * F + 0.09, 0.006, 0.30, -3.0, -1.5, -1.0, "CALIDAD"),
    _d(478.5 * F - 0.10, 478.5 * F + 0.10, 0.08, 0.25, 0.0, -1.0, -2.0, "whoosh 19,14"),
    _d(509 * F, 537 * F, 0.15, 0.25, -0.5, -1.5, -2.5, "viaje de camara 20,36-21,48"),
    _d(534 * F, 534 * F + 0.08, 0.006, 0.25, -1.5, -1.0, -0.5, "corte a rojo"),
    _d(538 * F, IMPACT - 0.13, 0.10, 0.05, 0.0, -1.0, -2.0, "riser del punto"),
    _d(IMPACT - 0.11, IMPACT - 0.006, 0.03, 0.004, -7.0, -7.0, -7.0, "VACIO previo al impacto"),
    _d(IMPACT, IMPACT + 0.12, 0.002, 0.50, -3.5, -1.5, -1.0, "IMPACTO"),
]
