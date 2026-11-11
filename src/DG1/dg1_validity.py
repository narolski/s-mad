"""Diffusion-autoencoder generation on Athena (DG1): equivalence gate, manifest and validity numbers (DGX; no detector).

Face-recognition embedder = the A43 manifest's route: prep_eval.kps (registered prep_eval.py, imported unchanged after
its sha256 check; insightface buffalo_l detection) -> insightface norm_crop -> a2f_common.embed_crops('glint')
(glintr100, sha-checked a2f_common.py); verification threshold = A23's false-match rate 1e-3 for glint, 0.239399
(arc2face_stats.json). Image statistics on the 256-px PNG (the A43 / AD1b frame): left-right asymmetry = mean
|img - mirror(img)| in rows 70-220, columns 64-192 (AD1b); Laplacian variance = var(cv2.Laplacian(grey, CV_64F)) in the
same box and in the whole frame; mean and standard deviation of the pixels.

  equiv     --gen DIR(out of eq.csv) --ref /mnt/t7/smad_heldout/a43/gen --out JSON
  manifest  --gen-root DIR (folders that each hold gen_rows.csv) --pool CSV --out-dir DIR [--gen-run athena_DG1]

usage: .venv-spark/bin/python -I dg1_validity.py <cmd> ...
"""
import argparse
import csv
import hashlib
import importlib.util
import json
import pathlib
import sys

import numpy as np

PE = pathlib.Path("/home/narolski/mambamorph-code/smadcvpr/prep_eval.py")
PE_SHA = "374408ab3a886e6df25b563bc2344d190efe2ab7b3163efbb17c9b6ca9100628"
A2F = pathlib.Path("/mnt/t7/smad_heldout/arc2face/scripts/a2f_common.py")
A2F_SHA = "d27701dbe187dd6fcc2b50f21e3631a1c1a0678cfdc9d5a6989cd9c355bfcc3c"
STATS = pathlib.Path("/mnt/t7/smad_heldout/arc2face/data/arc2face_stats.json")
STATS_SHA = "ba0422babf753faf5fd7547f41c497e5fd8d034a4ee10a7d188885eadb140b72"
RAW_FRLL = pathlib.Path("/mnt/t7/Datasety/downloads/frll_base/extracted")
BOX = (slice(70, 221), slice(64, 193))


def sha(p):
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for b in iter(lambda: f.read(1 << 22), b""):
            h.update(b)
    return h.hexdigest()


def load(path, name, pin):
    if sha(path) != pin:
        sys.exit(f"{path} is not its pinned file {pin}")
    spec = importlib.util.spec_from_file_location(name, path)
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


class Embedder:
    def __init__(self):
        self.pe = load(PE, "prep_eval", PE_SHA)
        self.a2f = load(A2F, "a2f_common", A2F_SHA)
        if sha(STATS) != STATS_SHA:
            sys.exit("arc2face_stats.json is not its pinned file")
        self.thr = float(json.load(open(STATS))["thresholds"]["glint"]["fmr_1e-3"])
        self.cache = {}

    def embed(self, paths, bs=128):
        import cv2
        from insightface.utils.face_align import norm_crop
        todo = [str(p) for p in dict.fromkeys(paths) if str(p) not in self.cache]
        for i in range(0, len(todo), bs):
            crops, ok = [], []
            for p in todo[i:i + bs]:
                img = cv2.imread(p)
                k = self.pe.kps(img) if img is not None else None
                crops.append(norm_crop(img, k) if k is not None else np.zeros((112, 112, 3), np.uint8))
                ok.append(k is not None)
            E = self.a2f.embed_crops("glint", crops)
            for p, e, o in zip(todo[i:i + bs], E, ok):
                self.cache[p] = e if o else None
            print(f"embedded {min(i + bs, len(todo))}/{len(todo)}", flush=True)

    def cos(self, p, q):
        e, f = self.cache.get(str(p)), self.cache.get(str(q))
        return float(e @ f) if e is not None and f is not None else float("nan")


def img_stats(path):
    import cv2
    im = cv2.imread(str(path))
    g = cv2.cvtColor(im, cv2.COLOR_BGR2GRAY)
    a = im.astype(np.float64)
    box = a[BOX]
    return {"mean": float(a.mean()), "std": float(a.std()),
            "asym_box": float(np.abs(box - box[:, ::-1]).mean()),
            "lapvar_box": float(cv2.Laplacian(g[BOX], cv2.CV_64F).var()),
            "lapvar_full": float(cv2.Laplacian(g, cv2.CV_64F).var())}


def pixdiff(p, q):
    import cv2
    a, b = cv2.imread(str(p)).astype(int), cv2.imread(str(q)).astype(int)
    if a.shape != b.shape:
        return None
    d = np.abs(a - b)
    return {"mean_abs": float(d.mean()), "max_abs": int(d.max()), "share_diff": float((d.max(2) > 0).mean())}


def q(v):
    v = np.asarray([x for x in v if x == x], float)
    if not len(v):
        return {"n": 0}
    return {"n": int(len(v)), "median": float(np.median(v)), "q25": float(np.percentile(v, 25)),
            "q75": float(np.percentile(v, 75)), "min": float(v.min()), "max": float(v.max())}


def cmd_equiv(a):
    gen, ref = pathlib.Path(a.gen), pathlib.Path(a.ref)
    rows = list(csv.DictReader(open(gen / "gen_rows.csv")))
    refpool = {"EQ_D20": "D20", "EQ_B20": "B20"}
    refsha = {(r["pool"], r["name"]): r["sha256"] for r in csv.DictReader(open(ref / "gen_log.rows.csv"))}
    E = Embedder()
    pairs = []
    for r in rows:
        p = gen / r["pool"] / r["name"]
        rp = ref / refpool[r["pool"]] / "png256" / r["name"]
        if sha(rp) != refsha[(refpool[r["pool"]], r["name"])]:
            sys.exit(f"{rp} is not its A43 generation-log file")
        pairs.append((r, p, rp))
    # spread between different images of the same rung (all stored A43 files of that pool)
    spread = {}
    for pool, rp in refpool.items():
        fs = sorted((ref / rp / "png256").glob("*.png"))
        st = [img_stats(f) for f in fs]
        spread[pool] = {k: {"sd": float(np.std([s[k] for s in st])), "n": len(st)} for k in st[0]}
    E.embed([p for _, p, _ in pairs] + [rp for _, _, rp in pairs])
    out = []
    for r, p, rp in pairs:
        d = pixdiff(p, rp)
        s1, s2 = img_stats(p), img_stats(rp)
        out.append({"pool": r["pool"], "name": r["name"], **d, "glint_cos_athena_vs_dgx": E.cos(p, rp),
                    "stats_athena": s1, "stats_dgx": s2,
                    "delta_over_between_image_sd": {k: abs(s1[k] - s2[k]) / spread[r["pool"]][k]["sd"] for k in s1}})
    res = {"n": len(out), "per_image": out,
           "pooled_mean_abs": float(np.mean([o["mean_abs"] for o in out])),
           "max_mean_abs": float(max(o["mean_abs"] for o in out)), "max_abs": int(max(o["max_abs"] for o in out)),
           "min_glint_cos": float(min(o["glint_cos_athena_vs_dgx"] for o in out)),
           "between_image_sd": spread,
           "reading_rule": "equivalent if the mean |difference| of every one of the 8 images is <= 2 grey levels"}
    res["equivalent"] = bool(res["max_mean_abs"] <= 2.0 and res["n"] == 8)
    json.dump(res, open(a.out, "w"), indent=1)
    print(json.dumps({k: v for k, v in res.items() if k not in ("per_image", "between_image_sd")}, indent=1))
    for o in out:
        print(o["pool"], o["name"], round(o["mean_abs"], 4), o["max_abs"], round(o["glint_cos_athena_vs_dgx"], 5))


def cmd_manifest(a):
    roots = sorted({p.parent for p in pathlib.Path(a.gen_root).glob("**/gen_rows.csv")})
    pool = {r["pid"]: r for r in csv.DictReader(open(a.pool))}
    E = Embedder()
    items = []
    for rt in roots:
        log = json.load(open(rt / "gen_log.json"))
        for r in csv.DictReader(open(rt / "gen_rows.csv")):
            f = rt / r["pool"] / r["name"]
            if sha(f) != r["sha256"]:
                sys.exit(f"{f}: not its generation-row sha256")
            items.append((rt, log, r, f))
    names = {}
    for rt, log, r, f in items:
        key = (r["pool"], r["name"])
        if key in names:
            sys.exit(f"{key} produced twice ({names[key]} and {rt})")
        names[key] = rt

    def refs(r):
        """(host reference, partner reference, host independent reference, partner independent reference)."""
        if r["set"] in ("A", "EQ"):
            h = RAW_FRLL / "neutral_front" / f"{r['src_a'][:3]}_03.jpg"
            pb = None
            if r["rung"] == "CONF":
                pb = RAW_FRLL / "smiling_front" / f"{r['host']}_08.jpg"
            elif r["rung"] == "X":
                pb = RAW_FRLL / "neutral_front" / f"{r['partner']}_03.jpg"
            return h, pb, None, None
        hr = pool[r["host"]]
        if r["rung"] == "G" and r["name"].endswith("_S.png"):
            return pathlib.Path(hr["S"]), None, pathlib.Path(hr["R"]) if hr["R"] else None, None
        pb = pi = None
        if r["rung"] in ("SAME", "NOISES", "SEMS", "DOSES"):          # second photo of the host (add-on rungs too)
            pb = pathlib.Path(hr["S"])
        elif r["rung"] in ("X", "DOSE", "NOISEX", "SEMX", "DOSEX"):
            pr = pool[r["partner"]]
            pb, pi = pathlib.Path(pr["S"]), (pathlib.Path(pr["R"]) if pr["R"] else None)
        return pathlib.Path(hr["H"]), pb, (pathlib.Path(hr["R"]) if hr["R"] else None), pi

    allp = [f for _, _, _, f in items]
    for _, _, r, _ in items:
        allp += [x for x in refs(r) if x is not None]
    E.embed(allp)
    man = []
    for rt, log, r, f in items:
        h, pb, hi, pi = refs(r)
        st = img_stats(f)
        c_h, c_p = E.cos(f, h), (E.cos(f, pb) if pb else float("nan"))
        c_hi, c_pi = (E.cos(f, hi) if hi else float("nan")), (E.cos(f, pi) if pi else float("nan"))
        man.append({"image": str(f.relative_to(pathlib.Path(a.gen_root))), "set": r["set"], "pool": r["pool"],
                    "rung": r["rung"], "host": r["host"], "partner": r["partner"], "src_a": r["src_a"],
                    "src_b": r["src_b"], "steps": r["steps"], "alpha": r["alpha"],
                    "seed": r.get("seed", "0"), "mode": r.get("mode", ""), "fresh_seed": r.get("fresh_seed", ""),
                    "gen_run": a.gen_run, "gen_node": log.get("node", ""), "device": log.get("device", ""),
                    "torch": log.get("torch", ""), "sha256": r["sha256"], "theta_xT": r["theta_xT"],
                    "face_found": int(E.cache.get(str(f)) is not None),
                    "cos_host": round(c_h, 5), "cos_partner": round(c_p, 5),
                    "cos_host_indep": round(c_hi, 5), "cos_partner_indep": round(c_pi, 5),
                    "ver_host": int(c_h >= E.thr), "ver_partner": int(c_p >= E.thr) if pb else "",
                    **{k: round(v, 4) for k, v in st.items()},
                    "ref_host": str(h), "ref_partner": str(pb or "")})
    od = pathlib.Path(a.out_dir)
    od.mkdir(parents=True, exist_ok=True)
    with open(od / "manifest.csv", "w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=list(man[0]), lineterminator="\n")
        w.writeheader()
        w.writerows(man)
    summ = {}
    for key in sorted({(m["set"], m["pool"]) for m in man}):
        g = [m for m in man if (m["set"], m["pool"]) == key]
        two = g[0]["rung"] in ("X", "DOSE", "SAME", "CONF", "NOISEX", "SEMX", "NOISES", "SEMS", "DOSEX", "DOSES")
        s = {"n": len(g), "rung": g[0]["rung"], "steps": g[0]["steps"], "faces_found": sum(m["face_found"] for m in g),
             "cos_host": q([m["cos_host"] for m in g]), "verify_host": float(np.mean([m["ver_host"] for m in g])),
             "cos_host_indep": q([m["cos_host_indep"] for m in g]),
             "asym_box": q([m["asym_box"] for m in g]), "lapvar_box": q([m["lapvar_box"] for m in g]),
             "lapvar_full": q([m["lapvar_full"] for m in g])}
        if two:
            s["cos_partner"] = q([m["cos_partner"] for m in g])
            s["cos_partner_indep"] = q([m["cos_partner_indep"] for m in g])
            s["verify_partner"] = float(np.mean([m["ver_partner"] for m in g]))
            s["verify_both"] = float(np.mean([m["ver_host"] and m["ver_partner"] for m in g]))
        summ[f"{key[0]}/{key[1]}"] = s
    out = {"threshold_glint_fmr_1e-3": E.thr, "gen_roots": [str(r) for r in roots], "rungs": summ,
           "manifest_sha256": sha(od / "manifest.csv"), "n_images": len(man)}
    json.dump(out, open(od / "validity.json", "w"), indent=1)
    with open(od / "validity.csv", "w", newline="") as fh:
        w = csv.writer(fh, lineterminator="\n")
        w.writerow(["set_pool", "rung", "steps", "n", "faces", "cos_host_med", "cos_host_iqr", "cos_partner_med",
                    "cos_partner_iqr", "verify_host", "verify_partner", "verify_both", "asym_med", "asym_iqr",
                    "lapvar_box_med", "lapvar_box_iqr"])
        for k, s in summ.items():
            iq = lambda d: f"{d.get('q25', float('nan')):.3f}-{d.get('q75', float('nan')):.3f}"  # noqa: E731
            cp = s.get("cos_partner", {})
            w.writerow([k, s["rung"], s["steps"], s["n"], s["faces_found"], f"{s['cos_host'].get('median', float('nan')):.4f}",
                        iq(s["cos_host"]), f"{cp.get('median', float('nan')):.4f}" if cp else "", iq(cp) if cp else "",
                        f"{s['verify_host']:.3f}", f"{s.get('verify_partner', float('nan')):.3f}" if cp else "",
                        f"{s.get('verify_both', float('nan')):.3f}" if cp else "",
                        f"{s['asym_box'].get('median', float('nan')):.2f}", iq(s["asym_box"]),
                        f"{s['lapvar_box'].get('median', float('nan')):.1f}", iq(s["lapvar_box"])])
    print(open(od / "validity.csv").read())


def main():
    ap = argparse.ArgumentParser()
    sp = ap.add_subparsers(dest="cmd", required=True)
    p = sp.add_parser("equiv")
    for k in ("gen", "ref", "out"):
        p.add_argument("--" + k, required=True)
    p = sp.add_parser("manifest")
    for k in ("gen-root", "pool", "out-dir"):
        p.add_argument("--" + k, required=True)
    p.add_argument("--gen-run", default="athena_DG1")
    a = ap.parse_args()
    {"equiv": cmd_equiv, "manifest": cmd_manifest}[a.cmd](a)


if __name__ == "__main__":
    main()
