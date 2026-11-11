"""Extra extraction lists: ar1g = AR1's graded FaceMorpher set (AR2, levels m = 0 ... 0.5, 300 hosts);
af0_w2 = AF0 images built after wave 1; af0_h = the warped halves W_A, W_B (wave-2 negatives, ghost.py).
  python3 -I lists_extra.py ar1g | af0_w2 | af0_h | h1 | soft_src | soft
"""
import csv
import sys

sys.path.insert(0, __import__("os").path.dirname(__import__("os").path.abspath(__file__)))
import lists as LS  # noqa: E402


def main():
    which = sys.argv[1]
    rows = []
    if which == "ar1g":
        for r in csv.DictReader(open(LS.AR1 / "manifest.csv")):
            if r["pool"] == "frgcferet" and r["rung"] == "G":
                rows.append(dict(id="ar1_" + r["id"], path=r["path"], set="ar1g", cell="frgcferet",
                                 rung=f"m{float(r['level']):.1f}", tool=r["tool"], p1=r["p1"], p2=r["p2"], geom="tem",
                                 g1=r["tem1"], g2=r["tem2"], w1=r["w1"]))
    elif which == "af0_w2":
        w1 = {r["id"] for r in csv.DictReader(open(LS.OUT / "lists" / "af0_w1.csv"))}
        rows = [r for r in csv.DictReader(open(LS.OUT / "lists" / "af0.csv")) if r["id"] not in w1]
    elif which == "h1":          # approved Poisson set (A27), orig variant only, evaluation only
        root = LS.pathlib.Path("/mnt/t7/smad_heldout/h1_poisson/data")
        for r in csv.DictReader(open(root / "manifests/h1poisson.csv")):
            if r["variant"] != "orig":
                continue
            m = r["label"] == "1"
            rows.append(dict(id="h1_" + r["id"], path=str(root / r["path"]), set="h1", cell="h1poisson",
                             rung="morph" if m else "bona", tool="poisson", p1="casia:" + r["contrib_a"],
                             p2="casia:" + (r["contrib_b"] if m else r["contrib_a"]), geom="fixed", g1="", g2="", w1=""))
    elif which == "soft_src":    # wave 4 sources: photos, uniform-0.5 morphs, and the halves of uniform-0.5 pairs
        for n in ("af0_w1", "af0_w2", "af0_h"):
            for r in csv.DictReader(open(LS.OUT / "lists" / f"{n}.csv")):
                if r["cell"] != "train":
                    continue                                   # training split only (CPU-bound detector)
                if r["rung"] in ("photo", "u50"):
                    rows.append(r)
                elif r["rung"] in ("halfA", "halfB") and "_u50_" in r["id"]:
                    k = int(r["id"].split("_")[3])          # one half per pair: A for even, B for odd pair index
                    if (r["rung"] == "halfA") == (k % 2 == 0):
                        rows.append(r)
    elif which == "soft":        # wave 4 softened copies (soften.py build): same geometry / persons as the source
        src = {r["id"]: r for r in csv.DictReader(open(LS.OUT / "lists" / "soft_src.csv"))}
        for r in csv.DictReader(open(LS.OUT / "soft_soft_src.csv")):
            if not r["path"]:
                continue
            s0 = dict(src[r["src_id"]])
            s0.update(id=f"{r['src_id']}_{r['strength']}", path=r["path"], rung=f"{s0['rung']}_soft_{r['strength']}")
            rows.append(s0)
    elif which == "ar1soft_src":  # wave 4 evaluation: AR1 frgcferet R0 and R2w (both tools) to be softened
        import random
        cand = [r for r in csv.DictReader(open(LS.OUT / "lists" / "ar1.csv"))
                if r["cell"] == "frgcferet" and r["rung"] in ("R0", "R2w")]
        hosts = sorted({r["p1"] for r in cand})
        keep = set(random.Random(401).sample(hosts, 200))        # 200 seeded hosts (CPU-bound detector)
        rows = [r for r in cand if r["p1"] in keep]
    elif which == "ar1soft":
        src = {r["id"]: r for r in csv.DictReader(open(LS.OUT / "lists" / "ar1soft_src.csv"))}
        for r in csv.DictReader(open(LS.OUT / "soft_ar1soft_src.csv")):
            if not r["path"]:
                continue
            s0 = dict(src[r["src_id"]])
            s0.update(id=f"{r['src_id']}_{r['strength']}", path=r["path"], rung=f"{s0['rung']}_soft_{r['strength']}",
                      set="ar1soft")
            rows.append(s0)
    elif which == "ladsoft_src":  # lead 18:45: OpenCV R4 + R3 of all 536 primary hosts, R3m of the 200 ar1soft hosts
        keep = {r["p1"] for r in csv.DictReader(open(LS.OUT / "lists" / "ar1soft_src.csv"))}
        for r in csv.DictReader(open(LS.OUT / "lists" / "ar1.csv")):
            if r["cell"] == "frgcferet" and r["tool"] == "opencv" and (
                    r["rung"] in ("R4", "R3") or (r["rung"] == "R3m" and r["p1"] in keep)):
                rows.append(r)
    elif which == "ladsoft":      # after soften.py build: hard links under img/soft_ladder/<rung>_<strength>/,
        import hashlib            # the lead's list lists/ar1soft_ladder.csv, and the extraction list lists/ladsoft.csv
        import os
        src = {r["id"]: r for r in csv.DictReader(open(LS.OUT / "lists" / "ladsoft_src.csv"))}
        lead = []
        info = {}
        for fn in ("soft_ladsoft_src_rev.csv", "soft_ladsoft_src.csv"):      # merge both softening processes' logs
            if (LS.OUT / fn).exists():
                for r in csv.DictReader(open(LS.OUT / fn)):
                    k = (r["src_id"], r["strength"])
                    if k not in info or (r["aligned"] not in ("", "None") and info[k]["aligned"] in ("", "None")):
                        info[k] = r
        for r in info.values():
            if not r["path"]:
                continue
            s0 = dict(src[r["src_id"]])
            d = LS.OUT / "img" / "soft_ladder" / f"{s0['rung']}_{r['strength']}"
            d.mkdir(parents=True, exist_ok=True)
            dst = d / (s0["p1"].replace(":", "_") + ".png")
            if not dst.exists():
                os.link(r["path"], dst)
            sha = hashlib.sha256(open(dst, "rb").read()).hexdigest()
            lead.append(dict(host=s0["p1"], person=s0["p2"], rung=s0["rung"], strength=r["strength"],
                             target_ied_px={"amsl112": 112.71795654296875, "fm61": 61.21146774291992}[r["strength"]],
                             source_path=s0["path"], output_path=str(dst), sha256=sha, aligned=r["aligned"],
                             native_ied=r["native_ied"], scale=r["scale"]))
            s0.update(id=f"{r['src_id']}_{r['strength']}", path=str(dst), rung=f"{s0['rung']}_soft_{r['strength']}",
                      set="ladsoft")
            rows.append(s0)
        with open(LS.OUT / "lists" / "ar1soft_ladder.csv", "w", newline="") as f:
            w = csv.DictWriter(f, fieldnames=list(lead[0]))
            w.writeheader()
            w.writerows(lead)
    elif which == "af0_h":
        for r in csv.DictReader(open(LS.OUT / "halves.csv")):
            rows.append(dict(id=r["id"], path=r["path"], set="af0", cell=r["split"], rung=r["field"], tool=r["db"],
                             p1=r["pid_A"], p2=r["pid_B"], geom="lm", g1=r["lm"], g2="", w1=""))
    LS.write(which, rows)


if __name__ == "__main__":
    main()
