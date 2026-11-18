"""Print-size scientific tile plots of actual responses; source images never loaded."""
import json,hashlib
from pathlib import Path
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle
from matplotlib.text import Text

O=Path('/mnt/t7/smad_next/OCC1/20261114');F=O/'numeric_print_v3'
F.mkdir(exist_ok=False)
plt.rcParams.update({'font.family':'DejaVu Sans','font.size':8,'axes.labelsize':8,'xtick.labelsize':8,'ytick.labelsize':8,'svg.fonttype':'none','pdf.fonttype':42})
models=['A','B','Sb','mixfacenet_mad_smdd','selfmad_hrnet_w18']
pretty={'A':'A (frozen seed 403)','B':'B (frozen seed 403)','Sb':'Sb (frozen seed 403)',
        'mixfacenet_mad_smdd':'MixFaceNet-MAD (published)','selfmad_hrnet_w18':'SelfMAD (published, aligned-frame)'}
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
E=Path('/home/narolski/smad-next/experiments/OCC1_seam-surround-pilot_20261114')
audit_path=E/'ASTRA_POSTRESULT_NUMERICAL_CHECK.json'
assert sha(audit_path)=='4e9930e74212f94f053c779e9702ff89d91790586acf25d5e637e101a71bb1c3'
audited=json.loads(audit_path.read_text())['input_sha256']
preserved={}
for p,h in audited.items():
 p=Path(p)
 if p.is_relative_to(O) and (p.parent.name=='numeric_print_v2' or p.parent.name.endswith('_full') or p.name in ('baseline_scores.csv','regional_effects.csv','paired_rung_effects.csv')):
  assert sha(p)==h, str(p)
  preserved[str(p)]=h
outputs=[];display_values=[];layout_checks=[]
for model in models:
 d=O/(model+'_full');r=json.loads((d/'result.json').read_text());assert r['status']=='COMPLETE'
 with np.load(d/'raw_responses.npz',allow_pickle=False) as z:
  names=z['conditions'].tolist();delta=z['delta_logits'].copy();base=z['baseline_logits'].copy();occ=z['occluded_logits'].copy()
  seams=z['seam_cell_indices'].tolist();controls=z['matched_surround_indices'].tolist()
 vmax=float(np.abs(delta).max());vmax=max(vmax,1e-12);chosen=seams[0];cy,cx=divmod(chosen,8)
 expected={'A':5.7325520515441895,'B':6.336426734924316,'Sb':4.423853039741516,'mixfacenet_mad_smdd':12.020625531673431,'selfmad_hrnet_w18':1.6233634948730469}
 assert vmax==expected[model]
 assert chosen==18 # pre-score geometry-only selected first seam-overlapping cell
 for gray in (False,True):
  fig=plt.figure(figsize=(180/25.4,210/25.4));axes=[]
  fig.text(.5,.975,pretty[model]+': actual constant-occlusion responses',ha='center',va='top',fontsize=9,weight='bold')
  fig.text(.5,.948,'Native patch: 64x64px before model preprocessing; stride 64. Delta z = occluded - original logit.',ha='center',va='top',fontsize=8)
  fig.text(.5,.928,'s = uncalibrated sigmoid(z). Only S0/S3/S4 shown; full data contain 8 rungs.',ha='center',va='top',fontsize=8)
  fig.text(.5,.908,'Hatching: negative delta (less attack-like).' if gray else 'Blue: negative delta (less attack-like). Red: positive delta (more attack-like).',ha='center',va='top',fontsize=8)
  last=None;annotation_checks=[]
  for row,(condition,label) in enumerate([('S0','S0: seam-control'),('S3','S3: same-person'),('S4','S4: two-person')]):
   j=names.index(condition);bottom=.685-row*.26
   score=1/(1+np.exp(-base[j]))
   fig.text(.015,bottom+.12,label+'\nz = %.3f\ns = %.3g'%(base[j],score),fontsize=8,va='center')
   for fi,fill in enumerate((0,128)):
    ax=fig.add_axes([.20+fi*.35,bottom,.29,.175]);arr=delta[j,fi]
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
    first=fig.text(.20+fi*.35,bottom-.041,"P18: z'=%.3f, delta=%+.3f"%(zocc,dv),fontsize=8,ha='left')
    second=fig.text(.20+fi*.35,bottom-.059,"Mean delta S/C: %+.2f / %+.2f"%(reg['seam_mean_delta'],reg['matched_surround_mean_delta']),fontsize=8,ha='left')
    annotation_checks.append((ax,first,second))
    if not gray:display_values.append(dict(model=model,condition=condition,fill=fill,baseline_logit=float(base[j]),baseline_score=float(score),P18_occluded_logit=float(zocc),P18_delta=float(dv),seam_mean=reg['seam_mean_delta'],control_mean=reg['matched_surround_mean_delta'],vmax=vmax))
    axes.append(ax)
  cax=fig.add_axes([.86,.21,.018,.61]);cb=fig.colorbar(last,cax=cax);cb.ax.tick_params(labelsize=8,length=2,pad=2)
  cb.set_label('Absolute delta z' if gray else 'Signed delta z',fontsize=8)
  fig.text(.5,.0775,'Limits shared across all 8 rungs / 2 fills within each model; scales differ between models.',fontsize=8,ha='center')
  fig.text(.5,.0595,'S/C = seam/control. Solid: 17 seam-overlapping cells; dotted: 17 area/shape controls.',fontsize=8,ha='center')
  fig.text(.5,.0415,'S3 uses R2w; S0/S4 use R2w4. Controls are not texture/position matched; fill artifacts remain.',fontsize=8,ha='center')
  fig.text(.5,.0235,'Original faces withheld. One fixed host; no causal/population claim. Internal numerical research only.',fontsize=8,ha='center')
  stem=model+('_grayscale' if gray else '_color')
  fig.canvas.draw();ren=fig.canvas.get_renderer();mm_per_pixel=25.4/fig.dpi
  texts=[t for t in fig.findobj(match=Text) if t.get_visible() and t.get_text().strip()]
  text_boxes=[]
  for t in texts:
   b=t.get_window_extent(ren);margins=[b.x0,b.y0,fig.bbox.width-b.x1,fig.bbox.height-b.y1]
   assert t.get_fontsize()>=8 and min(margins)*mm_per_pixel>=1,(stem,t.get_text(),margins)
   text_boxes.append(dict(text=t.get_text(),font_pt=t.get_fontsize(),bbox_pixels=list(b.bounds),minimum_page_margin_mm=min(margins)*mm_per_pixel))
  gaps=[];bar_gaps=[]
  for ax,first,second in annotation_checks:
   ticks=[t.get_window_extent(ren) for t in ax.get_xticklabels() if t.get_visible()]
   gap=(min(b.y0 for b in ticks)-first.get_window_extent(ren).y1)*mm_per_pixel
   assert gap>=1.5,(stem,'tick/P18 gap',gap)
   gaps.append(gap)
   bar_gap=(cax.get_window_extent(ren).x0-second.get_window_extent(ren).x1)*mm_per_pixel
   assert bar_gap>=2,(stem,'annotation/colorbar gap',bar_gap)
   bar_gaps.append(bar_gap)
  layout_checks.append(dict(figure=stem,min_font_pt=min(t.get_fontsize() for t in texts),minimum_page_margin_mm=min(x['minimum_page_margin_mm'] for x in text_boxes),tick_P18_gaps_mm=gaps,summary_colorbar_gaps_mm=bar_gaps,texts=text_boxes))
  for ext in ('pdf','svg','png'):
   p=F/(stem+'.'+ext);fig.savefig(p,dpi=350,facecolor='white');outputs.append(dict(path=str(p),sha256=hashlib.sha256(p.read_bytes()).hexdigest()))
  plt.close(fig)
assert all(sha(p)==h for p,h in preserved.items()),'Previously reviewed numerical/v2 files changed'
for name,value in [('DISPLAY_VALUES.json',display_values),('MPL_LAYOUT_QA.json',layout_checks)]:
 with (F/name).open('x') as f:json.dump(value,f,indent=2);f.write('\n')
manifest=dict(scope='Numeric-only print-layout repair; not fulfillment of requested face-containing explanatory figure or publication clearance',
              page_width_mm=180,page_height_mm=210,min_font_pt=8,smoothing=False,measured_grid=[8,8],
              scales='Symmetric maximum absolute across all8rungs andbothfills permodel; grayscale absolute withnegativehatching',
              predetermined_highlight='P18: first seam cell fixed by geometry before scores',files=outputs,
              renderer_sha256=sha(__file__),prior_review_sha256=sha(E/'POSTRESULT_PRINT_REVIEW.md'),
              independent_numerical_audit_sha256=sha(audit_path),preserved_reviewed_files=preserved,
              data_numbers_scales_unchanged=True,display_values_sha256=sha(F/'DISPLAY_VALUES.json'),layout_qa_sha256=sha(F/'MPL_LAYOUT_QA.json'),
              excluded_models={'madation_vitb16':'Failed batch-parity smoke','madation_vitl14':'Failed CUDA OOM smoke; no full sweep'})
with (F/'FIGURE_MANIFEST.json').open('x') as f:json.dump(manifest,f,indent=2);f.write('\n')
print('Rendered 10 numeric-only v3 pages; source data/numbers/scales and v2 preserved; no faces or inference',F)
