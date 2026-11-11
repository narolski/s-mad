"""Own-crop re-score of the audit rows (RS1): markdown tables from rs1_results.json (for result.md).
  python3 -I tables.py > /mnt/t7/smad_next/RS1/tables.md
"""
import json
import pathlib

RES = pathlib.Path("/home/narolski/smad-next/experiments/RS1_own-crop-rescore")
CELL = {**{f"mad22_{f}": f"MAD22 {f}" for f in ("FaceMorpher", "MIPGAN_I", "MIPGAN_II", "OpenCV", "Webmorph")},
        "amsl": "FRLL AMSL", "facemorpher": "FRLL FaceMorpher", "opencv": "FRLL OpenCV", "webmorph": "FRLL WebMorph",
        "stylegan": "FRLL StyleGAN2", "mordiff": "MorDIFF", "dim_a": "DiM-A", "dim_c": "DiM-C", "fast_dim": "Fast-DiM",
        "fast_dim_ode": "Fast-DiM-ODE", "greedy_dim": "Greedy-DiM", "greedy_dim_s": "Greedy-DiM-S"}
SHORT = {"reproduced": "reproduced", "our pipeline, published number not reproduced": "not reproduced",
         "no published number": "no published number"}


def md(rows, cols, heads):
    s = "| " + " | ".join(heads) + " |\n|" + "---|" * len(heads) + "\n"
    for r in rows:
        s += "| " + " | ".join("" if r.get(c) is None else str(r.get(c)) for c in cols) + " |\n"
    return s


def main():
    d = json.load(open(RES / "rs1_results.json"))
    for r in d["reproduction"]:
        r["cellname"] = CELL[r["cell"]]
        r["eer"] = f"{r['native_eer']:.2f} [{r['lo']:.2f}, {r['hi']:.2f}]"
        r["lab"] = SHORT[r["label"]] + (f" (Table 2 value {r['alt_published']}: {SHORT[r['alt_label']]})"
                                        if r.get("alt_published") else "")
    print("## Reproduction\n")
    for r in d["reproduction"]:
        r["neer"] = f"{r['neutral_only_eer']:.2f} [{r['neutral_lo']:.2f}, {r['neutral_hi']:.2f}]"
        r["nlab"] = SHORT[r["neutral_label"]]
    print(md(d["reproduction"], ["detector", "platform", "cellname", "n_genuine", "n_morph", "eer", "published", "abs_diff",
                                 "window", "lab", "neer", "nlab"],
             ["Detector", "Platform", "Cell", "Genuine", "Morphs", "Native EER [95%]", "Published", "|diff|", "Window",
              "Label", "Neutral-only EER", "Label (neutral-only)"]))
    print("## History-matched genuine photos\n")
    for r in d["history"]:
        r["cellname"] = CELL[r["cell"]]
        r["lab"] = SHORT[r["label"]]
    print(md(d["history"], ["detector", "platform", "cellname", "lab", "native_eer", "e7_kind", "e7_eer", "history_effect",
                            "aligned_native_eer", "aligned_e7_eer", "aligned_history_effect"],
             ["Detector", "Platform", "Cell", "Label", "Native EER", "E7 kind", "EER, history-matched genuine",
              "History effect (raw E7 − native)", "EER, aligned native", "EER, aligned E7",
              "History effect (aligned E7 − aligned native)"]))
    print("## Flag rates (%)\n")
    fl = {}
    for r in d["flags"]:
        k = (r["detector"], r["platform"], r["cell"])
        fl.setdefault(k, {"detector": r["detector"], "platform": r["platform"], "cellname": CELL[r["cell"]],
                          "lab": SHORT[r["label"]]})
        pool = ("nat" if r["pool"].startswith("native") else "e7" if r["pool"].startswith("history")
                else "aln" if r["pool"].startswith("aligned") else "small")
        fl[k][f"{r['threshold']}_{pool}"] = r["flagged"]
    cols = ["detector", "platform", "cellname", "lab"] + [f"{t}_{p}" for t in ("t5", "t_eer") for p in ("nat", "e7", "aln", "small")]
    heads = ["Detector", "Platform", "Cell", "Label"] + [f"{t}: {p}" for t in ("5%-photo threshold", "EER threshold")
                                             for p in ("native", "history-matched", "aligned native", "stored-small")]
    print(md(list(fl.values()), cols, heads))
    print("## Genuine class split (EER %)\n")
    ex = {}
    for r in d["expression"]:
        k = (r["detector"], r["platform"], r["cell"])
        ex.setdefault(k, {"detector": r["detector"], "platform": r["platform"], "cellname": CELL[r["cell"]],
                          "lab": SHORT[r["label"]]})
        sp = "n" if r["genuine"].startswith("neutral") else "s"
        ex[k][f"nat_{sp}"] = r["native_eer"]
        ex[k][f"e7_{sp}"] = r.get("e7_eer")
        ex[k][f"f_{sp}"] = r.get("e7_flag_t5")
    print(md(list(ex.values()), ["detector", "platform", "cellname", "lab", "nat_n", "nat_s", "e7_n", "e7_s", "f_n", "f_s"],
             ["Detector", "Platform", "Cell", "Label", "Native, neutral only", "Native, smiling only", "History-matched, neutral only",
              "History-matched, smiling only", "History-matched flagged at 5%-photo threshold, neutral",
              "same, smiling"]))
    print("## MorDIFF ladder (AUC, higher rung positive)\n")
    lad = {}
    for r in d["ladder"]:
        lad.setdefault(r["contrast"], {"contrast": r["contrast"]})[r["detector"] + " / " + r["platform"]] = r["auc"]
    dets = list(dict.fromkeys(r["detector"] + " / " + r["platform"] for r in d["ladder"]))
    print(md(list(lad.values()), ["contrast"] + dets, ["Contrast"] + dets))
    print("## MorDIFF control images flagged (%)\n")
    lf = {}
    for r in d["ladder_flags"]:
        lf.setdefault((r["threshold"], r["arm"]), {"t": r["threshold"], "arm": r["arm"]})[r["detector"] + " / " + r["platform"]] = r["flagged"]
    print(md(list(lf.values()), ["t", "arm"] + dets, ["Threshold", "Image set"] + dets))
    print("## Genuine pools and morph sets at the release rule and at named threshold pools (% flagged)\n")
    pr = {}
    for r in d["pool_rates"]:
        k = (r["detector"], r["platform"], r["pool"])
        pr.setdefault(k, {"detector": r["detector"], "platform": r["platform"], "pool": r["pool"], "kind": r["kind"],
                          "n": r["n"]})[r["threshold_pool"]] = r["flagged"]
    tcols = ["release rule (p > 0.5)", "t5 on raw FRLL photos", "t5 on FFHQ orig", "t5 on FEI (all)"]
    print(md(list(pr.values()), ["detector", "platform", "kind", "pool", "n"] + tcols,
             ["Detector", "Platform", "Kind", "Pool", "n"] + tcols))
    print("## Paired logit shifts (processed copy minus its own unprocessed photo)\n")
    print(md(d["shifts"], ["detector", "platform", "processed", "base", "n_pairs", "mean_logit_shift", "median_logit_shift",
                           "share_rising"],
             ["Detector", "Platform", "Processed", "Base", "Pairs", "Mean shift [95%]", "Median", "Share rising [95%]"]))


if __name__ == "__main__":
    main()
