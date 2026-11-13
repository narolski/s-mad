"""Sealed MAD22 read (FINAL), END-TO-END TEST ONLY: run final_read.py on the stand-in B result tar (FFHQ development
frames under MAD22-like names; stand-in networks), with a synthetic release file built for the stand-in manifest, to
check that the real remote's result format reads end to end. Never used on the read's result.
  python3 -I e2e_read_standin.py --e2e /mnt/t7/smad_next/FINAL/e2e"""
import argparse
import hashlib
import json
import pathlib
import subprocess
import sys

import numpy as np

HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import mock_test as MT  # noqa: E402


def sha(p):
    return hashlib.sha256(pathlib.Path(p).read_bytes()).hexdigest()


def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--e2e", required=True); ap.add_argument("--tag", default="B")
    a = ap.parse_args()
    E = pathlib.Path(a.e2e)
    cfg = json.load(open(E / f"standin_config_{a.tag}.json"))
    pack = E / f"{cfg['read_id']}_pack.tar"
    man = MT.manifest(pack)
    L = MT.latent(man, 5)
    w = E / f"read_{a.tag}"; w.mkdir(exist_ok=True)
    rel = w / "rel.npz"; MT.release_npz(man, L, rel, "comparable")
    thr = json.load(open(HERE.parent.parent / "experiments/FINAL_sealed-benchmark-read/final_thresholds.json"))
    (w / "thr.json").write_text(json.dumps(thr))
    res = [p for p in sorted((E / "results").glob(f"{cfg['read_id']}_*.tar")) if "_dryrun" not in p.name][0]
    pins = dict(config=cfg, pack=sha(pack), release_existing=sha(rel), thresholds=sha(w / "thr.json"))
    (w / "pins.json").write_text(json.dumps(pins))
    cmd = [sys.executable, "-I", str(HERE / "final_read.py"), "--result", str(res), "--pack", str(pack),
           "--release-existing", str(rel), "--thresholds", str(w / "thr.json"), "--pins", str(w / "pins.json"),
           "--out", str(w / "read.json"), "--tables", str(w / "tables.md"), "--marker", str(w / "marker")]
    p = subprocess.run(cmd, capture_output=True, text=True)
    print(p.stdout[-500:], p.stderr[-2000:])
    o = json.load(open(w / "read.json"))
    print("E2E_READ outcome", o["outcome"], "rc", o["rc"], "gate all_pass", o["gate"]["all_pass"],
          "cells", {f: len(o["cells"][f]) for f in o["cells"]})


if __name__ == "__main__":
    main()
