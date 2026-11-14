"""Metadata-only preparation. Reads no detector logits/checkpoints or floor scores."""
import argparse,collections,csv,hashlib,json,math,pathlib
ap=argparse.ArgumentParser();ap.add_argument('--inputs',type=pathlib.Path,required=True);ap.add_argument('--out',type=pathlib.Path,required=True);a=ap.parse_args()
a.out.mkdir(parents=True,exist_ok=False)
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def read(n):return list(csv.DictReader((a.inputs/n).open()))
P=json.loads((a.inputs/'primary_rows.json').read_text());D={r['id']:r for r in read('d_values.csv')};L=read('ladder_split.csv');T=read('tt1_score.csv'); lm={r['pid']:r for r in L};parent={}
def root(x):
 parent.setdefault(x,x)
 if parent[x]!=x:parent[x]=root(parent[x])
 return parent[x]
def union(x,y):
 x,y=root(x),root(y)
 if x!=y:parent[max(x,y)]=min(x,y)
for r in L:union(r['pid'],r['partner_B'])
assert len(P)==200 and len({r['host'] for r in P})==100
assert collections.Counter(int(r['label']) for r in P)=={0:100,1:100}
assert all(r['role']=='dev' and r['rung'] in ('S3','S4') and D[r['id']]['host']==r['host'] for r in P)
v=sorted(math.log(float(D[r['id']]['D'])) for r in P)
def quantile(f):
 j=(len(v)-1)*f;k=int(j);return v[k]+(v[min(k+1,len(v)-1)]-v[k])*(j-k)
edges=[quantile(i/5) for i in range(1,5)]
rows=[]
for r in P:
 source=r['host'].split(':')[0];component=root(r['host'])
 assert source==component.split(':')[0]
 ld=math.log(float(D[r['id']]['D']))
 rows.append({**r,'D':float(D[r['id']]['D']),'log_D':ld,'D_stratum':sum(ld>e for e in edges),'component':component,'source':source,'partner_B':lm[r['host']]['partner_B']})
pc={r['component'] for r in rows};tc={root(r['pid']) for r in L if r['role']=='train'}
# Exclusion is graph-component based, not just exact host inequality.
cam=[r for r in T if r['rung']=='R_cam' and int(r['label'])==0 and root(r['host']) not in pc|tc]
byhost=collections.defaultdict(list)
for r in cam:byhost[r['host']].append(r)
# One canonical unprocessed image per person; lexical ID is prospective and score-blind.
cal=[min(rr,key=lambda r:r['id']) for h,rr in sorted(byhost.items())]
cal=[{**r,'component':root(r['host']),'source':r['host'].split(':')[0]} for r in cal]
assert not ({r['component'] for r in cal}&(pc|tc))
# Calibration IDs plus ALL rows sharing its components excluded from genuine evaluation.
calcomp={r['component'] for r in cal}
exclude=[r['id'] for r in T if root(r['host']) in calcomp]
for n,x in [('primary_with_D_components.json',rows),('calibration_proposal.json',cal),('tt1_calibration_component_exclusions.json',exclude)]:
 (a.out/n).write_text(json.dumps(x,indent=2)+'\n')
counts=collections.Counter((r['D_stratum'],int(r['label'])) for r in rows)
report={'status':'PREPARED_METADATA_ONLY_REQUIRES_INDEPENDENT_ADOPTION','inputs':{n:sha(a.inputs/n) for n in ['primary_rows.json','d_values.csv','ladder_split.csv','tt1_score.csv','METADATA_AUDIT.json']},'D_rule':'natural log, type7 linear pooled quantiles, ties go lower bin; fixed across bootstrap; equal five-stratum weights','D_edges':edges,'strata':[{'stratum':k,'negative':counts[k,0],'positive':counts[k,1]} for k in range(5)],'components':len(pc),'largest_component_rows':max(collections.Counter(r['component'] for r in rows).values()),'component_counts_by_source':dict(collections.Counter(next(r['source'] for r in rows if r['component']==c) for c in pc)),'calibration':{'raw_eligible_rows':len(cam),'unique_person_rows':len(cal),'components':len(calcomp),'sources':dict(collections.Counter(r['source'] for r in cal)),'excluded_tt1_rows_all_variants':len(exclude),'rule_proposed':'per-source threshold x_(ceil(.95*(n+1))) with +infinity when order exceeds n, strict score>threshold; common threshold maximum across sources; bootstrap calibration components jointly with paired seed triplets','training_and_primary_component_disjoint':True},'seed_allocation':{'seeds':[501,502,503,504,505],'scope':'SPRINT5_1 matched arm triplets only','evidence':'METADATA_AUDIT.json prior scoped hit search empty; smoke501 is sameexperiment infrastructure reuse','requires_lead_concurrent_reservation':True,'reserved_NEXT':[413,414,415,416,417]},'outputs':{p.name:sha(p) for p in a.out.glob('*.json')}}
(a.out/'PREPARATION.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report,indent=2))
