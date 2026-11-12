"""PN1 amendment 14 reader (draft; written before any amendment-14 score exists). Variant full or reduced (14R) is read
from the tar's variant.txt; HN8, the floor and the paired complete-minus-combined read exist only in the full variant.
Inputs: results_a14/PN1_A14.tar (sha256 checked), the tier-1 / Sb / Bv / Brescore / HN2 tars; full variant also
cues/a14_lcomb.npz (mandatory; sha256 must equal the committed tier1_a14/a14_lcomb_floor.sha256).
  gate  A_s401 and B_s402 on the HN2 list: new lease vs pn1a / pn1b scores; equivalent if max |d logit| <= 0.05,
        mean |d logit| <= 0.01 and |d AUC(b)| <= 0.002 for both. The gate binds only the reads that cross platforms
        (HN7, HN2b): if it fails they are printed "platform not equivalent" with no verdict. HN8 (one lease) is not
        voided. (HN7 also needs HN8's landmark_combined scores, which come from the one lease.) A failed gate is not re-run on another platform.
  HN7   associational, between arms. Per network (12): face-only R4 vs R2w AUC on test hosts (T_S4_bg vs T_S0_bg) and
        FFHQ landmark_combined AUC (development set; H1 is sealed and not read); Spearman across the 12 (supported if rho >= 0.6 and A's face-only AUC > B's on both seeds; falsified
        if rho <= 0.2; else inconclusive). Printed: arm-level rho (seed means, n = 6), rho without Sb (n = 10; arm
        level n = 5). The only prediction made blind: A's face-only AUC > B's on both seeds. Interval: 2,000 joint
        bootstraps (rng 20261117) of test partner cycles and landmark_combined images (not training).
  HN8   per network: AUC of landmark_combined orig morphs vs landmark_combined resmatch genuine. A seed with B >= 0.95
        is untestable (ceiling). Over testable seeds: falsified if Sb <= B on any; supported if both seeds testable,
        Sb - B >= 0.05 and Sb - A >= 0 on both; untestable if no seed is testable; else inconclusive. Intervals: 2,000
        bootstraps of images within class (rng 20261117). Floor: best of the 27 simple statistics by direction-free
        AUC; "reads the face splice" only if, on both seeds, the 2.5% bound of (Sb AUC - floor maximum re-taken in the
        same draw) exceeds 0. Printed: aligned==1 subset; paired complete-minus-combined logit per pair key.
        Disclosure: A's reading of the history-matched pool is history-driven (72-78% of FFHQ persons rise when
        history-matched, tier1/posthoc_b2.json), which moves "Sb >= A" for reasons other than face reading.
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
LIST_SHA = {"full": ("a14_tree", "9f199c3a8a981fd2e3e46f0d7c66ddfe8f8cf0e2a48e68d7f8c3e374f0ba2fc2"),
            "reduced": ("a14r_tree", "2603c4a62cf8f0861d0b650bb7f6a889ad787e0afe48209d5f99c6c74dbde30d")}
FLOOR_NPZ = K.PN1 / "cues" / "a14_lcomb.npz"
FLOOR_SHA = K.RES / "tier1_a14" / "a14_lcomb_floor.sha256"
FFHQM = pathlib.Path("/mnt/t7/smad_heldout/ffhq_morphs/manifests/ffhqm.csv")
NETS = [(a, s) for s in (401, 402) for a in ("A", "B", "Bn", "C", "Sb", "Bv")]
ARMS = ("A", "B", "Bn", "C", "Sb", "Bv")


def npz(p):
    z = np.load(p)
    return dict(zip([str(i) for i in z["id"]], z["logit"].astype(float)))


def sha(p):
    return hashlib.sha256(pathlib.Path(p).read_bytes()).hexdigest()


def untar(tar):
    assert sha(tar) == (tar.parent / (tar.name + ".sha256")).read_text().split()[0], tar
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


def fauc(pos, neg):
    """AUC with ties counted half (rank form)."""
    x = np.r_[pos, neg]
    from scipy.stats import rankdata
    r = rankdata(x)[: len(pos)]
    return (r.sum() - len(pos) * (len(pos) + 1) / 2) / (len(pos) * len(neg))


def main():
    from scipy.stats import spearmanr
    A14 = untar(RA / "PN1_A14.tar")
    var = (A14 / "variant.txt").read_text().strip()
    tree, lsha = LIST_SHA[var]
    MAN = K.PN1 / tree / "pn14" / "data" / "manifests" / "pn1_a14.csv"
    assert sha(MAN) == lsha
    man = list(csv.DictReader(open(MAN)))
    out = {"variant": var, "list_sha256": lsha, "gpu": (A14 / "gpu.txt").read_text().strip(),
           "rc": (A14 / "rc").read_text().strip()}
    have = {p.name for p in A14.glob("*.npz")}
    # ---- gate (binds HN7 and HN2b only)
    g = {}
    hrows = {r["id"]: r for r in man if r["fam"] == "ffhq"}
    hn2ids = list(hrows)
    for arm, seed in (("A", 401), ("B", 402)):
        f = f"PN1_{arm}_s{seed}__ffhq.npz"
        if f not in have:
            g[f"{arm}_s{seed}"] = dict(ok=False, missing=True)
            continue
        new = npz(A14 / f)
        old = npz(untar(RR / f"PN1_HN2_s{seed}.tar") / f"scores_hn2_{arm}.npz")
        d = np.array([new[i] - old[i] for i in hn2ids])
        mo = [i for i in hn2ids if hrows[i]["rung"] == "landmark_complete_orig"]
        bo = [i for i in hn2ids if hrows[i]["rung"] == "ffhq_bona_orig"]
        da = fauc(np.array([new[i] for i in mo]), np.array([new[i] for i in bo])) - fauc(np.array([old[i] for i in mo]), np.array([old[i] for i in bo]))
        g[f"{arm}_s{seed}"] = dict(max_abs=float(np.abs(d).max()), mean_abs=float(np.abs(d).mean()), d_auc=float(da),
                                   ok=bool(np.abs(d).max() <= 0.05 and np.abs(d).mean() <= 0.01 and abs(da) <= 0.002))
    gate = all(v["ok"] for v in g.values())
    out["gate"] = dict(per_net=g, equivalent=gate, binds=["HN7", "HN2b"])
    xlab = "" if gate else "platform not equivalent; no verdict (rule outcome printed only): "
    # ---- scores
    P = pools()
    S = {}
    for a, s in NETS:
        x = npz(untar(RR / f"PN1_{a}_s{s}.tar") / "scores_eval.npz")
        if a == "B":
            x.update(npz(untar(RR / f"PN1_Brescore_s{s}.tar") / "scores_splice.npz"))
        for fam in ("splice", "ffhq_lcomb", "ffhq"):
            f = f"PN1_{a}_s{s}__{fam}.npz"
            if f in have and not (fam == "splice" and a in ("B", "Sb", "Bv")):
                x.update(npz(A14 / f))
        if a in ("A", "B", "Bn", "C"):
            x.update(npz(untar(RR / f"PN1_HN2_s{s}.tar") / f"scores_hn2_{a}.npz"))
        S[(a, s)] = x
    # ---- HN7
    # transfer axis: FFHQ landmark_combined (development set, lead ruling 12 Nov); H1 is sealed and not read
    pos, neg = P["T_S4_bg"], P["T_S0_bg"]
    hm = [dict(id=r["id"], host=r["id"]) for r in man if r["fam"] == "ffhq_lcomb" and r["label"] == "1"]
    hb = [dict(id=r["id"], host=r["id"]) for r in man if r["fam"] == "ffhq_lcomb" and r["label"] == "0"]
    ok7 = bool(hm) and all(all(r["id"] in S[k] for r in pos + neg + hm + hb) for k in NETS)
    if ok7:
        units = sorted({RD.unit(r) for r in pos + neg})
        hosts = sorted({r["host"] for r in hm + hb})

        def aucs(wu=None, wh=None):
            fo, h1 = [], []
            for k in NETS:
                s = S[k]

                def sel(rr, w, key):
                    v = []
                    for r in rr:
                        v += [s[r["id"]]] * (1 if w is None else w.get(key(r), 0))
                    return np.array(v)
                fo.append(fauc(sel(pos, wu, RD.unit), sel(neg, wu, RD.unit)))
                h1.append(fauc(sel(hm, wh, lambda r: r["host"]), sel(hb, wh, lambda r: r["host"])))
            return np.array(fo), np.array(h1)

        def rhos(fo, h1):
            ns = [i for i, k in enumerate(NETS) if k[0] != "Sb"]
            am = lambda v: np.array([np.mean([v[NETS.index((a, s))] for s in (401, 402)]) for a in ARMS])
            fa, ha = am(fo), am(h1)
            return (spearmanr(fo, h1).correlation, spearmanr(fa, ha).correlation, spearmanr(fo[ns], h1[ns]).correlation,
                    spearmanr(np.delete(fa, ARMS.index("Sb")), np.delete(ha, ARMS.index("Sb"))).correlation)
        fo, h1 = aucs()
        r12, r6, r10, r5 = rhos(fo, h1)
        rng = np.random.default_rng(20261117)
        bs = []
        for _ in range(2000):
            wu, wh = {}, {}
            for i in rng.choice(len(units), len(units)):
                wu[units[i]] = wu.get(units[i], 0) + 1
            for i in rng.choice(len(hosts), len(hosts)):
                wh[hosts[i]] = wh.get(hosts[i], 0) + 1
            bs.append(rhos(*aucs(wu, wh)))
        bs = np.array(bs, float)
        a_gt_b = all(fo[NETS.index(("A", s))] > fo[NETS.index(("B", s))] for s in (401, 402))
        v7 = "supported" if r12 >= 0.6 and a_gt_b else "falsified" if r12 <= 0.2 else "inconclusive, no claim"
        ci = lambda j: [float(np.nanpercentile(bs[:, j], 2.5)), float(np.nanpercentile(bs[:, j], 97.5))]
        out["HN7"] = dict(label="associational, between arms", blind_prediction="A face-only AUC > B on both seeds",
                          faceonly_auc={f"{a}_s{s}": float(x) for (a, s), x in zip(NETS, fo)},
                          lcomb_auc={f"{a}_s{s}": float(x) for (a, s), x in zip(NETS, h1)},
                          rho_12=float(r12), rho_12_ci=ci(0), rho_arm_6=float(r6), rho_arm_6_ci=ci(1),
                          rho_without_Sb_10=float(r10), rho_without_Sb_10_ci=ci(2), rho_arm_without_Sb_5=float(r5),
                          A_faceonly_above_B_both_seeds=a_gt_b, verdict=xlab + v7)
    else:
        out["HN7"] = dict(verdict="not read: splice or landmark_combined scores missing (rc)")
    # ---- HN8 (full variant)
    if var == "full":
        assert FLOOR_NPZ.exists(), "floor file missing"
        assert sha(FLOOR_NPZ) == FLOOR_SHA.read_text().split()[0], "floor sha256 differs from the committed value"
        aligned = {"lcomb_" + r["id"]: r["aligned"] == "1" for r in csv.DictReader(open(FFHQM)) if r["family"] == "landmark_combined"}
        lc = {r["id"]: r for r in man if r["fam"] == "ffhq_lcomb"}
        mo = sorted(i for i, r in lc.items() if r["rung"] == "landmark_combined_orig")
        gb = sorted(i for i, r in lc.items() if r["rung"] == "landmark_combined_resmatch")
        z = np.load(FLOOR_NPZ)
        cid = {str(i): c for i, c in zip(z["ids"], z["cues"])}
        assert set(cid) == set(mo) | set(gb)
        names = [str(n) for n in z["names"]]
        CM = np.array([cid[i] for i in mo]); CG = np.array([cid[i] for i in gb])
        rng = np.random.default_rng(20261117)
        draws = [(rng.integers(0, len(mo), len(mo)), rng.integers(0, len(gb), len(gb))) for _ in range(2000)]

        def fmax(im, ig):
            v = [fauc(CM[im, j], CG[ig, j]) for j in range(len(names))]
            v = [max(u, 1 - u) for u in v]
            return max(v), names[int(np.argmax(v))]
        f0, fname = fmax(np.arange(len(mo)), np.arange(len(gb)))
        fdraw = np.array([fmax(im, ig)[0] for im, ig in draws])
        h8 = {}
        for k in NETS:
            if not all(i in S[k] for i in mo + gb):
                h8[f"{k[0]}_s{k[1]}"] = dict(missing=True)
                continue
            m = np.array([S[k][i] for i in mo]); b = np.array([S[k][i] for i in gb])
            sd = np.array([fauc(m[im], b[ig]) for im, ig in draws])
            ma = [j for j, i in enumerate(mo) if aligned.get(i)]; ba = [j for j, i in enumerate(gb) if aligned.get(i)]
            h8[f"{k[0]}_s{k[1]}"] = dict(auc=float(fauc(m, b)), ci=[float(np.percentile(sd, 2.5)), float(np.percentile(sd, 97.5))],
                                         minus_floor_lo=float(np.percentile(sd - fdraw, 2.5)),
                                         auc_aligned_only=float(fauc(m[ma], b[ba])), n_aligned=(len(ma), len(ba)),
                                         morph_miss_own=float(np.mean(m <= 0)), genuine_flag_own=float(np.mean(b > 0)))
        seeds = {}
        for s in (401, 402):
            try:
                A_, B_, Sb_ = (h8[f"{a}_s{s}"]["auc"] for a in ("A", "B", "Sb"))
            except KeyError:
                seeds[s] = dict(testable=False, reason="missing scores")
                continue
            seeds[s] = dict(testable=B_ < 0.95, reason="ceiling (B >= 0.95)" if B_ >= 0.95 else "", Sb_minus_B=Sb_ - B_,
                            Sb_minus_A=Sb_ - A_, Sb_exceeds_floor=h8[f"Sb_s{s}"]["minus_floor_lo"] > 0)
        t = [s for s in seeds if seeds[s]["testable"]]
        if not t:
            v8 = "untestable (ceiling or missing)"
        elif any(seeds[s]["Sb_minus_B"] <= 0 for s in t):
            v8 = "falsified"
        elif len(t) == 2 and all(seeds[s]["Sb_minus_B"] >= 0.05 and seeds[s]["Sb_minus_A"] >= 0 for s in t):
            v8 = "supported"
        else:
            v8 = "inconclusive, no claim"
        face = all(seeds.get(s, {}).get("Sb_exceeds_floor") for s in (401, 402))
        # paired complete-minus-combined per pair key (orig morphs)
        comp = {r["host"]: r["id"] for r in man if r["fam"] == "ffhq" and r["rung"] == "landmark_complete_orig"}
        comb = {r["host"]: r["id"] for r in man if r["fam"] == "ffhq_lcomb" and r["rung"] == "landmark_combined_orig"}
        keys = sorted(set(comp) & set(comb))
        pc = {}
        for k in NETS:
            if not all(comp[q] in S[k] and comb[q] in S[k] for q in keys):
                continue
            d = np.array([S[k][comp[q]] - S[k][comb[q]] for q in keys])
            bsd = [d[rng.integers(0, len(d), len(d))].mean() for _ in range(2000)]
            pc[f"{k[0]}_s{k[1]}"] = dict(n=len(keys), mean=float(d.mean()), ci=[float(np.percentile(bsd, 2.5)), float(np.percentile(bsd, 97.5))],
                                         median=float(np.median(d)), share_complete_higher=float(np.mean(d > 0)))
        out["HN8"] = dict(per_net=h8, seeds={str(s): v for s, v in seeds.items()}, verdict=v8,
                          paired_note="complete scores of A, B, Bn, C come from pn1a / pn1b (cross-platform), of Sb, Bv "
                                      "from the new lease; printed only",
                          floor=dict(best_stat=fname, best_auc=float(f0), sha256=sha(FLOOR_NPZ)),
                          reads_the_face_splice=bool(face),
                          paired_complete_minus_combined=pc,
                          disclosure="A's reading of the history-matched pool is history-driven (72-78% of FFHQ persons "
                                     "rise when history-matched); Sb >= A moves for reasons other than face reading")
    # ---- HN2b
    bo = [i for i, r in hrows.items() if r["rung"] == "ffhq_bona_orig"]
    mo2 = [i for i, r in hrows.items() if r["rung"] == "landmark_complete_orig"]
    hb2 = {}
    for a in ("Sb", "Bv"):
        for s in (401, 402):
            f = f"PN1_{a}_s{s}__ffhq.npz"
            if f not in have:
                hb2[f"{a}_s{s}"] = dict(verdict="not read (missing)")
                continue
            x = npz(A14 / f)
            av = float(np.mean(np.array([x[i] for i in bo]) > 0))
            bv = float(fauc(np.array([x[i] for i in mo2]), np.array([x[i] for i in bo])))
            hb2[f"{a}_s{s}"] = dict(a=av, b=bv, verdict=xlab + H2.verdict(av, bv) + " (added under amendment 14)")
    out["HN2b"] = hb2
    d = K.RES / "tier1_a14"
    d.mkdir(parents=True, exist_ok=True)
    K.dump(out, d / "a14.json")
    print("variant", var, "rc", out["rc"], "gate", gate)
    print("HN7", {k: v for k, v in out["HN7"].items() if k.startswith("rho") or k == "verdict"})
    if "HN8" in out:
        print("HN8", out["HN8"]["verdict"], out["HN8"]["seeds"], out["HN8"]["floor"], out["HN8"]["reads_the_face_splice"])
    print("HN2b", hb2)


if __name__ == "__main__":
    if not sys.flags.isolated:
        sys.exit("run with python3 -I")
    main()
