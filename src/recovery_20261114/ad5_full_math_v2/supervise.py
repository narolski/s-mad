"""R1 real child/process-group supervision; no model imports or numeric payload decoding."""
import argparse,datetime,hashlib,json,os,pathlib,selectors,signal,subprocess,sys,time
def syncdir(path):
 fd=os.open(path,os.O_RDONLY)
 try:os.fsync(fd)
 finally:os.close(fd)
def put(path,obj):
 with path.open("x") as f:json.dump(obj,f,indent=2,allow_nan=False);f.write("\n");f.flush();os.fsync(f.fileno())
 syncdir(path.parent)
def mirror(local,dest,deadline):
 """Incremental snapshots; no claim of checkpoint validity while producer is running."""
 entries=[]
 if not local.exists():return entries
 for p in sorted(local.rglob("*")):
  if time.monotonic()>=deadline:raise TimeoutError("collection budget")
  if not p.is_file() or p.is_symlink():continue
  if p.name not in ("training.log","40_backbone.pth","40_header.pth") and not p.name.startswith("events.out.tfevents"):continue
  rel=p.relative_to(local);q=dest/rel;q.parent.mkdir(parents=True,exist_ok=True)
  tmp=q.with_name(q.name+".inflight_snapshot")
  before=p.stat();h=hashlib.sha256()
  with p.open("rb") as source,tmp.open("wb") as target:
   while True:
    if time.monotonic()>=deadline:raise TimeoutError("collection budget")
    b=source.read(1<<20)
    if not b:break
    target.write(b);h.update(b)
   target.flush();os.fsync(target.fileno())
  after=p.stat();os.replace(tmp,q);syncdir(q.parent)
  entries.append(dict(path=str(rel),bytes=q.stat().st_size,sha256=h.hexdigest(),stable_during_copy=before.st_size==after.st_size and before.st_mtime_ns==after.st_mtime_ns,snapshot_not_semantic_checkpoint_validation=True))
 return entries
def run(keep,local,argv,start_epoch,max_seconds=21000,term_grace=10,collection_seconds=300,echo=True):
 deadline=time.monotonic()+max(0,start_epoch+max_seconds-time.time())
 reason=[None];proc=None;sent=None;killed=False;errors=[];last_mirror=0;mirrors=[]
 def handler(sig,frame):reason[0]=reason[0] or ("SIGNAL_"+str(sig))
 old={s:signal.signal(s,handler) for s in (signal.SIGTERM,signal.SIGINT)}
 put(keep/"SUPERVISOR_START.json",dict(argv=argv,allocation_epoch=start_epoch,budget_seconds=max_seconds,term_grace_seconds=term_grace,collection_seconds=collection_seconds,automatic_retry=False,direct_durable_technical_records=True,live_snapshots="NOT_ATTESTED_COMPLETE"))
 try:
  if time.monotonic()>=deadline:reason[0]="ALLOCATION_BUDGET_EXHAUSTED_BEFORE_CHILD"
  if reason[0] is None:
   proc=subprocess.Popen(argv,stdout=subprocess.PIPE,stderr=subprocess.STDOUT,start_new_session=True,bufsize=0)
   sel=selectors.DefaultSelector();sel.register(proc.stdout,selectors.EVENT_READ)
   exited_at=None
   with (keep/"technical/train_stdout.log").open("xb",buffering=0) as log:
    while sel.get_map() or proc.poll() is None:
     now=time.monotonic()
     if now>=deadline:reason[0]=reason[0] or "PRE_HARD_LIMIT_TIMEOUT"
     if proc.poll() is not None and exited_at is None:exited_at=now
     if exited_at is not None and sel.get_map() and now-exited_at>term_grace:reason[0]=reason[0] or "ORPHAN_STDOUT_INCOMPLETE"
     if reason[0] and sent is None:
      try:os.killpg(proc.pid,signal.SIGTERM)
      except ProcessLookupError:pass
      sent=now
     if sent is not None and now-sent>=term_grace and not killed:
      try:os.killpg(proc.pid,signal.SIGKILL)
      except ProcessLookupError:pass
      killed=True
     for key,_ in sel.select(.1):
      data=os.read(key.fd,1<<16)
      if data:
       log.write(data);os.fsync(log.fileno())
       if echo:
        try:os.write(1,data)
        except OSError:pass
      else:sel.unregister(key.fileobj);key.fileobj.close()
     if now-last_mirror>=1:
      try:mirrors=mirror(local,keep/"original_run",min(time.monotonic()+2,deadline))
      except (OSError,TimeoutError) as e:errors.append(type(e).__name__)
      last_mirror=now
     if killed and sent is not None and now-sent>term_grace+2:
      # A descendant retaining stdout must not block the final failure receipt.
      for key in list(sel.get_map().values()):sel.unregister(key.fileobj);key.fileobj.close()
      if proc.poll() is None:raise TimeoutError("child could not be reaped after KILL")
    child=proc.wait(timeout=2)
  else:child=None
 except BaseException as e:
  errors.append(type(e).__name__);reason[0]=reason[0] or "SUPERVISOR_ERROR"
  if proc is not None:
   try:os.killpg(proc.pid,signal.SIGKILL);killed=True
   except ProcessLookupError:pass
   try:proc.wait(timeout=2)
   except subprocess.TimeoutExpired:pass
  child=proc.returncode if proc is not None else None
 finally:
  collection_deadline=time.monotonic()+collection_seconds
  try:mirrors=mirror(local,keep/"original_run",collection_deadline)
  except (OSError,TimeoutError) as e:errors.append("final_"+type(e).__name__)
  result=None
  try:result=json.loads((keep/"technical/MULTI_RESULT.json").read_text())
  except (ValueError,OSError):pass
  complete=isinstance(result,dict) and result.get("status")=="FULL_B_6200_UPDATES_AND_CHECKPOINT_ROUNDTRIP_COMPLETE" and result.get("effective_batches")==6200
  eligible=reason[0] is None and not errors and child==0 and complete and all(v["stable_during_copy"] for v in mirrors)
  rc=0 if eligible else (124 if reason[0] and "TIMEOUT" in reason[0] else 94)
  put(keep/"SUPERVISOR_EXIT.json",dict(child_exit=child,supervisor_exit=rc,status="COMPLETE_PENDING_INDEPENDENT_REVIEW" if eligible else "INCOMPLETE_OR_FAILED",reason=reason[0],errors=errors,term_sent=sent is not None,kill_sent=killed,eligible_for_technical_review=eligible,partial_multi_result_never_overrides_timeout=True,final_snapshots=mirrors,arbitrary_hardware_loss_retention="NOT_GUARANTEED",automatic_retry=False))
  try:
   lines=[]
   for p in sorted(keep.rglob("*")):
    if not p.is_file() or p.is_symlink() or p.name=="SHA256SUMS":continue
    h=hashlib.sha256()
    with p.open("rb") as f:
     while True:
      if time.monotonic()>=collection_deadline:raise TimeoutError("manifest budget")
      b=f.read(1<<20)
      if not b:break
      h.update(b)
    lines.append(h.hexdigest()+"  "+str(p.relative_to(keep))+"\n")
   with (keep/"SHA256SUMS").open("x") as f:f.writelines(lines);f.flush();os.fsync(f.fileno())
   syncdir(keep)
  except (OSError,TimeoutError) as e:
   rc=94
   put(keep/"MANIFEST_FAILURE.json",dict(status="INCOMPLETE",error_type=type(e).__name__,eligible_for_technical_review=False))
  for sig,h in old.items():signal.signal(sig,h)
 return rc
def main():
 p=argparse.ArgumentParser();p.add_argument("--keep",required=True);p.add_argument("--local-run",required=True);p.add_argument("--allocation-start-file",required=True);p.add_argument("--max-seconds",type=float,default=21000);p.add_argument("--term-grace",type=float,default=10);p.add_argument("--collection-seconds",type=float,default=300);p.add_argument("command",nargs=argparse.REMAINDER);a=p.parse_args()
 argv=a.command[1:] if a.command[:1]==["--"] else a.command
 assert argv
 return run(pathlib.Path(a.keep),pathlib.Path(a.local_run),argv,float(pathlib.Path(a.allocation_start_file).read_text()),a.max_seconds,a.term_grace,a.collection_seconds)
if __name__=="__main__":sys.exit(main())
