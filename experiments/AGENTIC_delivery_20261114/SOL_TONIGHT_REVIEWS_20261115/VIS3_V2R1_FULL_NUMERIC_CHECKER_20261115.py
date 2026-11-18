'''VIS3 v2r1 FULL numeric post-review - fresh independent checker (does NOT import numeric_worker).
Reads only released JSONs on /mnt/t7 + repo control files; recomputes every reported aggregate from raw responses.'''
import json, hashlib, math
R='/mnt/t7/smad_next/VIS3/20261115/v2r1/numeric/full'
S='/mnt/t7/smad_next/VIS3/20261115/v2r1/numeric/smoke'
C='/mnt/t7/smad_next/VIS3/20261115/v2r1/constructed'
ROOT='/home/narolski/smad-next/experiments/AGENTIC_delivery_20261114/SOL_SEAM_TONIGHT_20261115'
REV='/home/narolski/smad-next/experiments/AGENTIC_delivery_20261114/SOL_TONIGHT_REVIEWS_20261115'
sha=lambda p: hashlib.sha256(open(p,'rb').read()).hexdigest()
fails=[]
def chk(name, ok, detail=''):
    print(('PASS ' if ok else 'FAIL ')+name+(' :: '+detail if detail else ''))
    if not ok: fails.append(name+(' :: '+detail if detail else ''))

MODELS=['selfmad_hrnet_w18','A','B']
INP=['42_samephoto','42_crossphoto','56_samephoto','56_crossphoto']
FILLS=[0,128]; BOUNDARY=[3,4,10,13]; SURROUND=[0,7,56,63]
TOL=1e-6

# 0) provenance pins
rel=f'{ROOT}/ROOT_NUMERIC_FULL_RELEASE.json'
grant=json.load(open(rel))
chk('grant file sha == external pin 342a1715...', sha(rel)=='342a171554c08a6b7667b0bd9f46d6ca1bd65a01d193d695e860abd4862edb29')
chk('grant review sha c0234ae matches repo file', sha(REV+'/VIS3_V2R1_SOURCE_DELTA_REVIEW_20261115.md')==grant['independent_review_sha256'])
HASHES={'inventory':'d67d18e3193887ea085e9cd7be95054bb2bb946fde655e9d5e158a8f2ae4aecf',
 'prereg':'636428eb3a2db72f287ee8eadbb2fd54f2dcd1606d93e309d15b0d9d9aa88e57',
 'construction_receipt':'27fb7fbf4a4df542dbe5f5abeb6114bd7e8529d9c2ea7780c1dca5cc44cd8731',
 'input_admission':'a83ed75db4a60ce30973e533eb49c7c451efe1decaef72f59ef364850e793026',
 'roster':'ef50ff6893e01aed01a39cc55cc8b550fe22a846a9e299480f927b7685916365',
 'smoke_postreview':'84ecb026068243323a4191cdd9f041ccedf3647072dbf0f99b127c411da3491e'}
chk('grant: reviewer/decision fields', grant['decision']=='GO_VIS3_PRIVATE_NUMERIC_FULL' and grant['phase']=='full' and grant['models']==MODELS)

# 1) constructed dir: actual hashes == SHA256.json == roster
cs=json.load(open(f'{C}/SHA256.json'))
badc=[f for f,h in cs.items() if f!='STARTED.json' and sha(f'{C}/{f}')!=h]
chk('constructed/SHA256.json all match', not badc, str(badc))
roster=json.load(open(f'{C}/DERIVED_INPUT_ROSTER.json'))
chk('roster sha matches pinned', sha(f'{C}/DERIVED_INPUT_ROSTER.json')==HASHES['roster'])
chk('roster entries sha==constructed hashes', all(r['sha256']==cs[r['path'].split('/')[-1]] for r in roster))
chk('roster ids/conditions/host-donor logic', sorted(r['id'] for r in roster)==sorted(INP)
    and all(r['id']==r['host_photo'].lstrip('0')+'_'+r['condition'] for r in roster)
    and all((r['donor_photo']==r['host_photo']) == (r['condition']=='samephoto') for r in roster)
    and sorted(r['condition'] for r in roster)==['crossphoto','crossphoto','samephoto','samephoto'])
chk('receipt sha pinned', sha(f'{C}/CONSTRUCTION_RECEIPT.json')==HASHES['construction_receipt'])
chk('alpha sha in constructed SHA256 matches', cs['actual_used_alpha.npy']==sha(f'{C}/actual_used_alpha.npy'))

# 2) per-model RESULT verification
summary={}
for m in MODELS:
    d=json.load(open(f'{R}/{m}/RESULT.json'))
    chk(f'{m}: status/phase/model', d['status']=='COMPLETE' and d['phase']=='full' and d['model']==m)
    # digests
    sd=json.load(open(f'{R}/{m}/SHA256.json'))
    bad=[f for f,h in sd.items() if sha(f'{R}/{m}/{f}')!=h]
    chk(f'{m}: SHA256.json of outputs match', not bad, str(bad))
    # provenance snapshots in RESULT
    a=d['authority_snapshots']
    for k,pin in [('root_release_sha256','342a171554c08a6b7667b0bd9f46d6ca1bd65a01d193d695e860abd4862edb29'),
                  ('inventory_sha256',HASHES['inventory']),('source_manifest_sha256','4aa997c961f65487d7cf46fd9a9629760adf643c2cb04411a8f8ea4945b666c5'),
                  ('construction_receipt_sha256',HASHES['construction_receipt']),('constructed_input_admission_sha256',HASHES['input_admission']),
                  ('derivative_roster_sha256',HASHES['roster']),('smoke_postreview_sha256',HASHES['smoke_postreview'])]:
        chk(f'{m}: snapshot {k}', a[k]==pin)
    chk(f'{m}: snapshot source review sha == grant', a['independent_source_review_sha256']==grant['independent_review_sha256'])
    # responses: completeness and geometry
    reps=d['responses']
    keys=[(r['input_id'],r['fill_uint8'],r['cell']) for r in reps]
    chk(f'{m}: 512 responses', len(reps)==512, str(len(reps)))
    chk(f'{m}: no duplicate keys', len(set(keys))==len(keys))
    want=set((i,f,c) for i in INP for f in FILLS for c in range(64))
    chk(f'{m}: complete 4x2x64 grid', set(keys)==want, str(len(want-set(keys)))+' missing')
    geo=[r for r in reps if not (r['row']==r['cell']//8 and r['col']==r['cell']%8 and r['native_x']==r['col']*64 and r['native_y']==r['row']*64 and r['native_area']==4096)]
    chk(f'{m}: geometry consistent (row/col/x/y/area)', not geo, str(geo[:2]))
    # delta consistency
    bad=[r for r in reps if abs((r['occluded_logit']-r['baseline_logit'])-r['delta_logit'])>TOL]
    chk(f'{m}: delta_logit == occluded-baseline (all rows)', not bad, str(len(bad)))
    # finite
    chk(f'{m}: all logits finite', all(math.isfinite(r[k]) for r in reps for k in ('baseline_logit','occluded_logit','delta_logit')))
    # baseline per input constant
    bl={}
    okb=True
    for i in INP:
        vals=sorted({r['baseline_logit'] for r in reps if r['input_id']==i})
        okb &= len(vals)==1
        bl[i]=vals[0]
    chk(f'{m}: single baseline logit per input', okb)
    chk(f'{m}: baseline_logits block == per-input constants', all(abs(a-b)<1e-12 for a,b in zip([bl[i] for i in INP], d['baseline_logits'])))
    # regional means recomputed
    badr=[]
    for reg in d['regional_means']:
        rows=[r['delta_logit'] for r in reps if r['input_id']==reg['input_id'] and r['fill_uint8']==reg['fill_uint8'] and r['cell'] in BOUNDARY]
        rows2=[r['delta_logit'] for r in reps if r['input_id']==reg['input_id'] and r['fill_uint8']==reg['fill_uint8'] and r['cell'] in SURROUND]
        mb=sum(rows)/len(rows); ms=sum(rows2)/len(rows2)
        if abs(mb-reg['mean_boundary_delta_z'])>TOL or abs(ms-reg['mean_surround_delta_z'])>TOL: badr.append(reg)
        if reg['boundary_cells']!=BOUNDARY or reg['surround_cells']!=SURROUND: badr.append(reg)
    chk(f'{m}: all 8 regional means recomputed from raw cells', len(d['regional_means'])==8 and not badr, f'{len(d["regional_means"])} regions, bad={len(badr)}')
    # anchor + baseline controls
    ancx=d['anchor_controls']
    chk(f'{m}: 4 anchor controls, z==repeat==literal==reference', len(ancx)==4 and all(a['z']==a['repeat_z']==a['literal_copy_z']==a['reference_z'] for a in ancx))
    dbc=d['derived_baseline_checks']
    chk(f'{m}: 4 derived baselines, z==repeat==literal', len(dbc)==4 and all(b['z']==b['repeat_z']==b['literal_copy_z'] for b in dbc) and all(abs(b['z']-bl[b['input_id']])<1e-12 for b in dbc))
    # scope flags
    chk(f'{m}: scope flags (no render/no export/no publication/no threshold)', d['maps_rendered'] is False and d['source_pixels_exported'] is False and d['publication_allowed'] is False and d['threshold'] is None and d['decision_flips'] is None)
    reg={ (r['input_id']+'|fill'+str(r['fill_uint8'])):(r['mean_boundary_delta_z']-r['mean_surround_delta_z']) for r in d['regional_means']}
    summary[m]={'n':len(reps),'anchors':[a['z'] for a in ancx],'baselines':bl,'reg_boundary_minus_surround':reg}

# 3) cross-model smoke digests consistency: smoke RESULT shas match smoke_postreview
sp=json.load(open(REV+'/VIS3_V2R1_SMOKE_POSTREVIEW_20261115.json'))
chk('smoke postreview decision/roster', sp['decision']=='GO_VIS3_FULL_NUMERIC' and sp['models']==MODELS and sp['generated_regional_indexing_verified'] is True)
for m in MODELS:
    got=sha(f'{S}/{m}/RESULT.json')
    chk(f'{m}: admitted smoke RESULT sha matches', got==sp['smoke_result_sha256'][m], got)

# 4) descriptive cross-model sense check (no selection): print summary
print('\n=== SUMMARY (descriptive, no claims) ===')
print(json.dumps(summary, indent=1))
print('\nVERDICT:', 'PASS' if not fails else 'FAIL - '+str(len(fails))+' failed checks')
for f in fails: print('  FAILED:', f)
