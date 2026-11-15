"""PD1 landmark: compact CSV tables and the family verdict from the per-feature JSON files in RES.

  python3 -I summarize.py   -> RES/{q1,q3q4,flags,q2_readings,q5,bench}.csv, RES/verdict.json, prints markdown rows
"""
import csv
import json
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import pd1_common as K  # noqa: E402

FEATN = {"clip_cls": "CLIP class token", "clip_mean": "CLIP mean patch token", "dino_mean": "DINOv3 mean patch token",
         "stats27": "27 simple statistics (control)"}


def f3(x):
    return "" if x is None else f"{x:.3f}"


def ci(c):
    return "" if not c or c[0] is None else f"[{c[0]:.3f}, {c[1]:.3f}]"


def wcsv(name, rows):
    if not rows:
        return
    with open(K.RES / name, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0]))
        w.writeheader()
        w.writerows(rows)


def main():
    feats = [f for f in K.FEATS + K.CONTROLS if (K.RES / f"readings_{f}.json").exists()]
    q1r, q3r, flr, q2r, q5r, ber = [], [], [], [], [], []
    verdicts = {}
    for f in feats:
        q1 = json.load(open(K.RES / f"q1_{f}.json"))
        for k, v in q1.items():
            q1r.append(dict(feature=f, engine=v["engine"], step=v["step"], a=v["a"], b=v["b"], share=v["share"],
                            share_ci=ci(v["share_ci"]), auc=v["auc"], auc_ci=ci(v["auc_ci"]),
                            consistent=v["consistent"]))
        c = json.load(open(K.RES / f"q3q4_contrasts_{f}.json"))["contrasts"]
        for k, v in c.items():
            q3r.append(dict(feature=f, variant=v["variant"], head=v["head"], train_engine=v["train_engine"],
                            score_engine=v["score_engine"], contrast=v["contrast"], auc=v["auc"],
                            auc_ci=ci(v["auc_ci"]), paired_share=v["paired_share_b_above_a"],
                            floor_stat=v.get("floor_stat", ""), floor_auc=v.get("floor_auc", ""),
                            excess=v.get("excess", ""), excess_ci=ci(v.get("excess_ci")),
                            lapvar_folded=f3(None if v.get("lapvar_auc") is None else max(v["lapvar_auc"],
                                                                                       1 - v["lapvar_auc"])),
                            minus_two=v.get("minus_two_person_head", ""),
                            minus_two_ci=ci(v.get("minus_two_person_head_ci"))))
        ex = json.load(open(K.RES / f"external_{f}.json"))
        for hk, sets in ex.items():
            variant, head, eng = hk.split("|")
            for s, r in sets.items():
                row = dict(feature=f, variant=variant, head=head, train_engine=eng, set=s)
                for m, val in r.items():
                    if isinstance(val, dict):
                        row[m] = f3(val["rate"]) + " " + ci(val["ci"]) + f" ({val['k']}/{val['n']})"
                    else:
                        row[m] = val
                if any(x in s for x in ("FRLL-Morphs", "MAD22")):
                    ber.append(row)
                else:
                    flr.append(row)
        q2 = json.load(open(K.RES / f"q2_{f}.json"))
        for eng, r in q2["readings"].items():
            q2r.append(dict(feature=f, engine=eng, **r))
        q5 = json.load(open(K.RES / f"q5_{f}.json"))
        for k, v in q5.items():
            q5r.append(dict(feature=f, key=k, **{kk: json.dumps(vv) if isinstance(vv, (list, dict)) else vv
                                                for kk, vv in v.items()}))
        verdicts[f] = json.load(open(K.RES / f"readings_{f}.json"))
    wcsv("q1.csv", q1r)
    wcsv("q3q4.csv", q3r)
    allk = sorted({k for r in flr for k in r}, key=lambda x: (x not in ("feature", "variant", "head", "train_engine",
                                                                       "set"), x))
    wcsv("external_sets.csv", [{k: r.get(k, "") for k in allk} for r in flr])
    allk = sorted({k for r in ber for k in r}, key=lambda x: (x not in ("feature", "variant", "head", "train_engine",
                                                                       "set"), x))
    wcsv("bench.csv", [{k: r.get(k, "") for k in allk} for r in ber])
    allk = sorted({k for r in q2r for k in r}, key=lambda x: (x not in ("feature", "engine"), x))
    wcsv("q2_readings.csv", [{k: r.get(k, "") for k in allk} for r in q2r])
    allk = sorted({k for r in q5r for k in r}, key=lambda x: (x not in ("feature", "key"), x))
    wcsv("q5.csv", [{k: r.get(k, "") for k in allk} for r in q5r])
    fam = {}
    for v in ("none", "soft", "pipe", "both"):
        vs = [verdicts[f][v]["verdict"] for f in feats if v in verdicts[f] and f in K.FEATS]
        if len(vs) == 3:
            fam[v] = ("idea works" if vs.count("works") >= 2 else "idea fails" if vs.count("fails") >= 2 else "mixed")
    json.dump(dict(per_feature=verdicts, family=fam), open(K.RES / "verdict.json", "w"), indent=1)
    print(json.dumps(dict(family=fam, per_feature={f: {v: r["verdict"] for v, r in verdicts[f].items()}
                                                   for f in feats}), indent=1))


if __name__ == "__main__":
    main()
