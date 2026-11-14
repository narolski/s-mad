"""Narrow source-only correction of RZ native fragments; frozen v2 untouched."""
import ast,hashlib,json,pathlib
R=pathlib.Path('/home/narolski/smad-next');B=R/'experiments/AGENTIC_delivery_20261114';V=B/'NEXT_TECHNICAL_COLLECTOR_V2_20261114';O=B/'NEXT_TECHNICAL_COLLECTOR_V2R1_20261114'
assert not O.exists(),'new namespace required'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
scope=json.loads((V/'TYPED_SCOPE.json').read_text())
pins=None
for node in ast.parse((R/'src/NEXT/read_selection.py').read_text()).body:
 if isinstance(node,ast.Assign) and any(isinstance(t,ast.Name) and t.id=='PINS' for t in node.targets):pins={k.arg:ast.literal_eval(k.value) for k in node.value.keywords}
assert pins is not None
changed=[]
for key,record in scope['archives'].items():
 if record.get('format')!='rz1_fit':continue
 spec=record['members'][record['prefix']+'/task_info.txt'];e=spec['expected']
 fragments=[f'{k} {v}' for k,v in pins.items()]
 fragments += ['spec '+e['spec'][0]+' ','primary '+e['primary'][0]+' ','res '+e['res'][0]+' bs '+e['bs'][0]+' accum '+e['accum'][0]+' ','steps 6250 limit 0 skip_tt1 0']
 spec['native_fragments']=fragments;changed.append(key)
scope['schema']='next-typed-technical-scope-v2r1'
for name in ['TYPED_SCOPE.json','PACKAGE_SHA256SUMS','INDEPENDENT_IMPLEMENTATION_REVIEW_20261114.md','INDEPENDENT_IMPLEMENTATION_CHECKS_20261114.json']:
 scope['pins'][str(V/name)]=sha(V/name)
assert len(scope['archives'])==77
O.mkdir()
(O/'TYPED_SCOPE.json').write_text(json.dumps(scope,indent=2)+'\n')
for name in ['UNKNOWN_PROOFS.json']:(O/name).write_bytes((V/name).read_bytes())
(O/'DELTA.json').write_text(json.dumps({'parent_package_sha256':sha(V/'PACKAGE_SHA256SUMS'),'review_sha256':sha(V/'INDEPENDENT_IMPLEMENTATION_REVIEW_20261114.md'),'changed_rz_fit_records':changed,'archive_count':77,'member_scope_unchanged':True,'change':'Exact source PINS+four native fragments; individual token constraints strict-only','actual_member_access':False},indent=2)+'\n')
print('V2R1_PREPARED_SOURCE_ONLY')
