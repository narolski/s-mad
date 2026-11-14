"""Post-auxiliary-claim serialization exception; only538/468 numerical IDs returned."""
import hashlib
import io
import json
import pathlib
import tarfile
import zipfile
import numpy as np
import bridge
import metadata as M
import policy as P


def require_claim():
    path=pathlib.Path(P.ONCE)/'CLAIM.json';M.need(path.is_file(),'permanent auxiliary claim missing')
    c=M.obj(path)
    M.need(c['experiment_id']==P.EXPERIMENT and c['scope']==P.READ_SCOPE and c['policy_adoption_sha256']==P.POLICY_SHA,'wrong claim scope/policy')
    M.need(c['new_primary_read'] is False and c['full_container_validation_after_auxiliary_claim_only'] is True,'serialization exception missing')


def read_selected(archive,archive_sha,member,digest,manifest,allowed):
    require_claim()
    M.need(bridge.sha(archive)==archive_sha,'archive changed after auxiliary admission')
    with tarfile.open(archive,'r:*') as t:
        matches=[m for m in t.getmembers() if m.name==member]
        M.need(len(matches)==1 and matches[0].isfile() and 0<matches[0].size<=32<<20,'invalid score member')
        raw=t.extractfile(matches[0]).read();M.need(hashlib.sha256(raw).hexdigest()==digest,'score member changed')
    with zipfile.ZipFile(io.BytesIO(raw)) as z:
        info=z.infolist();M.need(len({x.filename for x in info})==len(info) and sum(x.file_size for x in info)<=64<<20,'duplicate/oversized NPZ')
    with np.load(io.BytesIO(raw),allow_pickle=False) as z:
        M.need({'id','logit','manifest_sha256'}<=set(z.files),'NPZ fields missing')
        ids=z['id'];values=z['logit']
        M.need(ids.ndim==values.ndim==1 and ids.dtype.kind in 'US' and values.dtype==np.float32,'wrong NPZ dtype/shape')
        M.need(len(ids)==len(values)==len(manifest['ids']),'full container length mismatch')
        M.need(ids.tolist()==manifest['ids'] and len(set(ids.tolist()))==len(ids),'full ordered ID alignment mismatch')
        M.need(str(z['manifest_sha256'].item())==manifest['sha256'],'embedded manifest mismatch')
        M.need(np.isfinite(values).all(),'nonfinite container; no values logged')
        # Full-container validation is authorized only here; no statistics/export
        # on nonallowlisted values. Candidate calibration rows never returned.
        selected={str(i):float(v) for i,v in zip(ids,values) if str(i) in allowed}
        M.need(set(selected)==set(allowed),'missing allowed ID')
    return selected


def arrays(binding,meta,technical):
    require_claim();cal=[r['id'] for r in meta['calibration']];ev=[r['id'] for r in meta['evaluation']]
    baseline=read_selected(P.BASELINE,P.BASELINE_SHA,P.MEMBER,technical['score_member_sha256'],meta['manifest'],set(cal+ev))
    C=np.array([baseline[i] for i in cal],np.float64);B=np.array([baseline[i] for i in ev],np.float64)
    Z=np.empty((3,5,len(ev)))
    for entry in binding['candidates']:
        selected=read_selected(entry['archive_path'],entry['archive_sha256'],entry['exact_aux_score_member'],entry['score_member_sha256'],meta['manifest'],set(ev))
        Z[P.ARMS.index(entry['arm']),P.SEEDS.index(entry['seed'])]=[selected[i] for i in ev]
    return C,B,Z


def own_companion(binding):
    require_claim();spec=binding['primary_files']['result'];M.need(bridge.sha(spec['path'])==spec['sha256'],'primary result changed')
    original=json.loads(pathlib.Path(spec['path']).read_text())
    # Copy exact existing summaries only. No original threshold/statistic/design
    # function, model code or RNG is imported/called anywhere in this adapter.
    return {'calibration':original['calibration'],'genuine_FA_rates':original['genuine_false_alarms']['per_network_rates'],
       'positive_family_sensitivity':original['positive_evaluation']['per_network_sensitivity'],
       'original_primary_contrasts_and_intervals':original['genuine_false_alarms']['contrasts'],
       'original_utility_guards':original['positive_evaluation']['utility_guards'],
       'original_utility_status':original['positive_evaluation']['overall_utility_status'],
       'original_primary_result_sha256':spec['sha256']}
