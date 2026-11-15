"""Generated reporting fixtures; no candidate archives or scientific reader execution."""
import copy
import hashlib
import importlib.util
import json
import pathlib
import sys
import unittest
import numpy as np
sys.path.insert(0,str(pathlib.Path(__file__).resolve().parent.parent))
from paired_ranking_reader_v2 import ranking_statistics as S,reporting,admit,data,collect_metadata,read


def fixture():
    rng=np.random.default_rng(20261114)
    y=np.tile([0,1],100)
    primary=[{'id':'dev'+str(i),'role':'dev','rung':'S4' if y[i] else 'S3',
              'label':int(y[i]),'D_stratum':int((i//2)%5),
              'component':'p'+str(i//2),'source':'source'+str((i//2)%2)} for i in range(200)]
    cal=[{'id':'cal'+str(i),'component':'c'+str(i),'source':'camera'} for i in range(132)]
    cells=[{'cell_index':j,'set':'dev','source':'genuine','metadata':{'fixture':True},'n_components':20,
            'rows':[{'id':f'j{j}r{i}','components':['g'+str(i)]} for i in range(20)]} for j in range(119)]
    P=rng.normal(size=(3,5,200))+y[None,None,:]*.5
    C=rng.normal(size=(3,5,132));G=[rng.normal(size=(3,5,20)) for _ in cells]
    F=rng.normal(size=(200,15));thresholds=np.array([[S.threshold(v) for v in arm] for arm in C])
    return primary,cal,cells,P,C,G,F,thresholds


class Reporting(unittest.TestCase):
    def test_all_networks_denominators_cells_and_differences(self):
        p,c,g,P,C,G,F,t=fixture()
        r=reporting.operating_point_report(p,c,g,P,C,G,t)
        self.assertEqual(set(r['threshold_policies']),{'camera_calibrated_95','own_rule_zero'})
        for policy,values in r['threshold_policies'].items():
            thresh=t if policy=='camera_calibrated_95' else np.zeros((3,5))
            self.assertEqual(len(values['heldout_genuine_cells']),119)
            self.assertEqual([v['cell_index'] for v in values['heldout_genuine_cells']],list(range(119)))
            for label,name in [(0,'S3_control_false_alarms'),(1,'S4_attack_sensitivity')]:
                v=values['primary_all'][name];self.assertEqual(v['n_per_network'],100)
                self.assertEqual(len(v['per_network']),15)
                self.assertEqual({(n['arm'],n['seed']) for n in v['per_network']},
                                 {(a,s) for a in reporting.ARMS for s in reporting.SEEDS})
                rates=np.mean(P[:,:,np.array([x['label']==label for x in p])]>thresh[:,:,None],axis=2)
                self.assertEqual([n['flag_count'] for n in v['per_network']],(rates*100).round().astype(int).ravel().tolist())
                for name,a,b in reporting.CONTRASTS:
                    ds=v['paired_differences'][name]['per_seed']
                    self.assertEqual(len(ds),5)
                    np.testing.assert_allclose([d['rate_difference'] for d in ds],rates[a]-rates[b])
                    self.assertAlmostEqual(v['paired_differences'][name]['seed_mean_rate_difference'],(rates[a]-rates[b]).mean())
                    self.assertTrue(all(d['arm_n']==100 and d['comparator_n']==100 for d in ds))
            self.assertEqual(values['calibration_camera_BPCER']['n_per_network'],132)
            self.assertTrue(all(v['rates']['n_per_network']==20 for v in values['heldout_genuine_cells']))
            self.assertTrue(all(v['S3_control_false_alarms']['n_per_network']==50 for v in values['primary_by_source']))

    def test_strict_threshold_ties_and_shift_behavior(self):
        p,c,g,P,C,G,F,t=fixture()
        C=np.broadcast_to(np.arange(132,dtype=float),(3,5,132)).copy();t=np.full((3,5),126.)
        P=np.broadcast_to(np.tile([-1.,0.,126.,127.],50),(3,5,200)).copy()
        G=[np.broadcast_to(np.tile([-1.,0.,126.,127.],5),(3,5,20)).copy() for _ in g]
        before=reporting.operating_point_report(p,c,g,P,C,G,t)
        shifted=reporting.operating_point_report(p,c,g,P+10,C+10,[v+10 for v in G],t+10)
        def counts(x):
            if isinstance(x,dict):return {k:counts(v) for k,v in x.items() if k!='threshold'}
            if isinstance(x,list):return [counts(v) for v in x]
            return x
        self.assertEqual(counts(before['threshold_policies']['camera_calibrated_95']),
                         counts(shifted['threshold_policies']['camera_calibrated_95']))
        own=before['threshold_policies']['own_rule_zero']['primary_all']['S3_control_false_alarms']
        ownshift=shifted['threshold_policies']['own_rule_zero']['primary_all']['S3_control_false_alarms']
        self.assertNotEqual(own['per_network'][0]['flag_count'],ownshift['per_network'][0]['flag_count'])
        self.assertEqual(before['threshold_policies']['camera_calibrated_95']['calibration_camera_BPCER']['per_network'][0]['flag_count'],5)
        self.assertEqual(reporting._rates(np.full((3,5,2),126.),t)['per_network'][0]['flag_count'],0)

    def test_existing_statistics_exactly_unchanged_and_report_deterministic(self):
        p,c,g,P,C,G,F,t=fixture()
        spec=importlib.util.spec_from_file_location('frozen_statistics_fixture_reference',
            pathlib.Path(__file__).resolve().parent.parent/'paired_ranking_reader/ranking_statistics.py')
        self.assertEqual(hashlib.sha256(pathlib.Path(spec.origin).read_bytes()).hexdigest(),
                         'e3a5d8eb5b15c28aa0bf3f3495daf970126b52827b35230123553182ae028d8a')
        old=importlib.util.module_from_spec(spec);spec.loader.exec_module(old)
        baseline=old.analyze(p,c,g,P,C,G,F,draws=40)
        changed=S.analyze(p,c,g,P,C,G,F,draws=40)
        added=changed.pop('operating_point_report')
        self.assertEqual(json.dumps(baseline,sort_keys=True),json.dumps(changed,sort_keys=True))
        self.assertEqual(added,reporting.operating_point_report(p,c,g,P,C,G,t))
        self.assertEqual(changed['detection_guard']['point_difference'],
                         added['threshold_policies']['camera_calibrated_95']['primary_all']['S4_attack_sensitivity']
                         ['paired_differences']['ranking_minus_paired_BCE']['seed_mean_rate_difference'])

    def test_versioned_imports_cannot_resolve_to_frozen_modules(self):
        for module in (S,reporting,admit,data,collect_metadata,read):
            self.assertEqual(pathlib.Path(module.__file__).resolve().parent,pathlib.Path(__file__).resolve().parent)
        self.assertIs(data.require,admit.require)
        self.assertIs(collect_metadata.admit,admit)
        self.assertIs(read.stats,S)
        self.assertIs(S.operating_point_report,reporting.operating_point_report)

    def test_historical_or_wrong_population_rejected_and_no_extra_rows(self):
        p,c,g,P,C,G,F,t=fixture()
        p[0]['role']='test'
        with self.assertRaises(AssertionError):reporting.operating_point_report(p,c,g,P,C,G,t)
        p[0]['role']='dev'
        with self.assertRaises(AssertionError):reporting.operating_point_report(p+[p[0]],c,g,np.concatenate([P,P[:,:,:1]],axis=2),C,G,t)
        report=reporting.operating_point_report(p,c,g,P,C,G,t)
        self.assertNotIn('historical',json.dumps(report))
        self.assertTrue(all(n['n']==100 for n in report['threshold_policies']['camera_calibrated_95']['primary_all']['S4_attack_sensitivity']['per_network']))


if __name__=='__main__':unittest.main()
