"""Threshold transfer on unseen genuine sources (TT1): per-source and per-family counts of the genuine pools (no score).
Joins raw_manifest.csv and aligned_manifest.csv; writes pools_summary.json and pools_summary.md in the experiment folder.
  python3 -I summary.py"""
import csv
import hashlib
import json
import pathlib
import statistics as st

OUT = pathlib.Path("/mnt/t7/smad_next/TT1")
RES = pathlib.Path("/home/narolski/smad-next/experiments/TT1_threshold-transfer-unseen-genuine")
ORDER = ["replay_attack", "msu_mfsd", "oulu_npu", "casia_fasd", "lfw", "calfw", "cfp_ff", "agedb_30"]


def q(xs, p):
    xs = sorted(xs)
    if not xs:
        return None
    k = (len(xs) - 1) * p
    lo, hi = int(k), min(int(k) + 1, len(xs) - 1)
    return xs[lo] + (xs[hi] - xs[lo]) * (k - lo)


def block(rs):
    al = [r for r in rs if r["aligned"] == "1"]
    det = [r for r in rs if r["detected"] == "1"]
    enl = [float(r["enlarge"]) for r in al]
    lap = [float(r["lap_var"]) for r in rs]
    return dict(
        photos=len(rs), persons=len({r["person"] for r in rs}),
        persons_aligned=len({r["person"] for r in al}),
        detected=len(det), aligned=len(al), aligned_share=round(len(al) / len(rs), 4),
        fail_no_face=sum(r["fail_reason"] == "no_face" for r in rs),
        fail_frontal_filter=sum(r["fail_reason"] == "frontal_filter" for r in rs),
        median_ied_src_aligned=round(st.median(float(r["ied_src"]) for r in al), 2) if al else None,
        median_enlarge_aligned=round(st.median(enl), 3) if enl else None,
        enlarge_p10_p90=[round(q(enl, .1), 3), round(q(enl, .9), 3)] if enl else None,
        median_lap_var=round(st.median(lap), 1), lap_var_p10_p90=[round(q(lap, .1), 1), round(q(lap, .9), 1)],
        median_lap_var_aligned=round(st.median(float(r["lap_var"]) for r in al), 1) if al else None,
        greyscale_share=round(sum(r["greyscale"] == "1" for r in rs) / len(rs), 4),
        median_border_frac_aligned=round(st.median(float(r["border_frac"]) for r in al), 4) if al else None,
        size=sorted({f"{r['width']}x{r['height']}" for r in rs}),
    )


def main():
    raw = {r["id"]: r for r in csv.DictReader(open(OUT / "raw_manifest.csv"))}
    ali = list(csv.DictReader(open(OUT / "aligned_manifest.csv")))
    assert len(ali) == len(raw)
    rows = [{**raw[a["id"]], **a} for a in ali]
    out = dict(raw_manifest_sha256=hashlib.sha256((OUT / "raw_manifest.csv").read_bytes()).hexdigest(),
               aligned_manifest_sha256=hashlib.sha256((OUT / "aligned_manifest.csv").read_bytes()).hexdigest(),
               per_source={}, per_family={})
    for s in ORDER:
        out["per_source"][s] = block([r for r in rows if r["source"] == s])
    for f in sorted({r["family"] for r in rows}, key=lambda f: ORDER.index(f) if f in ORDER else 4.5):
        out["per_family"][f] = block([r for r in rows if r["family"] == f])
    out["all"] = block(rows)
    (RES / "pools_summary.json").write_text(json.dumps(out, indent=1))
    hdr = ("| Source | Photos kept | Persons / pseudo-identities | Aligned share | Failures (no face / frontal filter) | "
           "Median source IED (px) | Median enlargement to 132 px (p10-p90) | Median Laplacian variance (p10-p90) | "
           "Greyscale share | Median black-border share of the 512 frame |\n|---|---|---|---|---|---|---|---|---|---|\n")
    md = ["# Genuine pools of the threshold-transfer experiment (TT1)", "",
          f"raw_manifest.csv sha256 `{out['raw_manifest_sha256']}`; aligned_manifest.csv sha256 "
          f"`{out['aligned_manifest_sha256']}`. Enlargement, IED and border: aligned images only. Sharpness and "
          "greyscale: all kept photos (raw images).", ""]
    for title, d in (("Per source", out["per_source"]), ("Per family", out["per_family"])):
        md += [f"## {title}", "", hdr.rstrip("\n")]
        for k, b in list(d.items()) + ([("all", out["all"])] if title == "Per family" else []):
            md.append(f"| {k} | {b['photos']} | {b['persons']} | {b['aligned_share']:.3f} ({b['aligned']}) | "
                      f"{b['fail_no_face']} / {b['fail_frontal_filter']} | {b['median_ied_src_aligned']} | "
                      f"{b['median_enlarge_aligned']} ({b['enlarge_p10_p90'][0]}-{b['enlarge_p10_p90'][1]}) | "
                      f"{b['median_lap_var']} ({b['lap_var_p10_p90'][0]}-{b['lap_var_p10_p90'][1]}) | "
                      f"{b['greyscale_share']:.3f} | {b['median_border_frac_aligned']} |")
        md.append("")
    (RES / "pools_summary.md").write_text("\n".join(md) + "\n")
    print("\n".join(md))


if __name__ == "__main__":
    main()
