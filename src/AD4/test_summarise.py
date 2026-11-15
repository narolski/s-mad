"""Synthetic tests of the AD4 reader (summarise.py). No real score of any network is opened: every score here is drawn
from a seeded generator on the row structure of ad4_eval.csv. Outputs under /mnt/t7/smad_next/AD4/read/synth_test/.

  python test_summarise.py [--order]     (--order adds the sample-order gate test, about 2 CPU minutes)
"""
import csv
import hashlib
import io
import json
import os
import pathlib
import shutil
import subprocess
import sys
import tarfile

import numpy as np
from scipy.stats import norm

HERE = pathlib.Path(__file__).resolve().parent
W = pathlib.Path("/mnt/t7/smad_next/AD4/test/work/task_AD4_m3mf_s401")
T = pathlib.Path("/mnt/t7/smad_next/AD4/read/synth_test")
ROWS = list(csv.DictReader(open(W / "ad4/data/manifests/ad4_eval.csv")))
EVAL_SHA = "5d3950ab5ccdeed4d376a15126cff660da2a35041579b3513eb7a1059baaa061"
I3_SHA = "0273c11bd0fe4b70fc9c5490859bc185ea50b9ed971a783993b843a399e7b880"
OLD_EVAL_SHA = "86d055d349c63a225893ace30cb3db8b1e9aea4e72350d78152126d7a49d56c9"
PERM = {k: v["sha256"] for k, v in json.load(open(W / "ad4/build_info.json"))["perms"].items()}
fails = []


def check(name, cond, detail=""):
    print(("PASS " if cond else "FAIL ") + name + (f"  ({detail})" if detail else ""))
    if not cond:
        fails.append(name)


# planted morph shifts (in N(0,1) units) per (set, family) for the morph-free arm; references get none
DELTA_MF = {("mordiff", "mordiff"): 8.0, ("dim", "dim_a"): 8.0, ("dim", "dim_c"): 1.7, ("dim", "fast_dim"): 8.0,
            ("dim", "fast_dim_ode"): 8.0, ("dim", "greedy_dim"): 8.0, ("dim", "greedy_dim_s"): 0.0,
            ("frllm", "amsl"): 8.0, ("frllm", "facemorpher"): 8.0, ("frllm", "webmorph"): 8.0,
            ("frllm", "opencv"): 1.5, ("frllm", "stylegan"): 0.5, ("mad22c", "FaceMorpher"): 3.0,
            ("mad22c", "OpenCV"): 1.0, ("mad22c", "Webmorph"): 1.0, ("mad22c", "MIPGAN_I"): 0.0,
            ("mad22c", "MIPGAN_II"): 0.0}


def scores(seed, arm):
    rng = np.random.default_rng([seed, {"mf": 1, "perm": 2, "zero": 3, "twin": 4}[arm]])
    z = rng.standard_normal(len(ROWS))
    for i, r in enumerate(ROWS):
        if r["label"] == "1" and arm in ("mf", "twin"):
            z[i] += DELTA_MF[(r["set"], r["family"])]
    return (1 / (1 + np.exp(-z))).astype(np.float32)


def npz(**kw):
    b = io.BytesIO()
    np.savez(b, **kw)
    return b.getvalue()


def make_tar(d, recipe, arm, seed, steps=6250, limit=0, nan=False, bad_sha=False, comp=None, train_sha=None):
    t = f"AD4_{recipe}{arm}_s{seed}"
    s = scores(seed, arm)
    if nan:
        s[5] = np.nan
    ids = np.array([r["id"] for r in ROWS])
    files = {
        "scores_eval.npz": npz(id=ids, score=s, score_noTTA=s, manifest_sha256=EVAL_SHA),
        "scores_train.npz": npz(manifest_sha256=train_sha or (I3_SHA if arm == "mf" else PERM[str(seed)])),
        "metrics.json": json.dumps({"info": {"limit": limit, "device": "SYNTH", "torch": "x", "train_hours": 0.1},
                                    "cells": {}, "train": {"n": 10, "acc_vs_training_labels": 0.9,
                                                           "acc_vs_true_labels": 0.9 if arm == "mf" else 0.5,
                                                           "auc_vs_training_labels": 0.95, "auc_vs_true_labels": 0.95,
                                                           "frac_labels_permuted": 0.0 if arm == "mf" else 0.5}}).encode(),
        "meta.json": json.dumps({"steps": steps, "seed": seed,
                                 "arch": "a12_clip_vitb16_madation" if recipe == "m3" else "a12_clip_vitl14_madation",
                                 "composition": {"per_batch": comp or [[128, 128, 0]] * 200}}).encode()}
    p = d / f"{t}.tar"
    with tarfile.open(p, "w") as tf:
        for n, b in files.items():
            ti = tarfile.TarInfo(f"{t}/{n}")
            ti.size = len(b)
            tf.addfile(ti, io.BytesIO(b))
    h = hashlib.sha256(p.read_bytes()).hexdigest()
    (d / f"{t}.tar.sha256").write_text(("0" * 64 if bad_sha else h) + f"  {t}.tar\n")


def run(stage, results, recipe, out, extra=()):
    env = dict(os.environ, AD4_TEST_B="400", AD4_TEST_ORDER_DIR=str(T / "order"), CUDA_VISIBLE_DEVICES="")
    cmd = [sys.executable, str(HERE / "summarise.py"), "--stage", stage, "--results", str(results), "--recipe", recipe,
           "--synthetic", "--zero-dir", str(T / "zero"), "--twin-root", str(T / "twin"), "--out-dir", str(out),
           *extra]
    p = subprocess.run(cmd, capture_output=True, text=True, env=env)
    if p.returncode != 0:
        print(p.stdout[-3000:], p.stderr[-3000:])
    return p


def main():
    if T.exists():
        shutil.rmtree(T)          # only this test's own outputs
    for d in ("full", "incomplete", "refuse", "orderres", "zero", "out_full", "out_inc", "out_ref", "out_l", "order",
              "out_order"):
        (T / d).mkdir(parents=True)
    zs = scores(401, "zero")
    np.savez(T / "zero/scores_eval.npz", id=np.array([r["id"] for r in ROWS]), score=zs, manifest_sha256=EVAL_SHA)
    json.dump({"info": {"device": "SYNTH-DGX"}, "train": {"n": 10, "acc_vs_training_labels": 0.3,
               "acc_vs_true_labels": 0.3, "auc_vs_training_labels": 0.2, "auc_vs_true_labels": 0.2,
               "frac_labels_permuted": 0.0}}, open(T / "zero/metrics.json", "w"))
    for s in (1, 2, 3, 4, 5):
        d = T / "twin" / f"a12_clip_vitl14_madation_r224_d0_train90_none_lr3.33e-06_s{s}_r"
        d.mkdir(parents=True)
        keep = [i for i, r in enumerate(ROWS) if r["set"] != "mad22c"]
        tw = scores(s, "twin")
        np.savez(d / "scores_eval_last.npz", id=np.array([ROWS[i]["id"] for i in keep]), score=tw[keep],
                 manifest_sha256=OLD_EVAL_SHA)
    for recipe in ("m3", "m3l"):
        for s in (401, 402, 403, 404, 405):
            make_tar(T / "full", recipe, "mf", s)
            make_tar(T / "full", recipe, "perm", s)
    for s in (401, 402, 403, 404):
        make_tar(T / "incomplete", "m3", "mf", s)
    make_tar(T / "incomplete", "m3", "perm", 401)
    make_tar(T / "refuse", "m3", "mf", 401, steps=6000)
    make_tar(T / "refuse", "m3", "mf", 402, bad_sha=True)
    make_tar(T / "refuse", "m3", "mf", 403, nan=True)
    make_tar(T / "refuse", "m3", "mf", 404, limit=8)
    make_tar(T / "refuse", "m3", "perm", 405, train_sha="f" * 64)
    make_tar(T / "refuse", "m3", "mf", 405)

    # 1. full ViT-B/16 reading
    p = run("read", T / "full", "m3", T / "out_full", ["--no-order"])
    check("full m3 read exits 0", p.returncode == 0)
    R = json.load(open(T / "out_full/ad4_reading_m3.json"))
    G = json.load(open(T / "out_full/ad4_gates_m3.json"))
    check("status final", R["status"] == "final", R["status"])
    c = R["cells"]
    check("MorDIFF passable, A1 not falsified", c["mordiff/mordiff/native"]["passable"] == "yes"
          and c["mordiff/mordiff/native"]["a1"] == "not falsified")
    check("MorDIFF perfect separation CI [0,0]", c["mordiff/mordiff/native"]["mf"]["eer_mean_ci95"] == [0.0, 0.0])
    dc = c["dim/dim_c/native"]
    exp = 100 * norm.cdf(-1.7 / 2)
    check("DiM-C mean EER near the planted 19.8%", abs(dc["mf"]["eer_mean"] - exp) < 3, f"{dc['mf']['eer_mean']:.2f}")
    check("DiM-C named case (beats references, above 15%) and A1 falsified",
          dc["passable"] == "yes" and dc["a1"] == "falsified" and "not at the published level" in dc["note"], dc["note"])
    gs = c["dim/greedy_dim_s/native"]
    check("Greedy-DiM-S (no shift) not passable, falsified", gs["passable"] == "no" and gs["a1"] == "falsified")
    check("MIPGAN-I descriptive, A1 '-'", c["mad22c/MIPGAN_I/native"]["a1"] == "-")
    check("E7 n/a label", c["frllm/stylegan/e7"]["note"].startswith("E7 not applicable"))
    check("E7 partial label", "E7 partial (108/204 identical)" in c["mad22c/OpenCV/e7"]["note"])
    check("landmark wording", "not 'above chance'" in c["frllm/amsl/native"]["note"])
    check("reproduction gate computed on 5 seeds", "cells" in G["reproduction"], G["reproduction"]["status"])
    rp = G["reproduction"]["cells"]
    check("reproduction: OpenCV planted ~22.7% inside 8.8-26", rp["frllm/opencv/native"]["pass"],
          f"{rp['frllm/opencv/native']['mean_eer']:.2f}")
    check("reproduction: Greedy-DiM-S planted 50% misses", not rp["dim/greedy_dim_s/native"]["pass"])
    # interval sanity: point inside CI for every reference network
    rows = list(csv.DictReader(open(T / "out_full/ad4_cells_m3.csv")))
    inside = all(float(r["eer_ci95_lo"]) - 1e-9 <= float(r["eer_pct"]) <= float(r["eer_ci95_hi"]) + 1e-9
                 for r in rows if r["arm"] in ("perm", "zero"))
    check("reference EER points inside their intervals", inside)
    check("every row labelled our frames", all(r["frames"] == "our frames" for r in rows))
    # fixed thresholds, independent recomputation for one network and cell
    s = scores(403, "mf").astype(np.float64)
    ib = [i for i, r in enumerate(ROWS) if r["set"] == "frllm" and r["family"] == "frll_bona"]
    im = [i for i, r in enumerate(ROWS) if r["set"] == "dim" and r["family"] == "dim_c" and r["label"] == "1"]
    ibd = [i for i, r in enumerate(ROWS) if r["set"] == "dim" and r["family"] == "dim_bona"]
    t5 = np.sort(s[ib])[::-1][10]
    r = [x for x in rows if x["network"] == "AD4_m3mf_s403" and x["cell"] == "dim/dim_c/native"][0]
    check("FRLL-5% flag rate on its own pool <= 4.9%",
          float([x for x in rows if x["network"] == "AD4_m3mf_s403" and x["cell"] == "frllm/amsl/native"][0]
                ["flag_frll5"]) <= 10 / 204 + 1e-9)
    check("fixed thresholds recomputed", abs(float(r["flag_frll5"]) - (s[ibd] > t5).mean()) < 1e-4
          and abs(float(r["miss_frll5"]) - (s[im] <= t5).mean()) < 1e-4
          and abs(float(r["flag_0.5"]) - (s[ibd] >= 0.5).mean()) < 1e-4
          and abs(float(r["miss_0.5"]) - (s[im] < 0.5).mean()) < 1e-4)
    md = (T / "out_full/ad4_reading_m3.md").read_text()
    check("tables labelled our frames", md.count("our frames") >= 5)
    check("reproduction flag on top and under every table", "not reproduced on this stack** (reproduction gate, 2 of 11"
          in md and md.count("Flag: not reproduced on this stack") == 5 and "reproduction_flag" in R
          and "per seed" in R["reproduction_flag"])
    check("reproduction flag in every trained row of the csv", all(r["reproduction_gate"] == "not reproduced on this stack"
          for r in rows if r["arm"] in ("mf", "perm")))

    # 2. ViT-L/14 with twin
    p = run("read", T / "full", "m3l", T / "out_l", ["--no-order"])
    check("m3l read exits 0", p.returncode == 0)
    L = json.load(open(T / "out_l/ad4_reading_m3l.json"))
    check("twin present on FRLL cells", "twin" in L["cells"]["frllm/amsl/native"])
    check("no twin on corrected MAD22", "twin" not in L["cells"]["mad22c/FaceMorpher/native"]
          and "no twin" in L["cells"]["mad22c/FaceMorpher/native"]["note"])
    check("m3l falsified wording with twin", "the morph-trained recipe reaches" in
          L["cells"]["dim/greedy_dim_s/native"]["note"], L["cells"]["dim/greedy_dim_s/native"]["note"])
    check("twin file hashes printed", len(L["twin_files_sha256"]) == 5)
    check("no reproduction gate for m3l", json.load(open(T / "out_l/ad4_gates_m3l.json"))["reproduction"]["status"]
          == "not registered for this recipe")

    # 3. incomplete arm
    p = run("read", T / "incomplete", "m3", T / "out_inc", ["--no-order"])
    check("incomplete read exits 0", p.returncode == 0)
    I = json.load(open(T / "out_inc/ad4_reading_m3.json"))
    check("incomplete status", I["status"].startswith("incomplete (4 of 5"), I["status"])
    check("incomplete rows carry no verdict", I["cells"]["mordiff/mordiff/native"]["passable"] == "incomplete (4 of 5)")
    check("reproduction gate incomplete", json.load(open(T / "out_inc/ad4_gates_m3.json"))["reproduction"]["status"]
          == "incomplete (4 of 5)")

    # 4. refusals
    p = run("gates", T / "refuse", "m3", T / "out_ref", ["--no-order"])
    check("refusal run exits 0", p.returncode == 0)
    F = json.load(open(T / "out_ref/ad4_gates_m3.json"))["refused"]
    check("steps refused", "steps 6000" in F.get("AD4_m3mf_s401", ""))
    check("tar sha refused", "sha256 mismatch" in F.get("AD4_m3mf_s402", ""))
    check("non-finite refused", "non-finite" in F.get("AD4_m3mf_s403", ""))
    check("limit refused", "limit 8" in F.get("AD4_m3mf_s404", ""))
    check("training manifest refused", "training manifest" in F.get("AD4_m3perm_s405", ""))
    check("good tar accepted", "AD4_m3mf_s405" not in F)

    # 5. sample-order gate (optional; builds the CLIP model twice on CPU)
    if "--order" in sys.argv:
        env = dict(os.environ, CUDA_VISIBLE_DEVICES="")
        q = subprocess.run([sys.executable, str(HERE / "gates.py"), "order", "--arch", "a12_clip_vitb16_madation",
                            "--seed", "401", "--manifest", "train_i3.csv", "--out", str(T / "pred401.json")],
                           capture_output=True, text=True, env=env)
        pred = json.load(open(T / "pred401.json"))["per_batch"]
        check("seed-401 prediction first3", pred[:3] == [[139, 117, 0], [125, 131, 0], [124, 132, 0]], str(pred[:3]))
        make_tar(T / "orderres", "m3", "mf", 401, comp=pred)
        make_tar(T / "orderres", "m3", "mf", 402, comp=pred)       # seed 402 given seed 401's order: must miss
        p = run("gates", T / "orderres", "m3", T / "out_order")
        check("order run exits 0", p.returncode == 0)
        O = json.load(open(T / "out_order/ad4_gates_m3.json"))["order"]
        check("order gate pass for the matching record", O["AD4_m3mf_s401"]["pass"])
        check("order gate MISS for the wrong record", not O["AD4_m3mf_s402"]["pass"], str(O["AD4_m3mf_s402"]))
    print(f"\n{len(fails)} failures" + (f": {fails}" if fails else ""))
    sys.exit(1 if fails else 0)


if __name__ == "__main__":
    main()
