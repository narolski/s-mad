"""Signal isolation by paired differences (PD1), DiffAE family: item list of every image used.

Writes /mnt/t7/smad_next/PD1/diffae/lists/items.csv with columns
  id, path, set, arm, rung, block, host, persons (';'-joined), steps, storage, expr, split
sets: tr (training hosts, FERET/FRGC), f256 (FRLL 256 lossless), fr512 (A43 frames + R0/R1 eval frames),
      ev (benchmark cells), smdd (softening pairs), ad1b (mirror mixes, if present).
No image is read or written here except a size check of 8 files per set.
Run: /home/narolski/mambamorph-code/.venv-spark/bin/python -I src/PD1/diffae/pd1_items.py
"""
import csv, hashlib, json, pathlib, sys
from collections import Counter

R = pathlib.Path("/mnt/t7/smad_research")
E123 = R / "diffae-expanded123-v1"
C64 = R / "confirmation64-diffae-v1"
C64A = R / "confirmation64-alignment-v1"
C64P = R / "confirmation64-selection-v2/PLAN.json"
A43 = pathlib.Path("/mnt/t7/smad_heldout/a43")
A41 = pathlib.Path("/mnt/t7/smad_heldout/a41_diffae/data/a41diffae")
MC = pathlib.Path("/home/narolski/mambamorph-code")
EVAL = MC / "smadcvpr_data/manifests/eval.csv"
EVAL_SHA = "86d055d349c63a225893ace30cb3db8b1e9aea4e72350d78152126d7a49d56c9"
A43_MAN = A43 / "data/manifests/a43.csv"
A43_SHA = "ce3a264adb30928d6ae3abfb63619ed4b35fcb0ebb7fcca7e5001b212a5df4b8"
SMDD_O = MC / "smadcvpr_data/train/smdd/os25k_bf_t"
SMDD_E = pathlib.Path("/mnt/t7/smad_heldout/a47/data47/i3/train/smdd_a47e7/os25k_bf_t")
AD1B = pathlib.Path("/mnt/t7/smad_next/AD1b")
OUT = pathlib.Path("/mnt/t7/smad_next/PD1/diffae/lists/items.csv")
EXCLUDE = {"confirm64-feret-F-05": "person A is a val10 subject (prep_train.is_val sha1 rule)"}
BENCH = ("mordiff", "dim_a", "dim_c", "fast_dim", "fast_dim_ode", "greedy_dim", "greedy_dim_s")
COLS = ["id", "path", "set", "arm", "rung", "block", "host", "persons", "steps", "storage", "expr", "split"]


def sha(p):
    return hashlib.sha256(open(p, "rb").read()).hexdigest()


def is_val(s):
    return int(hashlib.sha1(f"smadcvpr:{s}".encode()).hexdigest(), 16) % 10 == 0


def complete(live):
    return {b["block"] for b in json.load(open(live))["blocks"] if b.get("complete_case")}


def train_rows():
    rows = []
    plans = [(E123 / "PLAN.json", complete(E123 / "run/LIVE.json"), lambda b: E123 / "run" / b, lambda b: E123 / "run" / b, "e123"),
             (C64P, complete(C64 / "LIVE.json"), lambda b: C64 / b, lambda b: C64A / b, "c64")]
    for plan, comp, gdir, adir, cohort in plans:
        for b in json.load(open(plan))["blocks"]:
            bid = b["id"]
            if bid not in comp or bid in EXCLUDE:
                continue
            src = b["sources"]
            pers = {k: f"{v['db']}:{v['subject']}" for k, v in src.items()}
            assert pers["a0"] == pers["a1"] and pers["b0"] == pers["b1"] and pers["a0"] != pers["b0"], bid
            assert not any(is_val(v["subject"]) for v in src.values()), bid
            A, B = pers["a0"], pers["b0"]
            g, a = gdir(bid), adir(bid)
            for h in ("a0", "a1", "b0", "b1"):
                p = A if h[0] == "a" else B
                rows.append(dict(id=f"tr|{bid}|{h}", path=str(a / f"{h}-aligned.png"), set="tr", arm="photo", rung="x0", block=bid,
                                 host=f"{bid}|{h}", persons=p, steps="", storage="png256", expr="", split=cohort))
                rec = ("RA" if h[0] == "a" else "RB") + h[1]
                rows.append(dict(id=f"tr|{bid}|{rec}", path=str(g / f"{rec}.png"), set="tr", arm="rec20", rung="x1", block=bid,
                                 host=f"{bid}|{h}", persons=p, steps="20", storage="png256", expr="", split=cohort))
            for s, p, hosts in (("SA", A, "a0;a1"), ("SB", B, "b0;b1")):
                rows.append(dict(id=f"tr|{bid}|{s}", path=str(g / f"{s}.png"), set="tr", arm="self20", rung="x2", block=bid,
                                 host=";".join(f"{bid}|{h}" for h in hosts.split(";")), persons=p, steps="20", storage="png256",
                                 expr="", split=cohort))
            for m, hosts in (("P0", "a0;b0"), ("P1", "a1;b1")):
                rows.append(dict(id=f"tr|{bid}|{m}", path=str(g / f"{m}.png"), set="tr", arm="morph20", rung="x3", block=bid,
                                 host=";".join(f"{bid}|{h}" for h in hosts.split(";")), persons=f"{A};{B}", steps="20",
                                 storage="png256", expr="", split=cohort))
    return rows


def frll_name_persons(name):
    """001_03 -> ['frll:001']; morph_001_03_and_032_03 -> ['frll:001','frll:032']; 001_self -> ['frll:001']."""
    st = pathlib.PurePath(name).stem
    if st.startswith("morph_"):
        p = st.split("_")
        return [f"frll:{p[1]}", f"frll:{p[4]}"], p[2]
    if st.endswith("_self"):
        return [f"frll:{st[:3]}"], "03+08"
    return [f"frll:{st[:3]}"], st[4:6]


def f256_rows():
    rows = []
    spec = [("a256", A41 / "a256/png256", "x0", "", None), ("D20", A43 / "data/a43/gen/D20/png256", "x1", "20", None),
            ("rec100", A41 / "rec/png256", "x1", "100", None), ("C20", A43 / "data/a43/gen/C20/png256", "x2", "20", None),
            ("self100", A41 / "self/png256", "x2", "100", None), ("B20", A43 / "data/a43/gen/B20/png256", "x3", "20", None),
            ("B100", A43 / "data/a43/gen/B/png256", "x3", "100", None)]
    for arm, d, rung, steps, _ in spec:
        for f in sorted(d.glob("*.png")):
            pp, ex = frll_name_persons(f.name)
            host = f"frll|{pp[0][5:]}_{ex[:2]}" if rung != "x2" else f"frll|{pp[0][5:]}_03;frll|{pp[0][5:]}_08"
            rows.append(dict(id=f"f256|{arm}|{f.stem}", path=str(f), set="f256", arm=arm, rung=rung, block="", host=host,
                             persons=";".join(pp), steps=steps, storage="png256", expr=ex, split=""))
    return rows


def fr512_rows():
    assert sha(A43_MAN) == A43_SHA
    rows = []
    for r in csv.DictReader(open(A43_MAN)):
        if r["source"] == "a43":
            arm = r["arm"]
            path = A43 / "data" / r["path"]
        elif r["family"] == "mordiff_bona":
            arm = "R0"
            path = MC / "smadcvpr_data" / r["path"]
        else:
            continue
        name = pathlib.PurePath(r["path"]).name
        pp = [f"frll:{r['src_a'][:3]}"] + ([f"frll:{r['src_b'][:3]}"] if r["src_b"] and arm not in ("C", "C20") else [])
        if arm == "R0":
            pp = [f"frll:{name[:3]}"]
        rung = {"A": "pub", "B": "x3", "B20": "x3", "C": "x2", "C20": "x2", "D": "x1", "D20": "x1", "E": "x0s", "R0": "R0"}[arm]
        ex = r["expr"] if r["expr"] else ("03+08" if arm in ("C", "C20") else name[4:6])
        rows.append(dict(id=f"fr512|{r['id']}", path=str(path), set="fr512", arm=arm, rung=rung, block="",
                         host="", persons=";".join(pp), steps=r["steps"], storage="stored" if arm != "R0" else "frame512",
                         expr=ex, split=""))
    return rows


def ev_rows():
    assert sha(EVAL) == EVAL_SHA
    rows = []
    for r in csv.DictReader(open(EVAL)):
        if r["set"] not in ("mordiff", "dim"):
            continue
        n = pathlib.PurePath(r["path"]).name
        if r["label"] == "0":
            pp = [f"frll:{n[:3]}"]
            ex = n[4:6]
            fam = r["family"] if r["variant"] == "orig" else r["family"]
            arm = f"{fam}|{r['variant']}"
        else:
            st = n
            if st.startswith("morph_"):
                p = st.split("_")
                pp = [f"frll:{p[1]}", f"frll:{p[4]}"]
                ex = p[2]
            else:
                p = st.split("_")
                pp = [f"frll:{p[0]}", f"frll:{p[1]}"]
                ex = ""
            arm = f"{r['family']}|{r['variant']}"
        rows.append(dict(id=f"ev|{r['id']}", path=str(MC / "smadcvpr_data" / r["path"]), set="ev", arm=arm, rung=r["label"], block="",
                         host="", persons=";".join(pp), steps="", storage="frame512", expr=ex, split=r["set"]))
    return rows


def smdd_rows():
    names = sorted((f.name for f in SMDD_E.glob("*.png")), key=lambda n: hashlib.sha256(f"PD1:{n}".encode()).hexdigest())[:1200]
    rows = []
    for k, n in enumerate(names):
        split = "fit" if k < 600 else "test"
        for arm, d in (("orig", SMDD_O), ("e7", SMDD_E)):
            rows.append(dict(id=f"smdd|{arm}|{n[:-4]}", path=str(d / n), set="smdd", arm=arm, rung=arm, block="", host=f"smdd|{n[:-4]}",
                             persons=f"smdd:{n[:-4]}", steps="", storage="png256" if arm == "orig" else "stored80", expr="", split=split))
    return rows


def ad1b_rows():
    rows = []
    for base in (AD1B / "gen", AD1B / "smoke_gen"):
        if (base / "PAF/png256").exists() and any((base / "PAF/png256").glob("*.png")):
            for arm in ("PAF", "D20r"):
                for f in sorted((base / arm / "png256").glob("*.png")):
                    pid = f.stem[:3]
                    rows.append(dict(id=f"ad1b|{arm}|{f.stem}", path=str(f), set="ad1b", arm=arm, rung="xm" if arm == "PAF" else "x1",
                                     block="", host=f"frll|{pid}_03", persons=f"frll:{pid}", steps="20", storage="png256", expr="03",
                                     split=base.name))
            break
    return rows


def main():
    from PIL import Image
    rows = train_rows() + f256_rows() + fr512_rows() + ev_rows() + smdd_rows() + ad1b_rows()
    ids = [r["id"] for r in rows]
    assert len(ids) == len(set(ids)), [k for k, v in Counter(ids).items() if v > 1][:5]
    miss = [r["path"] for r in rows if not pathlib.Path(r["path"]).exists()]
    assert not miss, miss[:5]
    by = {}
    for r in rows:
        by.setdefault((r["set"], r["arm"]), []).append(r)
    for k, v in sorted(by.items()):
        sizes = Counter(Image.open(x["path"]).size for x in v[:8])
        print(k, len(v), dict(sizes))
    OUT.parent.mkdir(parents=True, exist_ok=True)
    with open(OUT, "w", newline="") as f:
        w = csv.DictWriter(f, COLS)
        w.writeheader()
        w.writerows(rows)
    tr = [r for r in rows if r["set"] == "tr"]
    print("training: blocks", len({r["block"] for r in tr}), "persons", len({p for r in tr for p in r["persons"].split(";")}),
          "hosts", len({r["host"] for r in tr if r["rung"] == "x0"}), "excluded", EXCLUDE)
    print("wrote", OUT, len(rows), "sha", sha(OUT))


if __name__ == "__main__":
    main()
