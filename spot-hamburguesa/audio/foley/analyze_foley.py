"""Analyse the client's foley originals: decode to 48 kHz float, per-file spectrogram + RMS envelope +
detected transients, and a JSON summary used to pick fragments. Originals are never modified."""
import os, json, subprocess, numpy as np, matplotlib
matplotlib.use("Agg"); import matplotlib.pyplot as plt
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(os.path.dirname(HERE))
SRC = os.path.join(HERE, "originales"); OUT = os.path.join(ROOT, "qa", "foley_analysis"); SR = 48000
os.makedirs(OUT, exist_ok=True)

def load(path):
    raw = subprocess.run(["ffmpeg", "-v", "quiet", "-i", path, "-ar", str(SR), "-ac", "2", "-f", "f32le", "-"], capture_output=True).stdout
    return np.frombuffer(raw, np.float32).reshape(-1, 2)

def transients(m, hop=240, k=6.0):
    e = np.sqrt(np.convolve(m ** 2, np.ones(hop) / hop, "same"))[::hop] + 1e-6
    led = 20 * np.log10(e); flux = np.maximum(np.diff(led, prepend=led[0]), 0)
    thr = np.median(flux) + k * (np.median(np.abs(flux - np.median(flux))) + 1e-3)
    idx = [i for i in range(1, len(flux) - 1) if flux[i] > thr and flux[i] >= flux[i - 1] and flux[i] >= flux[i + 1]]
    out = []
    for i in idx:
        if out and i - out[-1][0] < int(0.06 * SR / hop): continue
        pk = led[i:i + int(0.05 * SR / hop)].max()
        out.append((i, float(flux[i]), float(pk)))
    return [(i * hop / SR, f, p) for i, f, p in out], led, hop

summary = {}
for f in sorted(os.listdir(SRC)):
    x = load(os.path.join(SRC, f)); m = x.mean(1); d = len(m) / SR
    tr, led, hop = transients(m)
    peak = 20 * np.log10(np.abs(x).max() + 1e-9); rms = 10 * np.log10((m ** 2).mean() + 1e-12)
    # spectral centroid over time
    fig, ax = plt.subplots(2, 1, figsize=(16, 6), sharex=True, gridspec_kw={"height_ratios": [2, 1]})
    ax[0].specgram(m, NFFT=2048, Fs=SR, noverlap=1536, cmap="magma", vmin=-130, vmax=-20); ax[0].set_yscale("log"); ax[0].set_ylim(30, 20000)
    ax[0].set_title(f"{f}  dur {d:.2f}s  peak {peak:.1f} dBFS  rms {rms:.1f} dB")
    tt = np.arange(len(led)) * hop / SR; ax[1].plot(tt, led, lw=.6); ax[1].set_ylim(-80, 0); ax[1].grid(alpha=.3)
    strong = sorted(tr, key=lambda z: -z[2])[:12]
    for t, fl, p in strong: ax[1].axvline(t, color="r", lw=.6); ax[1].text(t, -5, f"{t:.2f}", fontsize=7, color="r", rotation=90)
    plt.tight_layout(); plt.savefig(os.path.join(OUT, f[:-4] + ".png"), dpi=60); plt.close()
    summary[f] = dict(duration=round(float(d), 3), peak_db=round(float(peak), 1), rms_db=round(float(rms), 1),
                      strongest_transients=[dict(t=round(t, 3), flux=round(fl, 1), peak_db=round(p, 1)) for t, fl, p in sorted(strong)])
json.dump(summary, open(os.path.join(OUT, "summary.json"), "w"), indent=1)
for k, v in summary.items():
    print(k, v["duration"], v["peak_db"], v["rms_db"], [(z["t"], z["peak_db"]) for z in v["strongest_transients"]][:8])
