"""NE1 pack (prereg.md sections 2-4): one tar with code, base weights, the images and manifests of sets T, L, C, G, B, S,
plus a network tar with the five Sb networks and their TT1-FS gate references. No benchmark row (asserted).
  manifests: ne1_train.csv (T, unique images, with kind and host), ne1_gate.csv (G, tt1_score.csv fam-gate order),
             ne1_read.csv (L, C, B, S with column set)
  python3 -I build_ne1_pack.py"""
import csv, hashlib, json, os, pathlib, shutil, subprocess, sys, tarfile
sys.path.insert(0, "/home/narolski/smad-next/src/PN1")
FS = pathlib.Path("/mnt/t7/smad_next/PN1/fs_tree/pn1")
TT = pathlib.Path("/mnt/t7/smad_next/TT1")
MS = pathlib.Path("/mnt/t7/smad_next/MS1/pack_tree/pn1/data")
OUT = pathlib.Path("/mnt/t7/smad_next/NE1")
FSR = pathlib.Path("/mnt/t7/smad_next/PN1/results_fs")
GREF = TT / "results/unpacked_fs/TT1_A100_pn1fs_fs/scores"
NETS = [f"PN1_Sb_s{s}" for s in (403, 404, 405, 406, 407)]
BENCH = ("frll", "mad22", "mordiff", "dim", "/h1", "fei", "casia_web", "valx", "fst", "a12sp")


def sha(p):
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for b in iter(lambda: f.read(1 << 22), b""):
            h.update(b)
    return h.hexdigest()


def main():
    import pn1lib as K
    cat = [r for r in K.catalog() if r["fam"] in ("af0", "ladder")]
    host = {r["id"]: r["host"] for r in cat}
    lad_hosts = {r["host"] for r in cat if r["fam"] == "ladder"}

    def t_host(i):  # SM1 warped halves sm1h_<db>_<n>_h{A,B} and SM-splices sp2_S<k>_<tool>_<db>_<n>: host = ladder pid <db>:<n>
        if i in host:
            return host[i]
        stem = i[5:-3] if i.startswith("sm1h_") else "_".join(i.split("_")[-2:]) if i.startswith("sp2_") else None
        h = stem.replace("_", ":", 1) if stem else None
        assert h in lad_hosts, (i, h)
        return h
    tree = OUT / "pack_tree"
    if tree.exists():
        shutil.rmtree(tree)
    root = tree / "ne1"; D = root / "data"; (D / "manifests").mkdir(parents=True)
    os.symlink(FS / "code", root / "code"); (root / "hf" / "a12").mkdir(parents=True)
    for f in (FS / "hf" / "a12").iterdir():
        os.symlink(f.resolve(), root / "hf" / "a12" / f.name)
    links = {}
    # T
    seen, T = set(), []
    for r in csv.DictReader(open(FS / "data/manifests/train_Sb.csv")):
        if r["path"] in seen:
            continue
        seen.add(r["path"])
        T.append(dict(id=r["id"], path=r["path"], label=r["label"], kind=r["kind"], host=t_host(r["id"]), set="T"))
        links[r["path"]] = FS / "data" / r["path"]
    # G
    src = json.load(open(TT / "tt1_score_sources.json"))
    G = []
    for r in csv.DictReader(open(TT / "tt1_score.csv")):
        if r["fam"] == "gate":
            G.append(dict(id=r["id"], path=r["path"], label=r["label"], kind=r["rung"], host=r["host"], set="G")); links[r["path"]] = pathlib.Path(src[r["path"]])
    # L, C
    R = []
    for r in csv.DictReader(open(FS / "data/manifests/pn1_eval.csv")):
        if r["fam"] in ("ladder", "splice") and r["role"] in ("dev", "test"):
            R.append(dict(id=r["id"], path=r["path"], label=r["label"], kind=f"{r['fam']}:{r['rung']}:{r['strength']}:{r['tool']}", host=r["host"], set="L"))
        elif r["fam"] == "ffhq_lcomb":
            R.append(dict(id=r["id"], path=r["path"], label=r["label"], kind=r["rung"], host=r["host"], set="C"))
        else:
            continue
        links[r["path"]] = FS / "data" / r["path"]
    # B
    for r in csv.DictReader(open(TT / "tt1_score.csv")):
        if r["rung"] == "R_cam_border":
            R.append(dict(id=r["id"], path=r["path"], label="0", kind=f"border:{r['cell']}", host=r["host"], set="B")); links[r["path"]] = pathlib.Path(src[r["path"]])
    # S
    for r in csv.DictReader(open(MS / "manifests/pn1_eval.csv")):
        if r["fam"] == "ms1ffhq":
            R.append(dict(id=r["id"], path=r["path"], label=r["label"], kind=f"{r['rung']}:{r['strength']}", host=r["host"], set="S")); links[r["path"]] = MS / r["path"]
    for rows in (T, G, R):  # ids unique within each manifest; 291 G R_cam photos are also L ladder genuine rows (other path, same source image)
        assert len({x["id"] for x in rows}) == len(rows), "duplicate ids"
    assert not ({x["id"] for x in T} & {x["id"] for x in G + R}), "fit ids overlap read ids"
    assert not ({x["path"] for x in T} & {x["path"] for x in G + R}), "fit rows overlap read rows"
    for p, s in links.items():
        assert not any(b in str(p).lower() or b in str(s).lower() for b in BENCH), p
        (D / p).parent.mkdir(parents=True, exist_ok=True); os.symlink(s.resolve(), D / p)
    for name, rows in (("ne1_train.csv", T), ("ne1_gate.csv", G), ("ne1_read.csv", R)):
        with open(D / "manifests" / name, "w", newline="") as fh:
            w = csv.DictWriter(fh, fieldnames=["id", "path", "label", "kind", "host", "set"]); w.writeheader(); w.writerows(rows)
        shutil.copyfile(D / "manifests" / name, OUT / name)
    ss = subprocess.run(f"cd {root} && find -L . -type f ! -name SHA256SUMS -print0 | sort -z | xargs -0 sha256sum", shell=True, check=True, capture_output=True, text=True).stdout
    (root / "SHA256SUMS").write_text(ss)
    tar = OUT / "ne1_pack.tar"
    subprocess.run(["tar", "-C", str(tree), "-chf", str(tar), "--sort=name", "--owner=0", "--group=0", "--numeric-owner", "--mtime=2026-11-13 00:00:00", "ne1"], check=True)
    (OUT / "ne1_pack.tar.sha256").write_text(f"{sha(tar)}  ne1_pack.tar\n")
    # nets
    nt = OUT / "nets_tree"
    if nt.exists():
        shutil.rmtree(nt)
    nr = nt / "ne1nets"; (nr / "gate_ref").mkdir(parents=True)
    for n in NETS:
        want = (FSR / f"{n}.tar.sha256").read_text().split()[0]; assert sha(FSR / f"{n}.tar") == want, n
        (nr / "nets" / n).mkdir(parents=True)
        with tarfile.open(FSR / f"{n}.tar") as tf:
            for f in ("meta.json", "last_trainable.pt"):
                (nr / "nets" / n / f).write_bytes(tf.extractfile(f"{n}/{f}").read())
        shutil.copyfile(GREF / f"{n}__gate.npz", nr / "gate_ref" / f"{n}.npz")
    ss = subprocess.run(f"cd {nr} && find . -type f ! -name SHA256SUMS -print0 | sort -z | xargs -0 sha256sum", shell=True, check=True, capture_output=True, text=True).stdout
    (nr / "SHA256SUMS").write_text(ss)
    nt_tar = OUT / "ne1_nets.tar"
    subprocess.run(["tar", "-C", str(nt), "-cf", str(nt_tar), "--sort=name", "--owner=0", "--group=0", "--numeric-owner", "--mtime=2026-11-13 00:00:00", "ne1nets"], check=True)
    (OUT / "ne1_nets.tar.sha256").write_text(f"{sha(nt_tar)}  ne1_nets.tar\n")
    print(json.dumps(dict(T=len(T), G=len(G), R=len(R), by_set={s: sum(1 for x in R if x["set"] == s) for s in "LCBS"}, files=len(ss.splitlines()),
                          pack=(OUT / "ne1_pack.tar.sha256").read_text().split()[0], nets=(OUT / "ne1_nets.tar.sha256").read_text().split()[0],
                          size=tar.stat().st_size)))


if __name__ == "__main__":
    main()
