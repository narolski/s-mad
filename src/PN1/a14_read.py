"""PN1 amendment 14 reader (draft; written before any amendment-14 score exists).
Inputs: results_a14/PN1_A14.tar (sha256 checked), the tier-1 / Sb / Bv / Brescore / HN2 tars, cues/a14_lcomb.npz.
  gate  A_s401 and B_s402 on the HN2 list: new lease vs pn1a / pn1b scores; equivalent if max |d logit| <= 0.05,
        mean |d logit| <= 0.01 and |d AUC(b)| <= 0.002 for both; otherwise every read below is printed with the label
        "platform not equivalent" and no verdict is given.
  HN7   per network (12): face-only R4 vs R2w AUC on test hosts (T_S4_bg vs T_S0_bg) and H1 AUC (Poisson morphs vs
        genuine); Spearman across the 12. Supported if rho >= 0.6 and A's face-only AUC > B's on both seeds;
        falsified if rho <= 0.2; otherwise inconclusive. Interval: 2,000 joint bootstraps (rng 20261117) of test
        partner cycles and H1 hosts, all 24 AUCs recomputed per draw.
  HN8   per network: AUC of FFHQ landmark_combined orig morphs vs landmark_combined resmatch genuine. Supported if
        Sb - B >= 0.05 on both seeds and Sb >= A on both seeds; falsified if Sb <= B on either seed; otherwise
        inconclusive. Intervals: 2,000 bootstraps of images within class (rng 20261117). Floor (printed beside, no
        mark): best single statistic of the 27 (cues27.py) by direction-free AUC on the same 3,000 images.
  HN2b  Sb, Bv on the HN2 list under the amendment-13 rule, labelled "added under amendment 14".
  python3 -I a14_read.py -> experiments/PN1_.../tier1_a14/a14.json"""
import csv
import hashlib
import pathlib
import re
import sys
import tarfile

import numpy as np

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import pn1lib as K  # noqa: E402
import reads as RD  # noqa: E402
import hn2_read as H2  # noqa: E402

RR = K.PN1 / "results_rented"
RA = K.PN1 / "results_a14"
MAN = K.PN1 / "a14_tree" / "pn14" / "data" / "manifests" / "pn1_a14.csv"
LIST_SHA = "9f199c3a8a981fd2e3e46f0d7c66ddfe8f8cf0e2a48e68d7f8c3e374f0ba2fc2"
NETS = [(a, s) for s in (401, 402) for a in ("A", "B", "Bn", "C", "Sb", "Bv")]


def npz(p):
    z = np.load(p)
    return dict(zip([str(i) for i in z["id"]], z["logit"].astype(float)))


def untar(tar):
    h = hashlib.sha256(tar.read_bytes()).hexdigest()
    assert h == (tar.parent / (tar.name + ".sha256")).read_text().split()[0], tar
    d = tar.parent / "unpacked"
    if not (d / tar.name[:-4]).exists():
        with tarfile.open(tar) as t:
            t.extractall(d)
    return d / tar.name[:-4]


def pools():
    cat = {r["id"]: r for r in K.catalog()}
    rows = []
    for r in csv.DictReader(open(K.PN1 / "manifests2" / "pn1_eval.csv")):
        x = dict(r)
        x["neutral"] = r["neutral"] == "True"
        c = cat.get(r["id"])
        if r["fam"] == "splice":
            x.update(field="", persons=(r["host"],), pool="ladder")
        elif c is not None:
            x.update(field=c.get("field", ""), persons=c["persons"], pool=c["pool"])
        else:
            ids = re.findall(r"(\d{3})_\d{2}", pathlib.Path(r["path"]).name)
            x.update(field="", persons=tuple(sorted({"frll:" + i for i in ids})), pool=r["cell"])
            x["host"] = x["persons"][0] if x["persons"] else r["id"]
        rows.append(x)
    P = RD.pools([r for r in rows if r["fam"] != "splice"])
    for r in rows:
        if r["fam"] == "splice":
            P.setdefault(("T_" if r["role"] == "test" else "D_") + r["rung"], []).append(dict(r, fam="ladder"))
    return P


def main():
    assert hashlib.sha256(MAN.read_bytes()).hexdigest() == LIST_SHA
    man = list(csv.DictReader(open(MAN)))
    A14 = untar(RA / "PN1_A14.tar")
    out = {"list_sha256": LIST_SHA, "gpu": (A14 / "gpu.txt").read_text().strip()}
    # gate
    g = {}
    hn2ids = [r["id"] for r in man if r["fam"] == "ffhq"]
    hrows = {r["id"]: r for r in man if r["fam"] == "ffhq"}
    for arm, seed in (("A", 401), ("B", 402)):
        new = npz(A14 / f"PN1_{arm}_s{seed}__ffhq.npz")
        old = npz(untar(RR / f"PN1_HN2_s{seed}.tar") / f"scores_hn2_{arm}.npz")
        d = np.array([new[i] - old[i] for i in hn2ids])
        mo = [i for i in hn2ids if hrows[i]["rung"] == "landmark_complete_orig"]
        bo = [i for i in hn2ids if hrows[i]["rung"] == "ffhq_bona_orig"]
        da = K.auc(np.array([new[i] for i in mo]), np.array([new[i] for i in bo])) - K.auc(np.array([old[i] for i in mo]), np.array([old[i] for i in bo]))
        g[f"{arm}_s{seed}"] = dict(max_abs=float(np.abs(d).max()), mean_abs=float(np.abs(d).mean()), d_auc=float(da),
                                   ok=bool(np.abs(d).max() <= 0.05 and np.abs(d).mean() <= 0.01 and abs(da) <= 0.002))
    gate = all(v["ok"] for v in g.values())
    out["gate"] = dict(per_net=g, equivalent=gate)
    lab = "" if gate else "platform not equivalent: "
    # scores per network
    P = pools()
    S = {}
    for a, s in NETS:
        x = npz(untar(RR / f"PN1_{a}_s{s}.tar") / "scores_eval.npz")
        if a == "B":
            x.update(npz(untar(RR / f"PN1_Brescore_s{s}.tar") / "scores_splice.npz"))
        if a in ("A", "Bn", "C"):
            x.update(npz(A14 / f"PN1_{a}_s{s}__splice.npz"))
        x.update(npz(A14 / f"PN1_{a}_s{s}__ffhq_lcomb.npz"))
        S[(a, s)] = x
    # HN7
    pos, neg = P["T_S4_bg"], P["T_S0_bg"]
    hm, hb = P["H1_morph"], P["H1_bona"]
    units = sorted({RD.unit(r) for r in pos + neg})
    hosts = sorted({r["host"] for r in hm + hb})

    def aucs(wu=None, wh=None):
        fo, h1 = [], []
        for k in NETS:
            s = S[k]
            def sel(rr, w, key):
                v, c = [], []
                for r in rr:
                    m = 1 if w is None else w.get(key(r), 0)
                    v += [s[r["id"]]] * m
                return np.array(v)
            fo.append(K.auc(sel(pos, wu, RD.unit), sel(neg, wu, RD.unit)))
            h1.append(K.auc(sel(hm, wh, lambda r: r["host"]), sel(hb, wh, lambda r: r["host"])))
        return np.array(fo), np.array(h1)

    from scipy.stats import spearmanr
    fo, h1 = aucs()
    rho = float(spearmanr(fo, h1).correlation)
    rng = np.random.default_rng(20261117)
    bs = []
    for _ in range(2000):
        cu = rng.choice(len(units), len(units)); ch = rng.choice(len(hosts), len(hosts))
        wu, wh = {}, {}
        for i in cu:
            wu[units[i]] = wu.get(units[i], 0) + 1
        for i in ch:
            wh[hosts[i]] = wh.get(hosts[i], 0) + 1
        f2, h2 = aucs(wu, wh)
        bs.append(spearmanr(f2, h2).correlation)
    a_gt_b = all(fo[NETS.index(("A", s))] > fo[NETS.index(("B", s))] for s in (401, 402))
    v7 = "supported" if rho >= 0.6 and a_gt_b else "falsified" if rho <= 0.2 else "inconclusive"
    out["HN7"] = dict(faceonly_auc={f"{a}_s{s}": float(x) for (a, s), x in zip(NETS, fo)},
                      h1_auc={f"{a}_s{s}": float(x) for (a, s), x in zip(NETS, h1)}, spearman=rho,
                      spearman_ci=[float(np.nanpercentile(bs, 2.5)), float(np.nanpercentile(bs, 97.5))],
                      A_faceonly_above_B_both_seeds=a_gt_b, verdict=lab + v7)
    # HN8
    lc = {r["id"]: r for r in man if r["fam"] == "ffhq_lcomb"}
    mo = [i for i, r in lc.items() if r["rung"] == "landmark_combined_orig"]
    gb = [i for i, r in lc.items() if r["rung"] == "landmark_combined_resmatch"]
    h8 = {}
    for k in NETS:
        m = np.array([S[k][i] for i in mo]); b = np.array([S[k][i] for i in gb])
        h8[f"{k[0]}_s{k[1]}"] = dict(auc=float(K.auc(m, b)), ci=H2.boot(lambda p, n: K.auc(p, n), m, b, rng),
                                     morph_miss_own=float(np.mean(m <= 0)), genuine_flag_own=float(np.mean(b > 0)))
    sb_b = [h8[f"Sb_s{s}"]["auc"] - h8[f"B_s{s}"]["auc"] for s in (401, 402)]
    sb_a = [h8[f"Sb_s{s}"]["auc"] - h8[f"A_s{s}"]["auc"] for s in (401, 402)]
    v8 = ("falsified" if min(sb_b) <= 0 else "supported" if min(sb_b) >= 0.05 and min(sb_a) >= 0 else "inconclusive")
    floor = None
    cf = K.PN1 / "cues" / "a14_lcomb.npz"
    if cf.exists():
        z = np.load(cf)
        cid = {str(i): c for i, c in zip(z["ids"], z["cues"])}
        names = [str(n) for n in z["names"]]
        best = []
        for j, n in enumerate(names):
            u = K.auc(np.array([cid[i][j] for i in mo]), np.array([cid[i][j] for i in gb]))
            best.append((max(u, 1 - u), n))
        best.sort(reverse=True)
        floor = dict(best_stat=best[0][1], best_auc=float(best[0][0]), top5=[(n, float(v)) for v, n in best[:5]])
    out["HN8"] = dict(per_net=h8, Sb_minus_B=sb_b, Sb_minus_A=sb_a, verdict=lab + v8, floor=floor)
    # HN2b
    h2rows = {r["id"]: r for r in man if r["fam"] == "ffhq"}
    bo = [i for i, r in h2rows.items() if r["rung"] == "ffhq_bona_orig"]
    mo2 = [i for i, r in h2rows.items() if r["rung"] == "landmark_complete_orig"]
    hb2 = {}
    for a in ("Sb", "Bv"):
        for s in (401, 402):
            x = npz(A14 / f"PN1_{a}_s{s}__ffhq.npz")
            av = float(np.mean(np.array([x[i] for i in bo]) > 0))
            bv = float(K.auc(np.array([x[i] for i in mo2]), np.array([x[i] for i in bo])))
            hb2[f"{a}_s{s}"] = dict(a=av, b=bv, verdict=lab + H2.verdict(av, bv) + " (added under amendment 14)")
    out["HN2b"] = hb2
    d = K.RES / "tier1_a14"
    d.mkdir(parents=True, exist_ok=True)
    K.dump(out, d / "a14.json")
    print("gate", gate, g)
    print("HN7", round(rho, 3), out["HN7"]["spearman_ci"], v7)
    print("HN8", [round(x, 3) for x in sb_b], [round(x, 3) for x in sb_a], v8, floor and (floor["best_stat"], round(floor["best_auc"], 3)))
    print("HN2b", {k: (round(v["a"], 3), round(v["b"], 3), v["verdict"]) for k, v in hb2.items()})


if __name__ == "__main__":
    if not sys.flags.isolated:
        sys.exit("run with python3 -I")
    main()
