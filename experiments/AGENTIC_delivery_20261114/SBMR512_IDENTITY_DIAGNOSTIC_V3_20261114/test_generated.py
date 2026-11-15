import importlib.util,pathlib,tempfile,os,json,hashlib,sys,unittest
from unittest.mock import patch
HERE=pathlib.Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location('safeio',HERE/'safeio.py');m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);sys.modules['safeio']=m
spec=importlib.util.spec_from_file_location('acquire',HERE/'acquire.py');a=importlib.util.module_from_spec(spec);spec.loader.exec_module(a)
class T(unittest.TestCase):
 def setUp(self):
  self.tmp=tempfile.TemporaryDirectory();self.v=pathlib.Path(self.tmp.name).resolve()/'venv';(self.v/'bin').mkdir(parents=True)
  (self.v/'bin/python3').write_bytes(b'GENERATED_NOT_EXECUTABLE');(self.v/'bin/python').symlink_to('python3')
  (self.v/'pyvenv.cfg').write_text('home = /synthetic\nversion = 3.12\ncommand = OMIT\n')
  self.site=self.v/'lib/python3.12/site-packages';self.site.mkdir(parents=True)
  self.uv=self.v.parent/'uv';self.uv.mkdir();self.alias=self.uv/'cpython-generic';self.version=self.uv/'cpython-versioned';(self.version/'bin').mkdir(parents=True)
  self.canonical=self.version/'bin/python3.12';self.canonical.write_bytes(b'GENERATED_NOT_EXECUTABLE')
  self.alias.symlink_to(self.version,target_is_directory=True)
  (self.v/'bin/python').unlink();(self.v/'bin/python').symlink_to(str(self.alias/'bin/python3.12'))
  self.patches=[patch.object(a,'UV_ALIAS_DIR',str(self.alias)),patch.object(a,'UV_VERSION_DIR',str(self.version)),patch.object(a,'EXPECTED_PRIMARY_TARGET',str(self.alias/'bin/python3.12')),patch.object(a,'CANONICAL_INTERPRETER',str(self.canonical))]
  for item in self.patches:item.start()

 def tearDown(self):
  for item in reversed(self.patches):item.stop()
  self.tmp.cleanup()
 def dist(self,name='torch'):
  d=self.site/(name+'-2.11.0.dist-info');d.mkdir();(d/'RECORD').write_text('NOT_PARSED');(d/'METADATA').write_text('Name: '+name+'\nVersion: 2.11.0\n');return d
 def test_identity_without_execution(self):
  self.dist();r=a.collect(str(self.v));self.assertEqual(r['interpreter']['resolved'],str(self.canonical));self.assertFalse(r['target_interpreter_executed']);self.assertNotIn('command',r['pyvenv_cfg']['selected_fields'])
 def test_ignore_unrelated_names_and_no_recursive_read(self):
  self.dist();(self.site/'private_data').mkdir();(self.site/'private_data/payload.npz').write_bytes(b'CANARY');r=a.collect(str(self.v));self.assertNotIn('private_data',str(r))
 def test_fixed_source_and_missing_unknown(self):
  self.dist();(self.site/'torch').mkdir();(self.site/'torch/__init__.py').write_text('raise RuntimeError("NEVER IMPORT")');r=a.collect(str(self.v));self.assertTrue(any(x['status']=='UNKNOWN_ABSENT' for x in r['site_packages'][0]['source_files']))
 def test_metadata_fallback_blocked(self):
  d=self.dist();(d/'METADATA').write_bytes(b'');(d/'PKG-INFO').write_text('Name: torch\nVersion: BAD\n')
  with self.assertRaises(ValueError):a.collect(str(self.v))
 def test_source_symlink_refused(self):
  self.dist();(self.site/'torch').mkdir();(self.site/'torch/__init__.py').symlink_to(self.v/'bin/python3')
  with self.assertRaises(OSError):a.collect(str(self.v))
 def test_interpreter_target_outside_grant(self):
  (self.v/'bin/python').unlink();(self.v/'bin/python').symlink_to('/unadmitted/python')
  with self.assertRaises(ValueError):a.collect(str(self.v))
 def test_interpreter_cycle_bound(self):
  self.alias.unlink();self.alias.symlink_to(self.alias)
  with self.assertRaises(ValueError):a.collect(str(self.v))
 def test_duplicate_dist_refused(self):
  self.dist();(self.site/'torch-9.dist-info').mkdir()
  with self.assertRaises(ValueError):a.collect(str(self.v))
 def test_directory_bound(self):
  with self.assertRaises(ValueError):a.names(str(self.v/'bin'),1)
 def test_missing_site_retained(self):
  self.site.rmdir();r=a.collect(str(self.v));self.assertEqual(r['site_packages'][0]['status'],'UNKNOWN_ABSENT')
 def test_dist_filters(self):
  self.assertEqual(a.dist_name('Pillow-12.0.dist-info'),'Pillow');self.assertIsNone(a.dist_name('torch_bad-1.dist-info'));self.assertIsNone(a.dist_name('torch-1.dist-info.bak'))
if __name__=='__main__':unittest.main(verbosity=2)
