"""Sealed MAD22 read (FINAL): the reader. Run ONCE on the read's result tar, after the driver has verified two copies.
It applies the registration (experiments/FINAL_sealed-benchmark-read/prereg.md) mechanically and writes numbers and
registered verdicts only.

  python3 -I final_read.py --result RESULT.tar --pack PACK.tar --release-existing REL.npz \
      [--selfmad SELFMAD.npz] [--beststat STAT.npz] --thresholds final_thresholds.json --out OUT.json --tables OUT.md
  (--marker DIR: the one-read marker; default /mnt/t7/smad_next/FINAL/READ_ONCE_<read_id>. Mock tests pass their own.)

Inputs are verified by sha256 against the pins in final_pins.json (written at registration; the mock tests pass
--pins of their own). Nothing is printed to the terminal except file names, the gate line and verdict labels."""
import argparse
import csv
import hashlib
import io
import json
import pathlib
import sys
import tarfile

import numpy as np

HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import final_metrics as FM  # noqa: E402

FAMS = ("FaceMorpher", "MIPGAN_I", "MIPGAN_II", "OpenCV", "Webmorph")
SATURATED = {"FaceMorpher"}            # AD4 morph-free ViT-B/16 (WCSS registered arm) EER 0.0% native and E7; ViT-L/14 0.0% native
NOT_SPECIFIC = {"MIPGAN_I", "MIPGAN_II"}
PRIMARY_FAMS = PRIMARY_FAMS_ = tuple(f for f in FAMS if f not in SATURATED)
RELEASES = ("madation_vitb16", "madation_vitl14", "mixfacenet_mad_smdd", "selfmad_hrnet_w18")
REL_NAME = {"madation_vitb16": "MADation ViT-B/16", "madation_vitl14": "MADation ViT-L/14",
            "mixfacenet_mad_smdd": "MixFaceNet-MAD", "selfmad_hrnet_w18": "SelfMAD"}
FORMS = ("S", "H", "BE_S", "BE_H")
FORM_NAME = {"S": "standard (native genuine)", "H": "history-matched: aligned-frame history (our aligner plus history)",
             "BE_S": "border-equalised standard", "BE_H": "border-equalised history-matched"}
B_REPS, SEED = 2000, 20261121
NI_MARGIN = 0.01                       # non-inferiority margin, +1.0 EER point
ALPHA1 = 0.025                         # one-sided, each test
BORDER_CAVEAT = 0.03                   # BE-H minus H seed-mean EER above 3 points -> border caveat on that family
LAB_SAT = "shortcut-saturated (a morph-free network reaches 0.0% EER on this cell, AD4): no state-of-the-art sentence"
LANDMARK_FAMS = ("OpenCV", "Webmorph")
MEANS = (("mean4", PRIMARY_FAMS_), ("mean5", FAMS), ("mean2", LANDMARK_FAMS))
# AD4 morph-free networks, seed means of EER % (printed reference lines; experiments/AD4/ad4_reading_m3.md lines 48-57,
# ad4_reading_m3l.md lines 51-60; "our preprocessing", our frames; reversed cells printed as read)
MORPHFREE = {"ViT-B/16 (WCSS)": {"S": {"FaceMorpher": 0.0, "MIPGAN_I": 72.5, "MIPGAN_II": 72.5, "OpenCV": 37.0, "Webmorph": 26.7},
                                 "H": {"FaceMorpher": 0.0, "MIPGAN_I": 72.5, "MIPGAN_II": 72.5, "OpenCV": 39.6, "Webmorph": 28.9}},
             "ViT-L/14": {"S": {"FaceMorpher": 0.0, "MIPGAN_I": 87.2, "MIPGAN_II": 92.8, "OpenCV": 46.6, "Webmorph": 36.5},
                          "H": {"FaceMorpher": 37.7, "MIPGAN_I": 87.2, "MIPGAN_II": 92.8, "OpenCV": 49.8, "Webmorph": 39.9}}}
F3_LIMIT = 0.02
LAB_NS = "not shown to be morph-specific: the network flags one-photo GAN renders"
LAB_SEEN = "seen during development (corrected MAD22; genuine side = the 204 FRLL photos)"


def sha(p):
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for b in iter(lambda: f.read(1 << 22), b""):
            h.update(b)
    return h.hexdigest()


def holm(ps):
    """Holm step-down adjusted p-values."""
    ps = np.asarray(ps, float)
    o = np.argsort(ps)
    m = len(ps)
    adj = np.empty(m)
    run = 0.0
    for i, k in enumerate(o):
        run = max(run, (m - i) * ps[k])
        adj[k] = min(1.0, run)
    return adj


def verdict(p_exc, p_lost, p_ni, seeds_better, n_seeds):
    """registered order: exceeded > lost > matched > comparable."""
    need = 4 if n_seeds == 5 else int(np.ceil(0.8 * n_seeds))
    if p_exc <= ALPHA1 and seeds_better >= need:
        return "exceeded"
    if p_lost <= ALPHA1:
        return "lost (within the 1-point margin)" if p_ni <= ALPHA1 else "lost"
    if p_ni <= ALPHA1:
        return "matched"
    return "comparable, not separated"


class Read:
    def __init__(self, a):
        self.a = a
        self.pins = json.load(open(a.pins))
        self.cfg = self.pins["config"]
        self.out = dict(read_id=self.cfg["read_id"], labels=dict(set=LAB_SEEN), inputs={}, gate=None, cells={},
                        verdicts={}, sentences={}, forecasts={}, border={}, notes=[])

    # ------------------------------------------------------------------ inputs
    def load(self):
        a, P = self.a, self.pins
        for k in ("selfmad", "beststat"):          # guard amendment F2: a pinned comparison input cannot be dropped
            if k in P and not getattr(a, k):
                sys.exit(f"{k} is pinned in final_pins.json: pass --{k}; it cannot be dropped at read time")
        for k, p in (("result", a.result), ("pack", a.pack), ("release_existing", a.release_existing),
                     ("thresholds", a.thresholds)):
            h = sha(p)
            self.out["inputs"][k] = dict(path=str(p), sha256=h)
            if k != "result":
                assert h == P[k], f"{k} not at its pin"
        assert h_ok(a.result), "result tar: sha256 file mismatch"
        for k, p in (("selfmad", a.selfmad), ("beststat", a.beststat)):
            if p:
                h = sha(p)
                assert h == P.get(k), f"{k} not at its pin"
                self.out["inputs"][k] = dict(path=str(p), sha256=h)
            else:
                self.out["inputs"][k] = None
        with tarfile.open(a.pack) as t:
            sums = t.extractfile("final/SHA256SUMS").read().decode()
            man = t.extractfile("final/data/manifests/final_bench.csv").read()
            binfo = json.loads(t.extractfile("final/build_info.json").read())
        line = {l.split("  ", 1)[1]: l.split("  ", 1)[0] for l in sums.strip().split("\n")}
        assert hashlib.sha256(man).hexdigest() == line["data/manifests/final_bench.csv"]
        self.man = list(csv.DictReader(io.StringIO(man.decode())))
        self.binfo = binfo
        rid = self.cfg["read_id"]
        with tarfile.open(a.result) as t:
            names = t.getnames()
            top = names[0].split("/")[0]
            assert top.startswith(rid + "_"), top
            rc = t.extractfile(f"{top}/rc").read().decode().strip()
            self.out["rc"] = rc
            gj = f"{top}/gate.json"
            self.out["gate"] = json.loads(t.extractfile(gj).read()) if gj in names else None
            self.out["versions"] = t.extractfile(f"{top}/versions.txt").read().decode() if f"{top}/versions.txt" in names else None
            self.out["gpu"] = t.extractfile(f"{top}/gpu.txt").read().decode() if f"{top}/gpu.txt" in names else None
            cfg_in = json.loads(t.extractfile(f"{top}/final_config.json").read())
            assert cfg_in == self.cfg, "result was made with another config"
            self.scores = {}
            if rc == "0" and self.out["gate"] and self.out["gate"]["all_pass"]:
                for n in self.cfg["networks"]:
                    z = np.load(io.BytesIO(t.extractfile(f"{top}/scores/{n['name']}__final.npz").read()))
                    self.scores[n["name"]] = dict(zip(z["id"].tolist(), z["logit"].astype(np.float64).tolist()))
                    assert len(self.scores[n["name"]]) == len(self.man), n["name"]
                    assert set(self.scores[n["name"]]) == {r["id"] for r in self.man}, n["name"]
        self.nonfinite = [n for n, m in self.scores.items() if not np.all(np.isfinite(list(m.values())))]
        self.thr = json.load(open(a.thresholds))

    def validate(self):
        """every input parsed and complete BEFORE the one-read marker is taken (no statistic computed here)."""
        need_rel = {"G22_raw", "G22_aln", "FF_orig"} | {f"M22_{f}" for f in FAMS} | {f"E7aln22_{f}" for f in FAMS}
        for n in self.cfg["networks"]:
            assert n["name"] in self.thr["nets"], f"threshold missing: {n['name']}"
        z = np.load(self.a.release_existing)
        for det in RELEASES[:3]:
            for v in ("v1", "v2"):
                assert f"{det}/{v}" in self.thr["releases"], f"threshold missing: {det}/{v}"
                k = (z["det"] == det) & (z["variant"] == v)
                assert need_rel <= set(z["pool"][k].tolist()), f"release pools missing: {det}/{v}"
        assert np.all(np.isfinite(z["logit"])), "release file has non-finite scores"
        if self.a.selfmad:
            zs = np.load(self.a.selfmad)
            assert need_rel - {"FF_orig"} <= set(zs["pool"].tolist()), "SelfMAD pools missing"
            assert "selfmad_hrnet_w18/own_dgx" in self.thr["releases"]
            assert np.all(np.isfinite(zs["logit"])), "SelfMAD file has non-finite scores"
        if self.a.beststat:
            zb = np.load(self.a.beststat)
            assert {r["id"] for r in self.man} <= set(zb["id"].tolist()), "statistic rows missing"
            assert np.all(np.isfinite(zb["noise_std_face"])), "statistic non-finite"
        pers = {r["pa"] for r in self.man} | {r["pb"] for r in self.man}
        assert set(z["pa"][z["pool"] != "FF_orig"].tolist()) | set(z["pb"][z["pool"] != "FF_orig"].tolist()) <= pers, "release persons outside the manifest"
        return True

    # ------------------------------------------------------------------ pools
    def our_pools(self, getscore):
        """-> {form: {family: (s_morph, pp_morph, s_gen, pp_gen, expr_gen)}} for one score map."""
        by = {}
        for r in self.man:
            by.setdefault((r["form"], r["pool"], r["family"]), []).append(r)
        bona = by[("std", "native", "bona")]
        out = {f: {} for f in FORMS}
        for fam in FAMS:
            m = by[("std", "morph", fam)]
            e7 = by[("std", "e7", fam)]
            be = self.binfo["be"][fam]["copies"] > 0
            mb = by.get((f"be:{fam}", "morph", fam), []) if be else m
            nb = by.get((f"be:{fam}", "native", "bona"), []) if be else bona
            eb = by.get((f"be:{fam}", "e7", fam), []) if be else e7
            for form, (mm, gg) in (("S", (m, bona)), ("H", (m, e7)), ("BE_S", (mb, nb)), ("BE_H", (mb, eb))):
                out[form][fam] = (np.array([getscore(r) for r in mm]), [(r["pa"], r["pb"]) for r in mm],
                                  np.array([getscore(r) for r in gg]), [(r["pa"],) for r in gg],
                                  np.array([r["expr"] for r in gg]))
        return out

    def rel_pools(self, z, det, variant, mode="e7"):
        """mode e7: H = raw morphs vs our aligned E7 frames (registered H); mode raw: H = raw morphs vs raw genuine
        (= S; comparator only, B1 option A); mode aln: S and H with our aligned native frames as genuine (printed)."""
        k = (z["det"] == det) & (z["variant"] == variant)
        if not k.any():
            return None

        def pool(name):
            m = k & (z["pool"] == name)
            if not m.any():
                return None
            return z["logit"][m].astype(np.float64), list(zip(z["pa"][m].tolist(), z["pb"][m].tolist())), z["expr"][m]

        out = {f: {} for f in FORMS}
        g = pool("G22_aln" if mode == "aln" else "G22_raw")
        for fam in FAMS:
            m = pool(f"M22_{fam}")
            e = g if mode in ("raw", "aln") else pool(f"E7aln22_{fam}")
            if m is None or g is None or e is None:
                return None
            S = (m[0], m[1], g[0], [(p[0],) for p in g[1]], g[2])
            H = (m[0], m[1], e[0], [(p[0],) for p in e[1]], e[2])
            out["S"][fam], out["H"][fam] = S, H
            if det == "selfmad_hrnet_w18" or mode == "aln":
                out["BE_S"][fam] = out["BE_H"][fam] = None      # border on SelfMAD's own preprocessing not measured
            else:
                out["BE_S"][fam], out["BE_H"][fam] = S, H       # own crop path border-free in both classes (rs1_border.csv)
        return out

    # ------------------------------------------------------------------ statistics
    def draws(self):
        pers = set()
        for r in self.man:
            pers.add(r["pa"]); pers.add(r["pb"])
        self.per = sorted(pers)
        self.pos = {p: i for i, p in enumerate(self.per)}
        rng = np.random.default_rng(SEED)
        n = len(self.per)
        self.C = rng.multinomial(n, np.full(n, 1.0 / n), size=B_REPS).astype(np.float64)
        ns = len(self.cfg["networks"])
        self.SI = rng.integers(0, ns, size=(B_REPS, ns))

    def wts(self, ppm, ppg):
        a = np.array([self.pos[p[0]] for p in ppm]); b = np.array([self.pos[p[1]] for p in ppm])
        wm = self.C[:, a] * self.C[:, b]
        same = a == b
        if same.any():
            wm[:, same] = self.C[:, a[same]]
        wg = self.C[:, [self.pos[p[0]] for p in ppg]]
        return np.c_[wm, wg]

    def cell_stats(self, cell, tau):
        sm, ppm, sg, ppg, ex = cell
        s = np.r_[sm, sg]; y = np.r_[np.ones(len(sm)), np.zeros(len(sg))]
        W = self.wts(ppm, ppg)
        neu = ex == "03"
        s_n = np.r_[sm, sg[neu]]; y_n = np.r_[np.ones(len(sm)), np.zeros(int(neu.sum()))]
        st = dict(n_morph=len(sm), n_genuine=len(sg), eer=FM.eer(s, y), auc=FM.auc(s, y),
                  bpcer_at_apcer={str(x): FM.bpcer_at_apcer(s, y, x) for x in (0.01, 0.05, 0.10, 0.20)},
                  eer_neutral_genuine=FM.eer(s_n, y_n), n_genuine_neutral=int(neu.sum()),
                  own_rule=FM.rates(s, y, 0.0) if tau is not None else None, tau_ffhq=FM.rates(s, y, tau) if tau is not None else None)
        return st, FM.eer_w(s, y, W)

    def unit(self, pools, tau):
        """-> stats {form: {fam: st}}, reps {form: {fam or mean5 or mean4: (R,)}}, points likewise."""
        st, rep, pt = {}, {}, {}
        for form in FORMS:
            st[form], rep[form], pt[form] = {}, {}, {}
            for fam in FAMS:
                c = pools[form][fam]
                if c is None:
                    st[form][fam] = None
                    continue
                st[form][fam], rep[form][fam] = self.cell_stats(c, tau)
                pt[form][fam] = st[form][fam]["eer"]
                st[form][fam]["eer_ci_person"] = [float(np.percentile(rep[form][fam], 2.5)), float(np.percentile(rep[form][fam], 97.5))]
            for key, fams in MEANS:
                if all(f in rep[form] for f in fams):
                    rep[form][key] = np.mean([rep[form][f] for f in fams], 0)
                    pt[form][key] = float(np.mean([pt[form][f] for f in fams]))
        return st, rep, pt

    # ------------------------------------------------------------------ the read
    def run(self):
        g = self.out["gate"]
        if self.nonfinite:
            self.out["outcome"] = "no read"
            self.out["sentences"]["primary"] = f"No read: non-finite scores for {self.nonfinite}. Reported to the lead; never re-run."
            return self.out
        if self.out["rc"] != "0" or not g or not g.get("all_pass"):
            self.out["outcome"] = "no read"
            self.out["sentences"]["primary"] = ("The platform gate failed or the job did not finish; no benchmark row "
                                                "was scored or read. Reported to the lead; no second platform, no "
                                                "changed tolerance.")
            return self.out
        self.draws()
        # our networks
        ours = {}
        for n in self.cfg["networks"]:
            m = self.scores[n["name"]]
            tau = self.thr["nets"][n["name"]]["tau_ffhq"]
            ours[n["name"]] = self.unit(self.our_pools(lambda r, m=m: m[r["id"]]), tau)
        names = [n["name"] for n in self.cfg["networks"]]
        # releases
        rels = {}
        z = np.load(self.a.release_existing)
        printed = {}                                    # aligned-native genuine rows (printed only)
        for det in RELEASES[:3]:
            for v in ("v1", "v2"):
                tau = self.thr["releases"][f"{det}/{v}"]["tau_ffhq"]
                p = self.rel_pools(z, det, v)
                rels[f"{det}/{v}"] = self.unit(p, tau) if p else None
                if v == "v1":
                    p = self.rel_pools(z, det, v, "raw")
                    rels[f"{det}/{v}:rawpool"] = self.unit(p, tau) if p else None
                    p = self.rel_pools(z, det, v, "aln")
                    printed[f"{det}/{v}:aligned_native"] = self.unit(p, tau) if p else None
        if self.a.selfmad:
            zs = np.load(self.a.selfmad)
            tau = self.thr["releases"]["selfmad_hrnet_w18/own_dgx"]["tau_ffhq"]
            p = self.rel_pools(zs, "selfmad_hrnet_w18", "own_dgx")
            rels["selfmad_hrnet_w18/own_dgx"] = self.unit(p, tau) if p else None
            p = self.rel_pools(zs, "selfmad_hrnet_w18", "own_dgx", "raw")
            rels["selfmad_hrnet_w18/own_dgx:rawpool"] = self.unit(p, tau) if p else None
            p = self.rel_pools(zs, "selfmad_hrnet_w18", "own_dgx", "aln")
            printed["selfmad_hrnet_w18/own_dgx:aligned_native"] = self.unit(p, tau) if p else None
        else:
            rels["selfmad_hrnet_w18/own_dgx"] = rels["selfmad_hrnet_w18/own_dgx:rawpool"] = None
            self.out["notes"].append("SelfMAD MAD22 rows: pending (not scored before the read); SelfMAD is not in the comparison set")
        # reference statistic
        ref = None
        if self.a.beststat:
            zb = np.load(self.a.beststat)
            mv = dict(zip(zb["id"].tolist(), (-zb["noise_std_face"].astype(np.float64)).tolist()))
            ref = self.unit(self.our_pools(lambda r: mv[r["id"]]), None)
        # tables
        cells = {}
        for form in FORMS:
            cells[form] = {}
            for fam in FAMS + tuple(k for k, _ in MEANS):
                row = dict(ours={n: (ours[n][0][form].get(fam) if fam in FAMS else ours[n][2][form].get(fam)) for n in names})
                pts = [ours[n][2][form].get(fam) for n in names]
                row["ours_seed_eer"] = pts
                row["ours_mean_eer"] = float(np.mean(pts)); row["ours_sd_eer"] = float(np.std(pts, ddof=1))
                row["ours_min_eer"], row["ours_max_eer"] = float(np.min(pts)), float(np.max(pts))
                agg = np.stack([ours[n][1][form][fam] for n in names])[self.SI, np.arange(B_REPS)[:, None]].mean(1)
                row["ours_mean_eer_ci_two_level"] = [float(np.percentile(agg, 2.5)), float(np.percentile(agg, 97.5))]
                row["releases_eer_ci_person"] = {k: (None if v is None or v[1][form].get(fam) is None else
                                                     [float(np.percentile(v[1][form][fam], 2.5)), float(np.percentile(v[1][form][fam], 97.5))])
                                                 for k, v in rels.items()}
                row["releases_aligned_native_printed"] = {k: (None if v is None or v[2][form].get(fam) is None else v[2][form][fam])
                                                          for k, v in printed.items()} if form in ("S", "H") else None
                row["morph_free_AD4_eer_pct"] = ({k: v[form].get(fam) for k, v in MORPHFREE.items()} if form in ("S", "H") and fam in FAMS else None)
                row["releases"] = {k: (None if v is None or v[2][form].get(fam) is None else
                                       (v[0][form][fam] if fam in FAMS else v[2][form][fam])) for k, v in rels.items()}
                row["reference_statistic"] = None if ref is None else (ref[0][form][fam] if fam in FAMS else ref[2][form][fam])
                row["labels"] = [LAB_SEEN] + ([LAB_SAT] if fam in SATURATED or fam == "mean5" else []) + ([LAB_NS] if fam in NOT_SPECIFIC or fam in ("mean4", "mean5") else []) \
                    + (["MIPGAN E7 pool = native genuine photos by construction"] if fam in NOT_SPECIFIC and form in ("H", "BE_H") else []) \
                    + (["no border in either class (mask empty): border-equalised = unblanked"] if fam in FAMS and form.startswith("BE") and self.binfo["be"][fam]["copies"] == 0 else [])
                if fam in FAMS and form.startswith("BE"):
                    row["mask_share"] = self.binfo["be"][fam]["mask_share"]
                if fam in FAMS:                    # F7: where a release cell's n differs from ours, say so
                    o0 = ours[names[0]][0][form][fam]
                    row["n_ours"] = (o0["n_morph"], o0["n_genuine"])
                    row["n_differs"] = {k: (v[0][form][fam]["n_morph"], v[0][form][fam]["n_genuine"]) for k, v in rels.items()
                                        if v is not None and v[0][form].get(fam) is not None
                                        and (v[0][form][fam]["n_morph"], v[0][form][fam]["n_genuine"]) != row["n_ours"]}
                cells[form][fam] = row
        self.out["cells"] = cells
        # comparisons: best comparison = the released detector (variant 1 crop; SelfMAD own DGX) with the lowest point EER
        # B1 option A: in every form the candidates are each release with its registered genuine pool AND with raw
        # genuine photos (":rawpool"); the lowest point EER is the best comparison (conservative for us)
        comp_keys = [k for k in rels if rels[k] is not None and ("/v1" in k or k.startswith("selfmad"))]
        ver = {}
        for form in FORMS:
            ver[form] = {}
            rows = []
            for fam in FAMS + tuple(k for k, _ in MEANS):
                cand = [(rels[k][2][form][fam], k) for k in comp_keys if rels[k][2][form].get(fam) is not None]
                if not cand:
                    ver[form][fam] = dict(verdict="not available (no comparison row)")
                    continue
                best_v, best_k = min(cand)
                our_rep = np.stack([ours[n][1][form][fam] for n in names])          # (seeds, R)
                agg = our_rep[self.SI, np.arange(B_REPS)[:, None]].mean(1)            # seeds drawn per replicate
                diff = agg - rels[best_k][1][form][fam]
                pts = np.array([ours[n][2][form][fam] for n in names])
                d0 = float(pts.mean() - best_v)
                p_exc = (1 + (diff >= 0).sum()) / (B_REPS + 1)
                p_lost = (1 + (diff <= 0).sum()) / (B_REPS + 1)
                p_ni = (1 + (diff >= NI_MARGIN).sum()) / (B_REPS + 1)
                better = int((pts < best_v).sum())
                ver[form][fam] = dict(best=best_k, best_name=REL_NAME[best_k.split("/")[0]] + (" (raw genuine photos)" if best_k.endswith(":rawpool") else ""), best_eer=best_v,
                                      ours_mean_eer=float(pts.mean()), diff=d0,
                                      diff_ci=[float(np.percentile(diff, 2.5)), float(np.percentile(diff, 97.5))],
                                      p_exceeded=p_exc, p_lost=p_lost, p_noninferior=p_ni, seeds_better=better,
                                      n_seeds=len(names))
                if fam in FAMS:
                    rows.append(fam)
            # Holm across the five families (per test), for every form
            fams_ok = [f for f in FAMS if "p_exceeded" in ver[form].get(f, {})]
            if fams_ok:
                for key in ("p_exceeded", "p_lost", "p_noninferior"):
                    adj = holm([ver[form][f][key] for f in fams_ok])
                    for f, v in zip(fams_ok, adj):
                        ver[form][f][key + "_holm"] = float(v)
                for f in fams_ok:
                    v = ver[form][f]
                    v["verdict"] = verdict(v["p_exceeded_holm"], v["p_lost_holm"], v["p_noninferior_holm"],
                                           v["seeds_better"], v["n_seeds"])
            for key, _ in MEANS:
                v = ver[form].get(key, {})
                if "p_exceeded" in v:
                    v["verdict"] = verdict(v["p_exceeded"], v["p_lost"], v["p_noninferior"], v["seeds_better"], v["n_seeds"])
        self.out["verdicts"] = ver
        # border rule: BE_H minus H, our seed mean, per family with a non-empty mask
        for fam in FAMS:
            if self.binfo["be"][fam]["copies"] == 0:
                self.out["border"][fam] = dict(delta=0.0, caveat=False, note="mask empty")
                continue
            dr = np.stack([ours[n][1]["BE_H"][fam] - ours[n][1]["H"][fam] for n in names])
            agg = dr[self.SI, np.arange(B_REPS)[:, None]].mean(1)
            d0 = float(np.mean([ours[n][2]["BE_H"][fam] - ours[n][2]["H"][fam] for n in names]))
            self.out["border"][fam] = dict(delta=d0, ci=[float(np.percentile(agg, 2.5)), float(np.percentile(agg, 97.5))],
                                           caveat=bool(d0 > BORDER_CAVEAT))
        be_f = [f for f in FAMS if self.binfo["be"][f]["copies"] > 0]
        self.out["forecasts"]["F3_border_rise_at_most_2_points"] = dict(
            delta={f: self.out["border"][f]["delta"] for f in be_f},
            verdict="held" if all(self.out["border"][f]["delta"] <= F3_LIMIT for f in be_f) else "falsified")
        # forecasts (registered before the read)
        f1 = {}
        zb = rels.get("madation_vitb16/v1")
        for fam in ("FaceMorpher", "OpenCV", "Webmorph"):
            our_rep = np.stack([ours[n][1]["S"][fam] for n in names])
            agg = our_rep[self.SI, np.arange(B_REPS)[:, None]].mean(1)
            diff = agg - zb[1]["S"][fam]
            f1[fam] = dict(diff=float(np.mean([ours[n][2]["S"][fam] for n in names]) - zb[2]["S"][fam]),
                           ci=[float(np.percentile(diff, 2.5)), float(np.percentile(diff, 97.5))],
                           trails=bool((1 + (diff <= 0).sum()) / (B_REPS + 1) <= ALPHA1))
        k1 = sum(v["trails"] for v in f1.values())
        self.out["forecasts"]["F1_trails_madation_vitb16_standard_landmark"] = dict(
            cells=f1, held_on=k1, verdict="held" if k1 >= 2 else "falsified")
        m2 = {fam: float(np.mean([ours[n][2]["S"][fam] for n in names])) for fam in ("MIPGAN_I", "MIPGAN_II")}
        self.out["forecasts"]["F2_mipgan_cells_look_good"] = dict(
            seed_mean_eer=m2, verdict="held" if all(v <= 0.10 for v in m2.values()) else "falsified", label=LAB_NS)
        # sentences (registered table, primary = H form, mean over the four families not shortcut-saturated)
        v = ver["H"]["mean4"]
        rel_txt = f"{v['best_name']}" if "best_name" in v else "the released detectors"

        def pct(x):
            return f"{100 * x:.1f}"
        span = f"{pct(v['diff'])} points [{pct(v['diff_ci'][0])}, {pct(v['diff_ci'][1])}]" if "diff" in v else ""
        span_abs = f"{pct(-v['diff'])} points [{pct(-v['diff_ci'][1])}, {pct(-v['diff_ci'][0])}]" if "diff" in v else ""
        base = ("On corrected MAD22 (seen during development; genuine side the 204 FRLL photos), against genuine photos "
                "with aligned-frame history (our aligner plus history), the frozen network's mean EER over OpenCV, "
                "Webmorph, MIPGAN-I and MIPGAN-II (FaceMorpher is solvable without morphs and excluded)")
        S = {"exceeded": f"{base} is lower than that of the best released detector ({rel_txt}) by {span_abs}, with {v.get('seeds_better')} of {v.get('n_seeds')} seeds individually lower.",
             "matched": f"{base} is within one point of the best released detector ({rel_txt}): difference {span} (non-inferiority margin +1.0 point).",
             "comparable, not separated": f"{base} is not separated from the best released detector ({rel_txt}): difference {span}.",
             "lost": f"{base} trails the best released detector ({rel_txt}) by {span}.",
             "lost (within the 1-point margin)": f"{base} trails the best released detector ({rel_txt}) by {span}, within the one-point margin."}
        self.out["outcome"] = v.get("verdict", "not available")
        self.out["sentences"]["primary"] = S.get(self.out["outcome"], "No comparison row: no sentence.")
        self.out["sentences"]["labels_always"] = [LAB_SEEN, LAB_NS + " (MIPGAN cells)",
                                                  "FaceMorpher: " + LAB_SAT,
                                                  "Frozen by the authors' decision on 13 Nov 2026; the registered freeze rule did not freeze any method.",
                                                  "For the released detectors, morphs are the raw benchmark files and the history-matched genuine photos pass through our aligner; each release is compared at the better of its raw-genuine and aligned-history forms."]
        v2 = ver["H"].get("mean2", {})
        self.out["sentences"]["landmark_only"] = (
            f"Landmark families only (OpenCV, Webmorph), history-matched: {v2.get('verdict', 'not available')} against "
            f"{v2.get('best_name', '-')}" + (" (differs from the primary verdict; the primary sentence must say so)."
                                              if v2.get("verdict") != v.get("verdict") else " (same as the primary)."))
        self.out["primary_and_landmark_differ"] = v2.get("verdict") != v.get("verdict")
        for form in ("S", "BE_H", "BE_S"):
            vv = ver[form].get("mean4", {})
            self.out["sentences"][f"secondary_{form}"] = f"{FORM_NAME[form]}: {vv.get('verdict', 'not available')} against {vv.get('best_name', '-')} (descriptive)."
        cav = [f for f, b in self.out["border"].items() if b["caveat"]]
        self.out["sentences"]["border"] = (f"Border caveat on {', '.join(cav)}: equalising the border raises the "
                                           f"frozen network's EER by more than 3 points there." if cav else
                                           "No family's EER rises by more than 3 points when the border is equalised.")
        return self.out


def h_ok(p):
    p = pathlib.Path(p)
    f = p.parent / (p.name + ".sha256")
    return f.exists() and f.read_text().split()[0] == sha(p)


def tables_md(o):
    L = [f"# Sealed MAD22 read ({o['read_id']}): tables", "", f"Outcome (primary): **{o.get('outcome')}**", "",
         o["sentences"].get("primary", ""), ""]
    if not o.get("cells"):
        return "\n".join(L)
    for form in FORMS:
        L += [f"## {FORM_NAME[form]}", "", "| Family | ours seeds EER % | mean (SD) | best release | its EER % | diff [95%] | verdict | labels |", "|---|---|---|---|---|---|---|---|"]
        for fam in FAMS + tuple(k for k, _ in MEANS):
            c = o["cells"][form][fam]; v = o["verdicts"][form].get(fam, {})
            seeds = ", ".join(f"{100 * x:.1f}" for x in c["ours_seed_eer"])
            dci = f"{100 * v['diff']:+.1f} [{100 * v['diff_ci'][0]:+.1f}, {100 * v['diff_ci'][1]:+.1f}]" if "diff" in v else "-"
            if c.get("n_differs"):
                L.append(f"| {fam} n | ours {c['n_ours']} | releases with another n: {c['n_differs']} | | | | | |")
            L.append(f"| {fam} | {seeds} | {100 * c['ours_mean_eer']:.1f} ({100 * c['ours_sd_eer']:.1f}) | {v.get('best_name', '-')} | "
                     f"{100 * v['best_eer']:.1f} | {dci} | {v.get('verdict', '-')} | {'; '.join(c['labels'][1:])} |" if "best_eer" in v else
                     f"| {fam} | {seeds} | {100 * c['ours_mean_eer']:.1f} ({100 * c['ours_sd_eer']:.1f}) | - | - | - | {v.get('verdict', '-')} | |")
        L.append("")
    return "\n".join(L)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--result", required=True); ap.add_argument("--pack", required=True)
    ap.add_argument("--release-existing", required=True); ap.add_argument("--selfmad"); ap.add_argument("--beststat")
    ap.add_argument("--thresholds", required=True); ap.add_argument("--pins", default=str(HERE / "final_pins.json"))
    ap.add_argument("--out", required=True); ap.add_argument("--tables", required=True)
    ap.add_argument("--marker", default=None)
    a = ap.parse_args()
    pins = json.load(open(a.pins))
    marker = pathlib.Path(a.marker or f"/mnt/t7/smad_next/FINAL/READ_ONCE_{pins['config']['read_id']}")
    if pathlib.Path(a.out).exists() or pathlib.Path(a.tables).exists():
        sys.exit("output exists: the reader runs once")
    real = str(pathlib.Path(a.result).resolve())  # guard amendment F3: the real result only with default pins and marker
    if real.startswith(("/mnt/t7/smad_next/FINAL/results/", "/mnt/t7/smad_next/vast/")) and \
            (a.marker is not None or pathlib.Path(a.pins).resolve() != (HERE / "final_pins.json").resolve()):
        sys.exit("the real result is read only with the default pins and marker")
    if marker.exists():
        sys.exit(f"read marker {marker} exists: the reader runs once")
    rd = Read(a)
    rd.load()                       # pins, sha256, every input parsed: a failure here uses up nothing
    rd.validate()
    try:
        marker.mkdir()
    except FileExistsError:
        sys.exit(f"read marker {marker} exists: the reader runs once")
    o = rd.run()

    def conv(x):
        if isinstance(x, dict):
            return {str(k): conv(v) for k, v in x.items()}
        if isinstance(x, (list, tuple)):
            return [conv(v) for v in x]
        if isinstance(x, (np.floating, np.integer)):
            return x.item()
        if isinstance(x, np.ndarray):
            return x.tolist()
        return x
    pathlib.Path(a.out).write_text(json.dumps(conv(o), indent=1))
    pathlib.Path(a.tables).write_text(tables_md(conv(o)))
    (marker / "done").write_text(f"{a.out} {sha(a.out)}\n")
    print("FINAL_READ outcome:", o.get("outcome"), "| out", a.out)


if __name__ == "__main__":
    if not sys.flags.isolated:
        sys.exit("run with python3 -I")
    main()
