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
class ContextFixtures(unittest.TestCase):
 def test_counts_and_sequence(self):
  self.assertEqual(D.work_counts(),dict(per_model_samples=1177806,total_samples=5889030,per_model_calls=18424,total_calls=92120))
  seq=list(D.full_context_schedule());self.assertEqual(seq[0][1:],("ab1x_eval",0,64,"native"));self.assertEqual(seq[1][1:],("ab1x_eval",0,64,"horizontal_flip"))
  for spec in D.SPECS:
   rows=[r for r in seq if r[0]==spec]
   self.assertEqual(len(rows),1316)
   self.assertEqual(rows[777][1:],("ab1x_eval",24832,24859,"horizontal_flip"))
   self.assertEqual(rows[778][1:],("tt1",0,64,"native"))
   self.assertEqual(rows[-1][1:],("tt1",34368,34411,"native"))
   self.assertFalse(any(r[1]=="tt1" and r[4]!="native" for r in rows))
 def test_invalid_kappa(self):
  for bad in [float('nan'),float('inf'),float('-inf'),-.01,True,False,None]:
   with self.subTest(bad=repr(bad)):
    x={s:dict(kappa_train512=bad,kappa_ho512=bad) for s in D.SEEDS}
    q=D.operational_summary(x);self.assertEqual(q['train_pass_seeds'],0);self.assertEqual(q['heldout_pass_seeds'],0)
 def test_missing_quantity(self):
  q=D.operational_summary({s:dict(kappa_train512=.01) for s in D.SEEDS})
  self.assertTrue(q['train_condition']);self.assertFalse(q['heldout_condition']);self.assertEqual(q['denominator'],5)
 def test_opposite_failed_seeds(self):
  x={s:dict(kappa_train512=.01,kappa_ho512=.01) for s in D.SEEDS}
  x[408]['kappa_train512']=.06;x[412]['kappa_ho512']=.06
  q=D.operational_summary(x);self.assertTrue(q['train_condition'] and q['heldout_condition'])
  self.assertEqual(q['train_pass_seeds'],4);self.assertEqual(q['heldout_pass_seeds'],4)
if __name__=="__main__":unittest.main()
