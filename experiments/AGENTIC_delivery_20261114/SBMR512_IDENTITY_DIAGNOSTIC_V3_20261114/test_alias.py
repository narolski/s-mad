import importlib.util,pathlib,sys,unittest,os
from unittest.mock import patch
HERE=pathlib.Path(__file__).resolve().parent
sp=importlib.util.spec_from_file_location('diagnostic',HERE/'test_diagnostic.py');d=importlib.util.module_from_spec(sp);sp.loader.exec_module(d);a=d.a
class Alias(d.Diagnostic):
 def test_primary_mismatch_before_any_file_body(self):
  (self.v/'bin/python').unlink();(self.v/'bin/python').symlink_to('/outside/SECRET')
  with patch.object(a.Reader,'get',side_effect=AssertionError('body forbidden')):
   with self.assertRaisesRegex(ValueError,'interpreter_primary_alias_mismatch'):a.interpreter(a.Reader(),str(self.v))
 def test_second_alias_mismatch_before_any_file_body(self):
  self.alias.unlink();self.alias.symlink_to('/outside/SECRET')
  with patch.object(a.Reader,'get',side_effect=AssertionError('body forbidden')):
   with self.assertRaisesRegex(ValueError,'interpreter_uv_alias_mismatch'):a.interpreter(a.Reader(),str(self.v))
 def test_equivalent_relative_alias_is_not_accepted(self):
  self.alias.unlink();self.alias.symlink_to(self.version.name)
  with self.assertRaisesRegex(ValueError,'interpreter_uv_alias_mismatch'):a.interpreter(a.Reader(),str(self.v))
 def test_canonical_leaf_symlink_never_read(self):
  self.canonical.unlink();self.canonical.symlink_to(self.v/'bin/python3')
  with patch.object(a.safeio.os,'read',side_effect=AssertionError('body forbidden')):
   with self.assertRaises(OSError):a.interpreter(a.Reader(),str(self.v))
 def test_canonical_ancestor_symlink_never_read(self):
  target=self.v.parent/'replacement';self.version.rename(target);self.version.symlink_to(target,target_is_directory=True)
  with patch.object(a.safeio.os,'read',side_effect=AssertionError('body forbidden')):
   with self.assertRaises(OSError):a.interpreter(a.Reader(),str(self.v))
 def test_canonical_growth_closed_telemetry(self):
  real=a.safeio.os.read;once=False
  def grow(fd,n):
   nonlocal once
   if not once:
    with self.canonical.open('ab') as f:f.write(b'CANARY')
    once=True
   return real(fd,n)
  with patch.object(a.safeio.os,'read',side_effect=grow):
   with self.assertRaises(ValueError) as caught:a.interpreter(a.Reader(),str(self.v))
  result=a.diagnostic(caught.exception);self.assertEqual(result['stage'],'INTERPRETER_READ');self.assertEqual(result['condition'],'VALIDATION_FILE_GREW');self.assertNotIn('CANARY',str(result))
 def test_alias_changes_after_literal_snapshot_cannot_redirect_hash(self):
  original=a.literal_link
  def changing(path):
   got=original(path)
   if path==str(self.alias):self.alias.unlink();self.alias.symlink_to('/outside/SECRET')
   return got
  with patch.object(a,'literal_link',side_effect=changing):
   r=a.interpreter(a.Reader(),str(self.v))
  self.assertEqual(r['resolved'],str(self.canonical));self.assertEqual(r['content']['path'],str(self.canonical))
 def test_exact_scope_permission_required_before_body(self):
  release=dict(decision='GO_SBMR512_FIXED_IDENTITY_DIAGNOSTIC_V3',root_authorized=True,repeat_metadata_read_for_diagnostic_authorized=True,exact_two_alias_and_canonical_interpreter_scope_authorized=False)
  with patch.object(sys,'argv',['acquire','--release','/synthetic']),patch.object(a.safeio,'control',return_value=(release,'0'*64)),patch.object(a,'collect',side_effect=AssertionError('must not collect')):
   with self.assertRaisesRegex(ValueError,'exact_alias_scope_not_authorized'):a.main()
if __name__=='__main__':unittest.main(verbosity=2)
