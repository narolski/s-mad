"""PN1 extraction / scoring lists in the AF0 list format (id,path,set,cell,rung,tool,p1,p2,geom,g1,g2,w1).
  python3 -I lists.py r2w4 | frll_e5 | devsoft | ladsoft
r2w4    : AR1 warp-only toward the two-person mean shape (R2w4), both tools, 536 hosts (AR1 manifest_extra2.csv)
frll_e5 : the 204 FRLL genuine photos in the registered benign variants jpeg90, jpeg70, jpeg50, blur1, resample50
          (smadcvpr_data/manifests/eval.csv, set frllm, label 0, variants as named; existing files, evaluation only)
devsoft : PN1's stored-small copies of the development camera photos (soften_dev.py output)
ladsoft : the AF0 owner's stored-small copies of the ladder's OpenCV-style two-person (R4) and same-person (R3)
          morphs, when they exist (looked up under /mnt/t7/smad_next/AF0/img/soft/ and its lists; never built here)
"""
import csv
import hashlib
import pathlib
import sys

OUT = pathlib.Path("/mnt/t7/smad_next/PN1/lists")
AR1 = pathlib.Path("/mnt/t7/smad_next/AR1")
EVAL = pathlib.Path("/home/narolski/mambamorph-code/smadcvpr_data/manifests/eval.csv")
EVAL_ROOT = pathlib.Path("/home/narolski/mambamorph-code/smadcvpr_data")
FIELDS = ["id", "path", "set", "cell", "rung", "tool", "p1", "p2", "geom", "g1", "g2", "w1"]
FORBID = ("fst", "valx", "a12sp", "a12-sp")
SPLIT = pathlib.Path("/home/narolski/smad-next/experiments/PN1_protocol-network-first-tests/split")


def write(name, rows):
    OUT.mkdir(parents=True, exist_ok=True)
    for r in rows:
        assert not any(f in r["path"].lower() for f in FORBID), r["path"]
    f = OUT / f"{name}.csv"
    with open(f, "w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=FIELDS)
        w.writeheader()
        for r in rows:
            w.writerow({k: r.get(k, "") for k in FIELDS})
    print(name, len(rows), hashlib.sha256(f.read_bytes()).hexdigest())


def main(which):
    rows = []
    if which == "r2w4":
        for r in csv.DictReader(open(AR1 / "manifest_extra2.csv")):
            assert r["rung"] == "R2w4" and r["pool"] == "frgcferet"
            rows.append(dict(id="ar1_" + r["id"], path=r["path"], set="ar1", cell="frgcferet", rung="R2w4",
                             tool=r["tool"], p1=r["p1"], p2=r["p2"], geom="tem", g1=r["tem1"], g2=r["tem2"],
                             w1=r["w1"]))
    elif which == "frll_e5":
        for r in csv.DictReader(open(EVAL)):
            if r["set"] == "frllm" and r["label"] == "0" and r["variant"] in (
                    "jpeg90", "jpeg70", "jpeg50", "blur1", "resample50"):
                pid = "frll:" + pathlib.Path(r["path"]).name[:3]
                rows.append(dict(id="frllm_" + r["id"], path=str(EVAL_ROOT / r["path"]), set="bench",
                                 cell="frllm_frll_bona", rung=r["variant"], tool="frll_bona", p1=pid, p2=pid,
                                 geom="fixed"))
    elif which == "devsoft":
        src = {r["id"]: r for r in csv.DictReader(open(OUT / "devsoft_src.csv"))}
        for r in csv.DictReader(open(OUT.parent / "soft_devsoft_src.csv")):
            if not r["path"]:
                continue
            s0 = dict(src[r["src_id"]])
            s0.update(id=f"{r['src_id']}_{r['strength']}", path=r["path"],
                      rung=f"{s0['rung']}_soft_{r['strength']}", set="devsoft")
            rows.append(s0)
    elif which == "ladsoft":    # AF0 owner's stored copies of the ladder morphs (R4, R3, R3m; OpenCV-style), read only
        A0 = pathlib.Path("/mnt/t7/smad_next/AF0")
        src = {r["id"]: r for r in csv.DictReader(open(A0 / "lists" / "ladsoft_src.csv"))}
        seen = set()
        for f in ("soft_ladsoft_src.csv", "soft_ladsoft_src_rev.csv"):
            for r in csv.DictReader(open(A0 / f)):
                k = (r["src_id"], r["strength"])
                if not r["path"] or k in seen or not pathlib.Path(r["path"]).exists():
                    continue
                seen.add(k)
                s0 = dict(src[r["src_id"]])
                s0.update(id=f"{r['src_id']}_{r['strength']}", path=r["path"],
                          rung=f"{s0['rung']}_soft_{r['strength']}", set="ladsoft")
                rows.append(s0)
        rows.sort(key=lambda r: r["id"])
    elif which == "ar1h":       # SMDD-rebuild owner's warped halves of the ladder OpenCV morphs (R4), ladder training hosts
        lad = {r["pid"]: r for r in csv.DictReader(open(SPLIT / "ladder_split.csv"))}
        H = pathlib.Path("/mnt/t7/smad_next/SM1/img/ar1h")
        for pid, r in sorted(lad.items()):
            if r["train_morph"] != "1":
                continue
            stem = pid.replace(":", "_")
            for h in ("hA", "hB"):
                p = H / f"{stem}_{h}.png"
                assert p.exists(), p
                rows.append(dict(id=f"sm1h_{stem}_{h}", path=str(p), set="ar1h", cell="frgcferet",
                                 rung="halfA" if h == "hA" else "halfB", tool="opencv", p1=pid, p2=r["partner_B"],
                                 geom=""))
    elif which in ("cert_a", "cert_b"):   # certificate cue lists: (a) training pools and ladder; (b) benchmarks, H1
        sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
        import pn1lib as K
        cat = [r for r in K.catalog() if r["role"] != "excluded"]
        if which == "cert_a":
            rows = [dict(id=r["id"], path=r["path"]) for r in cat if r["fam"] in ("af0", "ladder")]
            rows += [dict(id=r["id"], path=r["path"]) for r in csv.DictReader(open(OUT / "ar1h.csv"))]
        else:
            rows = [dict(id=r["id"], path=r["path"]) for r in cat if r["fam"] in ("h1", "bench")]
    else:
        sys.exit(f"unknown list {which}")
    write(which, rows)


if __name__ == "__main__":
    if not sys.flags.isolated:
        sys.exit("run with python3 -I")
    main(sys.argv[1])
