"""Exercise all 77 schema records with synthetic metadata; no real archives."""
import hashlib,io,json,pathlib,sys,tarfile,tempfile
import technical_collector_v1 as c

def value(schema):
 if '*' in schema:return [value(schema['*'])]
 if 'type' not in schema:return {k:value(v) for k,v in schema.items()}
 if 'equals' in schema:return schema['equals']
 if 'one_of' in schema:return schema['one_of'][0]
 return {'int':1,'number':0.0,'bool':True,'str':'a'*64}[schema['type']]

def raw(spec,canary):
 kind=spec['kind']
 if kind=='json':
  obj=value(spec['schema']);obj.update(AUC=canary,EER=canary,APCER=canary,BPCER=canary,val_metrics={'scores':[canary]})
  return json.dumps(obj).encode()
 if kind=='opaque':return ('opaque canary '+str(canary)).encode()
 if kind=='tasks':return '\n'.join(spec['expected']).encode()
 if kind=='scripts':return '\n'.join(h+' '+n for n,h in spec['expected'].items()).encode()
 if kind=='count':return b'0'
 base={'loss':'loss=0.5\n','guard':'RZ1 GUARD pre ok\nRZ1 GUARD post ok\n','gpu':'NVIDIA H100\n','tokens':'','env':''}[kind]
 if kind=='tokens':base=' '.join(k+' '+' '.join(v) for k,v in spec['expected'].items())+'\n'
 if kind=='env':base='\n'.join(k+'='+str(v) for k,v in spec['expected'].items())+'\n'
 return (base+'AUC '+str(canary)+' EER '+str(canary)+'\nval_loss='+str(canary)+'\n').encode()

def without_hashes(obj):
 if isinstance(obj,dict):return {k:without_hashes(v) for k,v in obj.items() if k!='opaque_sha256'}
 if isinstance(obj,list):return [without_hashes(v) for v in obj]
 return obj

packet=json.loads(pathlib.Path(sys.argv[1]).read_text());assert len(packet['archives'])==77
count=0
with tempfile.TemporaryDirectory() as tmp:
 for key,record in packet['archives'].items():
  outputs=[]
  for canary in (0.123456789,987654.321):
   path=pathlib.Path(tmp)/'synthetic.tar'
   with tarfile.open(path,'w') as tf:
    for name,spec in record['members'].items():
     data=raw(spec,canary);info=tarfile.TarInfo(name);info.size=len(data);tf.addfile(info,io.BytesIO(data))
   out=c.collect_archive(dict(record,archive=str(path.resolve()),sha256=hashlib.sha256(path.read_bytes()).hexdigest()))
   assert out['status']=='COLLECTED_TECHNICAL_ONLY'
   assert len(out['members'])==len(record['members'])
   assert all('reason' not in m for m in out['members'].values())
   assert str(canary) not in json.dumps(out)
   outputs.append(without_hashes(out))
  assert outputs[0]==outputs[1],key
  count+=1
print(json.dumps({'synthetic_archive_records':count,'canary_variants_per_record':2,'all_checks_passed':True,'real_archive_access':False}))
