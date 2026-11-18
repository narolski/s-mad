"""Private VIS1 figure from exact admitted JSONs and four licensed fixed PNGs. CPU only."""
from pathlib import Path
import base64
import hashlib
import html
import json
from datetime import datetime, timezone

from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.utils import ImageReader
from reportlab.lib.colors import HexColor

HERE=Path(__file__).resolve().parent
OUT=HERE.parents[2]/'outputs/shortcut_private_review_20261114'
# Set absolute target from shared user workspace, never home-root.
OUT=Path('/Users/narolski/Documents/Codex/2026-11-14/na/outputs/shortcut_private_review_20261114')
OUT.mkdir(parents=True,exist_ok=True)
MM=72/25.4; W,H=180*MM,280*MM
FONT='/System/Library/Fonts/Supplemental/Arial.ttf'
BOLD='/System/Library/Fonts/Supplemental/Arial Bold.ttf'
pdfmetrics.registerFont(TTFont('Body',FONT));pdfmetrics.registerFont(TTFont('Bold',BOLD))
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
result_hashes={'selfmad_hrnet_w18':'a0c7793f2596e6ddc6f653a0a6e971fcfb63dc6410bd8f66478ce274d12e1d7e',
               'A':'18c46b3d3fced82f6162bcd2a5542601a72a08739675aa7b0421e1d82fa5bc62',
               'B':'35fa6ad2f0a74c152ca8b8437d543942c06a51423fc15c0393fe90898d456214'}
assert sha(HERE/'VIS1_CONTROLS_POSTRESULT_REVIEW_20261114.md')=='ff9d1a19e2ad57ac1592803abc746314199c7f7b9d040ed641e86ad2181b5e81'
results={}
for name,h in result_hashes.items():
    p=HERE/name/'RESULT.json';assert sha(p)==h
    results[name]=json.loads(p.read_text());assert results[name]['status']=='COMPLETE'
audit=json.loads((HERE/'INPUT_AUDIT.json').read_text());inputs={x['input']['id']:x for x in audit['inputs']}
render_grant=HERE/'ROOT_PRIVATE_RENDER_GRANT.json'
assert render_grant.is_file(), 'exact separate private render grant required'
grant=json.loads(render_grant.read_text())
assert grant['decision']=='GO_PRIVATE_RESEARCH_RENDER_ONLY'
assert grant['photos']==['FFHQ00042','FFHQ00056']
assert grant['models']==['selfmad_hrnet_w18','A','B']
assert grant['publication']=='HOLD'
assert grant['independent_numeric_review_sha256']==sha(HERE/'VIS1_CONTROLS_POSTRESULT_REVIEW_20261114.md')
for id,x in inputs.items():
    assert sha(HERE/(id+'.png'))==x['input']['sha256']
    assert x['attribution']['license_url']=='https://creativecommons.org/licenses/by-nc/2.0/'
pdf=OUT/'same_photo_processing_private.pdf'
c=canvas.Canvas(str(pdf),pagesize=(W,H),pageCompression=1,invariant=1)
c.setTitle('Same photograph, different detector response - private research preview')
c.setAuthor('');c.setSubject('Private research preview; not publication cleared')
svg=[f'<svg xmlns="http://www.w3.org/2000/svg" width="180mm" height="280mm" viewBox="0 0 {W} {H}">',
     '<title>Private VIS1 same-photo processing response; not publication cleared</title>',
     f'<rect width="{W}" height="{H}" fill="white"/>']
QA={'page_mm':[180,280],'text_boxes':[],'image_boxes':[],'model_rows':[]}
INK='#192d3a';MUTED='#536571';TEAL='#116877';LINE='#d6dee2'


def rect(x,y,w,h,color):
    x*=MM;y*=MM;w*=MM;h*=MM
    c.setFillColor(HexColor(color));c.rect(x,H-y-h,w,h,fill=1,stroke=0)
    svg.append(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" fill="{color}"/>')


def txt(x,y,text,size=8.3,bold=False,color=INK):
    x*=MM;y*=MM
    font='Bold' if bold else 'Body';width=pdfmetrics.stringWidth(text,font,size)
    assert size>=8 and x>=0 and x+width<=W-5*MM, (text,width/MM)
    assert y>=size and y<=H-2*MM
    c.setFillColor(HexColor(color));c.setFont(font,size);c.drawString(x,H-y,text)
    svg.append(f'<text x="{x}" y="{y}" font-family="Arial,sans-serif" font-size="{size}" font-weight="{700 if bold else 400}" fill="{color}">{html.escape(text)}</text>')
    QA['text_boxes'].append({'text':text,'x_mm':x/MM,'baseline_y_mm':y/MM,'width_mm':width/MM,'font_pt':size})


def img(x,y,id):
    p=HERE/(id+'.png');x*=MM;y*=MM;edge=74*MM
    c.drawImage(ImageReader(str(p)),x,H-y-edge,width=edge,height=edge,mask='auto')
    data=base64.b64encode(p.read_bytes()).decode()
    svg.append(f'<image x="{x}" y="{y}" width="{edge}" height="{edge}" href="data:image/png;base64,{data}"/>')
    QA['image_boxes'].append({'id':id,'x_mm':x/MM,'y_mm':y/MM,'edge_mm':74,'source_sha256':sha(p),'operation':'display-size only; source PNG unchanged'})


txt(8,9,'TA SAMA FOTOGRAFIA. INNY WYNIK DETEKTORA.',11.3,True)
txt(8,15,'Nie dodano drugiej osoby. Zmieniono historię zmiany rozmiaru i wyrównania.',8.6)
for top,key,index in [(22,'00042','1'),(129,'00056','2')]:
    # Two fixed examples, identical figure geometry and all three model dispositions.
    txt(8,top,f'Przykład {index}  |  oryginalny wariant',8.8,True)
    txt(98,top,'Ta sama fotografia po przetworzeniu',8.8,True)
    img(8,top+3,key+'_native');img(98,top+3,key+'_history')
    txt(8,top+82,'Jak zareagowały detektory?',8.5,True)
    txt(72,top+82,'Wynik: przed → po',8.3,True)
    txt(130,top+82,'Zmiana logitu',8.3,True)
    for j,(name,label) in enumerate([('selfmad_hrnet_w18','SelfMAD'),('A','Kontrola A (403)'),('B','Kontrola B (403)')]):
        z=results[name];rows={x['id']:x for x in z['rows']};pair=next(x for x in z['pairs'] if x['photo_key']==key)
        a,b=rows[key+'_native'],rows[key+'_history'];assert pair['threshold'] is None and pair['decision_flip'] is None
        assert pair['delta_logit']==b['logit']-a['logit']
        score=f"{a['uncalibrated_sigmoid']:.3f} → {b['uncalibrated_sigmoid']:.3f}".replace('.',',')
        delta=f"{pair['delta_logit']:+.3f}".replace('.',',')
        y=top+87+j*5.2
        if j==0:rect(7,y-3.7,166,5.2,'#eef5f5')
        txt(8,y,label,8.5,j==0,TEAL if j==0 else INK)
        txt(72,y,score,8.5,j==0,TEAL if j==0 else INK)
        txt(130,y,delta,8.5,j==0,TEAL if j==0 else INK)
        QA['model_rows'].append({'photo_key':key,'model':name,'native_logit':a['logit'],'history_logit':b['logit'],'native_score':a['uncalibrated_sigmoid'],'history_score':b['uncalibrated_sigmoid'],'delta_logit':pair['delta_logit'],'displayed_score':score,'displayed_delta':delta})
rect(8,234,164,.25,LINE)
foot=[
 ('Wynik nie jest prawdopodobieństwem ataku. Nie stosowano progu decyzji.',True),
 ('To dwa stałe przykłady. Wzrost wyniku SelfMAD nie dowodzi ogólnej skuteczności ani błędu.',False),
 ('Historia łączy zmniejszenie obrazu i ponowne wyrównanie; kadry nie są identyczne.',False),
 ('Nie jest to osobny test JPEG ani samego rozmycia. A/B: 224 px; SelfMAD: 384 px.',False),
 ('Zdjęcia FFHQ: 00042 / Rebecca Brown; 00056 / RAFFI YOUREDJIAN. CC BY-NC 2.0.',False),
 ('Zmiany przedstawione w parze: istniejące wyrównanie i wariant historii przetwarzania.',False),
 ('PRIVATE RESEARCH PREVIEW — NOT PUBLICATION CLEARED',True)]
for i,(s,b) in enumerate(foot):txt(8,240+i*5,s,8.1,b,color=MUTED if not b else INK)
c.showPage();c.save();svg.append('</svg>')
(OUT/'same_photo_processing_private.svg').write_text('\n'.join(svg))
caption='''Same photograph, different detector response. Two fixed FFHQ bona-fide photographs (00042 and 00056), selected before their VIS1 scores, are shown in their existing native-aligned and landmark_complete-history variants. No second contributor was added. The history combines INTER_AREA downsampling before separate alignment/cropping: source00042 changes1024→265px before alignment to512px; source00056 changes1024→249px before alignment to512px. Consequently this is neither a JPEG-only nor a blur-only intervention, and displayed crops are not identical. Every fixed model is retained: released SelfMAD and A/B seed403 last checkpoints. Table scores are uncalibrated sigmoid outputs; delta is history-minus-native in each model's own logit units. No operational threshold, decision flip, error-rate or cross-model robustness ranking is claimed. SelfMAD was chosen as the demonstration model after an earlier private pilot; these two photographs and A/B controls were fixed before the new scores. Cases are potentially exposed development illustrations with unknown person/component/full-training overlap. Private noncommercial research preview only; publication/likeness clearance remains unresolved. No source images were generated, retouched or replaced. No heatmap is shown and no new inference was run for rendering. Source photographs: Rebecca Brown, “Shirtless, bearded Josh.” (FFHQ00042), https://www.flickr.com/photos/rebeccacbrown13/2168341402/ ; RAFFI YOUREDJIAN, “MANGAGAN-7” (FFHQ00056), https://www.flickr.com/photos/62487011@N08/28696918755/ . Both CC BY-NC2.0, https://creativecommons.org/licenses/by-nc/2.0/ . FFHQ/FFHQ-Morphs dataset documentation is BY-NC-SA4.0; technical source attribution and transformation descriptions remain in the manifest.'''
(OUT/'caption_en.txt').write_text(caption+'\n')
manifest={'created_utc':datetime.now(timezone.utc).isoformat(),'scope':'PRIVATE_RESEARCH_PREVIEW_NOT_PUBLICATION_CLEARED','render_permission':'Root explicit task/message grants private rendering of42/56 in protected repository and user workspace, separate from inference no-source-pixel-save constraint; no public publication grant.',
          'rights_basis':'Verified exact per-image CC BY-NC2.0 allowing noncommercial attribution/adaptation; author/URL/change credits retained. Dataset documentation BY-NC-SA4.0. No consent/adulthood/document-acceptability claim.',
          'result_hashes':result_hashes,'independent_review_sha256':sha(HERE/'VIS1_CONTROLS_POSTRESULT_REVIEW_20261114.md'),
          'root_private_render_grant_sha256':sha(render_grant),
          'source_inputs':[x for x in audit['inputs']],
          'selection':'Fixed42/56 before new scores; all3fixedmodels and6pairs retained. No hero/outcome selection among cases.',
          'excluded_reference':'00010 numeric-reproduction control only; source pixels not displayed or embedded.',
          'displayed_numbers':QA['model_rows'],'caption_en':caption,'new_inference':False,'maps':'NONE; score-only illustration',
          'minimum_configured_font_pt':min(x['font_pt'] for x in QA['text_boxes']),
          'render_source_sha256':sha(__file__),'files':{p.name:{'sha256':sha(p),'bytes':p.stat().st_size} for p in [pdf,OUT/'same_photo_processing_private.svg',OUT/'caption_en.txt']},
          'QA':'Author source geometry/text-width assertions pass; actualPDF render/font/visual inspection pending, independent review required.'}
(OUT/'manifest.json').write_text(json.dumps(manifest,indent=2,ensure_ascii=False)+'\n')
(HERE/'AUTHOR_LAYOUT_QA.json').write_text(json.dumps(QA,indent=2,ensure_ascii=False)+'\n')
print(json.dumps({'pdf':str(pdf),'minimum_font':manifest['minimum_configured_font_pt'],'pairs':len(QA['model_rows'])}))
