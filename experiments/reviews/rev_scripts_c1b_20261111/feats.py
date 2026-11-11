"""Reviewer zero-GPU covariates for C1b: read-only decode of existing eval frames; simple statistics only
(finite differences, means, zero-mask geometry). No blur, no resampling, no re-encoding; nothing written but a small npz
in the scratchpad. The C1 expression-probe feature is imported unchanged from src/C_cue_checks/c_checks.py."""
import csv, os, re, sys
from multiprocessing import Pool
import numpy as np
sys.path.insert(0, "/home/narolski/smad-next/src/C_cue_checks")
from c_checks import stats_job  # noqa: E402
D = "/home/narolski/mambamorph-code/smadcvpr_data/"
OUT = "/tmp/claude-1000/-home-narolski-mambamorph/c2840dc9-dd37-4619-9347-d8a76080b93f/scratchpad/c1b_review/feats.npz"

def ge(g):
    return float((np.diff(g, axis=0) ** 2).mean() + (np.diff(g, axis=1) ** 2).mean())

def job(r):
    from PIL import Image
    p = D + r["path"]
    with Image.open(p) as im:
        a = np.asarray(im.convert("RGB"), dtype=np.float64)
    assert a.shape[:2] == (512, 512), a.shape
    g = a.mean(2)
    nzmask = a.sum(2) > 0
    o = dict(id=r["id"], bytes=os.path.getsize(p), ied=float(r["ied"]), lum=float(g.mean()), zero=float(1 - nzmask.mean()),
             ge_all=ge(g), ge_mouth=ge(g[300:432, 150:366]), ge_upper=ge(g[120:260, 130:382]), ge_cheek=ge(g[260:300, 150:366]),
             lum_mouth=float(g[300:432, 150:366].mean()), lum_upper=float(g[120:260, 130:382].mean()))
    # border tilt (only meaningful where a zero-filled border exists): slope of the top edge of the non-zero region
    ang = np.nan
    if o["zero"] > 0.05:
        cols = np.where(nzmask.any(0))[0]
        if len(cols) > 50:
            c0, c1 = cols[0], cols[-1]
            cs = np.arange(c0 + (c1 - c0) // 4, c1 - (c1 - c0) // 4)
            top = np.array([np.argmax(nzmask[:, c]) for c in cs], float)
            sl = np.polyfit(cs, top, 1)[0]
            ang = float(np.degrees(np.arctan(sl)))
    o["angle"] = ang
    o["mouth"] = stats_job((p, "al"))["mouth"]
    return o

def main():
    rows = [r for r in csv.DictReader(open(D + "manifests/eval.csv")) if r["variant"] == "orig"]
    sel = [r for r in rows if r["family"] in ("frll_bona", "mordiff_bona")]
    sel += [r for r in rows if r["set"] == "devbona" and re.match(r"^\d{5}_\d{6}_(fa|fb)", r["path"].rsplit("/", 1)[1])]
    sel += [r for r in rows if r["set"] == "devbona" and r["path"].rsplit("/", 1)[1].startswith("nd1")]
    print(len(sel), "frames", flush=True)
    with Pool(14) as pool:
        R = pool.map(job, sel, chunksize=32)
    keys = [k for k in R[0] if k not in ("id", "mouth")]
    np.savez_compressed(OUT, id=np.array([o["id"] for o in R]), path=np.array([r["path"] for r in sel]), family=np.array([r["family"] for r in sel]),
                        mouth=np.array([o["mouth"] for o in R], np.float32), **{k: np.array([o[k] for o in R], float) for k in keys})
    print("saved", OUT)

if __name__ == "__main__":
    main()
