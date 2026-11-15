"""Standing adversary (ADV), amendment 3 (post hoc): lcomb_bal, a history-balanced subset of FFHQ landmark_combined built
from existing images only (no image operation; a row selection).

Matching variables (never a face-containing score, which would match blending away):
  s  = logit of the cross-fitted surround score: gbt (the floor's boosted trees; a first try with logreg left the gbt
       surround floor at 0.80 and is recorded in the README) on the 18
       SURR region measures (feats.regional; cue_floor's border ring, black pixels and their 2-px edge excluded),
       held-out by the ADV person folds;
  e  = pre_ied (eye distance of the image that entered alignment; ffhqm_meta.csv sidecar, development set).
Greedy 1:1 nearest-neighbour matching without replacement (morphs in numpy default_rng(20261116) order), distance
|ds|/sd(s) + |de|/sd(e), caliper c on each standardised difference (start 0.2). Then the cross-fitted surround floor
(single, logreg, gbt on SURR) and file floor (the same on the PNG size and container values) are refitted on the matched
rows; while any of them is above 0.60 the surround score is re-estimated on the matched rows, c is multiplied by 0.7 and
the matching is repeated within the current matched rows (at most 12 rounds). Output: floors/lcomb_bal_rows.csv
(id, label, pair) and floors/lcomb_bal_build.json (history). The contrast `lcomb_bal` then gets the full floor report.
"""
import csv
import json
import sys

import numpy as np

sys.path.insert(0, "/home/narolski/smad-next/src/adversary")
import contrasts as C  # noqa: E402
import floor as FL  # noqa: E402
import run_floors as RF  # noqa: E402

META = "/mnt/t7/smad_heldout/ffhq_morphs/manifests/ffhqm_meta.csv"


def surround_X(rl):
    rg = RF.regmap()
    import feats as F
    cols = [i for i, n in enumerate(F.REGION_NAMES) if n.startswith("SURR:")]
    return np.stack([rg[p][cols] for _, p, _, _ in rl])


def file_X(rl):
    X, nm = RF.X_of(rl)
    cols = [i for i, n in enumerate(nm) if n in RF.FILE_SIZE]
    return X[:, cols]


def floors3(X, y, persons):
    g = FL.components(persons)
    fl = FL.folds(y, g)
    out = {}
    for k in ("single", "logreg", "gbt"):
        s, _ = FL.crossfit(X, y, g, k, fl)
        out[k] = FL.auc(s, y)
    return out


def surround_score(X, y, persons, kind="gbt"):
    g = FL.components(persons)
    s, _ = FL.crossfit(X, y, g, kind, FL.folds(y, g))
    s = np.clip(s, 1e-6, 1 - 1e-6)
    return np.log(s / (1 - s))


def match(idx_pos, idx_neg, s, e, cal, rng):
    sd_s, sd_e = s.std() + 1e-9, e.std() + 1e-9
    free = set(idx_neg.tolist())
    pairs = []
    for i in rng.permutation(idx_pos):
        cand = np.array(sorted(free))
        if not len(cand):
            break
        ds = np.abs(s[cand] - s[i]) / sd_s
        de = np.abs(e[cand] - e[i]) / sd_e
        ok = (ds <= cal) & (de <= cal)
        if not ok.any():
            continue
        d = np.where(ok, ds + de, np.inf)
        j = int(cand[int(np.argmin(d))])
        pairs.append((int(i), j))
        free.discard(j)
    return pairs


def main():
    rl = C.build("lcomb")
    meta = {r["id"]: float(r["pre_ied"]) for r in csv.DictReader(open(META))}
    e_all = np.array([meta[i.replace("lcomb_", "")] for i, *_ in rl])
    y_all = np.array([l for _, _, l, _ in rl])
    S_all, F_all = surround_X(rl), file_X(rl)
    persons = [p for *_, p in rl]
    keep = np.arange(len(rl))
    rng = np.random.default_rng(20261116)
    cal, hist = 0.2, []
    for it in range(12):
        yk = y_all[keep]
        pk = [persons[k] for k in keep]
        s = surround_score(S_all[keep], yk, pk)
        pos, neg = np.where(yk == 1)[0], np.where(yk == 0)[0]
        pairs = match(pos, neg, s, e_all[keep], cal, rng)
        if len(pairs) < 50:
            hist.append(dict(round=it, caliper=cal, n_pairs=len(pairs), stopped="fewer than 50 pairs"))
            print("stopped: fewer than 50 pairs", flush=True)
            break
        sel = np.array(sorted([a for a, _ in pairs] + [b for _, b in pairs]), int)
        keep2 = keep[sel]
        y2 = y_all[keep2]
        p2 = [persons[k] for k in keep2]
        fs = floors3(S_all[keep2], y2, p2)
        ff = floors3(F_all[keep2], y2, p2)
        rec = dict(round=it, caliper=cal, n_pairs=len(pairs), surround_floor=fs, file_floor=ff)
        hist.append(rec)
        print(json.dumps(rec), flush=True)
        pair_of = {}
        for q, (a_, b_) in enumerate(pairs):
            pair_of[int(keep[a_])] = q
            pair_of[int(keep[b_])] = q
        keep = keep2
        if max(fs.values()) <= 0.60 and max(ff.values()) <= 0.60:
            break
        cal *= 0.7
    last = [h for h in hist if "surround_floor" in h][-1]
    ok = max(last["surround_floor"].values()) <= 0.60 and max(last["file_floor"].values()) <= 0.60
    # pair ids for the final rows
    out_rows = [(rl[k][0], int(y_all[k]), pair_of[int(k)]) for k in keep]
    with open(RF.FDIR / "lcomb_bal_rows.csv", "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["id", "label", "pair"])
        w.writerows(out_rows)
    rg = RF.regmap()
    import feats as F
    fc = [i for i, n in enumerate(F.REGION_NAMES) if n.startswith("FACE:")]
    Ff = np.stack([rg[rl[k][1]][fc] for k in keep])
    face = floors3(Ff, y_all[keep], [persons[k] for k in keep])
    n_m = int(y_all[keep].sum())
    (RF.FDIR / "lcomb_bal_build.json").write_text(json.dumps(dict(
        converged=ok, n_morph=n_m, n_genuine=int(len(keep) - n_m), rounds=hist, final_surround_floor=last["surround_floor"],
        final_file_floor=last["file_floor"], final_face_floor=face,
        below_150_per_class=bool(n_m < 150)), indent=1))
    print("converged", ok, "rows", len(keep), flush=True)


if __name__ == "__main__":
    if not sys.flags.isolated:
        sys.exit("run with python3 -I")
    main()
