"""TT1-X Part 2 printed reads (prereg_x_block.md + amendment): MS1's Sb, SbM3, SbV networks (seeds 403-407, L40S), from
scores MS1 already made. No scoring, no rule, no verdict.
Sources per network: in-pack scores (fit tar MS1_<arm>_s<seed>/scores_eval.npz, pn1_score.py, TF32 on) for the U frames
(tt1_* ids, the 21,089 aligned frames), R_cam (FS1 ids), R_ffhq, M_ffhq; the held-out step (MS1H_m*.tar
out/MS1H_<arm>_s<seed>_tt1ref.npz, rescore.py, TF32 off) for R_cam (ids rcam_<id>), R_cam^border, R_cam^geo224/112,
R_ffhq^border.
Reads: TT1 reader statistics unchanged (tt1_read.py read_net, family_ci), with pools restricted to rows present
(aligned=0 frames are not in MS1's pack: the U_all pools are cut to aligned frames and labelled). R3(a), R3(b), u:
in-pack only (TF32 on). R3(c), R3(g): mixed (U on, references off), labelled. R3(e), R3(f): recomputed with the tt1ref
R_cam (off) on both sides. R3(d): R_ffhq^border (off) vs in-pack R_ffhq (on), labelled mixed. TF32 split printed
(tt1ref R_cam vs in-pack R_cam). For SbM3, reads on FFHQ pools carry the trained-source label.
Bootstrap draws: default_rng(20261122) as TT1, over the restricted pools (so draws differ from TT1's; labelled).
  python -I tt1_read_ms1.py --out OUT.json [--mock]"""
import argparse
import io
import json
import pathlib
import sys
import tarfile

import numpy as np

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import tt1common as T  # noqa: E402
import tt1_read as TR  # noqa: E402
import tt1_read_fs as TF  # noqa: E402

RR = pathlib.Path("/mnt/t7/smad_next/MS1/results_rented")
NETS = pathlib.Path("/mnt/t7/smad_next/TT1/nets_ms1")
MACHINE = {403: "m1", 406: "m1", 404: "m2", 407: "m2", 405: "m3"}
ARMS = ("Sb", "SbM3", "SbV")
SEEDS = (403, 404, 405, 406, 407)
TRAINED_FFHQ = "trained source (FFHQ), development persons excluded, other pipeline"


def npz_from_tar(tar, member):
    with tarfile.open(tar) as tf:
        return np.load(io.BytesIO(tf.extractfile(member).read()))


def extract_net(arm, s):
    n = f"MS1_{arm}_s{s}"
    d = NETS / n
    if not (d / "scores_eval.npz").exists():
        d.mkdir(parents=True, exist_ok=True)
        with tarfile.open(RR / f"{n}.tar") as tf:
            for f in ("meta.json", "last_trainable.pt", "scores_eval.npz"):
                (d / f).write_bytes(tf.extractfile(f"{n}/{f}").read())
    return d


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True)
    ap.add_argument("--mock", action="store_true")
    a = ap.parse_args()
    P0, tt = TR.load_pools()
    out = dict(label="TT1-X Part 2 printed reads (MS1 L40S scores); no rule", nets={}, missing={})
    Pcache = {}
    for arm in ARMS:
        for s in SEEDS:
            n = f"MS1_{arm}_s{s}"
            if a.mock:
                mr = np.random.default_rng(s * 7 + ARMS.index(arm))
                ids = [i for v in P0.values() for i, _ in v if not (i.startswith("tt1_") and tt[i]["aligned"] != "1")]
                inpack = {i: float(np.clip(mr.normal(-3.0, 1.2), -3.87, 3.87)) for i in ids}
                for i, _ in P0["M_ffhq"]:
                    inpack[i] = float(np.clip(mr.normal(3.0, 1.0), -3.87, 3.87))
                ref = {("rcam_" + i): v + 0.001 for i, v in inpack.items() if any(i == j for j, _ in P0["R_cam"])}
                ref.update({i: inpack[i] for k in P0 if k.startswith(("Rcb:", "Rgeo:", "Rfb")) for i, _ in P0[k]})
                floor, tc = -3.87, -3.6
            else:
                d = extract_net(arm, s)
                z = np.load(d / "scores_eval.npz")
                inpack = dict(zip(z["id"].tolist(), z["logit"].astype(float).tolist()))
                zr = npz_from_tar(RR / f"MS1H_{MACHINE[s]}.tar", f"out/MS1H_{arm}_s{s}_tt1ref.npz")
                ref = dict(zip(zr["id"].tolist(), zr["logit"].astype(float).tolist()))
                floor = TR.head_floor(d)
                tc = TF.tau_cam_fs(d)
            L = dict(inpack)
            for k in P0:
                if k.startswith(("Rcb:", "Rgeo:", "Rfb")):
                    for i, _ in P0[k]:
                        L[i] = ref[i]
            P = {k: [(i, h) for i, h in v if i in L] for k, v in P0.items()}
            miss = {k: len(P0[k]) - len(P[k]) for k in P0 if len(P0[k]) != len(P[k])}
            key = tuple(sorted((k, len(v)) for k, v in P.items()))
            if key not in Pcache:
                Pcache[key] = TR.boot_weights(P, np.random.default_rng(TR.SEED))
            W = Pcache[key]
            r = TR.read_net(L, P, W, tt, floor, tc)
            TR.family_ci(r, P, W, L)
            # R3(e), R3(f) with the tt1ref R_cam (TF32 off) on both sides
            L2 = dict(L)
            for i, _ in P["R_cam"]:
                L2[i] = ref["rcam_" + i]
            r2 = TR.read_net(L2, P, W, tt, floor, tc)
            r["auc"]["e_cam_border"] = r2["auc"]["e_cam_border"]
            r["auc"]["f_geo"] = r2["auc"]["f_geo"]
            r["printed"] = TF.extra_reads(L, P)
            r["printed"]["geo_flag"] = TF.extra_reads(L2, P)["geo_flag"]
            corr = {}
            for f in T.FAMILIES:
                srcs = [f] if f != "lfw_calfw" else ["lfw", "calfw"]
                x = np.concatenate([np.array([L[i] for i, _ in P[f"U:{q}"]]) > 0 for q in srcs])
                lo, hi = r["fam_flag_ci"][f]
                corr[f] = dict(boot_ci_clipped=[max(0.0, lo), hi], cp=TR.cp(int(x.sum()), len(x)), zero_event=bool(x.sum() == 0))
            r["family_flag_corrected"] = corr
            camids = [i for i, _ in P["R_cam"]]
            dd = np.array([ref["rcam_" + i] - inpack[i] for i in camids])
            r["tf32_split_R_cam_L40S"] = dict(max_abs=float(np.abs(dd).max()), median_abs=float(np.median(np.abs(dd))),
                                              flips=int(sum((ref["rcam_" + i] > 0) != (inpack[i] > 0) for i in camids)))
            r["labels"] = {"R3(a), R3(b), u": "in-pack only (TF32 on)", "R3(c), R3(g)": "mixed TF32 (U on, references off)",
                           "R3(e), R3(f), geo_flag": "tt1ref R_cam (off) on both sides",
                           "R3(d)": "mixed (R_ffhq^border off vs in-pack R_ffhq on)",
                           "U pools": "aligned frames only (MS1 pack); U_p unchanged",
                           "bootstrap": "default_rng(20261122) over the restricted pools (draws differ from TT1's)",
                           "platform": f"L40S 48 GB, machine {MACHINE[s]} (seeds 403+406 m1, 404+407 m2, 405 m3)"}
            if arm == "SbM3":
                r["labels"]["FFHQ pools (R_ffhq, R_ffhq^border, M_ffhq, u, R3(b), R3(d))"] = TRAINED_FFHQ
            r["r5"].pop("_draws", None)
            out["nets"][n] = r
            out["missing"][n] = miss
            print("read", n, flush=True)
    pathlib.Path(a.out).write_text(json.dumps(out, indent=1, default=float))


if __name__ == "__main__":
    main()
