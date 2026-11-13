"""PR1 GD0 / GD1 / GD2 reader (prereg.md sections 6, 6a, "GD rows fixed"). Zero GPU; reads the pn1fs result tar
once. Development data only.
  python -I gd_read.py --tar /mnt/t7/smad_next/PR1/results/PR1_GD_pn1fs.tar --out gd_read.json
  python -I gd_read.py --mock --out gd_read_mock.json     (random logits over the true GD ids; baseline check on lcomb)"""
import argparse
import csv
import hashlib
import io
import json
import pathlib
import sys
import tarfile

import numpy as np

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from pr1_read import auc, share, sha  # noqa: E402

PR1 = pathlib.Path("/mnt/t7/smad_next/PR1")
GDMAN = PR1 / "pr1_gd_tree" / "pr1g" / "data" / "manifests" / "pr1_gd.csv"
GDMAN_SHA = "3577a91351131b104457424054c29ca3c6f3fc59666e9204598e45e608e15157"
SPLIT = pathlib.Path("/home/narolski/smad-next/experiments/PN1_protocol-network-first-tests/split")
AR1L = pathlib.Path("/mnt/t7/smad_next/AF0/lists/ar1.csv")
SPLL = pathlib.Path("/mnt/t7/smad_next/PN1/lists/splice_nat.csv")
CUE_LAD = pathlib.Path("/mnt/t7/smad_next/AF0/cues/ar1.npz")
CUE_SPL = pathlib.Path("/mnt/t7/smad_next/PN1/cues/splice_nat.npz")
CUE_LC = pathlib.Path("/mnt/t7/smad_next/PN1/cues/a14_lcomb.npz")
LC_MAN = pathlib.Path("/mnt/t7/smad_next/PN1/a14_tree/pn14/data/manifests/pn1_a14.csv")
CUE_GD0 = PR1 / "cues" / "gd0.npz"
FS = pathlib.Path("/mnt/t7/smad_next/PN1/results_fs")
ARMS, SEEDS = ("A", "B", "Sb"), (403, 404, 405, 406, 407)
B = 2000


def cues(f):
    z = np.load(f)
    return {str(i): c for i, c in zip(z["ids"], z["cues"])}, [str(n) for n in z["names"]]


def baseline_models():
    """PN1 amendment 15 baselines rebuilt without pn1lib.catalog (which opens benchmark lists); counts and the
    landmark_combined AUC are asserted equal to tier1_a14/baseline27.json before use."""
    from sklearn.linear_model import LogisticRegression
    from sklearn.pipeline import make_pipeline
    from sklearn.preprocessing import StandardScaler
    lad = {r["pid"]: r for r in csv.DictReader(open(SPLIT / "ladder_split.csv"))}

    def tr(p):
        return p in lad and lad[p]["role"] == "train" and lad[p]["is_val"] == "0"
    L, nl = cues(CUE_LAD)
    S, ns = cues(CUE_SPL)
    assert nl == ns
    ar1 = [r for r in csv.DictReader(open(AR1L)) if r["cell"] == "frgcferet"]
    pos_b = [r["id"] for r in ar1 if r["rung"] == "R4" and r["tool"] == "opencv" and tr(r["p1"]) and tr(lad[r["p1"]]["partner_B"])]
    neg_b = [r["id"] for r in ar1 if r["rung"] in ("R0", "R2w") and r["tool"] in ("opencv", "none") and tr(r["p1"])]
    sp = list(csv.DictReader(open(SPLL)))
    pos_s = [r["id"] for r in sp if r["rung"] == "S4" and r["tool"] == "opencv" and tr(r["p1"]) and lad[r["p1"]]["train_morph"] == "1"
             and all(lad.get(p, {}).get("is_val", "0") == "0" for p in (r["p1"], r["p2"]))]
    neg_s = [r["id"] for r in sp if r["rung"] in ("S0", "S3") and r["tool"] == "opencv" and tr(r["p1"])]
    M = {}
    for name, P, N in (("b_lad", [L[i] for i in pos_b if i in L], [L[i] for i in neg_b if i in L]),
                       ("s_lad", [L[i] for i in pos_b if i in L] + [S[i] for i in pos_s if i in S],
                        [L[i] for i in neg_b if i in L] + [S[i] for i in neg_s if i in S])):
        X = np.r_[np.array(P), np.array(N)]
        y = np.r_[np.ones(len(P)), np.zeros(len(N))]
        M[name] = (make_pipeline(StandardScaler(), LogisticRegression(C=1.0, max_iter=2000, class_weight="balanced")).fit(X, y),
                   len(P), len(N))
    ref = json.load(open("/home/narolski/smad-next/experiments/PN1_protocol-network-first-tests/tier1_a14/baseline27.json"))
    lc, nc = cues(CUE_LC)
    assert nc == nl
    man = list(csv.DictReader(open(LC_MAN)))
    lm = np.array([lc[r["id"]] for r in man if r["fam"] == "ffhq_lcomb" and r["rung"] == "landmark_combined_orig"])
    lg = np.array([lc[r["id"]] for r in man if r["fam"] == "ffhq_lcomb" and r["rung"] == "landmark_combined_resmatch"])
    chk = {}
    for name, (m, npos, nneg) in M.items():
        a = auc(m.decision_function(lm), m.decision_function(lg))
        chk[name] = dict(n_pos=npos, n_neg=nneg, lcomb_auc=a, ref=ref[name]["auc"])
        assert npos == ref[name]["n_train_pos"] and nneg == ref[name]["n_train_neg"], chk
        assert abs(a - ref[name]["auc"]) < 1e-6, chk
    return M, nl, chk


def boot_unit(pos, neg, upos, uneg, seed):
    """AUC interval resampling units (hosts / persons) with replacement, same draw for both classes"""
    rng = np.random.default_rng(seed)
    units = sorted(set(upos) | set(uneg))
    ip = {u: [] for u in units}
    ineg = {u: [] for u in units}
    for k, u in enumerate(upos):
        ip[u].append(k)
    for k, u in enumerate(uneg):
        ineg[u].append(k)
    pos, neg = np.asarray(pos), np.asarray(neg)
    v = []
    for _ in range(B):
        d = rng.choice(units, len(units))
        a = [i for u in d for i in ip[u]]
        b = [i for u in d for i in ineg[u]]
        if a and b:
            v.append(auc(pos[a], neg[b]))
    return [float(np.percentile(v, 2.5)), float(np.percentile(v, 97.5))]


def boot_img(p, n, seed):
    rng = np.random.default_rng(seed)
    p, n = np.asarray(p), np.asarray(n)
    v = [auc(p[rng.integers(0, len(p), len(p))], n[rng.integers(0, len(n), len(n))]) for _ in range(B)]
    return [float(np.percentile(v, 2.5)), float(np.percentile(v, 97.5))]


def cnt(vals, cond):
    return int(sum(1 for v in vals if v is not None and cond(v)))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--tar")
    ap.add_argument("--out", required=True)
    ap.add_argument("--mock", action="store_true")
    a = ap.parse_args()
    assert sha(GDMAN) == GDMAN_SHA
    man = list(csv.DictReader(open(GDMAN)))
    by = {r["id"]: r for r in man}
    M, names, chk = baseline_models()
    out = dict(mock=a.mock, baseline_check=chk, per_net={})
    scores, gate = {}, {}
    if a.mock:
        for arm in ARMS:
            for s in SEEDS:
                rng = np.random.default_rng(s)
                scores[f"PN1_{arm}_s{s}"] = {r["id"]: float(rng.normal(-1, 2) + (1.0 if r["label"] == "1" else 0)) for r in man}
                gate[f"PN1_{arm}_s{s}"] = dict(ok=True)
    else:
        t = pathlib.Path(a.tar)
        want = pathlib.Path(str(t) + ".sha256").read_text().split()[0]
        assert sha(t) == want
        out["tar_sha256"] = want
        with tarfile.open(t) as tf:
            g = json.loads(tf.extractfile("PR1_GD_pn1fs/gate_gd.json").read())
            assert not g.get("test"), "test-mode gate"
            assert hashlib.sha256(tf.extractfile("PR1_GD_pn1fs/pr1_gd.csv").read()).hexdigest() == GDMAN_SHA
            gate = g["nets"]
            for n in gate:
                d = {}
                for fam in ("gd0", "gd1", "gd2"):
                    z = np.load(io.BytesIO(tf.extractfile(f"PR1_GD_pn1fs/scores/{n}__{fam}.npz").read()))
                    d.update(dict(zip(z["id"].tolist(), z["logit"].astype(float).tolist())))
                scores[n] = d
        out["gate"] = gate
    # stored native FFHQ bona scores (FS1, printed beside GD0)
    def bona_native(arm, s):
        if a.mock:
            return None
        n = f"PN1_{arm}_s{s}"
        with tarfile.open(FS / f"{n}.tar") as tf:
            z = np.load(io.BytesIO(tf.extractfile(f"{n}/scores_eval.npz").read()))
        fsman = {r["id"]: r for r in csv.DictReader(open("/mnt/t7/smad_next/PN1/fs_tree/pn1/data/manifests/pn1_eval.csv"))}
        return np.array([lg for i, lg in zip(z["id"].tolist(), z["logit"].tolist()) if fsman[i]["rung"] == "ffhq_bona_orig"])
    G0 = ("stylegan_wplus", "stylegan_w", "diffae")

    def r0_native(arm, s):                # F8: G's flags printed beside the stored test R0 native flags
        if a.mock:
            return None
        n = f"PN1_{arm}_s{s}"
        with tarfile.open(FS / f"{n}.tar") as tf:
            z = np.load(io.BytesIO(tf.extractfile(f"{n}/scores_eval.npz").read()))
        fsman = {r["id"]: r for r in csv.DictReader(open("/mnt/t7/smad_next/PN1/fs_tree/pn1/data/manifests/pn1_eval.csv"))}
        x = [lg for i, lg in zip(z["id"].tolist(), z["logit"].tolist()) if fsman[i]["fam"] == "ladder"
             and fsman[i]["role"] == "test" and fsman[i]["rung"] == "R0" and fsman[i]["strength"] == ""]
        assert len(x) == 191
        return share(x)
    ids = lambda **kw: [r["id"] for r in man if all(r[k] == v for k, v in kw.items())]   # noqa: E731
    # cue baselines on GD0 (once)
    base = {}
    if CUE_GD0.exists():
        cg, ng = cues(CUE_GD0)
        assert ng == names
        for f in G0:
            pi, ni = ids(fam="gd0", rung=f"{f}_orig"), ids(fam="gd0", rung=f"{f}_resmatch")
            assert all(i in cg for i in pi + ni), "missing GD0 cues"
            P, N = np.array([cg[i] for i in pi]), np.array([cg[i] for i in ni])
            row = {k: auc(m.decision_function(P), m.decision_function(N)) for k, (m, _, _) in M.items()}
            single = [max(auc(P[:, j], N[:, j]), 1 - auc(P[:, j], N[:, j])) for j in range(P.shape[1])]
            row["best_single"] = float(max(single))
            row["best_single_name"] = names[int(np.argmax(single))]
            base[f] = row
    out["gd0_baselines"] = base
    for n, sc in scores.items():
        arm, s = n.split("_")[1], int(n.split("_s")[1])
        ok = gate.get(n, {}).get("ok", False)
        finite = all(np.isfinite(x) for x in sc.values())          # F14: non-finite GD logits -> part not read
        R = dict(gate_ok=ok, finite=bool(finite), gate=gate.get(n))
        ok = ok and finite
        if not ok:
            out["per_net"][f"{arm}_s{s}"] = R
            continue
        v = lambda L: np.array([sc[i] for i in L])   # noqa: E731
        bn = bona_native(arm, s)
        gd0 = {}
        for f in G0:
            pi, ni = ids(fam="gd0", rung=f"{f}_orig"), ids(fam="gd0", rung=f"{f}_resmatch")
            p, q = v(pi), v(ni)
            gd0[f] = dict(auc=auc(p, q), ci=boot_img(p, q, 20261143), miss_own=share(p, gt=False), gen_flag_own=share(q),
                          auc_vs_bona_native=(auc(p, bn) if bn is not None else None),
                          minus_s_lad=(auc(p, q) - base[f]["s_lad"]) if f in base else None)
        R["gd0"] = gd0
        rung = lambda fam, rg: [i for i in ids(fam=fam, rung=rg)]   # noqa: E731
        h = lambda L: [by[i]["host"] for i in L]                    # noqa: E731
        gd1 = {}
        for x, y in (("X", "REC"), ("REC", "G"), ("SAME", "REC"), ("X", "SAME"), ("MIR", "REC")):
            P, N = rung("gd1", x), rung("gd1", y)
            gd1[f"{x}_vs_{y}"] = dict(auc=auc(v(P), v(N)), ci=boot_unit(v(P), v(N), h(P), h(N), 20261144))
        gd1["flags_own_frame_confounded"] = {rg: share(v(rung("gd1", rg))) for rg in ("G", "REC", "MIR", "SAME", "X")}
        gd1["test_R0_native_flag_own_stored"] = r0_native(arm, s)
        R["gd1"] = gd1
        gd2 = {}
        for x, y in (("R4", "R2"), ("R4", "R3"), ("R2", "R0"), ("R2s", "R0"), ("R4", "R2s"), ("R3", "R0"), ("R3m", "R0"), ("R4", "R0")):
            P, N = rung("gd2", x), rung("gd2", y)
            gd2[f"{x}_vs_{y}"] = dict(auc=auc(v(P), v(N)), ci=boot_unit(v(P), v(N), h(P), h(N), 20261145))
        gd2["flags_own"] = {rg: share(v(rung("gd2", rg))) for rg in ("R0", "R2", "R2s", "R3", "R3m", "R4")}
        gd2["n"] = {rg: len(rung("gd2", rg)) for rg in ("R0", "R2", "R2s", "R3", "R3m", "R4")}
        R["gd2"] = gd2
        out["per_net"][f"{arm}_s{s}"] = R
    pn = out["per_net"]
    get = lambda arm, f: [f(pn[f"{arm}_s{s}"]) if pn.get(f"{arm}_s{s}", {}).get("gate_ok") else None for s in SEEDS]  # noqa: E731
    V = {}
    for arm in ARMS:
        fv = {}
        for f in ("stylegan_wplus", "stylegan_w"):
            x = get(arm, lambda r, f=f: r["gd0"][f]["auc"])
            ver = "transfers" if cnt(x, lambda z: z >= 0.80) >= 4 else ("does not transfer" if cnt(x, lambda z: z <= 0.65) >= 4 else "inconclusive, no claim")
            d = get(arm, lambda r, f=f: r["gd0"][f]["minus_s_lad"])
            q = ("beyond the 27-statistic baseline" if cnt(d, lambda z: z >= 0.05) >= 4 else "not shown beyond simple statistics") if ver == "transfers" else ""
            fv[f] = dict(auc=x, minus_s_lad=d, verdict=ver, qualifier=q)
        hyp = ("supported" if all(fv[f]["verdict"] == "transfers" for f in fv) else
               "falsified" if all(fv[f]["verdict"] == "does not transfer" for f in fv) else "mixed")
        fv["diffae_printed"] = get(arm, lambda r: r["gd0"]["diffae"]["auc"])
        V[f"GD0_{arm}"] = dict(families=fv, H_GD0=hyp, decides=(arm == "Sb"))
        xr = get(arm, lambda r: r["gd1"]["X_vs_REC"]["auc"])
        rg_ = get(arm, lambda r: r["gd1"]["REC_vs_G"]["auc"])
        notused = sum(1 for p_, q_ in zip(xr, rg_) if p_ is not None and q_ is not None and p_ >= 0.75 and q_ <= 0.60)
        used = cnt(rg_, lambda z: z >= 0.75) >= 4 or cnt(xr, lambda z: z <= 0.60) >= 4
        V[f"GD1_{arm}"] = dict(X_vs_REC=xr, REC_vs_G=rg_, label=("history-confounded (G is a camera photo resampled to 256 px)"
                                                                  if arm == "A" else ""), verdict="render path not used" if notused >= 4 else
                               ("render path used" if used else "inconclusive, no claim"))
        f2 = get(arm, lambda r: r["gd2"]["flags_own"]["R2"])
        a42 = get(arm, lambda r: r["gd2"]["R4_vs_R2"]["auc"])
        like = sum(1 for p_, q_ in zip(f2, a42) if p_ is not None and q_ is not None and p_ >= 0.50 and q_ <= 0.65)
        V[f"GD2_{arm}"] = dict(f_R2=f2, R4_vs_R2=a42, verdict="one-person render flagged like a morph" if like >= 4 else
                               ("not flagged" if cnt(f2, lambda z: z <= 0.10) >= 4 else "inconclusive"))
    # F2: GD0 label and coupling to Sb's GD2 verdict
    for arm in ARMS:
        V[f"GD0_{arm}"]["label"] = "StyleGAN morph against camera photo; the GAN render cue is not separated"
        for f in ("stylegan_wplus", "stylegan_w"):
            fam = V[f"GD0_{arm}"]["families"][f]
            if fam["verdict"] == "transfers" and V[f"GD2_{arm}"]["verdict"] != "not flagged":
                fam["qualifier"] = (fam["qualifier"] + "; " if fam["qualifier"] else "") + \
                    "not shown to be morph detection (GAN one-person renders are not separated, GD2)"
    out["verdicts"] = V
    pathlib.Path(a.out).write_text(json.dumps(out, indent=1))
    print(json.dumps(dict(baseline_check=chk, gd0_baselines=base), indent=0))
    for k, x in V.items():
        print(k, json.dumps(x))


if __name__ == "__main__":
    if not sys.flags.isolated:
        sys.exit("run with python -I")
    main()
