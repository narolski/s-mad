"""SM1 amendment A12 item 3 (post hoc re-read, review F5): fixed-threshold paired table for every arm.

Per head (arm x seed; FE header as reference) and two thresholds:
  cam  = camera-photo threshold, the 95th percentile of the head's logits on AR1 FRGC/colorFERET R0 (5% flagged)
  own  = the head's own rule, logit >= 0
flag rates (genuine-class images scored >= t): AR1 halves (HA + HB), AR1 R2w (OpenCV, FaceMorpher), AR1 R0 (frgcferet
and FRLL pools), every history-matched genuine pool (E7 of each cell), untouched FRLL photos (frllm:bona, 204),
FRLL photos under JPEG 90 / 70 / 50 and the paired increments JPEG q - untouched (same 204 photos, same person
weights); miss rates (morphs scored < t): FRLL landmark-4 pooled, each history-matched cell's morphs, AR1 OpenCV and
FaceMorpher R4 (frgcferet pool). 5-seed means with person-bootstrap intervals (read_p3.Reader draws, B = 2,000), and
paired step differences (same draws) for the registered steps.

  python3 -I a12_fixed.py [--dir OUT/heads] [--name a12_fixed] [--arms ...] -> RES/<name>.json, RES/<name>_seeds.csv
"""
import argparse
import csv
import json
import pathlib
import sys

import numpy as np

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import sm1_common as K  # noqa: E402
import sm1_stats as S  # noqa: E402
import read_p3 as P  # noqa: E402


def rate(R, z, ix, t, ar1, flag=True):
    f = (z[ix] >= t) if flag else (z[ix] < t)
    f = f.astype(float)
    W = R.w(ix, ar1)
    return float(f.mean()), (W * f).sum(1) / np.maximum(W.sum(1), 1e-12)


def one(R, z):
    m = {}
    g = lambda pool, tool, rung, lab="0": R.sel(f"ar1:{pool}:{tool}:{rung}", lab, "")  # noqa: E731
    r0 = g("frgcferet", "none", "R0")
    thr = {"cam": float(np.quantile(z[r0], 0.95)), "own": 0.0}
    m["thr:cam"] = (thr["cam"], None)
    ar1 = {"halves": np.concatenate([g("frgcferet", "opencv", "HA"), g("frgcferet", "opencv", "HB")]),
           "r2w_opencv": g("frgcferet", "opencv", "R2w"), "r2w_facemorpher": g("frgcferet", "facemorpher", "R2w"),
           "r0_frgcferet": r0, "r0_frll": g("frll", "none", "R0")}
    ar1m = {"r4_opencv": g("frgcferet", "opencv", "R4", "1"), "r4_facemorpher": g("frgcferet", "facemorpher", "R4", "1")}
    nat = R.sel("frllm:bona", "0", "native")
    for tn, t in thr.items():
        for k, ix in ar1.items():
            if len(ix):
                m[f"flag:{tn}:ar1_{k}"] = rate(R, z, ix, t, True)
        for k, ix in ar1m.items():
            if len(ix):
                m[f"miss:{tn}:ar1_{k}"] = rate(R, z, ix, t, True, flag=False)
        fn = rate(R, z, nat, t, False)
        m[f"flag:{tn}:frll_untouched"] = fn
        for q in ("jpeg90", "jpeg70", "jpeg50"):
            ix = R.sel(f"frllm:bona_{q}", "0", q)
            if len(ix):
                assert [R.rows[i]["path"].rsplit("_", 1)[0] for i in ix] == \
                       [R.rows[i]["path"].rsplit("_", 1)[0] for i in nat]          # same 204 photos, same order
                fq = rate(R, z, ix, t, False)
                m[f"flag:{tn}:frll_{q}"] = fq
                m[f"jinc:{tn}:{q}"] = (fq[0] - fn[0], fq[1] - fn[1])
        lm = np.concatenate([R.sel(f"frllm:{f}", "1", "morph") for f in P.FRLLM if f != "stylegan"])
        m[f"miss:{tn}:frll_landmark4"] = rate(R, z, lm, t, False, flag=False)
        for c, (gn, ge, mo) in P.cells().items():
            ig, im = R.sel(*ge), R.sel(*mo)
            if len(ig) and len(im):
                m[f"flag:{tn}:e7_{c}"] = rate(R, z, ig, t, False)
                m[f"miss:{tn}:e7_{c}"] = rate(R, z, im, t, False, flag=False)
    return m


STEPS = (("a", "b"), ("b", "bp"), ("bp", "cr"), ("cr", "c"), ("c", "d"), ("c", "dplus"), ("d", "e"), ("e", "f"),
         ("a", "e"), ("a", "f"), ("b", "d50"), ("b", "d500"), ("a", "a256"), ("b", "d5"), ("d5", "d50"))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--arms", default="a,a256,b,d5,d50,d500,bp,cr,c,d,dplus,e,f")
    ap.add_argument("--seeds", default="401,402,403,404,405")
    ap.add_argument("--dir", default=None)
    ap.add_argument("--name", default="a12_fixed")
    ap.add_argument("--B", type=int, default=2000)
    ap.add_argument("--no-feref", action="store_true")
    a = ap.parse_args()
    if not sys.flags.isolated:
        sys.exit("run with python3 -I")
    rows = P.meta()
    hd = pathlib.Path(a.dir) if a.dir else K.OUT / "heads"
    first = next((hd / f"{arm}_s{s}.npz" for arm in a.arms.split(",") for s in a.seeds.split(",")
                  if (hd / f"{arm}_s{s}.npz").exists()))
    have = {str(i) for i in np.load(first)["id"]}
    rows = [r for r in rows if r["id"] in have]
    R = P.Reader(rows, a.B)
    raw, csvrows = {}, []
    sets = [(arm, s) for arm in a.arms.split(",") for s in a.seeds.split(",")]
    if not a.no_feref:
        sets.append(("feref", None))
    for arm, s in sets:
        f = K.OUT / "heads/feref.npz" if arm == "feref" else hd / f"{arm}_s{s}.npz"
        if not f.exists():
            continue
        zf = np.load(f)
        zi = {str(i): v for i, v in zip(zf["id"], zf["logit"])}
        z = np.array([zi.get(r["id"], np.nan) for r in rows], np.float64)
        if not np.isfinite(z).all():
            sys.exit(f"{f}: test rows without a score")
        m = one(R, z)
        raw.setdefault(arm, []).append(m)
        for k, (p, _) in m.items():
            csvrows.append(dict(arm=arm, seed=s or "", metric=k, value=round(float(p), 5)))
    res = dict(arms={arm: P.summarise(ms) for arm, ms in raw.items()}, steps={})
    for x, y in STEPS:
        if x in raw and y in raw:
            res["steps"][f"{x}->{y}"] = {k: P.diff(raw[x], raw[y], k) for k in raw[x][0]
                                        if not k.startswith("thr") and k in raw[y][0]}
    res["note"] = ("post hoc re-read (A12 item 3); cam = 95th percentile of the head's AR1 FRGC/colorFERET R0 logits; "
                   "own = logit >= 0; our frames, first-test data, arms fixed in advance")
    json.dump(res, open(K.RES / f"{a.name}.json", "w"), indent=1)
    with open(K.RES / f"{a.name}_seeds.csv", "w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=["arm", "seed", "metric", "value"])
        w.writeheader()
        w.writerows(csvrows)
    keys = ("flag:cam:ar1_halves", "flag:cam:ar1_r2w_opencv", "flag:cam:frll_untouched", "jinc:cam:jpeg50",
            "miss:cam:frll_landmark4", "miss:cam:ar1_r4_opencv", "flag:own:ar1_halves", "flag:own:frll_untouched",
            "jinc:own:jpeg50", "miss:own:frll_landmark4", "flag:cam:e7_mordiff:mordiff", "miss:cam:e7_mordiff:mordiff")
    print("arm " + " ".join(k.split(":", 1)[1] for k in keys))
    for arm, d in res["arms"].items():
        print(arm, " ".join(f"{d[k]['mean']:.3f}" if k in d else "-" for k in keys))


if __name__ == "__main__":
    main()
