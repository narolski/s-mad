"""SM1 amendment A12 item 2 (post hoc, review F2): sharpness acceptance inside each storage stratum.

Arms d, e, f, seed-401 compositions (compose.py): 2,000 seeded morphs + 2,000 seeded genuine-class images per arm
(numpy default_rng(401)); variance of the Laplacian of the grey image at stored size (cv2.imread grey) and at the
loader's 224 px (common.ImageItems load, as lapvar.py). Strata: 256 px, 80 px (a47 shrink copies), 256 px + JPEG,
80 px + JPEG (arm f). Per stratum: AUC = P(variance of a morph < variance of a genuine image), with the Hanley-McNeil
SE; pooled AUC for reference only (an artefact of pooling strata, never a reduction). Two-variable rule: 5-fold
stratified out-of-fold AUC (seed 401) of a logistic regression on (stratum indicators, log variance at 224 px), and
descriptively with stratum x log-variance interactions and at stored size.

Single process (DGX limit: at most 2 processes, OMP 2, nice 10).
  python3 -I a12_sharp.py -> RES/a12_sharp.json
"""
import csv
import json
import pathlib
import sys

import numpy as np

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import sm1_common as K  # noqa: E402
import sm1_stats as S  # noqa: E402
import lapvar as L  # noqa: E402

FL = K.OUT / "flists"
N = 2000


def stratum(i):
    j = i.endswith("_J90") or i.endswith("_J70")
    b = i[:-4] if j else i
    return ("80px" if (b.startswith("bfS:") or b.endswith("_S")) else "256px") + ("+jpeg" if j else "")


def gsub(i):
    """genuine sub-kind: render or warped half."""
    b = i[:-4] if (i.endswith("_J90") or i.endswith("_J70")) else i
    b = b[:-2] if b.endswith("_S") else b
    return "half" if (b.endswith("_hA") or b.endswith("_hB")) else "render"


def auc_hm(vm, vg):
    """AUC(morph variance < genuine variance) and Hanley-McNeil SE."""
    a = float(S.wauc(-vm, -vg, np.ones((1, len(vm))), np.ones((1, len(vg))))[0])
    q1, q2 = a / (2 - a), 2 * a * a / (1 + a)
    m, n = len(vm), len(vg)
    se = np.sqrt((a * (1 - a) + (m - 1) * (q1 - a * a) + (n - 1) * (q2 - a * a)) / (m * n))
    return dict(auc=round(a, 4), se=round(float(se), 4), n_morph=m, n_genuine=n,
                median_morph=round(float(np.median(vm)), 1), median_genuine=round(float(np.median(vg)), 1))


def rule(X, y, seed=401):
    from sklearn.linear_model import LogisticRegression
    from sklearn.metrics import roc_auc_score
    from sklearn.model_selection import StratifiedKFold
    p = np.zeros(len(y))
    for tr, te in StratifiedKFold(5, shuffle=True, random_state=seed).split(X, y):
        mu, sd = X[tr].mean(0), X[tr].std(0) + 1e-12
        m = LogisticRegression(max_iter=2000).fit((X[tr] - mu) / sd, y[tr])
        p[te] = m.predict_proba((X[te] - mu) / sd)[:, 1]
    return round(float(roc_auc_score(y, p)), 4)


def design(strata, lv, inter=False):
    lev = sorted(set(strata))
    D = [np.log(lv)]
    for s in lev[1:]:
        ind = np.array([x == s for x in strata], float)
        D.append(ind)
        if inter:
            D.append(ind * np.log(lv))
    return np.stack(D, 1)


def main():
    if not sys.flags.isolated:
        sys.exit("run with python3 -I")
    idp = {}
    for nm in ("train_bf", "train_arme_bfS", "train_armc_halves", "train_arme_hS", "train_armc", "train_arme_cS",
               "train_armf_jpeg"):
        for r in csv.DictReader(open(FL / f"{nm}.csv")):
            idp[r["id"]] = r["path"]
    L._init()
    res = {}
    for arm in ("d", "e", "f"):
        c = json.load(open(K.OUT / f"compose/{arm}_s401.json"))
        rng = np.random.default_rng(401)
        m = [c["morph"][i] for i in rng.choice(len(c["morph"]), N, replace=False)]
        g = [c["genuine"][i] for i in rng.choice(len(c["genuine"]), N, replace=False)]
        ids = m + g
        y = np.array([1] * len(m) + [0] * len(g))
        v = np.array([L.lv(idp[i]) for i in ids])          # (n, 2): stored, loader224
        st = [stratum(i) for i in ids]
        o = dict(pooled_reference_only={k: auc_hm(v[y == 1, j], v[y == 0, j])
                                        for j, k in ((0, "stored"), (1, "loader224"))}, strata={})
        for s in sorted(set(st)):
            ix = np.array([x == s for x in st])
            o["strata"][s] = {k: auc_hm(v[ix & (y == 1), j], v[ix & (y == 0), j])
                              for j, k in ((0, "stored"), (1, "loader224"))}
            o["strata"][s]["morph_share"] = round(float(y[ix].mean()), 3)
            sub = {}
            for gs in ("render", "half"):
                jx = ix & (y == 0) & np.array([gsub(i) == gs for i in ids])
                if jx.sum() >= 50:
                    sub[gs] = {k: auc_hm(v[ix & (y == 1), j], v[jx, j]) for j, k in ((0, "stored"), (1, "loader224"))}
            o["strata"][s]["morph_vs_genuine_subkind"] = sub
        o["two_variable_rule"] = dict(
            registered_stratum_plus_logvar224=rule(design(st, v[:, 1]), y),
            with_interactions_224=rule(design(st, v[:, 1], True), y),
            stratum_plus_logvar_stored=rule(design(st, v[:, 0]), y),
            stratum_only=rule(design(st, np.ones(len(y)))[:, 1:] if len(set(st)) > 1 else np.zeros((len(y), 1)), y))
        res[arm] = o
        print(arm, json.dumps(o, indent=1), flush=True)
    res["note"] = ("post hoc (A12 item 2); acceptance needs AUC <= 0.65 inside every stratum; the pooled AUC mixes "
                   "storage sizes (a network sees the stratum) and is never a reduction")
    json.dump(res, open(K.RES / "a12_sharp.json", "w"), indent=1)


if __name__ == "__main__":
    main()
