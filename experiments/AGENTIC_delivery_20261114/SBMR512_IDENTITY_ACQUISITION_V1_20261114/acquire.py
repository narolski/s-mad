"""First identity acquisition: fixed source/install metadata only, never model imports."""
import argparse, hashlib, json, os, pathlib, re, sys
import importlib.util
_spec=importlib.util.spec_from_file_location("safeio",pathlib.Path(__file__).absolute().with_name("safeio.py"))
safeio=importlib.util.module_from_spec(_spec);_spec.loader.exec_module(safeio)

VENV = '/home/narolski/dmenv'
OUTPUT = '/lustre/pd03/hpc-narolski-1790461090/smad-next/coordination_20261114/sbmr512_identity_acquisition_v1'
INTERPRETER = VENV + '/bin/python'
DEPS = ('torch','torchvision','timm','numpy','Pillow','opencv-python','opencv-python-headless','transformers','huggingface-hub','safetensors','tokenizers')
MODULES = ('torch','torchvision','timm','numpy','PIL','cv2','transformers','huggingface_hub','safetensors','tokenizers')
SOURCES = (
 'torch/__init__.py','torch/version.py','torch/nn/functional.py','torch/backends/cuda/__init__.py',
 'torchvision/transforms/transforms.py','torchvision/transforms/functional.py',
 'timm/__init__.py','timm/models/_factory.py','timm/models/_builder.py','timm/models/_helpers.py',
 'timm/models/vision_transformer.py','timm/layers/pos_embed.py','timm/layers/attention.py',
 'timm/layers/mlp.py','timm/layers/patch_embed.py',
 'PIL/Image.py','numpy/__init__.py','cv2/__init__.py',
 'huggingface_hub/__init__.py','safetensors/__init__.py','transformers/__init__.py')
MAX_TOTAL = 256 << 20
def require(ok, msg):
 if not ok: raise ValueError(msg)
def normal(name): return re.sub('[-_.]+','-',name).lower()
def dist_name(entry):
 for name in DEPS:
  prefix = name.replace('-','_') + '-'
  if entry.lower().startswith(prefix.lower()) and entry.endswith('.dist-info'):
   version=entry[len(prefix):-len('.dist-info')]
   if re.fullmatch(r'[A-Za-z0-9][A-Za-z0-9.!+_-]*',version): return name
 return None
def names(path, limit):
 fd=safeio.directory_fd(path)
 try:
  # Iterator limits directory entry processing without recursive traversal.
  with os.scandir(fd) as it:
   out=[]
   for item in it:
    require(len(out)<limit,'directory_entry_limit')
    out.append(item.name)
  return sorted(out)
 finally: os.close(fd)
class Reader:
 def __init__(self): self.used=0
 def get(self,path,cap,capture=False):
  require(self.used<MAX_TOTAL,'aggregate_limit')
  try:
   raw,h,n=safeio.snapshot(path,min(cap,MAX_TOTAL-self.used),capture=capture)
  except FileNotFoundError: return None,dict(path=path,status='UNKNOWN_ABSENT')
  self.used+=n
  return raw,dict(path=path,sha256=h,bytes=n,status='CONTENT_HASHED_CURRENT_ONLY')
def interpreter(reader,venv=VENV):
 path=venv+'/bin/python';chain=[]
 for _ in range(8):
  parent=safeio.directory_fd(str(pathlib.PurePosixPath(path).parent))
  try:
   try: target=os.readlink(pathlib.PurePosixPath(path).name,dir_fd=parent)
   except OSError as e:
    if e.errno!=22: raise
    target=None
  finally: os.close(parent)
  if target is None:
   _,entry=reader.get(path,128<<20)
   require(entry['status']!='UNKNOWN_ABSENT','interpreter_absent')
   return dict(requested=venv+'/bin/python',resolved=path,symlink_chain=chain,content=entry)
  require(len(target)<=4096,'link_target_limit')
  resolved=os.path.normpath(target if target.startswith('/') else str(pathlib.PurePosixPath(path).parent/target))
  require(any(resolved.startswith(p+'/') for p in (venv,'/usr/bin','/usr/local/bin','/opt')),'interpreter_target_outside_grant')
  chain.append(dict(path=path,target=target,resolved=resolved));path=resolved
 raise ValueError('symlink_chain_limit')
def collect(venv=VENV):
 # venv override exists for generated fixtures only; CLI never accepts a path override.
 reader=Reader();answer=dict(status='CURRENT_IDENTITY_ACQUISITION_NOT_HISTORICAL',venv=venv)
 answer['interpreter']=interpreter(reader,venv)
 raw,entry=reader.get(venv+'/pyvenv.cfg',65536,True)
 fields={}
 if raw is not None:
  for line in raw.decode('utf-8').splitlines():
   if '=' in line:
    key,val=line.split('=',1);key=key.strip()
    if key in ('home','include-system-site-packages','version','version_info','executable'):
     require(key not in fields,'duplicate_pyvenv_key');fields[key]=val.strip()
 answer['pyvenv_cfg']=dict(entry,selected_fields=fields)
 try: libnames=names(venv+'/lib',128)
 except FileNotFoundError: libnames=[]
 versions=[n for n in libnames if re.fullmatch(r'python3\.[0-9]{1,2}',n)]
 require(len(versions)<=4,'python_directory_limit')
 answer['site_packages']=[]
 for version in versions:
  site=venv+'/lib/'+version+'/site-packages'
  try: entries=names(site,20000)
  except FileNotFoundError:
   answer['site_packages'].append(dict(path=site,status='UNKNOWN_ABSENT'));continue
  selected=[n for n in entries if n in MODULES or dist_name(n)]
  ds=[n for n in selected if dist_name(n)]
  require(len(ds)<=len(DEPS),'metadata_directory_limit')
  require(len({normal(dist_name(n)) for n in ds})==len(ds),'duplicate_distribution')
  record=dict(path=site,relevant_entry_names=selected,distributions=[],source_files=[])
  for d in ds:
   name=dist_name(d);meta=site+'/'+d
   _,rec=reader.get(meta+'/RECORD',16<<20)
   raw,metadata=reader.get(meta+'/METADATA',16<<20,True)
   fields=safeio.metadata_fields(raw,name) if raw is not None else None
   record['distributions'].append(dict(name=name,metadata_root=site,metadata_dir=meta,record=rec,metadata=metadata,fields=fields))
  # Fixed exact filenames, no import-based discovery, package execution, recursion or native binary scan.
  for rel in SOURCES:
   if rel.split('/')[0] in selected:
    _,item=reader.get(site+'/'+rel,4<<20);record['source_files'].append(item)
  answer['site_packages'].append(record)
 answer.update(bytes_read=reader.used,historical_executed_identity='UNKNOWN',backend_defaults='UNKNOWN',
               weights_images_checkpoint_schema='NOT_ACCESSED',scientific_read='HOLD',
               target_interpreter_executed=False,native_bytegate='NOT_RUN')
 return answer
def main():
 ap=argparse.ArgumentParser();ap.add_argument('--release',required=True);a=ap.parse_args()
 release,rh=safeio.control(a.release)
 require(sys.flags.isolated==1 and sys.flags.no_site==1 and sys.flags.optimize==0,'startup_flags')
 require(release['decision']=='GO_SBMR512_FIXED_IDENTITY_ACQUISITION_V1' and release['root_authorized'] is True,'root_grant')
 require(release['author']!=release['reviewer'] and bool(release['reviewer']),'other_review')
 require(release['venv']==VENV and release['output']==OUTPUT and release['automatic_retry'] is False,'fixed_paths')
 require(release['scope']=='FIXED_CURRENT_SOURCE_INSTALL_METADATA_ONLY' and release['scientific_read']=='HOLD','scope')
 safeio.snapshot(release['independent_review_path'],4<<20,expected_hash=release['independent_review_sha256'],capture=False)
 here=pathlib.Path(__file__).absolute().parent
 for name in ('acquire.py','safeio.py'):
  safeio.snapshot(str(here/name),4<<20,expected_hash=release['source_sha256'][name],capture=False)
 # Bootstrap interpreter is separately root-pinned, not the target interpreter being discovered.
 require(os.path.realpath(sys.executable)==release['bootstrap_interpreter'],'bootstrap_identity')
 safeio.snapshot(release['bootstrap_interpreter'],128<<20,expected_hash=release['bootstrap_interpreter_sha256'],capture=False)
 parent=safeio.directory_fd(str(pathlib.PurePosixPath(OUTPUT).parent))
 try:
  os.mkdir(pathlib.PurePosixPath(OUTPUT).name,0o700,dir_fd=parent);os.fsync(parent)
  out=safeio.directory_fd(OUTPUT)
 finally: os.close(parent)
 try:
  safeio.put(out,'CLAIM.json',dict(release_sha256=rh,automatic_retry=False))
  try:
   result=collect();result['release_sha256']=rh
   h=safeio.put(out,'RECEIPT.json',result)
   safeio.put(out,'COMPLETE.json',dict(receipt_sha256=h,scientific_read='HOLD'))
  except BaseException as e:
   safeio.put(out,'FAILED.json',dict(error_type=type(e).__name__,status='HOLD_NO_RETRY'))
   return 1
 finally: os.close(out)
 return 0
if __name__=='__main__': sys.exit(main())
