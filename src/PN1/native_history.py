"""PN1 native history table (pre-run review PRERUN_PN1_FRESH_SEEDS_20261112.md improvement 1, lead item A).
POST HOC / descriptive, measurement only, no GPU, no new score: per genuine source the native inter-eye distance,
file format and frame size, beside the tier-1 own-rule (and tau_cam) flag rates already computed from the tier-1 tars.
Sources of the native numbers:
  FRGC       raw still (nd1/<session>/<id>.jpg) header; eyes from the FRGC metadata dump (rec_sub_face lefteye/righteye)
  colorFERET raw still (data/images/<subj>/<name>.ppm.bz2) header; eyes from the colorFERET ground truth (name_value)
  FRLL, H1, FFHQ, FEI   the 'native_w', 'native_h', 'ied' columns of their manifests (prep_eval.kps on the native file)
  FFHQ and FEI carry no tier-1 score (not in pn1_eval.csv): flags 'not scored' (FFHQ is scored only under amendment 13).
  python3 -I native_history.py -> experiments/PN1_.../tier1/native_history.json"""
import bz2
import csv
import pathlib
import struct
import sys

import numpy as np

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import pn1lib as K  # noqa: E402
import reads as RD  # noqa: E402
import tier1 as T1  # noqa: E402

RR = K.PN1 / "results_rented"
DS = pathlib.Path("/mnt/t7/Datasety")
FRGC_SQL = DS / "FRGC-2.0/FRGC-2.0-dist/bbaselite_FRGC_2.0/bbaselite_data_frgc2.1.sql"
FRGC_ND1 = DS / "FRGC-2.0/FRGC-2.0-dist/nd1"
FERET = DS / "colorferet"
MC = pathlib.Path("/home/narolski/mambamorph-code/smadcvpr_data/manifests")
FFHQM = pathlib.Path("/mnt/t7/smad_heldout/ffhq_morphs/manifests/ffhqm.csv")
H1M = pathlib.Path("/mnt/t7/smad_heldout/h1_poisson/data/manifests/h1poisson.csv")
FRLL_RAW = DS / "downloads/frll_base/extracted/neutral_front"
FEI_RAW = pathlib.Path("/home/narolski/mambamorph/Datasety/downloads/FEI/extracted")
FFHQ_RAW = pathlib.Path("/home/narolski/mambamorph/Datasety/downloads/FFHQ-1024")
CANON_IED = 132.0          # prep_eval.py line 3: eyes 132 px apart in the 512 frame


def magic(path):
    h = open(path, "rb").read(4)
    return "jpeg" if h[:3] == b"\xff\xd8\xff" else "png" if h[:4] == b"\x89PNG" else "bz2" if h[:3] == b"BZh" else "other"


def jpeg_size(path):
    with open(path, "rb") as f:
        f.read(2)
        while True:
            m = f.read(2)
            if len(m) < 2 or m[0] != 0xFF:
                return None
            ln = struct.unpack(">H", f.read(2))[0]
            if m[1] in (0xC0, 0xC1, 0xC2):
                f.read(1)
                h, w = struct.unpack(">HH", f.read(4))
                return w, h
            f.read(ln - 2)


def ppm_size(path):
    raw = bz2.open(path).read(64).split()
    return int(raw[1]), int(raw[2])


def frgc_eyes():
    rec_of, eyes, sec = {}, {}, None
    for line in open(FRGC_SQL, errors="replace"):
        if line.startswith("COPY "):
            sec = line.split()[1]
            continue
        if line.startswith("\\."):
            sec = None
            continue
        f = line.rstrip("\n").split("\t")
        if sec == "rec_frame":
            rec_of[pathlib.Path(f[2]).stem.lower()] = f[0]
        elif sec == "rec_sub_face" and f[7] != "\\N":
            eyes[f[0]] = tuple(float(x) for x in f[7:11])
    return rec_of, eyes


def summ(v):
    v = np.array([x for x in v if x is not None], float)
    if not len(v):
        return None
    return dict(n=int(len(v)), median=float(np.median(v)), p5=float(np.percentile(v, 5)), p95=float(np.percentile(v, 95)),
                enlargement_to_frame=float(CANON_IED / np.median(v)))


def main():
    rows = T1.eval_rows()
    P = RD.pools(rows)
    pool = {r["pid"]: r for r in csv.DictReader(open(K.PN1.parent / "AR1" / "pool.csv"))}
    test_hosts = sorted({r["host"] for r in P["T_R0"]})
    rec_of, eyes = frgc_eyes()
    nat = {"FRGC": dict(ied=[], size=[], fmt={}), "colorFERET": dict(ied=[], size=[], fmt={})}
    missing = []
    for h in test_hosts:
        p = pool[h]
        if p["db"] == "frgc":
            raw = FRGC_ND1 / p["H_raw"]
            if not raw.exists():
                raw = next(FRGC_ND1.glob(p["H_raw"].split("/")[0] + "/**/" + pathlib.Path(p["H_raw"]).name), None)
            e = eyes.get(rec_of.get(pathlib.Path(p["H_raw"]).stem.lower()))
            d = nat["FRGC"]
            d["ied"].append(None if e is None else float(np.hypot(e[0] - e[2], e[1] - e[3])))
            if raw is not None and raw.exists():
                d["size"].append(jpeg_size(raw))
                d["fmt"][magic(raw)] = d["fmt"].get(magic(raw), 0) + 1
            else:
                missing.append(h)
        else:
            stem = pathlib.Path(p["H_raw"]).stem
            subj = stem.split("_")[0]
            gt = next(iter(sorted(FERET.glob(f"dvd*/data/ground_truths/name_value/{subj}/{stem}.txt"))), None)
            d = nat["colorFERET"]
            if gt is None:
                missing.append(h)
                d["ied"].append(None)
                continue
            kv = dict(x.split("=", 1) for x in open(gt).read().splitlines() if "=" in x)
            le, re_ = kv.get("left_eye_coordinates"), kv.get("right_eye_coordinates")
            d["ied"].append(None if not le or not re_ else float(np.hypot(*(np.array(le.split(), float) - np.array(re_.split(), float)))))
            img = gt.parents[4] / kv["relative"]
            if img.exists():
                d["size"].append(ppm_size(img))
                k = "ppm (bzip2)"
                d["fmt"][k] = d["fmt"].get(k, 0) + 1
    out = {"post_hoc": True, "canonical_ied": CANON_IED, "missing_native": missing, "sources": {}}
    for k, d in nat.items():
        sz = {}
        for s in d["size"]:
            sz[f"{s[0]}x{s[1]}" if s else "?"] = sz.get(f"{s[0]}x{s[1]}" if s else "?", 0) + 1
        out["sources"][k] = dict(pool="test ladder R0 hosts", native_ied=summ(d["ied"]), native_sizes=sz, raw_format=d["fmt"])

    def from_manifest(name, man, pick, raw_examples, pool_name=None, note=""):
        rr = [r for r in csv.DictReader(open(man)) if pick(r)]
        sz = {}
        for r in rr:
            s = f"{r['native_w']}x{r['native_h']}"
            sz[s] = sz.get(s, 0) + 1
        fm = {}
        for f in raw_examples:
            fm[magic(f)] = fm.get(magic(f), 0) + 1
        out["sources"][name] = dict(pool=pool_name or name, native_ied=summ([float(r["ied"]) for r in rr if r["ied"]]),
                                    native_sizes=sz, raw_format=fm, raw_format_files_checked=len(raw_examples), note=note)

    cat = {r["id"]: r for r in K.catalog()}
    frll_ids = {r["id"].split("_", 1)[1] for r in P["FRLL_bona_native"]}
    from_manifest("FRLL", MC / "eval.csv", lambda r: r["family"] == "frll_bona" and r["id"] in frll_ids,
                  sorted(FRLL_RAW.glob("*.jpg"))[:300], "FRLL native (= MAD22 genuine), bench rows")
    h1_ids = {r["id"].split("_", 1)[1] for r in P["H1_bona"]}
    from_manifest("H1 (CASIA)", H1M, lambda r: r["family"] == "h1_bona" and r["id"] in h1_ids,
                  [pathlib.Path(cat[r["id"]]["path"]) for r in P["H1_bona"]][:300], "H1 genuine",
                  "the 112x112 files are the native files of this set (CASIA-WebFace history before them not recorded)")
    from_manifest("FFHQ", FFHQM, lambda r: r["family"] == "ffhq_bona", sorted(FFHQ_RAW.glob("Part*/*.png"))[:300],
                  "ffhqm ffhq_bona orig (2,000)", "morph files of the same set: landmark_complete native 256x256")
    out["sources"]["FFHQ"]["morph_landmark_complete_native"] = dict(
        native_ied=summ([float(r["ied"]) for r in csv.DictReader(open(FFHQM)) if r["family"] == "landmark_complete" and r["variant"] == "orig"]))
    from_manifest("FEI", MC / "gtest.csv", lambda r: r["family"].startswith("fei_bona"), sorted(FEI_RAW.rglob("*.jpg"))[:300],
                  "gtest fei_bona (385; manifest metadata only, no score opened)")
    # tier-1 flags per source, every fit (own rule tau_0.5 and tau_cam), split FRGC / colorFERET
    sub = {"FRGC": [r for r in P["T_R0"] if r["host"].startswith("frgc:")],
           "colorFERET": [r for r in P["T_R0"] if r["host"].startswith("feret:")],
           "FRLL": P["FRLL_bona_native"], "H1 (CASIA)": P["H1_bona"]}
    fl = {}
    for arm in ("A", "B", "Bn", "C"):
        for seed in (401, 402):
            name = f"{arm}_s{seed}"
            s, _, _ = T1.load_result(RR / f"PN1_{name}.tar")
            T = RD.thresholds(s, P, 0.0)
            fl[name] = {k: dict(n=len(v), own=float(np.mean(RD.scores_of(s, v) > 0.0)), cam=float(np.mean(RD.scores_of(s, v) > T["cam"])))
                        for k, v in sub.items()}
    out["tier1_flags"] = fl
    out["tier1_flags_note"] = "FFHQ, FEI: not scored by any tier-1 network (FFHQ under amendment 13 only)"
    K.dump(out, K.RES / "tier1" / "native_history.json")
    for k, v in out["sources"].items():
        print(k, v["native_ied"], v["native_sizes"] if len(v["native_sizes"]) < 6 else len(v["native_sizes"]), v["raw_format"])
    print("missing", len(missing))
    for n, v in fl.items():
        print(n, {k: (round(x["own"], 3), round(x["cam"], 3)) for k, x in v.items()})


if __name__ == "__main__":
    if not sys.flags.isolated:
        sys.exit("run with python3 -I")
    main()
