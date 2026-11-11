import csv, collections, numpy as np, pathlib
p = pathlib.Path("/mnt/t7/smad_heldout/a43/data/manifests/a43.csv")
rows = list(csv.DictReader(open(p)))
print(rows[0].keys())
c = collections.Counter((r["source"], r.get("arm"), r.get("family")) for r in rows)
for k,v in sorted(c.items(), key=str): print(k, v)
E = [r for r in rows if r["source"]=="a43" and r["arm"]=="E"]
print(E[0])
for key in ("native_w","native_h","file_bytes","ied"):
    if key in E[0]:
        x = np.array([float(r[key]) for r in E]); print("E", key, np.percentile(x,[0,50,100]))
z = np.load("/mnt/t7/smad_next/EV1/feat.npz", allow_pickle=False)
print(z.files[:60])
for k in z.files[:60]:
    print(k, z[k].shape, z[k].dtype)
G = list(csv.DictReader(open("/home/narolski/mambamorph-code/smadcvpr_data/manifests/gtest.csv")))
c = collections.Counter((r["set"], r["family"], r["variant"], r["label"]) for r in G)
for k,v in sorted(c.items()): print(k, v)
for fam in ("fei_bona_neutral","fei_bona_smiling"):
    rr = [r for r in G if r["family"]==fam]
    print(rr[0])
    for key in ("native_w","native_h","file_bytes","ied"):
        x = np.array([float(r[key]) for r in rr]); print(fam, key, np.percentile(x,[0,25,50,75,100]))
