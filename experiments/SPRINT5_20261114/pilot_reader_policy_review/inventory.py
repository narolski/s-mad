import collections,csv,hashlib,json,pathlib,re
R=pathlib.Path('/home/narolski/smad-next');O=R/'experiments/SPRINT5_20261114/pilot_reader_policy_review';O.mkdir(exist_ok=True)
source=R/'src/DATA/partner_overlap_audit.py';raw=source.read_text().split('# ---------- lists')[0];assert 'OUT.mkdir' not in raw
raw=raw.replace('return list(csv.DictReader(open(p)))','READ_FILES[str(p)]=sha(p)\n    return list(csv.DictReader(open(p)))');g={'READ_FILES':{}};exec(compile(raw,str(source),'exec'),g)
def sha(p):return hashlib.sha256(pathlib.Path(p).read_bytes()).hexdigest()
def rd(p):g['READ_FILES'][str(p)]=sha(p);return list(csv.DictReader(open(p)))
def resolve(r):
 x=g['resolve'](r['id'],r.get('host',''))
 if x is None:return None
 people=set(x[0])|set(x[1]);photos=set(x[2])
 m=re.fullmatch(r'sp2?_S[034]_opencv_(feret|frgc)_(\d+)(?:_fm\d+|_amsl\d+)?',r['id'])
 if m:
  p=g['pool'][f'{m.group(1)}:{m.group(2)}'];people.add(p['B_pid']);photos.add(g['photo'](p['B']))
 if not people or not photos or any(p.startswith('unmapped:') for p in photos):return None
 return people,photos
train=rd('/mnt/t7/smad_next/PN1/fs_tree/pn1/data/manifests/train_Sb.csv');tp=set();tf=set()
for r in train:
 x=resolve(r);assert x,r['id'];tp|=x[0];tf|=x[1]
primary=json.load(open('/mnt/t7/smad_next/SPRINT5_1/floor_execution_v1/prepared/primary_with_D_components.json'));pp=set();pf=set()
for r in primary:
 x=resolve(r);assert x;pp|=x[0];pf|=x[1]
rows=rd('/mnt/t7/smad_next/AB1/overlay_tree/pn1/data/manifests/ab1_eval.csv');pos=[];neg=[];unresolved=[]
for r in rows:
 if r['role']!='dev' or r['fam'] not in ['af0','ladder','splice']:continue
 use=int(r['label'])==1 or (r['fam']=='af0' and r['rung']=='photo') or (r['fam']=='ladder' and r['rung']=='R0')
 if not use:continue
 x=resolve(r)
 if x is None:unresolved.append(r['id']);continue
 people,photos=x
 out=dict(r,persons=sorted(people),photos=sorted(photos),training_person_overlap=sorted(people&tp),training_photo_overlap=sorted(photos&tf),primary_person_overlap=sorted(people&pp),primary_photo_overlap=sorted(photos&pf))
 (pos if int(r['label']) else neg).append(out)
# Graph over all selected positive and camera rows plus the complete original geometry graph.
parent={}
def root(p):
 parent.setdefault(p,p)
 if parent[p]!=p:parent[p]=root(parent[p])
 return parent[p]
def union(ps):
 for p in ps:root(p)
 for p in ps[1:]:
  a,b=root(ps[0]),root(p)
  if a!=b:parent[max(a,b)]=min(a,b)
for r in rd(R/'experiments/PN1_protocol-network-first-tests/split/ladder_split.csv'):union([r['pid'],r['partner_B']])
for r in pos+neg:union(r['persons'])
for r in pos+neg:r['component']=root(r['persons'][0]);r['source']='+'.join(sorted({p.split(':')[0] for p in r['persons']}))
trainroots={root(p) for p in tp};primaryroots={root(p) for p in pp}
for r in pos+neg:r['training_component_overlap']=r['component'] in trainroots;r['primary_component_overlap']=r['component'] in primaryroots
summary=[]
for key,items in __import__('itertools').groupby(sorted(pos,key=lambda r:(r['fam'],r['rung'],r['tool'],r['strength'])),key=lambda r:(r['fam'],r['rung'],r['tool'],r['strength'])):
 rr=list(items);clean=[r for r in rr if not(r['training_person_overlap'] or r['training_photo_overlap'] or r['training_component_overlap'])];away=[r for r in clean if not(r['primary_person_overlap'] or r['primary_photo_overlap'] or r['primary_component_overlap'])]
 summary.append({'family':key,'rows':len(rr),'train_clean_rows':len(clean),'train_clean_components':len({r['component'] for r in clean}),'also_primary_disjoint_rows':len(away),'also_primary_disjoint_components':len({r['component'] for r in away})})
report={'scope':'source metadata only; no candidate or image payload','training_people':len(tp),'training_photos':len(tf),'primary_people':len(pp),'positive_groups':summary,'unresolved_selected_ids':unresolved,'metadata_pins':g['READ_FILES'],'resolver_sha256':sha(source),'script_sha256':sha(__file__),'camera_rows':len(neg),'train_clean_camera_rows':sum(not(r['training_person_overlap'] or r['training_photo_overlap'] or r['training_component_overlap']) for r in neg)}
(O/'POSITIVE_INVENTORY.json').write_text(json.dumps(report,indent=2)+'\n');(O/'RESOLVED_CANDIDATE_INPUTS.json').write_text(json.dumps({'positive':pos,'camera':neg},indent=2)+'\n');print(json.dumps(report,indent=2))
