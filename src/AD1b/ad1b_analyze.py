"""AD1b analysis (CPU, spark venv): code distances (Part 1), pixel comparisons, asymmetry and glintr100 cosines (Part 2).
usage: python -I ad1b_analyze.py --gen DIR --out DIR [--smoke]
"""
import argparse, csv, importlib.util, json, pathlib, sys
import numpy as np
import cv2

A43 = pathlib.Path("/mnt/t7/smad_heldout/a43/gen")
A256 = pathlib.Path("/mnt/t7/smad_heldout/a41_diffae/data/a41diffae/a256/png256")
RAW = pathlib.Path("/mnt/t7/Datasety/downloads/frll_base/extracted")
PE_P = pathlib.Path("/home/narolski/mambamorph-code/smadcvpr/prep_eval.py")
A2F_P = pathlib.Path("/mnt/t7/smad_heldout/arc2face/scripts/a2f_common.py")
A2F_SHA = "d27701dbe187dd6fcc2b50f21e3631a1c1a0678cfdc9d5a6989cd9c355bfcc3c"
BOX = (slice(70, 220), slice(64, 192))     # rows, cols of the 256 frame (symmetric about column 128)


def load(p, name):
    sys.path.insert(0, str(p.parent))
    spec = importlib.util.spec_from_file_location(name, p)
    m = importlib.util.module_from_spec(spec)
    sys.modules[name] = m
    spec.loader.exec_module(m)
    return m


def med_iqr(v):
    v = np.asarray(v, float)
    v = v[np.isfinite(v)]
    if not len(v):
        return None
    return {"median": float(np.median(v)), "q25": float(np.percentile(v, 25)), "q75": float(np.percentile(v, 75)), "n": int(len(v))}


def im(p):
    x = cv2.imread(str(p), cv2.IMREAD_COLOR)
    if x is None:
        raise FileNotFoundError(p)
    return x.astype(np.float64)


def mad(a, b):
    d = np.abs(im(a) - im(b))
    return float(d.mean()), float(d.max())


def asym(p):
    x = im(p)
    return float(np.abs(x - x[:, ::-1])[BOX].mean())


def dists(Z, a, b):
    u, v = Z[a].ravel().astype(np.float64), Z[b].ravel().astype(np.float64)
    return float(np.linalg.norm(u - v)), float(1 - u @ v / (np.linalg.norm(u) * np.linalg.norm(v)))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--gen", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--smoke", action="store_true")
    ap.add_argument("--no-fr", action="store_true")
    a = ap.parse_args()
    G, O = pathlib.Path(a.gen), pathlib.Path(a.out)
    O.mkdir(parents=True, exist_ok=True)
    zf = np.load(G / "codes_z.npz")
    Z = dict(zip(zf["names"].tolist(), zf["z"]))
    xf = np.load(G / "codes_xT.npz")
    X = dict(zip(xf["names"].tolist(), xf["xT"]))
    persons = sorted({k[:3] for k in Z if not k.startswith("pool_")})
    nxt = {p: persons[(i + 1) % len(persons)] for i, p in enumerate(persons)}
    res = {"part1": {}, "part2": {}}
    # ---------------- Part 1
    for label, CODES, plist in (("z_sem FRLL", Z, persons), ("x_T FRLL (subset)", X, [p for p in persons if f"{p}_08" in X])):
        per = []
        for p in plist:
            A, F, Ap, B = f"{p}_03", f"{p}_03_flip", f"{p}_08", f"{nxt[p]}_03"
            if not all(k in CODES for k in (A, F, Ap, B)):
                continue
            ef, cf = dists(CODES, A, F)
            ea, ca = dists(CODES, A, Ap)
            eb, cb = dists(CODES, A, B)
            per.append({"person": p, "euc_flip": ef, "euc_other_photo": ea, "euc_other_person": eb, "cos_flip": cf, "cos_other_photo": ca,
                        "cos_other_person": cb, "ratio_euc": ef / ea, "ratio_cos": cf / ca})
        res["part1"][label] = {k: med_iqr([r[k] for r in per]) for k in per[0] if k != "person"} if per else None
        with open(O / f"part1_{label.split()[0]}_{label.split()[1]}.csv", "w", newline="") as fh:
            if per:
                w = csv.DictWriter(fh, fieldnames=list(per[0])); w.writeheader(); w.writerows(per)
    tags = sorted({k[5:-2] for k in Z if k.startswith("pool_") and k.endswith("_H")})
    per = []
    for t in tags:
        H, F, S, B = f"pool_{t}_H", f"pool_{t}_H_flip", f"pool_{t}_S", f"pool_{t}_B"
        if not all(k in Z for k in (H, F, S, B)):
            continue
        ef, cf = dists(Z, H, F); ea, ca = dists(Z, H, S); eb, cb = dists(Z, H, B)
        per.append({"host": t, "euc_flip": ef, "euc_other_photo": ea, "euc_other_person": eb, "cos_flip": cf, "cos_other_photo": ca,
                    "cos_other_person": cb, "ratio_euc": ef / ea, "ratio_cos": cf / ca})
    res["part1"]["z_sem FRGC/colorFERET pool"] = {k: med_iqr([r[k] for r in per]) for k in per[0] if k != "host"} if per else None
    with open(O / "part1_z_pool.csv", "w", newline="") as fh:
        if per:
            w = csv.DictWriter(fh, fieldnames=list(per[0])); w.writeheader(); w.writerows(per)
    # ---------------- Part 2 (a), (b), (c)
    rows = {(r["pool"], r["name"]): r for r in csv.DictReader(open(G / "gen_rows.csv"))}
    b20 = [r for r in csv.DictReader(open(A43 / "gen_log.rows.csv")) if r["pool"] == "B20"]
    pa = []
    persons = [p for p in persons if (G / "PAF/png256" / f"{p}_03.png").exists()]
    res["part2"]["n_persons"] = len(persons)
    for p in persons:
        A = f"{p}_03"
        PAA, PAF, D20r = (G / k / "png256" / f"{A}.png" for k in ("PAA", "PAF", "D20r"))
        D20, C20 = A43 / "D20/png256" / f"{A}.png", A43 / "C20/png256" / f"{p}_self.png"
        r = {"person": p, "theta_PAA": rows[("PAA", A)]["theta_xT"], "PAA_finite": rows[("PAA", A)]["finite"],
             "PAA_xT_mix_finite": rows[("PAA", A)]["xT_mix_finite"], "PAA_xT_mix_maxabs_minus_xTA": rows[("PAA", A)]["xT_mix_maxabs_minus_xTA"],
             "PAA_z_equal_zA": rows[("PAA", A)]["z_equal_zA"], "theta_PAF": rows[("PAF", A)]["theta_xT"]}
        r["PAA_vs_D20_mean"], r["PAA_vs_D20_max"] = mad(PAA, D20)
        r["PAA_vs_D20r_mean"], r["PAA_vs_D20r_max"] = mad(PAA, D20r)
        r["D20r_vs_D20_mean"], r["D20r_vs_D20_max"] = mad(D20r, D20)
        r["PAF_vs_PAA_mean"], _ = mad(PAF, PAA)
        r["PAF_vs_D20_mean"], _ = mad(PAF, D20)
        r["C20_vs_PAA_mean"], _ = mad(C20, PAA)
        r["C20_vs_D20_mean"], _ = mad(C20, D20)
        r["asym_input_A"] = asym(A256 / f"{A}.png")
        r["asym_D20"], r["asym_PAA"], r["asym_PAF"], r["asym_C20"] = asym(D20), asym(PAA), asym(PAF), asym(C20)
        pa.append(r)
    bb = []
    for r in b20:
        if r["src_a"][:3] not in persons:
            continue
        f = A43 / "B20/png256" / r["name"]
        bb.append({"name": r["name"], "host": r["src_a"], "B20_vs_D20host_mean": mad(f, A43 / "D20/png256" / f"{r['src_a']}.png")[0], "asym_B20": asym(f)})
    keys = [k for k in pa[0] if k not in ("person",) and not k.startswith(("theta", "PAA_finite", "PAA_xT", "PAA_z"))]
    res["part2"]["per_person"] = {k: med_iqr([r[k] for r in pa]) for k in keys}
    res["part2"]["B20"] = {k: med_iqr([r[k] for r in bb]) for k in ("B20_vs_D20host_mean", "asym_B20")}
    res["part2"]["PAA_mixing_path"] = {"theta_values": sorted({r["theta_PAA"] for r in pa})[:10],
                                       "z_equal_zA_all": all(r["PAA_z_equal_zA"] == "True" for r in pa),
                                       "xT_mix_finite_all": all(r["PAA_xT_mix_finite"] == "True" for r in pa),
                                       "xT_mix_maxabs_minus_xTA": med_iqr([float(r["PAA_xT_mix_maxabs_minus_xTA"]) for r in pa if r["PAA_xT_mix_maxabs_minus_xTA"] not in ("", "None")]) if any(r["PAA_xT_mix_maxabs_minus_xTA"] not in ("", "None") for r in pa) else None,
                                       "PAA_render_finite_all": all(r["PAA_finite"] == "1" for r in pa),
                                       "max_PAA_vs_D20_max": max(r["PAA_vs_D20_max"] for r in pa)}
    with open(O / "part2_per_person.csv", "w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=list(pa[0])); w.writeheader(); w.writerows(pa)
    # ---------------- Part 2 (d): glintr100 cosine to the raw photo A (A43 route)
    if a.no_fr:
        res["part2"]["fr_glint"] = "skipped (--no-fr)"
        return finish(res, pa, a, O)
    PE = load(PE_P, "prep_eval")
    import hashlib
    assert hashlib.sha256(open(A2F_P, "rb").read()).hexdigest() == A2F_SHA
    A2F = load(A2F_P, "a2f_common")
    from insightface.utils.face_align import norm_crop

    def crop(path):
        img = cv2.imread(str(path))
        k = PE.kps(img)
        return (norm_crop(img, k), True) if k is not None else (np.zeros((112, 112, 3), np.uint8), False)
    keys, crops, okf = [], [], []
    for p in persons:
        for tag, path in (("raw", RAW / "neutral_front" / f"{p}_03.jpg"), ("PAF", G / "PAF/png256" / f"{p}_03.png"),
                          ("PAA", G / "PAA/png256" / f"{p}_03.png"), ("D20", A43 / "D20/png256" / f"{p}_03.png"),
                          ("C20", A43 / "C20/png256" / f"{p}_self.png")):
            c, f_ = crop(path)
            keys.append((tag, p)); crops.append(c); okf.append(f_)
    E = A2F.embed_crops("glint", crops)
    emb = {k: (e, f_) for k, e, f_ in zip(keys, E, okf)}
    fr = {}
    for tag in ("PAF", "PAA", "D20", "C20"):
        v = [float(emb[(tag, p)][0] @ emb[("raw", p)][0]) if emb[(tag, p)][1] and emb[("raw", p)][1] else np.nan for p in persons]
        fr[f"cos_{tag}_to_rawA"] = med_iqr(v)
        fr[f"faces_found_{tag}"] = int(sum(emb[(tag, p)][1] for p in persons))
    thr = 0.23939879320561908
    v = [float(emb[("PAF", p)][0] @ emb[("raw", p)][0]) for p in persons if emb[("PAF", p)][1] and emb[("raw", p)][1]]
    fr["PAF_verifies_A_at_FMR1e-3"] = float(np.mean(np.array(v) >= thr))
    res["part2"]["fr_glint"] = fr
    return finish(res, pa, a, O)


def finish(res, pa, a, O):
    # ---------------- readings (fixed in the prereg)
    p1 = res["part1"]["z_sem FRLL"]
    code_ratio = p1["ratio_euc"]["median"]
    pix_ref = "PAA"
    if not res["part2"]["PAA_mixing_path"]["PAA_render_finite_all"] or not res["part2"]["PAA_mixing_path"]["xT_mix_finite_all"]:
        pix_ref = "D20"
    num = res["part2"]["per_person"][f"PAF_vs_{pix_ref}_mean"]["median"]
    den = res["part2"]["per_person"][f"C20_vs_{pix_ref}_mean"]["median"]
    pix_ratio = num / den
    if code_ratio < 0.25 and pix_ratio < 0.25:
        flip = "flip is close to a no-op for this diffusion pipeline, so a mirror self-morph is not a useful diffusion control"
    elif code_ratio >= 0.5 and pix_ratio >= 0.5:
        flip = "flip yields a genuinely different second image"
    else:
        flip = "partial"
    m = res["part2"]["per_person"]["PAA_vs_D20_mean"]
    ident = ("Identical inputs reduce to the reconstruction" if m["median"] <= 1.0 and max(r["PAA_vs_D20_mean"] for r in pa) <= 1.0
             else "Identical inputs do not reduce to the reconstruction within 1 grey level (see cause)")
    res["readings"] = {"code_ratio_median_euc": code_ratio, "pixel_ratio": pix_ratio, "pixel_reference": pix_ref,
                       "flip_reading": flip, "identical_reading": ident}
    json.dump(res, open(O / "ad1b_result.json", "w"), indent=1)
    print(json.dumps(res["readings"], indent=1))


if __name__ == "__main__":
    main()
