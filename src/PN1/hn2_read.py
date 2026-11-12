"""PN1 amendment 13 reader (HN2, FFHQ only), written before any HN2 score exists.
Per tier-1 network (A, B, Bn, C x seeds 401, 402), from PN1_HN2_s<seed>.tar (scores_hn2_<arm>.npz, logit, no flip):
  (a) share of FFHQ bona fide (ffhq_bona orig, 2,000) with logit > 0 (own rule tau_0.5)
  (b) within-source AUC: landmark_complete orig morphs (1,000) vs ffhq_bona orig (2,000); disjoint persons
  rule: 'shortcut supported' if (a) >= 0.30 and (b) <= 0.75; 'calibration shift (not a shortcut)' if (b) >= 0.90;
        otherwise 'inconclusive'. An arm-level sentence needs both seeds with the same verdict, else 'mixed'.
  printed only: 95% bootstrap intervals (2,000 draws, rng 20261113, images resampled within class); (a) at tau_cam of
  the same network (tier-1 thresholds); AUC of the morphs vs the history-matched bona fide (landmark_complete resmatch)
  and its flag share.
  python3 -I hn2_read.py -> experiments/PN1_.../tier1/hn2.json"""
import hashlib
import pathlib
import sys
import tarfile

import numpy as np

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import pn1lib as K  # noqa: E402
import reads as RD  # noqa: E402
import tier1 as T1  # noqa: E402

RR = K.PN1 / "results_rented"
MAN = K.PN1 / "hn2_tree" / "pn1h" / "data" / "manifests" / "pn1_hn2.csv"
LIST_SHA = "4c0caa89ab25406854b6865c17943ef5e9532b0e5cc8bed58ad8e73d53b15871"


def verdict(a, b):
    if a >= 0.30 and b <= 0.75:
        return "shortcut supported"
    if b >= 0.90:
        return "calibration shift (not a shortcut)"
    return "inconclusive"


def boot(fn, pos, neg, rng, n=2000):
    v = [fn(pos[rng.integers(0, len(pos), len(pos))], neg[rng.integers(0, len(neg), len(neg))]) for _ in range(n)]
    return [float(np.percentile(v, 2.5)), float(np.percentile(v, 97.5))]


def main():
    import csv
    assert hashlib.sha256(MAN.read_bytes()).hexdigest() == LIST_SHA
    rows = list(csv.DictReader(open(MAN)))
    grp = {k: [r["id"] for r in rows if r["rung"] == k] for k in ("ffhq_bona_orig", "landmark_complete_orig", "landmark_complete_resmatch")}
    ev = T1.eval_rows()
    P = RD.pools(ev)
    out = {"list_sha256": LIST_SHA, "rule": "a>=0.30 and b<=0.75 shortcut; b>=0.90 calibration shift; else inconclusive"}
    rng = np.random.default_rng(20261113)
    for seed in (401, 402):
        tar = RR / f"PN1_HN2_s{seed}.tar"
        if not tar.exists():
            out[f"s{seed}"] = "not landed"
            continue
        h = hashlib.sha256(tar.read_bytes()).hexdigest()
        assert h == (RR / (tar.name + ".sha256")).read_text().split()[0]
        d = RR / "unpacked"
        if not (d / tar.name[:-4]).exists():
            with tarfile.open(tar) as t:
                t.extractall(d)
        for arm in ("A", "B", "Bn", "C"):
            z = np.load(d / tar.name[:-4] / f"scores_hn2_{arm}.npz")
            s = dict(zip([str(i) for i in z["id"]], z["logit"].astype(float)))
            bona = np.array([s[i] for i in grp["ffhq_bona_orig"]])
            mor = np.array([s[i] for i in grp["landmark_complete_orig"]])
            rm = np.array([s[i] for i in grp["landmark_complete_resmatch"]])
            st, _, _ = T1.load_result(RR / f"PN1_{arm}_s{seed}.tar")
            cam = RD.thresholds(st, P, 0.0)["cam"]
            a = float(np.mean(bona > 0))
            b = float(K.auc(mor, bona))
            out[f"{arm}_s{seed}"] = dict(
                a_bona_flag_own=a, a_ci=boot(lambda p, n: np.mean(n > 0), mor, bona, rng),
                b_auc_morph_vs_bona=b, b_ci=boot(lambda p, n: K.auc(p, n), mor, bona, rng), verdict=verdict(a, b),
                printed=dict(bona_flag_cam=float(np.mean(bona > cam)), tau_cam=float(cam),
                             morph_miss_own=float(np.mean(mor <= 0)), resmatch_bona_flag_own=float(np.mean(rm > 0)),
                             auc_morph_vs_resmatch_bona=float(K.auc(mor, rm)),
                             bona_median_logit=float(np.median(bona)), morph_median_logit=float(np.median(mor))))
    arms = {}
    for arm in ("A", "B", "Bn", "C"):
        v = [out.get(f"{arm}_s{s}", {}).get("verdict") for s in (401, 402)]
        arms[arm] = v[0] if v[0] is not None and v[0] == v[1] else ("mixed" if None not in v else "incomplete")
    out["arm_verdicts"] = arms
    K.dump(out, K.RES / "tier1" / "hn2.json")
    for k, v in out.items():
        if isinstance(v, dict) and "verdict" in v:
            print(k, round(v["a_bona_flag_own"], 3), round(v["b_auc_morph_vs_bona"], 3), v["verdict"])
    print(arms)


if __name__ == "__main__":
    if not sys.flags.isolated:
        sys.exit("run with python3 -I")
    main()
