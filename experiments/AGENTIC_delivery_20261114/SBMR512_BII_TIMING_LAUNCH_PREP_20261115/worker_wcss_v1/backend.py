"""Future released original-source derivative; imports model libraries only on construction."""
import hashlib,json,os,pathlib,sys
class Backend:
 def __init__(self,admission,context,seed):
  import numpy as np
  import torch
  from torch.utils.data import DataLoader
  self.np=np;self.torch=torch;self.DataLoader=DataLoader;self.context=context;self.admission=admission
  assert torch.__version__=="2.11.0+cu128" and torch.version.cuda=="12.8"
  assert torch.cuda.device_count()==1 and "H100" in torch.cuda.get_device_name(0)
  os.environ["HF_HUB_OFFLINE"]="1";os.environ["HF_HOME"]=admission["hf_home"]
  os.environ["SMAD_DATA"]=admission["data_root"];os.environ["RZ1_RES512"]="1";os.environ["RZ1_TRANSFORM"]="fixed:pil_bilinear"
  sys.path.insert(0,admission["rz1_source_dir"]);import rz1_patch
  self.patch=rz1_patch;rz1_patch.apply(admission["code_dir"])
  import common as C
  self.C=C
  # Record/compare defaults; never silently choose new deterministic/precision defaults.
  actual={"cudnn_benchmark":torch.backends.cudnn.benchmark,"cudnn_deterministic":torch.backends.cudnn.deterministic,"float32_matmul_precision":torch.get_float32_matmul_precision(),"default_dtype":str(torch.get_default_dtype())}
  assert actual==admission["reviewed_backend_defaults"],"runtime defaults unbound/mismatch"
  torch.backends.cuda.matmul.allow_tf32=True;torch.backends.cudnn.allow_tf32=True
  meta=json.loads(pathlib.Path(admission["meta_path"]).read_text())
  assert meta["seed"]==seed and meta["res"]==512 and meta["arch"]=="a12_clip_vitb16_madation"
  assert meta==admission["reviewed_meta"]
  model,_=C.build_run_model(meta)
  expected={n for n,p in model.named_parameters() if p.requires_grad}
  assert sorted(expected)==admission["expected_trainable_names"]
  sd=torch.load(admission["trainable_path"],map_location="cpu",weights_only=True)
  assert set(sd)==expected
  assert {k:{"shape":list(v.shape),"dtype":str(v.dtype)} for k,v in sd.items()}==admission["reviewed_trainable_schema"]
  assert all(torch.isfinite(v).all() for v in sd.values())
  loaded=model.load_state_dict(sd,strict=False)
  assert not loaded.unexpected_keys and set(loaded.missing_keys)==set(model.state_dict())-expected
  # Original timm factory does the original224->512 positional rebuild ONCE; no manual interpolation.
  assert admission["positional_rebuild_source_and_runtime_reviewed"] is True
  self.model=model.to("cuda").eval()
  assert not any(m.training for m in self.model.modules())
  assert all(torch.isfinite(v).all() for v in self.model.state_dict().values() if v.is_floating_point())
  self.reference=None
 def set_spec(self,spec):self.patch.set_spec(spec)
 def batches(self,pop,limit_rows=None):
  rows=self.context["ordered_context_rows"][pop]
  if limit_rows is not None:rows=rows[:limit_rows]
  dl=self.DataLoader(self.C.ImageItems([(r["path"],int(r["label"])) for r in rows],512),batch_size=64,num_workers=7)
  # Exactly original DataLoader defaults; no shuffle/augment/worker-seed invention.
  for bi,(x,_) in enumerate(dl):
   assert tuple(x.shape[1:])==(3,512,512) and x.dtype==self.torch.float32
   yield bi*64,min((bi+1)*64,len(rows)),x.to("cuda",non_blocking=True)
 def native_host(self,x):
  with self.torch.no_grad():l0=self.C.forward_logit(self.model,x)[0].float()
  return l0,l0.cpu().tolist()
 def flip_tta_host_discard(self,x,l0):
  t=self.torch
  with t.no_grad():
   l1=self.C.forward_logit(self.model,t.flip(x,dims=[3]))[0].float()
   transient=((t.sigmoid(l0)+t.sigmoid(l1))/2).cpu().tolist()
  assert len(transient)==len(x)
  del transient,l1
 def state_digest(self):
  h=hashlib.sha256()
  for n,v in sorted(self.model.state_dict().items()):
   a=v.detach().cpu().contiguous()
   h.update(n.encode());h.update(str(a.dtype).encode());h.update(str(tuple(a.shape)).encode());h.update(a.numpy().tobytes())
  return h.hexdigest()
 def _references(self,requested_ids):
  # Explicit future root permission covers compressed full-container schema decode.
  # No population with zero fixed requested targets may even be opened.
  np=self.np;out={};requested=set(requested_ids)
  assert len(requested)==len(requested_ids)
  for pop in ("ab1x_eval","tt1"):
   rows=self.context["ordered_context_rows"][pop]
   prefix="ab1x:" if pop=="ab1x_eval" else "tt1:"
   wanted=[(i,prefix+r["id"]) for i,r in enumerate(rows) if prefix+r["id"] in requested]
   if not wanted:continue
   with np.load(self.admission["reference_paths"][pop],allow_pickle=False) as z:
    # NpzFile indexing may decompress: exactly ONE access to each required array.
    ids=z["id"];logits=z["logit"];manifest=z["manifest_sha256"]
    assert ids.tolist()==[r["id"] for r in rows]
    assert logits.shape==(len(rows),) and logits.dtype==np.float32
    assert str(manifest)==self.admission["reference_manifest_sha256"][pop]
    for i,cid in wanted:
     value=logits[i];assert np.isfinite(value);out[cid]=value
   del ids,logits,manifest
  assert set(out)==requested
  return out
 def native_reference_equal(self,ids,values):
  if self.reference is None:self.reference=self._references(ids)
  a=self.np.asarray(values,dtype=self.np.float32)
  b=self.np.asarray([self.reference[i] for i in ids],dtype=self.np.float32)
  return a.tobytes()==b.tobytes()
