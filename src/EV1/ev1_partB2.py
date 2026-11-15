"""Fixed-threshold re-read (EV1), amendment 1, Part B side: A3 neutral-only genuine class as the headline of the
imbalanced cells (nulls refit on the neutral-only cell; detector AUC, EER, paired excess) and A5 split-half choice of the
best non-content null (chosen on one half of the persons, reported on the other). Reuses ev1_partB's null and cell code.
Run: python3 -I src/EV1/ev1_partB2.py [--smoke]
"""
import csv, hashlib, json, sys, time, pathlib
import numpy as np

HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(HERE.parent / "C_cue_checks"))
import ev1_common as K  # noqa: E402
import ev1_partB as PB  # noqa: E402
import c_checks as CC  # noqa: E402

SMOKE = "--smoke" in sys.argv
B = 50 if SMOKE else K.B_FULL
T0 = time.time()
IMB = set(K.FRLLM) | set(K.DIM) | {"MAD22c_Webmorph"}


def log(*a):
    print(f"[{time.time() - T0:7.1f}s]", *a, flush=True)


def half(p):
    return int(hashlib.sha1(f"ev1-half-{p}".encode()).hexdigest(), 16) % 2


def build_cells(F, rows, I):
    """identical to ev1_partB.main's cell construction."""
    alpos = {p: i for i, p in enumerate(F["al_path"].tolist())}
    rawpos = {p: i for i, p in enumerate(F["raw_path"].tolist())}
    C17 = CC.cells()
    cells = []
    for f in K.FAMS:
        cc = C17.get(PB.A41_CELL[f])
        if cc is None:
            continue
        mi, gi = I.morph(f), I.bona(K.NATIVE_BONA[f])
        ix = np.r_[mi, gi]
        rr = [rows[i] for i in ix]
        alp = [str(K.MC / "smadcvpr_data" / r["path"]) for r in rr]
        keep = [j for j, p in enumerate(alp) if p in alpos]
        if len({rr[j]["label"] for j in keep}) < 2:
            continue
        ix, rr, alp = ix[keep], [rr[j] for j in keep], [alp[j] for j in keep]
        c = PB.Cell(f, f, [r["pers"] for r in rr], [int(r["label"]) for r in rr], [r["expr"] for r in rr], alp, rows=rr)
        c.eval_idx = ix
        c.al_idx = np.array([alpos[p] for p in alp])
        mr = [str(p) for p in cc["m_raw"] if str(p) in rawpos]
        br = [str(p) for p in cc["b_raw"] if str(p) in rawpos]
        rp = mr + br
        c.raw_idx = np.array([rawpos[p] for p in rp]) if rp else None
        c.raw_P = [CC.persons(pathlib.Path(p).name)[0] for p in rp]
        c.raw_E = [CC.persons(pathlib.Path(p).name)[1][0] if p in br else "03" for p in rp]
        c.raw_y = np.array([1] * len(mr) + [0] * len(br))
        cells.append(c)
    for f in PB.MAD22:
        cc = C17.get(f"MAD22c/{f}")
        if cc is None:
            continue
        alp = [str(p) for p in cc["m_al"]] + [str(p) for p in cc["b_al"]]
        y = [1] * len(cc["m_al"]) + [0] * len(cc["b_al"])
        rmap = {PB.stem(p): p for p in map(str, list(cc["m_raw"]) + list(cc["b_raw"])) if p in rawpos}
        keep = [j for j, p in enumerate(alp) if p in alpos and rmap.get(PB.stem(p))]
        alp, y = [alp[j] for j in keep], [y[j] for j in keep]
        if len(set(y)) < 2:
            continue
        P = [CC.persons(pathlib.Path(p).name)[0] for p in alp]
        E = ["".join(CC.persons(pathlib.Path(p).name)[1]) for p in alp]
        c = PB.Cell(f"MAD22c {f}", f"MAD22c_{f}", P, y, E, alp)
        c.al_idx = np.array([alpos[p] for p in alp])
        c.raw_idx = np.array([rawpos[rmap[PB.stem(p)]] for p in alp])
        c.raw_P, c.raw_y, c.raw_E, c.eval_idx = P, np.array(y), E, None
        cells.append(c)
    return cells


def neutral_only(c):
    keep = np.array([(yy == 1) or (e in ("03", "0303")) for yy, e in zip(c.y, c.expr)])
    n = PB.Cell(c.name, c.fam, [p for p, k in zip(c.P, keep) if k], c.y[keep], c.expr[keep],
                [p for p, k in zip(c.al, keep) if k], rows=None if c.rows is None else [r for r, k in zip(c.rows, keep) if k])
    n.al_idx = c.al_idx[keep]
    n.eval_idx = None if c.eval_idx is None else c.eval_idx[keep]
    if c.rows is None:              # MAD22c: raw list aligned to items
        n.raw_idx = c.raw_idx[keep]
        n.raw_P, n.raw_y, n.raw_E = n.P, n.y, list(np.array(c.raw_E)[keep])
    else:
        kr = np.array([(yy == 1) or (e == "03") for yy, e in zip(c.raw_y, c.raw_E)])
        n.raw_idx = c.raw_idx[kr]
        n.raw_P = [p for p, k in zip(c.raw_P, kr) if k]
        n.raw_y = c.raw_y[kr]
        n.raw_E = [e for e, k in zip(c.raw_E, kr) if k]
    return n


def main():
    F = dict(np.load(K.BIG / ("feat_smoke.npz" if SMOKE else "feat.npz"), allow_pickle=False))
    rows = [r for r in K.eval_rows() if r["set"] != "mad22" and r["variant"] != "chip"]
    I = K.Index(rows)
    ids = [r["id"] for r in rows]
    cells = build_cells(F, rows, I)
    allp = sorted({p for r in rows if r["pers"] for p in r["pers"]})
    D = K.Draw(allp, B, K.SEED)
    dets = K.detectors()
    if SMOKE:
        dets = [d for d in dets if d["name"] in ("MADation ViT-L/14 release", "SelfMAD release, own preprocessing")]
    S = {d["name"]: K.load_scores(d, "eval", ids)[0] for d in dets}
    CEL, DET, SPL = [], [], []
    for c0 in cells:
        variants = [("all photos", c0)] + ([("neutral-only", neutral_only(c0))] if c0.fam in IMB else [])
        for sub, c in variants:
            nul, W = PB.nulls_for_with_raw(c, F, D)
            if sub == "neutral-only":
                nul = {k: v for k, v in nul.items() if not k.startswith("file (A41 table)")}
            nul = {("smiling-half label" if k == "expression label" else k): v for k, v in nul.items()}
            y = c.y
            nonc = {k: v for k, v in nul.items() if v["kind"].startswith("non-content")}
            best = max(nonc, key=lambda k: nonc[k]["O"])
            best_al = max((k for k, v in nul.items() if v["kind"] == "non-content aligned"), key=lambda k: nul[k]["O"])
            CEL.append([c.name, sub, int((y == 1).sum()), int((y == 0).sum()), best, nonc[best]["O"], nonc[best]["O"] < 0.90,
                        best_al, nul[best_al]["O"], nul[best_al]["O"] < 0.90, nul["thumbnail 32 x 32 grey regression"]["O"]])
            # ---- A5 split-half on per-image nulls
            hp = [set(half(p) for p in pp) for pp in c.P]
            inh = [np.array([h == {k} for h in hp]) for k in (0, 1)]
            per = {k: v for k, v in nonc.items() if v["score"] is not None}
            for sel_h, rep_h in ((0, 1), (1, 0)):
                ms, mr = inh[sel_h], inh[rep_h]
                Osel = {}
                for k, v in per.items():
                    sc = v["score"]
                    a = K.auc(sc[ms & (y == 1)], sc[ms & (y == 0)])
                    fold = "regression" not in k
                    Osel[k] = (max(a, 1 - a) if fold else a, (-1 if (fold and a < 0.5) else 1))
                ch = max(Osel, key=lambda k: Osel[k][0])
                sc = Osel[ch][1] * per[ch]["score"]
                ok = (mr & (y == 1)).sum() >= 5 and (mr & (y == 0)).sum() >= 5
                arep = K.auc(sc[mr & (y == 1)], sc[mr & (y == 0)]) if ok else float("nan")
                SPL.append([c.name, sub, f"choose on half {sel_h}, report on half {rep_h}", int((ms & (y == 1)).sum()), int((ms & (y == 0)).sum()),
                            int((mr & (y == 1)).sum()), int((mr & (y == 0)).sum()), ch, Osel[ch][0], arep, (arep < 0.90) if ok else None])
            if c.eval_idx is None:
                continue
            nb = nul[best]
            for d in dets:
                sc = S[d["name"]][c.eval_idx]
                if not np.isfinite(sc).all():
                    continue
                m_, b_ = sc[y == 1], sc[y == 0]
                a = K.auc(m_, b_)
                rep = K.wauc(m_, b_, W[:, y == 1], W[:, y == 0])
                exc = rep - (nb["rep"] if (nb["rep"] is not None and nb["score"] is not None) else nb["O"])
                DET.append([d["name"], d["block"], c.name, sub, a, *K.ci(rep), K.eer_fast(b_, m_)[0], best, nb["O"], a - nb["O"], *K.ci(exc)])
        log(c0.name, [(r[1], r[4], round(r[5], 3), r[6]) for r in CEL if r[0] == c0.name],
            [(r[2][:12], r[7], round(r[9], 3)) for r in SPL if r[0] == c0.name])
    summ = {}
    for sub in ("all photos", "neutral-only"):
        R = [r for r in CEL if r[1] == sub]
        summ[sub] = {"n_cells": len(R), "diagnostic": [r[0] for r in R if r[6]], "diagnostic_aligned_only": [r[0] for r in R if r[9]]}
        for sp in ("choose on half 0, report on half 1", "choose on half 1, report on half 0"):
            Q = [r for r in SPL if r[1] == sub and r[2] == sp]
            summ[sub][sp] = {"diagnostic": [r[0] for r in Q if r[10]], "n": len(Q), "not_measurable": [r[0] for r in Q if r[10] is None]}
        a, b = (set(summ[sub][sp]["diagnostic"]) for sp in ("choose on half 0, report on half 1", "choose on half 1, report on half 0"))
        summ[sub]["split_count_unstable"] = a != b or a != set(summ[sub]["diagnostic"])
    # headline: neutral-only where imbalanced, else all photos
    head = {}
    for r in CEL:
        if (r[0] if not r[0].startswith("MAD22c") else "MAD22c_" + r[0].split()[-1]) in IMB:
            if r[1] == "neutral-only":
                head[r[0]] = r
        elif r[1] == "all photos":
            head[r[0]] = r
    summ["headline_diagnostic_cells"] = [k for k, r in head.items() if r[6]]
    summ["headline_n_cells"] = len(head)
    log(json.dumps(summ)[:2000])
    if SMOKE:
        print("smoke ok")
        return
    W_ = lambda fn_, hdr, R: (lambda fh: (csv.writer(fh).writerow(hdr), csv.writer(fh).writerows(R)))(open(K.OUT / fn_, "w", newline=""))  # noqa: E731
    W_("AM_B_cells_neutral.csv", ["cell", "genuine_class", "n_morph", "n_genuine", "best_noncontent_null", "O", "diagnostic",
                                  "best_aligned_null", "O_aligned", "diagnostic_aligned_only", "thumbnail_auc"], CEL)
    W_("AM_B_detectors_neutral.csv", ["detector", "block", "cell", "genuine_class", "auc", "lo95", "hi95", "eer_pct", "best_null",
                                      "null_O", "excess", "excess_lo95", "excess_hi95"], DET)
    W_("AM_B_splithalf.csv", ["cell", "genuine_class", "split", "n_morph_sel", "n_gen_sel", "n_morph_rep", "n_gen_rep", "chosen_null",
                              "O_on_selection_half", "auc_on_report_half", "diagnostic_on_report_half"], SPL)
    json.dump({"B": B, "seed": K.SEED, "summary": summ}, open(K.OUT / "AM_partB.json", "w"), indent=1)
    log("written")


if __name__ == "__main__":
    main()
