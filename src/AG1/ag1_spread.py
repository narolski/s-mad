"""AG1 spread-matched one-person renders R2s (amendment 3, rule 6; GPU, render only, Athena after the core array).
For every host p of a (generator, database) pool: G(m + (w_R2 - m) / sqrt(2)), w_R2 = the final latent of the host's R2
on s1 (lat/<gen>_R2_<p>__s1.npz in the core result tars), m = the mean of all inversion latents of that pool
(lat/inv_*.npz; e4e codes for mip2), the A37 rule. Same generator and output format as ag1_gen.py.
Output dir: png/<gen>_R2s_<p>.png, lat/<gen>_R2s_<p>.npz, log.csv (stem, rung, gen, a, b, alpha, latdist to w_avg,
latdist to m for R2s and for the source R2, seconds, png_sha256), meta.json.
Usage: python -I ag1_spread.py --gen mip1|mip2 --pool frll|feret|frgc --lat DIR --inputs DIR --weights DIR --sg1 FILE --out DIR
"""
import argparse
import csv
import functools
import hashlib
import json
import os
import pathlib
import sys
import time

HERE = pathlib.Path(__file__).resolve().parent


def sha(p):
    return hashlib.sha256(open(p, "rb").read()).hexdigest()


def main():
    ap = argparse.ArgumentParser()
    for k in ("gen", "pool", "lat", "inputs", "weights", "sg1", "out"):
        ap.add_argument("--" + k, required=True)
    a = ap.parse_args()
    if not sys.flags.isolated:
        sys.exit("refused: run with python -I")
    for line in open(HERE / "vendor/VENDOR.sha256"):
        h, f = line.split()
        if sha(HERE / "vendor" / f) != h:
            sys.exit(f"refused: vendor/{f} is not the registered file")
    os.environ.update(GAN_WEIGHTS=a.weights, SG1_WEIGHTS=a.sg1, TORCH_HOME=str(pathlib.Path(a.weights) / "torch"))
    sys.path.insert(0, str(pathlib.Path(a.weights) / "py"))
    sys.path.insert(0, str(HERE / "vendor"))
    import numpy as np
    import torch
    _load = torch.load

    @functools.wraps(_load)
    def load_weights_only(*args, **kw):
        kw["weights_only"] = True
        return _load(*args, **kw)
    torch.load = load_weights_only
    import generate as GEN
    import generate_mip1 as G1
    from PIL import Image
    torch.backends.cuda.matmul.allow_tf32 = False
    torch.backends.cudnn.allow_tf32 = False
    lat = pathlib.Path(a.lat)
    photos = json.load(open(pathlib.Path(a.inputs) / "photos.json"))
    inv = sorted(f for f in lat.glob(f"inv_{a.pool}_*.npz") if not f.stem.endswith("s1m"))
    if not inv:
        sys.exit(f"no inversion latents of pool {a.pool} in {lat}")
    hosts = sorted({m["person"] for m in photos.values() if m["db"] == a.pool})
    t0 = time.time()
    m_ = G1.Models1("cuda") if a.gen == "mip1" else GEN.Models("cuda")
    w_avg = (m_.G.w_avg.view(1, 1, -1) if a.gen == "mip1" else m_.net.latent_avg.view(1, -1, 512)).detach().float()
    M = torch.from_numpy(np.mean([np.load(f)["w"] for f in inv], axis=0)).cuda().float()
    out = pathlib.Path(a.out)
    (out / "png").mkdir(parents=True, exist_ok=True)
    (out / "lat").mkdir(parents=True, exist_ok=True)
    ld = lambda w, c: float((w - c).norm(dim=-1).mean())
    rows = []
    for p in hosts:
        src = lat / f"{a.gen}_R2_{p}__s1.npz"
        if not src.exists():
            sys.exit(f"missing {src}")
        t = time.time()
        w2 = torch.from_numpy(np.load(src)["w"]).cuda().float()
        ws = M + (w2 - M) / np.sqrt(2.0)
        with torch.no_grad():
            img = m_.synth(ws)
        arr = ((img[0].clamp(-1, 1) + 1) * 127.5).round().byte().permute(1, 2, 0).cpu().numpy()
        stem = f"{a.gen}_R2s_{p}"
        Image.fromarray(arr).save(out / "png" / f"{stem}.png", compress_level=1)
        np.savez_compressed(out / "lat" / f"{stem}.npz", w=ws.cpu().numpy().astype(np.float32))
        rows.append({"stem": stem, "rung": "R2s", "gen": a.gen, "a": f"{p}__s1", "b": f"{p}__s1", "alpha": 0.0,
                     "latdist": ld(ws, w_avg), "latdist_to_m": ld(ws, M), "src_latdist": ld(w2, w_avg),
                     "src_latdist_to_m": ld(w2, M), "seconds": round(time.time() - t, 3),
                     "png_sha256": sha(out / "png" / f"{stem}.png")})
    with open(out / "log.csv", "w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=list(rows[0]))
        w.writeheader()
        w.writerows(rows)
    json.dump({"gen": a.gen, "pool": a.pool, "n": len(rows), "n_inversions_in_m": len(inv),
               "seconds": time.time() - t0, "device": torch.cuda.get_device_name(), "torch": torch.__version__,
               "script_sha256": sha(__file__)}, open(out / "meta.json", "w"), indent=1)
    print(f"SPREAD_DONE {a.gen} {a.pool} {len(rows)} renders, m from {len(inv)} inversions")


if __name__ == "__main__":
    main()
