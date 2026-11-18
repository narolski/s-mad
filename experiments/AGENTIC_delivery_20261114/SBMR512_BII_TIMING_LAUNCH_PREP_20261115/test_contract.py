import copy,json,pathlib,unittest
from contract import *
class Contract(unittest.TestCase):
 def setUp(self):
  x=json.loads((pathlib.Path(__file__).parent/'REQUIREMENTS.json').read_text())
  self.c=dict(decision='GO_SBMR512_BII_TIMING_EXTENSION_V1',root_authorized=True,author='A',reviewer='OTHER',mode='timing',seed=408,worker_source_manifest_sha256=SOURCE,scientific_read='HOLD',automatic_retry=False,output=OUTPUT,profile=dict(partition='lem-gpu-interactive',gpus=1,cpus=8,memory='32G',local_scratch='8G',walltime='00:15:00'),reference_scope=dict(population='ab1x_eval',container_decode=True,selected_indices=x['selected_original_indices'],tt1_open=False),runtime_defaults=dict(historical_identity='UNKNOWN',prospective_runtime_reviewed=True),admissions={r:dict(path='/synthetic/'+r,sha256='1'*64,status='ROOT_ADOPTED') for r in ROLES},content_pins={'/synthetic/python':'2'*64,'/synthetic/release':'3'*64,'/synthetic/admission':'4'*64},worker_release='/synthetic/release',worker_admission='/synthetic/admission',worker_dir='/synthetic/worker',python='/synthetic/python',driver_dir='/synthetic/newdriver',durable_parent=OUTPUT.rsplit('/',1)[0],runtime_env={},isolated_home='/synthetic/home')
 def test_valid_fixture(self):self.assertTrue(validate(self.c))
 def test_rejections(self):
  changes=[('seed',409),('mode','full'),('scientific_read','GO'),('automatic_retry',True),('root_authorized',False),('output','/tmp/output'),('reviewer','A'),('worker_source_manifest_sha256','0'*64),('content_pins',{}),('runtime_env',{'PYTHONPATH':'/tmp'}),('reference_scope',dict(population='tt1',container_decode=True,selected_indices=list(range(13)),tt1_open=True)),('admissions',{})]
  for k,v in changes:
   with self.subTest(k=k),self.assertRaises((ValueError,KeyError)):
    c=copy.deepcopy(self.c);c[k]=v;validate(c)
 def test_missing_each_role(self):
  for role in ROLES:
   with self.subTest(role=role),self.assertRaises(ValueError):
    c=copy.deepcopy(self.c);c['admissions'][role]['sha256']=None;validate(c)
 def test_historical_and_defaults(self):
  for k,v in [('historical_identity','PROVEN'),('prospective_runtime_reviewed',False)]:
   with self.subTest(k=k),self.assertRaises(ValueError):
    c=copy.deepcopy(self.c);c['runtime_defaults'][k]=v;validate(c)
if __name__=='__main__':unittest.main()
