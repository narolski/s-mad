"""Create-only sealed producer. NO live release exists in this packet."""
import argparse,hashlib,json,os,pathlib,sys,time
from engine import run,mapping
from design import SPECS
def sha(p):
 h=hashlib.sha256()
 with pathlib.Path(p).open("rb") as f:
  for b in iter(lambda:f.read(4<<20),b""):h.update(b)
 return h.hexdigest()
def put(p,obj):
 with p.open("x") as f:json.dump(obj,f,indent=2,allow_nan=False);f.write("\n");f.flush();os.fsync(f.fileno())
 fd=os.open(p.parent,os.O_RDONLY)
 try:os.fsync(fd)
 finally:os.close(fd)
def authorize(r,a,mode,seed,source):
 assert r["decision"]==("GO_SBMR512_BII_TIMING_V1" if mode=="timing" else "GO_SBMR512_BII_FULL_V1")
 assert r["root_authorized"] is True and r["author"]!=r["reviewer"] and r["reviewer"]
 assert r["seed"]==seed and seed in (408,409,410,411,412) and (mode!="timing" or seed==408)
 assert r["scientific_read"]=="HOLD" and r["automatic_retry"] is False
 assert r["source_manifest_sha256"]==sha(source/"SHA256SUMS")
 assert sha(r["independent_review_path"])==r["independent_review_sha256"]
 assert sha(r["staging_admission_path"])==r["staging_admission_sha256"]
 for line in (source/"SHA256SUMS").read_text().splitlines():
  h,n=line.split("  ",1);p=source/n;assert p.resolve().is_relative_to(source.resolve()) and sha(p)==h
 assert a["status"]=="ROOT_ADOPTED_ALL_ACTUAL_INPUT_RUNTIME_STATE_HISTORY_FIELDS"
 for flag in ("image_bytes_verified","pretrained_content_verified","checkpoint_schema_reviewed","runtime_source_reviewed","positional_rebuild_source_and_runtime_reviewed","omitted_train_meds_without_replay_reviewed","full_reference_container_decode_exception"):
  assert a[flag] is True,flag
 assert a["extra_train_meds_replay"] is False
 assert a["trainable_bytes"]==312981
 authority=json.loads((source/"AUTHORITY.json").read_text());known=authority["trainable_overlays"][str(seed)]
 assert a["trainable_sha256"]==known["trainable_member"]["sha256"]
 assert a["archive_sha256"]==known["archive_sha256"]
 assert a["cross_ids"]==authority["cross_ids"]
 assert sha(a["context_binding_path"])==authority["context_binding_sha256"]
 assert a["full_checkpoint_hash_substituted_for_trainable"] is False
 assert pathlib.Path(r["output"]).resolve()==pathlib.Path("/mnt/t7/smad_next/RZ1/SbMR512_bii_producer_v1")/(mode+"_s"+str(seed))
 assert sha(r["technical_attachment_adoption_path"])==r["technical_attachment_adoption_sha256"]
 assert r["technical_attachment_postreview_sha256"]=="495f24ddccbb5b69383a9790ea7dc2c175f5ba72ee11a0d67db605ee0afd5b16"
 if mode=="full":
  assert r["timing_rebuild_independently_admitted"] is True
  assert sha(r["timing_rebuild_receipt_path"])==r["timing_rebuild_receipt_sha256"]
 assert r["native_bytegate_scope"]=="SAME_ORIGINAL_TARGETS_EXACT_FLOAT32_BYTES_NO_FALLBACK"
 return True
def main():
 p=argparse.ArgumentParser();p.add_argument("--release",required=True);p.add_argument("--seed",type=int,required=True);p.add_argument("--mode",choices=("timing","full"),required=True);a=p.parse_args()
 source=pathlib.Path(__file__).resolve().parent;r=json.loads(pathlib.Path(a.release).read_text())
 admission=json.loads(pathlib.Path(r["staging_admission_path"]).read_text())
 authorize(r,admission,a.mode,a.seed,source)
 out=pathlib.Path(r["output"]);out.mkdir(parents=True,exist_ok=False)
 put(out/"CLAIM.json",dict(release_sha256=sha(a.release),mode=a.mode,seed=a.seed,scientific_read="HOLD",automatic_retry=False))
 try:
  # All actual source/model/input/reference/body hashing and decoding is AFTER release+exclusiveclaim.
  for path,h in admission["actual_content_pins"].items():assert sha(path)==h
  authority=json.loads((source/"AUTHORITY.json").read_text())
  for name,h in authority["required_source_content"].items():
   path=pathlib.Path(admission["code_dir"])/"smadcvpr"/name if name in ("common.py","archs_a12.py") else pathlib.Path(admission["rz1_source_dir"])/name
   assert sha(path)==h
  assert sha(admission["trainable_path"])==admission["trainable_sha256"]
  assert pathlib.Path(admission["trainable_path"]).stat().st_size==312981
  context=json.loads(pathlib.Path(admission["context_binding_path"]).read_text())
  ids=admission["cross_ids"];assert len(ids)==13771;mapping(context,ids)
  assert len(context["ordered_context_rows"]["ab1x_eval"])==24859 and len(context["ordered_context_rows"]["tt1"])==34411
  from backend import Backend
  b=Backend(admission,context,a.seed);start=time.monotonic()
  if a.mode=="timing":
   # Fixed first original eval batch0,64rows, containing metadata-bound crosstargets; native+flip only.
   b.set_spec(SPECS[0]);before=b.state_digest()
   lo,hi,x=next(b.batches("ab1x_eval",limit_rows=64));assert (lo,hi)==(0,64)
   l0,host=b.native_host(x);dest=mapping(context,ids);pairs=sorted((oi,host[i]) for (pop,i),oi in dest.items() if pop=="ab1x_eval" and i<64)
   assert pairs;b.flip_tta_host_discard(x,l0);assert b.state_digest()==before
   assert b.native_reference_equal([ids[oi] for oi,_ in pairs],[v for _,v in pairs])
   put(out/"TIMING_REBUILD.json",dict(native_target_bytegate=True,original_batch_index=0,original_rows=64,forward_calls=2,exported_logits=0,elapsed_seconds=time.monotonic()-start,peak_memory_allocated=b.torch.cuda.max_memory_allocated(),status="TECHNICAL_ONLY_NO_FULL_KERNEL_OUTPUT"))
  else:
   values=run(context,ids,b)
   # Seal exact all14cross tensor; only later registered NEXTonce reader may interpret it.
   with (out/"SEALED_CROSS.npz").open("xb") as f:
    b.np.savez(f,id=b.np.asarray(ids),specs=b.np.asarray(SPECS),logit=b.np.asarray(values,dtype=b.np.float32))
    f.flush();os.fsync(f.fileno())
   put(out/"PRODUCER_RECEIPT.json",dict(status="SEALED_NOT_SCIENTIFIC_ADMISSION",seed=a.seed,native_bytegate=True,shape=[14,13771],dtype="float32",sealed_sha256=sha(out/"SEALED_CROSS.npz"),elapsed_seconds=time.monotonic()-start,peak_memory_allocated=b.torch.cuda.max_memory_allocated(),all_kappa_metrics="NOT_COMPUTED"))
  put(out/"COMPLETE.json",dict(scope="SEALED_PRODUCER_OR_TECHNICAL_TIMING_ONLY",scientific_read="HOLD"))
 except BaseException as e:
  put(out/"FAILED.json",dict(error_type=type(e).__name__,status="HOLD_NO_RETRY_NO_FALLBACK"));raise
if __name__=="__main__":main()
