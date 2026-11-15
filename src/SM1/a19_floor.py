"""SM1 A18 post hoc addendum (labelled post hoc; A19 note): the network's X20-vs-SAME20 increment over an extended floor
that adds the noise-map similarity of the two inverted noise maps (FZ2 amendment 2 features: band cosines c0-c3,
8x8 low-pass cosine) and the semantic-code cosine. Codes: DG1 `*_codes.tar` of shards 2-6 (local) and 0-1 (fetched
from Athena 13 Nov); shard 7's codes are lost, so the test read is shard 6 only.
Reads (2-seed mean 401, 402; 3-seed mean as stability):
  (i)  cross-fit on shard-6 partner cycles (hn2_incr.incremental) with the floor F, F + band/low-pass, F + band/low-pass
       + semantic-code cosine;
  (ii) floor fit on the training shards (0-5, and 2-5 for comparison) with the extended features, applied to shard 6;
       its score and the network logit combined by logistic regression cross-fit on shard-6 cycles; ΔAUC over the
       floor score alone.

  python3 -I a19_floor.py -> RES/a19_floor.json
"""
import csv
import hashlib
import io
import json
import pathlib
import sys
import tarfile

import numpy as np

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
sys.path.insert(0, "/home/narolski/smad-next/src/FZ2")
import sm1_common as K  # noqa: E402
import hn2_incr as I  # noqa: E402
from fz2_amend2 import feats, cos  # noqa: E402

TARS = {k: f"/mnt/t7/smad_next/DG1/rented_results/DG1_addon_s{k}_codes.tar" for k in range(2, 7)}
TARS.update({k: f"/mnt/t7/smad_next/SM1/dg1_codes01/DG1_addon_s{k}_codes.tar" for k in (0, 1)})


def codes():
    out = {}
    for k, t in TARS.items():
        assert hashlib.sha256(open(t, "rb").read()).hexdigest() == open(t + ".sha256").read().split()[0], t
        with tarfile.open(t) as tf:
            m = [x for x in tf.getmembers() if x.name.endswith("codes.npz")][0]
            z = np.load(io.BytesIO(tf.extractfile(m).read()))
        ix = {n: i for i, n in enumerate(z["names"])}
        for j in csv.DictReader(open(f"/mnt/t7/smad_next/DG1/addon_jobs/addon_s{k}.csv")):
            if j["pool"] not in ("AO_X20", "AO_SAME20") or j["src_a"] not in ix or j["src_b"] not in ix:
                continue
            a, b = z["xT"][ix[j["src_a"]]].astype(np.float64), z["xT"][ix[j["src_b"]]].astype(np.float64)
            f = feats(a, b)
            f["zcos"] = cos(z["z"][ix[j["src_a"]]].astype(np.float64), z["z"][ix[j["src_b"]]].astype(np.float64))
            out[(j["pool"][3:], j["host"])] = f
    return out


def lr_fit(X, y):
    from sklearn.linear_model import LogisticRegression
    mu, sd = X.mean(0), X.std(0) + 1e-12
    m = LogisticRegression(max_iter=5000).fit((X - mu) / sd, y)
    return lambda Z: m.decision_function((Z - mu) / sd)


def main():
    if not sys.flags.isolated:
        sys.exit("run with python3 -I")
    C = codes()
    items = [r for r in csv.DictReader(open("/mnt/t7/smad_next/FZ2/read_addon_items.csv")) if r["key"] in ("X20", "SAME20")]
    dropped = set(json.load(open(K.OUT / "hn2/lists.json"))["dropped_crossing_X20"])

    def fvec(r, c, ext):
        f = [c["theta"], np.log(float(r["lapvar_box"])), np.log(float(r["png_bytes"])), float(r["asym_box"]), float(r["d"])]
        if ext >= 1:
            f += [c[k] for k in ("c0", "c1", "c2", "c3", "lp8")]
        if ext >= 2:
            f += [c["zcos"]]
        return f
    net = {}
    for s in (401, 402, 403):
        z = np.load(K.OUT / f"results_rented/hn2/HN2_RS_s{s}/hn2test/scores_eval.npz")
        p = np.clip(z["score_noTTA"].astype(float), 1e-7, 1 - 1e-7)
        net[s] = dict(zip([str(i) for i in z["id"]], np.log(p / (1 - p))))
    rows = I.test_rows()
    itm = {r["id"]: r for r in items}
    s6 = []
    for r in rows:
        a = itm[r["item_id"]]
        c = C.get((a["key"], a["host"]))
        if c is not None and a["list"] == "addon_s6":
            assert abs(c["theta"] - r["f"][0]) < 1e-6
            s6.append(dict(r, a=a, c=c))
    res = dict(n_shard6=len(s6), n_cycles=len({r["cycle"] for r in s6}))
    for ext in (0, 1, 2):
        rr = [dict(r, f=fvec(r["a"], r["c"], ext)) for r in s6]
        per = [I.incremental(rr, net[s]) for s in (401, 402, 403)]
        sm2, sm3 = I.summarise(per[:2]), I.summarise(per)
        res[f"crossfit_ext{ext}"] = dict(F=sm2["F"], F_plus=sm2["F_plus"], dAUC_2seed=sm2["dAUC_over_F"],
                                         dAUC_3seed=sm3["dAUC_over_F"], net_raw=sm2["score_raw_auc"])
        print("crossfit ext", ext, sm2["F"]["mean"], sm2["F_plus"]["mean"], sm2["dAUC_over_F"], sm3["dAUC_over_F"]["mean"], flush=True)
    for name, shards in (("train0to5", range(6)), ("train2to5", range(2, 6))):
        tr = [r for r in items if r["list"] in {f"addon_s{k}" for k in shards} and r["id"] not in dropped
              and (r["key"], r["host"]) in C]
        Xtr = np.array([fvec(r, C[(r["key"], r["host"])], 2) for r in tr])
        ytr = np.array([1 if r["key"] == "X20" else 0 for r in tr])
        fl = lr_fit(Xtr, ytr)
        fs = {r["id"]: float(fl(np.array([fvec(r["a"], r["c"], 2)]))[0]) for r in s6}
        per = []
        for s in (401, 402, 403):
            rr = [dict(r, f=[fs[r["id"]], fs[r["id"]]]) for r in s6]   # duplicated column: incremental() also builds F[:, 1:]
            per.append(I.incremental(rr, net[s]))
        sm2, sm3 = I.summarise(per[:2]), I.summarise(per)
        fsa = np.array([fs[r["id"]] for r in s6]); y6 = np.array([r["y"] for r in s6])
        import sm1_stats as S
        res[f"floor_{name}"] = dict(n_train=len(tr), floor_auc_shard6=round(float(S.wauc(fsa[y6 == 1], fsa[y6 == 0],
                                    np.ones((1, (y6 == 1).sum())), np.ones((1, (y6 == 0).sum())))[0]), 4),
                                    combined=sm2["F_plus"], dAUC_2seed=sm2["dAUC_over_F"], dAUC_3seed=sm3["dAUC_over_F"])
        print(name, res[f"floor_{name}"], flush=True)
    res["note"] = "post hoc (A18 review F1 / A19 addendum); shard 6 only (shard 7 codes lost)"
    json.dump(res, open(K.RES / "a19_floor.json", "w"), indent=1)


if __name__ == "__main__":
    main()
