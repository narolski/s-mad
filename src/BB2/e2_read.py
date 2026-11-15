"""BB2 amendment 5 (E2) reader: zero-LoRA ablation and the frozen-feature linear probe (descriptive, post hoc,
development and training rows only; registered before the E2 job ran).
Inputs: BB2E2.tar (from wcss/bb2_e2.sbatch), the BB2 fit tars (/mnt/t7/smad_next/BB2/results, frozen in seed_mode.json),
the FS1 CLIP fit tars (/mnt/t7/smad_next/PN1/results_fs), the FS1 evaluation and training manifests.
  python3 -I e2_read.py --e2 BB2E2.tar --out OUT.json
Reads (per network): own-rule training accuracy, Sb's training AUC lad_S4 vs lad_S3, FFHQ landmark_combined AUC, test-
ladder face-only AUC (rungs S4_bg vs S0_bg, unpaired), each for the network as trained (stored fit scores) and with
LoRA zeroed (head on the frozen tower); the difference is LoRA's contribution. CLIP networks: their H100 head-only
scores are used only if the network passes the C2P.2 gate (LoRA on, H100 rescoring against the stored A100 logits;
p99 |d| <= 0.05, max <= 0.10, decisions agree >= 99.5%); otherwise only their stored (as-trained) values are printed.
Linear probe: frozen DINOv3 CLS features of train_Sb's unique rows; StandardScaler + LogisticRegression(C=1,
max_iter 5000); StratifiedGroupKFold(5, shuffle, random_state 0), groups = the person key (last two '_' tokens of the
row id); CV AUC for lad_S4 vs lad_S3 and lad_S4 vs lad_S0. Pre-stated readings in prereg amendment 5."""
import argparse
import csv
import io
import json
import pathlib
import sys
import tarfile

import numpy as np

HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / "PN1"))
import c2p_read as P  # noqa: E402  (fauc, gate: unchanged C2P functions)

FS1M = "/mnt/t7/smad_next/PN1/fs_tree/pn1/data/manifests"
BB2R = pathlib.Path("/mnt/t7/smad_next/BB2/results")
FS1R = pathlib.Path("/mnt/t7/smad_next/PN1/results_fs")
SEEDS, ARMS = (403, 404, 405, 406, 407), ("A", "B", "Sb")


def npz_tar(tar, name):
    with tarfile.open(tar) as t:
        m = [x for x in t.getmembers() if x.name.endswith(name)]
        return None if not m else dict(np.load(io.BytesIO(t.extractfile(m[0]).read()), allow_pickle=True))


def reads(eval_ids, eval_logit, tr, man):
    E = dict(zip([str(i) for i in eval_ids], eval_logit.astype(float)))
    lm = [r["id"] for r in man if r["fam"] == "ffhq_lcomb" and r["rung"] == "landmark_combined_orig"]
    lg = [r["id"] for r in man if r["fam"] == "ffhq_lcomb" and r["rung"] == "landmark_combined_resmatch"]
    s4 = [r["id"] for r in man if r["fam"] == "splice" and r["role"] == "test" and r["rung"] == "S4_bg"]
    s0 = [r["id"] for r in man if r["fam"] == "splice" and r["role"] == "test" and r["rung"] == "S0_bg"]
    out = dict(lcomb_auc=P.fauc([E[i] for i in lm], [E[i] for i in lg]),
               faceonly_test_auc_unpaired=P.fauc([E[i] for i in s4], [E[i] for i in s0]))
    k, l, y = tr["kind"].astype(str), tr["logit"].astype(float), tr["label"].astype(int)
    out["train_acc_rule0"] = float(((l > 0).astype(int) == y).mean())
    if (k == "lad_S3").any():
        out["train_auc_S4_vs_S3"] = P.fauc(l[k == "lad_S4"], l[k == "lad_S3"])
    return out


def probe(feat_npz):
    from sklearn.linear_model import LogisticRegression
    from sklearn.model_selection import StratifiedGroupKFold
    from sklearn.pipeline import make_pipeline
    from sklearn.preprocessing import StandardScaler
    k = feat_npz["kind"].astype(str)
    ids = feat_npz["id"].astype(str)
    X = feat_npz["feat"]
    res = {}
    for neg in ("lad_S3", "lad_S0"):
        m = (k == "lad_S4") | (k == neg)
        Xm, y = X[m], (k[m] == "lad_S4").astype(int)
        if y.sum() < 10 or (1 - y).sum() < 10:
            res[f"S4_vs_{neg[4:]}"] = None
            continue
        g = np.array(["_".join(i.split("_")[-2:]) for i in ids[m]])
        oof = np.zeros(len(y))
        for trn, tst in StratifiedGroupKFold(5, shuffle=True, random_state=0).split(Xm, y, g):
            mdl = make_pipeline(StandardScaler(), LogisticRegression(C=1.0, max_iter=5000)).fit(Xm[trn], y[trn])
            oof[tst] = mdl.decision_function(Xm[tst])
        res[f"S4_vs_{neg[4:]}"] = dict(cv_auc=P.fauc(oof[y == 1], oof[y == 0]), n_pos=int(y.sum()), n_neg=int((1 - y).sum()))
    return res


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--e2", required=True)
    ap.add_argument("--out", required=True)
    a = ap.parse_args()
    if pathlib.Path(a.out).exists():
        sys.exit("refused: output exists (read once)")
    import hashlib
    sha = lambda p: hashlib.sha256(pathlib.Path(p).read_bytes()).hexdigest()  # noqa: E731
    e2s = pathlib.Path(a.e2 + ".sha256")
    if not e2s.exists() or sha(a.e2) != e2s.read_text().split()[0]:
        sys.exit("refused: E2 tar sha256 missing or mismatched")
    frozen = json.load(open(HERE.parents[1] / "experiments" / "BB2_second-backbone" / "seed_mode.json"))["tars"]
    for t, h in frozen.items():
        if sha(BB2R / t) != h:
            sys.exit(f"refused: {t} is not the frozen BB2 tar")
    for arm in ARMS:
        for s in SEEDS:
            t = FS1R / f"PN1_{arm}_s{s}.tar"
            if sha(t) != (FS1R / f"PN1_{arm}_s{s}.tar.sha256").read_text().split()[0]:
                sys.exit(f"refused: {t} off its sha256")
    man = list(csv.DictReader(open(f"{FS1M}/pn1_eval.csv")))
    assert {r["fam"] for r in man} <= {"af0", "ladder", "splice", "ffhq", "ffhq_lcomb"}
    gate_ids = [r["id"] for r in man if r["fam"] in ("af0", "ffhq")]
    R = dict(dinov3={}, clip={})
    with tarfile.open(a.e2) as t:
        prec = t.extractfile([m for m in t.getmembers() if m.name.endswith("precision.txt")][0]).read().decode()
    R["precision"] = prec.strip().splitlines()[-1]
    for bb, rdir, pre in (("dinov3", BB2R, "BB2"), ("clip", FS1R, "PN1")):
        for arm in ARMS:
            for s in SEEDS:
                T = f"{pre}_{arm}_s{s}"
                st_eval = npz_tar(rdir / f"{T}.tar", "scores_eval.npz")
                st_tr = npz_tar(rdir / f"{T}.tar", "scores_train.npz")
                z_eval = npz_tar(a.e2, f"E2_{T}_eval0.npz")
                z_tr = npz_tar(a.e2, f"E2_{T}_train0.npz")
                rec = dict(as_trained=reads(st_eval["id"], st_eval["logit"], st_tr, man))
                ok = (z_eval is not None and z_tr is not None and set(map(str, z_eval["id"])) >= {r["id"] for r in man}
                      and bool(np.isfinite(z_eval["logit"]).all() and np.isfinite(z_tr["logit"]).all()))
                if bb == "clip":
                    g = npz_tar(a.e2, f"E2_{T}_gate.npz")
                    stored = dict(zip([str(i) for i in st_eval["id"]], st_eval["logit"].astype(float)))
                    rec["gate"] = P.gate(dict(zip([str(i) for i in g["id"]], g["logit"].astype(float))), stored, gate_ids) if g is not None else dict(passed=False, reason="missing")
                    ok = ok and rec["gate"]["passed"]
                if ok:
                    rec["lora_zeroed"] = reads(z_eval["id"], z_eval["logit"], z_tr, man)
                    rec["lora_contribution"] = {k: rec["as_trained"][k] - rec["lora_zeroed"][k] for k in rec["lora_zeroed"] if k in rec["as_trained"]}
                else:
                    rec["lora_zeroed"] = None
                    rec["note"] = "head-only scores not used (gate failed or missing): stored as-trained values only"
                R[bb][T] = rec
    f = npz_tar(a.e2, "E2_dinov3_feat_trainSb.npz")
    R["linear_probe_frozen_dinov3"] = probe(f) if f is not None else None
    # pre-stated summaries (prereg amendment 5)
    def small(bb, key, tol):
        v = [R[bb][f"{'BB2' if bb == 'dinov3' else 'PN1'}_Sb_s{s}"] for s in SEEDS]
        v = [x for x in v if x["lora_zeroed"] is not None]
        return dict(n=len(v), n_within=sum(abs(x["lora_contribution"][key]) <= tol for x in v))
    R["summary"] = {
        "dinov3_sb_trainS4S3_within_0.03": small("dinov3", "train_auc_S4_vs_S3", 0.03),
        "dinov3_sb_lcomb_within_0.02": small("dinov3", "lcomb_auc", 0.02),
        "clip_sb_trainS4S3_within_0.03": small("clip", "train_auc_S4_vs_S3", 0.03),
        "clip_gate_passed": sum(1 for v in R["clip"].values() if v.get("gate", {}).get("passed"))}
    pr = R["linear_probe_frozen_dinov3"]
    if pr:
        v = pr["S4_vs_S3"]["cv_auc"] if pr["S4_vs_S3"] else float("nan")
        R["summary"]["probe_reading"] = "not read" if not pr["S4_vs_S3"] else ("S4 vs S3 is linearly separable in frozen DINOv3 CLS features (>= 0.80): the under-fit "
                                         "is an optimisation matter" if v >= 0.80 else
                                         "frozen DINOv3 CLS features barely separate S4 from S3 (<= 0.65)" if v <= 0.65 else
                                         "partly separable (0.65-0.80)")
    d = R["summary"]["dinov3_sb_trainS4S3_within_0.03"]
    R["summary"]["lora_reading_dinov3"] = ("LoRA did little for Sb's splice fit on DINOv3" if d["n"] >= 4 and d["n_within"] >= 4
                                           else "LoRA contributed to Sb's splice fit on DINOv3" if d["n"] >= 4 else "not read")
    json.dump(R, open(a.out, "w"), indent=1, default=lambda o: o.item() if isinstance(o, np.generic) else str(o))
    print(json.dumps(R["summary"], indent=1))


if __name__ == "__main__":
    if not sys.flags.isolated:
        sys.exit("run with python3 -I")
    main()
