"""MS1 exclusion proof (prereg part 1, section 3.1): no FFHQ development image (ffhqm, the FFHQ-Morphs universe) enters
any MS1 FFHQ image, by key, by raw-file sha256 and by identity; hold-out persons disjoint from training persons; no
benchmark path in any MS1 list.  python3 -I proof.py -> experiments/MS1.../exclusion_proof.json"""
import csv
import json
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import numpy as np  # noqa: E402

import ms1common as C  # noqa: E402

O = C.OUT / "ffhq"
BAD = ("frll", "mad22", "mordiff", "dim-", "dim_", "h1_poisson", "fei", "casia", "valx", "fst", "a12sp", "ffhq_morphs")


def main():
    ex, named = C.excluded_keys()
    log = list(csv.DictReader(open(O / "select_log.csv")))
    kept = [r for r in log if r["outcome"] == "kept"]
    persons = list(csv.DictReader(open(O / "persons.csv")))
    exsha = {r["sha256"]: r["key"] for r in csv.DictReader(open(O / "excluded_raw_sha256.csv"))}
    assert len(exsha) <= 20000
    keys = [r["key"] for r in kept]
    by_key = sorted(set(keys) & ex)
    by_sha = sorted(r["key"] for r in kept if r["raw_sha256"] in exsha)
    kept_sha_dup = len(keys) - len({r["raw_sha256"] for r in kept})
    frame_dup = len(keys) - len({r["frame_sha256"] for r in kept})
    # identity: recompute from saved embeddings (not from the log)
    zr, zk = np.load(O / "emb_ref.npz"), np.load(O / "emb_kept.npz")
    ref = zr["emb"][zr["found"]]
    K = zk["emb"]
    cr = (K @ ref.T).max(1)
    G = K @ K.T
    np.fill_diagonal(G, -1)
    parts = {p["key"]: p["part"] for p in persons}
    tr = [i for i, k in enumerate(zk["key"]) if parts.get(k) in ("af0", "ladder")]
    ho = [i for i, k in enumerate(zk["key"]) if parts.get(k) == "holdout"]
    bad_paths = []
    for f in sorted((O / "lists").glob("*.csv")):
        for r in csv.DictReader(open(f)):
            for v in r.values():
                if isinstance(v, str) and v.startswith("/") and any(b in v.lower() for b in BAD):
                    bad_paths.append(v)
    res = dict(excluded_keys=len(ex), ffhqm_named_keys=len(named), ffhqm_named_inside_universe=named <= ex,
               excluded_raw_files_hashed=len(exsha), kept=len(kept), refs_found=int(zr["found"].sum()),
               refs_total=len(zr["found"]),
               overlap_by_key=by_key, overlap_by_raw_sha256=by_sha, duplicate_raw_sha256_among_kept=kept_sha_dup,
               duplicate_frame_sha256_among_kept=frame_dup,
               max_cos_to_ffhqm_refs=round(float(cr.max()), 4), n_cos_ref_ge_040=int((cr >= 0.40).sum()),
               max_cos_among_kept=round(float(G.max()), 4), n_pairs_kept_ge_040=int((np.triu(G, 1) >= 0.40).sum()),
               max_cos_holdout_vs_training=round(float(G[np.ix_(ho, tr)].max()), 4) if ho and tr else None,
               holdout_training_person_overlap=len({k for k, p in parts.items() if p == "holdout"} &
                                                   {k for k, p in parts.items() if p != "holdout"}),
               benchmark_paths_in_lists=bad_paths[:20], n_benchmark_paths=len(bad_paths))
    res["pass"] = (not by_key and not by_sha and kept_sha_dup == 0 and res["n_cos_ref_ge_040"] == 0
                   and res["n_pairs_kept_ge_040"] == 0 and res["holdout_training_person_overlap"] == 0
                   and not bad_paths and res["ffhqm_named_inside_universe"])
    json.dump(res, open(C.RES / "exclusion_proof.json", "w"), indent=1)
    print(json.dumps(res, indent=1))


if __name__ == "__main__":
    if not sys.flags.isolated:
        sys.exit("run with python3 -I")
    main()
