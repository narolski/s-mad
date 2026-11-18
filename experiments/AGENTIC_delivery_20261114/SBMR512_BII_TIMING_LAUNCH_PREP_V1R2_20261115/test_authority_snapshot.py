import copy,hashlib,io,json,os,pathlib,sys,tempfile,unittest
from unittest.mock import patch
import authority,launch
import test_contract as fixtures
HERE=pathlib.Path(__file__).parent
class Snapshot(unittest.TestCase):
 def test_full_launch_config_replacement_uses_bound_A_only(self):
  fixture=fixtures.Contract();fixture.setUp();a=fixture.c;b=copy.deepcopy(a);b['node_bootstrap']='/synthetic/UNBOUND_BOOTSTRAP';b['content_pins'][b['node_bootstrap']]='9'*64
  raw=json.dumps(a).encode();expected=hashlib.sha256(raw).hexdigest()
  with tempfile.TemporaryDirectory(dir=HERE) as d:
   root=pathlib.Path(d);cfg=root/'config.json';cfg.write_bytes(raw);j=root/'dispatch';source=root/'source';source.mkdir()
   def snapshot_then_replace(path,digest):
    captured=authority.capture_json(path,digest);cfg.write_text(json.dumps(b));return captured
   with patch.object(launch,'BASE',root),patch.object(launch,'J',j),patch.object(launch,'SRC',source),patch.object(launch,'capture_json',side_effect=snapshot_then_replace),patch.object(launch,'sha',return_value='1'*64),patch.object(launch.os,'isatty',return_value=True),patch.dict(launch.os.environ,{'TMUX_PANE':'%synthetic'}),patch.object(launch.subprocess,'check_output',return_value='0'),patch.object(launch.subprocess,'run'),patch.object(launch.subprocess,'call',return_value=0) as call,patch.object(sys,'argv',['launch',str(cfg),expected]):
    self.assertEqual(launch.main(),0)
   claim=json.loads((j/'CLAIM.json').read_text());intent=json.loads((j/'INTENT.json').read_text());self.assertEqual(claim['config_sha256'],expected);self.assertIn('/synthetic/bootstrap',intent['argv']);self.assertNotIn('/synthetic/UNBOUND_BOOTSTRAP',intent['argv']);self.assertEqual(call.call_args.args[0],intent['argv']);self.assertNotEqual(hashlib.sha256(cfg.read_bytes()).hexdigest(),expected)
 def test_authority_single_capture_and_caps(self):
  raw=b'{"bootstrap":"BOUND"}';evil=b'{"bootstrap":"UNBOUND"}';calls=[]
  def swap(*args,**kwargs):calls.append(True);return io.BytesIO(raw if len(calls)==1 else evil)
  with patch('builtins.open',side_effect=swap):self.assertEqual(authority.capture_json('/synthetic/config',hashlib.sha256(raw).hexdigest())['bootstrap'],'BOUND')
  self.assertEqual(len(calls),1)
  with patch('builtins.open',return_value=io.BytesIO(b'12345')),self.assertRaises(ValueError):authority.capture_json('/synthetic/config','0'*64,4)
  with patch('builtins.open',return_value=io.BytesIO(b'{')),self.assertRaises(json.JSONDecodeError):authority.capture_json('/synthetic/config',hashlib.sha256(b'{').hexdigest())
 def test_source_uses_captured_authorities(self):
  for name in ('launch.py','node_driver.py'):
   source=(HERE/name).read_text();self.assertIn('capture_json(',source);self.assertNotIn('sha(path)!=expected',source);self.assertNotIn('json.loads(pathlib.Path(path).read_bytes())',source)
if __name__=='__main__':unittest.main()
