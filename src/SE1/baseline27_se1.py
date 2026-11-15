"""Seam-shortcut training arm (SE1), prereg section 7.5: the 27-statistic baseline trained like the SE arm on the
ladder TRAINING hosts (amendment-15 model, unchanged: StandardScaler + logistic regression, C = 1, balanced, no
tuning), read on the development rows the networks are read on. Zero GPU; development data only; computed and
committed before any SE1 result tar is pulled.
  Training: attacks R4 OpenCV (both persons training hosts) + S4 OpenCV (train_morph = 1);
            negatives R0, R2w, S0, S3, R3, R3m (OpenCV, training hosts).
  Reads   : AUC dev R4 vs R3 (OpenCV, FaceMorpher), dev S4 vs S3 (OpenCV, FaceMorpher), FFHQ landmark_combined
            orig vs resmatch; 2,000 bootstraps within class, default_rng(20261141).
  python3 -I baseline27_se1.py -> experiments/SE1_seam-shortcut-training-arm/baseline27_se1.json
"""
import csv
import json
import pathlib
import sys

import numpy as np

sys.path.insert(0, "/home/narolski/smad-next/src/PN1")
import pn1lib as K  # noqa: E402
import splice as SP  # noqa: E402

EVAL = "/mnt/t7/smad_next/SE1/manifests/se_eval.csv"
OUT = pathlib.Path("/home/narolski/smad-next/experiments/SE1_seam-shortcut-training-arm/baseline27_se1.json")


def fauc(p, n):
    from scipy.stats import rankdata
    r = rankdata(np.r_[p, n])[: len(p)]
    return float((r.sum() - len(p) * (len(p) + 1) / 2) / (len(p) * len(n)))


def cues(f):
    z = np.load(f)
    return {str(i): c for i, c in zip(z["ids"], z["cues"])}, [str(n) for n in z["names"]]


def main():
    from sklearn.linear_model import LogisticRegression
    from sklearn.pipeline import make_pipeline
    from sklearn.preprocessing import StandardScaler
    lad, nl = cues(K.AF0 / "cues" / "ar1.npz")
    spl, ns = cues(K.PN1 / "cues" / "splice_nat.npz")
    lc, nc = cues(K.PN1 / "cues" / "a14_lcomb.npz")
    assert nl == ns == nc
    allc = {**lad, **spl, **lc}
    cat = [r for r in K.catalog() if r["fam"] == "ladder" and r["role"] == "train" and r["strength"] == ""]
    split, _ = K.split_tables()
    pos = [r["id"] for r in cat if r["rung"] == "R4" and r["tool"] == "opencv"
           and all(split.get(p, {}).get("role") == "train" for p in r["persons"])]
    neg = [r["id"] for r in cat if (r["rung"] in ("R0", "R2w", "R3", "R3m") and r["tool"] in ("opencv", "none"))]
    sp = SP.splice_rows()
    pos += [r["id"] for r in sp if r["rung"] == "S4" and r["tool"] == "opencv" and r["role"] == "train" and r["train_morph"] == "1"]
    neg += [r["id"] for r in sp if r["rung"] in ("S0", "S3") and r["tool"] == "opencv" and r["role"] == "train"]
    P = np.array([allc[i] for i in pos]); N = np.array([allc[i] for i in neg])
    mdl = make_pipeline(StandardScaler(), LogisticRegression(C=1.0, max_iter=2000, class_weight="balanced"))
    mdl.fit(np.r_[P, N], np.r_[np.ones(len(P)), np.zeros(len(N))])
    ev = list(csv.DictReader(open(EVAL)))

    def ids(**kw):
        return [r["id"] for r in ev if all(r[k] == v for k, v in kw.items())]
    reads = {}
    for t in ("opencv", "facemorpher"):
        tt = "cv" if t == "opencv" else "fm"
        reads[f"R4_vs_R3_{tt}"] = (ids(fam="ladder", role="dev", rung="R4", strength="", tool=t),
                                   ids(fam="ladder", role="dev", rung="R3", strength="", tool=t))
        reads[f"S4_vs_S3_{tt}"] = (ids(fam="splice", role="dev", rung="S4", tool=t),
                                   ids(fam="splice", role="dev", rung="S3", tool=t))
    reads["lcomb"] = (ids(fam="ffhq_lcomb", rung="landmark_combined_orig"), ids(fam="ffhq_lcomb", rung="landmark_combined_resmatch"))
    rng = np.random.default_rng(20261141)
    out = dict(n_train_pos=len(P), n_train_neg=len(N), model="StandardScaler+LogisticRegression(C=1, balanced)")
    for k, (a, b) in reads.items():
        assert len(a) and len(b) and all(i in allc for i in a + b), k
        sa = mdl.decision_function(np.array([allc[i] for i in a])); sb = mdl.decision_function(np.array([allc[i] for i in b]))
        bs = [fauc(sa[rng.integers(0, len(sa), len(sa))], sb[rng.integers(0, len(sb), len(sb))]) for _ in range(2000)]
        out[f"auc_{k}"] = fauc(sa, sb)
        out[f"ci_{k}"] = [float(np.percentile(bs, 2.5)), float(np.percentile(bs, 97.5))]
        out[f"n_{k}"] = [len(a), len(b)]
    OUT.write_text(json.dumps(out, indent=1))
    print(json.dumps(out, indent=1))


if __name__ == "__main__":
    if not sys.flags.isolated:
        sys.exit("run with python3 -I")
    main()
