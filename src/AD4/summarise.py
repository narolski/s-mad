"""Reader of the morph-free networks experiment (AD4): the pre-registration, Amendments 1, 1b, 1c and 2
(experiments/AD4/prereg.md). Replaces the 11 Nov 16:24 reader (sha256 33269760...), which lacked the person bootstrap,
the ViT-L/14 twin and the fixed-threshold rates.

Two stages, so that the gates are read before anything else:
  --stage gates   refusal checks (Amendment 1 (b)), printed checks (Amendment 2 (g)), the sample-order gate
                  (gates.py prediction vs meta.json composition, every trained network) and, for ViT-B/16, the
                  reproduction gate (morph-free seed means of 12 cells). Prints only gate outcomes.
  --stage read    everything: per network and cell EER (analyze.eer) and signed AUC (analyze.auc) with the 95% person
                  bootstrap (Amendment 2 (a)), the untrained and label-permuted references, the morph-trained ViT-L/14
                  twin (Amendment 1 (d), 2 (b)), fixed-threshold flag and miss rates (Amendment 2 (c)), the training
                  accuracies, and the fixed AD4 reading (11_AUDIT_PLAN.md + Amendment 1 (b)), or "incomplete (k of 5)"
                  descriptive rows (Amendment 2 (d)).

  python summarise.py --stage gates|read --results DIR --recipe m3|m3l [--platform NAME] [--no-order]
  python summarise.py ... --synthetic --zero-dir D --twin-root T --out-dir O --work-dir X   (tests only; B may be
                  lowered with AD4_TEST_B in synthetic mode only)

Outputs (out dir, default experiments/AD4/): ad4_gates_<recipe>.json; with --stage read also ad4_cells_<recipe>.csv
(one row per network and cell), ad4_train_<recipe>.csv, ad4_reading_<recipe>.json and ad4_reading_<recipe>.md (the
tables). Every table is labelled "our frames".
"""
import argparse
import csv
import hashlib
import io
import json
import os
import pathlib
import re
import subprocess
import sys
import tarfile

import numpy as np

HERE = pathlib.Path(__file__).resolve().parent
W = pathlib.Path("/mnt/t7/smad_next/AD4/test/work/task_AD4_m3mf_s401")   # DGX test extraction of the AD4 pack
sys.path.insert(0, str(W / "ad4/code/smadcvpr"))
sys.path.insert(0, str(HERE))
import analyze as A  # noqa: E402  (pack copy, sha256 6dd9220f...)
import ad4_score as S  # noqa: E402

EXP = pathlib.Path("/home/narolski/smad-next/experiments/AD4")
SEEDS = (401, 402, 403, 404, 405)
EVAL_SHA = "5d3950ab5ccdeed4d376a15126cff660da2a35041579b3513eb7a1059baaa061"
OLD_EVAL = pathlib.Path("/home/narolski/mambamorph-code/smadcvpr_data/manifests/eval.csv")
OLD_EVAL_SHA = "86d055d349c63a225893ace30cb3db8b1e9aea4e72350d78152126d7a49d56c9"
I3_SHA = "0273c11bd0fe4b70fc9c5490859bc185ea50b9ed971a783993b843a399e7b880"
TWIN_ROOT = pathlib.Path("/home/narolski/mambamorph-code/smadcvpr_runs/A12_scored/A12BR")
TWIN_RUN = "a12_clip_vitl14_madation_r224_d0_train90_none_lr3.33e-06_s{}_r"
TWIN_SEEDS = (1, 2, 3, 4, 5)
B_REAL = 10000
BOOT_SEED = [20261111, 4]
N_PERSONS = 102
CHUNK = 1000
ORDER_DIR = pathlib.Path("/mnt/t7/smad_next/AD4/read/order")
PRIMARY = ["mordiff/mordiff/native"]
SECONDARY = [f"dim/{f}/native" for f in ("dim_a", "dim_c", "fast_dim", "fast_dim_ode", "greedy_dim", "greedy_dim_s")]
LANDMARK = [f"frllm/{f}/native" for f in ("amsl", "facemorpher", "opencv", "webmorph")] + \
    [f"mad22c/{f}/native" for f in ("FaceMorpher", "OpenCV", "Webmorph")]
E7_NA = {"frllm/stylegan/e7", "mad22c/MIPGAN_I/e7", "mad22c/MIPGAN_II/e7"}
E7_PARTIAL = {"mad22c/OpenCV/e7": 108, "mad22c/Webmorph/e7": 104}
REPRO = {**{c: (None, 3.0) for c in PRIMARY + SECONDARY},
         "frllm/facemorpher/native": (None, 5.6), "frllm/webmorph/native": (None, 5.6),
         "frllm/amsl/native": (None, 5.6), "frllm/opencv/native": (8.8, 26.0)}
ARCH = {"m3": "a12_clip_vitb16_madation", "m3l": "a12_clip_vitl14_madation"}
RECIPE_NAME = {"m3": "CLIP ViT-B/16 with LoRA (M3)", "m3l": "CLIP ViT-L/14 with LoRA (M3L)"}
ARM_NAME = {"mf": "morph-free", "perm": "label-permuted", "zero": "untrained", "twin": "morph-trained twin"}
SET_ORDER = {"mordiff": 0, "dim": 1, "frllm": 2, "mad22c": 3}
NICE = {"mordiff/mordiff": "MorDIFF", "dim/dim_a": "DiM-A", "dim/dim_c": "DiM-C", "dim/fast_dim": "Fast-DiM",
        "dim/fast_dim_ode": "Fast-DiM-ODE", "dim/greedy_dim": "Greedy-DiM", "dim/greedy_dim_s": "Greedy-DiM-S",
        "frllm/amsl": "FRLL AMSL", "frllm/facemorpher": "FRLL FaceMorpher", "frllm/opencv": "FRLL OpenCV",
        "frllm/webmorph": "FRLL Webmorph", "frllm/stylegan": "FRLL StyleGAN",
        "mad22c/FaceMorpher": "corrected MAD22 FaceMorpher", "mad22c/OpenCV": "corrected MAD22 OpenCV",
        "mad22c/Webmorph": "corrected MAD22 Webmorph", "mad22c/MIPGAN_I": "corrected MAD22 MIPGAN-I",
        "mad22c/MIPGAN_II": "corrected MAD22 MIPGAN-II"}


def sha(p):
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for b in iter(lambda: f.read(1 << 20), b""):
            h.update(b)
    return h.hexdigest()


def die(msg):
    raise SystemExit(f"AD4 reader stopped: {msg}")


def nice(c):
    k, kind = c.rsplit("/", 1)
    return f"{NICE.get(k, k)} {'native' if kind == 'native' else 'E7 (history-matched)'}"


def cell_label(c):
    if c in E7_NA:
        return "E7 not applicable"
    if c in E7_PARTIAL:
        return f"E7 partial ({E7_PARTIAL[c]}/204 identical)"
    return ""


def cell_key(c):
    st, fam, kind = c.split("/")
    return (SET_ORDER.get(st, 9), fam.lower(), 0 if kind == "native" else 1)


# ------------------------------------------------------------------ persons and draws: a41_read.py (sha256 0bc7381b...)
# lines 326-383, unchanged (die() as here), plus the two corrected-MAD22 patterns of Amendment 2 (a).
RX = {"mordiff": re.compile(r"^morph_(\d{3})_\d{2}_and_(\d{3})_\d{2}_"), "vs": re.compile(r"^(\d{3})_\d{2}-vs-(\d{3})_\d{2}_"),
      "pair": re.compile(r"^(\d{3})_(\d{3})_"), "bona": re.compile(r"^(\d{3})_(\d{2})_")}
RX_MAD22C = {"bona": re.compile(r"^(\d{3})_(\d{2})\.png$"), "vs": re.compile(r"^(\d{3})_\d{2}-vs-(\d{3})_\d{2}\.png$")}


def persons(r):
    """FRLL person ids of an eval row: a bona fide photo -> (p,), a morph -> (a, b), from the file name only."""
    b = pathlib.PurePath(r["path"]).name
    if r["set"] == "mad22c":
        m = RX_MAD22C["bona" if r["label"] == "0" else "vs"].match(b)
        if not m:
            die(f"{b}: no FRLL person pattern (corrected MAD22)")
        return (m.group(1),) if r["label"] == "0" else (m.group(1), m.group(2))
    if r["label"] == "0":
        m = RX["bona"].match(b)
        if not m:
            die(f"{b}: no FRLL person prefix")
        return (m.group(1),)
    for k in ("mordiff", "vs", "pair"):
        m = RX[k].match(b)
        if m:
            return (m.group(1), m.group(2))
    die(f"{b}: no FRLL contributor pair")


class Draw:
    """the pigeonhole (dyadic) person bootstrap (Owen 2007): persons ~ Multinomial(n, 1/n) per replicate; a bona fide
    photo weighs its person's count, a morph the product of its two contributors' counts (a self-pair: the count), the
    same draw for every pool, family and network (paired)."""

    def __init__(self, pers, B, seed):
        self.per = sorted(set(pers))
        self.pos = {p: i for i, p in enumerate(self.per)}
        n = len(self.per)
        self.C = np.random.default_rng(seed).multinomial(n, np.full(n, 1.0 / n), size=B).astype(np.float64)
        self.B = B

    def wb(self, pp, C=None):
        C = self.C if C is None else C
        return C[:, [self.pos[p[0]] for p in pp]]

    def wm(self, pp, C=None):
        C = self.C if C is None else C
        a = np.array([self.pos[p[0]] for p in pp])
        b = np.array([self.pos[p[1]] for p in pp])
        w = C[:, a] * C[:, b]
        same = a == b
        if same.any():
            w[:, same] = C[:, a[same]]
        return w


def wauc(pos, neg, wp, wn):
    """a36_read.py wauc (sha256 684aea1b...), unchanged: weighted Mann-Whitney AUC for (R, n) weights -> (R,)."""
    ob = np.argsort(neg, kind="stable")
    ns = neg[ob]
    lo, hi = np.searchsorted(ns, pos, "left"), np.searchsorted(ns, pos, "right")
    C = np.concatenate([np.zeros((wn.shape[0], 1)), np.cumsum(wn[:, ob], 1)], 1)
    below, tie = C[:, lo], C[:, hi] - C[:, lo]
    num = (wp * (below + 0.5 * tie)).sum(1)
    return num / np.maximum(wp.sum(1) * C[:, -1], 1e-12)


def ci(rep):
    rep = np.asarray(rep, float)
    rep = rep[np.isfinite(rep)]
    return [float(x) for x in np.percentile(rep, [2.5, 97.5])] if len(rep) else [None, None]


# ------------------------------------------------------------------ fixed thresholds (Amendment 2 (c))
def thresholds(score, ifrll):
    s = np.sort(score[ifrll])[::-1]
    return {"0.5 rule": ("ge", 0.5), "FRLL-5%": ("gt", float(s[10]))}


def flagged(score, thr):
    op, t = thr
    return score >= t if op == "ge" else score > t


# ------------------------------------------------------------------ loading
def read_tar(tar, t):
    with tarfile.open(tar) as tf:
        g = lambda n: tf.extractfile(f"{t}/{n}").read()  # noqa: E731
        return (json.loads(g("metrics.json")), json.loads(g("meta.json")), np.load(io.BytesIO(g("scores_eval.npz"))),
                np.load(io.BytesIO(g("scores_train.npz"))))


def load_trained(results, recipe, rows, perm_sha, platform):
    nets, refused, checks, present = {}, {}, {}, {"mf": [], "perm": []}
    ids = [r["id"] for r in rows]
    for arm in ("mf", "perm"):
        for s in SEEDS:
            t = f"AD4_{recipe}{arm}_s{s}"
            tar, sf = results / f"{t}.tar", results / f"{t}.tar.sha256"
            if not (tar.is_file() and sf.is_file()):
                continue
            present[arm].append(s)
            tsha = sha(tar)
            if sf.read_text().split()[0] != tsha:
                refused[t] = "result tar sha256 mismatch"
                continue
            m, meta, ev, tr = read_tar(tar, t)
            why = []                                            # Amendment 1 (b): refusals
            if meta.get("steps") != 6250:
                why.append(f"steps {meta.get('steps')}")
            if m["info"].get("limit") != 0:
                why.append(f"limit {m['info'].get('limit')}")
            if str(ev["manifest_sha256"]) != EVAL_SHA:
                why.append("eval manifest sha256")
            want = I3_SHA if arm == "mf" else perm_sha[str(s)]
            if str(tr["manifest_sha256"]) != want:
                why.append("training manifest sha256")
            sc = ev["score"].astype(np.float64)
            if not np.all(np.isfinite(sc)):
                why.append("non-finite score")
            if list(ev["id"]) != ids:
                why.append("eval ids differ from ad4_eval.csv")
            checks[t] = {"tar_sha256": tsha, "meta_seed_ok": meta.get("seed") == s,        # Amendment 2 (g)
                         "meta_arch_ok": meta.get("arch") == ARCH[recipe], "device": m["info"].get("device"),
                         "torch": m["info"].get("torch"), "train_hours": m["info"].get("train_hours")}
            if why:
                refused[t] = "; ".join(why)
                continue
            nets[t] = dict(arm=arm, seed=s, score=sc, train=m["train"], meta=meta, info=m["info"],
                           platform=f"{platform}, {m['info'].get('device')}")
    return nets, refused, checks, present


def load_zero(zdir, recipe):
    zn, zm = zdir / "scores_eval.npz", zdir / "metrics.json"
    if not (zn.is_file() and zm.is_file()):
        return {}
    z = np.load(zn)
    m = json.load(open(zm))
    if str(z["manifest_sha256"]) != EVAL_SHA or not np.all(np.isfinite(z["score"])):
        die(f"untrained network {zdir}: manifest or non-finite score")
    return {f"AD4_{recipe}zero_s401": dict(arm="zero", seed=401, score=z["score"].astype(np.float64), train=m["train"],
                                           meta=None, info=m["info"], platform=f"DGX, {m['info'].get('device')}")}


def load_twin(root, rows, synthetic):
    """Amendment 2 (b): the A12BR M3L R x d0 networks, last checkpoint, on the old eval.csv, matched by id."""
    if not synthetic:
        if sha(OLD_EVAL) != OLD_EVAL_SHA:
            die("eval.csv sha256")
        old = {r["id"]: r["path"] for r in csv.DictReader(open(OLD_EVAL))}
        for r in rows:
            if r["set"] != "mad22c" and old.get(r["id"]) != r["path"]:
                die(f"ad4_eval.csv row {r['id']} does not equal eval.csv")
    out, files = {}, {}
    for s in TWIN_SEEDS:
        f = root / TWIN_RUN.format(s) / "scores_eval_last.npz"
        z = np.load(f)
        if str(z["manifest_sha256"]) != OLD_EVAL_SHA:
            die(f"{f}: manifest sha256")
        mp = dict(zip(z["id"].tolist(), z["score"].astype(np.float64)))
        sc = np.array([mp.get(r["id"], np.nan) for r in rows])
        files[str(f)] = sha(f)
        out[f"A12BR_m3l_R_d0_s{s}"] = dict(arm="twin", seed=s, score=sc, train=None, meta=None, info={},
                                           platform="WCSS H100 (A12BR)")
    return out, files


# ------------------------------------------------------------------ gates
def order_gate(nets, recipe, synthetic):
    out = {}
    od = ORDER_DIR if not synthetic else pathlib.Path(os.environ["AD4_TEST_ORDER_DIR"])
    od.mkdir(parents=True, exist_ok=True)
    env = {"CUDA_VISIBLE_DEVICES": "", "PATH": "/usr/bin:/bin", "OMP_NUM_THREADS": "2", "OPENBLAS_NUM_THREADS": "2",
           "MKL_NUM_THREADS": "2", "NUMEXPR_NUM_THREADS": "2", "HOME": os.environ.get("HOME", "/tmp")}
    for t, n in sorted(nets.items()):
        if n["arm"] not in ("mf", "perm"):
            continue
        mf = od / f"meta_{t}.json"
        mf.write_text(json.dumps({"composition": n["meta"]["composition"]}))
        man = "train_i3.csv" if n["arm"] == "mf" else f"train_perm_s{n['seed']}.csv"
        p = subprocess.run([sys.executable, str(HERE / "gates.py"), "order", "--arch", ARCH[recipe], "--seed",
                            str(n["seed"]), "--manifest", man, "--meta", str(mf), "--out", str(od / f"pred_{t}.json")],
                           capture_output=True, text=True, env=env)
        if p.returncode != 0:
            die(f"gates.py order failed for {t}: {p.stderr[-2000:]}")
        r = json.loads(p.stdout.strip().splitlines()[-1])
        out[t] = {"pass": r["gate_pass"], "equal_rows": r["equal_rows"], "recorded_n": r["recorded_n"],
                  "first3_pred": r["first3"], "first3_rec": r["recorded_first3"]}
    return out


def repro_gate(nets, recipe, rows):
    mf = [n for n in nets.values() if n["arm"] == "mf"]
    if recipe != "m3":
        return {"status": "not registered for this recipe"}
    if len(mf) != 5:
        return {"status": f"incomplete ({len(mf)} of 5)"}
    cl = S.cells(rows)
    rep, ok = {}, True
    for c, (lo, hi) in REPRO.items():
        m, b = cl[c]
        e = [100 * A.eer(n["score"][b], n["score"][m]) for n in sorted(mf, key=lambda x: x["seed"])]
        mean = float(np.mean(e))
        p = (lo is None or mean >= lo) and mean <= hi
        ok &= p
        rep[c] = {"mean_eer": mean, "per_seed": e, "bound": [lo, hi], "pass": bool(p)}
    return {"status": "pass" if ok else "MISS: not reproduced on this stack", "cells": rep}


# ------------------------------------------------------------------ the reading
def compute(nets, rows, D, synthetic):
    """per network and cell: point EER / AUC, bootstrap replicates, fixed-threshold rates."""
    cl = S.cells(rows)
    ifr = np.array(cl["frllm/amsl/native"][1])
    assert all(rows[i]["family"] == "frll_bona" for i in ifr)
    pp = {c: ([persons(rows[i]) for i in m], [persons(rows[i]) for i in b]) for c, (m, b) in cl.items()}
    res = {t: {} for t in nets}
    thr = {t: thresholds(n["score"], ifr) for t, n in nets.items() if np.all(np.isfinite(n["score"][ifr]))}
    for t, n in nets.items():
        for c, (m, b) in cl.items():
            sm, sb = n["score"][m], n["score"][b]
            if not (np.all(np.isfinite(sm)) and np.all(np.isfinite(sb))):
                continue                                         # the twin has no scores on corrected MAD22
            r = {"n_morph": len(m), "n_bona": len(b), "eer": 100 * A.eer(sb, sm), "auc": A.auc(sm, sb)}
            e1 = 100 * A.eer_weighted(sb, sm, np.ones((1, len(sb))), np.ones((1, len(sm))))[0]
            a1 = wauc(sm, sb, np.ones((1, len(sm))), np.ones((1, len(sb))))[0]
            if abs(e1 - r["eer"]) > 1e-9 or abs(a1 - r["auc"]) > 1e-9:
                die(f"unit weights do not reproduce {t} {c} ({e1} vs {r['eer']}, {a1} vs {r['auc']})")
            if t in thr:
                for k, th in thr[t].items():
                    r[f"flag {k}"] = float(flagged(sb, th).mean())
                    r[f"miss {k}"] = float((~flagged(sm, th)).mean())
                    r[f"thr {k}"] = th[1]
            r["_eer"], r["_auc"] = np.empty(D.B), np.empty(D.B)
            res[t][c] = r
    for a in range(0, D.B, CHUNK):
        C = D.C[a:a + CHUNK]
        for c, (m, b) in cl.items():
            wm, wb = D.wm(pp[c][0], C), D.wb(pp[c][1], C)
            for t, n in nets.items():
                if c not in res[t]:
                    continue
                sm, sb = n["score"][m], n["score"][b]
                res[t][c]["_eer"][a:a + CHUNK] = 100 * A.eer_weighted(sb, sm, wb, wm)
                res[t][c]["_auc"][a:a + CHUNK] = wauc(sm, sb, wm, wb)
        print(f"  bootstrap {min(a + CHUNK, D.B)}/{D.B}", flush=True)
    for t in res:
        for c, r in res[t].items():
            r["eer_ci95"], r["auc_ci95"] = ci(r["_eer"]), ci(r["_auc"])
    return res, cl


def f1(x, d=1):
    return "-" if x is None else f"{x:.{d}f}"


def fci(v, d=1):
    return f"[{f1(v[0], d)}, {f1(v[1], d)}]"


def reading(nets, res, cells, recipe, order, present):
    by = {a: sorted([t for t, n in nets.items() if n["arm"] == a], key=lambda t: nets[t]["seed"])
          for a in ("mf", "perm", "zero", "twin")}
    k_mf, k_perm = len(by["mf"]), len(by["perm"])
    ref = by["perm"] + by["zero"]
    if k_mf < 5:
        status = f"incomplete ({k_mf} of 5 morph-free networks): descriptive rows only"
    elif k_perm == 5 and len(by["zero"]) == 1:
        status = "final"
    else:
        status = f"provisional ({len(ref)} of 6 references)"
    miss_order = {t for t, g in order.items() if not g["pass"]}
    mark = lambda t: f"{nets[t]['seed']}{' (order MISS)' if t in miss_order else ''}"  # noqa: E731
    out = {"status": status, "recipe": recipe, "networks": {t: {"arm": n["arm"], "seed": n["seed"],
                                                                "platform": n["platform"]} for t, n in nets.items()},
           "order_miss": sorted(miss_order), "cells": {}}
    for c in cells:
        def arm_vals(a, k):
            return [res[t][c][k] for t in by[a] if c in res[t]]
        e_mf, e_ref = arm_vals("mf", "eer"), [res[t][c]["eer"] for t in ref if c in res[t]]
        d = {"role": "primary" if c in PRIMARY else "secondary" if c in SECONDARY else "descriptive",
             "note": cell_label(c)}
        for a in ("mf", "perm", "zero", "twin"):
            ts = [t for t in by[a] if c in res[t]]
            if not ts:
                continue
            er = np.mean([res[t][c]["_eer"] for t in ts], 0)
            ar = np.mean([res[t][c]["_auc"] for t in ts], 0)
            d[a] = {"seeds": [nets[t]["seed"] for t in ts], "eer": [res[t][c]["eer"] for t in ts],
                    "eer_ci95": [res[t][c]["eer_ci95"] for t in ts], "auc": [res[t][c]["auc"] for t in ts],
                    "auc_ci95": [res[t][c]["auc_ci95"] for t in ts], "eer_mean": float(np.mean(arm_vals(a, "eer"))),
                    "eer_mean_ci95": ci(er), "auc_mean": float(np.mean(arm_vals(a, "auc"))), "auc_mean_ci95": ci(ar)}
            for k in ("0.5 rule", "FRLL-5%"):
                fl, mi = arm_vals(a, f"flag {k}"), arm_vals(a, f"miss {k}")
                d[a][f"flag {k}"], d[a][f"miss {k}"] = fl, mi
                d[a][f"flag {k} mean"] = float(np.mean(fl)) if fl else None
                d[a][f"miss {k} mean"] = float(np.mean(mi)) if mi else None
        if e_ref:
            lo, hi = min(e_ref), max(e_ref)
            d["ref_lowest"], d["ref_range"] = lo, [lo, hi]
            d["folded_ref_auc_max"] = max(abs(res[t][c]["auc"] - 0.5) + 0.5 for t in ref if c in res[t])
        if e_mf and e_ref:
            mean = float(np.mean(e_mf))
            rep_ref = np.min([res[t][c]["_eer"] for t in ref if c in res[t]], 0)
            rep_mf = np.mean([res[t][c]["_eer"] for t in by["mf"] if c in res[t]], 0)
            d["margin"] = mean - lo
            d["margin_ci95"] = ci(rep_mf - rep_ref)
            passable = mean <= lo - 10
            k_margin = sum(x <= lo - 10 for x in e_mf)
            k15 = sum(x > 15 for x in e_mf)
            d["seeds_margin"], d["seeds_above_15"] = f"{k_margin}/{k_mf}", f"{k15}/{k_mf}"
            if k_mf < 5:
                d["passable"] = d["a1"] = f"incomplete ({k_mf} of 5)"
            else:
                d["passable"] = ("yes" if passable else "no") + ("" if status == "final" else " (provisional)")
                d["a1"] = ("falsified" if k15 >= 3 else "not falsified") if d["role"] != "descriptive" else "-"
                notes = [d["note"]]
                if passable and k15 >= 3:
                    notes.append("below every label-free reference, not at the published level (above 15% in "
                                 f"{k15} of 5 seeds)" + ("; A1 falsified on this cell although the network beats the "
                                                         "references" if d["role"] != "descriptive" else ""))
                if c in LANDMARK and passable:
                    notes.append(f"at least 10 points below every label-free reference (range {lo:.1f} to "
                                 f"{hi:.1f}%); not 'above chance'")
                if c in LANDMARK and not passable:
                    notes.append("a miss on a landmark cell does not show that the cell needs morphs")
                if recipe == "m3l" and d["a1"] == "falsified":
                    tw = d.get("twin")
                    notes.append("does not reach 15%; " + (f"the morph-trained recipe reaches {tw['eer_mean']:.1f}%"
                                                           if tw else "no twin"))
                d["note"] = "; ".join(x for x in notes if x)
        if recipe == "m3l" and "twin" not in d:
            d["note"] = "; ".join(x for x in (d["note"], "no twin") if x)
        out["cells"][c] = d
    out["by_arm"] = by
    out["present_tars"] = present
    return out


def md_tables(out, nets, cells, recipe, gates, train_rows):
    by = out["by_arm"]
    L = [f"# Morph-free networks (AD4), {RECIPE_NAME[recipe]}: reading, our frames", "",
         f"Status: **{out['status']}**. All numbers on our frames (our alignment of every benchmark). EER in %, signed "
         "AUC (morph positive). 95% intervals: person bootstrap (Amendment 2 (a)), descriptive; the verdicts use point "
         "values.", ""]
    rg = gates.get("reproduction", {})
    if str(rg.get("status", "")).startswith("MISS"):
        miss = [c for c, g in rg["cells"].items() if not g["pass"]]
        flag = ("**FLAG on every number of this recipe's trained networks: not reproduced on this stack** (reproduction "
                f"gate, {len(miss)} of {len(rg['cells'])} cells: " + "; ".join(
                    f"{nice(c)}, morph-free seed mean {rg['cells'][c]['mean_eer']:.2f}% against a bound of "
                    f"{rg['cells'][c]['bound'][1]} (per seed {', '.join(f'{x:.2f}' for x in rg['cells'][c]['per_seed'])})"
                    for c in miss) + "). The registered remedy (the WCSS cluster tasks) decides when it runs; until then "
                "this reading is descriptive. No seed is dropped or reweighted.")
        out["reproduction_flag"] = flag
        L += [flag, ""]
    elif rg.get("status") == "pass":
        L += ["Reproduction gate: pass.", ""]
    L.append("Networks (arm, seed, platform and card):")
    for a in ("mf", "perm", "zero", "twin"):
        for t in by[a]:
            o = gates.get("order", {}).get(t)
            og = "" if o is None else f"; sample-order gate {'pass' if o['pass'] else 'MISS'} ({o['equal_rows']}/200)"
            L.append(f"- {ARM_NAME[a]} seed {nets[t]['seed']} (`{t}`): {nets[t]['platform']}{og}")
    for a in ("mf", "perm"):
        miss = [s for s in SEEDS if s not in out["present_tars"].get(a, [])]
        if miss:
            L.append(f"- {ARM_NAME[a]}: seeds {', '.join(map(str, miss))} not present")
    fl = ["", "Flag: not reproduced on this stack (see top)."] if "reproduction_flag" in out else []
    L += ["", f"## Table 1. EER per cell (%), our frames, {RECIPE_NAME[recipe]}", *fl, "",
          "| cell | role | morph-free: mean [95% CI] (per seed) | label-permuted: mean (range) | untrained | "
          "lowest reference | margin = morph-free mean minus lowest reference [95% CI] | passable without morphs | "
          "seeds meeting margin | seeds above 15% | A1 |" + (" morph-trained twin: mean (range) |" if recipe == "m3l"
                                                              else "") + " note |",
          "|---" * (12 + (recipe == "m3l")) + "|"]
    for c in cells:
        d = out["cells"][c]
        mf, pm, z, tw = d.get("mf"), d.get("perm"), d.get("zero"), d.get("twin")
        smf = (f"{mf['eer_mean']:.1f} {fci(mf['eer_mean_ci95'])} ({', '.join(f1(x) for x in mf['eer'])})"
               if mf else "-")
        spm = f"{pm['eer_mean']:.1f} ({min(pm['eer']):.1f} to {max(pm['eer']):.1f}), n={len(pm['eer'])}" if pm else "-"
        sz = f"{z['eer'][0]:.1f}" if z else "-"
        stw = f"{tw['eer_mean']:.1f} ({min(tw['eer']):.1f} to {max(tw['eer']):.1f})" if tw else "no twin"
        row = (f"| {nice(c)} | {d['role']} | {smf} | {spm} | {sz} | {f1(d.get('ref_lowest'))} | "
               f"{f1(d.get('margin'))} {fci(d['margin_ci95']) if 'margin_ci95' in d else ''} | {d.get('passable', '-')} "
               f"| {d.get('seeds_margin', '-')} | {d.get('seeds_above_15', '-')} | {d.get('a1', '-')} |")
        if recipe == "m3l":
            row += f" {stw} |"
        L.append(row + f" {d['note']} |")
    L += ["", f"## Table 2. Signed AUC per cell, our frames, {RECIPE_NAME[recipe]}", *fl, "",
          "| cell | morph-free: mean [95% CI] (per seed) | label-permuted: mean (range) | untrained | folded reference "
          "AUC, max |" + (" morph-trained twin: mean |" if recipe == "m3l" else ""),
          "|---" * (5 + (recipe == "m3l")) + "|"]
    for c in cells:
        d = out["cells"][c]
        mf, pm, z, tw = d.get("mf"), d.get("perm"), d.get("zero"), d.get("twin")
        row = (f"| {nice(c)} | " + (f"{mf['auc_mean']:.3f} {fci(mf['auc_mean_ci95'], 3)} "
                                     f"({', '.join(f1(x, 3) for x in mf['auc'])})" if mf else "-") + " | "
               + (f"{pm['auc_mean']:.3f} ({min(pm['auc']):.3f} to {max(pm['auc']):.3f})" if pm else "-") + " | "
               + (f"{z['auc'][0]:.3f}" if z else "-") + f" | {f1(d.get('folded_ref_auc_max'), 3)} |")
        if recipe == "m3l":
            row += (f" {tw['auc_mean']:.3f} |" if tw else " no twin |")
        L.append(row)
    for k, pool in (("0.5 rule", "none (score at least 0.5)"),
                    ("FRLL-5%", "204 unprocessed FRLL genuine photos, at most 10 flagged")):
        L += ["", f"## Table 3{'a' if k == '0.5 rule' else 'b'}. Fixed threshold \"{k}\": flag rate (genuine photos "
              f"flagged) and miss rate (morphs not flagged), %, our frames, {RECIPE_NAME[recipe]}", "",
              f"Threshold pool: {pool}. Arm means; per-seed miss rates in brackets.", *fl, "",
              "| cell | morph-free flag / miss (per-seed miss) | label-permuted flag / miss | untrained flag / miss |"
              + (" morph-trained twin flag / miss |" if recipe == "m3l" else ""),
              "|---" * (4 + (recipe == "m3l")) + "|"]
        for c in cells:
            d = out["cells"][c]

            def fm(a, per=False):
                x = d.get(a)
                if not x or x.get(f"flag {k} mean") is None:
                    return "no twin" if a == "twin" else "-"
                s = f"{100 * x[f'flag {k} mean']:.1f} / {100 * x[f'miss {k} mean']:.1f}"
                return s + (f" ({', '.join(f'{100 * v:.1f}' for v in x[f'miss {k}'])})" if per else "")
            row = f"| {nice(c)} | {fm('mf', True)} | {fm('perm')} | {fm('zero')} |"
            if recipe == "m3l":
                row += f" {fm('twin')} |"
            L.append(row)
    L += ["", f"## Table 4. Training accuracy (threshold 0.5, no TTA), {RECIPE_NAME[recipe]}", *fl, "",
          "| network | arm | own training labels: accuracy / AUC | true labels: accuracy / AUC | share of labels "
          "permuted | train hours |", "|---|---|---|---|---|---|"]
    for r in train_rows:
        L.append(f"| `{r[0]}` | {ARM_NAME[r[1]]} | {r[4]} / {r[6]} | {r[5]} / {r[7]} | {r[8]} | {r[9]} |")
    return "\n".join(L) + "\n"


# ------------------------------------------------------------------ main
def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--stage", choices=("gates", "read"), required=True)
    ap.add_argument("--results", required=True)
    ap.add_argument("--recipe", choices=("m3", "m3l"), required=True)
    ap.add_argument("--platform", default=None, help="printed beside each trained network")
    ap.add_argument("--no-order", action="store_true", help="skip the sample-order gate (tests only)")
    ap.add_argument("--synthetic", action="store_true")
    ap.add_argument("--zero-dir", default=None)
    ap.add_argument("--twin-root", default=None)
    ap.add_argument("--out-dir", default=None)
    a = ap.parse_args()
    if not a.synthetic and (a.zero_dir or a.twin_root or a.out_dir or a.no_order):
        ap.error("--zero-dir/--twin-root/--out-dir/--no-order are for --synthetic tests only")
    out_dir = pathlib.Path(a.out_dir) if a.out_dir else EXP
    zdir = pathlib.Path(a.zero_dir) if a.zero_dir else pathlib.Path(f"/mnt/t7/smad_next/AD4/zero_step/{a.recipe}")
    twin_root = pathlib.Path(a.twin_root) if a.twin_root else TWIN_ROOT
    results = pathlib.Path(a.results)
    platform = a.platform or ("rented machine (Vast)" if "vast" in results.name else
                              "Athena A100 (Amendment 1c)" if "athena" in results.name else results.name)
    man = W / "ad4/data/manifests/ad4_eval.csv"
    if sha(man) != EVAL_SHA:
        die("ad4_eval.csv sha256")
    rows = list(csv.DictReader(open(man)))
    perm_sha = {k: v["sha256"] for k, v in json.load(open(W / "ad4/build_info.json"))["perms"].items()}
    nets, refused, checks, present = load_trained(results, a.recipe, rows, perm_sha, platform)
    gates = {"reader_sha256": sha(__file__), "results": str(results), "present_tars": present, "refused": refused,
             "checks": checks}
    print(f"present tars: morph-free {present['mf']}, label-permuted {present['perm']}")
    print("refused:", json.dumps(refused) if refused else "none")
    for t, c in sorted(checks.items()):
        if not (c["meta_seed_ok"] and c["meta_arch_ok"]):
            print(f"CHECK {t}: meta seed ok {c['meta_seed_ok']}, arch ok {c['meta_arch_ok']}")
    gates["order"] = {} if a.no_order else order_gate(nets, a.recipe, a.synthetic)
    for t, g in sorted(gates["order"].items()):
        print(f"sample-order gate {t}: {'pass' if g['pass'] else 'MISS'} ({g['equal_rows']}/200; recorded "
              f"{g['recorded_n']} rows; first3 recorded {g['first3_rec']}, predicted {g['first3_pred']})")
    gates["reproduction"] = repro_gate(nets, a.recipe, rows)
    print(f"reproduction gate: {gates['reproduction']['status']}")
    for c, g in gates["reproduction"].get("cells", {}).items():
        lo, hi = g["bound"]
        print(f"  {nice(c)}: morph-free seed mean {g['mean_eer']:.2f}% (bound {'' if lo is None else f'{lo} to '}"
              f"{hi}) {'pass' if g['pass'] else 'MISS'}")
    sc_eq = EXP / "gate_scorer_equivalence.json"
    if sc_eq.is_file() and not a.synthetic:
        gates["scorer_equivalence"] = {"file": str(sc_eq), "gate_pass": json.load(open(sc_eq))["gate_pass"]}
        print(f"scorer-equivalence gate (11 Nov 16:46): {'pass' if gates['scorer_equivalence']['gate_pass'] else 'MISS'}")
    out_dir.mkdir(parents=True, exist_ok=True)
    json.dump(gates, open(out_dir / f"ad4_gates_{a.recipe}.json", "w"), indent=1, default=float)
    if a.stage == "gates":
        return
    # ---------------------------------------------------------------- stage read
    nets.update(load_zero(zdir, a.recipe))
    twin_files = {}
    if a.recipe == "m3l":
        tw, twin_files = load_twin(twin_root, rows, a.synthetic)
        nets.update(tw)
    cl = S.cells(rows)
    pers = sorted({p for i in cl["frllm/amsl/native"][1] for p in persons(rows[i])})
    if not a.synthetic and len(pers) != N_PERSONS:
        die(f"{len(pers)} FRLL persons, registered {N_PERSONS}")
    allp = {p for r in rows for p in persons(r)}
    if not allp <= set(pers):
        die(f"persons outside the FRLL genuine set: {sorted(allp - set(pers))[:10]}")
    B = int(os.environ.get("AD4_TEST_B", B_REAL)) if a.synthetic else B_REAL
    D = Draw(pers, B, BOOT_SEED)
    print(f"bootstrap: {B} replicates over {len(pers)} persons, seed {BOOT_SEED}", flush=True)
    res, cl = compute(nets, rows, D, a.synthetic)
    cells = sorted(cl, key=cell_key)
    out = reading(nets, res, cells, a.recipe, gates["order"], present)
    out["bootstrap"] = {"B": B, "seed": BOOT_SEED, "persons": len(pers), "scheme": "pigeonhole (dyadic) person "
                        "bootstrap (a41_read.py Draw)"}
    out["twin_files_sha256"] = twin_files
    out["reader_sha256"] = gates["reader_sha256"]
    out["label"] = "our frames"
    with open(out_dir / f"ad4_cells_{a.recipe}.csv", "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["network", "arm", "seed", "platform", "cell", "n_morph", "n_bona", "eer_pct", "eer_ci95_lo",
                    "eer_ci95_hi", "auc_signed", "auc_ci95_lo", "auc_ci95_hi", "flag_0.5", "miss_0.5", "thr_frll5",
                    "flag_frll5", "miss_frll5", "order_gate", "reproduction_gate", "note", "frames"])
        for t in sorted(nets):
            n = nets[t]
            og = gates["order"].get(t)
            for c in cells:
                if c not in res[t]:
                    continue
                v = res[t][c]
                w.writerow([t, n["arm"], n["seed"], n["platform"], c, v["n_morph"], v["n_bona"], round(v["eer"], 3),
                            round(v["eer_ci95"][0], 3), round(v["eer_ci95"][1], 3), round(v["auc"], 5),
                            round(v["auc_ci95"][0], 5), round(v["auc_ci95"][1], 5),
                            round(v.get("flag 0.5 rule", np.nan), 4), round(v.get("miss 0.5 rule", np.nan), 4),
                            v.get("thr FRLL-5%"), round(v.get("flag FRLL-5%", np.nan), 4),
                            round(v.get("miss FRLL-5%", np.nan), 4),
                            "" if og is None else ("pass" if og["pass"] else "MISS"),
                            ("not reproduced on this stack" if str(gates["reproduction"].get("status", "")).startswith(
                                "MISS") and n["arm"] in ("mf", "perm") else gates["reproduction"].get("status", "")),
                            cell_label(c), "our frames"])
    train_rows = []
    for t in sorted(nets):
        n = nets[t]
        if n["train"] is None:
            continue
        tr = n["train"]
        train_rows.append([t, n["arm"], n["seed"], tr["n"], round(tr["acc_vs_training_labels"], 4),
                           round(tr["acc_vs_true_labels"], 4), round(tr["auc_vs_training_labels"], 4),
                           round(tr["auc_vs_true_labels"], 4), round(tr["frac_labels_permuted"], 4),
                           n["info"].get("train_hours")])
    with open(out_dir / f"ad4_train_{a.recipe}.csv", "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["network", "arm", "seed", "n", "acc_training_labels", "acc_true_labels", "auc_training_labels",
                    "auc_true_labels", "frac_permuted", "train_hours"])
        w.writerows(train_rows)
    md = md_tables(out, nets, cells, a.recipe, gates, train_rows)
    json.dump(out, open(out_dir / f"ad4_reading_{a.recipe}.json", "w"), indent=1, default=float)
    (out_dir / f"ad4_reading_{a.recipe}.md").write_text(md)
    print(md)


if __name__ == "__main__":
    main()
