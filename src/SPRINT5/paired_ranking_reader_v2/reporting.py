"""Additive descriptive rates from the already allowlisted populations only.

No RNG, resampling, inference, file I/O, threshold fitting or verdicts.
Thresholds are supplied by the unchanged statistical analysis.
"""
import numpy as np

ARMS=('bce','paired_bce','paired_rank')
SEEDS=(501,502,503,504,505)
CONTRASTS=(('ranking_minus_paired_BCE',2,1),
           ('paired_BCE_minus_BCE',1,0),
           ('ranking_minus_BCE_descriptive',2,0))


def _rates(scores,thresholds):
    scores=np.asarray(scores,float);thresholds=np.asarray(thresholds,float)
    assert scores.shape[:2]==(3,5) and scores.ndim==3
    assert thresholds.shape==(3,5) and np.isfinite(scores).all()
    assert not np.isnan(thresholds).any()
    n=scores.shape[2]
    assert n>0
    flags=(scores>thresholds[:,:,None]).sum(axis=2)
    rates=flags/n
    networks=[{'arm':arm,'seed':seed,'threshold':float(thresholds[a,s]),
               'flag_count':int(flags[a,s]),'n':n,'flag_rate':float(rates[a,s])}
              for a,arm in enumerate(ARMS) for s,seed in enumerate(SEEDS)]
    contrasts={}
    for name,a,b in CONTRASTS:
        d=rates[a]-rates[b]
        contrasts[name]={'per_seed':[{'seed':seed,'arm_flag_count':int(flags[a,s]),
                      'comparator_flag_count':int(flags[b,s]),'arm_n':n,'comparator_n':n,
                      'rate_difference':float(d[s])} for s,seed in enumerate(SEEDS)],
                      'seed_mean_rate_difference':float(d.mean())}
    return {'n_per_network':n,'per_network':networks,'paired_differences':contrasts}


def operating_point_report(primary,calibration,cells,P,C,G,point_thresholds):
    """Only point-rate reporting. S3 control flags are distinct from camera BPCER."""
    P=np.asarray(P,float);C=np.asarray(C,float)
    assert len(primary)==200 and len(calibration)==132 and len(cells)==119
    assert P.shape==(3,5,200) and C.shape==(3,5,132) and len(G)==119
    y=np.asarray([int(r['label']) for r in primary])
    assert set(y)=={0,1}
    assert all(r.get('role','dev')=='dev' and r.get('rung','S4' if r['label'] else 'S3') in ('S3','S4') for r in primary)
    result={'scope':'Descriptive registered point rates only; no added inference or reduction/adoption verdict.',
            'rule':'Strict logit > threshold; all 3 arms and 5 seeds; seed means never pooled logits.',
            'S3_label':'Same-person splice control flag rate, not camera BPCER.',
            'S4_label':'Two-person face-splice sensitivity.',
            'threshold_policies':{}}
    for policy,thresholds in [('camera_calibrated_95',np.asarray(point_thresholds,float)),
                              ('own_rule_zero',np.zeros((3,5)))]:
        primary_rates={}
        for label,name in [(0,'S3_control_false_alarms'),(1,'S4_attack_sensitivity')]:
            primary_rates[name]=_rates(P[:,:,y==label],thresholds)
        by_source=[]
        for source in sorted({r['source'] for r in primary}):
            smask=np.asarray([r['source']==source for r in primary])
            entry={'source':source}
            for label,name in [(0,'S3_control_false_alarms'),(1,'S4_attack_sensitivity')]:
                mask=smask&(y==label)
                if mask.any():entry[name]=_rates(P[:,:,mask],thresholds)
                else:entry[name]={'n_per_network':0,'status':'NO_ROWS','per_network':[],'paired_differences':{}}
            by_source.append(entry)
        genuine=[]
        for cell,scores in zip(cells,G):
            scores=np.asarray(scores,float)
            assert scores.shape==(3,5,len(cell['rows']))
            genuine.append({'cell_index':cell['cell_index'],'set':cell['set'],'source':cell['source'],
                            'metadata':cell['metadata'],'rates':_rates(scores,thresholds)})
        result['threshold_policies'][policy]={
            'primary_all':primary_rates,'primary_by_source':by_source,
            'calibration_camera_BPCER':_rates(C,thresholds),
            'heldout_genuine_cells':genuine}
    return result
