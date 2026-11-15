"""ID0: compact markdown tables from arm_<arm>.json (for result.md).  python3 -I summarize.py [arm ...]"""
import json
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import id0_common as C  # noqa: E402

KEY = ["frgcferet opencv R0 vs R4", "frgcferet opencv R2w vs R4", "frgcferet opencv R2 vs R4", "frgcferet opencv R3 vs R4",
       "frgcferet opencv R3m vs R4", "frgcferet opencv R2w vs R3", "frgcferet opencv R0 vs R2w",
       "frgcferet opencv NC vs R3 (negative control: R3 positive)",
       "frgcferet facemorpher R0 vs R4", "frgcferet facemorpher R2w vs R4", "frgcferet facemorpher R3 vs R4",
       "MorDIFF stored E vs B20", "MorDIFF stored D20 vs B20", "MorDIFF stored C20 vs B20", "MorDIFF stored D20 vs C20",
       "MorDIFF stored E vs D20", "MorDIFF stored D vs B", "MorDIFF stored E vs A (published)",
       "MorDIFF stored D20 vs A (published)",
       "MorDIFF DiffAE-native a256 vs B20", "MorDIFF DiffAE-native D20 vs B20", "MorDIFF DiffAE-native C20 vs B20",
       "MorDIFF DiffAE-native D20 vs C20", "MorDIFF DiffAE-native a256 vs D20",
       "StyleGAN3 h3_bona vs h3_sg3", "StyleGAN3 a37spread vs h3_sg3", "StyleGAN3 FRLL native photo vs h3_sg3 (cross-pool)",
       "a46 rec vs published MorDIFF", "a46 rec vs published DiM-C", "a46 rec vs published Greedy-DiM",
       "a46 a43_D vs a43_B", "a46 a256 vs rec (negative control: aligner copy vs reconstruction)",
       "FRLL native vs published opencv morph frames", "FRLL native vs published facemorpher morph frames",
       "frll opencv R0 vs R4", "frll opencv R2w vs R4", "frll opencv R3 vs R4"]


def f(r):
    return f"{r['auc']:.3f} [{r['ci95'][0]:.3f}, {r['ci95'][1]:.3f}]"


def main():
    arms = sys.argv[1:] or ["glint", "clip", "dino", "diffae"]
    for a in arms:
        p = C.RES / f"arm_{a}.json"
        if not p.exists():
            continue
        r = json.load(open(p))
        print(f"\n### {a}\nfit {r['fit']}\nvirtual {r['virtual_in_domain']}")
        print("ceiling", [(x["c"], x["closed"], x["spectrum"]) for x in r["ceiling_curve"]])
        cs = {(x["label"], x["score"]): x for x in r["contrasts"]}
        print("| contrast | ISS | TYP | SES | n neg/pos | c | pred closed/spectrum |\n|---|---|---|---|---|---|---|")
        for k in KEY:
            if (k, "iss") not in cs:
                continue
            x = cs[(k, "iss")]
            t, s = cs.get((k, "typ")), cs.get((k, "ses"))
            pr = (f"{x['pred_closed']} / {x['pred_spectrum']} | pool-c {x.get('c_pool_centred_median')}: "
                  f"{x.get('pred_closed_pool_c')} / {x.get('pred_spectrum_pool_c')}") if "pred_closed" in x else ""
            print(f"| {k} | {f(x)} | {f(t) if t else ''} | {f(s) if s else ''} | {x['n_neg']}/{x['n_pos']} | "
                  f"{x.get('c_arm_median', '')} | {pr} |")
        print("controls (ISS):")
        for x in r["contrasts"]:
            if x["kind"].startswith("control") and x["score"] == "iss":
                print(f"  {x['label']}: {f(x)}  | TYP {f(cs[(x['label'], 'typ')])}")
        for k, d in r.get("dose", {}).items():
            print("dose", k, "hosts", d["hosts"], "p", d["p"], "monotone", d["monotone_means"],
                  {g: f(v) for g, v in d["auc_vs_m000"].items() if v})
        for k, v in r.get("shrink_law", {}).items():
            print("shrink", k, v)
        for k, v in r.get("shrink_law_power", {}).items():
            print("power", k, v)
        for k, v in r.get("fidelity", {}).items():
            print("fid", k, v)
        if "geo0" in r:
            g = r["geo0"]
            print("Lambda", g["Lambda"], g["Lambda_ridge_sensitivity"], "twin cos", g["twin_cos_fit_median"])
            print("ceiling table", g["ceiling_table"])
            print("in-domain", g["virtual_head_in_domain"])
            for x in g["virtual_head_applied"]:
                print("head", x["label"], f(x), x["n_neg"], x["n_pos"])
            for k, v in g["gain"].items():
                print("gain", k, v)


if __name__ == "__main__":
    main()
