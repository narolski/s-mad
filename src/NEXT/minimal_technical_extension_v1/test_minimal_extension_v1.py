import contextlib,copy,hashlib,io,json,os,pathlib,tarfile,tempfile,unittest
from unittest.mock import patch
import minimal_extension_v1 as c

class Tests(unittest.TestCase):
 def archive(self,d,name,entries,members,kind='bb2_batch_match'):
  p=pathlib.Path(d).resolve()/(name+'.tar')
  with tarfile.open(p,'w') as tf:
   for member,raw,typ in entries:
    info=tarfile.TarInfo(member);info.type=typ;info.size=len(raw) if typ==tarfile.REGTYPE else 0
    if typ in (tarfile.SYMTYPE,tarfile.LNKTYPE):info.linkname='outside'
    tf.addfile(info,io.BytesIO(raw) if typ==tarfile.REGTYPE else None)
  return {'kind':kind,'archive':str(p),'sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'archive_bytes':p.stat().st_size,'members':members}

 def test_native_token_expected_and_no_alternative(self):
  expected={'bs':256,'accum':1}
  for text,wanted in [('bs 256 accum 1','PASS'),('bs\t256\naccum 1','PASS'),('bs 128 accum 2','FAIL'),('bs 256suffix accum 1','FAIL'),('bs 256 bs 256 accum 1','FAIL'),('accum 1','UNKNOWN'),('bs','UNKNOWN')]:
   values=[v['status'] for v in c.token_checks(text,expected).values()]
   actual='FAIL' if 'FAIL' in values else 'UNKNOWN' if 'UNKNOWN' in values else 'PASS'
   self.assertEqual(actual,wanted)

 def test_env_native_vs_integrity(self):
  out=c.env_checks('TASK=x\nTASK=y\nARM=A\nSEED=403',{'TASK':'x','ARM':'A','SEED':403})
  self.assertTrue(out['TASK']['native_exact_line_once']);self.assertFalse(out['TASK']['strict_unique_key_match']);self.assertEqual(out['TASK']['status'],'FAIL')

 def test_canary_values_ignored(self):
  outs=[]
  for value in ('0.123456789','987654.321'):
   text='bs 256 accum 1 AUC '+value+' EER '+value+' APCER '+value+' BPCER '+value+' train_acc_rule0 '+value
   out=c.token_checks(text,{'bs':256,'accum':1});outs.append(out);self.assertNotIn(value,json.dumps(out))
  self.assertEqual(*outs)

 def test_opaque_streaming_and_no_other_extract(self):
  raw=b'PK\x03\x04FAKE_CHECKPOINT_CANARY'+b'x'*(9*1024*1024)
  with tempfile.TemporaryDirectory() as d:
   rec=self.archive(d,'s',[('s/last_trainable.pt',raw,tarfile.REGTYPE),('s/scores.npz',b'FORBIDDEN_ARRAY',tarfile.REGTYPE),('s/info.json',b'{"train_acc_rule0":0.99887766}',tarfile.REGTYPE)],{'s/last_trainable.pt':{'operation':'opaque_sha256'}},'sbmr512_trainable_hash')
   original=tarfile.TarFile.extractfile
   def guarded(tf,member):
    self.assertEqual(member.name,'s/last_trainable.pt');f=original(tf,member)
    orig_read=f.read
    def read(n=-1):self.assertLessEqual(n,1024*1024);self.assertGreater(n,0);return orig_read(n)
    f.read=read;return f
   with patch.object(tarfile.TarFile,'extractfile',guarded):out=c.collect_record(rec)
   m=out['members']['s/last_trainable.pt'];self.assertEqual(m['sha256'],hashlib.sha256(raw).hexdigest());self.assertFalse(m['decoded']);self.assertNotIn('CANARY',json.dumps(out));self.assertNotIn('99887766',json.dumps(out))

 def test_missing_member_unknown(self):
  with tempfile.TemporaryDirectory() as d:
   r=self.archive(d,'s',[],{'s/last_trainable.pt':{'operation':'opaque_sha256'}},'sbmr512_trainable_hash');out=c.collect_record(r)
   self.assertEqual(out['members']['s/last_trainable.pt'],{'status':'UNKNOWN','reason':'MEMBER_ABSENT'})

 def test_unsafe_and_duplicate_fail_no_partial_digest(self):
  for extra,typ,reason in [('./s/last_trainable.pt',tarfile.REGTYPE,'TAR_DUPLICATE_ALIAS'),('../escape',tarfile.REGTYPE,'TAR_PATH'),('/absolute',tarfile.REGTYPE,'TAR_PATH'),('link',tarfile.SYMTYPE,'TAR_TYPE'),('hard',tarfile.LNKTYPE,'TAR_TYPE'),('device',tarfile.CHRTYPE,'TAR_TYPE')]:
   with tempfile.TemporaryDirectory() as d:
    r=self.archive(d,'s',[('s/last_trainable.pt',b'bytes',tarfile.REGTYPE),(extra,b'',typ)],{'s/last_trainable.pt':{'operation':'opaque_sha256'}},'sbmr512_trainable_hash');out=c.collect_record(r)
    self.assertEqual(out['reason'],reason);self.assertEqual(out['members'],{});self.assertFalse(out['unique_member_namespace_verified'])

 def test_hash_size_and_text_encoding(self):
  with tempfile.TemporaryDirectory() as d:
   r=self.archive(d,'s',[('s/task_info.txt',b'\xff',tarfile.REGTYPE)],{'s/task_info.txt':{'operation':'recipe_tokens','expected':{'bs':256}}})
   self.assertEqual(c.collect_record(r)['members']['s/task_info.txt']['reason'],'TEXT_ENCODING')
   wrong=dict(r,sha256='0'*64);self.assertEqual(c.collect_record(wrong)['reason'],'ARCHIVE_HASH')
   wrong=dict(r,archive_bytes=1);self.assertEqual(c.collect_record(wrong)['reason'],'ARCHIVE_SIZE')
   with patch.object(c,'MAX_TEXT',0):self.assertEqual(c.collect_record(r)['reason'],'TEXT_SIZE')

 def synthetic_scope(self,d):
  records={}
  for arm in ('A','B','Sb'):
   for seed in range(403,408):
    key=f'BB2L_{arm}_s{seed}';members={key+'/task_info.txt':{'operation':'recipe_tokens','expected':{'bs':256,'accum':1}},key+'/task.env':{'operation':'task_env','expected':{'TASK':key,'ARM':arm,'SEED':seed}}}
    entries=[(key+'/task_info.txt',b'bs 256 accum 1 EER 0.99887766',tarfile.REGTYPE),(key+'/task.env',f'TASK={key}\nARM={arm}\nSEED={seed}\n'.encode(),tarfile.REGTYPE)]
    records[key]=self.archive(d,key,entries,members)
  for seed in range(408,413):
   key=f'RZ1_SbMR512_s{seed}';records[key]=self.archive(d,key,[(key+'/last_trainable.pt',b'SYNTHETIC NOT A MODEL',tarfile.REGTYPE)],{key+'/last_trainable.pt':{'operation':'opaque_sha256'}},'sbmr512_trainable_hash')
  return {'schema':'next-minimal-technical-extension-v1','records':records,'pins':{}}

 def test_scope_no_expansion_or_batch_switch(self):
  with tempfile.TemporaryDirectory() as d:
   scope=self.synthetic_scope(d);c.validate_scope(scope)
   scope['records']['BB2L_A_s403']['members']['BB2L_A_s403/task_info.txt']['expected']['bs']=128
   with self.assertRaisesRegex(c.Refusal,'EXPECTED_BATCH_FIXED'):c.validate_scope(scope)

 def test_cli_release_before_any_archive_then_synthetic_20_complete(self):
  with tempfile.TemporaryDirectory() as d:
   root=pathlib.Path(d).resolve();scope=self.synthetic_scope(d);sp=root/'scope.json';sp.write_text(json.dumps(scope));rp=root/'release.json';rp.write_text('{}');out=root/'out';review=root/'synthetic_review.txt';source=hashlib.sha256(pathlib.Path(c.__file__).read_bytes()).hexdigest()
   argv=['collector','--scope',str(sp),'--release',str(rp),'--output',str(out)]
   with patch('sys.argv',argv),patch.object(c,'collect_record',side_effect=AssertionError('no access')),contextlib.redirect_stdout(io.StringIO()) as stdout:self.assertEqual(c.main(),2)
   self.assertEqual(stdout.getvalue(),'HOLD RELEASE_REQUIRED\n');self.assertFalse(out.exists())
   review.write_text('SYNTHETIC TEST ONLY\nGO_NEXT_MINIMAL_TECHNICAL_EXTENSION '+source+'\n')
   rel={'decision':'GO_NEXT_MINIMAL_TECHNICAL_EXTENSION_V1','real_member_access_authorized':True,'checkpoint_hash_only_no_decode':True,'expected_batch_binding_adopted':True,'prior_technical_postreview_adopted':True,'scope_sha256':hashlib.sha256(sp.read_bytes()).hexdigest(),'collector_sha256':source,'cpu_only':True,'output':str(out),'implementation_review':str(review),'implementation_review_sha256':hashlib.sha256(review.read_bytes()).hexdigest()};rp.write_text(json.dumps(rel))
   with patch('sys.argv',argv),patch.dict(os.environ,{'CUDA_VISIBLE_DEVICES':''}),contextlib.redirect_stdout(io.StringIO()):self.assertEqual(c.main(),0)
   result=json.loads((out/'TECHNICAL_EXTENSION.json').read_text());self.assertEqual(len(result['records']),20);self.assertFalse(result['scientific_admission']);self.assertEqual(result['planned_seed_denominator'],5)
   self.assertTrue(all(r['status']=='COLLECTED_TECHNICAL_ONLY' for r in result['records'].values()));self.assertNotIn('99887766',json.dumps(result));self.assertEqual((out/'TECHNICAL_WRITE_COMPLETE').read_text(),'NOT_SCIENTIFIC_ADMISSION\n');self.assertFalse(list(out.glob('*.partial')))
   with patch('sys.argv',argv),patch.dict(os.environ,{'CUDA_VISIBLE_DEVICES':''}),contextlib.redirect_stdout(io.StringIO()) as stdout:self.assertEqual(c.main(),2)
   self.assertEqual(stdout.getvalue(),'HOLD OUTPUT_GATE\n')

if __name__=='__main__':unittest.main()
