"""Fail-closed implementation of approved NEXT selection rule version 3.

Production entry points require a committed, independently reviewed admission
manifest and exact input/support/code pins in a clean checkout. This module has
no import-time data reads. Tests call its pure functions on synthetic fixtures.
Native RZ1 and registered SbFM/E3 fit/supplement formats are supported.
GX and fresh native sources remain registration-blocked before member access.
"""
import argparse
import csv
import datetime as dt
import hashlib
import importlib.util
import io
import json
import math
import os
import pathlib
import re
import subprocess
import sys
import tarfile

import numpy as np

ORDER = ('SbFM', 'GX', 'SbMR', 'SbM', 'Sb512', 'SbMR512', 'Sbc', 'DINOv3')
RZ = {'SbMR', 'SbM', 'Sb512', 'SbMR512', 'Sbc'}
MIX = {'SbMR', 'SbM', 'SbMR512'}
DEADLINE = dt.datetime.fromisoformat('2026-11-15T18:00:00+01:00')
BINDING = 'dbeb9404b2e1bd0db1ef8a60b18e18457e324af2'
RULE = 'experiments/NEXT_method-selection-rule/prereg_draft_v3.md'
NB = 2000
ONCE_ROOT = pathlib.Path('/mnt/t7/smad_next/NEXT')
FORBIDDEN = ('fst', 'valx', 'a12sp', 'a12-sp', 'train90', 'val10')
PINS = dict(pack_sha256='96c31ae29c4118947e3fd0a7a97600805cbfa5a82369c8ecbc6ee3d6349f2004',
            ab1_overlay='171fdb213444442762d4a716b7470dd885cd5879ba9ddda0c542060af4b4d149',
            ab1x_overlay='e5886e72622b618cb260689820efea861b63b061749db561d256ad57116f819c',
            tt1='2109f742b0378c188f394a3b26c363ef2ffb0ea43eab78ecea7674884022c554',
            meds='3fb917b226c6d31fab176a4d8fdd5d6e6b22b8274cc091591f444e623a87ab61',
            rz1_overlay='dccf37d20ca0074780a15d99012c3302f52e4ad5a7773b66981b5d316276d383')
ARM_SPEC = {
    'A0': ('train_A.csv', 'fixed:pil_bilinear', 224, 256, 1),
    'Sb0': ('train_Sb.csv', 'fixed:pil_bilinear', 224, 256, 1),
    'SbM': ('train_Sb.csv', 'mix', 224, 256, 1),
    'SbMR': ('train_Sb.csv', 'mixR', 224, 256, 1),
    'A512': ('train_A.csv', 'fixed:pil_bilinear', 512, 64, 4),
    'Sb512': ('train_Sb.csv', 'fixed:pil_bilinear', 512, 64, 4),
    'SbMR512': ('train_Sb.csv', 'mixR', 512, 64, 4),
    'Sbc': ('train_Sb.csv', 'crop:144:160', 224, 256, 1),
    'Ac': ('train_A.csv', 'crop:144:160', 224, 256, 1),
}
AB1_SB_SOURCE_PINS = {
    408: 'a84b551f2f18c51898213f4932965f89b88fe7eac0398ac28cd37c04e4b3b0aa',
    409: 'dd575673e437b2ad34aa50e9f2785ee2c17a1b89b424b2324b4beb6ae5f32352',
    410: '40b47155a7a1ca1a13bc9ae101b135b3d0730d70d968af6e7ad235453ca96875',
    411: '764a4e5e6a5692cb974a15957cf55ac88d475a519381d8ef827f932791144aa6',
    412: 'c1e0f081194ffb46395e896bd872f509a930967b8ed5da101823d95659070c84',
}
NATIVE_CODE = pathlib.Path(__file__).with_name('native_adapters.py')
SBFM_CONFIG_SHA256 = '4ec95da9ac37d3f958124b5d5cb72a812497601b3acaad4d264bc00e41294ddf'
NATIVE_PRODUCERS = {
    'sbfm_supplement': ('src/recovery_20261114/sbfm_supplement/run_supplement.py',
                        '2dd5535b64901691176f0268130fecc48f34145709d7081bde8f9f9cbb41474b'),
    'dinov3_w2': ('src/BB2/wcss/bb2l_w2.sbatch',
                 'b44834782a552ab87c66518fa90563ce804963f763b2c54d0b6642d3120db507'),
}
NATIVE_MANIFEST_PINS = {
    'ab1_eval': '93a5ba234f91e57951829c5536fabbe0f792ee4ad0a293f074aaca72f7465bd5',
    'fm_eval': '5257fb63f321612c39f8da6613989976450a68cd97c0b55d51667b554995d35f',
    'fs_eval': 'f0f29f2201bd3a1dc67f24772347960ba7a383a9e5c1fa8920d0cc1b854a5045',
    'train_A': 'af070a60529db3e8636d31a62ee613faa6ecdb106d20f5c855eb106ee8eb12ca',
    'train_Sb': '2cf3fda3affc8dd3d1574857f494037ea0382c8a2d314754b615686401b7fa4a',
    'train_SbFM': '1231204496664287e4513ac4cf004156a5140386987e3b6cc8a83084c242e491',
}


def native_module():
    spec = importlib.util.spec_from_file_location('next_native', NATIVE_CODE)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class Refusal(RuntimeError):
    """Global precondition failed: never reinterpret this as scientific failure."""


class SeedUnavailable(RuntimeError):
    """Registered per-network provenance/gate/finite-data failure."""


def need(ok, message):
    if not ok:
        raise Refusal(message)


def checked_path(path):
    p = pathlib.Path(path)
    need(not any(x in str(p).lower() for x in FORBIDDEN), 'forbidden source path')
    return p


def digest(path):
    h = hashlib.sha256()
    with checked_path(path).open('rb') as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b''):
            h.update(chunk)
    return h.hexdigest()


def read_json(path):
    return json.loads(checked_path(path).read_text())


def read_csv(path):
    with checked_path(path).open() as f:
        return list(csv.DictReader(f))


def unique_rows(rows):
    m = {r['id']: r for r in rows}
    need(len(m) == len(rows), 'duplicate input row IDs')
    return m


def ci(values):
    a = np.asarray(values, float)
    a = a[np.isfinite(a)]
    need(len(a) > 0, 'no finite bootstrap replicates')
    return [float(x) for x in np.percentile(a, [2.5, 97.5])]


def auc(scores, labels):
    """Tie-aware rank AUC, algebraically identical to reviewed check._auc."""
    x, y = np.asarray(scores, float), np.asarray(labels, int)
    need(len(x) == len(y) and np.isfinite(x).all(), 'AUC data invalid')
    need(set(y) == {0, 1}, 'AUC requires both classes')
    order = np.argsort(x, kind='mergesort')
    xx, yy = x[order], y[order]
    starts = np.r_[0, np.flatnonzero(xx[1:] != xx[:-1]) + 1]
    pos = np.add.reduceat(yy.astype(float), starts)
    total = np.diff(np.r_[starts, len(x)])
    neg = total - pos
    return float(np.sum(pos * (np.cumsum(neg) - .5 * neg)) / (pos.sum() * neg.sum()))


def within_d(scores, labels, values):
    """BD1 rule: recompute quintile edges on these drawn rows, ≥10/class."""
    x, y, d = np.asarray(scores, float), np.asarray(labels, int), np.asarray(values, float)
    need(len(x) == len(y) == len(d) and np.isfinite(d).all() and (d > 0).all(), 'invalid D rows')
    z = np.log(d)
    q = np.searchsorted(np.quantile(z, [.2, .4, .6, .8]), z, side='right')
    numerator = denominator = covered = 0
    for k in range(5):
        ix = q == k
        p, n = int(y[ix].sum()), int(ix.sum() - y[ix].sum())
        if p >= 10 and n >= 10:
            numerator += p * n * auc(x[ix], y[ix])
            denominator += p * n
            covered += int(ix.sum())
    return (float(numerator / denominator) if denominator else float('nan'), covered / len(y))


class Contrast:
    def __init__(self, rows, *, stratified=False, n_boot=NB):
        self.rows = rows
        self.ids = [r['id'] for r in rows]
        unique_rows(rows)
        self.y = np.array([int(r['label']) for r in rows])
        self.d = np.array([float(r['D']) for r in rows]) if stratified else None
        groups = np.array([str(r['component']) for r in rows])
        # Numeric component ordering matches reviewed np.unique(integer groups).
        try:
            groups = groups.astype(int)
        except ValueError:
            pass
        ug = np.unique(groups)
        index = {g: np.flatnonzero(groups == g) for g in ug}
        rng = np.random.default_rng(20261115)
        self.draws = [np.concatenate([index[g] for g in rng.choice(ug, len(ug), replace=True)]) for _ in range(n_boot)]
        self.stratified = stratified
        self._cache = {}

    def vector(self, values):
        try:
            x = np.array([values[i] for i in self.ids], float)
        except KeyError as e:
            raise SeedUnavailable('required contrast rows missing') from e
        if not np.isfinite(x).all():
            raise SeedUnavailable('required contrast scores non-finite')
        return x

    def statistic(self, x, indices=None):
        ii = np.arange(len(self.y)) if indices is None else indices
        if self.stratified:
            return within_d(x[ii], self.y[ii], self.d[ii])[0]
        return auc(x[ii], self.y[ii]) if set(self.y[ii]) == {0, 1} else float('nan')

    def values(self, vector):
        key = np.asarray(vector, float).tobytes()
        if key not in self._cache:
            self._cache[key] = self.statistic(vector), np.array([self.statistic(vector, ii) for ii in self.draws])
        return self._cache[key]


def paired_mean_interval(candidate, comparator):
    """All seeds share the same row draws; no ensemble scores are formed."""
    return ci(np.mean([a - b for a, b in zip(candidate, comparator)], axis=0))


def unpaired_seed_component_interval(candidate, comparator, seed=20261115):
    """DINOv3: independent seed resampling plus shared component draw per replicate."""
    a, b = np.asarray(candidate), np.asarray(comparator)
    need(a.ndim == b.ndim == 2 and a.shape[1] == b.shape[1], 'bootstrap arrays differ')
    # Independent seed-resampling stream; component replicates already use
    # default_rng(20261115), so resetting that same stream here would couple them.
    rng = np.random.default_rng(np.random.SeedSequence(seed).spawn(1)[0])
    out = []
    for j in range(a.shape[1]):
        ia = rng.integers(0, len(a), len(a))
        ib = rng.integers(0, len(b), len(b))
        out.append(float(np.mean(a[ia, j]) - np.mean(b[ib, j])))
    return ci(out)


def four_of_five(values):
    return sum(bool(x) for x in values) >= 4


def decide(criteria):
    """Pure fixed-order decision: observed gain is never a tie breaker."""
    for arm in ORDER:
        r = criteria.get(arm)
        if r and r.get('status') == 'read' and all(r.get('criteria', {}).get(k) is True for k in 'abcdef'):
            return arm
    return 'Sb'


def evaluate_criteria(per_seed, *, resize=False, kernel=False, unpaired=False):
    """Inclusive unrounded bars; every missing/failed seed stays in the 5 denominator."""
    valid = [v for v in per_seed.values() if v.get('valid')]
    if len(valid) < 4:
        return {k: False for k in 'abcdef'}, {'status': 'not read (too few seeds)', 'read_seeds': len(valid), 'denominator': 5}
    full = float(np.mean([v['lcomb_gain'] for v in valid]))
    ladder = float(np.mean([v['ladder_gain'] for v in valid]))
    matched = float(np.mean([v['matched_gain'] for v in valid]))
    gain = full >= .025 and sum(v['lcomb_gain'] > 0 for v in valid) >= 4
    if resize:
        gain = gain and all(v.get('refit_max_abs') is not None for v in valid)
        gain = gain and full > max((v.get('refit_max_abs') or 0) for v in valid)
    aa = bool(gain and ladder >= -.02 and all(v['ladder_gain'] >= -.06 for v in valid)
              and matched >= .015 and matched >= .5 * full and all(v['floors_printed'] for v in valid))
    # V3(b): the SAME >=4 seeds must satisfy the storage-rise bound at BOTH
    # sizes. The plain control and H-new-1 retain their own registered per-size
    # counts; those are not interchangeable with the joint challenger bound.
    bb = four_of_five([v.get('valid') and all(v['storage_pass'][z] for z in ('fm61', 'amsl112'))
                       for v in per_seed.values()])
    bb = bb and all(four_of_five([v.get('valid') and v['control_pass'][size]
                                for v in per_seed.values()]) for size in ('fm61', 'amsl112'))
    bb = bb and all(four_of_five([v.get('valid') and v['storage_evasion_falsified'][size]
                                 for v in per_seed.values()]) for size in ('fm61', 'amsl112'))
    cc = float(np.mean([v['Fbar_gain'] for v in valid])) <= .02
    cc = cc and four_of_five([v.get('valid') and v['meds_upper95'] <= .10 for v in per_seed.values()])
    dd = four_of_five([v.get('valid') and v['S3_gain'] <= .05 for v in per_seed.values()])
    dd = dd and four_of_five([v.get('valid') and v['border_gain'] <= .01 and v['border_same_path'] for v in per_seed.values()])
    # V3(e) explicitly says EACH kernel quantity on >=4/5, unlike (b)'s
    # requirement that the same seeds satisfy both storage sizes.
    ee = not kernel or all(four_of_five([v.get('valid') and v.get(key, math.inf) <= .05
                                       for v in per_seed.values()]) for key in ('kappa_ho', 'kappa_train'))
    ff = four_of_five([v.get('valid') and v.get('own_registration_guards') for v in per_seed.values()])
    return dict(a=aa, b=bool(bb), c=bool(cc), d=bool(dd), e=bool(ee), f=bool(ff)), dict(
        status='read', read_seeds=len(valid), denominator=5, seed_mean_lcomb_gain=full,
        seed_mean_ladder_gain=ladder, seed_mean_matched_gain=matched,
        seed_mean_Fbar_gain=float(np.mean([v['Fbar_gain'] for v in valid])), unpaired=unpaired)


def git(root, *args, binary=False):
    r = subprocess.run(['git', '-C', str(root), *args], capture_output=True, check=True)
    return r.stdout if binary else r.stdout.decode().strip()


def pin_paths(root, path):
    result = {}
    for line in checked_path(path).read_text().splitlines():
        if not line.strip():
            continue
        h, name = line.split(None, 1)
        p = checked_path(name.strip())
        p = p if p.is_absolute() else root / p
        p = p.resolve()
        need(re.fullmatch('[0-9a-f]{64}', h) is not None, 'invalid pin hash')
        need(p not in result, 'duplicate pin path')
        result[p] = h
    return result


def validate_confirmation_selection(selected, winner, rule_sha256):
    """Bind confirmation to the actual prior fixed-order result, not its label."""
    need(selected.get('schema') == 'next-selection-result-v1' and selected.get('stage') == 'selection',
         'confirmation requires a selection result')
    need(selected.get('rule_sha256') == rule_sha256, 'confirmation selection rule differs')
    need(winner in ORDER and selected.get('choice') == winner, 'wrong selection record')
    need(set(selected.get('arms', {})) == set(ORDER), 'selection dispositions incomplete')
    need(decide(selected['arms']) == winner, 'selection choice contradicts fixed-order criteria')


def native_preflight(root, admission, paths, support):
    """Control-plane/manifest reads only. Never inspects an archive member."""
    native_arms = {k: v for k, v in admission['arms'].items()
                   if k in ('SbFM', 'DINOv3') and v['status'] == 'read'}
    if not native_arms:
        return set(), set()
    need(admission['stage'] == 'selection', 'fresh native sources require a registered adapter extension')
    need(NATIVE_CODE.resolve() in paths, 'native adapter module not pinned')
    def pinned_json(field):
        p = (root / admission[field]).resolve()
        need(p in paths, field + ' not pinned')
        return read_json(p)
    inventory = pinned_json('native_source_inventory')
    context = {'manifests': {}, 'border_ids': support['border_ids'], 'module_sha256': paths[NATIVE_CODE.resolve()]}
    for name, rec in admission['native_manifests'].items():
        p = (root / rec['path']).resolve()
        need(p in paths and paths[p] == rec['sha256'], 'native manifest not exactly pinned')
        if name in NATIVE_MANIFEST_PINS:
            need(rec['sha256'] == NATIVE_MANIFEST_PINS[name], 'registered native manifest changed')
        context['manifests'][name] = read_csv(p)
    needed = {'ab1_eval', 'train_A', 'train_Sb', 'tt1', 'meds'}
    if 'SbFM' in native_arms:
        needed |= {'fm_eval', 'train_SbFM'}
        need('SbFM' in admission['transfer_files'], 'SbFM training-list transfer rows absent')
    if 'DINOv3' in native_arms:
        needed |= {'fs_eval', 'train_B', 'ms1'}
        mode = pinned_json('dinov3_seed_mode')
        need(mode['mode'] == 'five' and mode['seeds'] == list(range(403, 408)),
             'DINOv3 frozen mode does not supply v3 five-seed route')
        context['mode'] = mode
    need(needed <= set(context['manifests']), 'native source manifests incomplete')
    for key, support_key in (('tt1', 'tt1_sha256'), ('meds', 'meds_score_manifest_sha256')):
        need(admission['native_manifests'][key]['sha256'] == support[support_key], 'native/support manifest differs')
    context['families'] = {key: [r['id'] for r in context['manifests'][key] if r['fam'] == fam]
                           for key, fam in [('tt1', 'tt1'), ('meds', 'meds')] +
                           ([('ms1', 'ms1ffhq')] if 'DINOv3' in native_arms else [])}
    for key, count in (('tt1', 30994), ('meds', 1018), ('ms1', 1480)):
        if key in context['families']:
            ids = context['families'][key]
            need(len(ids) == count and len(set(ids)) == count, 'native family population differs')
    need(set(support['border_ids']) <= set(context['families']['tt1']), 'supplement missing exact border rows')
    network_ids, supplement_ids = set(), set()
    for name, arm in native_arms.items():
        seeds = list(range(403, 408)) if name == 'DINOv3' else list(range(408, 413))
        need(arm['seeds'] == seeds, 'wrong native fixed seeds')
        roles = {'candidate': ('Sb' if name == 'DINOv3' else 'SbFM', seeds),
                 'control': ('A', seeds), 'comparator': ('Sb', list(range(408, 413)))}
        if name == 'DINOv3':
            roles['fit_guard'] = ('B', seeds)
        for role, (wanted, role_seeds) in roles.items():
            need(set(arm[role]) == set(map(str, role_seeds)), 'native role seed disposition incomplete')
            for seed, key in arm[role].items():
                if key is None:
                    need(not (name == 'DINOv3' and role == 'comparator'),
                         'v3 five-comparator mean undefined with a missing comparator')
                    continue
                n = admission['networks'][key]
                need(n['format'] == 'native_fit' and n['arm'] == wanted and type(n['seed']) is int and n['seed'] == int(seed),
                     'native role/seed/adapter differs')
                origin = 'BB2L' if name == 'DINOv3' and role != 'comparator' else ('AB1FM' if role == 'candidate' else 'AB1')
                need(n['prefix'] == f'{origin}_{wanted}_s{seed}', 'native source role identity differs')
                need(inventory.get(n['prefix']) == n['sha256'], 'native source inventory differs')
                if origin == 'AB1' and wanted == 'Sb':
                    need(n['sha256'] == AB1_SB_SOURCE_PINS[int(seed)], 'original AB1 comparator source changed')
                if origin == 'BB2L':
                    need(context['mode']['tars'].get(n['prefix'] + '.tar') == n['sha256'], 'E3 source differs from frozen mode')
                    need(n.get('batch_spec') == [256, 1], 'E3 registered batch 256 x 1 required')
                network_ids.add(key)
        # Both compared roles must use the very same supplemental artifact.
        supkey = arm['supplement']
        sup = admission['supplements'][supkey]
        need(sup['format'] == ('sbfm_supplement' if name == 'SbFM' else 'dinov3_w2'), 'wrong supplemental route')
        producer, producer_hash = NATIVE_PRODUCERS[sup['format']]
        need(paths.get((root / producer).resolve()) == producer_hash and sup.get('producer_sha256') == producer_hash,
             'registered supplement producer not pinned')
        supplement_ids.add(supkey)
        if name == 'SbFM':
            cfgpath = (root / sup['config']).resolve()
            need(cfgpath in paths and paths[cfgpath] == sup['config_sha256'], 'submitted supplement config not pinned')
            need(sup['config_sha256'] == SBFM_CONFIG_SHA256, 'registered submitted supplement config changed')
            need(sup['config'] == 'src/recovery_20261114/sbfm_supplement/config.json', 'unregistered supplement config path')
            cfg = read_json(cfgpath)
            configured = {m['name']: m['sha256'] for m in cfg['models']}
            for role in ('candidate', 'comparator'):
                for key in arm[role].values():
                    if key is not None:
                        n = admission['networks'][key]
                        need(configured.get(n['prefix']) == n['sha256'], 'source not in submitted SbFM supplement')
    need(network_ids.isdisjoint(supplement_ids), 'receipt namespace collision')
    # Training-list reference is bound to the manifest, not just a label/file.
    for tag in ('Sb', 'SbFM') if 'SbFM' in native_arms else ('Sb',):
        ref = admission['transfer_training_sha256'][tag]
        need(ref == admission['native_manifests']['train_' + tag]['sha256'], 'transfer training-list reference differs')
    admission['_native_context'] = context
    return network_ids, supplement_ids


def check_arrival(record, receipt, stage):
    need(receipt['sha256'] == record['sha256'] and receipt.get('hash_verified') is True, 'opaque receipt mismatch')
    if 'producer_sha256' in record:
        need(receipt.get('producer_sha256') == record['producer_sha256'], 'opaque receipt producer differs')
    at = dt.datetime.fromisoformat(receipt['verified_at'])
    need(at.tzinfo is not None, 'receipt timestamp needs timezone')
    if stage == 'selection':
        need(at <= DEADLINE, 'late archive cannot be admitted')
    need(checked_path(record['archive']).resolve() == checked_path(receipt['archive']).resolve(), 'receipt path differs')
    need(digest(record['archive']) == record['sha256'], 'archive digest mismatch')


def preflight(root, admission_path):
    root = root.resolve()
    admission_path = checked_path(admission_path).resolve()
    need(not git(root, 'status', '--porcelain', '--untracked-files=all'), 'work tree is not clean')
    git(root, 'merge-base', '--is-ancestor', BINDING, 'HEAD')
    admission = read_json(admission_path)
    need(admission.get('schema') == 'next-admission-v1', 'unsupported admission schema')
    need(admission.get('stage') in ('selection', 'confirmation'), 'unknown stage')
    need(admission.get('approved') is True and admission.get('batch_closed') is True, 'batch not approved/closed')
    need(admission.get('numpy_version') == np.__version__, 'unreviewed numpy build')
    paths = {}
    for filename in admission['pinfiles']:
        pf = (root / filename).resolve()
        extra = pin_paths(root, pf)
        for p, h in extra.items():
            need(p not in paths or paths[p] == h, 'conflicting pins')
        paths.update(extra)
        rel = str(pf.relative_to(root))
        need(git(root, 'show', f'HEAD:{rel}', binary=True) == pf.read_bytes(), 'pinfile not committed')
    mandatory = [root / RULE, pathlib.Path(__file__).resolve(), admission_path,
                 root / admission['support'], root / admission['review'], root / admission['receipt_manifest']]
    mandatory += [root / f for f in admission['input_files'].values()]
    mandatory += [root / f for f in admission['transfer_files'].values()]
    need(all(p.resolve() in paths for p in mandatory), 'mandatory rule/reader/admission/support/review/receipt/input pin absent')
    for p, h in paths.items():
        need(digest(p) == h, 'pin mismatch: ' + str(p))
        if p.is_relative_to(root):
            rel = str(p.relative_to(root))
            need(git(root, 'show', f'HEAD:{rel}', binary=True) == p.read_bytes(), 'pinned file not committed: ' + rel)
    need(digest(root / RULE) == admission['rule_sha256'], 'rule fingerprint changed')
    need('**Status: APPROVED.**' in (root / RULE).read_text(), 'rule not approved')
    review = (root / admission['review']).read_text()
    # Avoid a self-referential admission hash: its independently committed review
    # must state the exact hash, while the manifest stores its review's filename.
    need('NEXT_ADMISSION_GO ' + digest(admission_path) in review.splitlines(),
         'independent GO does not bind exact admission bytes')
    receipts = read_json(root / admission['receipt_manifest'])
    support = read_json(root / admission['support'])
    need(support.get('schema') == 'next-support-v1', 'support schema unavailable')
    need(set(admission['arms']) == set(ORDER), 'all eight fixed arms need an explicit disposition')
    for name, arm in admission['arms'].items():
        statuses = ('read', 'not_read', 'ablation', 'not_selected') if admission['stage'] == 'confirmation' else ('read', 'not_read', 'ablation')
        need(arm['status'] in statuses, 'unreviewed arm disposition')
        if arm['status'] != 'read':
            need(arm.get('reason') and arm.get('evidence') and (root / arm['evidence']).resolve() in paths,
                 'excluded arm requires pinned authoritative reason')
            allowed = {'deadline', 'infrastructure_failure', 'missing_seeds', 'failed_registered_gate',
                       'missing_required_inputs'} if arm['status'] == 'not_read' else {'pre_binding_scientific_open'}
            if arm['status'] == 'not_selected':
                allowed = {'not_selected_by_fixed_rule'}
            need(arm['reason'] in allowed, 'implementation limitation is not a scientific exclusion reason')
            continue
        need(name in RZ | {'SbFM', 'DINOv3'}, 'native adapter not yet validated for arm ' + name)
        need(name != 'SbMR512', 'SbMR512 kernel test/native adapter not registered')
        need(arm.get('pre_binding_scientific_open') is False, 'pre-binding exposure unresolved')
        need(arm.get('eligibility_review') and (root / arm['eligibility_review']).resolve() in paths,
             'eligible arm review absent')
        if name in ('SbFM', 'DINOv3'):
            continue
        if name == 'Sbc':
            need(arm.get('crop_scope_ruling') and (root / arm['crop_scope_ruling']).resolve() in paths,
                 'crop author scope ruling absent')
        seeds = list(range(413, 418)) if admission['stage'] == 'confirmation' else list(range(408, 413))
        need(arm.get('seeds') == seeds, 'wrong fixed seed set')
        need(set(arm['candidate']) == set(map(str, seeds)), 'incomplete candidate seed disposition')
        for role in ('comparator', 'control', 'yardstick'):
            need(set(arm[role]) == set(map(str, seeds)), 'incomplete ' + role + ' seed disposition')
        expected_arm = dict(candidate=name, comparator='Sb0',
                            control='A512' if name in ('Sb512', 'SbMR512') else 'A0', yardstick='Sb')
        for role, wanted in expected_arm.items():
            for seed, key in arm[role].items():
                if key is None:
                    continue
                network = admission['networks'][key]
                need(network['arm'] == wanted and network['seed'] == int(seed), 'wrong role/seed network mapping')
                need(network['format'] == ('rz1_refit' if role == 'yardstick' else 'rz1_fit'), 'wrong role adapter')
                if role == 'yardstick':
                    source = network['source_network']
                    need(int(seed) in AB1_SB_SOURCE_PINS,
                         'fresh AB1 source pins need a registered and reviewed adapter extension')
                    need(source['name'] == f'AB1_Sb_s{seed}.tar' and source['sha256'] == AB1_SB_SOURCE_PINS[int(seed)],
                         'yardstick source differs from original fixed AB1 comparator')
    network_ids, supplement_ids = native_preflight(root, admission, paths, support)
    for name, arm in admission['arms'].items():
        if arm['status'] == 'read' and name in RZ:
            for role in ('candidate', 'comparator', 'control', 'yardstick'):
                network_ids.update(v for v in arm[role].values() if v is not None)
    for key in network_ids:
        n = admission['networks'][key]
        need(n['format'] in ('rz1_fit', 'rz1_refit', 'native_fit'), 'unsupported native network format')
        need(key in receipts, 'network missing arrival/hash receipt')
        check_arrival(n, receipts[key], admission['stage'])
    for key in supplement_ids:
        need(key in receipts, 'supplement missing arrival/hash receipt')
        check_arrival(admission['supplements'][key], receipts[key], admission['stage'])
    if admission['stage'] == 'confirmation':
        need(admission.get('confirmation_registration') and
             (root / admission['confirmation_registration']).resolve() in paths, 'fresh-seed confirmation registration not pinned')
        need(admission.get('selected_arm') in ORDER, 'confirmation winner absent')
        need(sum(a['status'] == 'read' for a in admission['arms'].values()) == 1,
             'confirmation may read only the preselected arm')
        need(admission['arms'][admission['selected_arm']]['status'] == 'read', 'confirmation arm differs from winner')
        selection_path = root / admission['selection_record']
        need(selection_path.resolve() in paths, 'selection result not pinned')
        selected = read_json(selection_path)
        validate_confirmation_selection(selected, admission['selected_arm'], admission['rule_sha256'])
    return admission, support, paths


def safe_npz(tf, member):
    p = pathlib.PurePosixPath(member)
    need(not p.is_absolute() and '..' not in p.parts, 'unsafe archive member')
    m = tf.getmember(member)
    need(m.isfile() and m.size <= 256 * 1024 * 1024, 'unexpected archive member type/size')
    with tf.extractfile(m) as f:
        with np.load(io.BytesIO(f.read()), allow_pickle=False) as z:
            return {k: z[k] for k in z.files}


def scores(z):
    ids = [str(i) for i in z['id']]
    values = np.asarray(z['logit'], float)
    if values.shape != (len(ids),) or len(set(ids)) != len(ids) or not np.isfinite(values).all():
        raise SeedUnavailable('invalid/duplicate/non-finite network score rows')
    return dict(zip(ids, values.tolist()))


def load_rz_network(record, support):
    """Strict native RZ1 schema, based on the existing reviewed RZ1 loaders."""
    path = checked_path(record['archive'])
    with path.open('rb') as binary:
        # Verify the bytes on the same descriptor subsequently read by tarfile.
        h = hashlib.file_digest(binary, 'sha256').hexdigest()
        need(h == record['sha256'], 'archive changed after preflight')
        binary.seek(0)
        with tarfile.open(fileobj=binary, mode='r:') as tf:
            prefix = record['prefix']
            expected_prefix = ('RZ1_' if record['format'] == 'rz1_fit' else 'RZ1R_') + record['arm'] + '_s' + str(record['seed'])
            need(prefix == expected_prefix, 'native archive/network identity differs')
            names = tf.getnames()
            need(len(names) == len(set(names)), 'duplicate tar member paths')
            def raw(name):
                member = tf.getmember(prefix + '/' + name)
                need(member.isfile() and member.size < 8 * 1024 * 1024, 'invalid metadata member')
                return tf.extractfile(member).read().decode()
            try:
                gpu, taskinfo = raw('gpu.txt'), raw('task_info.txt')
                if 'H100' not in gpu:
                    raise SeedUnavailable('wrong training/scoring GPU')
                if record['format'] == 'rz1_fit':
                    arm = record['arm']
                    need(arm in ARM_SPEC, 'unsupported RZ1 arm')
                    man, spec, res, bs, accum = ARM_SPEC[arm]
                    meta = json.loads(raw('meta.json'))
                    transform = json.loads(raw('rz1_transform.json'))
                    guard, task, log = raw('guard.log'), raw('task.env'), raw('train.log')
                    expected = [f'{k} {v}' for k, v in PINS.items()]
                    primary = spec if arm in ('Sbc', 'Ac') else 'fixed:pil_bilinear'
                    expected += [f'spec {spec} ', f'primary {primary} ',
                                 f'res {res} bs {bs} accum {accum} ', 'steps 6250 limit 0 skip_tt1 0']
                    checks = all(v in taskinfo + ' ' for v in expected)
                    checks &= f'ARM={arm}\n' in task + '\n' and f'SEED={record["seed"]}\n' in task + '\n'
                    checks &= 'RZ1 GUARD pre ok' in guard and 'RZ1 GUARD post ok' in guard
                    checks &= transform.get('spec') == spec and transform.get('res') == res
                    checks &= all(meta.get(k) == v for k, v in dict(steps=6250, res=res, bs=bs, accum=accum, seed=record['seed']).items())
                    tm = support['train']['A0' if man == 'train_A.csv' else 'Sb0']
                    checks &= meta.get('n_items') == tm['n_items']
                    losses = [float(v) for v in re.findall(r'loss[ =:]+(-?(?:inf|nan)|[-+0-9.eE]+)', log, re.I)]
                    checks &= bool(losses) and all(math.isfinite(v) for v in losses)
                    if not checks:
                        raise SeedUnavailable('RZ1 fit provenance/guard/loss failure')
                else:
                    gate = json.loads(raw('gate.json'))
                    if gate.get('verdict') != 'passed' or gate.get('n') != 21277 or gate.get('n_differ') != 0 or gate.get('max_abs') != 0:
                        raise SeedUnavailable('refit yardstick exact gate refused')
                    expected = record['source_network']
                    if f'source_tar {expected["name"]} {expected["sha256"]}' not in taskinfo or 'limit 0' not in taskinfo:
                        raise SeedUnavailable('yardstick source provenance mismatch')
                    expected_name = f'AB1_{record["arm"]}_s{record["seed"]}.tar'
                    if expected['name'] != expected_name or gate.get('tar') != expected_name or gate.get('tar_sha256') != expected['sha256']:
                        raise SeedUnavailable('yardstick exact gate source mismatch')
                    if 'H100' not in str(gate.get('device')) or gate.get('own_rule_agree') != 1:
                        raise SeedUnavailable('yardstick gate GPU/agreement mismatch')
                    expected_pins = [f'{k} {v}' for k, v in PINS.items()]
                    expected_pins += ['rz1_rescore 02628562fb495cfedabd0e409db1b397fd0fb2d90ff4886ce4f865764b94bfd6',
                                      'train_manifest ' + ('train_A.csv' if record['arm'] == 'A' else 'train_Sb.csv')]
                    if not all(v in taskinfo + ' ' for v in expected_pins):
                        raise SeedUnavailable('yardstick input/scorer pins differ')
                    primary = 'fixed:pil_bilinear'
                zs = {key: safe_npz(tf, prefix + '/' + filename) for key, filename in dict(
                    x='scores_eval.npz', tr='scores_train.npz', tt1='scores_tt1.npz', meds='scores_meds.npz', cross='scores_cross.npz').items()}
                if str(zs['x']['manifest_sha256']) != support['eval_sha256'] or str(zs['tt1']['manifest_sha256']) != support['tt1_sha256']:
                    raise SeedUnavailable('eval/TT1 scoring manifest mismatch')
                if str(zs['meds']['manifest_sha256']) != support['meds_score_manifest_sha256']:
                    raise SeedUnavailable('MEDS scoring manifest mismatch')
                for key in ('x', 'tr', 'tt1', 'meds'):
                    if str(zs[key]['spec']) != primary:
                        raise SeedUnavailable('primary scoring transform mismatch')
                if record['format'] == 'rz1_refit':
                    tm = support['train']['A0' if record['arm'] == 'A' else 'Sb0']
                if str(zs['tr']['manifest_sha256']) != tm['sha256']:
                    raise SeedUnavailable('training scoring manifest mismatch')
                for key in ('x', 'tt1', 'meds'):
                    if list(map(str, zs[key]['id'])) != support['_expected_ids'][key]:
                        raise SeedUnavailable('score row identity/order differs from pinned manifest')
                train_key = 'A0' if (record['arm'].startswith('A') or record['arm'] == 'Ac') else 'Sb0'
                expected_train = support['_expected_train'][train_key]
                for field in ('path', 'kind'):
                    if list(map(str, zs['tr'][field])) != [r[field] for r in expected_train]:
                        raise SeedUnavailable('unique training score rows/order differ')
                if list(map(int, zs['tr']['label'])) != [int(r['label']) for r in expected_train]:
                    raise SeedUnavailable('training score labels differ')
                if not np.isfinite(np.asarray(zs['tr']['logit'], float)).all():
                    raise SeedUnavailable('non-finite training scores')
                cross_specs = [str(s) for s in zs['cross']['specs']]
                expected_cross = support['kernel']['train9'] + support['kernel']['held4'] if record['arm'] in ('A0', 'Sb0', 'SbMR', 'SbM') or record['format'] == 'rz1_refit' else []
                if cross_specs != expected_cross or (cross_specs and str(zs['cross']['manifest_sha256']) != support['cross_sha256']):
                    raise SeedUnavailable('cross table provenance mismatch')
                output = {k: scores(zs[k]) for k in ('x', 'tt1', 'meds')}
                cross_ids = [str(i) for i in zs['cross']['id']]
                cross_logits = np.asarray(zs['cross']['logit'], float)
                if cross_ids != (support['_expected_ids']['cross'] if cross_specs else []):
                    raise SeedUnavailable('cross row order differs')
                if cross_logits.shape != (len(cross_specs), len(cross_ids)) or len(set(cross_ids)) != len(cross_ids) or not np.isfinite(cross_logits).all():
                    raise SeedUnavailable('invalid cross scores')
                output['cross'] = {sp: dict(zip(cross_ids, cross_logits[j].tolist())) for j, sp in enumerate(cross_specs)}
                output['border_path'] = 'rz1_primary_fit_or_exact_refit'
                output['registration_guards'] = True
                return output
            except (KeyError, ValueError, TypeError) as e:
                raise SeedUnavailable('native RZ1 member/schema incomplete') from e


def flag(values, ids):
    if not ids:
        raise SeedUnavailable('empty required flag pool')
    try:
        x = np.array([values[i] for i in ids], float)
    except KeyError as e:
        raise SeedUnavailable('required flag rows missing') from e
    if not np.isfinite(x).all():
        raise SeedUnavailable('non-finite required flags')
    return float(np.mean(x > 0))


def storage_statistics(data, support):
    x = data['x']
    st = {'storage': {}, 'control': {}, 'evasion_falsified': {}}
    native = np.array([x[i] for i in support['storage']['native_photo_ids']], float)
    sd = float(native.std(ddof=1))
    if not math.isfinite(sd) or sd <= 0:
        raise SeedUnavailable('native storage normalisation undefined')
    for size in ('fm61', 'amsl112'):
        pairs = support['storage']['pairs'][size]
        nat = np.array([x[p['native']] for p in pairs]); stored = np.array([x[p['stored']] for p in pairs])
        morph = support['storage']['morph_pairs'][size]
        mn = np.array([x[p['native']] for p in morph]); ms = np.array([x[p['stored']] for p in morph])
        delta = float(np.mean(stored > 0) - np.mean(nat > 0))
        mean = float(np.mean(stored - nat) / sd)
        att = float(np.mean(ms - mn) / sd)
        st['storage'][size] = delta
        st['control'][size] = bool(delta >= .05 and mean > 0)
        st['evasion_falsified'][size] = bool(att >= -.10)
        st.setdefault('storage_detail', {})[size] = {'rise': delta, 'mean_shift_sd': mean, 'morph_shift_sd': att}
    return st


def network_statistics(data, support, *, n_boot=NB):
    x = data['x']
    st = storage_statistics(data, support)
    st['Fbar'] = float(np.mean([flag(data['tt1'], ids) for ids in support['tt1_families'].values()]))
    st['tt1_families'] = {name: flag(data['tt1'], ids) for name, ids in support['tt1_families'].items()}
    # Private MEDS IDs are resolved in memory only, never copied to the result.
    meds_ids = support['_meds_ids']
    prim = support['meds_primary']
    vals = np.array([data['meds'][meds_ids[r['row_index']]] > 0 for r in prim], float)
    groups = np.array([str(r['person']) for r in prim]); ug = np.unique(groups)
    rng = np.random.default_rng(20261125)
    draws = rng.integers(0, len(ug), size=(n_boot, len(ug)))
    group_sums = np.array([vals[groups == g].sum() for g in ug]); group_n = np.array([(groups == g).sum() for g in ug])
    boot = np.sum(group_sums[draws], axis=1) / np.sum(group_n[draws], axis=1)
    st['meds_ci'] = ci(boot); st['meds_flag'] = float(vals.mean())
    st['S3'] = flag(x, support['S3_ids']); st['border'] = flag(x, support['border_ids'])
    if data['cross']:
        ks = support['kernel']; primary = data['cross'][ks['primary']]
        base = [flag(primary, ks[p]) for p in ('genuine_ids', 'morph_ids')]
        deltas = {sp: max(abs(flag(v, ks[p]) - base[j]) for j, p in enumerate(('genuine_ids', 'morph_ids')))
                  for sp, v in data['cross'].items()}
        st['kappa_train'] = max(deltas[sp] for sp in ks['train9'])
        st['kappa_ho'] = max(deltas[sp] for sp in ks['held4'])
    return st


def floor_prints(contrast, candidate_vector, floor_columns, transfer_rows):
    point, bootstrap = contrast.values(candidate_vector)
    output = {'network_auc': point, 'network_ci': ci(bootstrap), 'floors': {}}
    for title, col in floor_columns.items():
        vector = np.array([float(r[col]) for r in contrast.rows])
        floor, draw = contrast.values(vector)
        interval = ci(bootstrap - draw)
        output['floors'][title] = dict(auc=floor, network_minus_floor=point - floor, ci=interval, exceeds=interval[0] > 0)
    for model in ('logreg', 'gbt'):
        vals = contrast.vector({r['id']: float(r[model]) for r in transfer_rows})
        floor, draw = contrast.values(vals); interval = ci(bootstrap - draw)
        output['floors']['same_data_transfer_' + model] = dict(auc=floor, network_minus_floor=point - floor,
                                                              ci=interval, exceeds=interval[0] > 0)
    return output, bootstrap


def validate_support(root, admission, support, pinned):
    need(set(admission['floor_columns']) == {'lcomb', 'ladder', 'matched'}, 'missing floor contrast definitions')
    for columns in admission['floor_columns'].values():
        need(set(columns) == {'all_cue', 'non_F27_non_BLEND', 'surround', 'face_box'}, 'all four floor families required')
    need(len(support['tt1_families']) == 7 and len(support['S3_ids']) == 100 and len(support['border_ids']) == 1582,
         'wrong TT1/S3/border pool sizes')
    need(len(support['meds_primary']) == 865 and len({r['person'] for r in support['meds_primary']}) == 400,
         'wrong MEDS primary/person counts')
    p = checked_path(support['meds_manifest_path']).resolve()
    need(p in pinned and digest(p) == support['meds_manifest_sha256'], 'private MEDS manifest not pinned')
    meds = read_csv(p); support['_meds_ids'] = [r['id'] for r in meds]
    need(len(set(support['_meds_ids'])) == len(meds), 'duplicate MEDS IDs')
    need(all(meds[r['row_index']]['aligned'] == '1' for r in support['meds_primary']), 'MEDS primary selection mismatch')
    need(len(support['kernel']['train9']) == 9 and len(support['kernel']['held4']) == 4, 'wrong kernel definitions')
    need(set(support['kernel']['train9']).isdisjoint(support['kernel']['held4']), 'held-out kernel overlap')
    for name, info in support.get('sources', {}).items():
        want = info['sha256'] if isinstance(info, dict) else info
        p = pathlib.Path(name); p = p if p.is_absolute() else root / p
        need(p.resolve() in pinned and digest(p) == want, 'unpinned support source')
    def source_rows(h):
        matches = []
        for name, info in support['sources'].items():
            want = info['sha256'] if isinstance(info, dict) else info
            if want == h:
                p = pathlib.Path(name); matches.append(p if p.is_absolute() else root / p)
        need(matches, 'required support manifest source absent')
        return read_csv(matches[0])
    support['_expected_ids'] = {key: [r['id'] for r in source_rows(support[hash_key])]
                                for key, hash_key in dict(x='eval_sha256', tt1='tt1_sha256',
                                                         meds='meds_score_manifest_sha256', cross='cross_sha256').items()}
    need(support['_expected_ids']['meds'] == support['_meds_ids'], 'MEDS private/score manifest order differs')
    support['_expected_train'] = {}
    for key in ('A0', 'Sb0'):
        unique = {}
        for r in source_rows(support['train'][key]['sha256']):
            unique.setdefault(r['path'], r)
        support['_expected_train'][key] = list(unique.values())


def prepare_contrasts(root, admission, *, n_boot=NB):
    """Validate all shared rows/floors before the once journal or candidate access."""
    inp = {k: root / v for k, v in admission['input_files'].items()}
    rows = {key: read_csv(inp[key]) for key in ('lcomb', 'ladder', 'matched', 'lcomb_bal', 'ladder_dev', 'ladder_test', 'ladder_no_shape', 'facemorpher')}
    need(len(rows['lcomb']) == 3000 and sum(int(r['label']) for r in rows['lcomb']) == 1000, 'wrong landmark rows')
    need(len(rows['ladder']) == 360 and len({r['component'] for r in rows['ladder']}) == 110, 'wrong ladder population')
    need(len(rows['matched']) == 720 and len({r['pair'] for r in rows['matched']}) == 360, 'wrong matched pairs')
    contrasts = {k: Contrast(v, stratified=k.startswith('ladder'), n_boot=n_boot) for k, v in rows.items()}
    transfers = {tag: read_csv(root / path) for tag, path in admission['transfer_files'].items()}
    need('Sb' in transfers, 'same-data Sb transfer learner missing')
    for key in ('lcomb', 'ladder', 'matched'):
        con = contrasts[key]
        for column in admission['floor_columns'][key].values():
            vals = np.array([float(r[column]) for r in con.rows])
            need(np.isfinite(vals).all(), 'non-finite pinned floor predictions')
        setname = {'lcomb':'lcomb', 'ladder':'sel360', 'matched':'lcomb_smatch'}[key]
        for transfer in transfers.values():
            rr = [r for r in transfer if r['set'] == setname]
            indexed = unique_rows(rr)
            need(set(indexed) == set(con.ids), 'transfer learner rows differ')
            for r in con.rows:
                q = indexed[r['id']]
                need(q['label'] == r['label'] and str(q['component']) == str(r['component']), 'transfer learner row metadata differs')
                need(all(math.isfinite(float(q[m])) for m in ('logreg', 'gbt')), 'transfer learner non-finite')
    return contrasts, transfers


def native_fit_gates(train, origin, arm):
    logits = np.asarray(train['logit'], float); labels = np.asarray(train['label'], int)
    accuracy = float(np.mean((logits > 0) == labels))
    result = dict(training_accuracy=accuracy, registration_guards=True)
    if origin == 'BB2L':
        result['registration_guards'] = accuracy >= .75
        if arm == 'Sb':
            kinds = np.asarray(train['kind'])
            selected = np.isin(kinds, ['lad_S3', 'lad_S4'])
            result['splice_fit_auc'] = auc(logits[selected], (kinds[selected] == 'lad_S4').astype(int))
            result['registration_guards'] &= result['splice_fit_auc'] >= .80
    return result


def native_network(admission, key, supplement_key=None, *, storage_only=False):
    """After once claim: decode fit and optional exact-gated supplemental route."""
    if key is None:
        raise SeedUnavailable('registered missing/failed seed')
    n = admission['networks'][key]
    ctx = admission['_native_context']; manifests = ctx['manifests']
    need(digest(NATIVE_CODE) == ctx['module_sha256'], 'native adapter module changed after admission')
    origin = n['prefix'].split('_')[0]
    eval_key = {'AB1': 'ab1_eval', 'AB1FM': 'fm_eval', 'BB2L': 'fs_eval'}[origin]
    train_key = 'train_' + n['arm']
    train = manifests[train_key]; unique = {}
    for row in train:
        if row['path'] in unique:
            need(all(unique[row['path']][f] == row[f] for f in ('kind', 'label')), 'conflicting repeated training row')
        unique.setdefault(row['path'], row)
    N = native_module()
    try:
        fit = N.load_fit(n, [r['id'] for r in manifests[eval_key]], list(unique.values()),
                         admission['native_manifests'][train_key]['sha256'],
                         admission['native_manifests'][eval_key]['sha256'], len(train))
        fit.update(cross={}, **native_fit_gates(fit['train'], origin, n['arm']))
        if supplement_key is None:
            return fit
        sup = admission['supplements'][supplement_key]
        src = dict(name=n['prefix'], sha256=n['sha256'], arm=n['arm'], seed=n['seed'])
        families = {k: ctx['families'][k] for k in ('tt1', 'meds')}
        if sup['format'] == 'sbfm_supplement':
            extra = N.load_sbfm_supplement(sup, src, families)
        else:
            if storage_only:
                need(n['prefix'].startswith('BB2L_A_'), 'storage-only rescore is for the E3 plain control')
                families = {}
            families['ms1ffhq'] = ctx['families']['ms1']
            extra = N.load_dinov3_w2(sup, src, families)
            # AB1 already scored MS1 in-fit; the admitted W2 path is used for
            # these rows for both arms, with its own exact reproduction gate.
            fit['x'].update(extra.pop('ms1ffhq'))
        fit.update(extra)
        if not storage_only:
            for row in ctx['border_ids']:
                fit['x'][row] = fit['tt1'][row]
        return fit
    except N.NativeIntegrityError as e:
        raise Refusal(str(e)) from e
    except (N.NativeRefusal, KeyError, ValueError, TypeError, OSError, tarfile.TarError) as e:
        # Do not leak private MEDS IDs or raw exception payloads.
        raise SeedUnavailable('native fit/supplement schema, finite-data or exact gate failure') from e


def fm_original_engine_guard(candidate, comparator, manifests):
    rows = [r for r in manifests['fm_eval'] if r['fam'] == 'ladder' and r['role'] == 'test'
            and r['tool'] == 'opencv' and r['strength'] == '' and r['rung'] in ('R4', 'R2w')]
    need(len(rows) == 382 and sum(r['rung'] == 'R4' for r in rows) == 191, 'SbFM original-engine guard population differs')
    labels = [int(r['rung'] == 'R4') for r in rows]
    c = auc([candidate['x'][r['id']] for r in rows], labels)
    b = auc([comparator['x'][r['id']] for r in rows], labels)
    return dict(candidate_auc=c, comparator_auc=b, testable=b < .98, gain=c-b,
                passed=bool(b < .98 and c-b >= -.02))


def execute(root, admission, support, *, n_boot=NB, prepared=None):
    contrasts, transfers = prepared or prepare_contrasts(root, admission, n_boot=n_boot)
    cache = {}
    def load(key, supplement=None, *, storage_only=False):
        if key is None:
            raise SeedUnavailable('registered missing/failed seed')
        ck = (key, supplement, storage_only)
        if ck not in cache:
            record = admission['networks'][key]
            cache[ck] = (native_network(admission, key, supplement, storage_only=storage_only) if record['format'] == 'native_fit'
                         else load_rz_network(record, support))
        return cache[ck]
    result = {'schema': 'next-selection-result-v1', 'stage': admission['stage'], 'arms': {},
              'rule_sha256': admission['rule_sha256'], 'labels': ['development selection', 'selection-biased', 'no benchmark claim'],
              'bootstrap': {'draws': n_boot, 'component_seed': 20261115, 'within_D_edges_recomputed_in_each_draw': True}}
    for name in ORDER:
        arm = admission['arms'][name]
        if arm['status'] != 'read':
            result['arms'][name] = {'status': arm['status'], 'reason': arm['reason'], 'evidence': arm['evidence']}
            continue
        seed_results = {}; draw_pairs = []; unpaired_draws = []
        unpaired = name == 'DINOv3'
        supplemental = arm.get('supplement')
        baseline_networks = []
        if unpaired:
            try:
                baseline_networks = [load(arm['comparator'][str(s)], supplemental) for s in range(408, 413)]
                baseline_stats = [network_statistics(v, support, n_boot=n_boot) for v in baseline_networks]
            except (SeedUnavailable, KeyError) as e:
                raise Refusal('v3 five-comparator mean undefined: comparator failed; no reduced-mean fallback') from e
        # Yardstick is the maximum absolute difference over all eligible same-seed
        # Sb refits, never a candidate-specific or selectively favourable seed.
        yard = []
        for seed in arm['seeds'] if name in RZ else []:
            s = str(seed)
            try:
                refit, original = load(arm['comparator'][s]), load(arm['yardstick'][s])
                con = contrasts['lcomb']
                yard.append(abs(con.statistic(con.vector(refit['x'])) - con.statistic(con.vector(original['x']))))
            except SeedUnavailable:
                continue
        # Amendment 1 makes the yardstick unavailable when >2/5 gates fail.
        refit_max = max(yard) if len(yard) >= 3 else None
        for seed in arm['seeds']:
            s = str(seed)
            try:
                seed_draws = {}
                candidate = load(arm['candidate'][s], supplemental)
                control = load(arm['control'][s], supplemental if unpaired else None, storage_only=unpaired)
                baselines = baseline_networks if unpaired else [load(arm['comparator'][s], supplemental)]
                bs = baseline_stats if unpaired else [network_statistics(baselines[0], support, n_boot=n_boot)]
                x = network_statistics(candidate, support, n_boot=n_boot)
                ctl = storage_statistics(control, support)
                b = {key: float(np.mean([v[key] for v in bs])) for key in ('Fbar', 'S3', 'border')}
                b['storage'] = {z: float(np.mean([v['storage'][z] for v in bs])) for z in ('fm61', 'amsl112')}
                guard = None
                if name == 'SbFM':
                    guard = fm_original_engine_guard(candidate, baselines[0], admission['_native_context']['manifests'])
                if unpaired:
                    aux = load(arm['fit_guard'][s])
                    adequate = all(v['training_accuracy'] >= .75 for v in (candidate, control, aux))
                    storage_adequate = all(v['training_accuracy'] >= .75 for v in (candidate, control))
                    ctl['control'] = {z: ok and control['training_accuracy'] >= .75 for z, ok in ctl['control'].items()}
                per = {'valid': True, 'floors_printed': True, 'refit_max_abs': refit_max,
                       'storage_pass': {z: x['storage'][z] - b['storage'][z] <= .02 and (storage_adequate if unpaired else True)
                                        for z in ('fm61', 'amsl112')},
                       'control_pass': ctl['control'], 'storage_evasion_falsified': x['evasion_falsified'],
                       'Fbar_gain': x['Fbar'] - b['Fbar'], 'meds_upper95': x['meds_ci'][1],
                       'S3_gain': x['S3'] - b['S3'], 'border_gain': x['border'] - b['border'],
                       'border_same_path': all(candidate['border_path'] == v['border_path'] for v in baselines),
                       'own_registration_guards': bool(candidate['registration_guards'] and all(v['registration_guards'] for v in baselines)
                                                      and control['registration_guards'] and
                                                      (guard['passed'] if guard else True) and (adequate if unpaired else True)),
                       'network': x, 'comparator': bs if unpaired else bs[0], 'control': ctl, 'detection': {}}
                if guard:
                    per['original_engine_guard'] = guard
                if unpaired:
                    per['fit_gates'] = dict(three_arm_adequacy=adequate, splice_fit_auc=candidate['splice_fit_auc'])
                if name in MIX:
                    per.update(kappa_ho=x.get('kappa_ho', math.inf), kappa_train=x.get('kappa_train', math.inf))
                ladder_draw_pair = None
                for key, gain_name in (('lcomb', 'lcomb_gain'), ('ladder', 'ladder_gain'), ('matched', 'matched_gain')):
                    con = contrasts[key]; cv = con.vector(candidate['x'])
                    setname = {'lcomb':'lcomb', 'ladder':'sel360', 'matched':'lcomb_smatch'}[key]
                    tr = [r for r in transfers['SbFM' if name == 'SbFM' else 'Sb'] if r['set'] == setname]
                    printed, cd = floor_prints(con, cv, admission['floor_columns'][key], tr)
                    btr = [r for r in transfers['Sb'] if r['set'] == setname]
                    bprints = [floor_prints(con, con.vector(v['x']), admission['floor_columns'][key], btr) for v in baselines]
                    bp = float(np.mean([v['network_auc'] for v, _ in bprints]))
                    bd = np.mean([d for _, d in bprints], axis=0)
                    per[gain_name] = printed['network_auc'] - bp
                    printed.update(comparator_auc=bp, gain=per[gain_name], gain_ci=ci(cd - bd))
                    printed['comparator_floor_prints'] = [v for v, _ in bprints] if unpaired else bprints[0][0]
                    if unpaired:
                        del printed['gain_ci']
                        printed['gain_ci_scope'] = 'seeds x components interval reported for arm seed mean'
                        seed_draws[key] = (cd, [d for _, d in bprints])
                    per['detection'][key] = printed
                    if key == 'ladder':
                        printed['within_D_coverage'] = within_d(cv, con.y, con.d)[1]
                        ladder_draw_pair = (cd, [d for _, d in bprints] if unpaired else bd)
                per['descriptive'] = {}
                for key in ('lcomb_bal', 'ladder_dev', 'ladder_test', 'ladder_no_shape', 'facemorpher'):
                    con = contrasts[key]; cv = con.vector(candidate['x'])
                    cp, cd = con.values(cv)
                    baseline_values = [con.values(con.vector(v['x'])) for v in baselines]
                    bp = float(np.mean([v for v, _ in baseline_values])); bd = np.mean([v for _, v in baseline_values], axis=0)
                    per['descriptive'][key] = {'network': cp, 'comparator': bp, 'gain': cp - bp, 'ci': ci(cd - bd),
                                               'label': 'descriptive; do not cite as a test' if key == 'lcomb_bal' else 'printed only'}
                    if unpaired:
                        del per['descriptive'][key]['ci']
                        seed_draws[key] = (cd, [d for _, d in baseline_values])
                    if key == 'facemorpher' and name == 'SbFM':
                        per['descriptive'][key]['label'] += '; seen engine'
                seed_results[s] = per; draw_pairs.append(ladder_draw_pair)
                if unpaired:
                    unpaired_draws.append(seed_draws)
            except SeedUnavailable as e:
                seed_results[s] = {'valid': False, 'reason': str(e), 'fails_every_seed_count_criterion': True}
            except KeyError:
                # A missing private MEDS row must never leak its identifier.
                seed_results[s] = {'valid': False, 'reason': 'required network row missing', 'fails_every_seed_count_criterion': True}
        criteria, summary = evaluate_criteria(seed_results, resize=name in RZ, kernel=name in MIX, unpaired=unpaired)
        out = dict(summary, criteria=criteria, seeds=seed_results, refit_yardstick_n=len(yard), refit_max_abs=refit_max)
        out['transfer_learner_scope'] = ('hand-made statistics trained on the stored frames of the same list'
                                        if name in MIX else 'hand-made statistics trained on the same data')
        # V3's estimand is the mean over read candidate seeds. Bootstrap that
        # empirical population (4 or 5), retaining all five fixed comparators
        # and the planned denominator of five for seed-count criteria.
        if unpaired and len(unpaired_draws) >= 4:
            out['seed_mean_intervals'] = {key: unpaired_seed_component_interval(
                [d[key][0] for d in unpaired_draws], unpaired_draws[0][key][1]) for key in unpaired_draws[0]}
        if len(draw_pairs) >= 4:
            out['ladder_seed_mean_component_ci'] = (unpaired_seed_component_interval([a for a, _ in draw_pairs], draw_pairs[0][1])
                                                    if unpaired else paired_mean_interval([a for a, _ in draw_pairs], [b for _, b in draw_pairs]))
        result['arms'][name] = out
    result['choice'] = decide(result['arms'])
    result['next_step'] = 'fresh-seed confirmation required before freeze' if result['choice'] != 'Sb' and admission['stage'] == 'selection' else 'Sb stays'
    if admission['stage'] == 'confirmation':
        winner = admission['selected_arm']
        result['confirmed'] = result['choice'] == winner
        result['next_step'] = 'freeze and registered sealed read' if result['confirmed'] else 'Sb stays'
    return result


def claim_once(path, intent):
    """Atomic durable claim; a partial scientific read may never be blindly replayed."""
    p = pathlib.Path(path)
    try:
        p.mkdir(parents=False, exist_ok=False)
    except FileExistsError as e:
        raise Refusal('once journal already exists; reconcile without replay') from e
    target = p / 'INTENT.json'
    with target.open('x') as f:
        json.dump(intent, f, indent=2, allow_nan=False); f.flush(); os.fsync(f.fileno())
    fd = os.open(p.parent, os.O_DIRECTORY)
    try:
        os.fsync(fd)
    finally:
        os.close(fd)
    return p


def run_admitted(args, *, n_boot=NB):
    """Production orchestration, also exercised on isolated synthetic inputs."""
    admission, support, pins = preflight(args.root, args.admission)
    validate_support(args.root, admission, support, pins)
    prepared = prepare_contrasts(args.root, admission, n_boot=n_boot)
    if args.preflight:
        print(json.dumps({'admitted': True, 'stage': admission['stage'], 'production_members_opened': False}))
        return
    journal_path = checked_path(admission['once_journal'])
    need(journal_path.is_absolute() and not journal_path.is_relative_to(args.root), 'journal must be outside clean repository')
    need(journal_path.resolve() == ONCE_ROOT / (admission['stage'] + '_rule_v3_once'),
         'once journal is fixed by rule/stage, never chosen per invocation')
    journal = claim_once(journal_path, {'at': dt.datetime.now(dt.timezone.utc).isoformat(), 'stage': admission['stage'],
                                      'head': git(args.root, 'rev-parse', 'HEAD'), 'admission_sha256': digest(args.admission)})
    try:
        result = execute(args.root, admission, support, prepared=prepared, n_boot=n_boot)
        with (journal / 'result.json').open('x') as f:
            json.dump(result, f, indent=2, allow_nan=False); f.flush(); os.fsync(f.fileno())
        (journal / 'COMPLETE').write_text(digest(journal / 'result.json') + '\n')
        print(json.dumps({'choice': result['choice'], 'stage': result['stage'], 'journal': str(journal)}))
    except Exception as e:
        (journal / 'FAILED.json').write_text(json.dumps({'error': str(e), 'replay_permitted': False}, indent=2))
        raise


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--root', type=pathlib.Path, default=pathlib.Path(__file__).resolve().parents[2])
    parser.add_argument('--admission', type=pathlib.Path, required=True)
    parser.add_argument('--preflight', action='store_true')
    run_admitted(parser.parse_args())


if __name__ == '__main__':
    try:
        main()
    except Refusal as e:
        sys.exit('REFUSED before scientific adoption: ' + str(e))
