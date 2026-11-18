import importlib.util,json,os,pathlib,tempfile,time,unittest
from unittest import mock
import verify,launch
class Gates(unittest.TestCase):
 def test_invalid_seed_precedes_file_access(self):
  for seed in [True,400,406,'401']:
   with self.assertRaises(AssertionError):verify.release(seed)
 def test_unsigned_release_refused(self):
  with tempfile.TemporaryDirectory() as t:
   j=pathlib.Path(t);(j/'s401').mkdir();(j/'s401/ROOT_RELEASE.json').write_text('{"decision":"PROPOSED"}')
   with mock.patch.object(verify,'JOURNAL',j),self.assertRaises(AssertionError):verify.release(401)
 def test_real_exclusive_claim_precedes_single_mocked_batch_submission(self):
  for code,stdout in [(0,'12345\n'),(1,''),(0,'not-job-id')]:
   with tempfile.TemporaryDirectory() as t:
    root=pathlib.Path(t);j=root/'dispatch';(j/'s401').mkdir(parents=True);(j/'s401/ROOT_RELEASE.json').write_text('{}')
    def run(cmd,**kw):
     self.assertTrue((j/'s401/CLAIM.json').is_file());self.assertIn('--time=06:00:00',cmd);self.assertIn('--export=NONE',cmd);self.assertIn('--no-requeue',cmd);self.assertNotIn('PYTHONPATH',kw['env'])
     return type('R',(),dict(returncode=code,stdout=stdout,stderr=''))()
    with mock.patch.object(verify,'ROOT',root),mock.patch.object(verify,'JOURNAL',j),mock.patch.object(verify,'release',return_value={'resource_profile':{}}),mock.patch.object(launch.subprocess,'run',side_effect=run) as call:
     self.assertEqual(launch.main(401),0 if code==0 and stdout.strip().isdigit() else 94)
     with self.assertRaises(FileExistsError):launch.main(401)
     self.assertEqual(call.call_count,1)
 def test_full_csv_recipe_and_no_scorer(self):
  s=(pathlib.Path(__file__).parent/'body.sh').read_text()
  for required in ('--num_epoch=40','--save_every=40','--log_every=50','--batch_size=256','39723','83c01705e140843afa6cb4c89765d0528ff21e2f444aee23aa50de49eaf894a3'):self.assertIn(required,s)
  self.assertNotIn('NR-2',s);self.assertNotIn('a36_madation',s);self.assertNotIn('ad5_score',s)
if __name__=='__main__':unittest.main()
