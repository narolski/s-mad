"""SM1 amendment A3 tests that need no new image.

  python3 -I tab.py tc        T-C: release CSVs vs folders (listed, present, label vs folder) -> RES/tc_files.json
  python3 -I tab.py lists     T-A / T-B scoring list -> OUT/flists/tab.csv (id, path, split, kind, partner)
  python3 -I tab.py read      T-A / T-B readings from OUT/p2scores/tab/scores_rel_<det>.npz -> RES/tab.json
T-A: threshold t = EER threshold of the training split (5,000 genuine vs 15,000 morphs, flag = logit >= t); miss rate
per second contributor and pooled per split; difference eval - train with 2,000 bootstrap draws over first
contributors within each split (seed 20261111). T-B: percentile of each partner render among 5,000 seeded
non-contributor source renders of its split (share of renders with a lower logit); top-10% count, binomial p.
"""
import collections
import csv
import json
import pathlib
import sys

import numpy as np

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import sm1_common as K  # noqa: E402
import sm1_stats as S  # noqa: E402

E = K.SMDD / "SMDD_release_evaluation"
SPL = {"train": dict(csv=K.SMDD / "SMDD_release_train/train.csv", root=K.SMDD / "SMDD_release_train",
                     m="m15k_t", g="os25k_bf_t", src=K.SRC_T),
       "eval": dict(csv=E / "evaluation.csv", root=E, m="m15k_e", g="os25k_bf_e", src=K.SMDD / "os25k_m_e")}
DETS = ("madation_vitb16", "madation_vitl14", "madation_fe_vitb16", "madation_fe_vitl14", "mixfacenet_mad_smdd",
        "madation_fs_vitb16", "madation_fs_vitl14")


def pairs_of(d):
    return [K.PAT.match(f).groups() for f in sorted(x.name for x in d.iterdir()) if K.PAT.match(f)]


def tc():
    out = {}
    for sp, s in SPL.items():
        rows = list(csv.DictReader(open(s["csv"])))
        listed = collections.Counter(r["image_path"] for r in rows)
        folder = {r["image_path"].split("/")[0] for r in rows}
        files = {f"{d}/{x.name}" for d in (s["m"], s["g"]) for x in (s["root"] / d).iterdir() if x.suffix == ".png"}
        lab = collections.Counter((r["image_path"].split("/")[0], r["label"]) for r in rows)
        out[sp] = dict(csv=str(s["csv"]), rows=len(rows), duplicates=sum(v > 1 for v in listed.values()),
                       folders=sorted(folder), files_on_disk=len(files), listed_missing=len(set(listed) - files),
                       on_disk_not_listed=len(files - set(listed)), label_by_folder={f"{a}:{b}": v for (a, b), v in
                                                                                      sorted(lab.items())},
                       morph_names_parsed=len(pairs_of(s["root"] / s["m"])))
    json.dump(out, open(K.RES / "tc_files.json", "w"), indent=1)
    print(json.dumps(out, indent=1))


def lists():
    rows = []
    for sp, s in SPL.items():
        pr = pairs_of(s["root"] / s["m"])
        for a, b in pr:
            rows.append(dict(id=f"tA:{sp}:m:{a}_{b}", path=str(s["root"] / s["m"] / f"morphed_{a}_{b}.png"), split=sp,
                             kind="morph", key=a, partner=b))
        g = sorted(x.name for x in (s["root"] / s["g"]).iterdir() if x.suffix == ".png")
        for n in sorted(np.random.default_rng(K.SEED + 21).choice(g, size=5000, replace=False).tolist()):
            rows.append(dict(id=f"tA:{sp}:g:{n[:-4]}", path=str(s["root"] / s["g"] / n), split=sp, kind="genuine",
                             key="", partner=""))
        contrib = {x for p in pr for x in p}
        parts = sorted({b for _, b in pr})
        src = sorted(x.name[:-4] for x in s["src"].iterdir() if x.suffix == ".png" and x.name[:-4] not in contrib)
        for n in sorted(np.random.default_rng(K.SEED + 22).choice(src, size=5000, replace=False).tolist()):
            rows.append(dict(id=f"tB:{sp}:r:{n}", path=str(s["src"] / f"{n}.png"), split=sp, kind="render", key="",
                             partner=""))
        for n in parts:
            rows.append(dict(id=f"tB:{sp}:p:{n}", path=str(s["src"] / f"{n}.png"), split=sp, kind="partner", key="",
                             partner=n))
    with open(K.OUT / "flists/tab.csv", "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0]))
        w.writeheader()
        w.writerows(rows)
    print("tab.csv", len(rows), collections.Counter((r["split"], r["kind"]) for r in rows))


def read():
    from scipy.stats import binom
    import os
    tl = os.environ.get("TABLIST", "tab")                    # A8: tab_sub (DGX subsample) or tab (full set)
    meta = list(csv.DictReader(open(K.OUT / f"flists/{tl}.csv")))
    res = {}
    for det in DETS:
        f = K.OUT / f"p2scores/{tl}" / f"scores_rel_{det}.npz"
        if not f.exists():
            continue
        zf = np.load(f, allow_pickle=False)
        z = {str(i): float(v) for i, v in zip(zf["id"], zf["logit_noTTA"])}
        o = {}
        sel = lambda sp, kind: [r for r in meta if r["split"] == sp and r["kind"] == kind and r["id"] in z]  # noqa
        g_t, m_t = sel("train", "genuine"), sel("train", "morph")
        gt = np.array([z[r["id"]] for r in g_t])
        mt = np.array([z[r["id"]] for r in m_t])
        eer_t, thr = S.eer_unit(gt, mt)
        o["train"] = dict(eer=eer_t, thr=thr, n_genuine=len(gt), n_morph=len(mt))
        rng = np.random.default_rng(K.SEED)
        boots = {}
        for sp in ("train", "eval"):
            mm = sel(sp, "morph")
            gg = np.array([z[r["id"]] for r in sel(sp, "genuine")])
            zz = np.array([z[r["id"]] for r in mm])
            miss = (zz < thr).astype(float)
            keys = np.array([r["key"] for r in mm])
            uk, inv = np.unique(keys, return_inverse=True)
            C = rng.multinomial(len(uk), np.full(len(uk), 1 / len(uk)), size=2000)[:, inv]
            boots[sp] = (C * miss).sum(1) / C.sum(1)
            per = {}
            for p in sorted({r["partner"] for r in mm}):
                ix = np.array([r["partner"] == p for r in mm])
                per[p] = dict(n=int(ix.sum()), miss=round(float(miss[ix].mean()) * 100, 3))
            e, _ = S.eer_unit(gg, zz)
            o[sp + "_at_train_thr"] = dict(miss_pooled=round(float(miss.mean()) * 100, 3),
                                           miss_ci=[round(100 * x, 3) for x in S.ci(boots[sp])],
                                           false_alarm_genuine=round(float((gg >= thr).mean()) * 100, 3),
                                           eer_own_split=round(e, 3), per_partner=per)
        d = 100 * (boots["eval"] - boots["train"])
        o["miss_eval_minus_train"] = dict(diff=round(o["eval_at_train_thr"]["miss_pooled"] -
                                                     o["train_at_train_thr"]["miss_pooled"], 3),
                                          ci=[round(x, 3) for x in S.ci(d)],
                                          within_1_point=bool(abs(o["eval_at_train_thr"]["miss_pooled"] -
                                                                  o["train_at_train_thr"]["miss_pooled"]) <= 1))
        for sp in ("train", "eval"):
            rr = np.array([z[r["id"]] for r in sel(sp, "render")])
            pp = [(r["partner"], z[r["id"]]) for r in sel(sp, "partner")]
            pct = [(n, float((rr < v).mean())) for n, v in pp]
            k = sum(p >= 0.9 for _, p in pct)
            o[f"rank_{sp}_partners"] = dict(n_renders=len(rr), percentiles={n: round(p, 4) for n, p in pct},
                                            in_top10=k, p_binom_ge=float(binom.sf(k - 1, len(pct), 0.1)),
                                            render_logit_mean=float(rr.mean()))
        res[det] = o
        print(det, json.dumps({k: (v if not isinstance(v, dict) or "per_partner" not in v else
                                   {kk: vv for kk, vv in v.items() if kk != "per_partner"}) for k, v in o.items()})[:900])
    json.dump(res, open(K.RES / f"{tl}.json", "w"), indent=1)


if __name__ == "__main__":
    if not sys.flags.isolated:
        sys.exit("run with python3 -I")
    {"tc": tc, "lists": lists, "read": read}[sys.argv[1]]()
