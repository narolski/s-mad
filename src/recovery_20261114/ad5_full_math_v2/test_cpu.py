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
   def visit_ImportFrom(self,n):return None if n.module=="ad5_full_math_runtime" else n
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
 def test_progression6200_and_zeroA_accepted(self):
  for step in (1,2,6200):
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
 def test_mock_full_original6200_lifecycle(self):
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
  c=types.SimpleNamespace(**dict(lr_model=1e-5,lr_header=1e-4,weight_decay=.05,num_epoch=40,scheduler_type="cosine",warmup=True,num_warmup_epochs=5,T_0=5,T_mult=2,lr_func_drop=[22,30,40],max_norm=5,test_data=[]))
  t=types.SimpleNamespace(model=Model(),header=Model(),config=c,start_epoch=0,global_step=0,rank=0,train_sampler=types.SimpleNamespace(set_epoch=lambda e:None),dataloader=[(T(),T()) for _ in range(155)],loss_log=types.SimpleNamespace(update=lambda *a:events.append("losslog")),tensorboard_callback=types.SimpleNamespace(log_info=lambda **kw:events.append("tensorboard"),close=lambda:events.append("close")),callback_logging=lambda *a:events.append("logging"),callback_save_model=lambda e,*a:events.append(("save",e)))
  t.test_model=lambda epoch,data: events.append(("empty_test",epoch)) or []
  scope={"torch":fake,"F":types.SimpleNamespace(normalize=lambda x:x),"clip_grad_norm_":lambda *a,**k:events.append("clip") or 1.,"get_scheduler":lambda **kw:Sched()}
  fn=next(n for n in ast.walk(ast.parse(patch.patched(ORIGINAL.read_bytes()))) if isinstance(n,ast.FunctionDef) and n.name=="MAD_training")
  exec(compile(ast.Module(body=[fn],type_ignores=[]),"generated","exec"),scope)
  with mock.patch.dict(sys.modules,{"ad5_full_math_runtime":types.SimpleNamespace(MultiProbe=Probe)}):scope["MAD_training"](t)
  self.assertEqual(t.global_step,6200)
  for name,n in [("construct",2),("backward",6200),("update",12400),("zero",12400),("schedule",80),("logging",6200),("tensorboard",6200),("close",1),("done",1)]:self.assertEqual(events.count(name),n,name)
  for e in range(40):self.assertLess(events.index(("save",e)),events.index(("saved",e)))
  self.assertEqual(events[-2:],["close","done"])
  self.assertEqual(events.count(("empty_test",39)),1)


if __name__=="__main__":unittest.main()
