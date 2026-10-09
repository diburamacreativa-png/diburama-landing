"""DIBURAMA spot — fetch CC0 foley from Freesound and lay it on the master timeline.

1. For every cue in audio/foley/foley_cues.json, search Freesound (API v2) with license filter
   "Creative Commons 0", rank candidates, download the best ones, convert to 48 kHz / 24-bit WAV.
2. Build the foley stems by placing the chosen file of each cue at its timeline positions
   (transient-aligned for impacts, looped with crossfades for beds, trimmed, faded, gain-staged).
3. Write MANIFEST.json (provenance: id, author, URL, license, licence check) and CREDITS.md.

Requirements: FREESOUND_API_KEY (free key: https://freesound.org/apiv2/apply). With it, the script
downloads Freesound's high-quality previews (OGG ~192 kbps). If FREESOUND_OAUTH_TOKEN is also set,
it downloads the uploaded original files instead (lossless when the uploader provided WAV/FLAC).
The host freesound.org (and cdn.freesound.org) must be reachable from the machine running it.

usage:
  python3 audio/foley/fetch_freesound.py search          # search + download candidates
  python3 audio/foley/fetch_freesound.py build           # place chosen files → audio/stems_v2/*.wav
  python3 audio/foley/fetch_freesound.py all             # both
  python3 audio/foley/fetch_freesound.py import DIR      # use your own licensed files instead:
                                                         #   DIR/<cue_id>*.wav|flac|mp3|ogg
Re-running is incremental: already downloaded files are not fetched again. To force a candidate,
set "choice": <freesound id> on the cue in foley_cues.json.
"""
import json, math, os, re, subprocess, sys, time, urllib.error, urllib.parse, urllib.request
import numpy as np, soundfile as sf
from scipy import signal

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
LIB = os.path.join(HERE, "library")
OUT = os.path.join(ROOT, "audio", "stems_v2")
CUES = json.load(open(os.path.join(HERE, "foley_cues.json")))["cues"]
MANIFEST = os.path.join(HERE, "MANIFEST.json")
SR, DUR = 48000, 25.0
API = "https://freesound.org/apiv2"
CC0 = "http://creativecommons.org/publicdomain/zero/1.0/"
N_CANDIDATES = 4


# ------------------------------------------------------------------ freesound
def api_get(path, params):
    key = os.environ.get("FREESOUND_API_KEY")
    if not key:
        sys.exit("FREESOUND_API_KEY is not set (get one at https://freesound.org/apiv2/apply)")
    params = dict(params, token=key)
    url = f"{API}{path}?{urllib.parse.urlencode(params)}"
    for attempt in range(4):
        try:
            with urllib.request.urlopen(url, timeout=30) as r:
                return json.load(r)
        except urllib.error.URLError as e:
            if "403" in str(e) or "Tunnel" in str(e):
                sys.exit(f"freesound.org is not reachable from this machine ({e}). "
                         "Allow freesound.org and cdn.freesound.org in the network policy, or run the script locally.")
            if attempt == 3: raise
            time.sleep(2 ** attempt)

def download(url, dest, oauth=None):
    req = urllib.request.Request(url)
    if oauth: req.add_header("Authorization", f"Bearer {oauth}")
    with urllib.request.urlopen(req, timeout=120) as r, open(dest + ".part", "wb") as f:
        while True:
            b = r.read(1 << 16)
            if not b: break
            f.write(b)
    os.replace(dest + ".part", dest)

def to_wav(src, dst):
    subprocess.run(["ffmpeg", "-y", "-v", "error", "-i", src, "-ar", str(SR), "-ac", "2", "-c:a", "pcm_s24le", dst], check=True)

def score(s):
    # quality signal: rating weighted by how many people trusted it; mild preference for 44.1/48k+ originals
    return (s.get("avg_rating") or 2.5) * math.log10(10 + (s.get("num_downloads") or 0)) * (1.1 if (s.get("samplerate") or 0) >= 44100 else 1)

def search():
    os.makedirs(LIB, exist_ok=True)
    man = json.load(open(MANIFEST)) if os.path.exists(MANIFEST) else {}
    oauth = os.environ.get("FREESOUND_OAUTH_TOKEN")
    for cue in CUES:
        seen = {}
        lo, hi = cue["dur"]
        for q in cue["queries"]:
            res = api_get("/search/text/", {
                "query": q, "page_size": 15, "sort": "rating_desc",
                "filter": f'license:"Creative Commons 0" duration:[{lo} TO {hi}]',
                "fields": "id,name,username,license,duration,previews,avg_rating,num_downloads,samplerate,url,tags,type"})
            for s in res.get("results", []):
                if s["license"].rstrip("/") + "/" != CC0:      # double check: CC0 only
                    continue
                seen.setdefault(s["id"], s)
        cands = sorted(seen.values(), key=score, reverse=True)[:N_CANDIDATES]
        entry = man.setdefault(cue["id"], {"candidates": []})
        have = {c["id"] for c in entry["candidates"]}
        d = os.path.join(LIB, cue["id"]); os.makedirs(d, exist_ok=True)
        for s in cands:
            if s["id"] in have: continue
            slug = re.sub(r"[^a-z0-9]+", "_", s["name"].lower())[:40]
            raw = os.path.join(d, f"{s['id']}_{slug}.src")
            if oauth:
                download(f"{API}/sounds/{s['id']}/download/", raw, oauth)
                quality = "original"
            else:
                download(s["previews"]["preview-hq-ogg"], raw)
                quality = "preview-hq-ogg"
            wav = raw[:-4] + ".wav"; to_wav(raw, wav); os.remove(raw)
            entry["candidates"].append(dict(id=s["id"], name=s["name"], author=s["username"], url=s["url"],
                                            license=s["license"], duration=s["duration"], rating=s.get("avg_rating"),
                                            downloads=s.get("num_downloads"), quality=quality,
                                            file=os.path.relpath(wav, ROOT)))
            print(f"[{cue['id']}] {s['id']} {s['name']!r} by {s['username']} ({s['duration']:.1f}s, {quality})")
        if not entry["candidates"]:
            print(f"[{cue['id']}] WARNING: no CC0 result — refine queries or import a licensed file")
        json.dump(man, open(MANIFEST, "w"), indent=1, ensure_ascii=False)
    write_credits(man)

def import_dir(path):
    """use local, already licensed files: DIR/<cue_id>*.ext (first match per cue)"""
    man = json.load(open(MANIFEST)) if os.path.exists(MANIFEST) else {}
    files = sorted(os.listdir(path))
    for cue in CUES:
        hits = [f for f in files if f.lower().startswith(cue["id"].lower())]
        if not hits: continue
        d = os.path.join(LIB, cue["id"]); os.makedirs(d, exist_ok=True)
        wav = os.path.join(d, "local_" + os.path.splitext(hits[0])[0] + ".wav")
        to_wav(os.path.join(path, hits[0]), wav)
        man[cue["id"]] = {"candidates": [dict(id=f"local:{hits[0]}", name=hits[0], author="(local)", url="",
                                              license="licensed by the client (verify)", quality="original",
                                              file=os.path.relpath(wav, ROOT))]}
        print(f"[{cue['id']}] imported {hits[0]}")
    json.dump(man, open(MANIFEST, "w"), indent=1, ensure_ascii=False)
    write_credits(man)

def write_credits(man):
    with open(os.path.join(HERE, "CREDITS.md"), "w") as f:
        f.write("# Foley — procedencia y licencias\n\nCC0 no exige atribución; se conserva la procedencia para auditoría.\n\n")
        f.write("| Cue | Usado | Freesound ID | Nombre | Autor | Licencia | Calidad |\n|---|---|---|---|---|---|---|\n")
        for cue in CUES:
            e = man.get(cue["id"])
            if not e: continue
            used = chosen(cue, e)
            for c in e["candidates"]:
                f.write(f"| {cue['id']} | {'✔' if c is used else ''} | {c['id']} | {c['name']} | {c['author']} | {c['license']} | {c['quality']} |\n")


# ------------------------------------------------------------------ timeline
def chosen(cue, entry):
    if not entry or not entry["candidates"]: return None
    if "choice" in cue:
        for c in entry["candidates"]:
            if str(c["id"]) == str(cue["choice"]): return c
    return entry["candidates"][0]

def onset(x):
    """first strong transient (s): energy-flux peak in the first 2 s"""
    m = np.abs(x).mean(axis=1)
    hop = 120; e = np.sqrt(np.convolve(m ** 2, np.ones(hop) / hop, "same"))[::hop]
    flux = np.maximum(np.diff(e, prepend=e[0]), 0)
    lim = min(len(flux), int(2.0 * SR / hop))
    i = int(np.argmax(flux[:lim])) if lim > 0 else 0
    return max(0, i * hop - int(0.004 * SR)) / SR      # 4 ms of pre-attack

def fit_length(x, n, loop, xf=0.08):
    if len(x) >= n or not loop:
        return x[:n]
    L = int(xf * SR); out = x.copy()
    while len(out) < n:
        a = out[-L:] * np.linspace(1, 0, L)[:, None] + x[:L] * np.linspace(0, 1, L)[:, None]
        out = np.concatenate([out[:-L], a, x[L:]])
    return out[:n]

def build():
    man = json.load(open(MANIFEST)) if os.path.exists(MANIFEST) else {}
    os.makedirs(OUT, exist_ok=True)
    N = int(DUR * SR); stems = {}; per_cue = {}; missing = []
    for cue in CUES:
        c = chosen(cue, man.get(cue["id"]))
        if c is None:
            missing.append(cue["id"]); continue
        x, sr = sf.read(os.path.join(ROOT, c["file"]), always_2d=True)
        if sr != SR: x = signal.resample_poly(x, SR, sr, axis=0)
        x = x / (np.abs(x).max() + 1e-9) * 0.89                    # peak-normalise the source, then gain-stage
        track = np.zeros((N, 2))
        for p in cue["placements"]:
            off = onset(x) if p.get("align") == "onset" else 0.0
            seg = x[int(off * SR):]
            seg = fit_length(seg, int(p["length"] * SR), p.get("loop", False))
            fi, fo = int(p.get("fade_in", 0.003) * SR), int(p.get("fade_out", 0.05) * SR)
            env = np.ones(len(seg))
            if fi: env[:fi] = np.linspace(0, 1, fi) ** 2
            if fo: env[-fo:] *= np.linspace(1, 0, fo) ** 2
            seg = seg * env[:, None] * 10 ** (p.get("gain_db", 0) / 20)
            i = int(round(p["t"] * SR)); j = min(N, i + len(seg))
            track[i:j] += seg[: j - i]
        per_cue[cue["id"]] = track
        stems[cue["stem"]] = stems.get(cue["stem"], 0) + track
    for k, v in per_cue.items():
        sf.write(os.path.join(OUT, f"cue_{k}.wav"), v.astype(np.float32), SR, subtype="PCM_24")
    for k, v in stems.items():
        sf.write(os.path.join(OUT, f"{k}.wav"), v.astype(np.float32), SR, subtype="PCM_24")
    json.dump({"placed": sorted(per_cue), "missing": missing}, open(os.path.join(OUT, "foley_build.json"), "w"), indent=1)
    print("stems:", ", ".join(sorted(stems)), "| missing cues:", ", ".join(missing) or "none")


if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else "all"
    if cmd in ("search", "all"): search()
    if cmd == "import": import_dir(sys.argv[2])
    if cmd in ("build", "all", "import"): build()
