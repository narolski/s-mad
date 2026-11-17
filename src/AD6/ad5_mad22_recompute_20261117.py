"""AD5 (released weights RW + authors'-recipe retrains H_native): MAD22 five-family cells on the main paper's
Table 1 genuine definitions (2026-11-17). S = G22_raw (204); H = E7aln22_<family> (204, family-specific
aligned-history genuine). Same score files and metric (final_metrics.eer on logit_noTTA) as the 16 Nov aggregate,
which used pooled G22_raw+G22_aln (408). Validation: RW v1 must reproduce Table 1 Panel A; pooled cells must
reproduce the 16 Nov aggregate."""
import csv, sys, json, collections, numpy as np
sys.path.insert(0, "/home/narolski/smad-next/src/FINAL")
import final_metrics as FM
MAN = "/mnt/t7/smad_next/RS1/regen_pack/manifests/athena_manifest.csv"
PROD = "/mnt/t7/smad_next/RS1/results_rented"; OWN = "/mnt/t7/smad_next/AD5/scores_retrains"
tags = {r["id"]: r["set"] for r in csv.DictReader(open(MAN)) if r["label"] != ""}
F = ["FaceMorpher", "OpenCV", "Webmorph", "MIPGAN_I", "MIPGAN_II"]
def sets(f):
    z = np.load(f, allow_pickle=True); d = collections.defaultdict(list); miss = 0
    for i, v in zip(map(str, z["id"]), np.asarray(z["logit_noTTA"], float)):
        t = tags.get(i)
        if t is None: miss += 1
        else: d[t].append(v)
    assert miss == 0, (f, miss); return d
def eer(p, n): return 100 * FM.eer(np.r_[p, n], np.r_[np.ones(len(p)), np.zeros(len(n))].astype(int))
def cells(d):
    return {fam: {"S": eer(d["M22_" + fam], d["G22_raw"]), "H": eer(d["M22_" + fam], d["E7aln22_" + fam]),
                  "pooled": eer(d["M22_" + fam], d["G22_raw"] + d["G22_aln"])} for fam in F}
out = {}
for v in ("v1", "v2"):
    for arm, rel, pat in (("B", "madation_vitb16", "madation_B_s40%d"), ("L", "madation_vitl14", "madation_L_s40%d"),
                          ("X", "mixfacenet_mad_smdd", "mixfacenet_X_s40%d")):
        out[f"RW_{arm}_{v}"] = cells(sets(f"{PROD}/prod_{v}_rented/scores/scores_rel_{rel}__{v}.npz"))
        per = [cells(sets(f"{OWN}/scores_rel_{pat % s}__ad5{v}.npz")) for s in range(1, 6)]
        out[f"H_{arm}_{v}"] = {fam: {k: (float(np.mean([p[fam][k] for p in per])), float(np.std([p[fam][k] for p in per], ddof=1)))
                                     for k in ("S", "H", "pooled")} for fam in F}
json.dump(out, open(sys.argv[1], "w"), indent=1)
for k, c in out.items():
    print(k, " ".join(f"{fam[:6]} S={(c[fam]['S'] if k.startswith('RW') else c[fam]['S'][0]):.2f} H={(c[fam]['H'] if k.startswith('RW') else c[fam]['H'][0]):.2f} P={(c[fam]['pooled'] if k.startswith('RW') else c[fam]['pooled'][0]):.2f}" for fam in F))
