"""VIS3 v2r1 private RGB/map render driver. Reuses the accepted VIS2 layout_v2 page
geometry/primitives verbatim (180x279.4 mm, 58 mm panels, min 8.2 pt, no interpolation,
one shared per-model scale over all 512 responses). Adapted only to the VIS3 v2r1 contract:
inputs are the four exact constructed single-morph images (42/56 x samephoto/crossphoto);
descriptive regional boundary-vs-surround means are printed as text; no causal/identity claim
and no anatomical seam claim is made on the page. CPU only; create-only output; publication HOLD.
Grant gates this source exactly like VIS2: pinned source manifest, pinned numeric postreviews
covering all three models, pinned full RESULT files, pinned constructed inputs."""
import argparse
import base64
import hashlib
import html
import importlib.metadata
import json
import math
import os
from pathlib import Path
import sys

MODELS=('selfmad_hrnet_w18','A','B')
INP=('42_samephoto','42_crossphoto','56_samephoto','56_crossphoto')
FILLS=(0,128)
BOUNDARY=(3,4,10,13)
SURROUND=(0,7,56,63)
MM=72/25.4
WIDTH_MM,HEIGHT_MM=180,279.4
EDGE_MM=58
MAP_X=(17,105)
MAP_Y=(100,173)
MIN_FONT=8.2
CREDITS={  # from construction INVENTORY, copied verbatim (rights recorded CC BY-NC 2.0)
 '42':'FFHQ 00042 host / Rebecca Brown "Shirtless, bearded Josh" donor for 56_crossphoto; CC BY-NC 2.0.',
 '56':'FFHQ 00056 host / RAFFI YOUREDJIAN "MANGAGAN-7" donor for 42_crossphoto; CC BY-NC 2.0.',
}
LABELS={'selfmad_hrnet_w18':'SelfMAD (release)','A':'Sb s403 (A)','B':'Sb s403 (B)'}
_ACTIVE_OUTPUT=None


def write(path,obj):
    path=Path(path)
    payload=(json.dumps(obj,indent=2,allow_nan=False)+'\n').encode('utf-8')
    with path.open('xb') as f:
        f.write(payload);f.flush();os.fsync(f.fileno())
    fd=os.open(str(path.parent),os.O_RDONLY|getattr(os,'O_DIRECTORY',0))
    try:os.fsync(fd)
    finally:os.close(fd)


def need(ok,message):
    if not ok:raise ValueError(message)


def sha(path):
    h=hashlib.sha256()
    with Path(path).open('rb') as f:
        for b in iter(lambda:f.read(1024*1024),b''):h.update(b)
    return h.hexdigest()


def finite(v):return type(v) in (float,int) and math.isfinite(v)


def validate_result(r,model,grant,config):
    """Fresh VIS3 full-512 contract; mirrors the admitted post-review checks, no plotting here."""
    need(r['model']==model and r['phase']=='full' and r['status']=='COMPLETE','full COMPLETE only')
    need(r['experiment']=='VIS3_CONTROLLED_SOFT_SPLICE_V2R1','wrong experiment')
    need(r['release_sha256']==grant['release_sha256'],'numeric ran under a different grant')
    need(r['construction_receipt_sha256']==grant['construction_receipt_sha256'],'construction provenance changed')
    need(r['actual_derived_roster_sha256']==grant['derivative_roster_sha256'],'roster changed')
    need(r['inputs_ids']==list(INP) and r['fills_uint8']==list(FILLS),'fixed input/fill roster changed')
    need(r['threshold'] is None and r['decision_flips'] is None,'no operational decision allowed in numeric')
    need(r['source_pixels_exported'] is False and r['maps_rendered'] is False,'numeric export flags mismatch')
    need(r['publication_allowed'] is False,'numeric claims publication')
    baseline=r['baseline_logits'];need(len(baseline)==4 and all(finite(x) for x in baseline),'bad baselines')
    got=sorted(set(r['baseline_logits']))==sorted(baseline)  # constant per input check via rows below
    rows=r['responses'];need(len(rows)==512,'complete512 responses required')
    values={};baselines_from_rows={}
    for row in rows:
        id,fill,cell=row['input_id'],row['fill_uint8'],row['cell']
        need(id in INP and type(fill) is int and fill in FILLS and type(cell) is int and 0<=cell<64,'foreign input/fill/cell')
        token=(id,fill,cell);need(token not in values,'duplicate response')
        need((row['row'],row['col'],row['native_y'],row['native_x'],row['native_area'])==(cell//8,cell%8,(cell//8)*64,(cell%8)*64,4096),'wrong native geometry')
        z0,z1,d=row['baseline_logit'],row['occluded_logit'],row['delta_logit']
        need(all(finite(x) for x in (z0,z1,d)),'nonfinite response')
        need(abs(d-(z1-z0))<=1e-6,'delta mismatch')
        values[token]=float(d);baselines_from_rows.setdefault(id,set()).add(z0)
        baselines_from_rows[id].add(z0)
    need(all(len(v)==1 and abs(list(v)[0]-baseline[INP.index(id)])<=1e-12 for id,v in baselines_from_rows.items()),'baseline rows disagree')
    # regional means recomputed from raw cells
    reg=r['regional_means'];need(len(reg)==8,'8 regional entries required')
    regress={}
    for entry in reg:
        need(entry['boundary_cells']==list(BOUNDARY) and entry['surround_cells']==list(SURROUND),'registered cells changed')
        inp,fill=entry['input_id'],entry['fill_uint8']
        mb=sum(values[(inp,fill,c)] for c in BOUNDARY)/4.0
        ms=sum(values[(inp,fill,c)] for c in SURROUND)/4.0
        need(abs(mb-entry['mean_boundary_delta_z'])<=1e-6 and abs(ms-entry['mean_surround_delta_z'])<=1e-6,'regional mean mismatch')
        regress[(inp,fill)]=(mb,ms)
    need(set(regress)=={(i,f) for i in INP for f in FILLS},'regional coverage')
    need(set(values)=={(i,f,c) for i in INP for f in FILLS for c in range(64)},'missing cells')
    # anchor and derived-baseline determinism blocks
    for blk,tag in ((r['anchor_controls'],'anchor'),(r['derived_baseline_checks'],'derived')):
        need(len(blk)==4 and all(e['z']==e['repeat_z']==e['literal_copy_z'] for e in blk),tag+' determinism broken')
    need(all(a['z']==a['reference_z'] for a in r['anchor_controls']),'anchor reference reproduction broken')
    limit=max(abs(x) for x in values.values())
    return {'values':values,'limit':limit,'baseline':dict(zip(INP,baseline)),'regional':regress}


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


def authorize(config_path,release_path,data_root,out_root):
    cfg=json.loads(Path(config_path).read_text());grant=json.loads(Path(release_path).read_text())
    need(grant['decision']=='GO_VIS3_PRIVATE_RGB_MAP_RENDER','new render grant required')
    need(grant['publication']=='HOLD' and grant['render_allowed'] is True,'private-only scope')
    need(grant['new_inference_allowed'] is False,'render must not score')
    need(grant['source_pixels_export_allowed'] is True and grant['constructed_input_render_allowed'] is True,'constructed-input render not granted')
    need(grant['config_sha256']==sha(config_path),'configuration changed')
    need(grant['models']==list(MODELS),'no selected model subset')
    need(grant['data_root']==str(Path(data_root).resolve()) and grant['out_root']==str(Path(out_root).resolve()),'staging/output scope differs')
    postreviews=grant['numeric_postreviews'];need(len(postreviews)==1,'exactly the admitted full numeric postreview required')
    for review in postreviews:
        need(sha(review['path'])==review['sha256'],'full numerical postreview changed')
        need(review['decision']=='GO_VIS3_FULL_NUMERIC','postreview decision changed')
    roster=json.loads((data_root/'DERIVED_INPUT_ROSTER.json').read_text())
    need(grant['derivative_roster_sha256']==sha(data_root/'DERIVED_INPUT_ROSTER.json'),'roster sha mismatch')
    mask_ok=json.loads(Path(config_path).read_text())  # nothing; roster below
    need({e['id'] for e in roster}==set(INP) and grant['inputs_ids']==list(INP),'input roster changed')
    for item in cfg['inputs']:
        need(item['id'] in INP and item['replica_name']==item['id']+'.png','foreign image')
        entry=[e for e in roster if e['id']==item['id']][0]
        need(Path(data_root/item['replica_name']).resolve()==Path(entry['path']).resolve() and sha(data_root/item['replica_name'])==entry['sha256']==item['sha256'],'constructed image differs from admitted roster')
    measured={};result_pins={}
    for entry in grant['full_result_roster']:
        p=Path(entry['canonical_full_result'])
        need(sha(p)==entry['sha256'],'full result hash changed')
        measured[entry['model']]=validate_result(json.loads(p.read_text()),entry['model'],grant,cfg)
        result_pins[entry['model']]=entry['sha256']
    need(set(measured)==set(MODELS),'three models required')
    need(cfg['render_mode']=='source_overlay' and cfg['map_interpolation']=='none','only measured native cells allowed')
    need(cfg['page_width_mm']==WIDTH_MM and cfg['page_height_mm']==HEIGHT_MM and cfg['photo_map_edge_mm']==EDGE_MM and cfg['minimum_font_pt']==MIN_FONT,'layout configuration differs from accepted VIS2 source')
    need(cfg['overlay_alpha']==0.45,'overlay alpha differs from accepted VIS2 config')
    need(importlib.metadata.version('reportlab')==cfg['render_runtime']['reportlab'],'render library changed')
    need(importlib.metadata.version('pillow')==cfg['render_runtime']['pillow'],'image library changed')
    need(str(Path(sys.executable).resolve())==str(Path(cfg['render_runtime']['python']).resolve()),'interpreter differs from pinned runtime')
    need(grant['source_manifest_sha256']==sha(Path(__file__).resolve().parent/'SHA256SUMS'),'renderer source manifest changed')
    base=Path(__file__).resolve().parent
    for line in (base/'SHA256SUMS').read_text().splitlines():
        h,name=line.split('  ',1);need(sha(base/name)==h,'renderer source changed')
    return cfg,grant,measured,result_pins


def _main():
    global _ACTIVE_OUTPUT
    ap=argparse.ArgumentParser()
    ap.add_argument('--config',required=True,type=Path)
    ap.add_argument('--release',required=True,type=Path)
    ap.add_argument('--data-root',required=True,type=Path)
    ap.add_argument('--out-root',required=True,type=Path)
    args=ap.parse_args();need(sys.flags.isolated,'python -I required')
    cfg,grant,measured,result_pins=authorize(args.config,args.release,args.data_root,args.out_root)
    args.out_root.mkdir(parents=True,exist_ok=False)
    _ACTIVE_OUTPUT=args.out_root
    from reportlab.pdfgen import canvas
    from reportlab.pdfbase import pdfmetrics
    from reportlab.pdfbase.ttfonts import TTFont
    from reportlab.lib.utils import ImageReader
    from reportlab.lib.colors import Color
    need(sha(cfg['fonts']['regular'])==cfg['fonts']['regular_sha256'] and sha(cfg['fonts']['bold'])==cfg['fonts']['bold_sha256'],'font changed')
    pdfmetrics.registerFont(TTFont('Body',cfg['fonts']['regular']))
    pdfmetrics.registerFont(TTFont('Bold',cfg['fonts']['bold']))
    width,height=WIDTH_MM*MM,HEIGHT_MM*MM
    image_bytes={item['id']:(args.data_root/item['replica_name']).read_bytes() for item in cfg['inputs']}
    texts=[];files=[];summary=[];cell_records=[]
    for gray in (False,True):
        edition='gray_sign_hatching' if gray else 'signed_color'
        pdf=args.out_root/(edition+'.pdf')
        c=canvas.Canvas(str(pdf),pagesize=(width,height),pageCompression=1,invariant=1)
        c.setTitle('VIS3 private constructed soft-splice response; no publication clearance');c.setAuthor('')
        for model in MODELS:
            data=measured[model];limit=data['limit'];baseline=data['baseline'];regvals=data['regional']
            for inp in INP:
                sv=[f'<svg xmlns="http://www.w3.org/2000/svg" width="180mm" height="279.4mm" viewBox="0 0 {width} {height}">',
                    '<title>Private measured constructed-input response; not causal attribution</title>',f'<rect width="{width}" height="{height}" fill="white"/>']
                def text(x,y,s,size=MIN_FONT,bold=False):
                    font='Bold' if bold else 'Body';x*=MM;y*=MM
                    need(size>=MIN_FONT and x+pdfmetrics.stringWidth(s,font,size)<=width-7*MM,'text overflow/minfont; repair layout only')
                    need(y>=size and y<height-3*MM,'text outside page')
                    c.setFont(font,size);c.setFillColor(Color(.10,.17,.21));c.drawString(x,height-y,s)
                    sv.append(f'<text x="{x}" y="{y}" font-family="DejaVu Sans,sans-serif" font-size="{size}" font-weight="{700 if bold else 400}" fill="#192b36">{html.escape(s)}</text>')
                    texts.append({'edition':edition,'model':model,'input_id':inp,'text':s,'font':size})
                def photo(x,y):
                    c.drawImage(ImageReader(str(args.data_root/(inp+'.png'))),x*MM,height-(y+EDGE_MM)*MM,width=EDGE_MM*MM,height=EDGE_MM*MM,mask='auto')
                    s=base64.b64encode(image_bytes[inp]).decode()
                    sv.append(f'<image x="{x*MM}" y="{y*MM}" width="{EDGE_MM*MM}" height="{EDGE_MM*MM}" href="data:image/png;base64,{s}"/>')
                def rectangle(x,y,w,h,rgb,alpha=1):
                    c.saveState();c.setFillColor(Color(*rgb));c.setFillAlpha(alpha);c.rect(x*MM,height-(y+h)*MM,w*MM,h*MM,fill=1,stroke=0);c.restoreState()
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
                text(8,8,'Ten sam host. Sklejka konstrukcyjna; zasłaniamy mały fragment.',11.1,True)
                text(8,14,f'{LABELS[model]} | wejście {inp} | rzeczywiste pomiary, nie mapa przyczynowa',8.3)
                photo(MAP_X[0],24);z=baseline[inp]
                text(MAP_X[0],88,f'Wynik morph (z): {z:+.3f}',9.4,True)
                text(MAP_X[1],24.5,'Zmierzone względné średnie zmian (opisowe)',8.3,True)
                for i,(fill,tag) in enumerate(zip(FILLS,('czernią','szarością'))):
                    mb,ms=regvals[(inp,fill)]
                    text(MAP_X[1],30+i*11,f'zasłonięcie {tag}: szew {mb:+.3f} / otoczenie {ms:+.3f}',8.2)
                text(MAP_X[1],56,'średnia 4 oddzielnych łatek 64x64; nie symultaniczne',8.2)
                text(MAP_X[1],62,'Zasłaniamy 64x64 px; poniżej zmiana z.',8.3)
                text(8,93,'Poniżej: zmiana z po zasłonięciu wskazanego kwadratu 64 x 64 px.',8.3)
                for fill,y,title in [(0,MAP_Y[0],'Zasłonięcie czernią (0/255)'),(128,MAP_Y[1],'Zasłonięcie szarością (128/255)')]:
                    text(MAP_X[0],y-4,title,8.8,True)
                    photo(MAP_X[0],y)
                    for cell in range(64):
                        val=data['values'][inp,fill,cell];xx=MAP_X[0]+(cell%8)*EDGE_MM/8;yy=y+(cell//8)*EDGE_MM/8
                        rectangle(xx,yy,EDGE_MM/8,EDGE_MM/8,color(val,limit,gray),0.0 if limit==0 else cfg['overlay_alpha'])
                        if gray and val<0:hatch(xx,yy,f'{fill}_{inp}_{cell}')
                        cell_records.append({'edition':edition,'model':model,'input_id':inp,'fill':fill,'cell':cell,
                                             'delta_logit':val,'limit':limit,'normalized':normalized(val,limit),'color_RGB':color(val,limit,gray),
                                             'negative_hatching':bool(gray and val<0),'overlay_alpha':0.0 if limit==0 else cfg['overlay_alpha'],
                                             'x_mm':xx,'y_mm':yy,'edge_mm':EDGE_MM/8})
                if limit==0:
                    rectangle(12,237,156,3,(1,1,1),1)
                    text(12,245,'Wszystkie zmierzone zmiany wynoszą 0. Nie dodano kontrastu.',8.3,True)
                else:
                    for i in range(64):
                        value=limit*i/63 if gray else -limit+2*limit*i/63
                        rectangle(12+i*156/64,237,156/64,3,color(value,limit,gray),1)
                    ticks=f'0 → {limit:.3g}' if gray else f'{-limit:.3g}  /  0  /  {limit:.3g}'
                    text(12,245,ticks+' | wspólna skala 512 pomiarów/model; modele mają różne skale.',8.2)
                if gray:
                    text(8,249,'Szara nakładka: wielkość zmiany; kreskowanie: obniżenie wyniku morph.',8.2)
                text(8,253,'Maska przejścia: zarejestrowany fallback-ellipse; nie zweryfikowana anatomicznie szew.',8.2)
                text(8,257,'samephoto: przetworzona konstrukcja, nie no-op; literal copy = no-op.',8.2)
                text(8,261,'Nie wnioskujemy o tożsamości, anatomii ani benchmarku; pozycje i treści skonfudowane.',8.2)
                text(8,267,'Dwa hosty FFHQ (00042, 00056); donor/hosts zapisane w manifestach.',8.2)
                if inp=='42_crossphoto' or inp=='56_crossphoto':
                    Khi='42' if inp.startswith('42') else '56';Dhi='56' if inp.startswith('42') else '42'
                    text(8,272,CREDITS[Khi]+' Donor: '+CREDITS[Dhi],8.2)
                else:
                    text(8,272,CREDITS['42' if inp.startswith('42') else '56'],8.2)
                text(8,275,'PRIVATE RESEARCH PREVIEW - NOT PUBLICATION CLEARED',8.2,True)
                c.showPage();sv.append('</svg>')
                svg=args.out_root/f'{edition}_{model}_{inp}.svg';svg.write_text('\n'.join(sv));files.append(svg)
                summary.append({'edition':edition,'model':model,'input_id':inp,'shared_full_model_limit':limit,'zero_limit':limit==0})
        c.save();files.append(pdf)
    need(len(cell_records)==3072,'all actual cells/editions must be retained')
    write(args.out_root/'CELL_RENDER_RECORDS.json',cell_records)
    files.append(args.out_root/'CELL_RENDER_RECORDS.json')
    caption=('Actual constant-occlusion responses of three fixed models on four constructed single-morph inputs '
             '(hosts 00042/00056 x samephoto/crossphoto, actual fallback-ellipse mixing mask). Each measured native 64 px cell '
             'displayed without interpolation; black 0 and gray 128 replacements separate. Delta=z_occluded - z_baseline; not error rate, '
             'probability, segmentation, or causal reliance. A single symmetric scale per model covers all 512 full responses across '
             'the four inputs and both fills; no clipping or smoothing. Red: hiding the patch raises z; blue: lowers z. The top panel '
             'shows the constructed input and its baseline z; measured mean boundary [3,4,10,13] vs surround [0,7,56,63] cell deltas are '
             'printed instead of a second photo column (means of four separate interventions, not simultaneous region removal). '
             'samephoto is processed content, not a noop; literal copy is the noop. The transition mask is a registered fallback ellipse, '
             'not anatomically verified seam geometry. Two hosts only; position and content confounded; no identity, anatomy, or benchmark claim. '
             'Image rights CC BY-NC 2.0; PRIVATE RESEARCH PREVIEW, publication clearance pending.')
    manifest={'scope':'PRIVATE_MEASURED_RENDER_ONLY','release_sha256':sha(args.release),'config_sha256':sha(args.config),
              'result_pins':result_pins,'roster_sha256':grant['derivative_roster_sha256'],
              'source_inputs':cfg['inputs'],'credits':CREDITS,
              'caption_en':caption,'page_mm':[WIDTH_MM,HEIGHT_MM],'minimum_font_pt':MIN_FONT,
              'map_scale_policy':'Shared per model ALL4inputs x 2fills x 64; no clipping/interpolation/smoothing; exact 0 handled without boost',
              'pages':summary,'new_inference':False,'render_mode':cfg['render_mode'],
              'actual_print_QA':'REQUIRED_AFTER_RENDER; source checks do not certify real PDF readability',
              'publication':'HOLD','reviewer_limitation':'Single-agent continuation review (MAIN); numeric postreview and this renderer reviewed within the same agent lineage.',
              'files':{p.name:sha(p) for p in files}}
    write(args.out_root/'MANIFEST.json',manifest);write(args.out_root/'TEXT_LAYOUT_RECORD.json',texts)
    (args.out_root/'caption_en.txt').write_text(caption+'\n')
    need(len(files)==15 and len(summary)==12,'complete artifact/edition count required')
    write(args.out_root/'COMPLETE.json',{'status':'COMPLETE','manifest_sha256':sha(args.out_root/'MANIFEST.json'),
                                      'pdf_files':2,'svg_files':12,'cell_records':len(cell_records),
                                      'scope':'Private measured render only; actual print/caption review still required'})
    print('VIS3_ACTUAL_MEASURED_PRIVATE_RENDER_COMPLETE; independent print/caption review still required')


def main():
    global _ACTIVE_OUTPUT
    _ACTIVE_OUTPUT=None
    try:return _main()
    except BaseException as exc:
        if _ACTIVE_OUTPUT is not None:
            try:(_ACTIVE_OUTPUT/'FAILED.txt').write_text(repr(exc)[:2000]+'\n')
            except OSError:pass
        raise


if __name__=='__main__':main()
