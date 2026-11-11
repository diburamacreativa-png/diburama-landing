# Sustitución de fuentes por los fragmentos originales en alta calidad (restauración, no rediseño).
# Cada fotograma que el montaje pide al vídeo original (SRC.frame(i), índice a 25 fps de Thermoline_HD_ESP.mp4) se lee
# del clip HD cuando ese instante está cubierto; si no, del original. Encuadres, máscaras, tiempos, fondos y gráficos no
# cambian: los fondos atmosféricos y los registros se regeneran automáticamente desde la nueva fuente.
# Desplazamientos medidos por correspondencia de imagen (exactos al fotograma; ver README).
import os, subprocess
import numpy as np
from lib import SRC, FPS

HERE = os.path.dirname(os.path.abspath(__file__))
HD_DIR = os.environ.get("THERMO_HD_DIR", os.path.join(HERE, "in", "hd"))
CLIPS = [  # (archivo, inicio en el original (s), duración (s))
    ("05_MULTICAPA.mp4", 68.0, 15.0), ("06_RODILLO.mp4", 129.0, 10.0), ("07_PROYECCION.mp4", 159.0, 16.0),
    ("08_SPRAY.mp4", 191.0, 8.0), ("09_EDIFICIO.mp4", 210.0, 17.0),
    # V3: cortes HD de los segundos 3, 4 y 19 (en el solape 39,32–39,72 s prevalece 03_PARTICULA_FINAL)
    ("THERMOLINE_01_CRISTALES_HD.mp4", 7.00, 2.12), ("THERMOLINE_03_PARTICULA_FINAL_HD.mp4", 39.32, 3.28),
    ("THERMOLINE_02_PARTICULA_HD.mp4", 38.16, 1.56)]
# Si llegan 01_TEXTURA_AZUL, 02_PROPIEDADES, 03_PARTICULAS y 04_TERMOGRAFIA, se añaden aquí con su desplazamiento.

_orig_frame = SRC.frame
_cache, _used = {}, {}

def _hd_for(i):
    for name, t0, d in CLIPS:
        a = int(round(t0 * FPS))
        if a <= i < a + int(round(d * FPS)) and os.path.exists(os.path.join(HD_DIR, name)): return name, i - a
    return None

def _load(name, j, n=40):
    raw = subprocess.run(["ffmpeg", "-v", "error", "-ss", f"{j / FPS:.4f}", "-i", os.path.join(HD_DIR, name), "-frames:v", str(n),
                          "-f", "rawvideo", "-pix_fmt", "bgr24", "-"], capture_output=True, check=True).stdout
    arr = np.frombuffer(raw, np.uint8).reshape(-1, 1080, 1920, 3)
    for k in range(arr.shape[0]): _cache[(name, j + k)] = arr[k]

def frame(i):
    hit = _hd_for(i)
    if hit is None: return _orig_frame(i)
    name, j = hit
    if (name, j) not in _cache: _load(name, j)
    _used[name] = _used.get(name, 0) + 1
    return _cache[(name, j)]

def install():
    SRC.frame = frame            # SRC.at() y todos los módulos usan el mismo objeto: la sustitución es global
    SRC.cache.clear()

def report(): return dict(_used)
