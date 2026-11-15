"""Signal isolation by paired differences (PD1), landmark family: analysis (Q1 to Q5, benchmark cells).

  python3 -I analyse.py first                    first small pass: DINOv3 mean patch token, OpenCV engine, fold 0
  python3 -I analyse.py full --feat dino_mean    everything for one feature -> OUT/scores/<feat>/*.json, RES/*.json
Definitions and fixed readings: experiments/PD1_signal-isolation-paired-differences/landmark/prereg.md.
"""
import argparse
import json
import os
import pathlib
import sys
import time

os.environ.setdefault("OMP_NUM_THREADS", "1")
os.environ.setdefault("OPENBLAS_NUM_THREADS", "1")
import numpy as np  # noqa: E402

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import pd1_common as K  # noqa: E402
import pd1_lib as L  # noqa: E402

ENGINES = ("opencv", "facemorpher")
AR1_RUNGS = ("R0", "R2w", "R2wm", "R3m", "R3", "R4")
STEPS = [("pipeline", "R0", "R2w"), ("mirror_mix", "R2w", "R3m"), ("mirror_mix_matched", "R2wm", "R3m"),
         ("same_person_mix", "R2w", "R3"), ("second_identity", "R3", "R4"), ("whole_morph", "R2w", "R4"),
         ("photo_to_morph", "R0", "R4")]
CONTRASTS = [("x1_vs_x3", "R2w", "R4"), ("x0_vs_x3", "R0", "R4"), ("x2_vs_x3", "R3", "R4"), ("xm_vs_x3", "R3m", "R4"),
             ("x0_vs_x1", "R0", "R2w"), ("x1_vs_x2", "R2w", "R3"), ("x1_vs_xm", "R2w", "R3m"),
             ("x1m_vs_xm", "R2wm", "R3m"), ("x0_vs_x2", "R0", "R3"), ("x0_vs_xm", "R0", "R3m")]
VARIANTS = ("none", "soft", "pipe", "both", "softh")
HEADS = ("one", "two")
FLOOR_CONTRASTS = ("x1_vs_x3", "x0_vs_x3", "x2_vs_x3", "xm_vs_x3", "x0_vs_x1", "x1_vs_x2", "x1_vs_xm", "x1m_vs_xm")
CS = (1e-3, 1e-2, 1e-1, 1.0)
TAG = ""


def jdump(obj, path):
    path = pathlib.Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    json.dump(obj, open(path, "w"), indent=1, default=lambda o: o.tolist() if hasattr(o, "tolist") else str(o))


def r3(x):
    return None if x is None else round(float(x), 4)


# ------------------------------------------------------------------------------------------------ cues / floor
def load_cues(lst="ar1"):
    """AF0's cached statistics (read only, same function and names) plus PD1's own files for ids AF0 does not cover."""
    out, names = {}, None
    files = [f for f in (K.AF0 / "cues").glob("*.npz") if "smoke" not in f.name]
    files += [f for f in (K.OUT / "cues").glob(f"{lst}*.npz") if "limit" not in f.name]
    for f in files:
        z = np.load(f)
        names = list(z["names"])
        for i, c in zip(z["ids"], z["cues"]):
            out[str(i)] = c
    return out, names


def floor(D, cues, names, pos_ids, pos_p, neg_ids, neg_p):
    """best folded AUC among the 27 statistics on these images; replicate array signed like the point estimate."""
    P = np.stack([cues[i] for i in pos_ids])
    N = np.stack([cues[i] for i in neg_ids])
    best = (-1, None, None)
    per = {}
    for j, nm in enumerate(names):
        a = K.auc(P[:, j], N[:, j])
        per[nm] = r3(a)
        if L.fold_auc(a) > best[0]:
            best = (L.fold_auc(a), j, a)
    j, a = best[1], best[2]
    rep = K.wauc(P[:, j], N[:, j], D.w(pos_p), D.w(neg_p))
    if a < 0.5:
        rep = 1 - rep
    return dict(best=names[j], auc=r3(best[0]), ci=K.ci(rep), lapvar=per.get("lapvar"),
                lapvar_face=per.get("lapvar_face")), rep


# ------------------------------------------------------------------------------------------------ data sets
class Ext:
    """external sets for one feature: SMDD fit/test, benchmark, H1, AF0, graded."""

    def __init__(self, feat):
        self.feat = feat
        self.rows = {n: K.rows(K.OUT / "lists" / f"{n}.csv") for n in ("smdd", "bench", "h1", "af0", "ar1g")}
        self.F = {n: L.load(feat, n) for n in self.rows}

    def smdd(self, split):
        rr = [r for r in self.rows["smdd"] if r["split"] == split]
        ren = {r["p1"]: self.F["smdd"].get(r["id"]) for r in rr if r["rung"] == "render"}
        sma = {r["p1"]: self.F["smdd"].get(r["id"]) for r in rr if r["rung"] == "small"}
        keys = [k for k in sorted(ren) if ren[k] is not None and sma.get(k) is not None]
        if not keys:
            return None, None
        return np.stack([ren[k] for k in keys]), np.stack([sma[k] for k in keys])

    def bench_cells(self):
        """-> dict name -> dict(native, native_neutral, e7, morph) arrays (None where missing)."""
        F, rr = self.F["bench"], self.rows["bench"]
        if not F:
            return {}

        def arr(sel):
            v = [F[r["id"]] for r in sel if r["id"] in F]
            return np.stack(v) if v and len(v) == len(sel) else None

        fr_nat = [r for r in rr if r["pool"] == "frllm_frll_bona" and r["rung"] == "native"]
        m_nat = [r for r in rr if r["pool"] == "mad22_BonaFide" and r["rung"] == "native"]
        out = {}
        for fam in ("amsl", "facemorpher", "opencv", "webmorph"):
            c = f"frllm_{fam}"
            out[f"FRLL-Morphs {fam}"] = dict(
                native=arr(fr_nat), native_neutral=arr([r for r in fr_nat if "_03_orig" in r["path"]]),
                e7=arr([r for r in rr if r["pool"] == c and r["rung"] == "e7"]),
                morph=arr([r for r in rr if r["pool"] == c and r["rung"] == "morph"]))
        for fam in ("FaceMorpher", "OpenCV", "Webmorph"):
            c = f"mad22_{fam}"
            out[f"MAD22 {fam}"] = dict(
                native=arr(m_nat), native_neutral=arr([r for r in m_nat if r["path"].endswith("_03.png")]),
                e7=arr([r for r in rr if r["pool"] == c and r["rung"] == "e7"]),
                morph=arr([r for r in rr if r["pool"] == c and r["rung"] == "morph"]))
        return out

    def frll_soft_pairs(self):
        """FRLL native frames and their E7 OpenCV-family frames, paired by file stem (diagnostic only)."""
        F, rr = self.F["bench"], self.rows["bench"]
        nat = {pathlib.Path(r["path"]).name.replace("_orig.png", ""): r["id"] for r in rr
               if r["pool"] == "frllm_frll_bona" and r["rung"] == "native"}
        e7 = {pathlib.Path(r["path"]).name.replace("_resmatch_opencv.png", ""): r["id"] for r in rr
              if r["pool"] == "frllm_opencv" and r["rung"] == "e7"}
        ks = [k for k in sorted(nat) if k in e7 and nat[k] in F and e7[k] in F]
        if not ks:
            return None, None
        return np.stack([F[nat[k]] for k in ks]), np.stack([F[e7[k]] for k in ks])

    def h1(self):
        F, rr = self.F["h1"], self.rows["h1"]
        b = [F[r["id"]] for r in rr if r["rung"] == "bona" and r["id"] in F]
        m = [F[r["id"]] for r in rr if r["rung"] == "morph" and r["id"] in F]
        if len(b) != 598 or len(m) != 598:
            return None, None
        return np.stack(b), np.stack(m)

    def af0(self):
        F, rr = self.F["af0"], self.rows["af0"]
        out = {}
        for g in ("photo", "zero", "u25", "u50"):
            sel = [r for r in rr if r["rung"] == g]
            v = [F[r["id"]] for r in sel if r["id"] in F]
            out[g] = (np.stack(v), [r["id"] for r in sel]) if len(v) == len(sel) else None
        return out

    def cues_af0(self):
        if not hasattr(self, "_cu"):
            self._cu = load_cues("af0")
        return self._cu

    def halves(self):
        """AF0 u50 morphs and their two warped halves (amendment 1): (morph X, morph ids, halves X, halves morph ids)."""
        if "af0h" not in self.F:
            self.rows["af0h"] = K.rows(K.OUT / "lists/af0h.csv")
            self.F["af0h"] = L.load(self.feat, "af0h")
        F, rr = self.F["af0h"], self.rows["af0h"]
        a = self.af0().get("u50")
        if a is None or len(F) != len(rr):
            return None
        return a[0], a[1], np.stack([F[r["id"]] for r in rr]), [r["level"] for r in rr], [r["id"] for r in rr]

    def graded(self):
        F, rr = self.F["ar1g"], self.rows["ar1g"]
        if len(F) != len(rr):
            return None
        hosts = sorted({r["p1"] for r in rr})
        lv = sorted({float(r["level"]) for r in rr})
        X = {}
        for r in rr:
            X[(r["p1"], float(r["level"]))] = F[r["id"]]
        return hosts, lv, X


def load_soft(feat, T):
    """amendment 1: AF0 wave-4 shrink-and-enlarge copies of 200 hosts -> {(tool, rung): (host idx, X, ids)}."""
    F = L.load(feat, "ar1soft")
    out = {}
    for r in K.rows(K.OUT / "lists/ar1soft.csv"):
        if r["id"] not in F or r["p1"] not in T.ix:
            continue
        out.setdefault((r["tool"], r["rung"]), ([], [], []))
        out[(r["tool"], r["rung"])][0].append(T.ix[r["p1"]])
        out[(r["tool"], r["rung"])][1].append(F[r["id"]])
        out[(r["tool"], r["rung"])][2].append(r["id"])
    return {k: (np.array(v[0]), np.stack(v[1]), v[2]) for k, v in out.items()}


# ------------------------------------------------------------------------------------------------ Q1
def q1(T, fold, D):
    out = {}
    for eng in ENGINES:
        for name, a, b in STEPS:
            if not (T.has(eng, a) and T.has(eng, b)):
                continue
            p = np.full(len(T.hosts), np.nan)
            sa, sb = p.copy(), p.copy()
            for k in range(5):
                tr, _, te = L.fold_split(T, fold, k)
                Xtr = np.vstack([T.get(eng, r)[tr] for r in AR1_RUNGS if T.has(eng, r)])
                mu, sd = Xtr.mean(0), Xtr.std(0) + 1e-6
                za, zb = (T.get(eng, a) - mu) / sd, (T.get(eng, b) - mu) / sd
                d = L.unit((zb[tr] - za[tr]).mean(0))
                p[te] = (zb[te] - za[te]) @ d
                sa[te], sb[te] = za[te] @ d, zb[te] @ d
            idx = np.arange(len(T.hosts))
            pp = T.persons("R4" if "R4" in (a, b) else a, idx)
            W = D.w(pp)
            share_rep = (W @ (p > 0).astype(float)) / W.sum(1)
            share = float((p > 0).mean())
            A, Aci, _ = L.auc_ci(D, sb, T.persons(b, idx), sa, T.persons(a, idx))
            lo = K.ci(share_rep)[0]
            out[f"{eng}|{name}"] = dict(engine=eng, step=name, a=K.XN[a], b=K.XN[b], share=r3(share),
                                        share_ci=K.ci(share_rep), auc=r3(A), auc_ci=Aci,
                                        consistent=bool(share >= 0.75 and lo > 0.65))
    return out


# ------------------------------------------------------------------------------------------------ Q2
def half_splits(gid, n_split=20, seed=K.SEED):
    groups = {}
    for p, g in gid.items():
        groups.setdefault(g, []).append(p)
    gl = sorted(groups)
    rng = np.random.default_rng(seed + 7)
    out = []
    for _ in range(n_split):
        h = [set(), set()]
        sz = [0, 0]
        for g in rng.permutation(gl):
            j = int(np.argmin(sz))
            h[j] |= set(groups[g])
            sz[j] += len(groups[g])
        out.append(h)
    return out


def q2(T, gid, ext, heads_final):
    Xall = np.vstack([v for v in T.Z.values()])
    mu, sd = Xall.mean(0), Xall.std(0) + 1e-6

    def z(X):
        return (X - mu) / sd

    fixed = {}
    ren, sma = ext.smdd("fit")
    if ren is not None:
        fixed["softening (SMDD stored-small minus render)"] = L.unit((z(sma) - z(ren)).mean(0))
    nat, e7 = ext.frll_soft_pairs()
    if nat is not None:
        fixed["softening diagnostic (FRLL E7 opencv minus native; FRLL-only)"] = L.unit((z(e7) - z(nat)).mean(0))
    for key, hd in heads_final.items():          # head weights mapped into this z space
        fixed[f"head weights {key}"] = L.unit(hd.w / hd.sd * sd)
    splits = half_splits(gid)
    steps = [(f"{eng}|{n}", eng, a, b) for eng in ENGINES for n, a, b in STEPS if T.has(eng, a) and T.has(eng, b)]
    H = [[{}, {}] for _ in splits]
    soft_keys = sorted(k for k in T.soft if k[0] == "none")
    for s, (h0, h1) in enumerate(splits):
        for j, hs in enumerate((h0, h1)):
            idx = np.array([T.ix[p] for p in sorted(hs)])
            for key, eng, a, b in steps:
                H[s][j][key] = L.unit((z(T.get(eng, b)[idx]) - z(T.get(eng, a)[idx])).mean(0))
            hset = set(idx.tolist())
            dd = []
            for sk in soft_keys:
                si, X, _ = T.soft[sk]
                m = np.array([i in hset for i in si])
                d = z(X[m]) - z(T.get("opencv", "R0")[si[m]])
                dd.append(d)
                H[s][j][f"softening on hosts ({sk[1].replace('R0_soft_', '')})"] = L.unit(d.mean(0))
            if dd:
                H[s][j]["softening on hosts (pooled)"] = L.unit(np.vstack(dd).mean(0))
    hs_names = sorted(k for k in H[0][0] if k.startswith("softening on hosts"))
    names = [k for k, *_ in steps] + hs_names + list(fixed)
    M = {}
    for A in names:
        for B in names:
            vals = []
            for s in range(len(splits)):
                for j in (0, 1):
                    va = H[s][j][A] if A in H[s][j] else fixed[A]
                    vb = H[s][1 - j][B] if B in H[s][1 - j] else fixed[B]
                    vals.append(float(va @ vb))
            M[f"{A} || {B}"] = dict(mean=r3(np.mean(vals)), p2_5=r3(np.percentile(vals, 2.5)),
                                    p97_5=r3(np.percentile(vals, 97.5)))
    read = {}
    sk = [k for k in fixed if k.startswith("softening (SMDD")]
    for eng in ENGINES:
        def c(a, b):
            return M.get(f"{eng}|{a} || {eng}|{b}", {}).get("mean")
        r = dict(same_person_vs_whole=c("same_person_mix", "whole_morph"),
                 mirror_vs_whole=c("mirror_mix", "whole_morph"),
                 mirror_matched_vs_whole=c("mirror_mix_matched", "whole_morph"),
                 same_person_vs_second_identity=c("same_person_mix", "second_identity"),
                 same_person_vs_pipeline=c("same_person_mix", "pipeline"),
                 mirror_vs_pipeline=c("mirror_mix", "pipeline"),
                 whole_vs_pipeline=c("whole_morph", "pipeline"))
        if sk:
            for st in ("same_person_mix", "mirror_mix", "mirror_mix_matched", "whole_morph", "second_identity",
                       "pipeline"):
                if f"{eng}|{st} || {sk[0]}" in M:
                    r[f"{st}_vs_softening"] = M[f"{eng}|{st} || {sk[0]}"]["mean"]
        if "softening on hosts (pooled)" in names:
            for st in ("same_person_mix", "mirror_mix", "mirror_mix_matched", "whole_morph", "second_identity",
                       "pipeline"):
                if f"{eng}|{st} || softening on hosts (pooled)" in M:
                    r[f"{st}_vs_host_softening"] = M[f"{eng}|{st} || softening on hosts (pooled)"]["mean"]
            r["host_softening_vs_smdd_softening"] = (M[f"softening on hosts (pooled) || {sk[0]}"]["mean"] if sk
                                                     else None)
        r["reading_same_person_signal_is_morph_signal"] = (r["same_person_vs_whole"] or 0) >= 0.5
        r["reading_mirror_signal_is_morph_signal"] = (r["mirror_vs_whole"] or 0) >= 0.5
        if sk:
            r["reading_mixing_signal_is_softness"] = bool(max(r["same_person_mix_vs_softening"],
                                                              r["mirror_mix_vs_softening"]) > 0.5)
        if "same_person_mix_vs_host_softening" in r:
            r["reading_mixing_signal_is_host_softness (amendment 1)"] = bool(max(
                r["same_person_mix_vs_host_softening"], r["mirror_mix_vs_host_softening"]) > 0.5)
        read[eng] = r
    return dict(matrix=M, names=names, readings=read, n_splits=len(splits))


# ------------------------------------------------------------------------------------------------ Q3 / Q4 heads
def proj_fn(variant, T, eng, tr, ext):
    if variant == "none":
        return None
    if variant == "softh":
        trs = set(np.asarray(tr).tolist())
        keys = [k for k in T.soft if k[0] == "none"]
        if not keys:
            raise RuntimeError("host-softened features missing")

        def fh(mu, sd):
            dd = []
            for k in keys:
                idx, X, _ = T.soft[k]
                m = np.array([i in trs for i in idx])
                dd.append(((X[m] - mu) / sd) - ((T.get(eng, "R0")[idx[m]] - mu) / sd))
            return [np.vstack(dd).mean(0)]
        return fh
    ren, sma = ext.smdd("fit")

    def f(mu, sd):
        out = []
        if variant in ("soft", "both"):
            if ren is None:
                raise RuntimeError("SMDD features missing")
            out.append((((sma - mu) / sd) - ((ren - mu) / sd)).mean(0))
        if variant in ("pipe", "both"):
            out.append((((T.get(eng, "R2w")[tr] - mu) / sd) - ((T.get(eng, "R0")[tr] - mu) / sd)).mean(0))
        return out
    return f


def fit_head(T, gid, eng, head, tr, tr2, variant, ext):
    g = np.array([gid[T.hosts[i]] for i in tr])
    if head == "one":
        P = np.vstack([T.get(eng, "R3")[tr], T.get(eng, "R3m")[tr]])
        N = np.vstack([T.get(eng, "R2w")[tr], T.get(eng, "R2w")[tr]])
        gg = np.r_[g, g]
    else:
        P, N = T.get(eng, "R4")[tr2], T.get(eng, "R2w")[tr2]
        gg = np.array([gid[T.hosts[i]] for i in tr2])
    return L.fit_paired(P, N, gg, Cs=CS, proj=proj_fn(variant, T, eng, tr, ext))


def heads_all(T, fold, gid, ext, variants):
    """OOF scores S[(variant, head, train_eng)][(score_eng, rung)] (n_hosts,), fold heads, final heads."""
    S, FH, FIN = {}, {}, {}
    n = len(T.hosts)
    for variant in variants:
        for head in HEADS:
            for eng in ENGINES:
                key = (variant, head, eng)
                S[key] = {}
                for k in range(5):
                    tr, tr2, te = L.fold_split(T, fold, k)
                    hd = fit_head(T, gid, eng, head, tr, tr2, variant, ext)
                    FH[key + (k,)] = hd
                    for se in ENGINES:
                        for r in AR1_RUNGS:
                            if not T.has(se, r):
                                continue
                            S[key].setdefault((se, r), np.full(n, np.nan))[te] = hd.score(T.get(se, r)[te])
                    tes = set(te.tolist())
                    for sk, (idx, X, _) in T.soft.items():
                        m = np.array([i in tes for i in idx])
                        if m.any():
                            S[key].setdefault(("soft",) + sk, np.full(n, np.nan))[idx[m]] = hd.score(X[m])
                allh = np.arange(n)
                FIN[key] = fit_head(T, gid, eng, head, allh, allh, variant, ext)
                print(time.strftime("%T"), "heads", key, "C(final)", FIN[key].C, flush=True)
    return S, FH, FIN


def eval_contrasts(T, D, S, cues, names):
    out, reps = {}, {}
    fl = {}
    for se in ENGINES:
        for cn, a, b in CONTRASTS:
            if cn in FLOOR_CONTRASTS and cues and T.has(se, a) and T.has(se, b):
                ia, ib = T.ids[(("none", "R0") if a == "R0" else (se, a))], T.ids[(("none", "R0") if b == "R0" else (se, b))]
                if all(i in cues for i in ia + ib):
                    idx = np.arange(len(T.hosts))
                    fl[(se, cn)] = floor(D, cues, names, ib, T.persons(b, idx), ia, T.persons(a, idx))
    for key, sc in S.items():
        for se in ENGINES:
            for cn, a, b in CONTRASTS:
                if (se, a) not in sc and a != "R0" or (se, b) not in sc:
                    continue
                sa = sc[(se, a)] if (se, a) in sc else sc[(se, "R0")]
                sb = sc[(se, b)]
                idx = np.arange(len(T.hosts))
                A, Aci, rep = L.auc_ci(D, sb, T.persons(b, idx), sa, T.persons(a, idx))
                pair_share = float((sb > sa).mean())
                rec = dict(variant=key[0], head=key[1], train_engine=key[2], score_engine=se, contrast=cn,
                           auc=r3(A), auc_ci=Aci, paired_share_b_above_a=r3(pair_share))
                if (se, cn) in fl:
                    f, frep = fl[(se, cn)]
                    rec.update(floor_stat=f["best"], floor_auc=f["auc"], floor_ci=f["ci"], lapvar_auc=f["lapvar"],
                               lapvar_face_auc=f["lapvar_face"], excess=r3(A - f["auc"]), excess_ci=K.ci(rep - frep))
                out["|".join(key) + f"|{se}|{cn}"] = rec
                reps["|".join(key) + f"|{se}|{cn}"] = rep
    # one-person minus two-person, same variant / engines (paired draws)
    for k in list(out):
        v = out[k]
        if v["head"] != "one":
            continue
        k2 = k.replace("|one|", "|two|", 1)
        if k2 in reps:
            d = reps[k] - reps[k2]
            v["minus_two_person_head"] = r3(v["auc"] - out[k2]["auc"])
            v["minus_two_person_head_ci"] = K.ci(d)
    return out, {f"{se}|{cn}": f for (se, cn), (f, _) in fl.items()}


def eval_soft(T, D, S, cues, names):
    """amendment 1: flag set (iii) and the contrast softened x1 vs x3, out-of-fold, on the 200 softened hosts."""
    out = {}
    for key, sc in S.items():
        kk = "|".join(key)
        for sk in [k for k in sc if k[0] == "soft"]:
            _, tool, rung = sk
            m = ~np.isnan(sc[sk])
            idx = np.where(m)[0]
            base = "R0" if rung.startswith("R0") else "R2w"
            se = "opencv" if tool == "none" else tool
            unt = sc[(se, base)]
            r = dict(n=int(m.sum()), flag_vs_untouched_all_hosts_5pct=K.flag_rate(unt, sc[sk][m]),
                     auc_soft_vs_untouched_same_hosts=r3(K.auc(sc[sk][m], unt[m])))
            if base == "R2w":
                pos, neg = sc[(tool, "R4")][idx], sc[sk][idx]
                A, Aci, rep_ = L.auc_ci(D, pos, T.persons("R4", idx), neg, T.persons("R2w", idx))
                r.update(auc_x3_vs_softened_x1=r3(A), auc_x3_vs_softened_x1_ci=Aci)
                A2, A2ci, rep2 = L.auc_ci(D, pos, T.persons("R4", idx), sc[(tool, "R2w")][idx], T.persons("R2w", idx))
                r.update(auc_x3_vs_x1_same_hosts=r3(A2), auc_x3_vs_x1_same_hosts_ci=A2ci)
                sid = dict(zip(T.soft[(tool, rung)][0].tolist(), T.soft[(tool, rung)][2]))
                ia = [sid[i] for i in idx]
                ib = [T.ids[(tool, "R4")][i] for i in idx]
                if cues and all(i in cues for i in ia + ib):
                    f, frep = floor(D, cues, names, ib, T.persons("R4", idx), ia, T.persons("R2w", idx))
                    r.update(floor_stat=f["best"], floor_auc=f["auc"], floor_ci=f["ci"], lapvar_auc=f["lapvar"],
                             excess=r3(A - f["auc"]), excess_ci=K.ci(rep_ - frep))
            out[f"{kk}|{tool}|{rung}"] = r
    return out


def flag_tables(FIN, ext):
    cells = ext.bench_cells()
    ren, sma = ext.smdd("test")
    out = {}
    for key, hd in FIN.items():
        kk = "|".join(key)
        rec = {}
        for cell, c in cells.items():
            if c["native"] is None:
                continue
            nat = hd.score(c["native"])
            r = {}
            if c["e7"] is not None:
                r["e7_flag_at_native5"] = K.flag_rate(nat, hd.score(c["e7"]))
            if c["morph"] is not None:
                m = hd.score(c["morph"])
                r["auc_morph_vs_native"] = r3(K.auc(m, nat))
                r["eer_native"] = r3(K.eer(nat, m))
                if c["native_neutral"] is not None:
                    r["auc_morph_vs_native_neutral"] = r3(K.auc(m, hd.score(c["native_neutral"])))
                if c["e7"] is not None:
                    r["auc_morph_vs_e7"] = r3(K.auc(m, hd.score(c["e7"])))
                r["morph_flag_at_native5"] = K.flag_rate(nat, m)
            rec[cell] = r
        if ren is not None:
            rec["SMDD test pairs (stored-small vs render)"] = dict(
                e7_flag_at_native5=K.flag_rate(hd.score(ren), hd.score(sma)), auc_small_vs_render=r3(
                    K.auc(hd.score(sma), hd.score(ren))))
        b, m = ext.h1()
        if b is not None:
            rec["H1 Poisson (unseen tool and source)"] = dict(auc_morph_vs_bona=r3(K.auc(hd.score(m), hd.score(b))),
                                                              morph_flag_at_bona5=K.flag_rate(hd.score(b), hd.score(m)))
        a = ext.af0()
        if all(a.get(g) is not None for g in ("photo", "zero", "u25", "u50")):
            s = {g: hd.score(a[g][0]) for g in a}
            rec["AF0 unseen persons (OpenCV engine)"] = dict(
                auc_u50_vs_zero=r3(K.auc(s["u50"], s["zero"])), auc_u25_vs_zero=r3(K.auc(s["u25"], s["zero"])),
                auc_zero_vs_photo=r3(K.auc(s["zero"], s["photo"])), auc_u50_vs_photo=r3(K.auc(s["u50"], s["photo"])),
                zero_flag_at_photo5=K.flag_rate(s["photo"], s["zero"]))
        hv = ext.halves()
        if hv is not None:
            Xm, mid, Xh, hmid, hid = hv
            sm, sh = hd.score(Xm), hd.score(Xh)
            pos = dict(zip(mid, sm))
            hmax = {}
            for m_, v in zip(hmid, sh):
                hmax[m_] = max(hmax.get(m_, -np.inf), v)
            r = dict(auc_u50_vs_its_halves=r3(K.auc(sm, sh)),
                     share_morph_above_both_halves=r3(np.mean([pos[m_] > hmax[m_] for m_ in hmax])),
                     halves_flag_at_photo5=(K.flag_rate(hd.score(a["photo"][0]), sh) if a.get("photo") is not None
                                            else None))
            cu, nm = ext.cues_af0()
            if cu and all(i in cu for i in mid + hid):
                P, N = np.stack([cu[i] for i in mid]), np.stack([cu[i] for i in hid])
                aucs = [K.auc(P[:, j], N[:, j]) for j in range(P.shape[1])]
                j = int(np.argmax([L.fold_auc(x) for x in aucs]))
                r.update(floor_stat=nm[j], floor_auc=r3(L.fold_auc(aucs[j])),
                         lapvar_auc=r3(aucs[nm.index("lapvar")]), excess=r3(r["auc_u50_vs_its_halves"] -
                                                                       L.fold_auc(aucs[j])))
            rec["AF0 u50 morph vs its own two warped halves (matched geometry, unseen persons)"] = r
        out[kk] = rec
    return out


def readings(ev, flags, feat):
    out = {}
    for variant in VARIANTS:
        k = f"{variant}|one|opencv|opencv|x1_vs_x3"
        if k not in ev:
            continue
        e = ev[k]
        f = flags.get(f"{variant}|one|opencv", {})
        fr = [f.get("FRLL-Morphs opencv", {}).get("e7_flag_at_native5", {}).get("rate"),
              f.get("MAD22 OpenCV", {}).get("e7_flag_at_native5", {}).get("rate")]
        A, ex = e["auc"], e.get("excess")
        flag_ok = None if any(x is None for x in fr) else all(x <= 0.15 for x in fr)
        if ex is None or flag_ok is None:
            verdict = "incomplete"
        elif A >= 0.75 and ex >= 0.05 and flag_ok:
            verdict = "works"
        elif A < 0.60 or ex <= 0:
            verdict = "fails"
        else:
            verdict = "mixed"
        out[variant] = dict(feature=feat, auc_x1_vs_x3=A, auc_ci=e["auc_ci"], excess=ex, excess_ci=e.get("excess_ci"),
                            floor=e.get("floor_auc"), floor_stat=e.get("floor_stat"),
                            flag_frll_opencv_e7=fr[0], flag_mad22_opencv_e7=fr[1], verdict=verdict)
    if "none" in out and len(out) > 1:
        base = out["none"]
        for v, r in out.items():
            if v == "none":
                continue
            r["keeps_separation"] = bool(r["auc_x1_vs_x3"] >= base["auc_x1_vs_x3"] - 0.05)
            r["loses_reaction_to_softened"] = (None if r["flag_frll_opencv_e7"] is None or r["flag_mad22_opencv_e7"]
                                               is None else bool(max(r["flag_frll_opencv_e7"],
                                                                     r["flag_mad22_opencv_e7"]) <= 0.15))
    return out


# ------------------------------------------------------------------------------------------------ Q5
def q5(T, fold, FH, FIN, S, ext, variants):
    from scipy.stats import page_trend_test, spearmanr
    out = {}
    G = ext.graded()
    if G is not None:
        hosts, lv, X = G
        for variant in variants:
            for head in HEADS:
                for eng in ENGINES:
                    M = np.zeros((len(hosts), len(lv)))
                    for i, h in enumerate(hosts):
                        hd = FH[(variant, head, eng, fold[h])]
                        M[i] = hd.score(np.stack([X[(h, l)] for l in lv]))
                    pt = page_trend_test(M)
                    out[f"graded FaceMorpher|{variant}|{head}|{eng}"] = dict(
                        levels=lv, mean=[r3(x) for x in M.mean(0)], page_L=float(pt.statistic), page_p=float(pt.pvalue),
                        rises=bool(pt.pvalue < 0.05 and M[:, -1].mean() > M[:, 0].mean()),
                        auc_vs_m0=[r3(K.auc(M[:, j], M[:, 0])) for j in range(len(lv))], n_hosts=len(hosts))
    a = ext.af0()
    rng = np.random.default_rng(K.SEED)
    if all(a.get(g) is not None for g in ("zero", "u25", "u50")):
        for variant in variants:
            for head in HEADS:
                hd = FIN[(variant, head, "opencv")]
                s = np.r_[hd.score(a["zero"][0]), hd.score(a["u25"][0]), hd.score(a["u50"][0])]
                lvl = np.r_[np.zeros(len(a["zero"][0])), np.full(len(a["u25"][0]), .25), np.full(len(a["u50"][0]), .5)]
                rho = spearmanr(s, lvl).statistic
                reps = []
                for _ in range(K.B_BOOT):
                    ii = rng.integers(0, len(s), len(s))
                    reps.append(spearmanr(s[ii], lvl[ii]).statistic)
                c = K.ci(reps)
                out[f"AF0 OpenCV dose|{variant}|{head}|opencv"] = dict(
                    spearman=r3(rho), spearman_ci=c, rises=bool(c[0] > 0),
                    mean={"0": r3(s[lvl == 0].mean()), "0.25": r3(s[lvl == .25].mean()), "0.5": r3(s[lvl == .5].mean())})
    for variant in variants:
        for head in HEADS:
            sc = S[(variant, head, "opencv")]
            d = sc[("opencv", "R4")] - sc[("opencv", "R2w")]
            dis = np.array([1 - T.cosHB[h] for h in T.hosts])
            for nm, y in (("s(x3)-s(x1)", d), ("s(x3)", sc[("opencv", "R4")])):
                rho = spearmanr(y, dis).statistic
                reps = []
                for _ in range(K.B_BOOT):
                    ii = rng.integers(0, len(y), len(y))
                    reps.append(spearmanr(y[ii], dis[ii]).statistic)
                c = K.ci(reps)
                out[f"dissimilarity|{variant}|{head}|opencv|{nm}"] = dict(spearman=r3(rho), ci=c, rises=bool(c[0] > 0))
    return out


# ------------------------------------------------------------------------------------------------ FRLL diagnostic
def frll_diag(feat, FIN):
    try:
        T = L.Table(feat, pool="frll")
    except Exception as e:  # noqa: BLE001
        return dict(error=repr(e))
    for h in T.hosts:
        assert h.startswith("frll:")
    out = {}
    for key, hd in FIN.items():
        for se in ENGINES:
            for cn, a, b in CONTRASTS:
                if not (T.has(se, a) and T.has(se, b)):
                    continue
                out["|".join(key) + f"|{se}|{cn}"] = r3(K.auc(hd.score(T.get(se, b)), hd.score(T.get(se, a))))
    return dict(label="diagnostic only: every FRLL rung beyond x0 involves a smiling photo; no conclusion", auc=out)


# ------------------------------------------------------------------------------------------------ drivers
def setup(feat):
    pr = K.rows(K.POOL)
    gid, fold = K.groups_and_folds(pr)
    T = L.Table(feat)
    for h in T.hosts:
        assert not h.startswith("frll:")
    T.soft = load_soft(feat, T)
    D = K.Draw(T.hosts, B=K.B_BOOT)
    return pr, gid, fold, T, D


def first():
    t0 = time.time()
    feat = "dino_mean"
    pr, gid, fold, T, D = setup(feat)
    ext = Ext(feat)
    tr, tr2, te = L.fold_split(T, fold, 0)
    res = dict(feature=feat, engine="opencv", fold=0, n_train=len(tr), n_train_two=len(tr2), n_test=len(te),
               fold_sizes=[int(sum(fold[h] == k for h in T.hosts)) for k in range(5)])
    heads = {h: fit_head(T, gid, "opencv", h, tr, tr2, "none", ext) for h in HEADS}
    cues, names = load_cues("ar1")
    need = [T.ids[k][i] for k in (("none", "R0"), ("opencv", "R2w"), ("opencv", "R4")) for i in te]
    import cues as CU
    have = CU.af0_cache()
    cues.update({i: have[i] for i in need if i in have and i not in cues})
    miss = [i for i in need if i not in cues]
    if miss:                                   # first pass only: compute the fold-0 test images' statistics now
        from multiprocessing import Pool
        path = {r["id"]: r["path"] for r in K.rows(K.OUT / "lists/ar1.csv")}
        with Pool(2) as p:
            vals = p.map(CU.one, [path[i] for i in miss], chunksize=8)
        cues.update(dict(zip(miss, vals)))
        sys.path.insert(0, str(K.MC / "smadcvpr"))
        import cue_floor as CF
        names = list(CF.NAMES) + ["png_bytes"]
        np.savez(K.OUT / "cues/first_pass_fold0.npz", ids=np.array(miss), cues=np.stack(vals), names=np.array(names),
                 source=np.array(["pd1"] * len(miss)))
    if names is None:
        sys.path.insert(0, str(K.MC / "smadcvpr"))
        import cue_floor as CF
        names = list(CF.NAMES) + ["png_bytes"]
    res["cues_available"] = len(cues)
    for h, hd in heads.items():
        res[f"C_{h}"] = hd.C
        for cn, a, b in CONTRASTS:
            if not (T.has("opencv", a) and T.has("opencv", b)):
                continue
            sa, sb = hd.score(T.get("opencv", a)[te]), hd.score(T.get("opencv", b)[te])
            A, Aci, rep = L.auc_ci(D, sb, T.persons(b, te), sa, T.persons(a, te))
            rec = dict(auc=r3(A), ci=Aci)
            if cn in ("x1_vs_x3", "x0_vs_x3"):
                ia = [T.ids[("none", "R0") if a == "R0" else ("opencv", a)][i] for i in te]
                ib = [T.ids[("opencv", b)][i] for i in te]
                if all(i in cues for i in ia + ib):
                    f, frep = floor(D, cues, names, ib, T.persons(b, te), ia, T.persons(a, te))
                    rec.update(floor=f, excess=r3(A - f["auc"]), excess_ci=K.ci(rep - frep))
            res[f"{h}|{cn}"] = rec
    res["seconds"] = round(time.time() - t0, 1)
    jdump(res, K.RES / "first_pass_dino_opencv_fold0.json")
    print(json.dumps(res, indent=1, default=str))


def full(feat, variants):
    t0 = time.time()
    pr, gid, fold, T, D = setup(feat)
    ext = Ext(feat)
    od = K.OUT / "scores" / (feat + TAG)
    od.mkdir(parents=True, exist_ok=True)
    ren, _ = ext.smdd("fit")
    if ren is None:
        variants = [v for v in variants if v not in ("soft", "both")]
        print("SMDD features missing: variants", variants, flush=True)
    if not T.soft:
        variants = [v for v in variants if v != "softh"]
        print("host-softened features missing: variants", variants, flush=True)
    meta = dict(feature=feat, n_hosts=len(T.hosts), n_soft={"|".join(k): len(v[0]) for k, v in T.soft.items()}, fold_sizes=[int(sum(fold[h] == k for h in T.hosts)) for k in
                                                                 range(5)],
                n_groups=len(set(gid.values())), variants=list(variants),
                ext_counts={n: len(v) for n, v in ext.F.items()})
    r1 = q1(T, fold, D)
    jdump(r1, K.RES / f"q1_{feat}{TAG}.json")
    print(time.strftime("%T"), "Q1 done", flush=True)
    S, FH, FIN = heads_all(T, fold, gid, ext, variants)
    np.savez(od / "oof_scores.npz", **{"|".join(k) + "|" + "|".join(kk): v for k, d in S.items() for kk, v in d.items()},
             hosts=np.array(T.hosts))
    cues, names = load_cues("ar1")
    meta["cues_available"] = len(cues)
    ev, fl = eval_contrasts(T, D, S, cues, names)
    jdump(dict(meta=meta, contrasts=ev, floors=fl), K.RES / f"q3q4_contrasts_{feat}{TAG}.json")
    jdump(eval_soft(T, D, S, cues, names), K.RES / f"softened_hosts_{feat}{TAG}.json")
    flags = flag_tables(FIN, ext)
    jdump(flags, K.RES / f"external_{feat}{TAG}.json")
    rd = readings(ev, flags, feat)
    jdump(rd, K.RES / f"readings_{feat}{TAG}.json")
    print(time.strftime("%T"), "Q3/Q4 done", json.dumps(rd, default=str), flush=True)
    r2 = q2(T, gid, ext, {"|".join(k): v for k, v in FIN.items() if k[0] == "none"})
    jdump(r2, K.RES / f"q2_{feat}{TAG}.json")
    r5 = q5(T, fold, FH, FIN, S, ext, variants)
    jdump(r5, K.RES / f"q5_{feat}{TAG}.json")
    jdump(frll_diag(feat, FIN), K.RES / f"frll_diagnostic_{feat}{TAG}.json")
    meta["seconds"] = round(time.time() - t0, 1)
    jdump(meta, K.RES / f"meta_{feat}{TAG}.json")
    print(time.strftime("%T"), "ALL DONE", feat, meta["seconds"], flush=True)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("mode", choices=("first", "full", "q1"))
    ap.add_argument("--feat", default="dino_mean", choices=K.FEATS + K.CONTROLS)
    ap.add_argument("--variants", default=",".join(VARIANTS))
    ap.add_argument("--test", action="store_true", help="code-path test: B = 200, one C, outputs tagged _test")
    a = ap.parse_args()
    global CS, TAG
    if a.test:
        K.B_BOOT, CS, TAG = 200, (1e-2,), "_test"
        K.RES = K.OUT / "test_res"
    if a.mode == "first":
        first()
    elif a.mode == "q1":
        pr, gid, fold, T, D = setup(a.feat)
        jdump(q1(T, fold, D), K.RES / f"q1_{a.feat}.json")
        print("Q1 done", a.feat)
    else:
        full(a.feat, a.variants.split(","))


if __name__ == "__main__":
    main()
