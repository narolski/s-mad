"""Pure score statistics for the bound paired-ranking cycle. No file access."""
import math
import numpy as np

ARMS=('bce','paired_bce','paired_rank')
SEEDS=(501,502,503,504,505)


class UnexpectedGuardDraws(ValueError):
    def __init__(self,details):
        self.details=details
        super().__init__('Unexpected nonfinite guard bootstrap: '+str(details))


def auc(scores,labels):
    s=np.asarray(scores,float);y=np.asarray(labels,int)
    assert s.ndim==y.ndim==1 and len(s)==len(y) and np.isfinite(s).all()
    assert set(np.unique(y))<={0,1}
    p=int(y.sum());n=len(y)-p
    if not p or not n:return float('nan')
    order=np.argsort(s,kind='stable');rank=np.empty(len(s),float)
    values=s[order];starts=np.r_[0,np.flatnonzero(values[1:]!=values[:-1])+1];ends=np.r_[starts[1:],len(s)]
    for a,b in zip(starts,ends):rank[order[a:b]]=(a+1+b)/2
    return float((rank[y==1].sum()-p*(p+1)/2)/(p*n))


def within_d(scores,labels,strata):
    y=np.asarray(labels,int);q=np.asarray(strata,int)
    values=[auc(np.asarray(scores)[q==k],y[q==k]) for k in range(5)]
    return float(np.mean(values)) if np.isfinite(values).all() else float('nan')


def max_floor_statistic(floors,labels,strata):
    f=np.asarray(floors)
    assert f.shape==(len(labels),15)
    values=np.array([within_d(f[:,j],labels,strata) for j in range(15)])
    return float(values.max()) if np.isfinite(values).all() else float('nan')


def threshold(scores):
    s=np.asarray(scores,float)
    assert s.ndim==1 and np.isfinite(s).all()
    n=len(s);k=math.ceil(.95*(n+1))
    return float('inf') if k>n else float(np.partition(s,k-1)[k-1])


def draw_indices(components,sources,rng):
    c=np.asarray(components,str);s=np.asarray(sources,str)
    assert len(c)==len(s)>0
    for group in np.unique(c):assert len(set(s[c==group]))==1,'component crosses source strata'
    result=[]
    for source in sorted(set(s)):
        units=sorted(set(c[s==source]))
        for group in rng.choice(units,len(units),replace=True):result.extend(np.flatnonzero(c==group))
    return np.asarray(result,int)


class ComponentSampler:
    """Precomputed ragged component rows; exact legacy ordering/RNG choices."""
    def __init__(self,components,sources):
        rows={};source_of={}
        assert len(components)==len(sources)>0
        for i,(component,source) in enumerate(zip(components,sources)):
            if component in source_of:assert source_of[component]==source,'component crosses source strata'
            source_of[component]=source;rows.setdefault(component,[]).append(i)
        self.strata=[]
        for source in sorted(set(sources)):
            units=sorted(g for g in rows if source_of[g]==source)
            lengths=np.array([len(rows[g]) for g in units],int)
            starts=np.r_[0,np.cumsum(lengths)[:-1]]
            flat=np.array([i for g in units for i in rows[g]],int)
            self.strata.append((len(units),lengths,starts,flat))
    def draw(self,rng):
        result=[]
        for n,lengths,starts,flat in self.strata:
            # numpy choice(array,n) draws these same integer positions internally.
            selected=rng.choice(n,n,replace=True)
            sizes=lengths[selected];prefix=np.r_[0,np.cumsum(sizes)[:-1]]
            positions=np.repeat(starts[selected]-prefix,sizes)+np.arange(sizes.sum())
            result.append(flat[positions])
        return np.concatenate(result)


def merged_components(rows):
    """A multi-provider row connects all of its person components."""
    parent={}
    def root(x):
        parent.setdefault(x,x)
        if parent[x]!=x:parent[x]=root(parent[x])
        return parent[x]
    for r in rows:
        parts=r['components'];assert parts
        for p in parts[1:]:
            a,b=root(parts[0]),root(p)
            if a!=b:parent[max(a,b)]=min(a,b)
        root(parts[0])
    return np.asarray([root(r['components'][0]) for r in rows])


def interval(values,lo,hi):
    x=np.asarray(values,float);x=x[np.isfinite(x)]
    return None if not len(x) else np.quantile(x,[lo,hi],method='linear').tolist()


def guard_result(values,components,detection=False,minimum_components=20,context=None):
    v=np.asarray(values,float)
    bad=int((~np.isfinite(v)).sum());total=len(v)
    result={'independent_components':int(components),'bootstrap_draws_readable':len(v),
            'bootstrap_draws_total':total,'unreadable_draw_count':bad,
            'unreadable_fraction':float(bad/total) if total else None,
            'support_minimum_components':minimum_components,'status':'INCONCLUSIVE',
            'coverage':'Approximate marginal one-sided bootstrap; engineering support minimum is not a validity proof.'}
    if bad:
        raise UnexpectedGuardDraws(dict(result,bootstrap_draws_readable=total-bad,
                                        reason='UNEXPECTED_NONFINITE_GUARD_BOOTSTRAP',context=context))
    if components<minimum_components:
        return dict(result,reason='SPARSE_COMPONENTS',bounds=None)
    if len(v)<2:
        return dict(result,reason='UNREADABLE_BOOTSTRAP',bounds=None)
    if np.ptp(v)==0:
        return dict(result,reason='ZERO_BOOTSTRAP_VARIANCE',bounds=None)
    lo,hi=interval(v,.05,.95)
    if detection:
        status='PASS' if lo>=-.02 else ('FAIL' if hi<-.02 else 'INCONCLUSIVE')
        rule='lower marginal95% bound >= -0.02'
    else:
        status='PASS' if hi<=.02 else ('FAIL' if lo>.02 else 'INCONCLUSIVE')
        rule='upper marginal95% bound <= +0.02'
    return dict(result,status=status,reason='MARGINAL_BOUND',bounds=[lo,hi],rule=rule)


def optimization_result(seed_effects,unstratified_effect,draws,unreadable_fraction):
    e=np.asarray(seed_effects,float);b=np.asarray(draws,float);b=b[np.isfinite(b)]
    result={'per_seed_effect':e.tolist(),'seed_mean':float(e.mean()),
            'unstratified_seed_mean_gain':float(unstratified_effect),
            'positive_seeds':int((e>0).sum()),'unreadable_fraction':float(unreadable_fraction),
            'ci_97_5':interval(b,.0125,.9875),'status':'INCONCLUSIVE'}
    if unreadable_fraction>.05:return dict(result,reason='TOO_MANY_UNREADABLE_D_DRAWS')
    if not np.isfinite(e).all() or len(b)<2 or np.ptp(b)==0:return dict(result,reason='UNSUPPORTED_OR_DEGENERATE')
    positive=(e.mean()>=.03 and result['ci_97_5'][0]>0 and (e>0).sum()>=4 and unstratified_effect>0)
    return dict(result,status='PRESENT' if positive else 'NOT_ESTABLISHED',reason='FIXED_OPTIMIZATION_RULE')


def analyze(primary,calibration,cells,primary_scores,calibration_scores,cell_scores,floors,draws=10000):
    """Scores shapes(3arms,5seeds,nrows), floors(nprimary,15). No selection of nets."""
    P=np.asarray(primary_scores,float);C=np.asarray(calibration_scores,float);F=np.asarray(floors,float)
    assert P.shape==(3,5,len(primary)) and C.shape==(3,5,len(calibration))
    assert F.shape==(len(primary),15)
    assert len(cell_scores)==len(cells),'guard score/cell count mismatch'
    assert np.isfinite(P).all() and np.isfinite(C).all() and np.isfinite(F).all()
    y=np.array([int(r['label']) for r in primary]);q=np.array([r['D_stratum'] for r in primary])
    pc=[r['component'] for r in primary];ps=[r['source'] for r in primary]
    cc=[r['component'] for r in calibration];cs=[r['source'] for r in calibration]
    assert not(set(pc)&set(cc))
    component_rng=np.random.default_rng(2026111401)
    seed_rng=np.random.default_rng(2026111403);cal_rng=np.random.default_rng(2026111404)
    # Generate all primary draws first: guard enumeration never changes this stream.
    primary_sampler=ComponentSampler(pc,ps);calibration_sampler=ComponentSampler(cc,cs)
    pi=[primary_sampler.draw(component_rng) for _ in range(draws)]
    si=seed_rng.integers(0,5,size=(draws,5))
    ci=[calibration_sampler.draw(cal_rng) for _ in range(draws)]
    point=np.array([[within_d(P[a,s],y,q) for s in range(5)] for a in range(3)])
    plain=np.array([[auc(P[a,s],y) for s in range(5)] for a in range(3)])
    floor_point=np.array([within_d(F[:,j],y,q) for j in range(15)])
    boot=np.full((draws,3),np.nan);floor_boot=np.full(draws,np.nan)
    thresholds=np.empty((draws,3,5));point_thresholds=np.array([[threshold(C[a,s]) for s in range(5)] for a in range(3)])
    detection=np.empty(draws)
    for b in range(draws):
        ii=pi[b];seeds=si[b]
        thresholds[b]=[[threshold(C[a,s,ci[b]]) for s in range(5)] for a in range(3)]
        for a in range(3):boot[b,a]=np.mean([within_d(P[a,s,ii],y[ii],q[ii]) for s in seeds])
        floor_boot[b]=max_floor_statistic(F[ii],y[ii],q[ii])
        pos=ii[y[ii]==1]
        detection[b]=np.mean([np.mean(P[2,s,pos]>thresholds[b,2,s])-np.mean(P[1,s,pos]>thresholds[b,1,s]) for s in seeds])
    valid=np.isfinite(boot).all(1)&np.isfinite(floor_boot);unreadable=1-float(valid.mean())
    contrasts={}
    for name,a,b in [('ranking_minus_paired_BCE',2,1),('paired_BCE_minus_BCE',1,0)]:
        contrasts[name]=optimization_result(point[a]-point[b],float((plain[a]-plain[b]).mean()),boot[:,a]-boot[:,b],unreadable)
    floor_gain=boot[:,2]-floor_boot
    floor_report={'per_floor_AUC':floor_point.tolist(),'maximum_floor_point':float(np.max(floor_point)),
          'ranking_seed_mean_minus_max_floor':float(point[2].mean()-floor_point.max()),
          'ci_97_5':interval(floor_gain,.0125,.9875),
          'rule':'Recompute maximum of ALL15 floor statistics in EVERY shared draw.',
          'status':'INCONCLUSIVE'}
    if unreadable<=.05 and np.isfinite(floor_gain).sum()>1 and np.ptp(floor_gain[np.isfinite(floor_gain)])>0:
        floor_report['status']='ABOVE_FLOOR' if floor_report['ci_97_5'][0]>0 else 'NOT_ESTABLISHED'
    guards=[]
    point_detection=np.mean([(P[2,s,y==1]>point_thresholds[2,s]).mean()-(P[1,s,y==1]>point_thresholds[1,s]).mean() for s in range(5)])
    detection_report=guard_result(detection,len(set(np.asarray(pc)[y==1])),detection=True,context='S4_detection')
    detection_report.update(name='S4_detection',point_difference=float(point_detection))
    for cell,S in zip(cells,cell_scores):
        S=np.asarray(S,float);assert S.shape==(3,5,len(cell['rows'])) and np.isfinite(S).all()
        gc=merged_components(cell['rows']);ng=len(set(gc))
        assert not(set(c for r in cell['rows'] for c in r['components'])&set(cc))
        pd=float(np.mean([(S[2,s]>point_thresholds[2,s]).mean()-(S[1,s]>point_thresholds[1,s]).mean() for s in range(5)]))
        bvals=[]
        if ng>=20:
            guard_sampler=ComponentSampler(gc,[cell['source']]*len(gc))
            for b in range(draws):
                ii=guard_sampler.draw(component_rng)
                bvals.append(np.mean([(S[2,s,ii]>thresholds[b,2,s]).mean()-(S[1,s,ii]>thresholds[b,1,s]).mean() for s in si[b]]))
        result=guard_result(bvals,ng,context={'cell_index':cell['cell_index'],'set':cell['set']})
        result.update(cell_index=cell['cell_index'],set=cell['set'],source=cell['source'],metadata=cell['metadata'],
                      n_rows=len(cell['rows']),raw_declared_components=cell['n_components'],point_difference=pd)
        guards.append(result)
    assert len(guards)==len(cells)
    all_pass=all(g['status']=='PASS' for g in [detection_report,*guards])
    return {'scope':'MAD22-informed separate cycle; no historical191/scaled benchmark metrics or NEXT winner',
      'inference_limit':'Approximate component/seed bootstrap. IUT supports a conjunctive claim only to the extent each marginal test is valid. No finite-sample or simultaneous-cellwise coverage guarantee.',
      'networks':{'arms':list(ARMS),'seeds':list(SEEDS),'per_network_within_D_AUC':point.tolist(),'per_network_unstratified_AUC':plain.tolist()},
      'optimization':contrasts,'floor':floor_report,'detection_guard':detection_report,'genuine_guards':guards,
      'guard_IUT':{'all_pass':all_pass,'required_guards':len(guards)+1,'status_counts':{k:sum(g['status']==k for g in [detection_report,*guards]) for k in ('PASS','FAIL','INCONCLUSIVE')}},
      'calibration':{'n_original':len(calibration),'order_original':math.ceil(.95*(len(calibration)+1)),
           'point_thresholds':point_thresholds.tolist(),'achieved_calibration_flag_rates':[[float(np.mean(C[a,s]>point_thresholds[a,s])) for s in range(5)] for a in range(3)],
           'rule':'Strict >; bootstrap recomputes threshold for each network and resampled calibration population.'},
      'bootstrap':{'draws':draws,'unreadable_primary_fraction':unreadable,'fixed_D_strata':True,'component_rng':2026111401,'seed_rng':2026111403,'calibration_rng':2026111404},
      'operational_qualification':('NOT_QUALIFIED' if any(g['status']=='FAIL' for g in [detection_report,*guards]) else
         'INCONCLUSIVE' if any(g['status']=='INCONCLUSIVE' for g in [detection_report,*guards]) else
         'REQUIRES_SEPARATE_REVIEW' if all_pass and contrasts['ranking_minus_paired_BCE']['status']=='PRESENT' and floor_report['status']=='ABOVE_FLOOR' else 'NOT_ESTABLISHED')}
