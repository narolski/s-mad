"""SOURCE ONLY: bounded prospective import/runtime observation, never a model build."""
import hashlib,importlib,json,os,pathlib,re,stat,subprocess,sys,time
sys.path.insert(0,str(pathlib.Path(__file__).resolve().parent))
from authority import capture_json
MODULES=('numpy','PIL','torch','torchvision','timm')
ALLOWED_ROOTS=('/home/narolski/dmenv','/home/narolski/.local/share/uv/python/cpython-3.12.15-linux-x86_64-gnu','/usr/lib64','/lib64','/usr/lib/x86_64-linux-gnu','/lib/x86_64-linux-gnu')
MAX_MAPS=2<<20;MAX_LIBRARIES=512;MAX_LIBRARY=2<<30;MAX_TOTAL=4<<30
OUT='/lustre/pd03/hpc-narolski-1790461090/smad-next/RZ1/sbmr512_runtime_metadata_phase1_v1/result'
def req(v,msg):
 if not v:raise ValueError(msg)
def normalized(path):
 p=pathlib.PurePosixPath(path)
 req(isinstance(path,str) and path.startswith('/') and '..' not in p.parts and str(p)==path,'noncanonical/traversal path')
 return p
def inside(path,roots):
 p=normalized(path)
 return any(p==pathlib.PurePosixPath(r) or pathlib.PurePosixPath(r) in p.parents for r in roots)
def open_components(path,trust_root=False):
 """Descriptor-relative nofollow walk from /. No unrestricted resolve/follow."""
 parts=normalized(path).parts[1:];req(parts,'root is not a file')
 fd=os.open('/',os.O_RDONLY|os.O_DIRECTORY|os.O_NOFOLLOW)
 try:
  for part in parts[:-1]:
   nxt=os.open(part,os.O_RDONLY|os.O_DIRECTORY|os.O_NOFOLLOW,dir_fd=fd)
   if trust_root:
    s=os.fstat(nxt);req(s.st_uid==0 and not s.st_mode&0o022,'untrusted tool ancestor')
   os.close(fd);fd=nxt
  leaf=os.open(parts[-1],os.O_RDONLY|os.O_NOFOLLOW|os.O_NONBLOCK,dir_fd=fd)
  return leaf
 finally:os.close(fd)
def canonical_alias(path,aliases):
 """Only exact root-registered literal aliases; none discovered/followed broadly."""
 normalized(path);matches=[a for a in aliases if path==a['path'] or path.startswith(a['path']+'/')]
 req(len(matches)<=1,'ambiguous aliases')
 if not matches:return path
 a=matches[0];normalized(a['path']);normalized(a['canonical'])
 parent=str(pathlib.PurePosixPath(a['path']).parent)
 # Validate every alias ancestor without following links, then readlink once.
 parent_fd=os.open('/',os.O_RDONLY|os.O_DIRECTORY|os.O_NOFOLLOW)
 try:
  for part in pathlib.PurePosixPath(parent).parts[1:]:
   nxt=os.open(part,os.O_RDONLY|os.O_DIRECTORY|os.O_NOFOLLOW,dir_fd=parent_fd);os.close(parent_fd);parent_fd=nxt
  name=pathlib.PurePosixPath(a['path']).name
  req(os.readlink(name,dir_fd=parent_fd)==a['target'],'literal alias changed')
 finally:os.close(parent_fd)
 target=pathlib.PurePosixPath(a['target'])
 req('..' not in target.parts,'alias parent traversal')
 intended=str(target if target.is_absolute() else pathlib.PurePosixPath(parent)/target)
 req(intended==a['canonical'],'alias canonical mismatch')
 return a['canonical']+path[len(a['path']):]
def parse_maps(raw):
 req(len(raw)<=MAX_MAPS,'maps cap');records={}
 for line in raw.decode('utf-8',errors='strict').splitlines():
  cells=line.split(None,5)
  if len(cells)<6 or not cells[5].startswith('/'):continue
  path=cells[5];req(not path.endswith(' (deleted)'),'deleted mapping')
  if '.so' not in pathlib.PurePosixPath(path).name:continue
  req(inside(path,ALLOWED_ROOTS),'loaded library outside exact granted roots')
  major,minor=cells[3].split(':');dev=os.makedev(int(major,16),int(minor,16));inode=int(cells[4]);req(inode>0,'mapped inode')
  rec=dict(path=path,device=dev,inode=inode)
  req(path not in records or records[path]==rec,'inconsistent map identity');records[path]=rec
 req(len(records)<=MAX_LIBRARIES,'library count cap')
 return [records[k] for k in sorted(records)]
def snapshot(s):return (s.st_dev,s.st_ino,s.st_size,s.st_mtime_ns,s.st_ctime_ns,s.st_uid,s.st_mode)
def hash_fd(fd,a,cap,elf=False):
 req(stat.S_ISREG(a.st_mode) and 0<=a.st_size<=cap,'regular/file size cap')
 h=hashlib.sha256();count=0
 if elf:
  head=os.read(fd,min(4,a.st_size));req(head==b'\x7fELF','not ELF');h.update(head);count=len(head)
 while count<a.st_size:
  chunk=os.read(fd,min(4<<20,a.st_size-count));req(chunk,'file shrank');h.update(chunk);count+=len(chunk)
 req(os.read(fd,1)==b'','file grew')
 req(snapshot(a)==snapshot(os.fstat(fd)),'unstable file');return h.hexdigest()
def file_identity(mapped,body,remaining,aliases=()):
 path=mapped['path'];req(inside(path,ALLOWED_ROOTS),'root')
 canonical=canonical_alias(path,aliases);req(inside(canonical,ALLOWED_ROOTS),'canonical root')
 fd=open_components(canonical)
 try:
  a=os.fstat(fd);req(stat.S_ISREG(a.st_mode) and a.st_size<=MAX_LIBRARY,'file class/size')
  req((a.st_dev,a.st_ino)==(mapped['device'],mapped['inode']),'mapped descriptor identity mismatch')
  rec=dict(path=path,canonical_path=canonical,bytes=a.st_size,device=a.st_dev,inode=a.st_ino,mtime_ns=a.st_mtime_ns)
  if body:
   req(a.st_size<=remaining,'aggregate body cap');rec['sha256']=hash_fd(fd,a,min(MAX_LIBRARY,remaining),elf=True);rec['scope']='ACTUALLY_LOADED_ELF_CURRENT_BODY_ONLY'
  else:
   req(snapshot(a)==snapshot(os.fstat(fd)),'unstable stat');rec['sha256']=None;rec['scope']='LOADED_SO_PATH_STAT_ONLY_NO_BODY_IDENTITY'
  return rec,a.st_size if body else 0
 finally:os.close(fd)
def driver_query(g,record_identity=None):
 tool='/usr/bin/nvidia-smi';req(g['nvidia_smi_path']==tool,'fixed driver tool')
 req(g['nvidia_smi_identity_mode'] in ('KNOWN_PIN','ACQUIRE_FIXED_ROOT_OS_TOOL'),'tool identity mode')
 canonical=canonical_alias(tool,g['path_aliases']);req(inside(canonical,('/usr/bin','/usr/lib','/usr/lib64','/bin')),'fixed utility canonical class')
 fd=open_components(canonical,trust_root=True)
 try:
  a=os.fstat(fd);req(a.st_uid==0 and not a.st_mode&0o022,'untrusted tool owner/write mode')
  digest=hash_fd(fd,a,32<<20,elf=True)
  expected=g['nvidia_smi_sha256']
  if g['nvidia_smi_identity_mode']=='KNOWN_PIN':req(isinstance(expected,str) and len(expected)==64 and digest==expected,'known tool pin')
  else:req(expected is None and g['root_managed_tool_identity_acquisition'] is True,'explicit OS tool acquisition permission')
  identity=dict(path=tool,canonical_path=canonical,sha256=digest,bytes=a.st_size,uid=a.st_uid,mode=oct(stat.S_IMODE(a.st_mode)),identity_mode=g['nvidia_smi_identity_mode'],provenance='ROOT_MANAGED_FIXED_SITE_UTILITY_CURRENT_NODE_OBSERVATION')
  if record_identity is not None:record_identity(identity)
  # Execute this already hashed descriptor, avoiding pathname replacement races.
  command=[tool,'--query-gpu=driver_version','--format=csv,noheader,nounits']
  result=subprocess.run(command,executable='/proc/self/fd/'+str(fd),pass_fds=(fd,),capture_output=True,timeout=5,check=True)
  req(snapshot(a)==snapshot(os.fstat(fd)),'tool changed during query')
  req(len(result.stdout)<=16384 and len(result.stderr)<=16384,'driver output cap')
  rows=result.stdout.decode('utf-8').strip().splitlines();req(1<=len(rows)<=16 and len(set(rows))==1 and re.fullmatch(r'[0-9]+(?:\.[0-9]+){1,3}',rows[0]),'numeric driver version')
  identity['driver_version']=rows[0];return identity
 finally:os.close(fd)
def put(path,obj):
 with pathlib.Path(path).open('x') as f:json.dump(obj,f,indent=2,allow_nan=False);f.write('\n');f.flush();os.fsync(f.fileno())
 fd=os.open(pathlib.Path(path).parent,os.O_RDONLY)
 try:os.fsync(fd)
 finally:os.close(fd)
def main():
 grant_path,expected=sys.argv[1:];g=capture_json(grant_path,expected,65536)
 req(g['decision']=='GO_SBMR512_RUNTIME_METADATA_PHASE1_V1R1' and g['root_authorized'] is True and g['reviewer'] and g['author']!=g['reviewer'],'release')
 req(g['scientific_read']=='HOLD' and g['automatic_retry'] is False and g['output']==OUT,'scope')
 req(g['modules']==list(MODULES) and g['allowed_roots']==list(ALLOWED_ROOTS),'finite import/file scope')
 req(isinstance(g['path_aliases'],list) and len(g['path_aliases'])<=4,'literal alias count cap')
 req(g['max_library_bytes']==MAX_LIBRARY and g['max_total_elf_bytes']==MAX_TOTAL and g['max_libraries']==MAX_LIBRARIES,'caps')
 req(g['model_construction'] is False and g['weights_images_npz'] is False,'no payload')
 req(type(g['loaded_elf_body_hash'])==bool and g['input_current_identity_receipt_sha256']=='7847e2007570f75012f36fccd9257f73231c9a28cafbfb38ba86c2286d76e61b','identity constraints')
 req(sys.flags.isolated==1 and sys.flags.no_site==1 and sys.flags.optimize==0 and sys.dont_write_bytecode,'isolated bootstrap flags')
 req(os.environ.get('SLURM_JOB_PARTITION')=='lem-gpu-interactive' and os.environ.get('SLURM_JOB_ID'),'native interactive receipt')
 # Shell NATIVE_JOB_ID/driver preallocation claims are separate and required.
 out=pathlib.Path(OUT);out.mkdir(exist_ok=False)
 put(out/'CLAIM.json',dict(grant_sha256=expected,scientific_read='HOLD',scope='IMPORT_RUNTIME_METADATA_ONLY_NO_MODEL',native_job_id=os.environ['SLURM_JOB_ID']))
 start=time.monotonic()
 try:
  driver_identity=driver_query(g,lambda identity:put(out/'DRIVER_TOOL_IDENTITY.json',identity))
  # Exact current native installation; no package scan, no .pth/sitecustomize execution.
  site='/home/narolski/dmenv/lib/python3.12/site-packages';sys.path.append(site)
  empty=out/'empty_home';empty.mkdir();os.environ['HOME']=str(empty);os.environ['HF_HOME']=str(empty/'hf');os.environ['TORCH_HOME']=str(empty/'torch');os.environ['XDG_CACHE_HOME']=str(empty/'cache');os.environ['HF_HUB_DISABLE_TELEMETRY']='1'
  os.environ['HF_HUB_OFFLINE']='1';os.environ['TRANSFORMERS_OFFLINE']='1';os.environ['HF_DATASETS_OFFLINE']='1'
  imported={}
  for name in MODULES:
   m=importlib.import_module(name);p=str(pathlib.Path(m.__file__).resolve());req(inside(p,ALLOWED_ROOTS),'module origin')
   imported[name]=dict(path=p,version=str(getattr(m,'__version__','UNKNOWN')))
  t=sys.modules['torch'];req(t.cuda.device_count()==1,'one GPU');name=t.cuda.get_device_name(0);req('H100' in name,'H100 required')
  defaults=dict(cudnn_benchmark=t.backends.cudnn.benchmark,cudnn_deterministic=t.backends.cudnn.deterministic,float32_matmul_precision=t.get_float32_matmul_precision(),default_dtype=str(t.get_default_dtype()),matmul_allow_tf32=t.backends.cuda.matmul.allow_tf32,cudnn_allow_tf32=t.backends.cudnn.allow_tf32)
  # Fixed proc file only, bounded same-descriptor read. No /proc traversal.
  with open('/proc/self/maps','rb') as f:maps=f.read(MAX_MAPS+1)
  libraries=[];total=0
  for mapped in parse_maps(maps):
   rec,n=file_identity(mapped,g['loaded_elf_body_hash'],MAX_TOTAL-total,g['path_aliases']);total+=n;libraries.append(rec)
  import multiprocessing
  put(out/'RECEIPT.json',dict(status='PROSPECTIVE_IMPORT_ONLY_NOT_HISTORICAL_NOT_FIRSTBATCH',modules=imported,python=dict(executable=sys.executable,prefix=sys.prefix,version=sys.version,flags=dict(isolated=sys.flags.isolated,no_site=sys.flags.no_site)),gpu=dict(name=name,count=t.cuda.device_count(),compute_capability=list(t.cuda.get_device_capability(0)),torch_cuda=t.version.cuda,cudnn_version=t.backends.cudnn.version()),backend_defaults=defaults,multiprocessing_start_method=multiprocessing.get_start_method(allow_none=True),loaded_shared_objects=libraries,total_elf_body_bytes=total,elapsed_seconds=time.monotonic()-start,full_loader_closure='NOT_CLAIMED',worker_site_startup_equivalence='NOT_CLAIMED_NO_SITE_USED',native_driver_metadata=driver_identity,historical_identity='UNKNOWN',model_constructed=False,forward_calls=0,weights_images_npz_access=False,scientific_read='HOLD'))
  put(out/'COMPLETE.json',dict(scope='TECHNICAL_RUNTIME_METADATA_ONLY',scientific_read='HOLD'))
 except BaseException as e:
  put(out/'FAILED.json',dict(error_type=type(e).__name__,status='HOLD_NO_AUTOMATIC_RETRY'));raise
if __name__=='__main__':main()
