"""Panel C comparability recompute (2026-11-17): AD6 matched-recipe retrains on the SAME genuine definitions as
Panel A. S = G22_raw (204), H = E7aln22_<family> (204, family-specific aligned-history genuine), old = G22_raw+G22_aln.
Same metric as everywhere: final_metrics.eer on logit_noTTA. Validation: released rows must reproduce Panel A."""
import csv, sys, glob, collections, hashlib, numpy as np
sys.path.insert(0, "/home/narolski/smad-next/src/FINAL")
import final_metrics as FM
man = "/mnt/t7/smad_next/RS1/regen_pack/manifests/athena_manifest.csv"
tags = {r["id"]: (r["set"], r["label"]) for r in csv.DictReader(open(man)) if r["label"] != ""}
F = ["FaceMorpher", "OpenCV", "Webmorph", "MIPGAN_I", "MIPGAN_II"]
def sets(f):
    z = np.load(f, allow_pickle=True); d = collections.defaultdict(list); miss = 0
    for i, v in zip(map(str, z["id"]), np.asarray(z["logit_noTTA"], float)):
        t = tags.get(i)
        if t is None: miss += 1
        else: d[t[0]].append(v)
    return d, miss
def eer(p, n): return 100*FM.eer(np.r_[p, n], np.r_[np.ones(len(p)), np.zeros(len(n))].astype(int))
def cells(d):
    out = {}
    for fam in F:
        p = d["M22_" + fam]
        out[fam] = {"S": eer(p, d["G22_raw"]), "H": eer(p, d["E7aln22_" + fam]), "old": eer(p, d["G22_raw"] + d["G22_aln"]),
                    "n": (len(p), len(d["G22_raw"]), len(d["E7aln22_" + fam]))}
    for k in ("S", "H", "old"):
        out.setdefault("LM2", {})[k] = np.mean([out[f][k] for f in ("OpenCV", "Webmorph")])
        out.setdefault("M4", {})[k] = np.mean([out[f][k] for f in ("OpenCV", "Webmorph", "MIPGAN_I", "MIPGAN_II")])
    return out
COLS = F + ["LM2", "M4"]
def row(c, k): return " ".join("%6.2f" % c[x][k] for x in COLS)
print("cols:", COLS)
R = "/mnt/t7/smad_next/RS1/results_rented"
for v in ("v1", "v2"):
    print(f"\n=== released weights, {v} (validation vs Panel A: S->H)")
    for det in ("madation_vitb16", "madation_vitl14", "mixfacenet_mad_smdd"):
        d, m = sets(f"{R}/prod_{v}_rented/scores/scores_rel_{det}__{v}.npz")
        c = cells(d); print(f"{det:22s} S {row(c,'S')}\n{'':22s} H {row(c,'H')}  missing {m}")
A = "/home/narolski/ad6_stage/scores_h_sbr"
res = {}
for arm in ("madation_B_sbr", "madation_L_sbr", "mixfacenet_X_sbr"):
    for v in ("ad6v1", "ad6v2"):
        fs = sorted(glob.glob(f"{A}/scores_h_{arm}_s40?__{v}.npz")); per = []
        for f in fs:
            d, m = sets(f); assert m == 0, (f, m); per.append(cells(d))
        res[(arm, v)] = per
        print(f"\n=== {arm} {v}: {len(fs)} seeds")
        for k, lab in (("old", "G22 raw+aln (current Panel C)"), ("S", "raw genuine S"), ("H", "aligned-history H")):
            mean = {x: {k: np.mean([p[x][k] for p in per])} for x in COLS}
            sd = {x: {k: np.std([p[x][k] for p in per], ddof=1)} for x in COLS}
            print(f"  {lab:30s} mean {row(mean,k)}\n  {'':30s} sd   {row(sd,k)}")
        print("  per-seed H M4:", ["%.2f" % p["M4"]["H"] for p in per], " n(morph,raw,E7):", per[0]["OpenCV"]["n"])
import json
json.dump({f"{a}|{v}": [{x: {k: float(p[x][k]) for k in ("S", "H", "old")} for x in COLS} for p in per]
           for (a, v), per in res.items()}, open("panelC_recompute_20261117.json", "w"), indent=1)
print("\nsha256 json", hashlib.sha256(open("panelC_recompute_20261117.json","rb").read()).hexdigest()[:16])
