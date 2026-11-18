"""Backend-injected fixed Bii engine. No model, image, NPZ or archive imports."""
import math
from design import SPECS
def mapping(context,cross_ids):
 assert len(cross_ids)==len(set(cross_ids))
 out={i:n for n,i in enumerate(cross_ids)};by={};seen=set()
 for m in context["target_mapping"]:
  cid=m["cross_id"];pop=m["population"];idx=m["index"]
  assert cid in out and cid not in seen and (pop,idx) not in by
  row=context["ordered_context_rows"][pop][idx]
  assert row["id"]==cid.split(":",1)[1] and row["path"]==m["path"] and str(row["label"])==str(m["label"])
  assert m["batch"]==idx//64 and m["offset"]==idx%64
  by[pop,idx]=out[cid];seen.add(cid)
 assert seen==set(cross_ids)
 return by
def run(context,cross_ids,backend,specs=SPECS):
 assert tuple(specs)==SPECS
 dest=mapping(context,cross_ids);outputs=[]
 for si,spec in enumerate(specs):
  backend.set_spec(spec);selected=[None]*len(cross_ids);writes=set()
  for pop in ("ab1x_eval","tt1"):
   before=backend.state_digest();cursor=0;n=len(context["ordered_context_rows"][pop])
   for start,stop,x in backend.batches(pop):
    assert start==cursor and stop==min(start+64,n);cursor=stop
    # Original l0.cpu().tolist precedes flip. Full batch values are transient, never accumulated.
    l0,host=backend.native_host(x)
    assert len(host)==stop-start and all(type(v) in (float,int) and math.isfinite(v) for v in host)
    for offset,value in enumerate(host):
     oi=dest.get((pop,start+offset))
     if oi is not None:
      assert oi not in writes;selected[oi]=float(value);writes.add(oi)
    if pop=="ab1x_eval":backend.flip_tta_host_discard(x,l0)
    del host,l0,x
   assert cursor==n and backend.state_digest()==before,"forward state mutation"
  assert len(writes)==len(cross_ids) and all(v is not None for v in selected)
  # Strict gate BEFORE any perturbation; mismatch never invokes alternative schedule.
  if si==0:assert backend.native_reference_equal(cross_ids,selected),"native exact byte gate failed"
  outputs.append(selected)
 return outputs
