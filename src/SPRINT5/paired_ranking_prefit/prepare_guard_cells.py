"""Candidate-independent enumeration of genuine source/processing guard cells."""
import argparse,collections,csv,hashlib,json,pathlib,re
ap=argparse.ArgumentParser();ap.add_argument('--inputs',type=pathlib.Path,required=True);ap.add_argument('--prepared',type=pathlib.Path,required=True);a=ap.parse_args()
parent={}
def f(x):
 parent.setdefault(x,x)
 if parent[x]!=x:parent[x]=f(parent[x])
 return parent[x]
def union(x,y):
 x,y=f(x),f(y)
 if x!=y:parent[max(x,y)]=min(x,y)
for r in csv.DictReader((a.inputs/'ladder_split.csv').open()):union(r['pid'],r['partner_B'])
cal=json.loads((a.prepared/'calibration_proposal.json').read_text());excluded={r['component'] for r in cal}
def hosts(r):
 h=r.get('host','');assert h,r.get('id')
 if '|' in h:return h.split('|')
 if ':' in h:return [h]
 if re.fullmatch(r'\d{5}(?:_\d{5})?',h):return ['ffhq:'+x for x in h.split('_')]
 if re.fullmatch(r'(feret|frgc)_\d+',h):return [h.replace('_',':',1)]
 return ['unresolved:'+h]
files={'dev':'ab1_eval.csv','tt1':'tt1_score.csv','meds':'meds_score.csv','gd':'pr1_gd.csv'};groups=collections.defaultdict(list);unresolved=[];removed=collections.Counter()
for setname,filename in files.items():
 for r in csv.DictReader((a.inputs/filename).open()):
  if int(r['label'])!=0:continue
  if setname=='dev' and r['role']=='test':removed['historical_test_rows']+=1;continue
  ps=hosts(r)
  if any(x.startswith('unresolved:') for x in ps):unresolved.append({'set':setname,'id':r['id']});continue
  comps=sorted({f(h) for h in ps})
  if any(c in excluded for c in comps):removed['calibration_component_rows']+=1;continue
  source='+'.join(sorted({h.split(':')[0] for h in ps}))
  # strength is overloaded: TT1 border reference ROW ID and MEDS capture number are not processing cells.
  strength=r.get('strength','') if setname=='dev' or r.get('strength','') in ('primary','secondary') else ''
  key=(setname,source,r.get('fam',''),r.get('role',''),r.get('rung',''),strength,r.get('tool',''),r.get('cell',''))
  groups[key].append({'id':r['id'],'components':comps})
assert not unresolved,unresolved[:3]
cells=[{'cell_index':j,'set':k[0],'source':k[1],'metadata':dict(zip(['fam','role','rung','strength','tool','cell'],k[2:])),'n_rows':len(v),'n_components':len({c for r in v for c in r['components']}),'rows':v} for j,(k,v) in enumerate(sorted(groups.items()))]
# One S4 detection guard plus every fixed genuine cell; no post-result cell dropping.
G=len(cells)+1
report={'status':'PROPOSAL_REQUIRES_ROOT_ADOPTION','genuine_guard_cells':len(cells),'detection_guards':1,'total_guards_G':G,'family_alpha':.05,'one_sided_alpha_per_guard':.05/G,'bootstrap_draws':10000,'expected_tail_draws_per_guard':10000*.05/G,'note':'Bonferroni simultaneous one-sided bounds. This manycells causes coarse10000drawtails; root may prospectively choose exact intersection-union decision with marginal95%one-sidedbounds and remove simultaneouscoverageclaim. No post-score change. Zero-event confidence cannot use zero-widthbootstrap. Missing cell/metadata prevents adoption, not cell deletion.','removed_rows':dict(removed),'cells_by_set':dict(collections.Counter(c['set'] for c in cells)),'smallest_components':min(c['n_components'] for c in cells),'input_sha256':{v:hashlib.sha256((a.inputs/v).read_bytes()).hexdigest() for v in files.values()}}
(a.prepared/'genuine_guard_cells_proposal.json').write_text(json.dumps(cells,indent=2)+'\n');(a.prepared/'GUARD_PREPARATION.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report,indent=2))
