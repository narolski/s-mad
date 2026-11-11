"""Fixed-threshold re-read (EV1), amendment 1 A4: controls for the identity-dose slope (the six morph-free networks of the
morph-free study (A47 I-3) and the stored file size of each morph), and MorDIFF strata by expression subset and gender
(gender from the release's folder names). Same strata, dose, bootstrap and statistic as ev1_partC.py.
Run: python3 -I src/EV1/ev1_partC2.py [--smoke]
"""
import csv, json, sys, time, pathlib
import numpy as np
from scipy.stats import spearmanr

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import ev1_common as K  # noqa: E402

SMOKE = "--smoke" in sys.argv
B = 50 if SMOKE else K.B_FULL
T0 = time.time()
A46 = pathlib.Path("/mnt/t7/smad_heldout/a46/feat/a46_feat.npz")
MDR = pathlib.Path("/mnt/t7/Datasety/downloads/MorDIFF/MorDIFF_crop")


def log(*a):
    print(f"[{time.time() - T0:7.1f}s]", *a, flush=True)


def main():
    rows = [r for r in K.eval_rows() if r["set"] != "mad22" and r["variant"] != "chip"]
    I = K.Index(rows)
    ids = [r["id"] for r in rows]
    z = np.load(A46, allow_pickle=False)
    E = z["emb"].astype(np.float64)
    E /= np.linalg.norm(E, axis=1, keepdims=True)
    raw = {str(k).split("|", 1)[1]: e for k, e, f in zip(z["keys"], E, z["found"]) if str(k).startswith("raw|") and f}
    gender = {}
    for d in MDR.glob("*_front_*_aligned"):
        g = "female" if "_female_" in d.name else "male"
        for p in (d / "morphed").glob("*.png"):
            gender[p.stem] = g
    allp = sorted({p for r in rows if r["pers"] for p in r["pers"]})
    D = K.Draw(allp, B, K.SEED)
    strata = {}
    for f in K.FAMS:
        mi = [i for i in I.morph(f) if rows[i]["pers"][0] != rows[i]["pers"][1]]
        for st, ee in (("neutral-neutral", "0303"), ("smiling-smiling", "0808")):
            ix = [i for i in mi if rows[i]["expr"] == ee]
            if ix:
                strata[(f, st)] = ix
                if f == "mordiff":
                    for g in ("female", "male"):
                        jx = [i for i in ix if gender.get(rows[i]["stem"]) == g]
                        strata[(f, f"{st}, {g}")] = jx
    n_nog = sum(1 for i in I.morph("mordiff") if rows[i]["stem"] not in gender)
    log("MorDIFF morphs without a gender folder:", n_nog, {k: len(v) for k, v in strata.items() if k[0] == "mordiff"})
    if SMOKE:
        strata = {k: v[:40] for k, v in strata.items()}
    cache = {}
    for k, ix in strata.items():
        e = k[1][:2]
        e = "03" if k[1].startswith("neutral") else "08"
        delta = np.array([1 - raw[rows[i]["pers"][0] + "_" + e] @ raw[rows[i]["pers"][1] + "_" + e] for i in ix])
        cache[k] = (np.array(ix), delta, K.RankCache(delta, D.w([rows[i]["pers"] for i in ix])))
    # controls
    ctrl = [("file size of the stored morph (bytes)", np.array([float(r["file_bytes"]) for r in rows]))]
    for d in K.morph_free_networks():
        ctrl.append((d["name"], K.load_scores(d, "eval", ids)[0]))
    if SMOKE:
        ctrl = ctrl[:2]
    CT = []
    for nm, s in ctrl:
        for k, (ix, delta, RC) in cache.items():
            x = s[ix]
            r_ = spearmanr(x, delta).statistic
            lo, hi = K.ci(RC.spearman(x))
            CT.append([nm, k[0], k[1], len(ix), float(r_), lo, hi, bool(lo > 0 or hi < 0)])
        log(nm, [(r[1][:6], r[2][:8], round(r[4], 2), r[7]) for r in CT if r[0] == nm][:8])
    # detectors on the MorDIFF gender strata
    dets = K.detectors()
    if SMOKE:
        dets = [d for d in dets if d["name"] in ("MADation ViT-L/14 release", "SelfMAD release, own preprocessing")]
    DG = []
    gk = [k for k in cache if k[0] == "mordiff" and "," in k[1]]
    for det in dets:
        s, _ = K.load_scores(det, "eval", ids)
        boot = det["block"] != "other recipe"
        for k in gk:
            ix, delta, RC = cache[k]
            x = s[ix]
            r_ = spearmanr(x, delta).statistic
            lo, hi = K.ci(RC.spearman(x)) if boot else ("", "")
            DG.append([det["name"], det["block"], k[0], k[1], len(ix), float(r_), lo, hi])
    # readings per family / stratum
    read = {}
    for k in cache:
        sl = [r[0] for r in CT if (r[1], r[2]) == k and r[7]]
        read[f"{k[0]} {k[1]}"] = ("the dose test can be produced by construction here: a control has a slope (" + "; ".join(sl) + ")"
                                  if sl else "no control has a slope (both controls' 95% intervals include 0)")
    log(json.dumps(read, indent=0)[:1500])
    if SMOKE:
        print("smoke ok")
        return
    W_ = lambda fn_, hdr, R: (lambda fh: (csv.writer(fh).writerow(hdr), csv.writer(fh).writerows(R)))(open(K.OUT / fn_, "w", newline=""))  # noqa: E731
    W_("AM_C_controls.csv", ["control", "family", "stratum", "n", "spearman", "lo95", "hi95", "has_slope"], CT)
    W_("AM_C_mordiff_gender.csv", ["detector", "block", "family", "stratum", "n", "spearman", "lo95", "hi95"], DG)
    json.dump({"B": B, "seed": K.SEED, "n_mordiff_without_gender_folder": n_nog,
               "strata_n": {f"{k[0]} {k[1]}": len(v[0]) for k, v in cache.items()}, "readings": read},
              open(K.OUT / "AM_partC.json", "w"), indent=1)
    log("written")


if __name__ == "__main__":
    main()
