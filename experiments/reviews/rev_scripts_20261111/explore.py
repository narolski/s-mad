import csv, collections, numpy as np, pathlib
MAN="/mnt/t7/smad_heldout/a43/data/manifests/a43.csv"
rows=list(csv.DictReader(open(MAN)))
print(len(rows))
c=collections.Counter((r["source"],r["set"],r["family"],r["arm"],r["steps"],r["label"],r["variant"]) for r in rows)
for k,v in sorted(c.items()): print(k,v)
# expr dist
c2=collections.Counter((r["arm"],r["expr"]) for r in rows if r["source"]=="a43")
print(sorted(c2.items()))
# native size by arm
import statistics
for arm in sorted(set(r["arm"] for r in rows)):
    rr=[r for r in rows if r["arm"]==arm and r["source"]=="a43"]
    if rr:
        print(arm, len(rr), "native_w med", statistics.median(float(r["native_w"]) for r in rr), "ied med", statistics.median(float(r["ied"]) for r in rr if r["ied"]), "border", statistics.median(float(r["border_frac"]) for r in rr if r["border_frac"]), "lossless", collections.Counter(r["lossless"] for r in rr))
rr=[r for r in rows if r["source"]!="a43"]
for fam in sorted(set(r["family"] for r in rr)):
    q=[r for r in rr if r["family"]==fam]
    print(fam, len(q), "native_w med", statistics.median(float(r["native_w"]) for r in q if r["native_w"]), collections.Counter(r["variant"] for r in q))
z=np.load("/mnt/t7/smad_heldout/a43/a43_out/a43/madation_vitb16/rel/scores_a43.npz", allow_pickle=False)
print(z.files)
for k in z.files:
    print(k, z[k].shape, z[k].dtype, (z[k][:3] if z[k].ndim else z[k]))
z=np.load("/mnt/t7/smad_heldout/a43/a43_out/a43/selfmad_hrnet_w18/own/scores_a43.npz", allow_pickle=False)
print(z.files)
