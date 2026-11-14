"""HN post-claim primary200-only loader. No camera, historical or checkpoint return."""
import pathlib
import tarfile
import numpy as np
import shared
import policy as P
import admission as A


def load_entry(e,meta,claim_path):
    A.need(pathlib.Path(claim_path).is_file(),'permanent claim missing')
    A.need(shared.sha(e['archive_path'])==e['archive_sha256'],'archive changed after admission')
    S=shared.load();task=e['task'];r=e['envelope'];spec=meta['manifests']['dev']
    with tarfile.open(e['archive_path'],'r:*') as t:
        own=task+'/scores_eval.npz';dev=task+'/battery/logits_dev.npz'
        ids,z=S.data.read_npz_member(t,dev,r['score_member_sha256'][dev],spec)
        oi,oz=S.data.read_npz_member(t,own,r['score_member_sha256'][own],spec)
        A.need(np.array_equal(ids,oi) and np.array_equal(z,oz),'own-fit/battery mismatch')
        allowed={r['id'] for r in meta['primary']}
        selected={str(i):float(x) for i,x in zip(ids,z) if str(i) in allowed}
        A.need(set(selected)==allowed,'primary ID missing')
    return selected


def arrays(entries,meta,claim_path):
    A.need(len(entries)==10,'all10fits required')
    z=np.empty((2,5,len(meta['primary'])))
    for e in entries:
        chosen=load_entry(e,meta,claim_path)
        z[P.ARMS.index(e['arm']),P.SEEDS.index(e['seed'])]=[chosen[r['id']] for r in meta['primary']]
    return z
