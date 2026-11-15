"""G11 (registered in experiments/SA1_shortcut-audit-table/prereg.md): does a paired neutral/happy pool exist?
File names only, no image opened. Output: experiments/SA1_shortcut-audit-table/g11_expression_pool.json"""
import os, re, csv, json, sys, collections
CFD = "/mnt/t7/Datasety/downloads/ChicagoFaceDatabase/cfd/CFD Version 3.0.1/Images"
KDEF = "/mnt/t7/Datasety/downloads/KDEF_and_AKDEF/KDEF_and_AKDEF/KDEF"
out = {}
ex = collections.defaultdict(set); sub = {}
for root, _, files in os.walk(CFD):
    for f in files:
        m = re.match(r"(CFD(?:-INDIA|-MR)?)-(.+)-(N|HC|HO|A|F)\.jpg$", f)
        if m and "-" in m.group(2):
            person = m.group(1) + "-" + m.group(2).rsplit("-", 1)[0]
            ex[person].add(m.group(3)); sub[person] = m.group(1)
pool_cfd = {r["raw"] for r in csv.DictReader(open("/mnt/t7/smad_next/MS1/cfd/pool.csv"))}
both = [p for p, e in ex.items() if "N" in e and ({"HC", "HO"} & e)]
out["cfd"] = {"persons": len(ex), "persons_neutral_and_happy": len(both),
              "by_subset": dict(collections.Counter(sub[p] for p in both)),
              "happy_closed": sum("HC" in ex[p] for p in both), "happy_open": sum("HO" in ex[p] for p in both),
              "ms1_pool_images": len(pool_cfd),
              "ms1_pool_all_neutral": all(x.endswith("-N.jpg") for x in pool_cfd)}
kd = collections.defaultdict(set)
for root, _, files in os.walk(KDEF):
    for f in files:
        m = re.match(r"([AB])([FM]\d\d)(AF|AN|DI|HA|NE|SA|SU)(S|HL|HR|FL|FR)\.JPG$", f, re.I)
        if m and m.group(4).upper() == "S":
            kd[m.group(2).upper()].add((m.group(1).upper(), m.group(3).upper()))
kboth = [p for p, e in kd.items() if any(x[1] == "NE" for x in e) and any(x[1] == "HA" for x in e)]
out["kdef"] = {"persons_front": len(kd), "persons_neutral_and_happy_front": len(kboth),
               "same_session_pairs": sum(any((s, "NE") in kd[p] and (s, "HA") in kd[p] for s in "AB") for p in kboth)}
n = out["cfd"]["persons_neutral_and_happy"] + out["kdef"]["persons_neutral_and_happy_front"]
out["reading"] = "a paired expression pool exists" if max(out["cfd"]["persons_neutral_and_happy"], out["kdef"]["persons_neutral_and_happy_front"]) >= 100 or n >= 100 else "no usable pool"
out["note"] = "CFD and KDEF are MS1 held-out evaluation sources (never training); scoring there needs its own registration and the lead's approval. Happy images are not aligned yet (MS1 pools hold neutral images only)."
json.dump(out, open(sys.argv[1], "w"), indent=1); print(json.dumps(out, indent=1))
