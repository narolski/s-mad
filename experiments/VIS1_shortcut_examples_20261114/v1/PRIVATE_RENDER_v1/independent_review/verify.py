from pathlib import Path
import json,hashlib,base64,re
from PIL import Image
from pypdf import PdfReader
import pdfplumber
p=Path('outputs/shortcut_private_review_20261114');s=Path('work/shortcut_visual_examples/VIS1_render_v1');m=json.loads((p/'manifest.json').read_text());h=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
checks={}
checks['artifacts']=all(h(p/k)==v['sha256'] for k,v in m['files'].items())
checks['grant']=h(s/'ROOT_PRIVATE_RENDER_GRANT.json')==m['root_private_render_grant_sha256']
checks['prior_review']=h(s/'VIS1_CONTROLS_POSTRESULT_REVIEW_20261114.md')==m['independent_review_sha256']
inputs={x['input']['id']:s/(x['input']['id']+'.png') for x in m['source_inputs']}
checks['source_hashes']=all(h(inputs[x['input']['id']])==x['input']['sha256'] for x in m['source_inputs'])
pix=lambda im:(im.size,im.convert('RGB').tobytes())
r=PdfReader(p/'same_photo_processing_private.pdf');embedded=list(r.pages[0].images)
checks['pdf_exact_4_pixels']=len(embedded)==4 and sorted(hashlib.sha256(pix(x.image)[1]).hexdigest() for x in embedded)==sorted(hashlib.sha256(pix(Image.open(v))[1]).hexdigest() for v in inputs.values()) and all(x.image.size==(512,512) for x in embedded)
svg=(p/'same_photo_processing_private.svg').read_text(); blobs=re.findall(r'data:image/png;base64,([^\"]+)',svg)
checks['svg_exact_4_pngs']=len(blobs)==4 and sorted(hashlib.sha256(base64.b64decode(x)).hexdigest() for x in blobs)==sorted(h(v) for v in inputs.values())
checks['six_numbers']=len(m['displayed_numbers'])==6
for model,expected in m['result_hashes'].items():
 f=s/model/'RESULT.json'; assert h(f)==expected
 d=json.loads(f.read_text()); rows={v['id']:v for v in d['rows']}; pairs={v['photo_key']:v for v in d['pairs']}
 for v in [v for v in m['displayed_numbers'] if v['model']==model]:
  key=v['photo_key']; pair=pairs[key]
  for k in ('native_logit','history_logit','delta_logit'):assert v[k]==pair[k]
  assert pair['threshold'] is None and pair['decision_flip'] is None
  for mode in ('native','history'):assert v[mode+'_score']==rows[key+'_'+mode]['uncalibrated_sigmoid']
  assert v['displayed_delta']==f"{v['delta_logit']:+.3f}".replace('.',',')
  assert v['displayed_score']==f"{v['native_score']:.3f} → {v['history_score']:.3f}".replace('.',',')
with pdfplumber.open(p/'same_photo_processing_private.pdf') as pdf:
 pg=pdf.pages[0]; text=pg.extract_text();font=min(c['size'] for c in pg.chars); dims=[pg.width*25.4/72,pg.height*25.4/72]
 checks['all_displayed_numbers_in_pdf']=all(v['displayed_delta'] in text and v['displayed_score'] in text for v in m['displayed_numbers'])
 checks['text_in_bounds']=all(c['x0']>=0 and c['x1']<=pg.width and c['top']>=0 and c['bottom']<=pg.height for c in pg.chars)
 checks['min8pt']=font>=8;checks['180x280mm']=all(abs(a-b)<.001 for a,b in zip(dims,[180,280]))
receipt={'checks':checks,'minimum_actual_font_pt':font,'page_mm':dims,'source_png_sha256':{k:h(v) for k,v in inputs.items()},'artifacts_sha256':{x.name:h(x) for x in p.iterdir() if x.is_file()},'proofs_sha256':{x.name:h(x) for x in Path('work/vis1_independent_review').glob('actual_pdf*.png')}}
Path('work/vis1_independent_review/VERIFICATION.json').write_text(json.dumps(receipt,indent=2)+'\n');print(json.dumps(receipt,indent=2));assert all(checks.values())
