"""Diffusion-autoencoder generation on Athena (DG1): inputs and job lists (DGX CPU; no image operation of its own).

  poolin  --pool CSV --out DIR
          byte-identical copies of the 1,072 FRGC / colorFERET photos of the landmark ladder pool (AR1 pool.csv: H and S
          of every host) named <db>_<subject>_H.png / _S.png, the input folder of DiffAE's align.py (run unchanged)
  lists   --pool CSV --pool-a256 DIR --frll-a256 DIR --a43-pairs CSV --self-pairs CSV --out DIR [--b-shards 4]
          job lists (columns set,pool,rung,name,src_a,src_b,alpha,steps,host,partner):
            eq.csv       equivalence gate: A43 D20 of 001_03..004_03 and A43 B20 of neutral draws 0-3 (20 steps)
            smoke8.csv   8 generated images of both sets (20 and 100 steps) plus 2 genuine-photo writes
            setA.csv     FRLL, 102 persons, neutral: G, REC20/100, MIR20/100, X20/100 (A43 neutral pairs), CONF20/100
            setB_s<k>.csv  FRGC / colorFERET, hosts cut into k shards along the partner cycles: G (H and S), REC20,
                         MIR20, SAME20, X20, DOSE alpha 0.1-0.4 (first 100 hosts by sha1 of the person id)
          plus lists_summary.json (counts, drops, hashes)
"""
import argparse
import csv
import hashlib
import json
import pathlib
import shutil
import sys

COLS = ["set", "pool", "rung", "name", "src_a", "src_b", "alpha", "steps", "host", "partner"]
A43_PAIRS_SHA = "5cce5fcbf9eacb1eae2c4c5e0021c9d00d9f4b345c18bdb9537b4ff2d1d4ea77"
SELF_PAIRS_SHA = "4366459d35ea27940fc471d72cee21dfb8075e5efb4e156119d9d89dfd711650"
DOSE = (0.1, 0.2, 0.3, 0.4)
N_DOSE = 100


def sha(p):
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for b in iter(lambda: f.read(1 << 22), b""):
            h.update(b)
    return h.hexdigest()


def stem(pid):
    db, subj = pid.split(":")
    return f"{db}_{subj}"


def job(set_, pool, rung, name, a, b="", alpha="", steps=20, host="", partner=""):
    return dict(zip(COLS, [set_, pool, rung, name, a, b, alpha, steps, host, partner]))


def write(path, rows):
    with open(path, "w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=COLS, lineterminator="\n")
        w.writeheader()
        w.writerows(rows)
    return sha(path)


def cmd_poolin(a):
    out = pathlib.Path(a.out)
    if out.exists():
        sys.exit(f"{out} exists")
    out.mkdir(parents=True)
    rows = list(csv.DictReader(open(a.pool)))
    n = 0
    for r in rows:
        for role in ("H", "S"):
            dst = out / f"{stem(r['pid'])}_{role}.png"
            shutil.copyfile(r[role], dst)
            if sha(dst) != sha(r[role]):
                sys.exit(f"copy of {r[role]} differs")
            n += 1
    print(json.dumps({"copied": n, "hosts": len(rows), "pool_sha256": sha(a.pool)}))


def cmd_lists(a):
    out = pathlib.Path(a.out)
    out.mkdir(parents=True, exist_ok=True)
    if sha(a.a43_pairs) != A43_PAIRS_SHA or sha(a.self_pairs) != SELF_PAIRS_SHA:
        sys.exit("A43 pair list or X3 self list is not its pinned file")
    frll = {p.stem for p in pathlib.Path(a.frll_a256).glob("*.png")}
    pool_al = {p.stem for p in pathlib.Path(a.pool_a256).glob("*.png")}
    persons = sorted({r["person"] for r in csv.DictReader(open(a.self_pairs))})
    if len(persons) != 102 or any(f"{p}_03" not in frll or f"{p}_08" not in frll for p in persons):
        sys.exit("FRLL a256 incomplete")
    pairs = [r for r in csv.DictReader(open(a.a43_pairs)) if r["expr"] == "03"]
    summ = {"pool_sha256": sha(a.pool), "a43_pairs_sha256": sha(a.a43_pairs), "self_pairs_sha256": sha(a.self_pairs),
            "frll_persons": len(persons), "a43_neutral_pairs": len(pairs)}

    # ---- equivalence gate (A43 D20 and B20 references, 20 steps)
    eq = [job("EQ", "EQ_D20", "REC", f"{p}_03.png", f"{p}_03", host=p) for p in persons[:4]]
    eq += [job("EQ", "EQ_B20", "X", r["name"], r["src_a"], r["src_b"], 0.5, host=r["id_a"], partner=r["id_b"])
           for r in pairs[:4]]
    if [r["draw"] for r in pairs[:4]] != ["0", "1", "2", "3"]:
        sys.exit("first neutral draws are not 0-3")
    summ["eq_sha256"] = write(out / "eq.csv", eq)

    # ---- set A
    A = [job("A", "A_G", "G", f"{p}_03.png", f"{p}_03", steps=0, host=p) for p in persons]
    for st in (20, 100):
        A += [job("A", f"A_REC{st}", "REC", f"{p}_03.png", f"{p}_03", steps=st, host=p) for p in persons]
        A += [job("A", f"A_MIR{st}", "MIR", f"{p}_03.png", f"{p}_03", f"{p}_03__flip", 0.5, st, p) for p in persons]
        A += [job("A", f"A_X{st}", "X", r["name"], r["src_a"], r["src_b"], 0.5, st, r["id_a"], r["id_b"]) for r in pairs]
        A += [job("A", f"A_CONF{st}", "CONF", f"{p}_self.png", f"{p}_03", f"{p}_08", 0.5, st, p, p) for p in persons]
    summ["setA_jobs"] = len(A)
    summ["setA_sha256"] = write(out / "setA.csv", A)

    # ---- set B
    rows = list(csv.DictReader(open(a.pool)))
    by = {r["pid"]: r for r in rows}
    if any(by[r["B_pid"]]["S"] != r["B"] for r in rows):
        sys.exit("a partner photo is not the partner's S photo")
    hok = {p for p in by if f"{stem(p)}_H" in pool_al}
    sok = {p for p in by if f"{stem(p)}_S" in pool_al}
    summ["pool_hosts"] = len(by)
    summ["aligned_H"], summ["aligned_S"] = len(hok), len(sok)
    summ["dropped_H_no_face"] = sorted(set(by) - hok)
    summ["dropped_S_no_face"] = sorted(set(by) - sok)
    order, seen = [], set()
    for p in sorted(by):                      # walk the partner cycles so most partners fall in the host's shard
        q = p
        while q not in seen:
            seen.add(q)
            order.append(q)
            q = by[q]["B_pid"]
    if sorted(order) != sorted(by):
        sys.exit("partner map is not a permutation")
    dose_hosts = set(sorted((p for p in by if p in hok and by[p]["B_pid"] in sok),
                            key=lambda p: hashlib.sha1(p.encode()).hexdigest())[:N_DOSE])
    k = a.b_shards
    cut = [order[i * len(order) // k:(i + 1) * len(order) // k] for i in range(k)]
    summ["setB_shards"] = {}
    counts = {}
    for i, hosts in enumerate(cut):
        B = []
        for p in hosts:
            s = stem(p)
            if p in hok:
                B.append(job("B", "B_G", "G", f"{s}_H.png", f"{s}_H", steps=0, host=p))
            if p in sok:
                B.append(job("B", "B_G", "G", f"{s}_S.png", f"{s}_S", steps=0, host=p))
        for p in hosts:
            if p not in hok:
                continue
            s, q = stem(p), by[p]["B_pid"]
            B.append(job("B", "B_REC20", "REC", f"{s}.png", f"{s}_H", host=p))
            B.append(job("B", "B_MIR20", "MIR", f"{s}.png", f"{s}_H", f"{s}_H__flip", 0.5, 20, p))
            if p in sok:
                B.append(job("B", "B_SAME20", "SAME", f"{s}.png", f"{s}_H", f"{s}_S", 0.5, 20, p, p))
            if q in sok:
                B.append(job("B", "B_X20", "X", f"{s}__{stem(q)}.png", f"{s}_H", f"{stem(q)}_S", 0.5, 20, p, q))
        for al in DOSE:
            for p in hosts:
                if p in dose_hosts:
                    s, q = stem(p), by[p]["B_pid"]
                    B.append(job("B", f"B_DOSE{int(al * 100):02d}_20", "DOSE", f"{s}__{stem(q)}.png", f"{s}_H",
                                 f"{stem(q)}_S", al, 20, p, q))
        f = out / f"setB_s{i}.csv"
        enc = {x for j in B if int(j["steps"]) > 0 for x in (j["src_a"], j["src_b"]) if x}
        summ["setB_shards"][f.name] = {"hosts": len(hosts), "jobs": len(B), "encodes": len(enc),
                                       "renders": sum(int(j["steps"]) > 0 for j in B), "sha256": write(f, B)}
        for j in B:
            counts[j["pool"]] = counts.get(j["pool"], 0) + 1
    summ["setB_counts"] = counts
    summ["dose_hosts"] = len(dose_hosts)

    # ---- the 8-image check (both sets, 20 and 100 steps) + 2 genuine-photo writes
    h = next(p for p in sorted(dose_hosts))
    s, q = stem(h), by[h]["B_pid"]
    r0 = pairs[0]
    sm = [job("A", "A_G", "G", "001_03.png", "001_03", steps=0, host="001"),
          job("A", "A_REC20", "REC", "001_03.png", "001_03", host="001"),
          job("A", "A_MIR100", "MIR", "001_03.png", "001_03", "001_03__flip", 0.5, 100, "001"),
          job("A", "A_CONF20", "CONF", "001_self.png", "001_03", "001_08", 0.5, 20, "001", "001"),
          job("A", "A_X100", "X", r0["name"], r0["src_a"], r0["src_b"], 0.5, 100, r0["id_a"], r0["id_b"]),
          job("B", "B_G", "G", f"{s}_H.png", f"{s}_H", steps=0, host=h),
          job("B", "B_REC20", "REC", f"{s}.png", f"{s}_H", host=h),
          job("B", "B_SAME20", "SAME", f"{s}.png", f"{s}_H", f"{s}_S", 0.5, 20, h, h),
          job("B", "B_X20", "X", f"{s}__{stem(q)}.png", f"{s}_H", f"{stem(q)}_S", 0.5, 20, h, q),
          job("B", "B_DOSE10_20", "DOSE", f"{s}__{stem(q)}.png", f"{s}_H", f"{stem(q)}_S", 0.1, 20, h, q)]
    summ["smoke8_sha256"] = write(out / "smoke8.csv", sm)
    json.dump(summ, open(out / "lists_summary.json", "w"), indent=1)
    print(json.dumps({k: v for k, v in summ.items() if not k.startswith("dropped")}, indent=1))
    print("dropped H", len(summ["dropped_H_no_face"]), "dropped S", len(summ["dropped_S_no_face"]))


def main():
    ap = argparse.ArgumentParser()
    sp = ap.add_subparsers(dest="cmd", required=True)
    p = sp.add_parser("poolin")
    p.add_argument("--pool", required=True)
    p.add_argument("--out", required=True)
    p = sp.add_parser("lists")
    for k in ("pool", "pool-a256", "frll-a256", "a43-pairs", "self-pairs", "out"):
        p.add_argument("--" + k, required=True)
    p.add_argument("--b-shards", type=int, default=4)
    a = ap.parse_args()
    {"poolin": cmd_poolin, "lists": cmd_lists}[a.cmd](a)


if __name__ == "__main__":
    main()
