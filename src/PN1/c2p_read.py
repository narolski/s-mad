"""Registration C2P (PN1): reader for contrast 2-prime, H-new-1, H-new-2 and the platform gate, exactly as registered.

Inputs: C2P_<Q>.tar (out/C2P_PN1_<arm>_s<seed>_<fam>.npz with id, logit; fam af0, ffhq, ms1ffhq; rescored on the
MS1 L40S host), the 15 FS1 result tars (stored A100 logits for the gate), the MS1 evaluation manifest (hold-out rows,
fam ms1ffhq), the FS1 evaluation manifest (gate rows) and the hold-out sharpness file (cues27, lapvar_face).
  python3 -I c2p_read.py --c2p C2P_m1.tar --out OUT.json
  python3 -I c2p_read.py --mock           (random scores; tests the code path only)
"""
import argparse
import csv
import io
import json
import math
import tarfile

import numpy as np

ARMS = ("A", "B", "Sb")
SEEDS = (403, 404, 405, 406, 407)
SIZES = ("fm61", "amsl112")
FS1 = "/mnt/t7/smad_next/PN1/results_fs"
MS1M = "/mnt/t7/smad_next/MS1/pack_tree/pn1/data/manifests/pn1_eval.csv"
FS1M = "/mnt/t7/smad_next/PN1/fs_tree/pn1/data/manifests/pn1_eval.csv"
CUES = "/mnt/t7/smad_next/PN1/cues/c2p_holdout.npz"
B_BOOT, RNG_G, RNG_M = 2000, 20261131, 20261132


def fauc(pos, neg):
    pos, neg = np.asarray(pos, float), np.asarray(neg, float)
    allv = np.concatenate([pos, neg])
    order = allv.argsort(kind="mergesort")
    ranks = np.empty(len(allv))
    s = allv[order]
    i = 0
    while i < len(s):
        j = i
        while j + 1 < len(s) and s[j + 1] == s[i]:
            j += 1
        ranks[order[i:j + 1]] = (i + j) / 2 + 1
        i = j + 1
    return float((ranks[:len(pos)].sum() - len(pos) * (len(pos) + 1) / 2) / (len(pos) * len(neg)))


def npz_from_tar(tar, name):
    with tarfile.open(tar) as t:
        m = [x for x in t.getmembers() if x.name.endswith(name)]
        if not m:
            return None
        z = np.load(io.BytesIO(t.extractfile(m[0]).read()))
        return dict(zip([str(i) for i in z["id"]], z["logit"].astype(float)))


def gate(new, stored, ids):
    common = [i for i in ids if i in new and i in stored]
    if len(common) < len(ids):
        return dict(n=len(common), expected=len(ids), passed=False, reason="missing rows")
    a = np.array([new[i] for i in common])
    b = np.array([stored[i] for i in common])
    d = np.abs(a - b)
    agree = float(((a > 0) == (b > 0)).mean())
    ok = bool(np.percentile(d, 99) <= 0.05 and d.max() <= 0.10 and agree >= 0.995)
    return dict(n=len(common), p99=float(np.percentile(d, 99)), max=float(d.max()), agree=agree, passed=ok)


def holdout(M):
    photo = {r["id"]: r for r in M if r["fam"] == "ms1ffhq" and r["rung"] == "photo" and r["strength"] == ""}
    u50 = {r["id"]: r for r in M if r["fam"] == "ms1ffhq" and r["rung"] == "u50" and r["strength"] == ""}
    ids = {r["id"] for r in M if r["fam"] == "ms1ffhq"}
    pairs = {z: [i for i in sorted(photo) if f"{i}_{z}" in ids] for z in SIZES}
    mpairs = {z: [i for i in sorted(u50) if f"{i}_{z}" in ids] for z in SIZES}
    return sorted(photo), sorted(u50), pairs, mpairs


def net_stats(L, natp, natm, pairs, mpairs, boot):
    g = np.array([L[i] for i in natp])
    sd = g.std(ddof=1)
    out = dict(native_flag=float((g > 0).mean()), sd_native=float(sd))
    m_nat = np.array([L[i] for i in natm])
    out["miss_native"] = float((m_nat <= 0).mean())
    out["auc_native_u50_vs_photo"] = fauc(m_nat, g)
    for z in SIZES:
        ids = pairs[z]
        nat = np.array([L[i] for i in ids])
        sto = np.array([L[f"{i}_{z}"] for i in ids])
        df = float((sto > 0).mean() - (nat > 0).mean())
        dm = float((sto - nat).mean() / sd)
        rep = []
        for w in boot[z]:
            rep.append(((sto[w] > 0).mean() - (nat[w] > 0).mean()))
        mids = mpairs[z]
        mn = np.array([L[i] for i in mids])
        ms = np.array([L[f"{i}_{z}"] for i in mids])
        gs = np.array([L[f"{i}_{z}"] for i in ids])
        out[z] = dict(n_pairs=len(ids), d_flag=df, d_flag_ci=[float(np.percentile(rep, 2.5)), float(np.percentile(rep, 97.5))],
                      d_flag_upper95=float(np.percentile(rep, 97.5)), d_mean_sd=dm,
                      up=int(((nat <= 0) & (sto > 0)).sum()), down=int(((nat > 0) & (sto <= 0)).sum()),
                      n_morph_pairs=len(mids), d_mean_att_sd=float((ms - mn).mean() / sd),
                      miss_stored=float((ms <= 0).mean()), miss_native_paired=float((mn <= 0).mean()),
                      auc_stored_u50_vs_stored_photo=fauc(ms, gs))
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--c2p", action="append", default=[])
    ap.add_argument("--out")
    ap.add_argument("--mock", action="store_true")
    a = ap.parse_args()
    M = list(csv.DictReader(open(MS1M)))
    F = list(csv.DictReader(open(FS1M)))
    gate_ids = [r["id"] for r in F if r["fam"] in ("af0", "ffhq")]
    natp, natm, pairs, mpairs = holdout(M)
    rng = np.random.default_rng(RNG_G)
    boot = {z: [rng.integers(0, len(pairs[z]), len(pairs[z])) for _ in range(B_BOOT)] for z in SIZES}
    cz = np.load(CUES)
    names = list(cz["names"])
    lap = dict(zip([str(i) for i in cz["ids"]], cz["cues"][:, names.index("lapvar_face")]))
    edges = np.quantile([lap[i] for i in natp], 0.75)
    top = {i for i in natp if lap[i] >= edges}
    nets, gates = {}, {}
    for arm in ARMS:
        for s in SEEDS:
            T = f"PN1_{arm}_s{s}"
            if a.mock:
                r = np.random.default_rng(s * 10 + len(arm))
                L = {}
                for row in M:
                    if row["fam"] != "ms1ffhq":
                        continue
                    base = -3.0 if row["label"] == "0" else 1.0
                    shift = (1.0 if arm == "A" else 0.05) if row["strength"] else 0.0
                    L[row["id"]] = float(r.normal(base + shift * (row["label"] == "0"), 1.5))
                gates[T] = dict(passed=True, mock=True)
            else:
                L, ok = {}, True
                new_g = {}
                for c in a.c2p:
                    for fam in ("af0", "ffhq", "ms1ffhq"):
                        d = npz_from_tar(c, f"C2P_{T}_{fam}.npz")
                        if d is not None:
                            (L if fam == "ms1ffhq" else new_g).update(d)
                stored = npz_from_tar(f"{FS1}/{T}.tar", "scores_eval.npz") or {}
                gates[T] = gate(new_g, stored, gate_ids)
                need = set(natp) | set(natm) | {f"{i}_{z}" for z in SIZES for i in pairs[z]} | \
                    {f"{i}_{z}" for z in SIZES for i in mpairs[z]}
                if not need <= set(L) or not all(math.isfinite(L[i]) for i in need):
                    gates[T]["holdout_complete"] = False
                    continue
            if not gates[T]["passed"]:
                continue
            nets[(arm, s)] = net_stats(L, natp, natm, pairs, mpairs, boot)
            st = nets[(arm, s)]
            for z in SIZES:          # H-new-2 counts (top sharpness quartile)
                ids = pairs[z]
                up_t = sum(1 for i in ids if i in top and L[i] <= 0 < L[f"{i}_{z}"])
                dn_t = sum(1 for i in ids if i in top and L[i] > 0 >= L[f"{i}_{z}"])
                net = st[z]["up"] - st[z]["down"]
                st[z]["hnew2_top_share"] = float((up_t - dn_t) / net) if net > 0 else None
    R = dict(gates=gates, per_network={f"{k[0]}_s{k[1]}": v for k, v in nets.items()}, mock=a.mock,
             lapvar_face_q75=float(edges))
    # contrast 2-prime
    c2 = {}
    ctrl = {z: {s: ((("A", s) in nets) and nets[("A", s)][z]["d_flag"] >= 0.05 and nets[("A", s)][z]["d_mean_sd"] > 0)
                for s in SEEDS} for z in SIZES}
    R["A_control"] = ctrl
    for X in ("B", "Sb"):
        res = {}
        for z in SIZES:
            per = {}
            for s in SEEDS:
                if not ctrl[z][s] or (X, s) not in nets:
                    per[s] = False
                    continue
                x, A = nets[(X, s)][z], nets[("A", s)][z]
                per[s] = bool(x["d_flag"] <= A["d_flag"] / 3 and abs(x["d_mean_sd"]) <= A["d_mean_sd"] / 3
                              and x["d_flag"] <= 0.05 and x["d_flag_upper95"] <= 0.08)
            res[z] = dict(per_seed=per, n_pass=sum(per.values()), n_control=sum(ctrl[z].values()))
            k = sum(1 for s in SEEDS if (X, s) in nets and ("A", s) in nets and
                    nets[(X, s)][z]["d_flag"] < nets[("A", s)][z]["d_flag"] / 3)
            res[z]["sign_test"] = dict(k=k, n=5, p_one_sided=float(sum(math.comb(5, j) for j in range(k, 6)) / 32))
        if any(res[z]["n_control"] <= 3 for z in SIZES):
            v = "uninformative"
        elif all(res[z]["n_pass"] >= 4 for z in SIZES):
            v = "passes"
        elif any(res[z]["n_pass"] <= 1 and res[z]["n_control"] >= 4 for z in SIZES):
            v = "fails"
        else:
            v = "inconclusive, no claim"
        res["verdict"] = v
        c2[X] = res
    R["contrast2prime"] = c2
    # H-new-1
    h1 = {}
    for X in ("B", "Sb"):
        vals = {z: {s: nets[(X, s)][z]["d_mean_att_sd"] for s in SEEDS if (X, s) in nets} for z in SIZES}
        sup = any(sum(1 for v in vals[z].values() if v <= -0.20) >= 4 for z in SIZES)
        fal = all(sum(1 for v in vals[z].values() if v >= -0.10) >= 4 for z in SIZES)
        h1[X] = dict(values=vals, verdict="supported" if sup else ("falsified" if fal else "inconclusive"))
    R["H_new_1"] = h1
    # H-new-2 (A only)
    sh = {z: {s: nets[("A", s)][z]["hnew2_top_share"] for s in SEEDS if ("A", s) in nets} for z in SIZES}
    s2 = all(sum(1 for v in sh[z].values() if v is not None and v >= 0.50) >= 4 for z in SIZES)
    f2 = all(sum(1 for v in sh[z].values() if v is not None and v <= 0.35) >= 4 for z in SIZES)
    R["H_new_2"] = dict(values=sh, verdict="supported" if s2 else ("falsified" if f2 else "inconclusive"))
    # freeze outcome implied (FINAL section 1 as amended; FS1 contrast 1 replicated, 5 of 5)
    if c2["Sb"]["verdict"] == "passes" and h1["Sb"]["verdict"] == "falsified":
        fr = "Sb"
    elif c2["B"]["verdict"] == "passes" and h1["B"]["verdict"] == "falsified":
        fr = "B"
    else:
        fr = "no method"
    R["freeze_implied"] = fr
    out = a.out or "/home/narolski/smad-next/experiments/PN1_protocol-network-first-tests/c2p_read_mock.json"
    json.dump(R, open(out, "w"), indent=1, default=lambda o: o if not isinstance(o, np.generic) else o.item())
    print(json.dumps(dict(contrast2prime={X: c2[X]["verdict"] for X in c2}, H_new_1={X: h1[X]["verdict"] for X in h1},
                          H_new_2=R["H_new_2"]["verdict"], freeze_implied=fr,
                          gates_failed=[k for k, v in gates.items() if not v.get("passed")])))


if __name__ == "__main__":
    main()
