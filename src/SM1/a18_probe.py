"""SM1 A18 parallel arm (zero GPU): linear probe on the existing frozen CLIP (clip_mad) and DINOv2 features of the DG1
add-on shards (`/mnt/t7/smad_next/FZ2/results/dgx/out/<feat>_addon_s{0..7}.npz`).
Train: X20 (1) vs SAME20 (0) of shards 0-5 (X20 rows whose partner crosses to the test side are dropped, as in
hn2_lists.py); logistic regression on standardised features (sklearn defaults, C = 1, max_iter 5000). Score = the probe's
decision value on the test-shard rows. Read: the A18 incremental test over the fixed floor (hn2_incr.py), all rows and
without flagged rows.

  python3 -I a18_probe.py -> RES/a18_probe.json
"""
import csv
import json
import pathlib
import sys

import numpy as np

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import sm1_common as K  # noqa: E402
import hn2_incr as I  # noqa: E402

FD = pathlib.Path("/mnt/t7/smad_next/FZ2/results/dgx/out")


def main():
    if not sys.flags.isolated:
        sys.exit("run with python3 -I")
    from sklearn.linear_model import LogisticRegression
    dropped = set(json.load(open(K.OUT / "hn2/lists.json"))["dropped_crossing_X20"])
    items = [r for r in csv.DictReader(open("/mnt/t7/smad_next/FZ2/read_addon_items.csv")) if r["key"] in ("X20", "SAME20")]
    train = [r for r in items if r["list"] in {f"addon_s{k}" for k in range(6)} and r["id"] not in dropped]
    test_map = {f"hn2:{r['key']}:{r['host']}": r["id"] for r in items if r["list"] in ("addon_s6", "addon_s7")}
    res = {}
    for feat in ("clip_mad", "dinov2"):
        F = {}
        for k in range(8):
            z = np.load(FD / f"{feat}_addon_s{k}.npz", allow_pickle=False)
            F.update(zip([str(i) for i in z["id"]], z["feat"].astype(np.float64)))
        Xtr = np.stack([F[r["id"]] for r in train])
        ytr = np.array([1 if r["key"] == "X20" else 0 for r in train])
        mu, sd = Xtr.mean(0), Xtr.std(0) + 1e-12
        m = LogisticRegression(max_iter=5000).fit((Xtr - mu) / sd, ytr)
        res[feat] = dict(n_train=len(ytr), n_train_X=int(ytr.sum()))
        for tag, drop in (("all", False), ("unflagged", True)):
            rows = I.test_rows(drop_flagged=drop)
            sc = {r["id"]: float(m.decision_function(((F[test_map[r["id"]]] - mu) / sd)[None])[0]) for r in rows}
            o = I.summarise([I.incremental(rows, sc)])
            o["verdict"] = I.verdict(o["dAUC_over_F"])
            res[feat][tag] = o
            print(feat, tag, "raw", o["score_raw_auc"], "F", o["F"]["mean"], "F+", o["F_plus"]["mean"], "dAUC", o["dAUC_over_F"],
                  "Fimg", o["Fimg"]["mean"], "dAUC_img", o["dAUC_over_Fimg"], o["verdict"], flush=True)
    res["note"] = "A18 parallel arm (frozen-feature probe), registered with A18; development data only"
    json.dump(res, open(K.RES / "a18_probe.json", "w"), indent=1)


if __name__ == "__main__":
    main()
