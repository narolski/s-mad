"""C1c step 3 and H4: which photo of a two-expression pair does each score set rank as more morph-like?
(a) FRLL frames, (b) every registered variant of the same 204 photos, (c) FERET fa/fb and FRGC same-session pairs with
C1-probe expression labels (not ground truth). Counts above / below / tied; share = above / (above + below).
H4: flag rate on the 204 FRLL frames at thresholds fixed on the development genuine photos (devbona), neutral-only vs all.
Existing scores only. Needs c1c_files.py outputs (pair lists with probe logits).
Run: /home/narolski/mambamorph-code/.venv-spark/bin/python -I src/C1c/c1c_sep.py [--smoke]
"""
import csv, json, pathlib, re, sys, collections
import numpy as np

SMOKE = "--smoke" in sys.argv
sys.argv = [a for a in sys.argv if a != "--smoke"]
sys.path.insert(0, "/home/narolski/smad-next/src/C1b")
import c1b_read as C1B  # noqa: E402  (detector list and score locations of C1b)

MC = pathlib.Path("/home/narolski/mambamorph-code")
EVAL = MC / "smadcvpr_data/manifests/eval.csv"
EVAL_SHA = "86d055d349c63a225893ace30cb3db8b1e9aea4e72350d78152126d7a49d56c9"
OUT = pathlib.Path("/home/narolski/smad-next/experiments/C1c_smiling-half-expression-or-detail")
AD4 = pathlib.Path("/mnt/t7/smad_next/AD4/zero_step")
B = 50 if SMOKE else 10000
SEED = 20261111
DEV_T = (0.01, 0.05, 0.10)


def variants(rows):
    """name -> {(person, expr): id} for every registered genuine variant of the 204 FRLL photos (frllm, dim, mordiff)."""
    V = collections.OrderedDict()
    for r in rows:
        if r["label"] != "0" or r["set"] not in ("frllm", "dim", "mordiff"):
            continue
        if r["family"] == "dim_bona":            # byte-identical to frll_bona (checked in C1b)
            continue
        m = re.match(r"^(\d{3})_(\d{2})_", r["path"].rsplit("/", 1)[1])
        name = f"resmatch:{r['family']}" if r["variant"] == "resmatch" else f"{r['family']}:{r['variant']}"
        V.setdefault(name, {})[(m.group(1), m.group(2))] = r["id"]
    order = ["frll_bona:orig", "frll_bona:jpeg90", "frll_bona:jpeg70", "frll_bona:jpeg50", "frll_bona:chip", "frll_bona:blur1", "frll_bona:resample50",
             "resmatch:stylegan", "resmatch:facemorpher", "resmatch:opencv", "resmatch:amsl", "resmatch:webmorph", "resmatch:dim_a", "resmatch:dim_c",
             "resmatch:fast_dim", "resmatch:fast_dim_ode", "resmatch:greedy_dim", "resmatch:greedy_dim_s", "resmatch:mordiff", "mordiff_bona:orig"]
    assert set(order) == set(V), set(V) ^ set(order)
    return collections.OrderedDict((k, V[k]) for k in order)


def detectors():
    D = [(lab, grp, f, key, ck) for lab, grp, f, key, ck in C1B.detectors()]
    for rc, name in (("m3", "AD4 untrained ViT-B/16 (zero-step, seed 401)"), ("m3l", "AD4 untrained ViT-L/14 (zero-step, seed 401)")):
        f = AD4 / rc / "scores_eval.npz"
        if f.exists():
            D.append((name, "untrained", f, "score", "zero"))
    if SMOKE:
        D = [d for d in D if d[0] in ("MADation ViT-L/14 release", "M3 s1 last", "M3 s1 es") or d[4] == "zero"][:4]
    return D


def counts(a, b):
    return int((a > b).sum()), int((a < b).sum()), int((a == b).sum())


def boot_share(above, below, groups, rng_C):
    """share = sum(above) / sum(above + below) under a cluster bootstrap (multinomial counts over groups)."""
    u, inv = np.unique(groups, return_inverse=True)
    sa = np.bincount(inv, weights=above, minlength=len(u)); sn = np.bincount(inv, weights=above + below, minlength=len(u))
    C = rng_C(len(u))
    num, den = C @ sa, C @ sn
    s = num / np.maximum(den, 1e-12)
    return [float(np.percentile(s, 2.5)), float(np.percentile(s, 97.5))]


def main():
    import hashlib
    assert hashlib.sha256(EVAL.read_bytes()).hexdigest() == EVAL_SHA
    rows = list(csv.DictReader(open(EVAL)))
    V = variants(rows)
    dev_ids = [r["id"] for r in rows if r["set"] == "devbona" and r["variant"] == "orig"]
    pairs = {}
    for name in ("feret", "frgc"):
        L = list(csv.DictReader(open(OUT / f"c1c_{name}_pairs.csv")))
        for o in L:
            o["probe_a"], o["probe_b"], o["probe_clear"] = float(o["probe_a"]), float(o["probe_b"]), int(o["probe_clear"])
        pairs[name] = L
    rngs = {}

    def rng_C(n):
        if n not in rngs:
            rngs[n] = np.random.default_rng(SEED).multinomial(n, np.full(n, 1.0 / n), size=B).astype(np.float64)
        return rngs[n]

    out = []
    for lab, grp, f, key, ck in detectors():
        z = np.load(f, allow_pickle=False)
        if "manifest_sha256" in z.files and ck != "zero":
            assert str(z["manifest_sha256"]) == EVAL_SHA, f
        sc = dict(zip(z["id"].tolist(), z[key].astype(np.float64)))
        res = {"label": lab, "group": grp, "ckpt": ck, "file": str(f), "key": key, "variants": {}, "pairs": {}}
        for vn, G in V.items():
            P = sorted(p for p, e in G if e == "03" and (p, "08") in G)
            if not all(G[(p, e)] in sc for p in P for e in ("03", "08")):
                res["variants"][vn] = None
                continue
            a = np.array([sc[G[(p, "03")]] for p in P]); b = np.array([sc[G[(p, "08")]] for p in P])
            up, dn, ti = counts(a, b)
            ci = boot_share((a > b).astype(float), (a < b).astype(float), np.array(P), rng_C)
            res["variants"][vn] = {"n": len(P), "above": up, "below": dn, "tied": ti, "share": up / max(up + dn, 1), "ci": ci}
        for pn, L in pairs.items():
            if not all(o["id_a"] in sc and o["id_b"] in sc for o in L):
                res["pairs"][pn] = None
                continue
            sa = np.array([sc[o["id_a"]] for o in L]); sb = np.array([sc[o["id_b"]] for o in L])
            mb = np.array([o["more_smiling"] == "b" for o in L])
            less = np.where(mb, sa, sb); more = np.where(mb, sb, sa)
            clear = np.array([o["probe_clear"] == 1 for o in L])
            subj = np.array([o["subject"] for o in L])
            d = {}
            for sel_name, sel in (("probe_clear", clear), ("all", np.ones(len(L), bool))):
                up, dn, ti = counts(less[sel], more[sel])
                d[sel_name] = {"n": int(sel.sum()), "above": up, "below": dn, "tied": ti, "share": up / max(up + dn, 1),
                               "ci": boot_share((less[sel] > more[sel]).astype(float), (less[sel] < more[sel]).astype(float), subj[sel], rng_C)}
            dp = np.abs(np.array([o["probe_b"] - o["probe_a"] for o in L]))
            q = np.quantile(dp, [1 / 3, 2 / 3]); t = np.digitize(dp, q)
            d["tertiles_abs_probe_diff"] = []
            for k in range(3):
                up, dn, ti = counts(less[t == k], more[t == k])
                d["tertiles_abs_probe_diff"].append({"above": up, "below": dn, "tied": ti, "share": up / max(up + dn, 1)})
            res["pairs"][pn] = d
        # H4: thresholds fixed on devbona (flag = score > quantile(dev, 1 - t), the analyze.operating_points convention)
        if all(i in sc for i in dev_ids):
            dev = np.array([sc[i] for i in dev_ids])
            G = V["frll_bona:orig"]; P = sorted(p for p, e in G if e == "03")
            s3 = np.array([sc[G[(p, "03")]] for p in P]); s8 = np.array([sc[G[(p, "08")]] for p in P])
            Cp = rng_C(len(P))
            h4 = {}
            for tg in DEV_T:
                thr = float(np.quantile(dev, 1 - tg))
                f3, f8 = (s3 > thr).astype(float), (s8 > thr).astype(float)
                fa, fn = (f3.mean() + f8.mean()) / 2, f3.mean()
                # person bootstrap: flag(all) = (C f3 + C f8) / (2 sum C), flag(neu) = C f3 / sum C
                tot = Cp.sum(1)
                diff = (Cp @ f3) / tot - (Cp @ f3 + Cp @ f8) / (2 * tot)
                h4[f"bpcer_dev{int(tg * 100)}"] = {"threshold": thr, "flag_all_pct": 100 * fa, "flag_neutral_pct": 100 * fn, "flag_smiling_pct": 100 * f8.mean(),
                                                   "neu_minus_all_pts": 100 * (fn - fa), "ci_pts": [100 * float(np.percentile(diff, 2.5)), 100 * float(np.percentile(diff, 97.5))]}
            res["h4"] = h4
        else:
            res["h4"] = None
        out.append(res)
        v0 = res["variants"]["frll_bona:orig"]; fp = res["pairs"].get("feret")
        print(lab, "FRLL", v0 and (v0["above"], v0["below"], v0["tied"], round(v0["share"], 3)),
              "FERET clear", fp and (fp["probe_clear"]["above"], fp["probe_clear"]["below"], fp["probe_clear"]["tied"], round(fp["probe_clear"]["share"], 3)), flush=True)
    if SMOKE:
        print(json.dumps(out[0], indent=0)[:2500])
        print("smoke ok")
        return
    json.dump({"B": B, "seed": SEED, "variants": list(V), "n_pairs": {k: len(v) for k, v in pairs.items()}, "detectors": out}, open(OUT / "c1c_sep.json", "w"), indent=1)
    with open(OUT / "c1c_sep.csv", "w", newline="") as fh:
        w = csv.writer(fh)
        w.writerow(["detector", "group", "ckpt", "check", "n", "above", "below", "tied", "share", "lo", "hi"])
        for r in out:
            for vn, v in r["variants"].items():
                if v:
                    w.writerow([r["label"], r["group"], r["ckpt"], f"FRLL {vn}", v["n"], v["above"], v["below"], v["tied"], f"{v['share']:.4f}", f"{v['ci'][0]:.4f}", f"{v['ci'][1]:.4f}"])
            for pn, d in r["pairs"].items():
                if d:
                    for sn in ("probe_clear", "all"):
                        v = d[sn]
                        w.writerow([r["label"], r["group"], r["ckpt"], f"{pn.upper()} {sn}", v["n"], v["above"], v["below"], v["tied"], f"{v['share']:.4f}", f"{v['ci'][0]:.4f}", f"{v['ci'][1]:.4f}"])
    print("done", flush=True)


if __name__ == "__main__":
    main()
