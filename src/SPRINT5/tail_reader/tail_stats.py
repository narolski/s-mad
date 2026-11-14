"""Pooled-positive calibration, joint component/seed bootstrap and fixed eight NI slots."""
import hashlib
import numpy as np
import policy as P
import shared


def threshold(positive_scores):
    z=np.asarray(positive_scores,dtype=np.float64)
    assert z.ndim==1 and len(z)>0 and np.isfinite(z).all(),'invalid positive calibration scores'
    k=int(np.floor(.10*len(z)))
    return float(np.nextafter(np.sort(z)[k],-np.inf))


def design(meta,draws=P.DRAWS):
    S=shared.load().stats;E=meta['evaluation'];C=meta['calibration']
    ev=S.ComponentSampler([r['component'] for r in E],[r['source'] for r in E])
    cal=S.ComponentSampler([r['component'] for r in C],[r['source'] for r in C])
    rng=np.random.default_rng(P.RNG);plans=[];digest=hashlib.sha256();empty_guards=[0]*4
    eval_masks=[np.isin(np.arange(len(E)),x['indices']) for x in meta['genuine_cells']]
    guard_masks=[np.isin(np.arange(len(E)),x['indices']) for x in meta['positive_guards']]
    for _ in range(draws):
        ei=ev.draw(rng);ci=cal.draw(rng);ss=rng.integers(0,5,size=5)
        assert len(ci)>0 and all(mask[ei].any() for mask in eval_masks),'empty required genuine/calibration draw; no redraw permitted'
        present=[bool(mask[ei].any()) for mask in guard_masks]
        for j,ok in enumerate(present):
            if not ok:empty_guards[j]+=1
            if meta['positive_guards'][j]['components']>=P.NI_MIN_COMPONENTS:assert ok,'empty supported positive guard'
        for x in (ei,ci,ss):digest.update(len(x).to_bytes(8,'little'));digest.update(x.astype('<i8').tobytes())
        plans.append((ei,ci,ss,present))
    return plans,{'attempts':draws,'rng':P.RNG,'redraws':0,'seed_indices_shared_across_all_models_and_contrasts':True,
        'draw_order':'evaluation full components within sources; independent calibration full components within sources; jointfivepairedseedindices',
        'design_sha256':digest.hexdigest(),'empty_sparse_or_absent_guard_draws':dict(zip(P.FAMILIES,empty_guards)),
        'required_genuine_and_calibration_empty_draws':0,'condition':'No rejection/filtering; fixed10000attempts'}


def percentile(values):
    v=np.asarray(values,float);assert np.isfinite(v).all(),'nonfinite primary bootstrap statistic'
    if len(v)<2 or np.ptp(v)==0:return {'status':'INCONCLUSIVE_INTERVAL','interval':None,'reason':'FEWER_THAN_TWO_DRAWS_OR_ZERO_VARIANCE'}
    return {'status':'DESCRIPTIVE_POINTWISE_INTERVAL','interval':np.quantile(v,[.025,.975],method='linear').tolist(),
            'confidence':.95,'simultaneous':False,'coverage':'Approximate percentile bootstrap; no finite-sample95%guarantee'}


def ni_guard(values,n_components,calibration_components,rows,draws=P.DRAWS):
    base={'status':'INCONCLUSIVE','lower_bound':None,'margin':P.NI_MARGIN,'alpha':P.NI_ALPHA,
          'family_size':8,'evaluation_components':n_components,'calibration_components':calibration_components,
          'rows':rows,'support_rule':'Engineering minimum20components, not proof of bootstrap coverage'}
    if rows==0:return dict(base,reason='MISSING_FAMILY')
    if n_components<20:return dict(base,reason='SPARSE_EVALUATION_COMPONENTS')
    if calibration_components<20:return dict(base,reason='SPARSE_CALIBRATION_COMPONENTS')
    v=np.asarray(values,float);assert len(v)==draws and np.isfinite(v).all(),'nonfinite/incomplete supported NI draws'
    if np.ptp(v)==0:return dict(base,reason='ZERO_BOOTSTRAP_VARIANCE')
    lower=float(np.quantile(v,P.NI_ALPHA,method='linear'))
    return dict(base,status='PASS' if lower>=P.NI_MARGIN else 'FAIL',lower_bound=lower,
                reason='APPROXIMATE_BONFERRONI_ONE_SIDED_BOUND',
                coverage='Approximate simultaneous one-sided95%family conditional on valid marginal bootstrap bounds; no finite-sample guarantee')


def statistics(meta,C,Z,ci=None,ei=None):
    C=np.asarray(C,float);Z=np.asarray(Z,float)
    assert C.shape[:2]==Z.shape[:2]==(3,5) and C.shape[2]==len(meta['calibration']) and Z.shape[2]==len(meta['evaluation'])
    assert np.isfinite(C).all() and np.isfinite(Z).all()
    ci=np.arange(C.shape[2]) if ci is None else ci;ei=np.arange(Z.shape[2]) if ei is None else ei
    tau=np.array([[threshold(C[a,s,ci]) for s in range(5)] for a in range(3)])
    cal_sens=(C[:,:,ci]>tau[:,:,None]).mean(2)
    pred=Z[:,:,ei]>tau[:,:,None]
    far=[];sens=[]
    for cell in meta['genuine_cells']:
        mask=np.isin(ei,cell['indices']);assert mask.any(),'empty genuine cell'
        far.append(pred[:,:,mask].mean(2))
    for guard in meta['positive_guards']:
        mask=np.isin(ei,guard['indices'])
        sens.append(pred[:,:,mask].mean(2) if mask.any() else np.full((3,5),np.nan))
    return tau,cal_sens,np.stack(far,axis=2),np.stack(sens,axis=2)


def analyze(meta,calibration_scores,evaluation_scores,draws=P.DRAWS):
    C=np.asarray(calibration_scores,float);Z=np.asarray(evaluation_scores,float)
    tau,cal_sens,far,sensitivity=statistics(meta,C,Z)
    plans,report=design(meta,draws);fa_draws=np.empty((2,6,draws));guard_draws=np.full((2,4,draws),np.nan);records=[]
    for j,(ei,ci,seeds,present) in enumerate(plans):
        dt,ds,df,dg=statistics(meta,C,Z,ci,ei)
        for c,(_,left,right) in enumerate(P.CONTRASTS):
            fa_draws[c,:,j]=(df[left,seeds]-df[right,seeds]).mean(0)
            for g,ok in enumerate(present):
                if ok:guard_draws[c,g,j]=(dg[left,seeds,g]-dg[right,seeds,g]).mean()
        assert np.isfinite(dt).all() and np.isfinite(ds).all() and np.isfinite(fa_draws[:,:,j]).all()
        records.append({'draw':j,'paired_seed_indices':seeds.tolist(),'thresholds':dt.tolist(),
              'mean_calibration_sensitivity':ds[:,seeds].mean(1).tolist(),'genuine_FA_differences':fa_draws[:,:,j].tolist(),
              'positive_guard_sensitivity_differences':guard_draws[:,:,j].tolist(),'positive_family_present':present})
    contrasts=[];guards=[]
    for c,(name,left,right) in enumerate(P.CONTRASTS):
        cells=[]
        for k,cell in enumerate(meta['genuine_cells']):
            effects=far[left,:,k]-far[right,:,k]
            cells.append({key:cell[key] for key in ('source','processing','rows','components')}|{
                'per_seed_FA_difference':effects.tolist(),'seed_mean_FA_difference':float(effects.mean()),**percentile(fa_draws[c,k])})
        contrasts.append({'contrast':name,'cells':cells,'interpretation':'Negative differences mean fewer genuine false alarms; all six fixed cells retained; no winner selection'})
        for g,guard in enumerate(meta['positive_guards']):
            effects=sensitivity[left,:,g]-sensitivity[right,:,g]
            result=ni_guard(guard_draws[c,g],guard['components'],meta['calibration_components'],guard['rows'],draws)
            result.update(contrast=name,family=guard['family'],per_seed_sensitivity_difference=effects.tolist(),
                    seed_mean_sensitivity_difference=float(effects.mean()),
                    readable_draws=int(np.isfinite(guard_draws[c,g]).sum()),unreadable_draws=int((~np.isfinite(guard_draws[c,g])).sum()))
            guards.append(result)
    assert len(guards)==8
    overall='INCONCLUSIVE' if any(g['status']=='INCONCLUSIVE' for g in guards) else 'ALL_NI_GUARDS_PASS' if all(g['status']=='PASS' for g in guards) else 'NI_NOT_ESTABLISHED'
    return {'experiment_id':P.EXPERIMENT,'scope':P.SCOPE,'arms':list(P.ARMS),'seeds':list(P.SEEDS),'networks':15,
       'calibration':{'rows':len(meta['calibration']),'components':meta['calibration_components'],'target_sensitivity':.9,
          'threshold_rule':'strict score>nextafter(sortedpositive[floor(.10*n)],-inf) in float64',
          'per_network_thresholds':tau.tolist(),'achieved_per_network_sensitivity':cal_sens.tolist(),
          'interpretation':'90%is the calibration operating point, not guaranteed held-out sensitivity'},
       'genuine_false_alarms':{'cells':[dict(x,indices=None) for x in meta['genuine_cells']],
          'per_network_rates':far.tolist(),'contrasts':contrasts,'intervals':'pointwise descriptive95%, not simultaneous'},
       'positive_evaluation':{'families':[dict(x,indices=None) for x in meta['positive_guards']],
          'per_network_sensitivity':sensitivity.tolist(),'utility_guards':guards,'overall_utility_status':overall,
          'interpretation':'Eight slots retained including absentaf0_u5061; noR4proxy. Missing/sparse guards prevent complete NI utility regardless of candidate effects.'},
       'bootstrap':report,'all_bootstrap_replicates':records,'diagnostic_panels':'HOLD_PENDING_PROSPECTIVE_DIAGNOSTIC_BINDING',
       'baseline_threshold_auxiliary':'HOLD_SEPARATE_SCORE_MEMBER_ID_BINDING_REQUIRED','camera_auxiliary':'HOLD_NOT_READ',
       'decision_policy':'Descriptive conditional warmstart pilot only; no primary winner, .03/4-of5 gate, superiority, adoption or NEXT selection.'}
