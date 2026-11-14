"""Differential synthetic primitives from pinned source AST; no loader imports.

Only the RZ expected-fragment construction and native token helper are compiled
in isolation. Neither canonical loader nor any archive/data operation is called.
"""
import ast,copy,hashlib,json,math,os,pathlib,re,unittest
import native_metadata_predicates_v2 as p

ROOT=pathlib.Path(os.environ.get('NEXT_SOURCE_ROOT','/home/narolski/smad-next'))
SCOPE=pathlib.Path(os.environ.get('NEXT_TYPED_SCOPE',str(ROOT/'experiments/AGENTIC_delivery_20261114/NEXT_TECHNICAL_COLLECTOR_V2R1_20261114/TYPED_SCOPE.json')))

class SourceEquivalence(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  cls.scope=json.loads(SCOPE.read_text());rz=(ROOT/'src/NEXT/read_selection.py').read_bytes();native=(ROOT/'src/NEXT/native_adapters.py').read_bytes()
  assert hashlib.sha256(rz).hexdigest()=='f20f42578275aa3d92b8c695ab86827a526b7f62016b98ec242bf17c0b390830'
  assert hashlib.sha256(native).hexdigest()=='ebb40edda27a08034a6087a737109509e65c3c5ad76c748767cd19a49f2ff17c'
  tree=ast.parse(rz);ntree=ast.parse(native)
  cls.pins={}
  for n in tree.body:
   if isinstance(n,ast.Assign) and any(isinstance(t,ast.Name) and t.id=='PINS' for t in n.targets):cls.pins={k.arg:ast.literal_eval(k.value) for k in n.value.keywords}
  # Exactly source lines constructing PINS + four required fragments.
  nodes=[n for n in ast.walk(tree) if isinstance(n,(ast.Assign,ast.AugAssign)) and n.lineno in (572,573,574)]
  assert len(nodes)==3
  cls.fragment_code=compile(ast.fix_missing_locations(ast.Module(body=sorted(nodes,key=lambda n:n.lineno),type_ignores=[])),'<source-fragments-only>','exec')
  token=next(n for n in ast.walk(ntree) if isinstance(n,ast.FunctionDef) and n.name=='token')
  cls.token_code=compile(ast.fix_missing_locations(ast.Module(body=[token],type_ignores=[])),'<source-token-helper-only>','exec')

 def test_every_rz_recipe_fragment_against_source(self):
  count=0
  for key,record in self.scope['archives'].items():
   if record.get('format')!='rz1_fit':continue
   member=key+'/task_info.txt';spec=record['members'][member];e=spec['expected']
   env=dict(PINS=self.pins,arm=record['arm'],spec=e['spec'][0],res=int(e['res'][0]),bs=int(e['bs'][0]),accum=int(e['accum'][0]))
   exec(self.fragment_code,env);expected=env['expected']
   self.assertEqual(spec['native_fragments'],expected)
   base=' '.join(k+' '+' '.join(v) for k,v in e.items())
   variants=[base,base+' ',base+'\t',base+'\n',base.replace(' ','\t'),base.replace(' ','\n'),base.replace('res '+e['res'][0]+' bs','bs '+e['bs'][0]+' res'),base.replace(' bs ',' unexpected bs ')]
   for field in self.pins:variants.append(base.replace(e[field][0],e[field][0]+'suffix',1))
   variants += [base.replace('skip_tt1 0','skip_tt1 0suffix'),base.replace('spec '+e['spec'][0]+' ','spec '+e['spec'][0]+'suffix ')]
   for text in variants:
    rows=p.evaluate(record,{member:text});native=[r for r in rows if r['predicate'].startswith('recipe.grouped_fragment_')]
    self.assertEqual([r['native_status']=='PASS' for r in native],[v in text+' ' for v in expected])
    self.assertTrue(all(r['native_status']=='UNKNOWN' for r in rows if r['predicate'].startswith('recipe.') and not r['predicate'].startswith('recipe.grouped_fragment_')))
    count+=1
   suffix=base.replace(e['pack_sha256'][0],e['pack_sha256'][0]+'suffix',1)
   row=next(r for r in p.evaluate(record,{member:suffix}) if r['predicate']=='recipe.pack_sha256')
   self.assertEqual(row['strict_integrity_status'],'FAIL')
  self.assertGreater(count,500)

 def test_every_native_fit_recipe_token_against_source(self):
  for key,record in self.scope['archives'].items():
   if record.get('format')!='native_fit':continue
   member=key+'/task_info.txt';e=record['members'][member]['expected'];base=' '.join(k+' '+' '.join(v) for k,v in e.items())
   for text in [base,base.replace(' ','\t'),base.replace(' ','\n'),base+' steps 6250',base.replace('6250','6250suffix')]:
    ns={'tokens':text.split()};exec(self.token_code,ns)
    rows={r['predicate']:r for r in p.evaluate(record,{member:text})}
    for k,v in e.items():self.assertEqual(rows['recipe.'+k]['native_status']=='PASS',ns['token'](k,v[0]))

 def test_every_refit_raw_substring(self):
  for key,record in self.scope['archives'].items():
   if record.get('format')!='rz1_refit':continue
   member=key+'/task_info.txt';e=record['members'][member]['expected'];base=' '.join(k+' '+' '.join(v) for k,v in e.items())
   for text in [base,base+'suffix',base.replace(' ','\t'),base.replace('limit 0','limit 0suffix'),base+base]:
    rows={r['predicate']:r for r in p.evaluate(record,{member:text})}
    for k,v in e.items():self.assertEqual(rows['recipe.'+k]['native_status']=='PASS',(k+' '+' '.join(v)) in text)

 def test_numeric_equality_and_boolean_source_families(self):
  for wanted in [0,1,408,6250,512,'passed','NVIDIA H100']:
   typ='int' if type(wanted) is int else 'str'
   for actual in [False,True,0,1,408,6250,512,'0','1','passed',None,[],{}]:
    rows=[];p.compare_json(rows,'field',{'x':actual},{'x':{'type':typ,'equals':wanted}},'source','member')
    self.assertEqual(rows[0]['native_status']=='PASS',actual==wanted)
  for wanted in (True,False):
   for actual in (0,1,True,False,'true','false',None):
    rows=[];p.compare_json(rows,'flag',{'x':actual},{'x':{'type':'bool','equals':wanted}},'source','member')
    self.assertEqual(rows[0]['native_status']=='PASS',actual is wanted)

 def test_env_gpu_guard_types_substrings(self):
  for fmt in ('native_fit','rz1_fit'):
   rec={'format':fmt,'members':{'task.env':{'kind':'env','source':'source','expected':{'ARM':'Sb','SEED':408,'TASK':'x'}},'gpu.txt':{'kind':'gpu','source':'source'},'guard.log':{'kind':'guard','source':'source'}}}
   for text in ['ARM=Sb\nSEED=408\nTASK=x','ARM=Sb\nARM=Sb\nSEED=408\nTASK=x','prefixARM=Sb\nSEED=408\nTASK=x','ARM=Sb\r\nSEED=408\r\nTASK=x']:
    rows={r['predicate']:r for r in p.evaluate(rec,{'task.env':text,'gpu.txt':'prefixH100suffix','guard.log':'prefixRZ1 GUARD pre oksuffix RZ1 GUARD post ok'})}
    for k,v in rec['members']['task.env']['expected'].items():
     if fmt=='rz1_fit' and k=='TASK':self.assertEqual(rows['task_env.'+k]['native_status'],'UNKNOWN');continue
     ref=(f'{k}={v}\n' in text+'\n') if fmt=='rz1_fit' else text.splitlines().count(f'{k}={v}')==1
     self.assertEqual(rows['task_env.'+k]['native_status']=='PASS',ref)
    self.assertEqual(rows['gpu_substring']['native_status'],'PASS');self.assertEqual(rows['pre_post_guard']['native_status'],'PASS')

 def test_counter_int_raw_semantics(self):
  record={'members':{'n_fail.txt':{'kind':'count','source':'source'}}}
  for text in ['0','+0',' -1 ','0001','1_0','１','1.0','False','9999999999999999999999','']:
   row=p.evaluate(record,{'n_fail.txt':text})[0]
   try:ref='PASS' if int(text)>=0 else 'FAIL'
   except ValueError:ref='UNKNOWN'
   self.assertEqual(row['native_status'],ref)

 def test_exact_loss_reference_both_native_branches(self):
  for text in ['','loss=0.25','val_loss = nan','loss +inf','loss 0.125abc','loss nan loss .','loss . loss nan','loss 1e999','"loss":0.2','LOSS=0.0\rLOSS=-1.0','loss_norm=1']:
   vals=re.findall(r'loss[ =:]+(-?(?:inf|nan)|[-+0-9.eE]+)',text,re.I);out=p.loss_predicate(text)
   for branch in ('native_fit','rz1_fit'):
    try:
     v=vals if branch=='native_fit' else [float(x) for x in vals]
     ref='PASS' if v and all(math.isfinite(float(x)) for x in v) else 'FAIL'
    except ValueError:ref='UNKNOWN'
    self.assertEqual(out[branch]['status'],ref)

if __name__=='__main__':unittest.main()
