"""End-to-end synthetic NEXT admission/dispatch; never touches experiment data.

Only git control-plane and immutable production manifest/source constants are
replaced by generated equivalents. Native tar readers, gates, row validation,
contrast preparation, statistics and decisions execute normally.
"""
import copy
import contextlib
import csv
import importlib.util
import io
import json
import pathlib
import tarfile
import tempfile
import unittest
from types import SimpleNamespace
from unittest.mock import patch

import numpy as np

HERE = pathlib.Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location('fixtures', HERE / 'mock_native_adapters.py')
F = importlib.util.module_from_spec(spec); spec.loader.exec_module(F)
S, N = F.S, F.N


def write_csv(path, rows):
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open('w', newline='') as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0])); w.writeheader(); w.writerows(rows)


def tar(path, members):
    with tarfile.open(path, 'w') as tf:
        for name, raw in members.items():
            m = tarfile.TarInfo(name); m.size = len(raw); tf.addfile(m, io.BytesIO(raw))
    return dict(archive=str(path), sha256=S.digest(path))


class Fixture:
    def __init__(self, root):
        self.root = root; self.files = []; self.manifests = {}; self.receipts = {}
        self.rows = {}
        for name, n, positives in [('lcomb', 3000, 1000), ('ladder', 360, 180)]:
            self.rows[name] = [dict(id=f'{name}-{i}', label=str(int(i < positives)), component=str(i % 110),
                                    D='1', floor='0') for i in range(n)]
        self.rows['matched'] = [dict(r, pair=str(i % 360)) for i, r in enumerate(self.rows['lcomb'][:360] + self.rows['lcomb'][1000:1360])]
        for key in ('lcomb_bal', 'ladder_dev', 'ladder_test', 'ladder_no_shape', 'facemorpher'):
            self.rows[key] = self.rows['ladder']
        self.input_files = {}
        for key, rows in self.rows.items():
            p = root / (key + '.csv'); write_csv(p, rows); self.files.append(p); self.input_files[key] = p.name
        for tag in ('Sb', 'SbFM'):
            rows = [dict(r, set=target, logreg='0', gbt='0') for key, target in
                    [('lcomb', 'lcomb'), ('ladder', 'sel360'), ('matched', 'lcomb_smatch')] for r in self.rows[key]]
            # common CSV fields, pair is descriptive and omitted here
            rows = [{k: r[k] for k in ('id', 'label', 'component', 'set', 'logreg', 'gbt')} for r in rows]
            if tag == 'SbFM':
                for r in rows:
                    r['logreg'] = r['gbt'] = r['label']
            p = root / ('transfer_' + tag + '.csv'); write_csv(p, rows); self.files.append(p)
        base = []
        for row in self.rows['lcomb'] + self.rows['ladder']:
            base.append(dict(id=row['id'], fam='synthetic', role='dev', rung='', tool='', strength='', label=row['label']))
        base += [dict(id=f'guard-{i}', fam='ladder', role='test', rung='R4' if i < 191 else 'R2w',
                      tool='opencv', strength='', label=str(int(i < 191))) for i in range(382)]
        base += [dict(id=i, fam='synthetic', role='dev', rung='', tool='', strength='', label='0')
                 for i in ['native0', 'native1', 'stored0', 'stored1', 'morph0', 'morphstore0'] +
                 [f's3-{i}' for i in range(100)] + [f'border-{i}' for i in range(1582)]]
        self.base = base
        for key, count in [('fs_eval', 19797), ('ab1_eval', 21277), ('fm_eval', 24859)]:
            rows = base + [dict(id=f'pad-{i}', fam='synthetic', role='dev', rung='', tool='', strength='', label='0')
                           for i in range(count-len(base))]
            self.manifest(key, rows)
        for arm in ('A', 'B', 'Sb', 'SbFM'):
            self.manifest('train_' + arm, [dict(path='train/s3', kind='lad_S3', label='0'),
                                         dict(path='train/s4', kind='lad_S4', label='1')])
        self.manifest('tt1', [dict(id=f'border-{i}' if i < 1582 else f'tt-{i}', fam='tt1') for i in range(30994)])
        self.manifest('meds', [dict(id=f'private-synthetic-{i}', fam='meds', aligned='1') for i in range(1018)])
        ms = ['stored0', 'stored1', 'morphstore0'] + [f'ms-{i}' for i in range(1477)]
        self.manifest('ms1', [dict(id=i, fam='ms1ffhq') for i in ms])
        self.manifest('cross', [dict(id='cross0')])
        self.networks = {}; self.inventory = {}; self.fit_members = {}
        for origin, arms, seeds in [('AB1', ('A', 'Sb'), range(408, 413)), ('AB1FM', ('SbFM',), range(408, 413)),
                                    ('BB2L', ('A', 'B', 'Sb'), range(403, 408))]:
            for arm in arms:
                for seed in seeds:
                    self.fit(origin, arm, seed)
        self.supplements = {}; self.make_supplements()
        self.support = dict(schema='next-support-v1', S3_ids=[f's3-{i}' for i in range(100)],
            border_ids=[f'border-{i}' for i in range(1582)],
            tt1_families={f'f{i}': [f'tt-{1600+i}'] for i in range(7)},
            meds_manifest_path=str(root / 'meds_manifest.csv'), meds_manifest_sha256=self.manifests['meds']['sha256'],
            meds_primary=[dict(row_index=i, person=i % 400) for i in range(865)],
            eval_sha256=self.manifests['fm_eval']['sha256'], tt1_sha256=self.manifests['tt1']['sha256'],
            meds_score_manifest_sha256=self.manifests['meds']['sha256'], cross_sha256=self.manifests['cross']['sha256'],
            kernel=dict(train9=[f'k{i}' for i in range(9)], held4=[f'k{i}' for i in range(9, 13)]),
            train={k: dict(sha256=self.manifests[v]['sha256'], n_items=2) for k, v in [('A0', 'train_A'), ('Sb0', 'train_Sb')]},
            sources={str(root / v['path']): v['sha256'] for v in self.manifests.values()},
            storage=dict(native_photo_ids=['native0', 'native1'],
                         pairs={z: [dict(native='native0', stored='stored0'), dict(native='native1', stored='stored1')]
                                for z in ('fm61', 'amsl112')},
                         morph_pairs={z: [dict(native='morph0', stored='morphstore0')] for z in ('fm61', 'amsl112')}))
        self.json('support.json', self.support)
        p = root / S.RULE; p.parent.mkdir(parents=True); p.write_text('**Status: APPROVED.**\n'); self.files.append(p)
        self.json('inventory.json', self.inventory)
        self.json('mode.json', dict(mode='five', seeds=list(range(403, 408)),
                                   tars={k + '.tar': h for k, h in self.inventory.items() if k.startswith('BB2L_')}))
        p = root / 'eligibility.md'; p.write_text('Synthetic independently pinned eligibility fixture.\n'); self.files.append(p)
        self.a = dict(schema='next-admission-v1', stage='selection', approved=True, batch_closed=True,
            numpy_version=np.__version__, pinfiles=['pins.sha256'], support='support.json', review='review.md',
            receipt_manifest='receipts.json', input_files=self.input_files,
            transfer_files={k: 'transfer_' + k + '.csv' for k in ('Sb', 'SbFM')},
            transfer_training_sha256={k: self.manifests['train_' + k]['sha256'] for k in ('Sb', 'SbFM')},
            floor_columns={key: {k: 'floor' for k in ('all_cue', 'non_F27_non_BLEND', 'surround', 'face_box')}
                           for key in ('lcomb', 'ladder', 'matched')},
            rule_sha256=S.digest(root / S.RULE), native_source_inventory='inventory.json', dinov3_seed_mode='mode.json',
            native_manifests=self.manifests, networks=self.networks, supplements=self.supplements, arms={},
            once_journal=str(root / 'selection_rule_v3_once'))
        self.path = root / 'admission.json'

    def json(self, name, value):
        p = self.root / name; p.parent.mkdir(parents=True, exist_ok=True); p.write_text(json.dumps(value))
        if p not in self.files: self.files.append(p)
        return p

    def manifest(self, key, rows):
        p = self.root / (key + '_manifest.csv'); write_csv(p, rows); self.files.append(p)
        self.manifests[key] = dict(path=p.name, sha256=S.digest(p))

    def values(self, ids, origin, arm, seed):
        values = []
        for id in ids:
            v = -1.
            if id.startswith(('lcomb-', 'ladder-')):
                positive = int(id.split('-')[1]) < (1000 if id.startswith('lcomb') else 180)
                v = (1. if positive else -1.) if origin != 'AB1' else (1000. if positive else -1000.) if seed == 408 else 0.
            elif id.startswith('guard-'):
                v = (1. if int(id.split('-')[1]) < 191 else -1.) if origin != 'AB1' else 0.
            elif id == 'native0': v = -2.
            elif id == 'native1': v = -1.
            elif id.startswith('stored'): v = 2. if arm == 'A' else -1.
            elif id.startswith('morph'): v = 2.
            elif id.startswith('border'): v = 99.  # must be replaced from gated TT1
            values.append(v)
        return np.asarray(values, np.float32)

    def fit(self, origin, arm, seed):
        name = f'{origin}_{arm}_s{seed}'
        evalkey = {'AB1': 'ab1_eval', 'AB1FM': 'fm_eval', 'BB2L': 'fs_eval'}[origin]
        ids = [r['id'] for r in S.read_csv(self.root / self.manifests[evalkey]['path'])]
        arch = 'a12_dinov3_vitl16_madation' if origin == 'BB2L' else 'a12_clip_vitb16_madation'
        overlay = {'AB1': S.PINS['ab1_overlay'], 'AB1FM': 'e554b84f74e5de8791fddc168b99a7c46376ee48ab7902baf358ecbe668d8e47',
                   'BB2L': '7c0a0b41f2e7bf656dc49db33c34a33ef62b10e8f0aaec24e247e684098d0bad'}[origin]
        members = {name + '/' + k: raw for k, raw in {
            'gpu.txt': b'NVIDIA H100', 'task.env': f'TASK={name}\nARM={arm}\nSEED={seed}\n'.encode(),
            'task_info.txt': f'pack_sha256 {S.PINS["pack_sha256"]} overlay_sha256 {overlay} arch {arch} steps 6250 limit 0 lr 1.17e-05 bs 256 accum 1'.encode(),
            'meta.json': F.js(dict(seed=seed, steps=6250, n_items=2, res=224, arch=arch)), 'train.log': b'step 6250 loss .1',
            'scores_eval.npz': F.npz(id=ids, logit=self.values(ids, origin, arm, seed), manifest_sha256=self.manifests[evalkey]['sha256']),
            'scores_train.npz': F.npz(path=['train/s3', 'train/s4'], kind=['lad_S3', 'lad_S4'], label=[0, 1], logit=[-1., 1.],
                                       manifest_sha256=self.manifests['train_' + arm]['sha256'])}.items()}
        self.fit_members[name] = members
        rec = tar(self.root / (name + '.tar'), members)
        self.networks[name] = dict(rec, format='native_fit', prefix=name, arm=arm, seed=seed, batch_spec=[256, 1])
        self.inventory[name] = rec['sha256']; self.receipt(name, rec)

    def receipt(self, key, rec):
        self.receipts[key] = dict(rec, hash_verified=True, verified_at='2026-11-14T12:00:00+01:00')
        if key in getattr(self, 'supplements', {}):
            self.receipts[key]['producer_sha256'] = self.supplements[key]['producer_sha256']

    def make_supplements(self):
        self.supp_members = {}
        for route in ('fm', 'w2'):
            names = [k for k in self.networks if (k.startswith('AB1FM_') or k.startswith('AB1_Sb'))] if route == 'fm' else [k for k in self.networks if k.startswith(('BB2L_', 'AB1_Sb'))]
            members = {}; models = []; status = []
            for name in names:
                n = self.networks[name]; src = dict(name=name, arm=n['arm'], seed=n['seed'], sha256=n['sha256'])
                _, manifest, count = N.source_identity(src)
                models.append(dict(src, gate_manifest=manifest, gate_rows=count))
                pre = './' if route == 'fm' else 'out/'
                members[pre + 'gate_' + name + '.json'] = F.js(F.gate(src))
                family_status = []
                for family in (('tt1', 'meds') if route == 'fm' else ('ms1ffhq', 'tt1', 'meds')):
                    mk = 'ms1' if family == 'ms1ffhq' else family
                    ids = [r['id'] for r in S.read_csv(self.root / self.manifests[mk]['path'])]
                    values = self.values(ids, name.split('_')[0], n['arm'], n['seed']) if family == 'ms1ffhq' else np.full(len(ids), -1.)
                    raw = F.npz(id=ids, logit=values, seed=n['seed'])
                    members[pre + (name + '__' + family if route == 'fm' else 'W2_' + name + '_' + family) + '.npz'] = raw
                    family_status.append(dict(name=family, valid=True, sha256=F.sha(raw)))
                status.append(dict(name=name, seed=n['seed'], gate='passed', families=family_status))
            extra = {}
            if route == 'fm':
                receipt = F.js(dict(synthetic=True))
                cfg = dict(schema='AB1FMSUPP-v1', expected_gpu='NVIDIA H100', models=models, pre_read_receipt_sha256=F.sha(receipt))
                p = self.json('src/recovery_20261114/sbfm_supplement/config.json', cfg)
                members.update({'./config.json': p.read_bytes(), './pre_read_receipt.json': receipt,
                                './technical_status.json': F.js(dict(eight_row_smoke_passed=True, fits=0, scientific_contrasts_read=False, models=status))})
                extra = dict(config=str(p.relative_to(self.root)), config_sha256=S.digest(p))
            else:
                members.update({'out/tasks.txt': ('\n'.join(names) + '\n').encode(), 'out/gpu.txt': b'NVIDIA H100',
                    'out/scripts.sha256': ''.join(f'{h}  {k}\n' for k, h in N.W2_SCRIPTS.items()).encode(),
                    'out/n_fail.txt': b'0', 'out/n_refused.txt': b'0'})
            self.supp_members[route] = members
            rec = tar(self.root / (route + '.tar'), members)
            fmt = 'sbfm_supplement' if route == 'fm' else 'dinov3_w2'
            producer, _ = S.NATIVE_PRODUCERS[fmt]
            p = self.root / producer; p.parent.mkdir(parents=True, exist_ok=True)
            p.write_text('Synthetic producer fixture, never executed.\n')
            if p not in self.files: self.files.append(p)
            rec['producer_sha256'] = S.digest(p)
            self.supplements[route] = dict(rec, format=fmt, **extra)
            self.receipt(route, rec)

    def admit(self, which):
        self.a['arms'] = {k: dict(status='not_read', reason='missing_seeds', evidence='eligibility.md') for k in S.ORDER}
        for arm in which:
            dino = arm == 'DINOv3'; seeds = list(range(403, 408)) if dino else list(range(408, 413))
            self.a['arms'][arm] = dict(status='read', pre_binding_scientific_open=False, eligibility_review='eligibility.md',
                seeds=seeds, supplement='w2' if dino else 'fm',
                candidate={str(s): f'BB2L_Sb_s{s}' if dino else f'AB1FM_SbFM_s{s}' for s in seeds},
                control={str(s): f'BB2L_A_s{s}' if dino else f'AB1_A_s{s}' for s in seeds},
                comparator={str(s): f'AB1_Sb_s{s}' for s in range(408, 413)})
            if dino: self.a['arms'][arm]['fit_guard'] = {str(s): f'BB2L_B_s{s}' for s in seeds}
        self.repin()

    def repin(self):
        self.json('receipts.json', self.receipts)
        self.json('admission.json', self.a)
        p = self.root / 'review.md'; p.write_text('NEXT_ADMISSION_GO ' + S.digest(self.path) + '\n')
        files = set(self.files + [p, S.NATIVE_CODE, pathlib.Path(S.__file__)])
        (self.root / 'pins.sha256').write_text(''.join(S.digest(p) + '  ' + str(p) + '\n' for p in sorted(files)))

    def fake_git(self, root, *args, binary=False):
        if args[0] == 'show': return (root / args[1].split(':', 1)[1]).read_bytes()
        return b'' if binary else ''

    def patches(self):
        from contextlib import ExitStack
        stack = ExitStack()
        stack.enter_context(patch.object(S, 'git', side_effect=self.fake_git))
        stack.enter_context(patch.object(S, 'NATIVE_MANIFEST_PINS', {k: v['sha256'] for k, v in self.manifests.items()}))
        stack.enter_context(patch.object(S, 'AB1_SB_SOURCE_PINS', {s: self.networks[f'AB1_Sb_s{s}']['sha256'] for s in range(408, 413)}))
        stack.enter_context(patch.object(S, 'SBFM_CONFIG_SHA256', self.supplements['fm']['config_sha256']))
        stack.enter_context(patch.object(S, 'NATIVE_PRODUCERS', {k: (p, S.digest(self.root / p)) for k, (p, _) in S.NATIVE_PRODUCERS.items()}))
        return stack

    def run(self, claim=False):
        a, support, pins = S.preflight(self.root, self.path)
        S.validate_support(self.root, a, support, pins)
        prepared = S.prepare_contrasts(self.root, a, n_boot=12)
        if claim: S.claim_once(self.root / 'synthetic-once', {'synthetic': True})
        return S.execute(self.root, a, support, n_boot=12, prepared=prepared)


class Integration(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.temp = tempfile.TemporaryDirectory(prefix='next-integration-', dir='/tmp/opencode')
        cls.addClassCleanup(cls.temp.cleanup)
        cls.f = Fixture(pathlib.Path(cls.temp.name))

    def setUp(self):
        self.f.admit(['SbFM', 'DINOv3'])

    def test_complete_native_admission_once_dispatch_and_fixed_order(self):
        f = self.f
        original = S.native_network
        def guarded(*args, **kwargs):
            self.assertTrue((f.root / 'synthetic-once' / 'INTENT.json').exists())
            return original(*args, **kwargs)
        with f.patches(), patch.object(S, 'native_network', side_effect=guarded):
            # No archive member operation is permitted anywhere in preflight.
            with patch.object(tarfile, 'open', side_effect=AssertionError('member access during preflight')):
                S.preflight(f.root, f.path)
            result = f.run(claim=True)
            self.assertEqual(result['choice'], 'SbFM')
            for name in ('SbFM', 'DINOv3'):
                self.assertTrue(all(result['arms'][name]['criteria'].values()), result['arms'][name]['criteria'])
            dino = result['arms']['DINOv3']
            self.assertAlmostEqual(dino['seed_mean_lcomb_gain'], .4)  # mean AUC, NOT AUC of mean logits
            self.assertTrue(dino['unpaired'])
            self.assertEqual(len(dino['seeds']['403']['detection']['lcomb']['comparator_floor_prints']), 5)
            self.assertEqual(dino['seeds']['403']['network']['border'], 0.)
            self.assertIn('seen engine', result['arms']['SbFM']['seeds']['408']['descriptive']['facemorpher']['label'])
            fm = result['arms']['SbFM']['seeds']['409']['detection']['lcomb']
            self.assertEqual(fm['floors']['same_data_transfer_gbt']['auc'], 1.)
            self.assertEqual(fm['comparator_floor_prints']['floors']['same_data_transfer_gbt']['auc'], .5)
            self.assertEqual(set(dino['seed_mean_intervals']), set(f.rows))
            with self.assertRaises(S.Refusal): S.claim_once(f.root / 'synthetic-once', {})

    def test_preflight_mutations_never_open_member(self):
        f = self.f
        mutations = [lambda: f.a['arms']['DINOv3']['comparator'].__setitem__('408', None),
                     lambda: f.a['arms']['SbFM'].__setitem__('supplement', 'w2'),
                     lambda: f.a['transfer_training_sha256'].__setitem__('SbFM', '0' * 64),
                     lambda: f.receipts['fm'].__setitem__('verified_at', '2026-11-16T12:00:00+01:00'),
                     lambda: f.receipts['w2'].__setitem__('producer_sha256', '0' * 64),
                     lambda: f.a['networks']['AB1FM_SbFM_s408'].__setitem__('sha256', '0' * 64),
                     lambda: f.a['arms']['DINOv3']['control'].__setitem__('403', 'BB2L_A_s404')]
        saved_a, saved_r = copy.deepcopy(f.a), copy.deepcopy(f.receipts)
        try:
            for mutation in mutations:
                f.a, f.receipts = copy.deepcopy(saved_a), copy.deepcopy(saved_r)
                mutation(); f.repin()
                with f.patches(), patch.object(tarfile, 'open', side_effect=AssertionError('opened')):
                    with self.assertRaises(S.Refusal): S.preflight(f.root, f.path)
        finally:
            f.a, f.receipts = saved_a, saved_r; f.repin()

    def test_missing_candidate_keeps_denominator_and_missing_comparator_blocks(self):
        f = self.f; f.admit(['DINOv3'])
        f.a['arms']['DINOv3']['candidate']['403'] = None; f.repin()
        bootstrap = S.unpaired_seed_component_interval
        with f.patches(), patch.object(S, 'unpaired_seed_component_interval', wraps=bootstrap) as intervals:
            result = f.run()
            arm = result['arms']['DINOv3']
            self.assertEqual(result['choice'], 'DINOv3')
            self.assertEqual((arm['read_seeds'], arm['denominator']), (4, 5))
            self.assertAlmostEqual(arm['seed_mean_lcomb_gain'], .4)
            self.assertFalse(arm['seeds']['403']['valid'])
            self.assertTrue(arm['seeds']['403']['fails_every_seed_count_criterion'])
            self.assertEqual(set(arm['seed_mean_intervals']), set(f.rows))
            self.assertEqual(arm['ladder_seed_mean_component_ci'], arm['seed_mean_intervals']['ladder'])
            self.assertEqual(intervals.call_count, len(f.rows) + 1)
            for call in intervals.call_args_list:
                self.assertEqual(np.asarray(call.args[0]).shape, (4, 12))
                self.assertEqual(np.asarray(call.args[1]).shape, (5, 12))
            # All four surviving seeds must pass each four-of-five count.
            per = copy.deepcopy(arm['seeds'])
            per['404']['own_registration_guards'] = False
            self.assertFalse(S.evaluate_criteria(per, unpaired=True)[0]['f'])
        f.a['arms']['DINOv3']['candidate']['404'] = None; f.repin()
        with f.patches():
            result = f.run()
            self.assertEqual(result['choice'], 'Sb')
            self.assertEqual(result['arms']['DINOv3']['read_seeds'], 3)
            self.assertNotIn('seed_mean_intervals', result['arms']['DINOv3'])
            self.assertNotIn('ladder_seed_mean_component_ci', result['arms']['DINOv3'])

    def test_four_by_five_read_seed_bootstrap_oracle(self):
        # Nonconstant seed effects and shared component variation distinguish
        # independent 4/5 resampling from pairing, imputation and mean logits.
        row = np.linspace(-7., 9., 2000)
        candidate = np.array([.05, .3, .7, 1.2])[:, None] + row
        comparator = np.array([-.2, .1, .4, .6, .8])[:, None] + row
        rng = np.random.default_rng(np.random.SeedSequence(20261115).spawn(1)[0])
        values = []
        for j in range(2000):
            ca = rng.integers(0, 4, size=4)
            cb = rng.integers(0, 5, size=5)
            values.append(candidate[ca, j].mean() - comparator[cb, j].mean())
        np.testing.assert_allclose(S.unpaired_seed_component_interval(candidate, comparator),
                                   np.percentile(values, [2.5, 97.5]), rtol=0, atol=1e-14)

    def test_failed_comparator_gate_and_changed_module_abort_globally(self):
        f = self.f; f.admit(['DINOv3'])
        members = copy.deepcopy(f.supp_members['w2'])
        gate = json.loads(members['out/gate_AB1_Sb_s408.json']); gate['n_differ'] = 1
        members['out/gate_AB1_Sb_s408.json'] = F.js(gate)
        try:
            rec = tar(f.root / 'w2.tar', members)
            f.supplements['w2'].update(rec); f.receipt('w2', rec); f.repin()
            with f.patches():
                with self.assertRaisesRegex(S.Refusal, 'five-comparator mean undefined'):
                    f.run()
        finally:
            rec = tar(f.root / 'w2.tar', f.supp_members['w2'])
            f.supplements['w2'].update(rec); f.receipt('w2', rec); f.repin()
        with f.patches():
            a, _, _ = S.preflight(f.root, f.path)
            real_digest = S.digest
            with patch.object(S, 'digest', side_effect=lambda p: 'changed' if pathlib.Path(p) == S.NATIVE_CODE else real_digest(p)):
                with self.assertRaisesRegex(S.Refusal, 'module changed'):
                    S.native_network(a, 'BB2L_Sb_s403', 'w2')

    def test_registered_fit_and_original_engine_guards_affect_decision(self):
        # Independent fixture avoids changing any other test's admitted sources.
        with tempfile.TemporaryDirectory(prefix='next-guards-', dir='/tmp/opencode') as tmp:
            f = Fixture(pathlib.Path(tmp))
            # Two E3 B fits are finite but under-trained; two SbFM seeds lose
            # the registered original-engine contrast. Detection stays strong.
            for name in ('BB2L_B_s403', 'BB2L_B_s404', 'AB1FM_SbFM_s408', 'AB1FM_SbFM_s409'):
                members = f.fit_members[name]
                member = name + ('/scores_train.npz' if name.startswith('BB2L') else '/scores_eval.npz')
                z = N.unpack_npz(members[member])
                if name.startswith('BB2L'):
                    z['logit'] = np.array([-1., -1.])
                else:
                    for i, id in enumerate(z['id']):
                        if id.startswith('guard-'): z['logit'][i] *= -1
                members[member] = F.npz(**z)
                rec = tar(f.root / (name + '.tar'), members)
                f.networks[name].update(rec); f.inventory[name] = rec['sha256']; f.receipt(name, rec)
            f.json('inventory.json', f.inventory)
            f.json('mode.json', dict(mode='five', seeds=list(range(403, 408)),
                                    tars={k + '.tar': h for k, h in f.inventory.items() if k.startswith('BB2L_')}))
            f.make_supplements(); f.admit(['SbFM', 'DINOv3'])
            with f.patches(): result = f.run()
            self.assertEqual(result['choice'], 'Sb')
            for name in ('SbFM', 'DINOv3'):
                self.assertTrue(result['arms'][name]['criteria']['a'])
                self.assertFalse(result['arms'][name]['criteria']['f'])
            self.assertFalse(result['arms']['DINOv3']['seeds']['403']['fit_gates']['three_arm_adequacy'])
            self.assertTrue(result['arms']['DINOv3']['criteria']['b'])  # B adequacy is not the A/X storage gate

    def test_actual_orchestrator_preflight_once_success_and_failed_receipt(self):
        f = self.f; f.admit(['DINOv3'])
        old_journal = f.a['once_journal']
        original = S.native_network
        try:
            for failure in (None, 'candidate', 'comparator'):
                with tempfile.TemporaryDirectory(prefix='next-journal-', dir='/tmp/opencode') as tmp:
                    parent = pathlib.Path(tmp); journal = parent / 'selection_rule_v3_once'
                    f.a['once_journal'] = str(journal)
                    f.a['arms']['DINOv3']['candidate']['403'] = 'BB2L_Sb_s403'
                    f.repin()
                    args = SimpleNamespace(root=f.root, admission=f.path, preflight=True)
                    def guarded(*a, **kw):
                        self.assertTrue((journal / 'INTENT.json').is_file())
                        failed_key = {'candidate': 'BB2L_Sb_s403', 'comparator': 'AB1_Sb_s408'}.get(failure)
                        if a[1] == failed_key:
                            raise S.SeedUnavailable('synthetic post-claim fit failure')
                        return original(*a, **kw)
                    with f.patches(), patch.object(S, 'ONCE_ROOT', parent), contextlib.redirect_stdout(io.StringIO()):
                        with patch.object(tarfile, 'open', side_effect=AssertionError('preflight payload access')):
                            S.run_admitted(args, n_boot=12)
                        self.assertFalse(journal.exists())
                        args.preflight = False
                        with patch.object(S, 'native_network', side_effect=guarded):
                            if failure == 'comparator':
                                with self.assertRaisesRegex(S.Refusal, 'five-comparator mean undefined'):
                                    S.run_admitted(args, n_boot=12)
                                self.assertTrue((journal / 'FAILED.json').exists())
                                self.assertFalse((journal / 'result.json').exists())
                            else:
                                S.run_admitted(args, n_boot=12)
                                raw = (journal / 'result.json').read_text()
                                self.assertEqual(json.loads(raw)['choice'], 'DINOv3')
                                arm = json.loads(raw)['arms']['DINOv3']
                                self.assertEqual((arm['read_seeds'], arm['denominator']),
                                                 (4 if failure == 'candidate' else 5, 5))
                                self.assertEqual(set(arm['seed_mean_intervals']), set(f.rows))
                                self.assertFalse((journal / 'FAILED.json').exists())
                                if failure == 'candidate':
                                    self.assertFalse(arm['seeds']['403']['valid'])
                                    self.assertTrue(arm['seeds']['403']['fails_every_seed_count_criterion'])
                                self.assertNotIn('private-synthetic', raw)
                                self.assertEqual((journal / 'COMPLETE').read_text().strip(), S.digest(journal / 'result.json'))
                        with patch.object(S, 'native_network', side_effect=AssertionError('replay reached payload')):
                            with self.assertRaisesRegex(S.Refusal, 'once journal already exists'):
                                S.run_admitted(args, n_boot=12)
        finally:
            f.a['once_journal'] = old_journal; f.admit(['SbFM', 'DINOv3'])

    def test_plain_control_needs_only_its_registered_storage_rescore(self):
        f = self.f; f.admit(['DINOv3'])
        members = copy.deepcopy(f.supp_members['w2'])
        for seed in range(403, 408):
            del members[f'out/W2_BB2L_A_s{seed}_meds.npz']
            del members[f'out/W2_BB2L_A_s{seed}_tt1.npz']
        try:
            rec = tar(f.root / 'w2.tar', members)
            f.supplements['w2'].update(rec); f.receipt('w2', rec); f.repin()
            with f.patches(): self.assertEqual(f.run()['choice'], 'DINOv3')
        finally:
            rec = tar(f.root / 'w2.tar', f.supp_members['w2'])
            f.supplements['w2'].update(rec); f.receipt('w2', rec); f.repin()

    def test_splice_fit_and_training_accuracy_inclusive_boundaries(self):
        tr = dict(logit=[-1.] * 5 + [1., 2., 3., 4., -2.], label=[0] * 5 + [1] * 5,
                  kind=['lad_S3'] * 5 + ['lad_S4'] * 5)
        gates = S.native_fit_gates(tr, 'BB2L', 'Sb')
        self.assertEqual(gates['splice_fit_auc'], .8)
        self.assertTrue(gates['registration_guards'])
        tr['logit'][0] = 2.
        gates = S.native_fit_gates(tr, 'BB2L', 'Sb')
        self.assertGreaterEqual(gates['training_accuracy'], .75)
        self.assertFalse(gates['registration_guards'])
        tr = dict(logit=[0., 0., 1., -1.], label=[0, 0, 1, 1])
        self.assertTrue(S.native_fit_gates(tr, 'BB2L', 'A')['registration_guards'])
        tr['logit'][0] = 1.
        self.assertFalse(S.native_fit_gates(tr, 'BB2L', 'A')['registration_guards'])
    def test_module_and_native_manifest_pins_required(self):
        f = self.f
        pins = f.root / 'pins.sha256'; saved = pins.read_text()
        try:
            for target in (str(S.NATIVE_CODE), str(f.root / f.manifests['fs_eval']['path'])):
                pins.write_text(''.join(line for line in saved.splitlines(True) if target not in line))
                with f.patches(), patch.object(tarfile, 'open', side_effect=AssertionError('opened')):
                    with self.assertRaises(S.Refusal): S.preflight(f.root, f.path)
        finally: pins.write_text(saved)


if __name__ == '__main__':
    unittest.main(verbosity=2)
