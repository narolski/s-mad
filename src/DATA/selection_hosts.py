"""Selection host lists (lead, review 3d14793 finding 10). Lists only, CPU.

The 32 shape-linked test hosts are taken from partner_overlap_addendum.py itself (its `t32` = training hosts whose
pool partner is a test host; the linked test hosts are their partners B_pid). Writes, on /mnt/t7/smad_next/DATA/overlap/:
shape_linked_test_hosts.csv, selection_hosts_180.csv (100 development hosts + 80 test hosts clean of development),
selection_hosts_169.csv (the same without the shape-linked hosts among the 80), each with a .sha256 file; counts and
hashes to experiments/DATA_builds/selection_hosts.json.
  python3 -I selection_hosts.py
"""
import csv
import hashlib
import json
import pathlib
import runpy

HERE = pathlib.Path(__file__).resolve().parent
g = runpy.run_path(str(HERE / "partner_overlap_addendum.py"))
pool, role, t32 = g["pool"], g["role"], g["t32"]
O = pathlib.Path("/mnt/t7/smad_next/DATA/overlap")
R = pathlib.Path("/home/narolski/smad-next")
ls = {r["pid"]: r for r in csv.DictReader(open(R / "experiments/PN1_protocol-network-first-tests/split/ladder_split.csv"))}
pmap = {pool[h]["B_pid"]: h for h in t32}
linked = sorted(pmap)
clean = [l.strip() for l in open(O / "test_hosts_clean_of_dev.csv") if l.strip() and l.strip() != "host"]
dev = sorted(h for h in pool if role.get(h) == "dev")
inter = set(linked) & set(clean)


def w(name, rows, header):
    p = O / name
    with open(p, "w", newline="") as f:
        wr = csv.writer(f)
        wr.writerow(header)
        wr.writerows(rows)
    h = hashlib.sha256(p.read_bytes()).hexdigest()
    (O / (name + ".sha256")).write_text(f"{h}  {name}\n")
    return h


h1 = w("shape_linked_test_hosts.csv", [[x, pmap[x], int(x in clean)] for x in linked],
       ["test_host", "training_host_whose_partner_it_is", "clean_of_dev"])
sel = [[x, "dev"] for x in dev] + [[x, "test_clean_of_dev"] for x in sorted(clean)]
h2 = w("selection_hosts_180.csv", sel, ["host", "group"])
sel2 = [r for r in sel if r[0] not in inter]
h3 = w("selection_hosts_169.csv", sel2, ["host", "group"])
res = dict(derived_by="src/DATA/selection_hosts.py from partner_overlap_addendum.py t32",
           shape_linked_test_hosts=len(linked), all_read=sum(ls[x]["test_read"] == "1" for x in linked),
           shape_linked_sha256=h1, test_hosts_clean_of_dev=len(clean),
           clean_of_dev_sha256=hashlib.sha256((O / "test_hosts_clean_of_dev.csv").read_bytes()).hexdigest(),
           overlap_shape_linked_and_clean=len(inter), dev_hosts=len(dev), selection_180=len(sel), selection_180_sha256=h2,
           selection_169=len(sel2), selection_169_sha256=h3)
json.dump(res, open(R / "experiments/DATA_builds/selection_hosts.json", "w"), indent=1)
print(json.dumps(res, indent=1))
