"""Fixed-threshold re-read (EV1), Part B: morph-blind null rows above the detectors, paired excess over the best
non-content null, diagnostic-cell count, null-conditional AUC, expression-balanced reading.
Needs /mnt/t7/smad_next/EV1/feat.npz (ev1_feat.py). Run: python3 -I src/EV1/ev1_partB.py [--smoke]
"""
import csv, json, sys, time, pathlib
import numpy as np

HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(HERE.parent / "C_cue_checks"))
import ev1_common as K  # noqa: E402
import c_checks as CC  # noqa: E402

SMOKE = "--smoke" in sys.argv
B = 50 if SMOKE else K.B_FULL
T0 = time.time()
A41 = K.MC / "experiments/A41_shortcut-proof-zero-gpu/raw/results/a41_files.json"
MAD = pathlib.Path("/mnt/t7/smad_heldout/mad22_incoming/marco_owncloud_20261109T103840Z/author_files/original_sorted")
MADA = pathlib.Path("/mnt/t7/smad_heldout/mad22_canonical_E7_inputs_v3_20261109T113746Z/native")
MAD22 = ("FaceMorpher", "MIPGAN_I", "MIPGAN_II", "OpenCV", "Webmorph")
A41_CELL = {**{f: f"FRLL-Morphs/{f}" for f in K.FRLLM}, "mordiff": "MorDIFF", **{f: f"DiM/{f}" for f in K.DIM}}


def log(*a):
    print(f"[{time.time() - T0:7.1f}s]", *a, flush=True)


def stem(p):
    n = pathlib.PurePath(p).stem
    return n[:-5] if n.endswith("_orig") else n


def oof_lr(X, y, P, C=1.0, max_iter=2000):
    """out-of-fold decision scores: item tested in the fold of its first person; trained on items with no person in
    that fold (C3 fold rule)."""
    from sklearn.linear_model import LogisticRegression
    from sklearn.preprocessing import StandardScaler
    from sklearn.pipeline import make_pipeline
    fo = {p: CC.fold_of(p) for pp in P for p in pp}
    first = np.array([fo[pp[0]] for pp in P])
    s = np.full(len(y), np.nan)
    for f in range(5):
        te = first == f
        tr = np.array([all(fo[q] != f for q in pp) for pp in P])
        if not te.any() or len(set(y[tr])) < 2:
            continue
        m = make_pipeline(StandardScaler(), LogisticRegression(C=C, max_iter=max_iter)).fit(X[tr], y[tr])
        s[te] = m.decision_function(X[te])
    return s


def cat_score(x, y):
    """categorical attribute -> in-sample morph rate per category (as c_checks.cat_o)."""
    x = np.asarray(x).astype(str)
    out = np.zeros(len(x))
    nm, nb = max((y == 1).sum(), 1), max((y == 0).sum(), 1)
    for c in np.unique(x):
        rm, rb = ((x == c) & (y == 1)).sum() / nm, ((x == c) & (y == 0)).sum() / nb
        out[x == c] = rm / (rm + rb)
    return out


class Cell:
    """items: morphs then genuine; persons; per-item arrays."""

    def __init__(self, name, fam, P, y, expr, al_paths, raw_paths=None, rows=None):
        self.name, self.fam, self.P, self.y, self.expr = name, fam, P, np.asarray(y), np.asarray(expr)
        self.al, self.raw, self.rows = al_paths, raw_paths, rows


def nulls_for(cell, F, D):
    """dict null name -> (kind, per-item score or None, point O/AUC, reps or None, note)."""
    y, P = cell.y, cell.P
    W = D.w(P)
    wm, wg = W[:, y == 1], W[:, y == 0]
    out = {}

    def add(name, kind, sc, fold=True, items=None, note=""):
        if items is None:
            yy, ww_m, ww_g = y, wm, wg
        else:
            yy, ww = items
            ww_m, ww_g = ww[:, yy == 1], ww[:, yy == 0]
        ok = np.isfinite(sc)
        if ok.sum() < len(sc):
            note += f" ({len(sc) - ok.sum()} items without a score dropped)"
        pos, neg = sc[(yy == 1) & ok], sc[(yy == 0) & ok]
        if len(pos) < 2 or len(neg) < 2:
            print("  null skipped (too few scored items):", cell.name, name, flush=True)
            return
        a = K.auc(pos, neg)
        sgn = -1.0 if (fold and a < 0.5) else 1.0
        rep = K.wauc(sgn * pos, sgn * neg, ww_m[:, ok[yy == 1]], ww_g[:, ok[yy == 0]])
        out[name] = {"kind": kind, "score": sgn * sc if items is None else None, "O": max(a, 1 - a) if fold else a,
                     "rep": rep, "note": note.strip()}

    al = cell.al_idx
    # ---- file attributes
    if cell.rows is not None:
        r = cell.rows
        w_ = np.array([float(x["native_w"]) for x in r]); h_ = np.array([float(x["native_h"]) for x in r])
        b_ = np.array([float(x["file_bytes"]) for x in r]); ied = np.array([float(x["ied"]) for x in r])
        X = np.c_[w_, h_, b_, b_ / (w_ * h_), ied]
        for j, nm in enumerate(("width", "height", "bytes", "bytes per pixel", "inter-eye distance")):
            add(f"file: {nm}", "non-content file", X[:, j])
        add("file: 5-attribute regression", "non-content file", oof_lr(X, y, P), fold=False)
        a41 = json.load(open(A41))["DC-A"]["cells"][A41_CELL[cell.fam]]["O"]
        for k, v in a41.items():
            if v is None:
                continue
            out[f"file (A41 table): {k}"] = {"kind": "non-content file", "score": None, "O": float(v), "rep": None,
                                             "note": "stored file, point value from the file-table study (A41)"}
    else:  # corrected MAD22: raw headers
        ri = cell.raw_idx
        w_, h_, b_ = F["raw_w"][ri].astype(float), F["raw_h"][ri].astype(float), F["raw_bytes"][ri].astype(float)
        X = np.c_[w_, h_, b_, b_ / (w_ * h_)]
        for j, nm in enumerate(("width", "height", "bytes", "bytes per pixel")):
            add(f"file: {nm}", "non-content file", X[:, j])
        cont, sub = F["raw_container"][ri], F["raw_sub"][ri]
        add("file: container", "non-content file", cat_score(cont, y), note="in-sample category rate")
        add("file: chroma subsampling", "non-content file", cat_score(np.char.add(np.char.add(cont, "|"), sub), y),
            note="in-sample category rate (container|subsampling)")
        oh = np.c_[[(cont == c).astype(float) for c in np.unique(cont)]].T
        sh = np.c_[[(sub == c).astype(float) for c in np.unique(sub)]].T
        add("file: 6-attribute regression", "non-content file", oof_lr(np.c_[X, oh, sh], y, P), fold=False)
    # ---- colour (aligned frame), border, expression
    Xc = np.c_[F["al_mean"][al], F["al_std"][al]]
    add("colour: 6 statistics, aligned frame", "non-content aligned", oof_lr(Xc, y, P), fold=False)
    add("border: zero-border fraction", "non-content aligned", F["al_zero"][al].astype(float))
    ex = np.array([1.0 if e in ("03", "0303") else 0.0 if e in ("08", "0808") else 0.5 for e in cell.expr])
    add("expression label", "non-content aligned", ex,
        note={"frllm": "morph expression inferred (C1 probe)", "dim": "morphs neutral by README"}.get(
            K.FAM_SET.get(cell.fam, ""), "from names"))
    # ---- colour of the stored file (own item list = raw files; paired at the person level)
    if cell.raw_idx is not None:
        ri = cell.raw_idx
        add("colour: 6 statistics, stored file", "non-content file",
            oof_lr(np.c_[F["raw_mean"][ri], F["raw_std"][ri]], y, P), fold=False, note="framing-confounded")
    # ---- content null
    add("thumbnail 32 x 32 grey regression", "content", oof_lr(F["al_thumb"][al].astype(float), y, P, C=0.1, max_iter=5000),
        fold=False)
    return out, W


def nullcond(det, nul, y, W=None, q=5):
    """overlap-weighted AUC within quintiles of the null score (pooled). Returns (auc or None, n usable strata)."""
    edges = np.quantile(nul, np.linspace(0, 1, q + 1)[1:-1])
    st = np.digitize(nul, edges)
    num, den, used = 0.0, 0.0, 0
    for s in np.unique(st):
        k = st == s
        nm, ng = int((k & (y == 1)).sum()), int((k & (y == 0)).sum())
        if nm < 5 or ng < 5:
            continue
        a = K.auc(det[k & (y == 1)], det[k & (y == 0)])
        wt = nm * ng / (nm + ng)
        num += wt * a; den += wt; used += 1
    return (num / den if den else None), used


def main():
    F = dict(np.load(K.BIG / ("feat_smoke.npz" if SMOKE else "feat.npz"), allow_pickle=False))
    alpos = {p: i for i, p in enumerate(F["al_path"].tolist())}
    rawpos = {p: i for i, p in enumerate(F["raw_path"].tolist())}
    rows = [r for r in K.eval_rows() if r["set"] != "mad22" and r["variant"] != "chip"]
    I = K.Index(rows)
    ids = [r["id"] for r in rows]
    C17 = CC.cells()
    cells = []
    for f in K.FAMS:
        cc = C17.get(A41_CELL[f])
        if cc is None:
            assert SMOKE, f
            continue
        mi, gi = I.morph(f), I.bona(K.NATIVE_BONA[f])
        ix = np.r_[mi, gi]
        rr = [rows[i] for i in ix]
        alp = [str(K.MC / "smadcvpr_data" / r["path"]) for r in rr]
        if SMOKE:
            keep = [j for j, p in enumerate(alp) if p in alpos]
            if not keep or len({rr[j]["label"] for j in keep}) < 2:
                continue
            ix, rr, alp = ix[keep], [rr[j] for j in keep], [alp[j] for j in keep]
        c = Cell(f, f, [r["pers"] for r in rr], [int(r["label"]) for r in rr], [r["expr"] for r in rr], alp, rows=rr)
        c.eval_idx = ix
        c.al_idx = np.array([alpos[p] for p in alp])
        # stored files: own item list (morph raw then genuine raw); persons from names
        rp = [str(p) for p in cc["m_raw"]] + [str(p) for p in cc["b_raw"]]
        rp = [p for p in rp if p in rawpos]
        c.raw_idx = np.array([rawpos[p] for p in rp]) if rp else None
        if c.raw_idx is not None:
            c.raw_P = [CC.persons(pathlib.Path(p).name)[0] for p in rp]
            c.raw_y = np.array([1] * sum(p in set(map(str, cc["m_raw"])) for p in rp) + [0] * sum(p in set(map(str, cc["b_raw"])) for p in rp))
        cells.append(c)
    for f in MAD22:
        cc = C17.get(f"MAD22c/{f}")
        if cc is None:
            continue
        alp = [str(p) for p in cc["m_al"]] + [str(p) for p in cc["b_al"]]
        y = [1] * len(cc["m_al"]) + [0] * len(cc["b_al"])
        keep = [j for j, p in enumerate(alp) if p in alpos]
        alp, y = [alp[j] for j in keep], [y[j] for j in keep]
        P = [CC.persons(pathlib.Path(p).name)[0] for p in alp]
        E = ["".join(CC.persons(pathlib.Path(p).name)[1]) for p in alp]
        c = Cell(f"MAD22c {f}", f"MAD22c_{f}", P, y, E, alp)
        c.al_idx = np.array([alpos[p] for p in alp])
        # raw headers aligned to the aligned items by stem
        rmap = {stem(p): p for p in map(str, list(cc["m_raw"]) + list(cc["b_raw"])) if p in rawpos}
        rp = [rmap.get(stem(p)) for p in alp]
        if SMOKE:
            kk = [j for j, q in enumerate(rp) if q]
            alp, y, P, E, rp = [alp[j] for j in kk], [y[j] for j in kk], [P[j] for j in kk], [E[j] for j in kk], [rp[j] for j in kk]
            c = Cell(f"MAD22c {f}", f"MAD22c_{f}", P, y, E, alp)
            c.al_idx = np.array([alpos[p] for p in alp])
            if len(set(y)) < 2:
                continue
        assert all(rp), "MAD22c raw/aligned stem mismatch"
        c.raw_idx = np.array([rawpos[p] for p in rp])
        c.raw_P, c.raw_y = P, np.array(y)
        c.eval_idx = None
        cells.append(c)
    allp = sorted({p for r in rows if r["pers"] for p in r["pers"]})
    D = K.Draw(allp, B, K.SEED)
    log(len(cells), "cells")
    # detectors and morph-free networks
    dets = K.detectors()
    mf = K.morph_free_networks()
    if SMOKE:
        dets = [d for d in dets if d["name"] in ("MADation ViT-L/14 release", "SelfMAD release, own preprocessing")]
        mf = mf[:1]
    S = {}
    for d in dets + mf:
        S[d["name"]] = K.load_scores(d, "eval", ids)[0]
    NUL, CELLS, DET, EXP = [], [], [], []
    for c in cells:
        # raw-file colour uses the raw list; patch nulls_for for that item list
        nul, W = nulls_for_with_raw(c, F, D)
        y = c.y
        noncontent = {k: v for k, v in nul.items() if v["kind"].startswith("non-content")}
        best = max(noncontent, key=lambda k: noncontent[k]["O"])
        best_al = max((k for k, v in nul.items() if v["kind"] == "non-content aligned"), key=lambda k: nul[k]["O"])
        per_image = {k: v for k, v in noncontent.items() if v["score"] is not None}
        best_pi = max(per_image, key=lambda k: per_image[k]["O"])
        for k, v in nul.items():
            NUL.append([c.name, k, v["kind"], int((y == 1).sum()), int((y == 0).sum()), v["O"], *(K.ci(v["rep"]) if v["rep"] is not None else ["", ""]), v["note"]])
        mfres = {}
        if c.eval_idx is not None:
            for d in mf:
                sc = S[d["name"]][c.eval_idx]
                b_, m_ = sc[y == 0], sc[y == 1]
                mfres[d["name"]] = {"auc": K.auc(m_, b_), "eer": K.eer_fast(b_, m_)[0],
                                    "ci": K.ci(K.wauc(m_, b_, W[:, y == 1], W[:, y == 0]))}
                NUL.append([c.name, d["name"], "morph-free network", int((y == 1).sum()), int((y == 0).sum()),
                            mfres[d["name"]]["auc"], *mfres[d["name"]]["ci"], f"EER {mfres[d['name']]['eer']:.2f}%"])
        diag = noncontent[best]["O"] < 0.90
        diag_al = nul[best_al]["O"] < 0.90
        diag_mf = diag and bool(mfres) and all(v["auc"] < 0.90 for v in mfres.values())
        CELLS.append([c.name, int((y == 1).sum()), int((y == 0).sum()), best, noncontent[best]["O"], diag, best_al,
                      nul[best_al]["O"], diag_al, nul["thumbnail 32 x 32 grey regression"]["O"],
                      max([v["auc"] for v in mfres.values()]) if mfres else "", diag_mf if mfres else "", best_pi])
        if c.eval_idx is None:
            log(c.name, "best", best, round(noncontent[best]["O"], 3), "diag", diag, "| aligned", best_al,
                round(nul[best_al]["O"], 3), "| thumb", round(nul["thumbnail 32 x 32 grey regression"]["O"], 3))
            continue
        nb = nul[best]
        for d in dets:
            sc = S[d["name"]][c.eval_idx]
            if not np.isfinite(sc).all():
                continue
            m_, b_ = sc[y == 1], sc[y == 0]
            a = K.auc(m_, b_)
            rep = K.wauc(m_, b_, W[:, y == 1], W[:, y == 0])
            exc = rep - (nb["rep"] if nb["rep"] is not None and nb["score"] is not None and len(nb["rep"]) == len(rep) else nb["O"])
            nc, nused = nullcond(sc, per_image[best_pi]["score"], y)
            nca, nausd = nullcond(sc, nul[best_al]["score"], y)
            DET.append([d["name"], d["block"], c.name, a, *K.ci(rep), best, nb["O"], a - nb["O"], *K.ci(exc),
                        best_pi, "" if nc is None else nc, nused, best_al, "" if nca is None else nca, nausd])
            # expression-balanced
            neu, smi = (y == 0) & (c.expr == "03"), (y == 0) & (c.expr == "08")
            an, as_ = K.auc(m_, sc[neu]), K.auc(m_, sc[smi])
            rn = K.wauc(m_, sc[neu], W[:, y == 1], W[:, neu])
            rs = K.wauc(m_, sc[smi], W[:, y == 1], W[:, smi])
            EXP.append([d["name"], d["block"], c.name, a, an, *K.ci(rn - rep), as_, *K.ci(rs - rep),
                        K.eer_fast(b_, m_)[0], K.eer_fast(sc[neu], m_)[0], K.eer_fast(sc[smi], m_)[0]])
        log(c.name, "best", best, round(noncontent[best]["O"], 3), "diag", diag, "| aligned", best_al, round(nul[best_al]["O"], 3),
            "| thumb", round(nul["thumbnail 32 x 32 grey regression"]["O"], 3))
    # ---------------- falsifier summary
    summ = {"n_cells": len(CELLS), "diagnostic_primary": [r[0] for r in CELLS if r[5]],
            "diagnostic_aligned_only": [r[0] for r in CELLS if r[8]],
            "diagnostic_primary_and_morph_free": [r[0] for r in CELLS if r[11] is True]}
    rel_names = [d["name"] for d in dets if d["block"] == "release"]
    with_overlap = [(r[0], r[2]) for r in DET if r[0] in rel_names and r[12] != ""]
    summ["release_cells_with_overlap_primary"] = len(with_overlap)
    summ["nullcond_within_0.03_all"] = (all(abs(r[12] - r[3]) <= 0.03 for r in DET if r[0] in rel_names and r[12] != "")
                                        if with_overlap else "vacuous (no cell with overlap)")
    _al = [abs(r[15] - r[3]) for r in DET if r[0] in rel_names and r[15] != ""]
    summ["nullcond_aligned_within_0.03_all"] = all(x <= 0.03 for x in _al) if _al else "vacuous (no cell with overlap)"
    summ["release_cells_with_overlap_aligned"] = len(_al)
    summ["nullcond_aligned_max_abs_diff"] = max([abs(r[15] - r[3]) for r in DET if r[0] in rel_names and r[15] != ""], default=None)
    gaps = [abs(r[10] - r[9]) for r in EXP if r[0] in rel_names]
    summ["expression_eer_gap_max_points"] = max(gaps) if gaps else None
    summ["expression_row_crossed_out"] = bool(gaps) and all(g <= 2 for g in gaps)
    pred = {}
    for d in mf:
        e = [r for r in NUL if r[1] == d["name"]]
        pred[d["name"]] = int(sum(float(r[8].split()[1].rstrip("%")) <= 2.6 for r in e))
    summ["morph_free_cells_eer_le_2.6"] = pred
    summ["falsifier_dropped_10plus_diagnostic"] = len(summ["diagnostic_primary"]) >= 10
    log(json.dumps(summ)[:1500])
    if SMOKE:
        print("smoke ok")
        return
    out = K.OUT
    W_ = lambda fn, hdr, R: (lambda fh: (csv.writer(fh).writerow(hdr), csv.writer(fh).writerows(R)))(open(out / fn, "w", newline=""))  # noqa: E731
    W_("B_null_rows.csv", ["cell", "null", "kind", "n_morph", "n_genuine", "auc_or_O", "lo95", "hi95", "note"], NUL)
    W_("B_cells.csv", ["cell", "n_morph", "n_genuine", "best_noncontent_null", "best_noncontent_O", "diagnostic_primary",
                       "best_aligned_null", "best_aligned_O", "diagnostic_aligned_only", "thumbnail_auc",
                       "best_morph_free_auc", "diagnostic_primary_and_morph_free", "best_per_image_noncontent_null"], CELLS)
    W_("B_detectors.csv", ["detector", "block", "cell", "auc", "lo95", "hi95", "best_noncontent_null", "null_O", "excess",
                           "excess_lo95", "excess_hi95", "stratifying_null", "nullcond_auc", "usable_strata",
                           "aligned_stratifying_null", "nullcond_auc_aligned", "usable_strata_aligned"], DET)
    W_("B_expression.csv", ["detector", "block", "cell", "auc_all", "auc_neutral_only", "d_neutral_lo95", "d_neutral_hi95",
                            "auc_smiling_only", "d_smiling_lo95", "d_smiling_hi95", "eer_all", "eer_neutral_only", "eer_smiling_only"], EXP)
    json.dump({"B": B, "seed": K.SEED, "summary": summ}, open(out / "B_partB.json", "w"), indent=1)
    log("written")


def nulls_for_with_raw(c, F, D):
    """nulls_for, with the stored-file colour null computed on the raw item list and its own weights."""
    raw_idx = c.raw_idx
    c.raw_idx = None if c.rows is not None else raw_idx   # MAD22c: raw list is aligned to items already
    out, W = nulls_for(c, F, D)
    c.raw_idx = raw_idx
    if c.rows is not None and raw_idx is not None:
        Wr = D.w(c.raw_P)
        sc = oof_lr(np.c_[F["raw_mean"][raw_idx], F["raw_std"][raw_idx]], c.raw_y, c.raw_P)
        a = K.auc(sc[c.raw_y == 1], sc[c.raw_y == 0])
        rep = K.wauc(sc[c.raw_y == 1], sc[c.raw_y == 0], Wr[:, c.raw_y == 1], Wr[:, c.raw_y == 0])
        out["colour: 6 statistics, stored file"] = {"kind": "non-content file", "score": None, "O": a, "rep": rep,
                                                    "note": "stored files (own item list, paired by person draw); framing-confounded"}
    return out, W


if __name__ == "__main__":
    main()
