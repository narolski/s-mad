"""Generated native payloads only; no experiment files, scores or journals.

Run: python -I src/NEXT/tests/mock_native_adapters.py
"""
import copy
import hashlib
import importlib.util
import io
import json
import pathlib
import tarfile
import tempfile
import unittest
from unittest.mock import patch

import numpy as np

HERE = pathlib.Path(__file__).resolve().parents[1]


def module(name):
    spec = importlib.util.spec_from_file_location(name, HERE / (name + '.py'))
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


N = module('native_adapters')
S = module('read_selection')


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def js(value):
    return json.dumps(value).encode()


def npz(**values):
    f = io.BytesIO()
    np.savez(f, **values)
    return f.getvalue()


def source(origin='AB1FM', arm='SbFM', seed=408):
    return dict(name=f'{origin}_{arm}_s{seed}', arm=arm, seed=seed, sha256='a' * 64)


def gate(src):
    _, manifest, count = N.source_identity(src)
    return dict(tar=src['name'] + '.tar', tar_sha256=src['sha256'], manifest=manifest,
                n=count, verdict='passed', n_differ=0, max_abs=0, own_rule_agree=1,
                device='NVIDIA H100')


def family(src):
    return npz(id=np.array(['synthetic-0', 'synthetic-1']), logit=np.array([-.2, .7], np.float32), seed=src['seed'])


def supplement(src):
    _, manifest, count = N.source_identity(src)
    receipt = js({'synthetic': True})
    config = dict(schema='AB1FMSUPP-v1', expected_gpu='NVIDIA H100',
                  pre_read_receipt_sha256=sha(receipt),
                  models=[dict(src, gate_manifest=manifest, gate_rows=count)])
    members = {'./config.json': js(config), './pre_read_receipt.json': receipt,
               './gate_' + src['name'] + '.json': js(gate(src))}
    families = []
    for name in ('tt1', 'meds'):
        raw = family(src)
        members['./' + src['name'] + '__' + name + '.npz'] = raw
        families.append(dict(name=name, valid=True, sha256=sha(raw)))
    members['./technical_status.json'] = js(dict(eight_row_smoke_passed=True, fits=0,
        scientific_contrasts_read=False, failures=1, models=[dict(name=src['name'], seed=src['seed'], gate='passed',
                                                               families=families), dict(name='other', gate='refused')]))
    return members, dict(config_sha256=sha(js(config)))


def w2(src):
    return {'out/tasks.txt': (src['name'] + '\nother-refused\n').encode(),
            'out/gpu.txt': b'GPU-synthetic, NVIDIA H100\n',
            'out/scripts.sha256': ''.join(f'{h}  {p}\n' for p, h in N.W2_SCRIPTS.items()).encode(),
            'out/n_fail.txt': b'1\n', 'out/n_refused.txt': b'1\n',
            'out/gate_' + src['name'] + '.json': js(gate(src)),
            **{'out/W2_' + src['name'] + '_' + f + '.npz': family(src) for f in ('ms1ffhq', 'tt1', 'meds')}}


class NativeTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix='next-native-', dir='/tmp/opencode')
        self.addCleanup(self.temp.cleanup)

    def tar(self, members, **extra):
        path = pathlib.Path(self.temp.name) / 'synthetic.tar'
        with tarfile.open(path, 'w') as tf:
            for name, data in members.items():
                info = tarfile.TarInfo(name)
                info.size = len(data)
                tf.addfile(info, io.BytesIO(data))
        return dict(archive=str(path), sha256=sha(path.read_bytes()), **extra)

    def ids(self, *families):
        return {f: ['synthetic-0', 'synthetic-1'] for f in families}

    def test_supplement_native_dot_prefix_and_other_failed_model(self):
        for src in (source(), source('AB1', 'Sb')):
            members, extra = supplement(src)
            result = N.load_sbfm_supplement(self.tar(members, **extra), src, self.ids('tt1', 'meds'))
            self.assertGreater(result['meds']['synthetic-1'], 0)
            self.assertTrue(result['border_path'].startswith('AB1FMSUPP:'))

    def test_gate_refusal_precedes_any_score_decode(self):
        for src, loader in ((source(), 'supplement'), (source('BB2L', 'Sb', 403), 'w2')):
            members, extra = supplement(src) if loader == 'supplement' else (w2(src), {})
            key = ('./' if loader == 'supplement' else 'out/') + 'gate_' + src['name'] + '.json'
            bad = gate(src)
            bad['max_abs'] = 1e-12  # no tolerance fallback
            members[key] = js(bad)
            fn = N.load_sbfm_supplement if loader == 'supplement' else N.load_dinov3_w2
            ids = self.ids('tt1', 'meds') if loader == 'supplement' else self.ids('ms1ffhq', 'tt1', 'meds')
            with patch.object(N, 'unpack_npz', side_effect=AssertionError('opened before gate')):
                with self.assertRaisesRegex(N.NativeRefusal, 'identity gate'):
                    fn(self.tar(members, **extra), src, ids)

    def test_full_gate_source_manifest_rows_and_gpu(self):
        src = source('BB2L', 'Sb', 403)
        for field, value in [('n', 6339), ('tar_sha256', 'b' * 64), ('tar', 'BB2_Sb_s403.tar'),
                             ('manifest', 'ab1_eval.csv'), ('device', 'NVIDIA A100'), ('own_rule_agree', .999)]:
            with self.subTest(field=field):
                members = w2(src)
                g = gate(src); g[field] = value
                members['out/gate_' + src['name'] + '.json'] = js(g)
                with self.assertRaises(N.NativeRefusal):
                    N.load_dinov3_w2(self.tar(members), src, self.ids('ms1ffhq', 'tt1', 'meds'))

    def test_w2_decodes_candidate_control_comparator_and_preserves_counters(self):
        for src in (source('BB2L', 'Sb', 403), source('BB2L', 'A', 407), source('AB1', 'Sb', 412)):
            out = N.load_dinov3_w2(self.tar(w2(src)), src, self.ids('ms1ffhq', 'tt1', 'meds'))
            self.assertEqual(out['technical_failures'], dict(n_fail=1, n_refused=1))
            self.assertEqual(set(out['ms1ffhq']), {'synthetic-0', 'synthetic-1'})

    def test_supplement_partial_config_and_family_integrity(self):
        src = source()
        for mutation in ('partial', 'config', 'family', 'receipt'):
            members, extra = supplement(src)
            if mutation == 'partial':
                del members['./technical_status.json']
            else:
                key = {'config': './config.json', 'family': './' + src['name'] + '__meds.npz',
                       'receipt': './pre_read_receipt.json'}[mutation]
                members[key] += b' '
            with self.assertRaises(N.NativeRefusal):
                N.load_sbfm_supplement(self.tar(members, **extra), src, self.ids('tt1', 'meds'))

    def test_score_order_shape_finiteness_and_seed(self):
        src = source('BB2L', 'Sb', 403)
        for change in (dict(id=['synthetic-1', 'synthetic-0']), dict(id=['synthetic-0'] * 2),
                       dict(logit=[[.1, .2]]), dict(logit=[np.nan, .2]), dict(seed=404),
                       dict(logit=np.array([1, 2], dtype=object))):
            values = dict(id=['synthetic-0', 'synthetic-1'], logit=np.array([.1, .2]), seed=403)
            values.update(change)
            members = w2(src)
            members['out/W2_' + src['name'] + '_meds.npz'] = npz(**values)
            with self.assertRaises(ValueError):
                N.load_dinov3_w2(self.tar(members), src, self.ids('ms1ffhq', 'tt1', 'meds'))

    def test_tar_alias_traversal_and_digest(self):
        for members in ({'x': b'a', './x': b'b'}, {'../x': b'a'}, {'/x': b'a'}):
            with self.assertRaises(N.NativeRefusal):
                with N.archive(self.tar(members)):
                    self.fail('unsafe archive accepted')
        record = self.tar({'x': b'a'}); record['sha256'] = '0' * 64
        with self.assertRaises(N.NativeRefusal):
            with N.archive(record):
                self.fail('wrong digest accepted')

    def test_fresh_and_gx_sources_refused_without_invented_schema(self):
        for src in (source(seed=413), source('BB2L', 'Sb', 413), source('GX1', 'GX', 408)):
            with self.assertRaises(N.NativeRefusal):
                N.source_identity(src)

    def test_fit_native_roundtrip_and_training_integrity(self):
        for src in (source(), source('AB1', 'A'), source('BB2L', 'Sb', 403)):
            origin, _, count = N.source_identity(src)
            arch = 'a12_dinov3_vitl16_madation' if origin == 'BB2L' else 'a12_clip_vitb16_madation'
            overlay = {'AB1FM': 'e554b84f74e5de8791fddc168b99a7c46376ee48ab7902baf358ecbe668d8e47',
                       'AB1': '171fdb213444442762d4a716b7470dd885cd5879ba9ddda0c542060af4b4d149',
                       'BB2L': '7c0a0b41f2e7bf656dc49db33c34a33ef62b10e8f0aaec24e247e684098d0bad'}[origin]
            ids = [f'generated-{i}' for i in range(count)]
            rows = [dict(path='train/a', kind='lad_S3', label=0), dict(path='train/b', kind='lad_S4', label=1)]
            tr = dict(path=['train/a', 'train/b'], kind=['lad_S3', 'lad_S4'], label=[0, 1],
                      logit=np.array([-.2, .4]), manifest_sha256='train-pin')
            prefix = src['name'] + '/'
            members = {prefix + 'gpu.txt': b'NVIDIA H100',
                prefix + 'task_info.txt': (f'pack_sha256 96c31ae29c4118947e3fd0a7a97600805cbfa5a82369c8ecbc6ee3d6349f2004 '
                    f'overlay_sha256 {overlay} arch {arch} steps 6250 limit 0 lr 1.17e-05 bs 128 accum 2').encode(),
                prefix + 'task.env': f'TASK={src["name"]}\nARM={src["arm"]}\nSEED={src["seed"]}\n'.encode(),
                prefix + 'meta.json': js(dict(seed=src['seed'], steps=6250, n_items=3, res=224, arch=arch)),
                prefix + 'train.log': b'step 6250 loss=0.1\n',
                prefix + 'scores_eval.npz': npz(id=ids, logit=np.zeros(count), manifest_sha256='eval-pin'),
                prefix + 'scores_train.npz': npz(**tr)}
            def load():
                record = self.tar(members, prefix=src['name'], arm=src['arm'], seed=src['seed'], batch_spec=[128, 2])
                return N.load_fit(record, ids, rows, 'train-pin', 'eval-pin', 3)
            self.assertEqual(len(load()['x']), count)
            for change in (dict(path=['train/b', 'train/a']), dict(label=[1, 0]),
                           dict(logit=np.array([[.1, .2]])), dict(manifest_sha256='wrong')):
                bad = dict(tr, **change)
                members[prefix + 'scores_train.npz'] = npz(**bad)
                with self.assertRaises(N.NativeRefusal):
                    load()


class ConfirmationTests(unittest.TestCase):
    def test_prior_result_binds_rule_and_fixed_order(self):
        arms = {name: dict(status='not_read') for name in S.ORDER}
        arms['SbMR'] = dict(status='read', criteria={k: True for k in 'abcdef'})
        result = dict(schema='next-selection-result-v1', stage='selection', rule_sha256='rule', choice='SbMR', arms=arms)
        S.validate_confirmation_selection(result, 'SbMR', 'rule')
        for change in (dict(stage='confirmation'), dict(rule_sha256='other'), dict(choice='Sb'), dict(arms={})):
            with self.assertRaises(S.Refusal):
                S.validate_confirmation_selection(dict(result, **change), 'SbMR', 'rule')
        earlier = copy.deepcopy(result)
        earlier['arms']['SbFM'] = dict(status='read', criteria={k: True for k in 'abcdef'})
        with self.assertRaisesRegex(S.Refusal, 'fixed-order'):
            S.validate_confirmation_selection(earlier, 'SbMR', 'rule')


if __name__ == '__main__':
    unittest.main()
