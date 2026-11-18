"""Create and verify an additional durable XAI copy; never delete originals."""
from datetime import datetime,timezone
import hashlib,json,os,shutil
from pathlib import Path

root=Path('/home/narolski/smad-next')
source=root/'manuscript_cvpr2027/figures/shortcut_attribution_20261114'
store=Path('/mnt/t7/smad_next/XAI/backup_20261114')
free=shutil.disk_usage('/mnt/t7').free
if free<50*1024**3:
 raise RuntimeError('50 GiB free-space floor not met')
stamp=datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S_%fZ')
destination=store/('shortcut_attribution_20261114__'+stamp)
def sha(p):
 h=hashlib.sha256()
 with p.open('rb') as f:
  for b in iter(lambda:f.read(1024*1024),b''):h.update(b)
 return h.hexdigest()
def inventory(base):
 result={}
 for p in sorted(base.rglob('*')):
  if p.is_symlink():raise ValueError('Refusing symlink: '+str(p))
  if p.is_file():
   a=p.stat(); digest=sha(p);b=p.stat()
   if (a.st_ino,a.st_size,a.st_mtime_ns)!=(b.st_ino,b.st_size,b.st_mtime_ns):
    raise RuntimeError('File changed while hashing: '+str(p))
   result[str(p.relative_to(base))]=dict(bytes=b.st_size,sha256=digest)
 return result
before=inventory(source)
store.mkdir(parents=True,exist_ok=True)
shutil.copytree(source,destination,copy_function=shutil.copy2)
copied=inventory(destination)
after=inventory(source)
if before!=after or before!=copied:
 raise RuntimeError('Copy not verified: source changed or destination differs; preserve copy for investigation')
# Sync all destination file data before writing the completion receipt.
for rel in copied:
 with (destination/rel).open('rb') as f:os.fsync(f.fileno())
for directory in sorted((p for p in destination.rglob('*') if p.is_dir()),reverse=True)+[destination,store]:
 fd=os.open(directory,os.O_RDONLY|os.O_DIRECTORY)
 try:os.fsync(fd)
 finally:os.close(fd)
receipt=dict(status='VERIFIED_DURABLE_COPY',created_utc=datetime.now(timezone.utc).isoformat(),
 source=str(source),destination=str(destination),source_preserved=True,deletions=0,
 source_unchanged_during_copy=True,all_relative_paths_sizes_sha256_equal=True,
 file_count=len(copied),bytes=sum(v['bytes'] for v in copied.values()),
 free_bytes_before=free,free_bytes_after=shutil.disk_usage('/mnt/t7').free,
 script_sha256=sha(Path(__file__)),private_noncommercial_draft_only=True,
 publication_clearance='PENDING; original asset restrictions unchanged',files=copied)
name='XAI_DURABLE_COPY_RECEIPT_'+stamp+'.json'
for p in (store/name,root/'experiments/AGENTIC_delivery_20261114'/name):
 with p.open('x') as f:
  json.dump(receipt,f,indent=2);f.write('\n');f.flush();os.fsync(f.fileno())
print(json.dumps(dict(destination=str(destination),files=receipt['file_count'],bytes=receipt['bytes'],
 receipt=str(store/name),receipt_sha256=sha(store/name),source_preserved=True)))
