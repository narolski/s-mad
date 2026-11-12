import glob, numpy as np, csv
from PIL import Image
from scipy.stats import spearmanr
B=(slice(70,221),slice(64,193))
th={}
for f in glob.glob('/mnt/t7/smad_next/DG1/gen/addon_s*/out_addon_s*/addon_s*/gen_rows.csv'):
    for r in csv.DictReader(open(f)): th[(r['pool'],r['name'])]=r['theta_xT']
res={k:[] for k in ['NOISES20','SEMS20','SAME20','X20','FRESH1_20','NOISEX20','SEMX20']}
lap={}
import cv2
for d in sorted(glob.glob('/mnt/t7/smad_next/DG1/gen/addon_s*/out_addon_s*/addon_s*')):
    for f in sorted(glob.glob(d+'/AO_REC20/*.png')):
        n=f.split('/')[-1]; rec=np.asarray(Image.open(f).convert('RGB'),float)
        for k in res:
            g=glob.glob(f"{d}/AO_{k}/{n[:-4]}*.png")
            if not g: continue
            im=np.asarray(Image.open(g[0]).convert('RGB'),float)
            full=np.abs(im-rec).mean(); box=np.abs(im-rec)[B].mean(); out=full*im.size; 
            sur=(np.abs(im-rec).sum()-np.abs(im-rec)[B].sum())/(im.size-np.abs(im-rec)[B].size)
            t=th.get(('AO_'+k,g[0].split('/')[-1]),'')
            res[k].append((box,sur,float(t) if t else np.nan))
for k,v in res.items():
    v=np.array(v); print(k,len(v),'mean|d| vs REC face box',v[:,0].mean().round(2),'surround',v[:,1].mean().round(2), 'spearman box~theta', None if np.isnan(v[:,2]).all() else round(spearmanr(v[:,0],v[:,2])[0],3))
