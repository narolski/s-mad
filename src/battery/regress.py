"""Shared test battery (BATTERY): regression test on stored logits of already-reviewed networks. CPU only, no image opened.

For every reviewed network whose logits exist on /mnt/t7/smad_next, the battery blocks (stats.py) are run on the stored
logits and every leaf of the reviewed reader's per-network JSON record is compared with the battery's value at the same
path, by exact equality (floats: ==, NaN equal to NaN; lists element by element; strings and booleans equal).
Every leaf that differs or is absent is listed with its path. Inputs are read from the verified result tars (sha256 against
the .sha256 file beside each tar), as the readers do.
  cd src && python -m battery.regress --out ../experiments/BATTERY_shared-test-battery/regression_v1.json"""
import argparse
import io
import json
import math
import pathlib
import sys
import tarfile
import time

import numpy as np

from . import VERSION, guard, legacy, stats

T7 = pathlib.Path("/mnt/t7/smad_next")
EXP = pathlib.Path("/home/narolski/smad-next/experiments")
REF = dict(
    fs1=EXP / "PN1_protocol-network-first-tests/tier_fs/fs.json",
    sp=EXP / "PN1_protocol-network-first-tests/tier_fs/sp.json",
    pr1=EXP / "PR1_protocol-reads-existing-networks/z_read.json",
    gd=EXP / "PR1_protocol-reads-existing-networks/gd_read.json",
    tt1=EXP / "TT1_threshold-transfer-unseen-genuine/tt1_read_fs.json",
    tt1sp=EXP / "TT1_threshold-transfer-unseen-genuine/tt1_read_x_sp.json",
    meds=EXP / "TT1_threshold-transfer-unseen-genuine/tt1_read_meds.json",
    c2p=EXP / "PN1_protocol-network-first-tests/c2p_read.json",
    ab1=EXP / "AB1_protocol-ablation-and-replication/ab1_read.json",
    bd1=EXP / "BD1_blend-difference-attribution/bd1_read.json",
)
TARS = dict(
    gd=T7 / "PR1/results/PR1_GD_pn1fs.tar", tt1=T7 / "TT1/results/TT1_A100_pn1fs_fs.tar",
    tt1sp=T7 / "TT1/results/TT1_pn1fs_sp.tar", meds=T7 / "TT1/results/TT1M_se1d.tar", c2p=T7 / "MS1/c2p/C2P_m1.tar")
_TARCACHE = {}


def verified(tar):
    tar = pathlib.Path(tar)
    if tar in _TARCACHE:
        return _TARCACHE[tar]
    want = (tar.parent / (tar.name + ".sha256")).read_text().split()[0]
    got = legacy.sha(tar)
    assert got == want, f"{tar} sha256 {got} != {want}"
    t = tarfile.open(tar)
    _TARCACHE[tar] = (t, {m.name: m for m in t.getmembers()}, got)
    return _TARCACHE[tar]


def npz(tar, member, keys=("id", "logit")):
    t, ms, _ = verified(tar)
    m = [n for n in ms if n.endswith(member)]
    if not m:
        return None
    assert len(m) == 1, (tar, member, m)
    z = np.load(io.BytesIO(t.extractfile(ms[m[0]]).read()))
    return z


def logits(z):
    return dict(zip([str(i) for i in z["id"]], z["logit"].astype(float).tolist()))


def train_rows(z):
    return [dict(path=p, kind=k, label=int(lb), logit=float(lg))
            for p, k, lb, lg in zip(z["path"].tolist(), z["kind"].tolist(), z["label"].tolist(), z["logit"].tolist())]


def train_kinds(z):
    tr = {}
    for k, v in zip([str(i) for i in z["kind"]], z["logit"].astype(float)):
        tr.setdefault(k, []).append(v)
    return tr


# --------------------------------------------------------------------------- comparison
def same(a, b):
    if isinstance(a, bool) or isinstance(b, bool):
        return a == b
    if isinstance(a, (int, float, np.floating, np.integer)) and isinstance(b, (int, float, np.floating, np.integer)):
        a, b = float(a), float(b)
        return (math.isnan(a) and math.isnan(b)) or a == b
    return a == b


def compare(ref, got, path=""):
    """-> (n_leaves_compared, [mismatch dicts]). Walks every leaf of ref."""
    n, bad = 0, []
    if isinstance(ref, dict):
        if not isinstance(got, dict):
            return 1, [dict(path=path, ref="dict", got=type(got).__name__)]
        for k, v in ref.items():
            if k not in got:
                bad.append(dict(path=f"{path}/{k}", ref="present", got="absent"))
                n += 1
                continue
            a, b = compare(v, got[k], f"{path}/{k}")
            n += a
            bad += b
        return n, bad
    if isinstance(ref, (list, tuple)):
        if not isinstance(got, (list, tuple)) or len(got) != len(ref):
            return 1, [dict(path=path, ref=f"list[{len(ref)}]", got=repr(got)[:80])]
        for i, (x, y) in enumerate(zip(ref, got)):
            a, b = compare(x, y, f"{path}[{i}]")
            n += a
            bad += b
        return n, bad
    if ref is None or got is None:
        return 1, ([] if (ref is None and got is None) else [dict(path=path, ref=ref, got=got)])
    if not same(ref, got):
        d = None
        try:
            d = abs(float(ref) - float(got))
        except (TypeError, ValueError):
            pass
        return 1, [dict(path=path, ref=ref, got=got, abs_diff=d)]
    return 1, []


def jsonable(o):
    return json.loads(json.dumps(o, default=lambda x: x.item() if isinstance(x, np.generic) else x.tolist()))


# --------------------------------------------------------------------------- the networks
def run(only=None):
    R = dict(version=VERSION, started=time.strftime("%Y-%m-%d %H:%M:%S %Z"), comparisons=[], notes=[])
    ref = {k: json.load(open(v)) for k, v in REF.items()}
    R["reference_files"] = {k: dict(path=str(v), sha256=legacy.sha(v)) for k, v in REF.items()}

    def add(net, block, label, ref_rec, got_rec, note=""):
        n, bad = compare(jsonable(ref_rec), jsonable(got_rec))
        R["comparisons"].append(dict(network=net, block=block, reference=label, leaves=n, mismatches=len(bad),
                                     exact=(len(bad) == 0), details=bad[:50], note=note))
        print(f"{net:12s} {block:5s} {label:48s} leaves {n:6d} mismatches {len(bad)}", flush=True)

    fs_rng = None
    tt1 = ref["tt1"]
    # ---- FS1 block of seeds 403-407 (A, B, Sb), in fs_read.py's order: seeds outer, arms inner, one shared stream
    for s in (403, 404, 405, 406, 407):
        for a in ("A", "B", "Sb"):
            n = f"PN1_{a}_s{s}"
            key = f"{a}_s{s}"
            if only and key not in only:
                continue
            tar = T7 / "PN1/results_fs" / f"{n}.tar"
            ev = npz(tar, f"{n}/scores_eval.npz")
            tr = npz(tar, f"{n}/scores_train.npz", None)
            info = json.loads(verified(tar)[0].extractfile(verified(tar)[1][f"{n}/info.json"]).read())
            dev = logits(ev)
            if fs_rng is None:
                fs_rng = stats.fresh_fs1_rng()
            b = stats.block_fs1(dev, rng=fs_rng)
            add(key, "FS1", "fs.json seeds/<s>/<arm>", ref["fs1"]["seeds"][str(s)][a], b["record"],
                "share_ci replayed with fs_read.py's single stream (seed-major order)")
            add(key, "FS1", "fs.json printed_R1_R6/<s>/<arm>", ref["fs1"]["printed_R1_R6"][str(s)][a], b["printed_R1_R6"])
            add(key, "FS1", "fs.json printed_R1_R6/<s>/R3_base,R5", {k: ref["fs1"]["printed_R1_R6"][str(s)][k] for k in ("R3_base", "R5_noise_std_border_auc")},
                {k: b["context"][k] for k in ("R3_base", "R5_noise_std_border_auc")})
            add(key, "PR1", "z_read.json per_net/<arm>_s<seed>", ref["pr1"]["per_net"][key], stats.block_pr1(dev, train_rows(tr), info))
            add(key, "BD1", "bd1_read.json blocks/FS1/per_net", ref["bd1"]["blocks"]["FS1"]["per_net"][key], stats.block_bd1(dev))
            g = {}
            for fam in ("gd0", "gd1", "gd2"):
                g.update(logits(npz(TARS["gd"], f"PR1_GD_pn1fs/scores/{n}__{fam}.npz")))
            gref = {k: v for k, v in ref["gd"]["per_net"][key].items() if k not in ("gate_ok", "finite", "gate")}
            add(key, "GD", "gd_read.json per_net (gd0, gd1, gd2)", gref, stats.block_gd(g, dev))
            if n in tt1["nets"]:
                L = logits(npz(TARS["tt1"], f"scores/{n}__gate.npz")) | logits(npz(TARS["tt1"], f"scores/{n}__tt1.npz"))
                nd = T7 / "TT1/nets_fs" / n
                assert legacy.sha(nd / "scores_eval.npz") == legacy.sha(T7 / "PN1/results_fs/unpacked" / n / "scores_eval.npz")
                add(key, "TT1", "tt1_read_fs.json nets/<net>", tt1["nets"][n], stats.block_tt1(L, nd, nd))
            if n in ref["meds"]["nets"]:
                L = logits(npz(TARS["meds"], f"scores/{n}__gate.npz")) | logits(npz(TARS["meds"], f"scores/{n}__meds.npz"))
                mref = {k: v for k, v in ref["meds"]["nets"][n].items() if k != "_bf"}
                add(key, "MEDS", "tt1_read_meds.json nets/<net>", mref, stats.block_meds(L))
            if key in ref["c2p"]["per_network"]:
                L = logits(npz(TARS["c2p"], f"C2P_{n}_ms1ffhq.npz"))
                add(key, "C2P", "c2p_read.json per_network (L40S rescoring)", ref["c2p"]["per_network"][key], stats.block_c2p(L))
    # ---- Sp 403-405 (FS1 pack, A100): sp_read.py prints, TT1-X, MEDS
    for s in (403, 404, 405):
        n, key = f"PN1_Sp_s{s}", f"Sp_s{s}"
        if only and key not in only:
            continue
        tar = T7 / "PN1/results_fs" / f"{n}.tar"
        dev = logits(npz(tar, f"{n}/scores_eval.npz"))
        b = stats.block_fs1(dev)
        p = stats.block_pr1(dev)
        sp = ref["sp"]["seeds"][str(s)]["Sp"]
        add(key, "FS1", "sp.json seeds/<s>/Sp/R1_R6", sp["R1_R6"], b["printed_R1_R6"])
        add(key, "FS1", "sp.json seeds/<s>/Sp lcomb, storage share",
            dict(lcomb_auc=sp["lcomb_auc"], storage_share_rising=sp["storage_share_rising"]),
            dict(lcomb_auc=b["record"]["lcomb_auc"], storage_share_rising=b["record"]["share_rising"]),
            "sp_read.py's lcomb and share by other code paths; compared to the FS1 block's values")
        add(key, "PR1", "sp.json seeds/<s>/Sp dev S0/S3 flags, S0-vs-S4 AUC",
            dict(dev_S0_flag_own=sp["dev_S0_flag_own"], dev_S3_flag_own=sp["dev_S3_flag_own"], dev_S0_vs_S4_auc=sp["dev_S0_vs_S4_auc"]),
            dict(dev_S0_flag_own=p["pools"]["spl_S0_dev"]["above_own"], dev_S3_flag_own=p["pools"]["spl_S3_dev"]["above_own"],
                 dev_S0_vs_S4_auc=p["auc"]["S4_vs_S0_dev"]),
            "sp_read.py computes these with pn1lib/reads; the battery takes them from the PR1 block")
        if n in ref["tt1sp"]["nets"]:
            L = logits(npz(TARS["tt1sp"], f"scores/{n}__gate.npz")) | logits(npz(TARS["tt1sp"], f"scores/{n}__tt1.npz"))
            nd = T7 / "TT1/nets_fs" / n
            got = stats.block_tt1(L, nd, nd)
            add(key, "TT1", "tt1_read_x_sp.json nets/<net>", ref["tt1sp"]["nets"][n], got)
        if n in ref["meds"]["nets"]:
            L = logits(npz(TARS["meds"], f"scores/{n}__gate.npz")) | logits(npz(TARS["meds"], f"scores/{n}__meds.npz"))
            add(key, "MEDS", "tt1_read_meds.json nets/<net>", {k: v for k, v in ref["meds"]["nets"][n].items() if k != "_bf"},
                stats.block_meds(L))
    # ---- AB1 block (WCSS H100, seeds 408-412): A, B, Sb, Sp (and the leave-one-out arms)
    for arm in ("A", "B", "Sb", "Sp", "SbZ", "SbH", "SbS", "AS"):
        for s in (408, 409, 410, 411, 412):
            n, key = f"AB1_{arm}_s{s}", f"{arm}_s{s}"
            if (only and key not in only) or key not in ref["ab1"]["networks"]:
                continue
            tar = T7 / "AB1/results" / f"{n}.tar"
            ev, tr = npz(tar, f"{n}/scores_eval.npz"), npz(tar, f"{n}/scores_train.npz", None)
            dev = logits(ev)
            add(key, "AB1", "ab1_read.json networks/<arm>_s<seed>", ref["ab1"]["networks"][key], stats.block_ab1(dev, train_kinds(tr)))
            if arm == "Sb":
                add(key, "BD1", "bd1_read.json blocks/AB1/per_net", ref["bd1"]["blocks"]["AB1"]["per_net"][key], stats.block_bd1(dev))
    # ---- SE1 A100 block, Sb 408-411: BD1 replication block
    for s in (408, 409, 410, 411):
        n, key = f"SE1_Sb_s{s}", f"Sb_s{s}"
        if only and key not in only:
            continue
        tar = T7 / "SE1/results" / f"{n}.tar"
        add("SE1 " + key, "BD1", "bd1_read.json blocks/SE1/per_net", ref["bd1"]["blocks"]["SE1"]["per_net"][key],
            stats.block_bd1(logits(npz(tar, f"{n}/scores_eval.npz"))))
    R["tars"] = {str(k): v[2] for k, v in _TARCACHE.items()}
    R["reader_files"] = legacy.loaded_files()
    R["summary"] = dict(comparisons=len(R["comparisons"]), exact=sum(c["exact"] for c in R["comparisons"]),
                        leaves=sum(c["leaves"] for c in R["comparisons"]),
                        mismatching_leaves=sum(c["mismatches"] for c in R["comparisons"]))
    R["finished"] = time.strftime("%Y-%m-%d %H:%M:%S %Z")
    return R


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True)
    ap.add_argument("--only", nargs="*", help="network keys such as Sb_s403 (test runs)")
    a = ap.parse_args()
    guard.self_test()
    guard.install()
    R = run(set(a.only) if a.only else None)
    pathlib.Path(a.out).write_text(json.dumps(R, indent=1, default=lambda x: x.item() if isinstance(x, np.generic) else str(x)))
    print("REGRESSION", json.dumps(R["summary"]))
    sys.exit(0)


if __name__ == "__main__":
    main()
