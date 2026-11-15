"""Standing adversary (ADV), amendment 3 (post hoc; lead's request 13 Nov ~20:30): weight-based history balancing of FFHQ
landmark_combined over all 3,000 rows (lcomb_ipw). No image operation; no network score.

Propensity: LogisticRegression(C = 1e6, i.e. unpenalised, max_iter 3000) of the label on
  [logit of the round-0 cross-fitted surround score (floors/lcomb_regional_heldout.csv column surround_logreg),
   pre_ied (ffhqm_meta.csv sidecar), pre_ied squared], standardised, fitted on all 3,000 rows.
Stabilised inverse-probability weights: morph w = P(morph) / p, genuine w = P(genuine) / (1 - p), with p clipped to
its own 1st and 99th percentiles (trimming). Reported: the weighted cross-fitted surround floor, file floor and
face-region floor (single, logreg, gbt; models trained with the weights, AUC weighted on held-out rows; ADV person
folds), and the effective sample size per class (sum w)^2 / sum w^2. Usable by a consumer only if the effective
sample size is at least 300 per class and the weighted surround floor is at most 0.60 for both logreg and gbt.
Outputs: floors/lcomb_ipw_weights.csv (id, label, weight), floors/lcomb_ipw_build.json.
"""
import csv
import json
import sys

import numpy as np

sys.path.insert(0, "/home/narolski/smad-next/src/adversary")
import contrasts as C  # noqa: E402
import floor as FL  # noqa: E402
import run_floors as RF  # noqa: E402

META = "/mnt/t7/smad_heldout/ffhq_morphs/manifests/ffhqm_meta.csv"


def wauc(s, y, w):
    """Weighted Mann-Whitney AUC (ties count one half)."""
    o = np.argsort(s, kind="mergesort")
    s, y, w = s[o], y[o], w[o]
    wn_below, tot, i = 0.0, 0.0, 0
    while i < len(s):
        j = i
        while j + 1 < len(s) and s[j + 1] == s[i]:
            j += 1
        wp = w[i:j + 1][y[i:j + 1] == 1].sum()
        wn = w[i:j + 1][y[i:j + 1] == 0].sum()
        tot += wp * (wn_below + 0.5 * wn)
        wn_below += wn
        i = j + 1
    return float(tot / (w[y == 1].sum() * w[y == 0].sum()))


def wfloors(X, y, w, persons):
    g = FL.components(persons)
    fl = FL.folds(y, g)
    out = {}
    for kind in ("single", "logreg", "gbt"):
        s = np.full(len(y), np.nan)
        for tr, te in fl:
            Xtr, Xte, _ = FL._clean(X[tr], X[te])
            if kind == "single":
                best = (-1, 0, 1)
                for j in range(Xtr.shape[1]):
                    a = wauc(Xtr[:, j], y[tr], w[tr])
                    for sg, v in ((1, a), (-1, 1 - a)):
                        if v > best[0]:
                            best = (v, j, sg)
                s[te] = best[2] * Xte[:, best[1]]
                s[te] = np.searchsorted(np.sort(best[2] * Xtr[:, best[1]]), s[te], side="right") / len(tr)
            else:
                m = FL._model(kind)
                if kind == "logreg":
                    m.fit(Xtr, y[tr], logisticregression__sample_weight=w[tr])
                else:
                    m.fit(Xtr, y[tr], sample_weight=w[tr])
                s[te] = m.predict_proba(Xte)[:, 1]
        out[kind] = wauc(s, y, w)
    return out


def main():
    from sklearn.linear_model import LogisticRegression
    from sklearn.preprocessing import StandardScaler
    import feats as F
    rl = C.build("lcomb")
    ids = [i for i, *_ in rl]
    y = np.array([l for _, _, l, _ in rl])
    persons = [p for *_, p in rl]
    meta = {r["id"]: float(r["pre_ied"]) for r in csv.DictReader(open(META))}
    e = np.array([meta[i.replace("lcomb_", "")] for i in ids])
    rh = {r["id"]: float(r["surround_logreg"]) for r in csv.DictReader(open(RF.FDIR / "lcomb_regional_heldout.csv"))}
    s = np.clip(np.array([rh[i] for i in ids]), 1e-6, 1 - 1e-6)
    Z = StandardScaler().fit_transform(np.c_[np.log(s / (1 - s)), e, e ** 2])
    p = LogisticRegression(C=1e6, max_iter=3000).fit(Z, y).predict_proba(Z)[:, 1]
    lo, hi = np.percentile(p, [1, 99])
    p = np.clip(p, lo, hi)
    pi = y.mean()
    w = np.where(y == 1, pi / p, (1 - pi) / (1 - p))
    ess = {c: float(w[y == c].sum() ** 2 / (w[y == c] ** 2).sum()) for c in (1, 0)}
    rg = RF.regmap()
    S = np.stack([rg[p_][[i for i, n in enumerate(F.REGION_NAMES) if n.startswith("SURR:")]] for _, p_, _, _ in rl])
    Fa = np.stack([rg[p_][[i for i, n in enumerate(F.REGION_NAMES) if n.startswith("FACE:")]] for _, p_, _, _ in rl])
    X, nm = RF.X_of(rl)
    Fi = X[:, [i for i, n in enumerate(nm) if n in RF.FILE_SIZE]]
    rep = dict(n_morph=int(y.sum()), n_genuine=int(len(y) - y.sum()), trim_percentiles=[1, 99],
               propensity_clip=[float(lo), float(hi)], ess_morph=ess[1], ess_genuine=ess[0],
               weighted_surround_floor=wfloors(S, y, w, persons), weighted_file_floor=wfloors(Fi, y, w, persons),
               weighted_face_floor=wfloors(Fa, y, w, persons),
               weighted_all_cue_floor=wfloors(X, y, w, persons))
    rep["usable"] = bool(min(ess.values()) >= 300 and max(rep["weighted_surround_floor"]["logreg"],
                                                          rep["weighted_surround_floor"]["gbt"]) <= 0.60)
    with open(RF.FDIR / "lcomb_ipw_weights.csv", "w", newline="") as f:
        wr = csv.writer(f)
        wr.writerow(["id", "label", "weight"])
        for i, l, ww in zip(ids, y, w):
            wr.writerow([i, int(l), repr(float(ww))])
    (RF.FDIR / "lcomb_ipw_build.json").write_text(json.dumps(rep, indent=1))
    print(json.dumps(rep, indent=1))


if __name__ == "__main__":
    if not sys.flags.isolated:
        sys.exit("run with python3 -I")
    main()
