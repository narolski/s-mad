"""Fixed-threshold re-read (EV1): SHA-256 of every input file the EV1 scripts read (manifests, score files, embeddings)
and of every output file. Writes /mnt/t7/smad_next/EV1/input_sha256.txt and
/home/narolski/smad-next/experiments/EV1_fixed-threshold-reread/output_sha256.txt. Never opens forbidden names.
Run: nice -n 10 python3 -I src/EV1/ev1_hashes.py
"""
import hashlib, pathlib, sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import ev1_common as K  # noqa: E402
import ev1_amend as AM  # noqa: E402


def sha(p):
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for b in iter(lambda: f.read(1 << 20), b""):
            h.update(b)
    return h.hexdigest()


def main():
    files = [K.EVAL, K.GTEST, K.FFHQM, K.A36NET, K.SELFMAD_OWN, AM.A43MAN, AM.H3MAN, AM.SPMAN,
             K.MC / "experiments/A41_shortcut-proof-zero-gpu/raw/results/a41_files.json",
             pathlib.Path("/mnt/t7/smad_heldout/a46/feat/a46_feat.npz"), pathlib.Path("/mnt/t7/smad_next/AR1/frll_src_emb.npz"),
             pathlib.Path("/mnt/t7/smad_heldout/a41_diffae/work/glint_embeddings.npz"),
             K.SN / "src/C_cue_checks/c_checks.py", K.SN / "src/AD1/ad1_read.py"]
    for d, _ in K.RELEASES:
        for w in ("eval", "gtest", "ffhqm", "h3sg3"):
            p = K.A12REL / d / f"scores_{w}.npz"
            if p.exists():
                files.append(p)
    for n in K.recipe_networks():
        for w in ("eval_last", "gtest_last"):
            p = K.A12BR / n["run"] / f"scores_{w}.npz"
            if p.exists():
                files.append(p)
    for d in K.morph_free_networks():
        files.append(d["dir"] / "scores_eval_last.npz")
    for lab in [l for _, l in K.RELEASES] + ["SelfMAD release, own preprocessing"]:
        files += [p for p in AM.ext_paths(lab) if p is not None]
    files = sorted({pathlib.Path(p) for p in files if not K.forbidden(p)}, key=str)
    with open(K.BIG / "input_sha256.txt", "w") as fh:
        for p in files:
            fh.write(f"{sha(p)}  {p}\n")
    outs = sorted(p for p in K.OUT.iterdir() if p.is_file() and p.name != "output_sha256.txt")
    outs += sorted(p for p in K.BIG.iterdir() if p.is_file() and p.suffix in (".npz",))
    with open(K.OUT / "output_sha256.txt", "w") as fh:
        for p in outs:
            fh.write(f"{sha(p)}  {p}\n")
    print(len(files), "inputs,", len(outs), "outputs hashed")


if __name__ == "__main__":
    main()
