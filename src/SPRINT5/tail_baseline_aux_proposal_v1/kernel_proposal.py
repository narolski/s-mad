"""Math-only fixed-Sb408 auxiliary proposal; no files, readers, RNG, claims or model calls."""
import numpy as np

FAMILIES=('af0_u50','af0_u5061','lad_R4','lad_S4')
CONTRASTS=(('cvar_minus_mean',2,1),('bce_minus_mean',0,1))


def original_baseline_threshold(positive_scores):
    z=np.asarray(positive_scores,np.float64)
    assert z.shape==(70,) and np.isfinite(z).all(),'exact original70baseline positives required'
    return float(np.nextafter(np.sort(z)[int(np.floor(.1*len(z)))],-np.inf))


def fixed_threshold_rates(meta,evaluation_scores,tau):
    z=np.asarray(evaluation_scores,np.float64);assert z.shape[-1]==len(meta['evaluation']) and np.isfinite(z).all() and np.isfinite(tau)
    pred=z>tau;fa=[];sensitivity=[]
    for cell in meta['genuine_cells']:
        ii=cell['indices'];assert ii
        fa.append(pred[...,ii].mean(-1))
    for family in meta['positive_guards']:
        ii=family['indices']
        sensitivity.append(pred[...,ii].mean(-1) if ii else np.full(z.shape[:-1],np.nan))
    return np.stack(fa,axis=-1),np.stack(sensitivity,axis=-1)


def proposal(meta,baseline_calibration,baseline_evaluation,candidate_evaluation,own_recalibrated_fa,own_recalibrated_sensitivity):
    """All arrays must be supplied by a future independently admitted auxiliary-only path."""
    tau=original_baseline_threshold(baseline_calibration)
    B=np.asarray(baseline_evaluation,np.float64);Z=np.asarray(candidate_evaluation,np.float64)
    assert B.shape==(len(meta['evaluation']),) and Z.shape==(3,5,len(meta['evaluation']))
    baseline_fa,baseline_sensitivity=fixed_threshold_rates(meta,B,tau)
    fa,sensitivity=fixed_threshold_rates(meta,Z,tau)
    own_fa=np.asarray(own_recalibrated_fa,np.float64);own_sensitivity=np.asarray(own_recalibrated_sensitivity,np.float64)
    assert own_fa.shape==(3,5,6) and own_sensitivity.shape==(3,5,4) and np.isfinite(own_fa).all()
    assert all(np.isfinite(own_sensitivity[:,:,j]).all() for j,g in enumerate(meta['positive_guards']) if g['indices'])
    contrasts=[]
    for name,left,right in CONTRASTS:
        f=fa[left]-fa[right];s=sensitivity[left]-sensitivity[right]
        contrasts.append({'contrast':name,'per_seed_fixed_baseline_FA_difference':f.tolist(),'mean_fixed_baseline_FA_difference':f.mean(0).tolist(),
            'per_seed_fixed_baseline_sensitivity_difference':s.tolist(),'mean_fixed_baseline_sensitivity_difference':s.mean(0).tolist()})
    return {'status':'MATHEMATICAL_POINT_KERNEL_PROPOSAL_NOT_A_READ_RELEASE',
       'baseline_original_positive_threshold':tau,'baseline_achieved_calibration_sensitivity':float((np.asarray(baseline_calibration)>tau).mean()),
       'baseline_original_FA_rates':baseline_fa.tolist(),'baseline_original_positive_family_sensitivity':baseline_sensitivity.tolist(),
       'candidate_fixed_baseline_FA_rates':fa.tolist(),'candidate_fixed_baseline_positive_family_sensitivity':sensitivity.tolist(),
       'candidate_own_recalibrated_FA_rates_from_existing_result':own_fa.tolist(),
       'candidate_own_recalibrated_sensitivity_from_existing_result':own_sensitivity.tolist(),
       'fixed_minus_own_recalibrated_FA_rates':(fa-own_fa).tolist(),
       'fixed_minus_own_recalibrated_sensitivity':(sensitivity-own_sensitivity).tolist(),
       'candidate_minus_baseline_original_FA_rates':(fa-baseline_fa).tolist(),
       'candidate_minus_baseline_original_sensitivity':(sensitivity-baseline_sensitivity).tolist(),
       'contrasts':contrasts,'uncertainty_policy':'UNRESOLVED_REQUIRES_EXPLICIT_REVIEW_AFTER_PRIMARY_RESULTS_SEEN',
       'winner_or_adoption_criteria':None,'primary_recomputed':False,'primary_bootstrap_or_RNG_modified':False,
       'missing_family_policy':'Keep all4slots including absentaf0_u5061; noR4proxy; no invented zero sensitivity or NI pass'}
