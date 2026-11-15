import json, collections
d = json.load(open("/home/narolski/smad-next/experiments/AG5/ag5_ladder.json"))
print(d["G-b"], d["n"], d["B"], len(d["networks"]))
rowc = collections.OrderedDict()
arm_counts = collections.Counter()
for n in d["networks"]:
    c = n["contrasts"]; b = c["bench R4 vs R0"]; m = c["main R2 vs R4 (morphs vs renders)"]; x = c.get("main X4: R2x4 vs R4")
    sh = n["shares_R0_to_R2"].get("R2"); 
    sep = b["ci95"][0] > 0.5
    arm1 = sh is not None and sh.get("ci95") is not None and sh["ci95"][0] >= 0.5
    arm2 = m["fold"] < 0.60 and m["fold_ub95"] < 0.65
    v = n["verdict_main_H3renders"]
    rowc.setdefault(n["row"], []).append((n["network"][-28:], round(b["auc"],3), [round(q,3) for q in b["ci95"]], round(c["R0->R2 (renders vs camera)"]["auc"],3), round(m["auc"],3), [round(q,3) for q in m["ci95"]], None if x is None else round(x["auc"],3), None if sh is None or sh["point"] is None else round(sh["point"],2), sep, arm1, arm2, v, n["verdict_main_X4"]))
    if sep: arm_counts[(n["row"].split("|")[0].strip()[:30], "share-arm" if arm1 else "", "fold-arm" if arm2 else "", v[:20])] += 1
tot = collections.Counter()
for r, L in rowc.items():
    print("\n", r)
    for t in L: print("   ", t)
    for t in L:
        tot[("sep" if t[8] else "nosep", t[11][:22])] += 1
print(tot)
for k,v in sorted(arm_counts.items()): print(k, v)
# main contrast direction: how many separating nets have R2vsR4 significantly below / above 0.5
lo=hi=ns=0; mx=0
for n in d["networks"]:
    m=n["contrasts"]["main R2 vs R4 (morphs vs renders)"]; mx=max(mx,m["auc"])
    if m["ci95"][1]<0.5: lo+=1
    elif m["ci95"][0]>0.5: hi+=1
    else: ns+=1
print("R2vsR4: CI below 0.5:",lo," CI above 0.5:",hi," includes 0.5:",ns," max",mx)
lo=hi=ns=0
for n in d["networks"]:
    m=n["contrasts"].get("main X4: R2x4 vs R4")
    if m is None: continue
    if m["ci95"][1]<0.5: lo+=1
    elif m["ci95"][0]>0.5: hi+=1
    else: ns+=1
print("X4 R2x4vsR4: CI below 0.5:",lo," above:",hi," includes:",ns)
