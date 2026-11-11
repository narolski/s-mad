"""Follow-up (a) of the morph-free networks experiment (AD4), prereg Amendment 4: face-only softness null (H-new-1) and the
rank test on the history-matched diffusion cells (H-new-2). DGX CPU, one process; reads the evaluation PNGs (our frames), writes
no image. Measures: M1 = variance of the 3x3 Laplacian inside the fixed face ellipse; M2 = share of spectral power above 0.25
cycles/pixel in the fixed face box after a 2-D Hann window (DC excluded). Statistic S = -M2.

  python fu_sharpness.py [--limit N]      (--limit: test on N images per cell; no verdict)
"""
import argparse
import csv
import json
import pathlib

import cv2
import numpy as np
from PIL import Image
from scipy.stats import spearmanr

import summarise as R

A, S = R.A, R.S
CX, CY, AX, AY = 256, 264, 125, 172
BX0, BX1, BY0, BY1 = 166, 346, 160, 380          # x 166..345, y 160..379
OUT = R.EXP


def masks():
    yy, xx = np.mgrid[0:512, 0:512]
    ell = ((xx - CX) / AX) ** 2 + ((yy - CY) / AY) ** 2 <= 1.0
    assert ell[BY0:BY1, BX0:BX1].all()                 # the box lies inside the ellipse
    h = np.outer(np.hanning(BY1 - BY0), np.hanning(BX1 - BX0))
    fy = np.fft.fftfreq(BY1 - BY0)[:, None]
    fx = np.fft.fftfreq(BX1 - BX0)[None, :]
    rad = np.sqrt(fx ** 2 + fy ** 2)
    return ell, h, rad > 0.25, rad > 0


def measure(path, ell, han, hi, nodc):
    im = np.asarray(Image.open(path).convert("RGB"), np.float64)
    assert im.shape == (512, 512, 3)
    g = 0.299 * im[..., 0] + 0.587 * im[..., 1] + 0.114 * im[..., 2]
    lap = cv2.Laplacian(g, cv2.CV_64F, ksize=3)
    m1 = float(lap[ell].var())
    box = g[BY0:BY1, BX0:BX1]
    p = np.abs(np.fft.fft2((box - box.mean()) * han)) ** 2
    m2 = float(p[hi].sum() / max(p[nodc].sum(), 1e-12))
    return m1, m2


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--limit", type=int, default=0)
    ap.add_argument("--results", default="/mnt/t7/smad_next/AD4/results_vast")
    a = ap.parse_args()
    man = R.W / "ad4/data/manifests/ad4_eval.csv"
    assert R.sha(man) == R.EVAL_SHA
    rows = list(csv.DictReader(open(man)))
    cl = S.cells(rows)
    need = sorted({i for m, b in cl.values() for i in list(m) + list(b)})
    if a.limit:
        keep = set()
        for m, b in cl.values():
            keep |= set(list(m)[:a.limit]) | set(list(b)[:a.limit])
        need = sorted(keep)
    ell, han, hi, nodc = masks()
    M1, M2 = np.full(len(rows), np.nan), np.full(len(rows), np.nan)
    for k, i in enumerate(need):
        M1[i], M2[i] = measure(R.W / "data" / rows[i]["path"], ell, han, hi, nodc)
        if k % 2000 == 0:
            print(f"  measured {k}/{len(need)}", flush=True)
    np.savez(pathlib.Path("/mnt/t7/smad_next/AD4/read") / f"fu_sharpness{'_test' if a.limit else ''}.npz",
             id=np.array([r["id"] for r in rows]), m1=M1, m2=M2)
    perm_sha = {k: v["sha256"] for k, v in json.load(open(R.W / "ad4/build_info.json"))["perms"].items()}
    nets, refused, _, _ = R.load_trained(pathlib.Path(a.results), "m3", rows, perm_sha, "rented")
    mf = sorted([t for t, n in nets.items() if n["arm"] == "mf"], key=lambda t: nets[t]["seed"])
    assert len(mf) == 5 and not refused
    pers = sorted({p for i in cl["frllm/amsl/native"][1] for p in R.persons(rows[i])})
    D = R.Draw(pers, R.B_REAL if not a.limit else 200, R.BOOT_SEED)
    out = {"amendment": "4 (a)", "frames": "our frames", "label": "post hoc follow-up", "cells": {}}
    Sx = -M2
    for c in sorted(cl, key=R.cell_key):
        m, b = cl[c]
        if a.limit:
            m, b = [i for i in m if np.isfinite(Sx[i])], [i for i in b if np.isfinite(Sx[i])]
        pm, pb = [R.persons(rows[i]) for i in m], [R.persons(rows[i]) for i in b]
        ar = np.empty(D.B)
        for k in range(0, D.B, R.CHUNK):
            Cc = D.C[k:k + R.CHUNK]
            ar[k:k + R.CHUNK] = R.wauc(Sx[m], Sx[b], D.wm(pm, Cc), D.wb(pb, Cc))
        idx = list(m) + list(b)
        out["cells"][c] = {
            "auc_S": A.auc(Sx[m], Sx[b]), "auc_S_ci95": R.ci(ar), "auc_M1_softer": A.auc(-M1[m], -M1[b]),
            "median_M2_morph": float(np.median(M2[m])), "median_M2_genuine": float(np.median(M2[b])),
            "net_auc": [A.auc(nets[t]["score"][m], nets[t]["score"][b]) for t in mf],
            "spearman_net_S": [float(spearmanr(nets[t]["score"][idx], Sx[idx])[0]) for t in mf]}
    nat = {c: v for c, v in out["cells"].items() if c.endswith("/native")}
    qual = [c for c, v in nat.items() if min(v["net_auc"]) >= 0.99]
    ok_auc = [c for c in qual if nat[c]["auc_S"] >= 0.7]
    ok_sp = [c for c in qual if np.median(nat[c]["spearman_net_S"]) >= 0.7]
    low = [c for c in qual if nat[c]["auc_S"] < 0.7]
    v1 = ("supported" if qual and len(ok_auc) == len(qual) and len(ok_sp) == len(qual) else
          "falsified" if qual and len(low) >= len(qual) / 2 else "mixed")
    out["H-new-1"] = {"qualifying_cells": qual, "S_auc_ge_0.7": ok_auc, "median_spearman_ge_0.7": ok_sp, "verdict": v1}
    diff = ["mordiff/mordiff/e7"] + [f"dim/{f}/e7" for f in ("dim_a", "dim_c", "fast_dim", "fast_dim_ode", "greedy_dim",
                                                             "greedy_dim_s")]
    x = [out["cells"][c]["auc_S"] for c in diff]
    y = [float(np.median(out["cells"][c]["net_auc"])) for c in diff]
    rho = float(spearmanr(x, y)[0])
    out["H-new-2"] = {"cells": diff, "x_auc_S_morph_vs_history_matched": x, "y_median_net_auc": y, "spearman": rho,
                      "reading": "consistent with overshoot" if rho >= 0.7 else "inconsistent" if rho <= 0 else "weak"}
    tag = "_test" if a.limit else ""
    json.dump(out, open(OUT / f"fu_sharpness_m3{tag}.json", "w"), indent=1, default=float)
    L = ["# Face-only softness null (H-new-1) and rank test (H-new-2), morph-free ViT-B/16 networks (AD4 Amendment 4 (a)), "
         "our frames, post hoc follow-up", "",
         "Flag on the networks: not reproduced on this stack. S = minus the high-frequency power share in the fixed face box; "
         "M1 = Laplacian variance inside the face ellipse (AUC of 'lower = morph').", "",
         "| cell | AUC of S [95% CI] | AUC of M1 | median M2 morph / genuine | network AUC per seed | Spearman(network, S) per seed |",
         "|---|---|---|---|---|---|"]
    for c, v in out["cells"].items():
        L.append(f"| {R.nice(c)} | {v['auc_S']:.3f} {R.fci(v['auc_S_ci95'], 3)} | {v['auc_M1_softer']:.3f} | "
                 f"{v['median_M2_morph']:.4f} / {v['median_M2_genuine']:.4f} | {', '.join(f'{x:.3f}' for x in v['net_auc'])} | "
                 f"{', '.join(f'{x:.2f}' for x in v['spearman_net_S'])} |")
    h1, h2 = out["H-new-1"], out["H-new-2"]
    L += ["", f"**H-new-1 (post hoc follow-up): {h1['verdict']}.** Qualifying native cells (network AUC >= 0.99 in all seeds): "
          f"{len(h1['qualifying_cells'])}; S AUC >= 0.7 in {len(h1['S_auc_ge_0.7'])}; median Spearman >= 0.7 in "
          f"{len(h1['median_spearman_ge_0.7'])}.", "",
          f"**H-new-2 (rank test, 7 diffusion history-matched cells): Spearman {h2['spearman']:.2f}, {h2['reading']}.** "
          "x = AUC of S (morphs vs history-matched photos): " + ", ".join(f"{R.nice(c).split(' ')[0]} {v:.3f}" for c, v in
                                                                          zip(diff, x)) +
          "; y = median network AUC: " + ", ".join(f"{v:.3f}" for v in y) + "."]
    (OUT / f"fu_sharpness_m3{tag}.md").write_text("\n".join(L) + "\n")
    print("\n".join(L))


if __name__ == "__main__":
    main()
