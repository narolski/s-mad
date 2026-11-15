"""Signal isolation by paired differences (PD1), cross-family transfer: small tables and fixed readings from the
analysis outputs (res/<feat>.json, res/<feat>_posthoc.json).

  tf_summary.py   -> experiments/PD1_signal-isolation-paired-differences/transfer/{cosines,lofo,probes,infamily,
                     sensitivity,pairwise_posthoc}.csv, readings.json
"""
import csv
import json
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import tf_lib as K  # noqa: E402

FEATS = ("clip_pool", "clip_patch", "dino_pool")


def r3(x):
    return None if x is None else round(float(x), 3)


def write(name, rows):
    p = K.RES / name
    with open(p, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0]))
        w.writeheader()
        w.writerows(rows)
    print("wrote", p, len(rows))


def majority(vals, labels):
    for lab in labels:
        if sum(v == lab for v in vals) >= 2:
            return lab
    return "mixed"


def main():
    K.RES.mkdir(parents=True, exist_ok=True)
    R = {f: json.load(open(K.OUT / "res" / f"{f}.json")) for f in FEATS}
    P = {f: json.load(open(K.OUT / "res" / f"{f}_posthoc.json")) for f in FEATS if (K.OUT / "res" / f"{f}_posthoc.json").exists()}
    cos, lofo, prb, inf, sens, pw = [], [], [], [], [], []
    for f, r in R.items():
        for sp in ("cos_z", "cos_l2"):
            c = r[sp]
            for a in c["names"]:
                for b in c["names"]:
                    if c["names"].index(b) < c["names"].index(a):
                        continue
                    m = c["M"][f"{a} || {b}"]
                    cos.append(dict(feature=f, space=sp[4:], a=a, b=b, cross=r3(m["cross"]),
                                    range_lo=r3(m["range"][0]) if m["range"] else None,
                                    range_hi=r3(m["range"][1]) if m["range"] else None,
                                    disattenuated=r3(m["disatt"]), full=r3(m["full"]),
                                    rel_a=r3(c["reliability"][a]), rel_b=r3(c["reliability"][b])))
        for T in K.FAMS:
            l = r["lofo"][T]
            for hn in ("O", "O_meandir", "T2", "T2_meandir"):
                e = l[hn]
                lofo.append(dict(feature=f, held_out=K.FAMNAME[T], head=hn,
                                 train_hosts=";".join(f"{K.FAMNAME[k]} {v}" for k, v in l["train_hosts"].items()),
                                 test_hosts=l["test_hosts"], C=e.get("C"), auc_x1_x3=r3(e["auc_x1_x3"]),
                                 ci_lo=r3(e["ci"][0]), ci_hi=r3(e["ci"][1]), floor_statistic=l["floor"]["statistic"],
                                 floor_auc=r3(l["floor"]["auc"]), excess=r3(e["excess"]), excess_lo=r3(e["excess_ci"][0]),
                                 excess_hi=r3(e["excess_ci"][1]), share_x3_gt_x1=r3(e["share_x3_gt_x1"]),
                                 primary_flag=r3(e["primary_flag"]),
                                 flags=";".join(f"{k} {v['rate']:.3f}" for k, v in e["flags"].items()),
                                 C_range=";".join(f"{c} {v['auc_x1_x3']:.3f}" for c, v in e.get("C_range", {}).items()),
                                 reading=e.get("reading", "descriptive")))
                if hn == "O":
                    for k, v in e["probes"].items():
                        prb.append(dict(feature=f, held_out=K.FAMNAME[T], head="O (registered)", probe=k,
                                        auc=r3(v["auc"]), ci_lo=r3(v["ci"][0]) if "ci" in v else None,
                                        ci_hi=r3(v["ci"][1]) if "ci" in v else None,
                                        note=(f"100-step flagged at 20-step 5%: {v['flag_100_at_20step_5pct']['rate']:.3f}"
                                              if "flag_100_at_20step_5pct" in v else "")))
                    for k, v in e.get("probes_blank_D", {}).items():
                        prb.append(dict(feature=f, held_out=K.FAMNAME[T], head="O (registered)",
                                        probe="blanked (verifier features, TF32 off) " + k, auc=r3(v["auc"]),
                                        ci_lo=r3(v["ci"][0]), ci_hi=r3(v["ci"][1]), note=""))
            ii = r["infamily"][T]
            for hn in ("O", "T2"):
                e = ii[hn]
                inf.append(dict(feature=f, family=K.FAMNAME[T], head=hn, auc_x1_x3=r3(e["auc_x1_x3"]),
                                ci_lo=r3(e["ci"][0]), ci_hi=r3(e["ci"][1]), x2_vs_x3=r3(e["x2_vs_x3"]),
                                xm_vs_x3=r3(e.get("xm_vs_x3")), primary_flag=r3(e["primary_flag"]),
                                C_per_fold=";".join(str(c) for c in e["C_per_fold"]),
                                lofo_minus_infamily=r3(e["transfer_gap"]["diff"]),
                                gap_lo=r3(e["transfer_gap"]["ci"][0]), gap_hi=r3(e["transfer_gap"]["ci"][1])))
            for sk in ("sens_nopurge", "sens_Lx2only", "sens_unweighted"):
                if sk in r:
                    l2 = r[sk][T]
                    for hn in ("O", "T2", "O_meandir"):
                        e = l2[hn]
                        sens.append(dict(feature=f, variant=sk[5:], held_out=K.FAMNAME[T], head=hn, C=e.get("C"),
                                         train_hosts=";".join(f"{K.FAMNAME[k]} {v}" for k, v in l2["train_hosts"].items()),
                                         auc_x1_x3=r3(e["auc_x1_x3"]), ci_lo=r3(e["ci"][0]), ci_hi=r3(e["ci"][1]),
                                         excess=r3(e["excess"]), primary_flag=r3(e["primary_flag"]),
                                         reading=e.get("reading", "descriptive")))
        if f in P:
            for key, v in P[f]["pairwise"].items():
                Af, T = key.split("->")
                for hn in ("O", "O_meandir", "T2", "T2_meandir"):
                    e = v[hn]
                    pw.append(dict(feature=f, train=K.FAMNAME[Af], held_out=K.FAMNAME[T], head=hn, C=e.get("C"),
                                   train_hosts=v["train_hosts"], auc_x1_x3=r3(e["auc_x1_x3"]), ci_lo=r3(e["ci"][0]),
                                   ci_hi=r3(e["ci"][1]), excess=r3(e["excess"]), primary_flag=r3(e["primary_flag"]),
                                   reading_posthoc=e["reading_posthoc"]))
            for T, pr in P[f]["meandir_probes"].items():
                for k, v in pr.items():
                    prb.append(dict(feature=f, held_out=K.FAMNAME[T], head="mean direction (post hoc)", probe=k,
                                    auc=r3(v["auc"]), ci_lo=r3(v["ci"][0]) if "ci" in v else None,
                                    ci_hi=r3(v["ci"][1]) if "ci" in v else None,
                                    note=(f"100-step flagged at 20-step 5%: {v['flag_100_at_20step_5pct']['rate']:.3f}"
                                          if "flag_100_at_20step_5pct" in v else "")))
    write("cosines.csv", cos)
    write("lofo.csv", lofo)
    write("probes.csv", prb)
    write("infamily.csv", inf)
    if sens:
        write("sensitivity.csv", sens)
    if pw:
        write("pairwise_posthoc.csv", pw)
    # fixed readings
    rd = {"cosines (z-space, registered)": {}, "lofo (registered)": {}}
    for st in ("M", "P", "W"):
        per = {f: R[f]["readings_cos"]["cos_z"][st]["overall"] for f in FEATS}
        simple = ["one shared direction" if v == "one shared direction" else
                  "no shared direction" if v == "no shared direction" else "partly shared" for v in per.values()]
        rd["cosines (z-space, registered)"][st] = dict(
            per_feature=per, pairs={f: {k: v["reading"] for k, v in R[f]["readings_cos"]["cos_z"][st]["pairs"].items()}
                                    for f in FEATS},
            across_features=majority(simple, ("one shared direction", "no shared direction", "partly shared")))
    per_T = {}
    for T in K.FAMS:
        per = {f: R[f]["lofo"][T]["O"]["reading"] for f in FEATS}
        per_T[T] = majority(list(per.values()), ("transfers", "fails", "mixed"))
        rd["lofo (registered)"][K.FAMNAME[T]] = dict(per_feature=per, family_reading=per_T[T])
    v = list(per_T.values())
    ans = "yes" if all(x == "transfers" for x in v) else "no" if sum(x == "fails" for x in v) >= 2 else \
        "partly (" + ", ".join(f"{K.FAMNAME[T]}: {per_T[T]}" for T in K.FAMS) + ")"
    rd["answer (3), registered rule"] = ans
    json.dump(rd, open(K.RES / "readings.json", "w"), indent=1)
    print(json.dumps(rd, indent=1))


if __name__ == "__main__":
    main()
