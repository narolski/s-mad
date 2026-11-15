"""Candidate-free HN bootstrap draw schedule proposal; input labels/components only."""
import hashlib,json,pathlib
import numpy as np
R=pathlib.Path('/home/narolski/smad-next');O=R/'experiments/SPRINT5_20261114/pilot_reader_policy_review'
p=pathlib.Path('/mnt/t7/smad_next/SPRINT5_1/floor_execution_v1/prepared/primary_with_D_components.json');rows=json.loads(p.read_text());assert hashlib.sha256(p.read_bytes()).hexdigest()=='03202a4afd96ce5e2d65acf1b4285310747efb86983615f95f05abfae221e6ce'
strata={}
for i,r in enumerate(rows):strata.setdefault(r['source'],{}).setdefault(r['component'],[]).append(i)
rng=np.random.default_rng(2026111402);accepted=[];rejected=0;attempts=0
while len(accepted)<10000:
 attempts+=1;assert attempts<=1000000,'metadata support problem; no silent alternate RNG'
 ii=[]
 for source in sorted(strata):
  units=sorted(strata[source])
  for component in rng.choice(units,len(units),replace=True):ii.extend(strata[source][component])
 if {(rows[i]['D_stratum'],int(rows[i]['label'])) for i in ii}!={(d,y) for d in range(5) for y in (0,1)}:rejected+=1;continue
 accepted.append(ii)
seeds=rng.integers(0,5,size=(10000,5)).tolist()
encode=lambda value:json.dumps(value,separators=(',',':')).encode()
report={'status':'PROPOSED_METADATA_ONLY_CONDITIONAL_BOOTSTRAP','rng':'numpy.default_rng(2026111402), PCG64; source/component draws first; then10000x5paired-seed-index draws','numpy':np.__version__,'accepted':len(accepted),'attempts':attempts,'rejected':rejected,'rejected_fraction':rejected/attempts,'conditioning':'all5fixedDstrata containbothlabels; rejectusinglabels/components only, neverusing scores','component_draws_sha256':hashlib.sha256(encode(accepted)).hexdigest(),'seed_draws_sha256':hashlib.sha256(encode(seeds)).hexdigest(),'input_sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'script_sha256':hashlib.sha256(pathlib.Path(__file__).read_bytes()).hexdigest(),'scope':'proposal requires independentrootreview; no reader/source/fitregistration changes'}
(O/'HN_DRAW_PLAN_PROPOSAL.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report,indent=2))
