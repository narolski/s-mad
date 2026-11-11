"""SM1 A12 item 11: stage the build of armd5 (five random pool partners) as an overlay on pack b.

Pack b (sm1_b_pack.tar, sha256 d59b86a9..., already on leaseB) holds every source render and .tem file armd5 needs
(first contributors of arm b; the five partners are arm b' replacement renders) and the same build.py / engine files
(sha256 checked here). This writes OUT/wcss/staging/SM1/cpu/SM1_cpu_d5/ with run.sh (= wcss_run.sh plus one step
that copies overlay/ into the work dir after the pack is unpacked), task.env (pack b's sha256), cpus, and overlay/
(lists/armd5.csv with work-dir-relative paths, lists/compare_ref.csv, ref/armd5/ = DGX reference outputs of the
first 8 rows, made here with the same build.py, one process).

  python3 -I prep_d5.py
"""
import csv
import json
import os
import pathlib
import shutil
import subprocess
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import sm1_common as K  # noqa: E402
import wcss_prep as WP  # noqa: E402

HERE = pathlib.Path(__file__).resolve().parent


def main():
    if not sys.flags.isolated:
        sys.exit("run with python3 -I")
    pb = json.load(open(WP.W / "pack_b.json"))
    src_b = WP.W / "packsrc_b"
    for f in ("build.py", "sm1_common.py"):
        assert K.sha(HERE / f) == K.sha(src_b / "code/sm1" / f), f
    for f in (K.S68, K.S78):
        assert K.sha(f) == K.sha(src_b / "code/scripts" / f.name), f
    td = WP.W / "staging/SM1/cpu/SM1_cpu_d5"
    if td.exists():
        shutil.rmtree(td)
    ov = td / "overlay"
    (ov / "lists").mkdir(parents=True)
    rows = list(csv.DictReader(open(K.OUT / "lists/armd5.csv")))
    have = set()
    with tarfile_names(WP.W / "packs/SM1/sm1_b_pack.tar") as names:
        have = names
    out = []
    for r in rows:
        q = dict(r)
        for k in ("a", "ta", "b", "tb"):
            q[k] = WP.rel(r[k])
            assert ("./" + q[k]) in have or q[k] in have, q[k]
        q["out"] = WP.rel(r["out"])
        out.append(q)
    with open(ov / "lists/armd5.csv", "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(out[0]))
        w.writeheader()
        w.writerows(out)
    refrows, comp = [], []
    for r in rows[:8]:
        rr = dict(r)
        rr["out"] = str(ov / "ref/armd5" / pathlib.Path(r["out"]).name)
        refrows.append(rr)
        comp.append(dict(out=f"out/armd5/{pathlib.Path(r['out']).name}", ref=f"ref/armd5/{pathlib.Path(r['out']).name}"))
    rc = WP.W / "ref_d5.csv"
    with open(rc, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(refrows[0]), extrasaction="ignore")
        w.writeheader()
        w.writerows(refrows)
    p = subprocess.run([K.PY, "-I", str(HERE / "build.py"), "--list", str(rc), "--workers", "1",
                        "--log-dir", str(ov / "ref")], capture_output=True, text=True)
    assert p.returncode == 0, p.stdout + p.stderr
    with open(ov / "lists/compare_ref.csv", "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=["out", "ref"])
        w.writeheader()
        w.writerows(comp)
    run = open(HERE / "wcss_run.sh").read()
    anchor = 'tar xf "$PACK"\n'
    assert anchor in run
    run = run.replace(anchor, anchor + 'cp -r "$HERE/overlay/." "$WK/"   # A12 item 11: armd5 list + references\n')
    (td / "run.sh").write_text(run)
    os.chmod(td / "run.sh", 0o755)
    (td / "cpus").write_text("96\n")
    (td / "est_minutes").write_text("10\n")
    (td / "task.env").write_text(f"SM1_TASK=d5\nSM1_LISTS=\"armd5\"\nSM1_PACK_SHA256={pb['pack_sha256']}\n")
    info = dict(task="d5", overlay_on=pb["pack"], pack_sha256=pb["pack_sha256"], n=len(out), staging=str(td))
    json.dump(info, open(WP.W / "pack_d5.json", "w"), indent=1)
    print(json.dumps(info, indent=1))


class tarfile_names:
    def __init__(self, p):
        import tarfile
        self.t = tarfile.open(p)

    def __enter__(self):
        return set(self.t.getnames())

    def __exit__(self, *a):
        self.t.close()


if __name__ == "__main__":
    main()
