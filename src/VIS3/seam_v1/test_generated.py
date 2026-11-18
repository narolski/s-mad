"""Generated non-face fixtures only; no real photo, model, score or export."""
import importlib.util
from pathlib import Path
import unittest
import numpy as np
import random
import sys

spec=importlib.util.spec_from_file_location('vis3',Path(__file__).with_name('construction.py'))
M=importlib.util.module_from_spec(spec);spec.loader.exec_module(M)
SOURCE='/mnt/t7/smad_next/PN1/fs_tree/pn1/code/morphmamba/data/selfblend.py'


class Generated(unittest.TestCase):
    def setUp(self):self.ns=M.load_registered(SOURCE)

    def test_unmodified_function_and_capture(self):
        a=np.full((512,512,3),100,np.uint8);out,c=M.capture_registered(a,self.ns)
        self.assertTrue(np.array_equal(out,M.compose(a,c['source'],c['alpha'])))
        self.assertTrue((a==100).all());self.assertIsNone(sys.getprofile())

    def test_same_mask_across_generated_sources(self):
        _,a=M.capture_registered(np.full((512,512,3),80,np.uint8),self.ns)
        _,b=M.capture_registered(np.full((512,512,3),170,np.uint8),self.ns)
        self.assertTrue(np.array_equal(a['alpha'],b['alpha']))
        self.assertEqual(a['sigma'],b['sigma'])

    def test_sham_exact_and_cross_arithmetic(self):
        base=np.full((512,512,3),80,np.uint8);donor=np.full((512,512,3),160,np.uint8)
        _,c=M.capture_registered(base,self.ns)
        self.assertTrue(np.array_equal(base.copy(),base))
        # Registered float32 mixing is NOT an exact no-op: retain literal-copy sham.
        rounded=M.compose(base,base,c['alpha'])
        self.assertLessEqual(int(np.abs(rounded.astype(int)-base.astype(int)).max()),1)
        cross=M.compose(base,donor,c['alpha']);self.assertTrue((cross>=80).all() and (cross<=120).all())

    def test_equal_area_and_disjoint(self):
        _,c=M.capture_registered(np.full((512,512,3),100,np.uint8),self.ns);p=M.region_plan(c['alpha'])
        self.assertEqual(len(p['selected_seam']),len(p['selected_surround']));self.assertGreaterEqual(p['K'],3)
        self.assertFalse(set(p['selected_seam'])&set(p['selected_surround']));self.assertEqual(p['area_per_patch'],4096)

    def test_all_fixed_constructions(self):
        base=np.full((512,512,3),80,np.uint8);donor=np.full((512,512,3),170,np.uint8)
        out,alpha,plan=M.construct_pair(base,donor,self.ns)
        self.assertEqual(list(out),['42_samephoto','42_crossphoto','56_samephoto','56_crossphoto'])
        self.assertTrue(all(x.shape==(512,512,3) and x.dtype==np.uint8 for x in out.values()))
        expected,_=M.capture_registered(base,self.ns)
        self.assertTrue(np.array_equal(expected,out['42_samephoto']))
        self.assertTrue((base==80).all() and (donor==170).all())

    def test_rng_restored(self):
        random.seed(1234);expected=random.getstate();np.random.seed(1234);before=np.random.get_state()
        M.capture_registered(np.zeros((512,512,3),np.uint8),self.ns)
        self.assertEqual(random.getstate(),expected);after=np.random.get_state()
        self.assertEqual(before[0],after[0]);self.assertTrue(np.array_equal(before[1],after[1]));self.assertEqual(before[2:],after[2:])


if __name__=='__main__':unittest.main()
