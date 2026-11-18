"""VIS2 renderer SOURCE ONLY. Real results/pixels require a new exact private grant."""
import argparse
import base64
import hashlib
import html
import importlib.metadata
import json
import math
from pathlib import Path
import sys

MODELS=('selfmad_hrnet_w18','A','B')
IDS=('00042_native','00042_history','00056_native','00056_history')
KEYS=('00042','00056')
MM=72/25.4
WIDTH_MM,HEIGHT_MM=180,322
EDGE_MM=68
MAP_X=(12,100)
MAP_Y=(116,201)
MIN_FONT=8.2


def need(ok,message):
    if not ok:raise ValueError(message)


def sha(path):
    h=hashlib.sha256()
    with Path(path).open('rb') as f:
        for b in iter(lambda:f.read(1024*1024),b''):h.update(b)
    return h.hexdigest()


def finite(v):return type(v) in (float,int) and math.isfinite(v)


def validate_result(r,model,expected_inventory,anchors):
    """Full512 response contract; no file opening or plotting in this pure function."""
    need(model in MODELS and r['model']==model,'wrong model')
    need(r['experiment']=='VIS2_PRIVATE_OCCLUSION_V1' and r['status']=='COMPLETE' and r['phase']=='full','full COMPLETE only')
    need(r['inventory_sha256']==expected_inventory,'numeric inventory changed')
    need(r['inputs_ids']==list(IDS) and r['fills_uint8']==[0,128],'fixed input/fill order changed')
    need(r['batch_size']==1 and r['res']==(384 if model==MODELS[0] else 224),'wrong scorer resolution/batch')
    need(r['threshold'] is None and r['decision_flips'] is None,'no operational decision allowed')
    need(r['source_pixels_exported'] is False and r['maps_rendered'] is False,'numeric source export mismatch')
    need(r['noTTA'] is True and r['tf32_matmul'] is False and r['tf32_cudnn'] is False,'wrong arithmetic')
    need(r['gpu']=='NVIDIA GB10' and r['torch']=='2.12.1+cu130' and r['cuda']=='13.0','wrong native VIS2 runtime')
    need(r['seam_masks']=='NONE_EXISTS_ON_THESE_GENUINE_PHOTOS; no seam localization claim','fabricated seam scope')
    baseline=r['baseline_logits'];need(len(baseline)==4 and all(finite(x) for x in baseline),'bad baselines')
    need(all(abs(baseline[i]-anchors[model][id])<=1e-5 for i,id in enumerate(IDS)),'VIS1 anchor mismatch')
    rows=r['responses'];need(len(rows)==512,'complete512 responses required')
    values={}
    for row in rows:
        id,fill,cell=row['input_id'],row['fill_uint8'],row['cell']
        need(id in IDS and type(fill) is int and fill in (0,128) and type(cell) is int and 0<=cell<64,'foreign input/fill/cell')
        token=(id,fill,cell);need(token not in values,'duplicate response')
        need((row['row'],row['col'],row['native_y'],row['native_x'],row['native_area'])==(cell//8,cell%8,(cell//8)*64,(cell%8)*64,4096),'wrong native geometry')
        z0,z1,d=row['baseline_logit'],row['occluded_logit'],row['delta_logit']
        need(all(finite(x) for x in (z0,z1,d)),'nonfinite/Boolean response')
        need(z0==baseline[IDS.index(id)] and abs(d-(z1-z0))<=1e-12,'delta/baseline mismatch')
        values[token]=float(d)
    need(set(values)=={(id,f,i) for id in IDS for f in (0,128) for i in range(64)},'missing fixed cells')
    # ALL four inputs/both fills before any case/page is rendered; never per-panel scaling.
    limit=max(abs(x) for x in values.values())
    return {'values':values,'limit':limit,'baseline':dict(zip(IDS,baseline))}


def normalized(delta,limit):
    need(finite(delta) and finite(limit) and limit>=0 and abs(delta)<=limit,'scale must cover exact measured value')
    if limit==0:
        need(delta==0,'nonzero delta under zero scale')
        return 0.0
    return delta/limit


def color(delta,limit,gray=False):
    q=normalized(delta,limit)
    if gray:
        a=1-abs(q);return a,a,a
    if q>=0:return 1.,1.-q,1.-q
    return 1.+q,1.+q,1.


def layout_boxes():
    photos=[{'kind':'source','x':x,'y':24,'w':EDGE_MM,'h':EDGE_MM} for x in MAP_X]
    maps=[{'kind':'measured_map','x':x,'y':y,'w':EDGE_MM,'h':EDGE_MM} for y in MAP_Y for x in MAP_X]
    return photos+maps


def validate_layout():
    boxes=layout_boxes()
    need(all(b['x']>=8 and b['y']>=20 and b['x']+b['w']<=WIDTH_MM-8 and b['y']+b['h']<=HEIGHT_MM-32 for b in boxes),'layout outside page')
    for i,a in enumerate(boxes):
        for b in boxes[i+1:]:
            overlap=(a['x']<b['x']+b['w'] and b['x']<a['x']+a['w'] and a['y']<b['y']+b['h'] and b['y']<a['y']+a['h'])
            need(not overlap,'source/map panels overlap')
    need(MIN_FONT>=8 and len(maps:= [b for b in boxes if b['kind']=='measured_map'])==4,'print contract')
    return boxes


def authorize(config_path,release_path,data_root,out_root):
    """Only config/grant/source/review metadata read before explicit authorization."""
    cfg=json.loads(Path(config_path).read_text());grant=json.loads(Path(release_path).read_text())
    need(grant['decision']=='GO_VIS2_PRIVATE_MEASURED_RENDER','new measured-render grant required')
    need(grant['source_pixel_export_allowed'] is True and grant['new_overlay_render_allowed'] is True,'legacy numeric/VIS1 grant cannot render new overlays')
    need(grant['publication']=='HOLD','private-only scope')
    need(grant['config_sha256']==sha(config_path),'configuration changed')
    need(grant['models']==list(MODELS) and grant['photos']==list(KEYS),'no selected model/photo subset')
    need(grant['data_root']==str(Path(data_root).resolve()) and grant['out_root']==str(Path(out_root).resolve()),'staging/output scope differs')
    need(grant['render_author']!=grant['code_reviewer'] and grant['code_reviewer'],'independent code review required')
    need(sha(grant['code_review_path'])==grant['code_review_sha256'],'code review changed')
    code=Path(__file__).resolve().parent
    need(sha(code/'SHA256SUMS')==grant['source_manifest_sha256'],'renderer manifest changed')
    for line in (code/'SHA256SUMS').read_text().splitlines():
        h,name=line.split('  ',1);p=code/name
        need(p.resolve().is_relative_to(code) and sha(p)==h,'renderer source changed')
    reviews=grant['numeric_postreviews'];covered=set()
    for review in reviews:
        need(sha(review['path'])==review['sha256'],'full numerical postreview changed')
        need(review['author']!=review['reviewer'] and review['reviewer'],'OTHER numerical postreview required')
        covered.update(review['models'])
    need(covered==set(MODELS),'allthree full sweeps need admitted postreview')
    roster=grant['full_result_roster'];need(len(roster)==3 and {x['model'] for x in roster}==set(MODELS),'complete3model roster')
    for x in roster:
        need(x['canonical_origin']==cfg['canonical_full_results'][x['model']],'smoke/foreign result origin refused')
        need(x['replica_relpath']==x['model']+'/RESULT.json','unregistered replica layout')
    need(cfg['inputs_ids']==list(IDS) and cfg['models']==list(MODELS),'configuration roster changed')
    need([x['id'] for x in cfg['inputs']]==list(IDS),'source input order/duplicates changed')
    need(cfg['render_mode']=='source_overlay' and cfg['map_interpolation']=='none','only measured native cells allowed')
    need(importlib.metadata.version('reportlab')==cfg['render_runtime']['reportlab'],'render library changed')
    need(importlib.metadata.version('pillow')==cfg['render_runtime']['pillow'],'image library changed')
    need(str(Path(sys.executable).resolve())==str(Path(cfg['render_runtime']['python']).resolve()),'render interpreter changed')
    validate_layout()
    return cfg,grant


def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('--config',required=True,type=Path)
    ap.add_argument('--release',required=True,type=Path)
    ap.add_argument('--data-root',required=True,type=Path)
    ap.add_argument('--out-root',required=True,type=Path)
    args=ap.parse_args();need(sys.flags.isolated,'python -I required')
    cfg,grant=authorize(args.config,args.release,args.data_root,args.out_root)
    # First real FULL numeric response access occurs only after the complete newgrant above.
    measured={};result_pins={}
    for entry in grant['full_result_roster']:
        p=args.data_root/entry['replica_relpath'];need(sha(p)==entry['sha256'],'full result hash changed')
        measured[entry['model']]=validate_result(json.loads(p.read_text()),entry['model'],cfg['numeric_inventory_sha256'],cfg['baseline_anchors'])
        result_pins[entry['model']]=entry['sha256']
    # Only now verify and open specifically released existing face pixels; never reference00010.
    input_paths={}
    for item in cfg['inputs']:
        id=item['id'];need(id in IDS and item['replica_name']==id+'.png','foreign image')
        p=args.data_root/'inputs'/item['replica_name'];need(sha(p)==item['sha256'],'source image differs')
        input_paths[id]=p
    need(set(input_paths)==set(IDS),'four faces required')
    args.out_root.mkdir(parents=True,exist_ok=False)
    from reportlab.pdfgen import canvas
    from reportlab.pdfbase import pdfmetrics
    from reportlab.pdfbase.ttfonts import TTFont
    from reportlab.lib.utils import ImageReader
    from reportlab.lib.colors import Color
    need(sha(cfg['fonts']['regular'])==cfg['fonts']['regular_sha256'] and sha(cfg['fonts']['bold'])==cfg['fonts']['bold_sha256'],'font changed')
    pdfmetrics.registerFont(TTFont('Body',cfg['fonts']['regular']))
    pdfmetrics.registerFont(TTFont('Bold',cfg['fonts']['bold']))
    width,height=WIDTH_MM*MM,HEIGHT_MM*MM
    image_bytes={id:p.read_bytes() for id,p in input_paths.items()}
    texts=[];files=[];summary=[];cell_records=[]
    for gray in (False,True):
        edition='gray_sign_hatching' if gray else 'signed_color'
        pdf=args.out_root/(edition+'.pdf')
        c=canvas.Canvas(str(pdf),pagesize=(width,height),pageCompression=1,invariant=1)
        c.setTitle('VIS2 private measured occlusion; no publication clearance');c.setAuthor('')
        for model in MODELS:
            data=measured[model];limit=data['limit']
            for key in KEYS:
                sv=[f'<svg xmlns="http://www.w3.org/2000/svg" width="180mm" height="322mm" viewBox="0 0 {width} {height}">',
                    '<title>Private measured occlusion response; not causal attribution</title>',f'<rect width="{width}" height="{height}" fill="white"/>']
                def text(x,y,s,size=MIN_FONT,bold=False):
                    font='Bold' if bold else 'Body';x*=MM;y*=MM
                    need(size>=8 and x+pdfmetrics.stringWidth(s,font,size)<=width-7*MM,'text overflow/minfont; repair layout only')
                    need(y>=size and y<height-3*MM,'text outside page')
                    c.setFont(font,size);c.setFillColor(Color(.10,.17,.21));c.drawString(x,height-y,s)
                    sv.append(f'<text x="{x}" y="{y}" font-family="Arial,sans-serif" font-size="{size}" font-weight="{700 if bold else 400}" fill="#192b36">{html.escape(s)}</text>')
                    texts.append({'edition':edition,'model':model,'photo':key,'text':s,'font':size})
                def photo(id,x,y):
                    c.drawImage(ImageReader(str(input_paths[id])),x*MM,height-(y+EDGE_MM)*MM,width=EDGE_MM*MM,height=EDGE_MM*MM,mask='auto')
                    s=base64.b64encode(image_bytes[id]).decode()
                    sv.append(f'<image x="{x*MM}" y="{y*MM}" width="{EDGE_MM*MM}" height="{EDGE_MM*MM}" href="data:image/png;base64,{s}"/>')
                def rectangle(x,y,w,h,rgb,alpha=1):
                    c.saveState();c.setFillAlpha(alpha);c.setFillColor(Color(*rgb));c.rect(x*MM,height-(y+h)*MM,w*MM,h*MM,fill=1,stroke=0);c.restoreState()
                    col='rgb('+','.join(str(round(t*255)) for t in rgb)+')'
                    sv.append(f'<rect x="{x*MM}" y="{y*MM}" width="{w*MM}" height="{h*MM}" fill="{col}" opacity="{alpha}"/>')
                def hatch(x,y,tag):
                    edge=EDGE_MM/8;xx=x*MM;yy=height-(y+edge)*MM;ee=edge*MM
                    c.saveState();p=c.beginPath();p.rect(xx,yy,ee,ee);c.clipPath(p,stroke=0,fill=0);c.setLineWidth(.22);c.setStrokeColor(Color(0,0,0))
                    for offset in range(-24,48,5):c.line(xx+offset,yy,xx+offset+ee,yy+ee)
                    c.restoreState();ident='h'+tag
                    sv.append(f'<clipPath id="{ident}"><rect x="{xx}" y="{y*MM}" width="{ee}" height="{ee}"/></clipPath><g clip-path="url(#{ident})" stroke="black" stroke-width=".22">')
                    for off in range(-24,48,5):sv.append(f'<line x1="{xx+off}" y1="{(y+edge)*MM}" x2="{xx+off+ee}" y2="{y*MM}"/>')
                    sv.append('</g>')
                text(8,8,'Ta sama fotografia. Zasłaniamy mały fragment.',11.1,True)
                text(8,14,f"{cfg['labels'][model]} | fotografia {key} | rzeczywiste pomiary, nie mapa przyczynowa",8.3)
                text(12,21,'Wariant oryginalny',8.8,True);text(100,21,'Istniejąca historia przetworzenia',8.8,True)
                for id,x in [(key+'_native',12),(key+'_history',100)]:
                    photo(id,x,24);z=data['baseline'][id];score=1/(1+math.exp(-z)) if z>=0 else math.exp(z)/(1+math.exp(z))
                    text(x,98,f'Wynik bazowy: {score:.3f}; z={z:+.3g}',8.6,True)
                text(8,105,'Poniżej: zmiana z po zasłonięciu wskazanego kwadratu 64 x 64 px.',8.3)
                for fill,y,title in [(0,116,'Zasłonięcie czernią (0/255)'),(128,201,'Zasłonięcie szarością (128/255)')]:
                    text(12,y-4,title,8.8,True)
                    for id,x in [(key+'_native',12),(key+'_history',100)]:
                        photo(id,x,y)
                        for cell in range(64):
                            val=data['values'][id,fill,cell];xx=x+(cell%8)*EDGE_MM/8;yy=y+(cell//8)*EDGE_MM/8
                            # Cell values are never interpolated, clipped, normalized per-panel or smoothed.
                            rectangle(xx,yy,EDGE_MM/8,EDGE_MM/8,color(val,limit,gray),0.0 if limit==0 else cfg['overlay_alpha'])
                            if gray and val<0:hatch(xx,yy,f'{fill}_{id}_{cell}')
                            cell_records.append({'edition':edition,'model':model,'photo_key':key,'input_id':id,'fill':fill,'cell':cell,
                                                 'delta_logit':val,'limit':limit,'normalized':normalized(val,limit),'color_RGB':color(val,limit,gray),
                                                 'negative_hatching':bool(gray and val<0),'overlay_alpha':0.0 if limit==0 else cfg['overlay_alpha'],
                                                 'x_mm':xx,'y_mm':yy,'edge_mm':EDGE_MM/8})
                if limit==0:
                    rectangle(12,275,156,3,(1,1,1),1)
                    text(12,283,'Wszystkie zmierzone zmiany wynoszą 0. Nie dodano kontrastu.',8.3,True)
                else:
                    for i in range(64):
                        value=limit*i/63 if gray else -limit+2*limit*i/63
                        rectangle(12+i*156/64,275,156/64,3,color(value,limit,gray),1)
                    text(12,283,('0' if gray else f'{-limit:.3g}')+'   |   '+('wartość bezwzględna; kreskowanie: minus' if gray else 'ujemna zmiana  /  0  /  dodatnia zmiana')+f'   |   {limit:.3g}',8.2)
                text(8,290,'Δz = z po zasłonięciu − z oryginalne. Wspólna skala 512 pomiarów/model.',8.2)
                text(8,295,'Wynik bazowy to niekalibrowany sigmoid(z), a nie prawdopodobieństwo ataku.',8.2)
                text(8,300,'Maska usuwa treść i tworzy artefakt. Lokalna reakcja nie wskazuje przyczyny.',8.2)
                text(8,305,'Kadry różnią się wyrównaniem. Nie ma szwu; pozycje nie są dopasowane anatomicznie.',8.2)
                text(8,310,cfg['credits_short'][key],8.2)
                text(8,316,'PRIVATE RESEARCH PREVIEW - NOT PUBLICATION CLEARED',8.3,True)
                c.showPage();sv.append('</svg>')
                svg=args.out_root/f'{edition}_{model}_{key}.svg';svg.write_text('\n'.join(sv));files.append(svg)
                summary.append({'edition':edition,'model':model,'photo_key':key,'shared_full_model_limit':limit,'zero_limit':limit==0})
        c.save();files.append(pdf)
    need(len(cell_records)==3072,'all actual cells/editions must be retained')
    write(args.out_root/'CELL_RENDER_RECORDS.json',cell_records)
    files.append(args.out_root/'CELL_RENDER_RECORDS.json')
    caption=('Actual constant-occlusion responses on two fixed potentially exposed developmental FFHQ photographs. '
             'Each measured native64pxcell is displayed without interpolation; black0 andgray128 replacements are separate. '
             'Delta=z_occluded−z_original, not error rate, probability, segmentation or causal reliance. Baseline display is the mathematical sigmoid of measuredlogit, not calibrated probability. '
             'A single symmetric scale permodel covers all512fullresponses acrossbothphotos/histories/fills; grayscale shows absolute magnitude and negative hatching. '
             'Native/history alignments differ. No morph splice/seam exists on these genuine photographs. '
             'Models/resolutions differ; no robustness ranking, utility or population claim. RankingNOT_QUALIFIED and its5falsealarmFAILs remain unchanged. '
             'SelfMAD demonstration choice was post-hoc; cases and allthree models fixed, all outcomes retained. '
             'Image source credits/URLs/licences and exact changed histories are in manifest. Private grant only; publication/likeness/consent remain unresolved.')
    manifest={'scope':'PRIVATE_MEASURED_RENDER_ONLY','release_sha256':sha(args.release),'config_sha256':sha(args.config),
              'result_pins':result_pins,'source_inputs':cfg['inputs'],'source_credits':cfg['source_credits'],
              'caption_en':caption,'page_mm':[WIDTH_MM,HEIGHT_MM],'minimum_font_pt':MIN_FONT,
              'map_scale_policy':'Shared per model ALL4inputs×2fills×64; no clipping/interpolation/smoothing; exact L0handledwithoutboost',
              'pages':summary,'source00010_pixels':False,'new_inference':False,'render_mode':cfg['render_mode'],
              'actual_print_QA':'REQUIRED_AFTER_RENDER; sourcechecks do not certify real PDF readability',
              'publication':'HOLD','files':{p.name:sha(p) for p in files}}
    write(args.out_root/'MANIFEST.json',manifest);write(args.out_root/'TEXT_LAYOUT_RECORD.json',texts)
    (args.out_root/'caption_en.txt').write_text(caption+'\n')
    print('VIS2_ACTUAL_MEASURED_PRIVATE_RENDER_COMPLETE; independent print/caption review still required')


if __name__=='__main__':main()
