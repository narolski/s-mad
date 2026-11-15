"""One exact approved list/model through existing AD5 scorer. No default inputs.
Source-only --emit-command validates control plane, prints command, no image/model read.
Actual execution requires separate signed scope, OTHER pre-review, admitted checkpoint.
"""
import argparse,csv,hashlib,json,os,pathlib,subprocess,sys
sys.path.insert(0,str(pathlib.Path(__file__).resolve().parent))
from technical_entry import capture,h

def require(ok,why):
    if not ok:raise ValueError(why)
def command(s):
    require(s['phase'] in ('corrected_MAD22_and_approved_dev','FRLL_final_separate'),'PHASE')
    require(s['admission']=='OTHER_TECHNICAL_PASS_CHECKPOINT_AND_INPUTS','ADMISSION')
    require(s['mode'] in ('rel','own'),'MODE')
    require(s['resource']['gpus']==1 and 1<=s['resource']['seconds']<=7200,'BOUND')
    require(1<=s['resource']['workers']<=6 and s['resource']['batch_size']==32,'BATCH')
    a=[s['python'],'-I',s['wrapper']]
    if s['mode']=='rel':a += [s['runtime_root'],s['site'],'--as',s['release_spec']]
    a += ['--name',s['name'],'--weights',s['weights'],'--','--mode',s['mode'],'--manifest',s['manifest'],'--out-dir',s['output'],'--tag',s['tag'],'--workers',str(s['resource']['workers']),'--bs','32']
    return a

def main():
    p=argparse.ArgumentParser();p.add_argument('--scope',required=True);p.add_argument('--scope-sha256',required=True);p.add_argument('--execute',action='store_true');a=p.parse_args()
    raw=capture(a.scope);require(h(raw)==a.scope_sha256,'EXTERNAL_SCOPE_PIN');s=json.loads(raw)
    require(s['decision']=='GO_AD5_SINGLE_MODEL_SCOPED_INFERENCE','GRANT')
    review=capture(s['review']);require(h(review)==s['review_sha256'],'REVIEW_PIN')
    require('GO_AD5_SINGLE_MODEL_SCOPED_INFERENCE' in review.decode().splitlines(),'OTHER')
    argv=command(s)
    if not a.execute:print(json.dumps(argv));return
    require(s['launcher_sha256']==h(pathlib.Path(__file__).read_bytes()),'SOURCE_PIN')
    for path,sha in s['source_pins'].items():require(h(capture(path,200000000))==sha,'RUNTIME_SOURCE_PIN')
    manifest=capture(s['manifest']);require(h(manifest)==s['manifest_sha256'],'MANIFEST_PIN')
    rows=list(csv.DictReader(manifest.decode().splitlines()));require(rows and len(rows)==s['rows'],'ROWS')
    require(list(rows[0])==['id','path'] and len(set(r['id'] for r in rows))==len(rows),'IDS')
    require(rows==s['approved_rows'],'EXACT_INPUT_LIST')
    # Per-image hashes are deliberately not read here: root's admitted manifest and
    # exact row scope are the inputs; scorer consumes only this manifest.
    out=pathlib.Path(s['output']);require(out.is_absolute() and out.resolve()==out and not out.exists(),'CREATE_ONLY')
    out.mkdir()
    (out/'CLAIM.json').write_text(json.dumps({'scope_sha256':h(raw),'argv':argv})+'\n')
    with open(out/'scorer.log','xb') as log:
        r=subprocess.run(argv,stdout=log,stderr=subprocess.STDOUT,timeout=s['resource']['seconds'],env={**os.environ,'CUDA_VISIBLE_DEVICES':s['cuda_visible_device'],'HF_HUB_OFFLINE':'1','TRANSFORMERS_OFFLINE':'1'})
    (out/'PROCESS_STATUS.json').write_text(json.dumps({'returncode':r.returncode,'score_payload_opened':False})+'\n')
    require(r.returncode==0,'SCORER_FAILED_KEEP_CLAIM')
if __name__=='__main__':main()
