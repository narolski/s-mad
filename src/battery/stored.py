"""Shared test battery (BATTERY): battery-format records built from STORED logits of already-reviewed networks (no scoring).
Used by the regression test (to print the audit rows through the battery reader and check them against the table) and
never mixed with battery-scored outputs: every record says source = "stored", and the reader shows stored records only
with --include-stored, labelled. Each block names the stored file and platform its logits come from.
  cd src && python -m battery.stored --out /mnt/t7/smad_next/BATTERY/stored"""
import argparse
import json
import pathlib
import time

import numpy as np

from . import VERSION, guard, legacy, rows, stats
from .regress import T7, TARS, logits, npz, train_kinds, train_rows, verified

SRC_FS1 = "FS1 fit job (pn1_score.py, TF32 on), NVIDIA A100-PCIE-40GB, torch 2.2.1"
SRC_TT1 = "TT1-FS rescoring (rescore.py, TF32 off), A100, TT1_A100_pn1fs_fs.tar"
SRC_TT1SP = "TT1-X rescoring (rescore.py, TF32 off), A100, TT1_pn1fs_sp.tar"
SRC_MEDS = "TT1-M rescoring (rescore.py, TF32 off), A100, TT1M_se1d.tar"
SRC_GD = "PR1 GD scoring, PR1_GD_pn1fs.tar"
SRC_C2P = "C2P rescoring (L40S, TF32 off), MS1/c2p/C2P_m1.tar; gate-passed networks only"
SRC_AB1 = "AB1 fit job (pn1_score.py, TF32 on), WCSS NVIDIA H100, torch 2.11.0+cu128"


def write(out, arm, seed, block_name, blocks, sources):
    d = pathlib.Path(out) / f"{arm}_s{seed}_{block_name}"
    d.mkdir(parents=True, exist_ok=True)
    from .run import code_hash
    files, ch = code_hash()
    rec = dict(battery_version=VERSION, battery_code=files, battery_code_sha256=ch, arm=arm, seed=seed, source="stored",
               block_set=block_name, sources=sources,
               created=time.strftime("%Y-%m-%d %H:%M:%S %Z"), platform=dict(key="stored: " + "; ".join(sorted(set(sources.values())))),
               gate=dict(stored_logits=True, note="logits of the registered run; no battery scoring, no battery gate"),
               sets={}, blocks=blocks, rows=rows.extract(blocks), reader_files=legacy.loaded_files())
    (d / "battery.json").write_text(json.dumps(rec, indent=1, default=lambda o: o.item() if isinstance(o, np.generic) else str(o)))
    return d


def nc(why):
    return dict(not_computed=why)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True)
    a = ap.parse_args()
    guard.install()
    ttj = json.load(open(legacy.SRC.parent / "experiments/TT1_threshold-transfer-unseen-genuine/tt1_read_fs.json"))
    mj = json.load(open(legacy.SRC.parent / "experiments/TT1_threshold-transfer-unseen-genuine/tt1_read_meds.json"))
    c2j = json.load(open(legacy.SRC.parent / "experiments/PN1_protocol-network-first-tests/c2p_read.json"))
    spx = json.load(open(legacy.SRC.parent / "experiments/TT1_threshold-transfer-unseen-genuine/tt1_read_x_sp.json"))
    fs_rng = stats.fresh_fs1_rng()
    for s in (403, 404, 405, 406, 407):
        for arm in ("A", "B", "Sb"):
            n, key = f"PN1_{arm}_s{s}", f"{arm}_s{s}"
            tar = T7 / "PN1/results_fs" / f"{n}.tar"
            dev = logits(npz(tar, f"{n}/scores_eval.npz"))
            tr = npz(tar, f"{n}/scores_train.npz", None)
            info = json.loads(verified(tar)[0].extractfile(verified(tar)[1][f"{n}/info.json"]).read())
            B, src = {}, {}
            B["FS1"] = stats.block_fs1(dev, rng=fs_rng); src["FS1"] = SRC_FS1
            B["PR1"] = stats.block_pr1(dev, train_rows(tr), info); src["PR1"] = SRC_FS1
            B["BD1"] = stats.block_bd1(dev); src["BD1"] = SRC_FS1
            B["AB1"] = nc("FS1 networks were not scored on the MS1 hold-out in their fit job")
            g = {}
            for fam in ("gd0", "gd1", "gd2"):
                g.update(logits(npz(TARS["gd"], f"PR1_GD_pn1fs/scores/{n}__{fam}.npz")))
            B["GD"] = stats.block_gd(g, dev); src["GD"] = SRC_GD
            if n in ttj["nets"]:
                L = logits(npz(TARS["tt1"], f"scores/{n}__gate.npz")) | logits(npz(TARS["tt1"], f"scores/{n}__tt1.npz"))
                B["TT1"] = stats.block_tt1(L, T7 / "TT1/nets_fs" / n, T7 / "TT1/nets_fs" / n); src["TT1"] = SRC_TT1
            else:
                B["TT1"] = nc("not in the TT1-FS read (gate)")
            if n in mj["nets"]:
                L = logits(npz(TARS["meds"], f"scores/{n}__gate.npz")) | logits(npz(TARS["meds"], f"scores/{n}__meds.npz"))
                B["MEDS"] = stats.block_meds(L); src["MEDS"] = SRC_MEDS
            else:
                B["MEDS"] = nc("not in the MEDS read (gate)")
            if key in c2j["per_network"]:
                B["C2P"] = stats.block_c2p(logits(npz(TARS["c2p"], f"C2P_{n}_ms1ffhq.npz"))); src["C2P"] = SRC_C2P
            else:
                B["C2P"] = nc("failed the C2P platform gate (L40S); not read")
            print("stored", write(a.out, arm, s, "FS1block", B, src), flush=True)
    for s in (403, 404, 405):
        n = f"PN1_Sp_s{s}"
        tar = T7 / "PN1/results_fs" / f"{n}.tar"
        dev = logits(npz(tar, f"{n}/scores_eval.npz"))
        tr = npz(tar, f"{n}/scores_train.npz", None)
        B, src = {}, {}
        B["FS1"] = stats.block_fs1(dev); src["FS1"] = SRC_FS1
        B["PR1"] = stats.block_pr1(dev, train_rows(tr)); src["PR1"] = SRC_FS1
        B["BD1"] = stats.block_bd1(dev); src["BD1"] = SRC_FS1
        B["AB1"] = nc("not scored on the MS1 hold-out")
        B["C2P"] = nc("not in C2P")
        B["GD"] = nc("Sp was not scored on the GD sets")
        if n in spx["nets"]:
            L = logits(npz(TARS["tt1sp"], f"scores/{n}__gate.npz")) | logits(npz(TARS["tt1sp"], f"scores/{n}__tt1.npz"))
            B["TT1"] = stats.block_tt1(L, T7 / "TT1/nets_fs" / n, T7 / "TT1/nets_fs" / n); src["TT1"] = SRC_TT1SP
        if n in mj["nets"]:
            L = logits(npz(TARS["meds"], f"scores/{n}__gate.npz")) | logits(npz(TARS["meds"], f"scores/{n}__meds.npz"))
            B["MEDS"] = stats.block_meds(L); src["MEDS"] = SRC_MEDS
        print("stored", write(a.out, "Sp", s, "FS1block", B, src), flush=True)
    for arm in ("A", "B", "Sb", "Sp"):
        for s in (408, 409, 410, 411, 412):
            n = f"AB1_{arm}_s{s}"
            tar = T7 / "AB1/results" / f"{n}.tar"
            ev, tr = npz(tar, f"{n}/scores_eval.npz"), npz(tar, f"{n}/scores_train.npz", None)
            dev = logits(ev)
            B = dict(FS1=stats.block_fs1(dev), PR1=stats.block_pr1(dev, train_rows(tr)), AB1=stats.block_ab1(dev, train_kinds(tr)),
                     C2P=stats.block_c2p(dev), BD1=stats.block_bd1(dev), TT1=nc("not scored on TT1 rows"),
                     MEDS=nc("not scored on MEDS"), GD=nc("not scored on GD"))
            print("stored", write(a.out, arm, s, "AB1block", B, {k: SRC_AB1 for k in ("FS1", "PR1", "AB1", "C2P", "BD1")}), flush=True)


if __name__ == "__main__":
    main()
