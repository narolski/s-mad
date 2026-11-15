"""Receipt metadata and sidecars only. Never opens an archive body/member."""
import hashlib,json,pathlib,re
ARMS=("bce","paired_bce","paired_rank");SEEDS=range(501,506)
WANTED={f"SPRINT5_1_production_v3_{a}_s{s}.tar":(a,s) for s in SEEDS for a in ARMS}
def sha(p):return hashlib.sha256(pathlib.Path(p).read_bytes()).hexdigest()
def assemble(receipt_paths,require_complete=True):
 entries=[];provenance=[];seen=set()
 for receipt in map(pathlib.Path,receipt_paths):
  d=json.loads(receipt.read_text())
  assert d["remote_local_sidecar_equal"] is True
  assert d["archive_members_opened"] is False and d["scientific_read_authorized"] is False
  assert not d.get("missing",[])
  files=d["files"];names=[f["name"] for f in files]
  assert len(names)==len(set(names)),"duplicate receipt member"
  for f in files:
   name=f["name"]
   if not name.startswith("SPRINT5_1_production_v3_") or not name.endswith(".tar"):continue
   assert name in WANTED,"foreign production identity"
   assert name not in seen,"duplicate task across receipts"
   seen.add(name);arm,seed=WANTED[name];h=f["sha256"]
   assert isinstance(h,str) and re.fullmatch("[0-9a-f]{64}",h),"bad archive digest"
   size=f.get("bytes",f.get("size"));assert type(size) is int and size>0
   local=receipt.parent/name;assert local.is_file() and not local.is_symlink() and local.stat().st_size==size
   side=receipt.parent/(name+".sha256")
   sr=[x for x in files if x["name"]==name+".sha256"];assert len(sr)==1
   assert side.is_file() and sha(side)==sr[0]["sha256"],"sidecar receipt hash"
   tokens=side.read_text().split();assert len(tokens)==2 and tokens[0]==h and pathlib.Path(tokens[1].lstrip("*")).name==name,"sidecar archive identity"
   e=dict(task=name[:-4],arm=arm,seed=seed,archive_path=str(local.resolve()),archive_sha256=h)
   entries.append(e)
   provenance.append(dict(**e,archive_bytes=size,source_receipt=str(receipt.resolve()),source_receipt_sha256=sha(receipt),sidecar_path=str(side.resolve()),sidecar_sha256=sha(side),opaque_archive_body_rehashed_here=False))
 missing=sorted(set(WANTED)-seen)
 if require_complete:assert not missing,"missing fixed15fits: "+",".join(missing)
 assert len({e["archive_sha256"] for e in entries})==len(entries),"duplicate archive digest"
 assert len({e["archive_path"] for e in entries})==len(entries),"duplicate archive path"
 order=lambda e:(e["seed"],ARMS.index(e["arm"]))
 return sorted(entries,key=order),sorted(provenance,key=order),missing
