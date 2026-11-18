import pathlib,json,hashlib,sys
B=pathlib.Path(__file__).resolve().parent
R=B.parents[2]
def read(n): return json.loads((B/n).read_text())
pins=read('SOURCE_PINS.json')
for p,h in pins.items():
    assert hashlib.sha256((R/p).read_bytes()).hexdigest()==h, 'source drift: '+p
x=read('BRANCHES.json'); expected=['SbFM','GX','SbMR','SbM','Sb512','SbMR512','Sbc','DINOv3']
assert x['fixed_order']==expected
assert [b['arm'] for b in x['branches']]==expected
for b in x['branches']:
    assert b['fresh_seeds']==list(range(413,418))
    assert not b['selected'] and b['dispatch']=='HOLD'
    if b['recipe']: assert b['recipe']['final']=='last' and b['recipe']['steps']==6250 and b['recipe']['warmstart'] is False
t=read('TASK_TEMPLATES.json')
assert len({i['task'] for i in t})==len(t)
assert len(t)==sum(b['minimum_role_tasks'] for b in x['branches'])
for b in x['branches']:
    for seed in range(413,418):
        assert {(z['role'],z['producer_arm']) for z in t if z['branch']==b['arm'] and z['seed']==seed}=={tuple(r) for r in b['roles_at_every_seed']}
d=read('DISPATCH_TEMPLATE.json')
hold=[k for k,v in d.items() if v is None]
assert d['sealed_read_authorized'] is False
print(json.dumps({'template_integrity':'PASS','dispatch':'HOLD','unresolved_fields':hold,'source_pin_count':len(pins),'conditional_task_count':len(t),'scientific_admission':False},indent=2))
sys.exit(2 if hold or d['status']=='HOLD' else 0)
