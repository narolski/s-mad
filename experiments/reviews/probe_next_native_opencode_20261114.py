"""Independent synthetic acceptance probes for corrected review finding F1."""
import importlib.util
import pathlib
import tempfile
import unittest
import numpy as np

ROOT = pathlib.Path(__file__).resolve().parents[2]
spec = importlib.util.spec_from_file_location('fixture', ROOT / 'src/NEXT/tests/mock_native_integration.py')
I = importlib.util.module_from_spec(spec)
spec.loader.exec_module(I)
S = I.S


class IndependentReview(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.tmp = tempfile.TemporaryDirectory(prefix='next-independent-', dir='/tmp/opencode')
        cls.addClassCleanup(cls.tmp.cleanup)
        cls.f = I.Fixture(pathlib.Path(cls.tmp.name))

    def test_four_read_candidates_admissible_under_v3(self):
        f = self.f
        f.admit(['DINOv3'])
        f.a['arms']['DINOv3']['candidate']['403'] = None
        f.repin()
        with f.patches():
            S.preflight(f.root, f.path)

    def test_post_admission_failure_retains_four_seed_result(self):
        f = self.f
        f.admit(['DINOv3'])
        with f.patches():
            a, support, pins = S.preflight(f.root, f.path)
            S.validate_support(f.root, a, support, pins)
            prepared = S.prepare_contrasts(f.root, a, n_boot=12)
            # Simulate failure without touching any production file or journal.
            a['arms']['DINOv3']['candidate']['403'] = None
            result = S.execute(f.root, a, support, n_boot=12, prepared=prepared)
        arm = result['arms']['DINOv3']
        self.assertEqual(arm['read_seeds'], 4)
        self.assertEqual(arm['denominator'], 5)
        self.assertEqual(result['choice'], 'DINOv3')
        self.assertEqual(set(arm['seed_mean_intervals']), set(f.rows))

    def test_independent_seed_draws_shared_component_oracle(self):
        # Nonconstant seed effects detect pairing; large shared row effects
        # cancel only when both networks use the same component replicate.
        row = np.linspace(-10, 10, 2000)
        b = np.array([0., .1, .3, .6, .9])[:, None] + row
        for count in (4, 5):
            a = np.array([.2, .4, .5, .8, 1.])[:count, None] + row
            rng = np.random.default_rng(np.random.SeedSequence(20261115).spawn(1)[0])
            draws = []
            for j in range(len(row)):
                ca = rng.integers(count, size=count)
                cb = rng.integers(5, size=5)
                draws.append(a[ca, j].mean() - b[cb, j].mean())
            expected = np.percentile(draws, [2.5, 97.5])
            np.testing.assert_allclose(S.unpaired_seed_component_interval(a, b), expected)
            self.assertGreater(expected[1] - expected[0], .1)


if __name__ == '__main__':
    unittest.main(verbosity=2)
