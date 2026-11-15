"""Paired ranking [SPRINT5-1]. Pure-stdlib exposure planner; torch loaded lazily."""
import collections
import hashlib
import json
import random

ARMS = ('bce', 'paired_bce', 'paired_rank')


def pair_key(row):
    if row['kind'] not in ('lad_S3', 'lad_S4'):
        return None
    return row['path'].replace('lad_S3', 'lad_SX').replace('lad_S4', 'lad_SX').replace('_S3_', '_SX_').replace('_S4_', '_SX_')


def units(rows):
    groups = collections.defaultdict(lambda: {0: [], 1: []})
    for i, row in enumerate(rows):
        key = pair_key(row)
        if key is not None:
            label = int(row['label'])
            assert label == (row['kind'] == 'lad_S4')
            groups[key][label].append(i)
    paired, used = [], set()
    for key in sorted(groups):
        p, n = groups[key][1], groups[key][0]
        if p and n:
            # One instance per eligible host, remaining repeated positives are singles.
            paired.append((p[0], n[0]))
            used.update((p[0], n[0]))
    return paired + [(i,) for i in range(len(rows)) if i not in used]


def plan(rows, seed, steps, bs, arm):
    """All arms have exactly the same total row-index multiset, including tail."""
    if arm not in ARMS or bs < 2 or steps < 1:
        raise ValueError('invalid arm/steps/batch size')
    rng = random.Random(seed)
    pool, batches, batch = [], [], []
    base = units(rows)
    while len(batches) < steps:
        if not pool:
            pool = list(base)
            rng.shuffle(pool)
        item = pool.pop()
        if len(batch) + len(item) > bs:
            # A singleton always exists in the registered Sb manifest.
            j = next((j for j in range(len(pool)-1, -1, -1) if len(pool[j]) == 1), None)
            if j is None:
                refill = list(base)
                rng.shuffle(refill)
                pool.extend(refill)
                j = next((j for j in range(len(pool)-1, -1, -1) if len(pool[j]) == 1), None)
                if j is None:
                    raise ValueError('cannot fill batch without singleton')
            pool.append(item)
            item = pool.pop(j)
        batch.extend(item)
        if len(batch) == bs:
            batches.append(batch)
            batch = []
    flat = [i for b in batches for i in b]
    if arm == 'bce':
        random.Random(seed + 1000003).shuffle(flat)
        batches = [flat[i:i+bs] for i in range(0, len(flat), bs)]
    counts = collections.Counter(flat)
    # Canonical JSON makes the digest machine-independent.
    meta = {'arm': arm, 'seed': seed, 'steps': steps, 'bs': bs,
            'pair_units_per_cycle': sum(len(u) == 2 for u in base),
            'schedule_sha256': hashlib.sha256(json.dumps(batches, separators=(',', ':')).encode()).hexdigest(),
            'exposure_sha256': hashlib.sha256(json.dumps(sorted(counts.items()), separators=(',', ':')).encode()).hexdigest(),
            'row_occurrences': len(flat), 'unique_row_indices': len(counts)}
    return batches, meta


def rank_loss(logit, idx, rows, margin=1.0, return_count=False):
    """Mean softplus(m-zS4+zS3) over all within-batch matching instances."""
    import torch
    import torch.nn.functional as F
    groups = collections.defaultdict(lambda: {0: [], 1: []})
    for j, i in enumerate(idx.tolist()):
        row = rows[i]
        key = pair_key(row)
        if key is not None:
            groups[key][int(row['label'])].append(j)
    pos, neg = [], []
    for g in groups.values():
        for p in g[1]:
            for n in g[0]:
                pos.append(p)
                neg.append(n)
    if not pos:
        value = logit.sum() * 0
    else:
        value = F.softplus(margin - logit[pos] + logit[neg]).mean()
    return (value, len(pos)) if return_count else value


def loader(C, rows, res, bs, workers, seed, steps, arm, out):
    import pathlib
    import torch
    from torch.utils.data import DataLoader
    batches, meta = plan(rows, seed, steps, bs, arm)
    pathlib.Path(out).mkdir(parents=True, exist_ok=True)
    pathlib.Path(out, 'sprint_schedule.json').write_text(json.dumps(meta, indent=2) + '\n')
    ds = C.ImageItems([(r['path'], int(r['label'])) for r in rows], res,
                      aug='flip', with_index=True)
    return DataLoader(ds, batch_sampler=batches, num_workers=workers, pin_memory=True,
                      persistent_workers=workers > 0,
                      generator=torch.Generator().manual_seed(seed + 2))
