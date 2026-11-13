"""PR1 amendment 3 reads Z1b-1, Z1b-2, Z1b-3, Z3b (post hoc, registered before computing). Stored scores of the 15 FS1
networks, read from tar members after the sha256 check. Development data only.
  python -I z1b_read.py --out z1b_read.json"""
import argparse
import itertools
import json
import pathlib
import re
import sys

import numpy as np

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from pr1_read import ARMS, SEEDS, auc, load_net, manifest  # noqa: E402

B = 2000


def host_of(path):
    m = re.search(r"sp2_S[034]_opencv_(feret|frgc)_(\d+)", path)
    return f"{m.group(1)}:{m.group(2)}" if m else None


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True)
    a = ap.parse_args()
    rows = manifest()
    by = {r["id"]: r for r in rows}
    nets = {(arm, s): load_net(arm, s, False, set(by), None) for arm in ARMS for s in SEEDS}
    out = dict(per_net={})
    flagged = {}
    for s in SEEDS:
        tr = nets[("Sb", s)]["train"]
        s3 = {host_of(r["path"]): r["logit"] for r in tr if r["kind"] == "lad_S3"}
        s4 = {host_of(r["path"]): r["logit"] for r in tr if r["kind"] == "lad_S4"}
        assert len(s3) == 156 and len(s4) == 124, (len(s3), len(s4))
        flagged[s] = {h for h, x in s3.items() if x > 0}
        cut = float(np.quantile(list(s3.values()), 0.95))
        m_at = float(np.mean([x <= cut for x in s4.values()]))
        both = sorted(set(s3) & set(s4))
        marg_tr = float(np.median([s4[h] - s3[h] for h in both]))
        e = nets[("Sb", s)]["eval"]
        res = {}
        for role in ("dev", "test"):
            t3 = {by[i]["host"]: e[i] for i in e if by[i]["fam"] == "splice" and by[i]["role"] == role and by[i]["rung"] == "S3"}
            t4 = {by[i]["host"]: e[i] for i in e if by[i]["fam"] == "splice" and by[i]["role"] == role and by[i]["rung"] == "S4"}
            hs = sorted(set(t3) & set(t4))
            res[role] = dict(hosts=hs, s3=np.array([t3[h] for h in hs]), s4=np.array([t4[h] for h in hs]))
        marg_te = float(np.median(res["test"]["s4"] - res["test"]["s3"]))
        d_obs = auc(res["dev"]["s4"], res["dev"]["s3"]) - auc(res["test"]["s4"], res["test"]["s3"])
        rng = np.random.default_rng(20261146)
        bs = []
        for _ in range(B):
            i = rng.integers(0, len(res["dev"]["hosts"]), len(res["dev"]["hosts"]))
            j = rng.integers(0, len(res["test"]["hosts"]), len(res["test"]["hosts"]))
            bs.append(auc(res["dev"]["s4"][i], res["dev"]["s3"][i]) - auc(res["test"]["s4"][j], res["test"]["s3"][j]))
        ci = [float(np.percentile(bs, 2.5)), float(np.percentile(bs, 97.5))]
        out["per_net"][f"Sb_s{s}"] = dict(n_train_S3_flagged=len(flagged[s]), train_S4_miss_at_S3_5pct=m_at, cut=cut,
                                          margin_train_median=marg_tr, margin_test_median=marg_te, n_pairs_train=len(both),
                                          dev_minus_test_S4vsS3=d_obs, dev_minus_test_ci=ci)
    # Z1b-1 overlaps
    N = 156
    ratio = {}
    pairs = {}
    for s, t in itertools.combinations(SEEDS, 2):
        A_, B_ = flagged[s], flagged[t]
        inter, uni = len(A_ & B_), len(A_ | B_)
        e_int = len(A_) * len(B_) / N
        e_uni = len(A_) + len(B_) - e_int
        j, jc = inter / uni, e_int / e_uni
        pairs[f"{s}-{t}"] = dict(jaccard=j, chance=jc, ratio=j / jc)
    for s in SEEDS:
        ratio[s] = float(np.mean([v["ratio"] for k, v in pairs.items() if str(s) in k.split("-")]))
    out["z1b1_pairs"] = pairs
    out["z1b1_ratio_per_seed"] = ratio
    V = {}
    r = list(ratio.values())
    V["Z1b1"] = dict(ratio=r, verdict="falsified" if sum(x <= 1.5 for x in r) >= 4 else ("supported" if sum(x >= 3.0 for x in r) >= 4 else "weak"))
    m = [out["per_net"][f"Sb_s{s}"]["train_S4_miss_at_S3_5pct"] for s in SEEDS]
    V["Z1b2"] = dict(miss=m, verdict="supported" if sum(x >= 0.30 for x in m) >= 4 else ("falsified" if sum(x <= 0.10 for x in m) >= 4 else "weak"))
    c = [out["per_net"][f"Sb_s{s}"]["dev_minus_test_ci"] for s in SEEDS]
    V["Z1b3"] = dict(diff=[out["per_net"][f"Sb_s{s}"]["dev_minus_test_S4vsS3"] for s in SEEDS], ci=c,
                     verdict="sampling-compatible" if sum(lo <= 0 <= hi for lo, hi in c) >= 3 else "a dev/test difference beyond sampling")
    # Z3b
    for arm in ARMS:
        d3, d3m, ci3 = [], [], []
        for s in SEEDS:
            e = nets[(arm, s)]["eval"]
            H = {}
            for i, x in e.items():
                rr = by[i]
                if rr["fam"] == "ladder" and rr["role"] == "test" and rr["strength"] == "" and rr["rung"] in ("R4", "R3", "R3m") and rr["tool"] in ("opencv", "facemorpher"):
                    H.setdefault((rr["tool"], rr["rung"]), {})[rr["host"]] = x
            hs = sorted(set.intersection(*[set(v) for v in H.values()]))
            M = {k: np.array([v[h] for h in hs]) for k, v in H.items()}
            f = lambda neg, ix=slice(None): auc(M[("opencv", "R4")][ix], M[("opencv", neg)][ix]) - auc(M[("facemorpher", "R4")][ix], M[("facemorpher", neg)][ix])  # noqa: E731
            d3.append(f("R3"))
            d3m.append(f("R3m"))
            rng = np.random.default_rng(20261146)
            bs = [f("R3", rng.integers(0, len(hs), len(hs))) for _ in range(B)]
            ci3.append([float(np.percentile(bs, 2.5)), float(np.percentile(bs, 97.5))])
        V[f"Z3b_{arm}"] = dict(delta_R3=d3, ci=ci3, delta_R3m=d3m, n_hosts=len(hs),
                               verdict="engine gap" if sum(x >= 0.03 for x in d3) >= 4 else ("no engine gap" if sum(x <= 0.01 for x in d3) >= 4 else "inconclusive"))
    out["verdicts"] = V
    pathlib.Path(a.out).write_text(json.dumps(out, indent=1))
    for k, v in V.items():
        print(k, json.dumps({kk: (np.round(vv, 3).tolist() if isinstance(vv, list) else vv) for kk, vv in v.items()}))
    for s in SEEDS:
        print(s, {k: (round(v, 3) if isinstance(v, float) else v) for k, v in out["per_net"][f"Sb_s{s}"].items() if k != "dev_minus_test_ci"})


if __name__ == "__main__":
    if not sys.flags.isolated:
        sys.exit("run with python -I")
    main()
