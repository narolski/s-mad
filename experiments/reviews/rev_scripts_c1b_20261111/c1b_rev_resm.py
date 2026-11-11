"""Reviewer: 03-vs-08 ordering on the registered resolution-matched variants of the same 204 genuine frames (existing scores),
and whether the background-noise difference between 03 and 08 frames survives in each registered variant (read-only decode)."""
import csv, re, collections, os
import numpy as np
from PIL import Image
MC = "/home/narolski/mambamorph-code/"; S = MC + "smadcvpr_runs/A12_scored/"; D = MC + "smadcvpr_data/"
allrows = [r for r in csv.DictReader(open(D + "manifests/eval.csv")) if r["set"] in ("frllm", "dim", "mordiff") and r["label"] == "0"]
def rel(n): return (S + f"A12REL/{n}/scores_eval.npz", "score_noTTA")
def rec(arch, seed, ck): return (S + f"A12BR/a12_{arch}_madation_r224_d0_train90_none_lr3.33e-06_s{seed}_r/scores_eval_{ck}.npz", "score")
DET = collections.OrderedDict()
for k, n in (("REL ViT-L/14", "madation_vitl14"), ("REL ViT-B/16", "madation_vitb16"), ("REL FE ViT-B/16", "madation_fe_vitb16"), ("REL FE ViT-L/14", "madation_fe_vitl14"), ("REL SelfMAD ourpipe", "selfmad_hrnet_w18")): DET[k] = rel(n)
for ck in ("last", "es"):
    for s in range(1, 6): DET[f"M3L s{s} {ck}"] = rec("clip_vitl14", s, ck)
    for s in range(1, 9): DET[f"M3 s{s} {ck}"] = rec("clip_vitb16", s, ck)
SC = {}
for n, (f, k) in DET.items():
    z = np.load(f, allow_pickle=False); SC[n] = dict(zip(z["id"].tolist(), z[k].astype(np.float64)))
V = collections.OrderedDict(); PATH = {}
for r in allrows:
    m = re.match(r"^(\d{3})_(\d{2})_", r["path"].rsplit("/", 1)[1])
    key = f"{r['family']}:{r['variant']}"
    V.setdefault(key, {})[(m.group(1), m.group(2))] = r["id"]; PATH[r["id"]] = r["path"]
order = ["frll_bona:orig", "frll_bona:blur1", "frll_bona:resample50", "frll_bona:jpeg50", "frll_bona:chip", "stylegan:resmatch", "amsl:resmatch", "webmorph:resmatch", "facemorpher:resmatch", "opencv:resmatch",
         "dim_a:resmatch", "greedy_dim:resmatch", "mordiff_bona:orig", "mordiff:resmatch"]
order = [o for o in order if o in V]
print("variants:", {k: len(v) for k, v in V.items()})
def ge(g): return float((np.diff(g, axis=0) ** 2).mean() + (np.diff(g, axis=1) ** 2).mean())
print("\n## noise check on the frames themselves: share of persons with 08 > 03 and median ratio 08/03 of gradient energy in background boxes (top-left 5:90,5:40 / top-right 5:90,472:507) and forehead 90:150,200:310, mouth 300:432,150:366; and zero-pixel share")
for o in order:
    G = V[o]; P = sorted({p for p, e in G if (p, "03") in G and (p, "08") in G}); st = {}
    for (p, e), i in G.items():
        with Image.open(D + PATH[i]) as im: a = np.asarray(im.convert("RGB"), dtype=np.float64)
        g = a.mean(2); st[(p, e)] = (ge(g[5:90, 5:40]), ge(g[5:90, 472:507]), ge(g[90:150, 200:310]), ge(g[300:432, 150:366]), float((a.sum(2) == 0).mean()), a.shape[0])
    out = []
    for j, nm in enumerate(("bgL", "bgR", "forehead", "mouth")):
        a3 = np.array([st[(p, "03")][j] for p in P]); a8 = np.array([st[(p, "08")][j] for p in P]); ok = (a3 > 0) & (a8 > 0)
        out.append(f"{nm} {np.mean(a8[ok] > a3[ok]):.2f} x{np.median(a8[ok] / a3[ok]):.2f} (abs03 {np.median(a3):.1f})")
    print(f"  {o:22s} n={len(P)} size {st[(P[0],'03')][5]} zero {np.median([st[(p,'03')][4] for p in P]):.2f} | " + " | ".join(out))
print("\n## AUC_wp (share of persons with s(03) > s(08)) per registered variant of the same 204 photos")
print("  detector | " + " | ".join(order))
def wp(n, o):
    G = V[o]; P = sorted({p for p, e in G if (p, "03") in G and (p, "08") in G}); sc = SC[n]
    a = np.array([sc[G[(p, "03")]] for p in P]); b = np.array([sc[G[(p, "08")]] for p in P]); return np.mean((a > b) + 0.5 * (a == b))
for n in ["REL ViT-L/14", "REL ViT-B/16", "REL FE ViT-B/16", "REL FE ViT-L/14", "REL SelfMAD ourpipe"]:
    print(f"  {n:18s} | " + " | ".join(f"{wp(n, o):.2f}" for o in order))
for grp, names in (("M3L last", [f"M3L s{s} last" for s in range(1, 6)]), ("M3 last", [f"M3 s{s} last" for s in range(1, 9)]), ("M3L es", [f"M3L s{s} es" for s in range(1, 6)]), ("M3 es", [f"M3 s{s} es" for s in range(1, 9)])):
    print(f"  {grp:18s} | " + " | ".join(f"{np.mean([wp(n, o) for n in names]):.2f} ({min(wp(n, o) for n in names):.2f}-{max(wp(n, o) for n in names):.2f})" for o in order))
