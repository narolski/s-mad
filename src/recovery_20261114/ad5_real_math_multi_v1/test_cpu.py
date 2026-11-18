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


class Source(unittest.TestCase):
 def test_original_pin_and_wrongsource(self):
  raw=ORIGINAL.read_bytes();ast.parse(patch.patched(raw))
  for bad in (raw+b"\\n",patch.patched(raw)):
   with self.assertRaises(AssertionError):patch.patched(bad)
 def test_restored_original_ast_except_math_and_observation(self):
  def method(raw):return next(n for n in ast.walk(ast.parse(raw)) if isinstance(n,ast.FunctionDef) and n.name=="MAD_training")
  a=method(ORIGINAL.read_bytes());b=method(patch.patched(ORIGINAL.read_bytes()))
  class Strip(ast.NodeTransformer):
   def visit_ImportFrom(self,n):return None if n.module=="ad5_math_multi_runtime" else n
   def visit_Assign(self,n):
    if any(isinstance(t,ast.Name) and t.id=="probe" for t in n.targets):return None
    if any(isinstance(t,ast.Name) and t.id in ("model_preclip_norm","header_preclip_norm") for t in n.targets):return ast.Expr(value=n.value)
    return self.generic_visit(n)
   def visit_Expr(self,n):
    if isinstance(n.value,ast.Call) and isinstance(n.value.func,ast.Attribute) and isinstance(n.value.func.value,ast.Name) and n.value.func.value.id=="probe":return None
    return self.generic_visit(n)
   def visit_With(self,n):
    c=n.items[0].context_expr;assert ast.unparse(c.func)=="torch.backends.cuda.sdp_kernel"
    assert {v.arg:ast.literal_eval(v.value) for v in c.keywords}==dict(enable_flash=False,enable_math=True,enable_mem_efficient=False)
    return [x for v in n.body if (x:=self.visit(v)) is not None]
  self.assertEqual(ast.dump(Strip().visit(copy.deepcopy(b))),ast.dump(a))
  self.assertFalse(any(isinstance(x,ast.Return) for x in ast.walk(b)))
 def test_progression36_and_zeroA_accepted(self):
  for step in (1,2,36):
   r={g:{n:dict(finite=True,changed=not n.endswith("_A"),optimizer_step=step) for n in ns} for g,ns in contract.expected_names().items()}
   contract.updates(r,step)
   with self.assertRaises(AssertionError):contract.updates(r,step+1)
  g={k:{n:dict(present=True,finite=True,norm=0. if n.endswith("_A") else 1.) for n in ns} for k,ns in contract.expected_names().items()}
  contract.gradients(g);g["header"]["linear.bias"]["finite"]=False
  with self.assertRaises(AssertionError):contract.gradients(g)
 def test_checkpoint_scope_and_byte_not_numeric_equality(self):
  s=(HERE/"runtime.py").read_text()
  self.assertIn('torch.load(p,map_location="cpu",weights_only=True)',s)
  self.assertIn('m.load_state_dict(loaded[k],strict=True)',s);self.assertIn('b1==b2',s)
  self.assertIn('self.last_images',s);self.assertNotIn("test_dataloader",s)
  self.assertLess(s.index('self.t.model.train();self.t.header.train()'),s.index('m.load_state_dict'))
 def test_mock_full_original36_lifecycle(self):
  events=[];active={"math":False}
  class T:
   def cuda(self,*a,**k):return self
   def backward(self):assert active["math"];events.append("backward")
   def item(self):return .125
  class Ctx:
   def __enter__(self):active["math"]=True
   def __exit__(self,*a):active["math"]=False
  class Model:
   def __init__(self):self.module=self;self.visual=self
   def parameters(self):return []
   def encode_image(self,x):assert active["math"];return T()
   def __call__(self,*a):assert active["math"];return None,T()
  class Opt:
   def __init__(self,*a,**k):events.append("construct")
   def step(self):events.append("update")
   def zero_grad(self):events.append("zero")
  class Sched:
   def step(self):events.append("schedule")
   def get_last_lr(self):return [1e-5]
  class Probe:
   def __init__(self,*a):pass
   def epoch(self,e):pass
   def inputs(self,*a):pass
   def backend(self):assert active["math"]
   def loss(self,*a):pass
   def grads(self):pass
   def finish(self,*a):events.append("finish")
   def saved(self,e):events.append(("saved",e))
   def done(self):events.append("done")
  fake=types.SimpleNamespace(optim=types.SimpleNamespace(AdamW=Opt),backends=types.SimpleNamespace(cuda=types.SimpleNamespace(sdp_kernel=lambda **kw:Ctx())))
  c=types.SimpleNamespace(**dict(lr_model=1e-5,lr_header=1e-4,weight_decay=.05,num_epoch=3,scheduler_type="cosine",warmup=True,num_warmup_epochs=5,T_0=5,T_mult=2,lr_func_drop=[22,30,40],max_norm=5))
  t=types.SimpleNamespace(model=Model(),header=Model(),config=c,start_epoch=0,global_step=0,rank=0,train_sampler=types.SimpleNamespace(set_epoch=lambda e:None),dataloader=[(T(),T()) for _ in range(12)],loss_log=types.SimpleNamespace(update=lambda *a:events.append("losslog")),tensorboard_callback=types.SimpleNamespace(log_info=lambda **kw:events.append("tensorboard"),close=lambda:events.append("close")),callback_logging=lambda *a:events.append("logging"),callback_save_model=lambda e,*a:events.append(("save",e)))
  scope={"torch":fake,"F":types.SimpleNamespace(normalize=lambda x:x),"clip_grad_norm_":lambda *a,**k:events.append("clip") or 1.,"get_scheduler":lambda **kw:Sched()}
  fn=next(n for n in ast.walk(ast.parse(patch.patched(ORIGINAL.read_bytes()))) if isinstance(n,ast.FunctionDef) and n.name=="MAD_training")
  exec(compile(ast.Module(body=[fn],type_ignores=[]),"generated","exec"),scope)
  with mock.patch.dict(sys.modules,{"ad5_math_multi_runtime":types.SimpleNamespace(MultiProbe=Probe)}):scope["MAD_training"](t)
  self.assertEqual(t.global_step,36)
  for name,n in [("construct",2),("backward",36),("update",72),("zero",72),("schedule",6),("logging",36),("tensorboard",36),("close",1),("done",1)]:self.assertEqual(events.count(name),n,name)
  for e in range(3):self.assertLess(events.index(("save",e)),events.index(("saved",e)))
  self.assertEqual(events[-2:],["close","done"])

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
   text=(HERE/'allocation_entry.sh').read_text().replace('/lustre/pd03/hpc-narolski-1790461090/smad-next/AD5/dispatch/ad5_real_math_multi_v1_20261114',str(j))
   f=root/'entry.sh';f.write_text(text);env=dict(os.environ,SLURM_JOB_ID='987',PATH=str(b)+':/usr/bin:/bin')
   run=subprocess.run(['/bin/bash',str(f)],env=env,capture_output=True,text=True);self.assertEqual(run.returncode,73);self.assertEqual((j/'NATIVE_JOB_ID.txt').read_text(),'987\n')
   self.assertNotEqual(subprocess.run(['/bin/bash',str(f)],env=env,capture_output=True).returncode,0)
 def test_node_sanitizes_env_retains_missing_malformed_failure_status(self):
  for content,worker_rc,expected in [(json.dumps({'status':'THIRTY_SIX_REAL_MATH_UPDATES_AND_CHECKPOINT_ROUNDTRIP_COMPLETE'}),0,0),(None,0,94),('{',0,94),(json.dumps({'status':'THIRTY_SIX_REAL_MATH_UPDATES_AND_CHECKPOINT_ROUNDTRIP_COMPLETE'}),7,7)]:
   with self.subTest(content=content),tempfile.TemporaryDirectory() as td:
    m=module('node');root=pathlib.Path(td);j=root/'journal';j.mkdir();(j/'NATIVE_JOB_ID.txt').write_text('321\n')
    source=root/'ad5_real_math_multi_v1';source.mkdir();(source/'verify.py').write_text('def release(): return {}\n');(source/'worker.sh').write_text('# generated')
    keep=root/'logs/keep/ad5_real_math_multi_v1_20261114';keep.mkdir(parents=True);(keep/'technical').mkdir()
    if content is not None:(keep/'technical/MULTI_RESULT.json').write_text(content)
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
