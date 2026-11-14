import ast,importlib.util,json,pathlib,unittest
P=pathlib.Path('/home/narolski/smad-next/experiments/AGENTIC_delivery_20261114/SBMR512_IDENTITY_DIAGNOSTIC_V2_20261114')
s=importlib.util.spec_from_file_location('acquire',P/'acquire.py');a=importlib.util.module_from_spec(s);s.loader.exec_module(a)
class Review(unittest.TestCase):
 def test_closed_registry_agrees_with_code(self):
  r=json.loads((P/'ENUM_REGISTRY.json').read_text())
  for key in ('DEPS','MODULES','STAGES','CONDITIONS'):self.assertEqual(set(r[key]),set(getattr(a,key)))
  allowed=set(r['OTHER_CONDITIONS'])|{'VALIDATION_'+c.upper() for c in a.CONDITIONS}
  for stage in a.STAGES:
   a.stage(stage)
   for exc in (ValueError('unknown /SECRET'),ValueError('file_cap'),OSError(777,'SECRET'),MemoryError('SECRET')):
    got=a.diagnostic(exc,'0'*64);self.assertIn(got['condition'],allowed);self.assertNotIn('SECRET',json.dumps(got));self.assertEqual(got['release_sha256'],'0'*64)
 def test_arbitrary_exception_arg_never_stringified(self):
  class Canary:
   def __str__(self):raise AssertionError('stringification leaked')
   def __repr__(self):raise AssertionError('repr leaked')
  for exc in (ValueError(Canary()),RuntimeError(Canary()),ValueError('unknown',Canary())):self.assertEqual(a.diagnostic(exc)['condition'],'UNCLASSIFIED')
 def test_parent_repeat_gate_before_claim(self):
  text=(P/'acquire.py').read_text();main=next(n for n in ast.parse(text).body if isinstance(n,ast.FunctionDef) and n.name=='main');block=ast.get_source_segment(text,main)
  for token in ("release['repeat_metadata_read_for_diagnostic_authorized'] is True","release['parent_failure_review_sha256']==PARENT_FAILURE_REVIEW","release['parent_release_sha256']==PARENT_RELEASE"):
   self.assertLess(block.index(token),block.index("'CLAIM.json'"))
  template=json.loads((P/'ROOT_DIAGNOSTIC_GRANT_TEMPLATE_NOT_AUTHORITY.json').read_text());self.assertFalse(template['repeat_metadata_read_for_diagnostic_authorized']);self.assertFalse(template['root_authorized'])
 def test_original_reader_caps_sources_unchanged(self):
  parent=P.parent/'SBMR512_IDENTITY_ACQUISITION_V1_20261114/acquire.py';old=ast.parse(parent.read_text());new=ast.parse((P/'acquire.py').read_text())
  before=next(n for n in old.body if isinstance(n,ast.ClassDef) and n.name=='Reader');after=next(n for n in new.body if isinstance(n,ast.ClassDef) and n.name=='Reader');self.assertEqual(ast.dump(before),ast.dump(after))
  def values(tree):return {n.targets[0].id:ast.dump(n.value) for n in tree.body if isinstance(n,ast.Assign) and isinstance(n.targets[0],ast.Name) and n.targets[0].id in ('VENV','DEPS','MODULES','SOURCES','MAX_TOTAL')}
  self.assertEqual(values(old),values(new))
 def test_no_old_output_or_original_failure_reinterpretation(self):
  self.assertTrue(a.OUTPUT.endswith('/sbmr512_identity_diagnostic_v2'));self.assertEqual(a.PARENT_FAILURE_REVIEW,'54dd026d34345eb9b30d3726d984fad82f2eeeb05f66b9b6be8250a14e40879e');self.assertEqual(a.PARENT_RELEASE,'f8c358e06b62fbc41c81bcb6ae8ce897534aa26529901119bab284aa629cb974')
if __name__=='__main__':unittest.main(verbosity=2)
