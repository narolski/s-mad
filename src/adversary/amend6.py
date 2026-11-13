"""ADV amendment 6: same-data shortcut learner for AB1 batch C (train_SpV, train_BN; AB1 amendment 7, 06a2351).
Summary AUCs and flag shares on every development contrast (run_floors transfer, unchanged) plus per-row scores on
sel360 and on the native S4 / S3 / S0 splice rows of the 80 test hosts clean of development (splice80).
The list hashes are checked against AB1's pins.sha256 before fitting. No network score is read. python3 -I amend6.py"""
import csv
import hashlib
import json
import sys
import types

import numpy as np

sys.path.insert(0, "/home/narolski/smad-next/src/adversary")
import contrasts as C  # noqa: E402
import floor as FL  # noqa: E402
import run_floors as RF  # noqa: E402

AB1PINS = "/home/narolski/smad-next/experiments/AB1_protocol-ablation-and-replication/pins.sha256"
CLEAN = "/mnt/t7/smad_next/DATA/overlap/test_hosts_clean_of_dev.csv"


def check_hashes():
    pinned = {line.split()[1]: line.split()[0] for line in open(AB1PINS) if line.strip()}
    for arm in ("SpV", "BN"):
        p = str(C.TRAIN[arm])
        h = hashlib.sha256(open(p, "rb").read()).hexdigest()
        assert h == C.TRAIN_SHA[arm] == pinned.get(p), (arm, h[:16], pinned.get(p, "")[:16])
    return {a: C.TRAIN_SHA[a] for a in ("SpV", "BN")}


def main():
    hs = check_hashes()
    RF.cmd_transfer(types.SimpleNamespace(only=["SpV", "BN"]))
    clean = {r["host"] for r in csv.DictReader(open(CLEAN))}
    sel = {r["id"] for r in csv.DictReader(open(RF.FDIR / "sel360_rows.csv"))}
    ri = {r["id"]: int(r["component"]) for r in csv.DictReader(open(RF.FDIR / "ri_R4_vs_R3_heldout.csv"))}
    man = C.rows(C.AB1X)
    spl = [r for r in man if r["fam"] == "splice" and r["role"] == "test" and r["rung"] in ("S4", "S3", "S0")
           and r["host"] in clean]
    spl_rows = [(r["id"], C.resolve(r["path"]), int(r["label"]), C.persons(r)) for r in spl]
    spl_comp = FL.components([p for *_, p in spl_rows])
    rung = {r["id"]: r["rung"] for r in spl}
    sets = {"sel360": ([r for r in C.build("ri_R4_vs_R3") if r[0] in sel], None),
            "splice80": (spl_rows, {i: int(c) for (i, *_), c in zip(spl_rows, spl_comp)})}
    for arm in ("SpV", "BN"):
        T = C.train_rows(arm)
        rl = [(r["id"], C.resolve(r["path"]), int(r["label"]), C.train_persons(r)) for r in T]
        X, nm = RF.X_of(rl)
        y = np.array([l for _, _, l, _ in rl])
        Xc, _, keep = FL._clean(X, X[:1])
        med = np.nanmedian(np.where(np.isfinite(X), X, np.nan), 0)
        models = {k: FL._model(k).fit(Xc, y) for k in ("logreg", "gbt")}
        out, summ = [], {}
        for sname, (rows_, comp) in sets.items():
            Z, _ = RF.X_of(rows_)
            Z = np.where(np.isfinite(Z), Z, med)[:, keep]
            lr = models["logreg"].decision_function(Z)
            gb = models["gbt"].predict_proba(Z)[:, 1]
            yy = np.array([l for _, _, l, _ in rows_])
            ids = [i for i, *_ in rows_]
            if sname == "splice80":
                m43 = np.array([rung[i] in ("S4", "S3") for i in ids])
                summ[sname] = dict(n=len(rows_), S4_vs_S3=dict(logreg=FL.auc(lr[m43], yy[m43]), gbt=FL.auc(gb[m43], yy[m43])),
                                   flag_logreg={k: float(np.mean(lr[[rung[i] == k for i in ids]] > 0)) for k in ("S4", "S3", "S0")},
                                   flag_gbt={k: float(np.mean(gb[[rung[i] == k for i in ids]] > 0.5)) for k in ("S4", "S3", "S0")})
            else:
                summ[sname] = dict(n=len(rows_), logreg=FL.auc(lr, yy), gbt=FL.auc(gb, yy))
            for k, i in enumerate(ids):
                c = comp[i] if comp else ri[i]
                out.append([sname, i, rung.get(i, ""), int(yy[k]), c, repr(float(lr[k])), repr(float(gb[k]))])
        with open(RF.FDIR / f"transfer_{arm}_rows.csv", "w", newline="") as f:
            w = csv.writer(f)
            w.writerow(["set", "id", "rung", "label", "component", "logreg", "gbt"])
            w.writerows(out)
        (RF.FDIR / f"transfer_{arm}_rows_summary.json").write_text(json.dumps(dict(arm=arm, list_sha256=hs[arm],
                                                                                    summary=summ), indent=1))
        print(arm, json.dumps(summ), flush=True)


if __name__ == "__main__":
    if not sys.flags.isolated:
        sys.exit("run with python3 -I")
    main()
