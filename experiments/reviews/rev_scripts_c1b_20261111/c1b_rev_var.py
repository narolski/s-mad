"""Reviewer: (b) 03-vs-08 ordering on the registered variants of the same 204 frames (existing scores only);
(a) extra-region gradient energy on the FRLL frames; (c) release on FERET in logit units; (d) release mean EER; (e,f) es / last tables."""
import csv, re, collections, os
import numpy as np
MC = "/home/narolski/mambamorph-code/"; S = MC + "smadcvpr_runs/A12_scored/"; D = MC + "smadcvpr_data/"
allrows = list(csv.DictReader(open(D + "manifests/eval.csv")))
def rel(n): return (S + f"A12REL/{n}/scores_eval.npz", "score_noTTA")
def rec(arch, seed, ck): return (S + f"A12BR/a12_{arch}_madation_r224_d0_train90_none_lr3.33e-06_s{seed}_r/scores_eval_{ck}.npz", "score")
DET = collections.OrderedDict()
for k, n in (("REL ViT-L/14", "madation_vitl14"), ("REL ViT-B/16", "madation_vitb16"), ("REL FE ViT-B/16", "madation_fe_vitb16"), ("REL FE ViT-L/14", "madation_fe_vitl14")): DET[k] = rel(n)
for ck in ("last", "es"):
    for s in range(1, 6): DET[f"M3L s{s} {ck}"] = rec("clip_vitl14", s, ck)
    for s in range(1, 9): DET[f"M3 s{s} {ck}"] = rec("clip_vitb16", s, ck)
SC = {}
for n, (f, k) in DET.items():
    z = np.load(f, allow_pickle=False); SC[n] = dict(zip(z["id"].tolist(), z[k].astype(np.float64)))
# ---- (b) variants
V = collections.defaultdict(dict)
for r in allrows:
    if r["family"] == "frll_bona":
        m = re.match(r"^(\d{3})_(\d{2})_(.+)\.png$", r["path"].rsplit("/", 1)[1]); V[r["variant"]][(m.group(1), m.group(2))] = r["id"]
print("## (b) frll_bona variants registered in eval.csv:", {v: len(d) for v, d in V.items()})
var = [v for v in ("orig", "jpeg90", "jpeg70", "jpeg50", "blur1", "resample50", "chip", "resmatch") if v in V]
print("  AUC_wp (share of persons with s(03) > s(08)) on each registered variant of the same frames; n persons with both in brackets if < 102")
print("  detector | " + " | ".join(var))
def wp(n, v):
    G = V[v]; P = sorted({p for p, e in G if (p, "03") in G and (p, "08") in G}); sc = SC[n]
    a = np.array([sc[G[(p, "03")]] for p in P]); b = np.array([sc[G[(p, "08")]] for p in P]); return np.mean((a > b) + 0.5 * (a == b)), len(P)
for n in ["REL ViT-L/14", "REL ViT-B/16", "REL FE ViT-B/16", "REL FE ViT-L/14"]:
    print(f"  {n:16s} | " + " | ".join(f"{wp(n, v)[0]:.3f}" + (f" [{wp(n, v)[1]}]" if wp(n, v)[1] != 102 else "") for v in var))
for grp, names in (("M3L last", [f"M3L s{s} last" for s in range(1, 6)]), ("M3 last", [f"M3 s{s} last" for s in range(1, 9)]), ("M3L es", [f"M3L s{s} es" for s in range(1, 6)]), ("M3 es", [f"M3 s{s} es" for s in range(1, 9)])):
    print(f"  {grp:16s} | " + " | ".join(f"{np.mean([wp(n, v)[0] for n in names]):.3f} ({min(wp(n, v)[0] for n in names):.2f}-{max(wp(n, v)[0] for n in names):.2f})" for v in var))
# does a variant move both photos? mean logit shift orig -> variant, for 03 and 08
def logit(p):
    p = np.clip(p, 1e-12, 1 - 1e-12); return np.log(p / (1 - p))
print("  median logit shift (variant - orig) for neutral / smiling frames, and median within-person logit gap (03 - 08) orig -> variant:")
for n in ["REL ViT-L/14", "M3L s1 last", "M3 s1 last", "M3L s1 es"]:
    out = []
    for v in var[1:]:
        G, G0 = V[v], V["orig"]; P = sorted({p for p, e in G if (p, "03") in G and (p, "08") in G}); sc = SC[n]
        d3 = np.median([logit(sc[G[(p, "03")]]) - logit(sc[G0[(p, "03")]]) for p in P]); d8 = np.median([logit(sc[G[(p, "08")]]) - logit(sc[G0[(p, "08")]]) for p in P])
        g0 = np.median([logit(sc[G0[(p, "03")]]) - logit(sc[G0[(p, "08")]]) for p in P]); g1 = np.median([logit(sc[G[(p, "03")]]) - logit(sc[G[(p, "08")]]) for p in P])
        out.append(f"{v}: {d3:+.2f}/{d8:+.2f}, gap {g0:+.3f}->{g1:+.3f}")
    print(f"  {n:14s} " + "; ".join(out))
# ---- (a) extra regions
from PIL import Image
G0 = V["orig"]; P = sorted({p for p, e in G0}); path = {r["id"]: r["path"] for r in allrows if r["family"] == "frll_bona" and r["variant"] == "orig"}
def ge(g): return float((np.diff(g, axis=0) ** 2).mean() + (np.diff(g, axis=1) ** 2).mean())
REG = {"forehead 90:150,200:310": (90, 150, 200, 310), "bg top-left 5:90,5:40": (5, 90, 5, 40), "bg top-right 5:90,472:507": (5, 90, 472, 507), "top hair 5:50,190:320": (5, 50, 190, 320),
       "eyes 190:235,150:366": (190, 235, 150, 366), "nose 235:300,215:300": (235, 300, 215, 300), "mouth 300:432,150:366": (300, 432, 150, 366), "left edge mid 200:330,5:40": (200, 330, 5, 40)}
st = {k: {} for k in REG}; lum = {k: {} for k in REG}
for (p, e), i in G0.items():
    with Image.open(D + path[i]) as im: g = np.asarray(im.convert("RGB"), dtype=np.float64).mean(2)
    for k, (r0, r1, c0, c1) in REG.items(): st[k][(p, e)] = ge(g[r0:r1, c0:c1]); lum[k][(p, e)] = float(g[r0:r1, c0:c1].mean())
print("\n## (a) FRLL frames: gradient energy per region, share of persons with 08 > 03, median ratio 08/03; mean luminance share 08 > 03")
for k in REG:
    a = np.array([st[k][(p, "03")] for p in P]); b = np.array([st[k][(p, "08")] for p in P]); la_ = np.array([lum[k][(p, "03")] for p in P]); lb_ = np.array([lum[k][(p, "08")] for p in P])
    print(f"  {k:28s} ge 08>03: {np.mean(b > a):.3f}  median ratio {np.median(b / a):.3f}   | lum 08>03: {np.mean(lb_ > la_):.3f} median diff {np.median(lb_ - la_):+.2f}")
