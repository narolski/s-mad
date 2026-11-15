"""FRLL read v1 (author ruling 2026-11-15): the reader. Implements the amendment
experiments/FINAL_sealed-benchmark-read/AMENDMENT_AUTHOR_RULING_FRLL_20261115.md mechanically:
per-family EER/AUC on the frozen 7,265-row roster (pinned final_metrics.py), exact Clopper-Pearson
intervals, own-rule flag rates (logit>0), dev-frozen tau_FFHQ flag rates (committed
final_thresholds.json), and the registered two-way person bootstrap (102 persons, B=2000,
numpy.random.default_rng(20261121); a genuine photo weighs its person's draw, a morph the product
of its two contributors' draws; the same draws for every detector, no re-drawing between cells).
DESCRIPTIVE read only: no verdict tests, no SOTA/generalises/shortcut-free sentences.
Detectors: Sb s403-407 (fresh rescore.py logits, loop rc=0), SelfMAD hrnet_w18 (fresh RS1 own-crop
scoring on the DGX GB10), released MADation ViT-B/16 + ViT-L/14 + MixFaceNet-MAD (existing
registered RS1 prod_v1/prod_v2 own-crop scores, READ not rescored; FaceMorpher cell = variant 2
only, RS1 result amendment 7). FE/FS MADation rows are not part of the registered comparison set
here and stay in the score files (available in the pinned npz for any later print).
Create-only outputs under /mnt/t7/smad_next/FRLL_READ_V1/read/.
  python3 -I frll_read_v1_read.py --freeze FREEZE.json --out OUTDIR
"""
import argparse
import csv
import hashlib
import json
import pathlib
import sys

import numpy as np

HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import final_metrics as FM  # noqa: E402

FAMS = ("amsl", "facemorpher", "opencv", "stylegan", "webmorph")
B, RNG_SEED, N_PERSONS = 2000, 20261121, 102
USED_RELEASES = ("madation_vitb16", "madation_vitl14", "mixfacenet_mad_smdd")


def sha(p):
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for b in iter(lambda: f.read(1 << 22), b""):
            h.update(b)
    return h.hexdigest()


def need(ok, msg):
    if not ok:
        raise SystemExit(f"FRLL_READ_V1_BLOCKED: {msg}")


def weighted_eer_ci(s, y, W):
    """Point EER (unweighted, ties half) + person-bootstrap 95% percentile interval."""
    point = FM.eer(s, y)
    vals = np.array([FM.eer_w(s, y, W[b])[0] for b in range(B)])
    lo, hi = np.percentile(vals, [2.5, 97.5])
    return point, float(lo), float(hi)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--freeze", required=True)
    ap.add_argument("--out", required=True)
    a = ap.parse_args()
    need(sys.flags.isolated, "python -I required")
    freeze = json.loads(pathlib.Path(a.freeze).read_text())
    FM.self_test()

    man_path = pathlib.Path(freeze["manifest"]["path"])
    need(sha(man_path) == freeze["manifest"]["sha256"], "frozen manifest changed")
    rows = list(csv.DictReader(open(man_path)))
    need(len(rows) == 7265, f"roster rows {len(rows)} != 7265")
    ids = [r["id"] for r in rows]
    rowidx = {i: j for j, i in enumerate(ids)}
    need(len(rowidx) == len(ids), "duplicate roster ids")
    labels_global = np.array([int(r["label"]) for r in rows])

    # ---------------- registered person bootstrap (one draw set, all detectors) ----------------
    persons_all = [r["persons"].split("|") for r in rows]
    plist = sorted({p for pp in persons_all for p in pp})
    need(len(plist) == N_PERSONS, f"{len(plist)} persons != 102")
    pidx = {p: i for i, p in enumerate(plist)}
    rng = np.random.default_rng(RNG_SEED)
    counts = np.stack([rng.multinomial(N_PERSONS, np.full(N_PERSONS, 1 / N_PERSONS)) for _ in range(B)])
    need(int(counts.sum()) == B * N_PERSONS, "person draws must conserve 102 per replicate")
    W = np.zeros((B, len(rows)))
    for j, pp in enumerate(persons_all):
        if len(pp) == 1:
            W[:, j] = counts[:, pidx[pp[0]]]
        else:
            need(len(pp) == 2, f"unexpected persons field {pp}")
            W[:, j] = counts[:, pidx[pp[0]]] * counts[:, pidx[pp[1]]]   # product of contributors' draws
    need(bool((W >= 0).all()), "negative bootstrap weight")

    # ---------------- detectors ----------------
    tau = json.loads(pathlib.Path(
        "/home/narolski/smad-next/experiments/FINAL_sealed-benchmark-read/final_thresholds.json").read_text())

    sb = {}
    for s in range(403, 408):
        f = f"/mnt/t7/smad_next/FRLL_READ_V1/sb_scores_s{s}.npz"
        z = np.load(f, allow_pickle=True)
        need(len(z["id"]) == 7265, f"s{s}: scored {len(z['id'])} rows != frozen 7265")
        need(sorted(str(i) for i in z["id"]) == sorted(ids), f"s{s}: scored ids differ from the frozen roster")
        need(int(z["seed"]) == s, f"s{s}: seed tag mismatch")
        lg = np.asarray(z["logit"], np.float64)
        need(bool(np.isfinite(lg).all()), f"s{s}: nonfinite logits")
        sb[s] = {str(i): float(v) for i, v in zip(z["id"], lg)}

    sm_path = pathlib.Path("/mnt/t7/smad_next/FRLL_READ_V1/selfmad_own/scores_frll_read_v1.npz")
    need(sm_path.exists(), "SelfMAD full selfmad-own read missing")
    z = np.load(sm_path, allow_pickle=True)
    need(str(z["det"]) == "selfmad_hrnet_w18" and str(z["mode"]) == "own", "selfmad det/mode changed")
    need(sorted(str(i) for i in z["id"]) == sorted(ids), "selfmad scored ids differ from frozen roster")
    need(str(z["manifest_sha256"]) == freeze["manifest"]["sha256"], "selfmad ran on a different manifest")
    need(str(z["script_sha256"]) == freeze["pins"]["rs1_score_py"], "selfmad scorer changed vs pin")
    lg = np.asarray(z["logit_noTTA"], np.float64)
    need(bool(np.isfinite(lg).all()), "selfmad nonfinite logits")
    selfmad = {str(i): float(v) for i, v in zip(z["id"], lg)}

    rel = {}
    R = "/mnt/t7/smad_next/RS1/results_rented"
    # The rented production runs stored these rows under the id "xr_" + the roster id (same src_path
    # per the pre-amend2 manifest, labels/persons cross-checked below). The freeze pins every src and
    # frame sha256; the score files are pinned in FREEZE.
    OLD_MAN = "/mnt/t7/smad_next/RS1/manifest_before_amend2.csv"
    OLD_MAN_PIN = "a3a10e250803560991e92261aa420e7cf77274431e07c3ab52d91bb3006246d8"
    need(sha(OLD_MAN) == OLD_MAN_PIN, "pre-amend2 RS1 manifest changed vs pin")
    old_by_src = {}
    for r in csv.DictReader(open(OLD_MAN)):
        need(r["src_path"] not in old_by_src, f"duplicate src_path in pre-amend2 manifest: {r['src_path']}")
        old_by_src[r["src_path"]] = r
    for r in rows:
        o = old_by_src.get(r["src_path"])
        need(o is not None, f"roster row {r['id']} has no pre-amend2 counterpart")
        need(int(o["label"]) == int(r["label"]) and o["persons"] == r["persons"],
             f"label/persons disagree between manifests for {r['id']}")
    keymap = {"madation_vitb16": "madation_vitb16", "madation_vitl14": "madation_vitl14",
              "mixfacenet_mad_smdd": "mixfacenet"}
    for det in USED_RELEASES:
        sub = keymap[det]
        stem = det if det == "mixfacenet_mad_smdd" else det
        for v in ("v1", "v2"):
            f = f"{R}/prod_{v}_rented/scores/scores_rel_{stem}__{v}.npz"
            pin = freeze["pins"][f"existing_scores_prod_{v}_{sub}"]
            need(sha(f) == pin, f"{det} {v}: score file hash changed vs FREEZE")
            z = np.load(f, allow_pickle=True)
            need(str(z["mode"]) == "rel", f"{det} {v}: mode")
            rel.setdefault(det, {})[v] = {str(i): float(x) for i, x in zip(z["id"], np.asarray(z["logit_noTTA"], np.float64))}

    # ---------------- per-family cells ----------------
    res = {
        "read": "FRLL_READ_V1", "descriptive": True, "no_verdict_tests": True,
        "B": B, "rng_seed": RNG_SEED, "frozen_manifest_sha256": freeze["manifest"]["sha256"],
        "sb_logit_npz_sha256": {f"s{s}": sha(f"/mnt/t7/smad_next/FRLL_READ_V1/sb_scores_s{s}.npz") for s in range(403, 408)},
        "selfmad_npz_sha256": sha(sm_path),
        "eer_note": "eer_pct is true percent (point = fraction x100), ties half, linear interpolation (pinned final_metrics.py); CI = person-bootstrap 95% percentile",
        "flag_note": "flag_own = logit>0 (own rule); flag_tau = dev-frozen tau_FFHQ (FFHQ genuine pool, never a training source)",
        "facemorpher_note": "release rows read from variant 2 only (crop script fails on these files; RS1 amendment 7)",
        "families": {}}
    variants_used = {}
    for fam in FAMS:
        mids = [r["id"] for r in rows if r["family"] == fam and r["set"] != "G_raw"]
        gids = [r["id"] for r in rows if r["set"] == "G_raw"]
        need(len(gids) == 204 and len(mids) > 0, f"{fam}: pool sizes {len(mids)}/{len(gids)}")
        idx = [rowidx[i] for i in mids + gids]
        y = labels_global[idx]
        Wc = W[:, idx]
        cells = {}

        def one_cell(name, scores, det, variant, dropped, have):
            if have is None:
                y_d, W_d = y, Wc
            else:
                ih = [rowidx[i] for i in have]
                y_d, W_d = labels_global[ih], W[:, ih]
            eer, lo, hi = weighted_eer_ci(s=scores, y=y_d, W=W_d)
            source = ("own frames (rescore.py)" if det.startswith("Sb")
                      else "own crop (GB10, fresh)" if det == "SelfMAD (release)"
                      else f"RS1 own crop {variant}")
            c = {"eer_pct": 100.0 * eer, "eer_ci95": [100.0 * lo, 100.0 * hi], "auc": FM.auc(scores, y_d),
                 "n_morph": int((y_d == 1).sum()), "n_genuine": int((y_d == 0).sum()), "source": source}
            if dropped:
                c["n_dropped_release_crop_fails"] = len(dropped)
                c["n_differs_note"] = (f"variant {variant} keeps {len(have)} of {len(mids)} frozen morphs "
                                       f"({len(dropped)} dropped by the release crop-script failure; not imputed)")
            c["flag_own"] = FM.rates(scores, y_d, 0.0)
            if det.startswith("Sb") and f"PN1_{det.replace('Sb ', 'Sb_s')}" in tau["nets"]:
                trec = tau["nets"][f"PN1_{det.replace('Sb ', 'Sb_s')}"]["tau_ffhq"]
            elif det == "SelfMAD (release)":
                trec = tau["releases"]["selfmad_hrnet_w18/own_dgx"]["tau_ffhq"]
            elif variant is not None:
                trec = tau["releases"][f"{det}/{variant}"]["tau_ffhq"]
            else:
                trec = None
            if trec is not None:
                c["tau_ffhq"] = trec
                c["flag_tau"] = FM.rates(scores, y_d, trec)
            cells[name] = c

        for s in range(403, 408):
            one_cell(f"Sb s{s}", np.array([sb[s][i] for i in mids + gids]), f"Sb s{s}", None, [], None)
        one_cell("SelfMAD (release)", np.array([selfmad[i] for i in mids + gids]), "SelfMAD (release)", None, [], None)
        for det in USED_RELEASES:
            variant = "v2" if fam == "facemorpher" else "v1"
            pool = rel[det][variant]
            have = [i for i in mids + gids if "xr_" + i in pool]
            dropped = [i for i in mids if "xr_" + i not in pool]          # release crop-script failures
            need(all("xr_" + i in pool for i in gids), f"{det} {fam}: genuine rows missing in {variant}")
            if fam == "facemorpher":
                miss_v1 = sum(1 for i in mids if "xr_" + i not in rel[det]["v1"])
                need(miss_v1 > 0, "facemorpher v1 must be incomplete (crop script fails) — v2-only read unjustified")
                dropped_v1 = miss_v1   # recorded; the published cell is the complete v2 run
            name = det + (f" [{variant}]" if variant else "")
            one_cell(name, np.array([pool["xr_" + i] for i in have]), det, variant, dropped, have)
        seeds = np.array([cells[f"Sb s{s}"]["eer_pct"] for s in range(403, 408)])
        cells["sb_seed_summary"] = {"mean_eer": float(seeds.mean()), "sd_eer": float(seeds.std(ddof=1)),
                                    "min": float(seeds.min()), "max": float(seeds.max())}
        res["families"][fam] = cells

    # ---------------- side record: a46 corrective consistency (ViT-B/16, shared ids) ----------------
    f46 = "/mnt/t7/smad_next/RS1/scores/scores_rel_madation_vitb16__a46.npz"
    pin46 = freeze["pins"]["side_record_a46_vitb16"]
    need(sha(f46) == pin46, "a46 side record hash changed")
    z = np.load(f46, allow_pickle=True)
    a46 = {str(i): float(x) for i, x in zip(z["id"], np.asarray(z["logit_noTTA"], np.float64))}
    v2 = rel["madation_vitb16"]["v2"]
    shared = [i for i in ids if i in a46 and "xr_" + i in v2]
    dd = np.abs(np.array([a46[i] for i in shared]) - np.array([v2["xr_" + i] for i in shared]))
    res["side_record"] = {"what": "a46 corrective npz (plain ids) vs RS1 prod_v2 xr_ rows (madation_vitb16)",
                          "shared_rows": len(shared), "max_abs_logit_delta": float(dd.max())}

    out = pathlib.Path(a.out)
    need(not out.exists(), "create-only: read output dir exists")
    out.mkdir(parents=True)
    (out / "FRLL_READ_RESULTS.json").write_text(json.dumps(res, indent=1, allow_nan=False) + "\n")

    lines = ["# FRLL read v1 — per-family results (DESCRIPTIVE read; EER %, AUC)", "",
             f"Population: the frozen 7,265-row roster (5 families x morphs vs 204 raw FRLL genuine). "
             f"CI = two-way person bootstrap 95% ({B} replicates, rng {RNG_SEED}).", "",
             "| family | detector | EER % [95% CI] | AUC | variant | flag_own (m/g %) | flag_tau_FFHQ (m/g %) |",
             "|---|---|---|---|---|---|---|"]
    for fam in FAMS:
        for det, c in res["families"][fam].items():
            if not isinstance(c, dict) or "flag_own" not in c:
                continue
            fo = c["flag_own"]; ft = c.get("flag_tau")
            fts = f"{100*ft['apcer']:.1f}/{100*ft['bpcer']:.1f}" if ft else "—"
            lines.append(f"| {fam} | {det} | {c['eer_pct']:.2f} [{c['eer_ci95'][0]:.2f}, {c['eer_ci95'][1]:.2f}] | "
                         f"{c['auc']:.3f} | {c['source']} | "
                         f"{100*fo['apcer']:.1f}/{100*fo['bpcer']:.1f} | {fts} |")
    (out / "FRLL_READ_TABLES.md").write_text("\n".join(lines) + "\n")
    print("FRLL_READ_V1_READ_DONE", len(FAMS), "families;", {f: round(res["families"][f]["sb_seed_summary"]["mean_eer"], 2) for f in FAMS})


if __name__ == "__main__":
    main()
