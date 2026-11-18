"""SOURCE ONLY: bounded prospective import/runtime observation, never a model build."""
import hashlib,importlib,json,os,pathlib,stat,subprocess,sys,time
MODULES=('numpy','PIL','torch','torchvision','timm')
ALLOWED_ROOTS=('/home/narolski/dmenv','/home/narolski/.local/share/uv/python/cpython-3.12.15-linux-x86_64-gnu','/usr/lib64','/lib64','/usr/lib/x86_64-linux-gnu','/lib/x86_64-linux-gnu')
MAX_MAPS=2<<20;MAX_LIBRARIES=512;MAX_LIBRARY=2<<30;MAX_TOTAL=4<<30
OUT='/lustre/pd03/hpc-narolski-1790461090/smad-next/RZ1/sbmr512_runtime_metadata_phase1_v1/result'
def req(v,msg):
 if not v:raise ValueError(msg)
def inside(path,roots):
 p=pathlib.Path(path)
 return p.is_absolute() and any(p==pathlib.Path(r) or pathlib.Path(r) in p.parents for r in roots)
def parse_maps(raw):
 req(len(raw)<=MAX_MAPS,'maps cap');paths=set()
 for line in raw.decode('utf-8',errors='strict').splitlines():
  cells=line.split(None,5)
  if len(cells)<6 or not cells[5].startswith('/'):continue
  path=cells[5];req(not path.endswith(' (deleted)'),'deleted mapping')
  name=pathlib.Path(path).name
  # Only loaded shared-object file class; never model/cache/data or arbitrary maps.
  if '.so' not in name:continue
  req(inside(path,ALLOWED_ROOTS),'loaded library outside exact granted roots')
  paths.add(path)
 req(len(paths)<=MAX_LIBRARIES,'library count cap');return sorted(paths)
def file_identity(path,body,remaining):
 req(inside(path,ALLOWED_ROOTS),'root')
 fd=os.open(path,os.O_RDONLY|os.O_NOFOLLOW)
 try:
  a=os.fstat(fd);req(stat.S_ISREG(a.st_mode) and a.st_size<=MAX_LIBRARY,'file class/size')
  rec=dict(path=path,bytes=a.st_size,device=a.st_dev,inode=a.st_ino,mtime_ns=a.st_mtime_ns)
  if body:
   req(a.st_size<=remaining,'aggregate body cap');head=os.read(fd,4);req(head==b'\x7fELF','not ELF')
   h=hashlib.sha256(head);count=4
   while True:
    chunk=os.read(fd,4<<20)
    if not chunk:break
    count+=len(chunk);req(count<=a.st_size,'file growth');h.update(chunk)
   b=os.fstat(fd);req((a.st_dev,a.st_ino,a.st_size,a.st_mtime_ns)==(b.st_dev,b.st_ino,b.st_size,b.st_mtime_ns) and count==a.st_size,'unstable file')
   rec['sha256']=h.hexdigest();rec['scope']='ACTUALLY_LOADED_ELF_CURRENT_BODY_ONLY'
  else:rec['sha256']=None;rec['scope']='LOADED_SO_PATH_STAT_ONLY_NO_BODY_IDENTITY'
  return rec,a.st_size if body else 0
 finally:os.close(fd)
def put(path,obj):
 with pathlib.Path(path).open('x') as f:json.dump(obj,f,indent=2,allow_nan=False);f.write('\n');f.flush();os.fsync(f.fileno())
 fd=os.open(pathlib.Path(path).parent,os.O_RDONLY)
 try:os.fsync(fd)
 finally:os.close(fd)
def main():
 grant_path,expected=sys.argv[1:];raw=pathlib.Path(grant_path).read_bytes();req(len(raw)<=65536 and hashlib.sha256(raw).hexdigest()==expected,'grant')
 g=json.loads(raw)
 req(g['decision']=='GO_SBMR512_RUNTIME_METADATA_PHASE1_V1' and g['root_authorized'] is True and g['reviewer'] and g['author']!=g['reviewer'],'release')
 req(g['scientific_read']=='HOLD' and g['automatic_retry'] is False and g['output']==OUT,'scope')
 req(g['modules']==list(MODULES) and g['allowed_roots']==list(ALLOWED_ROOTS),'finite import/file scope')
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
  # Fixed root-pinned driver metadata tool only; no shell, no model/data.
  tool='/usr/bin/nvidia-smi';req(g['nvidia_smi_path']==tool and isinstance(g['nvidia_smi_sha256'],str) and len(g['nvidia_smi_sha256'])==64,'driver tool pin')
  fd=os.open(tool,os.O_RDONLY|os.O_NOFOLLOW)
  try:
   st=os.fstat(fd);req(stat.S_ISREG(st.st_mode) and st.st_size<=32<<20,'driver tool cap');h=hashlib.sha256()
   for chunk in iter(lambda:os.read(fd,1<<20),b''):h.update(chunk)
   req(h.hexdigest()==g['nvidia_smi_sha256'],'driver tool changed')
  finally:os.close(fd)
  query=subprocess.run([tool,'--query-gpu=driver_version','--format=csv,noheader,nounits'],capture_output=True,timeout=5,check=True)
  req(len(query.stdout)<=16384 and len(query.stderr)<=16384,'driver output cap')
  driver_rows=query.stdout.decode('utf-8').strip().splitlines();req(1<=len(driver_rows)<=16 and len(set(driver_rows))==1,'driver version rows')
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
  for path in parse_maps(maps):
   rec,n=file_identity(path,g['loaded_elf_body_hash'],MAX_TOTAL-total);total+=n;libraries.append(rec)
  import multiprocessing
  put(out/'RECEIPT.json',dict(status='PROSPECTIVE_IMPORT_ONLY_NOT_HISTORICAL_NOT_FIRSTBATCH',modules=imported,python=dict(executable=sys.executable,prefix=sys.prefix,version=sys.version,flags=dict(isolated=sys.flags.isolated,no_site=sys.flags.no_site)),gpu=dict(name=name,count=t.cuda.device_count(),compute_capability=list(t.cuda.get_device_capability(0)),torch_cuda=t.version.cuda,cudnn_version=t.backends.cudnn.version()),backend_defaults=defaults,multiprocessing_start_method=multiprocessing.get_start_method(allow_none=True),loaded_shared_objects=libraries,total_elf_body_bytes=total,elapsed_seconds=time.monotonic()-start,full_loader_closure='NOT_CLAIMED',worker_site_startup_equivalence='NOT_CLAIMED_NO_SITE_USED',native_driver_metadata=driver_rows[0],historical_identity='UNKNOWN',model_constructed=False,forward_calls=0,weights_images_npz_access=False,scientific_read='HOLD'))
  put(out/'COMPLETE.json',dict(scope='TECHNICAL_RUNTIME_METADATA_ONLY',scientific_read='HOLD'))
 except BaseException as e:
  put(out/'FAILED.json',dict(error_type=type(e).__name__,status='HOLD_NO_AUTOMATIC_RETRY'));raise
if __name__=='__main__':main()
