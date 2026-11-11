"""AD1b step 1 (as run 11 Nov 2026 ~15:14 CET, inline): select the first 200 hosts of AR1's pool by sha1(pid) and
byte-copy their H, S, B images for the unchanged DiffAE align.py. Refuses nothing; rerun only into an empty pool_in."""
import csv, hashlib, shutil, pathlib
D = pathlib.Path('/mnt/t7/smad_next/AD1b')
(D / 'pool_in').mkdir(parents=True, exist_ok=True)
r = sorted(csv.DictReader(open('/mnt/t7/smad_next/AR1/pool.csv')), key=lambda x: hashlib.sha1(x['pid'].encode()).hexdigest())[:200]
out = []
for x in r:
    tag = x['pid'].replace(':', '_')
    for role in ('H', 'S', 'B'):
        shutil.copyfile(x[role], D / 'pool_in' / f"{tag}_{role}.png")
    out.append({'pid': x['pid'], 'tag': tag, 'db': x['db'], 'H': x['H'], 'S': x['S'], 'B': x['B'], 'B_pid': x['B_pid']})
with open(D / 'pool_selection.csv', 'w', newline='') as f:
    w = csv.DictWriter(f, fieldnames=list(out[0])); w.writeheader(); w.writerows(out)
print(len(out))
