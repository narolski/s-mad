from pathlib import Path
import hashlib,json,subprocess,xml.etree.ElementTree as ET
import numpy as np
R=Path('/home/narolski/smad-next');E=R/'experiments/OCC1_seam-surround-pilot_20261114';O=Path('/mnt/t7/smad_next/OCC1/20261114');F=O/'numeric_print_v3';H=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
a=E/'ASTRA_POSTRESULT_NUMERICAL_CHECK.json';assert H(a)=='4e9930e74212f94f053c779e9702ff89d91790586acf25d5e637e101a71bb1c3';audit=json.loads(a.read_text());n=0
for p,h in audit['input_sha256'].items():
 p=Path(p)
 if p.is_relative_to(O) and (p.parent.name=='numeric_print_v2' or p.parent.name.endswith('_full') or p.name in ('baseline_scores.csv','regional_effects.csv','paired_rung_effects.csv')):assert H(p)==h;n+=1
assert n==50
m=json.loads((F/'FIGURE_MANIFEST.json').read_text());pdf=[]
for x in m['files']:
 p=Path(x['path']);assert H(p)==x['sha256']
 if p.suffix!='.pdf':continue
 info=subprocess.check_output(['pdfinfo',str(p)],text=True);assert '510.236 x 595.276 pts' in info
 z=ET.fromstring(subprocess.check_output(['pdftohtml','-i','-xml','-stdout','-zoom','1',str(p)]));fonts=[float(v.attrib['size']) for v in z.findall('.//fontspec')];assert min(fonts)>=8
 text=subprocess.check_output(['pdftotext','-layout',str(p),'-'],text=True)
 for phrase in ['uncalibrated sigmoid(z)','full data contain 8 rungs','scales differ between models','Internal numerical research only']:assert phrase in text
 pdf.append({'file':p.name,'sha256':H(p),'min_font_pt':min(fonts),'page_points':[510.236,595.276]})
assert len(pdf)==10
values=json.loads((F/'DISPLAY_VALUES.json').read_text());assert len(values)==30
for model in ['A','B','Sb','mixfacenet_mad_smdd','selfmad_hrnet_w18']:
 with np.load(O/(model+'_full')/'raw_responses.npz',allow_pickle=False) as z:
  for v in [v for v in values if v['model']==model]:
   j=z['conditions'].tolist().index(v['condition']);f=[0,128].index(v['fill']);d=z['delta_logits'][j,f].ravel();assert v['baseline_logit']==z['baseline_logits'][j] and v['P18_occluded_logit']==z['occluded_logits'][j,f].ravel()[18] and v['P18_delta']==d[18] and v['vmax']==abs(z['delta_logits']).max()
   assert v['seam_mean']==d[z['seam_cell_indices']].mean() and v['control_mean']==d[z['matched_surround_indices']].mean()
pins={str(p):H(p) for p in [F/'FIGURE_MANIFEST.json',F/'DISPLAY_VALUES.json',F/'POPPLER_PRINT_QA.json',F/'MPL_LAYOUT_QA.json',R/'src/OCC1/render_numeric_v3.py',R/'src/OCC1/qa_numeric_v3.py',E/'PRINT_V3_OWNER_REPORT_20261114.md']}
out={'verdict':'PASS_NUMERIC_ONLY_PRINT_METADATA_AND_DISPLAY_FIDELITY','unchanged_previously_reviewed_files':n,'display_records_verified':30,'pdfs':pdf,'pins':pins,'no_inference':True,'source_face_export':False}
p=E/'PRINT_V3_INDEPENDENT_CHECKS.json';p.write_text(json.dumps(out,indent=2)+'\n');print(H(p));print(json.dumps(pins,indent=2))
