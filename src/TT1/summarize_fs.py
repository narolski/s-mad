"""TT1-FS / TT1-X tables from the readers' JSON (no new statistic).
  python3 -I summarize_fs.py tt1_read_fs.json tt1_read_x_sp.json [tt1_read_ms1.json] OUT.md"""
import json
import sys

FAM = ["replay_attack", "msu_mfsd", "oulu_npu", "casia_fasd", "lfw_calfw", "cfp_ff", "agedb_30"]
SRC = ["replay_attack", "msu_mfsd", "oulu_npu", "casia_fasd", "lfw", "calfw", "cfp_ff", "agedb_30"]


def f(x, d=3):
    return "n/a" if x is None else f"{x:.{d}f}"


def nettable(R, title):
    L = [f"## {title}", "",
         "| Network | F̄ | F_max | " + " | ".join(FAM) + " | R_cam flag | R_ffhq flag | geo224 flag | geo112 flag | AUC(U,R_cam) min-max | F̄ at -1 | F̄ at -2 | TF32 split R_cam max / flips |",
         "|---" * (len(FAM) + 12) + "|"]
    for n, r in R.items():
        fam = r.get("family_flag_corrected") or {}
        cells = []
        for x in FAM:
            c = fam.get(x)
            if c:
                s = f"{f(r['fam_flag'][x])} [{f(c['boot_ci_clipped'][0])}, {f(c['boot_ci_clipped'][1])}]"
                if c["zero_event"]:
                    s += f" CP≤{f(c['cp'][1])}"
            else:
                s = f(r["fam_flag"][x])
            cells.append(s)
        aucs = [r["auc"][s]["a"]["auc"] for s in SRC]
        pr = r.get("printed", {})
        ts = r.get("tf32_split_R_cam") or r.get("tf32_split_R_cam_L40S") or {}
        L.append(f"| {n} | {f(r['r5']['Fbar'])} | {f(r['r5']['Fmax'])} | " + " | ".join(cells) +
                 f" | {f(r['pools']['R_cam']['flag'])} | {f(r['pools']['R_ffhq']['flag'])} | {f(pr.get('geo_flag', {}).get('g224'))} | "
                 f"{f(pr.get('geo_flag', {}).get('g112'))} | {f(min(aucs))}-{f(max(aucs))} | {f(pr.get('Fbar_at', {}).get('-1'))} | "
                 f"{f(pr.get('Fbar_at', {}).get('-2'))} | {f(ts.get('max_abs'), 4)} / {ts.get('flips', 'n/a')} |")
    L.append("")
    L += [f"### {title}: AUCs R3(c) border-matched, R3(g) geometry-matched (per source), R3(d), R3(e) min-max, R3(f)", "",
          "| Network | R3(c) " + " ".join(SRC) + " | R3(g) " + " ".join(SRC) + " | d | e min-max | f g224 | f g112 |", "|---|---|---|---|---|---|---|"]
    for n, r in R.items():
        a = r["auc"]
        e = [a["e_cam_border"][x]["auc"] for x in FAM]
        L.append(f"| {n} | " + " ".join(f(a[s]["c"]["auc"]) for s in SRC) + " | " + " ".join(f(a[s]["g"]["auc"]) for s in SRC) +
                 f" | {f(a['d_ffhq_border']['auc'])} | {f(min(e))}-{f(max(e))} | {f(a['f_geo']['g224']['auc'])} | {f(a['f_geo']['g112']['auc'])} |")
    L.append("")
    return L


def main():
    fs = json.load(open(sys.argv[1]))
    sp = json.load(open(sys.argv[2]))
    ms1 = json.load(open(sys.argv[3])) if len(sys.argv) > 4 else None
    out = sys.argv[-1]
    L = ["# TT1 fresh-seed block (TT1-FS) and extension (TT1-X): tables", ""]
    L += nettable(fs["nets"], "TT1-FS: A, B, Sb at seeds 403-407 (pn1fs A100, gate 15/15 byte-identical)")
    V = fs["verdicts"]
    L += ["## TT1-FS registered verdicts", ""]
    for h in ("TT-H1", "TT-H2", "TT-H3", "TT-H4", "TT-H5"):
        for a, v in V[h].items():
            L.append(f"- {h} {a}: {v['verdict']}  (per seed: {v.get('seeds')})")
    L.append(f"- TT-H6 ({V['TT-H6']['label']}):")
    for k, v in V["TT-H6"]["pairs"].items():
        ds = "; ".join(f"s{s}: {f(x['dFbar'])} [{f(x['ci'][0])}, {f(x['ci'][1])}]" for s, x in v["seeds"].items() if x)
        acr = v["across_seeds"]
        L.append(f"  - {k}: {v['sentence']} | mean {f(acr['mean'])} SD {f(acr['sd'])} negative {acr['n_negative']}/{acr['n']} | {ds}")
    L.append("- Across-seed summary: " + json.dumps({a: {k: (round(x['mean'], 4), round(x['sd'], 4)) for k, x in s.items()} for a, s in V["across_seed_summary"].items()}))
    L.append("")
    L += nettable(sp["nets"], "TT1-X Part 1: Sp seeds 403-405 (printed only; gate 3/3 byte-identical)")
    if ms1:
        L += nettable(ms1["nets"], "TT1-X Part 2: MS1 Sb, SbM3, SbV seeds 403-407 (L40S; printed only; labels in JSON)")
    open(out, "w").write("\n".join(L) + "\n")
    print("\n".join(L))


if __name__ == "__main__":
    main()
