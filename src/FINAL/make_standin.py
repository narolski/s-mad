"""Sealed MAD22 read (FINAL), END-TO-END TEST ONLY: a stand-in "MAD22" folder made of FFHQ DEVELOPMENT frames (symlinks
under MAD22-like names, same layout and PROCESSED_SHA256SUMS), and stand-in configs, so that build_pack.py,
remote_final.sh, drive_final.sh and final_read.py can run end to end on the DGX without any benchmark image.
  config A: the real networks (their gate is expected to FAIL on the GB10: the fail path)
  config B: stand-in network tars whose scores_eval.npz carries GB10 scores of the gate rows (the pass path)
  python3 -I make_standin.py --out DIR [--gb10-gate DIR_WITH_<net>__gate.npz]"""
import argparse, csv, hashlib, io, json, pathlib, sys, tarfile
import numpy as np
HERE = pathlib.Path(__file__).resolve().parent
CFG = json.load(open(HERE / "final_config.json"))
FAMS = CFG["mad22"]["families"]


def sha(p):
    return hashlib.sha256(pathlib.Path(p).read_bytes()).hexdigest()


def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--out", required=True); ap.add_argument("--gb10-gate")
    a = ap.parse_args()
    out = pathlib.Path(a.out); root = out / "standin_mad22"
    src = pathlib.Path(CFG["gate"]["source_tree"])
    rows = [r for r in csv.DictReader(open(src / CFG["gate"]["source_manifest"])) if r["fam"] == "ffhq"]
    bona = [r for r in rows if r["rung"] == "ffhq_bona_orig"][:40]
    mor = [r for r in rows if r["rung"] == "landmark_complete_orig"]
    res = [r for r in rows if r["rung"] == "landmark_complete_resmatch"]
    lines = []
    def link(rel, r):
        d = root / rel; d.parent.mkdir(parents=True, exist_ok=True)
        if not d.exists():
            d.symlink_to(src / "data" / r["path"])
        lines.append(f"{sha(d)}  {rel}")
    for k, r in enumerate(bona):
        link(f"native/BonaFide/{k // 2 + 1:03d}_{'03' if k % 2 == 0 else '08'}.png", r)
    for j, fam in enumerate(FAMS):
        for k in range(30):
            r = mor[j * 30 + k]; p1, p2 = (k % 20) + 1, ((k + 3) % 20) + 1
            link(f"native/{fam}/{p1:03d}_03-vs-{p2:03d}_{'03' if k < 20 else '08'}.png", r)
        for k in range(40):
            r = res[j * 40 + k]
            link(f"e7/{fam}/{k // 2 + 1:03d}_{'03' if k % 2 == 0 else '08'}.png", r)
    (root / "PROCESSED_SHA256SUMS").write_text("\n".join(lines) + "\n")
    for tag in ("A", "B"):
        c = json.loads(json.dumps(CFG)); c["read_id"] = f"FINAL_standin{tag}"
        c["mad22"]["root"] = str(root); c["mad22"]["n_files"] = len(lines)
        if tag == "B":
            if not a.gb10_gate:
                continue
            nd = out / "standin_nets"; nd.mkdir(exist_ok=True)
            for n in c["networks"]:
                g = np.load(pathlib.Path(a.gb10_gate) / f"{n['name']}__gate.npz")
                gm = dict(zip(g["id"].tolist(), g["logit"].astype(np.float32).tolist()))
                with tarfile.open(n["tar"]) as t:
                    z = np.load(io.BytesIO(t.extractfile(f"{n['name']}/scores_eval.npz").read()))
                    ids = z["id"].tolist(); lg = z["logit"].astype(np.float32).copy()
                    for i, x in enumerate(ids):
                        if x in gm:
                            lg[i] = gm[x]
                    buf = io.BytesIO(); np.savez(buf, **{k: (lg if k == "logit" else z[k]) for k in z.files})
                    tp = nd / f"{n['name']}.tar"
                    with tarfile.open(tp, "w") as o:
                        for m in t.getmembers():
                            if m.name.endswith("/scores_eval.npz"):
                                b = buf.getvalue(); m.size = len(b); o.addfile(m, io.BytesIO(b))
                            else:
                                o.addfile(m, t.extractfile(m) if m.isfile() else None)
                n["tar"] = str(tp); n["sha256"] = sha(tp)
        (out / f"standin_config_{tag}.json").write_text(json.dumps(c, indent=1))
    print("STANDIN", len(lines), "files")


if __name__ == "__main__":
    main()
