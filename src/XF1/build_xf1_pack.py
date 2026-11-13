"""XF1 pack (prereg.md sections 2-4): FFHQ FaceMorpher two-person morphs FM(H,B) (DATA D12a), the one-photo renders
FM(H,H) (DATA D1d) and the plain MS1 hold-out photos H, for the 299 D12a hosts; plus the 3,417 registered gate rows
(NE1's ne1_gate.csv, TT1 fam-gate order) with the TT1-FS pn1fs gate references for the 15 FS1 networks A, B, Sb at
seeds 403-407. Every image's sha256 is checked against the DATA manifests. No benchmark row (asserted). Host ids stay
on /mnt/t7: the row list is written to /mnt/t7/smad_next/XF1/.
  python3 -I build_xf1_pack.py [--rows-only]
Writes /mnt/t7/smad_next/XF1/{xf1_rows.csv, xf1_pack.tar(.sha256), xf1_nets.tar(.sha256)}"""
import csv, hashlib, json, os, pathlib, shutil, subprocess, sys, tarfile

FS = pathlib.Path("/mnt/t7/smad_next/PN1/fs_tree/pn1")
FSR = pathlib.Path("/mnt/t7/smad_next/PN1/results_fs")
D12A = pathlib.Path("/mnt/t7/smad_next/DATA/D12a")
D1D = pathlib.Path("/mnt/t7/smad_next/DATA/D1d")
NE1 = pathlib.Path("/mnt/t7/smad_next/NE1")
GREF = pathlib.Path("/mnt/t7/smad_next/TT1/results/unpacked_fs/TT1_A100_pn1fs_fs/scores")
OUT = pathlib.Path("/mnt/t7/smad_next/XF1")
NETS = [f"PN1_{a}_s{s}" for a in ("A", "B", "Sb") for s in range(403, 408)]
PINS = {"D12a/manifest.csv": "9df020e1c5fa7a3bcc21d038c154405707780a05a90df579baad0f59eb7f7f4c",
        "D12a/pairs.csv": "b3c4bfc243c51796cb88ecd9494c7f01b9d66e1b56a77c871c28ee34b16373f5",
        "D1d/manifest.csv": "1bfa13ecbbade1734cf9e3dcb3e40a31a943635d28d12f0ba603908ed707cee8"}
BENCH = ("frll", "mad22", "mordiff", "dim", "/h1", "fei", "casia_web", "valx", "fst", "a12sp")
HEAD = ["id", "path", "label", "klass", "role", "fam", "rung", "strength", "tool", "cell", "host", "neutral"]


def sha(p):
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for b in iter(lambda: f.read(1 << 22), b""):
            h.update(b)
    return h.hexdigest()


def components(nx):
    comp, k = {}, 0
    for h in sorted(nx):
        if h in comp:
            continue
        x = h
        while x not in comp:
            comp[x] = k
            x = nx[x]
        k += 1
    return comp


def main():
    rows_only = "--rows-only" in sys.argv
    for rel, want in PINS.items():
        assert sha(pathlib.Path("/mnt/t7/smad_next/DATA") / rel) == want, rel
    m = list(csv.DictReader(open(D12A / "manifest.csv")))
    d1d = {r["out"]: r for r in csv.DictReader(open(D1D / "manifest.csv"))}
    assert len(m) == 299 and len({r["host"] for r in m}) == 299 and {r["host"] for r in m} == {r["partner"] for r in m}
    for a in ("A", "B", "Sb"):   # no FFHQ row in any FS1 training list
        assert not any("ffhq" in (v or "").lower() for r in csv.DictReader(open(FS / f"data/manifests/train_{a}.csv")) for v in r.values()), a
    comp = components({r["host"]: r["partner"] for r in m})
    read, links = [], {}
    for r in m:
        k = r["host"].split(":")[1]
        assert r["rung"] == "R4" and r["engine"] == "facemorpher"
        dr = d1d[r["d1d_render_host"]]
        assert dr["pid"] == r["host"] and dr["out_sha256"] == r["d1d_render_host_sha256"] and dr["frame_sha256"] == r["frame_host_sha256"]
        for klass, src, h, label in (("H", r["frame_host"], r["frame_host_sha256"], 0),
                                     ("FMHH", r["d1d_render_host"], r["d1d_render_host_sha256"], 0),
                                     ("FMHB", r["out"], r["out_sha256"], 1)):
            assert sha(src) == h, src
            i = f"xf1_{klass}_{k}"
            p = f"eval/xf1/{klass}/{k}.png"
            read.append(dict(id=i, path=p, label=str(label), klass=klass, role="dev", fam="xf1", rung=klass, strength="",
                             tool="facemorpher" if klass != "H" else "", cell=str(comp[r["host"]]), host=r["host"],
                             neutral="", partner=r["partner"] if klass == "FMHB" else "", sha256=h, src=src))
            links[p] = pathlib.Path(src)
    OUT.mkdir(parents=True, exist_ok=True)
    with open(OUT / "xf1_rows.csv", "w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=HEAD + ["partner", "sha256", "src"]); w.writeheader(); w.writerows(read)
    print(json.dumps(dict(rows=len(read), components=len(set(comp.values())), rows_sha256=sha(OUT / "xf1_rows.csv"))))
    if rows_only:
        return
    gate = []
    for r in csv.DictReader(open(NE1 / "ne1_gate.csv")):
        gate.append(dict(id=r["id"], path=r["path"], label=r["label"], klass=r["kind"], role="gate", fam="gate", rung=r["kind"],
                         strength="", tool="", cell="", host=r["host"], neutral=""))
        links[r["path"]] = (NE1 / "pack_tree/ne1/data" / r["path"]).resolve()
    assert len(gate) == 3417 and not ({x["id"] for x in gate} & {x["id"] for x in read})
    tree = OUT / "pack_tree"
    if tree.exists():
        shutil.rmtree(tree)
    root = tree / "xf1"; D = root / "data"; (D / "manifests").mkdir(parents=True)
    fs_sums = dict(reversed(line.rstrip("\n").split("  ", 1)) for line in open(FS / "SHA256SUMS"))
    for p, h in sorted(fs_sums.items()):
        if p.startswith(("code/", "hf/")):
            (root / p).parent.mkdir(parents=True, exist_ok=True); os.symlink((FS / p).resolve(), root / p)
    for p, s in links.items():
        assert not any(b in str(p).lower() or b in str(s).lower() for b in BENCH), p
        (D / p).parent.mkdir(parents=True, exist_ok=True); os.symlink(s.resolve(), D / p)
    with open(D / "manifests/xf1_eval.csv", "w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=HEAD, extrasaction="ignore"); w.writeheader(); w.writerows(gate + read)
    shutil.copyfile(D / "manifests/xf1_eval.csv", OUT / "xf1_eval.csv")
    ss = subprocess.run(f"cd {root} && find -L . -type f ! -name SHA256SUMS -print0 | sort -z | xargs -0 sha256sum", shell=True, check=True, capture_output=True, text=True).stdout
    (root / "SHA256SUMS").write_text(ss)
    for p, h in fs_sums.items():   # code and weights unchanged from the FS1 tree
        if p.startswith(("code/", "hf/")):
            assert f"{h}  ./{p}" in ss, p
    tar = OUT / "xf1_pack.tar"
    subprocess.run(["tar", "-C", str(tree), "-chf", str(tar), "--sort=name", "--owner=0", "--group=0", "--numeric-owner", "--mtime=2026-11-13 00:00:00", "xf1"], check=True)
    (OUT / "xf1_pack.tar.sha256").write_text(f"{sha(tar)}  xf1_pack.tar\n")
    nt = OUT / "nets_tree"
    if nt.exists():
        shutil.rmtree(nt)
    nr = nt / "xf1nets"; (nr / "gate_ref").mkdir(parents=True)
    for n in NETS:
        want = (FSR / f"{n}.tar.sha256").read_text().split()[0]; assert sha(FSR / f"{n}.tar") == want, n
        (nr / "nets" / n).mkdir(parents=True)
        with tarfile.open(FSR / f"{n}.tar") as tf:
            for f in ("meta.json", "last_trainable.pt"):
                (nr / "nets" / n / f).write_bytes(tf.extractfile(f"{n}/{f}").read())
        shutil.copyfile(GREF / f"{n}__gate.npz", nr / "gate_ref" / f"{n}.npz")
    ss2 = subprocess.run(f"cd {nr} && find . -type f ! -name SHA256SUMS -print0 | sort -z | xargs -0 sha256sum", shell=True, check=True, capture_output=True, text=True).stdout
    (nr / "SHA256SUMS").write_text(ss2)
    nt_tar = OUT / "xf1_nets.tar"
    subprocess.run(["tar", "-C", str(nt), "-cf", str(nt_tar), "--sort=name", "--owner=0", "--group=0", "--numeric-owner", "--mtime=2026-11-13 00:00:00", "xf1nets"], check=True)
    (OUT / "xf1_nets.tar.sha256").write_text(f"{sha(nt_tar)}  xf1_nets.tar\n")
    print(json.dumps(dict(gate=len(gate), read=len(read), files=len(ss.splitlines()), pack=(OUT / "xf1_pack.tar.sha256").read_text().split()[0],
                          nets=(OUT / "xf1_nets.tar.sha256").read_text().split()[0], size=tar.stat().st_size)))


if __name__ == "__main__":
    main()
