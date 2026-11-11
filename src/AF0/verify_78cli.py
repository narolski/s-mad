import csv, sys, numpy as np, cv2, json
sys.argv=['x']
import importlib.util
spec=importlib.util.spec_from_file_location('afm','/home/narolski/smad-next/src/AF0/af_morph.py'); M=importlib.util.module_from_spec(spec); spec.loader.exec_module(M)
rows=[r for r in csv.DictReader(open('/mnt/t7/smad_next/AF0/manifest.csv')) if r['kind']=='morph'][:8]
res=[]
for r in rows:
    A,B=cv2.imread(r['A']),cv2.imread(r['B'])
    out,*_=M.af_morph(A,M.parse_tem(r['A'][:-4]+'.tem'),B,M.parse_tem(r['B'][:-4]+'.tem'),'u50',np.random.default_rng(0))
    ref=cv2.imread(f"/mnt/t7/smad_next/AF0/verify78/{r['id']}.png")
    res.append(int(np.abs(out.astype(int)-ref.astype(int)).max()))
print("max abs diff vs 78_tool_morph.py CLI PNG output:", res)
json.dump(dict(per_pair_maxabs_vs_78_cli_png=res), open('/home/narolski/smad-next/experiments/AF0/verify_u50_vs_78cli.json','w'))
