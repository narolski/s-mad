"""Sealed MAD22 read (FINAL): write src/FINAL/final_pins.json (read by final_read.py) and the pins table of the
registration (replaces the line PINS_TABLE in prereg.md, or the table after '## 10. Pins').
  python3 -I make_pins.py [--selfmad NPZ] [--beststat NPZ]   (the two sealed outputs are added by the pin commit)"""
import argparse
import hashlib
import json
import pathlib
import re
import tarfile

HERE = pathlib.Path(__file__).resolve().parent
EXP = pathlib.Path("/home/narolski/smad-next/experiments/FINAL_sealed-benchmark-read")
O = pathlib.Path("/mnt/t7/smad_next/FINAL")


def sha(p):
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for b in iter(lambda: f.read(1 << 22), b""):
            h.update(b)
    return h.hexdigest()


def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--selfmad"); ap.add_argument("--beststat")
    a = ap.parse_args()
    cfg = json.load(open(HERE / "final_config.json"))
    pack = O / f"{cfg['read_id']}_pack.tar"
    assert (O / (pack.name + ".sha256")).read_text().split()[0] == sha(pack)
    with tarfile.open(pack) as t:
        sums = t.extractfile("final/SHA256SUMS").read().decode()
        binfo = json.loads(t.extractfile("final/build_info.json").read())
    line = {l.split("  ", 1)[1]: l.split("  ", 1)[0] for l in sums.strip().split("\n")}
    assert binfo["config_sha256"] == sha(HERE / "final_config.json"), "pack built with another config"
    rows = [("pack", str(pack), sha(pack)),
            ("pack SHA256SUMS (inside the pack)", "final/SHA256SUMS", hashlib.sha256(sums.encode()).hexdigest()),
            ("gate manifest (inside the pack)", "final/data/manifests/final_gate.csv", line["data/manifests/final_gate.csv"]),
            ("benchmark manifest (inside the pack)", "final/data/manifests/final_bench.csv", line["data/manifests/final_bench.csv"]),
            ("FS1 evaluation manifest (gate source)", cfg["gate"]["source_manifest"], cfg["gate"]["source_manifest_sha256"]),
            ("fresh-seed pack (gate source)", cfg["gate"]["source_pack"], cfg["gate"]["source_pack_sha256"]),
            ("MAD22 PROCESSED_SHA256SUMS", f"{cfg['mad22']['root']}/PROCESSED_SHA256SUMS", sha(f"{cfg['mad22']['root']}/PROCESSED_SHA256SUMS"))]
    rows += [(f"network {n['name']}", n["tar"], n["sha256"]) for n in cfg["networks"]]
    for k, v in cfg["scorer"].items():
        if isinstance(v, str) and re.fullmatch(r"[0-9a-f]{64}", v):
            rows.append((f"scorer {k}", k, v))
    files = ["final_config.json", "build_pack.py", "remote_final.sh", "drive_final.sh", "gate_check_final.py",
             "final_metrics.py", "final_read.py", "mock_test.py", "make_standin.py", "thresholds.py",
             "extract_release_scores.py", "selfmad_mad22.py", "beststat_mad22.py", "make_pins.py"]
    for f in files:
        rows.append((f"src/FINAL/{f}", str(HERE / f), sha(HERE / f)))
    ext = [("thresholds (committed)", EXP / "final_thresholds.json"),
           ("released detectors, existing rows", O / "release_scores_existing.npz"),
           ("AF0 cues_all.py (reference statistic)", pathlib.Path("/home/narolski/smad-next/src/AF0/cues_all.py")),
           ("RS1 score.py (SelfMAD scorer)", pathlib.Path("/home/narolski/smad-next/src/RS1/score.py")),
           ("RS1 athena_manifest.csv (SelfMAD inputs)", pathlib.Path("/mnt/t7/smad_next/RS1/athena/athena_manifest.csv")),
           ("rs1_border.csv (release crop border)", pathlib.Path("/home/narolski/smad-next/experiments/RS1_own-crop-rescore/rs1_border.csv"))]
    for k, p in ext:
        rows.append((k, str(p), sha(p)))
    pins = dict(config=cfg, pack=sha(pack), release_existing=sha(O / "release_scores_existing.npz"),
                thresholds=sha(EXP / "final_thresholds.json"), files={r[0]: r[2] for r in rows}, bytes_pack=pack.stat().st_size)
    for k, p in (("selfmad", a.selfmad), ("beststat", a.beststat)):
        if p:
            pins[k] = sha(p)
            rows.append((f"sealed output: {k}", p, pins[k]))
    (HERE / "final_pins.json").write_text(json.dumps(pins, indent=1))
    tab = "| Item | Path | sha256 |\n|---|---|---|\n" + "\n".join(f"| {k} | `{p}` | `{h}` |" for k, p, h in rows)
    tab += f"\n\nPack size {pack.stat().st_size:,} bytes. `final_pins.json` itself is pinned by the commit."
    pr = EXP / "prereg.md"
    s = pr.read_text()
    if a.selfmad or a.beststat:                      # after the registration commit: append a dated addendum only
        import subprocess
        now = subprocess.run(["date"], capture_output=True, text=True).stdout.strip()
        add = [f"\n## 12. Pin addendum ({now}): sealed outputs made after the registration commit\n",
               "Made by the registered scripts after the registration commit; not opened. Nothing above changes.\n"]
        add += [f"- {k}: `{p}` sha256 `{h}`" for k, p, h in rows if k.startswith("sealed output")]
        pr = EXP / "prereg.md"
        pr.write_text(pr.read_text().rstrip("\n") + "\n" + "\n".join(add) + "\n")
        print("PINS addendum", [k for k, _, _ in rows if k.startswith("sealed output")])
        return
    block = "<!-- PINS_BEGIN -->\n" + tab + "\n<!-- PINS_END -->"
    if "PINS_TABLE" in s:
        s = s.replace("PINS_TABLE", block)
    else:
        s = re.sub(r"<!-- PINS_BEGIN -->.*?<!-- PINS_END -->", lambda m: block, s, flags=re.S)
    pr.write_text(s)
    print("PINS", len(rows), "items; pack", pins["pack"])


if __name__ == "__main__":
    main()
