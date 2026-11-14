import ast,hashlib,importlib.util,json,pathlib,unittest,os
from unittest.mock import patch
P=pathlib.Path('/home/narolski/smad-next/experiments/AGENTIC_delivery_20261114/SBMR512_IDENTITY_DIAGNOSTIC_V3_20261114')
s=importlib.util.spec_from_file_location('generated',P/'test_generated.py');f=importlib.util.module_from_spec(s);s.loader.exec_module(f);a=f.a
class Review(unittest.TestCase):
 def setUp(self):f.T.setUp(self)
 def tearDown(self):f.T.tearDown(self)
 def test_primary_escape_and_equivalent_text_refused(self):
  for target in ('/outside/SECRET',str(self.alias)+'/bin/../bin/python3.12'):
   (self.v/'bin/python').unlink();(self.v/'bin/python').symlink_to(target)
   with patch.object(a.Reader,'get',side_effect=AssertionError('unapproved body read')):
    with self.assertRaisesRegex(ValueError,'interpreter_primary_alias_mismatch'):a.interpreter(a.Reader(),str(self.v))
 def test_canonical_bin_component_swap_nofollow(self):
  original=a.literal_link;swapped=False
  def change(path):
   nonlocal swapped
   literal=original(path)
   if path==str(self.alias) and not swapped:
    (self.version/'bin').rename(self.version/'oldbin');(self.version/'bin').symlink_to(self.version/'oldbin',target_is_directory=True);swapped=True
   return literal
  with patch.object(a,'literal_link',side_effect=change),patch.object(a.safeio.os,'read',side_effect=AssertionError('must not read linked body')):
   with self.assertRaises(OSError):a.interpreter(a.Reader(),str(self.v))
 def test_primary_mutation_after_snapshot_fixed_canonical_hash(self):
  original=a.literal_link
  def change(path):
   literal=original(path)
   if path==str(self.v/'bin/python'):(self.v/'bin/python').unlink();(self.v/'bin/python').symlink_to('/outside/SECRET')
   return literal
  expected=hashlib.sha256(self.canonical.read_bytes()).hexdigest()
  with patch.object(a,'literal_link',side_effect=change):result=a.interpreter(a.Reader(),str(self.v))
  self.assertEqual(result['content']['sha256'],expected);self.assertEqual(result['content']['path'],str(self.canonical))
 def test_canonical_same_inode_mutation_held_and_redacted(self):
  original=a.safeio.os.read;once=False
  def change(fd,n):
   nonlocal once
   block=original(fd,n)
   if not once:self.canonical.write_bytes(b'SECRET_MUTATION');once=True
   return block
  with patch.object(a.safeio.os,'read',side_effect=change):
   with self.assertRaises(ValueError) as caught:a.interpreter(a.Reader(),str(self.v))
  got=a.diagnostic(caught.exception);self.assertEqual(got['stage'],'INTERPRETER_READ');self.assertNotIn('SECRET',json.dumps(got));self.assertFalse(got['identity_admission'])
 def test_closed_telemetry_rejects_arbitrary_args(self):
  class Canary:
   def __str__(self):raise AssertionError('raw string')
   def __repr__(self):raise AssertionError('raw repr')
  for exc in (ValueError(Canary()),RuntimeError(Canary()),ValueError('raw/SECRET')):
   self.assertEqual(a.diagnostic(exc)['condition'],'UNCLASSIFIED');self.assertNotIn('SECRET',json.dumps(a.diagnostic(exc)))
 def test_scope_equality_before_body_and_unsigned_false(self):
  text=(P/'acquire.py').read_text();main=next(n for n in ast.parse(text).body if isinstance(n,ast.FunctionDef) and n.name=='main');block=ast.get_source_segment(text,main)
  self.assertLess(block.index("release['exact_alias_mapping']==dict("),block.index("'CLAIM.json'"));self.assertLess(block.index("release['exact_two_alias_and_canonical_interpreter_scope_authorized'] is True"),block.index('result=collect()'))
  unsigned=json.loads((P/'ROOT_V3_GRANT_TEMPLATE_NOT_AUTHORITY.json').read_text());self.assertFalse(unsigned['exact_two_alias_and_canonical_interpreter_scope_authorized']);self.assertFalse(unsigned['repeat_metadata_read_for_diagnostic_authorized'])
 def test_noninterpreter_scope_and_reader_unchanged(self):
  old=ast.parse((P.parent/'SBMR512_IDENTITY_DIAGNOSTIC_V2_20261114/acquire.py').read_text());new=ast.parse((P/'acquire.py').read_text())
  for name in ('collect','names','normal','dist_name','Reader','diagnostic','fail'):
   before=next(n for n in old.body if isinstance(n,(ast.FunctionDef,ast.ClassDef)) and n.name==name);after=next(n for n in new.body if isinstance(n,(ast.FunctionDef,ast.ClassDef)) and n.name==name);self.assertEqual(ast.dump(before),ast.dump(after))
if __name__=='__main__':unittest.main(verbosity=2)
