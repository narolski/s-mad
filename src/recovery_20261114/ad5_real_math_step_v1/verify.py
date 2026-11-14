"""New once-only technical release gate; no scheduler, model or dataset access."""
import hashlib
import json
import pathlib

ROOT=pathlib.Path('/lustre/pd03/hpc-narolski-1790461090/smad-next/AD5')
SOURCE=ROOT/'ad5_real_math_step_v1'
JOURNAL=ROOT/'dispatch/ad5_real_math_step_v1_20261114'
KEEP=ROOT/'logs/keep/ad5_real_math_step_v1_20261114'
DECISION='GO_ONE_NEW_AD5_REAL_MATH_STEP_V1'
CODE_SHA='94964c3689aa866ad7700f4b86496590c1b353e8e8be59173158e7b46c35d6ee'
WHEELS_SHA='3bd18def4da9cbec2766896fa160c34c0364de464ca3abd02d675c72620cf13c'
DATA_SHA='3189e52af12e2853b06c86993b1b8b5cfef891fda749395778492e3445924900'


def sha(path):
    h=hashlib.sha256()
    with pathlib.Path(path).open('rb') as f:
        for block in iter(lambda:f.read(8<<20),b''):h.update(block)
    return h.hexdigest()


def release():
    r=json.loads((JOURNAL/'ROOT_RELEASE.json').read_text())
    assert r['decision']==DECISION and r['root_authorized'] is True and r['author']!=r['reviewer']
    assert r['automatic_retry'] is False and r['scientific_read']=='HOLD' and r['production_recovery'] is False
    assert (r['arm'],r['seed'],r['global_batch'],r['effective_updates'])==('B',401,256,1)
    assert r['old_failed_job']=='6321768_401' and r['old_synthetic_job']=='6323083' and r['old_job_action']=='NONE'
    assert r['input_pins']=={'code':CODE_SHA,'wheels':WHEELS_SHA,'crops':DATA_SHA}
    assert r['source_manifest_sha256']==sha(SOURCE/'SHA256SUMS')
    for line in (SOURCE/'SHA256SUMS').read_text().splitlines():
        h,name=line.split('  ',1);p=SOURCE/name
        assert p.resolve().is_relative_to(SOURCE.resolve()) and sha(p)==h
    for key in ('prereg','source_review','launcher_review','owned_source_commit_check','site_preflight'):
        name=r[key+'_file'];assert pathlib.Path(name).name==name
        assert sha(JOURNAL/name)==r[key+'_sha256']
    assert r['owned_source_clean_committed'] is True and r['durable_free_gib']>=50
    return r
