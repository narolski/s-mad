"""Pinned metadata and post-claim minimal score allowlist. Never loads weights."""
import csv
import hashlib
import io
import json
import pathlib
import tarfile
import zipfile

import numpy as np

from .admit import COUNTS,ARMS,SEEDS,require,sha


def pinned_path(binding,suffix):
    paths=[p for p in binding['pins'] if p.endswith(suffix)]
    require(len(paths)==1,'ambiguous pinned input '+suffix)
    require(sha(paths[0])==binding['pins'][paths[0]],'metadata pin changed')
    return pathlib.Path(paths[0])


def validate_component_exclusion(primary,calibration,cells):
    cc={r['component'] for r in calibration}
    require(not(cc&{r['component'] for r in primary}),'calibration-primary component overlap')
    for cell in cells:
        require(not(cc&{p for r in cell['rows'] for p in r['components']}),'calibration-guard component overlap')


def metadata(binding):
    primary=json.loads(pinned_path(binding,'/prepared/primary_with_D_components.json').read_text())
    calibration=json.loads(pinned_path(binding,'/prepared/calibration_proposal.json').read_text())
    cells=json.loads(pinned_path(binding,'/prepared/genuine_guard_cells_proposal.json').read_text())
    audit=json.loads(pinned_path(binding,'/inputs/METADATA_AUDIT.json').read_text())
    require(len(primary)==200 and len(calibration)==132 and len(cells)==119,'population count drift')
    require(len({r['id'] for r in primary})==200 and len({r['host'] for r in primary})==100,'primary duplicates')
    require(all(r['role']=='dev' and r['rung'] in ('S3','S4') and int(r['label'])==(r['rung']=='S4') for r in primary),'wrong primary row/label')
    edges=np.asarray(binding['optimization']['fixed_D_edges'])
    require(all(int(np.searchsorted(edges,r['log_D'],side='left'))==r['D_stratum'] for r in primary),'D assignment drift')
    require(all(sum(r['D_stratum']==k and int(r['label'])==y for r in primary)>0 for k in range(5) for y in (0,1)),'unreadable original D population')
    parent={}
    def root(x):
        parent.setdefault(x,x)
        if parent[x]!=x:parent[x]=root(parent[x])
        return parent[x]
    ladder=pinned_path(binding,'/inputs/ladder_split.csv')
    for r in csv.DictReader(ladder.open()):
        a,b=root(r['pid']),root(r['partner_B'])
        if a!=b:parent[max(a,b)]=min(a,b)
    require(all(r['component']==root(r['host'])==root(r['partner_B']) for r in primary),'full primary person/geometry graph changed')
    require(len(set(r['component'] for r in primary))==40,'primary full-component graph changed')
    require(len({r['id'] for r in calibration})==132 and len({r['host'] for r in calibration})==132,'calibration person/row duplicated')
    require(all(r['rung']=='R_cam' and int(r['label'])==0 for r in calibration),'wrong calibration row')
    require(all(r['component']==root(r['host']) for r in calibration),'calibration full component mismatch')
    cc={r['component'] for r in calibration}
    require(not(cc&{r['component'] for r in primary}),'calibration-primary component overlap')
    require([c['cell_index'] for c in cells]==list(range(119)),'guard ordering changed')
    validate_component_exclusion(primary,calibration,cells)
    for c in cells:
        require(c['set'] in COUNTS and c['n_rows']==len(c['rows'])>0,'empty/malformed guard')
        require(len({r['id'] for r in c['rows']})==len(c['rows']),'guard row duplicated')
        require(not(cc&{p for r in c['rows'] for p in r['components']}),'calibration-guard component overlap')
    manifests={};specs=audit['manifests']
    for k,count in COUNTS.items():
        spec=specs[k]
        require(sha(spec['path'])==spec['sha256'] and spec['rows']==count,'manifest pin '+k)
        rows=list(csv.DictReader(open(spec['path'])));require(len(rows)==count,'manifest row count')
        require(len({r['id'] for r in rows})==count,'duplicate underlying ID')
        manifests[k]={'ids':[r['id'] for r in rows],'sha256':spec['sha256'],'rows':{r['id']:r for r in rows}}
    for r in primary:require(manifests['dev']['rows'][r['id']]['label']==r['label'],'primary label mismatch')
    for r in calibration:require(int(manifests['tt1']['rows'][r['id']]['label'])==0,'calibration label mismatch')
    for c in cells:
        for r in c['rows']:
            raw=manifests[c['set']]['rows'][r['id']]
            require(int(raw['label'])==0 and not(c['set']=='dev' and raw['role']=='test'),'historical/attack guard row')
    allow={k:set() for k in COUNTS}
    allow['dev'].update(r['id'] for r in primary);allow['tt1'].update(r['id'] for r in calibration)
    for c in cells:allow[c['set']].update(r['id'] for r in c['rows'])
    return {'primary':primary,'calibration':calibration,'cells':cells,'manifests':manifests,'allow':allow,
            'floor_path':pinned_path(binding,'/primary_floors_v1/primary_floors.csv')}


def floors(meta):
    p=meta['floor_path'];reader=csv.DictReader(p.open());names=reader.fieldnames
    expected=[f'{family}__{learner}' for family in ('all_cue','luma','render','storage','geometry') for learner in ('single','logreg','gbt')]
    require(names==['id','label','component','D_stratum',*expected],'floor columns changed')
    rows=list(reader);require(len(rows)==200,'floor row count')
    for r,p in zip(rows,meta['primary']):
        require((r['id'],int(r['label']),r['component'],int(r['D_stratum']))==(p['id'],int(p['label']),p['component'],p['D_stratum']),'floor population/order changed')
    X=np.asarray([[float(r[n]) for n in expected] for r in rows])
    require(np.isfinite(X).all(),'nonfinite floor')
    return X,expected


def read_npz_member(tar,name,digest,manifest):
    members=[m for m in tar.getmembers() if m.name==name]
    require(len(members)==1 and members[0].isfile() and members[0].size<=32<<20,'invalid score member')
    raw=tar.extractfile(members[0]).read()
    require(hashlib.sha256(raw).hexdigest()==digest,'score member digest mismatch')
    with zipfile.ZipFile(io.BytesIO(raw)) as z:
        require(sum(e.file_size for e in z.infolist())<=64<<20,'oversized NPZ')
    with np.load(io.BytesIO(raw),allow_pickle=False) as z:
        require({'id','logit','manifest_sha256'}<=set(z.files),'missing score fields')
        ids=z['id'];values=z['logit']
        require(ids.ndim==values.ndim==1 and ids.dtype.kind in 'US' and values.dtype==np.float32,'wrong score dtype/shape')
        require(ids.tolist()==manifest['ids'],'full underlying ID order changed')
        require(str(z['manifest_sha256'].item())==manifest['sha256'],'embedded manifest hash changed')
        require(np.isfinite(values).all(),'nonfinite candidate array')
        return ids.copy(),values.copy()


def load_allowlist(entry,meta,claim_path):
    """Called only after the one permanent claim. Never returns historical rows."""
    require(pathlib.Path(claim_path).is_file(),'no permanent read claim')
    require(sha(entry['archive_path'])==entry['archive_sha256'],'archive changed after admission')
    task=entry['task'];r=entry['envelope'];selected={}
    with tarfile.open(entry['archive_path'],'r:*') as t:
        for name,spec in meta['manifests'].items():
            member=task+'/battery/logits_'+name+'.npz'
            ids,z=read_npz_member(t,member,r['score_member_sha256'][member],spec)
            if name=='dev':
                own=task+'/scores_eval.npz'
                ownids,ownz=read_npz_member(t,own,r['score_member_sha256'][own],spec)
                require(np.array_equal(ownids,ids) and np.array_equal(ownz,z),'stored own-fit/battery mismatch')
            selected[name]={str(i):float(v) for i,v in zip(ids,z) if str(i) in meta['allow'][name]}
            require(set(selected[name])==meta['allow'][name],'allowlisted IDs missing')
    return selected


def arrays(entries,meta,claim_path):
    P=np.empty((3,5,len(meta['primary'])));C=np.empty((3,5,len(meta['calibration'])))
    G=[np.empty((3,5,len(c['rows']))) for c in meta['cells']]
    for e in entries:
        selected=load_allowlist(e,meta,claim_path);a=ARMS.index(e['arm']);s=SEEDS.index(e['seed'])
        P[a,s]=[selected['dev'][r['id']] for r in meta['primary']]
        C[a,s]=[selected['tt1'][r['id']] for r in meta['calibration']]
        for j,c in enumerate(meta['cells']):G[j][a,s]=[selected[c['set']][r['id']] for r in c['rows']]
    return P,C,G
