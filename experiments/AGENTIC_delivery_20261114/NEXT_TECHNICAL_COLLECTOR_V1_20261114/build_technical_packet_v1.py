"""Source-only typed schema builder; no archive access."""
import ast,csv,hashlib,json,pathlib
R=pathlib.Path('/home/narolski/smad-next');B=R/'experiments/AGENTIC_delivery_20261114';V=B/'NEXT_ADMISSION_PROPOSAL_V2_20261114';O=B/'NEXT_TECHNICAL_COLLECTOR_V1_20261114'
O.mkdir(exist_ok=True)
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def read(p):return json.loads(p.read_text())
def const(p,names):
 out={}
 for node in ast.parse(p.read_text()).body:
  if isinstance(node,ast.Assign):
   for t in node.targets:
    if isinstance(t,ast.Name) and t.id in names:
     v=node.value
     out[t.id]={k.arg:ast.literal_eval(k.value) for k in v.keywords} if isinstance(v,ast.Call) and isinstance(v.func,ast.Name) and v.func.id=='dict' and not v.args else ast.literal_eval(v)
 return out
c=const(R/'src/NEXT/read_selection.py',{'PINS','ARM_SPEC'});w=const(R/'src/NEXT/native_adapters.py',{'W2_SCRIPTS'})
a=read(V/'ADMISSION_PROPOSAL.json');al=read(V/'TECHNICAL_METADATA_ALLOWLIST_PROPOSAL.json')
cfg=read(R/'src/recovery_20261114/sbfm_supplement/config.json')
def s(typ,value=None,**kwargs):
 d={'type':typ};d.update(kwargs)
 if value is not None:d['equals']=value
 if typ=='str' and 'one_of' in kwargs and all(v in ('tt1','meds') or v.startswith(('AB1_','AB1FM_')) for v in kwargs['one_of']):d['emit_registered']=True
 return d
def gate(name,h,manifest,n):
 return {'tar':s('str',name+'.tar'),'tar_sha256':s('str',h),'manifest':s('str',manifest),'n':s('int',n),'verdict':s('str','passed'),'n_differ':s('int',0),'max_abs':s('number',0),'own_rule_agree':s('number',1),'device':s('str','NVIDIA H100')}
counts={}
for k,m in a['native_manifests'].items():
 if k.startswith('train_'):
  with open(m['path']) as f:counts[k]=sum(1 for _ in csv.DictReader(f))
archives={}
for key,outer in al['archives'].items():
 record={k:outer[k] for k in ('archive','sha256')};record['members']={}
 n=a['networks'].get(key)
 for member in outer['members']:
  base=pathlib.PurePosixPath(member).name;spec=None
  if base=='gpu.txt':spec={'kind':'gpu'}
  elif base=='train.log':spec={'kind':'loss'}
  elif base=='guard.log':spec={'kind':'guard'}
  elif base=='task.env':spec={'kind':'env','expected':{'ARM':n['arm'],'SEED':n['seed'],'TASK':n['prefix']}}
  elif base=='rz1_transform.json':
   _,transform,res,_,_=c['ARM_SPEC'][n['arm']];spec={'kind':'json','schema':{'spec':s('str',transform),'res':s('int',res)}}
  elif base=='meta.json':
   meta={'seed':s('int',n['seed']),'steps':s('int',6250)}
   if n['format']=='rz1_fit':
    man,transform,res,bs,accum=c['ARM_SPEC'][n['arm']]
    meta.update(res=s('int',res),bs=s('int',bs),accum=s('int',accum),n_items=s('int',counts['train_A' if man=='train_A.csv' else 'train_Sb']))
   else:
    arch='a12_dinov3_vitl16_madation' if key.startswith('BB2L') else 'a12_clip_vitb16_madation'
    meta.update(res=s('int',224),arch=s('str',arch),n_items=s('int',counts['train_'+n['arm']]))
   spec={'kind':'json','schema':meta}
  elif base=='task_info.txt':
   if n['format']=='rz1_fit':
    _,transform,res,bs,accum=c['ARM_SPEC'][n['arm']];expected={k:[v] for k,v in c['PINS'].items()}
    expected.update(spec=[transform],primary=[transform if n['arm']=='Sbc' else 'fixed:pil_bilinear'],res=[str(res)],bs=[str(bs)],accum=[str(accum)],steps=['6250'],limit=['0'],skip_tt1=['0'])
   elif n['format']=='rz1_refit':expected={'source_tar':[n['source_network']['name'],n['source_network']['sha256']],'limit':['0']}
   else:
    overlay={'AB1':'171fdb213444442762d4a716b7470dd885cd5879ba9ddda0c542060af4b4d149','AB1FM':'e554b84f74e5de8791fddc168b99a7c46376ee48ab7902baf358ecbe668d8e47','BB2L':'7c0a0b41f2e7bf656dc49db33c34a33ef62b10e8f0aaec24e247e684098d0bad'}[key.split('_')[0]]
    expected={'pack_sha256':[c['PINS']['pack_sha256']],'overlay_sha256':[overlay],'steps':['6250'],'limit':['0'],'arch':['a12_dinov3_vitl16_madation' if key.startswith('BB2L') else 'a12_clip_vitb16_madation']}
    if key.startswith('BB2L'):expected.update(lr=['1.17e-05'],bs=['256'],accum=['1'])
   spec={'kind':'tokens','expected':expected}
  elif base=='gate.json':spec={'kind':'json','schema':gate(n['source_network']['name'][:-4],n['source_network']['sha256'],'ab1_eval.csv',21277)}
  elif base.startswith('gate_'):
   source=base[5:-5];src=a['networks'][source]
   manifest,rows=('pn1_eval.csv',19797) if source.startswith('BB2L') else (('ab1x_eval.csv',24859) if source.startswith('AB1FM') else ('ab1_eval.csv',21277))
   spec={'kind':'json','schema':gate(source,src['sha256'],manifest,rows)}
  elif base=='pre_read_receipt.json':spec={'kind':'opaque','expected_sha256':cfg['pre_read_receipt_sha256']}
  elif base=='config.json':
   model={'name':s('str',one_of=[x['name'] for x in cfg['models']]),'seed':s('int',one_of=list(range(408,413))),'sha256':s('str',one_of=[x['sha256'] for x in cfg['models']]),'gate_manifest':s('str',one_of=['ab1_eval.csv','ab1x_eval.csv']),'gate_rows':s('int',one_of=[21277,24859])}
   spec={'kind':'json','schema':{'schema':s('str','AB1FMSUPP-v1'),'expected_gpu':s('str','NVIDIA H100'),'pre_read_receipt_sha256':s('str',cfg['pre_read_receipt_sha256']),'models':{'*':model}}}
  elif base=='technical_status.json':
   model={'name':s('str',one_of=[x['name'] for x in cfg['models']]),'seed':s('int',one_of=list(range(408,413))),'gate':s('str','passed'),'families':{'*':{'name':s('str',one_of=['tt1','meds']),'valid':s('bool',True),'sha256':s('str',sha256=True)}}}
   spec={'kind':'json','schema':{'eight_row_smoke_passed':s('bool',True),'fits':s('int',0),'scientific_contrasts_read':s('bool',False),'models':{'*':model}}}
  elif base=='tasks.txt':spec={'kind':'tasks','expected':[f'BB2L_{arm}_s{seed}' for arm in ('A','B','Sb') for seed in range(403,408)]+[f'AB1_Sb_s{seed}' for seed in range(408,413)]}
  elif base=='scripts.sha256':spec={'kind':'scripts','expected':w['W2_SCRIPTS']}
  elif base in ('n_fail.txt','n_refused.txt'):spec={'kind':'count'}
  assert spec is not None,base
  record['members'][member]=spec
 archives[key]=record
pins={str(V/x):sha(V/x) for x in ['ADMISSION_PROPOSAL.json','TECHNICAL_METADATA_ALLOWLIST_PROPOSAL.json','SOURCE_BINDINGS.json','NATIVE_MANIFEST_BINDINGS_DRAFT.json','NEXT_PROPOSAL_V2_INDEPENDENT_DESIGN_REVIEW_20261114.md']}
for p in ['src/NEXT/read_selection.py','src/NEXT/native_adapters.py','src/recovery_20261114/sbfm_supplement/config.json']:pins[str(R/p)]=sha(R/p)
packet={'schema':'next-typed-technical-scope-v1','is_scientific_admission':False,'pins':pins,'archives':archives,'known_partial_checks':['loss recognizes unambiguous whole lines only; native loss gate stays HOLD','config/status array entries check membership, not positional source association: native gate stays HOLD','RZ1R metadata subset only; registered full provenance gate remains unread','exposure/author/kernel/GX remain HOLD']}
(O/'TYPED_SCOPE.json').write_text(json.dumps(packet,indent=2)+'\n')
print('TYPED_SCOPE_WRITTEN_77_ARCHIVES_NO_MEMBER_ACCESS')
