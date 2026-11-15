"""Synthetic-only image/mask fixtures; no photographs, model or GPU."""
import importlib.util
from pathlib import Path
import unittest
import numpy as np

spec=importlib.util.spec_from_file_location('vis2',Path(__file__).with_name('occlusion_worker.py'))
M=importlib.util.module_from_spec(spec);spec.loader.exec_module(M)


class Geometry(unittest.TestCase):
    def test_tiling(self):
        cover=np.zeros((512,512),int)
        for y,x in M.cells():cover[y:y+64,x:x+64]+=1
        self.assertEqual(len(M.cells()),64);self.assertTrue((cover==1).all())

    def test_fill_area_and_no_source_mutation(self):
        a=np.full((512,512,3),100,np.uint8);before=a.copy()
        for fill in (0,128):
            b=M.replace(a,192,256,fill)
            self.assertTrue(np.array_equal(a,before))
            self.assertEqual(np.count_nonzero((b!=a).any(2)),4096)
            self.assertTrue((b[192:256,256:320]==fill).all())

    def test_linear_delta_signed(self):
        a=np.full((512,512,3),100,np.uint8)
        for fill in (0,128):
            b=M.replace(a,0,0,fill)
            self.assertEqual(float(b.astype(float).sum()-a.astype(float).sum()),4096*3*(fill-100))

    def test_grid_and_fill_failclosed(self):
        for y,x,fill in [(1,0,0),(0,512,0),(0,0,127)]:
            with self.assertRaises(ValueError):M.replace(np.zeros((512,512,3),np.uint8),y,x,fill)

    def test_noop(self):
        a=np.zeros((512,512,3),np.uint8);self.assertTrue(np.array_equal(M.replace(a,64,64,0),a))

    def test_dtype_and_shape(self):
        a=np.ones((512,512,3),np.uint8);b=M.replace(a,448,448,128)
        self.assertEqual(b.dtype,a.dtype);self.assertEqual(b.shape,a.shape)


if __name__=='__main__':unittest.main()
