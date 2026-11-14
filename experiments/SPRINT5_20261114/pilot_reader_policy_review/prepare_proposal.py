import collections,hashlib,json,pathlib
R=pathlib.Path('/home/narolski/smad-next');O=R/'experiments/SPRINT5_20261114/pilot_reader_policy_review'
def sha(p):return hashlib.sha256(pathlib.Path(p).read_bytes()).hexdigest()
x=json.loads((O/'RESOLVED_CANDIDATE_INPUTS.json').read_text())
def clean(r):return not(r['training_person_overlap'] or r['training_photo_overlap'] or r['training_component_overlap'])
def fam(r):
 if r['fam']=='af0' and r['rung']=='u50' and r['strength']=='':return 'af0_u50'
 if r['fam']=='ladder' and r['rung']=='R4' and r['tool']=='opencv' and r['strength']=='':return 'lad_R4'
 if r['fam']=='splice' and r['rung']=='S4' and r['strength']=='':return 'lad_S4'
 return None
p=[dict(r,positive_family=fam(r)) for r in x['positive'] if clean(r) and fam(r)]
comps={r['component']:r['source'] for r in p};assert all(len({r['source'] for r in p if r['component']==c})==1 for c in comps)
cal=set();rule='SPRINT5_3_POSITIVE_CALIBRATION_V1|'
for source in sorted(set(comps.values())):
 cs=sorted([c for c in comps if comps[c]==source],key=lambda c:(hashlib.sha256((rule+c).encode()).hexdigest(),c));cal.update(cs[:len(cs)//2])
C=[r for r in p if r['component'] in cal];P=[r for r in p if r['component'] not in cal]
G=[r for r in x['camera'] if clean(r) and r['component'] not in cal]
assert C and P and G
for rr in [P,G]:
 assert not {v for r in C for v in r['persons']}&{v for r in rr for v in r['persons']}
 assert not {v for r in C for v in r['photos']}&{v for r in rr for v in r['photos']}
 assert not {r['component'] for r in C}&{r['component'] for r in rr}
for r in G:r['processing']={'':'native','61':'s61','112':'s112'}[r['strength']]
family_order=['af0_u50','af0_u5061','lad_R4','lad_S4'];guards=[]
for family in family_order:
 rr=[r for r in P if r['positive_family']==family];guards.append({'family':family,'ids':[r['id'] for r in rr],'n_rows':len(rr),'n_components':len({r['component'] for r in rr}),'status_without_scores':'MISSING_FAMILY' if not rr else ('SPARSE_LT20' if len({r['component'] for r in rr})<20 else 'SUPPORTED_METADATA_ONLY')})
cells=[]
for source in ['feret','frgc']:
 for processing in ['native','s61','s112']:
  rr=[r for r in G if r['source']==source and r['processing']==processing];cells.append({'source':source,'processing':processing,'ids':[r['id'] for r in rr],'n_rows':len(rr),'n_people':len({v for r in rr for v in r['persons']}),'n_components':len({r['component'] for r in rr})})
for name,rr in [('TAIL_POSITIVE_CALIBRATION_PROPOSAL',C),('TAIL_POSITIVE_EVALUATION_PROPOSAL',P),('TAIL_GENUINE_EVALUATION_PROPOSAL',G)]:
 (O/(name+'.json')).write_text(json.dumps(rr,indent=2)+'\n')
pins={str(O/(name+'.json')):sha(O/(name+'.json')) for name in ['TAIL_POSITIVE_CALIBRATION_PROPOSAL','TAIL_POSITIVE_EVALUATION_PROPOSAL','TAIL_GENUINE_EVALUATION_PROPOSAL']}
report={'status':'PROPOSAL_REQUIRES_INDEPENDENT_ROOT_REVIEW_NO_READ_RELEASE','split_rule':'For each source, sort complete eligible full components by SHA256('+rule+'component), first floor(n/2) are calibration. All other training-clean camera components remain evaluation. No resampling or tuning this split.','positive_pool_rows':len(p),'positive_pool_components':len(comps),'calibration_rows':len(C),'calibration_components':len(cal),'calibration_people':len({v for r in C for v in r['persons']}),'calibration_source_rows':dict(collections.Counter(r['source'] for r in C)),'evaluation_positive_rows':len(P),'evaluation_positive_components':len({r['component'] for r in P}),'positive_guards':guards,'genuine_cells':cells,'forbidden_claim':'Missing af0_u5061 and sparse family guards prevent a complete simultaneous NI utility claim; neither is dropped.','input_pins':pins,'script_sha256':sha(__file__),'inventory_sha256':sha(O/'POSITIVE_INVENTORY.json')}
(O/'TAIL_SPLIT_PROPOSAL.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps({k:v for k,v in report.items() if k not in ['positive_guards','input_pins']},indent=2));print('GUARDS',[(g['family'],g['n_rows'],g['n_components'],g['status_without_scores']) for g in guards])
