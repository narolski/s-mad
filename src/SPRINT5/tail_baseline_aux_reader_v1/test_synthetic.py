"""Generated-only numerical/NPZ/archive/Git/claim fixtures. No actual member/reader run."""
import ast
import copy
import hashlib
import importlib.util
import io
import json
import pathlib
import subprocess
import sys
import tarfile
import tempfile
import unittest
from unittest import mock
sys.path.insert(0,str(pathlib.Path(__file__).resolve().parent))
import numpy as np
import admission as A
import bridge
import metadata as M
import payload
import point_report as Q
import policy as P
import technical_collector as TC


def fixture():
    E=[]
    for source,processing in P.CELLS:
        for j in range(4):E.append({'id':f'{source}{processing}{j}','label':0,'source':source,'processing':processing})
    for family in ('af0_u50','lad_R4','lad_S4'):
        for j in range(4):E.append({'id':family+str(j),'label':1,'positive_family':family})
    cells=[{'source':s,'processing':p,'indices':[i for i,r in enumerate(E) if r['label']==0 and (r['source'],r['processing'])==(s,p)],'rows':4,'components':4} for s,p in P.CELLS]
    guards=[]
    for f in P.FAMILIES:
        ii=[i for i,r in enumerate(E) if r['label']==1 and r['positive_family']==f]
        guards.append({'family':f,'indices':ii,'rows':len(ii),'components':len(ii)})
    meta={'evaluation':E,'genuine_cells':cells,'positive_guards':guards}
    own={'calibration':{'per_network_thresholds':np.arange(15).reshape(3,5).tolist(),'unchanged_metadata':'generated'},
         'genuine_FA_rates':np.full((3,5,6),.25).tolist(),'positive_family_sensitivity':[[[.75,None,.75,.75] for _ in range(5)] for _ in range(3)],
         'original_primary_contrasts_and_intervals':[{'label':'UNCHANGED','interval':[-.1,.1]}],
         'original_utility_guards':[{'family':f,'status':'INCONCLUSIVE'} for f in P.FAMILIES for _ in range(2)],
         'original_utility_status':'INCONCLUSIVE','original_primary_result_sha256':'a'*64}
    return meta,own


def claim(path):
    J=bridge.journal();J.Journal(path).claim({'experiment_id':P.EXPERIMENT,'scope':P.READ_SCOPE,'policy_adoption_sha256':P.POLICY_SHA,
      'new_primary_read':False,'full_container_validation_after_auxiliary_claim_only':True})


def npz(ids=('cal','eval','outside'),values=None,dtype=np.float32,embedded='a'*64):
    b=io.BytesIO();np.savez(b,id=np.array(ids),logit=np.array([1,2,1e9] if values is None else values,dtype=dtype),manifest_sha256=embedded);return b.getvalue()


def archive(path,members):
    with tarfile.open(path,'w') as t:
        for name,raw in members:
            ti=tarfile.TarInfo(name);ti.size=len(raw);t.addfile(ti,io.BytesIO(raw))


class PointMath(unittest.TestCase):
    def test_n70_order7_strict_ties_hex_and_all16cases(self):
        m,o=fixture();C=np.arange(70,dtype=float);tau=Q.baseline_threshold(C)
        self.assertEqual(tau,np.nextafter(7.,-np.inf))
        r=Q.analyze(m,C,np.zeros(36),np.ones((3,5,36))*8,o)
        self.assertEqual(len(r['cases']),16);self.assertEqual(r['baseline_threshold']['float64_hex'],tau.hex())
        self.assertEqual(r['baseline_threshold']['numerator_detected_calibration'],63)
        tied=Q.analyze(m,np.zeros(70),np.zeros(36),np.zeros((3,5,36)),o)
        self.assertEqual(tied['baseline_threshold']['achieved_calibration_sensitivity'],1)
        self.assertTrue(all(x['numerator']==x['denominator'] for case in tied['cases'] for x in case['genuine_cells']))
    def test_all_candidates_same_threshold_paired_contrasts_and_denominators(self):
        m,o=fixture();Z=np.full((3,5,36),6.);Z[2]=8;Z[0,::2]=8
        r=Q.analyze(m,np.arange(70),np.zeros(36),Z,o)
        self.assertEqual({(x['arm'],x['seed']) for x in r['cases'][1:]},{(a,s) for a in P.ARMS for s in P.SEEDS})
        self.assertEqual(r['contrasts'][0]['mean_fixed_threshold_FA_difference'],[1]*6)
        self.assertEqual(r['contrasts'][1]['mean_fixed_threshold_FA_difference'],[.6]*6)
        self.assertTrue(all(x['denominator']==4 for case in r['cases'] for x in case['genuine_cells']))
    def test_missing_family_null_reason_json_finite_no_ni_or_ci(self):
        m,o=fixture();r=Q.analyze(m,np.arange(70),np.zeros(36),np.zeros((3,5,36)),o)
        for case in r['cases']:
            g=case['positive_families'][1];self.assertIsNone(g['numerator']);self.assertIsNone(g['sensitivity']);self.assertEqual(g['reason'],Q.MISSING)
        json.dumps(r,allow_nan=False)
        self.assertEqual(r['uncertainty_status'],'NOT_ESTIMATED_DESCRIPTIVE_AUXILIARY');self.assertIsNone(r['interval'])
        self.assertIsNone(r['new_winner_or_adoption_criterion']);self.assertEqual(r['own_calibrated_companion_copy_only']['original_utility_status'],'INCONCLUSIVE')
    def test_own_summaries_copy_only_and_input_unchanged(self):
        m,o=fixture();before=copy.deepcopy(o);r=Q.analyze(m,np.arange(70),np.zeros(36),np.zeros((3,5,36)),o)
        self.assertEqual(o,before);self.assertEqual(r['own_calibrated_companion_copy_only'],before)
        self.assertEqual(r['cases'][1]['own_recalibrated_threshold_copied'],o['calibration']['per_network_thresholds'][0][0])
        self.assertEqual(r['cases'][1]['fixed_minus_own_FA'],[-.25]*6)
    def test_nonfinite_shape_missing_own_fails(self):
        m,o=fixture()
        with self.assertRaises(AssertionError):Q.analyze(m,np.zeros(69),np.zeros(36),np.zeros((3,5,36)),o)
        z=np.zeros((3,5,36));z[0,0,0]=np.nan
        with self.assertRaises(AssertionError):Q.analyze(m,np.zeros(70),np.zeros(36),z,o)
        bad=copy.deepcopy(o);bad['positive_family_sensitivity'][0][0][0]=None
        with self.assertRaises(AssertionError):Q.analyze(m,np.zeros(70),np.zeros(36),np.zeros((3,5,36)),bad)
    def test_no_rng_creation_or_primary_imports(self):
        m,o=fixture()
        with mock.patch.object(np.random,'default_rng',side_effect=AssertionError('no auxiliary RNG')):
            Q.analyze(m,np.zeros(70),np.zeros(36),np.zeros((3,5,36)),o)
        forbidden={'tail_stats','ranking_statistics','hn_stats','tail_inputs'}
        for name in ('read.py','point_report.py','payload.py','admission.py','metadata.py','technical_collector.py'):
            tree=ast.parse((pathlib.Path(__file__).parent/name).read_text())
            imported={alias.name for n in ast.walk(tree) if isinstance(n,ast.Import) for alias in n.names}
            self.assertFalse(imported&forbidden)


class NPZBoundary(unittest.TestCase):
    def check(self,raw,manifest=None,members=None):
        with tempfile.TemporaryDirectory() as root:
            root=pathlib.Path(root);path=root/'fixture.tar';member='generated/scores.npz'
            archive(path,[(member,raw)] if members is None else members)
            with mock.patch.object(P,'ONCE',str(root/'once')):
                claim(root/'once')
                return payload.read_selected(path,bridge.sha(path),member,hashlib.sha256(raw).hexdigest(),manifest or {'ids':['cal','eval','outside'],'sha256':'a'*64},{'cal','eval'})
    def test_only_allowed_values_returned_outside_extreme_ignored(self):
        selected=self.check(npz());self.assertEqual(selected,{'cal':1.,'eval':2.})
    def test_missing_or_wrong_claim_precedes_npz_load(self):
        with tempfile.TemporaryDirectory() as root,mock.patch.object(P,'ONCE',root),mock.patch.object(np,'load',side_effect=AssertionError('forbidden')) as load:
            with self.assertRaises(ValueError):payload.read_selected('GENERATED','a','m','h',{},set())
            self.assertEqual(load.call_count,0)
    def test_full_order_duplicates_embedded_hash_dtype_and_lengths_rejected(self):
        for raw in (npz(ids=('eval','cal','outside')),npz(ids=('cal','cal','outside')),npz(embedded='b'*64),npz(dtype=np.float64),npz(values=[1,2])):
            with self.subTest(),self.assertRaises(ValueError):self.check(raw)
    def test_nonfinite_outside_allowlist_is_fatal_after_claim_exception(self):
        with self.assertRaises(ValueError):self.check(npz(values=[1,2,np.nan]))
    def test_missing_duplicate_member_and_wrong_digest(self):
        raw=npz()
        with self.assertRaises(ValueError):self.check(raw,members=[('other',raw)])
        with self.assertRaises(ValueError):self.check(raw,members=[('generated/scores.npz',raw)]*2)
        with tempfile.TemporaryDirectory() as root:
            root=pathlib.Path(root);p=root/'f.tar';archive(p,[('m',raw)])
            with mock.patch.object(P,'ONCE',str(root/'once')):
                claim(root/'once')
                with self.assertRaises(ValueError):payload.read_selected(p,bridge.sha(p),'m','0'*64,{'ids':['cal','eval','outside'],'sha256':'a'*64},{'cal'})


class ReleaseAndGit(unittest.TestCase):
    def release_fixture(self,root,technical):
        binding=root/'binding';binding.write_text('{}');code=root/'fixture.py';code.write_text('# generated');review=root/'review';review.write_text('GENERATED REVIEW')
        (root/'SHA256SUMS').write_text(bridge.sha(code)+'  fixture.py\n')
        adoption=root/'input.json'
        adoption.write_text(json.dumps({'decision':'GO_AUXILIARY_INPUT_BINDING_ONLY','binding_sha256':bridge.sha(binding),'source_sums_sha256':bridge.sha(root/'SHA256SUMS'),
           'author':'a','reviewer':'b','policy_adoption_sha256':P.POLICY_SHA,'scientific_auxiliary_read':'HOLD','technical_member_access':'HOLD'}))
        r={'decision':P.TECH_GO if technical else P.READ_GO,'scope':P.TECH_SCOPE if technical else P.READ_SCOPE,'experiment_id':P.EXPERIMENT,'timing':P.TIMING,
          'policy_adoption_sha256':P.POLICY_SHA,'author':'a','reviewer':'b','binding_sha256':bridge.sha(binding),'source_sums_sha256':bridge.sha(root/'SHA256SUMS'),
          'independent_review_path':str(review),'independent_review_sha256':bridge.sha(review),'input_admission_path':str(adoption),'input_admission_sha256':bridge.sha(adoption),
          'baseline_archive_sha256':P.BASELINE_SHA,'baseline_score_member':P.MEMBER,'technical_directory':P.TECHDIR,'array_deserialization':False,'scientific_auxiliary_read':'HOLD',
          'auxiliary_once':P.ONCE,'auxiliary_output':P.OUTPUT,'new_primary_read':False,'candidate_reopening':'EXACT15_EVALUATION468_ONLY',
          'full_container_validation_after_auxiliary_claim_only':True,'allowed_baseline_numeric_ids':538,'allowed_candidate_numeric_ids':468,'uncertainty_status':'NOT_ESTIMATED_DESCRIPTIVE_AUXILIARY','interval':None}
        return binding,r
    def test_technical_and_scientific_scopes_not_interchangeable_or_selfapproved(self):
        for technical in (True,False):
            with tempfile.TemporaryDirectory() as root:
                root=pathlib.Path(root);binding,r=self.release_fixture(root,technical);decision=P.TECH_GO if technical else P.READ_GO
                A.validate_release(r,binding,root,decision)
                for key,value in [('scope','PRIMARY_READ'),('decision','PROPOSED_'+decision),('reviewer','a'),('policy_adoption_sha256','0'*64),('binding_sha256','0'*64)]:
                    bad=dict(r);bad[key]=value
                    with self.assertRaises(ValueError):A.validate_release(bad,binding,root,decision)
    def test_serialization_counts_primary_retry_and_alternate_journal_rejected(self):
        with tempfile.TemporaryDirectory() as root:
            root=pathlib.Path(root);binding,r=self.release_fixture(root,False)
            for key,value in [('new_primary_read',True),('auxiliary_once','/GENERATED/alternate'),('full_container_validation_after_auxiliary_claim_only',False),('allowed_candidate_numeric_ids',538),('interval',[0,1])]:
                bad=dict(r);bad[key]=value
                with self.assertRaises(ValueError):A.validate_release(bad,binding,root,P.READ_GO)
    def test_dirty_or_untracked_actual_binding_fails_real_git(self):
        with tempfile.TemporaryDirectory() as temp:
            repo=pathlib.Path(temp);binding=repo/'binding';binding.write_text('{}');code=repo/'code';code.mkdir();pin=repo/'lastpin';pin.write_text('generated')
            (code/'SHA256SUMS').write_text('0'*64+'  fixture.py\n');(code/'fixture.py').write_text('#generated')
            subprocess.run(['git','init','-q'],cwd=repo,check=True);subprocess.run(['git','add','.'],cwd=repo,check=True)
            subprocess.run(['git','-c','user.name=Generated Fixture','-c','user.email=fixture@example.invalid','commit','-qm','generated'],cwd=repo,check=True)
            with mock.patch.object(P,'ROOT',str(repo)):paths=M.committed_paths(binding,{'pins':{str(pin):'0'*64}},code)
            self.assertEqual(paths[0],binding.relative_to(repo));M.git_clean(repo,paths)
            binding.write_text('{"updated_release_hash_matches_new_bytes":true}')
            with self.assertRaises(ValueError):M.git_clean(repo,paths)
            binding.write_text('{}');M.git_clean(repo,paths)
            subprocess.run(['git','rm','--cached','--',binding.name],cwd=repo,check=True,capture_output=True)
            with self.assertRaises(subprocess.CalledProcessError):M.git_clean(repo,paths)
    def test_all15_roster_required_no_missing_or_replacement(self):
        cases=[]
        for a in P.ARMS:
            for s in P.SEEDS:
                task=f'SPRINT5_3_pilot_v1_{a}_s{s}'
                cases.append({'arm':a,'seed':s,'task':task,'archive_path':'/GENERATED/'+task,'archive_sha256':hashlib.sha256(task.encode()).hexdigest(),'exact_aux_score_member':task+'/battery/logits_dev.npz'})
        M.validate_candidate_cases(cases)
        for rows in (cases[:-1],cases[:-1]+[cases[0]],cases+cases[:1]):
            with self.assertRaises(ValueError):M.validate_candidate_cases(rows)


class TechnicalOnly(unittest.TestCase):
    def test_invalid_npz_is_hashed_without_decode_no_runtime_inference(self):
        with tempfile.TemporaryDirectory() as root:
            root=pathlib.Path(root);p=root/'baseline.tar';prefix='AB1_Sb_s408/';common='c'*64;npzbody=b'NOT_AN_NPZ_NO_NUMERICAL_READ'
            members=[(prefix+'meta.json',json.dumps({'seed':408,'arch':'a12_clip_vitb16_madation','res':224}).encode()),
              (prefix+'info.json',json.dumps({'seed':408,'n_eval':21277,'limit':0,'torch':'2.11.0+cu128','device':'NVIDIA H100','common_py_sha256':common}).encode()),
              (prefix+'task_info.txt',b'pack_sha256 96c31ae29c4118947e3fd0a7a97600805cbfa5a82369c8ecbc6ee3d6349f2004 overlay_sha256 171fdb213444442762d4a716b7470dd885cd5879ba9ddda0c542060af4b4d149'),
              (prefix+'env.txt',b'generated'),(prefix+'gpu.txt',b'generated'),(P.MEMBER,npzbody)]
            archive(p,members)
            with mock.patch.object(P,'BASELINE_SHA',bridge.sha(p)),mock.patch.object(np,'load',side_effect=AssertionError('no decode')) as load:
                t=TC.capture(p,{'expected_common_py_sha256':common,'baseline_gate_chain_sha256':'d'*64},{'binding_sha256':'a'*64,'source_sums_sha256':'b'*64,'_release_sha256':'e'*64})
            self.assertEqual(t['score_member_sha256'],hashlib.sha256(npzbody).hexdigest());self.assertEqual(load.call_count,0)
            self.assertEqual(t['payload_ID_schema_finiteness'],'UNKNOWN_UNTIL_AUXILIARY_CLAIM');self.assertFalse(t['independent_checkpoint_rehash'])
            # Missing runtime is recorded as HOLD, never a guessed PASS.
            info=json.loads(members[1][1]);info['torch']='UNKNOWN';members[1]=(members[1][0],json.dumps(info).encode());archive(p,members)
            with mock.patch.object(P,'BASELINE_SHA',bridge.sha(p)):
                t=TC.capture(p,{'expected_common_py_sha256':common,'baseline_gate_chain_sha256':'d'*64},{'binding_sha256':'a'*64,'source_sums_sha256':'b'*64,'_release_sha256':'e'*64})
            self.assertEqual(t['runtime_provenance_status'],'UNKNOWN_OR_MISMATCH_HOLD')
    def test_unique_regular_member_headers_required(self):
        with tempfile.TemporaryDirectory() as root:
            p=pathlib.Path(root)/'f.tar';archive(p,[('m',b'one'),('m',b'two')])
            with tarfile.open(p) as t:
                with self.assertRaises(ValueError):TC.member(t,'m',100)
            with tarfile.open(p,'w') as t:
                x=tarfile.TarInfo('m');x.type=tarfile.SYMTYPE;x.linkname='other';t.addfile(x)
            with tarfile.open(p) as t:
                with self.assertRaises(ValueError):TC.member(t,'m',100)


class PermanentReadBoundary(unittest.TestCase):
    def reader(self):
        spec=importlib.util.spec_from_file_location('generated_aux_reader',pathlib.Path(__file__).parent/'read.py');module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module);return module
    def test_admit_only_never_creates_claim_or_loads_arrays(self):
        reader=self.reader()
        with mock.patch.object(A,'admit',return_value=({},None,None,None)),mock.patch.object(M,'validate_primary',return_value={}),mock.patch.object(payload,'arrays',side_effect=AssertionError('forbidden')) as load:
            with mock.patch.object(sys,'argv',['generated','--release','GENERATED','--admit-only']):reader.main()
            self.assertEqual(load.call_count,0)
    def test_claim_before_arrays_failed_terminal_reentry_and_primary_preserved(self):
        reader=self.reader()
        with tempfile.TemporaryDirectory() as root:
            root=pathlib.Path(root);binding=root/'binding';binding.write_text('generated');release=root/'release';release.write_text('generated');primary=root/'primary';primary.write_text('UNCHANGED PRIMARY')
            before=bridge.sha(primary);b={'candidates':[{'archive_sha256':str(i)} for i in range(15)]};r={'source_sums_sha256':'a'*64,'technical_receipt_sha256':'b'*64}
            with mock.patch.object(P,'BINDING',str(binding)),mock.patch.object(P,'ONCE',str(root/'once')),mock.patch.object(P,'OUTPUT',str(root/'result')),mock.patch.object(A,'admit',return_value=(b,None,r,{})),mock.patch.object(M,'validate_primary',side_effect=lambda _: {'primary':bridge.sha(primary)}):
                def injected(*args):
                    self.assertTrue((root/'once/CLAIM.json').exists());raise RuntimeError('generated payload failure')
                with mock.patch.object(payload,'arrays',side_effect=injected) as load,mock.patch.object(sys,'argv',['generated','--release',str(release)]):
                    with self.assertRaises(RuntimeError):reader.main()
                    with self.assertRaises(FileExistsError):reader.main()
                    self.assertEqual(load.call_count,1)
            self.assertEqual(bridge.sha(primary),before);self.assertEqual(M.obj(root/'once/TERMINAL.json')['status'],'FAILED')
    def test_successful_fixture_complete_atomic_json_and_no_overwrite(self):
        reader=self.reader();m,own=fixture()
        with tempfile.TemporaryDirectory() as root:
            root=pathlib.Path(root);binding=root/'binding';binding.write_text('generated');release=root/'release';release.write_text('generated')
            b={'candidates':[{'archive_sha256':str(i)} for i in range(15)],'calibration_ids':[str(i) for i in range(70)],'evaluation_ids':[r['id'] for r in m['evaluation']]}
            r={'source_sums_sha256':'a'*64,'technical_receipt_sha256':'b'*64}
            with mock.patch.object(P,'BINDING',str(binding)),mock.patch.object(P,'ONCE',str(root/'once')),mock.patch.object(P,'OUTPUT',str(root/'result')),mock.patch.object(A,'admit',return_value=(b,m,r,{'score_member_sha256':'c'*64})),mock.patch.object(M,'validate_primary',return_value={'original':'d'*64}),mock.patch.object(payload,'arrays',return_value=(np.arange(70),np.zeros(36),np.zeros((3,5,36)))),mock.patch.object(payload,'own_companion',return_value=own),mock.patch.object(sys,'argv',['generated','--release',str(release)]):
                reader.main()
                self.assertEqual(M.obj(root/'result')['status'],'AUXILIARY_POINT_COVERAGE_COMPLETE')
                self.assertEqual(M.obj(root/'once/TERMINAL.json')['status'],'COMPLETE')
                with self.assertRaises(ValueError):reader.main()


if __name__=='__main__':unittest.main()
