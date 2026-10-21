# Hoja de cues final - ALSINA CHILE reel (25 fps, 25,24 s)
# Tiempos verificados fotograma a fotograma sobre Alsina_Reel_Chile_ref_01.mp4.
#
# Campos:
#   t      evento en segundos de VIDEO (fotograma / 25 salvo indicacion)
#   file   WAV del pack (ruta relativa a la raiz del pack)
#   mode   'attack' -> el pico del transitorio cae en t
#          'peak'   -> el maximo de la envolvente (whoosh) cae en t
#          'end'    -> el sonido termina en t (reverse / riser hacia el corte)
#          'start'  -> el sonido arranca en t (trazos de linea)
#   rel    nivel objetivo en dB relativo a la musica en ese instante
#          (pico de 100 ms ponderado K del SFX frente a la media ponderada K de
#          la musica en +-200 ms alrededor del evento)
#   pan    -1..+1 (equal power, siempre moderado)
#   st     variacion de pitch en semitonos (resample: cambia tono y longitud)
#   eq     preset de EQ correctiva
#   fade   (inicio, duracion) de fundido de salida en s, o None
#   note   descripcion visual

F = 1 / 25.0

CUES = [
    # ---------------- 00:00 - 04:28  GANCHO ----------------
    dict(id="G01", t=0.22, file="01_WHOOSHES/WHOOSH_03_AIRE_LIGERO.wav", mode="peak", rel=-17, pan=0.0, st=0, eq="air", fade=None,
         note="f0-5 apertura sobre la grua; arranca en f0 y culmina en la entrada de ¿Y"),
    dict(id="G02", t=6 * F, file="03_UI_POPS_CLICKS/UI_03_POP_TEXTO_SUAVE.wav", mode="attack", rel=-14.5, pan=-0.2, st=0, eq="pop", fade=None,
         note="f6 «¿Y» aparece (izquierda)"),
    dict(id="G03", t=12 * F, file="03_UI_POPS_CLICKS/UI_03_POP_TEXTO_SUAVE.wav", mode="attack", rel=-16, pan=0.2, st=2, eq="pop", fade=None,
         note="f12 «SI» aparece (derecha), mismo pop +2 st"),
    dict(id="G04", t=12 * F, file="01_WHOOSHES/WHOOSH_07_TRAZO_LINEA.wav", mode="start", rel=-21, pan=0.1, st=0, eq="air", fade=None,
         note="f12-19 linea grafica curva se dibuja"),
    dict(id="G05", t=20 * F, file="02_IMPACTS/HIT_03_GRUA_PROTAGONISTA.wav", mode="attack", rel=-3.5, pan=0.0, st=0, eq="hit_sub", fade=(0.28, 0.17),
         note="f20 «NO» + fondo a blanco: golpe heroe del gancho"),
    dict(id="G06", t=20 * F, file="03_UI_POPS_CLICKS/UI_04_POP_TEXTO_PUNCH.wav", mode="attack", rel=-12, pan=0.0, st=-2, eq="pop", fade=None,
         note="f20 capa de ataque para definir el «NO» sobre el bajo"),
    dict(id="G07", t=30 * F, file="03_UI_POPS_CLICKS/UI_02_TICK_MINIMO.wav", mode="attack", rel=-18.5, pan=0.1, st=0, eq="click", fade=None,
         note="f30 «NECE»"),
    dict(id="G08", t=34 * F, file="03_UI_POPS_CLICKS/UI_02_TICK_MINIMO.wav", mode="attack", rel=-18, pan=0.1, st=1, eq="click", fade=None,
         note="f34 «SITA» (acumulacion +1 st)"),
    dict(id="G09", t=38 * F, file="03_UI_POPS_CLICKS/UI_02_TICK_MINIMO.wav", mode="attack", rel=-17.5, pan=0.1, st=2, eq="click", fade=None,
         note="f38 «RAS» (acumulacion +2 st)"),
    dict(id="G10", t=46 * F, file="02_IMPACTS/HIT_02_PUNCH_CON_CUERPO.wav", mode="attack", rel=-5.5, pan=0.0, st=0, eq="hit", fade=None,
         note="f46 «GRUA» + fondo rojo"),
    dict(id="G11", t=46 * F, file="03_UI_POPS_CLICKS/UI_05_SNAP_PALABRA.wav", mode="attack", rel=-14.5, pan=0.0, st=0, eq="click", fade=None,
         note="f46 capa de ataque de «GRUA»"),
    dict(id="G12", t=66 * F, file="01_WHOOSHES/WHOOSH_02_RAPIDO_LATERAL.wav", mode="peak", rel=-16, pan=0.0, st=-1, eq="air", fade=None,
         note="f59-66 barrido vertical del panel; la musica remata «EN CADA MONTAJE?» en 2,74 s"),
    dict(id="G13", t=72 * F, file="01_WHOOSHES/WHOOSH_07_TRAZO_LINEA.wav", mode="start", rel=-22, pan=-0.15, st=-2, eq="air", fade=None,
         note="f72-80 linea alrededor del simbolo (motivo de linea, -2 st)"),
    dict(id="G14", t=107 * F, file="04_RISERS_REVERSE/REVERSE_02_PRE_CORTE.wav", mode="end", rel=-17, pan=0.0, st=0, eq="air", fade=None,
         note="aire invertido que termina en el gran cambio de escena f107"),
    dict(id="G15", t=107 * F, file="01_WHOOSHES/WHOOSH_04_MOTION_MEDIO.wav", mode="peak", rel=-13, pan=0.0, st=0, eq="air", fade=None,
         note="f107 corte a obra aerea: pico del whoosh en el corte"),
    # ---------------- 04:28 - 07:40  ALISPLAY MANUAL ----------------
    dict(id="P01", t=115 * F, file="01_WHOOSHES/WHOOSH_01_MICRO_SECO.wav", mode="peak", rel=-17, pan=0.0, st=0, eq="air", fade=None,
         note="f113-117 «ALISPLAY» sube y se asienta"),
    dict(id="P02", t=124 * F, file="01_WHOOSHES/WHOOSH_01_MICRO_SECO.wav", mode="peak", rel=-18, pan=0.0, st=-1.5, eq="air", fade=None,
         note="f122-127 «MANUAL» sube (mismo swish -1,5 st)"),
    # ---------------- 07:40 - 09:68  240 PLUS ----------------
    dict(id="P03", t=185 * F, file="01_WHOOSHES/WHOOSH_02_RAPIDO_LATERAL.wav", mode="peak", rel=-14, pan=0.0, st=0, eq="air", fade=None,
         note="f185 cambio de toma con barrido"),
    dict(id="P04", t=189 * F, file="01_WHOOSHES/WHOOSH_01_MICRO_SECO.wav", mode="peak", rel=-18, pan=0.2, st=1, eq="air", fade=None,
         note="f187-191 «240» entra desde la derecha"),
    dict(id="P05", t=197 * F, file="02_IMPACTS/HIT_01_PUNCH_TEXTO_SECO.wav", mode="attack", rel=-8, pan=0.0, st=0, eq="hit", fade=None,
         note="f197 «PLUS» consolidado (ultima letra asentada): hit seco"),
    # ---------------- 09:68 - 12:92  DISEÑADO PARA / EDIFICACION CHILENA / 2,40 m ----------------
    dict(id="D01", t=242 * F, file="01_WHOOSHES/WHOOSH_05_GRAVE_CON_CUERPO.wav", mode="peak", rel=-14, pan=0.0, st=0, eq="air_body", fade=None,
         note="f242 corte principal"),
    dict(id="D02", t=245 * F, file="03_UI_POPS_CLICKS/UI_03_POP_TEXTO_SUAVE.wav", mode="attack", rel=-15.5, pan=0.0, st=-1, eq="pop", fade=None,
         note="f245 «DISEÑADO» se materializa"),
    dict(id="D03", t=251 * F, file="03_UI_POPS_CLICKS/UI_07_GLITCH_SUTIL.wav", mode="peak", rel=-19, pan=0.1, st=0, eq="click", fade=None,
         note="f250-253 «PARA» entra en rojo con desenfoque glitch"),
    dict(id="D04", t=263 * F, file="03_UI_POPS_CLICKS/UI_05_SNAP_PALABRA.wav", mode="attack", rel=-18, pan=-0.1, st=0, eq="click", fade=None,
         note="f263 «EDIFICACION»"),
    dict(id="D05", t=268 * F, file="03_UI_POPS_CLICKS/UI_04_POP_TEXTO_PUNCH.wav", mode="attack", rel=-15.5, pan=0.0, st=0, eq="pop", fade=None,
         note="f268 «CHILENA»"),
    dict(id="D06", t=271 * F, file="03_UI_POPS_CLICKS/UI_01_CLICK_PRECISO.wav", mode="attack", rel=-20.5, pan=-0.1, st=0, eq="click", fade=None,
         note="f271 contador 0,01 m arranca"),
    dict(id="D07", t=274 * F, file="03_UI_POPS_CLICKS/UI_01_CLICK_PRECISO.wav", mode="attack", rel=-20.5, pan=-0.1, st=0.5, eq="click", fade=None,
         note="f274 contador 0,25 m"),
    dict(id="D08", t=277 * F, file="03_UI_POPS_CLICKS/UI_01_CLICK_PRECISO.wav", mode="attack", rel=-19.5, pan=-0.1, st=1, eq="click", fade=None,
         note="f277 contador 0,91 m"),
    dict(id="D09", t=280 * F, file="03_UI_POPS_CLICKS/UI_01_CLICK_PRECISO.wav", mode="attack", rel=-19.5, pan=-0.1, st=1.5, eq="click", fade=None,
         note="f280 contador 1,77 m"),
    dict(id="D10", t=283 * F, file="03_UI_POPS_CLICKS/UI_01_CLICK_PRECISO.wav", mode="attack", rel=-19.5, pan=-0.1, st=2, eq="click", fade=None,
         note="f283 contador 2,27 m (desacelera)"),
    dict(id="D11", t=286 * F, file="02_IMPACTS/HIT_05_ACENTO_LIGERO.wav", mode="attack", rel=-11, pan=0.0, st=0, eq="hit", fade=None,
         note="f286 la cota se fija en 2,40 m"),
    # ---------------- 12:92 - 16:00  MENOS DEPENDENCIA DE GRUA ----------------
    dict(id="M01", t=323 * F, file="01_WHOOSHES/WHOOSH_04_MOTION_MEDIO.wav", mode="peak", rel=-14, pan=0.0, st=1, eq="air", fade=None,
         note="f320-329 barrido del brazo de grua en primer plano (pico f323)"),
    dict(id="M02", t=338 * F, file="03_UI_POPS_CLICKS/UI_02_TICK_MINIMO.wav", mode="attack", rel=-18.5, pan=0.15, st=0, eq="click", fade=None,
         note="f338 «ME» entra"),
    dict(id="M03", t=348 * F, file="03_UI_POPS_CLICKS/UI_02_TICK_MINIMO.wav", mode="attack", rel=-19, pan=0.15, st=1, eq="click", fade=None,
         note="f348 «NOS»"),
    dict(id="M04", t=352 * F, file="03_UI_POPS_CLICKS/UI_02_TICK_MINIMO.wav", mode="attack", rel=-18.5, pan=0.15, st=2, eq="click", fade=None,
         note="f352 «DEPEN / DE»"),
    dict(id="M05", t=374 * F, file="02_IMPACTS/HIT_02_PUNCH_CON_CUERPO.wav", mode="attack", rel=-7.5, pan=0.0, st=-1, eq="hit", fade=None,
         note="f374 «GRUA» parpadea a rojo: golpe mediano (misma familia que el GRUA del gancho)"),
    dict(id="M06", t=382 * F, file="03_UI_POPS_CLICKS/UI_01_CLICK_PRECISO.wav", mode="attack", rel=-21, pan=0.0, st=-1, eq="click", fade=None,
         note="f382 segundo parpadeo rojo"),
    # ---------------- 16:00 - 19:16  MONTAJE SIMPLE / ACABADOS DE CALIDAD ----------------
    dict(id="S01", t=400 * F, file="01_WHOOSHES/WHOOSH_04_MOTION_MEDIO.wav", mode="peak", rel=-14, pan=0.0, st=-1, eq="air", fade=None,
         note="f400 corte a montaje"),
    dict(id="S02", t=406 * F, file="03_UI_POPS_CLICKS/UI_03_POP_TEXTO_SUAVE.wav", mode="attack", rel=-16, pan=-0.1, st=0, eq="pop", fade=None,
         note="f406 «MONTAJE» aparece"),
    dict(id="S03", t=425 * F, file="02_IMPACTS/HIT_01_PUNCH_TEXTO_SECO.wav", mode="attack", rel=-8, pan=0.0, st=1, eq="hit", fade=None,
         note="f425 «SIMPLE» completo: acento seco y corto"),
    dict(id="S04", t=425 * F, file="03_UI_POPS_CLICKS/UI_05_SNAP_PALABRA.wav", mode="attack", rel=-17, pan=0.0, st=1, eq="click", fade=None,
         note="f425 capa snap de «SIMPLE»"),
    dict(id="S05", t=431 * F, file="03_UI_POPS_CLICKS/UI_05_SNAP_PALABRA.wav", mode="attack", rel=-21, pan=0.1, st=-1, eq="click", fade=None,
         note="f431 «ACABADOS DE» empieza"),
    dict(id="S06", t=455 * F, file="02_IMPACTS/HIT_06_CALIDAD_CON_PESO.wav", mode="attack", rel=-5, pan=0.0, st=0, eq="hit", fade=None,
         note="f455 «CALIDAD.» completo: acento con peso"),
    dict(id="S07", t=455 * F, file="03_UI_POPS_CLICKS/UI_04_POP_TEXTO_PUNCH.wav", mode="attack", rel=-17, pan=0.0, st=-2, eq="pop", fade=None,
         note="f455 capa pop de «CALIDAD»"),
    dict(id="S08", t=478.5 * F, file="01_WHOOSHES/WHOOSH_03_AIRE_LIGERO.wav", mode="peak", rel=-14, pan=0.0, st=0, eq="air", fade=None,
         note="f476-479 latigazo con desenfoque y corte a toma vertical"),
    # ---------------- 19:16 - 21:36  CRESCENDO ----------------
    dict(id="Z01", t=510 * F, file="04_RISERS_REVERSE/REVERSE_02_PRE_CORTE.wav", mode="end", rel=-17, pan=0.0, st=0, eq="air", fade=None,
         note="aire invertido hacia el inicio del giro (f510)"),
    dict(id="Z02", t=516 * F, file="01_WHOOSHES/WHOOSH_06_SPIN_DRON.wav", mode="peak", rel=-14, pan=0.0, st=0, eq="air", fade=None,
         note="f509-520 giro acelerado (pico f516)"),
    dict(id="Z03", t=534 * F + 0.01, file="04_RISERS_REVERSE/RISER_01_MICRO.wav", mode="end", rel=-12, pan=0.0, st=0, eq="air", fade=None,
         note="f520-533 zoom planeta: micro-riser que termina en el corte a rojo"),
    # ---------------- 21:36 - 25:24  CIERRE DE MARCA ----------------
    dict(id="C01", t=534 * F, file="02_IMPACTS/HIT_07_CIERRE_MARCA.wav", mode="attack", rel=-9, pan=0.0, st=0, eq="hit_sub", fade=(0.30, 0.15),
         note="f534 corte duro a rojo corporativo: impacto de marca corto"),
    dict(id="C02", t=552 * F, file="05_OUTRO_MARCA/LOGO_01_CONFIRMACION_LIGERA.wav", mode="attack", rel=-15.5, pan=0.0, st=0, eq="pop", fade=None,
         note="f550-553 logotipo Alsina se arma: confirmacion digital 1"),
    dict(id="C03", t=557 * F, file="05_OUTRO_MARCA/LOGO_03_TICK_SIMBOLO.wav", mode="attack", rel=-19, pan=0.0, st=0, eq="click", fade=None,
         note="f557 «x» + icono ALTIUS: confirmacion digital 2"),
]

# Ducking local SUAVE de la musica (banda grave <160 Hz, resto) en dB
DUCKS = [
    (20 * F, -2.5, -1.0),   # NO
    (46 * F, -2.5, -0.8),   # GRUA
    (197 * F, -1.5, -0.5),  # PLUS
    (286 * F, -1.0, -0.3),  # 2,40 m
    (374 * F, -1.5, -0.5),  # GRUA roja
    (425 * F, -1.5, -0.5),  # SIMPLE
    (455 * F, -2.5, -0.8),  # CALIDAD
    (534 * F, -2.0, -0.8),  # marca
]
