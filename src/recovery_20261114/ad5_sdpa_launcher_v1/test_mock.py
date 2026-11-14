"""Generated-only branch tests: no Slurm/tmux/GPU commands are executed."""
import importlib.util,json,os,pathlib,subprocess,tempfile,unittest
from unittest import mock
HERE=pathlib.Path(__file__).resolve().parent

def mod(name):
 spec=importlib.util.spec_from_file_location('fixture_'+name,HERE/(name+'.py'));m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);return m

class Launch(unittest.TestCase):
 def test_one_shot_success_capacity_failure_timeout_and_exception(self):
  for rc,jid,boom in [(0,'123',False),(1,None,False),(124,'124',False),(1,'125',False),(125,None,True)]:
   with self.subTest(rc=rc,jid=jid,boom=boom),tempfile.TemporaryDirectory() as td:
    m=mod('launch');root=pathlib.Path(td);j=root/'journal';j.mkdir();(j/'ROOT_RELEASE.json').write_text('{}')
    calls=[]
    def execute(cmd,**kw):
     self.assertTrue((j/'CLAIM.json').exists());self.assertTrue((j/'INTENT.json').exists());calls.append((cmd,kw))
     self.assertIn('--pty',cmd);self.assertIn('--immediate=60',cmd);self.assertIn('--time=00:15:00',cmd)
     self.assertIn('--mem=120G',cmd);self.assertIn('--gres=gpu:hopper:1,storage:local:150G',cmd)
     self.assertNotIn('AD5_NG',kw['env']);self.assertNotIn('PYTHONPATH',kw['env'])
     if jid:(j/'NATIVE_JOB_ID.txt').write_text(jid+'\n')
     if boom:raise RuntimeError('generated launch error')
     return rc
    with mock.patch.object(m,'ROOT',root),mock.patch.object(m,'J',j),mock.patch.object(m,'SRC',root/'source'),mock.patch.object(m,'verify_release'),mock.patch.object(m.os,'isatty',return_value=True),mock.patch.dict(os.environ,{'TMUX_PANE':'%9','AD5_NG':'8','PYTHONPATH':'BAD'}),mock.patch.object(m.subprocess,'check_output',return_value='0\n'),mock.patch.object(m.subprocess,'run'),mock.patch.object(m.subprocess,'call',side_effect=execute):
     self.assertEqual(m.main(),rc)
     with self.assertRaises(FileExistsError):m.main()
    self.assertEqual(len(calls),1);terminal=json.loads((j/'TERMINAL.json').read_text());self.assertEqual(terminal['native_job_id'],jid)
    self.assertEqual(terminal['operator_verdict'],'NOT_INFERRED_FROM_SRUN_OR_WORKER_EXIT')
 def test_nonpty_refuses_before_claim(self):
  m=mod('launch')
  with mock.patch.object(m.os,'isatty',return_value=False),mock.patch.object(m,'verify_release') as v:
   with self.assertRaises(AssertionError):m.main()
   v.assert_not_called()
 def test_node_retains_backend_failure_even_workerzero(self):
  for exits in [('0','0'),('1','0'),('1','2'),(None,None)]:
   with self.subTest(exits=exits),tempfile.TemporaryDirectory() as td:
    m=mod('node');root=pathlib.Path(td);j=root/'journal';j.mkdir();(j/'NATIVE_JOB_ID.txt').write_text('321\n')
    worker=root/'ad5_sdpa_probe_v1/worker.sh';worker.parent.mkdir();worker.write_text('generated')
    keep=root/'logs/keep/ad5_sdpa_probe_v1_20261114';keep.mkdir(parents=True)
    for mode,status in zip(('default','math'),exits):
     if status is not None:(keep/(mode+'_exit.txt')).write_text(status+'\n')
    env={'SLURM_JOB_ID':'321','SLURM_JOB_PARTITION':'lem-gpu-interactive','SLURM_CPUS_PER_TASK':'8','CUDA_VISIBLE_DEVICES':'0','TMPDIR':'/generated','AD5_NG':'8','PYTHONPATH':'BAD'}
    def worker_call(cmd,**kw):self.assertNotIn('AD5_NG',kw['env']);self.assertNotIn('PYTHONPATH',kw['env']);return 0
    with mock.patch.object(m,'ROOT',root),mock.patch.object(m,'J',j),mock.patch.dict(os.environ,env,clear=True),mock.patch.object(m.os,'isatty',return_value=True),mock.patch.object(m.hashlib,'sha256') as h,mock.patch.object(m.subprocess,'call',side_effect=worker_call):
     h.return_value.hexdigest.return_value='7c3b602bdf091bf4d593ed5d5c0c5874ecea10723538b4feb32f4d2df6b3a76d';self.assertEqual(m.main(),0)
    out=json.loads((j/'NODE_EXIT.json').read_text());self.assertEqual(list(out['backend_exit_text'].values()),list(exits));self.assertEqual(out['operator_verdict'],'NOT_INFERRED_FROM_WORKER_EXIT')
 def test_allocation_id_survives_python_start_failure(self):
  with tempfile.TemporaryDirectory() as td:
   root=pathlib.Path(td);j=root/'journal';j.mkdir();bin=root/'bin';bin.mkdir()
   p=bin/'python3';p.write_text('#!/bin/sh\nexit 73\n');p.chmod(0o755)
   text=(HERE/'allocation_entry.sh').read_text().replace('/lustre/pd03/hpc-narolski-1790461090/smad-next/AD5/dispatch/ad5_sdpa_launcher_v1_20261114',str(j))
   script=root/'generated_entry.sh';script.write_text(text)
   env=dict(os.environ,SLURM_JOB_ID='987',PATH=str(bin)+':/usr/bin:/bin')
   run=subprocess.run(['/bin/bash',str(script)],env=env,capture_output=True,text=True)
   self.assertEqual(run.returncode,73);self.assertEqual((j/'NATIVE_JOB_ID.txt').read_text(),'987\n')
   again=subprocess.run(['/bin/bash',str(script)],env=env,capture_output=True,text=True);self.assertNotEqual(again.returncode,0)
if __name__=='__main__':unittest.main()
