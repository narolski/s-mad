"""Registered36-update observer; no evaluation dataset or performance statistics."""
import hashlib,json,os,pathlib,time,torch
from ad5_math_multi_base import BaseProbe,put
from ad5_math_multi_contract import expected_names,updates,batch_order
class MultiProbe(BaseProbe):
 def __init__(self,*args):
  super().__init__(*args)
  self.root=self.out;self.count=0;self.current_epoch=-1;self.epoch_batches=0
  assert self.t.global_step==0 and len(self.t.dataloader)==12
  self.t0=time.monotonic();torch.cuda.reset_peak_memory_stats()
 def epoch(self,epoch):
  assert epoch==self.current_epoch+1 and epoch in (0,1,2) and self.count==12*epoch
  self.current_epoch=epoch;self.epoch_batches=0
  with self.lock:self.visits.clear()
  state=torch.get_rng_state().clone()
  self.order=list(iter(self.t.train_sampler))[:3072]
  assert torch.equal(state,torch.get_rng_state()) and len(self.order)==3072
  assert self.t.train_sampler.seed==0 and self.t.train_sampler.epoch==epoch
 def inputs(self,images,target):
  assert self.epoch_batches<12 and self.count<36
  self.count+=1;offset=self.epoch_batches*256;self.epoch_batches+=1
  self.out=self.root/("step_%04d"%self.count);self.out.mkdir()
  assert tuple(images.shape)==(256,3,224,224) and images.dtype==torch.float32
  assert tuple(target.shape)==(256,) and target.dtype==torch.float32
  with self.lock:actual=self.visits[offset:offset+256].copy()
  expected=self.order[offset:offset+256];batch_order(expected,actual)
  crop=os.environ["AD5_CROP_ROOT"];ids=[];labels=[]
  for index in actual:
   row=self.t.trainset.data.iloc[index];path=str(row.iloc[0]);assert path.startswith(crop+"/")
   ids.append("CROP_ROOT"+path[len(crop):]);labels.append(1 if row.iloc[1]=="bonafide" else 0)
  assert target.detach().cpu().tolist()==labels
  self.before={(g,n):self.parameters[g][n].detach().clone() for g,ns in expected_names().items() for n in ns}
  self.last_images=images.detach();self.last_target=target.detach()
  put(self.out/"BATCH.json",dict(step=self.count,epoch=self.current_epoch,actual_indices=actual,original_sampler_indices=expected,canonical_image_ids_in_order=ids,order_sha256=hashlib.sha256(json.dumps(list(zip(actual,ids)),separators=(",",":")).encode()).hexdigest(),images_dtype=str(images.dtype),target_dtype=str(target.dtype),shape=list(images.shape),global_batch=256))
 def finish(self,model_norm,header_norm):
  torch.cuda.synchronize()
  norms={"model":float(model_norm.item()),"header":float(header_norm.item())}
  assert all(torch.isfinite(torch.tensor(v)) and v>0 for v in norms.values())
  records={}
  for group,names in expected_names().items():
   records[group]={}
   for name in names:
    p=self.parameters[group][name];st=self.optimizers[group].state[p]["step"]
    records[group][name]=dict(finite=bool(torch.isfinite(p).all()),changed=not torch.equal(p.detach(),self.before[group,name]),optimizer_step=int(st.item()) if hasattr(st,"item") else st)
  updates(records,self.count)
  for group,optimizer in self.optimizers.items():
   for name in expected_names()[group]:
    state=optimizer.state[self.parameters[group][name]]
    assert all(torch.isfinite(state[k]).all() for k in ("exp_avg","exp_avg_sq"))
  assert all(torch.isfinite(t).all() for m in (self.t.model.module,self.t.header.module) for t in m.state_dict().values() if t.is_floating_point())
  put(self.out/"UPDATED_TRAINABLES.json",records)
  put(self.out/"UPDATE.json",dict(step=self.count,loss_finite=True,all_model_header_float_state_finite=True,optimizer_moments_finite=True,preclip_gradient_norm=norms,optimizer_model_updates=self.count,optimizer_header_updates=self.count))
 def saved(self,epoch):
  assert epoch==self.current_epoch and self.epoch_batches==12 and self.count==(epoch+1)*12
  out=pathlib.Path(self.t.config.output_path)
  files=[out/"3_backbone.pth",out/"3_header.pth"]
  assert all(p.is_file() for p in files) if epoch==2 else not any(p.exists() for p in files)
  put(self.root/("EPOCH_%d.json"%epoch),dict(epoch=epoch,updates=self.count,original_checkpoint_callback_completed=True,schedulers_completed=True,checkpoints_present=epoch==2))
 def done(self):
  assert self.count==36 and self.t.global_step==36 and self.current_epoch==2
  out=pathlib.Path(self.t.config.output_path)
  models={"backbone":self.t.model.module,"header":self.t.header.module}
  paths={k:out/("3_"+k+".pth") for k in models}
  # Only the exact files just produced by the original callback may be deserialized.
  memory={k:{n:t.detach().cpu().clone() for n,t in m.state_dict().items()} for k,m in models.items()}
  loaded={}
  for k,p in paths.items():
   assert p.is_file() and not p.is_symlink()
   loaded[k]=torch.load(p,map_location="cpu",weights_only=True)
   assert set(loaded[k])==set(memory[k])
   for n,t in loaded[k].items():
    assert t.dtype==memory[k][n].dtype and t.shape==memory[k][n].shape and t.contiguous().numpy().tobytes()==memory[k][n].contiguous().numpy().tobytes()
    if t.is_floating_point():assert torch.isfinite(t).all()
  def logits():
   self.t.model.eval();self.t.header.eval()
   with torch.no_grad(),torch.backends.cuda.sdp_kernel(enable_flash=False,enable_math=True,enable_mem_efficient=False):
    f=self.t.model.module.encode_image(self.last_images)
    z,_=self.t.header(torch.nn.functional.normalize(f),self.last_target)
    assert z.dtype==torch.float32 and tuple(z.shape)==(256,2) and torch.isfinite(z).all()
    return z.detach().cpu().contiguous()
  z1=logits()
  # train() unmerges LoRA. Restore checkpoint in train mode to avoid merged-weight double application.
  self.t.model.train();self.t.header.train()
  for k,m in models.items():
   result=m.load_state_dict(loaded[k],strict=True);assert not result.missing_keys and not result.unexpected_keys
   assert all(t.detach().cpu().contiguous().numpy().tobytes()==loaded[k][n].contiguous().numpy().tobytes() for n,t in m.state_dict().items())
  z2=logits()
  b1=z1.numpy().tobytes();b2=z2.numpy().tobytes();assert b1==b2,"produced checkpoint last-used-batch bytegate failed"
  def sha(p):
   h=hashlib.sha256()
   with p.open("rb") as f:
    for b in iter(lambda:f.read(8<<20),b""):h.update(b)
   return h.hexdigest()
  put(self.root/"CHECKPOINT_ROUNDTRIP.json",dict(scope="EXACT_THIS_RUN_3_BACKBONE_AND_HEADER_ONLY",checkpoint_paths={k:str(p) for k,p in paths.items()},sha256={k:sha(p) for k,p in paths.items()},state_identity_before_and_after_strict_reload=True,last_used_training_batch_only=True,noTTA=True,logit_dtype="float32",logit_shape=[256,2],logit_byte_equality=True,logit_sha256=hashlib.sha256(b1).hexdigest(),numeric_logits_saved=False,performance_statistics="NOT_COMPUTED"))
  put(self.root/"MULTI_RESULT.json",dict(status="THIRTY_SIX_REAL_MATH_UPDATES_AND_CHECKPOINT_ROUNDTRIP_COMPLETE",effective_batches=36,optimizer_model_updates=36,optimizer_header_updates=36,epochs=3,global_batch=256,completed_drop_last_batches_per_epoch=12,legacy_printed_total_step=38,peak_memory_allocated_bytes=torch.cuda.max_memory_allocated(),elapsed_seconds=time.monotonic()-self.t0,scientific_performance="NOT_MEASURED",production_recovery="NOT_ESTABLISHED"))
