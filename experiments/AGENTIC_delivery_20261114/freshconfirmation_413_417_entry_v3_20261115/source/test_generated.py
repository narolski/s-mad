import copy,hashlib,json,os,pathlib,signal,subprocess,sys,tempfile,time,unittest
from unittest.mock import patch
import authority_gate as g
import run_guarded as runner
B=pathlib.Path(__file__).resolve().parent

class Fixtures(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory();self.p=pathlib.Path(self.tmp.name)
        self.policy={'policy_sha256':'a'*64,'fixed':{'rule_sha256':'b'*64},'branches':['SbFM','GX','SbMR','SbM','Sb512','SbMR512','Sbc','DINOv3'],'durable_root':'/fixture/NEVER_ACTUAL','input_files':{},'source_pins':{}}
        row={'task':'NEXTCONF_DINOv3_AB1_Sb_s413','producer_arm':'AB1_Sb','seed':413,'role':'comparator','branch':'DINOv3'}
        self.policy['cohorts']={'DINOv3':[row]};self.policy['ab1_tasks']={'DINOv3':[row]}
        self.resources={'gpu':'H100','gpu_count':1,'cpus':8,'ram_gb':64,'local_disk_gb':80,'walltime_seconds':3600}
        self.runtime={'python':{'path':'FAKE','sha256':'c'*64},'bash':{'path':'FAKE','sha256':'d'*64},'bootstrap_python':{'path':'/usr/bin/python3','sha256':'c'*64}}
        self.release={'schema':'next-common-ab1-root-release-v3','decision':'GO_FRESH_COMMON_AB1_FIT_AND_REGISTERED_DEV_NATIVE_SCORE','permissions':['COMMON_AB1_FIT','AB1_REGISTERED_DEV_EVAL_AND_TRAIN_NATIVE_SCORE'],'sealed_access':False,'scientific_confirmation_read':False,'policy_sha256':'a'*64,'rule_sha256':'b'*64,'selected_branch':'DINOv3','selection_independent_review_sha256':'e'*64,'runtime_files':self.runtime,'runtime_home':'/fixture/home','cuda_visible_devices':'FAKE_UUID','resources':self.resources,'owned_source_commit_clean':True,'owned_source_commit':'f'*40}
        selection={'schema':'next-selection-result-v1','stage':'selection','rule_sha256':'b'*64,'choice':'DINOv3','arms':{k:{} for k in self.policy['branches']}}
        self.release['selection_record']=self.doc('selection.json',selection)
        self.release['selection_admission']=self.doc('admission.json',{'decision':'ADMIT_ONCE_SELECTION_FOR_FRESH_CONFIRMATION','selection_sha256':self.release['selection_record']['sha256'],'selected_branch':'DINOv3','independent_review_sha256':'e'*64})
        reg={'schema':'next-fresh-common-ab1-registration-v3','selected_branch':'DINOv3','full_cohort':[row],'common_ab1_tasks':[row],'steps':6250,'batch':256,'final':'last','native_eval_manifest':'ab1_eval.csv','native_train_scoring':True,'durable_root':self.policy['durable_root'],'source_pins':{}}
        self.release['registration']=self.doc('reg.json',reg)
        for key,decision in [('source_review','GO_COMMON_AB1_V3_SOURCE_AND_METHOD'),('runtime_input_admission','ADMIT_EXACT_AB1_RUNTIME_AND_INPUTS'),('resource_budget_admission','GO_EXACT_COMMON_AB1_RESOURCES_AND_BUDGET'),('duplicate_check','NO_DUPLICATE_FRESH_TASKS')]:
            d={'decision':decision,'registration_sha256':self.release['registration']['sha256'],'selected_branch':'DINOv3'}
            if key=='runtime_input_admission':d.update(runtime_files=self.runtime,input_files={},gpu_model='H100',recipe_build='ORIGINAL_AB1_EXACT',runtime_home='/fixture/home',cuda_visible_devices='FAKE_UUID')
            if key=='resource_budget_admission':d.update(resources=self.resources,capacity_verified=True,budget_allocated=True,durability_verified=True)
            self.release[key]=self.doc(key+'.json',d)
    def tearDown(self):self.tmp.cleanup()
    def doc(self,name,obj):
        p=self.p/name;p.write_text(json.dumps(obj));return {'path':str(p),'sha256':hashlib.sha256(p.read_bytes()).hexdigest()}
    def task(self,text='TASK=NEXTCONF_DINOv3_AB1_Sb_s413\nARM=Sb\nSEED=413\n'):
        p=self.p/'task.env';p.write_text(text);return p
    def test_valid_control_is_not_execution(self):
        branch,reg=g.validate_authority(self.release,self.policy);self.assertEqual(branch,'DINOv3');self.assertFalse((self.p/'claim').exists())
    def test_denial_before_task_or_staged_data(self):
        bad=copy.deepcopy(self.release);bad['permissions']=['COMMON_AB1_FIT']
        rec=self.doc('release.json',bad)
        with patch.object(runner,'parse_task_env',side_effect=AssertionError('task touched')),patch.object(runner,'verify_staged_bytes',side_effect=AssertionError('input touched')):
            with self.assertRaises(g.Hold):runner.prepare_execution(rec,self.policy,self.p/'NEVER_OPEN')
    def test_source_permission_selection_and_cohort_mismatch(self):
        for field,value in [('decision','FIT_ONLY'),('selected_branch','GX'),('rule_sha256','x'),('policy_sha256','x'),('sealed_access',True),('scientific_confirmation_read',True),('owned_source_commit_clean',False),('resources',{})]:
            r=copy.deepcopy(self.release);r[field]=value
            with self.subTest(field=field):
                with self.assertRaises(g.Hold):g.validate_authority(r,self.policy)
        r=copy.deepcopy(self.release);s=g.control(r['selection_record']);s['choice']='SbFM';r['selection_record']=self.doc('wrong_selection.json',s)
        with self.assertRaises(g.Hold):g.validate_authority(r,self.policy)
        p=copy.deepcopy(self.policy);p['cohorts']['DINOv3']=[]
        with self.assertRaises(g.Hold):g.validate_authority(self.release,p)
    def test_control_hash_refusal_and_symlink(self):
        r=dict(self.release['registration'],sha256='0'*64)
        with self.assertRaises(g.Hold):g.control(r)
        link=self.p/'symlink';link.symlink_to(self.release['registration']['path'])
        with self.assertRaises(OSError):g.control(dict(self.release['registration'],path=str(link)))
    def test_untrusted_task_never_executed_and_badseed(self):
        marker=self.p/'EXECUTED'
        for text in ['TASK=$(touch '+str(marker)+')\nARM=Sb\nSEED=413\n','touch '+str(marker),'TASK=x\nARM=Sb\nSEED=413\nSEED=414\n']:
            with self.assertRaises(g.Hold):g.parse_task_env(self.task(text))
        self.assertFalse(marker.exists())
        for seed in [0,401,403,407,408,412,418,999,'0413']:
            with self.subTest(seed=seed):
                with self.assertRaises(g.Hold):g.parse_task_env(self.task('TASK=x\nARM=Sb\nSEED='+str(seed)+'\n'))
    def test_task_role_seed_binding_and_order(self):
        task=g.parse_task_env(self.task());g.validate_task(task,'DINOv3',self.policy)
        for key,val in [('TASK','NEXTCONF_SbFM_AB1_Sb_s413'),('ARM','A'),('SEED','414')]:
            with self.assertRaises(g.Hold):g.validate_task(dict(task,**{key:val}),'DINOv3',self.policy)
        rec=self.doc('good_release.json',self.release);events=[]
        with patch.object(runner,'verify_staged_bytes',side_effect=lambda *a:events.append('bytes')),patch.object(runner,'parse_task_env',side_effect=lambda *a:(events.append('task') or task)):
            runner.prepare_execution(rec,self.policy,'ignored')
        self.assertEqual(events,['bytes','task'])
    def test_staged_provenance_refusal(self):
        p=copy.deepcopy(self.policy);p['input_files']={'pack':{'path':str(self.task('fake pack')),'sha256':'0'*64}}
        r=copy.deepcopy(self.release);r['runtime_files']={'python':{'path':str(self.task('fake runtime')),'sha256':'0'*64},'bash':{'path':str(self.p/'absent'),'sha256':'0'*64}}
        with self.assertRaises(g.Hold):g.verify_staged_bytes(r,p)

class Durability(unittest.TestCase):
    def setUp(self):self.tmp=tempfile.TemporaryDirectory();self.p=pathlib.Path(self.tmp.name)
    def tearDown(self):self.tmp.cleanup()
    def test_create_only_no_overwrite(self):
        d=self.p/'task';fake="import pathlib,os;pathlib.Path(os.environ['NEXT_CONFIRM_TASK_DURABLE'],'last.pt').write_text('fixture only');print('fixture log')"
        self.assertEqual(runner.execute_claimed([sys.executable,'-u','-c',fake],dict(os.environ),d,'TASK=fixture\nARM=Sb\nSEED=413\n'),0)
        original=(d/'stdout.log').read_bytes()
        with self.assertRaises(FileExistsError):runner.execute_claimed(['NEVER_EXECUTE'],{},d,'bad')
        self.assertEqual((d/'stdout.log').read_bytes(),original)
    def interrupted(self,sig):
        d=self.p/('task'+str(sig));child_code="import pathlib,os,time,sys;pathlib.Path(os.environ['NEXT_CONFIRM_TASK_DURABLE'],'last.pt').write_text('fake fixture checkpoint');print('fixture stdout',flush=True);print('fixture stderr',file=sys.stderr,flush=True);time.sleep(20)"
        wrapper="import sys,pathlib,os;sys.path.insert(0,"+repr(str(B))+");import run_guarded as r;sys.exit(r.execute_claimed("+repr([sys.executable,'-u','-c',child_code])+",dict(os.environ),pathlib.Path("+repr(str(d))+"),'TASK=fixture\\nARM=Sb\\nSEED=413\\n'))"
        proc=subprocess.Popen([sys.executable,'-c',wrapper],stdout=subprocess.PIPE,stderr=subprocess.PIPE)
        pid=None
        try:
            end=time.monotonic()+5
            while time.monotonic()<end:
                if (d/'last.pt').exists() and (d/'stdout.log').read_bytes():break
                time.sleep(.02)
            self.assertTrue((d/'last.pt').exists());pid=json.loads((d/'RUNNING.json').read_text())['pid']
            proc.send_signal(sig);proc.communicate(timeout=5)
            self.assertTrue((d/'CLAIM.json').exists());self.assertEqual((d/'last.pt').read_text(),'fake fixture checkpoint')
            self.assertIn(b'fixture stdout',(d/'stdout.log').read_bytes());self.assertIn(b'fixture stderr',(d/'stderr.log').read_bytes())
            if sig==signal.SIGTERM:self.assertEqual(json.loads((d/'TERMINAL.json').read_text())['status'],'FAILED_OR_INTERRUPTED')
            else:self.assertFalse((d/'TERMINAL.json').exists())
            with self.assertRaises(FileExistsError):runner.execute_claimed(['NEVER_EXECUTE'],{},d,'bad')
        finally:
            if proc.poll() is None:proc.kill();proc.communicate()
            if pid:
                try:os.killpg(pid,signal.SIGKILL)
                except ProcessLookupError:pass
    def test_term_retention(self):self.interrupted(signal.SIGTERM)
    def test_kill_retention(self):self.interrupted(signal.SIGKILL)

if __name__=='__main__':unittest.main(verbosity=2)
