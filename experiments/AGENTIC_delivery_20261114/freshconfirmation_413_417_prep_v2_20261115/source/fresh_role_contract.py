"""Source-only task/provenance adapter; success never permits execution."""
import pathlib,json
B=pathlib.Path(__file__).resolve().parents[1]
TASKS=json.loads((B/'FULL_CONDITIONAL_TASKS.json').read_text())
KNOWN=json.loads((B/'KNOWN_AB1_PROVENANCE.json').read_text())
INDEX={x['task']:x for x in TASKS}
class Refusal(ValueError): pass
def need(ok,msg):
 if not ok: raise Refusal(msg)
def validate_ab1_task(r):
 need(type(r) is dict,'record object required')
 need(r.get('branch')!='GX','GX scope unknown')
 need(type(r.get('seed')) is int and r['seed'] in range(413,418),'fresh seeds only')
 x=INDEX.get(r.get('task'));need(x is not None,'unknown task')
 for k in ['branch','seed','role','producer_arm','task']:
  need(r.get(k)==x[k],'task/role mismatch: '+k)
 need(r['producer_arm'] in ['AB1_A','AB1_B','AB1_Sb'],'common AB1 roles only')
 for k in ['parent_sha256','pack_sha256','overlay_sha256','arch','steps','batch','accum','final','lr','head_lr','eval_manifest','scorer']:
  need(r.get(k)==KNOWN[k],'provenance mismatch: '+k)
 need(r.get('arm')==r['producer_arm'][4:],'arm mismatch')
 return {'source_role_contract':'PASS','execution':'HOLD','scientific_admission':False,'task':r['task']}
