"""Audio QA: spectrogram + momentary loudness (400 ms) + section markers + stem levels."""
import sys, os, json, numpy as np, soundfile as sf, matplotlib
matplotlib.use("Agg"); import matplotlib.pyplot as plt
import pyloudnorm as pyln
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
mix_path, out = sys.argv[1], sys.argv[2]
x, sr = sf.read(mix_path); m = x.mean(axis=1)
meter = pyln.Meter(sr)
hop = int(0.05 * sr); win = int(0.4 * sr); ts, lm = [], []
for i in range(0, len(x) - win, hop):
    seg = x[i:i + win]
    try: l = meter.integrated_loudness(seg) if False else 10 * np.log10(np.mean(seg ** 2) + 1e-12) - 0.691 + 3.0
    except Exception: l = -70
    ts.append((i + win / 2) / sr); lm.append(l)
stems_dir = os.path.join(os.path.dirname(mix_path), "stems")
fig, ax = plt.subplots(3, 1, figsize=(18, 11), sharex=True, gridspec_kw={"height_ratios": [3, 1.3, 1.3]})
ax[0].specgram(m, NFFT=2048, Fs=sr, noverlap=1536, cmap="magma", vmin=-130, vmax=-20); ax[0].set_ylim(20, 16000); ax[0].set_yscale("log")
ax[0].set_ylabel("Hz")
ax[1].plot(ts, lm, color="k"); ax[1].set_ylabel("RMS-ish LU (400ms)"); ax[1].set_ylim(-60, -5); ax[1].grid(alpha=.3)
for f in sorted(os.listdir(stems_dir)):
    s, _ = sf.read(os.path.join(stems_dir, f)); s = s.mean(axis=1)
    e = [10 * np.log10(np.mean(s[i:i + win] ** 2) + 1e-12) for i in range(0, len(s) - win, hop)]
    ax[2].plot(ts[:len(e)], e, label=f[:-4])
ax[2].legend(loc="lower left", fontsize=8); ax[2].set_ylim(-70, -5); ax[2].grid(alpha=.3)
edl = json.load(open(os.path.join(ROOT, "project", "edit_decisions.json")))
marks = [(s["in"] if i == 0 else s["in"], s["id"]) for i, s in enumerate(edl["segments"])] + [(edl["graphics"]["start"], "GFX")]
for a in ax:
    for t, n in marks: a.axvline(t, color="c", lw=.6)
for t, n in marks: ax[0].text(t + .03, 15000, n, color="w", fontsize=8)
ax[2].set_xlabel("s"); plt.tight_layout(); plt.savefig(out, dpi=70)
print("peak dBFS", 20 * np.log10(np.abs(x).max()), "integrated", meter.integrated_loudness(x))
