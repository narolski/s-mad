"""Synthetic-only verification; never reads real experiment inputs or scores.

Run with the numpy environment:
  OMP_NUM_THREADS=2 OPENBLAS_NUM_THREADS=2 MKL_NUM_THREADS=2 NUMEXPR_NUM_THREADS=2 \
    nice -n 10 /home/narolski/mambamorph-code/.venv-spark/bin/python -I src/NEXT/tests/mock_selection.py
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

CODE = pathlib.Path(__file__).resolve().parents[1] / 'read_selection.py'
spec = importlib.util.spec_from_file_location('next_selection', CODE)
S = importlib.util.module_from_spec(spec)
spec.loader.exec_module(S)


def passing_seed():
    return dict(valid=True, lcomb_gain=.025, ladder_gain=-.02, matched_gain=.015,
                floors_printed=True, refit_max_abs=.024,
                storage_pass=dict(fm61=True, amsl112=True),
                control_pass=dict(fm61=True, amsl112=True),
                storage_evasion_falsified=dict(fm61=True, amsl112=True),
                Fbar_gain=.02, meds_upper95=.10, S3_gain=.05, border_gain=.01,
                border_same_path=True, kappa_ho=.05, kappa_train=.05,
                own_registration_guards=True)


class NumericAndDecisionTests(unittest.TestCase):
    def test_auc_ties_and_order(self):
        self.assertEqual(S.auc([0, 0, 1, 1], [0, 1, 0, 1]), .5)
        self.assertEqual(S.auc([2, 3, -1, 0], [1, 1, 0, 0]), 1.)
        self.assertEqual(S.auc([-2, -3, 1, 0], [1, 1, 0, 0]), 0.)

    def test_inclusive_unrounded_margins(self):
        r = {str(i): passing_seed() for i in range(5)}
        flags, info = S.evaluate_criteria(r, resize=True, kernel=True)
        self.assertTrue(all(flags.values()), (flags, info))
        for v in r.values():
            v['lcomb_gain'] = np.nextafter(.025, -np.inf)
        self.assertFalse(S.evaluate_criteria(r, resize=True)[0]['a'])

    def test_failed_seed_not_removed_from_five(self):
        r = {str(i): passing_seed() for i in range(5)}
        r['4'] = dict(valid=False)
        flags, info = S.evaluate_criteria(r, resize=True, kernel=True)
        self.assertTrue(all(flags.values()))
        self.assertEqual(info['denominator'], 5)
        self.assertEqual(info['read_seeds'], 4)
        r['3'] = dict(valid=False)
        flags, info = S.evaluate_criteria(r)
        self.assertFalse(any(flags.values()))
        self.assertEqual(info['status'], 'not read (too few seeds)')

    def test_strict_gain_and_refit_rule(self):
        r = {str(i): passing_seed() for i in range(5)}
        for v in r.values():
            v['refit_max_abs'] = .025
        self.assertFalse(S.evaluate_criteria(r, resize=True)[0]['a'])
        for v in r.values():
            v['refit_max_abs'] = None
        self.assertFalse(S.evaluate_criteria(r, resize=True)[0]['a'])

    def test_storage_bound_requires_same_four_seeds_at_both_sizes(self):
        r = {str(i): passing_seed() for i in range(5)}
        r['0']['storage_pass']['fm61'] = False
        r['1']['storage_pass']['amsl112'] = False
        self.assertFalse(S.evaluate_criteria(r)[0]['b'])
        r['1']['storage_pass']['amsl112'] = True
        r['0']['storage_pass']['amsl112'] = False
        self.assertTrue(S.evaluate_criteria(r)[0]['b'])

    def test_every_bar_and_path_guard_matters(self):
        mutations = [
            ('a', 'ladder_gain', -.06000001), ('a', 'matched_gain', .01499999),
            ('c', 'Fbar_gain', .02000001), ('c', 'meds_upper95', .10000001),
            ('d', 'S3_gain', .05000001), ('d', 'border_gain', .01000001),
            ('d', 'border_same_path', False), ('e', 'kappa_ho', .05000001),
            ('e', 'kappa_train', .05000001), ('f', 'own_registration_guards', False),
            ('a', 'floors_printed', False)]
        for criterion, key, value in mutations:
            r = {str(i): passing_seed() for i in range(5)}
            for v in r.values():
                v[key] = value
            self.assertFalse(S.evaluate_criteria(r, resize=True, kernel=True)[0][criterion], key)
        r = {str(i): passing_seed() for i in range(5)}
        for v in r.values():
            v['storage_evasion_falsified']['amsl112'] = False
        self.assertFalse(S.evaluate_criteria(r)[0]['b'])

    def test_kernel_quantities_have_separate_four_seed_counts(self):
        r = {str(i): passing_seed() for i in range(5)}
        r['0']['kappa_ho'] = .06
        r['1']['kappa_train'] = .06
        self.assertTrue(S.evaluate_criteria(r, kernel=True)[0]['e'])

    def test_fixed_order_not_largest_gain(self):
        r = {name: dict(status='read', criteria={k: True for k in 'abcdef'}, gain=100 - i)
             for i, name in enumerate(reversed(S.ORDER))}
        self.assertEqual(S.decide(r), 'SbFM')
        r['SbFM']['criteria']['f'] = False
        self.assertEqual(S.decide(r), 'GX')
        for v in r.values():
            v['criteria']['a'] = False
        self.assertEqual(S.decide(r), 'Sb')

    def test_within_D_coverage_and_component_draws(self):
        rows = [dict(id=str(i), label=str(i % 2), component=str(i // 2), D=str(np.exp(i / 200))) for i in range(400)]
        con = S.Contrast(rows, stratified=True, n_boot=20)
        x = np.array([int(r['label']) for r in rows], float)
        a, coverage = S.within_d(x, con.y, con.d)
        self.assertEqual(a, 1.)
        self.assertEqual(coverage, 1.)
        other = S.Contrast(rows, stratified=True, n_boot=20)
        for a, b in zip(con.draws, other.draws):
            np.testing.assert_array_equal(a, b)
            # Each person component contributes both its class rows together.
            self.assertEqual(sum(con.y[a]), len(a) / 2)
        self.assertEqual(S.ci(con.values(x)[1]), [1., 1.])

    def test_unpaired_seed_by_component_bootstrap(self):
        a = np.full((5, 40), .8); b = np.full((5, 40), .4)
        np.testing.assert_allclose(S.unpaired_seed_component_interval(a, b), [.4, .4])
        a[:, :] = np.arange(5)[:, None] / 5
        lo, hi = S.unpaired_seed_component_interval(a, b)
        self.assertLess(lo, hi)

    def test_atomic_once_journal_refuses_replay(self):
        with tempfile.TemporaryDirectory() as t:
            p = pathlib.Path(t) / 'once'
            S.claim_once(p, {'synthetic': True})
            self.assertTrue((p / 'INTENT.json').exists())
            with self.assertRaises(S.Refusal):
                S.claim_once(p, {'synthetic': True})


class AdmissionTests(unittest.TestCase):
    def rewrite(self, root, admission, path):
        path.write_text(json.dumps(admission, indent=2))
        (root / 'review.md').write_text('NEXT_ADMISSION_GO ' + S.digest(path) + '\n')
        files = [root / S.RULE, root / 'support.json', root / 'receipts.json', root / 'excluded.md', path, root / 'review.md', CODE]
        (root / 'pins.sha256').write_text(''.join(S.digest(p) + '  ' + str(p) + '\n' for p in files))

    def fixture(self, root):
        (root / pathlib.Path(S.RULE).parent).mkdir(parents=True)
        (root / S.RULE).write_text('**Status: APPROVED.**\n')
        for n in ('support.json', 'receipts.json'):
            (root / n).write_text(json.dumps({'schema': 'next-support-v1'} if n.startswith('support') else {}))
        (root / 'excluded.md').write_text('Synthetic authoritative test disposition only.\n')
        a = {'schema': 'next-admission-v1', 'stage': 'selection', 'approved': True, 'batch_closed': True,
             'numpy_version': np.__version__, 'pinfiles': ['pins.sha256'], 'support': 'support.json',
             'review': 'review.md', 'receipt_manifest': 'receipts.json', 'input_files': {}, 'transfer_files': {},
             'rule_sha256': S.digest(root / S.RULE), 'networks': {}, 'arms': {}}
        for name in S.ORDER:
            a['arms'][name] = {'status': 'not_read', 'reason': 'missing_seeds', 'evidence': 'excluded.md'}
        seeds = list(range(408, 413))
        a['arms']['SbM'] = {'status': 'read', 'pre_binding_scientific_open': False, 'eligibility_review': 'excluded.md',
                            'seeds': seeds, **{role: {str(s): None for s in seeds}
                                              for role in ('candidate', 'comparator', 'control', 'yardstick')}}
        path = root / 'admission.json'
        path.write_text(json.dumps(a, indent=2))
        (root / 'review.md').write_text('Synthetic review\nNEXT_ADMISSION_GO ' + S.digest(path) + '\n')
        files = [root / S.RULE, root / 'support.json', root / 'receipts.json', root / 'excluded.md',
                 path, root / 'review.md', CODE]
        (root / 'pins.sha256').write_text(''.join(S.digest(p) + '  ' + str(p) + '\n' for p in files))
        return a, path

    def fake_git(self, root, *args, binary=False):
        # Only synthetic repository control-plane state, never a production bypass.
        if args[0] == 'show':
            return (root / args[1].split(':', 1)[1]).read_bytes()
        return b'' if binary else ''

    def test_pin_tamper_refuses_before_candidate_loader(self):
        with tempfile.TemporaryDirectory() as t:
            root = pathlib.Path(t); a, path = self.fixture(root)
            with patch.object(S, 'git', side_effect=self.fake_git), patch.object(S, 'load_rz_network') as loader:
                S.preflight(root, path)
                (root / 'support.json').write_text('{}')
                with self.assertRaisesRegex(S.Refusal, 'pin mismatch'):
                    S.preflight(root, path)
                loader.assert_not_called()

    def test_unsupported_eligible_arm_is_global_blocker(self):
        with tempfile.TemporaryDirectory() as t:
            root = pathlib.Path(t); a, path = self.fixture(root)
            a['arms']['GX'] = {'status': 'read'}
            path.write_text(json.dumps(a, indent=2))
            (root / 'review.md').write_text('NEXT_ADMISSION_GO ' + S.digest(path) + '\n')
            files = [root / S.RULE, root / 'support.json', root / 'receipts.json', root / 'excluded.md', path, root / 'review.md', CODE]
            (root / 'pins.sha256').write_text(''.join(S.digest(p) + '  ' + str(p) + '\n' for p in files))
            with patch.object(S, 'git', side_effect=self.fake_git), patch.object(S, 'load_rz_network') as loader:
                with self.assertRaisesRegex(S.Refusal, 'adapter not yet validated'):
                    S.preflight(root, path)
                loader.assert_not_called()

    def test_software_blocker_is_not_scientific_exclusion(self):
        with tempfile.TemporaryDirectory() as t:
            root = pathlib.Path(t); a, path = self.fixture(root)
            a['arms']['SbFM']['reason'] = 'adapter_unimplemented'
            path.write_text(json.dumps(a, indent=2))
            (root / 'review.md').write_text('NEXT_ADMISSION_GO ' + S.digest(path) + '\n')
            files = [root / S.RULE, root / 'support.json', root / 'receipts.json', root / 'excluded.md', path, root / 'review.md', CODE]
            (root / 'pins.sha256').write_text(''.join(S.digest(p) + '  ' + str(p) + '\n' for p in files))
            with patch.object(S, 'git', side_effect=self.fake_git):
                with self.assertRaisesRegex(S.Refusal, 'implementation limitation'):
                    S.preflight(root, path)

    def test_wrong_arm_seed_control_and_yardstick_source_refuse(self):
        examples = [('candidate', 'SbMR', 408, 'rz1_fit'),
                    ('candidate', 'SbM', 409, 'rz1_fit'),
                    ('comparator', 'SbM', 408, 'rz1_fit'),
                    ('control', 'Ac', 408, 'rz1_fit'),
                    ('yardstick', 'Sb', 408, 'rz1_refit')]
        for role, arm, seed, fmt in examples:
            with tempfile.TemporaryDirectory() as t:
                root = pathlib.Path(t); admission, path = self.fixture(root)
                admission['arms']['SbM'][role]['408'] = 'wrong-network'
                admission['networks']['wrong-network'] = dict(arm=arm, seed=seed, format=fmt,
                    source_network=dict(name='AB1_Sb_s408.tar', sha256='0' * 64))
                self.rewrite(root, admission, path)
                with patch.object(S, 'git', side_effect=self.fake_git), patch.object(S, 'load_rz_network') as loader:
                    with self.assertRaises(S.Refusal):
                        S.preflight(root, path)
                    loader.assert_not_called()


class NativeArchiveTests(unittest.TestCase):
    def fixture(self, folder, *, finite=True, arm_guard=True, meds_hash=None, meds_spec=None, reverse_eval=False):
        primary = 'fixed:pil_bilinear'; specs = ['test_spec_' + str(i) for i in range(13)]
        support = dict(eval_sha256='e' * 64, tt1_sha256='f' * 64, cross_sha256='c' * 64,
                       meds_score_manifest_sha256='d' * 64,
                       train={'Sb0': {'sha256': 'a' * 64, 'n_items': 2}},
                       kernel={'train9': specs[:9], 'held4': specs[9:]})
        support['_expected_ids'] = dict(x=['n', 'p'], tt1=['tt0'], meds=['private_mock_row'], cross=['cross0'])
        support['_expected_train'] = {'Sb0': [dict(path='train/n.png', label='0', kind='native'),
                                               dict(path='train/p.png', label='1', kind='morph')]}
        prefix = 'RZ1_SbM_s408'
        meta = dict(steps=6250, res=224, bs=256, accum=1, seed=408, n_items=2)
        taskinfo = ' '.join(k + ' ' + v for k, v in S.PINS.items())
        taskinfo += ' spec mix primary fixed:pil_bilinear res 224 bs 256 accum 1 steps 6250 limit 0 skip_tt1 0 '
        members = {
            'gpu.txt': b'NVIDIA H100', 'task_info.txt': taskinfo.encode(),
            'meta.json': json.dumps(meta).encode(),
            'rz1_transform.json': json.dumps({'spec': 'mix', 'res': 224}).encode(),
            'guard.log': b'RZ1 GUARD pre ok\nRZ1 GUARD post ok\n',
            'task.env': ('ARM=SbM\nSEED=' + ('408' if arm_guard else '409') + '\n').encode(),
            'train.log': b'step 6250 loss 0.25\n',
        }
        def npz(**kw):
            b = io.BytesIO(); np.savez(b, **kw); return b.getvalue()
        members.update({
            'scores_eval.npz': npz(id=np.array(['p', 'n'] if reverse_eval else ['n', 'p']), logit=np.array([-1., 1. if finite else np.nan]),
                                   manifest_sha256=np.array(support['eval_sha256']), spec=np.array(primary)),
            'scores_train.npz': npz(path=np.array(['train/n.png', 'train/p.png']), kind=np.array(['native', 'morph']),
                                    label=np.array([0, 1]), logit=np.array([-1., 1.]),
                                    manifest_sha256=np.array('a' * 64), spec=np.array(primary)),
            'scores_tt1.npz': npz(id=np.array(['tt0']), logit=np.array([-1.]), manifest_sha256=np.array('f' * 64), spec=np.array(primary)),
            'scores_meds.npz': npz(id=np.array(['private_mock_row']), logit=np.array([-1.]),
                                   manifest_sha256=np.array(meds_hash or 'd' * 64), spec=np.array(meds_spec or primary)),
            'scores_cross.npz': npz(id=np.array(['cross0']), logit=np.zeros((13, 1)),
                                    specs=np.array(specs), manifest_sha256=np.array('c' * 64)),
        })
        path = folder / 'synthetic.tar'
        with tarfile.open(path, 'w') as tf:
            for name, data in members.items():
                member = tarfile.TarInfo(prefix + '/' + name); member.size = len(data)
                tf.addfile(member, io.BytesIO(data))
        record = dict(archive=str(path), sha256=S.digest(path), prefix=prefix, seed=408, arm='SbM', format='rz1_fit')
        return record, support

    def test_native_fit_schema_and_provenance(self):
        with tempfile.TemporaryDirectory() as t:
            record, support = self.fixture(pathlib.Path(t))
            data = S.load_rz_network(record, support)
            self.assertEqual(data['x'], {'n': -1., 'p': 1.})
            self.assertEqual(len(data['cross']), 13)
            self.assertTrue(data['registration_guards'])

    def test_native_nonfinite_and_wrong_seed_refused(self):
        for kwargs in ({'finite': False}, {'arm_guard': False}, {'meds_hash': 'bad'},
                       {'meds_spec': 'wrong_transform'}, {'reverse_eval': True}):
            with tempfile.TemporaryDirectory() as t:
                record, support = self.fixture(pathlib.Path(t), **kwargs)
                with self.assertRaises(S.SeedUnavailable):
                    S.load_rz_network(record, support)

    def test_native_refit_gate_schema_and_source(self):
        for bad_gate in (False, True):
            with tempfile.TemporaryDirectory() as t:
                folder = pathlib.Path(t); record, support = self.fixture(folder)
                with tarfile.open(record['archive']) as tf:
                    members = {pathlib.PurePosixPath(m.name).name: tf.extractfile(m).read() for m in tf.getmembers()}
                source = dict(name='AB1_Sb_s408.tar', sha256=S.AB1_SB_SOURCE_PINS[408])
                gate = dict(verdict='passed', n=21277, n_differ=0, max_abs=0., own_rule_agree=1.,
                            tar=source['name'], tar_sha256=('0' * 64 if bad_gate else source['sha256']), device='NVIDIA H100')
                ti = 'source_tar ' + source['name'] + ' ' + source['sha256'] + ' '
                ti += ' '.join(k + ' ' + v for k, v in S.PINS.items())
                ti += ' rz1_rescore 02628562fb495cfedabd0e409db1b397fd0fb2d90ff4886ce4f865764b94bfd6 train_manifest train_Sb.csv limit 0 '
                members['task_info.txt'] = ti.encode(); members['gate.json'] = json.dumps(gate).encode()
                prefix = 'RZ1R_Sb_s408'
                path = folder / 'synthetic-refit.tar'
                with tarfile.open(path, 'w') as tf:
                    for name, data in members.items():
                        m = tarfile.TarInfo(prefix + '/' + name); m.size = len(data); tf.addfile(m, io.BytesIO(data))
                record.update(archive=str(path), sha256=S.digest(path), prefix=prefix, arm='Sb',
                              format='rz1_refit', source_network=source)
                if bad_gate:
                    with self.assertRaises(S.SeedUnavailable):
                        S.load_rz_network(record, support)
                else:
                    self.assertTrue(S.load_rz_network(record, support)['registration_guards'])

    def test_native_digest_tamper_is_global_refusal(self):
        with tempfile.TemporaryDirectory() as t:
            record, support = self.fixture(pathlib.Path(t))
            with pathlib.Path(record['archive']).open('ab') as f:
                f.write(b'tamper')
            with self.assertRaises(S.Refusal):
                S.load_rz_network(record, support)


if __name__ == '__main__':
    unittest.main(verbosity=2)
