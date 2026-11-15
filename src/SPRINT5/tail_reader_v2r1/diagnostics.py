"""Adopted point-only evaluation diagnostics; no RNG calls or calibration-score input."""
import numpy as np
import policy as P
import shared

GRID=(.10,.50,.90,.95)
UNCERTAINTY={'uncertainty_status':'NOT_ESTIMATED_DESCRIPTIVE_DIAGNOSTIC','interval':None,
             'interpretation':'Prospective point-only diagnostic; no uncertainty PASS, equivalence or completed CI analysis.'}


def pools(meta,verify_registered=True):
    E=meta['evaluation'];out=[]
    assert not {r['id'] for r in E}&{r['id'] for r in meta['calibration']},'calibration rows cannot enter diagnostic evaluation'
    for source,n,components,composition in [('feret',54,13,{'af0_u50':46,'lad_R4':4,'lad_S4':4}),('frgc',126,14,{'af0_u50':100,'lad_R4':13,'lad_S4':13})]:
        ii=[i for i,r in enumerate(E) if int(r['label'])==1 and r['source']==source]
        assert all(E[i].get('processing','native')=='native' and E[i].get('strength','')=='' for i in ii),'processed positive proxy forbidden'
        counts={f:sum(E[i]['positive_family']==f for i in ii) for f in ('af0_u50','lad_R4','lad_S4')}
        assert sum(counts.values())==len(ii),'unknown/processed positive proxy'
        ncomp=len({E[i]['component'] for i in ii})
        if verify_registered:assert (len(ii),ncomp,counts)==(n,components,composition),'bound positive mixture differs'
        out.append({'source':source,'processing':'native_positive_mixture','indices':ii,'rows':len(ii),'components':ncomp,'family_composition':counts})
    return out


def contrasts(values):
    out=[]
    for name,left,right in P.CONTRASTS:
        delta=values[left]-values[right]
        out.append({'contrast':name,'paired_seed_differences':delta.tolist(),'mean_difference':delta.mean(0).tolist(),**UNCERTAINTY})
    return out


def analyze(meta,scores,original_thresholds,verify_registered=True):
    E=meta['evaluation'];Z=np.asarray(scores,np.float64);tau=np.asarray(original_thresholds,np.float64)
    assert Z.shape==(3,5,len(E)) and tau.shape==(3,5) and np.isfinite(Z).all() and np.isfinite(tau).all()
    positive=pools(meta,verify_registered);S=shared.load().stats;auc_cells=[]
    for cell in meta['genuine_cells']:
        pp=next(p for p in positive if p['source']==cell['source']);pi=pp['indices'];gi=cell['indices']
        assert pi and gi and not set(pi)&set(gi)
        y=np.array([1]*len(pi)+[0]*len(gi));ii=pi+gi
        values=np.array([[S.auc(Z[a,s,ii],y) for s in range(5)] for a in range(3)])
        assert np.isfinite(values).all()
        auc_cells.append({'source':cell['source'],'genuine_processing':cell['processing'],
           'label':'same-source native attack mixture versus '+cell['processing']+' genuine',
           'positive_rows':len(pi),'positive_components':pp['components'],'positive_mixture':pp['family_composition'],
           'genuine_rows':len(gi),'genuine_components':cell['components'],'pair_denominator':len(pi)*len(gi),
           'per_network_AUC':values.tolist(),'per_arm_mean_AUC':values.mean(1).tolist(),
           'contrasts':contrasts(values),**UNCERTAINTY})
    distributions=[]
    for population in [*meta['genuine_cells'],*positive]:
        ii=population['indices'];assert len(ii)>0
        values=np.quantile(Z[:,:,ii],GRID,axis=2,method='linear').transpose(1,2,0)
        margins=values-tau[:,:,None]
        distributions.append({key:value for key,value in population.items() if key!='indices'}|{
          'quantile_probabilities':list(GRID),'method':'float64 empirical linear interpolation h=(n-1)*p',
          'raw_logit_per_network_quantiles':values.tolist(),'raw_logit_per_arm_mean_quantiles':values.mean(1).tolist(),
          'threshold_relative_per_network_quantiles':margins.tolist(),'threshold_relative_per_arm_mean_quantiles':margins.mean(1).tolist(),
          'raw_logit_contrasts':contrasts(values),'threshold_relative_contrasts':contrasts(margins),
          'tail_caution':'Finite-sample interpolation; at n26,p.95 only1.3nominalrows above that fraction; not reliable extreme-tail estimation.',**UNCERTAINTY})
    assert len(auc_cells)==6 and len(distributions)==8
    return {'status':'ADOPTED_POINT_ONLY_NOT_ESTIMATED','auc_cells':auc_cells,'quantile_distributions':distributions,
       'quantile_grid':list(GRID),'calibration_population_quantiles':False,'new_rng_draws':0,
       'limits':['Fixed unequal native attack mixtures; these AUCs are not processing-matched and do not identify a source effect.',
         'Repeated captures/components retained with image weights; AUC pair denominator is not independent-pair support.',
         'All five continuation seeds shown; no pooled-seed AUC or quantile, winner gate or equivalence claim.',
         'Diagnostic CI explicitly not estimated prospectively; primary FAR/NI/bootstrap stream unchanged.'],**UNCERTAINTY}
