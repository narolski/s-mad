"""AST, generated technical records and mocked runtime/launch only; no GPU/model/data."""
import ast
import contextlib
import copy
import importlib.util
import json
import os
import pathlib
import subprocess
import sys
import tempfile
import types
import unittest
from unittest import mock
sys.path.insert(0,str(pathlib.Path(__file__).resolve().parent))
import contract
import patch
HERE=pathlib.Path(__file__).resolve().parent
ORIGINAL=HERE/'grounding/build/madation_src/src/training/trainer.py'


def module(name):
 spec=importlib.util.spec_from_file_location('generated_'+name,HERE/(name+'.py'));m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);return m


class PatchAndGrounding(unittest.TestCase):
 def test_exact_original_pin_patch_compile_and_wrong_source_refused(self):
  raw=ORIGINAL.read_bytes();changed=patch.patched(raw);ast.parse(changed)
  with self.assertRaises(AssertionError):patch.patched(raw+b'\n')
  with self.assertRaises(AssertionError):patch.patched(changed)
 def test_optimizer_constructors_and_math_scope_exact(self):
  def method(raw):
   tree=ast.parse(raw);return next(n for n in ast.walk(tree) if isinstance(n,ast.FunctionDef) and n.name=='MAD_training')
  old=method(ORIGINAL.read_bytes());new=method(patch.patched(ORIGINAL.read_bytes()))
  for name in ('optimizer_model','optimizer_header'):
   take=lambda fn:ast.dump(next(n.value for n in ast.walk(fn) if isinstance(n,ast.Assign) and any(isinstance(t,ast.Name) and t.id==name for t in n.targets)))
   self.assertEqual(take(old),take(new))
  contexts=[n for n in ast.walk(new) if isinstance(n,ast.With)];self.assertEqual(len(contexts),1)
  call=contexts[0].items[0].context_expr
  self.assertEqual({x.arg:ast.literal_eval(x.value) for x in call.keywords},{'enable_flash':False,'enable_math':True,'enable_mem_efficient':False})
  segment=ast.unparse(contexts[0]);self.assertIn('encode_image(images)',segment);self.assertIn('loss_image.backward()',segment)
  self.assertEqual(sum(isinstance(n,ast.Call) and isinstance(n.func,ast.Attribute) and n.func.attr=='step' and isinstance(n.func.value,ast.Name) and n.func.value.id.startswith('optimizer_') for n in ast.walk(new)),2)
 def test_patched_method_exact_one_backward_clip_two_original_optimizers_then_return(self):
  tree=ast.parse(patch.patched(ORIGINAL.read_bytes()));fn=next(n for n in ast.walk(tree) if isinstance(n,ast.FunctionDef) and n.name=='MAD_training')
  events=[];inside={'math':False}
  class Tensor:
   def cuda(self,*a,**k):return self
   def backward(self):self_check();events.append('backward')
  def self_check():self.assertTrue(inside['math'])
  class Ctx:
   def __enter__(self):inside['math']=True
   def __exit__(self,*a):inside['math']=False
  class Model:
   def __init__(self,name):self.name=name;self.module=self
   def parameters(self):return [self.name]
   def encode_image(self,x):self_check();events.append('forward');return Tensor()
   def __call__(self,*a):self_check();events.append('header');return None,Tensor()
  class Opt:
   def __init__(self,*a,**kw):events.append('AdamW')
   def step(self):events.append('step')
  class Probe:
   def __init__(self,*a):pass
   def epoch(self,e):assert e==0
   def inputs(self,*a):pass
   def backend(self):self_check()
   def loss(self,*a):pass
   def grads(self):events.append('grads')
   def finish(self,*a):events.append('finish')
   def failed(self,e):raise AssertionError(str(e))
  fake=types.SimpleNamespace(optim=types.SimpleNamespace(AdamW=Opt),backends=types.SimpleNamespace(cuda=types.SimpleNamespace(sdp_kernel=lambda **kw:Ctx())),cuda=types.SimpleNamespace(synchronize=lambda:None))
  def clip(*a,**kw):events.append('clip');return 1.
  config=types.SimpleNamespace(**dict(lr_model=1e-5,lr_header=1e-4,weight_decay=.05,num_epoch=3,scheduler_type='cosine',warmup=True,num_warmup_epochs=5,T_0=5,T_mult=2,lr_func_drop=[22,30,40],max_norm=5))
  trainer=types.SimpleNamespace(model=Model('model'),header=Model('header'),config=config,start_epoch=0,global_step=0,rank=0,
   train_sampler=types.SimpleNamespace(set_epoch=lambda x:None),dataloader=[(Tensor(),Tensor()),(Tensor(),Tensor())])
  scope={'torch':fake,'F':types.SimpleNamespace(normalize=lambda x:x),'clip_grad_norm_':clip,'get_scheduler':lambda **kw:object()}
  exec(compile(ast.Module(body=[fn],type_ignores=[]),'generated_method','exec'),scope)
  with mock.patch.dict(sys.modules,{'ad5_math_step_runtime':types.SimpleNamespace(Probe=Probe)}):scope['MAD_training'](trainer)
  self.assertEqual(events,['AdamW','AdamW','forward','header','backward','grads','clip','clip','step','step','finish'])
  self.assertEqual(trainer.global_step,1)


class TechnicalGates(unittest.TestCase):
 def grad(self):return {g:{n:{'present':True,'finite':True,'norm':0. if n.endswith('_A') else 1.} for n in names} for g,names in contract.expected_names().items()}
 def update(self):return {g:{n:{'finite':True,'changed':not n.endswith('_A'),'optimizer_step':1} for n in names} for g,names in contract.expected_names().items()}
 def test_source_expected_sets_and_first_A_zero_legitimate(self):
  self.assertEqual(len(contract.expected_names()['model']),48);self.assertEqual(len(contract.expected_names()['header']),2)
  self.assertFalse(any('text' in n for n in contract.expected_names()['model']));contract.gradients(self.grad());contract.updates(self.update())
 def test_missing_nonfinite_allzero_gradients_fail(self):
  for kind in ('missing','nan','allzero'):
   r=self.grad();name=next(iter(r['model']))
   if kind=='missing':r['model'][name]['present']=False
   elif kind=='nan':r['model'][name]['finite']=False
   else:
    for v in r['model'].values():v['norm']=0
   with self.assertRaises(AssertionError):contract.gradients(r)
 def test_nonchange_nonfinite_or_multiple_updates_fail(self):
  for kind in ('unchanged','nonfinite','twosteps'):
   r=self.update();name=next(iter(r['model']))
   if kind=='unchanged':
    for v in r['model'].values():v['changed']=False
   elif kind=='nonfinite':r['model'][name]['finite']=False
   else:r['model'][name]['optimizer_step']=2
   with self.assertRaises(AssertionError):contract.updates(r)
 def test_batch256_order_and_no_microbatch(self):
  ii=list(range(256));contract.batch_order(ii,ii.copy())
  with self.assertRaises(AssertionError):contract.batch_order(ii,ii[::-1])
  with self.assertRaises(AssertionError):contract.batch_order(ii,ii[:128])


class Launcher(unittest.TestCase):
 def test_realpty_claim_precedes_single_srun_no_retry_all_terminal_branches(self):
  for rc,jid,boom in [(0,'123',False),(1,None,False),(124,'124',False),(1,'125',False),(125,None,True)]:
   with self.subTest(rc=rc),tempfile.TemporaryDirectory() as td:
    m=module('launch');root=pathlib.Path(td);j=root/'journal';j.mkdir();(j/'ROOT_RELEASE.json').write_text('{}');calls=[]
    def run(cmd,**kw):
     self.assertTrue((j/'CLAIM.json').exists());self.assertIn('--pty',cmd);self.assertIn('--time=00:15:00',cmd);self.assertIn('--mem=120G',cmd);self.assertIn('--gres=gpu:hopper:1,storage:local:150G',cmd)
     self.assertNotIn('AD5_NG',kw['env']);self.assertNotIn('PYTHONPATH',kw['env']);calls.append(cmd)
     if jid:(j/'NATIVE_JOB_ID.txt').write_text(jid+'\n')
     if boom:raise RuntimeError('generated')
     return rc
    with mock.patch.object(m,'ROOT',root),mock.patch.object(m,'J',j),mock.patch.object(m,'SRC',root/'source'),mock.patch.object(m,'verify_release'),mock.patch.object(m.os,'isatty',return_value=True),mock.patch.dict(os.environ,{'TMUX_PANE':'%9','AD5_NG':'8','PYTHONPATH':'BAD'}),mock.patch.object(m.subprocess,'check_output',return_value='0\n'),mock.patch.object(m.subprocess,'run'),mock.patch.object(m.subprocess,'call',side_effect=run):
     self.assertEqual(m.main(),rc)
     with self.assertRaises(FileExistsError):m.main()
    self.assertEqual(len(calls),1);self.assertEqual(json.loads((j/'TERMINAL.json').read_text())['native_job_id'],jid)
 def test_nonpty_refuses_without_claim(self):
  m=module('launch')
  with mock.patch.object(m.os,'isatty',return_value=False),mock.patch.object(m,'verify_release') as v:
   with self.assertRaises(AssertionError):m.main()
   v.assert_not_called()
 def test_native_id_survives_python_startup_failure(self):
  with tempfile.TemporaryDirectory() as td:
   root=pathlib.Path(td);j=root/'journal';j.mkdir();b=root/'bin';b.mkdir();py=b/'python3';py.write_text('#!/bin/sh\nexit 73\n');py.chmod(0o755)
   text=(HERE/'allocation_entry.sh').read_text().replace('/lustre/pd03/hpc-narolski-1790461090/smad-next/AD5/dispatch/ad5_real_math_step_v1_20261114',str(j))
   f=root/'entry.sh';f.write_text(text);env=dict(os.environ,SLURM_JOB_ID='987',PATH=str(b)+':/usr/bin:/bin')
   run=subprocess.run(['/bin/bash',str(f)],env=env,capture_output=True,text=True);self.assertEqual(run.returncode,73);self.assertEqual((j/'NATIVE_JOB_ID.txt').read_text(),'987\n')
   self.assertNotEqual(subprocess.run(['/bin/bash',str(f)],env=env,capture_output=True).returncode,0)
 def test_node_sanitizes_env_retains_missing_malformed_failure_status(self):
  for content,worker_rc,expected in [(json.dumps({'status':'ONE_REAL_EFFECTIVE_STEP_MATH_ONLY_COMPLETE'}),0,0),(None,0,94),('{',0,94),(json.dumps({'status':'ONE_REAL_EFFECTIVE_STEP_MATH_ONLY_COMPLETE'}),7,7)]:
   with self.subTest(content=content),tempfile.TemporaryDirectory() as td:
    m=module('node');root=pathlib.Path(td);j=root/'journal';j.mkdir();(j/'NATIVE_JOB_ID.txt').write_text('321\n')
    source=root/'ad5_real_math_step_v1';source.mkdir();(source/'verify.py').write_text('def release(): return {}\n');(source/'worker.sh').write_text('# generated')
    keep=root/'logs/keep/ad5_real_math_step_v1_20261114';keep.mkdir(parents=True)
    if content is not None:(keep/'STEP_RESULT.json').write_text(content)
    env={'SLURM_JOB_ID':'321','SLURM_JOB_PARTITION':'lem-gpu-interactive','SLURM_CPUS_PER_TASK':'8','SLURM_MEM_PER_NODE':'122880','CUDA_VISIBLE_DEVICES':'0','TMPDIR':'/mnt/lscratch/generated','PYTHONPATH':'BAD','AD5_NG':'8'}
    def execute(cmd,**kw):self.assertNotIn('PYTHONPATH',kw['env']);self.assertNotIn('AD5_NG',kw['env']);return worker_rc
    with mock.patch.object(m,'ROOT',root),mock.patch.object(m,'J',j),mock.patch.dict(os.environ,env,clear=True),mock.patch.object(m.os,'isatty',return_value=True),mock.patch.object(m.subprocess,'call',side_effect=execute):self.assertEqual(m.main(),expected)
    out=json.loads((j/'NODE_EXIT.json').read_text());self.assertEqual(out['worker_exit'],worker_rc);self.assertEqual(out['node_exit'],expected)
 def test_release_wrongscope_and_unsigned_refused(self):
  m=module('verify')
  for decision in ('GO_ONE_NEW_SYNTHETIC_SDPA_INTERACTIVE_V1','PROPOSED_'+m.DECISION):
   with tempfile.TemporaryDirectory() as td:
    j=pathlib.Path(td);(j/'ROOT_RELEASE.json').write_text(json.dumps({'decision':decision}))
    with mock.patch.object(m,'JOURNAL',j),self.assertRaises(AssertionError):m.release()


if __name__=='__main__':unittest.main()
