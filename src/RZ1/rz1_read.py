"""Input resolution and resize method (RZ1): the registered reader (prereg.md sections 4, 5, 12 and amendment 1).
Development data only. One read per wave:
  python3 -I rz1_read.py --wave 1    --out experiments/RZ1_.../rz1_read_w1.json     (A0 Sb0 AN AM SbM AMR SbMR + RZ1R yardstick)
  python3 -I rz1_read.py --wave crop --out .../rz1_read_crop.json                    (Ac Sbc against A0 Sb0)
  python3 -I rz1_read.py --wave 512  --out .../rz1_read_512.json                     (A512 Sb512 SbMR512 against A0 Sb0)
  python3 -I rz1_read.py --wave 1 --mock [--mock-drop AM_s409,...] --out MOCK.json    (random scores; code path only)
Reuses unchanged: src/AB1/ab1_read.py (pools, verdict counting), src/PN1/c2p_read.py (holdout, net_stats, fauc; pinned),
src/TT1/tt1_read.py (load_pools, boot_weights; TT1's draws, default_rng(20261122)), src/TT1/meds/tt1_read_meds.py's
person bootstrap (default_rng(20261125), its first draw = MEDS persons)."""
import argparse
import csv
import hashlib
import importlib.util
import io
import json
import math
import pathlib
import re
import sys
import tarfile

import numpy as np

HERE = pathlib.Path(__file__).resolve().parent
SRC = HERE.parent


def _mod(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


A = _mod("ab1_read", SRC / "AB1" / "ab1_read.py")
C2 = A.C2
sys.path.insert(0, str(SRC / "TT1"))
import tt1common as T  # noqa: E402
import tt1_read as TR  # noqa: E402
MR = _mod("tt1_read_meds", SRC / "TT1" / "meds" / "tt1_read_meds.py")

X_EVAL = pathlib.Path("/mnt/t7/smad_next/AB1/x/manifests/ab1x_eval.csv")
X_EVAL_SHA = "5257fb63f321612c39f8da6613989976450a68cd97c0b55d51667b554995d35f"
CROSS = pathlib.Path("/mnt/t7/smad_next/RZ1/overlay_tree/rz1/manifests/rz1_cross.csv")
CROSS_SHA = "2f41e6d4c99eb31ff3916c537b4fa631acbbf7a4532748d08143e31ca1bafcef"
TT1_SHA = "c0055b51467cf8d001d56cbc4689706d68f0bf35c64066b1ba49fada5cb45761"       # tt1_score.csv (TT1 reader pin)
FSMAN = pathlib.Path("/mnt/t7/smad_next/PN1/fs_tree/pn1/data/manifests")
PINS = dict(pack="96c31ae29c4118947e3fd0a7a97600805cbfa5a82369c8ecbc6ee3d6349f2004",
            ab1_overlay="171fdb213444442762d4a716b7470dd885cd5879ba9ddda0c542060af4b4d149",
            ab1x_overlay="e5886e72622b618cb260689820efea861b63b061749db561d256ad57116f819c",
            tt1="2109f742b0378c188f394a3b26c363ef2ffb0ea43eab78ecea7674884022c554",
            meds="3fb917b226c6d31fab176a4d8fdd5d6e6b22b8274cc091591f444e623a87ab61",
            rz1_overlay="dccf37d20ca0074780a15d99012c3302f52e4ad5a7773b66981b5d316276d383")
SEEDS = (408, 409, 410, 411, 412)
TRAIN9 = ["fixed:pil_bilinear", "fixed:pil_nearest", "fixed:pil_bicubic", "fixed:pil_lanczos", "fixed:pil_box",
          "fixed:cv_area", "fixed:cv_linear", "fixed:cv_cubic", "fixed:cv_lanczos4"]
HELD4 = ["fixed:pil_hamming", "fixed:cv_nearest", "fixed:cv_linear_exact", "two:300:pil_hamming:cv_linear_exact"]
K13 = TRAIN9 + HELD4
# arm: (manifest, training spec, primary spec, res, bs, accum, cross specs)
ARM = dict(
    A0=("train_A.csv", "fixed:pil_bilinear", "fixed:pil_bilinear", 224, 256, 1, K13),
    Sb0=("train_Sb.csv", "fixed:pil_bilinear", "fixed:pil_bilinear", 224, 256, 1, K13),
    AN=("train_A.csv", "fixed:pil_nearest", "fixed:pil_nearest", 224, 256, 1, K13),
    AM=("train_A.csv", "mix", "fixed:pil_bilinear", 224, 256, 1, K13),
    SbM=("train_Sb.csv", "mix", "fixed:pil_bilinear", 224, 256, 1, K13),
    AMR=("train_A.csv", "mixR", "fixed:pil_bilinear", 224, 256, 1, K13),
    SbMR=("train_Sb.csv", "mixR", "fixed:pil_bilinear", 224, 256, 1, K13),
    Ac=("train_A.csv", "crop:144:160", "crop:144:160", 224, 256, 1, []),
    Sbc=("train_Sb.csv", "crop:144:160", "crop:144:160", 224, 256, 1, []),
    A512=("train_A.csv", "fixed:pil_bilinear", "fixed:pil_bilinear", 512, 64, 4, []),
    Sb512=("train_Sb.csv", "fixed:pil_bilinear", "fixed:pil_bilinear", 512, 64, 4, []),
    SbMR512=("train_Sb.csv", "mixR", "fixed:pil_bilinear", 512, 64, 4, []),
)
WAVE = {"1": ["A0", "Sb0", "AN", "AM", "SbM", "AMR", "SbMR"], "crop": ["A0", "Sb0", "Ac", "Sbc"],
        "512": ["A0", "Sb0", "A512", "Sb512", "SbMR512"]}
RZ1R_PIN = {"A": {408: "bb1a0e9c", 409: "d9a8c1b8", 410: "78ef2e47", 411: "fd71be56", 412: "c0496a0f"},
            "Sb": {408: "a84b551f", 409: "dd575673", 410: "40b47155", 411: "764a4e5e", 412: "c1e0f081"}}
FLOOR_BIND = 0.886            # printed check: the frame-level best single statistic (AB1); recomputed below from a14


def sha(p):
    return hashlib.sha256(pathlib.Path(p).read_bytes()).hexdigest()


def k_of(n, k):
    return (n == 5 and k >= 4) or (n == 4 and k == 4)


def rule(sup, fal, n):
    """sup, fal: counts of seeds meeting the supporting / falsifying condition among n read seeds (AB1 counting)."""
    if n <= 3:
        return "not read (too few seeds)"
    if k_of(n, sup):
        return "supported"
    if k_of(n, fal):
        return "falsified"
    return "inconclusive, no claim"


def npz(t, name):
    return np.load(io.BytesIO(t.extractfile(name).read()))


def load_rz1(tar, arm):
    """(data, why): data = dict(x, tr, tt1, meds, cross) if the tar verifies with the registered provenance."""
    shf = tar.parent / (tar.name + ".sha256")
    if not tar.exists() or not shf.exists():
        return None, "missing"
    if sha(tar) != shf.read_text().split()[0]:
        return None, "sha256 mismatch"
    man, spec, prim, res, bs, acc, cross = ARM[arm]
    T_ = tar.name[:-4]
    try:
        with tarfile.open(tar) as t:
            f = lambda n: t.extractfile(f"{T_}/{n}").read().decode(errors="replace")
            gpu, ti, log, env, guard = f("gpu.txt"), f("task_info.txt"), f("train.log"), f("task.env"), f("guard.log")
            meta = json.loads(f("meta.json")); tj = json.loads(f("rz1_transform.json"))
            z, zt, zt1, zm, zc = (npz(t, f"{T_}/{n}") for n in ("scores_eval.npz", "scores_train.npz", "scores_tt1.npz",
                                                                    "scores_meds.npz", "scores_cross.npz"))
    except KeyError as e:
        return None, f"member missing: {e}"
    if "H100" not in gpu:
        return None, f"not an H100: {gpu.strip()}"
    want = [f"pack_sha256 {PINS['pack']}", f"ab1_overlay {PINS['ab1_overlay']}", f"ab1x_overlay {PINS['ab1x_overlay']}",
            f"tt1 {PINS['tt1']}", f"meds {PINS['meds']}", f"rz1_overlay {PINS['rz1_overlay']}", f"spec {spec} ",
            f"primary {prim} ", f"res {res} bs {bs} accum {acc} ", "steps 6250 limit 0 skip_tt1 0"]
    miss = [w for w in want if w not in ti + " "]
    if miss:
        return None, f"task_info off: {miss}"
    if f"ARM={arm}\n" not in env + "\n":
        return None, "task.env arm off"
    if "RZ1 GUARD pre ok" not in guard or "RZ1 GUARD post ok" not in guard:
        return None, "guard lines missing"
    if tj.get("spec") != spec or int(tj.get("res", -1)) != res:
        return None, f"rz1_transform off: {tj}"
    if int(meta.get("steps", -1)) != 6250 or int(meta.get("res", -1)) != res or int(meta.get("bs", -1)) != bs \
            or int(meta.get("accum", 1)) != acc or int(meta.get("n_items", -1)) != len(list(csv.DictReader(open(FSMAN / man)))):
        return None, "meta off"
    losses = [float(v) for v in re.findall(r"loss[ =:]+(-?(?:inf|nan)|[-+0-9.eE]+)", log, flags=re.I)]
    if not losses or not all(math.isfinite(v) for v in losses):
        return None, "no finite loss in train.log"
    if str(z["manifest_sha256"]) != X_EVAL_SHA or str(z["spec"]) != prim:
        return None, "eval manifest or spec off"
    if str(zt["manifest_sha256"]) != sha(FSMAN / man):
        return None, "train manifest off"
    if str(zt1["manifest_sha256"]) != TT1_SHA:
        return None, "tt1 manifest off"
    if list(map(str, zc["specs"])) != cross or (cross and str(zc["manifest_sha256"]) != CROSS_SHA):
        return None, "cross table off"
    return _pack(z, zt, zt1, zm, zc), "read"


def _pack(z, zt, zt1, zm, zc):
    d = dict(x=dict(zip(map(str, z["id"]), z["logit"].astype(float))),
             tt1=dict(zip(map(str, zt1["id"]), zt1["logit"].astype(float))),
             meds=dict(zip(map(str, zm["id"]), zm["logit"].astype(float))), tr={}, cross={})
    for k, v in zip(map(str, zt["kind"]), zt["logit"].astype(float)):
        d["tr"].setdefault(k, []).append(v)
    ids = list(map(str, zc["id"]))
    for j, s in enumerate(map(str, zc["specs"])):
        d["cross"][s] = dict(zip(ids, zc["logit"][j].astype(float)))
    return d


def load_rz1r(tar, arm, s):
    shf = tar.parent / (tar.name + ".sha256")
    if not tar.exists() or not shf.exists():
        return None, "missing"
    if sha(tar) != shf.read_text().split()[0]:
        return None, "sha256 mismatch"
    T_ = tar.name[:-4]
    try:
        with tarfile.open(tar) as t:
            f = lambda n: t.extractfile(f"{T_}/{n}").read().decode(errors="replace")
            gpu, ti, gate = f("gpu.txt"), f("task_info.txt"), json.loads(f("gate.json"))
            z, zt, zt1, zm, zc = (npz(t, f"{T_}/{n}") for n in ("scores_eval.npz", "scores_train.npz", "scores_tt1.npz",
                                                                    "scores_meds.npz", "scores_cross.npz"))
    except KeyError as e:
        return None, f"member missing: {e}"
    if "H100" not in gpu or f"source_tar AB1_{arm}_s{s}.tar {RZ1R_PIN[arm][s]}" not in ti or "limit 0" not in ti:
        return None, f"provenance off: {ti.strip()}"
    if gate.get("verdict") != "passed" or gate.get("n") != 21277:
        return None, f"gate {gate.get('verdict')} (differ {gate.get('n_differ')}, max {gate.get('max_abs')})"
    if str(z["manifest_sha256"]) != X_EVAL_SHA or list(map(str, zc["specs"])) != K13:
        return None, "manifests off"
    return _pack(z, zt, zt1, zm, zc), "read (gate passed)"


def mock_net(arm, s, M, TT, MD, CR, drop):
    if f"{arm}_s{s}" in drop:
        return None, "mock: dropped"
    r = np.random.default_rng(s * 1000 + sum(map(ord, arm)))
    plain = arm.startswith("A")
    shift = (1.0 if arm in ("A0", "AN", "A512", "RZ1R_A") else 0.4 if plain else 0.05)
    x = {m["id"]: float(r.normal((1.0 if m["label"] == "1" else -2.0) +
                                 (shift if m["fam"] == "ms1ffhq" and m["strength"] in C2.SIZES and m["label"] == "0" else 0), 1.5))
         for m in M}
    tt1 = {i: float(r.normal(-2.5, 1.2)) for i in TT}
    meds = {i: float(r.normal(-3.0, 1.0)) for i in MD}
    cross = {}
    for j, sp in enumerate(ARM.get(arm, (0, 0, 0, 0, 0, 0, K13))[6] if not arm.startswith("RZ1R") else K13):
        base = {**{f"ab1x:{k}": v for k, v in x.items()}, **{f"tt1:{k}": v for k, v in tt1.items()}}
        dk = (0.3 * j / 13 if "M" not in arm else 0.02) * (1 if plain else 0.5)
        cross[sp] = {i: base[i] + dk for i in CR}
    return dict(x=x, tt1=tt1, meds=meds, tr={}, cross=cross), "mock"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--wave", required=True, choices=("1", "crop", "512"))
    ap.add_argument("--res", default="/mnt/t7/smad_next/RZ1/results")
    ap.add_argument("--resr", default="/mnt/t7/smad_next/RZ1/results_r")
    ap.add_argument("--out", required=True)
    ap.add_argument("--mock", action="store_true")
    ap.add_argument("--mock-drop", default="")
    a = ap.parse_args()
    drop = {x for x in a.mock_drop.split(",") if x}
    assert sha(SRC / "PN1" / "c2p_read.py") == A.C2P_SHA, "c2p_read.py not at its pin"
    assert sha(X_EVAL) == X_EVAL_SHA and sha(CROSS) == CROSS_SHA and sha(T.OUT / "tt1_score.csv") == TT1_SHA
    assert sha(A.FLOOR) == A.FLOOR_SHA_FILE.read_text().split()[0]
    M = list(csv.DictReader(open(X_EVAL)))
    Mnb = [r for r in M if r["fam"] != "border"]
    P = A.pools(Mnb)
    P["R3"] = [r["id"] for r in Mnb if r["fam"] == "ladder" and r["role"] == "dev" and r["rung"] == "R3" and r["strength"] == ""]
    P["R3m"] = [r["id"] for r in Mnb if r["fam"] == "ladder" and r["role"] == "dev" and r["rung"] == "R3m" and r["strength"] == ""]
    natp, natm, pairs, mpairs = C2.holdout(M)
    rng = np.random.default_rng(C2.RNG_G)
    boot = {z: [rng.integers(0, len(pairs[z]), len(pairs[z])) for _ in range(C2.B_BOOT)] for z in C2.SIZES}
    # landmark_combined floor (binding, frame level) and its draws, exactly as AB1
    zf = np.load(A.FLOOR)
    cid = {str(i): c for i, c in zip(zf["ids"], zf["cues"])}
    CM = np.array([cid[i] for i in P["lc_m"]]); CG = np.array([cid[i] for i in P["lc_g"]])
    rng2 = np.random.default_rng(20261118)
    draws = [(rng2.integers(0, len(CM), len(CM)), rng2.integers(0, len(CG), len(CG))) for _ in range(2000)]

    def fmax(im, ig):
        return max(max(u, 1 - u) for u in (C2.fauc(CM[im, j], CG[ig, j]) for j in range(CM.shape[1])))
    fdraw = np.array([fmax(im, ig) for im, ig in draws])
    floor_pt = fmax(np.arange(len(CM)), np.arange(len(CG)))
    assert abs(floor_pt - FLOOR_BIND) < 0.0005, floor_pt
    # input-matched floors (printed only; pinned files, if present)
    fl_in = {}
    for tag in ("pil_bilinear", "pil_nearest", "crop"):
        p = pathlib.Path(f"/mnt/t7/smad_next/RZ1/floors/floor_{tag}.npz")
        if p.exists():
            zz = np.load(p); c2 = {str(i): c for i, c in zip(zz["ids"], zz["cues"])}
            Cm = np.array([c2[i] for i in P["lc_m"]]); Cg = np.array([c2[i] for i in P["lc_g"]])
            fl_in[tag] = dict(sha256=sha(p), best=float(max(max(u, 1 - u) for u in (C2.fauc(Cm[:, j], Cg[:, j]) for j in range(Cm.shape[1])))))
    # TT1 pools and draws; MEDS persons
    TP, _tt = TR.load_pools()
    TW = TR.boot_weights(TP, np.random.default_rng(TR.SEED))
    meds = list(csv.DictReader(open(MR.MEDS)))
    prim = [r for r in meds if r["aligned"] == "1"]
    Wm = MR.boot_w([r["person"] for r in prim], np.random.default_rng(20261125))
    fam_src = {f: ([f] if f != "lfw_calfw" else ["lfw", "calfw"]) for f in T.FAMILIES}
    CR = [r["id"] for r in csv.DictReader(open(CROSS))]
    crow = {r["id"]: r for r in csv.DictReader(open(CROSS))}
    gen_ids = [f"ab1x:{i}" for i in P["camera"] + natp] + [i for i, r in crow.items() if r["src"] == "tt1" and
                                                          (r["rung"] == "R_cam" or (r["role"] == "tt1" and r["rung"] in T.SOURCES))]
    mor_ids = [f"ab1x:{i}" for i in P["lc_m"]]
    gen_ids = [i for i in gen_ids if i in crow]
    TT_ids = [i for v in TP.values() for i, _ in v]
    MD_ids = [r["id"] for r in meds]

    def stats(d, prim_spec):
        x, L = d["x"], d["tt1"]
        need = set(natp) | set(natm) | {f"{i}_{z}" for z in C2.SIZES for i in pairs[z]} | \
            {f"{i}_{z}" for z in C2.SIZES for i in mpairs[z]} | {i for k in ("lc_m", "lc_g", "S3", "S0", "S4", "camera", "soft") for i in P[k]}
        if not need <= set(x) or not all(math.isfinite(x[i]) for i in need) or not set(TT_ids) <= set(L):
            return None
        m = np.array([x[i] for i in P["lc_m"]]); g = np.array([x[i] for i in P["lc_g"]])
        sd = np.array([C2.fauc(m[im], g[ig]) for im, ig in draws])
        st = dict(lcomb_auc=C2.fauc(m, g), lcomb_ci=[float(np.percentile(sd, 2.5)), float(np.percentile(sd, 97.5))],
                  lcomb_minus_floor_lo=float(np.percentile(sd - fdraw, 2.5)),
                  S3=A.share(x, P["S3"]), S0=A.share(x, P["S0"]), S4=A.share(x, P["S4"]),
                  S3_vs_S4_auc=C2.fauc([x[i] for i in P["S4"]], [x[i] for i in P["S3"]]),
                  R3=A.share(x, P["R3"]) if P["R3"] else None, R3m=A.share(x, P["R3m"]) if P["R3m"] else None,
                  warp=A.share(x, P["warp"]), camera=A.share(x, P["camera"]), soft=A.share(x, P["soft"]))
        st["dsoft"] = st["soft"] - st["camera"]
        st["c2p"] = C2.net_stats(x, natp, natm, pairs, mpairs, boot)
        st["_c2p_rep"] = {z: [(np.array([x[f"{i}_{z}"] for i in pairs[z]])[w] > 0).mean() -
                              (np.array([x[i] for i in pairs[z]])[w] > 0).mean() for w in boot[z]] for z in C2.SIZES}
        # unseen sources (TT1 pools and draws)
        fam_pt, fam_draw = {}, {}
        for f in T.FAMILIES:
            xs = np.concatenate([np.array([L[i] for i, _ in TP[f"U:{s}"]]) > 0 for s in fam_src[f]]).astype(float)
            w = np.concatenate([TW[f"U:{s}"] for s in fam_src[f]], axis=1)
            fam_pt[f], fam_draw[f] = float(xs.mean()), (w @ xs) / w.sum(1)
        st["fam_flag"] = fam_pt
        st["Fbar"] = float(np.mean(list(fam_pt.values())))
        st["_Fbar_draw"] = np.mean(np.stack(list(fam_draw.values())), 0)
        st["Fbar_cut-1"] = float(np.mean([np.mean(np.concatenate([np.array([L[i] for i, _ in TP[f"U:{s}"]]) for s in fam_src[f]]) > -1)
                                          for f in T.FAMILIES]))
        cam = np.array([L[i] for i, _ in TP["R_cam"]]) > 0
        bd_draw = []
        rcb = {f: np.array([L[i] for i, _ in TP[f"Rcb:{f}"]]) > 0 for f in T.FAMILIES if f"Rcb:{f}" in TP}
        st["Rcam_flag"] = float(cam.mean())
        st["Rcb_flag"] = {f: float(v.mean()) for f, v in rcb.items()}
        st["Bd"] = float(np.mean(list(st["Rcb_flag"].values())) - cam.mean())
        wc = TW["R_cam"]
        camd = (wc @ cam) / wc.sum(1)
        rcbd = np.mean(np.stack([(TW[f"Rcb:{f}"] @ v) / TW[f"Rcb:{f}"].sum(1) for f, v in rcb.items()]), 0)
        st["_Bd_draw"] = rcbd - camd
        st["geo_flag"] = {gname: float(np.mean(np.array([L[i] for i, _ in TP[f"Rgeo:{gname}"]]) > 0)) for gname in ("g224", "g112")}
        # MEDS (TT-M1)
        fm = np.array([d["meds"][r["id"]] > 0 for r in prim], float)
        bf = (Wm @ fm) / Wm.sum(1)
        lo, hi = np.percentile(bf, [2.5, 97.5])
        st["meds_flag"], st["meds_boot"] = float(fm.mean()), [float(lo), float(hi)]
        st["TT_M1"] = "fails" if lo > 0.05 else ("transfers" if hi <= 0.10 else "neither")
        # kernel sensitivity (cross table)
        if d["cross"]:
            pc = d["cross"][prim_spec]
            sh = {sp: (float(np.mean([v[i] > 0 for i in gen_ids])), float(np.mean([v[i] > 0 for i in mor_ids])))
                  for sp, v in d["cross"].items()}
            ch = {sp: max(abs(sh[sp][0] - sh[prim_spec][0]), abs(sh[sp][1] - sh[prim_spec][1])) for sp in sh}
            st["kappa_train"] = max(ch[sp] for sp in TRAIN9 if sp != prim_spec)
            st["kappa_ho"] = max(ch[sp] for sp in HELD4)
            st["cross_flag_gen_mor"] = sh
            st["cross_lcomb_auc"] = {sp: C2.fauc([v[f"ab1x:{i}"] for i in P["lc_m"]], [v[f"ab1x:{i}"] for i in P["lc_g"]])
                                     for sp, v in d["cross"].items()}
            st["cross_c2p_dflag_fm61"] = {sp: float(np.mean([v[f"ab1x:{i}_fm61"] > 0 for i in pairs["fm61"]]) -
                                                    np.mean([v[f"ab1x:{i}"] > 0 for i in pairs["fm61"]])) for sp, v in d["cross"].items()}
            assert sh[prim_spec] == (float(np.mean([pc[i] > 0 for i in gen_ids])), float(np.mean([pc[i] > 0 for i in mor_ids])))
        if d["tr"]:
            st["train_flag_by_kind"] = {k: float(np.mean(np.array(v) > 0)) for k, v in sorted(d["tr"].items())}
        return st

    R = dict(mock=a.mock, wave=a.wave, mock_drop=sorted(drop), floor_binding=floor_pt, floors_input_matched=fl_in,
             status={}, networks={})
    arms = WAVE[a.wave]
    nets = {}
    for arm in arms + ["RZ1R_A", "RZ1R_Sb"]:
        for s in SEEDS:
            key = f"{arm}_s{s}"
            if a.mock:
                d, why = mock_net(arm, s, M, TT_ids, MD_ids, CR, drop)
            elif arm.startswith("RZ1R_"):
                d, why = load_rz1r(pathlib.Path(a.resr) / f"{arm}_s{s}.tar", arm[5:], s)
            else:
                d, why = load_rz1(pathlib.Path(a.res) / f"RZ1_{arm}_s{s}.tar", arm)
            if d is None:
                R["status"][key] = why
                continue
            st = stats(d, "fixed:pil_bilinear" if arm.startswith("RZ1R") else ARM[arm][2])
            if st is None:
                R["status"][key] = "incomplete or non-finite scores"
                continue
            R["status"][key] = why
            nets[(arm, s)] = st
            R["networks"][key] = {k: v for k, v in st.items() if not k.startswith("_")}

    ok = lambda *ks: all(k in nets for k in ks)
    V = {}
    ctrl = {z: {s: ok(("A0", s)) and nets[("A0", s)]["c2p"][z]["d_flag"] >= 0.05 and nets[("A0", s)]["c2p"][z]["d_mean_sd"] > 0
                for s in SEEDS} for z in C2.SIZES}
    V["A0_control"] = ctrl

    def xpass(X, base, s, z, ctl):
        if not ctl[z][s] or not ok((X, s), (base, s)):
            return False
        x, b = nets[(X, s)]["c2p"][z], nets[(base, s)]["c2p"][z]
        return bool(x["d_flag"] <= b["d_flag"] / 3 and abs(x["d_mean_sd"]) <= b["d_mean_sd"] / 3
                    and x["d_flag"] <= 0.05 and x["d_flag_upper95"] <= 0.08)

    def c2p61(X, base="A0", ctl=ctrl):
        """C2P.3 at fm61 deciding (section 12 M4): passes on >= 4 of 5 / fails on <= 1 with the control met on >= 4."""
        per = {s: xpass(X, base, s, "fm61", ctl) for s in SEEDS}
        nctl = sum(ctl["fm61"].values()); nread = sum(1 for s in SEEDS if ctl["fm61"][s] and ok((X, s)))
        k = sum(per.values())
        if nctl <= 3:
            v = "uninformative"
        elif nread <= 3:
            v = "not read (too few seeds)"
        elif k >= 4:
            v = "passes"
        elif k <= 1:
            v = "fails"
        else:
            v = "inconclusive, no claim"
        per112 = {s: xpass(X, base, s, "amsl112", ctl) for s in SEEDS}
        return dict(fm61_per_seed=per, n_pass_fm61=k, n_control_fm61=nctl, verdict=v, printed_amsl112_per_seed=per112)

    def paired112(X, base):
        out = {}
        for s in SEEDS:
            if ok((X, s), (base, s)):
                d = nets[(X, s)]["c2p"]["amsl112"]["d_flag"] - nets[(base, s)]["c2p"]["amsl112"]["d_flag"]
                rep = np.array(nets[(X, s)]["_c2p_rep"]["amsl112"]) - np.array(nets[(base, s)]["_c2p_rep"]["amsl112"])
                out[s] = dict(diff=float(d), ci=[float(np.percentile(rep, 2.5)), float(np.percentile(rep, 97.5))])
        return out

    def dfbar(X, base):
        """per seed: dF, its interval (TT1 draws, paired), F(X), F(base)."""
        out = {}
        for s in SEEDS:
            if ok((X, s), (base, s)):
                x, b = nets[(X, s)], nets[(base, s)]
                dd = x["_Fbar_draw"] - b["_Fbar_draw"]
                out[s] = dict(d=x["Fbar"] - b["Fbar"], ci=[float(np.percentile(dd, 2.5)), float(np.percentile(dd, 97.5))],
                              FX=x["Fbar"], Fb=b["Fbar"])
        return out

    def fbar_lower_rule(X, base):
        d = dfbar(X, base)
        lower = {s: bool((v["d"] <= -0.01 or v["FX"] <= v["Fb"] / 2) and v["ci"][1] < 0) for s, v in d.items()}
        notl = {s: bool(v["d"] > -0.005) for s, v in d.items()}
        return dict(per_seed=d, verdict=rule(sum(lower.values()), sum(notl.values()), len(d)))

    def bd_rule(X, base, lo_m=-0.02, fal=-0.005):
        d = {s: nets[(X, s)]["Bd"] - nets[(base, s)]["Bd"] for s in SEEDS if ok((X, s), (base, s))}
        return dict(per_seed=d, verdict=rule(sum(v <= lo_m for v in d.values()), sum(v > fal for v in d.values()), len(d)))

    def lc_diff(X, base):
        return {s: nets[(X, s)]["lcomb_auc"] - nets[(base, s)]["lcomb_auc"] for s in SEEDS if ok((X, s), (base, s))}

    def guard(X, base, m=-0.02):
        d = lc_diff(X, base)
        n, k = len(d), sum(v >= m for v in d.values())
        v = "not read (too few seeds)" if n <= 3 else ("held" if k_of(n, k) else ("lost" if k_of(n, n - k) else "inconclusive, no claim"))
        return dict(per_seed=d, verdict=v)

    if a.wave == "1":
        for X in ("AM", "AMR"):
            rho = {s: nets[(X, s)]["c2p"]["fm61"]["d_flag"] / nets[("A0", s)]["c2p"]["fm61"]["d_flag"]
                   for s in SEEDS if ctrl["fm61"][s] and ok((X, s))}
            nctl = sum(ctrl["fm61"].values())
            v = "uninformative" if nctl <= 3 else rule(sum(r <= 0.5 for r in rho.values()), sum(r >= 0.8 for r in rho.values()), len(rho))
            V[f"H_mix1_{X}"] = dict(rho_fm61=rho, verdict=v, printed_paired_amsl112=paired112(X, "A0"))
            c = c2p61(X)
            V[f"H_mix2_{X}"] = dict(c2p=c, verdict={"passes": "supported", "fails": "falsified"}.get(c["verdict"], c["verdict"]))
            V[f"H_mix3_{X}"] = fbar_lower_rule(X, "A0")
            V[f"H_mix5_{X}"] = guard(X, "A0")
        V["c2p_Sb0_vs_A0"] = c2p61("Sb0")
        for X in ("SbM", "SbMR"):
            pa = fbar_lower_rule(X, "Sb0")
            pb = bd_rule(X, "Sb0")
            c = c2p61(X)
            d112 = {s: nets[(X, s)]["c2p"]["amsl112"]["d_flag"] - nets[("Sb0", s)]["c2p"]["amsl112"]["d_flag"]
                    for s in SEEDS if ok((X, s), ("Sb0", s))}
            n112 = len(d112); k112 = sum(v <= 0.01 for v in d112.values())
            pc = bool(c["verdict"] == "passes" and n112 >= 4 and k_of(n112, k112))
            pd = guard(X, "Sb0")
            if pa["verdict"] == "falsified" and pb["verdict"] == "falsified":
                v = "does not add (falsified)"
            elif "supported" in (pa["verdict"], pb["verdict"]) and pc and pd["verdict"] == "held":
                v = "adds (supported)"
            elif "supported" in (pa["verdict"], pb["verdict"]) and pd["verdict"] == "lost":
                v = "trades detection for " + ", ".join(n for n, p in (("unseen-source false alarms", pa), ("border reaction", pb)) if p["verdict"] == "supported")
            else:
                v = "inconclusive, no claim"
            V[f"H_mix4_{X}"] = dict(a_Fbar=pa, b_Bd=pb, c_storage=dict(c2p=c, amsl112_diff=d112, met=pc), d_guard=pd, verdict=v)
        # kernel sensitivity
        for X in ("A0", "Sb0"):
            kv = {s: nets[(X, s)].get("kappa_ho") for s in SEEDS if ok((X, s))}
            V[f"H_ker1_{X}_kernel_sensitivity"] = dict(kappa_ho=kv, kappa_train={s: nets[(X, s)].get("kappa_train") for s in kv},
                                                       verdict=rule(sum(v > 0.10 for v in kv.values()), sum(v <= 0.05 for v in kv.values()), len(kv)))
        for X, base in (("AM", "A0"), ("AMR", "A0"), ("SbM", "Sb0"), ("SbMR", "Sb0")):
            ks = {s: (nets[(X, s)]["kappa_ho"], nets[(base, s)]["kappa_ho"]) for s in SEEDS if ok((X, s), (base, s))}
            n = len(ks)
            if n > 3 and k_of(n, sum(b <= 0.05 for _, b in ks.values())):
                v = "uninformative (nothing to remove)"
            else:
                v = rule(sum(x <= b / 2 and x <= 0.05 for x, b in ks.values()), sum(x >= 0.8 * b for x, b in ks.values()), n)
            V[f"H_ker2_{X}"] = dict(kappa_ho_X_base=ks, verdict=v)
        dd = {s: nets[("AN", s)]["c2p"]["fm61"]["d_flag"] - nets[("A0", s)]["c2p"]["fm61"]["d_flag"] for s in SEEDS if ok(("AN", s), ("A0", s))}
        n = len(dd)
        same_dir = max(sum(v >= 0.10 for v in dd.values()), sum(v <= -0.10 for v in dd.values()))
        V["H_ker3_AN"] = dict(diff_fm61=dd, verdict=rule(same_dir, sum(abs(v) < 0.03 for v in dd.values()), n),
                              printed=dict(lcomb_diff=lc_diff("AN", "A0"), Fbar_diff=dfbar("AN", "A0")))
        # amendment 1: refit yardstick
        yard = {}
        for X, Y in (("A0", "RZ1R_A"), ("Sb0", "RZ1R_Sb")):
            ss = [s for s in SEEDS if ok((X, s), (Y, s))]
            nY = sum(1 for s in SEEDS if ok((Y, s)))
            if nY < 3:
                yard[X] = dict(status="not available", n_gate_passed=nY)
                continue
            reads = ("lcomb_auc", "S3", "S0", "camera", "dsoft", "Fbar", "Bd", "meds_flag", "kappa_ho", "kappa_train")
            dl = {r: {s: nets[(X, s)][r] - nets[(Y, s)][r] for s in ss} for r in reads}
            for z in C2.SIZES:
                dl[f"c2p_dflag_{z}"] = {s: nets[(X, s)]["c2p"][z]["d_flag"] - nets[(Y, s)]["c2p"][z]["d_flag"] for s in ss}
            yard[X] = dict(status="read", n_gate_passed=nY, n_paired=len(ss), delta=dl,
                           median_abs={r: float(np.median(np.abs(list(v.values())))) for r, v in dl.items() if v},
                           max_abs={r: float(np.max(np.abs(list(v.values())))) for r, v in dl.items() if v})
        V["amendment1_refit_yardstick"] = yard
    if a.wave == "crop":
        V["H_crop1"] = dict(diff=lc_diff("Sbc", "Sb0"), verdict=rule(sum(v >= 0.03 for v in lc_diff("Sbc", "Sb0").values()),
                                                                      sum(v < 0.01 for v in lc_diff("Sbc", "Sb0").values()),
                                                                      len(lc_diff("Sbc", "Sb0"))),
                            printed_Ac_minus_A0=lc_diff("Ac", "A0"))
        c = c2p61("Ac")
        V["H_crop2"] = dict(c2p=c, verdict={"passes": "supported", "fails": "falsified"}.get(c["verdict"], c["verdict"]),
                            printed_Sbc=c2p61("Sbc"))
        V["printed_geo112_diff"] = {X: {s: nets[(X, s)]["geo_flag"]["g112"] - nets[(b, s)]["geo_flag"]["g112"] for s in SEEDS if ok((X, s), (b, s))}
                                    for X, b in (("Ac", "A0"), ("Sbc", "Sb0"))}
    if a.wave == "512":
        d = lc_diff("Sb512", "Sb0")
        V["H_512a"] = dict(diff=d, verdict=rule(sum(v >= 0.03 for v in d.values()), sum(v < 0.01 for v in d.values()), len(d)),
                           printed_A512_minus_A0=lc_diff("A512", "A0"))
        dA = {s: nets[("A512", s)]["c2p"]["fm61"]["d_flag"] - nets[("A0", s)]["c2p"]["fm61"]["d_flag"] for s in SEEDS if ok(("A512", s), ("A0", s))}
        dS = {s: (nets[("Sb512", s)]["c2p"]["fm61"]["d_flag"] - nets[("Sb0", s)]["c2p"]["fm61"]["d_flag"],
                  nets[("Sb512", s)]["c2p"]["amsl112"]["d_flag"] - nets[("Sb0", s)]["c2p"]["amsl112"]["d_flag"]) for s in SEEDS if ok(("Sb512", s), ("Sb0", s))}
        rS = rule(sum(max(u) >= 0.05 for u in dS.values()), sum(max(u) < 0.02 for u in dS.values()), len(dS))
        ctrl512 = {z: {s: ok(("A512", s)) and nets[("A512", s)]["c2p"][z]["d_flag"] >= 0.05 and nets[("A512", s)]["c2p"][z]["d_mean_sd"] > 0
                       for s in SEEDS} for z in C2.SIZES}
        V["H_512b"] = dict(plain=dict(diff_fm61=dA, verdict=rule(sum(v >= 0.10 for v in dA.values()), sum(v < 0.03 for v in dA.values()), len(dA))),
                           candidate=dict(diff=dS, verdict={"supported": "rises", "falsified": "does not rise"}.get(rS, rS)),
                           printed_Sb512_c2p_vs_A512=c2p61("Sb512", "A512", ctrl512), printed_Sb512_c2p_vs_A0=c2p61("Sb512"))
        f = dfbar("Sb512", "Sb0")
        rf = rule(sum(v["d"] >= 0.01 and v["ci"][0] > 0 for v in f.values()), sum(v["d"] < 0.005 for v in f.values()), len(f))
        b = {s: nets[("Sb512", s)]["Bd"] - nets[("Sb0", s)]["Bd"] for s in SEEDS if ok(("Sb512", s), ("Sb0", s))}
        rb = rule(sum(v >= 0.02 for v in b.values()), sum(v < 0.005 for v in b.values()), len(b))
        gq = {s: nets[("Sb512", s)]["geo_flag"]["g112"] - nets[("Sb0", s)]["geo_flag"]["g112"] for s in SEEDS if ok(("Sb512", s), ("Sb0", s))}
        rg = rule(sum(v >= 0.05 for v in gq.values()), 0, len(gq))
        V["H_512c"] = dict(Fbar=dict(per_seed=f, verdict=rf), Bd=dict(per_seed=b, verdict=rb), geo112=dict(per_seed=gq, verdict=rg),
                           meds={s: nets[("Sb512", s)]["TT_M1"] for s in SEEDS if ok(("Sb512", s))})
        rises = [n for n, v in (("storage", V["H_512b"]["candidate"]["verdict"] == "rises"), ("F", rf == "supported"),
                                ("Bd", rb == "supported"), ("geo112", rg == "supported")) if v]
        h = V["H_512a"]["verdict"]
        V["trade_verdict"] = ("no gain" if h == "falsified" else ("a trade: " + ", ".join(rises) if h == "supported" and rises else
                              ("better at no measured cost" if h == "supported" and not rises else "inconclusive, no claim")))
        c = c2p61("SbMR512", "A512", ctrl512)
        dg = lc_diff("SbMR512", "Sb512")
        fl = {s: nets[("SbMR512", s)]["Fbar"] <= nets[("Sb512", s)]["Fbar"] for s in SEEDS if ok(("SbMR512", s), ("Sb512", s))}
        nctl = sum(ctrl512["fm61"].values())
        if nctl <= 3:
            v = "uninformative"
        elif c["verdict"] == "passes" and k_of(len(dg), sum(x >= -0.02 for x in dg.values())) and k_of(len(fl), sum(fl.values())):
            v = "supported"
        elif c["verdict"] == "fails":
            v = "falsified"
        else:
            v = "inconclusive, no claim"
        V["H_512d"] = dict(c2p_vs_A512=c, lcomb_minus_Sb512=dg, Fbar_le_Sb512=fl, verdict=v)
    R["verdicts"] = V
    out = pathlib.Path(a.out)
    out.write_text(json.dumps(R, indent=1, default=lambda o: o.item() if hasattr(o, "item") else str(o)) + "\n")
    print(json.dumps({k: (v.get("verdict") if isinstance(v, dict) else None) for k, v in V.items()}, indent=1))
    print("status", json.dumps(R["status"]))


if __name__ == "__main__":
    if not sys.flags.isolated:
        sys.exit("run with python3 -I")
    main()
