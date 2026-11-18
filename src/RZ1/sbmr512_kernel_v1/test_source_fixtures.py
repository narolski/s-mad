import importlib.util,pathlib,unittest,numpy as np
from PIL import Image
import design as D
R=pathlib.Path(__file__).resolve().parents[2]
class Fixtures(unittest.TestCase):
 def test_order(self):
  self.assertEqual(len(D.SPECS),14);self.assertEqual(len(set(D.SPECS)),14)
  self.assertEqual(D.SPECS[0],"fixed:pil_bilinear")
  self.assertEqual(D.SPECS[1:10],D.TRAIN);self.assertEqual(D.SPECS[10:],D.HELD)
 def test_failed_denominator(self):
  x={s:dict(kappa_train512=.01,kappa_ho512=.02) for s in D.SEEDS[:3]}
  q=D.operational_summary(x);self.assertEqual(q["denominator"],5);self.assertFalse(q["train_condition"])
  x[D.SEEDS[3]]=dict(kappa_train512=.05,kappa_ho512=.05)
  self.assertTrue(D.operational_summary(x)["heldout_condition"])
 def test_no_rng_and_nonidentity(self):
  sp=importlib.util.spec_from_file_location("fixture_rz1_kernels",R/"RZ1/rz1_kernels.py")
  k=importlib.util.module_from_spec(sp);sp.loader.exec_module(k)
  self.assertEqual(k.NAMES,D.NAMES)
  y,x=np.indices((512,512));a=np.repeat((((x+y)%2)*255).astype(np.uint8)[:,:,None],3,axis=2);im=Image.fromarray(a)
  self.assertIs(k.Transform(D.REFERENCE,512)(im),im)
  original=k.Transform.rng
  k.Transform.rng=lambda self:(_ for _ in ()).throw(AssertionError("RNG forbidden"))
  try:
   for spec in D.SPECS[1:]:
    with self.subTest(spec=spec):
     z=np.asarray(k.Transform(spec,512)(im));self.assertEqual(z.shape,(512,512,3));self.assertFalse(np.array_equal(z,a))
     self.assertTrue(np.array_equal(z,np.asarray(k.Transform(spec,512)(im))))
  finally:k.Transform.rng=original
if __name__=="__main__":unittest.main()
