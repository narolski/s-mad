"""Sealed MAD22 read (FINAL): POST HOC, DESCRIPTIVE, MAD22-informed reads on the EXISTING score files only (lead's
decisions after the read, 13 Nov 2026). Nothing is scored; no registered verdict changes; no method choice may follow.
  (1) fragility of the primary verdict: the registered statistic (H form, mean4, ours vs SelfMAD raw genuine) with
      R = 20,000 at the registered seed, and over 200 alternative seeds at R = 2,000;
  (2) SelfMAD's per-row crop flags ('cropped' of RS1 score.py --mode own) per pool;
  (3) development seeds 401/402 (PN1 tier-1 Sb read, MAD22 E7 EER OpenCV / Webmorph) beside the frozen seeds 403-407.
Uses final_read.Read (load only; the reader's main() and its marker are not touched).
  python3 -I posthoc_read.py --out experiments/FINAL_sealed-benchmark-read/posthoc_mad22_informed.json"""
import argparse
import csv
import json
import pathlib
import sys

import numpy as np

HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import final_read as FR  # noqa: E402
import final_metrics as FM  # noqa: E402

ROOT = pathlib.Path("/home/narolski/smad-next")
O = pathlib.Path("/mnt/t7/smad_next/FINAL")


def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--out", required=True)
    ap.add_argument("--alt-seeds", type=int, default=200)
    a = ap.parse_args()
    args = argparse.Namespace(result=str(O / "results/FINAL_mad22_final2.tar"), pack=str(O / "FINAL_mad22_pack.tar"),
                              release_existing=str(O / "release_scores_existing.npz"),
                              selfmad=str(O / "selfmad/selfmad_mad22_scores.npz"), beststat=str(O / "beststat/beststat_mad22.npz"),
                              thresholds=str(ROOT / "experiments/FINAL_sealed-benchmark-read/final_thresholds.json"),
                              pins=str(HERE / "final_pins.json"))
    rd = FR.Read(args)
    rd.load()
    names = [n["name"] for n in rd.cfg["networks"]]
    ours = {n: rd.our_pools(lambda r, m=rd.scores[n]: m[r["id"]])["H"] for n in names}
    zs = np.load(args.selfmad)
    rel = rd.rel_pools(zs, "selfmad_hrnet_w18", "own_dgx", "raw")["H"]
    fams = FR.PRIMARY_FAMS
    pers = sorted({r["pa"] for r in rd.man} | {r["pb"] for r in rd.man})
    pos = {p: i for i, p in enumerate(pers)}

    def eers(cell, C):
        sm, ppm, sg, ppg, _ = cell
        a_ = np.array([pos[p[0]] for p in ppm]); b_ = np.array([pos[p[1]] for p in ppm])
        wm = C[:, a_] * C[:, b_]; same = a_ == b_
        if same.any():
            wm[:, same] = C[:, a_[same]]
        W = np.c_[wm, C[:, [pos[p[0]] for p in ppg]]]
        return FM.eer_w(np.r_[sm, sg], np.r_[np.ones(len(sm)), np.zeros(len(sg))], W)

    def p_ni(seed, R):
        rng = np.random.default_rng(seed)
        C = rng.multinomial(len(pers), np.full(len(pers), 1 / len(pers)), size=R).astype(np.float64)
        SI = rng.integers(0, len(names), size=(R, len(names)))
        ourrep = np.stack([np.mean([eers(ours[n][f], C) for f in fams], 0) for n in names])
        agg = ourrep[SI, np.arange(R)[:, None]].mean(1)
        relrep = np.mean([eers(rel[f], C) for f in fams], 0)
        d = agg - relrep
        return dict(p_noninferior=float((1 + (d >= 0.01).sum()) / (R + 1)), p_exceeded=float((1 + (d >= 0).sum()) / (R + 1)),
                    ci=[float(np.percentile(d, 2.5)), float(np.percentile(d, 97.5))], n_beyond_margin=int((d >= 0.01).sum()))
    out = {"label": "post hoc, descriptive, MAD22-informed; the registered verdicts stand; no method choice follows",
           "registered_check": p_ni(FR.SEED, FR.B_REPS)}
    out["R20000_registered_seed"] = p_ni(FR.SEED, 20000)
    alt = [p_ni(FR.SEED + 1 + k, 2000)["p_noninferior"] for k in range(a.alt_seeds)]
    out["alt_seeds_R2000"] = dict(n=len(alt), median=float(np.median(alt)), q25=float(np.percentile(alt, 25)),
                                  q75=float(np.percentile(alt, 75)), share_le_0025=float(np.mean(np.array(alt) <= 0.025)))
    # (2) SelfMAD crop flags per pool
    meta = {r["id"]: r for r in csv.DictReader(open(O / "selfmad/selfmad_mad22_meta.csv"))}
    z = np.load(O / "selfmad/scores/scores_own_selfmad_mad22__dgx.npz")
    cnt = {}
    for i, c in zip(z["id"].tolist(), z["cropped"].tolist()):
        s = meta[i]["set"]
        k = cnt.setdefault(s, [0, 0]); k[0] += 1; k[1] += int(bool(c))
    out["selfmad_crop_flags"] = {s: dict(n=v[0], cropped_true=v[1], cropped_false=v[0] - v[1]) for s, v in sorted(cnt.items())}
    # (3) development seeds against frozen seeds (MAD22 E7 EER %, OpenCV / Webmorph)
    sb = json.load(open(ROOT / "experiments/PN1_protocol-network-first-tests/tier1_sb/sb_read.json"))
    dev = {s: sb[s]["Sb"]["mad22_e7_eer"] for s in ("s401", "s402") if "mad22_e7_eer" in sb[s].get("Sb", {})}
    fr = json.load(open(ROOT / "experiments/FINAL_sealed-benchmark-read/final_read.json"))
    frozen = {n: [100 * fr["cells"]["H"]["OpenCV"]["ours"][n]["eer"], 100 * fr["cells"]["H"]["Webmorph"]["ours"][n]["eer"]] for n in names}
    out["dev_vs_frozen_mad22_e7_eer_pct_opencv_webmorph"] = dict(development=dev, frozen=frozen,
        frozen_mean=[float(np.mean([v[0] for v in frozen.values()])), float(np.mean([v[1] for v in frozen.values()]))],
        note="development seeds: PN1 tier-1 Sb read (sb_read.json, key mad22_e7_eer = [OpenCV, Webmorph]); same aligned MAD22 frames")
    pathlib.Path(a.out).write_text(json.dumps(out, indent=1))
    print("POSTHOC written", a.out)


if __name__ == "__main__":
    if not sys.flags.isolated:
        sys.exit("run with python3 -I")
    main()
