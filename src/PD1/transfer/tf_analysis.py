"""Signal isolation by paired differences (PD1), cross-family transfer: analysis (registered in prereg.md).

(1) cross-fitted cosine matrix of step directions within and between families (z-space primary, L2 space secondary)
(2) leave one family out (LOFO): one-person head O and two-person head T2 fitted on two families (person-purged),
    scored on the third; floor, flag rates, threat probes; in-family out-of-fold reference on the same features
(3) fixed readings

  tf_analysis.py --feat clip_pool [--B 2000] [--splits 200] [--quick]
Writes /mnt/t7/smad_next/PD1/transfer/res/<feat>[_quick].json
Run: OMP_NUM_THREADS=2 ... nice -n 10 /home/narolski/mambamorph-code/.venv-spark/bin/python -I tf_analysis.py ...
"""
import argparse
import importlib.util
import json
import pathlib
import sys
import time

import numpy as np

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import tf_lib as K  # noqa: E402

T0 = time.time()


def log(*a):
    print(f"[{time.time() - T0:7.1f}s]", *a, flush=True)


def unit(v):
    n = np.linalg.norm(v)
    return v / n if n > 0 else v * np.nan


# ================================================================================================ (1) cosines
STEPS = {"P": ("x0", "x1"), "M": ("x1", "x2"), "W": ("x1", "x3"), "I": ("x2", "x3")}


def direction_units(F, H, R):
    """name -> (D (n, dim) per-unit differences, keys per unit (tuple of split keys))."""
    U = {}
    for f in K.FAMS:
        hs = H[f]
        steps = dict(STEPS)
        if f == "L":
            steps["Mm"] = ("x1", "xm")
        for s, (a, b) in steps.items():
            D = np.array([F[h[b]] - F[h[a]] for h in hs])
            keys = [K.step_persons(h, s) for h in hs]
            U[f"{f}:{s}"] = (D, keys)
        if f == "L":
            D1, k1 = U["L:M"]
            D2, k2 = U["L:Mm"]
            U["L:M+"] = (np.vstack([D1, D2]), k1 + k2)
    s = R["smdd_S_fit"]
    U["ref:SMDD softening"] = (np.array([F[b] - F[a] for a, b in zip(s["a"], s["b"])]), [("smdd:" + c,) for c in s["cl"]])
    h = R["H"]
    U["ref:GAN H latent spread"] = (np.array([F[b] - F[a] for a, b in zip(h["x1"], h["x1s"])]),
                                     [("H:" + c,) for c in h["cl"]])
    U["ref:GAN H whole morph"] = (np.array([F[b] - F[a] for a, b in zip(h["x1"], h["x3"])]),
                                   [("H:" + c,) for c in h["cl"]])
    x0 = {hh["person"]: hh["x0"] for hh in H["L"]}
    ls = R["L_soft_hosts"]
    U["ref:landmark host softening"] = (np.array([F[i] - F[x0[p]] for i, p in zip(ls["ids"], ls["person"])]),
                                         [(p,) for p in ls["person"]])
    k20, k100 = R["D_f256"]["D20"], R["D_f256"]["rec100"]
    rr = R["D_f256_rows"]
    ks = sorted(set(k20) & set(k100))
    U["ref:diffusion FRLL decoding steps (diagnostic)"] = (np.array([F[k100[k]] - F[k20[k]] for k in ks]),
                                                           [(rr[k20[k]]["persons"],) for k in ks])
    return U


def cosines(F, H, R, sd, n_splits, seed=K.SEED):
    U = direction_units(F, H, R)
    names = list(U)
    Z = {n: (D / sd, keys) for n, (D, keys) in U.items()}
    allkeys = sorted({k for _, keys in Z.values() for kk in keys for k in kk})
    kpos = {k: i for i, k in enumerate(allkeys)}
    KI = {n: np.array([[kpos[kk[0]], kpos[kk[-1]]] for kk in keys]) for n, (_, keys) in Z.items()}
    rng = np.random.default_rng(seed)
    nn = len(names)
    vals = np.full((n_splits, nn, nn), np.nan)
    counts = {n: [] for n in names}
    for s in range(n_splits):
        half = rng.permutation(len(allkeys)) < len(allkeys) / 2
        dirs = [[None] * nn, [None] * nn]
        for j, hv in enumerate((half, ~half)):
            for i, n in enumerate(names):
                m = hv[KI[n][:, 0]] & hv[KI[n][:, 1]]
                counts[n].append(int(m.sum()))
                dirs[j][i] = unit(Z[n][0][m].mean(0)) if m.sum() >= 5 else None
        for i in range(nn):
            for k in range(nn):
                a = [float(dirs[0][i] @ dirs[1][k]) if dirs[0][i] is not None and dirs[1][k] is not None else np.nan,
                     float(dirs[1][i] @ dirs[0][k]) if dirs[1][i] is not None and dirs[0][k] is not None else np.nan]
                vals[s, i, k] = np.nanmean(a) if np.isfinite(a).any() else np.nan
    full = [unit(Z[n][0].mean(0)) for n in names]
    out = {}
    for i, a in enumerate(names):
        for k, b in enumerate(names):
            v = vals[:, i, k]
            v = v[np.isfinite(v)]
            out[f"{a} || {b}"] = dict(cross=float(v.mean()) if len(v) else None,
                                      range=[float(np.percentile(v, 2.5)), float(np.percentile(v, 97.5))] if len(v) else None,
                                      full=float(full[i] @ full[k]), n_splits=int(len(v)))
    rel = {n: out[f"{n} || {n}"]["cross"] for n in names}
    for i, a in enumerate(names):
        for k, b in enumerate(names):
            c = out[f"{a} || {b}"]
            ra, rb = rel[a], rel[b]
            c["disatt"] = (c["cross"] / np.sqrt(ra * rb)) if (c["cross"] is not None and ra and rb and ra > 0 and rb > 0) else None
    return dict(names=names, M=out, reliability=rel, n_units={n: int(len(U[n][1])) for n in names},
                half_units_median={n: float(np.median(counts[n])) for n in names})


def read_pair(c, rel_a, rel_b):
    if c["cross"] >= 0.5:
        return "shared"
    if min(rel_a, rel_b) < 0.5:
        return "underpowered"
    if c["disatt"] is not None and c["disatt"] >= 0.5:
        return "attenuated"
    return "not shared"


def read_step(cos, step):
    pairs = [("L", "D"), ("L", "G"), ("D", "G")]
    rd = {}
    for a, b in pairs:
        c = cos["M"][f"{a}:{step} || {b}:{step}"]
        rd[f"{a}-{b}"] = dict(reading=read_pair(c, cos["reliability"][f"{a}:{step}"], cos["reliability"][f"{b}:{step}"]),
                              cross=c["cross"], disatt=c["disatt"], range=c["range"], full=c["full"])
    r = [v["reading"] for v in rd.values()]
    if all(x == "shared" for x in r):
        overall = "one shared direction"
    elif sum(x == "not shared" for x in r) >= 2:
        overall = "no shared direction"
    else:
        overall = "partly shared (" + ", ".join(f"{k}: {v['reading']}" for k, v in rd.items()) + ")"
    return dict(pairs=rd, overall=overall)


# ================================================================================================ statistics floors
def load_stats():
    S = {}
    z = np.load("/mnt/t7/smad_next/AF0/cues/ar1.npz", allow_pickle=False)
    names = ["AF0:" + n for n in z["names"].tolist()]
    for i, v in zip(z["ids"].tolist(), z["cues"]):
        S[i] = dict(zip(names, v.tolist()))
    z = np.load(K.DIF / "stats/tr.npz", allow_pickle=False)
    nm = ["own:" + n for n in z["names"].tolist()]
    for i, v in zip(z["id"].tolist(), z["stats"]):
        S.setdefault(i, {}).update(zip(nm, v.tolist()))
    z = np.load("/mnt/t7/smad_next/PD1/diffusion/verify/stats_native.npz", allow_pickle=False)
    nm = ["verifier:" + n for n in z["names"].tolist()]
    for i, v in zip(z["id"].tolist(), z["S"]):
        if i.startswith("tr|"):
            S.setdefault(i, {}).update(zip(nm, v.tolist()))
    z = np.load(K.GAN / "stats.npz", allow_pickle=False)
    nm = ["own:" + n for n in z["names"].tolist()]
    for i, v in zip(z["id"].tolist(), z["S"]):
        if i.startswith("G|"):
            S[i] = dict(zip(nm, v.tolist()))
    return S


# ================================================================================================ (2) LOFO
POS_O = {"L": ("x2", "xm"), "D": ("x2",), "G": ("x2",)}


def pair_share(head, F, hosts, pos):
    P, N, _ = K.family_pairs(F, hosts, pos)
    d = head.score(P) - head.score(N)
    return float(np.mean((d > 0) + 0.5 * (d == 0)))


def choose_C_lofo(F, train, pos, weighted):
    fa, fb = list(train)
    crit = {}
    for C in K.CS:
        v = []
        for a, b in ((fa, fb), (fb, fa)):
            hd, _ = K.fit_multi(F, {a: train[a]}, pos, C, weighted)
            v.append(pair_share(hd, F, train[b], pos[b]))
        crit[C] = float(np.mean(v))
    best = max(K.CS, key=lambda c: (round(crit[c], 12), -c))
    return best, crit


class TestSet:
    """Unique images of the held-out family with person tuples; host-level pairs."""

    def __init__(self, F, hosts, B, seed=K.SEED):
        self.hosts = hosts
        self.img = {}
        for h in hosts:
            for r in ("x0", "x1", "xm", "x2", "x3"):
                if r in h:
                    pp = (h["person"], h["partner"]) if r == "x3" else (h["person"],)
                    self.img.setdefault(r, {})[h[r]] = pp
        pers = sorted({p for h in hosts for p in (h["person"], h["partner"])})
        self.D = K.Draw(pers, B, seed)
        self.W = {r: self.D.w(list(d.values())) for r, d in self.img.items()}
        self.ids = {r: list(d) for r, d in self.img.items()}
        self.Wh = self.D.w([(h["person"], h["partner"]) for h in hosts])

    def auc(self, s, pos, neg):
        """s: dict id -> score. Returns point, replicates."""
        a = np.array([s[i] for i in self.ids[pos]])
        b = np.array([s[i] for i in self.ids[neg]])
        return K.auc(a, b), K.wauc(a, b, self.W[pos], self.W[neg])

    def share(self, s, pos, neg):
        v = np.array([(s[h[pos]] > s[h[neg]]) + 0.5 * (s[h[pos]] == s[h[neg]]) for h in self.hosts], float)
        return float(v.mean()), (self.Wh * v).sum(1) / np.maximum(self.Wh.sum(1), 1e-12)


def floor(ts, S, pos="x3", neg="x1"):
    names = sorted(set.intersection(*[set(S[i]) for r in (pos, neg) for i in ts.ids[r]]))
    best = None
    for n in names:
        a = np.array([S[i][n] for i in ts.ids[pos]], float)
        b = np.array([S[i][n] for i in ts.ids[neg]], float)
        if not (np.isfinite(a).all() and np.isfinite(b).all()):
            continue
        pt = K.auc(a, b)
        sign = 1.0 if pt >= 0.5 else -1.0
        fa = max(pt, 1 - pt)
        if best is None or fa > best[1]:
            best = (n, fa, sign)
    n, fa, sign = best
    a = sign * np.array([S[i][n] for i in ts.ids[pos]], float)
    b = sign * np.array([S[i][n] for i in ts.ids[neg]], float)
    rep = K.wauc(a, b, ts.W[pos], ts.W[neg])
    return dict(statistic=n, auc=fa, direction="x3 higher" if sign > 0 else "x3 lower", n_statistics=len(names)), rep


def score_ids(head, F, ids):
    ids = list(ids)
    return dict(zip(ids, head.score(np.array([F[i] for i in ids])).tolist()))


def flags_for(T, head, F, R, H):
    out = {}
    sets = {"L": ["L_flag_i", "L_flag_ii"], "D": ["D_flag"], "G": ["G_flag"]}[T]
    for k in sets:
        s = R[k]
        out[k] = dict(name=s["name"], **K.flag(head.score(np.array([F[i] for i in s["native"]])),
                                            head.score(np.array([F[i] for i in s["soft"]]))))
    st = R["smdd_S_test"]
    out["SMDD_S_test"] = dict(name="SMDD renders vs E7 copies (held-out 1,000)",
                              **K.flag(head.score(np.array([F[i] for i in st["a"]])),
                                       head.score(np.array([F[i] for i in st["b"]]))))
    if T == "L":
        x0 = np.array([F[h["x0"]] for h in H["L"]])
        ls = R["L_soft_hosts"]
        for strength in ("R0_soft_amsl112", "R0_soft_fm61"):
            ids = [i for i, r in zip(ls["ids"], ls["rung"]) if r == strength]
            out[f"L_hosts_{strength}"] = dict(name=f"landmark hosts' own softened photos ({strength})",
                                              **K.flag(head.score(x0), head.score(np.array([F[i] for i in ids]))))
    return out


def primary_flag(T, fl):
    keys = {"L": ["L_flag_i", "L_flag_ii"], "D": ["D_flag"], "G": ["G_flag"]}[T]
    return max(fl[k]["rate"] for k in keys)


def probes(T, head, F, R, ts):
    out = {}
    s = {}
    for r in ts.ids:
        s.update(score_ids(head, F, ts.ids[r]))

    def add(name, pos, neg):
        pt, rep = ts.auc(s, pos, neg)
        out[name] = dict(auc=pt, ci=K.ci(rep))

    add("x1 vs x2 (own one-person mix)", "x2", "x1")
    add("x0 vs x3", "x3", "x0")
    add("x2 vs x3", "x3", "x2")
    add("x0 vs x1", "x1", "x0")
    if T == "L":
        add("xm vs x3 (mirror self-morph)", "x3", "xm")
        bl, x1g = R["L_blank"], R["L_x1g"]
        for var, nm in (("bg", "face only (surround grey)"), ("face", "surround only (face grey)")):
            ss = {}
            for h in ts.hosts:
                for r in ("x1", "x3"):
                    ss[h[r]] = float(head.score(F[bl[(var, r, h["person"])]][None])[0])
            pt, rep = ts.auc(ss, "x3", "x1")
            out[f"blanked {nm}: x1 vs x3"] = dict(auc=pt, ci=K.ci(rep))
        ss = dict(s)
        for h in ts.hosts:
            ss[h["x1"]] = float(head.score(F[x1g[h["person"]]][None])[0])
        pt, rep = ts.auc(ss, "x3", "x1")
        out["matched-geometry warp-only x1g vs x3"] = dict(auc=pt, ci=K.ci(rep))
    if T == "D":
        d20 = list(R["D_f256"]["D20"].values())
        r100 = list(R["D_f256"]["rec100"].values())
        b20 = list(R["D_f256"]["B20"].values())
        s20, s100, sb = (head.score(np.array([F[i] for i in x])) for x in (d20, r100, b20))
        out["FRLL 100-step vs 20-step reconstruction (diagnostic)"] = dict(
            auc=K.auc(s100, s20), flag_100_at_20step_5pct=K.flag(s20, s100))
        out["FRLL 20-step morph vs 20-step reconstruction (diagnostic)"] = dict(auc=K.auc(sb, s20))
        out["FRLL 20-step morph vs 100-step reconstruction (diagnostic)"] = dict(auc=K.auc(sb, s100))
    if T == "G":
        h = R["H"]
        a1, a1s, a3 = (head.score(np.array([F[i] for i in h[x]])) for x in ("x1", "x1s", "x3"))
        D = K.Draw(h["cl"], 2000, K.SEED)
        W = D.w([(c,) for c in h["cl"]])
        for nm, p, n in (("set H x1 vs x3", a3, a1), ("set H x1s vs x3 (spread-matched one identity)", a3, a1s),
                         ("set H x1 vs x1s (one identity, spread only)", a1s, a1)):
            out[nm] = dict(auc=K.auc(p, n), ci=K.ci(K.wauc(p, n, W, W)))
    return out


def blank_probe_D(head, kind, ts):
    """diffusion verifier's CLIP features of face-box-only / face-blanked training images (TF32 off; descriptive)."""
    z = np.load("/mnt/t7/smad_next/PD1/diffusion/verify/blank_clip.npz", allow_pickle=False)
    out = {}
    for var in ("face", "surround", "full"):
        X = z[f"{var}_{kind}"].astype(np.float64)
        X /= np.linalg.norm(X, axis=1, keepdims=True)
        s = dict(zip(z["id"].tolist(), head.score(X).tolist()))
        pt, rep = ts.auc(s, "x3", "x1")
        out[f"{var}: x1 vs x3"] = dict(auc=pt, ci=K.ci(rep))
    return out


def read_transfer(auc_, excess, fl):
    if auc_ < 0.60 or excess <= 0:
        return "fails"
    if auc_ >= 0.75 and excess >= 0.05 and fl <= 0.15:
        return "transfers"
    return "mixed"


def lofo(F, H, R, S, B, feat, purge=True, pos_L=("x2", "xm"), weighted=True, crange=True, with_probes=True):
    res = {}
    for T in K.FAMS:
        tr_f = [f for f in K.FAMS if f != T]
        Tp = {p for h in H[T] for p in (h["person"], h["partner"])}
        train = {f: [h for h in H[f] if not (purge and ({h["person"], h["partner"]} & Tp))] for f in tr_f}
        for f in tr_f:
            assert not any(p.startswith("frll") for h in train[f] for p in (h["person"], h["partner"]))
            if purge:
                assert not ({p for h in train[f] for p in (h["person"], h["partner"])} & Tp)
        pos_o = {f: (pos_L if f == "L" else POS_O[f]) for f in tr_f}
        pos_t = {f: ("x3",) for f in tr_f}
        ts = TestSet(F, H[T], B)
        fl_stat, fl_rep = floor(ts, S)
        r = dict(train_hosts={f: len(train[f]) for f in tr_f}, test_hosts=len(H[T]),
                 test_images={k: len(v) for k, v in ts.ids.items()}, floor=dict(fl_stat, ci=K.ci(fl_rep)))
        reps = {}
        heads = {}
        for hn, pos in (("O", pos_o), ("T2", pos_t)):
            C, crit = choose_C_lofo(F, train, pos, weighted)
            head, mdir = K.fit_multi(F, train, pos, C, weighted)
            heads[hn] = head
            for nm, hd in ((hn, head), (hn + "_meandir", mdir)):
                s = {}
                for rr in ts.ids:
                    s.update(score_ids(hd, F, ts.ids[rr]))
                pt, rep = ts.auc(s, "x3", "x1")
                sh, shrep = ts.share(s, "x3", "x1")
                fl = flags_for(T, hd, F, R, H)
                e = dict(auc_x1_x3=pt, ci=K.ci(rep), excess=pt - fl_stat["auc"], excess_ci=K.ci(rep - fl_rep),
                         share_x3_gt_x1=sh, share_ci=K.ci(shrep), flags=fl, primary_flag=primary_flag(T, fl))
                if nm == hn:
                    e.update(C=C, inner_criterion={str(k): v for k, v in crit.items()},
                             n_pairs=head.info.get("n_pairs"))
                    e["reading"] = read_transfer(pt, e["excess"], e["primary_flag"])
                    if with_probes:
                        e["probes"] = probes(T, hd, F, R, ts)
                        if T == "D" and feat[0] == "clip":
                            e["probes_blank_D"] = blank_probe_D(hd, feat[1], ts)
                    if crange:
                        rg = {}
                        for c in K.CS:
                            hc, _ = K.fit_multi(F, train, pos, c, weighted)
                            sc = {}
                            for rr in ("x1", "x3"):
                                sc.update(score_ids(hc, F, ts.ids[rr]))
                            rg[str(c)] = dict(auc_x1_x3=ts.auc(sc, "x3", "x1")[0],
                                              primary_flag=primary_flag(T, flags_for(T, hc, F, R, H)))
                        e["C_range"] = rg
                    reps[hn] = rep
                else:
                    e["mean-direction share x2 > x1 on held-out"] = ts.share(s, "x2", "x1")[0]
                r[nm] = e
        r["O_minus_T2"] = dict(diff=r["O"]["auc_x1_x3"] - r["T2"]["auc_x1_x3"], ci=K.ci(reps["O"] - reps["T2"]))
        r["_reps"] = reps
        r["cos_O_T2_weights_z"] = float(unit(heads["O"].w) @ unit(heads["T2"].w))
        res[T] = r
        log(f"  LOFO {T}: O {r['O']['auc_x1_x3']:.3f} (C {r['O']['C']}), T2 {r['T2']['auc_x1_x3']:.3f}, floor "
            f"{fl_stat['auc']:.3f}, flag {r['O']['primary_flag']:.3f} -> {r['O']['reading']}")
    return res


# ================================================================================================ in-family OOF
def folds_for(T, hosts):
    if T == "L":
        spec = importlib.util.spec_from_file_location("pd1_landmark_common",
                                                      "/home/narolski/smad-next/src/PD1/landmark/pd1_common.py")
        m = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(m)
        gid, fold = m.groups_and_folds(m.rows(m.POOL))
        return np.array([fold[h["person"]] for h in hosts]), np.array([gid[h["person"]] for h in hosts])
    if T == "D":
        bl = sorted({h["cluster"] for h in hosts})
        order = sorted(bl, key=lambda b: K.hsh("PD1:" + b))
        fo = {b: i % 5 for i, b in enumerate(order)}
        return np.array([fo[h["cluster"]] for h in hosts]), np.array([h["cluster"] for h in hosts])
    u = sorted({h["cluster"] for h in hosts})
    perm = np.random.default_rng(401).permutation(len(u))
    fo = {u[j]: int(i % 5) for i, j in enumerate(perm)}
    return np.array([fo[h["cluster"]] for h in hosts]), np.array([h["cluster"] for h in hosts])


def choose_C_inner(F, f, hosts, pos, groups):
    ug = sorted(set(groups))
    gi = {g: K.hsh("PD1inner:" + str(g)) for g in ug}
    order = sorted(ug, key=lambda g: gi[g])
    fo = {g: i % 3 for i, g in enumerate(order)}
    hin = np.array([fo[g] for g in groups])
    crit = {}
    for C in K.CS:
        v = []
        for j in range(3):
            tr = [h for h, k in zip(hosts, hin) if k != j]
            te = [h for h, k in zip(hosts, hin) if k == j]
            tp = {p for h in te for p in (h["person"], h["partner"])}
            tr = [h for h in tr if not ({h["person"], h["partner"]} & tp)]
            hd, _ = K.fit_multi(F, {f: tr}, {f: pos}, C)
            v.append(pair_share(hd, F, te, pos))
        crit[C] = float(np.mean(v))
    return max(K.CS, key=lambda c: (round(crit[c], 12), -c))


def infamily(F, H, R, B, lofo_res):
    out = {}
    for T in K.FAMS:
        hosts = H[T]
        fold, groups = folds_for(T, hosts)
        ts = TestSet(F, hosts, B)
        r = {}
        for hn, pos in (("O", POS_O[T]), ("T2", ("x3",))):
            s = {}
            Cs = []
            for k in range(5):
                te = [h for h, f in zip(hosts, fold) if f == k]
                tp = {p for h in te for p in (h["person"], h["partner"])}
                tri = [i for i, (h, f) in enumerate(zip(hosts, fold)) if f != k and not ({h["person"], h["partner"]} & tp)]
                tr = [hosts[i] for i in tri]
                C = choose_C_inner(F, T, tr, pos, groups[tri])
                Cs.append(C)
                hd, _ = K.fit_multi(F, {T: tr}, {T: pos}, C)
                for h in te:
                    for rr in ("x0", "x1", "xm", "x2", "x3"):
                        if rr in h:
                            s[h[rr]] = float(hd.score(F[h[rr]][None])[0])
            pt, rep = ts.auc(s, "x3", "x1")
            e = dict(auc_x1_x3=pt, ci=K.ci(rep), C_per_fold=Cs, x2_vs_x3=ts.auc(s, "x3", "x2")[0])
            if T == "L":
                e["xm_vs_x3"] = ts.auc(s, "x3", "xm")[0]
            Cf = choose_C_inner(F, T, hosts, pos, groups)
            hf, _ = K.fit_multi(F, {T: hosts}, {T: pos}, Cf)
            fl = flags_for(T, hf, F, R, H)
            e.update(final_C=Cf, flags={k: dict(rate=v["rate"], ci=v["ci"], name=v["name"]) for k, v in fl.items()},
                     primary_flag=primary_flag(T, fl))
            # transfer gap on the same draws (the LOFO head re-scored here for paired replicates)
            r[hn] = e
            r[hn + "_rep"] = rep
        out[T] = r
        log(f"  in-family {T}: O {r['O']['auc_x1_x3']:.3f}, T2 {r['T2']['auc_x1_x3']:.3f}")
    return out


# ================================================================================================ main
def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--feat", required=True, choices=list(K.FKEY.values()))
    ap.add_argument("--B", type=int, default=2000)
    ap.add_argument("--splits", type=int, default=200)
    ap.add_argument("--quick", action="store_true", help="code-path test: B 50, 10 splits, no C range or sensitivity")
    ap.add_argument("--skip-sens", action="store_true")
    a = ap.parse_args()
    if not sys.flags.isolated:
        sys.exit("run with python3 -I")
    feat = [k for k, v in K.FKEY.items() if v == a.feat][0]
    B, NS = (50, 10) if a.quick else (a.B, a.splits)
    F = K.load_features(*feat)
    H = K.all_hosts()
    R = K.refs()
    need = [h[r] for f in H for h in H[f] for r in ("x0", "x1", "xm", "x2", "x3") if r in h]
    missing = [i for i in need if i not in F]
    assert not missing, (len(missing), missing[:5])
    log("features", a.feat, len(F), "hosts", {f: len(H[f]) for f in H})
    S = load_stats()
    res = dict(feature=K.FNAME[feat], B=B, splits=NS, hosts={f: len(H[f]) for f in H})
    # common z-space scaler: ladder images of the three primary pools, equal weight per family
    groups = []
    for f in K.FAMS:
        ids = sorted({h[r] for h in H[f] for r in ("x0", "x1", "xm", "x2", "x3") if r in h})
        groups.append(np.array([F[i] for i in ids]))
    mu, sd = K.balanced_scaler(groups)
    log("cosines z-space")
    res["cos_z"] = cosines(F, H, R, sd, NS)
    log("cosines L2 space")
    res["cos_l2"] = cosines(F, H, R, np.ones_like(sd), NS)
    res["readings_cos"] = {sp: {st: read_step(res[sp], st) for st in ("M", "P", "W")} for sp in ("cos_z", "cos_l2")}
    log("readings", {st: v["overall"] for st, v in res["readings_cos"]["cos_z"].items()})
    log("LOFO primary")
    res["lofo"] = lofo(F, H, R, S, B, feat, crange=not a.quick)
    log("in-family reference")
    inf = infamily(F, H, R, B, res["lofo"])
    for T in K.FAMS:
        reps = res["lofo"][T].pop("_reps")
        for hn in ("O", "T2"):
            rep_in = inf[T].pop(hn + "_rep")    # same TestSet draws (same persons, same seed): paired replicates
            inf[T][hn]["transfer_gap"] = dict(diff=res["lofo"][T][hn]["auc_x1_x3"] - inf[T][hn]["auc_x1_x3"],
                                              ci=K.ci(reps[hn] - rep_in))
    res["infamily"] = inf
    if not a.quick and not a.skip_sens:
        for key, kw in (("sens_nopurge", dict(purge=False)), ("sens_Lx2only", dict(pos_L=("x2",))),
                        ("sens_unweighted", dict(weighted=False))):
            log("sensitivity:", key)
            res[key] = lofo(F, H, R, S, B, feat, crange=False, with_probes=False, **kw)
            for T in K.FAMS:
                res[key][T].pop("_reps", None)
    # per-held-out readings
    res["readings_lofo"] = {T: res["lofo"][T]["O"]["reading"] for T in K.FAMS}
    od = K.OUT / "res"
    od.mkdir(parents=True, exist_ok=True)
    p = od / f"{a.feat}{'_quick' if a.quick else ''}.json"
    json.dump(res, open(p, "w"), indent=1, default=float)
    log("wrote", p)


if __name__ == "__main__":
    main()
