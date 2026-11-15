"""AG5 documentation check (CPU, re-read of ag5_ladder.json): how many separating networks separate one-identity renders
from FRLL photos at least half as strongly as the morphs (d' share R0->R2 >= 0.5), the review's corrected count."""
import json, collections
j = json.load(open("/home/narolski/smad-next/experiments/AG5/ag5_ladder.json"))
rel = ("SelfMAD release, own preprocessing", "MADation official ViT-B/16", "MADation official ViT-L/14")
c = collections.Counter(); per = collections.defaultdict(list)
for n in j["networks"]:
    sep = n["contrasts"]["bench R4 vs R0"]["ci95"][0] > 0.5
    sh = n["shares_R0_to_R2"].get("R2", {}).get("point")
    kind = "release" if n["row"] in rel else ("mixfacenet_release" if "MixFaceNet-MAD release" in n["row"] else "recipe")
    c[(kind, "separating", sep)] += 1
    if sep:
        c[(kind, "half_or_more", sh is not None and sh >= 0.5)] += 1
        lb = (n["shares_R0_to_R2"].get("R2", {}).get("ci95") or [None])[0]
        c[(kind, "half_or_more_lower95", lb is not None and lb >= 0.5)] += 1
        per[n["row"]].append(round(sh, 2) if sh is not None else None)
    mx = n["contrasts"]["main R2 vs R4 (morphs vs renders)"]["auc"]
    c["max_main"] = max(c.get("max_main", 0), mx)
print(dict(c)); print(dict(per))
json.dump({"counts": {str(k): v for k, v in c.items()}, "shares_by_row": per}, open("/home/narolski/smad-next/experiments/AG5/ag5_count.json", "w"), indent=1)
