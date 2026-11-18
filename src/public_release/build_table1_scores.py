"""PRIVATE helper (not for the public release): collects the score files behind Table 1 into one compact file
with pool labels only (no image identifiers, no paths). Sources are the verified archives on the lab drive."""
import numpy as np, csv, glob, os, collections
FAMS = ["FaceMorpher", "OpenCV", "Webmorph", "MIPGAN_I", "MIPGAN_II"]
rows = []  # (method, seed, pool, logit)
# 1) Sb, sealed read (seeds 403-407)
S = "/tmp/claude-1000/-home-narolski-mambamorph/c2840dc9-dd37-4619-9347-d8a76080b93f/scratchpad/final2/FINAL_mad22_final2/scores"
for seed in range(403, 408):
    z = np.load(f"{S}/PN1_Sb_s{seed}__final.npz", allow_pickle=True)
    for i, v in zip(map(str, z["id"]), z["logit"]):
        d = os.path.dirname(i)
        if d == "eval/mad22c/native/BonaFide": p = "genuine_raw"
        elif d.startswith("eval/mad22c/native/"): p = "morph_" + d.split("/")[-1]
        elif d.startswith("eval/mad22c/e7/"): p = "genuine_history_" + d.split("/")[-1]
        else: continue                      # border-equalised forms are not in Table 1
        rows.append(("Sb", seed, p, float(v)))
# 2) released weights (RW): MADation, MixFaceNet-MAD on release crops v1; SelfMAD with its own preprocessing
z = np.load("/mnt/t7/smad_next/FINAL/release_scores_existing.npz", allow_pickle=True)
NAME = {"madation_vitb16": "MADation-B16-RW", "madation_vitl14": "MADation-L14-RW", "mixfacenet_mad_smdd": "MixFaceNet-MAD-RW", "selfmad_hrnet_w18": "SelfMAD-RW"}
def std(pool):
    if pool == "G22_raw": return "genuine_raw"
    if pool.startswith("E7aln22_"): return "genuine_history_" + pool[8:]
    if pool.startswith("M22_"): return "morph_" + pool[4:]
for det, var, pool, v in zip(z["det"], z["variant"], z["pool"], z["logit"]):
    if (det == "selfmad_hrnet_w18") != (var == "own_dgx") or (det != "selfmad_hrnet_w18" and var != "v1"): continue
    p = std(str(pool))
    if p: rows.append((NAME[str(det)], 0, p, float(v)))
zs = np.load("/mnt/t7/smad_next/FINAL/selfmad/selfmad_mad22_scores.npz", allow_pickle=True)
for pool, v in zip(zs["pool"], zs["logit"]):
    p = std(str(pool))
    if p: rows.append(("SelfMAD-RW", 0, p, float(v)))
# 3) comparators retrained with our recipe (Panel B), seeds 401-405
tags = {r["id"]: r["set"] for r in csv.DictReader(open("/mnt/t7/smad_next/RS1/regen_pack/manifests/athena_manifest.csv")) if r["label"] != ""}
for arm, name in (("madation_B_sbr", "MADation-B16-ours"), ("madation_L_sbr", "MADation-L14-ours"), ("mixfacenet_X_sbr", "MixFaceNet-MAD-ours")):
    for s in range(1, 6):
        z = np.load(f"/home/narolski/ad6_stage/scores_h_sbr/scores_h_{arm}_s40{s}__ad6v1.npz", allow_pickle=True)
        for i, v in zip(map(str, z["id"]), z["logit_noTTA"]):
            p = std(tags.get(i, ""))
            if p: rows.append((name, 400 + s, p, float(v)))
m, sd, p, l = zip(*rows)
np.savez_compressed("results/table1/scores_table1.npz", method=np.array(m), seed=np.array(sd, np.int16), pool=np.array(p), logit=np.array(l, np.float32))
print(len(rows), collections.Counter(m))
