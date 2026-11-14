import csv,hashlib,json,pathlib,re
R=pathlib.Path('/home/narolski/smad-next');O=R/'experiments/SPRINT5_20261114/pilot_reader_policy_review';M=json.load(open('/mnt/t7/smad_next/SPRINT5_1/floor_execution_v1/inputs/METADATA_AUDIT.json'))['manifests']
def sha(p):return hashlib.sha256(pathlib.Path(p).read_bytes()).hexdigest()
hits=[];af0=[];other_soft=[]
for dataset,spec in M.items():
 assert sha(spec['path'])==spec['sha256']
 for r in csv.DictReader(open(spec['path'])):
  if int(r['label'])!=1 or (dataset=='dev' and r['role']=='test'):continue
  isaf0=r.get('fam')=='af0' or r.get('kind','').startswith('af0_u50') or re.match(r'(val|hold)_(feret|frgc)_u50_',r['id'])
  soft=r.get('strength') in ('61','fm61','s61') or r.get('hist')=='s61' or any(re.search(r'u5061|u50_61|soft_fm61|_fm61(?:\.|$)',str(v)) for k,v in r.items() if k in ('id','path','rung','kind','field'))
  if isaf0:af0.append({'set':dataset,**r})
  if isaf0 and soft:hits.append({'set':dataset,**r})
  if soft:other_soft.append({'set':dataset,'id':r['id'],'fam':r.get('fam'),'rung':r.get('rung'),'strength':r.get('strength')})
paths=[R/'src/PN1/tier1.py',R/'src/PN1/soften_dev.py',R/'src/PN1/mkmanifests.py',R/'src/PN1/pairs_check.py']
out={'scope':'all4admittedmanifest metadata + sourceonly; no candidatepayload','direct_AF0_positive_rows':len(af0),'direct_AF0_s61_positive_rows':len(hits),'direct_AF0_s61_matches':hits,'other_soft_positive_rows':len(other_soft),'other_soft_family_counts':dict(__import__('collections').Counter(str((r['set'],r['fam'],r['rung'],r['strength'])) for r in other_soft)),'source_pins':{str(p):sha(p) for p in paths},'manifest_pins':{v['path']:v['sha256'] for v in M.values()},'historical_proxy':'src/PN1/tier1.py:gaps maps af0_u5061 to D_R4_opencv_61 for train-vs-heldout logit gap. It is a ladder/OpenCV/s61 proxy, not AF0 morph lineage. No silent family-equivalence assumption.','source_evidence':'mkmanifests.py creates af0_u5061 from kept trainingu50 images; soften_dev.py adds AF0 heldout photo copies, not AF0 positiveu50 copies.','decision':'DIRECT_AF0_U5061_FAMILY_ABSENT; historicalproxyavailableonlyifexplicitlyseparatelyinterpreted','script_sha256':sha(__file__)}
(O/'AF0_U5061_ALIAS_AUDIT.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps(out,indent=2))
