import hashlib,pathlib,tempfile,unittest
from node_driver import verify_worker
HERE=pathlib.Path(__file__).parent
class Control(unittest.TestCase):
 def test_staged_manifest_fixture(self):
  with tempfile.TemporaryDirectory() as d:
   p=pathlib.Path(d)
   names=['produce.py','engine.py','backend.py','design.py','AUTHORITY.json']
   for n in names:(p/n).write_bytes(b'generated fixture')
   raw=''.join(hashlib.sha256((p/n).read_bytes()).hexdigest()+'  '+n+'\n' for n in names)
   (p/'SHA256SUMS').write_text(raw);h=hashlib.sha256(raw.encode()).hexdigest()
   verify_worker(p,h)
   (p/'engine.py').write_bytes(b'tampered generated fixture')
   with self.assertRaises(ValueError):verify_worker(p,h)
 def test_preallocation_shell_and_child_order(self):
  launch=(HERE/'launch.py').read_text();entry=(HERE/'allocation_entry.sh').read_text();node=(HERE/'node_driver.py').read_text()
  self.assertLess(launch.index("put('CLAIM.json'"),launch.index('subprocess.call(cmd'))
  self.assertLess(launch.index("put('INTENT.json'"),launch.index('subprocess.call(cmd'))
  self.assertLess(entry.index('NATIVE_JOB_ID.txt'),entry.index('exec '))
  self.assertLess(node.index("verify_worker(c['worker_dir']"),node.index('p=subprocess.run('))
  for text in ('--immediate=60','gpu:hopper:1,storage:local:8G','1200s','terminal.log','pipe-pane'):self.assertIn(text,launch)
  self.assertIn("'-s','-B'",node);self.assertIn('-I -S -B',entry)
 def test_parent_operational_worker_still_exact(self):
  w=HERE/'worker_wcss_v1'
  for line in (w/'SHA256SUMS').read_text().splitlines():
   h,n=line.split('  ',1);self.assertEqual(hashlib.sha256((w/n).read_bytes()).hexdigest(),h)
if __name__=='__main__':unittest.main()
