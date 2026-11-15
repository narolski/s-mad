"""Generated files only; never invokes main, target package imports or real env collection."""
import ast
import hashlib
import importlib.util
import json
import os
import pathlib
import tempfile
import unittest
from unittest.mock import patch
spec=importlib.util.spec_from_file_location('probe',pathlib.Path(__file__).with_name('probe.py'))
p=importlib.util.module_from_spec(spec);spec.loader.exec_module(p)
H=lambda raw:hashlib.sha256(raw).hexdigest()
class Fixtures(unittest.TestCase):
 def setUp(self):
  self.tmp=tempfile.TemporaryDirectory();self.root=pathlib.Path(self.tmp.name).resolve()
 def tearDown(self):self.tmp.cleanup()
 def file(self,name,raw=b'generated'):
  f=self.root/name;f.parent.mkdir(parents=True,exist_ok=True);f.write_bytes(raw);return f
 def request(self):return dict(schema='SBMR512_ENV_SOURCE_REQUEST_V1R1',interpreter='/synthetic/python',interpreter_sha256='0'*64,distributions=[],files=[])
 def dist(self,raw=b'Name: torch\nVersion: 1.2.3+cpu\n'):
  meta=self.root/'torch.dist-info';f=self.file('torch.dist-info/METADATA',raw);r=self.file('torch.dist-info/RECORD',b'not parsed\n')
  return dict(name='torch',metadata_root=str(self.root),metadata_dir=str(meta),record_sha256=H(r.read_bytes()),record_bytes=r.stat().st_size,metadata_sha256=H(raw),metadata_bytes=len(raw))
 def test_exact_generated_metadata(self):
  r=self.request();r['distributions']=[self.dist()];p.validate_request(r)
  self.assertEqual(p.collect(r)['distributions'][0]['version'],'1.2.3+cpu')
 def test_empty_metadata_never_falls_back(self):
  r=self.request();r['distributions']=[self.dist(b'')];self.file('torch.dist-info/PKG-INFO',b'Name: torch\nVersion: UNPINNED_FALLBACK_CANARY\n')
  original=p.os.open;opened=[]
  def tracked(path,*a,**kw):opened.append(str(path));return original(path,*a,**kw)
  with patch.object(p.os,'open',side_effect=tracked):
   with self.assertRaises(ValueError):p.collect(r)
  self.assertFalse(any('PKG-INFO' in x for x in opened))
 def test_duplicate_missing_malformed_fields(self):
  for raw in (b'Name: torch\n',b'Version: 1\n',b'Name: torch\nName: torch\nVersion: 1\n',b'Name: torch\nVersion: 1\nVersion: 2\n',b'Name: torch\nVersion: \n',b'Name: torch\nVersion: @bad\n',b'Name: foreign\nVersion: 1\n'):
   with self.assertRaises(ValueError):p.metadata_fields(raw,'torch')
 def test_authenticated_metadata_no_reopen(self):
  r=self.request();d=self.dist();r['distributions']=[d];real=p.snapshot;calls=[]
  def hooked(path,*a,**kw):
   got=real(path,*a,**kw);calls.append(path)
   if path.endswith('/METADATA'):pathlib.Path(path).write_bytes(b'Name: torch\nVersion: MUTATED\n')
   return got
  with patch.object(p,'snapshot',side_effect=hooked):got=p.collect(r)
  self.assertEqual(got['distributions'][0]['version'],'1.2.3+cpu');self.assertEqual(got['distributions'][0]['metadata_sha256'],d['metadata_sha256']);self.assertEqual(sum(x.endswith('/METADATA') for x in calls),1)
 def test_leaf_symlink_before_open_no_target_read(self):
  allowed=self.file('allowed.py');target=self.file('unallowlisted.py',b'CANARY');original=p.os.open;swapped=False
  def swap(path,*a,**kw):
   nonlocal swapped
   if path=='allowed.py' and not swapped:allowed.unlink();allowed.symlink_to(target);swapped=True
   return original(path,*a,**kw)
  with patch.object(p.os,'open',side_effect=swap),patch.object(p.os,'read',side_effect=AssertionError('must not read target')):
   with self.assertRaises(OSError):p.snapshot(str(allowed),100)
 def test_ancestor_symlink_before_open_no_target_read(self):
  f=self.file('dir/allowed.py');elsewhere=self.root/'other';elsewhere.mkdir();(elsewhere/'allowed.py').write_bytes(b'CANARY');original=p.os.open;swapped=False
  def swap(path,*a,**kw):
   nonlocal swapped
   if path=='dir' and not swapped:(self.root/'dir').rename(self.root/'old');(self.root/'dir').symlink_to(elsewhere,target_is_directory=True);swapped=True
   return original(path,*a,**kw)
  with patch.object(p.os,'open',side_effect=swap),patch.object(p.os,'read',side_effect=AssertionError('must not read target')):
   with self.assertRaises(OSError):p.snapshot(str(f),100)
 def test_leaf_replacement_after_open_keeps_descriptor(self):
  f=self.file('allowed.py',b'original');target=self.file('target.py',b'CANARY');real=p.os.read;once=False
  def swap(fd,n):
   nonlocal once
   if not once:f.rename(self.root/'saved.py');f.symlink_to(target);once=True
   return real(fd,n)
  # Rename changes ctime of original descriptor, so either authenticated original
  # snapshot or fail-closed is safe; the replacement can never supply read bytes.
  observed=[]
  def read(fd,n):
   block=swap(fd,n);observed.append(block);return block
  with patch.object(p.os,'read',side_effect=read):
   try:raw,_,_=p.snapshot(str(f),100,8,H(b'original'));self.assertEqual(raw,b'original')
   except ValueError:pass
  self.assertNotIn(b'CANARY',observed)
 def test_growth_cap_approved_plus_one(self):
  f=self.file('grow.py',b'abc');real=p.os.read;once=False;requested=[]
  def grow(fd,n):
   nonlocal once
   requested.append(n)
   if not once:
    with f.open('ab') as stream:stream.write(b'EXCESS')
    once=True
   return real(fd,n)
  with patch.object(p.os,'read',side_effect=grow):
   with self.assertRaises(ValueError):p.snapshot(str(f),3,3,H(b'abc'))
  self.assertEqual(requested,[4])
 def test_oversize_rejected_before_read(self):
  f=self.file('large.py',b'abcd')
  with patch.object(p.os,'read',side_effect=AssertionError('oversize read')):
   with self.assertRaises(ValueError):p.snapshot(str(f),3)
 def test_fifo_refused_without_blocking(self):
  f=self.root/'fifo.py';os.mkfifo(f)
  with self.assertRaises(ValueError):p.snapshot(str(f),100)
 def test_dangling_symlink_not_absent(self):
  f=self.root/'dangling.py';f.symlink_to(self.root/'missing.py');r=self.request();r['files']=[dict(path=str(f),sha256='0'*64,bytes=0,kind='python_source')]
  with self.assertRaises(OSError):p.collect(r)
 def test_unknown_absent(self):
  r=self.request();r['distributions']=[self.dist()];(self.root/'torch.dist-info/RECORD').unlink()
  self.assertEqual(p.collect(r)['distributions'][0]['status'],'UNKNOWN_ABSENT')
 def test_controls_parse_hash_same_snapshot_after_path_mutation(self):
  for name in ('request.json','release.json'):
   raw=b'{"version":"original"}';f=self.file(name,raw);real=p.snapshot
   def mutate(path,*a,**kw):
    got=real(path,*a,**kw);pathlib.Path(path).write_bytes(b'{"version":"replaced"}');return got
   with patch.object(p,'snapshot',side_effect=mutate):obj,digest=p.control(str(f))
   self.assertEqual(obj['version'],'original');self.assertEqual(digest,H(raw))
 def test_controls_growth_refused(self):
  f=self.file('control.json',b'{}')
  with self.assertRaises(ValueError):p.snapshot(str(f),1)
 def test_same_inode_mutation_refused(self):
  f=self.file('source.py',b'abc');real=p.os.read;once=False
  def mutate(fd,n):
   nonlocal once
   block=real(fd,n)
   if not once:f.write_bytes(b'xyz');once=True
   return block
  with patch.object(p.os,'read',side_effect=mutate):
   with self.assertRaises(ValueError):p.snapshot(str(f),3,3,H(b'abc'))
 def test_no_fallback_import_or_unsafe_open(self):
  text=pathlib.Path(p.__file__).read_text();tree=ast.parse(text)
  names=[a.name for n in ast.walk(tree) if isinstance(n,ast.Import) for a in n.names]
  self.assertFalse(set(names)&{'importlib.metadata','torch','numpy','timm','subprocess','socket'})
  self.assertNotIn('read_text(',text);self.assertNotIn('rglob(',text)
 def test_request_data_duplicates_bounds(self):
  r=self.request();r['files']=[dict(path='/synthetic/file.npz',sha256='0'*64,bytes=1,kind='python_source')]
  with self.assertRaises(ValueError):p.validate_request(r)
  r['files'][0]['path']='/synthetic/file.py';r['files']*=2
  with self.assertRaises(ValueError):p.validate_request(r)
 def test_root_authorization_retains_all_scope_guards(self):
  r=self.request();r['interpreter']=str(self.root/'python');r['interpreter_sha256']='1'*64
  release=dict(decision='GO_SBMR512_BII_ENV_SOURCE_METADATA_V1R1',root_authorized=True,author='author',reviewer='other',request_sha256='2'*64,probe_sha256='3'*64,output=p.OUTPUT,automatic_retry=False,scientific_read='HOLD',gpu_authorized=False,independent_review_path=str(self.root/'review'),independent_review_sha256='1'*64)
  with patch.object(p,'snapshot',return_value=(b'','1'*64,0)),patch.object(p,'sha',return_value='1'*64),patch.object(p.os.path,'realpath',return_value=r['interpreter']):
   p.authorize(r,release,'2'*64,'3'*64)
   for key,value in [('root_authorized',False),('reviewer','author'),('scientific_read','GO'),('gpu_authorized',True),('automatic_retry',True),('request_sha256','4'*64),('output','/alternate')]:
    bad=dict(release);bad[key]=value
    with self.assertRaises(ValueError):p.authorize(r,bad,'2'*64,'3'*64)
 def test_create_only_and_exact_receipt_hash(self):
  fd=p.directory_fd(str(self.root))
  try:
   digest=p.put(fd,'generated.json',{'fixture':True});self.assertEqual(digest,H((self.root/'generated.json').read_bytes()))
   with self.assertRaises(FileExistsError):p.put(fd,'generated.json',{})
  finally:os.close(fd)
if __name__=='__main__':unittest.main(verbosity=2)
