import importlib.util, collections, csv
spec = importlib.util.spec_from_file_location("ar1pool", "/home/narolski/smad-next/src/AR1/pool.py")
P = importlib.util.module_from_spec(spec); spec.loader.exec_module(P)
cand = P.candidates()
print(len(cand))
pool = list(csv.DictReader(open("/home/narolski/smad-next/experiments/AR1/pool.csv")))
used = set(r["pid"] for r in pool) | set(r["B_pid"] for r in pool)
print("ar1 used persons", len(used))
by = collections.defaultdict(list)
for c in cand:
    by[(c["db"], c["subject"])].append(c)
free = {k: v for k, v in by.items() if f"{k[0]}:{k[1]}" not in used}
print("subjects", len(by), "free", len(free), collections.Counter(k[0] for k in free))
neu = {k: [c for c in v if c["neutral"]] for k, v in free.items()}
print("free with >=1 neutral", collections.Counter(k[0] for k, v in neu.items() if v))
print("env", collections.Counter(c["env"] for c in cand))
print("neutral photos per free person", collections.Counter(min(len(v),10) for v in neu.values()))
print(cand[0]); print([c for c in cand if c['db']=='feret'][0])
