"""SM1 amendment A14 (H-new-D): within-key rank read of the partner audit for bounded (LoRA) heads.

Per key: AUC of its 5 trained-partner morphs (KP) over its 5 evaluation-partner morphs (KE), 25 pairs, ties one half;
the per-key AUC is averaged over the seeds of an arm, then over the 500 keys; 10,000 key-bootstrap draws (seed
20261111). Also trained − KE in logits (item 1 definition) and the rank DiD between arms (same draws).

  python3 -I a12_rank.py --dir OUT/lora_scores_vitb --arms a,b,c,e,f --seeds 401,402 --name a12_rank_vitb
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


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dir", required=True)
    ap.add_argument("--arms", default="a,b,c,e,f")
    ap.add_argument("--seeds", default="401,402")
    ap.add_argument("--name", required=True)
    a = ap.parse_args()
    if not sys.flags.isolated:
        sys.exit("run with python3 -I")
    meta = list(csv.DictReader(open(K.OUT / "flists/audit.csv")))
    keys = sorted({r["key"] for r in meta if r["kind"] == "KP"})
    idx = {(r["kind"], r["key"], int(r["slot"])): r["id"] for r in meta if r["kind"] in ("KP", "KE")}
    draws = np.random.default_rng(K.SEED).integers(0, len(keys), (10000, len(keys)))
    hd = pathlib.Path(a.dir)
    res, vec = {}, {}
    for arm in a.arms.split(","):
        aucs, gaps, used = [], [], []
        for s in a.seeds.split(","):
            f = hd / f"{arm}_s{s}.npz"
            if not f.exists():
                continue
            z = np.load(f)
            zi = {str(i): float(v) for i, v in zip(z["id"], z["logit"])}
            P = np.array([[zi[idx[("KP", k, j)]] for j in range(5)] for k in keys])
            E = np.array([[zi[idx[("KE", k, j)]] for j in range(5)] for k in keys])
            d = P[:, :, None] - E[:, None, :]
            aucs.append(((d > 0) + 0.5 * (d == 0)).mean((1, 2)))
            gaps.append(P.mean(1) - E.mean(1))
            used.append(int(s))
        if not used:
            continue
        au, gp = np.mean(aucs, 0), np.mean(gaps, 0)
        vec[arm] = au
        res[arm] = dict(seeds=used, auc=round(float(au.mean()), 4), auc_ci=[round(x, 4) for x in S.ci(au[draws].mean(1))],
                        auc_per_seed=[round(float(x.mean()), 4) for x in aucs],
                        trained_minus_KE=round(float(gp.mean()), 4), gap_ci=[round(x, 4) for x in S.ci(gp[draws].mean(1))])
        print(arm, json.dumps(res[arm]), flush=True)
    did = {}
    for x in ("a", "b"):
        for y in ("c", "e", "f"):
            if x in vec and y in vec:
                d = vec[x] - vec[y]
                did[f"{x}-{y}"] = dict(did=round(float(d.mean()), 4), ci=[round(v, 4) for v in S.ci(d[draws].mean(1))])
    res["rank_did"] = did
    print(json.dumps(did))
    json.dump(res, open(K.RES / f"{a.name}.json", "w"), indent=1)


if __name__ == "__main__":
    main()
