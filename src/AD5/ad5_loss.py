"""Retrains of released methods (AD5): training-loss fidelity check (prereg amendment 1, item 4). No test data.

Parses the MADation logger lines "Speed ... Loss <x> Epoch: <e>   Global Step: <s>" of the authors' release logs
(runs that reach epoch 39; the release logs hold four runs, runs 2 to 4 are complete) and of every retrain's
training.log, and prints the mean logged loss per epoch. Flag: a retrain whose last-epoch mean loss lies outside
[0.5 x min, 2 x max] of the authors' complete runs.

  python3 -I ad5_loss.py --arm L|B --release-log RELEASE/training.log --retrain NAME=training.log ... --out CSV
"""
import argparse
import csv
import json
import re
from collections import defaultdict

LINE = re.compile(r"Loss ([0-9.]+) Epoch: (\d+)\s+Global Step: (\d+)")


def runs(path):
    """list of runs; a new run starts at every 'Trainset lenght' line; each run: {epoch: [losses]}"""
    out, cur = [], None
    for ln in open(path, errors="replace"):
        if "Trainset lenght" in ln:
            cur = defaultdict(list)
            out.append(cur)
            continue
        m = LINE.search(ln)
        if m and cur is not None:
            cur[int(m.group(2))].append(float(m.group(1)))
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--arm", required=True)
    ap.add_argument("--release-log", required=True)
    ap.add_argument("--retrain", nargs="*", default=[])
    ap.add_argument("--out", required=True)
    a = ap.parse_args()
    authors = [r for r in runs(a.release_log) if max(r, default=-1) == 39]
    rows = []
    for i, r in enumerate(authors):
        for e in sorted(r):
            rows.append(dict(arm=a.arm, network=f"authors_run_{i + 1}_of_{len(authors)}", epoch=e,
                             mean_loss=round(sum(r[e]) / len(r[e]), 5), n=len(r[e])))
    last = [sum(r[39]) / len(r[39]) for r in authors]
    lo, hi = 0.5 * min(last), 2 * max(last)
    flags = {}
    for spec in a.retrain:
        name, path = spec.split("=", 1)
        rr = runs(path)
        r = rr[-1] if rr else {}
        for e in sorted(r):
            rows.append(dict(arm=a.arm, network=name, epoch=e, mean_loss=round(sum(r[e]) / len(r[e]), 5), n=len(r[e])))
        lv = sum(r[39]) / len(r[39]) if 39 in r else None
        flags[name] = dict(last_epoch_mean_loss=lv, outside_authors_range=None if lv is None else not (lo <= lv <= hi))
    with open(a.out, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0]))
        w.writeheader()
        w.writerows(rows)
    print(json.dumps(dict(arm=a.arm, authors_last_epoch_mean_loss=last, range=[lo, hi], retrains=flags), indent=1))


if __name__ == "__main__":
    main()
