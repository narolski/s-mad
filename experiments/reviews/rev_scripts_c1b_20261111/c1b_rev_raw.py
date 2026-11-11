"""Reviewer: raw FRLL neutral_front vs smiling_front files: bytes and flat-backdrop noise at native resolution (read-only decode);
colour balance of the aligned frames; dose-response of the score gap with the noise gap."""
import os, re, csv, collections
import numpy as np
from PIL import Image
from scipy.stats import spearmanr
B = "/mnt/t7/Datasety/downloads/frll_base/extracted/"
def ge(g): return float((np.diff(g, axis=0) ** 2).mean() + (np.diff(g, axis=1) ** 2).mean())
R = {}
for d, e in (("neutral_front", "03"), ("smiling_front", "08")):
    for f in sorted(os.listdir(B + d)):
        m = re.match(r"^(\d{3})_(\d{2})\.jpg$", f)
        if not m: continue
        with Image.open(B + d + "/" + f) as im: a = np.asarray(im.convert("RGB"), dtype=np.float64)
        g = a.mean(2)
        R[(m.group(1), e)] = dict(bytes=os.path.getsize(B + d + "/" + f), tl=ge(g[20:140, 20:140]), tr=ge(g[20:140, -140:-20]), sd_tl=float(g[20:140, 20:140].std()), all=ge(g),
                                  lum_tl=float(g[20:140, 20:140].mean()))
P = sorted({p for p, e in R}); print("persons", len(P))
for k in ("bytes", "tl", "tr", "sd_tl", "all", "lum_tl"):
    a = np.array([R[(p, "03")][k] for p in P]); b = np.array([R[(p, "08")][k] for p in P])
    print(f"  raw {k:7s}: median 03 {np.median(a):10.3f}  08 {np.median(b):10.3f}  share 08 > 03 {np.mean(b > a):.3f}  median ratio {np.median(b / a):.3f}  range ratio {np.min(b/a):.2f}-{np.max(b/a):.2f}")
# aligned-frame colour balance
MC = "/home/narolski/mambamorph-code/"; D = MC + "smadcvpr_data/"; S = MC + "smadcvpr_runs/A12_scored/"
rows = [r for r in csv.DictReader(open(D + "manifests/eval.csv")) if r["family"] == "frll_bona" and r["variant"] == "orig"]
C = {}; ID = {}
for r in rows:
    m = re.match(r"^(\d{3})_(\d{2})_", r["path"].rsplit("/", 1)[1])
    with Image.open(D + r["path"]) as im: a = np.asarray(im.convert("RGB"), dtype=np.float64)
    face = a[150:430, 150:366].reshape(-1, 3).mean(0); bg = a[5:90, 5:40].reshape(-1, 3).mean(0)
    mx = a[150:430, 150:366].max(2); mn = a[150:430, 150:366].min(2)
    C[(m.group(1), m.group(2))] = dict(face_R=face[0], face_G=face[1], face_B=face[2], face_RminusB=face[0] - face[2], face_sat=float(((mx - mn) / np.maximum(mx, 1)).mean()),
                                       bg_R=bg[0], bg_B=bg[2], bg_RminusB=bg[0] - bg[2], face_contrast=float(a[150:430, 150:366].mean(2).std()))
    ID[(m.group(1), m.group(2))] = r["id"]
print("\n aligned frames, colour/tone (face box 150:430,150:366; background 5:90,5:40):")
for k in ("face_R", "face_G", "face_B", "face_RminusB", "face_sat", "face_contrast", "bg_R", "bg_B", "bg_RminusB"):
    a = np.array([C[(p, "03")][k] for p in P]); b = np.array([C[(p, "08")][k] for p in P])
    print(f"  {k:14s}: median 03 {np.median(a):8.3f}  08 {np.median(b):8.3f}  share 08 > 03 {np.mean(b > a):.3f}  median diff {np.median(b - a):+.3f}")
# dose-response of the score gap with the raw noise gap
def logit(p):
    p = np.clip(p, 1e-12, 1 - 1e-12); return np.log(p / (1 - p))
nz = np.log(np.array([R[(p, "08")]["tl"] for p in P])) - np.log(np.array([R[(p, "03")]["tl"] for p in P]))
by = np.log(np.array([R[(p, "08")]["bytes"] for p in P])) - np.log(np.array([R[(p, "03")]["bytes"] for p in P]))
print("\n Spearman of the per-person logit gap (03 - 08) with log raw backdrop-noise ratio (08/03) and log raw byte ratio (08/03):")
dets = [("REL ViT-L/14", S + "A12REL/madation_vitl14/scores_eval.npz", "score_noTTA"), ("REL ViT-B/16", S + "A12REL/madation_vitb16/scores_eval.npz", "score_noTTA"), ("REL FE ViT-B/16", S + "A12REL/madation_fe_vitb16/scores_eval.npz", "score_noTTA")]
dets += [(f"M3L s{s} last", S + f"A12BR/a12_clip_vitl14_madation_r224_d0_train90_none_lr3.33e-06_s{s}_r/scores_eval_last.npz", "score") for s in range(1, 6)]
dets += [(f"M3 s{s} last", S + f"A12BR/a12_clip_vitb16_madation_r224_d0_train90_none_lr3.33e-06_s{s}_r/scores_eval_last.npz", "score") for s in range(1, 9)]
for n, f, k in dets:
    z = np.load(f, allow_pickle=False); sc = dict(zip(z["id"].tolist(), z[k].astype(np.float64)))
    d = logit(np.array([sc[ID[(p, "03")]] for p in P])) - logit(np.array([sc[ID[(p, "08")]] for p in P]))
    print(f"  {n:16s} rho(noise) {spearmanr(d, nz).statistic:+.2f}  rho(bytes) {spearmanr(d, by).statistic:+.2f}")
