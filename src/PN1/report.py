"""PN1: compact tables from the read JSONs (tier 0: tier0/<bb>_<arm>_s<seed>.json; tier 1: tier1/<arm>_s<seed>.json).
  python3 -I report.py tier0 | tier1   -> experiments/PN1_.../<tier>_tables.md and <tier>_key.csv
"""
import csv
import json
import pathlib
import sys

RES = pathlib.Path("/home/narolski/smad-next/experiments/PN1_protocol-network-first-tests")


def g(d, *ks):
    for k in ks:
        if not isinstance(d, dict) or k not in d:
            return None
        d = d[k]
    return d


def f3(x):
    return "n/a" if x is None or isinstance(x, str) else f"{x:.3f}"


def pct(x):
    return "n/a" if x is None else f"{100 * x:.1f}"


def ci(d):
    if not isinstance(d, dict) or d.get("auc") is None:
        return "n/a"
    return f"{d['auc']:.3f} [{d['lo']:.3f}, {d['hi']:.3f}]"


def key_row(R):
    fx = R["fixed"]
    row = {}
    for k in ("R2w_vs_R4_opencv", "R2w4_vs_R4_opencv", "R2w_vs_R4_facemorpher", "R2w4_vs_R4_facemorpher"):
        row[f"a {k}"] = ci(R["a"][k])
        row[f"a {k} excess"] = (f"{R['a'][k]['excess']:+.3f} [{R['a'][k]['excess_lo']:+.3f}, {R['a'][k]['excess_hi']:+.3f}] "
                                f"best={R['a'][k]['best_stat']} {R['a'][k]['best_stat_auc']:.3f}"
                                if isinstance(R["a"][k].get("excess"), float) else "n/a")
    for k in R["b"]:
        row[f"b {k}"] = ci(R["b"][k])
    c = R["c"]["R0_to_R0_61"]
    row["c shift R0->R0_61 (SD)"] = f"{c['shift_sd']:+.3f} [{c['lo']:+.3f}, {c['hi']:+.3f}]" if "shift_sd" in c else "n/a"
    c2 = R["c"]["R0_to_R0_112"]
    row["c shift R0->R0_112 (SD)"] = f"{c2['shift_sd']:+.3f} [{c2['lo']:+.3f}, {c2['hi']:+.3f}]" if "shift_sd" in c2 else "n/a"
    row["d H1 AUC"] = ci(R["d"])
    for k in ("OpenCV_native", "OpenCV_e7", "Webmorph_native", "Webmorph_e7"):
        e = R["e"][k]
        row[f"e MAD22 {k} EER%"] = f"{e['eer_eer']:.2f} [{e['eer_lo']:.2f}, {e['eer_hi']:.2f}]" if "eer_eer" in e else "n/a"
    for th in ("own", "cam", "dev"):
        t = fx[th]
        for p in ("T_R0", "T_R0_61", "T_R0_112", "FRLL_bona_native", "FRLL_bona_jpeg70", "FRLL_bona_jpeg50",
                  "FRLL_bona_resample50", "FRLL_bona_blur1", "MAD22_OpenCV_e7", "MAD22_Webmorph_e7",
                  "FRLL_amsl_e7", "FRLL_opencv_e7", "H1_bona",
                  "T_R2w_opencv", "T_R2w4_opencv", "T_R2w_opencv_61", "T_R3_opencv", "T_R3m_opencv",
                  "T_R4_opencv", "T_R4_facemorpher", "T_R4_opencv_61", "MAD22_OpenCV_morph", "MAD22_Webmorph_morph",
                  "H1_morph"):
            x = t.get(p)
            kind = {"genuine_flag": "flag", "single_placement": "placed", "attack_miss": "miss"}.get(x["kind"]) if x else ""
            row[f"{th} {kind} {p} %"] = f"{pct(x['rate'])} ({x['k']}/{x['n']})" if x else "n/a"
        row[f"{th} family-mean miss (gating) %"] = pct(g(t, "_family_mean_miss_gating", "mean"))
    row["tau_cam binding pool"] = R["thresholds"].get("cam_binding")
    row["tau_dev binding pool"] = R["thresholds"]["dev_binding"]
    row["tau_dev pools missing"] = ",".join(R["thresholds"]["dev_pools_missing"]) or "none"
    if "V" in fx:
        row["tau_V (AF0 val photos only): flag T_R0_61 / miss family-mean %"] = (
            f"{pct(fx['V'].get('T_R0_61', {}).get('rate'))} / {pct(g(fx['V'], '_family_mean_miss_gating', 'mean'))}")
    dl = R.get("dev_ladder", {})
    for k in ("a_R2w_vs_R4_opencv", "a_R2w4_vs_R4_opencv", "b_R0_61_vs_R4_opencv", "g3_R2w_vs_R4_61_opencv",
              "V_u50_vs_V_zero", "V_u50_vs_V_photo"):
        row[f"dev-ladder/AF0-val {k}"] = ci(dl.get(k))
    for k in ("c_R0_to_R0_61", "c_R0_to_R0_112"):
        c3 = dl.get(k, {})
        row[f"dev-ladder {k} (SD)"] = f"{c3['shift_sd']:+.3f} [{c3['lo']:+.3f}, {c3['hi']:+.3f}]" if "shift_sd" in c3 else "n/a"
    if "marks" in R and "NU_a_violations_gt10pct_own" in R["marks"]:
        m = R["marks"]
        row["K0 (R2w61 vs R4 < 0.60)"] = str(m.get("K0_b_R2w61_lt_0.60"))
        row["2x2"] = (f"min(g1..g3) {m['2x2_min_g1_g3']:.3f} pass {m['2x2_pass']} kill-set {m['2x2_kill_this_feature_set']}"
                      if "2x2_min_g1_g3" in m else m.get("2x2", ""))
        for th in ("own", "cam", "dev"):
            row[f"NU-a violations >10% ({th})"] = "; ".join(f"{a}={b}" for a, b in m[f"NU_a_violations_gt10pct_{th}"]) or "none"
            row[f"NU-d miss R4_61 ({th})"] = str(m.get(f"NU_d_miss_R4_61_{th}"))
        st = m["storage"]
        row["P-c (61.2 px: shift<=0.3 SD, <=10% at own and cam)"] = f"{st['P-c']['pass_']} {st['P-c']['flag']}"
        row["P-c2 (112.7 px)"] = f"{st['P-c2']['pass_']} shift {f3(st['P-c2']['shift_sd'])} {st['P-c2']['flag']}"
        row["P-c2 kernels / other E7 strengths <=10%"] = str(st["P-c2_kernels"]["pass_"])
    if "marks" in R and "P-a" in R["marks"]:
        m = R["marks"]
        for k in ("P-a", "P-b", "P-b_middle", "P-c", "P-c2", "P-d", "P-e", "P-f", "kill_parts"):
            row[f"mark {k}"] = str(m.get(k))
    if "gaps" in R:
        for k, v in R["gaps"].items():
            row[f"gap {k}"] = f"{v['gap']:+.2f} (train {v['train_mean']:+.2f}, held {v['heldout_mean']:+.2f})"
    return row


def main(tier):
    d = RES / tier
    files = sorted(f for f in d.glob("*.json") if "smoke" not in f.name and "summary" not in f.name)
    rows = {f.stem: key_row(json.load(open(f))) for f in files}
    keys = list(next(iter(rows.values())).keys()) if rows else []
    with open(RES / f"{tier}_key.csv", "w", newline="") as fh:
        w = csv.writer(fh)
        w.writerow(["read"] + list(rows))
        for k in keys:
            w.writerow([k] + [rows[n].get(k, "") for n in rows])
    named = [n for n in rows if n.endswith("_s401")]
    md = [f"# PN1 {tier}: key reads (named seed 401; all seeds in {tier}_key.csv)", "",
          "| read | " + " | ".join(named) + " |", "|---|" + "---|" * len(named)]
    for k in keys:
        md.append(f"| {k} | " + " | ".join(rows[n].get(k, "") for n in named) + " |")
    (RES / f"{tier}_tables.md").write_text("\n".join(md) + "\n")
    print("\n".join(md))


if __name__ == "__main__":
    main(sys.argv[1])
