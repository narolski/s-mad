"""Independent phase1 control contract; no image/model/reference flags."""
import re
OUTPUT='/lustre/pd03/hpc-narolski-1790461090/smad-next/RZ1/sbmr512_runtime_metadata_phase1_v1/result'
BASE=OUTPUT.rsplit('/',1)[0]
def req(ok,msg):
 if not ok:raise ValueError(msg)
def validate(c):
 req(c['decision']=='GO_SBMR512_RUNTIME_METADATA_PHASE1_DISPATCH_V1R1' and c['root_authorized'] is True and c['reviewer'] and c['author']!=c['reviewer'],'release')
 req(c['scientific_read']=='HOLD' and c['automatic_retry'] is False,'scope')
 req(c['driver_dir']==BASE+'/dispatch_s408' and c['worker_dir']==BASE+'/source','fixed namespace')
 req(c['output']==OUTPUT and c['input_identity_receipt_sha256']=='7847e2007570f75012f36fccd9257f73231c9a28cafbfb38ba86c2286d76e61b','adopted current identity')
 req(set(c['admissions'])=={'current_identity_adoption','OTHER_phase1_source_review','runtime_import_scope','native_elf_scope','site_profile'},'phase1 roles')
 for a in c['admissions'].values():req(a['path'].startswith('/') and re.fullmatch('[0-9a-f]{64}',a['sha256']) and a['status']=='ROOT_ADOPTED','admission')
 for k in ('node_bootstrap','python','runtime_grant','source_manifest_path'):
  req(c[k].startswith('/') and re.fullmatch('[0-9a-f]{64}',c['content_pins'][c[k]]),'exact tool/grant pin')
 req(c['python']=='/home/narolski/dmenv/bin/python','original venv entry path')
 req(c['source_manifest_path']==BASE+'/source/SOURCE_SHA256SUMS','manifest path')
 return True
