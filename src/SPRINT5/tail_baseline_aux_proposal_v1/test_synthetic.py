"""Generated arrays only; no real baseline/candidate payload, reader or journal."""
import pathlib
import sys
import unittest
from unittest import mock
sys.path.insert(0,str(pathlib.Path(__file__).resolve().parent))
import numpy as np
import kernel_proposal as K


def fixture():
    rows=[]
    for source in ('feret','frgc'):
        for processing in ('native','s61','s112'):
            for j in range(4):rows.append({'label':0,'source':source,'processing':processing})
    for family in ('af0_u50','lad_R4','lad_S4'):
        for j in range(4):rows.append({'label':1,'positive_family':family})
    cells=[{'source':s,'processing':p,'indices':[i for i,r in enumerate(rows) if r['label']==0 and (r['source'],r['processing'])==(s,p)]} for s in ('feret','frgc') for p in ('native','s61','s112')]
    guards=[{'family':f,'indices':[i for i,r in enumerate(rows) if r['label']==1 and r['positive_family']==f]} for f in K.FAMILIES]
    return {'evaluation':rows,'genuine_cells':cells,'positive_guards':guards}


class Auxiliary(unittest.TestCase):
    def test_exact70index7ties_and_strictthreshold(self):
        z=np.arange(70,dtype=float);tau=K.original_baseline_threshold(z)
        self.assertEqual(tau,np.nextafter(7.,-np.inf));self.assertEqual((z>tau).sum(),63)
        self.assertTrue((np.ones(70)>K.original_baseline_threshold(np.ones(70))).all())
        with self.assertRaises(AssertionError):K.original_baseline_threshold(np.zeros(69))
    def test_one_common_baseline_threshold_all15_models(self):
        m=fixture();B=np.zeros(36);C=np.arange(70,dtype=float);Z=np.ones((3,5,36))*8
        ownfa=np.zeros((3,5,6));owns=np.ones((3,5,4));owns[:,:,1]=np.nan
        r=K.proposal(m,C,B,Z,ownfa,owns)
        self.assertEqual(r['candidate_fixed_baseline_FA_rates'],np.ones((3,5,6)).tolist())
        self.assertEqual(r['baseline_original_FA_rates'],[0]*6)
        self.assertEqual(r['fixed_minus_own_recalibrated_FA_rates'],np.ones((3,5,6)).tolist())
    def test_missing_family_retained_and_no_proxy_or_ni_gate(self):
        m=fixture();fa,s=K.fixed_threshold_rates(m,np.zeros((3,5,36)),0)
        self.assertTrue(np.isnan(s[:,:,1]).all());self.assertTrue(np.isfinite(s[:,:,[0,2,3]]).all())
        self.assertEqual(s.shape,(3,5,4))
    def test_no_threshold_selection_and_bothpairedcontrasts(self):
        m=fixture();C=np.zeros(70);Z=np.stack([np.ones((5,36)),np.zeros((5,36)),np.ones((5,36))])
        own=np.zeros((3,5,6));owns=np.zeros((3,5,4));owns[:,:,1]=np.nan
        r=K.proposal(m,C,np.zeros(36),Z,own,owns)
        # Threshold is immediately BELOW zero, so zero itself is positive.
        self.assertEqual(r['candidate_fixed_baseline_FA_rates'],np.ones((3,5,6)).tolist())
        self.assertEqual([x['contrast'] for x in r['contrasts']],['cvar_minus_mean','bce_minus_mean'])
        self.assertIsNone(r['winner_or_adoption_criteria'])
    def test_nonfinite_and_wrongshape_failclosed(self):
        m=fixture()
        with self.assertRaises(AssertionError):K.fixed_threshold_rates(m,np.full(36,np.nan),0)
        with self.assertRaises(AssertionError):K.fixed_threshold_rates(m,np.zeros(35),0)
    def test_no_rng_and_no_primaryrecomputation(self):
        m=fixture();own=np.zeros((3,5,6));owns=np.zeros((3,5,4));owns[:,:,1]=np.nan
        with mock.patch.object(np.random,'default_rng',side_effect=AssertionError('no new RNG')):
            r=K.proposal(m,np.zeros(70),np.zeros(36),np.zeros((3,5,36)),own,owns)
        self.assertFalse(r['primary_recomputed']);self.assertFalse(r['primary_bootstrap_or_RNG_modified'])


if __name__=='__main__':unittest.main()
