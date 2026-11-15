import csv, collections, re
M="/mnt/t7/smad_next/PN1/manifests/"
def db(r):
    i=r["id"].lower()
    if i.startswith(("train_frgc","val_frgc")): return "frgc"
    if i.startswith(("train_feret","val_feret")): return "feret"
    m=re.search(r"(frgc|feret)[:_-]?\d", i) or re.search(r"(frgc|feret)", r["src"].lower().replace("frgcferet",""))
    return m.group(1) if m else "?"
for arm in "AB":
    src={r["id"]:r for r in csv.DictReader(open(M+f"src_{arm}.csv"))}
    rows=list(csv.DictReader(open(M+f"train_{arm}.csv")))
    d=collections.Counter((db(src[r["id"]]),r["label"]) for r in rows)
    print(arm, dict(d), {k: round(d[(k,"1")]/max(1,d[(k,"0")]+d[(k,"1")]),3) for k in ("frgc","feret","?")})
