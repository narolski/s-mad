"""CB1 amendment 5, cell 13-MFN: AD1 main contrast R2 (A43 arm D20, one-photo DiffAE reconstruction at 20 steps) vs R4
(arm B20, our same-pair DiffAE morph at 20 steps), AUC with R4 positive, MixFaceNet-MAD 'rel' scores (our frames); two-way
person bootstrap (B 10,000, seed 0, as AD1; a morph weighted by both contributors' draw counts). Also R3 (C20) vs R2 and the
bridge published (A) vs B20.
  python3 -I sa1_a43_mfn.py SCORES.npz OUT.json"""
import csv, json, sys
import numpy as np
from scipy.stats import rankdata
z = np.load(sys.argv[1]); S = dict(zip(z["id"].tolist(), z["logit_noTTA"].astype(float)))
rows = list(csv.DictReader(open("/mnt/t7/smad_heldout/a43/data/manifests/a43.csv")))
# amendment 6 checks: ids in manifest order, all rows, finite; consistency of the eval.csv frames with stored A12REL scores
assert z["id"].tolist() == [r["id"] for r in rows], "id order"
assert np.isfinite(z["logit_noTTA"]).all(), "non-finite"
st = np.load("/home/narolski/mambamorph-code/smadcvpr_runs/A12_scored/A12REL/mixfacenet_mad_smdd/scores_eval.npz")
sp = {e: i for i, e in enumerate(st["id"])}
ev = [r["id"] for r in rows if r["id"] in sp]
d = np.abs(np.array([S[e] for e in ev]) - st["logit_noTTA"][[sp[e] for e in ev]])
CONS = dict(n=len(ev), median=float(np.median(d)), max=float(d.max()), passed=bool(np.median(d) <= 0.05 and d.max() <= 0.5))
print("consistency", CONS)
G = {}
for r in rows:
    if r["arm"]:
        G.setdefault(r["arm"], []).append((S[r["id"]], r["src_a"][:3], (r["src_b"] or r["src_a"])[:3]))
    elif r["family"] == "mordiff_bona":
        pid = r["path"].split("/")[-1][:3]
        G.setdefault("R0", []).append((S[r["id"]], pid, pid))
per = sorted({p for v in G.values() for _, a, b in v for p in (a, b)}); pi = {p: i for i, p in enumerate(per)}
rng = np.random.default_rng(0); C = rng.multinomial(len(per), [1 / len(per)] * len(per), size=10000).astype(float)
def wauc(pos, neg, w_pos=None, w_neg=None):
    s = np.r_[pos, neg]; r = rankdata(s)
    if w_pos is None:
        n1, n0 = len(pos), len(neg); return (r[:n1].sum() - n1 * (n1 + 1) / 2) / (n1 * n0)
    # weighted Mann-Whitney via pairwise comparison (sizes are small)
    gt = (pos[:, None] > neg[None, :]) + 0.5 * (pos[:, None] == neg[None, :])
    W = w_pos[:, None] * w_neg[None, :]
    return float((gt * W).sum() / W.sum())
def contrast(pk, nk):
    P, N = G[pk], G[nk]
    ps = np.array([x[0] for x in P]); ns = np.array([x[0] for x in N])
    pa = np.array([pi[x[1]] for x in P]); pb = np.array([pi[x[2]] for x in P])
    na = np.array([pi[x[1]] for x in N]); nb = np.array([pi[x[2]] for x in N])
    pw = lambda c, a, b: c[a] * np.where(a == b, 1.0, c[b])
    reps = [wauc(ps, ns, pw(c, pa, pb), pw(c, na, nb)) for c in C]
    return dict(auc=round(float(wauc(ps, ns)), 3), ci95=[round(float(np.percentile(reps, 2.5)), 3), round(float(np.percentile(reps, 97.5)), 3)],
                n_pos=len(P), n_neg=len(N), boot=len(C))
val = contrast("A", "R0")
VALID = bool(val["auc"] > 0.5 and val["ci95"][0] > 0.5)
out = {"consistency_check": CONS, "validity: published MorDIFF (A) vs FRLL photos R0": val, "valid": VALID,
       "R4 (B20) vs R2 (D20) [AD1 main]": contrast("B20", "D20"), "R3 (C20) vs R2 (D20)": contrast("C20", "D20"),
       "R4 (B20) vs R3 (C20)": contrast("B20", "C20"), "published (A) vs B20 [bridge]": contrast("A", "B20")}
json.dump(out, open(sys.argv[2], "w"), indent=1); print(json.dumps(out, indent=1))
