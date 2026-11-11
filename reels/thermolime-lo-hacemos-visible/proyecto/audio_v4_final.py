# LinkedIn · AUDIO FINAL (V4): un único fragmento continuo de la canción original completa, sin ediciones
#   Digital Ascension 02:31,773 → 02:55,773 (24,000 s). Termina en la cola natural del final de la canción.
#   02:51,795 = último golpe de la canción → 20,022 s del vídeo (entrada del logotipo, f500).
# No hay cortes, bucles, repeticiones, filtros ni acordes añadidos en la música. Solo: 30 ms de fundido de entrada
# (evita un clic al empezar a mitad de forma de onda) y 60 ms al final (la cola ya está a −80 dBFS).
# Efectos: los de la versión LinkedIn en los mismos cortes, salvo 12 y 13 (ver abajo): el logotipo entra sobre el golpe real.
# uso: python3 audio_v4_final.py <cancion_completa.mp3> <sfx_dir> <out_dir>
import os, sys, json, subprocess
import numpy as np, soundfile as sf
from scipy.signal import butter, sosfiltfilt, stft
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import audio as A
import audio_linkedin as AL

SR, DUR = A.SR, 24.0; N = int(SR * DUR)
FRAG_START = 152.440                       # inicio del fragmento de 20 s usado en V1–V3 (medido por correlación)
BEAT = 60 / 90
SONG_START = FRAG_START - BEAT             # un tiempo antes: los cortes siguen cayendo sobre golpes
LAST_HIT_SONG = 171.795                    # último golpe de la canción (medido)

def decode(path):
    raw = subprocess.run(["ffmpeg", "-v", "error", "-i", path, "-ar", str(SR), "-ac", "2", "-f", "f32le", "-"], capture_output=True, check=True).stdout
    return np.frombuffer(raw, np.float32).reshape(-1, 2).astype(np.float64)

def onset_near(x, t0, win=0.04):
    seg = x[int((t0 - win) * SR):int((t0 + win) * SR)].mean(1)
    hf = sosfiltfilt(butter(4, 2000, 'high', fs=SR, output='sos'), seg)
    env = np.convolve(np.abs(hf), np.ones(48) / 48, 'same')
    return t0 - win + int(np.argmax(np.diff(env, prepend=env[0]))) / SR

def main(song_path, sfx_dir, out_dir):
    os.makedirs(out_dir, exist_ok=True)
    song = decode(song_path)
    hit_song = onset_near(song, LAST_HIT_SONG)
    i0 = int(round(SONG_START * SR))
    mus = song[i0:i0 + N].copy(); assert len(mus) == N
    fi, fo = int(0.03 * SR), int(0.06 * SR)
    mus[:fi] *= np.linspace(0, 1, fi)[:, None]; mus[-fo:] *= np.linspace(1, 0, fo)[:, None]
    hit = hit_song - SONG_START
    AL.HIT = hit                                             # 12 y 13 se sitúan sobre el golpe real
    # sin 12 (riser) ni 13 (sub de 39 Hz: bate a ~9 Hz con el bajo de 48 Hz de la cola y suena a golpes repetidos);
    # la marca entra sobre el último golpe real de la canción, sin refuerzo artificial
    _plan = AL.plan; AL.plan = lambda: [q for q in _plan() if not q[0].startswith(('12_', '13_'))]
    AL.build_music = lambda p: (mus, [])
    AL.EDIT = [(SONG_START, SONG_START + DUR, 0.0)]
    AL.main(song_path, sfx_dir, out_dir)
    rep = json.load(open(os.path.join(out_dir, 'audio_report.json')))
    rep.pop('edicion', None); rep.pop('croma_cola_21_6_23_6s', None)
    x, _ = sf.read(os.path.join(out_dir, 'master_mix.wav')); m = x.mean(1)
    rep['musica'] = dict(cancion='Digital Ascension (original completa, 176,28 s)', desde_s=round(SONG_START, 3), hasta_s=round(SONG_START + DUR, 3),
                         desde_mmss='02:%06.3f' % (SONG_START - 120), hasta_mmss='02:%06.3f' % (SONG_START + DUR - 120),
                         ultimo_golpe_cancion_s=round(hit_song, 3), ultimo_golpe_en_video_s=round(hit, 3), fotograma=int(hit * 25),
                         ediciones='ninguna (fragmento continuo; fundidos de 30 ms al inicio y 60 ms al final)')
    rep['rms_db_cada_0_5s_desde_17s'] = [round(float(20 * np.log10(np.sqrt((m[int(t * SR):int((t + .5) * SR)] ** 2).mean()) + 1e-12)), 1) for t in np.arange(17, 24, .5)]
    json.dump(rep, open(os.path.join(out_dir, 'audio_report.json'), 'w'), indent=1, ensure_ascii=False)
    print(json.dumps({k: rep[k] for k in ('musica', 'rms_db_cada_0_5s_desde_17s', 'master_true_peak_db', 'limitador_reduccion_max_db', 'ultimo_pico_dbfs', 'perdida_suma_mono_db')}, indent=1, ensure_ascii=False))
    print([(r['sfx'], r['pico_s']) for r in rep['sfx'] if r['pico_s'] > 16.5])

if __name__ == '__main__': main(*sys.argv[1:4])
