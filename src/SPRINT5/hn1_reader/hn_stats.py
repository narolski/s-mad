"""Adopted label-conditional component bootstrap, then paired continuation seeds."""
import hashlib
import json
import numpy as np
import policy as P
import shared


def design(primary,draws=P.DRAWS,verify_registered=False):
    S=shared.load().stats
    y=np.array([int(r['label']) for r in primary]);q=np.array([int(r['D_stratum']) for r in primary])
    sampler=S.ComponentSampler([r['component'] for r in primary],[r['source'] for r in primary])
    rng=np.random.default_rng(P.RNG);accepted=[];attempts=0
    while len(accepted)<draws:
        attempts+=1
        assert attempts<=1000000,'registered infrastructure attempt cap exceeded'
        ii=sampler.draw(rng)
        if {(int(q[i]),int(y[i])) for i in ii}!={(d,label) for d in range(5) for label in (0,1)}:continue
        accepted.append(ii)
    seeds=rng.integers(0,5,size=(draws,5)) # AFTER every accepted component draw.
    encode=lambda v:json.dumps(v,separators=(',',':')).encode()
    dh=hashlib.sha256(encode([x.tolist() for x in accepted])).hexdigest()
    sh=hashlib.sha256(encode(seeds.tolist())).hexdigest()
    report={'accepted':draws,'attempts':attempts,'rejected':attempts-draws,'rejected_fraction':(attempts-draws)/attempts,
            'rng':P.RNG,'component_draw_sha256':dh,'paired_seed_draw_sha256':sh,
            'condition':'Every fixed D stratum contains both classes; label/input-only rejection',
            'draw_order':'all accepted source-stratified full-component draws THEN joint10000x5seed-indexmatrix',
            'coverage':'Conditional descriptive component/continuation bootstrap given readable fixed D strata; no unconditional95%coverage guarantee.'}
    if verify_registered:
        assert draws==10000 and len(primary)==200 and len({r['component'] for r in primary})==40
        assert (attempts,attempts-draws)==(10178,178),'registered label support differs'
        assert dh==P.DRAW_SHA and sh==P.SEED_SHA,'registered bootstrap draw streams differ'
    return list(zip(accepted,seeds)),report


def interval(values):
    v=np.asarray(values,float)
    assert np.isfinite(v).all(),'unexpected nonfinite accepted-draw statistic'
    out={'confidence':.95,'status':'INCONCLUSIVE_INTERVAL','interval':None,
         'description':'95% conditional descriptive percentile component/continuation bootstrap interval',
         'coverage_claim':'Approximate, conditional on every fixed D stratum being readable; no unconditional95%coverage guarantee.'}
    if len(v)<2:return dict(out,reason='FEWER_THAN_TWO_FINITE_DRAWS')
    if np.ptp(v)==0:return dict(out,reason='ZERO_BOOTSTRAP_VARIANCE')
    return dict(out,status='DESCRIPTIVE_INTERVAL',interval=np.quantile(v,[.025,.975],method='linear').tolist())


def support_label(effects):
    x=np.asarray(effects,float);assert x.shape==(5,) and np.isfinite(x).all()
    gain=float(x.mean());positive=int((x>0).sum())
    return {'mean_gain':gain,'positive_seed_effects':positive,'criteria':{'mean_gain_at_least':.03,'positive_seed_effects_at_least':4},
            'label':'DESCRIPTIVE_TRANSFER_SUPPORT_CRITERIA_MET' if gain>=.03 and positive>=4 else 'CRITERIA_NOT_MET',
            'interpretation':'Descriptive point criteria only; interval must be shown alongside. No statistical-superiority or adoption claim.'}


def analyze(primary,scores,floors,draws=P.DRAWS,verify_registered=True):
    S=shared.load().stats;Z=np.asarray(scores,float);F=np.asarray(floors,float)
    assert Z.shape==(2,5,len(primary)) and F.shape==(len(primary),15)
    assert np.isfinite(Z).all() and np.isfinite(F).all()
    y=np.array([int(r['label']) for r in primary]);q=np.array([int(r['D_stratum']) for r in primary])
    point=np.array([[S.within_d(Z[a,s],y,q) for s in range(5)] for a in range(2)])
    plain=np.array([[S.auc(Z[a,s],y) for s in range(5)] for a in range(2)])
    floor_point=np.array([S.within_d(F[:,j],y,q) for j in range(15)])
    assert np.isfinite(point).all() and np.isfinite(plain).all() and np.isfinite(floor_point).all()
    resamples,report=design(primary,draws,verify_registered)
    delta=[];fd=[[],[]];records=[]
    for j,(ii,seeds) in enumerate(resamples):
        means=np.array([np.mean([S.within_d(Z[a,s,ii],y[ii],q[ii]) for s in seeds]) for a in range(2)])
        floor=S.max_floor_statistic(F[ii],y[ii],q[ii])
        assert np.isfinite(means).all() and np.isfinite(floor),'nonfinite readable bootstrap draw'
        difference=float(means[0]-means[1]);delta.append(difference)
        for a in range(2):fd[a].append(float(means[a]-floor))
        records.append({'draw':j,'paired_seed_indices':seeds.tolist(),'matched_minus_self':difference,
                        'arm_mean_AUC':means.tolist(),'max_floor_AUC':float(floor)})
    effects=point[0]-point[1]
    return {'experiment_id':P.EXPERIMENT,'scope':'Native qualified HN geometry-transfer descriptive pilot; shared Sb408 continuation',
      'arms':list(P.ARMS),'seeds':list(P.SEEDS),'networks':10,
      'primary':{'contrast':'matched_minus_self','statistic':'seed mean of per-network equal-five-fixed-D-stratum AUC',
         'per_network_AUC':point.tolist(),'per_seed_matched_minus_self':effects.tolist(),
         **support_label(effects),**interval(delta)},
      'unstratified':{'per_network_AUC':plain.tolist(),'per_seed_matched_minus_self':(plain[0]-plain[1]).tolist(),
                     'seed_mean_matched_minus_self':float((plain[0]-plain[1]).mean())},
      'fixed_floors':{'per_predictor_AUC':floor_point.tolist(),'maximum_AUC':float(floor_point.max()),
         'comparisons':[{'arm':P.ARMS[a],'seed_mean_minus_max_floor':float(point[a].mean()-floor_point.max()),**interval(fd[a])} for a in range(2)],
         'scope':'Existing15fixed nuisance predictions; maximum recomputed in every shared accepted draw; descriptive, no qualification gate'},
      'construction_floor_context':{'max_AUC':.7433476,'conditional_CI':[.7125105,.7959151],
         'luma_AUC':.6043131,'color_AUC':.5680630,'interpretation':'Preserved native construction-floor diagnostic, not identity-specificity or independent construction generalization.'},
      'bootstrap':report,'all_bootstrap_replicates':records,'camera_auxiliary':'HOLD_NOT_READ',
      'limits':['Fixed200rows/40fullcomponents; no score fusion, seed selection, historical191metrics or sealed benchmark read.',
                'One common admitted Sb408 warmstart; five continuation/dropout seeds, not five independent full-training initializations.',
                'Matched versus self target geometry preserves source/color composition; neither identity isolation nor adoption.',
                'Point criteria can hold when the descriptive interval includes zero. No additional CI/floor/unstratified positivity gate.']}
