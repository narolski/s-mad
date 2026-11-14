import hashlib,io,json,pathlib,types,unittest
from unittest.mock import patch
import authority,probe
HERE=pathlib.Path(__file__).parent
class AuthorityTool(unittest.TestCase):
 def test_config_and_grant_snapshots_never_reopen(self):
  for kind in ('config','grant'):
   original=json.dumps(dict(kind=kind,bootstrap='PINNED')).encode();evil=json.dumps(dict(kind=kind,bootstrap='UNBOUND')).encode();calls=[]
   def swapped(*args,**kwargs):
    calls.append(True);return io.BytesIO(original if len(calls)==1 else evil)
   with patch('builtins.open',side_effect=swapped):obj=authority.capture_json('/synthetic/'+kind,hashlib.sha256(original).hexdigest())
   self.assertEqual(obj['bootstrap'],'PINNED');self.assertEqual(len(calls),1)
  with patch('builtins.open',return_value=io.BytesIO(b'12345')),self.assertRaises(ValueError):authority.capture_bytes('/synthetic/x','0'*64,4)
 def test_all_parsed_authorities_use_snapshot_helper(self):
  for name in ('launch.py','node_driver.py','probe.py'):
   text=(HERE/name).read_text();self.assertIn('capture_json(',text)
   self.assertNotIn("json.loads(pathlib.Path(path).read_bytes())",text)
   self.assertNotIn("sha(path)!=expected",text)
 def test_fixed_root_os_tool_identity_modes_same_descriptor_query(self):
  # Fully mocked OS metadata/tool execution: no actual driver/native body read.
  st=types.SimpleNamespace(st_uid=0,st_mode=0o100755,st_dev=1,st_ino=17,st_size=18,st_mtime_ns=2,st_ctime_ns=3)
  result=types.SimpleNamespace(stdout=b'580.95.05\n580.95.05\n',stderr=b'')
  common=dict(nvidia_smi_path='/usr/bin/nvidia-smi',path_aliases=[],nvidia_smi_identity_mode='ACQUIRE_FIXED_ROOT_OS_TOOL',nvidia_smi_sha256=None,root_managed_tool_identity_acquisition=True)
  with patch.object(probe,'open_components',return_value=99),patch.object(probe.os,'fstat',return_value=st),patch.object(probe.os,'close'),patch.object(probe,'hash_fd',return_value='a'*64),patch.object(probe.subprocess,'run',return_value=result) as run:
   r=probe.driver_query(common);self.assertEqual(r['sha256'],'a'*64);self.assertEqual(r['bytes'],18)
   self.assertEqual(run.call_args.kwargs['executable'],'/proc/self/fd/99');self.assertEqual(run.call_args.kwargs['pass_fds'],(99,));self.assertEqual(run.call_args.args[0],['/usr/bin/nvidia-smi','--query-gpu=driver_version','--format=csv,noheader,nounits'])
   common['nvidia_smi_identity_mode']='KNOWN_PIN';common['nvidia_smi_sha256']='a'*64;self.assertEqual(probe.driver_query(common)['sha256'],'a'*64)
   common['nvidia_smi_sha256']='b'*64
   with self.assertRaises(ValueError):probe.driver_query(common)
 def test_driver_trust_and_numeric_grammar_rejections(self):
  g=dict(nvidia_smi_path='/usr/bin/nvidia-smi',path_aliases=[],nvidia_smi_identity_mode='ACQUIRE_FIXED_ROOT_OS_TOOL',nvidia_smi_sha256=None,root_managed_tool_identity_acquisition=True)
  st=types.SimpleNamespace(st_uid=0,st_mode=0o100755,st_dev=1,st_ino=17,st_size=18,st_mtime_ns=2,st_ctime_ns=3)
  with patch.object(probe,'open_components',return_value=99),patch.object(probe.os,'fstat',return_value=st),patch.object(probe.os,'close'),patch.object(probe,'hash_fd',return_value='a'*64),patch.object(probe.subprocess,'run',return_value=types.SimpleNamespace(stdout=b'580.95 evil\n',stderr=b'')),self.assertRaises(ValueError):probe.driver_query(g)
  st.st_uid=501
  with patch.object(probe,'open_components',return_value=99),patch.object(probe.os,'fstat',return_value=st),patch.object(probe.os,'close'),self.assertRaises(ValueError):probe.driver_query(g)
if __name__=='__main__':unittest.main()
