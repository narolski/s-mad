"""Guard-only tests. All archive/claim/output bytes are synthetic temporary fixtures."""
import ast
import hashlib
import importlib.util
import io
import json
import pathlib
import tarfile
import tempfile
import unittest
from unittest.mock import patch
from concurrent.futures import ThreadPoolExecutor

import numpy as np

SOURCE = pathlib.Path(__file__).resolve().parents[1] / 'ab1_pm3_read.py'
spec = importlib.util.spec_from_file_location('pm3', SOURCE)
M = importlib.util.module_from_spec(spec)
spec.loader.exec_module(M)


class Admission(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = pathlib.Path(self.tmp.name)
        self.out = self.root / 'out.json'
        self.claims = self.root / 'claims'
        self.eval_saved = M.A.EVAL, M.A.EVAL_SHA
        M.A.EVAL = self.root / 'eval.csv'
        M.A.EVAL.write_text('id\nsynthetic\nsecond\n')
        M.A.EVAL_SHA = M.A.sha(M.A.EVAL)

    def tearDown(self):
        M.A.EVAL, M.A.EVAL_SHA = self.eval_saved
        self.tmp.cleanup()

    def claim(self, **kw):
        return M._claim_read('C', kw.get('out', self.out), kw.get('mock', False),
                             self.root / 'synthetic-C', self.root / 'synthetic-AB1', self.claims)

    def test_claim_records_exact_sources(self):
        p = self.claim()
        value = json.loads(p.read_text())
        self.assertEqual(value['status'], 'claimed_before_score_access')
        self.assertEqual(value['reader_sha256'], hashlib.sha256(SOURCE.read_bytes()).hexdigest())
        self.assertEqual(value['c_overlay'], M.C_OVERLAY)

    def test_retry_new_output_still_refused(self):
        self.claim()
        with self.assertRaises(FileExistsError):
            self.claim(out=self.root / 'another.json')

    def test_existing_output_prevents_claim(self):
        self.out.write_text('existing')
        with self.assertRaises(FileExistsError):
            self.claim()
        self.assertFalse(self.claims.exists())
        self.assertEqual(self.out.read_text(), 'existing')

    def test_dangling_output_symlink_refused(self):
        self.out.symlink_to(self.root / 'absent')
        with self.assertRaises(FileExistsError):
            self.claim()

    def test_mock_does_not_consume_production(self):
        self.assertIsNone(self.claim(mock=True))
        self.assertFalse(self.claims.exists())
        self.claim()

    def test_output_cannot_be_overwritten(self):
        M._exclusive_json(self.out, {'first': 1})
        with self.assertRaises(FileExistsError):
            M._exclusive_json(self.out, {'second': 2})
        self.assertEqual(json.loads(self.out.read_text()), {'first': 1})

    def test_two_claimants_only_one_wins(self):
        def attempt(_):
            try:
                self.claim()
                return True
            except FileExistsError:
                return False
        with ThreadPoolExecutor(max_workers=2) as pool:
            self.assertEqual(sum(pool.map(attempt, range(2))), 1)

    def test_main_claim_precedes_archive_loading(self):
        tree = ast.parse(SOURCE.read_text())
        main = next(x for x in tree.body if isinstance(x, ast.FunctionDef) and x.name == 'main')
        calls = [x for x in ast.walk(main) if isinstance(x, ast.Call)]
        claim_line = next(x.lineno for x in calls if isinstance(x.func, ast.Name) and x.func.id == '_claim_read')
        loaders = [x.lineno for x in calls if (isinstance(x.func, ast.Attribute) and x.func.attr == 'load')
                   or (isinstance(x.func, ast.Name) and x.func.id in ('load_fs1', '_load_ab1_checked'))]
        self.assertTrue(loaders)
        self.assertTrue(all(line > claim_line for line in loaders))
        self.assertNotIn('--once-root', SOURCE.read_text())

    def test_overlay_matches_registered_launcher(self):
        launcher = SOURCE.with_name('run_c.sh').read_text()
        self.assertIn('OVERLAY_SHA=' + M.C_OVERLAY, launcher)
        self.assertEqual(M.C_OVERLAY, 'bf276e548c5dc5a3c8d590d0500754c1d49ec87ad2e7b30237f05db94ffcafa7')

    def fixture(self, arm, overlay, *, seed=408, ids=None, logits=None, extra_env=""):
        ids = ["synthetic", "second"] if ids is None else ids
        logits = [0.125, 0.25] if logits is None else logits
        directory = self.root / arm
        directory.mkdir(exist_ok=True)
        man = directory / f'train_{arm}.csv'
        man.write_text('id,kind\nsynthetic,control\n')
        task = f'AB1C_{arm}_s408'
        path = directory / f'{task}.tar'
        eval_io, train_io = io.BytesIO(), io.BytesIO()
        np.savez(eval_io, id=ids, logit=logits, manifest_sha256=M.A.EVAL_SHA)
        np.savez(train_io, kind=['control'], logit=[0.125], manifest_sha256=M.A.sha(man))
        payloads = {
            'scores_eval.npz': eval_io.getvalue(), 'scores_train.npz': train_io.getvalue(),
            'gpu.txt': b'NVIDIA H100', 'task_info.txt':
                f'pack_sha256 {M.A.PACK} overlay_sha256 {overlay} steps 6250 limit 0'.encode(),
            'train.log': b'loss=0.5', 'meta.json': b'{"n_items": 1, "steps": 6250}',
            'task.env': f'TASK={task}\nARM={arm}\nSEED={seed}\n{extra_env}'.encode()}
        with tarfile.open(path, 'w') as tar:
            for name, value in payloads.items():
                info = tarfile.TarInfo(task + '/' + name)
                info.size = len(value)
                tar.addfile(info, io.BytesIO(value))
        pathlib.Path(str(path) + '.sha256').write_text(M.A.sha(path) + '  ' + path.name + '\n')
        return path, directory

    def test_all_batch_c_arms_pass_real_loader_on_synthetic_archives(self):
        saved = M.A.OVERLAY['AB1'], M.A.MANDIR
        try:
            M.A.OVERLAY['AB1'] = M.C_OVERLAY
            for arm in ('SpV', 'BN', 'BV'):
                path, directory = self.fixture(arm, M.C_OVERLAY)
                M.A.MANDIR = directory
                scores, _, why = M._load_ab1_checked(path, arm, 408)
                self.assertEqual(scores, {'synthetic': 0.125, 'second': 0.25}, why)
        finally:
            M.A.OVERLAY['AB1'], M.A.MANDIR = saved

    def test_old_overlay_rejected_on_synthetic_archive(self):
        saved = M.A.OVERLAY['AB1'], M.A.MANDIR
        try:
            path, directory = self.fixture('BV', '62712bb9d5066443d5737c84da852d055ab248930d5f38fc8b77ba0074a34c68')
            M.A.OVERLAY['AB1'], M.A.MANDIR = M.C_OVERLAY, directory
            scores, _, why = M._load_ab1_checked(path, 'BV', 408)
            self.assertIsNone(scores)
            self.assertTrue(why.startswith('overlay off:'))
        finally:
            M.A.OVERLAY['AB1'], M.A.MANDIR = saved

    def rejected(self, expected, **kwargs):
        path, _ = self.fixture('BV', M.C_OVERLAY, **kwargs)
        scores, _, why = M._load_ab1_checked(path, 'BV', 408)
        self.assertIsNone(scores)
        self.assertEqual(why, expected)

    def test_wrong_seed_refused(self):
        self.rejected('task.env exact task/arm/seed mismatch', seed=409)

    def test_duplicate_seed_assignment_refused(self):
        self.rejected('task.env duplicate SEED', extra_env='SEED=408\n')

    def test_duplicate_eval_ids_refused(self):
        self.rejected('duplicate eval score IDs', ids=['synthetic', 'synthetic'])

    def test_truncated_logits_refused(self):
        self.rejected('eval id/logit shape or length mismatch', logits=[0.125])

    def test_reordered_ids_refused(self):
        self.rejected('eval score IDs/order differ from pinned manifest', ids=['second', 'synthetic'])

    def test_foreign_id_refused(self):
        self.rejected('eval score IDs/order differ from pinned manifest', ids=['synthetic', 'foreign'])

    def test_nonfinite_logits_refused(self):
        self.rejected('non-finite eval logits', logits=[0.125, float('nan')])


class WithinDContext(unittest.TestCase):
    """Committed bytes simulated at the git boundary; all floor values synthetic."""

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = pathlib.Path(self.tmp.name)
        self.directory = self.root / M.CONTEXT_DIR
        self.directory.mkdir(parents=True)
        self.saved = {}
        pins = []
        for i, c in enumerate(M.WITHIN_D_CONTRASTS):
            name = c + '_withinD.json'
            data = json.dumps({'synthetic_fixture': True, 'fixture_value': i}).encode()
            self.put(name, data)
            pins.append(hashlib.sha256(data).hexdigest() + '  ' + name)
        self.put('pins_stage6.sha256', ('\n'.join(pins) + '\n').encode())

    def tearDown(self):
        self.tmp.cleanup()

    def put(self, name, data):
        (self.directory / name).write_bytes(data)
        self.saved[(M.CONTEXT_DIR / name).as_posix()] = data

    def git_show(self, args, **kwargs):
        self.assertEqual(args[:4], ['git', '-C', str(self.root), 'show'])
        self.assertTrue(kwargs['check'])
        relative = args[4].removeprefix('HEAD:')
        return M.subprocess.CompletedProcess(args, 0, stdout=self.saved[relative])

    def load(self):
        with patch.object(M, 'CONTEXT_ROOT', self.root), patch.object(M.subprocess, 'run', side_effect=self.git_show):
            return M._within_d_context()

    def test_both_contexts_preserved_labeled_and_pinned(self):
        result = self.load()
        self.assertEqual(tuple(result), M.WITHIN_D_CONTRASTS)
        for i, c in enumerate(M.WITHIN_D_CONTRASTS):
            entry = result[c]
            self.assertEqual(entry['context'], {'synthetic_fixture': True, 'fixture_value': i})
            self.assertIn('Different row sets', entry['scope'])
            self.assertIn('context only', entry['scope'])
            self.assertIn('not used in any decision', entry['scope'])
            self.assertFalse(entry['synthetic'])
            self.assertEqual(entry['source']['sha256'], M.A.sha(self.directory / (c + '_withinD.json')))
            self.assertEqual(entry['source']['pinfile_sha256'], M.A.sha(self.directory / 'pins_stage6.sha256'))

    def test_committed_wrong_pin_refused(self):
        self.put('pins_stage6.sha256', b'0' * 64 + b'  ri_R4_vs_R3_withinD.json\n')
        with self.assertRaisesRegex(ValueError, 'missing committed stage-6 pin'):
            self.load()

    def test_dirty_context_refused(self):
        name = M.WITHIN_D_CONTRASTS[0] + '_withinD.json'
        (self.directory / name).write_text('{"changed": true}')
        with self.assertRaisesRegex(ValueError, 'uncommitted within-D context input'):
            self.load()

    def test_dirty_pinfile_refused(self):
        (self.directory / 'pins_stage6.sha256').write_text('changed\n')
        with self.assertRaisesRegex(ValueError, 'uncommitted within-D context input'):
            self.load()

    def test_mock_never_reads_context_or_git(self):
        with patch.object(pathlib.Path, 'read_bytes', side_effect=AssertionError('file read')), \
                patch.object(M.subprocess, 'run', side_effect=AssertionError('git called')):
            result = M._within_d_context(mock=True)
        self.assertEqual(tuple(result), M.WITHIN_D_CONTRASTS)
        self.assertTrue(all(x['synthetic'] and x['source'] is None for x in result.values()))

    def test_context_in_output_before_claim_only_for_batch_c(self):
        tree = ast.parse(SOURCE.read_text())
        main = next(x for x in tree.body if isinstance(x, ast.FunctionDef) and x.name == 'main')
        branch = next(x for x in main.body if isinstance(x, ast.If)
                      and any(isinstance(n, ast.Call) and isinstance(n.func, ast.Name)
                              and n.func.id == '_within_d_context' for n in ast.walk(x)))
        self.assertEqual(ast.unparse(branch.test), "a.pair == 'C'")
        self.assertEqual(ast.unparse(branch.body[0].targets[0]), "R['within_D_floors']")
        claim = next(n for n in ast.walk(main) if isinstance(n, ast.Call)
                     and isinstance(n.func, ast.Name) and n.func.id == '_claim_read')
        self.assertLess(branch.lineno, claim.lineno)


if __name__ == '__main__':
    unittest.main()
