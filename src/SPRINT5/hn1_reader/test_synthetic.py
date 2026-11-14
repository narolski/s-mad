"""Generated envelopes/scores/archives only. Never invokes a real collector/read."""
import copy
import hashlib
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
import hn_stats as B
import payload
import collector


def case(arm=P.ARMS[0],seed=531):
    return {'arm':arm,'seed':seed,'train_manifest_sha256':'a'*64,
      'schedule':{'mode':'full248rowshufflecycle','steps':100,'batch_size':248,'exact_per_image_exposures':100,
                  'total_image_exposures':24800,'row_ids':[f'generated_{arm}_{i}' for i in range(248)],'seed':seed}}


def envelope(arm=P.ARMS[0],seed=531):
    S=shared.load();c=case(arm,seed);task=P.task(arm,seed)
    entry={'arm':arm,'seed':seed,'task':task,'archive_path':'/GENERATED/'+task+'.tar',
           'archive_sha256':hashlib.sha256(task.encode()).hexdigest()}
    r={'status':'ELIGIBLE_METADATA_ONLY','task':task,'arm':arm,'seed':seed,'archive_sha256':entry['archive_sha256'],
      'source_sums_sha256':P.TRAIN_SOURCE,'train_manifest_sha256':c['train_manifest_sha256'],'eval_manifest_sha256':S.admit.EVAL_SHA,
      'steps':100,'batch_size':248,'forwards':24800,'limit':0,'checkpoint':'last','arch':'a12_clip_vitb16_madation','res':224,
      'training_complete':True,'checkpoint_saved':True,'all_logged_losses_finite':True,'schedule':copy.deepcopy(c['schedule']),
      'gpu_name':'NVIDIA H100','torch':'2.11.0+cu128','cuda_runtime':'12.8',
      'tf32_matmul':True,'tf32_cudnn':True,'cudnn_benchmark':False,'precision':'float32, eval mode, no autocast',
      'reference_gate':{'byte_identical':True,'n':2496,'n_differ':0,'max_abs':0},
      'ownfit_gate':{'passed':True,'n_common':21277,'n_differ':0,'max_abs':0},
      'battery_sets':{k:{'complete':True,'finite':True,'n_scored':n} for k,n in S.admit.COUNTS.items()},
      'score_member_sha256':{task+'/scores_eval.npz':'0'*64,task+'/battery/logits_dev.npz':'0'*64},
      'collector_review_sha256':'b'*64,
      'warmstart':{'path':'/GENERATED/warm/AB1_Sb_s408/last_trainable.pt','conditioning':'single admitted AB1 Sb408 initialization',
       'optimizer':'fresh AdamW; no inherited moments','trainable_parameter_names':['generated.head.weight']}}
    return entry,r,c


def primary_fixture():
    #100hosts, fiveDstrata, two sources, repeated S4/S3 belonging to same component.
    return [{'id':f'row{i}','label':i//100,'D_stratum':i%5,'component':'p'+str(i%100),
             'source':'a' if i%100<50 else 'b'} for i in range(200)]


class MetadataAdmission(unittest.TestCase):
    def test_exact10roster_not15(self):
        entries=[envelope(a,s)[0] for a in P.ARMS for s in P.SEEDS];A.validate_roster(entries)
        with self.assertRaises(ValueError):A.validate_roster(entries[:-1])
        with self.assertRaises(ValueError):A.validate_roster(entries+entries[:5])
        bad=copy.deepcopy(entries);bad[-1]=bad[0]
        with self.assertRaises(ValueError):A.validate_roster(bad)
        for key in ('archive_sha256','archive_path','task'):
            bad=copy.deepcopy(entries);bad[-1][key]=bad[0][key]
            with self.assertRaises(ValueError):A.validate_roster(bad)
    def test_protocol_source_seed_manifest_platform_rejections(self):
        e,r,c=envelope();A.validate_envelope(r,e,c)
        for key,value in [('seed',532),('source_sums_sha256','f'*64),('steps',2),('batch_size',256),('forwards',1600000),
                          ('checkpoint','swa'),('limit',8),('train_manifest_sha256','f'*64),('torch','other'),('res',532),('tf32_matmul',False)]:
            with self.subTest(key=key):
                bad=copy.deepcopy(r);bad[key]=value
                with self.assertRaises(ValueError):A.validate_envelope(bad,e,c)
    def test_exact_exposure_and_row_identity(self):
        e,r,c=envelope()
        for key,value in [('exact_per_image_exposures',99),('row_ids',['wrong']*248),('total_image_exposures',64)]:
            bad=copy.deepcopy(r);bad['schedule'][key]=value
            with self.assertRaises(ValueError):A.validate_envelope(bad,e,c)
    def test_tolerance_partial_or_nonfinite_battery_rejected(self):
        e,r,c=envelope();bad=copy.deepcopy(r);bad['reference_gate']['byte_identical']=False
        with self.assertRaises(ValueError):A.validate_envelope(bad,e,c)
        bad=copy.deepcopy(r);del bad['battery_sets']['gd']
        with self.assertRaises(ValueError):A.validate_envelope(bad,e,c)
        bad=copy.deepcopy(r);bad['battery_sets']['meds']['finite']=False
        with self.assertRaises(ValueError):A.validate_envelope(bad,e,c)
    def test_warmstart_conditioning_rejected(self):
        e,r,c=envelope()
        for key,value in [('conditioning','independent initialization'),('optimizer','inherited moments'),('path','/other.pt'),('trainable_parameter_names',[])]:
            bad=copy.deepcopy(r);bad['warmstart'][key]=value
            with self.assertRaises(ValueError):A.validate_envelope(bad,e,c)
    def test_primary_only_member_allowlist(self):
        e,r,c=envelope();r['score_member_sha256'][e['task']+'/battery/logits_tt1.npz']='0'*64
        with self.assertRaises(ValueError):A.validate_envelope(r,e,c)
    def test_release_review_binding_source_and_roster_pins(self):
        with tempfile.TemporaryDirectory() as root:
            root=pathlib.Path(root);binding=root/'binding';binding.write_text('GENERATED BINDING')
            review=root/'review';review.write_text('GENERATED REVIEW')
            roster=root/'roster';roster.write_text('[]')
            code=root/'fixture.py';code.write_text('# generated\n')
            sums=root/'SHA256SUMS';sums.write_text(shared.sha(code)+'  fixture.py\n')
            inp=root/'input_admission';inp.write_text(json.dumps({'decision':'GO_INPUT_BINDING_ONLY',
               'binding_sha256':shared.sha(binding),'author':'fixtureauthor','reviewer':'fixtureroot','scientific_read':'HOLD','camera_auxiliary':'HOLD',
               'policy_input_admission_path':str(review),'policy_input_admission_sha256':shared.sha(review)}))
            r={'decision':'GO_READER_READ','experiment_id':P.EXPERIMENT,'scope':'PRIMARY_DESCRIPTIVE_ONLY',
               'author':'fixtureauthor','reviewer':'fixturereviewer','binding_sha256':shared.sha(binding),
               'independent_review_path':str(review),'independent_review_sha256':shared.sha(review),
               'reader_sums_sha256':shared.sha(sums),'roster_sha256':shared.sha(roster),
               'input_admission_path':str(inp),'input_admission_sha256':shared.sha(inp)}
            A.validate_release(r,binding,roster,root,'GO_READER_READ')
            review.write_text('changed')
            with self.assertRaises(ValueError):A.validate_release(r,binding,roster,root,'GO_READER_READ')
            review.write_text('GENERATED REVIEW');code.write_text('changed')
            with self.assertRaises(ValueError):A.validate_release(r,binding,roster,root,'GO_READER_READ')
            code.write_text('# generated\n');binding.write_text('changed')
            with self.assertRaises(ValueError):A.validate_release(r,binding,roster,root,'GO_READER_READ')


class DescriptiveStatistics(unittest.TestCase):
    def test_registered_rng_components_then_seed_matrix(self):
        primary=primary_fixture();draws,report=B.design(primary,12)
        strata={}
        for i,row in enumerate(primary):strata.setdefault(row['source'],{}).setdefault(row['component'],[]).append(i)
        rng=np.random.default_rng(2026111402);accepted=[]
        while len(accepted)<12:
            ii=[]
            for source in sorted(strata):
                units=sorted(strata[source])
                for component in rng.choice(units,len(units),replace=True):ii.extend(strata[source][component])
            if {(primary[i]['D_stratum'],primary[i]['label']) for i in ii}!={(d,y) for d in range(5) for y in (0,1)}:continue
            accepted.append(ii)
        seeds=rng.integers(0,5,size=(12,5))
        for (ii,ss),jj,tt in zip(draws,accepted,seeds):
            self.assertTrue(np.array_equal(ii,jj));self.assertTrue(np.array_equal(ss,tt))
        self.assertEqual(report['accepted'],12)
    def test_reject_missing_class_inputs_only_and_report_fraction(self):
        primary=primary_fixture()
        for row in primary:
            row['source']='only'
            if row['D_stratum']==4:row['component']='one_component'
        draws,report=B.design(primary,100)
        self.assertEqual(len(draws),100);self.assertGreater(report['rejected'],0)
        self.assertAlmostEqual(report['rejected_fraction'],report['rejected']/report['attempts'])
    def test_registered_hash_mismatch_aborts(self):
        with self.assertRaises(AssertionError):B.design(primary_fixture(),10,verify_registered=True)
    def test_point_criteria_can_hold_with_interval_containing_zero(self):
        label=B.support_label([.10,.10,.10,.10,-.20])
        self.assertEqual(label['label'],'DESCRIPTIVE_TRANSFER_SUPPORT_CRITERIA_MET')
        ci=B.interval([-.1,.2]);self.assertLess(ci['interval'][0],0)
        self.assertGreater(ci['interval'][1],0)
        self.assertEqual(B.support_label([.1,.1,.1,0,0])['label'],'CRITERIA_NOT_MET')
        self.assertEqual(B.support_label([.01]*5)['label'],'CRITERIA_NOT_MET')
    def test_nonfinite_and_zero_variance(self):
        with self.assertRaises(AssertionError):B.interval([0,float('nan')])
        self.assertEqual(B.interval([0,0])['status'],'INCONCLUSIVE_INTERVAL')
    def test_mean_network_auc_not_score_fusion_and_sign(self):
        primary=primary_fixture();y=np.array([r['label'] for r in primary]);rng=np.random.default_rng(44)
        matched=np.stack([y,100*(1-y),y,y,y]).astype(float)
        result=B.analyze(primary,np.stack([matched,np.zeros((5,200))]),rng.normal(size=(200,15)),draws=15,verify_registered=False)
        self.assertAlmostEqual(np.mean(result['primary']['per_network_AUC'][0]),.8)
        self.assertAlmostEqual(result['primary']['mean_gain'],.3)
        self.assertEqual(shared.load().stats.auc(matched.mean(0),y),0)
        self.assertEqual(result['primary']['label'],'DESCRIPTIVE_TRANSFER_SUPPORT_CRITERIA_MET')
    def test_joint_seed_pairing_and_floor_no_extra_gate(self):
        primary=primary_fixture();rng=np.random.default_rng(6);z=rng.normal(size=(5,200));F=rng.normal(size=(200,15))
        r=B.analyze(primary,np.stack([z,z]),F,draws=20,verify_registered=False)
        self.assertEqual(r['primary']['mean_gain'],0)
        self.assertTrue(all(x['matched_minus_self']==0 for x in r['all_bootstrap_replicates']))
        self.assertEqual(r['primary']['status'],'INCONCLUSIVE_INTERVAL')
        self.assertNotIn('adoption',r);self.assertNotIn('floor_gate',r['primary'])
    def test_switching_floor_maximum_uses_all15(self):
        S=shared.load().stats;y=np.tile([0,0,1,1],5);q=np.repeat(np.arange(5),4)
        f=np.full((20,15),.5);f[:,0]=np.tile([0,1,1,0],5);f[:,1]=1-f[:,0]
        for j in (0,1):
            ii=np.array([4*k+p for k in range(5) for p in (j,j+2)])
            self.assertEqual(S.max_floor_statistic(f[ii],y[ii],q[ii]),1)


class PayloadAndJournal(unittest.TestCase):
    def test_only_primary_returned_extreme_historical_camera_sentinels_ignored(self):
        S=shared.load()
        with tempfile.TemporaryDirectory() as root:
            root=pathlib.Path(root);e,r,c=envelope();p=root/'generated.tar';e['archive_path']=str(p)
            def blob():
                b=io.BytesIO();np.savez(b,id=np.array(['selected','historical191','camera']),logit=np.array([.1,1e9,-1e9],np.float32),manifest_sha256='c'*64);return b.getvalue()
            b=blob()
            with tarfile.open(p,'w') as t:
                for name in r['score_member_sha256']:
                    ti=tarfile.TarInfo(name);ti.size=len(b);t.addfile(ti,io.BytesIO(b));r['score_member_sha256'][name]=hashlib.sha256(b).hexdigest()
                bad=b'NOT_NPZ_CAMERA_PAYLOAD';ti=tarfile.TarInfo(e['task']+'/battery/logits_tt1.npz');ti.size=len(bad);t.addfile(ti,io.BytesIO(bad))
            e['archive_sha256']=shared.sha(p);e['envelope']=r
            meta={'primary':[{'id':'selected'}],'manifests':{'dev':{'ids':['selected','historical191','camera'],'sha256':'c'*64}}}
            j=S.journal.Journal(root/'once');j.claim({'synthetic':True})
            selected=payload.load_entry(e,meta,root/'once/CLAIM.json')
            self.assertEqual(set(selected),{'selected'})
            with self.assertRaises(ValueError):payload.load_entry(e,meta,root/'missingclaim')
    def test_permanent_claim_failure_and_no_overwrite(self):
        S=shared.load()
        with tempfile.TemporaryDirectory() as root:
            root=pathlib.Path(root);j=S.journal.Journal(root/'once');j.claim({'synthetic':True});j.finish('FAILED',{'why':'injected'})
            with self.assertRaises(FileExistsError):j.claim({})
            with self.assertRaises(FileExistsError):j.finish('COMPLETE',{})
            p=root/'result';S.journal.atomic_result(p,{'generated':True})
            with self.assertRaises(FileExistsError):S.journal.atomic_result(p,{'overwritten':True})
    def test_admit_only_never_reaches_payload_or_journal(self):
        import importlib.util
        # The inherited module directory also contains read.py; select OUR
        # fixture entry explicitly rather than relying on global import order.
        spec=importlib.util.spec_from_file_location('generated_hn_entry',pathlib.Path(__file__).parent/'read.py')
        reader=importlib.util.module_from_spec(spec);spec.loader.exec_module(reader)
        fake=({},None,None,None,None,None)
        with mock.patch.object(A,'admit',return_value=fake),mock.patch.object(payload,'arrays',side_effect=AssertionError('payload forbidden')) as load:
            with mock.patch.object(sys,'argv',['generated_reader','--roster','GENERATED','--release','GENERATED','--admit-only']):reader.main()
            self.assertEqual(load.call_count,0)
    def test_payload_failure_consumes_once_claim_before_any_retry(self):
        import importlib.util
        spec=importlib.util.spec_from_file_location('generated_hn_failure',pathlib.Path(__file__).parent/'read.py')
        reader=importlib.util.module_from_spec(spec);spec.loader.exec_module(reader)
        with tempfile.TemporaryDirectory() as root:
            root=pathlib.Path(root);release=root/'release';release.write_text('GENERATED');roster=root/'roster';roster.write_text('GENERATED')
            binding=root/'binding';binding.write_text('GENERATED');(root/'SHA256SUMS').write_text('GENERATED')
            fake=({'provenance_audit_sha256':'0'*64},{},None,None,{},[{'archive_sha256':'0'*64}])
            real_sha=shared.sha
            def fixture_sha(path):
                return '0'*64 if pathlib.Path(path)==pathlib.Path(reader.__file__).parent/'SHA256SUMS' else real_sha(path)
            with mock.patch.object(A,'admit',return_value=fake),mock.patch.object(P,'ONCE',str(root/'once')),mock.patch.object(P,'OUTPUT',str(root/'result')),mock.patch.object(P,'BINDING',str(binding)),mock.patch.object(shared,'sha',side_effect=fixture_sha):
                def injected(*args):
                    self.assertTrue((root/'once/CLAIM.json').exists());raise RuntimeError('GENERATED payload failure')
                with mock.patch.object(payload,'arrays',side_effect=injected) as load,mock.patch.object(sys,'argv',['generated','--roster',str(roster),'--release',str(release)]):
                    with self.assertRaises(RuntimeError):reader.main()
                    with self.assertRaises(FileExistsError):reader.main()
                    self.assertEqual(load.call_count,1)
                self.assertEqual(json.loads((root/'once/TERMINAL.json').read_text())['status'],'FAILED')
    def test_collector_accepts_only_metadata_not_fake_weight_or_npz(self):
        S=shared.load();e,r,c=envelope();prefix=e['task']+'/'
        with tempfile.TemporaryDirectory() as root:
            p=pathlib.Path(root)/'fixture.tar';e['archive_path']=str(p);src=b'GENERATED SOURCE SUMS'
            b={'seed':531,'arm':P.ARMS[0],'test_mode':False,'status':'scored; statistics not computed',
               'netcheck':dict(r['ownfit_gate'],expect_eval_sha256='0'*64),'train':{'sha256':c['train_manifest_sha256']},'sets':{}}
            for k,n in S.admit.COUNTS.items():b['sets'][k]={'n':n,'n_scored':n,'finite':True,'image_check':{'verified':True},'logits_sha256':'0'*64,'sha256':S.admit.EVAL_SHA}
            raw={'meta.json':json.dumps({'seed':531,'arch':r['arch'],'res':224,'bs':248,'steps':100,'train_forward_passes':100,'final':'last'}).encode(),
              'info.json':json.dumps({'seed':531,'steps':100,'limit':0}).encode(),'battery/battery.json':json.dumps(b).encode(),
              'battery/gate.json':json.dumps(r['reference_gate']).encode(),'battery/platform.json':json.dumps({k:r[k] for k in ('gpu_name','torch','cuda_runtime','tf32_matmul','tf32_cudnn','cudnn_benchmark','precision')}).encode(),
              'sprint_schedule.json':json.dumps(c['schedule']).encode(),'HN_warmstart.json':json.dumps(r['warmstart']).encode(),'task.env':f'TASK={e["task"]}\nARM={P.ARMS[0]}\nSEED=531\n'.encode(),
              'battery_status.txt':b'battery_rc=0','train.log':b'step 100/100 loss 0.1',
              'task_info.txt':b'pack_sha256 96c31ae29c4118947e3fd0a7a97600805cbfa5a82369c8ecbc6ee3d6349f2004 overlay_sha256 171fdb213444442762d4a716b7470dd885cd5879ba9ddda0c542060af4b4d149 steps 100 limit 0',
              'SHA256SUMS':src,'last.pt':b'INVALID_WEIGHT_PAYLOAD','scores_eval.npz':b'INVALID_NPZ','battery/logits_dev.npz':b'INVALID_NPZ'}
            with tarfile.open(p,'w') as t:
                for name,value in raw.items():ti=tarfile.TarInfo(prefix+name);ti.size=len(value);t.addfile(ti,io.BytesIO(value))
            with mock.patch.object(P,'TRAIN_SOURCE',hashlib.sha256(src).hexdigest()):
                result=collector.envelope(e,c,'f'*64)
            self.assertEqual(result['status'],'ELIGIBLE_METADATA_ONLY')
            self.assertIn('never opened',result['payload_boundary'])


if __name__=='__main__':unittest.main()
