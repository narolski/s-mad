"""Diffusion-autoencoder generation on Athena (DG1), amendment 2: job lists of the add-on (DGX CPU).

Hosts: all 536 set B hosts (AR1 pool.csv), cut into N shards along the partner cycles (the same walk as dg1_lists.py).
Per host (pools AO_*): REC20, SAME20, X20, MIR20 (re-renders), FRESH1_20, FRESH2_20, NOISEX20, SEMX20, NOISES20,
SEMS20, REC100, SAME100, X100, FRESH1_100; dose hosts (union of the 100 production dose hosts and the 191 test-read
hosts of the protocol-network split PN1) also DOSEX<a>_20 and DOSES<a>_20 for alpha 0.1-0.4.
Columns: set,pool,rung,name,src_a,src_b,alpha,steps,host,partner,mode,fresh_k.

usage: python -I dg1_addon_lists.py --pool CSV --pn1-split CSV --prod-jobs DIR --pool-a256 DIR --out DIR [--shards 8]
"""
import argparse
import csv
import hashlib
import json
import pathlib
import sys

COLS = ["set", "pool", "rung", "name", "src_a", "src_b", "alpha", "steps", "host", "partner", "mode", "fresh_k"]
DOSE = (0.1, 0.2, 0.3, 0.4)


def sha(p):
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for b in iter(lambda: f.read(1 << 22), b""):
            h.update(b)
    return h.hexdigest()


def stem(pid):
    db, subj = pid.split(":")
    return f"{db}_{subj}"


def job(pool, rung, name, a, b, alpha, steps, host, partner, mode, k=""):
    return dict(zip(COLS, ["B", pool, rung, name, a, b, alpha, steps, host, partner, mode, k]))


def host_jobs(p, q):
    s, t = stem(p), stem(q)
    H, S, Hf, Q = f"{s}_H", f"{s}_S", f"{s}_H__flip", f"{t}_S"
    xn = f"{s}__{t}.png"
    J = [job("AO_REC20", "REC", f"{s}.png", H, "", "", 20, p, "", "rec"),
         job("AO_SAME20", "SAME", f"{s}.png", H, S, 0.5, 20, p, p, "mix"),
         job("AO_X20", "X", xn, H, Q, 0.5, 20, p, q, "mix"),
         job("AO_MIR20", "MIR", f"{s}.png", H, Hf, 0.5, 20, p, "", "mix"),
         job("AO_FRESH1_20", "FRESH", f"{s}.png", H, "", "", 20, p, "", "fresh", "1"),
         job("AO_FRESH2_20", "FRESH", f"{s}.png", H, "", "", 20, p, "", "fresh", "2"),
         job("AO_NOISEX20", "NOISEX", xn, H, Q, 0.5, 20, p, q, "noise"),
         job("AO_SEMX20", "SEMX", xn, H, Q, 0.5, 20, p, q, "sem"),
         job("AO_NOISES20", "NOISES", f"{s}.png", H, S, 0.5, 20, p, p, "noise"),
         job("AO_SEMS20", "SEMS", f"{s}.png", H, S, 0.5, 20, p, p, "sem"),
         job("AO_REC100", "REC", f"{s}.png", H, "", "", 100, p, "", "rec"),
         job("AO_SAME100", "SAME", f"{s}.png", H, S, 0.5, 100, p, p, "mix"),
         job("AO_X100", "X", xn, H, Q, 0.5, 100, p, q, "mix"),
         job("AO_FRESH1_100", "FRESH", f"{s}.png", H, "", "", 100, p, "", "fresh", "1")]
    return J


def dose_jobs(p, q):
    s, t = stem(p), stem(q)
    J = []
    for al in DOSE:
        J.append(job(f"AO_DOSEX{int(al * 100):02d}_20", "DOSEX", f"{s}__{t}.png", f"{s}_H", f"{t}_S", al, 20, p, q, "mix"))
        J.append(job(f"AO_DOSES{int(al * 100):02d}_20", "DOSES", f"{s}.png", f"{s}_H", f"{s}_S", al, 20, p, p, "mix"))
    return J


def write(path, rows):
    with open(path, "w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=COLS, lineterminator="\n")
        w.writeheader()
        w.writerows(rows)
    return sha(path)


def main():
    ap = argparse.ArgumentParser()
    for k in ("pool", "pn1-split", "prod-jobs", "pool-a256", "out"):
        ap.add_argument("--" + k, required=True)
    ap.add_argument("--shards", type=int, default=8)
    a = ap.parse_args()
    out = pathlib.Path(a.out)
    out.mkdir(parents=True, exist_ok=True)
    by = {r["pid"]: r for r in csv.DictReader(open(a.pool))}
    al = {p.stem for p in pathlib.Path(a.pool_a256).glob("*.png")}
    if any(f"{stem(p)}_{r}" not in al for p in by for r in ("H", "S")):
        sys.exit("aligned pool incomplete")
    split = {r["pid"]: r for r in csv.DictReader(open(a.pn1_split))}
    if set(split) != set(by):
        sys.exit("PN1 split hosts != pool hosts")
    test_read = {p for p, r in split.items() if r["test_read"] == "1"}
    prod_dose = set()
    for f in sorted(pathlib.Path(a.prod_jobs).glob("setB_s*.csv")):
        prod_dose |= {r["host"] for r in csv.DictReader(open(f)) if r["rung"] == "DOSE"}
    dose_hosts = prod_dose | test_read
    order, seen = [], set()
    for p in sorted(by):
        q = p
        while q not in seen:
            seen.add(q)
            order.append(q)
            q = by[q]["B_pid"]
    k = a.shards
    cut = [order[i * len(order) // k:(i + 1) * len(order) // k] for i in range(k)]
    summ = {"pool_sha256": sha(a.pool), "pn1_split_sha256": sha(a.pn1_split), "test_read": len(test_read),
            "prod_dose": len(prod_dose), "dose_hosts": len(dose_hosts), "dose_hosts_test_read_and_prod": len(prod_dose & test_read),
            "shards": {}}
    counts = {}
    for i, hosts in enumerate(cut):
        J = []
        for p in hosts:
            J += host_jobs(p, by[p]["B_pid"])
        for p in hosts:
            if p in dose_hosts:
                J += dose_jobs(p, by[p]["B_pid"])
        enc = {x for j in J for x in (j["src_a"], j["src_b"]) if x}
        f = out / f"addon_s{i}.csv"
        summ["shards"][f.name] = {"hosts": len(hosts), "jobs": len(J), "encodes": len(enc),
                                  "renders20": sum(j["steps"] == 20 for j in J),
                                  "renders100": sum(j["steps"] == 100 for j in J), "sha256": write(f, J)}
        for j in J:
            counts[j["pool"]] = counts.get(j["pool"], 0) + 1
    summ["counts"] = counts
    # the 8-image check: one dose host, one job of every mode, one 100-step render (+ a second fresh draw)
    h = sorted(dose_hosts)[0]
    q = by[h]["B_pid"]
    allj = host_jobs(h, q) + dose_jobs(h, q)
    pick = ["AO_REC20", "AO_X20", "AO_MIR20", "AO_FRESH1_20", "AO_FRESH2_20", "AO_NOISEX20", "AO_SEMS20", "AO_X100",
            "AO_DOSES10_20"]
    summ["test8_sha256"] = write(out / "addon_test8.csv", [j for j in allj if j["pool"] in pick])
    json.dump(summ, open(out / "addon_lists_summary.json", "w"), indent=1)
    print(json.dumps(summ, indent=1))


if __name__ == "__main__":
    main()
