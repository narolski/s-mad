import pathlib,json,hashlib,unittest,subprocess
from fresh_role_contract import validate_ab1_task,Refusal,TASKS,KNOWN
B=pathlib.Path(__file__).resolve().parents[1]
class Contracts(unittest.TestCase):
 def test_counts_core_identical(self):
  c=json.loads((B/'COHORT_COUNTS.json').read_text())
  self.assertEqual({k:v['full'] for k,v in c.items()},{'SbFM':20,'GX':15,'SbMR':25,'SbM':25,'Sb512':30,'SbMR512':30,'Sbc':25,'DINOv3':20})
  core=B/'CORE_TASK_TEMPLATES_V1_IDENTICAL.json'
  old=pathlib.Path('/home/narolski/smad-next/experiments/AGENTIC_delivery_20261114/freshconfirmation_413_417_prep_20261114/TASK_TEMPLATES.json')
  self.assertEqual(core.read_bytes(),old.read_bytes())
  self.assertEqual(TASKS[:150],json.loads(core.read_text()));self.assertEqual(len(TASKS),190)
  self.assertEqual(len({x['task'] for x in TASKS}),190)
 def test_all_ab1_common_rows(self):
  rows=[x for x in TASKS if x['branch']!='GX' and x['producer_arm'] in ['AB1_A','AB1_B','AB1_Sb']]
  self.assertEqual(len(rows),70)
  for x in rows:
   with self.subTest(task=x['task']):self.assertEqual(validate_ab1_task(dict(KNOWN,**x,arm=x['producer_arm'][4:]))['execution'],'HOLD')
 def test_seed_refusal(self):
  x=next(x for x in TASKS if x['branch']=='DINOv3' and x['producer_arm']=='AB1_Sb')
  for seed in [-1,0,401,403,407,408,412,418,999,'413',True,None]:
   with self.subTest(seed=seed):
    with self.assertRaises(Refusal):validate_ab1_task(dict(KNOWN,**dict(x,seed=seed),arm='Sb'))
 def test_identity_and_provenance_refusal(self):
  x=next(x for x in TASKS if x['branch']=='DINOv3' and x['producer_arm']=='AB1_Sb');base=dict(KNOWN,**x,arm='Sb')
  for k in ['branch','role','producer_arm','task','arm','parent_sha256','pack_sha256','overlay_sha256','arch','steps','batch','accum','final','lr','head_lr','eval_manifest','scorer']:
   with self.subTest(field=k):
    with self.assertRaises(Refusal):validate_ab1_task(dict(base,**{k:'wrong'}))
  with self.assertRaises(Refusal):validate_ab1_task(dict(base,branch='GX'))
 def test_dino_scope(self):
  d=[x for x in TASKS if x['branch']=='DINOv3'];self.assertEqual(len(d),20);self.assertNotIn('AB1_A',[x['producer_arm'] for x in d])
 def test_source_delta_preserves_math(self):
  f=(B/'source/run_ab1_fresh_DISABLED.sh').read_text()
  self.assertIn('exit 78',f.split('set -euo pipefail')[0]);self.assertIn('413|414|415|416|417',f);self.assertNotIn('case "$SEED" in 408',f)
  p=pathlib.Path('/home/narolski/smad-next')/KNOWN['parent_source']
  self.assertEqual(hashlib.sha256(p.read_bytes()).hexdigest(),KNOWN['parent_sha256']);s=p.read_text()
  self.assertIn(s[s.index('py "$W/pn1/code/smadcvpr/train.py"'):s.index('[ -f "$RUN/last.pt" ]')],f)
  self.assertIn(s[s.index('py "$W/pn1/src/pn1_score.py"'):s.index('cp "$RUN/meta.json"')],f)
  subprocess.run(['bash','-n',str(B/'source/run_ab1_fresh_DISABLED.sh')],check=True)
if __name__=='__main__':unittest.main(verbosity=2)
