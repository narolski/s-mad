import copy,hashlib,json,pathlib,tempfile,unittest
from unittest.mock import patch
import probe
from contract import validate,OUTPUT,BASE
class Generated(unittest.TestCase):
 def test_maps_fixed_class(self):
  p='/usr/lib64/libgenerated_fixture.so.1';raw=('0-1 r-xp 0 0:0 0 '+p+'\n0-1 r--p 0 0:0 0 '+p+'\n').encode()
  self.assertEqual(probe.parse_maps(raw),[p]);self.assertEqual(probe.parse_maps(b'0-1 r-xp 0 0:0 0 [vdso]\n'),[])
  for raw in (b'x x x x x /tmp/user/checkpoint.so\n',b'x x x x x /usr/lib64/libfixture.so (deleted)\n',b'x'*(probe.MAX_MAPS+1)):
   with self.assertRaises(ValueError):probe.parse_maps(raw)
 def test_generated_elf_body_metadata_and_no_follow(self):
  with tempfile.TemporaryDirectory() as d,patch.object(probe,'ALLOWED_ROOTS',(d,)):
   p=pathlib.Path(d)/'fixture.so';data=b'\x7fELF'+b'GENERATED_NOT_A_REAL_LIBRARY'*3;p.write_bytes(data)
   r,n=probe.file_identity(str(p),True,4096);self.assertEqual(r['sha256'],hashlib.sha256(data).hexdigest());self.assertEqual(n,len(data))
   r,n=probe.file_identity(str(p),False,0);self.assertIsNone(r['sha256']);self.assertEqual(n,0)
   with self.assertRaises(ValueError):probe.file_identity(str(p),True,1)
   q=pathlib.Path(d)/'link.so';q.symlink_to(p)
   with self.assertRaises(OSError):probe.file_identity(str(q),True,4096)
   p.write_bytes(b'not ELF')
   with self.assertRaises(ValueError):probe.file_identity(str(p),True,4096)
 def test_phase_contract_independent_of_model_inputs(self):
  c=dict(decision='GO_SBMR512_RUNTIME_METADATA_PHASE1_DISPATCH_V1',root_authorized=True,author='A',reviewer='OTHER',scientific_read='HOLD',automatic_retry=False,driver_dir=BASE+'/dispatch_s408',worker_dir=BASE+'/source',output=OUTPUT,input_identity_receipt_sha256='7847e2007570f75012f36fccd9257f73231c9a28cafbfb38ba86c2286d76e61b',admissions={r:dict(path='/synthetic/'+r,status='ROOT_ADOPTED',sha256='1'*64) for r in ('current_identity_adoption','OTHER_phase1_source_review','runtime_import_scope','native_elf_scope','site_profile')},node_bootstrap='/synthetic/bootstrap',python='/home/narolski/dmenv/bin/python',runtime_grant='/synthetic/grant',source_manifest_path=BASE+'/source/SOURCE_SHA256SUMS')
  c['content_pins']={c[k]:'2'*64 for k in ('node_bootstrap','python','runtime_grant','source_manifest_path')};self.assertTrue(validate(c))
  for k,v in [('root_authorized',False),('scientific_read','GO'),('driver_dir','/tmp/alternate'),('python','/tmp/other'),('admissions',{})]:
   with self.subTest(k=k),self.assertRaises((ValueError,KeyError)):
    t=copy.deepcopy(c);t[k]=v;validate(t)
 def test_source_control_order_and_no_model_ops(self):
  here=pathlib.Path(__file__).parent;source=(here/'probe.py').read_text();launch=(here/'launch.py').read_text();entry=(here/'allocation_entry.sh').read_text()
  self.assertLess(source.index("put(out/'CLAIM.json'"),source.index('importlib.import_module(name)'))
  self.assertLess(launch.index("put('CLAIM.json'"),launch.index('subprocess.call(cmd'))
  self.assertLess(launch.index("put('INTENT.json'"),launch.index('subprocess.call(cmd'))
  self.assertLess(entry.index('NATIVE_JOB_ID.txt'),entry.index('exec '))
  for absent in ('torch.load(', 'np.load(', 'create_model(', 'build_run_model(', 'forward_logit('):self.assertNotIn(absent,source)
if __name__=='__main__':unittest.main()
