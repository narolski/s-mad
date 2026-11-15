"""Generated fixtures only. No discovery of or access to actual candidate files."""
import copy
import hashlib
import io
import json
import pathlib
import sys
import tarfile
import tempfile
import unittest

sys.path.insert(0,str(pathlib.Path(__file__).resolve().parent.parent))
import numpy as np
from paired_ranking_reader_v2 import admit
from paired_ranking_reader_v2 import data
from paired_ranking_reader_v2 import ranking_statistics as S
from paired_ranking_reader_v2.journal import Journal,atomic_result


def envelope(arm='bce',seed=501):
    task=f'SPRINT5_1_production_v3_{arm}_s{seed}'
    digest=hashlib.sha256((arm+str(seed)).encode()).hexdigest()
    e={'arm':arm,'seed':seed,'task':task,'archive_sha256':digest,'archive_path':'/synthetic/'+task+'.tar'}
    r={'status':'ELIGIBLE_METADATA_ONLY','task':task,'arm':arm,'seed':seed,'archive_sha256':digest,
       'source_sums_sha256':admit.SOURCE_SHA,'train_manifest_sha256':admit.TRAIN_SHA,'eval_manifest_sha256':admit.EVAL_SHA,
       'steps':6250,'limit':0,'checkpoint':'last','arch':'a12_clip_vitb16_madation','res':224,'batch_size':256,
       'schedule':copy.deepcopy(next(p for p in admit.json_file(pathlib.Path(__file__).parent/'EXPECTED_PLANS.json')['plans'] if p['arm']==arm and p['seed']==seed)),
       'training_complete':True,'all_logged_losses_finite':True,'checkpoint_saved':True,
       'gpu_name':'NVIDIA H100','torch':'2.11.0+cu128','cuda_runtime':'12.8',
       'reference_gate':{'byte_identical':True,'n':2496,'n_differ':0,'max_abs':0},
       'ownfit_gate':{'passed':True,'n_common':21277,'n_differ':0,'max_abs':0},
       'battery_sets':{k:{'n_scored':n,'finite':True,'complete':True} for k,n in admit.COUNTS.items()},
       'score_member_sha256':{task+'/scores_eval.npz':'0'*64,**{task+'/battery/logits_'+k+'.npz':'0'*64 for k in admit.COUNTS}}}
    return e,r


class Statistics(unittest.TestCase):
    def test_tied_auc_and_missing_stratum(self):
        self.assertEqual(S.auc([0,0,0,0],[0,1,0,1]),.5)
        self.assertEqual(S.auc([0,1],[0,1]),1)
        self.assertTrue(np.isnan(S.within_d([0,1],[0,1],[0,0])))
    def test_threshold_order_ties_infinity(self):
        self.assertEqual(S.threshold(np.arange(132)),126)
        self.assertEqual(S.threshold(np.zeros(132)),0)
        self.assertEqual((np.zeros(5)>S.threshold(np.zeros(132))).sum(),0)
        self.assertEqual(S.threshold([]),float('inf'))
    def test_uniform_shift_cannot_improve_thresholded_rate(self):
        c=np.linspace(-2,2,132);g=np.array([-1,0,2,3.])
        self.assertEqual(np.mean(g>S.threshold(c)),np.mean(g+7>S.threshold(c+7)))
        self.assertEqual(S.auc(g,[0,0,1,1]),S.auc(g+7,[0,0,1,1]))
    def test_component_multiplicity_not_deduplicated(self):
        class Fixed:
            def choice(self,units,n,replace):return [units[0]]*n
        got=S.draw_indices(['a','a','b','b'],['x']*4,Fixed())
        self.assertEqual(got.tolist(),[0,1,0,1])
    def test_precomputed_sampler_exact_rng_and_ragged_row_equivalence(self):
        components=['a','a','b','c','c','c','d','e','e'];sources=['x']*6+['y']*3
        fast=S.ComponentSampler(components,sources)
        for seed in (0,1,9,2026111401,2026111404):
            old=np.random.default_rng(seed);new=np.random.default_rng(seed)
            for _ in range(50):
                self.assertTrue(np.array_equal(S.draw_indices(components,sources,old),fast.draw(new)))
    def test_source_crossing_rejected(self):
        with self.assertRaises(AssertionError):S.draw_indices(['a','a'],['x','y'],np.random.default_rng(1))
    def test_geometry_provider_union_and_sparse(self):
        c=S.merged_components([{'components':['a','b']},{'components':['b','c']},{'components':['d']}])
        self.assertEqual(len(set(c)),2)
        self.assertEqual(S.guard_result(np.linspace(-.01,.01,100),1)['reason'],'SPARSE_COMPONENTS')
    def test_zero_variance_never_passes(self):
        self.assertEqual(S.guard_result([0]*100,100)['reason'],'ZERO_BOOTSTRAP_VARIANCE')
    def test_nonfinite_guard_draws_fail_closed_and_record_counts(self):
        with self.assertRaises(S.UnexpectedGuardDraws) as caught:S.guard_result([0,float('nan'),.01],30)
        self.assertEqual(caught.exception.details['unreadable_draw_count'],1)
        self.assertEqual(caught.exception.details['bootstrap_draws_total'],3)
        self.assertEqual(caught.exception.details['unreadable_fraction'],1/3)
    def test_one_failing_guard_blocks_IUT(self):
        good=S.guard_result(np.linspace(-.01,.01,1000),30)
        bad=S.guard_result(np.linspace(.04,.06,1000),30)
        self.assertEqual(good['status'],'PASS');self.assertEqual(bad['status'],'FAIL')
        guards=[good]*118+[bad];self.assertFalse(all(g['status']=='PASS' for g in guards))
    def test_seedmean_is_not_auc_of_average(self):
        y=[0,1];z=np.array([[0,1],[100,0]])
        self.assertEqual(np.mean([S.auc(row,y) for row in z]),.5)
        self.assertEqual(S.auc(z.mean(0),y),0)
    def test_floor_maximum_recomputed_when_best_model_switches(self):
        y=np.tile([0,0,1,1],5);q=np.repeat(np.arange(5),4)
        F=np.full((20,15),.5);F[:,0]=np.tile([0,1,1,0],5);F[:,1]=1-F[:,0]
        a=np.array([4*k+j for k in range(5) for j in (0,2)])
        b=np.array([4*k+j for k in range(5) for j in (1,3)])
        self.assertEqual(S.max_floor_statistic(F[a],y[a],q[a]),1)
        self.assertEqual(S.max_floor_statistic(F[b],y[b],q[b]),1)
        self.assertEqual(S.within_d(F[b,0],y[b],q[b]),0)
    def test_favorable_optimization_with_inconclusive_adoption(self):
        rng=np.random.default_rng(66);y=np.r_[np.zeros(100,int),np.ones(100,int)];q=np.tile(np.arange(100)%5,2)
        primary=[{'label':int(y[i]),'D_stratum':int(q[i]),'component':'p'+str(i%100),'source':'x'} for i in range(200)]
        cal=[{'component':'c'+str(i),'source':'x'} for i in range(132)]
        P=np.empty((3,5,200))
        for a in range(3):
            for s in range(5):P[a,s]=rng.normal(0,1,200)+y*(.1+.1*a+1.5*(a==2))
        C=rng.normal(0,.2,(3,5,132));F=rng.normal(0,1,(200,15))
        cells=[{'cell_index':j,'set':'dev','source':'x','metadata':{},'n_components':20,
                'rows':[{'id':f'j{j}r{i}','components':['g'+str(i)]} for i in range(20)]} for j in range(119)]
        G=[np.zeros((3,5,20)) for _ in cells]
        r=S.analyze(primary,cal,cells,P,C,G,F,draws=80)
        self.assertEqual(r['optimization']['ranking_minus_paired_BCE']['status'],'PRESENT')
        self.assertFalse(r['guard_IUT']['all_pass']);self.assertEqual(r['operational_qualification'],'INCONCLUSIVE')
        self.assertEqual(len(r['genuine_guards']),119)


class Admission(unittest.TestCase):
    def test_all15_required(self):
        entries=[envelope(a,s)[0] for a in admit.ARMS for s in admit.SEEDS]
        admit.validate_roster(entries)
        with self.assertRaises(ValueError):admit.validate_roster(entries[:-1])
        changed=copy.deepcopy(entries);changed[-1]=changed[0]
        with self.assertRaises(ValueError):admit.validate_roster(changed)
    def test_metadata_rejection_paths(self):
        e,r=envelope();admit.validate_envelope(r,e)
        changes=[('seed',502),('task','wrong'),('steps',6249),('limit',8),('checkpoint','swa'),
                 ('source_sums_sha256','x'*64),('train_manifest_sha256','x'*64),('all_logged_losses_finite',False),('torch','other')]
        for key,value in changes:
            with self.subTest(key=key):
                bad=copy.deepcopy(r);bad[key]=value
                with self.assertRaises(ValueError):admit.validate_envelope(bad,e)
        bad=copy.deepcopy(r);bad['reference_gate']['byte_identical']=False
        with self.assertRaises(ValueError):admit.validate_envelope(bad,e)
        bad=copy.deepcopy(r);del bad['battery_sets']['gd']
        with self.assertRaises(ValueError):admit.validate_envelope(bad,e)
    def test_review_source_and_roster_hashes_bound(self):
        with tempfile.TemporaryDirectory() as root:
            root=pathlib.Path(root)
            review=root/'review';review.write_text('GENERATED INDEPENDENT REVIEW')
            collector=root/'collector';collector.write_text('GENERATED COLLECTOR REVIEW')
            roster=root/'roster';roster.write_text('[]')
            code=root/'code.py';code.write_text('# generated fixture\n')
            sums=root/'SHA256SUMS';sums.write_text(admit.sha(code)+'  code.py\n')
            r={'decision':'GO_READER_READ','binding_sha256':admit.BINDING_SHA,'reviewer':'testreviewer','author':'testauthor',
               'independent_review_path':str(review),'independent_review_sha256':admit.sha(review),
               'collector_review_path':str(collector),'collector_review_sha256':admit.sha(collector),
               'minimum_guard_components':20,'zero_variance_policy':'INCONCLUSIVE',
               'reader_sums_sha256':admit.sha(sums),'roster_sha256':admit.sha(roster)}
            admit.validate_release(r,roster,root)
            review.write_text('changed')
            with self.assertRaises(ValueError):admit.validate_release(r,roster,root)
            review.write_text('GENERATED INDEPENDENT REVIEW');code.write_text('changed')
            with self.assertRaises(ValueError):admit.validate_release(r,roster,root)
            code.write_text('# generated fixture\n');roster.write_text('["changed"]')
            with self.assertRaises(ValueError):admit.validate_release(r,roster,root)
    def test_mutated_schedule_rejected_before_payload(self):
        e,r=envelope();r['schedule']['schedule_sha256']='f'*64
        with self.assertRaises(ValueError):admit.validate_envelope(r,e)
    def test_calibration_overlap_rejected_including_geometry_supplier(self):
        primary=[{'component':'p'}];cal=[{'component':'c'}]
        cells=[{'rows':[{'components':['g','c']}]}]
        with self.assertRaises(ValueError):data.validate_component_exclusion(primary,cal,cells)
        with self.assertRaises(ValueError):data.validate_component_exclusion(primary,[{'component':'p'}],[])
    def test_floor_label_or_order_mismatch_rejected(self):
        import csv
        with tempfile.TemporaryDirectory() as root:
            p=pathlib.Path(root)/'floor.csv'
            names=[f'{f}__{m}' for f in ('all_cue','luma','render','storage','geometry') for m in ('single','logreg','gbt')]
            rows=[{'id':str(i),'label':i%2,'component':'c'+str(i),'D_stratum':i%5,**{n:.5 for n in names}} for i in range(200)]
            primary=[{k:r[k] for k in ('id','label','component','D_stratum')} for r in rows]
            def save():
                with p.open('w',newline='') as f:
                    w=csv.DictWriter(f,fieldnames=['id','label','component','D_stratum',*names]);w.writeheader();w.writerows(rows)
            save();data.floors({'floor_path':p,'primary':primary})
            rows[0]['label']=1;save()
            with self.assertRaises(ValueError):data.floors({'floor_path':p,'primary':primary})
    def test_claim_and_terminal_never_retried(self):
        with tempfile.TemporaryDirectory() as root:
            j=Journal(root);j.claim({'synthetic':True});j.finish('FAILED',{'why':'generated exception'})
            with self.assertRaises(FileExistsError):j.claim({})
            with self.assertRaises(FileExistsError):j.finish('COMPLETE',{})
            self.assertEqual(json.loads((pathlib.Path(root)/'TERMINAL.json').read_text())['status'],'FAILED')
    def test_result_never_overwritten(self):
        with tempfile.TemporaryDirectory() as root:
            p=pathlib.Path(root)/'result.json';atomic_result(p,{'one':1})
            with self.assertRaises(FileExistsError):atomic_result(p,{'two':2})
            self.assertEqual(json.loads(p.read_text()),{'one':1})
    def test_npz_order_label_finiteness_and_no_historical_return(self):
        with tempfile.TemporaryDirectory() as root:
            root=pathlib.Path(root);e,r=envelope();path=root/'generated.tar';e['archive_path']=str(path)
            manifests={k:{'ids':['allowed','historical'],'sha256':'a'*64} for k in admit.COUNTS}
            meta={'manifests':manifests,'allow':{k:{'allowed'} for k in admit.COUNTS}}
            def raw(values):
                b=io.BytesIO();np.savez(b,id=np.array(['allowed','historical']),logit=np.array(values,np.float32),manifest_sha256='a'*64);return b.getvalue()
            with tarfile.open(path,'w') as t:
                for name in r['score_member_sha256']:
                    b=raw([.1,1000]);info=tarfile.TarInfo(name);info.size=len(b);t.addfile(info,io.BytesIO(b))
                    r['score_member_sha256'][name]=hashlib.sha256(b).hexdigest()
            e['archive_sha256']=admit.sha(path);e['envelope']=r
            j=Journal(root/'journal');j.claim({'synthetic':True})
            selected=data.load_allowlist(e,meta,root/'journal/CLAIM.json')
            self.assertTrue(all(set(v)=={'allowed'} for v in selected.values()))
            with tarfile.open(path) as t:
                name=next(iter(r['score_member_sha256']))
                changed={'ids':['historical','allowed'],'sha256':'a'*64}
                with self.assertRaises(ValueError):data.read_npz_member(t,name,r['score_member_sha256'][name],changed)
            b=raw([float('nan'),0]);name='bad.npz'
            bad=root/'nonfinite.tar'
            with tarfile.open(bad,'w') as t:
                info=tarfile.TarInfo(name);info.size=len(b);t.addfile(info,io.BytesIO(b))
            with tarfile.open(bad) as t:
                with self.assertRaises(ValueError):data.read_npz_member(t,name,hashlib.sha256(b).hexdigest(),manifests['dev'])
    def test_collector_never_opens_npz_or_checkpoint_payload(self):
        from unittest import mock
        from paired_ranking_reader_v2 import collect_metadata
        e,r=envelope();task=e['task'];prefix=task+'/'
        with tempfile.TemporaryDirectory() as root:
            p=pathlib.Path(root)/'fixture.tar';e['archive_path']=str(p);source=b'generated source pinfile\n'
            meta={'seed':501,'steps':6250,'final':'last','train_forward_passes':6250,'arch':r['arch'],'res':224,'bs':256}
            info={'seed':501,'steps':6250,'limit':0,'last_pt_sha256':'4'*64}
            b={'arm':'bce','seed':501,'test_mode':False,'status':'scored; statistics not computed','netcheck':dict(r['ownfit_gate'],expect_eval_sha256='0'*64),
               'train':{'sha256':admit.TRAIN_SHA},'sets':{}}
            for k,n in admit.COUNTS.items():
                b['sets'][k]={'logits_file':'logits_'+k+'.npz','image_check':{'verified':True},'n_scored':n,'n':n,'finite':True,
                              'logits_sha256':'0'*64,'sha256':admit.EVAL_SHA if k=='dev' else '5'*64}
            raw={'meta.json':json.dumps(meta).encode(),'info.json':json.dumps(info).encode(),'battery/battery.json':json.dumps(b).encode(),
                 'battery/gate.json':json.dumps(r['reference_gate']).encode(),'battery/platform.json':json.dumps({'gpu_name':'NVIDIA H100','torch':'2.11.0+cu128','cuda_runtime':'12.8'}).encode(),
                 'sprint_schedule.json':json.dumps(r['schedule']).encode(),'SHA256SUMS':source,
                 'train.log':b'step 100/6250 loss 0.2\nstep 6200/6250 loss 0.1\n','battery_status.txt':b'battery_rc=0\n',
                 'task.env':f'TASK={task}\nARM=bce\nSEED=501\n'.encode(),
                 'task_info.txt':b'pack_sha256 96c31ae29c4118947e3fd0a7a97600805cbfa5a82369c8ecbc6ee3d6349f2004 overlay_sha256 171fdb213444442762d4a716b7470dd885cd5879ba9ddda0c542060af4b4d149 steps 6250 limit 0'}
            # Invalid NPZ/torch bytes prove that collector does not interpret them.
            raw['last.pt']=b'NOT_A_TORCH_CHECKPOINT'
            raw['scores_eval.npz']=b'NOT_A_NPZ'
            for k in admit.COUNTS:raw['battery/logits_'+k+'.npz']=b'NOT_A_NPZ'
            with tarfile.open(p,'w') as t:
                for name,blob in raw.items():
                    ti=tarfile.TarInfo(prefix+name);ti.size=len(blob);t.addfile(ti,io.BytesIO(blob))
            with mock.patch.object(admit,'SOURCE_SHA',hashlib.sha256(source).hexdigest()):
                result=collect_metadata.envelope(e,'f'*64)
            self.assertEqual(result['status'],'ELIGIBLE_METADATA_ONLY')
            self.assertIn('NOT opened',result['payload_boundary'])


if __name__=='__main__':unittest.main()
