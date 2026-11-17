"""H5: SelfMAD (released + retrains s401-405) MAD22 EERs, common-protocol rel-mode scores on the regen crops
(WCSS 6344965, verified set in /home/narolski/ad6_stage/scores_selfmad_m22_final). Definitions as main-paper
Table 1: S = G22_raw, H = E7aln22_<family>; pooled = G22_raw+G22_aln (408). Metric final_metrics.eer on logit_noTTA.
Note: these are NOT SelfMAD's own preprocessing (dlib-81 crops) used for the SelfMAD RW row in Table 1."""
import csv, sys, json, collections, numpy as np
sys.path.insert(0, "/home/narolski/smad-next/src/FINAL")
import final_metrics as FM
MAN = "/mnt/t7/smad_next/RS1/regen_pack/manifests/athena_manifest.csv"; D = "/home/narolski/ad6_stage/scores_selfmad_m22_final"
tags = {r["id"]: r["set"] for r in csv.DictReader(open(MAN)) if r["label"] != ""}
F = ["FaceMorpher", "OpenCV", "Webmorph", "MIPGAN_I", "MIPGAN_II"]
def sets(f):
    z = np.load(f, allow_pickle=True); d = collections.defaultdict(list)
    for i, v in zip(map(str, z["id"]), np.asarray(z["logit_noTTA"], float)):
        if i in tags: d[tags[i]].append(v)
    return d
def eer(p, n): return 100 * FM.eer(np.r_[p, n], np.r_[np.ones(len(p)), np.zeros(len(n))].astype(int))
def cells(d):
    c = {f: {"S": eer(d["M22_" + f], d["G22_raw"]), "H": eer(d["M22_" + f], d["E7aln22_" + f]),
             "pooled": eer(d["M22_" + f], d["G22_raw"] + d["G22_aln"])} for f in F}
    for k in ("S", "H", "pooled"):
        c.setdefault("LM2", {})[k] = float(np.mean([c[f][k] for f in ("OpenCV", "Webmorph")]))
        c.setdefault("M4", {})[k] = float(np.mean([c[f][k] for f in ("OpenCV", "Webmorph", "MIPGAN_I", "MIPGAN_II")]))
    return c
out = {}
for v in ("v1", "v2"):
    out[f"RW_{v}"] = cells(sets(f"{D}/scores_rel_selfmad_hrnet_w18__m22{v}.npz"))
    per = [cells(sets(f"{D}/scores_rel_selfmad_S_s40{s}__m22{v}.npz")) for s in range(1, 6)]
    out[f"H_{v}_perseed"] = per
    out[f"H_{v}"] = {f: {k: (float(np.mean([p[f][k] for p in per])), float(np.std([p[f][k] for p in per], ddof=1))) for k in ("S", "H", "pooled")} for f in per[0]}
json.dump(out, open(sys.argv[1], "w"), indent=1)
C = F + ["LM2", "M4"]
for v in ("v1", "v2"):
    for k in ("S", "H", "pooled"):
        print(f"{v} {k:6s} RW      " + " ".join(f"{out[f'RW_{v}'][f][k]:6.2f}" for f in C))
        print(f"{v} {k:6s} retrain " + " ".join(f"{out[f'H_{v}'][f][k][0]:6.2f}" for f in C) + "   sd " + " ".join(f"{out[f'H_{v}'][f][k][1]:.2f}" for f in C))
