"""Signal isolation by paired differences (PD1), GAN family: tables from res_*.json (CSV) and the family verdict.
Run: <spark python> -I src/PD1/gan/pd1_summary.py
"""
import csv, json, pathlib, sys
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import pd1_lib as L

HEADS = ("one-person head O (x2 vs x1)", "two-person head T (x3 vs x1)")


def w(name, rows):
    if not rows:
        return
    with open(L.OUT / name, "w", newline="") as f:
        wr = csv.DictWriter(f, list(rows[0]))
        wr.writeheader()
        wr.writerows(rows)


def r3(x):
    return None if x is None else round(float(x), 4)


def main():
    res = {}
    for bb, kind in L.FEATS:
        p = L.OUT / f"res_{bb}_{kind}.json"
        if p.exists():
            res[(bb, kind)] = json.load(open(p))
    q1, q2, q3, fl, q4, q5, be = [], [], [], [], [], [], []
    readings = {}
    for (bb, kind), r in res.items():
        fn = L.FNAME[(bb, kind)]
        for st, v in r["Q1"].items():
            q1.append(dict(feature=fn, step=st, n_hosts=v["n_hosts"], share=r3(v["share"]), share_lo=r3(v["share_ci"][0]),
                           share_hi=r3(v["share_ci"][1]), proj_auc=r3(v["proj_auc"]), proj_auc_lo=r3(v["proj_auc_ci"][0]),
                           proj_auc_hi=r3(v["proj_auc_ci"][1]), consistent=v["consistent"]))
        for pr, v in r["Q2"]["cosines"].items():
            q2.append(dict(feature=fn, pair=pr, cos=r3(v["cos"]), lo=r3(v["interval"][0]), hi=r3(v["interval"][1]), method=v["method"]))
        for d, v in r["Q2"]["split_half_reliability"].items():
            q2.append(dict(feature=fn, pair=f"{d} | itself (split-half reliability)", cos=r3(v["mean"]), lo=r3(v["pct"][0]),
                           hi=r3(v["pct"][1]), method="split halves (200)"))
        for h in HEADS:
            hr = r["Q3"][h]
            readings[(fn, h)] = hr["reading"]
            for key, v in hr.items():
                if not isinstance(v, dict) or "auc" not in v or key in ("flag_rates", "benchmarks"):
                    continue
                q3.append(dict(feature=fn, head=h, set="G (OOF)", contrast=key.replace("G ", ""), auc=r3(v["auc"]), lo=r3(v["ci"][0]),
                               hi=r3(v["ci"][1]), paired_win=r3(v.get("paired_win")),
                               floor_stat=v.get("floor", {}).get("best"), floor_auc=r3(v.get("floor", {}).get("auc")),
                               excess=r3(v.get("excess_over_floor", {}).get("point")),
                               excess_lo=r3(v.get("excess_over_floor", {}).get("ci", [None])[0]),
                               excess_hi=r3(v.get("excess_over_floor", {}).get("ci", [None, None])[1]),
                               latent_averageness_auc=r3(v.get("latent_averageness_auc", {}).get("auc_closer_to_mean_is_positive"))))
            for frame in ("H raw frame (transfer)", "H aligned frame (transfer, descriptive)"):
                for key, v in hr[frame].items():
                    q3.append(dict(feature=fn, head=h, set=frame, contrast=key, auc=r3(v["auc"]), lo=r3(v["ci"][0]), hi=r3(v["ci"][1]),
                                   paired_win=r3(v.get("paired_win")), floor_stat=v.get("floor", {}).get("best"),
                                   floor_auc=r3(v.get("floor", {}).get("auc")), excess=r3(v.get("excess_over_floor", {}).get("point")),
                                   excess_lo=r3(v.get("excess_over_floor", {}).get("ci", [None])[0]),
                                   excess_hi=r3(v.get("excess_over_floor", {}).get("ci", [None, None])[1]),
                                   latent_averageness_auc=r3(v.get("latent_averageness_auc", {}).get("auc_closer_to_mean_is_positive"))))
            for key, v in hr["flag_rates"].items():
                if isinstance(v, dict) and "rate" in v:
                    fl.append(dict(feature=fn, head=h, softened_set=key, n=v["n"], flagged=v["flagged"], rate=r3(v["rate"]),
                                   cp_lo=r3(v["cp95"][0]), cp_hi=r3(v["cp95"][1]), mean_shift_native_sd=r3(v["mean_shift_in_native_sd"]),
                                   share_above_own_native=r3(v["share_scored_above_own_native"])))
            for cell, v in hr["benchmarks"].items():
                be.append(dict(feature=fn, head=h, variant="none", cell=cell, n_morph=v["n_morph"], n_genuine=v["n_genuine"],
                               auc=r3(v["auc"]), lo=r3(v["ci"][0]), hi=r3(v["ci"][1]), eer=r3(v["eer"]),
                               auc_neutral_only=r3(v["auc_neutral_genuine_only"]), flagged_at_native5=r3(v["morphs_flagged_at_native_5pct"])))
        for vn, vv in r["Q4"].items():
            for h, v in vv.items():
                q4.append(dict(feature=fn, variant=vn, head=h, **{k: (r3(x) if isinstance(x, float) else x) for k, x in v.items()
                                                                  if k not in ("benchmarks", "G_x3_vs_x1_ci", "primary_flag_cp95")},
                               G_x3_vs_x1_lo=r3(v["G_x3_vs_x1_ci"][0]), G_x3_vs_x1_hi=r3(v["G_x3_vs_x1_ci"][1])))
                for cell, b in (v.get("benchmarks") or {}).items():
                    be.append(dict(feature=fn, head=h, variant=vn, cell=cell, n_morph=None, n_genuine=None, auc=r3(b["auc"]),
                                   lo=r3(b["ci"][0]), hi=r3(b["ci"][1]), eer=r3(b["eer"]), auc_neutral_only=None, flagged_at_native5=None))
        for h in HEADS:
            v = r["Q5"][h]
            q5.append(dict(feature=fn, head=h, G_rho_gain_vs_FR_dissim=r3(v["rho_gain_vs_FR_dissimilarity"]), G_lo=r3(v["ci"][0]),
                           G_hi=r3(v["ci"][1]), rises=v["rises"], G_rho_host_gain_vs_latent_dist=r3(v["rho_host_gain_vs_latent_distance_descriptive"]),
                           G_rho_pooled_x2x3_gain_vs_latent_dist=r3(v["rho_pooled_x2_x3_gain_vs_latent_distance_descriptive"]),
                           H_rho_x3_minus_x1=r3(v["H_rho_gain_x3_minus_x1_vs_dissimilarity"]["rho"]),
                           H_lo=r3(v["H_rho_gain_x3_minus_x1_vs_dissimilarity"]["ci"][0]),
                           H_hi=r3(v["H_rho_gain_x3_minus_x1_vs_dissimilarity"]["ci"][1]),
                           H_rho_x3_minus_x1s=r3(v["H_rho_gain_x3_minus_x1s_vs_dissimilarity"]["rho"]),
                           H_s_lo=r3(v["H_rho_gain_x3_minus_x1s_vs_dissimilarity"]["ci"][0]),
                           H_s_hi=r3(v["H_rho_gain_x3_minus_x1s_vs_dissimilarity"]["ci"][1])))
    w("q1_directions.csv", q1)
    w("q2_cosines.csv", q2)
    w("q3_heads.csv", q3)
    w("q3_flag_rates.csv", fl)
    w("q4_trace_subtraction.csv", q4)
    w("q5_dissimilarity.csv", q5)
    w("benchmarks.csv", be)
    prim = readings.get((L.FNAME[("clip", "pool")], HEADS[0]))
    others = [v for (fn, h), v in readings.items() if h == HEADS[0] and fn != L.FNAME[("clip", "pool")]]
    verdict = {"works": "idea works", "fails": "idea fails", "in-between": "mixed"}.get(prim)
    opposite = {"works": "fails", "fails": "works"}.get(prim)
    if opposite and opposite in others:
        verdict = "mixed"
    summ = dict(readings_one_person_head={fn: v for (fn, h), v in readings.items() if h == HEADS[0]},
                readings_two_person_head={fn: v for (fn, h), v in readings.items() if h == HEADS[1]},
                family_verdict=verdict, features_done=[L.FNAME[k] for k in res])
    json.dump(summ, open(L.OUT / "summary.json", "w"), indent=1)
    print(json.dumps(summ, indent=1))


if __name__ == "__main__":
    main()
