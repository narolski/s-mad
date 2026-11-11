"""PN1 tier 1: training manifests A, B, C and the evaluation manifest (prereg sections 4, 6 and amendment 1).
  python3 -I mkmanifests.py sources      # -> /mnt/t7/smad_next/PN1/manifests/src_{A,B}.csv (unique images, kind) and
                                         #    lists/jpeg_sel.csv (amendment 1 selection over B)
  python3 -I mkmanifests.py final        # after jpeg_c.py build: train_A/B/C.csv (balanced rows), pn1_eval.csv,
                                         #    pack_files.csv (pack path -> source file), manifests_summary.json
Training rows carry source=smdd (regime d0 keeps every row once; A47 I-3 / AD4 convention), label 0 = negative,
1 = attack; extra columns (id, kind) are ignored by train.py. Pack paths: train/<kind>/<id>.png, eval/pn1/<id>.png,
and eval/{frllm,mad22c}/... (the AD4 evaluation files, same relative paths as the AD4 pack).
"""
import collections
import csv
import hashlib
import json
import pathlib
import sys

import numpy as np

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import pn1lib as K  # noqa: E402

M = K.PN1 / "manifests"
AD4X = pathlib.Path("/mnt/t7/smad_next/AD4/test/work/task_AD4_m3mf_s401/ad4")
TRCOLS = ["path", "label", "source", "tool", "arm", "val", "mixed", "id", "kind", "db", "hist"]


def soft_rows():
    """AF0's softened training list (built by AF0's soften.py; only rows whose file exists and whose source is a kept
    training image): -> list of catalogue-like rows."""
    f = K.AF0 / "soft_soft_src.csv"
    if not f.exists():
        return []
    src = {r["id"]: r for r in K.read(K.AF0 / "lists" / "soft_src.csv")}
    out = []
    for r in K.read(f):
        if r["path"] and pathlib.Path(r["path"]).exists():
            s0 = dict(src[r["src_id"]])
            s0.update(id=f"{r['src_id']}_{r['strength']}", path=r["path"], rung=f"{s0['rung']}_soft_{r['strength']}")
            out.append(s0)
    return out


def db_of(r):
    """database of a training image: AF0 / SM1-half ids carry it (train_<db>_..., sm1h_<db>_...); ladder rows: pool."""
    i = r["id"]
    if i.startswith(("train_", "sm1h_")):
        d = i.split("_")[1]
    else:
        d = r["pool"].split("_")[1]
    assert d in ("frgc", "feret"), r
    return d


def draw_bn(rowsB, nneg, natt, seed=20261121):
    """amendment 4 item 3: within kinds, in proportion to B's kind counts, A's unique counts per class."""
    rng = np.random.default_rng(seed)
    out = []
    for lab, n in (("0", nneg), ("1", natt)):
        rs = [r for r in rowsB if r["label"] == lab]
        kinds = sorted({r["kind"] for r in rs})
        cnt = {k: sum(1 for r in rs if r["kind"] == k) for k in kinds}
        quota = {k: n * cnt[k] / len(rs) for k in kinds}
        take = {k: int(np.floor(q)) for k, q in quota.items()}
        for k in sorted(kinds, key=lambda k: -(quota[k] - take[k]))[: n - sum(take.values())]:
            take[k] += 1
        for k in kinds:
            ks = [r for r in rs if r["kind"] == k]
            out += [ks[i] for i in sorted(rng.permutation(len(ks))[: take[k]])]
    return out


def sources():
    lad, af = K.split_tables()
    cat = K.catalog()
    by = collections.defaultdict(list)
    for r in cat:
        if r["role"] != "train":
            continue
        if r["fam"] == "af0" and r["strength"] == "":
            if r["rung"] == "photo":
                by["af0_photo"].append(r)
            elif r["rung"] == "u50":
                by["af0_u50"].append(r)
            elif r["rung"] == "zero":
                by["af0_zero"].append(r)
            elif r["rung"] in ("halfA", "halfB") and r["field"] == "u50":
                by["af0_half"].append(r)
        if r["fam"] == "ladder" and r["strength"] == "":
            h = lad[r["host"]]
            if r["rung"] == "R0" and h["train_genuine"] == "1":
                by["lad_R0"].append(r)
            elif r["rung"] == "R2w" and r["tool"] == "opencv" and h["train_genuine"] == "1":
                by["lad_R2w"].append(r)
            elif r["rung"] == "R4" and r["tool"] == "opencv" and h["train_morph"] == "1":
                by["lad_R4"].append(r)
    for r in K.read(K.PN1 / "lists" / "ar1h.csv"):
        by["lad_half"].append(dict(id=r["id"], path=r["path"], persons=(r["p1"], r["p2"])))
    # AF0 61.2 px copies of kept training images
    kept = {r["id"] for k in ("af0_photo", "af0_u50", "af0_half") for r in by[k]}
    for r in soft_rows():
        src_id = r["id"].rsplit("_", 1)[0]
        if r["rung"].endswith("_soft_fm61") and src_id in kept:
            base = r["rung"].split("_soft_")[0]
            kind = {"photo": "af0_photo61", "u50": "af0_u5061", "halfA": "af0_half61", "halfB": "af0_half61"}[base]
            by[kind].append(dict(id=r["id"], path=r["path"]))
    A = [("af0_photo", 0), ("lad_R0", 0), ("af0_u50", 1), ("lad_R4", 1)]
    B = A + [("af0_zero", 0), ("af0_half", 0), ("lad_R2w", 0), ("lad_half", 0), ("af0_photo61", 0),
             ("af0_half61", 0), ("af0_u5061", 1)]
    M.mkdir(parents=True, exist_ok=True)
    summ = {"kinds": {k: len(v) for k, v in sorted(by.items())}}
    for name, spec in (("A", A), ("B", B)):
        rows = [dict(id=r["id"], src=r["path"], kind=k, label=lab, db=db_of(r), hist="s61" if k.endswith("61") else "native")
                for k, lab in spec for r in by[k]]
        ids = [r["id"] for r in rows]
        assert len(ids) == len(set(ids)), f"duplicate ids in {name}"
        with open(M / f"src_{name}.csv", "w", newline="") as f:
            w = csv.DictWriter(f, fieldnames=["id", "src", "kind", "label", "db", "hist"])
            w.writeheader()
            w.writerows(rows)
        summ[name] = dict(n=len(rows), by_label=dict(collections.Counter(r["label"] for r in rows)),
                          by_kind=dict(collections.Counter(r["kind"] for r in rows)), sha256=K.sha(M / f"src_{name}.csv"))
    rowsA = list(csv.DictReader(open(M / "src_A.csv")))
    rowsB0 = list(csv.DictReader(open(M / "src_B.csv")))
    bn = draw_bn(rowsB0, sum(r["label"] == "0" for r in rowsA), sum(r["label"] == "1" for r in rowsA))
    with open(M / "src_Bn.csv", "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=["id", "src", "kind", "label", "db", "hist"])
        w.writeheader()
        w.writerows(bn)
    summ["Bn"] = dict(n=len(bn), by_label=dict(collections.Counter(r["label"] for r in bn)),
                      by_kind=dict(collections.Counter(r["kind"] for r in bn)), sha256=K.sha(M / "src_Bn.csv"))
    # amendment 1 selection over B: 50% of each kind, half jpeg90 half jpeg70
    rng = np.random.default_rng(20261119)
    sel = []
    rowsB = list(csv.DictReader(open(M / "src_B.csv")))
    for k in sorted({r["kind"] for r in rowsB}):
        rs = [r for r in rowsB if r["kind"] == k]
        pick = rng.permutation(len(rs))[: len(rs) // 2]
        ops = rng.permutation(np.r_[np.zeros(len(pick) // 2, int), np.ones(len(pick) - len(pick) // 2, int)])
        for i, o in zip(pick, ops):
            sel.append(dict(id=rs[i]["id"], path=rs[i]["src"], kind=k, label=rs[i]["label"],
                            op=("jpeg90", "jpeg70")[o]))
    with open(K.PN1 / "lists" / "jpeg_sel.csv", "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=["id", "path", "kind", "label", "op"])
        w.writeheader()
        w.writerows(sel)
    summ["jpeg_sel"] = dict(n=len(sel), by_op=dict(collections.Counter(r["op"] for r in sel)),
                            sha256=K.sha(K.PN1 / "lists" / "jpeg_sel.csv"))
    K.dump(summ, M / "sources_summary.json")
    print(json.dumps(summ, indent=1))


def balanced(rows, seed=20261111):
    """repeat the smaller class's rows (each row floor(r) or ceil(r) times) so both labels have equal counts."""
    n0 = [r for r in rows if r["label"] == "0"]
    n1 = [r for r in rows if r["label"] == "1"]
    small, big = (n0, n1) if len(n0) < len(n1) else (n1, n0)
    q, rem = divmod(len(big), len(small))
    rng = np.random.default_rng(seed)
    extra = set(rng.permutation(len(small))[:rem].tolist())
    out = list(big)
    for i, r in enumerate(small):
        out += [r] * (q + (1 if i in extra else 0))
    assert sum(r["label"] == "0" for r in out) == sum(r["label"] == "1" for r in out)
    return out, q + (rem > 0) * 0, rem


def balanced_strata(rows):
    """amendment 4 item 1: the class balance inside each stratum of database x storage history."""
    out, rep = [], {}
    strata = sorted({(r["db"], r["hist"]) for r in rows})
    for i, st in enumerate(strata):
        rs = [r for r in rows if (r["db"], r["hist"]) == st]
        n0, n1 = sum(r["label"] == "0" for r in rs), sum(r["label"] == "1" for r in rs)
        if n0 == 0 or n1 == 0:
            raise SystemExit(f"stratum {st} has one class only ({n0}, {n1})")
        b, q, rem = balanced(rs, seed=20261111 + i)
        out += b
        rep["|".join(st)] = dict(unique_neg=n0, unique_att=n1, rows=len(b))
    return out, rep


def final():
    files = {}           # pack path -> source file
    summ = {}
    jb = {r["src_id"]: r for r in csv.DictReader(open(K.PN1 / "jpeg_build.csv"))} if (K.PN1 / "jpeg_build.csv").exists() \
        else {}
    for name in ("A", "B", "Bn", "C"):
        base = "B" if name == "C" else name
        src = list(csv.DictReader(open(M / f"src_{base}.csv")))
        if name == "C":
            if not jb:
                print("no jpeg_build.csv: manifest C not written")
                continue
            sel = list(csv.DictReader(open(K.PN1 / "lists" / "jpeg_sel.csv")))
            assert all(r["id"] in jb for r in sel), "JPEG copies missing"
            hb = {r["id"]: r for r in src}
            src = src + [dict(id=f"{r['id']}_{r['op']}", src=jb[r["id"]]["path"], kind=r["kind"] + "_" + r["op"],
                              label=r["label"], db=hb[r["id"]]["db"], hist=hb[r["id"]]["hist"] + "_" + r["op"])
                         for r in sel]
        rows = []
        for r in src:
            pp = f"train/{r['kind']}/{r['id']}.png"
            assert files.get(pp, r["src"]) == r["src"]
            files[pp] = r["src"]
            rows.append(dict(path=pp, label=r["label"], source="smdd", tool="smdd", arm="smdd", val="0", mixed="0",
                             id=r["id"], kind=r["kind"], db=r["db"], hist=r["hist"]))
        bal, strata = balanced_strata(rows)
        with open(M / f"train_{name}.csv", "w", newline="") as f:
            w = csv.DictWriter(f, fieldnames=TRCOLS)
            w.writeheader()
            w.writerows(bal)
        summ[name] = dict(unique_images=len(rows), unique_by_label=dict(collections.Counter(r["label"] for r in rows)),
                          rows=len(bal), rows_per_label=len(bal) // 2, strata=strata,
                          by_kind=dict(collections.Counter(r["kind"] for r in rows)),
                          draws_per_row_6250x256=round(6250 * 256 / len(bal), 1), sha256=K.sha(M / f"train_{name}.csv"))
    # evaluation manifest
    ev = []
    cat = K.catalog()
    for r in cat:
        if r["role"] in ("test", "dev") or (r["fam"] == "h1") or (r["src"] == "frll_e5"):
            pp = f"eval/pn1/{r['id']}.png"
            files[pp] = r["path"]
            ev.append(dict(id=r["id"], path=pp, label="1" if r["klass"] == "attack" else "0", klass=r["klass"],
                           role=r["role"], fam=r["fam"], rung=r["rung"], strength=r["strength"], tool=r["tool"],
                           cell=r["cell"], host=r["host"], neutral=r["neutral"]))
    for r in csv.DictReader(open(AD4X / "data" / "manifests" / "ad4_eval.csv")):
        if r["set"] not in ("frllm", "mad22c"):
            continue
        files[r["path"]] = str(AD4X / "data" / r["path"])
        k = "attack" if r["label"] == "1" else "genuine"
        neutral = None
        if k == "genuine" and r["set"] == "frllm":
            neutral = pathlib.Path(r["path"]).name.split("_")[1] == "03"
        ev.append(dict(id="ad4_" + r["id"], path=r["path"], label=r["label"], klass=k, role="bench", fam="bench",
                       rung=r["variant"], strength="", tool=r["family"], cell=f"{r['set']}_{r['family']}", host="",
                       neutral=neutral))
    ids = [r["id"] for r in ev]
    assert len(ids) == len(set(ids))
    with open(M / "pn1_eval.csv", "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(ev[0].keys()))
        w.writeheader()
        w.writerows(ev)
    summ["eval"] = dict(n=len(ev), by=dict(collections.Counter(f"{r['role']}/{r['klass']}" for r in ev)),
                        sha256=K.sha(M / "pn1_eval.csv"))
    with open(M / "pack_files.csv", "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["pack_path", "source"])
        for k in sorted(files):
            assert not any(x in files[k].lower() for x in K.FORBID)
            w.writerow([k, files[k]])
    summ["pack_files"] = len(files)
    K.dump(summ, M / "manifests_summary.json")
    print(json.dumps(summ, indent=1))


if __name__ == "__main__":
    if not sys.flags.isolated:
        sys.exit("run with python3 -I")
    {"sources": sources, "final": final}[sys.argv[1]]()
