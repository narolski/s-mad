"""AD5 technical-only wrapper around existing bounded metadata collector.
Never execute without the exact independently reviewed packet and root release.
"""
import argparse, hashlib, json, os, pathlib, sys
sys.path.insert(0,str(pathlib.Path(__file__).resolve().parent))
import ad5_technical_core as C
import native_metadata_predicates_v2 as P

def h(b):return hashlib.sha256(b).hexdigest()
def capture(path, cap=4000000):
    path=pathlib.Path(path)
    if not path.is_absolute() or path.resolve()!=path or path.is_symlink(): raise ValueError('CONTROL_PATH')
    with path.open('rb') as f:b=f.read(cap+1)
    if len(b)>cap:raise ValueError('CONTROL_CAP')
    return b

def execute(packet, release, review, output):
    C.require(release['decision']=='GO_AD5_TECHNICAL_METADATA_ONLY','GRANT')
    C.require(release['packet_sha256']==h(packet),'PACKET')
    C.require(release['review_sha256']==h(review),'REVIEW')
    C.require(release['output']==str(output) and output.is_absolute() and output.resolve()==output,'OUTPUT')
    C.require(release['cpu_only'] is True and os.environ.get('CUDA_VISIBLE_DEVICES','')=='','CPU')
    C.require(release['review_decision']=='GO_AD5_TECHNICAL_METADATA_ONLY','REVIEW_DECISION')
    C.require(release['review_decision'] in review.decode().splitlines(),'OTHER_REVIEW')
    for name in ('technical_entry.py','ad5_technical_core.py','native_metadata_predicates_v2.py'):
        C.require(release['source_sha256'][name]==h((pathlib.Path(__file__).parent/name).read_bytes()),'SOURCE')
    scope=json.loads(packet)
    C.require(scope['schema']=='ad5-technical-only-v1','SCHEMA')
    C.require(len(scope['archives'])<=17,'COUNT')
    C.require(not output.exists(),'EXISTS')
    for r in scope['archives'].values():
        C.require(set(r['members']) <= {'job.json','40_backbone.pth','40_header.pth','epoch_100.tar','mixfacenet_SMDD.pth'},'MEMBER_SCOPE')
        C.require(all(v['kind'] in ('json','header') for v in r['members'].values()),'PARSER_SCOPE')
        C.require(r['members']['job.json']['kind']=='json','JOB')
        C.require(all(v['kind']=='header' for k,v in r['members'].items() if k!='job.json'),'HEADER_ONLY')
    # Core scans headers, hashes archive, reads only job.json; checkpoints header-only.
    result={k:C.collect_archive(v) for k,v in scope['archives'].items()}
    output.mkdir()
    (output/'TECHNICAL_METADATA.json').write_text(json.dumps({'schema':'ad5-technical-only-result-v1','scientific_admission':False,'archives':result},indent=2)+'\n')
    (output/'COMPLETE').write_text('TECHNICAL_ONLY_NOT_ADMISSION\n')

def main():
    a=argparse.ArgumentParser();a.add_argument('--packet',required=True);a.add_argument('--release',required=True);a.add_argument('--release-sha256',required=True);a.add_argument('--output',required=True);x=a.parse_args()
    raw=capture(x.release);C.require(h(raw)==x.release_sha256,'EXTERNAL_GRANT_PIN');r=json.loads(raw)
    execute(capture(x.packet),r,capture(r['review']),pathlib.Path(x.output))
if __name__=='__main__':main()
