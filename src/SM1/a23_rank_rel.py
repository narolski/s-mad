"""SM1 amendment A23 (registered 80ba899 before computing; descriptive): within-key AUC (A14 definition) of the
released detectors on the Part 2 audit set, crop path (primary) and whole files (secondary).

  python3 -I a23_rank_rel.py -> RES/a23_rank_rel.json
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


def main():
    if not sys.flags.isolated:
        sys.exit("run with python3 -I")
    meta = list(csv.DictReader(open(K.OUT / "flists/audit.csv")))
    keys = sorted({r["key"] for r in meta if r["kind"] == "KP"})
    idx = {(r["kind"], r["key"], int(r["slot"])): r["id"] for r in meta if r["kind"] in ("KP", "KE")}
    draws = np.random.default_rng(K.SEED).integers(0, len(keys), (10000, len(keys)))
    res = {}
    for tag, d in (("crop_path", K.OUT / "p2scores"), ("whole_file", K.OUT / "p2scores/whole")):
        res[tag] = {}
        for det in DETS:
            f = d / f"scores_rel_{det}.npz"
            if not f.exists():
                continue
            z = np.load(f)
            zi = {str(i): float(v) for i, v in zip(z["id"], z["logit_noTTA"])}
            P = np.array([[zi[idx[("KP", k, j)]] for j in range(5)] for k in keys])
            E = np.array([[zi[idx[("KE", k, j)]] for j in range(5)] for k in keys])
            dd = P[:, :, None] - E[:, None, :]
            au = ((dd > 0) + 0.5 * (dd == 0)).mean((1, 2))
            res[tag][det] = dict(auc=round(float(au.mean()), 4), ci=[round(x, 4) for x in S.ci(au[draws].mean(1))],
                                 tie_share=round(float((dd == 0).mean()), 4),
                                 trained_minus_KE=round(float((P.mean(1) - E.mean(1)).mean()), 4))
            print(tag, det, res[tag][det], flush=True)
    res["note"] = "descriptive (A23); one network per release; key bootstrap only"
    json.dump(res, open(K.RES / "a23_rank_rel.json", "w"), indent=1)


if __name__ == "__main__":
    main()
