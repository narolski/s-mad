"""Shared test battery (BATTERY): end-to-end check of the statistics path on battery-format output folders (pre-run review
F6). CPU only, no image opened, no scoring. Two folders are built from STORED logits in exactly the layout battery.run
writes (logits_<set>.npz, logits_train.npz, scores_eval.npz, last_trainable.pt, meta.json, battery.json skeleton), then
run.compute_stats + rows.extract run on them as --stats-only would, and the result is compared with the stored-logit
records of battery.stored (built by calling the blocks directly):
  PN1_A_s403 (A100 FS1 block: dev, train, TT1 and MEDS from their TT1 tars, GD), first in fs_read's stream order, so even
             the storage-share interval must match;
  AB1_Sb_s408 (H100 AB1 block: dev incl. the MS1 hold-out, train).
It also asserts that every statistic path of rows.py resolves to a value wherever its block was computed.
  cd src && python -m battery.e2e --stored /mnt/t7/smad_next/BATTERY/stored --work /mnt/t7/smad_next/BATTERY/e2e --out OUT.json"""
import argparse
import json
import pathlib
import shutil

import numpy as np

from . import guard, rows, run, sets
from .regress import T7, TARS, compare, jsonable, npz, verified


def save(f, ids, lg, man_sha):
    np.savez(f, id=np.array(ids), logit=np.asarray(lg, np.float32), manifest_sha256=man_sha)


def build(work, name, dev, tt1=None, meds=None, gd=None, train=None, netdir=None):
    d = pathlib.Path(work) / name
    if d.exists():
        shutil.rmtree(d)                            # own temporary e2e folder
    d.mkdir(parents=True)
    rec = dict(battery_version="e2e", arm=name, seed=0, sets={}, gate=dict(passed=True, gate_class="e2e (stored logits)"))
    for s, z in (("dev", dev), ("tt1", tt1), ("meds", meds), ("gd", gd)):
        if z is None:
            continue
        ids, lg = z
        save(d / f"logits_{s}.npz", ids, lg, sets.SETS[s]["sha256"])
        man = pathlib.Path(sets.SETS[s]["default_roots"][-1 if s == "dev" else 0]) / "manifests" / sets.SETS[s]["manifest"]
        rec["sets"][s] = dict(manifest=str(man), logits_file=f"logits_{s}.npz")
    save(d / "scores_eval.npz", dev[0], dev[1], sets.SETS["dev"]["sha256"])
    if train is not None:
        np.savez(d / "logits_train.npz", path=train["path"], logit=train["logit"], label=train["label"], kind=train["kind"])
    for f in ("last_trainable.pt", "meta.json"):
        shutil.copy(pathlib.Path(netdir) / f, d / f)
    return d, rec


def check_paths(blocks):
    """every rows.py path resolves to a non-None value where its block was computed."""
    miss = []
    for rid, spec in rows.ROWS.items():
        for label, blk, paths in spec["stats"]:
            b = blocks.get(blk) or {}
            if "not_computed" in b:
                continue
            for p in (paths if isinstance(paths, list) else [paths]):
                if rows.get(b, p) is None:
                    miss.append(f"row {rid} {blk}:{p}")
    return miss


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--stored", required=True)
    ap.add_argument("--work", required=True)
    ap.add_argument("--out", required=True)
    a = ap.parse_args()
    guard.install()
    R = dict(cases={})
    # --- case 1: PN1_A_s403, FS1 block (A100)
    n = "PN1_A_s403"
    tar = T7 / "PN1/results_fs" / f"{n}.tar"
    ev, tr = npz(tar, f"{n}/scores_eval.npz"), npz(tar, f"{n}/scores_train.npz", None)
    g1, t1 = npz(TARS["tt1"], f"scores/{n}__gate.npz"), npz(TARS["tt1"], f"scores/{n}__tt1.npz")
    tt1 = (list(g1["id"]) + list(t1["id"]), np.r_[g1["logit"], t1["logit"]])
    m1 = npz(TARS["meds"], f"scores/{n}__meds.npz")
    gd = [npz(TARS["gd"], f"PR1_GD_pn1fs/scores/{n}__{f}.npz") for f in ("gd0", "gd1", "gd2")]
    gdz = (sum((list(z["id"]) for z in gd), []), np.concatenate([z["logit"] for z in gd]))
    d1, rec1 = build(a.work, n, (list(ev["id"]), ev["logit"]), tt1, (list(m1["id"]), m1["logit"]), gdz,
                     {k: tr[k] for k in ("path", "logit", "label", "kind")}, T7 / "TT1/nets_fs" / n)
    # --- case 2: AB1_Sb_s408, AB1 block (H100)
    n2 = "AB1_Sb_s408"
    tar2 = T7 / "AB1/results" / f"{n2}.tar"
    ev2, tr2 = npz(tar2, f"{n2}/scores_eval.npz"), npz(tar2, f"{n2}/scores_train.npz", None)
    nd2 = pathlib.Path(a.work) / "_net_AB1_Sb_s408"
    nd2.mkdir(parents=True, exist_ok=True)
    t, ms, _ = verified(tar2)
    for f in ("last_trainable.pt", "meta.json"):
        (nd2 / f).write_bytes(t.extractfile(ms[f"{n2}/{f}"]).read())
    d2, rec2 = build(a.work, n2, (list(ev2["id"]), ev2["logit"]), train={k: tr2[k] for k in ("path", "logit", "label", "kind")}, netdir=nd2)
    for name, d, rec, ref in ((n, d1, rec1, "A_s403_FS1block"), (n2, d2, rec2, "Sb_s408_AB1block")):
        blocks = run.compute_stats(d, rec)
        rws = rows.extract(blocks)
        st = json.load(open(pathlib.Path(a.stored) / ref / "battery.json"))
        nr, badr = compare(jsonable(st["rows"]), jsonable(rws))
        sb = {k: v for k, v in st["blocks"].items()}
        nb, badb = compare(jsonable(sb), jsonable({k: blocks[k] for k in sb if k in blocks}))
        miss = check_paths(blocks)
        R["cases"][name] = dict(stored_record=ref, rows_leaves=nr, rows_differ=len(badr), rows_details=badr[:30],
                                blocks_leaves=nb, blocks_differ=len(badb), blocks_details=badb[:30],
                                unresolved_row_paths=miss, computed_blocks=sorted(k for k, v in blocks.items()
                                                                                  if isinstance(v, dict) and "not_computed" not in v))
        print(name, "rows", nr, "differ", len(badr), "| blocks", nb, "differ", len(badb), "| unresolved paths", miss, flush=True)
        for b in badb[:10]:
            print("   ", b)
    R["union_unresolved"] = sorted(set(R["cases"][n]["unresolved_row_paths"]) & set(R["cases"][n2]["unresolved_row_paths"]))
    pathlib.Path(a.out).write_text(json.dumps(R, indent=1, default=str))
    print("E2E", json.dumps({k: (v["rows_differ"], v["blocks_differ"], len(v["unresolved_row_paths"])) for k, v in R["cases"].items()}))


if __name__ == "__main__":
    main()
