import csv, collections, pathlib
EV="/home/narolski/mambamorph-code/smadcvpr_data/manifests/eval.csv"
rows=list(csv.DictReader(open(EV)))
seen=set()
for r in rows:
    k=(r["set"],r["family"],r["label"],r["variant"])
    if r["set"] in ("frllm","dim","mordiff") and r["variant"] in ("orig","resmatch") and k not in seen:
        seen.add(k); print(k, r["id"], r["path"], r["native_w"], r["native_h"])
