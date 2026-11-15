"""Generated-only tests; never invoke an actual candidate collector/reader."""
import copy
import hashlib
import importlib.util
import io
import json
import pathlib
import sys
import tarfile
import tempfile
import unittest
from unittest import mock
sys.path.insert(0,str(pathlib.Path(__file__).resolve().parent))
import numpy as np
import shared
import policy as P
import admission as A
import tail_stats as T
import payload
import collector


def case(arm='bce',seed=521):
    return {'arm':arm,'seed':seed,'train_manifest_sha256':'a'*64,'schedule':{'seed':seed,'steps':100,'bs':256,'row_exposures':25600,
       'schedule_sha256':'b'*64,'camera_per_step':118,'positive_per_step':128,'protocol_controls_per_step':10,
       'smallest_camera_group_ids':22,'common_warmstart':'AB1_Sb_s408; conditional continuation'}}


def envelope(arm='bce',seed=521):
    S=shared.load();c=case(arm,seed);task=P.task(arm,seed)
    e={'arm':arm,'seed':seed,'task':task,'archive_path':'/GENERATED/'+task+'.tar','archive_sha256':hashlib.sha256(task.encode()).hexdigest()}
    r={'status':'ELIGIBLE_METADATA_ONLY','task':task,'arm':arm,'seed':seed,'archive_sha256':e['archive_sha256'],
      'source_sums_sha256':P.TRAIN_SOURCE,'train_manifest_sha256':c['train_manifest_sha256'],'eval_manifest_sha256':S.admit.EVAL_SHA,
      'steps':100,'batch_size':256,'forwards':25600,'limit':0,'checkpoint':'last','arch':'a12_clip_vitb16_madation','res':224,
      'training_complete':True,'checkpoint_saved':True,'all_logged_losses_finite':True,'schedule':copy.deepcopy(c['schedule']),
      'training_reference_sha256':P.REFERENCE_SHA,'objective_trace_valid':True,
      'gpu_name':'NVIDIA H100','torch':'2.11.0+cu128','cuda_runtime':'12.8','tf32_matmul':True,'tf32_cudnn':True,'cudnn_benchmark':False,
      'precision':'float32, eval mode, no autocast','reference_gate':{'byte_identical':True,'n':2496,'n_differ':0,'max_abs':0},
      'ownfit_gate':{'passed':True,'n_common':21277,'n_differ':0,'max_abs':0},
      'battery_sets':{k:{'complete':True,'finite':True,'n_scored':n} for k,n in S.admit.COUNTS.items()},
      'score_member_sha256':{task+'/scores_eval.npz':'0'*64,task+'/battery/logits_dev.npz':'0'*64},'collector_review_sha256':'c'*64}
    return e,r,c


def fixture():
    C=[];E=[]
    for source in ('feret','frgc'):
        for i in range(13):C.append({'id':f'{source}cal{i}','component':f'{source}:cal{i}','source':source,'label':1})
        for i in range(30):
            family=('af0_u50','lad_R4','lad_S4')[i//10]
            E.append({'id':f'{source}p{i}','component':f'{source}:eval{i}','source':source,'label':1,'positive_family':family})
            for processing in ('native','s61','s112'):
                E.append({'id':f'{source}g{i}{processing}','component':f'{source}:eval{i}','source':source,'label':0,'processing':processing})
    cells=[{'source':s,'processing':p,'indices':[i for i,r in enumerate(E) if r['label']==0 and r['source']==s and r['processing']==p],
            'rows':30,'components':30} for s,p in P.CELLS]
    guards=[]
    for family in P.FAMILIES:
        ii=[i for i,r in enumerate(E) if r['label']==1 and r['positive_family']==family]
        guards.append({'family':family,'indices':ii,'rows':len(ii),'components':len(ii)})
    return {'calibration':C,'evaluation':E,'genuine_cells':cells,'positive_guards':guards,'calibration_components':26}


class Admission(unittest.TestCase):
    def test_exact15allarmsseeds_and_unique_archives(self):
        ee=[envelope(a,s)[0] for a in P.ARMS for s in P.SEEDS];A.validate_roster(ee)
        for entries in (ee[:-1],ee+ee[:1],ee[:-1]+[ee[0]]):
            with self.assertRaises(ValueError):A.validate_roster(entries)
        for key in ('archive_path','archive_sha256','task'):
            bad=copy.deepcopy(ee);bad[-1][key]=bad[0][key]
            with self.assertRaises(ValueError):A.validate_roster(bad)
    def test_source_reference_schedule_budget_platform_failclosed(self):
        e,r,c=envelope();A.validate_envelope(r,e,c)
        for key,value in [('seed',522),('source_sums_sha256','f'*64),('training_reference_sha256','f'*64),('objective_trace_valid',False),
          ('steps',2),('batch_size',248),('forwards',24800),('limit',8),('checkpoint','swa'),('train_manifest_sha256','0'*64),
          ('arch','other'),('res',512),('torch','other'),('tf32_matmul',False)]:
            bad=copy.deepcopy(r);bad[key]=value
            with self.subTest(key=key),self.assertRaises(ValueError):A.validate_envelope(bad,e,c)
        for key,value in [('schedule_sha256','0'*64),('row_exposures',256),('camera_per_step',128)]:
            bad=copy.deepcopy(r);bad['schedule'][key]=value
            with self.assertRaises(ValueError):A.validate_envelope(bad,e,c)
    def test_bytegate_and_no_auxiliary_members(self):
        e,r,c=envelope();bad=copy.deepcopy(r);bad['ownfit_gate']['n_differ']=1
        with self.assertRaises(ValueError):A.validate_envelope(bad,e,c)
        bad=copy.deepcopy(r);del bad['battery_sets']['gd']
        with self.assertRaises(ValueError):A.validate_envelope(bad,e,c)
        bad=copy.deepcopy(r);bad['score_member_sha256'][e['task']+'/battery/logits_tt1.npz']='0'*64
        with self.assertRaises(ValueError):A.validate_envelope(bad,e,c)
    def test_release_requires_separate_scope_inputs_and_pins(self):
        with tempfile.TemporaryDirectory() as root:
            root=pathlib.Path(root);binding=root/'binding';binding.write_text('GENERATED');roster=root/'roster';roster.write_text('[]')
            review=root/'review';review.write_text('GENERATED REVIEW');code=root/'code.py';code.write_text('# generated')
            (root/'SHA256SUMS').write_text(shared.sha(code)+'  code.py\n')
            inp=root/'input';inp.write_text(json.dumps({'decision':'GO_INPUT_BINDING_ONLY','binding_sha256':shared.sha(binding),
               'author':'generatedauthor','reviewer':'generatedroot','scientific_read':'HOLD','camera_auxiliary':'HOLD',
               'baseline_threshold_auxiliary':'HOLD','diagnostic_panels':'HOLD','policy_input_admission_path':str(review),'policy_input_admission_sha256':shared.sha(review)}))
            r={'decision':'GO_READER_READ','experiment_id':P.EXPERIMENT,'scope':P.SCOPE,'author':'a','reviewer':'b','binding_sha256':shared.sha(binding),
               'roster_sha256':shared.sha(roster),'independent_review_path':str(review),'independent_review_sha256':shared.sha(review),
               'reader_sums_sha256':shared.sha(root/'SHA256SUMS'),'input_admission_path':str(inp),'input_admission_sha256':shared.sha(inp)}
            A.validate_release(r,binding,roster,root,'GO_READER_READ')
            for key,value in [('scope','CAMERA_ORDER127'),('reviewer','a'),('binding_sha256','f'*64),('roster_sha256','f'*64)]:
                bad=dict(r);bad[key]=value
                with self.assertRaises(ValueError):A.validate_release(bad,binding,roster,root,'GO_READER_READ')
            code.write_text('changed')
            with self.assertRaises(ValueError):A.validate_release(r,binding,roster,root,'GO_READER_READ')


class CalibrationBootstrap(unittest.TestCase):
    def test_exact_positive_order_index_and_strict_ties(self):
        z=np.arange(70,dtype=np.float64);tau=T.threshold(z)
        self.assertEqual(tau,np.nextafter(7.,-np.inf));self.assertEqual(int((z>tau).sum()),63)
        z=np.ones(70);self.assertTrue((z>T.threshold(z)).all())
        with self.assertRaises(AssertionError):T.threshold([0,np.nan])
        with self.assertRaises(AssertionError):T.threshold([])
    def test_camera_threshold_substitution_changes_expected_rates(self):
        m=fixture();C=np.full((3,5,26),10.);Z=np.full((3,5,240),1.)
        tau,cal,far,sens=T.statistics(m,C,Z)
        self.assertTrue((tau>9).all());self.assertTrue((far==0).all());self.assertTrue((sens[:,:,0]==0).all())
        # Zero/camera/training threshold would predict these genuine scores positive.
        self.assertTrue((Z>0).all());self.assertTrue((cal==1).all())
    def test_registered_rng_order_and_joint_components(self):
        m=fixture();plans,report=T.design(m,12);S=shared.load().stats
        e=S.ComponentSampler([r['component'] for r in m['evaluation']],[r['source'] for r in m['evaluation']])
        c=S.ComponentSampler([r['component'] for r in m['calibration']],[r['source'] for r in m['calibration']]);rng=np.random.default_rng(2026111403)
        for ei,ci,ss,present in plans:
            self.assertTrue(np.array_equal(ei,e.draw(rng)));self.assertTrue(np.array_equal(ci,c.draw(rng)))
            self.assertTrue(np.array_equal(ss,rng.integers(0,5,size=5)))
            # Every sampled component occurrence carries its positive and all processing variants.
            for component in {m['evaluation'][i]['component'] for i in ei}:
                counts=[int((ei==i).sum()) for i,r in enumerate(m['evaluation']) if r['component']==component]
                self.assertEqual(len(set(counts)),1)
        self.assertEqual(report['attempts'],12);self.assertEqual(report['redraws'],0)
    def test_calibration_resampled_independently_and_threshold_recomputed(self):
        m=fixture();C=np.tile(np.arange(26),(3,5,1));Z=np.full((3,5,240),3.)
        plans,_=T.design(m,20);taus=[]
        for ei,ci,ss,present in plans:taus.append(T.statistics(m,C,Z,ci,ei)[0][0,0])
        self.assertGreater(np.ptp(taus),0)
    def test_common_score_shift_cancels_after_positive_recalibration(self):
        m=fixture();rng=np.random.default_rng(9);c=rng.normal(size=(5,26));z=rng.normal(size=(5,240))
        C=np.stack([c,c,c+10]);Z=np.stack([z,z,z+10]);tau,cs,far,sens=T.statistics(m,C,Z)
        self.assertTrue(np.array_equal(far[1],far[2]));self.assertTrue(np.allclose(tau[2]-tau[1],10))
    def test_pernetwork_rates_not_fused_scores(self):
        m=fixture();C=np.stack([np.tile(np.arange(26),(5,1))]*3).astype(float);Z=np.zeros((3,5,240))
        Z[2,0]=1000;Z[2,1:]=0
        r=T.analyze(m,C,Z,draws=8)
        cv=r['genuine_false_alarms']['contrasts'][0]['cells'][0]
        self.assertEqual(cv['per_seed_FA_difference'],[1,0,0,0,0]);self.assertEqual(cv['seed_mean_FA_difference'],.2)
        self.assertNotIn('adoption',r);self.assertEqual(len(r['all_bootstrap_replicates']),8)
    def test_eight_slots_include_missingfamily_no_proxy(self):
        m=fixture();C=np.zeros((3,5,26));Z=np.zeros((3,5,240));r=T.analyze(m,C,Z,draws=8)
        guards=r['positive_evaluation']['utility_guards'];self.assertEqual(len(guards),8)
        missing=[g for g in guards if g['family']=='af0_u5061'];self.assertEqual(len(missing),2)
        self.assertTrue(all(g['reason']=='MISSING_FAMILY' for g in missing))
        self.assertEqual(r['positive_evaluation']['overall_utility_status'],'INCONCLUSIVE')
    def test_fixed_bonferroni_bound_not_marginal95percent(self):
        v=np.linspace(-.03,.2,10000);g=T.ni_guard(v,25,26,100)
        self.assertEqual(g['alpha'],.05/8);self.assertAlmostEqual(g['lower_bound'],np.quantile(v,.00625))
        self.assertEqual(g['status'],'FAIL');self.assertGreater(np.quantile(v,.05),-.02)
    def test_sparse_missing_and_zero_variance_inconclusive(self):
        self.assertEqual(T.ni_guard([],0,26,0)['reason'],'MISSING_FAMILY')
        self.assertEqual(T.ni_guard([],17,26,17)['reason'],'SPARSE_EVALUATION_COMPONENTS')
        self.assertEqual(T.ni_guard([],25,19,25)['reason'],'SPARSE_CALIBRATION_COMPONENTS')
        self.assertEqual(T.ni_guard(np.zeros(10000),25,26,25)['reason'],'ZERO_BOOTSTRAP_VARIANCE')
        with self.assertRaises(AssertionError):T.ni_guard([np.nan]*10000,25,26,25)
    def test_unexpected_nonfinite_primary_fatal(self):
        with self.assertRaises(AssertionError):T.percentile([0,np.nan])
        m=fixture();C=np.zeros((3,5,26));Z=np.zeros((3,5,240));Z[0,0,0]=np.nan
        with self.assertRaises(AssertionError):T.analyze(m,C,Z,draws=4)


class PayloadAndCollector(unittest.TestCase):
    def test_primary_ids_only_and_claim_required(self):
        S=shared.load()
        with tempfile.TemporaryDirectory() as root:
            root=pathlib.Path(root);e,r,c=envelope();path=root/'fixture.tar';e['archive_path']=str(path)
            b=io.BytesIO();np.savez(b,id=np.array(['cal','eval','historical191','cameraaux']),logit=np.array([.1,.2,1e9,-1e9],np.float32),manifest_sha256='d'*64);raw=b.getvalue()
            with tarfile.open(path,'w') as t:
                for name in r['score_member_sha256']:
                    ti=tarfile.TarInfo(name);ti.size=len(raw);t.addfile(ti,io.BytesIO(raw));r['score_member_sha256'][name]=hashlib.sha256(raw).hexdigest()
            e['archive_sha256']=shared.sha(path);e['envelope']=r
            m={'calibration':[{'id':'cal'}],'evaluation':[{'id':'eval'}],
               'manifests':{'dev':{'ids':['cal','eval','historical191','cameraaux'],'sha256':'d'*64}}}
            with self.assertRaises(ValueError):payload.load_entry(e,m,root/'missing')
            j=S.journal.Journal(root/'once');j.claim({'synthetic':True})
            self.assertEqual(set(payload.load_entry(e,m,root/'once/CLAIM.json')),{'cal','eval'})
            j.finish('FAILED',{'synthetic':True})
            with self.assertRaises(FileExistsError):j.claim({})
    def test_admit_only_never_payload(self):
        spec=importlib.util.spec_from_file_location('generated_tail_reader',pathlib.Path(__file__).parent/'read.py');reader=importlib.util.module_from_spec(spec);spec.loader.exec_module(reader)
        with mock.patch.object(A,'admit',return_value=({},None,None,None)),mock.patch.object(payload,'arrays',side_effect=AssertionError('forbidden')) as load:
            with mock.patch.object(sys,'argv',['fixture','--roster','GENERATED','--release','GENERATED','--admit-only']):reader.main()
            self.assertEqual(load.call_count,0)
    def test_failure_claim_precedes_payload_and_forbids_retry(self):
        spec=importlib.util.spec_from_file_location('generated_tail_failure',pathlib.Path(__file__).parent/'read.py');reader=importlib.util.module_from_spec(spec);spec.loader.exec_module(reader)
        with tempfile.TemporaryDirectory() as root:
            root=pathlib.Path(root);release=root/'release';release.write_text('GENERATED');roster=root/'roster';roster.write_text('GENERATED')
            binding=root/'binding';binding.write_text('GENERATED')
            fake=({},None,{},[{'archive_sha256':'0'*64}]);real_sha=shared.sha
            def fixture_sha(path):return '0'*64 if pathlib.Path(path)==pathlib.Path(reader.__file__).parent/'SHA256SUMS' else real_sha(path)
            with mock.patch.object(A,'admit',return_value=fake),mock.patch.object(P,'ONCE',str(root/'once')),mock.patch.object(P,'OUTPUT',str(root/'result')),mock.patch.object(P,'BINDING',str(binding)),mock.patch.object(shared,'sha',side_effect=fixture_sha):
                def injected(*args):
                    self.assertTrue((root/'once/CLAIM.json').exists());raise RuntimeError('GENERATED failure')
                with mock.patch.object(payload,'arrays',side_effect=injected) as load,mock.patch.object(sys,'argv',['fixture','--roster',str(roster),'--release',str(release)]):
                    with self.assertRaises(RuntimeError):reader.main()
                    with self.assertRaises(FileExistsError):reader.main()
                    self.assertEqual(load.call_count,1)
                self.assertEqual(json.loads((root/'once/TERMINAL.json').read_text())['status'],'FAILED')
    def test_collector_metadata_ignores_invalid_npz_weights(self):
        S=shared.load();e,r,c=envelope();prefix=e['task']+'/'
        with tempfile.TemporaryDirectory() as root:
            path=pathlib.Path(root)/'fixture.tar';e['archive_path']=str(path);source=b'GENERATED SOURCE';ref=b'GENERATED TRAINING REFERENCE'
            battery={'seed':521,'arm':'bce','test_mode':False,'status':'scored; statistics not computed',
              'netcheck':dict(r['ownfit_gate'],expect_eval_sha256='0'*64),'train':{'sha256':c['train_manifest_sha256']},'sets':{}}
            for k,n in S.admit.COUNTS.items():battery['sets'][k]={'n':n,'n_scored':n,'finite':True,'image_check':{'verified':True},'logits_sha256':'0'*64,'sha256':S.admit.EVAL_SHA}
            raw={'meta.json':json.dumps({'seed':521,'arch':r['arch'],'res':224,'bs':256,'steps':100,'train_forward_passes':100,'final':'last'}).encode(),
              'info.json':json.dumps({'seed':521,'steps':100,'limit':0}).encode(),'battery/battery.json':json.dumps(battery).encode(),
              'battery/gate.json':json.dumps(r['reference_gate']).encode(),'battery/platform.json':json.dumps({k:r[k] for k in ('gpu_name','torch','cuda_runtime','tf32_matmul','tf32_cudnn','cudnn_benchmark','precision')}).encode(),
              'sprint_schedule.json':json.dumps(c['schedule']).encode(),'TRAIN_ONLY_reference.json':ref,'task.env':f'TASK={e["task"]}\nARM=bce\nSEED=521\n'.encode(),
              'battery_status.txt':b'battery_rc=0','train.log':b'step 100/100 loss 0.1','SHA256SUMS':source,
              'task_info.txt':b'pack_sha256 96c31ae29c4118947e3fd0a7a97600805cbfa5a82369c8ecbc6ee3d6349f2004 overlay_sha256 171fdb213444442762d4a716b7470dd885cd5879ba9ddda0c542060af4b4d149 steps 100 limit 0',
              'last.pt':b'INVALID_WEIGHT','scores_eval.npz':b'INVALID_NPZ','battery/logits_dev.npz':b'INVALID_NPZ'}
            with tarfile.open(path,'w') as t:
                for name,value in raw.items():ti=tarfile.TarInfo(prefix+name);ti.size=len(value);t.addfile(ti,io.BytesIO(value))
            with mock.patch.object(P,'TRAIN_SOURCE',hashlib.sha256(source).hexdigest()),mock.patch.object(P,'REFERENCE_SHA',hashlib.sha256(ref).hexdigest()):
                self.assertEqual(collector.envelope(e,c,'c'*64)['status'],'ELIGIBLE_METADATA_ONLY')
    def test_trace_rejects_missing_duplicate_commits_nonfinite_and_bad_occupancy(self):
        prefix='generated/';count={'feret/native':32,'feret/s61':32,'frgc/native':32,'frgc/s61':22}
        rr=[{'step':j,'effective_negative_identities':count,'tail_occupancy':dict(count),'violation':[0.]*4,
             'dual':[0.]*4,'eta':[0.]*4,'dual_after':[0.]*4,'eta_after':[0.]*4} for j in range(100)]
        class Header:
            name=prefix+'tail_objective_state.pt';size=1
            def isfile(self):return True
        class Tar:
            def getmembers(self):return [Header()]
        raw=lambda name:'\n'.join(json.dumps(x) for x in rr).encode()
        self.assertTrue(collector.trace_valid(Tar(),prefix,raw,'cvar'))
        rr[-1]['step']=98
        with self.assertRaises(ValueError):collector.trace_valid(Tar(),prefix,raw,'cvar')
        rr[-1]['step']=99;rr[-1]['eta_after'][0]=float('nan')
        with self.assertRaises(ValueError):collector.trace_valid(Tar(),prefix,raw,'cvar')


if __name__=='__main__':unittest.main()
