"""Generated scalar fixtures only: no ML import, checkpoint or source photos."""
import importlib.util
from pathlib import Path
import unittest

spec = importlib.util.spec_from_file_location('vis1', Path(__file__).with_name('score_vis1.py'))
M = importlib.util.module_from_spec(spec); spec.loader.exec_module(M)


class Scores(unittest.TestCase):
    def rows(self):
        ids = ['reference_00010','00042_native','00042_history','00056_native','00056_history']
        return [dict(id=i, logit=float(n), repeat_logit=float(n)) for n,i in enumerate(ids)]

    def test_orientation_and_no_decision(self):
        p=M.summarize(self.rows()); self.assertEqual([x['delta_logit'] for x in p],[1.,1.])
        self.assertTrue(all(x['threshold'] is None and x['decision_flip'] is None for x in p))

    def test_duplicate(self):
        r=self.rows();r[-1]['id']=r[0]['id']
        with self.assertRaises(ValueError):M.summarize(r)

    def test_missing(self):
        with self.assertRaises(ValueError):M.summarize(self.rows()[:-1])

    def test_nonfinite(self):
        for field in ['logit','repeat_logit']:
            r=self.rows();r[2][field]=float('nan')
            with self.assertRaises(ValueError):M.summarize(r)

    def test_repeat(self):
        r=self.rows();r[1]['repeat_logit']+=.01
        with self.assertRaises(ValueError):M.summarize(r)

    def test_no_effect(self):
        r=self.rows()
        for x in r:x.update(logit=0.,repeat_logit=0.)
        self.assertEqual([x['delta_logit'] for x in M.summarize(r)],[0.,0.])

    def test_negative_effect_kept(self):
        r=self.rows();r[2].update(logit=-100.,repeat_logit=-100.)
        self.assertLess(M.summarize(r)[0]['delta_logit'],0)


if __name__=='__main__':unittest.main()
