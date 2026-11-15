import hashlib,os,pathlib,tempfile,unittest
from unittest.mock import patch
import probe
HERE=pathlib.Path(__file__).parent
class Boundaries(unittest.TestCase):
 def setUp(self):
  self.tmp=tempfile.TemporaryDirectory(dir=HERE);self.base=pathlib.Path(self.tmp.name);self.allowed=self.base/'allowed';self.outside=self.base/'outside';self.allowed.mkdir();self.outside.mkdir();self.patch=patch.object(probe,'ALLOWED_ROOTS',(str(self.allowed),));self.patch.start()
 def tearDown(self):self.patch.stop();self.tmp.cleanup()
 def mapped(self,p):
  s=p.stat();return dict(path=str(p),device=s.st_dev,inode=s.st_ino)
 def fixture(self,p,data=b'ELFGENERATED_CANARY'):
  p.write_bytes(data);return self.mapped(p)
 def test_reproduced_outside_ancestor_and_parent_traversal(self):
  p=self.outside/'canary.so';m=self.fixture(p);jump=self.allowed/'jump';jump.symlink_to(self.outside,target_is_directory=True)
  for path in (str(jump/'canary.so'),str(self.allowed)+'/../outside/canary.so'):
   with self.subTest(path=path),self.assertRaises((ValueError,OSError)):
    probe.file_identity(dict(m,path=path),True,4096)
 def test_device_inode_mismatch_and_replacement(self):
  p=self.allowed/'f.so';m=self.fixture(p)
  for key in ('device','inode'):
   with self.subTest(key=key),self.assertRaises(ValueError):probe.file_identity(dict(m,**{key:m[key]+1}),True,4096)
  q=self.allowed/'replacement.so';self.fixture(q,b'ELFREPLACEMENT');os.replace(q,p)
  with self.assertRaises(ValueError):probe.file_identity(m,True,4096)
 def test_ancestor_replaced_before_walk_is_rejected(self):
  a=self.allowed/'a';a.mkdir();m=self.fixture(a/'f.so');self.fixture(self.outside/'f.so',b'ELFOUTSIDE');a.rename(self.allowed/'old');a.symlink_to(self.outside,target_is_directory=True)
  with self.assertRaises(OSError):probe.file_identity(m,True,4096)
 def test_ancestor_replaced_after_open_uses_confined_descriptor(self):
  a=self.allowed/'a';a.mkdir();data=b'ELFINSIDE';m=self.fixture(a/'f.so',data);self.fixture(self.outside/'f.so',b'ELFOUTSIDE');original=probe.os.open;swapped=[]
  def race(path,flags,*args,**kwargs):
   if path=='f.so' and not swapped:
    a.rename(self.allowed/'old');a.symlink_to(self.outside,target_is_directory=True);swapped.append(True)
   return original(path,flags,*args,**kwargs)
  with patch.object(probe.os,'open',side_effect=race):r,n=probe.file_identity(m,True,4096)
  self.assertEqual(r['sha256'],hashlib.sha256(data).hexdigest());self.assertTrue(swapped)
 def test_snapshot_growth_read_bound_and_size_cap(self):
  p=self.allowed/'f.so';m=self.fixture(p);original=probe.os.read;counts=[];grown=[];size=p.stat().st_size
  def grow(fd,n):
   if not grown:
    with p.open('ab') as f:f.write(b'GROWTH')
    grown.append(True)
   b=original(fd,n);counts.append(len(b));return b
  with patch.object(probe.os,'read',side_effect=grow),self.assertRaises(ValueError):probe.file_identity(m,True,4096)
  self.assertLessEqual(sum(counts),size+1)
  with patch.object(probe,'MAX_LIBRARY',1),self.assertRaises(ValueError):probe.file_identity(self.mapped(p),True,4096)
 def test_exact_literal_alias_only(self):
  real=self.allowed/'canonical';real.mkdir();m=self.fixture(real/'f.so');alias=self.allowed/'alias';alias.symlink_to('canonical',target_is_directory=True);m['path']=str(alias/'f.so')
  with self.assertRaises(OSError):probe.file_identity(m,True,4096)
  a=dict(path=str(alias),target='canonical',canonical=str(real));r,n=probe.file_identity(m,True,4096,[a]);self.assertEqual(r['canonical_path'],str(real/'f.so'))
  a['target']='different'
  with self.assertRaises(ValueError):probe.file_identity(m,True,4096,[a])
if __name__=='__main__':unittest.main()
