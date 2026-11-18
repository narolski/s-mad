"""Print-size scientific tile plots of actual responses; source images never loaded."""
import json,hashlib
from pathlib import Path
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle

O=Path('/mnt/t7/smad_next/OCC1/20261114');F=O/'numeric_print_v2'
F.mkdir(exist_ok=False)
plt.rcParams.update({'font.family':'DejaVu Sans','font.size':8,'axes.labelsize':8,'xtick.labelsize':8,'ytick.labelsize':8,'svg.fonttype':'none','pdf.fonttype':42})
models=['A','B','Sb','mixfacenet_mad_smdd','selfmad_hrnet_w18']
pretty={'A':'A (frozen seed 403)','B':'B (frozen seed 403)','Sb':'Sb (frozen seed 403)',
        'mixfacenet_mad_smdd':'MixFaceNet-MAD (published)','selfmad_hrnet_w18':'SelfMAD (published, aligned-frame)'}
outputs=[]
for model in models:
 d=O/(model+'_full');r=json.loads((d/'result.json').read_text());assert r['status']=='COMPLETE'
 with np.load(d/'raw_responses.npz',allow_pickle=False) as z:
  names=z['conditions'].tolist();delta=z['delta_logits'].copy();base=z['baseline_logits'].copy();occ=z['occluded_logits'].copy()
  seams=z['seam_cell_indices'].tolist();controls=z['matched_surround_indices'].tolist()
 vmax=float(np.abs(delta).max());vmax=max(vmax,1e-12);chosen=seams[0];cy,cx=divmod(chosen,8)
 assert chosen==18 # pre-score geometry-only selected first seam-overlapping cell
 for gray in (False,True):
  fig=plt.figure(figsize=(180/25.4,210/25.4));axes=[]
  fig.text(.5,.975,pretty[model]+': actual constant-occlusion responses',ha='center',va='top',fontsize=9,weight='bold')
  fig.text(.5,.948,'64px square / stride 64; delta z = occluded - original attack logit',ha='center',va='top',fontsize=8)
  fig.text(.5,.927,'Hatching denotes negative delta.' if gray else 'Blue: less attack-like. Red: more attack-like. Uncalibrated scores.',ha='center',va='top',fontsize=8)
  last=None
  for row,(condition,label) in enumerate([('S0','S0: seam-control'),('S3','S3: same-person'),('S4','S4: two-person')]):
   j=names.index(condition);bottom=.68-row*.255
   score=1/(1+np.exp(-base[j]))
   fig.text(.015,bottom+.12,label+'\nz = %.3f\ns = %.3g'%(base[j],score),fontsize=8,va='center')
   for fi,fill in enumerate((0,128)):
    ax=fig.add_axes([.20+fi*.35,bottom,.29,.19]);arr=delta[j,fi]
    values=np.abs(arr) if gray else arr
    last=ax.pcolormesh(np.arange(9)*64,np.arange(9)*64,values,cmap='Greys' if gray else 'RdBu_r',
                      vmin=0 if gray else -vmax,vmax=vmax,shading='flat',edgecolors='0.7',linewidth=.25,rasterized=False)
    ax.set_xlim(0,512);ax.set_ylim(512,0);ax.set_aspect('equal');ax.set_xticks([0,256,512]);ax.set_yticks([0,256,512])
    ax.tick_params(length=2,pad=2)
    if row==0:ax.set_title('Black fill 0' if fill==0 else 'Gray fill 128',fontsize=8,pad=4)
    for k in seams:
     yy,xx=divmod(k,8);ax.add_patch(Rectangle((xx*64,yy*64),64,64,fill=False,edgecolor='black',linewidth=.8))
    for k in controls:
     yy,xx=divmod(k,8);ax.add_patch(Rectangle((xx*64,yy*64),64,64,fill=False,edgecolor='black',linewidth=.65,linestyle=':'))
    if gray:
     for yy in range(8):
      for xx in range(8):
       if arr[yy,xx]<0:ax.add_patch(Rectangle((xx*64,yy*64),64,64,fill=False,edgecolor='0.3',linewidth=0,hatch='///'))
    ax.text((cx+.5)*64,(cy+.5)*64,'P18',fontsize=8,ha='center',va='center',color='black',bbox=dict(facecolor='white',alpha=.85,edgecolor='none',pad=.3))
    zocc=occ[j,fi,cy,cx];dv=delta[j,fi,cy,cx];socc=1/(1+np.exp(-zocc))
    reg=next(v for v in r['regional_effects'] if v['condition']==condition and v['fill_rgb']==fill)
    fig.text(.20+fi*.35,bottom-.027,"P18: z'=%.3f, delta=%+.3f"%(zocc,dv),fontsize=8,ha='left')
    fig.text(.20+fi*.35,bottom-.047,"Mean delta seam/control: %+.2f / %+.2f"%(reg['seam_mean_delta'],reg['matched_surround_mean_delta']),fontsize=8,ha='left')
    axes.append(ax)
  cax=fig.add_axes([.925,.21,.018,.61]);cb=fig.colorbar(last,cax=cax);cb.ax.tick_params(labelsize=8,length=2,pad=2)
  cb.set_label('Absolute delta z' if gray else 'Signed delta z',fontsize=8)
  fig.text(.5,.105,'Solid outlines:17 seam-overlapping cells; dotted:17 spatial control cells.',fontsize=8,ha='center')
  fig.text(.5,.082,'Original faces withheld: internal research only; no source-pixel export.',fontsize=8,ha='center')
  fig.text(.5,.061,'One fixed dev host. Controls match area/shape, not texture/position.',fontsize=8,ha='center')
  fig.text(.5,.040,'Two fills do not eliminate mask artifacts. No causal or population claim.',fontsize=8,ha='center')
  stem=model+('_grayscale' if gray else '_color')
  for ext in ('pdf','svg','png'):
   p=F/(stem+'.'+ext);fig.savefig(p,dpi=350,facecolor='white');outputs.append(dict(path=str(p),sha256=hashlib.sha256(p.read_bytes()).hexdigest()))
  plt.close(fig)
manifest=dict(scope='Numeric-only actual-response figures; no sourceimage access; not face-containing display clearance',
              page_width_mm=180,page_height_mm=210,min_font_pt=8,smoothing=False,measured_grid=[8,8],
              scales='Symmetric maximum absolute across all8rungs andbothfills permodel; grayscale absolute withnegativehatching',
              predetermined_highlight='P18: first seam cell fixed by geometry before scores',files=outputs,
              excluded_models={'madation_vitb16':'Failed batch-parity smoke','madation_vitl14':'Failed CUDA OOM smoke; no full sweep'})
with (F/'FIGURE_MANIFEST.json').open('x') as f:json.dump(manifest,f,indent=2);f.write('\n')
print('Rendered10 actual-data180mm figures (5models xcolor/grayscale); nofacesloaded',F)
