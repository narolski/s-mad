"""AG5: post hoc ladder read of the existing StyleGAN3 sets (H3 morphs, H3 renders, A37 X4 spread-matched renders)
against FRLL camera photos, for the 12 primary method rows of A41 h3 (one network per result) plus the MixFaceNet-MAD
release as a descriptive row. No new images, no rescoring.
Run: python3 -I src/AG5/ag5_read.py [--smoke]
"""
import csv, hashlib, json, pathlib, re, sys
import numpy as np
from scipy.stats import norm

MC = pathlib.Path("/home/narolski/mambamorph-code")
S = MC / "smadcvpr_runs/A12_scored"
H3 = pathlib.Path("/mnt/t7/smad_heldout/h3_sg3/data/manifests/h3sg3.csv")
SP = pathlib.Path("/mnt/t7/smad_heldout/a37_sg3ctl/data/manifests/a37spread.csv")
X4 = pathlib.Path("/mnt/t7/smad_heldout/a41g/a41g_out/x4")
EVAL = MC / "smadcvpr_data/manifests/eval.csv"
EVAL_SHA = "86d055d349c63a225893ace30cb3db8b1e9aea4e72350d78152126d7a49d56c9"
NETS = MC / "experiments/A36_published-detector-shortcuts/raw/A36_networks.tsv"
OUT = pathlib.Path("/home/narolski/smad-next/experiments/AG5")
B = 10000
SMOKE = "--smoke" in sys.argv

sys.path.insert(0, "/home/narolski/smad-next/src/AD1")
from ad1_read import wauc, dprime, Draw  # noqa: E402


def sha(p):
    return hashlib.sha256(open(p, "rb").read()).hexdigest()


def load(f, ids, key, msha=None):
    z = np.load(f, allow_pickle=False)
    if msha is not None and "manifest_sha256" in z.files:
        assert str(z["manifest_sha256"]) == msha, f
    m = dict(zip(z["id"].tolist(), z[key].astype(np.float64)))
    return np.array([m[i] for i in ids])


def networks():
    """(row label, network name, h3 file, eval file, x4 spread file, key)"""
    out = []
    for ln in open(NETS):
        if ln.startswith("#") or not ln.strip():
            continue
        run, ck, _s, grp, method, arm, seed = ln.rstrip("\n").split("\t")
        if grp != "primary":
            continue
        name = run.rsplit("/", 1)[1]
        suf = "_es" if ck == "es.pt" else ""
        out.append((f"{method} | {arm}", f"{name} ({ck})", S / "A12BR" / name / f"scores_h3sg3{suf}.npz",
                    S / "A12BR" / name / f"scores_eval{suf}.npz", X4 / name / "nets/scores_a37spread.npz", "score"))
    rel = [("SelfMAD release, own preprocessing", "selfmad_hrnet_w18 own", MC / "smadcvpr_runs/A36/selfmad_own/own_h3sg3.npz",
            MC / "experiments/A32-RSX_resolution-shortcut/raw/selfmad_own_eval.npz", X4 / "selfmad_hrnet_w18/own/scores_a37spread.npz", "score"),
           ("MADation official ViT-B/16", "madation_vitb16", S / "A12REL/madation_vitb16/scores_h3sg3.npz",
            S / "A12REL/madation_vitb16/scores_eval.npz", X4 / "madation_vitb16/rel/scores_a37spread.npz", "score_noTTA"),
           ("MADation official ViT-L/14", "madation_vitl14", S / "A12REL/madation_vitl14/scores_h3sg3.npz",
            S / "A12REL/madation_vitl14/scores_eval.npz", X4 / "madation_vitl14/rel/scores_a37spread.npz", "score_noTTA"),
           ("MixFaceNet-MAD release (descriptive, our frames)", "mixfacenet_mad_smdd", S / "A12REL/mixfacenet_mad_smdd/scores_h3sg3.npz",
            S / "A12REL/mixfacenet_mad_smdd/scores_eval.npz",
            pathlib.Path("/mnt/t7/smad_heldout/a46/a41g_out/a46x4/mixfacenet_mad_smdd/rel/scores_a37spread.npz"), None)]
    return out + rel


def main():
    assert sha(EVAL) == EVAL_SHA
    hsha, ssha = sha(H3), sha(SP)
    hr = list(csv.DictReader(open(H3)))
    sr = list(csv.DictReader(open(SP)))
    ev = [r for r in csv.DictReader(open(EVAL)) if r["family"] == "frll_bona" and r["variant"] == "orig"]
    pairs = sorted({int(r["pair"]) for r in hr})
    ppos = {p: i for i, p in enumerate(pairs)}
    persons = sorted({re.match(r"^(\d{3})_", pathlib.PurePath(r["path"]).name).group(1) for r in ev})
    nb = 200 if SMOKE else B
    Wp = np.random.default_rng([20261111, 5, 1]).multinomial(len(pairs), np.full(len(pairs), 1 / len(pairs)), size=nb).astype(float)
    Dp = Draw(persons, nb, [20261111, 5, 2])
    g = {"R4": [r for r in hr if r["family"] == "h3_sg3" and r["variant"] == "orig"],
         "R2": [r for r in hr if r["family"] == "h3_bona" and r["variant"] == "orig"],
         "R2x4": [r for r in sr if r["variant"] == "orig"]}
    W = {k: Wp[:, [ppos[int(r["pair"])] for r in v]] for k, v in g.items()}
    W["R0"] = Dp.w([(re.match(r"^(\d{3})_", pathlib.PurePath(r["path"]).name).group(1),) for r in ev])
    # G-b (recorded potency, before scores): morphs verifying against both contributors at FMR 1e-3
    st = json.load(open("/mnt/t7/smad_heldout/h3_sg3/data/h3sg3_stats.json"))
    gb = {"thr": st["potency"]["glint"]["thr_fmr_1e-3"], "orig_morph_verifies_both": st["potency"]["glint"]["orig"]["morph_verifies_both_fmr_1e-3"]}
    print("G-b", gb, flush=True)
    res, rows_csv = {"G-b": gb, "n": {k: len(v) for k, v in g.items()} | {"R0": len(ev)}, "B": nb, "networks": []}, []
    for lab, net, fh, fe, fx, key in networks():
        if key is None:
            key = "score_noTTA" if "score_noTTA" in np.load(fh).files else "score"
        s = {"R4": load(fh, [r["id"] for r in g["R4"]], key, hsha), "R2": load(fh, [r["id"] for r in g["R2"]], key, hsha),
             "R0": load(fe, [r["id"] for r in ev], key, EVAL_SHA)}
        s["R2x4"] = load(fx, [r["id"] for r in g["R2x4"]], key, ssha) if fx.exists() else None
        if SMOKE:
            s = {k: (None if v is None else v[:8]) for k, v in s.items()}
            Wk = {k: v[:, :8] for k, v in W.items()}
        else:
            Wk = W
        o = {}
        for nm, (a, b) in {"bench R4 vs R0": ("R4", "R0"), "R0->R2 (renders vs camera)": ("R2", "R0"),
                           "main R2 vs R4 (morphs vs renders)": ("R4", "R2"), "R0->R2x4 (X4 renders vs camera)": ("R2x4", "R0"),
                           "main X4: R2x4 vs R4": ("R4", "R2x4")}.items():
            if s[a] is None or s[b] is None:
                o[nm] = None
                continue
            pt = float(wauc(s[a], s[b], np.ones((1, len(s[a]))), np.ones((1, len(s[b]))))[0])
            rep = wauc(s[a], s[b], Wk[a], Wk[b])
            fold = 0.5 + np.abs(rep - 0.5)
            o[nm] = {"auc": pt, "ci95": [float(np.percentile(rep, 2.5)), float(np.percentile(rep, 97.5))], "fold": 0.5 + abs(pt - 0.5),
                     "fold_ub95": float(np.percentile(fold, 97.5)), "dprime": dprime(pt), "_rep": rep}
        db = np.sqrt(2) * norm.ppf(np.clip(o["bench R4 vs R0"]["_rep"], 0.005, 0.995))
        verdicts, shares = {}, {}
        for r2, mainnm, stepnm in (("R2", "main R2 vs R4 (morphs vs renders)", "R0->R2 (renders vs camera)"),
                                   ("R2x4", "main X4: R2x4 vs R4", "R0->R2x4 (X4 renders vs camera)")):
            if o[mainnm] is None:
                verdicts[r2] = "not available"
                continue
            dr = np.sqrt(2) * norm.ppf(np.clip(o[stepnm]["_rep"], 0.005, 0.995))
            ok = db > 0
            sh = {"point": dprime(o[stepnm]["auc"]) / dprime(o["bench R4 vs R0"]["auc"]) if dprime(o["bench R4 vs R0"]["auc"]) > 0 else None,
                  "ci95": [float(np.percentile(dr[ok] / db[ok], 2.5)), float(np.percentile(dr[ok] / db[ok], 97.5))] if ok.mean() > 0.5 else None}
            shares[r2] = sh
            m = o[mainnm]
            if m["auc"] >= 0.75 and m["ci95"][0] > 0.65 and sh["point"] is not None and sh["point"] <= 0.2:
                v = "reads morphing"
            elif (sh["ci95"] is not None and sh["ci95"][0] >= 0.5) or (m["fold"] < 0.60 and m["fold_ub95"] < 0.65):
                v = "reads the benchmark"
            else:
                v = "mixed"
            if o["bench R4 vs R0"]["auc"] <= 0.5:
                v += " (benchmark-cell separation not positive: shares undefined)"
            verdicts[r2] = v
        res["networks"].append({"row": lab, "network": net, "key": key, "contrasts": {k: (None if v is None else {kk: vv for kk, vv in v.items() if kk != "_rep"}) for k, v in o.items()},
                                "shares_R0_to_R2": shares, "verdict_main_H3renders": verdicts["R2"], "verdict_main_X4": verdicts["R2x4"]})
        rows_csv.append([lab, net] + [("" if o[k] is None else f"{o[k]['auc']:.3f} [{o[k]['ci95'][0]:.3f}, {o[k]['ci95'][1]:.3f}]") for k in o] +
                        [("" if shares.get(k) is None or shares[k]["point"] is None else f"{shares[k]['point']:.2f} [{shares[k]['ci95'][0]:.2f}, {shares[k]['ci95'][1]:.2f}]" if shares[k]["ci95"] else f"{shares[k]['point']:.2f}") for k in ("R2", "R2x4")] +
                        [verdicts["R2"], verdicts["R2x4"]])
        print(lab, net, verdicts, {k: (None if v is None else round(v["auc"], 3)) for k, v in o.items()}, flush=True)
    if SMOKE:
        print("smoke ok")
        return
    json.dump(res, open(OUT / "ag5_ladder.json", "w"), indent=1)
    with open(OUT / "ag5_ladder.csv", "w", newline="") as fh:
        w = csv.writer(fh)
        w.writerow(["row", "network", "bench R4 vs R0", "R0->R2 renders vs camera", "main R2 vs R4", "R0->R2x4", "main X4 R2x4 vs R4",
                    "share R0->R2", "share R0->R2x4", "verdict (H3 renders)", "verdict (X4)"])
        w.writerows(rows_csv)


if __name__ == "__main__":
    main()
