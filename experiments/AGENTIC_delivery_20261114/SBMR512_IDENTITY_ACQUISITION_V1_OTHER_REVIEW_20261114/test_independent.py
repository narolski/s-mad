import importlib.util,pathlib,tempfile,unittest,os,hashlib,ast
from unittest.mock import patch
P=pathlib.Path('/home/narolski/smad-next/experiments/AGENTIC_delivery_20261114/SBMR512_IDENTITY_ACQUISITION_V1_20261114')
s=importlib.util.spec_from_file_location('acquire',P/'acquire.py');a=importlib.util.module_from_spec(s);s.loader.exec_module(a)
class Review(unittest.TestCase):
 def setUp(self):
  self.tmp=tempfile.TemporaryDirectory();self.v=pathlib.Path(self.tmp.name).resolve()/'venv';(self.v/'bin').mkdir(parents=True);(self.v/'bin/python').write_bytes(b'NONEXECUTABLE');self.site=self.v/'lib/python3.12/site-packages';self.site.mkdir(parents=True)
 def tearDown(self):self.tmp.cleanup()
 def test_payload_never_opened(self):
  (self.site/'torch').mkdir();(self.site/'torch/__init__.py').write_bytes(b'raise Exception("not executed")');(self.site/'torch/weights.pt').write_bytes(b'FORBIDDEN');(self.site/'private.npz').write_bytes(b'FORBIDDEN');original=a.safeio.os.open;seen=[]
  def track(p,*args,**kw):seen.append(str(p));return original(p,*args,**kw)
  with patch.object(a.safeio.os,'open',side_effect=track):r=a.collect(str(self.v))
  self.assertFalse(any(x.endswith(('.pt','.npz','.pth')) for x in seen));self.assertNotIn('private.npz',str(r))
 def test_ancestor_symlink_excluded(self):
  (self.v/'lib/python3.12').rename(self.v/'lib/old');(self.v/'lib/python3.12').symlink_to(self.v/'lib/old',target_is_directory=True)
  with self.assertRaises(OSError):a.collect(str(self.v))
 def test_record_symlink_does_not_read_target(self):
  d=self.site/'torch-1.dist-info';d.mkdir();(d/'RECORD').symlink_to(self.v/'bin/python');(d/'METADATA').write_bytes(b'Name: torch\nVersion: 1\n')
  with self.assertRaises(OSError):a.collect(str(self.v))
 def test_read_cap_before_body(self):
  p=self.v/'oversize';p.write_bytes(b'1234');original=a.safeio.os.read
  with patch.object(a.safeio.os,'read',side_effect=AssertionError('unexpected read')):
   with self.assertRaises(ValueError):a.Reader().get(str(p),3)
 def test_aggregate_cap(self):
  p=self.v/'small';p.write_bytes(b'1234');r=a.Reader();r.used=a.MAX_TOTAL-3
  with self.assertRaises(ValueError):r.get(str(p),100)
 def test_interpreter_absolute_escape_rejected(self):
  (self.v/'bin/python').unlink();(self.v/'bin/python').symlink_to('/usr/bin/../../etc/passwd')
  with self.assertRaises(ValueError):a.collect(str(self.v))
 def test_bootstrap_and_source_pins_required_before_collect(self):
  tree=ast.parse((P/'acquire.py').read_text());main=next(n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name=='main');text=ast.get_source_segment((P/'acquire.py').read_text(),main)
  self.assertLess(text.index("release['bootstrap_interpreter_sha256']"),text.index('result=collect()'))
  self.assertLess(text.index("release['source_sha256'][name]"),text.index('result=collect()'))
  self.assertLess(text.index("'CLAIM.json'"),text.index('result=collect()'))
 def test_fixed_source_classes_no_target_execution(self):
  self.assertEqual(len(a.SOURCES),21);self.assertTrue(all(x.endswith('.py') and '..' not in x for x in a.SOURCES))
  names=[n.func.id for n in ast.walk(ast.parse((P/'acquire.py').read_text())) if isinstance(n,ast.Call) and isinstance(n.func,ast.Name)]
  self.assertNotIn('exec',names);self.assertNotIn('eval',names)
if __name__=='__main__':unittest.main(verbosity=2)
