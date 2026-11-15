"""Real CPU child failures/TERM/KILL exercise production supervisor and fsynced put."""
import ast,json,os,pathlib,sys,tempfile,time,unittest
import supervise
HERE=pathlib.Path(__file__).resolve().parent
CHILD=r"""
import ast,json,os,pathlib,signal,sys,time
base=pathlib.Path(sys.argv[1]);keep=pathlib.Path(sys.argv[2]);local=pathlib.Path(sys.argv[3]);mode=sys.argv[4]
# Execute the exact production observer put() without importing torch.
tree=ast.parse(base.read_text());fn=next(n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name=='put')
exec(compile(ast.Module(body=[fn],type_ignores=[]),'actual_put','exec'),globals())
put(keep/'technical/COMPLETED_STEP.json',{'step':1,'finite':True})
local.mkdir();(local/'training.log').write_text('generated original log\\n');(local/'3_header.pth').write_bytes(b'generated fixture checkpoint, not a model')
print('GENERATED_CHILD_STARTED',flush=True)
if mode=='fail':sys.exit(7)
put(keep/'technical/MULTI_RESULT.json',{'status':'THIRTY_SIX_REAL_MATH_UPDATES_AND_CHECKPOINT_ROUNDTRIP_COMPLETE','effective_batches':36})
if mode=='term':
 signal.signal(signal.SIGTERM,lambda *a:sys.exit(23))
else:signal.signal(signal.SIGTERM,signal.SIG_IGN)
while True:time.sleep(.02)
"""
class Retention(unittest.TestCase):
 def run_child(self,mode):
  with tempfile.TemporaryDirectory() as td:
   p=pathlib.Path(td);keep=p/'durable';keep.mkdir();(keep/'technical').mkdir();(keep/'original_run').mkdir();local=p/'node_run'
   t=time.monotonic()
   rc=supervise.run(keep,local,[sys.executable,'-u','-c',CHILD,str(HERE/'base_runtime.py'),str(keep),str(local),mode],time.time(),max_seconds=.6,term_grace=.2,collection_seconds=1,echo=False)
   self.assertLess(time.monotonic()-t,4)
   self.assertTrue(json.loads((keep/'technical/COMPLETED_STEP.json').read_text())['finite'])
   self.assertIn(b'GENERATED_CHILD_STARTED',(keep/'technical/train_stdout.log').read_bytes())
   self.assertEqual((keep/'original_run/3_header.pth').read_bytes(),b'generated fixture checkpoint, not a model')
   status=json.loads((keep/'SUPERVISOR_EXIT.json').read_text());self.assertFalse(status['eligible_for_technical_review']);self.assertEqual(status['status'],'INCOMPLETE_OR_FAILED')
   self.assertFalse(status['automatic_retry'])
   # Exclusive control receipt makes a second supervisor launch fail before spawning child.
   with self.assertRaises(FileExistsError):supervise.run(keep,local,['not-a-real-command'],time.time(),.1,.1,.1,False)
   return rc,status
 def test_real_child_failure_retains_completed_receipt_stdout_and_artifacts(self):
  rc,s=self.run_child('fail');self.assertEqual(s['child_exit'],7);self.assertNotEqual(rc,0)
 def test_real_TERM_partial_success_file_cannot_override_timeout(self):
  rc,s=self.run_child('term');self.assertEqual(rc,124);self.assertTrue(s['term_sent']);self.assertFalse(s['kill_sent']);self.assertEqual(s['child_exit'],23)
 def test_real_KILL_ignoring_TERM_retains_completed_evidence(self):
  rc,s=self.run_child('kill');self.assertEqual(rc,124);self.assertTrue(s['term_sent']);self.assertTrue(s['kill_sent']);self.assertEqual(s['child_exit'],-9)
 def test_only_allowed_original_artifact_snapshots(self):
  with tempfile.TemporaryDirectory() as td:
   p=pathlib.Path(td);local=p/'local';local.mkdir();dest=p/'dest';dest.mkdir()
   (local/'unregistered_checkpoint.pth').write_bytes(b'not copied');(local/'scores.npz').write_bytes(b'not copied')
   (local/'training.log').write_text('generated');(local/'image.png').symlink_to(local/'training.log')
   rows=supervise.mirror(local,dest,time.monotonic()+1)
   self.assertEqual([r['path'] for r in rows],['training.log']);self.assertFalse((dest/'scores.npz').exists())
if __name__=='__main__':unittest.main()
