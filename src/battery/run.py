"""Shared test battery (BATTERY), the one command: platform record -> platform gate -> score every development set of the
audit rows -> logits + one JSON with every row statistic. Development data only (deny-list guard on every path).

  cd src && python -m battery.run --ckpt NETDIR --arm NAME --seed N --out OUTDIR \
      --code PN1_TREE/code --ref REFERENCE_TAR [--data dev=ROOT[,ROOT2] tt1=ROOT meds=ROOT gd=ROOT] \
      [--sets dev tt1 meds gd] [--train-manifest CSV] [--hf-home DIR] [--workers 7] [--stats auto|yes|no]
  cd src && python -m battery.run --stats-only OUTDIR          (zero-GPU completion of the statistics from saved logits)
  test on 8 rows per set, no gate, output marked TEST (never read):  ... --test-limit 8 --device cpu

NETDIR: meta.json + last_trainable.pt (or train.py's last.pt). REFERENCE_TAR: the pinned reference network of this platform
(gate.REFERENCES), verified by sha256. Exit codes: 0 done; 2 platform gate failed (nothing scored); 3 deny-list; 4 data
missing or off its pin; 5 platform without a pinned reference."""
import argparse
import json
import os
import pathlib
import shutil
import sys
import tarfile
import time

import numpy as np

from . import VERSION, backbones, gate, guard, legacy, rows, sets, stats


def sha(p):
    return legacy.sha(p)


def score_rows(model, C, rs, res, device, bs=gate.BS, workers=7):
    """the fit-job scorer's loop (src/PN1/pn1_score.py score(): common.ImageItems at meta res, batch 64 in list order,
    common.forward_logit, float32 logit without flip). Returns a float32 array in row order."""
    import torch
    from torch.utils.data import DataLoader
    dl = DataLoader(C.ImageItems([(r["abspath"], int(r["label"] or 0)) for r in rs], res, root="/"), batch_size=bs, num_workers=workers)
    lg = []
    with torch.no_grad():
        for x, _ in dl:
            x = x.to(device, non_blocking=True)
            lg += C.forward_logit(model, x)[0].float().cpu().tolist()
    return np.array(lg, np.float32)


def parse_data(items):
    out = {}
    for it in items or []:
        k, v = it.split("=", 1)
        out[k] = v.split(",")
    return out


def die(code, msg):
    print(msg, file=sys.stderr, flush=True)
    print(msg, flush=True)
    sys.exit(code)


def unpack_reference(ref, refspec, work):
    ref = pathlib.Path(ref)
    guard.check_path(ref, "reference")
    got = sha(ref)
    if got != refspec["tar_sha256"]:
        die(4, f"BATTERY: reference tar {ref} sha256 {got[:16]} != pinned {refspec['tar_sha256'][:16]}")
    d = pathlib.Path(work) / "_reference"
    d.mkdir(parents=True, exist_ok=True)
    n = refspec["network"]
    with tarfile.open(ref) as t:
        for f in ("meta.json", "last_trainable.pt", "scores_eval.npz"):
            m = t.getmember(f"{n}/{f}")
            with open(d / f, "wb") as o:
                o.write(t.extractfile(m).read())
    for f, k in (("scores_eval.npz", "scores_eval_sha256"), ("last_trainable.pt", "last_trainable_sha256")):
        if sha(d / f) != refspec[k]:
            die(4, f"BATTERY: reference {f} off its pin")
    return d


def compute_stats(out, rec):
    """all blocks from the logits saved in `out`; returns the blocks dict."""
    L = {}
    for s in sets.ORDER:
        f = out / f"logits_{s}.npz"
        if f.exists():
            z = np.load(f)
            L[s] = dict(zip([str(i) for i in z["id"]], z["logit"].astype(float).tolist()))
    tr, tk = None, None
    if (out / "logits_train.npz").exists():
        z = np.load(out / "logits_train.npz")
        tr = [dict(path=p, kind=k, label=int(lb), logit=float(lg)) for p, k, lb, lg in
              zip(z["path"].tolist(), z["kind"].tolist(), z["label"].tolist(), z["logit"].tolist())]
        tk = {}
        for k, v in zip([str(i) for i in z["kind"]], z["logit"].astype(float)):
            tk.setdefault(k, []).append(v)
    meds = None
    if "meds" in L and "tt1" in L:
        tt1rows = [r for r in __import__("csv").DictReader(open(rec["sets"]["tt1"]["manifest"])) if r["fam"] == "gate"]
        meds = dict(L["meds"]) | {r["id"]: L["tt1"][r["id"]] for r in tt1rows}
    blocks = stats.all_blocks(L.get("dev"), train=tr, train_kinds=tk, tt1=L.get("tt1"), meds=meds, gd=L.get("gd"),
                              netdir=out, scores_eval_dir=out, info=None)
    blocks["FS1_note"] = ("share_ci uses fs_read.py's bootstrap stream at its first position (fs_read.py draws one stream "
                          "for 15 networks in a fixed order); every other number is position-free")
    return blocks


def finish(out, rec, blocks):
    rec["blocks"] = blocks
    rec["rows"] = rows.extract(blocks)
    rec["reader_files"] = legacy.loaded_files()
    rec["finished"] = time.strftime("%Y-%m-%d %H:%M:%S %Z")
    p = out / "battery.json"
    tmp = out / "battery.json.part"
    tmp.write_text(json.dumps(rec, indent=1, default=lambda o: o.item() if isinstance(o, np.generic) else str(o)))
    os.replace(tmp, p)
    print("BATTERY_DONE", p, sha(p), flush=True)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--ckpt")
    ap.add_argument("--arm")
    ap.add_argument("--seed", type=int)
    ap.add_argument("--out", required=False)
    ap.add_argument("--backbone", default="clip_vitb16_lora", choices=sorted(backbones.LOADERS))
    ap.add_argument("--code", default="/mnt/t7/smad_next/PN1/fs_tree/pn1/code")
    ap.add_argument("--hf-home", default=os.environ.get("HF_HOME"))
    ap.add_argument("--ref", help="reference network tar of this platform (gate.REFERENCES)")
    ap.add_argument("--data", nargs="*", help="set=ROOT[,ROOT2] (default: the DGX copies)")
    ap.add_argument("--sets", nargs="*", default=list(sets.ORDER))
    ap.add_argument("--train-manifest", help="the network's training manifest (unique rows scored, as pn1_score.py)")
    ap.add_argument("--workers", type=int, default=7)
    ap.add_argument("--device", default="cuda")
    ap.add_argument("--stats", default="auto", choices=("auto", "yes", "no"))
    ap.add_argument("--stats-only", help="OUTDIR of an earlier run: compute the statistics from its saved logits")
    ap.add_argument("--test-limit", type=int, default=0, help="TEST ONLY: first N rows per set, no gate, output marked TEST")
    ap.add_argument("--test-gate-key", help="TEST ONLY: run the gate of this pinned platform on the present device (expected "
                                            "to fail off that platform); output marked TEST")
    a = ap.parse_args()
    guard.self_test()
    guard.install()
    if a.stats_only:
        out = pathlib.Path(a.stats_only)
        rec = json.load(open(out / "battery.json"))
        if rec.get("test_mode"):
            die(4, "BATTERY: this output is a TEST run; it is never read")
        if not rec.get("gate", {}).get("byte_identical"):
            die(2, "BATTERY: this output has no passed platform gate; statistics are not computed")
        for s, v in rec["sets"].items():
            if sha(out / v["logits_file"]) != v["logits_sha256"]:
                die(4, f"BATTERY: {v['logits_file']} changed since scoring")
        rec["stats_completed_on"] = dict(host=__import__("socket").gethostname(), time=time.strftime("%Y-%m-%d %H:%M:%S %Z"))
        finish(out, rec, compute_stats(out, rec))
        return
    for k in ("ckpt", "arm", "seed", "out"):
        if getattr(a, k) is None:
            ap.error(f"--{k} is required")
    import torch
    torch.backends.cuda.matmul.allow_tf32 = True          # as pn1_score.py (the fit-job scorer); recorded below
    torch.backends.cudnn.allow_tf32 = True
    device = a.device if (a.device == "cpu" or torch.cuda.is_available()) else die(5, "BATTERY: no CUDA device")
    out = pathlib.Path(a.out)
    out.mkdir(parents=True, exist_ok=True)
    if (out / "battery.json").exists():
        die(4, f"BATTERY: {out}/battery.json exists; outputs are never overwritten")
    T0 = time.time()
    plat = gate.record(device)
    gate.dump(plat, out / "platform.json")
    print("BATTERY platform", plat["key"], plat["nvidia_smi"].replace("\n", " | "), flush=True)
    test = a.test_limit > 0 or bool(a.test_gate_key)
    refspec = gate.REFERENCES.get(a.test_gate_key or plat["key"])
    if refspec is None and not test:
        die(5, f"BATTERY PLATFORM REFUSED: no pinned reference network for platform '{plat['key']}'. Pinned platforms: "
               f"{sorted(gate.REFERENCES)}. Nothing was scored.")
    if not backbones.LOADERS[a.backbone]["gate_reference"] and not test:
        die(5, f"BATTERY: backbone {a.backbone} has no pinned gate reference yet (see backbones.py); nothing was scored")
    data = {k: v for k, v in ((s, sets.SETS[s]["default_roots"]) for s in sets.ORDER)} | parse_data(a.data)
    want = ["dev"] + [s for s in a.sets if s != "dev"]
    try:
        S = {s: sets.load(s, data[s]) for s in want}
    except guard.DeniedPath as ex:
        die(3, str(ex))
    except (FileNotFoundError, RuntimeError, AssertionError) as ex:
        die(4, f"BATTERY DATA: {ex}")
    rec = dict(battery_version=VERSION, arm=a.arm, seed=a.seed, created=time.strftime("%Y-%m-%d %H:%M:%S %Z"),
               test_mode=test, platform=plat, command=sys.argv, deny_list=dict(self_test=guard.self_test(),
               tokens=sorted(guard.DENY_TOKENS), substrings=list(guard.DENY_SUB)),
               sets={s: dict(manifest=S[s][1], sha256=S[s][2], n=len(S[s][0]), roots=data[s]) for s in want})
    if test:
        rec["WARNING"] = "TEST RUN (--test-limit): no platform gate, truncated sets; never read, never entered in any table"
    # ---------------- platform gate
    if not test or a.test_gate_key:
        ref = a.ref or next((p for p in refspec["locations"] if os.path.exists(p)), None)
        if ref is None:
            die(4, f"BATTERY: reference tar {refspec['tar']} not found; pass --ref")
        rd = unpack_reference(ref, refspec, out)
        rmodel, rmeta, C, _, rprov = backbones.load(a.backbone, rd, a.code, device, a.hf_home)
        grows = gate.gate_rows(S["dev"][0])
        g = score_rows(rmodel, C, grows, rmeta["res"], device, workers=a.workers)
        z = np.load(rd / "scores_eval.npz")
        G = gate.compare(list(zip([r["id"] for r in grows], g.tolist())), z["id"], z["logit"])
        G.update(reference=refspec, reference_tar=str(ref), reference_provenance=rprov, gate_batches=gate.GATE_BATCHES,
                 seconds=round(time.time() - T0, 1))
        gate.dump(G, out / "gate.json")
        rec["gate"] = G
        del rmodel
        shutil.rmtree(rd)                                  # own temporary copy of the reference files
        if a.test_gate_key:
            rec["WARNING"] = f"TEST RUN (--test-gate-key {a.test_gate_key}): gate of another platform run on {plat['key']}"
        if not G["byte_identical"]:
            rec["status"] = "GATE FAILED: nothing scored"
            gate.dump(rec, out / "battery.json")
            die(2, f"BATTERY PLATFORM GATE FAILED on '{plat['key']}': {G['n_differ']} of {G['n']} reference logits differ "
                   f"(max |dlogit| {G['max_abs']:.3g}, own-rule flips {G['own_rule_flips']}). No row was scored. "
                   f"Do not score this network on this host; report gate.json to the BATTERY owner.")
        print(f"BATTERY gate PASSED: {G['n']} of {G['n']} reference logits byte-identical ({G['seconds']} s)", flush=True)
    else:
        rec["gate"] = dict(skipped="TEST RUN")
    # ---------------- the network
    model, meta, C, trainable, prov = backbones.load(a.backbone, a.ckpt, a.code, device, a.hf_home)
    rec["network"] = prov
    torch.save(trainable, out / "last_trainable.pt")
    shutil.copy(pathlib.Path(a.ckpt) / "meta.json", out / "meta.json")
    for s in want:
        rs = S[s][0][: a.test_limit] if test else S[s][0]
        t0 = time.time()
        lg = score_rows(model, C, rs, meta["res"], device, workers=a.workers)
        f = out / f"logits_{s}.npz"
        np.savez(f, id=np.array([r["id"] for r in rs]), logit=lg, manifest_sha256=S[s][2])
        rec["sets"][s].update(logits_file=f.name, logits_sha256=sha(f), n_scored=len(rs), finite=bool(np.isfinite(lg).all()),
                              seconds=round(time.time() - t0, 1))
        if s == "dev":
            np.savez(out / "scores_eval.npz", id=np.array([r["id"] for r in rs]), logit=lg, manifest_sha256=S[s][2])
        print(f"BATTERY scored {s}: {len(rs)} rows in {rec['sets'][s]['seconds']} s", flush=True)
    if a.train_manifest:
        import csv
        root = pathlib.Path(data["dev"][0])
        seen, tr = set(), []
        for r in csv.DictReader(open(guard.check_path(a.train_manifest, "training manifest"))):
            if r["path"] not in seen:
                seen.add(r["path"])
                tr.append(dict(r, abspath=str(guard.check_path(root / r["path"], "training image"))))
        tr = tr[: a.test_limit] if test else tr
        lt = score_rows(model, C, tr, meta["res"], device, workers=a.workers)
        f = out / "logits_train.npz"
        np.savez(f, path=np.array([r["path"] for r in tr]), logit=lt, label=np.array([int(r["label"]) for r in tr]),
                 kind=np.array([r.get("kind", "") for r in tr]), manifest_sha256=sha(a.train_manifest))
        rec["train"] = dict(manifest=a.train_manifest, sha256=sha(a.train_manifest), n_unique=len(tr), logits_sha256=sha(f))
    rec["scoring_seconds"] = round(time.time() - T0, 1)
    # ---------------- statistics
    if test or a.stats == "no":
        rec["status"] = "scored; statistics not computed" + (" (TEST)" if test else "")
        gate.dump(rec, out / "battery.json")
        print("BATTERY_SCORED", out, flush=True)
        return
    try:
        blocks = compute_stats(out, rec)
    except (FileNotFoundError, OSError) as ex:
        if a.stats == "yes":
            raise
        rec["status"] = (f"scored; statistics deferred (side data not on this host: {ex}). Complete with: "
                         f"cd src && python -m battery.run --stats-only {out}")
        gate.dump(rec, out / "battery.json")
        print("BATTERY_SCORED (statistics deferred)", out, flush=True)
        return
    rec["status"] = "complete"
    finish(out, rec, blocks)


if __name__ == "__main__":
    main()
