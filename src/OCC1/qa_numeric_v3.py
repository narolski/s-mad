"""Actual PDF page/font verification and numeric-only raster proofs; no model inputs."""
import hashlib,io,json,re,subprocess,xml.etree.ElementTree as ET
from pathlib import Path
from PIL import Image

F=Path('/mnt/t7/smad_next/OCC1/20261114/numeric_print_v3');Q=F/'qa_pdf150'
Q.mkdir(exist_ok=False)
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
manifest=json.loads((F/'FIGURE_MANIFEST.json').read_text())
for x in manifest['files']:assert sha(x['path'])==x['sha256']
reports=[]
for p in sorted(F.glob('*.pdf')):
 info=subprocess.check_output(['pdfinfo',str(p)],text=True)
 m=re.search(r'Page size:\s+([0-9.]+) x ([0-9.]+) pts',info)
 assert m
 points=[float(m.group(1)),float(m.group(2))];mm=[v/72*25.4 for v in points]
 assert abs(mm[0]-180)<.01 and abs(mm[1]-210)<.01,(p,mm)
 xml=ET.fromstring(subprocess.check_output(['pdftohtml','-i','-xml','-stdout','-zoom','1',str(p)]))
 fonts=[float(v.attrib['size']) for v in xml.findall('.//fontspec')]
 assert fonts and min(fonts)>=8,(p,fonts)
 # Stream raster proof to memory; this never loads a source photograph.
 raw=subprocess.check_output(['pdftoppm','-f','1','-singlefile','-r','150','-png',str(p)])
 image=Image.open(io.BytesIO(raw));image.load()
 out=Q/(p.stem+'_pdf150.png')
 with out.open('xb') as f:f.write(raw)
 reports.append(dict(pdf=str(p),pdf_sha256=sha(p),page_points=points,page_mm=mm,min_poppler_font_pt=min(fonts),
                     max_poppler_font_pt=max(fonts),raster_proof=str(out),raster_sha256=sha(out),raster_size=list(image.size)))
assert len(reports)==10
layout=json.loads((F/'MPL_LAYOUT_QA.json').read_text())
assert len(layout)==10 and all(v['minimum_page_margin_mm']>=1 and min(v['tick_P18_gaps_mm'])>=1.5 and v['min_font_pt']>=8 for v in layout)
for p,h in manifest['preserved_reviewed_files'].items():assert sha(p)==h
out=dict(scope='Actual numeric-only PDF print-layout QA; no source faces, overlays, model inference or candidate data',
         pages=reports,all_ten_pdf_dimensions_and_fonts_pass=True,matplotlib_all_text_page_bounds_pass=True,
         minimum_text_page_margin_mm=min(v['minimum_page_margin_mm'] for v in layout),
         minimum_tick_to_P18_gap_mm=min(min(v['tick_P18_gaps_mm']) for v in layout),
         v2_and_reviewed_numerical_files_unchanged=True,independent_reapproval='PENDING',physical_printer_proof=False)
p=F/'POPPLER_PRINT_QA.json'
with p.open('x') as f:json.dump(out,f,indent=2);f.write('\n')
print('PASS10PDFs:180x210mm,min8pt;all10rasterproofssaved;data+v2unchanged',sha(p))
