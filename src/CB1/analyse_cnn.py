"""CB1: checks and readings for the CNN re-score (prereg sections 5-6).
  python3 -I analyse_cnn.py --images IMAGES.csv --scores SCORE_DIR --stored WCSS_COPY --nets NETS.tsv[,NETS2.tsv]
                            --out OUT_DIR [--gate-only]
Primary score: logit_noTTA. C1: per-family EER on the gate (old MAD22 subset) and FRLL-Morphs rows against the stored
WCSS scores of the same checkpoint (scores_eval_<ckpt>.npz, both score versions), and row-wise differences.
C2: old-aligner vs CPU-backend frame of the same 204 FRLL photos. Readings: EER and BPCER at APCER 1/5/10/20% per
family, native and E7 genuine pool, two-way person bootstrap (B 2000, seed 0) for every network and for arm seed means;
reproduction rule of prereg section 5.
"""
import argparse
import csv
import json
import math
import pathlib
import re
from collections import defaultdict

import numpy as np

FAM = {"mad22c": ["FaceMorpher", "OpenCV", "Webmorph", "MIPGAN_I", "MIPGAN_II"],
       "frllm": ["amsl", "facemorpher", "opencv", "stylegan", "webmorph"]}
GATEFAM = ["FaceMorpher", "OpenCV", "Webmorph", "MIPGAN_I", "MIPGAN_II"]
PUB = {  # prereg section 5; order as FAM
    "Inception-MAD": {"frllm": [10.79, 3.17, 5.38, 11.37, 9.86], "mad22c": [0.00, 7.52, 18.00, 10.90, 16.22]},
    "MorphHRNet": {"frllm": None, "mad22c": [5.90, 5.69, 9.80, 15.30, 10.41]},
    "PW-MAD": {"frllm": [15.18, 2.20, 2.42, 16.64, 16.65], "mad22c": None},
    "OrthoMAD": {"frllm": [9.50, 0.98, 0.73, 6.54, 15.23], "mad22c": None},
    "OrthoMAD (IDistill Table I AMSL 14.80)": {"frllm": [14.80, 0.98, 0.73, 6.54, 15.23], "mad22c": None},
    "MixFaceNet-MAD": {"frllm": [15.18, 3.87, 4.39, 8.99, 12.35], "mad22c": [4.60, 8.33, 18.20, 16.70, 20.62]},
    "SelfMAD": {"frllm": None, "mad22c": None},          # M4 is descriptive only (prereg section 3; review F6)
    "FD-MAD": {"frllm": [0.00, 0.00, 0.00, 9.25, 0.00], "mad22c": [0.00, 2.54, 18.40, 2.45, 7.21]},
    "IDistill": {"frllm": [4.00, 2.05, 2.46, 1.96, 4.01], "mad22c": None},
}
ARMS = {  # arm -> (method, primary checkpoint, label)
    "A12BR_M1": ("Inception-MAD", "es", "M1: Inception-v3 scratch 299, our pipeline (A12-BR R x d0)"),
    "A12BR_M2": ("MorphHRNet", "es", "M2: HRNet-W48 scratch 256, our pipeline (A12-BR R x d0)"),
    "A12BR_M5": ("PW-MAD", "es", "M5: DenseNet-121 + pixel map 224, our pipeline (A12-BR R x d0)"),
    "A12BR_M6": ("OrthoMAD", "es", "M6: ResNet-18 + orthogonal heads 224, our pipeline (A12-BR R x d0)"),
    "A12BR_M8": ("MixFaceNet-MAD", "es", "M8: MixFaceNet-S 224, our pipeline, ImageNet input (A12-BR R x d0)"),
    "A12BR_M8O": ("MixFaceNet-MAD", "es", "M8O: MixFaceNet-S by the official SMDD procedure re-implemented (A12-BR O x d0)"),
    "A12BR_M4": ("SelfMAD", "es", "M4: SelfMAD-style HRNet-W18 IN-1k 384 (A12-BR R x d0b; descriptive)"),
    "A45_incepofc": ("Inception-MAD", "last", "A45 incep_ofc: Inception-v3 by the official SMDD procedure, 224"),
    "A45_hrnetw18": ("MorphHRNet", "last", "A45 hrnet_w18: MorphHRNet recipe at W18, 256, Adam 1e-3"),
    "FDMAD_g256": ("FD-MAD", "model", "FD-MAD re-implementation, global branch only, features at 256 (A45 primary)"),
    "FDMAD_g512": ("FD-MAD", "model", "FD-MAD re-implementation, global branch only, features at 512 (disclosed variant)"),
    "FDMAD_f256": ("FD-MAD", "model", "FD-MAD re-implementation, fused 0.6 global + 0.4 local MRF, 256"),
    "FDMAD_f512": ("FD-MAD", "model", "FD-MAD re-implementation, fused 0.6 global + 0.4 local MRF, 512 (windows 96 px as built)"),
}
APC = (0.01, 0.05, 0.10, 0.20)
C1_EXTERNAL_PASS = set()   # nets whose C1 was checked by a separate script (FD-MAD: fdmad_gate.py), filled from --c1-pass
B = 2000


def w_eer(s, y, w=None):
    """weighted EER (morph = 1 positive, higher = more morph); w None = unweighted. s, y numpy 1-D."""
    o = np.argsort(-s, kind="stable")
    y = y[o]
    w = np.ones_like(s, float) if w is None else w[o]
    P, N = (w * (y == 1)).sum(), (w * (y == 0)).sum()
    fnr = 1 - np.cumsum(w * (y == 1)) / max(P, 1e-12)
    fpr = np.cumsum(w * (y == 0)) / max(N, 1e-12)
    i = int(np.argmin(np.abs(fnr - fpr)))
    return float((fnr[i] + fpr[i]) / 2)


def eer_matrix(s, y, W):
    """EER for each weight row of W (R x n), vectorised."""
    o = np.argsort(-s, kind="stable")
    y, W = y[o], W[:, o]
    pos = W * (y == 1)
    neg = W * (y == 0)
    P = pos.sum(1, keepdims=True)
    N = neg.sum(1, keepdims=True)
    fnr = 1 - np.cumsum(pos, 1) / np.maximum(P, 1e-12)
    fpr = np.cumsum(neg, 1) / np.maximum(N, 1e-12)
    i = np.argmin(np.abs(fnr - fpr), 1)
    r = np.arange(W.shape[0])
    return (fnr[r, i] + fpr[r, i]) / 2


def bpcer_at(s, y, a):
    m = np.sort(s[y == 1])
    g = s[y == 0]
    k = int(math.floor(a * len(m)))
    thr = m[min(k, len(m) - 1)]
    return float((g >= thr).mean())


def load_images(p):
    rows = list(csv.DictReader(open(p)))
    return rows


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--images", required=True)
    ap.add_argument("--scores", required=True)
    ap.add_argument("--stored", required=True)
    ap.add_argument("--nets", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--gate-only", action="store_true")
    ap.add_argument("--c1-pass", default="", help="file listing net ids that passed an external C1")
    a = ap.parse_args()
    if a.c1_pass:
        C1_EXTERNAL_PASS.update(l.strip() for l in open(a.c1_pass) if l.strip())
    out = pathlib.Path(a.out)
    out.mkdir(parents=True, exist_ok=True)
    rows = load_images(a.images)
    ids = np.array([r["id"] for r in rows])
    nets = []
    for f in a.nets.split(","):
        nets += list(csv.DictReader(open(f), delimiter="\t"))
    persons = sorted({r["person_a"] for r in rows if r["bench"] in ("mad22c", "frllm")} |
                     {r["person_b"] for r in rows if r["bench"] in ("mad22c", "frllm")})
    pidx = {p: i for i, p in enumerate(persons)}
    rng = np.random.default_rng(0)
    C = rng.multinomial(len(persons), [1 / len(persons)] * len(persons), size=B).astype(float)   # B x persons

    # cells: (bench, family, pool) -> index arrays (genuine, morph)
    idx = defaultdict(list)
    for i, r in enumerate(rows):
        idx[(r["bench"], r["pool"], r["family"], int(r["label"]))].append(i)
    idx = {k: np.array(v) for k, v in idx.items()}

    def cell(bench, fam, pool):
        g = idx[(bench, "native", "bona", 0)] if pool == "native" else idx[(bench, "e7", fam, 0)]
        m = idx[(bench, "native", fam, 1)]
        return g, m

    gate, results, c2 = [], [], []
    boot = {}                                           # (net, bench, fam, pool) -> B EERs
    for n in nets:
        f = pathlib.Path(a.scores) / f"{n['net_id']}.npz"
        if not f.exists():
            print("missing", f)
            continue
        z = np.load(f)
        assert np.array_equal(z["id"], ids)
        S = {"logit": z["logit_noTTA"].astype(float), "noTTA": z["score_noTTA"].astype(float),
             "TTA": z["score"].astype(float)}
        # ---- C1 gate
        run = pathlib.Path(n["ckpt"]).parent.name
        exp = "A45" if n["net_id"].startswith("A45") else "A12BR"
        ck = n["net_id"].rsplit("_", 1)[1]
        st = pathlib.Path(a.stored) / exp / run / f"scores_eval_{ck}.npz"
        if st.exists():
            sz = np.load(st)
            spos = {e: i for i, e in enumerate(sz["id"])}
            for bench in ("gate", "frllm"):
                fams = GATEFAM if bench == "gate" else FAM["frllm"]
                for fam in fams:
                    g, m = cell(bench, fam, "native")
                    sel = np.concatenate([g, m])
                    eids = [ids[i].split("/", 2)[2] for i in sel]
                    si = np.array([spos[e] for e in eids])
                    y = np.r_[np.zeros(len(g)), np.ones(len(m))]
                    rec = dict(net=n["net_id"], bench=bench, family=fam, n_gen=len(g), n_morph=len(m))
                    for ver, key in (("noTTA", "score_noTTA"), ("TTA", "score")):
                        mine, stored = S[ver][sel], sz[key][si].astype(float)
                        rec[f"eer_mine_{ver}"] = 100 * w_eer(mine, y)
                        rec[f"eer_stored_{ver}"] = 100 * w_eer(stored, y)
                        rec[f"maxabs_{ver}"] = float(np.abs(mine - stored).max())
                        rec[f"medabs_{ver}"] = float(np.median(np.abs(mine - stored)))
                    gate.append(rec)
        # ---- C2 pipeline shift on the 204 FRLL photos
        go = {re.sub(r"_orig$", "", pathlib.Path(rows[i]["path"]).stem): i for i in idx[("frllm", "native", "bona", 0)]}
        gn = {pathlib.Path(rows[i]["path"]).stem: i for i in idx[("mad22c", "native", "bona", 0)]}
        common = sorted(set(go) & set(gn))
        lo, ln = S["logit"][[go[k] for k in common]], S["logit"][[gn[k] for k in common]]
        from scipy.stats import kendalltau
        c2.append(dict(net=n["net_id"], n=len(common), median_abs_logit_diff=float(np.median(np.abs(lo - ln))),
                       mean_diff_new_minus_old=float(np.mean(ln - lo)), kendall=float(kendalltau(lo, ln)[0])))
        if a.gate_only:
            continue
        # ---- readings
        for bench in ("mad22c", "frllm"):
            for fam in FAM[bench]:
                for pool in ("native", "e7"):
                    g, m = cell(bench, fam, pool)
                    s = np.r_[S["logit"][g], S["logit"][m]]
                    y = np.r_[np.zeros(len(g)), np.ones(len(m))]
                    pa = np.array([pidx[rows[i]["person_a"]] for i in np.r_[g, m]])
                    pb = np.array([pidx[rows[i]["person_b"]] for i in np.r_[g, m]])
                    W = np.where(y[None, :] == 1, C[:, pa] * C[:, pb], C[:, pa])
                    be = 100 * eer_matrix(s, y, W)
                    boot[(n["net_id"], bench, fam, pool)] = be
                    rec = dict(net=n["net_id"], bench=bench, family=fam, pool=pool, n_gen=len(g), n_morph=len(m),
                               eer=100 * w_eer(s, y), eer_lo=float(np.percentile(be, 2.5)),
                               eer_hi=float(np.percentile(be, 97.5)))
                    for ap_ in APC:
                        rec[f"bpcer_at_apcer{int(ap_ * 100)}"] = 100 * bpcer_at(s, y, ap_)
                    results.append(rec)
    # C1 (amendment 1, review F5): row-wise, on the score version chosen on M1 seed 1 (the one with the smaller median
    # difference there): median |dp| <= 1e-3 and max |dp| <= 1e-2 over every gate and FRLL-Morphs row; secondary: EER
    # within 0.5 points in at least 9 of 10 cells. A network without stored scores or failing C1 gets no reading.
    c1 = {}
    ref = [g for g in gate if g["net"].startswith(("A12BR_M1_s1_es", "A45_incepofc_s1_last"))]
    ver = "noTTA" if not ref or np.mean([g["medabs_noTTA"] for g in ref]) <= np.mean([g["medabs_TTA"] for g in ref]) else "TTA"
    for netid in sorted({g["net"] for g in gate}):
        gg = [g for g in gate if g["net"] == netid]
        med = float(np.median([g[f"medabs_{ver}"] for g in gg]))
        mx = float(max(g[f"maxabs_{ver}"] for g in gg))
        eer_ok = sum(abs(g[f"eer_mine_{ver}"] - g[f"eer_stored_{ver}"]) <= 0.5 for g in gg)
        c1[netid] = dict(net=netid, version=ver, cells=len(gg), median_cell_medabs=med, max_abs=mx,
                         eer_cells_within_0p5=eer_ok, passed=bool(med <= 1e-3 and mx <= 1e-2 and eer_ok >= 0.9 * len(gg)))
    json.dump(c1, open(out / "c1_verdicts.json", "w"), indent=1)
    if gate:
        with open(out / "c1_gate.csv", "w", newline="") as fh:
            w = csv.DictWriter(fh, fieldnames=list(gate[0]))
            w.writeheader()
            w.writerows(gate)
    with open(out / "c2_pipeline_shift.csv", "w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=list(c2[0]))
        w.writeheader()
        w.writerows(c2)
    if a.gate_only:
        return
    with open(out / "per_network.csv", "w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=list(results[0]))
        w.writeheader()
        w.writerows(results)
    # ---- arms
    R = {(r["net"], r["bench"], r["family"], r["pool"]): r for r in results}
    netids = sorted({r["net"] for r in results})
    arm_rows, verdicts = [], []
    for arm, (method, ck_primary, label) in ARMS.items():
        for ck in ("es", "last", "model"):
            members = [x for x in netids if re.fullmatch(rf"{arm}_s\d+_{ck}", x)]
            if not members:
                continue
            failed = [x for x in members if not (c1.get(x, {}).get("passed") or x in C1_EXTERNAL_PASS)]
            if failed:   # amendment 2: the arm is read on the networks that pass C1 when at least 3 do (count printed)
                arm_rows.append(dict(arm=arm, method=method, ckpt=ck, family="C1_EXCLUDED",
                                     reading=f"C1 missing or failed for {failed}"))
                members = [x for x in members if x not in failed]
                if len(members) < 3:
                    arm_rows.append(dict(arm=arm, method=method, ckpt=ck, family="WITHHELD",
                                         reading=f"no reading: fewer than 3 networks pass C1"))
                    continue
            for bench in ("mad22c", "frllm"):
                for pool in ("native", "e7"):
                    fam_means = []
                    for fam in FAM[bench]:
                        v = np.array([R[(x, bench, fam, pool)]["eer"] for x in members])
                        bb = np.mean([boot[(x, bench, fam, pool)] for x in members], 0)
                        rec = dict(arm=arm, method=method, ckpt=ck, primary=ck == ck_primary, bench=bench, pool=pool,
                                   family=fam, n_seeds=len(members), eer_mean=float(v.mean()), eer_sd=float(v.std(ddof=1)) if len(v) > 1 else 0.0,
                                   eer_boot_lo=float(np.percentile(bb, 2.5)), eer_boot_hi=float(np.percentile(bb, 97.5)))
                        for ap_ in APC:
                            k = f"bpcer_at_apcer{int(ap_ * 100)}"
                            rec[k] = float(np.mean([R[(x, bench, fam, pool)][k] for x in members]))
                        pub = PUB[method][bench]
                        if pub is not None:
                            p = pub[FAM[bench].index(fam)]
                            rec["published"] = p
                            rec["family_window"] = "within" if abs(rec["eer_mean"] - p) <= max(1.5, 0.25 * p) else "outside"
                        arm_rows.append(rec)
                        fam_means.append(v)
                    per_seed = np.mean(fam_means, 0)              # five-family mean per seed
                    bbm = np.mean([np.mean([boot[(x, bench, fam, pool)] for fam in FAM[bench]], 0) for x in members], 0)
                    mrec = dict(arm=arm, method=method, ckpt=ck, primary=ck == ck_primary, bench=bench, pool=pool,
                                family="MEAN5", n_seeds=len(members), eer_mean=float(per_seed.mean()),
                                eer_sd=float(per_seed.std(ddof=1)) if len(per_seed) > 1 else 0.0,
                                eer_boot_lo=float(np.percentile(bbm, 2.5)), eer_boot_hi=float(np.percentile(bbm, 97.5)))
                    pub = PUB[method][bench]
                    if pub is not None and pool == "native":
                        pm = float(np.mean(pub))
                        M = max(0.30 * pm, 1.5)
                        d = per_seed - pm
                        from scipy.stats import t as tdist
                        n_ = len(d)
                        half = tdist.ppf(0.95, n_ - 1) * d.std(ddof=1) / math.sqrt(n_) if n_ > 1 else float("nan")
                        lo, hi = d.mean() - half, d.mean() + half
                        if lo > -M and hi < M:
                            v_ = "reproduces the published number on the corrected set" if bench == "mad22c" else "reproduces the published number"
                        elif lo > M:
                            v_ = "does not reproduce (worse)"
                        elif hi < -M:
                            v_ = "does not reproduce (better)"
                        else:
                            v_ = "inconclusive"
                        mrec.update(published=round(pm, 2), delta=float(d.mean()), delta90_lo=float(lo), delta90_hi=float(hi),
                                    margin=M, reading=v_)
                        verdicts.append(mrec)
                    arm_rows.append(mrec)
    keys = []
    for r in arm_rows:
        for k in r:
            if k not in keys:
                keys.append(k)
    with open(out / "per_arm.csv", "w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=keys)
        w.writeheader()
        w.writerows(arm_rows)
    json.dump(verdicts, open(out / "readings.json", "w"), indent=1)
    for v in verdicts:
        print(v["arm"], v["ckpt"], "primary" if v["primary"] else "secondary", v["bench"], f"{v['eer_mean']:.2f}",
              "pub", v["published"], f"delta {v['delta']:+.2f} [{v['delta90_lo']:+.2f}, {v['delta90_hi']:+.2f}] M {v['margin']:.2f}",
              v["reading"])


if __name__ == "__main__":
    main()
