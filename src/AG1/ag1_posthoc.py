"""AG1 post-hoc analyses registered in prereg amendment 7 (after the independent review, after all scores were read;
every number here is post hoc). DGX CPU, thread caps.
Outputs: experiments/AG1/read/posthoc.json and posthoc.md; experiments/AG1/read_athena_only/ (the full reader on the
159 Athena hosts of the primary pool and all FRLL MIPGAN-I hosts; rented-only rungs R2s, AG3, AG3T and MIPGAN-II left out).
Usage: python -I ag1_posthoc.py
"""
import csv
import json
import pathlib
import sys
import zlib

import numpy as np

HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import ag1_read as AR  # noqa: E402

DATA = pathlib.Path("/mnt/t7/smad_next/AG1/data")
SC = pathlib.Path("/mnt/t7/smad_next/AG1/scoring/a41g_out/ag1")
LOGS = pathlib.Path("/mnt/t7/smad_next/AG1/results")
PHOTOS = pathlib.Path("/mnt/t7/smad_next/AG1/inputs/pack/photos.json")
OUT = pathlib.Path("/home/narolski/smad-next/experiments/AG1/read")
PRIM = ("madation_vitb16", "madation_vitl14", "selfmad_hrnet_w18__own")
B = 10000


def strat_auc(pos, neg, sc, key, D, q=5):
    """AUC within quintiles of a pooled covariate (key(row)), combined with fixed weights n_pos * n_neg; interval from
    the same dyadic draw."""
    v = np.array([key(r) for r in pos + neg])
    cuts = np.quantile(v, np.linspace(0, 1, q + 1)[1:-1])
    num, rep, den = 0.0, 0.0, 0.0
    for k in range(q):
        P = [r for r in pos if int(np.searchsorted(cuts, key(r))) == k]
        N = [r for r in neg if int(np.searchsorted(cuts, key(r))) == k]
        if not P or not N:
            continue
        sp, sn = np.array([sc[r["id"]] for r in P]), np.array([sc[r["id"]] for r in N])
        w = len(P) * len(N)
        num += w * AR.auc(sp, sn)
        rep = rep + w * AR.wauc(sp, sn, D.w([r["pa"] for r in P], [r["pb"] for r in P]),
                                D.w([r["pa"] for r in N], [r["pb"] for r in N]))
        den += w
    return {"auc": num / den, "ci": AR.ci(rep / den)} if den else None


def thumb_oof(pos, neg):
    from sklearn.linear_model import LogisticRegression
    from sklearn.model_selection import GroupKFold
    from sklearn.pipeline import make_pipeline
    from sklearn.preprocessing import StandardScaler
    rows = pos + neg
    X = np.stack([AR.BASE[r["id"]]["thumb"] for r in rows])
    y = np.r_[np.ones(len(pos)), np.zeros(len(neg))]
    g = np.array([r["pa"] for r in rows])
    oof = np.zeros(len(y))
    for tr, te in GroupKFold(n_splits=5).split(X, y, g):
        m = make_pipeline(StandardScaler(), LogisticRegression(max_iter=2000)).fit(X[tr], y[tr])
        oof[te] = m.decision_function(X[te])
    return {r["id"]: float(o) for r, o in zip(rows, oof)}


def shape_dist(k1, k2):
    """mean 5-point distance after similarity normalisation of each point set to its two eyes (inter-eye units)."""
    def norm(k):
        k = np.asarray(k, float)
        e = (k[0] + k[1]) / 2
        d = k[1] - k[0]
        s = np.hypot(*d)
        c, si = d / s
        R = np.array([[c, si], [-si, c]])
        return (k - e) @ R.T / s
    return float(np.linalg.norm(norm(k1) - norm(k2), axis=1).mean())


def main():
    import cv2
    from scipy.stats import spearmanr
    rows, P = AR.load_rows(DATA, LOGS, PHOTOS, False)
    S = AR.load_scores(rows, SC, False)
    z = dict(np.load(DATA / "baselines.npz"))
    AR.BASE = {i: {"bytes": z["bytes"][k], "lapvar": z["lapvar"][k], "hfband": z["hfband"][k], "sym": z["sym"][k],
                   "thumb": z["thumb"][k]} for k, i in enumerate(z["id"].tolist())}
    oz = np.load(DATA / "oracle_glint.npz")
    E = dict(zip(oz["id"].tolist(), oz["emb"]))
    pool = "primary"
    sub = [r for r in rows if AR.in_pool(r, pool) and r["gen"] in ("mip1", "camera")]
    pers = sorted({r["pa"] for r in rows if AR.in_pool(r, pool)} | {r["pb"] for r in rows if AR.in_pool(r, pool)})
    D = AR.Draw(pers, B, AR.SEED + zlib.crc32(pool.encode()) % 100000)
    g = {k: [r for r in sub if r["rung"] == k] for k in ("R0", "R2", "R2s", "R3", "R3m", "R4", "AG3", "AG3T")}
    R2s1 = [r for r in g["R2"] if r["photo_a"].endswith("__s1")]
    res = {"_label": "post hoc (amendment 7); primary pool MIPGAN-I unless stated"}
    contrasts = {"R2>R4": (g["R4"], g["R2"]), "R2s>R4": (g["R4"], g["R2s"]), "R3>R4": (g["R4"], g["R3"]),
                 "R2>R3": (g["R3"], g["R2"]), "R0>R2": (g["R2"], g["R0"])}
    oofs = {k: thumb_oof(*v) for k, v in contrasts.items()}
    res["stratified"] = {}
    for rel in PRIM:
        sc = S[rel]
        res["stratified"][rel] = {}
        for k, (pos, neg) in contrasts.items():
            d = {}
            for bk in ("bytes", "lapvar", "hfband", "sym"):
                d[bk] = strat_auc(pos, neg, sc, lambda r, bk=bk: AR.BASE[r["id"]][bk], D)
            d["thumb_probe"] = strat_auc(pos, neg, sc, lambda r, k=k: oofs[k][r["id"]], D)
            res["stratified"][rel][k] = d
    # d' decomposition (shares of the R2>R4 step)
    res["dprime"] = {}
    for rel in PRIM + ("selfmad_hrnet_w18__rel",):
        cf = AR.contrast_fn(S[rel], D)
        c24, c23, c34 = cf(g["R4"], g["R2"]), cf(g["R3"], g["R2"]), cf(g["R4"], g["R3"])
        d24 = np.array([AR.dprime(x) for x in c24["rep"]])
        res["dprime"][rel] = {
            "second_photo_share": {"est": AR.dprime(c23["auc"]) / AR.dprime(c24["auc"]),
                                   "ci": AR.ci(np.array([AR.dprime(x) for x in c23["rep"]]) / d24)},
            "second_identity_share": {"est": AR.dprime(c34["auc"]) / AR.dprime(c24["auc"]),
                                      "ci": AR.ci(np.array([AR.dprime(x) for x in c34["rep"]]) / d24)}}
    # matched-alpha AG3 minus AG3T (same hosts, AUC against the hosts' R2 s1)
    hosts = sorted({r["pa"] for r in g["AG3"]})
    neg = [r for r in R2s1 if r["pa"] in hosts]
    res["matched_alpha"] = {}
    cam = {r["photo_a"]: r["id"] for r in g["R0"]}
    for rel in PRIM + ("selfmad_hrnet_w18__rel",):
        cf = AR.contrast_fn(S[rel], D)
        out = {}
        for al in (0.1, 0.2, 0.3, 0.4, 0.5):
            if al < 0.5:
                A3 = [r for r in g["AG3"] if abs(float(r["alpha"]) - al) < 1e-9]
                AT = [r for r in g["AG3T"] if abs(float(r["alpha"]) - al) < 1e-9]
            else:
                A3 = [r for r in g["R4"] if r["pa"] in hosts]
                AT = [r for r in g["R3"] if r["pa"] in hosts]
            a, t = cf(A3, neg), cf(AT, neg)
            out[str(al)] = {"AG3": a["auc"], "AG3T": t["auc"], "diff": a["auc"] - t["auc"],
                            "ci": AR.ci(a["rep"] - t["rep"]),
                            "cos_to_B_AG3": float(np.mean([E[r["id"]] @ E[cam[r["photo_b"]]] for r in A3])),
                            "cos_to_Aprime_AG3T": float(np.mean([E[r["id"]] @ E[cam[r["photo_b"]]] for r in AT]))}
        res["matched_alpha"][rel] = out
    # spread-matched control support
    res["spread"] = {}
    band = lambda r: 5.9 <= r.get("latdist", -1) <= 6.3
    for rel in PRIM + ("selfmad_hrnet_w18__rel",):
        sc = S[rel]
        cf = AR.contrast_fn(sc, D)
        c = cf(g["R2s"], R2s1)
        sp = {k: float(spearmanr([sc[r["id"]] for r in g[k]], [r["latdist"] for r in g[k]])[0])
              for k in ("R2", "R2s", "R3", "R4")}
        bd = cf([r for r in g["R4"] if band(r)], [r for r in g["R2s"] if band(r)])
        res["spread"][rel] = {"R2s>R2": {"auc": c["auc"], "ci": c["ci"]}, "spearman_score_latdist": sp,
                              "band_5.9_6.3_R2s>R4": {"auc": bd["auc"], "ci": bd["ci"], "n": bd["n"]} if bd else None}
    # H-new-1
    pairs = {r["person"]: r for r in csv.DictReader(open("/home/narolski/smad-next/experiments/AG1/pairs.csv"))}
    res["H-new-1"] = {}
    for rel in PRIM:
        sc = S[rel]
        cos = [float(pairs[r["pa"]]["cos_s1p_s2q"]) for r in g["R4"]]
        rho = float(spearmanr([sc[r["id"]] for r in g["R4"]], cos)[0])
        sd = {r["pa"]: shape_dist(P[r["photo_a"]]["kps256"], P[r["photo_b"]]["kps256"]) for r in g["R4"]}
        q = np.quantile(list(sd.values()), [1 / 3, 2 / 3])
        cf = AR.contrast_fn(sc, D)
        tert = {}
        for k in range(3):
            hs = {h for h, v in sd.items() if int(np.searchsorted(q, v)) == k}
            c = cf([r for r in g["R4"] if r["pa"] in hs], [r for r in g["R3"] if r["pa"] in hs])
            tert[str(k)] = {"auc": c["auc"], "ci": c["ci"], "n": c["n"]}
        res["H-new-1"][rel] = {"spearman_R4score_vs_contributor_cos": rho, "R3>R4_by_shape_tertile": tert,
                               "shape_tertile_cuts": q.tolist()}
    v = [abs(x["spearman_R4score_vs_contributor_cos"]) for x in res["H-new-1"].values()]
    res["H-new-1"]["_verdict"] = ("falsified (|Spearman| < 0.1 in all three rows)" if max(v) < 0.1 else
                                  "supported" if all(x["spearman_R4score_vs_contributor_cos"] <= -0.15
                                                     for k, x in res["H-new-1"].items() if not k.startswith("_"))
                                  else "neither")
    # H-new-2
    def gray_mean(ph):
        return float(cv2.imread(str(pathlib.Path("/mnt/t7/smad_next/AG1/inputs/pack") / P[ph]["crop"]),
                                cv2.IMREAD_GRAYSCALE).mean())
    pose = {r["pa"]: shape_dist(P[r["photo_a"]]["kps256"], P[r["photo_b"]]["kps256"]) for r in g["R3"]}
    illum = {r["pa"]: abs(gray_mean(r["photo_a"]) - gray_mean(r["photo_b"])) for r in g["R3"]}
    res["H-new-2"] = {}
    spreads = []
    for rel in PRIM:
        cf = AR.contrast_fn(S[rel], D)
        d = {}
        for name, cov in (("pose", pose), ("illumination", illum)):
            q = np.quantile(list(cov.values()), [1 / 3, 2 / 3])
            tert = {}
            for k in range(3):
                hs = {h for h, v in cov.items() if int(np.searchsorted(q, v)) == k}
                c = cf([r for r in g["R3"] if r["pa"] in hs], [r for r in R2s1 if r["pa"] in hs])
                tert[str(k)] = {"auc": c["auc"], "ci": c["ci"], "n": c["n"]}
            aucs = [tert[str(k)]["auc"] for k in range(3)]
            spreads.append(max(aucs) - min(aucs))
            d[name] = {"R2>R3_by_tertile": tert, "cuts": q.tolist(), "max_minus_min": max(aucs) - min(aucs),
                       "increasing": bool(aucs[0] < aucs[1] < aucs[2])}
        res["H-new-2"][rel] = d
    res["H-new-2"]["_verdict"] = ("falsified (tertile AUCs within 0.05 for both covariates in all rows)"
                                  if max(spreads) < 0.05 else "not falsified (see per-row tertiles)")
    # G-a
    pub = json.load(open("/home/narolski/smad-next/experiments/AG1/published_eer.json"))
    R = json.load(open(OUT / "ag1_read.json"))
    res["G-a"] = {}
    for rel in ("madation_vitb16", "madation_vitl14", "selfmad_hrnet_w18__own", "selfmad_hrnet_w18__rel"):
        for gen in ("mip1", "mip2"):
            ours = R[f"{gen}/frll/{rel}"]["benchmark_eer_pct"]
            ref = pub.get(rel, {}).get(gen)
            res["G-a"][f"{rel}/{gen}"] = {"ours_corrected_mad22": ours, "published": ref,
                                         "verdict": "cannot be evaluated (no published value)" if ref is None else
                                         ("reproduced" if abs(ours - ref) <= 3 else "not reproduced, descriptive")}
    json.dump(res, open(OUT / "posthoc.json", "w"), indent=1, default=float)
    # Athena-only full readings
    athena_hosts = {r["pa"] for r in rows if r["rung"] in ("R2", "R3", "R4") and r["source"] == "ours"
                    and str(r.get("platform", "")).startswith("athena")}
    keep = [r for r in rows if r["source"] != "ours" or (r["gen"] == "mip1" and r["pa"] in athena_hosts
                                                        and r["rung"] not in ("R2s", "AG3", "AG3T"))]
    keep = [r for r in keep if not (r["source"] != "ours" and r["gen"] == "mip2")]
    keep = [r for r in keep if r["rung"] != "R0" or r["db"] == "frll" or r["pa"] in athena_hosts]
    od = OUT.parent / "read_athena_only"
    od.mkdir(exist_ok=True)
    AR.read(keep, S, E, od, B, pub)
    print("POSTHOC done")


if __name__ == "__main__":
    main()
