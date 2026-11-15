"""FZ1: one evaluation of a score vector (release or head) on the A43 ladder, R1, benchmarks and StyleGAN3 sets.

evaluate(s43, sev, ssg) with
  s43: scores in A43 manifest order (2,024 rows),
  sev: {eval id: score} covering R1, frll_bona and the benchmark cells of fz1_common.eval_cells,
  ssg: {h3 / a37 id: score} for the StyleGAN3 rows (or None).
"""
import pathlib
import numpy as np
import fz1_common as K

A43_CONTRASTS = [("B20", "D20"), ("B", "D"), ("C20", "D20"), ("C", "D"), ("B20", "C20"), ("B", "C"),
                 ("D", "R0"), ("D20", "R0"), ("E", "R0"), ("R1", "R0"), ("A", "R0"), ("B20", "R0"), ("B", "R0")]


class Ctx:
    def __init__(self, B=10000, B_eer=2000, smoke=False):
        self.rows = K.a43_rows()
        self.g = K.a43_groups(self.rows)
        ev = K.eval_rows()
        self.ev_by_id = {r["id"]: r for r in ev}
        self.cells = K.eval_cells(ev)
        self.R1 = [r for r in ev if r["set"] == "mordiff" and r["family"] == "mordiff" and r["variant"] == "resmatch"]
        self.frll_bona = self.cells["FRLLM/amsl"][1]
        allp = sorted({p for r in self.rows for p in K.pers_a43(r)})
        evp = {p for c in self.cells.values() for rr in c for r in rr for p in K.pers_eval(r)}
        assert evp <= set(allp), sorted(evp - set(allp))[:5]
        self.D = K.Draw(allp, 200 if smoke else B, K.SEED_A43)
        self.B_eer = 100 if smoke else B_eer
        self.P = {k: [K.pers_a43(self.rows[i]) for i in v] for k, v in self.g.items()}
        self.P["R1"] = [K.pers_eval(r) for r in self.R1]
        self.W = {k: self.D.w(v) for k, v in self.P.items()}
        R4, R2, RX = K.sg3_rows()
        self.sg = {"morph": R4, "render": R2, "spread": RX}
        pairs = sorted({int(r["pair"]) for r in R4 + R2 + RX})
        ppos = {p: i for i, p in enumerate(pairs)}
        Wp = np.random.default_rng(K.SEED_SG3).multinomial(len(pairs), np.full(len(pairs), 1 / len(pairs)),
                                                           size=200 if smoke else B).astype(float)
        self.sgW = {k: Wp[:, [ppos[int(r["pair"])] for r in v]] for k, v in self.sg.items()}

    def eval_ids(self):
        ids = [r["id"] for r in self.R1]
        for m, nb, e7 in self.cells.values():
            ids += [r["id"] for r in m + nb + e7]
        return sorted(set(ids))

    def sg_ids(self):
        return [r["id"] for v in self.sg.values() for r in v]


def name6(r):
    return pathlib.PurePath(r["path"]).name[:6]


def evaluate(ctx, s43, sev, ssg=None):
    rows, g, D = ctx.rows, ctx.g, ctx.D
    s43 = np.asarray(s43, float)
    S = {k: s43[np.array(v)] for k, v in g.items()}
    S["R1"] = np.array([sev[r["id"]] for r in ctx.R1])
    out = {"a43": {}, "sg3": {}, "bench": {}}
    for a, b in A43_CONTRASTS:
        rep = K.wauc(S[a], S[b], ctx.W[a], ctx.W[b])
        out["a43"][f"{a} vs {b}"] = {"auc": K.auc(S[a], S[b]), "ci": K.ci(rep), "n": [len(S[a]), len(S[b])]}
    # thresholds: MorDIFF full cell (eval rows) and the 200 sampled published morphs of A43 (AD1's choice)
    m, nb, e7 = ctx.cells["MorDIFF"]
    eer_full, t_full = K.eer_thr(np.array([sev[r["id"]] for r in nb]), np.array([sev[r["id"]] for r in m]))
    eer_200, t_200 = K.eer_thr(S["R0"], S["A_reg"])
    k0 = {name6(rows[i]): s43[i] for i in g["R0"]}
    k1 = {name6(r): sev[r["id"]] for r in ctx.R1}
    common = sorted(set(k0) & set(k1))
    s0, s1 = np.array([k0[c] for c in common]), np.array([k1[c] for c in common])
    out["flag_R0_R1"] = {"thr_full_mordiff": dict(K.flag_change(s0, s1, common, t_full, D), eer_cell=eer_full),
                         "thr_200_sampled": dict(K.flag_change(s0, s1, common, t_200, D), eer_cell=eer_200)}
    out["neutral_above_smiling"] = {
        "frll_bona": K.neutral_above_smiling({name6(r): sev[r["id"]] for r in ctx.frll_bona}, D),
        "mordiff_bona_R0": K.neutral_above_smiling(k0, D)}
    Ce = D.C[:ctx.B_eer]
    for cell, (m, nb, e7) in ctx.cells.items():
        sm = np.array([sev[r["id"]] for r in m])
        pm = [K.pers_eval(r) for r in m]
        res = {"n_morph": len(m)}
        for lab, gr in (("native", nb), ("E7", e7)):
            sg_ = np.array([sev[r["id"]] for r in gr])
            pg = [K.pers_eval(r) for r in gr]
            e, _ = K.eer_thr(sg_, sm)
            sub = K.Draw.__new__(K.Draw)
            sub.per, sub.pos, sub.C = D.per, D.pos, Ce
            rep = K.weer(sm, sg_, sub.w(pm), sub.w(pg))
            res[lab] = {"eer": float(e), "ci": K.ci(rep), "auc": K.auc(sm, sg_), "n_genuine": len(gr)}
        out["bench"][cell] = res
    if ssg is not None:
        Sg = {k: np.array([ssg[r["id"]] for r in v]) for k, v in ctx.sg.items()}
        for a, b in (("morph", "render"), ("morph", "spread")):
            rep = K.wauc(Sg[a], Sg[b], ctx.sgW[a], ctx.sgW[b])
            out["sg3"][f"{a} vs {b}"] = {"auc": K.auc(Sg[a], Sg[b]), "ci": K.ci(rep), "n": [len(Sg[a]), len(Sg[b])]}
    return out


def fmt(x):
    return f"{x['auc']:.3f} [{x['ci'][0]:.3f}, {x['ci'][1]:.3f}]"
