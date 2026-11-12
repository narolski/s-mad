"""Second backbone for the protocol recipe (BB2) reader. Implements experiments/BB2_second-backbone/prereg.md.
Written and committed before any BB2 fit exists. The per-seed statistics are FS1's (src/PN1/fs_read.py, c0d8dc19...,
imported, not edited): the same evaluation manifest (f0f29f22...), the same floor file, the same pools, bootstraps and
rng seeds; the per-seed block of fs_read.main is repeated here line for line with BB2 tar names. Only the seed counting
(3 seeds) and the comparison with the CLIP reading are new.
Inputs: /mnt/t7/smad_next/BB2/results/BB2_<arm>_s<seed>.tar (+ .sha256); for the comparison, FS1's reading
experiments/PN1_protocol-network-first-tests/tier_fs/fs.json when it exists (printed beside, never changes a BB2 count).
  python3 -I bb2_read.py            -> experiments/BB2_second-backbone/bb2.json
  python3 -I bb2_read.py --mock DIR -> the same reader on mock tars in DIR (test only; output bb2_mock.json)"""
import csv
import json
import pathlib
import sys
import tarfile

import numpy as np

HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / "PN1"))
import fs_read as F  # noqa: E402  (FS1 reader, unchanged)
import pn1lib as K  # noqa: E402
import reads as RD  # noqa: E402

FS_READ_SHA = "c0d8dc19cbf375aa2daf9dd434b7ab6cc1d7e5810c3da781730fe0cb159dcf21"
BB2 = pathlib.Path("/mnt/t7/smad_next/BB2")
RES = HERE.parents[1] / "experiments" / "BB2_second-backbone"
FS_JSON = HERE.parents[1] / "experiments" / "PN1_protocol-network-first-tests" / "tier_fs" / "fs.json"
SEEDS = (403, 404, 405)
ADEQ = 0.75   # training-adequacy threshold (prereg section 6), fixed before any BB2 fit
ARMS = ("A", "B", "Sb")


def info_of(tar):
    """train-set accuracy at the own rule (info.json) and the run's last logged loss values (train.log), from the tar."""
    d = tar.parent / "unpacked" / tar.name[:-4]
    out = {}
    try:
        out["train_acc_rule0"] = json.load(open(d / "info.json"))["train_acc_rule0"]
    except Exception:  # noqa: BLE001
        out["train_acc_rule0"] = None
    losses = []
    try:
        for line in open(d / "train.log", errors="replace"):
            if "loss" in line and line.lstrip().startswith(("step", "  step")):
                for tok in line.replace("=", " ").split():
                    try:
                        losses.append(float(tok))
                        break
                    except ValueError:
                        pass
    except Exception:  # noqa: BLE001
        pass
    out["train_log_nonfinite"] = any(not np.isfinite(v) for v in losses)
    return out


def count3(meets, n):
    """BB2 seed counting (prereg section 5): repeated = at least 2 of 3 (2 of 2 when one seed is lost); not repeated =
    otherwise; fewer than 2 read seeds = not read."""
    k = sum(bool(m) for m in meets)
    if n < 2:
        return "not read (too few seeds)"
    if (n == 3 and k >= 2) or (n == 2 and k == 2):
        return "repeated"
    return "not repeated"


def main(mock=None, mock_clip=None):
    rf = pathlib.Path(mock) if mock else BB2 / "results"
    assert F.sha(HERE.parent / "PN1" / "fs_read.py") == FS_READ_SHA, "fs_read.py changed"
    assert F.sha(F.EVAL) == F.EVAL_SHA
    assert F.sha(F.FLOOR) == F.FLOOR_SHA.read_text().split()[0]
    man = list(csv.DictReader(open(F.EVAL)))
    # FS1 pack assertion kept: the manifest holds development families only (no benchmark row)
    assert {r["fam"] for r in man} <= {"af0", "ladder", "splice", "ffhq", "ffhq_lcomb"}, {r["fam"] for r in man}
    # ---- from here to the end of the seed loop: fs_read.main, unchanged except RF / names / MACHINE
    lc_m = [r["id"] for r in man if r["fam"] == "ffhq_lcomb" and r["rung"] == "landmark_combined_orig"]
    lc_g = [r["id"] for r in man if r["fam"] == "ffhq_lcomb" and r["rung"] == "landmark_combined_resmatch"]
    nat = {r["host"]: r["id"] for r in man if r["fam"] == "ffhq" and r["rung"] == "ffhq_bona_orig"}
    rm = {r["host"]: r["id"] for r in man if r["fam"] == "ffhq" and r["rung"] == "landmark_complete_resmatch"}
    keys = sorted(set(nat) & set(rm))
    lad = [dict(r, fam="ladder", _splice=True) if r["fam"] == "splice" else r for r in man if r["fam"] in ("ladder", "splice", "af0")]
    cat = {r["id"]: r for r in K.catalog()}
    for r in lad:
        c = cat.get(r["id"])
        r["persons"] = c["persons"] if c else (r["host"],)
        r["neutral"] = False
        r.setdefault("field", "")
        r["pool"] = c["pool"] if c else "ladder"
    P = RD.pools([r for r in lad if not r.get("_splice")])
    for r in lad:
        if r.get("_splice"):
            P.setdefault(("T_" if r["role"] == "test" else "D_") + r["rung"], []).append(r)
    z = np.load(F.FLOOR)
    cid = {str(i): c for i, c in zip(z["ids"], z["cues"])}
    CM = np.array([cid[i] for i in lc_m]); CG = np.array([cid[i] for i in lc_g])
    rng = np.random.default_rng(20261118)
    draws = [(rng.integers(0, len(lc_m), len(lc_m)), rng.integers(0, len(lc_g), len(lc_g))) for _ in range(2000)]

    def fmax(im, ig):
        v = [F.fauc(CM[im, j], CG[ig, j]) for j in range(CM.shape[1])]
        return max(max(u, 1 - u) for u in v)
    fdraw = np.array([fmax(im, ig) for im, ig in draws])
    out = {"backbone": "DINOv3 ViT-L/16 (timm vit_large_patch16_dinov3.lvd1689m)", "mock": bool(mock),
           "floor_best_auc": float(fmax(np.arange(len(lc_m)), np.arange(len(lc_g)))), "seeds": {}}
    read = []
    for s in SEEDS:
        S = {a: F.load(rf / f"BB2_{a}_s{s}.tar") for a in ARMS}
        INF = {a: info_of(rf / f"BB2_{a}_s{s}.tar") for a in ARMS if S[a] is not None}
        # BB2 read-seed rule (prereg section 6): verified tars, finite logits, no non-finite loss in train.log
        rec = {"gpu_queue": "WCSS H100, one job per fit",
               "read": all(v is not None for v in S.values()) and not any(i["train_log_nonfinite"] for i in INF.values())}
        # BB2 training-adequacy control (prereg section 6): every arm's own-rule training-row accuracy >= 0.75
        rec["adequate"] = bool(rec["read"] and all((INF[a]["train_acc_rule0"] or 0) >= ADEQ for a in ARMS))
        if rec["read"]:
            read.append(s)
            for a in ARMS:
                x = S[a]
                m = np.array([x[i] for i in lc_m]); g = np.array([x[i] for i in lc_g])
                sd = np.array([F.fauc(m[im], g[ig]) for im, ig in draws])
                d = np.array([x[rm[k]] - x[nat[k]] for k in keys])
                pb = [np.mean(d[rng.integers(0, len(d), len(d))] > 0) for _ in range(2000)]
                fo = RD.paired(x, P, "T_S4_bg", "T_S0_bg")
                fb = RD.paired(x, P, "T_R4_face", "T_R2w_face")
                rec[a] = dict(lcomb_auc=float(F.fauc(m, g)), lcomb_ci=[float(np.percentile(sd, 2.5)), float(np.percentile(sd, 97.5))],
                              lcomb_minus_floor_lo=float(np.percentile(sd - fdraw, 2.5)),
                              share_rising=float(np.mean(d > 0)), share_ci=[float(np.percentile(pb, 2.5)), float(np.percentile(pb, 97.5))],
                              faceonly_test=fo.get("auc"), faceonly_test_ci=[fo.get("lo"), fo.get("hi")],
                              faceonly_dev=RD.paired(x, P, "D_S4_bg", "D_S0_bg").get("auc"),
                              faceblanked_test=fb.get("auc"), faceblanked_dev=RD.paired(x, P, "D_R4_face", "D_R2w_face").get("auc"),
                              flags_own={p: float(np.mean(RD.scores_of(x, P[p]) > 0)) for p in ("D_R0", "D_R0_61", "D_R0_112", "V_photo") if P.get(p)} |
                              {"ffhq_bona_orig": float(np.mean([x[nat[k]] > 0 for k in keys]))})
            A, B, Sb = (rec[a] for a in ARMS)
            rec["c1_testable"] = B["lcomb_auc"] < 0.95
            rec["c1_meets"] = bool(Sb["lcomb_auc"] - B["lcomb_auc"] >= 0.05 and Sb["lcomb_auc"] - A["lcomb_auc"] >= -0.02)
            rec["c1_floor_exceeded"] = Sb["lcomb_minus_floor_lo"] > 0
            rec["c2"] = {a: rec[a]["share_rising"] <= 0.65 for a in ARMS}
            rec["c3_meets"] = bool(Sb["faceonly_test"] - B["faceonly_test"] >= 0.05)
        # ---- BB2 additions (printed only): collapse marks, all eval logits
        for a in ARMS:
            t = rf / f"BB2_{a}_s{s}.tar"
            if S[a] is not None:
                v = np.array(list(S[a].values()))
                rec.setdefault("fit", {})[a] = dict(INF[a], eval_logit_sd=float(v.std()), eval_logit_min=float(v.min()),
                                                    eval_logit_max=float(v.max()),
                                                    collapsed=bool(v.std() < 1e-3))
            else:
                rec.setdefault("fit", {})[a] = dict(missing_or_nonfinite=True)
        out["seeds"][str(s)] = rec
    names = [str(n) for n in z["names"]]
    cmp_m = [r["id"] for r in man if r["fam"] == "ffhq" and r["rung"] == "landmark_complete_orig"]
    cmp_g = [r["id"] for r in man if r["fam"] == "ffhq" and r["rung"] == "landmark_complete_resmatch"]
    hc = {r["host"]: r["id"] for r in man if r["fam"] == "ffhq" and r["rung"] == "landmark_complete_orig"}
    hb_ = {r["host"]: r["id"] for r in man if r["fam"] == "ffhq_lcomb" and r["rung"] == "landmark_combined_orig"}
    pk = [(hc[k], hb_[k]) for k in sorted(set(hc) & set(hb_))]
    RR_ = {}
    for s in read:
        nets = {a: F.load(rf / f"BB2_{a}_s{s}.tar") for a in ARMS}
        RR_[s] = F.rreads(nets, lc_m, lc_g, cid, names, cmp_m, cmp_g, pk)
    out["printed_R1_R6"] = {str(s): v for s, v in RR_.items()}

    # ---- BB2 counting (prereg section 5)
    R = [out["seeds"][str(s)] for s in read]
    RA = [r for r in R if r["adequate"]]
    t1 = [r for r in RA if r["c1_testable"]]
    c1 = count3([r["c1_meets"] for r in t1], len(t1))
    if len(R) >= 2 and len(RA) < 2:
        c1 = "uninformative (under-trained)"
    floor_all = bool(t1) and all(r["c1_floor_exceeded"] for r in t1)
    a_fail = sum(not r["c2"]["A"] for r in R)
    control = len(R) >= 2 and a_fail >= len(R) - 1 and a_fail >= 2
    c2 = {a: ("not read (too few seeds)" if len(R) < 2 else
              count3([r["c2"][a] for r in R], len(R)) if control else "uninformative on these seeds") for a in ("B", "Sb")}
    c3 = count3([r["c3_meets"] for r in RA], len(RA))
    if len(R) >= 2 and len(RA) < 2:
        c3 = "uninformative (under-trained)"
    # printed R1-R6 sentence, FS1 conditions with the R3 count read on every read seed (prereg section 6)
    if c1 == "repeated" and not floor_all and RR_:
        meet = [s for s in read if out["seeds"][str(s)]["adequate"] and out["seeds"][str(s)]["c1_testable"]
                and out["seeds"][str(s)]["c1_meets"]]
        a_ = all(RR_[s]["R1_Sb_minus_B"]["point"] >= 0.05 for s in meet)
        b_ = all(max(abs(v) for v in RR_[s]["Sb"]["R2"].values()) <= 0.2 for s in RR_)
        c_ = all(RR_[s]["R3_Sb_inc27_minus_B"] > 0 for s in RR_)
        out["printed_R1_R6_sentence"] = dict(R1_ok=bool(a_), R2_ok=bool(b_), R3_ok_every_read_seed=bool(c_), sentence=(
            "Sb's gain over B on this development set is not explained by the best single simple statistic or by the 27 "
            "statistics combined; Sb does not exceed the best statistic's own AUC, and still reads the surround (R6)."
            if (a_ and b_ and c_) else "The gain is not separated from simple statistics."))
    out.update(read_seeds=read, adequate_seeds=[s for s in read if out["seeds"][str(s)]["adequate"]], contrast1=c1, contrast1_testable_seeds=len(t1), floor_exceeded_all=floor_all,
               contrast2=c2, contrast2_positive_control=control, contrast3=c3)

    # ---- comparison with the CLIP reading (FS1), prereg section 7
    clip = mock_clip if mock else (json.load(open(FS_JSON)) if FS_JSON.exists() else None)
    out["clip_fs1"] = None if clip is None else dict(contrast1=clip.get("contrast1"), floor_exceeded_all=clip.get("floor_exceeded_all"),
                                                     contrast2=clip.get("contrast2"), contrast2_positive_control=clip.get("contrast2_positive_control"),
                                                     contrast3=clip.get("contrast3"), read_seeds=clip.get("read_seeds"),
                                                     same_seeds={str(s): clip["seeds"].get(str(s)) for s in SEEDS} if clip.get("seeds") else None)
    out["sentences"] = sentences(out, clip)
    o = RES / ("bb2_mock.json" if mock else "bb2.json")
    o.parent.mkdir(parents=True, exist_ok=True)
    K.dump(out, o)
    print("read seeds", read, "| c1", c1, "floor", floor_all, "| c2", c2, "control", control, "| c3", c3)
    for k, v in out["sentences"].items():
        print(k, ":", v)


def sentences(out, clip):
    """Pre-stated paper sentences (prereg section 7). CLIP 'replicated' is FS1's registered word; anything else from FS1
    (not replicated, inconclusive, not read, uninformative) counts as 'no CLIP pattern to repeat'."""
    res = {}
    n = len(out["read_seeds"])
    if clip is None:
        res["note"] = "FS1 reading (tier_fs/fs.json) not available: BB2 counts printed without the CLIP comparison; no sentence."
        return res
    cv = lambda k: None if clip is None else clip.get(k)  # noqa: E731
    # contrast 1
    c1, c1c = out["contrast1"], cv("contrast1")
    if c1 in ("not read (too few seeds)", "uninformative (under-trained)"):
        res["contrast1"] = f"Second backbone: {c1}."
    elif c1c == "replicated":
        if c1 == "repeated":
            res["contrast1"] = (f"The gain of spliced positives over protocol-only training on FFHQ landmark_combined repeats on a "
                                f"second backbone (DINOv3 ViT-L/16, {n} seeds)" +
                                ("." if out["floor_exceeded_all"] else ", but is not shown beyond simple statistics there."))
        else:
            res["contrast1"] = "The gain of spliced positives on FFHQ landmark_combined did not repeat on a second backbone (DINOv3 ViT-L/16): it is not shown to be independent of the CLIP backbone."
    else:
        res["contrast1"] = (f"No CLIP effect to repeat (FS1 contrast 1: {c1c}); second backbone printed only"
                            + (" (it met the margins on at least 2 of 3 seeds; not claimed)." if c1 == "repeated" else "."))
    # contrast 2
    c2c = cv("contrast2") or {}
    for a in ("B", "Sb"):
        w, wc = out["contrast2"][a], c2c.get(a)
        if w == "uninformative on these seeds":
            res[f"contrast2_{a}"] = f"Second backbone, {a}: storage mark uninformative (A's positive control not met on DINOv3)."
        elif w == "not read (too few seeds)":
            res[f"contrast2_{a}"] = f"Second backbone, {a}: not read (too few seeds)."
        elif wc == "replicated":
            res[f"contrast2_{a}"] = (f"The protocol's removal of the storage reaction ({a}) repeats on a second backbone (DINOv3 ViT-L/16, {n} seeds), so it is not a CLIP property."
                                     if w == "repeated" else
                                     f"The removal of the storage reaction ({a}) did not repeat on a second backbone (DINOv3 ViT-L/16): it is not shown to be independent of the CLIP backbone.")
        else:
            res[f"contrast2_{a}"] = f"No CLIP effect to repeat for {a} (FS1 contrast 2: {wc}); second backbone printed only."
    # contrast 3
    c3, c3c = out["contrast3"], cv("contrast3")
    if c3 in ("not read (too few seeds)", "uninformative (under-trained)"):
        res["contrast3"] = f"Second backbone: {c3}."
    elif c3c == "replicated":
        res["contrast3"] = ("The face-only ladder gain of Sb over B repeats on a second backbone (DINOv3 ViT-L/16)." if c3 == "repeated"
                            else "The face-only ladder gain of Sb over B did not repeat on a second backbone (DINOv3 ViT-L/16).")
    else:
        res["contrast3"] = f"No CLIP effect to repeat (FS1 contrast 3: {c3c}); second backbone printed only."
    return res


def mock_test(d):
    """Mock tars from random logits (no real score): exercises loading, counting and sentences."""
    d = pathlib.Path(d)
    d.mkdir(parents=True, exist_ok=True)
    man = list(csv.DictReader(open(F.EVAL)))
    ids = [r["id"] for r in man]
    rg = np.random.default_rng(7)
    for s in SEEDS:
        for a in ARMS:
            name = f"BB2_{a}_s{s}"
            u = d / "src" / name
            u.mkdir(parents=True, exist_ok=True)
            lab = np.array([1.0 if ("orig" in r["rung"] and "bona" not in r["rung"]) or r["rung"].startswith(("R4", "S4", "u50")) else 0.0 for r in man])
            shift = {"A": 0.5, "B": 0.8, "Sb": 1.5}[a]
            lg = (rg.normal(0, 1, len(ids)) + shift * lab).astype(np.float32)
            np.savez(u / "scores_eval.npz", id=np.array(ids), logit=lg)
            json.dump({"train_acc_rule0": 0.9}, open(u / "info.json", "w"))
            (u / "train.log").write_text("step 100 loss 0.6\n")
            with tarfile.open(d / f"{name}.tar", "w") as t:
                t.add(u, arcname=name)
            (d / f"{name}.tar.sha256").write_text(F.sha(d / f"{name}.tar") + f"  {name}.tar\n")
    main(mock=d, mock_clip=dict(contrast1="replicated", floor_exceeded_all=False, contrast3="not replicated",
                                contrast2={"B": "replicated", "Sb": "inconclusive, no claim"}, contrast2_positive_control=True,
                                read_seeds=[403, 404, 405, 406, 407], seeds={}))


if __name__ == "__main__":
    if not sys.flags.isolated:
        sys.exit("run with python3 -I")
    if "--mock" in sys.argv[1:]:
        mock_test(sys.argv[sys.argv.index("--mock") + 1])
    else:
        main()
