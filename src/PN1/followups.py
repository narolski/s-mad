"""PN1 tier-1 follow-ups of review REVIEW_PN1_TIER1_20261112.md, all POST HOC / descriptive, zero GPU:
HN1 head norm and floor; scale-free storage reads; per-genuine-source flag table; HN3 JPEG-history check for arm C.
  python3 -I followups.py -> experiments/PN1_.../tier1/followups.json"""
import csv
import pathlib
import sys

import numpy as np

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import pn1lib as K  # noqa: E402
import reads as RD  # noqa: E402
import tier1 as T1  # noqa: E402

RR = K.PN1 / "results_rented"


def main():
    import torch
    rows = T1.eval_rows()
    P = RD.pools(rows)
    out = {"post_hoc": True}
    from scipy.stats import spearmanr
    # HN3 inputs: blockiness of the MAD22 Webmorph / OpenCV morph files (cue_floor 'blockiness8' at 512, AF0 bench_s cues)
    zb = np.load(K.AF0 / "cues" / "bench_s.npz")
    bi = [str(n) for n in zb["names"]].index("blockiness8")
    bench = {r["id"]: r for r in csv.DictReader(open(K.AF0 / "lists" / "bench_s.csv"))}
    blk_by_file = {pathlib.Path(bench[str(i)]["path"]).name + "|" + bench[str(i)]["cell"]: c[bi] for i, c in zip(zb["ids"], zb["cues"])}
    S = {}
    for arm in ("A", "B", "Bn", "C"):
        for seed in (401, 402):
            name = f"{arm}_s{seed}"
            s, zt, info = T1.load_result(RR / f"PN1_{name}.tar")
            S[name] = s
            tr = torch.load(RR / "unpacked" / f"PN1_{name}" / "last_trainable.pt", map_location="cpu", weights_only=True)
            hw = [k for k in tr if k.endswith("weight") and tr[k].ndim == 2 and tr[k].shape[0] == 1]
            hb = [k for k in tr if k.endswith("bias") and tr[k].numel() == 1]
            w = float(tr[hw[0]].norm()) if hw else None
            b = float(tr[hb[0]].reshape(-1)[0]) if hb else None
            r0 = RD.scores_of(s, P["T_R0"])
            floor = (-w + b) if w is not None else None
            ha = {r["host"]: s[r["id"]] for r in P["T_R0"]}
            h6 = {r["host"]: s[r["id"]] for r in P["T_R0_61"]}
            h1 = {r["host"]: s[r["id"]] for r in P["T_R0_112"]}
            hs = sorted(set(ha) & set(h6))
            rec = dict(head_weight_norm=w, head_bias=b, floor=floor, head_keys=hw + hb,
                       R0_median=float(np.median(r0)), R0_p5_p95=[float(np.percentile(r0, 5)), float(np.percentile(r0, 95))],
                       R0_median_above_floor=None if floor is None else float(np.median(r0) - floor),
                       share_rising_61=float(np.mean([h6[h] > ha[h] for h in hs])),
                       share_rising_112=float(np.mean([h1[h] > ha[h] for h in hs if h in h1])),
                       paired_auc_R0_61_vs_R0=RD.paired(s, P, "T_R0_61", "T_R0")["auc"])
            T = RD.thresholds(s, P, 0.0)
            src = {"test ladder R0 (FRGC/colorFERET)": "T_R0", "development ladder R0": "D_R0", "AF0 validation photos": "V_photo",
                   "FRLL native (= MAD22 genuine)": "FRLL_bona_native", "H1 genuine (CASIA)": "H1_bona"}
            rec["genuine_flags_by_source"] = {k: {th: float(np.mean(RD.scores_of(s, P[p]) > T[th])) for th in ("own", "cam")}
                                              for k, p in src.items()}
            out[name] = rec
    # HN3: C - A score difference against blockiness on MAD22 morph files
    for seed in (401, 402):
        for fam in ("Webmorph", "OpenCV"):
            rr = P[f"MAD22_{fam}_morph"]
            d, bl = [], []
            for r in rr:
                k = pathlib.Path(r["path"]).name + "|mad22_" + fam
                if k in blk_by_file:
                    d.append(S[f"C_s{seed}"][r["id"]] - S[f"A_s{seed}"][r["id"]])
                    bl.append(blk_by_file[k])
            rho = spearmanr(d, bl)
            out[f"HN3_s{seed}_{fam}"] = dict(n=len(d), spearman=float(rho.correlation), p=float(rho.pvalue))
    # raw-file formats of the corrected MAD22 release (file headers)
    raw = pathlib.Path("/mnt/t7/smad_heldout/mad22_incoming/marco_owncloud_20261109T103840Z/author_files/original_sorted")
    fmt = {}
    for fam in ("Webmorph", "OpenCV", "FaceMorpher", "BonaFide"):
        d_ = raw / fam
        if not d_.exists():
            cand = [x for x in raw.iterdir() if x.name.lower().startswith(fam.lower())] if raw.exists() else []
            d_ = cand[0] if cand else d_
        cnt = {}
        for f in sorted(d_.rglob("*"))[:5000] if d_.exists() else []:
            if f.is_file():
                h = open(f, "rb").read(4)
                kind = "jpeg" if h[:3] == b"\xff\xd8\xff" else "png" if h[:4] == b"\x89PNG" else "other"
                cnt[kind] = cnt.get(kind, 0) + 1
        fmt[fam] = cnt
    out["HN3_raw_file_formats"] = fmt
    out["HN5"] = "not computed: no ghost-energy measurement exists for the H1 (Poisson set) images"
    K.dump(out, K.RES / "tier1" / "followups.json")
    print("DONE")


if __name__ == "__main__":
    if not sys.flags.isolated:
        sys.exit("run with python3 -I")
    main()
