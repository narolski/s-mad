"""AF0 wave 4: softened examples through the EXISTING registered shrink-and-enlarge path (author's approval, 11 Nov).

Path, imported unchanged from smadcvpr/prep_eval.py (sha256 374408ab..., never edited):
  the E7 'resmatch' branch of prep_eval.main: native_ied = |k1 - k0| from prep_eval.kps(img); if native_ied > med_ied:
  img_deg = prep_eval.degrade(img, "R", scale=med_ied / native_ied) (cv2.INTER_AREA shrink), else a copy; then
  prep_eval.align(img_deg) (insightface buffalo_l detection + 2-eye similarity warp back to the canonical 512 frame,
  i.e. the enlarge step). The branch's 6 lines are reproduced verbatim below (they are inline in prep_eval.main).
Registered strengths used (family median native inter-eye distances of registered E7 cells):
  amsl112  : FRLL-Morphs AMSL, 112.71795654296875 px (eval.csv, orig morph rows, median of 'ied')
  fm61     : corrected MAD22 FaceMorpher, 61.21146774291992 px (canonical E7 inputs v3, family_native_ied_targets.json)
Verification before use (verify): (a) degrade(SMDD render, "R", 0.3125) against the stored A47 I-3 copies (8 images,
bit for bit); (b) the full branch on 8 FRLL raw photos against their registered eval frames *_resmatch_<family>.png.
  python3 -I soften.py verify
  python3 -I soften.py build --list soft_src --strengths amsl112,fm61 --workers 1
"""
import argparse
import csv
import hashlib
import json
import pathlib
import sys

import numpy as np

MC = pathlib.Path("/home/narolski/mambamorph-code")
PE = MC / "smadcvpr" / "prep_eval.py"
PE_SHA = "374408ab3a886e6df25b563bc2344d190efe2ab7b3163efbb17c9b6ca9100628"
OUT = pathlib.Path("/mnt/t7/smad_next/AF0")
RES = pathlib.Path("/home/narolski/smad-next/experiments/AF0")
STRENGTHS = {"amsl112": 112.71795654296875, "fm61": 61.21146774291992}


def sha(p):
    return hashlib.sha256(open(p, "rb").read()).hexdigest()


def load_pe():
    assert sha(PE) == PE_SHA, "prep_eval.py is not at its registered pin"
    import importlib.util
    sys.path.insert(0, str(MC / "smadcvpr"))
    spec = importlib.util.spec_from_file_location("prep_eval", PE)
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


def e7_branch(P, img_native, med_ied):
    """verbatim logic of prep_eval.main's resmatch branch (native IED from P.kps, as get_native_info does)."""
    k = P.kps(img_native)
    native_ied = float(np.linalg.norm(k[1] - k[0])) if k is not None else 0.0
    if native_ied <= 0:
        return None, False, native_ied, None
    if native_ied > med_ied:
        scale = med_ied / native_ied
        img_deg = P.degrade(img_native, "R", scale=scale)
    else:
        scale = 1.0
        img_deg = img_native.copy()
    aligned_r, aligned_flag_r, iod_aligned_r = P.align(img_deg)
    return aligned_r, bool(aligned_flag_r), native_ied, scale


def verify(a):
    import cv2
    P = load_pe()
    res = dict(prep_eval_sha256=PE_SHA, smdd=[], frll=[])
    D = MC / "smadcvpr_data"
    rows = [r for r in csv.DictReader(open("/mnt/t7/smad_heldout/a47/data47/i3/manifests/train.csv")) if r["label"] == "1"][:8]
    for r in rows:
        nat = D / r["path"].replace("smdd_a47e7", "smdd")
        cp = pathlib.Path("/mnt/t7/smad_heldout/a47/data47/i3") / r["path"]
        out = P.degrade(cv2.imread(str(nat)), "R", scale=0.3125)
        ref = cv2.imread(str(cp))
        res["smdd"].append(dict(native=str(nat), copy=str(cp), shape=list(out.shape),
                                max_abs=int(np.abs(out.astype(int) - ref.astype(int)).max()) if out.shape == ref.shape else None))
    ev = [r for r in csv.DictReader(open(D / "manifests/eval.csv")) if r["set"] == "frllm" and r["variant"] == "resmatch"
          and r["family"] in ("amsl", "opencv")]
    med = {"amsl": 112.71795654296875, "opencv": 129.72315979003906}
    raw = pathlib.Path("/home/narolski/mambamorph/Datasety/downloads/frll_base/extracted")
    for r in ev[:4] + [x for x in ev if x["family"] == "amsl"][:4]:
        base = pathlib.Path(r["path"]).name.split("_resmatch_")[0]
        src = (raw / ("neutral_front" if base.endswith("_03") else "smiling_front") / f"{base}.jpg")
        out, flag, nied, sc = e7_branch(P, cv2.imread(str(src)), med[r["family"]])
        ref = cv2.imread(str(D / r["path"]))
        res["frll"].append(dict(src=str(src), ref=r["path"], family=r["family"], native_ied=nied, registered_ied=float(r["ied"]),
                                scale=sc, aligned=flag, max_abs=int(np.abs(out.astype(int) - ref.astype(int)).max()),
                                n_diff_px=int((out != ref).any(2).sum())))
    json.dump(res, open(RES / "wave4_verify.json", "w"), indent=1)
    print(json.dumps(res, indent=1))


def _job(args):
    import cv2
    r, strength = args
    out = OUT / "img" / "soft" / strength / f"{r['id']}_{strength}.png"
    if out.exists():
        return r["id"], strength, str(out), None, None, None
    P = _job.P
    img, flag, nied, sc = e7_branch(P, cv2.imread(r["path"]), STRENGTHS[strength])
    if img is None:
        return r["id"], strength, "", False, nied, sc
    out.parent.mkdir(parents=True, exist_ok=True)
    assert cv2.imwrite(str(out), img)
    return r["id"], strength, str(out), flag, nied, sc


def build(a):
    P = load_pe()
    _job.P = P
    rows = list(csv.DictReader(open(OUT / "lists" / f"{a.list}.csv")))
    st = a.strengths.split(",")
    jobs = [(r, st[k % len(st)]) for k, r in enumerate(rows)] if a.alternate else [(r, s) for s in st for r in rows]
    log = []
    for k, j in enumerate(jobs):
        log.append(_job(j))
        if (k + 1) % 500 == 0:
            print(k + 1, len(jobs), flush=True)
    with open(OUT / f"soft_{a.list}.csv", "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["src_id", "strength", "path", "aligned", "native_ied", "scale"])
        w.writerows(log)
    print("done", len(log), "failed", sum(1 for x in log if not x[2]))


if __name__ == "__main__":
    if not sys.flags.isolated:
        sys.exit("run with python3 -I")
    ap = argparse.ArgumentParser()
    ap.add_argument("cmd", choices=("verify", "build"))
    ap.add_argument("--list", default="soft_src")
    ap.add_argument("--strengths", default="amsl112,fm61")
    ap.add_argument("--workers", type=int, default=1)
    ap.add_argument("--alternate", action="store_true", help="one strength per image, alternating by row")
    a = ap.parse_args()
    verify(a) if a.cmd == "verify" else build(a)
