"""Own-crop re-score of the audit rows (RS1): descriptive additions requested by the review of 12 Nov (zero GPU, existing
files). Writes experiments/RS1_own-crop-rescore/rs1_review_addons.json and prints a summary.
  H-new-2: variant 2, MADation ViT-B/16: D (100 steps) and D20 flag rates at t5, C20 vs D20 AUC.
  H-new-3: per-family JPEG-vs-PNG logit shift (jpegcheck scores): AMSL morph shift vs photo shift, per release.
  H-new-4: ViT-L/14 (variant 2) saturation of genuine logits and where the aligned-history shift sits.
  F3: aligned history pools at t5 on aligned native vs the same aligned photos without history.
  F4: miss rates at the release's 0.5 rule per cell (100 - flagged morphs).
"""
import csv
import json
import pathlib

import numpy as np

RES = pathlib.Path("/home/narolski/smad-next/experiments/RS1_own-crop-rescore")
R = pathlib.Path("/mnt/t7/smad_next/RS1/results_rented")
A46 = pathlib.Path("/mnt/t7/smad_heldout/a46_corrective_20261108")
out = {}
rd = lambda f: list(csv.DictReader(open(RES / f)))  # noqa: E731
V2 = "variant 2: corrected crop, PNG (secondary)"
# H-new-2
lf = {(r["detector"], r["platform"], r["threshold"], r["arm"]): r["flagged"] for r in rd("rs1_ladder_flags.csv")}
la = {(r["detector"], r["platform"], r["contrast"]): r["auc"] for r in rd("rs1_ladder.csv")}
d = "MADation ViT-B/16 (LoRA) release"
out["H-new-2"] = dict(D_t5=lf[(d, V2, "t5", "D")], D20_t5=lf[(d, V2, "t5", "D20")], C20_t5=lf[(d, V2, "t5", "C20")],
                      C20_vs_D20=la[(d, V2, "same-person mix C20 vs reconstruction D20")],
                      D_vs_E=la[(d, V2, "reconstruction D (100 steps) vs stored-small photo E")],
                      falsifier="D flagged < 50% at t5 or C20 vs D20 > 0.65")
# H-new-3
pool = {r["id"]: r["pool"] for r in csv.DictReader(open(A46 / "manifests/a46c_rgb_clip.csv"))}
h3 = {}
for f in sorted(pathlib.Path("/mnt/t7/smad_next/RS1/jpegcheck").glob("scores_rel_*__jpegcheck.npz")):
    z = np.load(f)
    lg = dict(zip(z["id"].tolist(), z["logit_noTTA"].astype(float)))
    per = {}
    for p in sorted({pool[i[2:]] for i in lg if i.startswith("j_")}):
        ids = [i[2:] for i in lg if i.startswith("j_") and pool[i[2:]] == p]
        dd = np.array([lg["j_" + i] - lg["p_" + i] for i in ids])
        per[p] = dict(n=len(ids), mean_shift=round(float(dd.mean()), 3), median_shift=round(float(np.median(dd)), 3))
    h3[f.name[11:-15]] = per
out["H-new-3"] = h3
# H-new-4
z = np.load(R / "prod_v2_rented/scores/scores_rel_madation_vitl14__v2.npz")
man = {r["id"]: r for r in csv.DictReader(open("/mnt/t7/smad_next/RS1/athena/athena_manifest.csv"))}
L = dict(zip(z["id"].tolist(), z["logit_noTTA"].astype(float)))
S = dict(zip(z["id"].tolist(), z["score_noTTA"].astype(np.float32)))
g = [i for i in L if man[i]["set"] == "G_raw"]
sv = np.array([S[i] for i in g])
vals, cnt = np.unique(sv, return_counts=True)
gl = np.array([L[i] for i in g])
alnN = {man[i]["photo"]: L[i] for i in L if man[i]["set"] == "Galn_frll"}
alnE = {man[i]["photo"]: L[i] for i in L if man[i]["set"] == "E7aln_amsl"}
ph = sorted(set(alnN) & set(alnE))
base = np.array([alnN[p] for p in ph])
shift = np.array([alnE[p] - alnN[p] for p in ph])
q = np.median(base)
out["H-new-4"] = dict(n_genuine=len(g), share_tied_float32_score=round(float(cnt[cnt > 1].sum() / len(g)), 3),
                      share_at_min_score=round(float(np.mean(sv == sv.min())), 3),
                      genuine_logit_median=round(float(np.median(gl)), 3), genuine_logit_sd=round(float(gl.std()), 3),
                      amsl_history_shift_low_half=round(float(shift[base <= q].mean()), 3),
                      amsl_history_shift_high_half=round(float(shift[base > q].mean()), 3),
                      falsifier="under 20% tied")
# F3 and F4
f3 = {}
for r in rd("rs1_flags.csv"):
    if r["threshold"] == "t5_aligned":
        f3.setdefault(f"{r['detector']} | {r['platform'][:9]} | {r['cell']}", {})[r["pool"]] = r["flagged"]
out["F3_t5_on_aligned_native"] = f3
f4 = {}
for r in rd("rs1_pool_rates.csv"):
    if r["kind"] == "morph" and r["threshold_pool"].startswith("release"):
        f4[f"{r['detector']} | {r['platform'][:9]} | {r['pool']}"] = round(100 - float(r["flagged_pt"]), 1)
out["F4_miss_at_release_rule"] = f4
json.dump(out, open(RES / "rs1_review_addons.json", "w"), indent=1)
print(json.dumps({k: out[k] for k in ("H-new-2", "H-new-4")}, indent=1))
for k, v in h3.items():
    print(k, {p: v[p]["mean_shift"] for p in v})
