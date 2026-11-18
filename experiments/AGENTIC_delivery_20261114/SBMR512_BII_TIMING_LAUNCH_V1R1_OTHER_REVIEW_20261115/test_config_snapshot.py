"""Generated-only reproduction; every subprocess/native command is mocked."""
import sys,pathlib,tempfile,hashlib,json,copy,os,unittest
from unittest.mock import patch
from types import SimpleNamespace
P=pathlib.Path('/home/narolski/smad-next/experiments/AGENTIC_delivery_20261114/SBMR512_BII_TIMING_LAUNCH_PREP_V1R1_20261115');sys.path.insert(0,str(P))
import launch,test_contract
class ConfigSnapshot(unittest.TestCase):
 def test_unbound_config_bootstrap_reproduction(self):
  fixture=test_contract.Contract();fixture.setUp();a=fixture.c;b=copy.deepcopy(a);b['node_bootstrap']='/synthetic/UNBOUND_BOOTSTRAP';b['content_pins'][b['node_bootstrap']]='6'*64
  with tempfile.TemporaryDirectory() as d:
   base=pathlib.Path(d).resolve();config=base/'config.json';config.write_text(json.dumps(a));expected=hashlib.sha256(config.read_bytes()).hexdigest();commands=[]
   def fake_sha(path):
    if str(path)==str(config):
     digest=hashlib.sha256(config.read_bytes()).hexdigest();config.write_text(json.dumps(b));return digest
    return '1'*64
   def no_run(argv,**kw):commands.append(argv);return SimpleNamespace(returncode=0)
   with patch.object(launch,'BASE',base),patch.object(launch,'J',base/'dispatch'),patch.object(launch,'sha',side_effect=fake_sha),patch.object(sys,'argv',['launch.py',str(config),expected]),patch.object(launch.os,'isatty',return_value=True),patch.dict(os.environ,{'TMUX_PANE':'%generated'}),patch.object(launch.subprocess,'check_output',return_value='0'),patch.object(launch.subprocess,'run',side_effect=no_run),patch.object(launch.subprocess,'call',side_effect=lambda cmd,**kw:commands.append(cmd) or 0):
    self.assertEqual(launch.main(),0)
   intent=json.loads((base/'dispatch/INTENT.json').read_text());claim=json.loads((base/'dispatch/CLAIM.json').read_text())
   self.assertEqual(claim['config_sha256'],expected)
   self.assertNotEqual(hashlib.sha256(config.read_bytes()).hexdigest(),expected)
   self.assertEqual(intent['srun_argv'][-1],'/synthetic/UNBOUND_BOOTSTRAP')
   self.assertNotEqual(intent['srun_argv'][-1],a['node_bootstrap'])
   self.assertTrue(commands)
if __name__=='__main__':unittest.main(verbosity=2)
