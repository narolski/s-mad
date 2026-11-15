"""C1c step 2: what differs between the neutral (03) and smiling (08) FRLL photos besides expression, and the same
statistics on FERET fa/fb and FRGC same-session pairs. Headers and decoded pixels only; nothing re-encoded or written
as an image. Also computes the C1 expression-probe logits for every frame used later and writes the pair lists.
Run: /home/narolski/mambamorph-code/.venv-spark/bin/python -I src/C1c/c1c_files.py [--smoke]
"""
import csv, json, os, pathlib, re, sys, collections
from multiprocessing import Pool
import numpy as np

SMOKE = "--smoke" in sys.argv
sys.argv = [a for a in sys.argv if a != "--smoke"]
sys.path.insert(0, "/home/narolski/smad-next/src/C_cue_checks")
import c_checks as K  # noqa: E402  (stats_job: the C1 probe feature, unchanged)
from sklearn.linear_model import LogisticRegression  # noqa: E402
from sklearn.preprocessing import StandardScaler  # noqa: E402
from sklearn.pipeline import make_pipeline  # noqa: E402

RAW = pathlib.Path("/mnt/t7/Datasety/downloads/frll_base/extracted")
MC = pathlib.Path("/home/narolski/mambamorph-code")
D = MC / "smadcvpr_data"
EVAL = D / "manifests/eval.csv"
OUT = pathlib.Path("/home/narolski/smad-next/experiments/C1c_smiling-half-expression-or-detail")
REG = {"bg_tl": (5, 90, 5, 40), "bg_tr": (5, 90, 472, 507), "forehead": (90, 150, 200, 310), "mouth": (300, 432, 150, 366)}


def ge(g):
    return float((np.diff(g, axis=0) ** 2).mean() + (np.diff(g, axis=1) ** 2).mean())


def raw_job(p):
    from PIL import Image, JpegImagePlugin
    with Image.open(p) as im:
        q = {int(k): list(v) for k, v in getattr(im, "quantization", {}).items()}
        sub = int(JpegImagePlugin.get_sampling(im)) if im.format == "JPEG" else None
        a = np.asarray(im.convert("RGB"), dtype=np.float64)
        size = im.size
    g = a.mean(2)
    tl, tr = g[20:140, 20:140], g[20:140, -140:-20]
    return {"path": str(p), "bytes": os.path.getsize(p), "w": size[0], "h": size[1], "qtables": q, "subsampling": sub,
            "noise_tl": ge(tl), "noise_tr": ge(tr), "sd_tl": float(tl.std()), "sd_tr": float(tr.std()), "noise_all": ge(g)}


def frame_job(p):
    from PIL import Image
    with Image.open(p) as im:
        a = np.asarray(im.convert("RGB"), dtype=np.float64)
    g = a.mean(2)
    o = {"path": str(p), "bytes": os.path.getsize(p)}
    for k, (r0, r1, c0, c1) in REG.items():
        o[f"noise_{k}"] = ge(g[r0:r1, c0:c1])
        o[f"lum_{k}"] = float(g[r0:r1, c0:c1].mean())
    o["mouth_feat"] = K.stats_job((str(p), "al"))["mouth"]
    return o


def pairs_from_manifest(rows):
    dev = [r for r in rows if r["set"] == "devbona" and r["variant"] == "orig"]
    fe = collections.defaultdict(dict)
    frg = collections.defaultdict(list)
    for r in dev:
        n = r["path"].rsplit("/", 1)[1]
        m = re.match(r"^(\d{5})_(\d{6})_(fa|fb)(_[a-z])?_orig", n)
        if m:
            fe[(m.group(1), m.group(2), m.group(4) or "")][m.group(3)] = r
            continue
        m = re.match(r"^nd1_([A-Za-z]+\d{4})_(\d{5})d(\d+)_orig", n)
        if m:
            frg[(m.group(2), m.group(1))].append((int(m.group(3)), r))
    fer = [("FERET", f"{k[0]}_{k[1]}{k[2]}", k[0], v["fa"], v["fb"]) for k, v in sorted(fe.items()) if len(v) == 2]
    fr = []
    for (s, season), L in sorted(frg.items()):
        L = sorted(L, key=lambda x: x[0])
        i = 0
        while i < len(L) - 1:
            if L[i + 1][0] == L[i][0] + 1:
                fr.append(("FRGC", f"{s}_{season}_d{L[i][0]}", s, L[i][1], L[i + 1][1]))
                i += 2
            else:
                i += 1
    return fer, fr


def share_line(a, b):
    a, b = np.asarray(a, float), np.asarray(b, float)
    ok = np.isfinite(a) & np.isfinite(b) & (a > 0)
    return {"n": int(ok.sum()), "share_08_gt_03": float(np.mean(b[ok] > a[ok])), "median_03": float(np.median(a[ok])), "median_08": float(np.median(b[ok])),
            "median_ratio": float(np.median(b[ok] / a[ok])), "min_ratio": float(np.min(b[ok] / a[ok])), "max_ratio": float(np.max(b[ok] / a[ok]))}


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    rows = list(csv.DictReader(open(EVAL)))
    # ---------------- FRLL raw files
    P = sorted({m.group(1) for f in os.listdir(RAW / "neutral_front") for m in [re.match(r"^(\d{3})_03\.jpg$", f)] if m})
    if SMOKE:
        P = P[:8]
    rp = [RAW / "neutral_front" / f"{p}_03.jpg" for p in P] + [RAW / "smiling_front" / f"{p}_08.jpg" for p in P]
    with Pool(8) as pool:
        RR = pool.map(raw_job, rp)
    R3 = {pathlib.Path(o["path"]).name[:3]: o for o in RR if "_03" in o["path"]}
    R8 = {pathlib.Path(o["path"]).name[:3]: o for o in RR if "_08" in o["path"]}
    res = {"raw": {}, "frame": {}, "pairs": {}}
    for k in ("bytes", "noise_tl", "noise_tr", "sd_tl", "sd_tr", "noise_all"):
        res["raw"][k] = share_line([R3[p][k] for p in P], [R8[p][k] for p in P])
    res["raw"]["same_pixel_size"] = int(sum((R3[p]["w"], R3[p]["h"]) == (R8[p]["w"], R8[p]["h"]) for p in P))
    res["raw"]["pixel_sizes"] = sorted({f"{R3[p]['w']}x{R3[p]['h']}" for p in P} | {f"{R8[p]['w']}x{R8[p]['h']}" for p in P})
    res["raw"]["same_qtables"] = int(sum(R3[p]["qtables"] == R8[p]["qtables"] for p in P))
    res["raw"]["n_distinct_qtable_sets"] = len({json.dumps(o["qtables"], sort_keys=True) for o in RR})
    res["raw"]["same_subsampling"] = int(sum(R3[p]["subsampling"] == R8[p]["subsampling"] for p in P))
    res["raw"]["subsampling_values"] = sorted({str(o["subsampling"]) for o in RR})
    # ---------------- aligned FRLL frames (frll_bona orig) and their region statistics
    fb = {re.match(r"^(\d{3})_(\d{2})_", r["path"].rsplit("/", 1)[1]).groups(): r for r in rows
          if r["family"] == "frll_bona" and r["variant"] == "orig"}
    fb = {k: v for k, v in fb.items() if k[0] in P}
    fer, frg = pairs_from_manifest(rows)
    if SMOKE:
        fer, frg = fer[:8], frg[:8]
    frames = sorted({str(D / r["path"]) for r in fb.values()} | {str(D / x[3]["path"]) for x in fer + frg} | {str(D / x[4]["path"]) for x in fer + frg})
    print(len(P), "persons;", len(frames), "frames;", len(fer), "FERET pairs;", len(frg), "FRGC pairs", flush=True)
    with Pool(8) as pool:
        FR = {o["path"]: o for o in pool.map(frame_job, frames, chunksize=16)}
    stats = [f"noise_{k}" for k in REG] + [f"lum_{k}" for k in REG] + ["bytes"]
    for k in stats:
        res["frame"][k] = share_line([FR[str(D / fb[(p, "03")]["path"])][k] for p in P], [FR[str(D / fb[(p, "08")]["path"])][k] for p in P])
    # ---------------- the C1 probe (fit on the 204 FRLL frames), logits for every frame
    Xg = np.array([FR[str(D / fb[(p, e)]["path"])]["mouth_feat"] for p in P for e in ("03", "08")])
    yg = np.array([0, 1] * len(P))
    probe = make_pipeline(StandardScaler(), LogisticRegression(C=0.1, max_iter=5000)).fit(Xg, yg)
    logit = {pth: float(probe.decision_function(np.array([o["mouth_feat"]]))[0]) for pth, o in FR.items()}
    with open(OUT / "c1c_probe_logits.csv", "w", newline="") as fh:
        w = csv.writer(fh)
        w.writerow(["path", "probe_logit"])
        for pth in frames:
            w.writerow([pth.replace(str(D) + "/", ""), f"{logit[pth]:.4f}"])
    # ---------------- pairs: lists and region statistics by probe direction
    for name, L in (("FERET", fer), ("FRGC", frg)):
        out = []
        for pool_, pid, subj, ra, rb in L:
            pa, pb = str(D / ra["path"]), str(D / rb["path"])
            la, lb = logit[pa], logit[pb]
            out.append({"pool": pool_, "pair": pid, "subject": subj, "id_a": ra["id"], "id_b": rb["id"], "path_a": ra["path"], "path_b": rb["path"],
                        "probe_a": la, "probe_b": lb, "probe_clear": int((la > 0) != (lb > 0)), "more_smiling": "b" if lb > la else "a"})
        with open(OUT / f"c1c_{name.lower()}_pairs.csv", "w", newline="") as fh:
            w = csv.DictWriter(fh, fieldnames=list(out[0]))
            w.writeheader()
            w.writerows(out)
        clear = [o for o in out if o["probe_clear"]]
        st = {"n_pairs": len(out), "n_subjects": len({o["subject"] for o in out}), "n_probe_clear": len(clear),
              "probe_smiling_share_a": float(np.mean([o["probe_a"] > 0 for o in out])), "probe_smiling_share_b": float(np.mean([o["probe_b"] > 0 for o in out]))}
        for k in stats:
            more = [FR[str(D / (o["path_b"] if o["more_smiling"] == "b" else o["path_a"]))][k] for o in clear]
            less = [FR[str(D / (o["path_a"] if o["more_smiling"] == "b" else o["path_b"]))][k] for o in clear]
            st[k + " (more-smiling vs less-smiling, probe-clear)"] = share_line(less, more)
        res["pairs"][name] = st
    # FRLL probe sanity: within-person share probe(08) > probe(03) (in-sample)
    res["frll_probe_insample_share_08_gt_03"] = float(np.mean([logit[str(D / fb[(p, "08")]["path"])] > logit[str(D / fb[(p, "03")]["path"])] for p in P]))
    # per-person CSV
    with open(OUT / "c1c_frll_files.csv", "w", newline="") as fh:
        w = csv.writer(fh)
        hdr = ["person"] + [f"raw_{k}_{e}" for k in ("bytes", "noise_tl", "noise_tr", "sd_tl") for e in ("03", "08")] + ["raw_same_qtables", "raw_same_size"]
        hdr += [f"frame_{k}_{e}" for k in stats for e in ("03", "08")] + [f"probe_{e}" for e in ("03", "08")]
        w.writerow(hdr)
        for p in P:
            f3, f8 = FR[str(D / fb[(p, "03")]["path"])], FR[str(D / fb[(p, "08")]["path"])]
            w.writerow([p] + [f"{(R3 if e == '03' else R8)[p][k]:.4f}" for k in ("bytes", "noise_tl", "noise_tr", "sd_tl") for e in ("03", "08")]
                       + [int(R3[p]["qtables"] == R8[p]["qtables"]), int((R3[p]["w"], R3[p]["h"]) == (R8[p]["w"], R8[p]["h"]))]
                       + [f"{(f3 if e == '03' else f8)[k]:.4f}" for k in stats for e in ("03", "08")]
                       + [f"{logit[str(D / fb[(p, e)]['path'])]:.4f}" for e in ("03", "08")])
    print(json.dumps(res, indent=1)[:6000], flush=True)
    if not SMOKE:
        json.dump(res, open(OUT / "c1c_files.json", "w"), indent=1)
    else:
        print("smoke ok")


if __name__ == "__main__":
    main()
