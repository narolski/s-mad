"""BB2 exact recipe match + SbMR512 trainable member opaque digest only.

Synthetic tests may call collect_record. Real CLI requires explicit root release
before opening any archive. No model, NPZ, checkpoint decoder or native reader.
"""
import argparse,hashlib,json,os,pathlib,re,stat,tarfile
MAX_TEXT=8*1024*1024
MAX_HEADERS=100000

class Refusal(Exception):pass
def need(ok,code):
 if not ok:raise Refusal(code)
def sha(data):return hashlib.sha256(data).hexdigest()

def token_checks(text,expected):
 tokens=text.split();out={}
 for key,value in expected.items():
  ix=[i for i,t in enumerate(tokens) if t==key]
  present=len(ix)>0;complete=len(ix)==1 and ix[0]+1<len(tokens)
  match=complete and tokens[ix[0]+1]==str(value)
  status='UNKNOWN' if not present or (len(ix)==1 and not complete) else ('PASS' if match else 'FAIL')
  out[key]={'status':status,'native_unique_token_match':match,'reason':'EXPECTED_MATCH' if match else 'MISSING_OR_INCOMPLETE' if status=='UNKNOWN' else 'WRONG_OR_DUPLICATED_TOKEN'}
 return out

def env_checks(text,expected):
 lines=text.splitlines();out={}
 for key,value in expected.items():
  count=sum(x.startswith(key+'=') for x in lines)
  native=lines.count(key+'='+str(value))==1
  strict=count==1 and native
  out[key]={'status':'UNKNOWN' if count==0 else 'PASS' if strict else 'FAIL','native_exact_line_once':native,'strict_unique_key_match':strict}
 return out

def collect_record(record):
 result={'status':'HOLD','kind':record['kind'],'archive':record['archive'],'archive_sha256':record['sha256'],'members':{},'scientific_admission':False}
 temporary={}
 try:
  p=pathlib.Path(record['archive']);need(p.is_absolute() and p.resolve()==p,'ARCHIVE_PATH')
  with os.fdopen(os.open(p,os.O_RDONLY|os.O_NOFOLLOW),'rb') as stream:
   st=os.fstat(stream.fileno());need(stat.S_ISREG(st.st_mode),'ARCHIVE_TYPE');need(st.st_size==record['archive_bytes'],'ARCHIVE_SIZE')
   need(hashlib.file_digest(stream,'sha256').hexdigest()==record['sha256'],'ARCHIVE_HASH')
   stream.seek(0);seen=set();headers=0
   with tarfile.open(fileobj=stream,mode='r:') as tf:
    for member in tf:
     headers+=1;need(headers<=MAX_HEADERS,'TAR_HEADER_LIMIT')
     pp=pathlib.PurePosixPath(member.name);need(not pp.is_absolute() and '..' not in pp.parts,'TAR_PATH');name=str(pp)
     need(name not in seen,'TAR_DUPLICATE_ALIAS');seen.add(name)
     need((member.isfile() or member.isdir()) and not member.issparse(),'TAR_TYPE')
     if name not in record['members']:continue
     need(member.isfile() and 0<=member.size<=record['archive_bytes'],'MEMBER_TYPE_SIZE')
     spec=record['members'][name]
     need(spec['operation'] in ('opaque_sha256','recipe_tokens','task_env'),'OPERATION_SCOPE')
     with tf.extractfile(member) as f:
      if spec['operation']=='opaque_sha256':
       digest=hashlib.sha256();size=0
       while True:
        block=f.read(1024*1024)
        if not block:break
        size+=len(block);need(size<=member.size,'MEMBER_OVERREAD');digest.update(block)
       need(size==member.size,'MEMBER_TRUNCATED')
       temporary[name]={'status':'OPAQUE_DIGEST_ONLY','member':name,'bytes':size,'sha256':digest.hexdigest(),'checkpoint_identity':'last_trainable.pt trainable overlay; NOT original full last.pt','decoded':False}
      else:
       need(member.size<=MAX_TEXT,'TEXT_SIZE');raw=f.read(MAX_TEXT+1);need(len(raw)==member.size,'MEMBER_TRUNCATED')
       try:text=raw.decode('utf-8')
       except UnicodeError:temporary[name]={'status':'UNKNOWN','reason':'TEXT_ENCODING','opaque_sha256':sha(raw)};continue
       checks=token_checks(text,spec['expected']) if spec['operation']=='recipe_tokens' else env_checks(text,spec['expected'])
       temporary[name]={'status':'TECHNICAL_COMPARISONS_ONLY','checks':checks,'opaque_sha256':sha(raw)}
   for name in record['members']:
    temporary.setdefault(name,{'status':'UNKNOWN','reason':'MEMBER_ABSENT'})
   # Publish any hash only after full header safety/uniqueness traversal.
   result['members']=temporary;result['status']='COLLECTED_TECHNICAL_ONLY';result['unique_member_namespace_verified']=True
   if record['kind']=='bb2_batch_match':
    statuses=[v['status'] for m in temporary.values() for v in m.get('checks',{}).values()]
    complete=all('checks' in m for m in temporary.values()) and len(statuses)==5
    result['expected_256_1_and_task_match']='PASS' if complete and all(s=='PASS' for s in statuses) else 'FAIL' if 'FAIL' in statuses else 'UNKNOWN'
    result['native_job_export_provenance']='NOT_ESTABLISHED_BY_THIS_MATCH'
   else:result['checkpoint_reconstruction']='NOT_DECODED_NOT_VALIDATED'
 except Refusal as exc:result['reason']=str(exc);result['unique_member_namespace_verified']=False
 except Exception:result['reason']='ARCHIVE_OR_STREAM_ERROR';result['unique_member_namespace_verified']=False
 return result

def atomic(out,name,content):
 p=out/(name+'.partial')
 with p.open('x') as f:f.write(content);f.flush();os.fsync(f.fileno())
 os.rename(p,out/name)

def validate_scope(scope):
 need(scope['schema']=='next-minimal-technical-extension-v1','SCOPE_SCHEMA')
 bb={f'BB2L_{a}_s{s}' for a in ('A','B','Sb') for s in range(403,408)};rz={f'RZ1_SbMR512_s{s}' for s in range(408,413)}
 need(set(scope['records'])==bb|rz,'EXACT_TWENTY_ROSTER')
 for key,r in scope['records'].items():
  if key in bb:
   need(r['kind']=='bb2_batch_match' and set(r['members'])=={key+'/task_info.txt',key+'/task.env'},'BB2_SCOPE')
   need(r['members'][key+'/task_info.txt']=={'operation':'recipe_tokens','expected':{'bs':256,'accum':1}},'EXPECTED_BATCH_FIXED')
   need(r['members'][key+'/task.env']=={'operation':'task_env','expected':{'TASK':key,'ARM':key.split('_')[1],'SEED':int(key.rsplit('s',1)[1])}},'TASK_SCOPE')
  else:need(r['kind']=='sbmr512_trainable_hash' and r['members']=={key+'/last_trainable.pt':{'operation':'opaque_sha256'}},'CHECKPOINT_HASH_ONLY_SCOPE')

def main():
 parser=argparse.ArgumentParser();parser.add_argument('--scope',required=True);parser.add_argument('--release',required=True);parser.add_argument('--output',required=True);args=parser.parse_args()
 try:
  raw=pathlib.Path(args.scope).read_bytes();scope=json.loads(raw);release_raw=pathlib.Path(args.release).read_bytes();release=json.loads(release_raw);source_hash=sha(pathlib.Path(__file__).read_bytes());out=pathlib.Path(args.output)
  need(release.get('decision')=='GO_NEXT_MINIMAL_TECHNICAL_EXTENSION_V1','RELEASE_REQUIRED')
  need(release.get('real_member_access_authorized') is True and release.get('checkpoint_hash_only_no_decode') is True,'EXPLICIT_OPAQUE_SCOPE')
  need(release.get('expected_batch_binding_adopted') is True and release.get('prior_technical_postreview_adopted') is True,'ROOT_ADOPTIONS_REQUIRED')
  need(release.get('scope_sha256')==sha(raw) and release.get('collector_sha256')==source_hash,'RELEASE_PINS')
  need(release.get('cpu_only') is True and os.environ.get('CUDA_VISIBLE_DEVICES')=='','CPU_SCOPE')
  need(out.is_absolute() and out.resolve()==out and release.get('output')==str(out) and not out.exists(),'OUTPUT_GATE')
  review=pathlib.Path(release['implementation_review']);need(sha(review.read_bytes())==release['implementation_review_sha256'],'REVIEW_HASH')
  need('GO_NEXT_MINIMAL_TECHNICAL_EXTENSION '+source_hash in review.read_text().splitlines(),'REVIEW_DECISION')
  validate_scope(scope)
  for name,h in scope['pins'].items():need(sha(pathlib.Path(name).read_bytes())==h,'INPUT_PIN')
  out.mkdir()
  result={'schema':'next-minimal-technical-extension-result-v1','scientific_admission':False,'planned_seed_denominator':5,'scope_sha256':sha(raw),'release_sha256':sha(release_raw),'collector_sha256':source_hash,'records':{k:collect_record(r) for k,r in scope['records'].items()}}
  atomic(out,'TECHNICAL_EXTENSION.json',json.dumps(result,indent=2,allow_nan=False)+'\n')
  atomic(out,'SHA256SUMS',sha((out/'TECHNICAL_EXTENSION.json').read_bytes())+'  TECHNICAL_EXTENSION.json\n')
  atomic(out,'TECHNICAL_WRITE_COMPLETE','NOT_SCIENTIFIC_ADMISSION\n');fd=os.open(out,os.O_RDONLY);os.fsync(fd);os.close(fd)
  print('TECHNICAL_EXTENSION_WRITTEN_NOT_ADMISSION');return 0
 except Refusal as exc:print('HOLD '+str(exc));return 2
 except Exception:print('HOLD CONTROL_PLANE_ERROR');return 2

if __name__=='__main__':raise SystemExit(main())
