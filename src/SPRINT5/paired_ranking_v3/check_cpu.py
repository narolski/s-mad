"""Exact exposure and source-patch smoke, no model/benchmark scoring."""
import collections
import csv
import json
import pathlib
import sys
import paired

rows = list(csv.DictReader(open(sys.argv[1])))
assert len(rows) == 8386
assert sum(len(u) == 2 for u in paired.units(rows)) == 124
report = {'checks': [], 'plans': []}
for seed in (501, 502, 503, 504, 505):
    base = None
    pair_sha = None
    for arm in paired.ARMS:
        batches, meta = paired.plan(rows, seed, 6250, 256, arm)
        counts = collections.Counter(i for batch in batches for i in batch)
        if base is None:
            base = counts
        assert counts == base
        assert len(batches) == 6250 and all(len(b) == 256 for b in batches)
        if arm != 'bce':
            if pair_sha is None:
                pair_sha = meta['schedule_sha256']
            assert pair_sha == meta['schedule_sha256']
        report['plans'].append(meta)
report['checks'].append('all15 full production schedules: exact row-index exposure equality, paired-arm identity')
print(json.dumps(report, indent=2))
