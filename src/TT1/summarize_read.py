"""Threshold transfer on unseen genuine sources (TT1): tables from the registered reader's JSON (no new statistic).
  python3 -I summarize_read.py READ.json OUT.md"""
import json
import sys

SRC = ["replay_attack", "msu_mfsd", "oulu_npu", "casia_fasd", "lfw", "calfw", "cfp_ff", "agedb_30"]
FAM = ["replay_attack", "msu_mfsd", "oulu_npu", "casia_fasd", "lfw_calfw", "cfp_ff", "agedb_30"]
NETS = [f"PN1_{a}_s{s}" for a in ("A", "B", "Sb", "Bn", "C", "Bv") for s in (401, 402)]


def f(x, d=3):
    return "n/a" if x is None else f"{x:.{d}f}"


def main():
    d = json.load(open(sys.argv[1]))
    R, V = d["nets"], d["verdicts"]
    global NETS
    NETS = [n for n in NETS if n in R]
    L0 = [f"Excluded (failed platform gate, TT1-D3): {', '.join(d.get('excluded_failed_platform_gate', [])) or 'none'}; "
          "every read that needs them is not available; Bn_s402 is printed alone (one seed)."]
    L = ["# TT1 registered reading: tables", "", f"Source: `{sys.argv[1]}`; registration {d['registration']}.", ""] + L0 + [""]
    L += ["## R1. Own-rule flag share (logit > 0) per source, primary pool U_p; [person-bootstrap 95%, inflated for packs]", "",
          "| Network | R_cam | R_ffhq | " + " | ".join(SRC) + " |", "|---" * (len(SRC) + 3) + "|"]
    for n in NETS:
        r = R[n]["pools"]
        cells = [f"{f(r['U:' + s]['flag'])} [{f(r['U:' + s]['flag_boot'][0])}, {f(r['U:' + s]['flag_boot'][1])}]" for s in SRC]
        L.append(f"| {n[4:]}{' (one seed)' if n.startswith('PN1_Bn') else ''} | {f(r['R_cam']['flag'])} | {f(r['R_ffhq']['flag'])} | " + " | ".join(cells) + " |")
    L += ["", "## R1. Family flag share (TT-H1 interval)", "", "| Network | " + " | ".join(FAM) + " |", "|---" * (len(FAM) + 1) + "|"]
    for n in NETS:
        r = R[n]
        L.append(f"| {n[4:]} | " + " | ".join(f"{f(r['fam_flag'][x])} [{f(r['fam_flag_ci'][x][0])}, {f(r['fam_flag_ci'][x][1])}]" for x in FAM) + " |")
    for key, title in (("a", "R3(a) AUC unseen source vs R_cam"), ("b", "R3(b) AUC unseen source vs R_ffhq"),
                       ("c", "R3(c) AUC unseen source vs border-matched R_cam"), ("g", "R3(g) AUC unseen source vs crop-geometry-matched R_cam")):
        L += ["", f"## {title} (* = floor-tied)", "", "| Network | " + " | ".join(SRC) + " |", "|---" * (len(SRC) + 1) + "|"]
        for n in NETS:
            a = R[n]["auc"]
            L.append(f"| {n[4:]} | " + " | ".join(f(a[s][key]["auc"]) + ("*" if a[s][key]["floor_tied"] else "") for s in SRC) + " |")
    L += ["", "## R3(d), R3(e), R3(f): border-only and geometry-only on reference photos", "",
          "| Network | d (R_ffhq^border vs R_ffhq) | e min-max over families | f g224 | f g112 |", "|---|---|---|---|---|"]
    for n in NETS:
        a = R[n]["auc"]
        e = [a["e_cam_border"][x]["auc"] for x in FAM]
        L.append(f"| {n[4:]} | {f(a['d_ffhq_border']['auc'])} | {f(min(e))}-{f(max(e))} | {f(a['f_geo']['g224']['auc'])} | {f(a['f_geo']['g112']['auc'])} |")
    L += ["", "## Scale: floor, u, R_cam and FFHQ medians, tau_cam", "",
          "| Network | floor | R_cam median | R_cam floor share | R_ffhq median | u | tau_cam |", "|---|---|---|---|---|---|---|"]
    for n in NETS:
        r = R[n]
        L.append(f"| {n[4:]} | {f(r['floor'])} | {f(r['pools']['R_cam']['median'])} | {f(r['pools']['R_cam']['floor_share'])} | "
                 f"{f(r['pools']['R_ffhq']['median'])} | {f(r['u'])} | {f(r['tau_cam'])} |")
    L += ["", "## R4(a) within-pack Spearman rho(logit, log sharpness) (* = floor-tied)", "", "| Network | lfw | calfw | cfp_ff | agedb_30 | antispoof pooled |", "|---|---|---|---|---|---|"]
    for n in NETS:
        r4 = R[n]["r4"]
        L.append(f"| {n[4:]} | " + " | ".join(f"{f(r4[p]['rho'])} [{f(r4[p]['rho_ci'][0])}, {f(r4[p]['rho_ci'][1])}]" + ("*" if r4[p]["floor_tied"] else "")
                                         for p in ("lfw", "calfw", "cfp_ff", "agedb_30", "antispoof_pooled")) + " |")
    L += ["", "## R4(c) leave-one-family-out error e_f (units of u)", "", "| Network | " + " | ".join(FAM) + " |", "|---" * (len(FAM) + 1) + "|"]
    for n in NETS:
        lo = R[n]["r4"]["lofo"]
        L.append(f"| {n[4:]} | " + " | ".join(f"{f(lo[x]['e_u'], 2)} [{f(lo[x]['ci'][0], 2)}, {f(lo[x]['ci'][1], 2)}]" for x in FAM) + " |")
    L += ["", "## R5 arm summary", "", "| Network | F̄ | F̄ without MSU | F_max | S_F | Ā | S_A |", "|---|---|---|---|---|---|---|"]
    for n in NETS:
        r5 = R[n]["r5"]
        L.append(f"| {n[4:]} | {f(r5['Fbar'])} | {f(r5['Fbar_noMSU'])} | {f(r5['Fmax'])} | {f(r5['S_F'])} | {f(r5['Abar'])} | {f(r5['S_A'])} |")
    L += ["", "## Registered verdicts", ""]
    for a, v in V["TT-H1"].items():
        L.append(f"- TT-H1 {a}: {v['verdict']}" + (f" (failing families s401 {v['seeds']['401']['n_fail']}, s402 {v['seeds']['402']['n_fail']})" if "seeds" in v else ""))
    for n, v in V["TT-H2"].items():
        L.append(f"- TT-H2 {n[4:]}: {v['verdict']} (sources >= 0.90: {v['n_ge_090']}; >= 0.75: {v['n_ge_075']})")
    for n, v in V["TT-H3"].items():
        L.append(f"- TT-H3 {n[4:]}: {v['verdict']}")
    for a, v in V["TT-H4"].items():
        L.append(f"- TT-H4 {a}: {v['verdict']}")
    for a, v in V["TT-H5"].items():
        L.append(f"- TT-H5 {a}: {v['verdict']}")
    L.append(f"- TT-H6 ({V['TT-H6']['label']}):")
    for k, v in V["TT-H6"]["pairs"].items():
        ds = "; ".join(f"s{s}: ΔF̄ {f(v['seeds'][s]['diff']['Fbar'])} [{f(v['seeds'][s]['ci']['Fbar'][0])}, {f(v['seeds'][s]['ci']['Fbar'][1])}]" for s in v["seeds"])
        L.append(f"  - {k}: {v['sentence']} ({ds})")
    open(sys.argv[2], "w").write("\n".join(L) + "\n")
    print("\n".join(L))


if __name__ == "__main__":
    main()
