import csv,hashlib,json,pathlib
R=pathlib.Path('/home/narolski/smad-next');O=R/'experiments/SPRINT5_20261114/hn1';poolpath=pathlib.Path('/mnt/t7/smad_next/AR1/pool.csv');splitpath=R/'experiments/PN1_protocol-network-first-tests/split/ladder_split.csv';primarypath=R/'experiments/SPRINT5_20261114/paired_ranking/primary_rows.json';trainpath=pathlib.Path('/mnt/t7/smad_next/SPRINT5_2/transfer_control124_v1/records.json')
def sha(p):return hashlib.sha256(pathlib.Path(p).read_bytes()).hexdigest()
pool={r['pid']:r for r in csv.DictReader(poolpath.open())};split={r['pid']:r for r in csv.DictReader(splitpath.open())};train=json.loads(trainpath.read_text());primary=json.loads(primarypath.read_text());devhosts={r['host'] for r in primary};assert len(devhosts)==100 and len(primary)==200
trainpeople={p for r in train for p in [r['host'],r['partner']]};devpeople={p for h in devhosts for p in [h,pool[h]['B_pid']]};assert not trainpeople&devpeople;assert all(split[p]['role']=='train' for p in trainpeople);assert all(split[p]['role']!='train' for p in devpeople)
tp={};dp={}
for r in train:
 assert r['partner']==pool[r['host']]['B_pid']
 for p,h in r['input_pins'].items():assert sha(p)==h;tp[p]=h
for h in devhosts:
 for k in ['H','S','B']:
  p=pathlib.Path(pool[h][k]);dp[str(p)]=sha(p);p=p.with_suffix('.tem');dp[str(p)]=sha(p)
assert not set(tp)&set(dp);assert not set(tp.values())&set(dp.values())
out={'status':'PASS','scope':'training versus fixed primary identity/source-byte/geometry-byte exclusion only; no detector scores','train_hosts':124,'train_people':len(trainpeople),'dev_hosts':100,'dev_people':len(devpeople),'train_input_files':len(tp),'dev_input_files':len(dp),'identity_intersection':[],'path_intersection':[],'input_bytehash_intersection':[],'metadata_pins':{str(p):sha(p) for p in [poolpath,splitpath,primarypath,trainpath]},'script_sha256':sha(__file__)}
(O/'TRANSFER_EXCLUSION_AUDIT.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps(out,indent=2))
