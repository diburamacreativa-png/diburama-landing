# Correccion de acentos del primer montaje «Build Momentum» (tema de 21,24 s) en VIDEO REEL CHILE_DEMO 6.
# Tres niveles: (1) musica continua, (2) impactos de camara/escena, (3) acentos ligeros de texto.
# Cada cue indica que se ha hecho respecto al primer montaje (MOVIDO, SUSTITUIDO, NUEVO, CONSERVADO).
# Afinacion: tema en Mi. Colas de HIT_02/03/06/07 (~89 Hz) -> -1,4 st = Mi 82 Hz; HIT_01 -> +1 st; metal -1,14 st.
# 'snap': funde el ataque con el transitorio del tema mas cercano (+-snap s) para no doblar el golpe;
# 'early': cuanto puede adelantarse a la imagen (por defecto 25 ms; aqui casi siempre 0-5 ms).

F = 1 / 25.0
DOT = 738 * F + 0.004      # f738 (29,52 s): el punto blanco aparece aislado sobre negro = ANCLA
E_ST, TXT_ST, MET_ST = -1.4, 1.0, -1.14

CUES = [
    # ===== INICIO: impulso 1 (f7) y 2 (f31) = camara; f23 = salto menor con «SIN" (texto) =====
    dict(id="Z1w", t=7 * F - 0.008, file="01_WHOOSHES/WHOOSH_01_MICRO_SECO.wav", mode="peak", rel=-11, pan=0.0, st=0, eq="air",
         early=0.03, note="f7 arrastre corto hacia el impulso 1"),
    dict(id="Z1h", t=7 * F + 0.002, file="02_IMPACTS/HIT_02_PUNCH_CON_CUERPO.wav", mode="attack", rel=0, pan=0.0, st=E_ST, eq="hit",
         fade=(0.20, 0.12), tier="IMPACTO", accion="MOVIDO de 0,300 a 0,282 s y reforzado; el tiempo del tema en 0,217 s se atenua",
         note="f7 impulso de camara 1 (alejamiento -21 %) + MONTAJES"),
    dict(id="Z1p", t=7 * F + 0.002, file="02_IMPACTS/HIT_01_PUNCH_TEXTO_SECO.wav", mode="attack", rel=-8, pan=0.0, st=TXT_ST, eq="pop",
         note="f7 capa de ataque en medios (movil)"),
    dict(id="Z2t", t=23 * F + 0.011, file="02_IMPACTS/HIT_01_PUNCH_TEXTO_SECO.wav", mode="attack", rel=-10, pan=0.0, st=TXT_ST, eq="pop",
         snap=0.02, early=0.005, tier="TEXTO", accion="SUSTITUIDO: el whoosh se cambia por un pop ligero fundido con el tiempo del tema (0,931 s)",
         note="f23 salto menor + aparece «SIN»"),
    dict(id="Z2r", t=31 * F - 0.004, file="04_RISERS_REVERSE/REVERSE_01_PREIMPACTO.wav", mode="end", rel=-13, pan=0.0, st=1, eq="air",
         stretch=0.25, width_env=[(0, 0.3), (1, 1.2)], amp_env=[(0, -40), (0.35, -3), (1, 0)], note="f25-31 aspiracion breve"),
    dict(id="Z2w", t=31 * F - 0.010, file="01_WHOOSHES/WHOOSH_02_RAPIDO_LATERAL.wav", mode="peak", rel=-10, pan=0.0, st=-1, eq="air",
         early=0.03, note="f31 arrastre rapido"),
    dict(id="Z2h", t=31 * F + 0.004, file="02_IMPACTS/HIT_03_GRUA_PROTAGONISTA.wav", mode="attack", rel=1, pan=0.0, st=E_ST, eq="hit_sub",
         fade=(0.26, 0.16), tier="IMPACTO", accion="MOVIDO de 1,285 a 1,244 s (llegaba en f32); el tiempo del tema en 1,285 s se atenua",
         note="f31 impulso de camara 2 (-16,5 %) + NECESIDAD"),
    dict(id="Z2p", t=31 * F + 0.004, file="02_IMPACTS/HIT_01_PUNCH_TEXTO_SECO.wav", mode="attack", rel=-8, pan=0.0, st=TXT_ST, eq="pop",
         note="f31 capa de ataque en medios"),
    # ===== DE GRUA =====
    dict(id="T01", t=83 * F - 0.004, file="04_RISERS_REVERSE/REVERSE_02_PRE_CORTE.wav", mode="end", rel=-15, pan=0.0, st=0, eq="air",
         stretch=0.30, width_env=[(0, 0.3), (1, 1.1)], amp_env=[(0, -30), (0.5, -6), (1, 0)], note="f79-82 arrastre muy breve"),
    dict(id="T02", t=81.8 * F, file="01_WHOOSHES/WHOOSH_02_RAPIDO_LATERAL.wav", mode="peak", rel=-10, pan=0.0, st=-1, eq="air",
         pan_env=[(0, -0.3), (1, 0.3)], early=0.06, note="f79-82 latigazo (su pico queda 50 ms antes: el arrastre desemboca en el golpe)"),
    dict(id="T03", t=83 * F + 0.002, file="02_IMPACTS/HIT_02_PUNCH_CON_CUERPO.wav", mode="attack", rel=-1, pan=0.0, st=E_ST, eq="hit",
         fade=(0.20, 0.12), tier="IMPACTO", accion="MOVIDO de 3,309 a 3,322 s (iba 11 ms antes del corte) y reforzado; el pico de 3,21 s queda como anticipacion",
         note="f83 llegada del encuadre «DE GRÚA» (el texto llega con el paneo: sin golpe aparte)"),
    dict(id="T03p", t=83 * F + 0.002, file="02_IMPACTS/HIT_01_PUNCH_TEXTO_SECO.wav", mode="attack", rel=-9, pan=0.0, st=TXT_ST, eq="pop",
         note="f83 capa de ataque"),
    # ===== ALISPLAY MANUAL =====
    dict(id="T04", t=130.6 * F, file="01_WHOOSHES/WHOOSH_02_RAPIDO_LATERAL.wav", mode="peak", rel=-11, pan=0.0, st=0, eq="air",
         pan_env=[(0, -0.35), (1, 0.35)], early=0.04, note="f127-130 paneo que acelera"),
    dict(id="T04h", t=131 * F + 0.002, file="02_IMPACTS/HIT_02_PUNCH_CON_CUERPO.wav", mode="attack", rel=-5, pan=0.0, st=E_ST, eq="hit",
         tier="IMPACTO MEDIO", accion="NUEVO: el corte solo tenia whoosh", fade=(0.2, 0.12),
         note="f131 cambio de plano"),
    dict(id="T04t", t=141 * F + 0.002, file="02_IMPACTS/HIT_01_PUNCH_TEXTO_SECO.wav", mode="attack", rel=-9, pan=0.0, st=TXT_ST, eq="pop",
         snap=0.03, early=0.005, tier="TEXTO", accion="NUEVO", note="f141 «ALISPLAY» se asienta"),
    # ===== 240 PLUS =====
    dict(id="T05r", t=230 * F - 0.004, file="04_RISERS_REVERSE/REVERSE_02_PRE_CORTE.wav", mode="end", rel=-14, pan=0.0, st=0, eq="air",
         stretch=0.30, amp_env=[(0, -30), (0.5, -6), (1, 0)], note="f227-229 aspiracion corta hacia el corte"),
    dict(id="T05", t=229.2 * F, file="01_WHOOSHES/WHOOSH_02_RAPIDO_LATERAL.wav", mode="peak", rel=-10, pan=0.0, st=-1, eq="air",
         early=0.06, accion="SUSTITUIDO: el whoosh grave largo (pico de energia ~9,26 s) por uno corto que termina en el corte",
         note="f227-229 latigazo"),
    dict(id="T06", t=230 * F + 0.002, file="02_IMPACTS/HIT_03_GRUA_PROTAGONISTA.wav", mode="attack", rel=-1, pan=0.0, st=E_ST, eq="hit_sub",
         fade=(0.24, 0.15), tier="IMPACTO", accion="SUSTITUIDO (HIT_01 debil -> HIT_03) en 9,202 s; el bombo del tema en 9,15 s se atenua",
         note="f230 llegada del plano 240 PLUS"),
    dict(id="T06p", t=230 * F + 0.002, file="02_IMPACTS/HIT_01_PUNCH_TEXTO_SECO.wav", mode="attack", rel=-9, pan=0.0, st=TXT_ST, eq="pop",
         note="f230 capa de ataque"),
    dict(id="T07", t=243 * F + 0.002, file="03_UI_POPS_CLICKS/UI_05_SNAP_PALABRA.wav", mode="attack", rel=-5, pan=0.0, st=0, eq="click",
         snap=0.03, early=0.005, tier="TEXTO", accion="CONSERVADO, algo mas presente", note="f243 «PLUS» se asienta"),
    # ===== DISENADO PARA (coincidencia con el tema conservada) =====
    dict(id="T08", t=297.5 * F, file="01_WHOOSHES/WHOOSH_05_GRAVE_CON_CUERPO.wav", mode="peak", rel=-12, pan=0.0, st=-1, eq="air_body",
         early=0.03, note="f298 corte a DISEÑADO PARA (pico 20 ms antes del corte)"),
    dict(id="T09", t=298 * F, file="02_IMPACTS/HIT_05_ACENTO_LIGERO.wav", mode="attack", rel=-11, pan=0.0, st=0, eq="hit", snap=0.04,
         tier="IMPACTO MEDIO", accion="CONSERVADO: fundido con el pico del tema en 11,947 s; ataque algo mas definido",
         note="f298 «DISEÑADO PARA»"),
    # ===== EDIFICACION CHILENA y medida =====
    dict(id="T20", t=341 * F + 0.002, file="02_IMPACTS/HIT_01_PUNCH_TEXTO_SECO.wav", mode="attack", rel=-15, pan=0.0, st=TXT_ST, eq="pop",
         snap=0.03, early=0.005, tier="TEXTO", accion="NUEVO", note="f341 «EDIFICACIÓN» completa su barrido"),
    dict(id="T21", t=393 * F + 0.002, file="03_UI_POPS_CLICKS/UI_05_SNAP_PALABRA.wav", mode="attack", rel=-8, pan=0.0, st=0, eq="click",
         snap=0.035, early=0.005, tier="TEXTO", accion="NUEVO: remate solo cuando la medida queda fija (sin golpe por cifra)",
         note="f393 la medida se fija en 2,40 m"),
    # ===== MENOS DEPENDENCIA DE GRUA =====
    dict(id="T10", t=427 * F, file="01_WHOOSHES/WHOOSH_04_MOTION_MEDIO.wav", mode="peak", rel=-9, pan=0.0, st=1, eq="air",
         pan_env=[(0, 0.35), (1, -0.35)], accion="CONSERVADO", note="f424-433 el cubo de la grua barre (der -> izq)"),
    dict(id="T11", t=430 * F, file="01_WHOOSHES/WHOOSH_05_GRAVE_CON_CUERPO.wav", mode="peak", rel=-11, pan=0.0, st=-3, eq="air_body",
         accion="CONSERVADO: el pico de 17,20 s coincide con el barrido", note="f430 masa de aire y corte oculto"),
    dict(id="T11h", t=433 * F + 0.002, file="02_IMPACTS/HIT_05_ACENTO_LIGERO.wav", mode="attack", rel=-3, pan=0.0, st=0, eq="hit",
         snap=0.03, early=0.005, tier="IMPACTO MEDIO", accion="NUEVO: remate cuando el plano queda libre",
         note="f433 el cubo sale y llega el plano de MENOS DEPENDENCIA"),
    dict(id="T22", t=444 * F + 0.002, file="02_IMPACTS/HIT_01_PUNCH_TEXTO_SECO.wav", mode="attack", rel=-11, pan=0.0, st=TXT_ST, eq="pop",
         snap=0.03, early=0.005, tier="TEXTO", accion="NUEVO", note="f444 «MENOS» completo"),
    dict(id="T23", t=458 * F + 0.002, file="02_IMPACTS/HIT_01_PUNCH_TEXTO_SECO.wav", mode="attack", rel=-11, pan=0.0, st=TXT_ST, eq="pop",
         snap=0.03, early=0.005, tier="TEXTO", accion="NUEVO", note="f458 «DEPENDENCIA» completo"),
    dict(id="T24", t=476 * F + 0.002, file="02_IMPACTS/HIT_01_PUNCH_TEXTO_SECO.wav", mode="attack", rel=-10, pan=0.0, st=TXT_ST, eq="pop",
         snap=0.03, early=0.005, tier="TEXTO", accion="NUEVO", note="f476 «DE GRÚA» completo"),
    dict(id="T12", t=503 * F, file="02_IMPACTS/HIT_04_METAL_MATE_SUTIL.wav", mode="attack", rel=-10, pan=0.0, st=MET_ST, eq="metal",
         snap=0.02, early=0.005, tier="TEXTO", accion="CONSERVADO, mas discreto", note="f503 «GRÚA» destella en rojo"),
    # ===== MONTAJE SIMPLE / ACABADOS DE CALIDAD =====
    dict(id="T13", t=544.6 * F, file="01_WHOOSHES/WHOOSH_02_RAPIDO_LATERAL.wav", mode="peak", rel=-11, pan=0.0, st=-1, eq="air",
         early=0.04, accion="SUSTITUIDO: whoosh mas corto que desemboca en el corte", note="f545 corte a MONTAJE SIMPLE"),
    dict(id="T13h", t=545 * F + 0.002, file="02_IMPACTS/HIT_02_PUNCH_CON_CUERPO.wav", mode="attack", rel=-3, pan=0.0, st=E_ST, eq="hit",
         fade=(0.2, 0.12), tier="IMPACTO", accion="NUEVO: la llegada no tenia golpe; el tiempo del tema en 21,64 s se atenua",
         note="f545 llegada del plano"),
    dict(id="T14", t=563 * F + 0.004, file="02_IMPACTS/HIT_01_PUNCH_TEXTO_SECO.wav", mode="attack", rel=-6, pan=0.0, st=TXT_ST, eq="hit",
         tier="TEXTO", accion="MOVIDO de 22,559 a 22,524 s (f563, cuando SIMPLE alcanza su tamano final)",
         note="f563 «SIMPLE» se asienta"),
    dict(id="T15", t=582 * F + 0.002, file="02_IMPACTS/HIT_06_CALIDAD_CON_PESO.wav", mode="attack", rel=-4, pan=0.0, st=E_ST, eq="hit",
         fade=(0.22, 0.14), tier="TEXTO", accion="MOVIDO de 23,269 a 23,282 s (iba 11 ms antes de f582)",
         note="f582 «CALIDAD.» completo"),
    # ===== HACIA EL CIERRE =====
    dict(id="T16", t=670 * F - 0.006, file="04_RISERS_REVERSE/REVERSE_02_PRE_CORTE.wav", mode="end", rel=-14, pan=0.0, st=0, eq="air",
         width_env=[(0, 0.3), (1, 1.1)], accion="CONSERVADO", note="f665-669 aspiracion"),
    dict(id="T17", t=669.5 * F, file="01_WHOOSHES/WHOOSH_03_AIRE_LIGERO.wav", mode="peak", rel=-11, pan=0.0, st=0, eq="air",
         accion="CONSERVADO", note="f668-669 latigazo"),
    dict(id="T18", t=670 * F + 0.002, file="02_IMPACTS/HIT_05_ACENTO_LIGERO.wav", mode="attack", rel=-2, pan=0.0, st=0, eq="hit",
         snap=0.02, early=0.005, tier="IMPACTO MEDIO", accion="NUEVO: marca el corte sin gastar el golpe del cierre (el break del tema entra en 26,816 s)",
         note="f670 corte a la toma cenital"),
    dict(id="Z10", t=DOT - 0.012, file="04_RISERS_REVERSE/RISER_03_ZOOM_SPIN.wav", mode="end", rel=-11, pan=0.0, st=0, eq="air",
         stretch=1.18, lp_env=[(0, 1800), (0.55, 5000), (1, 13000)], amp_env=[(0, -36), (0.6, -9), (1, 0)],
         width_env=[(0, 0.5), (1, 1.4)], accion="SUSTITUYE al Doppler descendente y a las aspiraciones Z01/Z03: una sola textura que crece",
         note="f708-737 el alejamiento acelera: textura que crece con la imagen (el redoble del tema entra en 28,95 s)"),
    dict(id="Z11", t=DOT - 0.006, file="04_RISERS_REVERSE/REVERSE_01_PREIMPACTO.wav", mode="end", rel=-12, pan=0.0, st=0, eq="air",
         amp_env=[(0, -30), (0.5, -6), (1, 0)], note="f735-737 el iris se cierra: aspiracion en el vacio antes del punto"),
    # ===== PUNTO BLANCO (ANCLA) =====
    dict(id="I01", t=DOT, file="02_IMPACTS/HIT_07_CIERRE_MARCA.wav", mode="attack", rel=-2, pan=0.0, st=E_ST, eq="hit", verb=-10,
         snap=0.012, early=0.004, tier="CIERRE", accion="MOVIDO de 30,125 s (f753) a 29,521 s (f738, 29,520-29,560 s), fundido con la resolucion del tema",
         note="f738 PUNTO BLANCO: cuerpo del golpe final"),
    dict(id="I02", t=DOT, file="02_IMPACTS/HIT_03_GRUA_PROTAGONISTA.wav", mode="attack", rel=-4, pan=0.0, st=E_ST, eq="hit_sub",
         fade=(0.4, 0.25), snap=0.012, early=0.004, note="f738 grave controlado afinado en Mi"),
    dict(id="I03", t=DOT, file="02_IMPACTS/HIT_04_METAL_MATE_SUTIL.wav", mode="attack", rel=-10, pan=0.0, st=MET_ST, eq="metal", verb=-4,
         snap=0.012, early=0.004, note="f738 contacto metalico en Mi"),
    dict(id="I05", t=DOT, file="02_IMPACTS/HIT_02_PUNCH_CON_CUERPO.wav", mode="attack", rel=-6, pan=0.0, st=-2, eq="pop",
         snap=0.012, early=0.004, note="f738 cuerpo en medios (movil)"),
    dict(id="I04", t=DOT, file="05_OUTRO_MARCA/LOGO_04_CLACK_IDENTIDAD.wav", mode="attack", rel=-14, pan=0.0, st=0, eq="click", verb=-12,
         snap=0.012, early=0.004, note="f738 ataque definido"),
    dict(id="I06", t=DOT + 0.012, file="05_OUTRO_MARCA/LOGO_02_AIRE_SALIDA.wav", mode="start", rel=-16, pan=0.0, st=-1, eq="air",
         lp_env=[(0, 9000), (1, 2200)], amp_env=[(0, 0), (1, -12)], width_env=[(0, 1.4), (1, 0.8)],
         note="f738+ aire que acompaña la caida del punto y la formacion del logo, sin golpes nuevos"),
]


def _d(t0, t1, att, rel, g, m, a, why):
    return dict(t0=t0, t1=t1, att=att, rel=rel, db=(g, m, a), why=why)


DUCKS = [
    # atenuaciones breves de acentos del tema que adelantaban o doblaban la llegada visual
    _d(0.205, 0.250, 0.012, 0.030, 0.0, -3.0, -6.0, "tiempo del tema 63 ms antes de f7"),
    _d(1.270, 1.330, 0.015, 0.060, -4.0, -4.0, -6.0, "tiempo del tema 45 ms despues de f31 (evita doble ataque)"),
    _d(9.135, 9.190, 0.010, 0.020, -6.0, -2.0, 0.0, "bombo del tema 50 ms antes del corte a 240"),
    _d(21.615, 21.680, 0.012, 0.040, 0.0, -3.0, -3.0, "tiempo del tema 160 ms antes del corte a MONTAJE SIMPLE"),
    _d(22.552, 22.590, 0.010, 0.030, 0.0, -3.0, -5.0, "semicorchea del tema 40 ms despues de SIMPLE"),
    _d(23.255, 23.282, 0.010, 0.030, 0.0, -3.0, -5.0, "semicorchea del tema 13 ms antes de CALIDAD"),
    # espacio para los impactos
    _d(7 * F, 7 * F + 0.08, 0.004, 0.22, -3.0, -2.0, -1.0, "impulso 1"),
    _d(31 * F, 31 * F + 0.11, 0.004, 0.25, -3.0, -2.0, -1.0, "impulso 2"),
    _d(83 * F, 83 * F + 0.08, 0.004, 0.22, -2.0, -1.5, -1.0, "DE GRUA"),
    _d(230 * F, 230 * F + 0.08, 0.004, 0.22, -2.0, -1.5, -1.0, "240 PLUS"),
    _d(427 * F - 0.12, 430 * F + 0.1, 0.08, 0.25, 0.0, -1.5, -2.5, "barrido del cubo"),
    _d(545 * F, 545 * F + 0.08, 0.004, 0.22, -2.0, -1.5, -1.0, "MONTAJE SIMPLE"),
    _d(582 * F, 582 * F + 0.08, 0.004, 0.25, -2.0, -1.0, -0.5, "CALIDAD"),
    _d(708 * F, 735 * F, 0.20, 0.10, 0.0, -1.0, -1.5, "alejamiento: sitio para la textura"),
    _d(DOT, DOT + 0.12, 0.002, 0.50, -2.5, -1.0, -0.5, "PUNTO"),
]
