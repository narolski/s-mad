"""G9 (registered in experiments/SA1_shortcut-audit-table/prereg.md): partner structure of our training manifests.
Reads manifest rows and pair lists only (no image). Output: experiments/SA1_shortcut-audit-table/g9_partners.json"""
import csv, json, collections, sys, hashlib
T = "/mnt/t7/smad_next/"
MAN = {"A": "PN1/manifests/train_A.csv", "B": "PN1/manifests/train_B.csv", "Bn": "PN1/manifests/train_Bn.csv",
       "C": "PN1/manifests/train_C.csv", "Sb": "PN1/manifests2/train_Sb.csv", "Sp": "PN1/manifests_sp/train_Sp.csv",
       "SbM3": "MS1/manifests/train_SbM3.csv", "SbV": "MS1/manifests/train_SbV.csv"}
pairs = {}
for f in ("AF0/manifest.csv", "MS1/ffhq/lists/af0_pairs.csv"):
    for r in csv.DictReader(open(T + f)):
        pairs[r["id"]] = (r["pid_A"], r["pid_B"])
for r in csv.DictReader(open(T + "AR1/manifest.csv")):
    pairs["ar1_" + r["id"]] = (r["p1"], r["p2"])
for r in csv.DictReader(open(T + "AR1/manifest_splice2.csv")):
    pairs[r["id"]] = (r["p1"], r["p2"])
for r in csv.DictReader(open(T + "MS1/ffhq/lists/ladder.csv")):
    pairs["lad_" + r["pid"].replace(":", "_") + "_R4"] = (r["pid"], r["B_pid"])
MORPH = {"af0_u50", "af0_u5061", "lad_R4", "lad_S4"}
out = {"rule": "no SMDD-like partner structure if no contributor is in more than 1% of the unique morphs of any manifest",
       "smdd_reference": "5 second contributors for 15,000 training morphs", "manifests": {}}
for arm, f in MAN.items():
    rows = list(csv.DictReader(open(T + f)))
    ids = sorted({r["id"] for r in rows if r["kind"] in MORPH and r["label"] == "1"})
    src = sorted({i[:-5] if i.endswith("_fm61") else i for i in ids})  # stored copy -> its source morph
    missing = [i for i in src if i not in pairs]
    pp = [pairs[i] for i in src if i in pairs]
    second = collections.Counter(b for a, b in pp)
    anyc = collections.Counter(p for ab in pp for p in set(ab))
    n = len(pp)
    top2, topc = second.most_common(1)[0], anyc.most_common(1)[0]
    out["manifests"][arm] = {
        "manifest": T + f, "sha256": hashlib.sha256(open(T + f, "rb").read()).hexdigest(),
        "unique_morph_rows": len(ids), "unique_source_morphs": len(src), "unmapped": len(missing),
        "unmapped_examples": missing[:5], "distinct_second_contributors": len(second),
        "distinct_contributors_any_side": len(anyc),
        "max_share_one_second_contributor": round(top2[1] / n, 4), "max_second_count": top2[1],
        "max_share_one_contributor_any_side": round(topc[1] / n, 4), "max_any_count": topc[1],
        "share_morphs_with_second_contributor_in_10plus": round(sum(c for c in second.values() if c >= 10) / n, 4),
    }
worst = max(v["max_share_one_contributor_any_side"] for v in out["manifests"].values())
out["reading"] = "no SMDD-like partner structure" if worst <= 0.01 else "partner structure present"
out["worst_share_any_side"] = worst
json.dump(out, open(sys.argv[1], "w"), indent=1)
for k, v in out["manifests"].items():
    print(k, {x: v[x] for x in ("unique_source_morphs", "unmapped", "distinct_second_contributors",
          "max_share_one_contributor_any_side", "max_any_count", "share_morphs_with_second_contributor_in_10plus")})
print(out["reading"], worst)
