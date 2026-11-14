"""Breadth-specific descriptive estimand and single registered RNG stream."""
import hashlib
import numpy as np
import policy as P
import shared


def design(primary,draws=P.DRAWS):
    S=shared.load().stats
    labels=np.array([int(r['label']) for r in primary]);q=np.array([int(r['D_stratum']) for r in primary])
    sampler=S.ComponentSampler([r['component'] for r in primary],[r['source'] for r in primary])
    rng=np.random.default_rng(P.RNG);out=[];digest=hashlib.sha256()
    for _ in range(draws):
        rows=sampler.draw(rng)
        seeds=rng.integers(0,5,size=5) # SAME five paired-arm indices, never independent arm draws.
        readable=all(any((q[rows]==k)&(labels[rows]==y)) for k in range(5) for y in (0,1))
        digest.update(len(rows).to_bytes(8,'little'));digest.update(rows.astype('<i8').tobytes());digest.update(seeds.astype('<i8').tobytes())
        out.append((rows,seeds,readable))
    n=sum(x[2] for x in out)
    return out,{'draws_total':draws,'structurally_readable':n,'structurally_unreadable':draws-n,
                'unreadable_fraction':(draws-n)/draws,'rng':P.RNG,
                'undefined_draw_indices':[j for j,x in enumerate(out) if not x[2]],
                'draw_order':'source-stratified full components THEN joint five paired-seed indices per replicate',
                'design_sha256':digest.hexdigest(),'redraws':0,'D_merging':False}


def descriptive_interval(values,design_report):
    values=np.asarray(values,float)
    expected=design_report['structurally_readable']
    assert len(values)==expected and np.isfinite(values).all(),'unexpected nonfinite statistic outside a structurally missing-class draw'
    base={'draws_total':design_report['draws_total'],'draws_readable':len(values),
      'draws_unreadable':design_report['structurally_unreadable'],'unreadable_fraction':design_report['unreadable_fraction'],
      'confidence':.95,'coverage_claim':'No unconditional95%coverage guarantee; bootstrap is approximate.',
      'description':('95% percentile bootstrap interval conditional on readable draws' if design_report['structurally_unreadable'] else '95% percentile bootstrap interval'),
      'status':'INCONCLUSIVE_INTERVAL','interval':None}
    if len(values)<2:return dict(base,reason='FEWER_THAN_TWO_FINITE_DRAWS')
    if np.ptp(values)==0:return dict(base,reason='ZERO_BOOTSTRAP_VARIANCE')
    return dict(base,status='DESCRIPTIVE_INTERVAL',reason='PERCENTILE_NO_SUCCESS_GATE',
                interval=np.quantile(values,[.025,.975],method='linear').tolist())


def analyze(primary,scores,floors,draws=P.DRAWS):
    S=shared.load().stats;Z=np.asarray(scores,float);F=np.asarray(floors,float)
    assert Z.shape==(2,5,len(primary)) and F.shape==(len(primary),15)
    assert np.isfinite(Z).all() and np.isfinite(F).all()
    y=np.array([int(r['label']) for r in primary]);q=np.array([r['D_stratum'] for r in primary])
    point=np.array([[S.within_d(Z[a,s],y,q) for s in range(5)] for a in range(2)])
    plain=np.array([[S.auc(Z[a,s],y) for s in range(5)] for a in range(2)])
    assert np.isfinite(point).all() and np.isfinite(plain).all(),'original primary statistic undefined'
    floor_point=np.array([S.within_d(F[:,j],y,q) for j in range(15)]);assert np.isfinite(floor_point).all()
    resamples,report=design(primary,draws)
    differences=[];floor_differences=[[],[]];draw_records=[]
    for number,(rows,seeds,readable) in enumerate(resamples):
        record={'draw':number,'structurally_readable':readable,'paired_seed_indices':seeds.tolist(),
                'broad_minus_narrow':None,'arm_mean_AUC':None,'max_floor_AUC':None}
        draw_records.append(record)
        if not readable:continue # Keep the undefined record; never redraw.
        a=np.array([np.mean([S.within_d(Z[arm,s,rows],y[rows],q[rows]) for s in seeds]) for arm in range(2)])
        f=S.max_floor_statistic(F[rows],y[rows],q[rows])
        assert np.isfinite(a).all() and np.isfinite(f),'unexpected nonfinite readable AUC'
        differences.append(a[1]-a[0])
        record.update(broad_minus_narrow=float(a[1]-a[0]),arm_mean_AUC=a.tolist(),max_floor_AUC=float(f))
        for arm in range(2):floor_differences[arm].append(a[arm]-f)
    sources=[]
    for source in sorted({r['source'] for r in primary}):
        ii=np.array([i for i,r in enumerate(primary) if r['source']==source])
        source_auc=np.array([[S.auc(Z[a,s,ii],y[ii]) for s in range(5)] for a in range(2)])
        assert np.isfinite(source_auc).all()
        sources.append({'source':source,'rows':len(ii),'components':len({primary[i]['component'] for i in ii}),
          'n_positive':int(y[ii].sum()),'n_negative':int(len(ii)-y[ii].sum()),
          'per_network_unstratified_AUC':source_auc.tolist(),
          'unstratified_seed_mean_broad_minus_narrow':float((source_auc[1]-source_auc[0]).mean())})
    return {'experiment_id':P.EXPERIMENT,'scope':'MAD22-informed tiny-data breadth-versus-capture/orientation allocation; primary descriptive only',
      'arms':list(P.ARMS),'seeds':list(P.SEEDS),'networks':10,
      'primary':{'contrast':'broad_minus_narrow','statistic':'mean of per-network equal-five-D-stratum AUCs',
         'per_network_AUC':point.tolist(),'per_seed_broad_minus_narrow':(point[1]-point[0]).tolist(),
         'seed_mean_broad_minus_narrow':float((point[1]-point[0]).mean()),
         **descriptive_interval(differences,report)},
      'unstratified':{'per_network_AUC':plain.tolist(),'per_seed_broad_minus_narrow':(plain[1]-plain[0]).tolist(),
                     'seed_mean_broad_minus_narrow':float((plain[1]-plain[0]).mean())},
      'source_cells':sources,
      'fixed_floors':{'per_predictor_AUC':floor_point.tolist(),'maximum_AUC':float(floor_point.max()),
          'comparisons':[{'arm':P.ARMS[a],'seed_mean_minus_max_floor':float(point[a].mean()-floor_point.max()),
                           **descriptive_interval(floor_differences[a],report)} for a in range(2)],
          'scope':'Descriptive conditional comparison with existing15cross-fitted predictions; max recomputed every shared draw; no nuisance refit or qualification gate'},
      'bootstrap':report,'all_bootstrap_replicates':draw_records,'camera_auxiliary':'HOLD_NOT_READ',
      'decision_policy':'No binary success, superiority, .03margin,4-of5gate, automatic adoption or NEXT selection.',
      'limits':['Five paired seeds jointly represent subset/optimizer/dropout variability.',
                'Fixed32-image budget estimates breadth versus capture/orientation allocation, not isolated identity-count effect.',
                'No score fusion, seed selection, historical191metrics or sealed benchmark read.',
                'Percentile bootstrap is approximate and intervals may condition on readable draws.']}
