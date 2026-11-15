"""MS1 part 3 (registered in prereg.md part 3 before this script is run on real scores): zero-GPU reads on the existing
MS1 results.

1. Printed items missing from the part-2 read (review F8): (a) training-row minus held-out mean logit per kind (PN1
   amendment 4 item 3 form), per network; (b) FS1 R1-R6 per arm on FFHQ landmark_combined (src/PN1/fs_read.rreads,
   imported unchanged, with the pinned cues file); (c) the smoke gate: not producible (the WCSS smoke was cancelled).
2. H-mem (memorisation / dilution): gap per kind = mean(train) - mean(held-out) for attack kinds and mean(held-out) -
   mean(train) for negative kinds (positive = training rows scored more confidently than held-out rows of the kind);
   M = mean gap over the 11 FRGC/colorFERET kinds with a held-out pool. Supported if M(SbM3) < M(Sb) on >= 4 of 5 seeds;
   falsified if M(SbM3) >= M(Sb) on >= 4 of 5 seeds; otherwise inconclusive.
3. H-new-4 (appearance cue on smooth faces): within each CFD race group (A, B, L, W; main CFD set with U.S. norming),
   Spearman rho of the network's CFD logit with the 'Feminine' norming mean, per seed; group rho = median over seeds.
   Supported if rho(Sb) > 0.2 in >= 3 of 4 groups AND |rho(SbM3)| < 0.1 in >= 3 of 4 groups; falsified if rho(Sb) < 0.1
   in >= 3 of 4 groups; otherwise inconclusive. Printed: Masculine, Attractive, Babyfaced, AgeRated, LuminanceMedian;
   flag rates by self-reported gender within group.
  python3 -I ms1_part3.py [--mock] --out OUT.json
"""
import argparse
import csv
import io
import json
import pathlib
import re
import sys
import tarfile
import zipfile
import xml.etree.ElementTree as ET

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import numpy as np  # noqa: E402

import ms1common as C  # noqa: E402

RES = C.OUT / "results_rented"
EVAL = C.OUT / "pack_tree/pn1/data/manifests/pn1_eval.csv"
MAN = {"Sb": pathlib.Path("/mnt/t7/smad_next/PN1/fs_tree/pn1/data/manifests/train_Sb.csv"),
       "SbM3": C.OUT / "manifests/train_SbM3.csv", "SbV": C.OUT / "manifests/train_SbV.csv"}
CFD_POOL = C.OUT / "cfd/pool.csv"
NORM = pathlib.Path("/mnt/t7/Datasety/downloads/ChicagoFaceDatabase/cfd/CFD Version 3.0.1/"
                    "CFD 3.0.1 Norming Data and Codebook.xlsx")
ARMS = ("Sb", "SbM3", "SbV")
SEEDS = (403, 404, 405, 406, 407)
# training kind -> (held-out selector) ; FRGC / colorFERET kinds used for M
HELD = {
    "af0_photo": lambda r: r["fam"] == "af0" and r["role"] == "dev" and r["rung"] == "photo" and r["strength"] == "",
    "af0_photo61": lambda r: r["fam"] == "af0" and r["role"] == "dev" and r["rung"] == "photo" and r["strength"] == "61",
    "af0_zero": lambda r: r["fam"] == "af0" and r["role"] == "dev" and r["rung"] == "zero",
    "af0_half": lambda r: r["fam"] == "af0" and r["role"] == "dev" and r["rung"] in ("halfA", "halfB"),
    "af0_u50": lambda r: r["fam"] == "af0" and r["role"] == "dev" and r["rung"] == "u50" and r["strength"] == "",
    "lad_R0": lambda r: r["fam"] == "ladder" and r["role"] == "dev" and r["rung"] == "R0" and r["strength"] == "",
    "lad_R2w": lambda r: r["fam"] == "ladder" and r["role"] == "dev" and r["rung"] == "R2w" and r["strength"] == "",
    "lad_R4": lambda r: r["fam"] == "ladder" and r["role"] == "dev" and r["rung"] == "R4" and r["strength"] == "",
    "lad_S0": lambda r: r["fam"] == "splice" and r["role"] == "dev" and r["rung"] == "S0",
    "lad_S3": lambda r: r["fam"] == "splice" and r["role"] == "dev" and r["rung"] == "S3",
    "lad_S4": lambda r: r["fam"] == "splice" and r["role"] == "dev" and r["rung"] == "S4",
}
HELD_FFHQ = {
    "af0_photo": lambda r: r["fam"] == "ms1ffhq" and r["rung"] == "photo" and r["strength"] == "",
    "af0_photo61": lambda r: r["fam"] == "ms1ffhq" and r["rung"] == "photo" and r["strength"] == "fm61",
    "af0_zero": lambda r: r["fam"] == "ms1ffhq" and r["rung"] == "zero",
    "af0_u50": lambda r: r["fam"] == "ms1ffhq" and r["rung"] == "u50" and r["strength"] == "",
    "af0_u5061": lambda r: r["fam"] == "ms1ffhq" and r["rung"] == "u50" and r["strength"] == "fm61",
    "lad_R0": lambda r: r["fam"] == "ms1ffhq" and r["rung"] == "photo" and r["strength"] == "",
    "lad_R4": lambda r: r["fam"] == "ms1ffhq" and r["rung"] == "u50" and r["strength"] == "",
}
ATTACK = {"af0_u50", "af0_u5061", "lad_R4", "lad_S4"}


def xlsx_rows(path, sheet):
    ns = {"m": "http://schemas.openxmlformats.org/spreadsheetml/2006/main"}
    z = zipfile.ZipFile(path)
    ss = ["".join(t.text or "" for t in si.iter("{%s}t" % ns["m"]))
          for si in ET.fromstring(z.read("xl/sharedStrings.xml")).findall("m:si", ns)]
    wb = ET.fromstring(z.read("xl/workbook.xml"))
    rels = {r.get("Id"): r.get("Target") for r in ET.fromstring(z.read("xl/_rels/workbook.xml.rels"))}
    for s in wb.find("m:sheets", ns):
        if s.get("name") != sheet:
            continue
        t = rels[s.get("{http://schemas.openxmlformats.org/officeDocument/2006/relationships}id")]
        t = t if t.startswith("xl/") else "xl/" + t.lstrip("/")
        out = []
        for r in ET.fromstring(z.read(t)).iter("{%s}row" % ns["m"]):
            row = {}
            for c in r.findall("m:c", ns):
                col = re.match(r"[A-Z]+", c.get("r")).group(0)
                v = c.find("m:v", ns)
                row[col] = None if v is None else (ss[int(v.text)] if c.get("t") == "s" else v.text)
            out.append(row)
        return out
    raise KeyError(sheet)


def norming():
    rows = xlsx_rows(NORM, "CFD U.S. Norming Data")
    hi = next(i for i, r in enumerate(rows) if r.get("A") == "Model")
    head = {v: k for k, v in rows[hi].items() if v}
    out = {}
    for r in rows[hi + 2:]:
        m = r.get("A")
        if not m or not re.match(r"^[ABLW][FM]-\d+$", m):
            continue
        rec = {}
        for var in ("Feminine", "Masculine", "Attractive", "Babyfaced", "AgeRated", "LuminanceMedian", "GenderSelf"):
            v = r.get(head[var])
            try:
                rec[var] = float(v)
            except (TypeError, ValueError):
                rec[var] = v
        out[m] = rec
    return out


def load_npz(tar, member_end):
    with tarfile.open(tar) as t:
        m = [x for x in t.getmembers() if x.name.endswith(member_end)][0]
        return np.load(io.BytesIO(t.extractfile(m).read()))


def spearman(a, b):
    from scipy.stats import spearmanr
    return float(spearmanr(a, b).correlation)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--mock", action="store_true")
    ap.add_argument("--out", required=True)
    a = ap.parse_args()
    M = list(csv.DictReader(open(EVAL)))
    rng = np.random.default_rng(1)
    ev, tr, cfd = {}, {}, {}
    for arm in ARMS:
        man = {r["path"]: r for r in csv.DictReader(open(MAN[arm]))}
        for s in SEEDS:
            if a.mock:
                ev[(arm, s)] = {r["id"]: float(rng.normal(-3 if r["label"] == "0" else 3, 0.5)) for r in M}
                tr[(arm, s)] = [(p, float(rng.normal(-3.2 if x["label"] == "0" else 3.2, 0.3)), x["kind"], x["db"])
                                for p, x in man.items()]
                cfd[(arm, s)] = {f"cfd_{i:04d}": float(rng.normal(-3.3, 0.4)) for i in range(831)}
                continue
            tar = RES / f"MS1_{arm}_s{s}.tar"
            z = load_npz(tar, "scores_eval.npz")
            ev[(arm, s)] = dict(zip([str(i) for i in z["id"]], z["logit"].astype(float)))
            z = load_npz(tar, "scores_train.npz")
            rows = []
            for p, lg in zip([str(x) for x in z["path"]], z["logit"].astype(float)):
                key = p[p.index("train/"):] if "train/" in p else p
                x = man.get(key)
                if x is not None:
                    rows.append((key, lg, x["kind"], x["db"]))
            tr[(arm, s)] = rows
            zc = np.load(RES / "heldout" / f"MS1H_{arm}_s{s}_cfd.npz")
            cfd[(arm, s)] = dict(zip([str(i) for i in zc["id"]], zc["logit"].astype(float)))
    out = {"mock": a.mock, "smoke_gate": "not producible: the WCSS smoke job (6308826) was cancelled by the lead on 13 Nov "
                                       "00:00 before it ran; the rented runs had no separate smoke"}
    # 1a + H-mem
    gaps, Mstat = {}, {}
    for (arm, s), rows in tr.items():
        E = ev[(arm, s)]
        g = {}
        for kind, sel in HELD.items():
            t = [lg for _, lg, k, db in rows if k == kind and db in ("frgc", "feret")]
            h = [E[r["id"]] for r in M if sel(r) and r["id"] in E]
            if t and h:
                d = np.mean(t) - np.mean(h)
                g[kind] = dict(n_train=len(t), n_held=len(h), train_mean=float(np.mean(t)), held_mean=float(np.mean(h)),
                               gap=float(d if kind in ATTACK else -d))
        for kind, sel in HELD_FFHQ.items():
            t = [lg for _, lg, k, db in rows if k == kind and db == "ffhq"]
            h = [E[r["id"]] for r in M if sel(r) and r["id"] in E]
            if t and h:
                d = np.mean(t) - np.mean(h)
                g["ffhq_" + kind] = dict(n_train=len(t), n_held=len(h), train_mean=float(np.mean(t)),
                                         held_mean=float(np.mean(h)), gap=float(d if kind in ATTACK else -d))
        gaps[f"{arm}_s{s}"] = g
        Mstat[(arm, s)] = float(np.mean([g[k]["gap"] for k in HELD if k in g]))
    lower = sum(1 for s in SEEDS if Mstat[("SbM3", s)] < Mstat[("Sb", s)])
    hm = "supported" if lower >= 4 else ("falsified" if (5 - lower) >= 4 else "inconclusive")
    out["train_minus_heldout"] = gaps
    out["H_mem"] = dict(M={f"{k[0]}_s{k[1]}": v for k, v in Mstat.items()}, seeds_SbM3_lower=lower, verdict=hm)
    # 1b FS1 R1-R6 per arm
    try:
        sys.path.insert(0, str(C.SRC / "PN1"))
        FR = C.load(C.SRC / "PN1/fs_read.py", "fs_read")
        zc = np.load("/mnt/t7/smad_next/PN1/cues/a14_lcomb.npz")
        cid = {str(i): c for i, c in zip(zc["ids"], zc["cues"])}
        names = [str(n) for n in zc["names"]]
        lc_m = [r["id"] for r in M if r["fam"] == "ffhq_lcomb" and r["rung"] == "landmark_combined_orig"]
        lc_g = [r["id"] for r in M if r["fam"] == "ffhq_lcomb" and r["rung"] == "landmark_combined_resmatch"]
        cmp_m = [r["id"] for r in M if r["fam"] == "ffhq" and r["rung"] == "landmark_complete_orig"]
        cmp_g = [r["id"] for r in M if r["fam"] == "ffhq" and r["rung"] == "landmark_complete_resmatch"]
        hc = {r["host"]: r["id"] for r in M if r["fam"] == "ffhq" and r["rung"] == "landmark_complete_orig"}
        hb = {r["host"]: r["id"] for r in M if r["fam"] == "ffhq_lcomb" and r["rung"] == "landmark_combined_orig"}
        pk = [(hc[k], hb[k]) for k in sorted(set(hc) & set(hb))]
        out["FS1_R1_R6"] = {str(s): FR.rreads({arm: ev[(arm, s)] for arm in ARMS}, lc_m, lc_g, cid, names, cmp_m, cmp_g, pk)
                            for s in SEEDS}
    except Exception as e:      # printed item only; a failure is reported, not hidden
        out["FS1_R1_R6"] = f"not produced: {type(e).__name__}: {e}"
    # H-new-4
    norm = norming()
    pool = list(csv.DictReader(open(CFD_POOL)))
    model_of = {}
    for r in pool:
        mm = re.search(r"CFD-([ABLW][FM]-\d+)-\d+-N\.jpg$", r["raw"])
        if mm and r["aligned"] == "1" and "/CFD/" in r["raw"]:
            model_of[r["id"]] = mm.group(1)
    ids = [i for i in sorted(model_of) if model_of[i] in norm]
    res = {}
    for var in ("Feminine", "Masculine", "Attractive", "Babyfaced", "AgeRated", "LuminanceMedian"):
        res[var] = {}
        for arm in ARMS:
            per = {}
            for grp in "ABLW":
                gi = [i for i in ids if model_of[i][0] == grp and isinstance(norm[model_of[i]][var], float)]
                rhos = [spearman([cfd[(arm, s)][i] for i in gi], [norm[model_of[i]][var] for i in gi]) for s in SEEDS]
                per[grp] = dict(n=len(gi), rho_per_seed=rhos, rho_median=float(np.median(rhos)))
            res[var][arm] = per
    fem = res["Feminine"]
    sb_hi = sum(1 for g in "ABLW" if fem["Sb"][g]["rho_median"] > 0.2)
    m3_lo = sum(1 for g in "ABLW" if abs(fem["SbM3"][g]["rho_median"]) < 0.1)
    sb_lo = sum(1 for g in "ABLW" if fem["Sb"][g]["rho_median"] < 0.1)
    v4 = "supported" if (sb_hi >= 3 and m3_lo >= 3) else ("falsified" if sb_lo >= 3 else "inconclusive")
    flags = {arm: {f"{grp}{sex}": float(np.mean([np.mean([cfd[(arm, s)][i] > 0 for i in ids
                                                         if model_of[i][:2] == grp + sex]) for s in SEEDS]))
                   for grp in "ABLW" for sex in "FM"} for arm in ARMS}
    out["H_new_4"] = dict(n_models=len(ids), correlations=res, Sb_groups_rho_gt_0_2=sb_hi,
                          SbM3_groups_abs_rho_lt_0_1=m3_lo, Sb_groups_rho_lt_0_1=sb_lo, verdict=v4,
                          own_rule_flag_by_group_sex_mean_over_seeds=flags)
    json.dump(out, open(a.out, "w"), indent=1, default=float)
    print(json.dumps(dict(H_mem=out["H_mem"]["verdict"], H_mem_lower=lower, H_new_4=v4, Sb_hi=sb_hi, SbM3_lo=m3_lo,
                          R1_R6=("ok" if isinstance(out["FS1_R1_R6"], dict) else out["FS1_R1_R6"]))))


if __name__ == "__main__":
    if not sys.flags.isolated:
        sys.exit("run with python3 -I")
    main()
