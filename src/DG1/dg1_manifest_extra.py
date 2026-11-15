"""Diffusion-autoencoder generation on Athena (DG1): person-use and cue columns for the manifest (pre-run review findings
5, 6, 8; no GPU, no detector). Reads manifest.csv written by dg1_validity.py and adds:

  png_bytes                file size of the image
  ver_host_indep / ver_partner_indep   verification against the independent AR1 reference photo R (glint, FMR 1e-3)
  db, cycle_id             database; index of the host's partner cycle (folds must hold out whole cycles)
  pn1_role, test_read, val_host, val_partner   protocol-network split (PN1 ladder_split.csv): role, test-read flag,
                           validation-reserved host / partner (prep_train.is_val, as written in the split file)
  pd1_host, pd1_partner    person used to fit the existing paired-differences heads (PD1 DiffAE items.csv, set 'tr')
  wedge_in, grey_in        the inputs of this image include a photo with a black wedge (share of exact-black pixels in
                           the DiffAE-aligned 256 input > 0.01) / a greyscale photo (channel spread max - min <= 2 grey levels
                           at every pixel; the aligner leaves at most 2 levels of colour noise in grey sources)
  twin_pair                host and partner are one of the two probable twin pairs (frgc:04637/04638, frgc:04692/04856)
  same_date                the two input photos share a capture date (H_session of the host = S_session of the partner)
  pair_disagree            mean |first input - second input| in the face box (rows 70-220, columns 64-192), grey levels
  flagged                  any of wedge_in, grey_in, twin_pair, same_date
Writes manifest_full.csv and validity_full.json (per pool: all images, unflagged images only, and per database; median
[IQR] of cosines, bytes, Laplacian variance, asymmetry; verification shares incl. against the independent reference).

usage: .venv-spark/bin/python -I dg1_manifest_extra.py --manifest CSV --pool CSV --pn1-split CSV --pd1-items CSV
                                --pool-a256 DIR --gen-root DIR --out-dir DIR
"""
import argparse
import csv
import json
import pathlib
import sys

import numpy as np

THR = 0.23939879320561908          # arc2face_stats.json thresholds.glint fmr_1e-3 (as dg1_validity.py)
TWINS = ({"frgc:04637", "frgc:04638"}, {"frgc:04692", "frgc:04856"})
BOX = (slice(70, 221), slice(64, 193))


def q(v):
    v = np.asarray([x for x in v if x == x], float)
    if not len(v):
        return {"n": 0}
    return {"n": int(len(v)), "median": float(np.median(v)), "q25": float(np.percentile(v, 25)),
            "q75": float(np.percentile(v, 75))}


def main():
    ap = argparse.ArgumentParser()
    for k in ("manifest", "pool", "pn1-split", "pd1-items", "pool-a256", "gen-root", "out-dir"):
        ap.add_argument("--" + k, required=True)
    a = ap.parse_args()
    from PIL import Image
    pool = {r["pid"]: r for r in csv.DictReader(open(a.pool))}
    split = {r["pid"]: r for r in csv.DictReader(open(a.pn1_split))}
    pd1 = set()
    for r in csv.DictReader(open(a.pd1_items)):
        if r["set"] == "tr":
            pd1 |= set(r["persons"].split(";"))
    cyc, n_cyc = {}, 0                 # cycles numbered 0..n-1 in order of their smallest host id
    for p in sorted(pool):
        if p in cyc:
            continue
        q_ = p
        while q_ not in cyc:
            cyc[q_] = n_cyc
            q_ = pool[q_]["B_pid"]
        n_cyc += 1
    al = pathlib.Path(a.pool_a256)
    stats, arr = {}, {}

    def inp(stem):
        if stem not in arr:
            x = np.asarray(Image.open(al / f"{stem}.png").convert("RGB")).astype(np.int16)
            arr[stem] = x
            stats[stem] = {"black": float((x.max(2) == 0).mean()),
                           "grey": bool(int(x.max(2).astype(int).__sub__(x.min(2)).max()) <= 2)}
        return arr[stem], stats[stem]

    rows = list(csv.DictReader(open(a.manifest)))
    gen_root = pathlib.Path(a.gen_root)
    for r in rows:
        r["png_bytes"] = (gen_root / r["image"]).stat().st_size
        hi, pi = float(r["cos_host_indep"]), float(r["cos_partner_indep"])
        r["ver_host_indep"] = int(hi >= THR) if hi == hi else ""
        r["ver_partner_indep"] = int(pi >= THR) if pi == pi else ""
        for k in ("db", "cycle_id", "pn1_role", "test_read", "val_host", "val_partner", "pd1_host", "pd1_partner",
                  "wedge_in", "grey_in", "twin_pair", "same_date", "pair_disagree", "flagged"):
            r[k] = ""
        if r["set"] != "B":
            r["db"] = "frll"
            continue
        h, p = r["host"], r["partner"]
        r["db"] = h.split(":")[0]
        r["cycle_id"] = cyc[h]
        sp = split[h]
        r["pn1_role"], r["test_read"], r["val_host"] = sp["role"], sp["test_read"], sp["is_val"]
        r["val_partner"] = split[p]["is_val"] if p else ""
        r["pd1_host"] = int(h in pd1)
        r["pd1_partner"] = int(p in pd1) if p else ""
        stems = [s for s in (r["src_a"], r["src_b"]) if s]
        stems = sorted({s.replace("__flip", "") for s in stems})
        st = [inp(s)[1] for s in stems]
        r["wedge_in"] = int(any(s["black"] > 0.01 for s in st))
        r["grey_in"] = int(any(s["grey"] for s in st))
        r["twin_pair"] = int(bool(p) and p != h and {h, p} in TWINS)
        r["same_date"] = int(bool(p) and p != h and pool[h]["H_session"] == pool[p]["S_session"])
        if r["src_b"] and not r["src_b"].endswith("__flip"):
            x1, x2 = inp(r["src_a"])[0], inp(r["src_b"])[0]
            r["pair_disagree"] = round(float(np.abs(x1[BOX] - x2[BOX]).mean()), 3)
        r["flagged"] = int(r["wedge_in"] or r["grey_in"] or r["twin_pair"] or r["same_date"])
    od = pathlib.Path(a.out_dir)
    od.mkdir(parents=True, exist_ok=True)
    with open(od / "manifest_full.csv", "w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=list(rows[0]), lineterminator="\n")
        w.writeheader()
        w.writerows(rows)

    def summ(g):
        f = lambda k: [float(m[k]) for m in g if m[k] not in ("", "nan")]  # noqa: E731
        s = {"n": len(g), "cos_host": q(f("cos_host")), "cos_partner": q(f("cos_partner")),
             "verify_host": float(np.mean([int(m["ver_host"]) for m in g])),
             "png_bytes": q(f("png_bytes")), "lapvar_box": q(f("lapvar_box")), "asym_box": q(f("asym_box"))}
        vp = [m for m in g if m["ver_partner"] != ""]
        if vp:
            s["verify_partner"] = float(np.mean([int(m["ver_partner"]) for m in vp]))
            s["verify_both"] = float(np.mean([int(m["ver_host"]) * int(m["ver_partner"]) for m in vp]))
        vi = [m for m in g if m["ver_host_indep"] != ""]
        if vi:
            s["verify_host_indep"] = float(np.mean([int(m["ver_host_indep"]) for m in vi]))
            s["n_host_indep"] = len(vi)
        vpi = [m for m in g if m["ver_partner_indep"] != ""]
        if vpi:
            s["verify_partner_indep"] = float(np.mean([int(m["ver_partner_indep"]) for m in vpi]))
            both = [m for m in vpi if m["ver_host_indep"] != ""]
            s["verify_both_indep"] = float(np.mean([int(m["ver_host_indep"]) * int(m["ver_partner_indep"]) for m in both]))
        return s

    out = {"threshold": THR, "pools": {}, "flags": {}}
    for key in sorted({(m["set"], m["pool"]) for m in rows}):
        g = [m for m in rows if (m["set"], m["pool"]) == key]
        e = {"all": summ(g)}
        if key[0] == "B":
            clean = [m for m in g if m["flagged"] == 0]
            e["unflagged"] = summ(clean) if clean else {"n": 0}
            for db in ("frgc", "feret"):
                gd = [m for m in g if m["db"] == db]
                if gd:
                    e[db] = summ(gd)
            out["flags"][key[1]] = {k: sum(1 for m in g if m[k] == 1) for k in ("wedge_in", "grey_in", "twin_pair", "same_date", "flagged")}
        out["pools"][f"{key[0]}/{key[1]}"] = e
    json.dump(out, open(od / "validity_full.json", "w"), indent=1)
    print(json.dumps(out["flags"], indent=1))


if __name__ == "__main__":
    sys.exit(main())
