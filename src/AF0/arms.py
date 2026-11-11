"""Wave 3 control 4 (five-arm ablation) and wave 4 (the same arms with softened copies): fits and reads.

Arms (heads.py ARMS; positives = uniform-0.5 morphs only, "one global mixing weight"):
  a  image-level logistic, camera photos as negatives      b  image-level logistic, warped halves as negatives
  c  per-patch ridge, constant 0.5 inside the face hull, halves as negatives
  d  per-patch ridge, measured map D (the only target accepted by the wave-3 sanity rule) with halves
  e  per-patch ridge, measured map D with camera photos only;   a4 ... e4: the same with softened copies added.
Reads per arm: held-out-tool AUC (landmark ladder (AR1) FaceMorpher R2w vs R4, descriptive; OpenCV R2w vs R4; the
Poisson set (A27) morph vs genuine; against softened warp-only images R2w_soft), each with the Laplacian-variance and
best-simple-statistic floor; FRLL genuine native -> E7 shift under mean and top-tenth pooling; flag rate of FRLL E7
genuine frames and of softened R0 photos at the threshold that flags 5% of the native ones; F4 drop (confounded:
positives from FRGC pairs, negatives from colorFERET; unconfounded: same counts half / half; crossed test: colorFERET
validation u50 vs FRGC validation zero-field + halves).
  python3 -I arms.py fit --backbone clip224 [--arms a,b,c,d,e]
  python3 -I arms.py read --backbone clip224
"""
import argparse
import collections
import json
import pathlib
import random
import subprocess
import sys

import numpy as np

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import af0lib as L  # noqa: E402
import heads as HD  # noqa: E402
import metrics as M  # noqa: E402

PY = "/home/narolski/mambamorph-code/.venv-spark/bin/python"
TRAIN = "af0_w1,af0_w2,af0_h"
TRAIN4 = "af0_w1,af0_w2,af0_h,soft"
EVAL = "af0_w1,af0_w2,af0_h,ar1,bench_s,h1,ar1soft"


def full_names(short):
    return [k for k in HD.ARMS if k.split("_")[0] in short.split(",")]


def f4_ids(arm, train_lists):
    spec = HD.ARMS[arm]
    R = [r for n in train_lists.split(",") for r in L.rows(n) if r["set"] == "af0" and r["cell"] == "train"]
    pos = [r for r in R if r["rung"] in spec["pos"]]
    neg = [r for r in R if r["rung"] in spec["neg"]]
    conf = [r["id"] for r in pos if r["tool"] == "frgc"] + [r["id"] for r in neg if r["tool"] == "feret"]
    rng = random.Random(401)
    unconf = []
    for cls, n_ in ((pos, sum(r["tool"] == "frgc" for r in pos)), (neg, sum(r["tool"] == "feret" for r in neg))):
        for db in ("frgc", "feret"):
            c = [r["id"] for r in cls if r["tool"] == db]
            rng.shuffle(c)
            unconf += c[: n_ // 2]
    return conf, unconf


def fit(a):
    for arm in full_names(a.arms):
        tl = TRAIN4 if arm[1] == "4" else TRAIN
        cmds = [["--tag", f"arm_{arm}"]]
        conf, unconf = f4_ids(arm, tl)
        d = L.OUT / "f4arms"
        d.mkdir(exist_ok=True)
        np.save(d / f"{arm}_conf.npy", np.array(conf))
        np.save(d / f"{arm}_unconf.npy", np.array(unconf))
        cmds.append(["--tag", f"arm_{arm}_f4conf", "--train-ids", str(d / f"{arm}_conf.npy")])
        cmds.append(["--tag", f"arm_{arm}_f4unconf", "--train-ids", str(d / f"{arm}_unconf.npy")])
        for extra in cmds:
            ev = EVAL if extra[1] == f"arm_{arm}" else "af0_w1,af0_w2,af0_h"
            if (L.OUT / "heads" / a.backbone / extra[1] / "log.json").exists():
                continue
            c = [PY, "-I", "heads.py", "--backbone", a.backbone, "--train", tl, "--eval", ev, "--arm", arm, "--partial"] + extra
            print(" ".join(c), flush=True)
            subprocess.run(c, check=True, cwd=str(pathlib.Path(__file__).resolve().parent))


def flag_rate(S, lst, ref_fn, test_fn, q=0.95):
    R = M.rows(lst)
    ref = [float(S[i]) for i, r in R.items() if i in S and ref_fn(r)]
    tst = [float(S[i]) for i, r in R.items() if i in S and test_fn(r)]
    if len(ref) < 5 or len(tst) < 5:
        return None
    thr = np.quantile(ref, q)
    return dict(rate=round(float(np.mean(np.array(tst) >= thr)), 4), n=len(tst), ref_rate=round(float(np.mean(np.array(ref) >= thr)), 4))


def read_arm(bb, tag, head, key):
    get = lambda lst: (M.load(bb, tag, head, lst, key) or (None,))[0]  # noqa
    out = {}
    S = get("ar1")
    if S:
        for tool in ("opencv", "facemorpher"):
            for name, pos, neg in (("R2wvsR4", "R4", "R2w"), ("R3vsR4", "R4", "R3"), ("R3mvsR4", "R4", "R3m"),
                                   ("R0vsR4", "R4", "R0")):
                nf = (lambda r: r["cell"] == "frgcferet" and r["rung"] == "R0") if neg == "R0" else \
                    (lambda r, t=tool, n=neg: r["cell"] == "frgcferet" and r["tool"] == t and r["rung"] == n)
                c = M.contrast(S, "ar1", lambda r, t=tool, p=pos: r["cell"] == "frgcferet" and r["tool"] == t and r["rung"] == p, nf)
                if c:
                    out[f"ladder_{tool}_{name}"] = c
    Ss = get("ar1soft")
    if S and Ss:
        both = dict(S)
        both.update(Ss)
        M._ROWS["ar1+soft"] = {**M.rows("ar1"), **M.rows("ar1soft")}
        M._CUES["ar1+soft"] = None
        for tool in ("opencv", "facemorpher"):
            for st in ("amsl112", "fm61"):
                c = M.contrast(both, "ar1+soft", lambda r, t=tool: r["cell"] == "frgcferet" and r["tool"] == t and r["rung"] == "R4",
                               lambda r, t=tool, s=st: r["tool"] == t and r["rung"] == f"R2w_soft_{s}")
                if c:
                    out[f"ladder_{tool}_R2w_soft_{st}_vs_R4"] = c
        for st in ("amsl112", "fm61"):
            fr = flag_rate(both, "ar1+soft", lambda r: r["cell"] == "frgcferet" and r["rung"] == "R0",
                           lambda r, s=st: r["rung"] == f"R0_soft_{s}")
            if fr:
                out[f"flag5_R0_soft_{st}"] = fr
    Sh = get("h1")
    if Sh:
        out["poisson_h1"] = M.contrast(Sh, "h1", lambda r: r["rung"] == "morph", lambda r: r["rung"] == "bona")
    Sb = get("bench_s")
    if Sb:
        for fam in ("opencv", "facemorpher", "amsl", "webmorph"):
            s_ = M.shift(Sb, "bench_s", lambda r: r["cell"] == "frllm_frll_bona", lambda r, f=fam: r["cell"] == f"frllm_{f}" and r["rung"] == "e7")
            if s_:
                out[f"FRLL_native_to_E7_{fam}"] = s_
            fr = flag_rate(Sb, "bench_s", lambda r: r["cell"] == "frllm_frll_bona", lambda r, f=fam: r["cell"] == f"frllm_{f}" and r["rung"] == "e7")
            if fr:
                out[f"flag5_FRLL_E7_{fam}"] = fr
    return out


def read_f4(bb, arm, head):
    res = {}
    for tag in (f"arm_{arm}_f4conf", f"arm_{arm}_f4unconf"):
        S = {}
        for lst in ("af0_w1", "af0_w2", "af0_h"):
            P = M.load(bb, tag, head, lst)
            if P:
                S.update(P[0])
        if not S:
            continue
        M._ROWS["af0all"] = {**M.rows("af0_w1"), **M.rows("af0_w2"), **M.rows("af0_h")}
        M._CUES["af0all"] = None
        c = M.contrast(S, "af0all", lambda r: r["cell"] == "val" and r["tool"] == "feret" and r["rung"] == "u50",
                       lambda r: r["cell"] == "val" and r["tool"] == "frgc" and r["rung"] in ("zero", "halfA", "halfB"))
        res[tag.split("_")[-1]] = c
    if "f4conf" in res and "f4unconf" in res and res["f4conf"] and res["f4unconf"]:
        res["drop"] = round(res["f4unconf"]["auc"] - res["f4conf"]["auc"], 4)
    return res


def read(a):
    res = {}
    for arm in HD.ARMS:
        head = "logreg" if HD.ARMS[arm]["kind"] == "img" else "ridge"
        if not (L.OUT / "heads" / a.backbone / f"arm_{arm}").exists():
            continue
        r = {"mean": read_arm(a.backbone, f"arm_{arm}", head, "score")}
        if head == "ridge":
            r["top10"] = read_arm(a.backbone, f"arm_{arm}", head, "score_top10")
        r["F4"] = read_f4(a.backbone, arm, head)
        res[arm] = r
        print(arm, json.dumps({k: v.get("auc", v) if isinstance(v, dict) else v for k, v in r["mean"].items()})[:400], flush=True)
    json.dump(res, open(L.RES / f"arms_{a.backbone}.json", "w"), indent=1)


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("cmd", choices=("fit", "read"))
    ap.add_argument("--backbone", default="clip224")
    ap.add_argument("--arms", default="a,b,c,d,e")
    a = ap.parse_args()
    fit(a) if a.cmd == "fit" else read(a)
