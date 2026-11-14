"""Exact point-only auxiliary; no primary computation, file I/O, NI, CI or RNG."""
import copy
import numpy as np
import policy as P

UNCERTAINTY={'uncertainty_status':'NOT_ESTIMATED_DESCRIPTIVE_AUXILIARY','interval':None,
             'uncertainty_reason':'AFTER_PRIMARY_RESULTS_SEEN_AUXILIARY_POINT_COMPLETION'}
MISSING='NOT_ESTIMABLE_ABSENT_FAMILY'


def baseline_threshold(values):
    z=np.asarray(values,np.float64);assert z.shape==(70,) and np.isfinite(z).all()
    return float(np.nextafter(np.sort(z)[7],-np.inf))


def counts(meta,values,tau):
    z=np.asarray(values,np.float64);assert z.shape==(len(meta['evaluation']),) and np.isfinite(z).all() and np.isfinite(tau)
    cells=[];families=[]
    for c in meta['genuine_cells']:
        ii=c['indices'];assert len(ii)==c['rows'] and ii
        numerator=int((z[ii]>tau).sum())
        cells.append({k:c[k] for k in ('source','processing','rows','components')}|{'numerator':numerator,'denominator':len(ii),'rate':numerator/len(ii)})
    for g in meta['positive_guards']:
        ii=g['indices'];assert len(ii)==g['rows']
        numerator=int((z[ii]>tau).sum()) if ii else None
        families.append({k:g[k] for k in ('family','rows','components')}|{'numerator':numerator,'denominator':len(ii),
             'sensitivity':numerator/len(ii) if ii else None,'reason':None if ii else MISSING})
    assert len(cells)==6 and len(families)==4
    return cells,families


def difference(left,right):return None if left is None or right is None else float(left-right)


def mean(values):return None if any(v is None for v in values) else float(sum(values)/len(values))


def analyze(meta,calibration,baseline,candidates,companion):
    C=np.asarray(calibration,np.float64);B=np.asarray(baseline,np.float64);Z=np.asarray(candidates,np.float64)
    assert Z.shape==(3,5,len(meta['evaluation'])) and B.shape==(len(meta['evaluation']),) and np.isfinite(Z).all() and np.isfinite(B).all()
    tau=baseline_threshold(C);bc,bg=counts(meta,B,tau)
    own=copy.deepcopy(companion)
    fa=np.asarray(own['genuine_FA_rates'],float);sens=own['positive_family_sensitivity'];thresholds=own['calibration']['per_network_thresholds']
    assert fa.shape==(3,5,6) and np.isfinite(fa).all() and ((0<=fa)&(fa<=1)).all()
    assert np.asarray(thresholds,float).shape==(3,5) and np.isfinite(np.asarray(thresholds,float)).all()
    assert len(sens)==3 and all(len(x)==5 for x in sens) and all(len(row)==4 for arm in sens for row in arm)
    for arm in sens:
        for row in arm:
            for j,value in enumerate(row):
                if meta['positive_guards'][j]['rows']==0:assert value is None
                else:assert value is not None and np.isfinite(value) and 0<=value<=1
    cases=[{'model':'AB1_Sb_s408','role':'single_common_baseline','arm':None,'seed':408,
            'genuine_cells':bc,'positive_families':bg,**UNCERTAINTY}]
    bycase={}
    for a,arm in enumerate(P.ARMS):
        for s,seed in enumerate(P.SEEDS):
            cells,guards=counts(meta,Z[a,s],tau)
            fixedfa=[x['rate'] for x in cells];fixedsens=[x['sensitivity'] for x in guards]
            row={'model':f'{arm}_s{seed}','role':'candidate','arm':arm,'seed':seed,'genuine_cells':cells,'positive_families':guards,
                 'own_recalibrated_threshold_copied':thresholds[a][s],
                 'own_recalibrated_FA_rates_copied':fa[a,s].tolist(),'own_recalibrated_positive_sensitivity_copied':copy.deepcopy(sens[a][s]),
                 'fixed_minus_own_FA':[difference(fixedfa[k],float(fa[a,s,k])) for k in range(6)],
                 'fixed_minus_own_sensitivity':[difference(fixedsens[k],sens[a][s][k]) for k in range(4)],
                 'candidate_minus_single_baseline_FA':[difference(fixedfa[k],bc[k]['rate']) for k in range(6)],
                 'candidate_minus_single_baseline_sensitivity':[difference(fixedsens[k],bg[k]['sensitivity']) for k in range(4)],**UNCERTAINTY}
            cases.append(row);bycase[a,s]=row
    contrasts=[]
    for name,left,right in P.CONTRASTS:
        faeffects=[[difference(bycase[left,s]['genuine_cells'][k]['rate'],bycase[right,s]['genuine_cells'][k]['rate']) for k in range(6)] for s in range(5)]
        effects=[[difference(bycase[left,s]['positive_families'][k]['sensitivity'],bycase[right,s]['positive_families'][k]['sensitivity']) for k in range(4)] for s in range(5)]
        contrasts.append({'contrast':name,'per_seed_fixed_threshold_FA_difference':faeffects,'mean_fixed_threshold_FA_difference':[mean([row[k] for row in faeffects]) for k in range(6)],
           'per_seed_fixed_threshold_sensitivity_difference':effects,'mean_fixed_threshold_sensitivity_difference':[mean([row[k] for row in effects]) for k in range(4)],
           'positive_family_reasons':[None if g['rows'] else MISSING for g in meta['positive_guards']],**UNCERTAINTY})
    assert len(cases)==16 and len(contrasts)==2
    return {'status':'AUXILIARY_POINT_COVERAGE_COMPLETE','experiment_id':P.EXPERIMENT,'scope':P.READ_SCOPE,'timing':P.TIMING,
        'registration_disclosure':'Required baseline reporting predates primary read; point-only uncertainty and separate auxiliary reopen are disclosed after-primary-results clarification, not retroactive preregistration.',
        'baseline_threshold':{'value':tau,'float64_hex':tau.hex(),'float64_little_endian_bits':np.asarray(tau,dtype='<f8').tobytes().hex(),
            'rule':'single originalSb408 same70positive logits; nextafter(sorted[7],-inf), strict>',
            'numerator_detected_calibration':int((C>tau).sum()),'denominator_calibration':70,'achieved_calibration_sensitivity':float((C>tau).mean()),
            'TRAIN_ONLY_anchor_used':False,'recalculated_for_candidates':False,'resampled':False},
        'cases':cases,'contrasts':contrasts,'own_calibrated_companion_copy_only':own,
        'fixed_cell_order':[list(x) for x in P.CELLS],'fixed_positive_family_order':list(P.FAMILIES),
        'primary_rerun':False,'primary_RNG_bootstrap_NI_thresholds_modified':False,'new_winner_or_adoption_criterion':None,
        'baseline_is_one_model_not_five_independent_fits':True,'camera_auxiliary':'HOLD','sealed_benchmark':'HOLD',
        'coverage_interpretation':'Report completeness only; no efficacy, NI, uncertainty PASS, equivalence or adoption claim',**UNCERTAINTY}
