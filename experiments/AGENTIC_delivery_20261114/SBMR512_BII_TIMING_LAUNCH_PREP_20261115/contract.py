"""Pure contract validation. No file, runtime, model, payload or GPU access."""
import re
SOURCE='6dc4375db303042904ca0725c631515ffaf00d7afc4266bf8334d067c0b698c7'
OUTPUT='/lustre/pd03/hpc-narolski-1790461090/smad-next/RZ1/SbMR512_bii_timing_wcss_v1/timing_s408'
ROLES=('worker_source','original_model_source','python_runtime','python_package_sources','native_libraries','bootstrap_tools','input_images64','base_weights','trainable_overlay','trainable_schema','model_metadata','original_eval_reference','runtime_defaults','positional_rebuild','durable_output_mount','worker_policy','exposure_permission')
def require(ok,msg):
 if not ok: raise ValueError(msg)
def pin(v):
 return isinstance(v,str) and re.fullmatch('[0-9a-f]{64}',v) is not None
def validate(c):
 require(c['decision']=='GO_SBMR512_BII_TIMING_EXTENSION_V1','release')
 require(c['root_authorized'] is True and c['author']!=c['reviewer'] and bool(c['reviewer']),'independent review')
 require(c['mode']=='timing' and c['seed']==408,'scope')
 require(c['worker_source_manifest_sha256']==SOURCE,'frozen source')
 require(c['scientific_read']=='HOLD' and c['automatic_retry'] is False,'policy')
 require(c['output']==OUTPUT,'fixed output')
 require(c['profile']==dict(partition='lem-gpu-interactive',gpus=1,cpus=8,memory='32G',local_scratch='8G',walltime='00:15:00'),'profile')
 require(c['reference_scope']==dict(population='ab1x_eval',container_decode=True,selected_indices=c['reference_scope']['selected_indices'],tt1_open=False),'reference scope')
 require(c['reference_scope']['selected_indices']==[40, 41, 42, 43, 44, 45, 46, 47, 48, 49, 50, 51, 52] and len(c['reference_scope']['selected_indices'])==13 and len(set(c['reference_scope']['selected_indices']))==13 and all(type(i)==int and 0<=i<64 for i in c['reference_scope']['selected_indices']),'13 targets')
 require(c['runtime_defaults']['historical_identity']=='UNKNOWN','historical identity')
 require(c['runtime_defaults']['prospective_runtime_reviewed'] is True,'runtime evidence')
 require(set(c['admissions'])==set(ROLES),'admission roles')
 for role,a in c['admissions'].items():
  require(a['status']=='ROOT_ADOPTED' and pin(a['sha256']) and a['path'].startswith('/'),'missing admission '+role)
 require(c['content_pins'] and all(p.startswith('/') and pin(h) for p,h in c['content_pins'].items()),'actual pins')
 for k in ('worker_release','worker_admission','worker_dir','python','driver_dir','durable_parent','isolated_home'):
  require(isinstance(c[k],str) and c[k].startswith('/'),'absolute '+k)
 require(c['durable_parent']==OUTPUT.rsplit('/',1)[0],'durable backing')
 require(all(c[k] in c['content_pins'] for k in ('python','worker_release','worker_admission')),'interpreter/release/admission pins')
 require(c['runtime_env'].keys() <= {'LD_LIBRARY_PATH','OMP_NUM_THREADS','MKL_NUM_THREADS'},'environment allowlist')
 require(all(isinstance(v,str) and '\x00' not in v for v in c['runtime_env'].values()),'environment values')
 return True
