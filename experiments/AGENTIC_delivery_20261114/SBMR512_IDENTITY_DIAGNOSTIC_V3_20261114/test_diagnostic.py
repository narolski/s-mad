"""Synthetic diagnostic regressions; no actual target main/collection."""
import ast,hashlib,importlib.util,json,os,pathlib,sys,unittest
from unittest.mock import patch
HERE=pathlib.Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location('fixture',HERE/'test_generated.py')
fixture=importlib.util.module_from_spec(spec);spec.loader.exec_module(fixture)
a=fixture.a
class Diagnostic(fixture.T):
 def test_every_collection_stage_durable_closed_failure(self):
  self.dist();(self.site/'torch').mkdir();(self.site/'torch/__init__.py').write_text('NEVER_IMPORT')
  expected=('INTERPRETER_PARENT','INTERPRETER_LINK','INTERPRETER_READ','PYVENV_READ','PYVENV_PARSE','LIB_DIRECTORY','PYTHON_DIRECTORY_SET','SITE_DIRECTORY','DISTRIBUTION_SET','RECORD','METADATA','METADATA_PARSE','FIXED_SOURCE')
  original=a.stage
  for index,target in enumerate(expected):
   def stop(stage,dependency=None):
    original(stage,dependency)
    if stage==target:raise ValueError('file_changed')
   out=self.v.parent/('out'+str(index));out.mkdir();fd=a.safeio.directory_fd(str(out))
   try:
    with patch.object(a,'stage',side_effect=stop):
     with self.assertRaises(ValueError) as caught:a.collect(str(self.v))
    a.fail(fd,caught.exception,'0'*64)
    r=json.loads((out/'FAILED.json').read_bytes());self.assertEqual(r['stage'],target);self.assertEqual(r['condition'],'VALIDATION_FILE_CHANGED')
    self.assertNotIn(str(self.v),json.dumps(r))
    with self.assertRaises(FileExistsError):a.fail(fd,caught.exception,'0'*64)
   finally:os.close(fd)
 def test_all_stage_condition_vocab_no_error_canary(self):
  for s in a.STAGES:
   a.stage(s)
   for exc in (ValueError('RAW_SECRET /outside/image.png'),RuntimeError('RAW_SECRET'),OSError(13,'RAW_SECRET','/outside/image.png'),UnicodeDecodeError('utf8',b'RAW_SECRET',0,1,'RAW_SECRET')):
    r=a.diagnostic(exc);self.assertEqual(r['stage'],s);self.assertNotIn('RAW_SECRET',json.dumps(r));self.assertNotIn('/outside',json.dumps(r))
  for c in a.CONDITIONS:self.assertEqual(a.diagnostic(ValueError(c))['condition'],'VALIDATION_'+c.upper())
 def test_internal_stage_dependency_refuse(self):
  for stage,dep in (('UNBOUND',None),('METADATA','RAW_SECRET')):
   with self.assertRaises(RuntimeError):a.stage(stage,dep)
 def test_repeat_permission_false_stops_before_target_access(self):
  release=dict(decision='GO_SBMR512_FIXED_IDENTITY_DIAGNOSTIC_V3',root_authorized=True,repeat_metadata_read_for_diagnostic_authorized=False)
  with patch.object(sys,'argv',['acquire.py','--release','/synthetic']),patch.object(a.safeio,'control',return_value=(release,'0'*64)),patch.object(a,'collect',side_effect=AssertionError('must not collect')):
   with self.assertRaisesRegex(ValueError,'repeat_read_not_authorized'):a.main()
 def test_same_computational_collect_interpreter_ast(self):
  prior=HERE.parent/'SBMR512_IDENTITY_ACQUISITION_V1_20261114/acquire.py'
  class Remove(ast.NodeTransformer):
   def visit_Expr(self,node):
    if isinstance(node.value,ast.Call) and isinstance(node.value.func,ast.Name) and node.value.func.id=='stage':return None
    return self.generic_visit(node)
  old=ast.parse(prior.read_text());new=ast.parse((HERE/'acquire.py').read_text())
  for name in ('collect','names','normal','dist_name'):
   before=next(n for n in old.body if isinstance(n,ast.FunctionDef) and n.name==name)
   after=next(n for n in new.body if isinstance(n,ast.FunctionDef) and n.name==name)
   self.assertEqual(ast.dump(before),ast.dump(Remove().visit(after)))
 def test_safeio_parent_unchanged(self):
  prior=HERE.parent/'SBMR512_IDENTITY_ACQUISITION_V1_20261114/safeio.py'
  self.assertEqual(prior.read_bytes(),(HERE/'safeio.py').read_bytes())
 def test_receipt_complete_failures_preserve_typed_terminal(self):
  for target in ('RECEIPT','COMPLETE'):
   out=self.v.parent/('main_'+target)
   release=dict(decision='GO_SBMR512_FIXED_IDENTITY_DIAGNOSTIC_V3',root_authorized=True,
    repeat_metadata_read_for_diagnostic_authorized=True,exact_two_alias_and_canonical_interpreter_scope_authorized=True,exact_alias_mapping=dict(primary_path=a.INTERPRETER,primary_target=a.EXPECTED_PRIMARY_TARGET,uv_alias=a.UV_ALIAS_DIR,uv_target=a.UV_VERSION_DIR,canonical_file=a.CANONICAL_INTERPRETER),parent_failure_review_sha256=a.PARENT_FAILURE_REVIEW,
    parent_release_sha256=a.PARENT_RELEASE,author='author',reviewer='other',venv=a.VENV,output=str(out),
    automatic_retry=False,scope='FIXED_CURRENT_SOURCE_INSTALL_METADATA_ONLY',scientific_read='HOLD',
    independent_review_path='/synthetic',independent_review_sha256='0'*64,
    source_sha256={'acquire.py':'0'*64,'safeio.py':'0'*64},bootstrap_interpreter=os.path.realpath(sys.executable),bootstrap_interpreter_sha256='0'*64)
   original=a.safeio.put
   def fail_write(fd,name,value):
    if name==target+'.json':raise OSError(28,'RAW_SECRET','/outside')
    return original(fd,name,value)
   with patch.object(a,'OUTPUT',str(out)),patch.object(sys,'argv',['acquire.py','--release','/synthetic']),patch.object(a.safeio,'control',return_value=(release,'0'*64)),patch.object(a.safeio,'snapshot',return_value=(b'','0'*64,0)),patch.object(a,'collect',return_value={'synthetic':True}),patch.object(a.safeio,'put',side_effect=fail_write):
    self.assertEqual(a.main(),1)
   r=json.loads((out/'FAILED.json').read_bytes());self.assertEqual(r['stage'],target);self.assertEqual(r['condition'],'OS_NO_SPACE')
   self.assertNotIn('RAW_SECRET',json.dumps(r));self.assertTrue((out/'CLAIM.json').exists());self.assertFalse((out/'COMPLETE.json').exists())
 def test_entry_preclaim_never_exports_exception_text(self):
  import contextlib,io
  stream=io.StringIO()
  with patch.object(a,'main',side_effect=ValueError('RAW_SECRET /outside')),contextlib.redirect_stderr(stream):
   self.assertEqual(a.entry(),1)
  self.assertNotIn('RAW_SECRET',stream.getvalue());self.assertNotIn('/outside',stream.getvalue())
if __name__=='__main__':unittest.main(verbosity=2)
