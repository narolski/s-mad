"""PN1 amendment 1: JPEG copies for manifest C through the registered function prep_eval.degrade (jpeg90 / jpeg70 only),
imported unchanged via the alpha-field probe's pinned loader (src/AF0/soften.py load_pe: sha256 pin of prep_eval.py
374408ab...). Never blur1, resample50 or chip.
  python3 -I jpeg_c.py verify            # raw FRLL photo -> degrade(jpeg70) -> align -> PNG == existing eval file?
  python3 -I jpeg_c.py build --sel /mnt/t7/smad_next/PN1/lists/jpeg_sel.csv [--limit 8]
       copies: degrade(frame, op) on the training frame itself, lossless PNG, no re-alignment ->
       /mnt/t7/smad_next/PN1/img/jpeg/<op>/<id>_<op>.png ; log /mnt/t7/smad_next/PN1/jpeg_build<_limitN>.csv
"""
import argparse
import csv
import hashlib
import importlib.util
import json
import pathlib
import sys

import numpy as np

AF0SOFT = pathlib.Path("/home/narolski/smad-next/src/AF0/soften.py")
AF0SOFT_SHA = "49fa41513fe7d94959361ed4b06579917d341d29d692562cdc21bdde2b0d6e17"
OUT = pathlib.Path("/mnt/t7/smad_next/PN1")
RES = pathlib.Path("/home/narolski/smad-next/experiments/PN1_protocol-network-first-tests")
MC = pathlib.Path("/home/narolski/mambamorph-code")
ALLOWED = ("jpeg90", "jpeg70")


def sha(p):
    return hashlib.sha256(open(p, "rb").read()).hexdigest()


def load_pe():
    assert sha(AF0SOFT) == AF0SOFT_SHA, "AF0 soften.py changed"
    spec = importlib.util.spec_from_file_location("af0_soften", AF0SOFT)
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m.load_pe()


def verify(a):
    import cv2
    P = load_pe()
    D = MC / "smadcvpr_data"
    raw = pathlib.Path("/home/narolski/mambamorph/Datasety/downloads/frll_base/extracted")
    ev = [r for r in csv.DictReader(open(D / "manifests/eval.csv")) if r["set"] == "frllm" and r["family"] == "frll_bona"
          and r["variant"] == "jpeg70"][:4]
    res = dict(prep_eval_sha256=sha(MC / "smadcvpr/prep_eval.py"), files=[])
    tmp = OUT / "jpeg_verify"
    tmp.mkdir(parents=True, exist_ok=True)
    for r in ev:
        base = pathlib.Path(r["path"]).name.split("_jpeg70")[0]
        src = raw / ("neutral_front" if base.endswith("_03") else "smiling_front") / f"{base}.jpg"
        img = cv2.imread(str(src))
        deg = P.degrade(img, "jpeg70", ied=float(r["ied"]))
        al, flag, _ = P.align(deg)
        f = tmp / f"{base}_jpeg70.png"
        cv2.imwrite(str(f), al)
        ref = D / r["path"]
        refi = cv2.imread(str(ref))
        res["files"].append(dict(src=str(src), ref=str(ref), aligned=bool(flag),
                                 max_abs_pixel=int(np.abs(al.astype(int) - refi.astype(int)).max()),
                                 bytes_equal=sha(f) == sha(ref), sha_ours=sha(f), sha_ref=sha(ref)))
    res["pass_pixels"] = all(x["max_abs_pixel"] == 0 for x in res["files"])
    res["pass_bytes"] = all(x["bytes_equal"] for x in res["files"])
    json.dump(res, open(RES / "jpeg_verify.json", "w"), indent=1)
    print(json.dumps(res, indent=1))


def build(a):
    import cv2
    P = load_pe()
    rows = list(csv.DictReader(open(a.sel)))[: a.limit or None]
    log = []
    for k, r in enumerate(rows):
        op = r["op"]
        assert op in ALLOWED, op
        out = OUT / "img" / "jpeg" / op / f"{r['id']}_{op}.png"
        if not out.exists():
            img = cv2.imread(r["path"])
            assert img is not None and img.shape == (512, 512, 3), r["path"]
            out.parent.mkdir(parents=True, exist_ok=True)
            assert cv2.imwrite(str(out), P.degrade(img, op))
        log.append((r["id"], op, r["path"], str(out)))
        if (k + 1) % 500 == 0:
            print(k + 1, len(rows), flush=True)
    tag = f"_limit{a.limit}" if a.limit else ""
    with open(OUT / f"jpeg_build{tag}.csv", "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["src_id", "op", "src_path", "path"])
        w.writerows(log)
    print("done", len(log), flush=True)


if __name__ == "__main__":
    if not sys.flags.isolated:
        sys.exit("run with python3 -I")
    ap = argparse.ArgumentParser()
    ap.add_argument("cmd", choices=("verify", "build"))
    ap.add_argument("--sel", default=str(OUT / "lists" / "jpeg_sel.csv"))
    ap.add_argument("--limit", type=int, default=0)
    a = ap.parse_args()
    verify(a) if a.cmd == "verify" else build(a)
