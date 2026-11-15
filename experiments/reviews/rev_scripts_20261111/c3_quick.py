"""Reviewer: does C3's 'non-zero pixels' mask remove the black out-of-hull background of the landmark morphs? Decode only (60 images per group)."""
import csv, pathlib, numpy as np
from PIL import Image
EV = pathlib.Path("/home/narolski/mambamorph-code/smadcvpr_data")
rows = [r for r in csv.DictReader(open(EV/"manifests/eval.csv")) if r["set"]=="frllm" and r["variant"]=="orig"]
def st(fam, lab, n=60):
    rr = [r for r in rows if r["family"]==fam and r["label"]==lab][::max(1, len([r for r in rows if r["family"]==fam and r["label"]==lab])//n)][:n]
    z, nb, face_mean, nz_mean = [], [], [], []
    for r in rr:
        a = np.asarray(Image.open(EV/r["path"]).convert("RGB"), dtype=np.float64); s = a.sum(2)
        z.append((s==0).mean()); nb.append(((s>0)&(s<45)).mean())
        face_mean.append(a[180:400,150:362].mean()); nz_mean.append(a[s>0].mean())
    return np.median(z), np.median(nb), np.array(face_mean), np.array(nz_mean)
from scipy.stats import mannwhitneyu
gz, gnb, gf, gn = st("frll_bona","0",102)
print(f"genuine      exactly-zero {gz:.3f}  near-black non-zero {gnb:.3f}")
for fam in ("facemorpher","opencv","amsl","webmorph","stylegan"):
    z, nb, f, n = st(fam,"1")
    a_nz = mannwhitneyu(n, gn).statistic/(len(n)*len(gn)); a_f = mannwhitneyu(f, gf).statistic/(len(f)*len(gf))
    print(f"{fam:12s} exactly-zero {z:.3f}  near-black non-zero {nb:.3f} | single-stat AUC, mean over non-zero pixels {max(a_nz,1-a_nz):.2f} vs mean inside a central face box {max(a_f,1-a_f):.2f}")
