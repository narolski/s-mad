"""SM1 amendment A12 item 7 (post hoc, H-new-6): partner-level variance of SMDD evaluation-split error rates.

From the T-A subsample scores (A8: per split 500 release morphs per partner, 1,000 genuine renders; whole-file path,
logit without TTA): per release and split, EER per partner (its 500 morphs against the split's 1,000 genuine
renders) and the pooled EER (2,500 morphs) with two bootstrap intervals (B = 2,000, seed 20261111):
  one-way = multinomial draws over first contributors (keys) and over genuine renders;
  two-way = the same, times multinomial draws over the 5 partners (morph weight = count(key) x count(partner)).
Prediction (review): evaluation-split per-partner spread > 5 points and two-way interval >= 3 x one-way;
falsified if the spread < 2 points.

  python3 -I a12_partner_var.py -> RES/a12_partner_var.json
"""
import csv
import json
import pathlib
import sys

import numpy as np

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import sm1_common as K  # noqa: E402
import sm1_stats as S  # noqa: E402

DETS = ("madation_vitb16", "madation_vitl14", "madation_fe_vitb16", "madation_fe_vitl14", "mixfacenet_mad_smdd",
        "madation_fs_vitb16", "madation_fs_vitl14")
B = 2000


def mult(n, rng):
    return rng.multinomial(n, np.full(n, 1.0 / n), size=B).astype(np.float64)


def main():
    if not sys.flags.isolated:
        sys.exit("run with python3 -I")
    rows = list(csv.DictReader(open(K.OUT / "flists/tab_sub.csv")))
    res = {}
    for det in DETS:
        f = K.OUT / f"p2scores/tab_sub/scores_rel_{det}.npz"
        zf = np.load(f)
        z = {str(i): float(v) for i, v in zip(zf["id"], zf["logit_noTTA"])}
        res[det] = {}
        for sp in ("eval", "train"):
            rng = np.random.default_rng([K.SEED, 7, ("eval", "train").index(sp)])
            mo = [r for r in rows if r["split"] == sp and r["kind"] == "morph"]
            ge = [r for r in rows if r["split"] == sp and r["kind"] == "genuine"]
            zm = np.array([z[r["id"]] for r in mo])
            zg = np.array([z[r["id"]] for r in ge])
            parts = sorted({r["partner"] for r in mo})
            keys = sorted({r["key"] for r in mo})
            per = {p: round(S.eer_unit(zg, zm[[r["partner"] == p for r in mo]])[0], 3) for p in parts}
            pooled = S.eer_unit(zg, zm)[0]
            Ck, Cp, Cg = mult(len(keys), rng), mult(len(parts), rng), mult(len(zg), rng)
            ki = np.array([keys.index(r["key"]) for r in mo])
            pi = np.array([parts.index(r["partner"]) for r in mo])
            e1, _ = S.weer(zg, zm, Cg, Ck[:, ki])
            e2, _ = S.weer(zg, zm, Cg, Ck[:, ki] * Cp[:, pi])
            c1, c2 = S.ci(e1), S.ci(e2)
            res[det][sp] = dict(eer_per_partner=per, spread=round(max(per.values()) - min(per.values()), 3),
                                pooled_eer=round(pooled, 3), one_way_ci=[round(x, 3) for x in c1],
                                two_way_ci=[round(x, 3) for x in c2],
                                width_ratio=round((c2[1] - c2[0]) / max(c1[1] - c1[0], 1e-9), 2),
                                n_keys=len(keys), n_morph=len(zm), n_genuine=len(zg))
            print(det, sp, json.dumps(res[det][sp]), flush=True)
    ev = {d: res[d]["eval"] for d in DETS[:5]}
    res["prediction"] = dict(
        text="evaluation split, 5 primary releases: per-partner spread > 5 points and two-way >= 3 x one-way width; "
             "falsified if spread < 2 points",
        spread=[ev[d]["spread"] for d in DETS[:5]], width_ratio=[ev[d]["width_ratio"] for d in DETS[:5]])
    json.dump(res, open(K.RES / "a12_partner_var.json", "w"), indent=1)


if __name__ == "__main__":
    main()
