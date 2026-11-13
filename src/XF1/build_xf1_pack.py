"""XF1 pack, revision b (prereg.md "Revision b"; second pre-run check PRERUN_XF1_B_20261113.md fixes 1-2): the 1,495
rows of the pinned row list xf1b_rows.csv (klass FMHB / WARP / H x form whole / face; every image sha256-checked
against the row list), plus the 3,417 registered gate rows (NE1's ne1_gate.csv, TT1 fam-gate order) with the TT1-FS
pn1fs gate references for the 15 FS1 networks A, B, Sb at seeds 403-407. FS1 code and base weights unchanged (sha256
asserted against the FS1 tree). No benchmark row (asserted). No file is deleted: an existing tree or tar is renamed
to .bak-<stamp> (F7). Host ids stay on /mnt/t7.
  python3 -I build_xf1_pack.py
Writes /mnt/t7/smad_next/XF1/{xf1b_eval.csv, xf1b_pack.tar(.sha256), xf1b_nets.tar(.sha256)}"""
import csv, hashlib, json, os, pathlib, subprocess, tarfile, time

FS = pathlib.Path("/mnt/t7/smad_next/PN1/fs_tree/pn1")
FSR = pathlib.Path("/mnt/t7/smad_next/PN1/results_fs")
NE1 = pathlib.Path("/mnt/t7/smad_next/NE1")
GREF = pathlib.Path("/mnt/t7/smad_next/TT1/results/unpacked_fs/TT1_A100_pn1fs_fs/scores")
OUT = pathlib.Path("/mnt/t7/smad_next/XF1")
ROWS = OUT / "xf1b_rows.csv"
ROWS_SHA = "4adcf914fba651f3b1b1ccfc5ea4b3e03155357aa5c84804180513da5925b271"
NETS = [f"PN1_{a}_s{s}" for a in ("A", "B", "Sb") for s in range(403, 408)]
BENCH = ("frll", "mad22", "mordiff", "dim", "/h1", "fei", "casia_web", "valx", "fst", "a12sp")
HEAD = ["id", "path", "label", "klass", "role", "fam", "rung", "strength", "tool", "cell", "host", "neutral"]
STAMP = time.strftime("%Y%m%d%H%M%S")


def sha(p):
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for b in iter(lambda: f.read(1 << 22), b""):
            h.update(b)
    return h.hexdigest()


def aside(p):
    """F7: never delete; rename an existing output to .bak-<stamp>."""
    if p.exists() or p.is_symlink():
        p.rename(p.with_name(p.name + f".bak-{STAMP}"))


def main():
    assert sha(ROWS) == ROWS_SHA
    src = list(csv.DictReader(open(ROWS)))
    assert len(src) == 1495
    read, links = [], {}
    for r in src:
        assert sha(r["src"]) == r["sha256"], r["src"]
        read.append(dict(id=r["id"], path=r["path"], label=r["label"], klass=r["klass"], role="dev", fam="xf1", rung=f"{r['klass']}_{r['form']}",
                         strength="", tool="facemorpher" if r["klass"] != "H" else "", cell=r["block"], host=r["host"], neutral=""))
        links[r["path"]] = pathlib.Path(r["src"])
    for a in ("A", "B", "Sb"):   # no FFHQ row in any FS1 training list
        assert not any("ffhq" in (v or "").lower() for r in csv.DictReader(open(FS / f"data/manifests/train_{a}.csv")) for v in r.values()), a
    gate = []
    for r in csv.DictReader(open(NE1 / "ne1_gate.csv")):
        gate.append(dict(id=r["id"], path=r["path"], label=r["label"], klass=r["kind"], role="gate", fam="gate", rung=r["kind"],
                         strength="", tool="", cell="", host=r["host"], neutral=""))
        links[r["path"]] = (NE1 / "pack_tree/ne1/data" / r["path"]).resolve()
    assert len(gate) == 3417 and not ({x["id"] for x in gate} & {x["id"] for x in read})
    assert len({x["id"] for x in read}) == len(read) and len({x["path"] for x in read}) == len(read)
    tree = OUT / "packb_tree"; aside(tree)
    root = tree / "xf1"; D = root / "data"; (D / "manifests").mkdir(parents=True)
    fs_sums = dict(reversed(line.rstrip("\n").split("  ", 1)) for line in open(FS / "SHA256SUMS"))
    for p, h in sorted(fs_sums.items()):
        if p.startswith(("code/", "hf/")):
            (root / p).parent.mkdir(parents=True, exist_ok=True); os.symlink((FS / p).resolve(), root / p)
    for p, s in links.items():
        assert not any(b in str(p).lower() or b in str(s).lower() for b in BENCH), p
        (D / p).parent.mkdir(parents=True, exist_ok=True); os.symlink(s.resolve(), D / p)
    with open(D / "manifests/xf1b_eval.csv", "w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=HEAD); w.writeheader(); w.writerows(gate + read)
    ev = OUT / "xf1b_eval.csv"; aside(ev); ev.write_bytes((D / "manifests/xf1b_eval.csv").read_bytes())
    ss = subprocess.run(f"cd {root} && find -L . -type f ! -name SHA256SUMS -print0 | sort -z | xargs -0 sha256sum", shell=True, check=True, capture_output=True, text=True).stdout
    (root / "SHA256SUMS").write_text(ss)
    for p, h in fs_sums.items():   # code and weights unchanged from the FS1 tree
        if p.startswith(("code/", "hf/")):
            assert f"{h}  ./{p}" in ss, p
    tar = OUT / "xf1b_pack.tar"; aside(tar); aside(OUT / "xf1b_pack.tar.sha256")
    subprocess.run(["tar", "-C", str(tree), "-chf", str(tar), "--sort=name", "--owner=0", "--group=0", "--numeric-owner", "--mtime=2026-11-13 00:00:00", "xf1"], check=True)
    (OUT / "xf1b_pack.tar.sha256").write_text(f"{sha(tar)}  xf1b_pack.tar\n")
    nt = OUT / "netsb_tree"; aside(nt)
    nr = nt / "xf1nets"; (nr / "gate_ref").mkdir(parents=True)
    for n in NETS:
        want = (FSR / f"{n}.tar.sha256").read_text().split()[0]; assert sha(FSR / f"{n}.tar") == want, n
        (nr / "nets" / n).mkdir(parents=True)
        with tarfile.open(FSR / f"{n}.tar") as tf:
            for f in ("meta.json", "last_trainable.pt"):
                (nr / "nets" / n / f).write_bytes(tf.extractfile(f"{n}/{f}").read())
        (nr / "gate_ref" / f"{n}.npz").write_bytes((GREF / f"{n}__gate.npz").read_bytes())
    ss2 = subprocess.run(f"cd {nr} && find . -type f ! -name SHA256SUMS -print0 | sort -z | xargs -0 sha256sum", shell=True, check=True, capture_output=True, text=True).stdout
    (nr / "SHA256SUMS").write_text(ss2)
    nt_tar = OUT / "xf1b_nets.tar"; aside(nt_tar); aside(OUT / "xf1b_nets.tar.sha256")
    subprocess.run(["tar", "-C", str(nt), "-cf", str(nt_tar), "--sort=name", "--owner=0", "--group=0", "--numeric-owner", "--mtime=2026-11-13 00:00:00", "xf1nets"], check=True)
    (OUT / "xf1b_nets.tar.sha256").write_text(f"{sha(nt_tar)}  xf1b_nets.tar\n")
    print(json.dumps(dict(gate=len(gate), read=len(read), files=len(ss.splitlines()), eval_sha256=sha(ev),
                          pack=(OUT / "xf1b_pack.tar.sha256").read_text().split()[0], nets=(OUT / "xf1b_nets.tar.sha256").read_text().split()[0],
                          size=tar.stat().st_size)))


if __name__ == "__main__":
    main()
