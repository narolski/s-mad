"""Generated-only source/geometry receipt; never opens real photos or model artifacts."""
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import subprocess
import sys
import numpy as np

base=Path(__file__).parent
spec=importlib.util.spec_from_file_location('construction',base/'construction.py')
m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
source='/mnt/t7/smad_next/PN1/fs_tree/pn1/code/morphmamba/data/selfblend.py'
run=subprocess.run([sys.executable,'-I',str(base/'test_generated.py')],capture_output=True,text=True)
if run.returncode:raise RuntimeError(run.stdout+run.stderr)
ns=m.load_registered(source)
_,c=m.capture_registered(np.full((512,512,3),100,np.uint8),ns)
receipt={'synthetic_only':True,'real_images_opened':False,'models_loaded':False,'source_sha256':hashlib.sha256((base/'construction.py').read_bytes()).hexdigest(),
         'registered_source_sha256':m.SBI_SHA,'sigma':c['sigma'],'shift_xy':c['shift_xy'],
         'alpha_raw_float32_sha256':hashlib.sha256(c['alpha'].tobytes()).hexdigest(),
         'alpha_dtype':str(c['alpha'].dtype),'alpha_shape':list(c['alpha'].shape),'alpha_range':[float(c['alpha'].min()),float(c['alpha'].max())],
         'region_plan':m.region_plan(c['alpha']),'fixtures_exit_code':run.returncode,'fixtures_stdout':run.stdout,'fixtures_stderr':run.stderr}
if len(sys.argv)!=2:raise ValueError('explicit create-only receipt path required')
with Path(sys.argv[1]).open('x') as f:
    json.dump(receipt,f,indent=2,allow_nan=False);f.write('\n');f.flush();os.fsync(f.fileno())
print('GENERATED_ONLY_6_TESTS_AND_GEOMETRY_PASS',receipt['shift_xy'],receipt['region_plan']['K'])
