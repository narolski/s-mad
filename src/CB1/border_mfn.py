"""CB1 amendment 7 (A): MixFaceNet-MAD release on our frames (stored A12REL eval scores, logit_noTTA) against the
black-border share of each 512-px frame (share of pixels with R = G = B = 0; read only). FRLL-Morphs orig morphs, the
204 FRLL photos (orig) and the E7 (resmatch) pools.
  python3 -I border_mfn.py OUT_DIR"""
import csv, json, pathlib, sys
import numpy as np
from PIL import Image
from scipy.stats import spearmanr, rankdata
OUT = pathlib.Path(sys.argv[1]); OUT.mkdir(parents=True, exist_ok=True)
D = pathlib.Path("/home/narolski/mambamorph-code/smadcvpr_data")
st = np.load("/home/narolski/mambamorph-code/smadcvpr_runs/A12_scored/A12REL/mixfacenet_mad_smdd/scores_eval.npz")
S = dict(zip(st["id"].tolist(), st["logit_noTTA"].astype(float)))
rows = [r for r in csv.DictReader(open(D / "manifests/eval.csv")) if r["set"] == "frllm" and r["variant"] in ("orig", "resmatch")]
rec = []
for i, r in enumerate(rows):
    a = np.asarray(Image.open(D / r["path"]).convert("RGB"))
    b = float((a.max(axis=2) == 0).mean())
    stem = pathlib.Path(r["path"]).stem
    pa = stem[:3]; pb = stem[4:7] if r["label"] == "1" else pa
    rec.append(dict(id=r["id"], family=r["family"], variant=r["variant"], label=int(r["label"]), border=b, logit=S[r["id"]], pa=pa, pb=pb))
    if i % 2000 == 0:
        print(i, len(rows), flush=True)
with open(OUT / "border_mfn_rows.csv", "w", newline="") as f:
    w = csv.DictWriter(f, fieldnames=list(rec[0])); w.writeheader(); w.writerows(rec)
per = sorted({x["pa"] for x in rec} | {x["pb"] for x in rec}); pi = {p: i for i, p in enumerate(per)}
C = np.random.default_rng(20261111).multinomial(len(per), [1 / len(per)] * len(per), size=2000).astype(float)
def auc_ci(pos, neg):
    if not pos or not neg:
        return None
    ps = np.array([x["logit"] for x in pos]); ns = np.array([x["logit"] for x in neg])
    r = rankdata(np.r_[ps, ns]); n1, n0 = len(ps), len(ns)
    a = (r[:n1].sum() - n1 * (n1 + 1) / 2) / (n1 * n0)
    gt = (ps[:, None] > ns[None, :]) + 0.5 * (ps[:, None] == ns[None, :])
    pa = np.array([pi[x["pa"]] for x in pos]); pb = np.array([pi[x["pb"]] for x in pos]); na = np.array([pi[x["pa"]] for x in neg])
    reps = []
    for c in C:
        wp = c[pa] * c[pb]; wn = c[na]
        W = wp[:, None] * wn[None, :]
        reps.append((gt * W).sum() / max(W.sum(), 1e-12))
    return dict(auc=round(float(a), 3), ci95=[round(float(np.percentile(reps, 2.5)), 3), round(float(np.percentile(reps, 97.5)), 3)], n_pos=n1, n_neg=n0)
gen = [x for x in rec if x["family"] == "frll_bona" and x["variant"] == "orig"]
res = {"genuine_orig_border": dict(median=float(np.median([x["border"] for x in gen])), max=float(max(x["border"] for x in gen)))}
for fam in ("amsl", "facemorpher", "opencv", "stylegan", "webmorph"):
    m = [x for x in rec if x["family"] == fam and x["label"] == 1]
    e7 = [x for x in rec if x["family"] == fam and x["variant"] == "resmatch"]
    bm = [x for x in m if x["border"] <= 0.005]
    rho = spearmanr([x["border"] for x in m], [x["logit"] for x in m])
    res[fam] = dict(morph_border_median=round(float(np.median([x["border"] for x in m])), 4),
                    share_morphs_border_le_0p005=round(len(bm) / len(m), 3),
                    e7_border_median=round(float(np.median([x["border"] for x in e7])), 4) if e7 else None,
                    spearman_logit_vs_border_morphs=[round(float(rho.correlation), 3), float(rho.pvalue)],
                    auc_all_morphs_vs_genuine=auc_ci(m, gen), auc_border_matched_morphs_vs_genuine=auc_ci(bm, gen),
                    auc_all_morphs_vs_e7=auc_ci(m, e7))
json.dump(res, open(OUT / "border_mfn.json", "w"), indent=1); print(json.dumps(res, indent=1))
