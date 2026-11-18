import copy,json,unittest
import native_metadata_predicates_v2 as p

class PredicatesTests(unittest.TestCase):
 def test_original_loss_cases(self):
  cases=[('loss=0.2','PASS'),('prefix val_loss = nan','FAIL'),('LOSS:1e999','FAIL'),('loss +inf','UNKNOWN'),('loss 0.125abc','PASS'),('"loss":0.5','FAIL'),('loss_norm 0.2','FAIL'),('loss .','UNKNOWN'),('step100 loss=0.5\rstep200 loss=0.2','PASS'),('loss=-inf','FAIL')]
  for text,status in cases:self.assertEqual(p.loss_predicate(text)['native_fit']['status'],status,text)
  r=p.loss_predicate('loss=nan loss=.');self.assertEqual(r['native_fit']['status'],'FAIL');self.assertEqual(r['rz1_fit']['status'],'UNKNOWN')
  self.assertNotIn('0.987654321',json.dumps(p.loss_predicate('val_loss=0.987654321')))

 def test_python_numeric_vs_literal_boolean(self):
  matrix=[];p.compare_json(matrix,'g',{'n':True,'flag':1},{'n':{'type':'int','equals':1},'flag':{'type':'bool','equals':True}},'source','member')
  self.assertEqual(matrix[0]['native_status'],'PASS');self.assertEqual(matrix[0]['strict_integrity_status'],'FAIL');self.assertEqual(matrix[1]['native_status'],'FAIL')

 def test_rz_substring_vs_strict(self):
  rec={'format':'rz1_refit','members':{'task_info.txt':{'kind':'tokens','source':'source','expected':{'limit':['0']}}}}
  rows=p.evaluate(rec,{'task_info.txt':'limit 0 limit 0'})
  self.assertEqual(rows[0]['native_status'],'PASS');self.assertEqual(rows[0]['strict_integrity_status'],'FAIL')

 def test_w2_native_and_integrity(self):
  rec={'kind':'dinov3_w2','models':[],'members':{'out/tasks.txt':{'kind':'tasks','source':'source','expected':['a','b']},'out/n_fail.txt':{'kind':'count','source':'source'}}}
  rows=p.evaluate(rec,{'out/tasks.txt':'a\n','out/n_fail.txt':' +0\n'})
  by={r['predicate']:r for r in rows}
  self.assertEqual(by['planned20_tasks_integrity']['strict_integrity_status'],'FAIL');self.assertEqual(by['task_source.a']['native_status'],'PASS');self.assertEqual(by['task_source.b']['native_status'],'FAIL')
  self.assertEqual(by['n_fail.txt']['native_status'],'PASS');self.assertEqual(by['n_fail.txt']['strict_integrity_status'],'FAIL')

 def test_missing_batch_proof_is_unknown(self):
  rec={'format':'native_fit','prefix':'BB2L_Sb_s403','submitted_batch_proof':None,'members':{}}
  rows=p.evaluate(rec,{})
  self.assertEqual(rows[0]['native_status'],'UNKNOWN')

 def supplement_fixture(self):
  model={'name':'AB1_Sb_s408','seed':408,'sha256':'a'*64,'gate_manifest':'ab1_eval.csv','gate_rows':21277}
  rec={'models':[model],'config_sha256':'c'*64,'members':{'config.json':{'schema':{'schema':{'type':'str','equals':'AB1FMSUPP-v1'}}},'technical_status.json':{'schema':{'eight_row_smoke_passed':{'type':'bool','equals':True}}},'gate_AB1_Sb_s408.json':{'schema':{'tar':{'type':'str','equals':'AB1_Sb_s408.tar'}}}}}
  evidence={'config.json':{'schema':'AB1FMSUPP-v1','models':[model]},'technical_status.json':{'eight_row_smoke_passed':True,'models':[{'name':model['name'],'seed':408,'gate':'passed','families':[{'name':f,'valid':True,'sha256':'f'*64} for f in ('tt1','meds')]}]},'gate_AB1_Sb_s408.json':{'tar':'AB1_Sb_s408.tar'},'_config_digest':'c'*64}
  return rec,evidence

 def test_supplement_full_tuple_and_literal_family_flags(self):
  rec,e=self.supplement_fixture();rows=p.supplement(rec,e);self.assertTrue(all(r['native_status']=='PASS' for r in rows if not r['predicate'].startswith('planned_model_association_integrity')))
  for mutation in ('wrong_seed','duplicate_config','duplicate_family','numeric_valid','wrong_gate_source','wrong_sha'):
   x=copy.deepcopy(e)
   if mutation=='wrong_seed':x['config.json']['models'][0]['seed']=409
   if mutation=='duplicate_config':x['config.json']['models']*=2
   if mutation=='duplicate_family':x['technical_status.json']['models'][0]['families'][1]['name']='tt1'
   if mutation=='numeric_valid':x['technical_status.json']['models'][0]['families'][0]['valid']=1
   if mutation=='wrong_gate_source':x['gate_AB1_Sb_s408.json']['tar']='AB1_Sb_s409.tar'
   if mutation=='wrong_sha':x['config.json']['models'][0]['sha256']='b'*64
   self.assertTrue(any(r['native_status']=='FAIL' for r in p.supplement(rec,x)),mutation)

 def test_missing_status_and_nonfinite_no_global_eligibility(self):
  rec,e=self.supplement_fixture();del e['technical_status.json']
  self.assertTrue(any(r['native_status']=='UNKNOWN' for r in p.supplement(rec,e)))

 def test_res512_string_not_truthiness(self):
  rows=[];p.compare_json(rows,'transform',{'res512':'0'},{'res512':{'type':'str','equals':'1','prospective_integrity_only':True}},'source','member')
  self.assertEqual(rows[0]['native_status'],'UNKNOWN');self.assertEqual(rows[0]['strict_integrity_status'],'FAIL')

 def test_technical_info_selective_export(self):
  import technical_collector_v2 as c
  spec={'kind':'json','schema':{'torch':{'type':'str','emit_version':True},'last_pt_sha256':{'type':'str','emit_hex':True}}}
  out=c.inspect_member(json.dumps({'torch':'2.8.0+cu128','last_pt_sha256':'a'*64,'train_acc_rule0':0.987654321,'info':{'EER':0.987654321}}).encode(),spec)
  self.assertEqual(out['checks']['torch']['technical_version'],'2.8.0+cu128');self.assertEqual(out['checks']['last_pt_sha256']['technical_sha256'],'a'*64);self.assertNotIn('987654321',json.dumps(out))

if __name__=='__main__':unittest.main()
