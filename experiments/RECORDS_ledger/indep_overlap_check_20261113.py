import csv,re,pathlib,collections
T7=pathlib.Path('/mnt/t7/smad_next')
def rows(p): return list(csv.DictReader(open(p)))
pool={r['pid']:r for r in rows(T7/'AR1/pool.csv')}
ar1={}
for f in ('manifest.csv','manifest_extra.csv','manifest_extra2.csv'):
    for r in rows(T7/'AR1'/f): ar1[r['id']]=r
af0={r['id']:r for r in rows(T7/'AF0/manifest.csv')}
def pkey(path):
    p=pathlib.Path(path); m=re.search(r'/(feret|frgc)/(\d+)/',path)
    if not m: return 'other:'+path
    st=p.stem
    if m.group(1)=='frgc' and '_' not in st:
        NOMAP.add(path); return 'frgc-unmapped:'+path
    return f"{m.group(1)}:{st.split('_',1)[1] if m.group(1)=='frgc' else st}"
def pers(path):
    m=re.search(r'/(feret|frgc)/(\d+)/',path); return f"{m.group(1)}:{m.group(2)}" if m else None
unres=collections.Counter()
NOMAP=set()
def res(i):
    b=re.sub(r'(__bg|__face|_fm\d+|_amsl\d+)+$','',i)
    m=re.fullmatch(r'ar1_(\d+)',b)
    if m:
        r=ar1[m.group(1)]; P={r['p1'],r['p2']}; Ph=set()
        for t in ('tem1','tem2'):
            if r[t]: Ph.add(pkey(r[t])); P.add(pers(r[t]))
        if not r['tem1'] and not r['tem2']: Ph.add(pkey(r['path']))
        return P-{None},Ph
    m=re.fullmatch(r'sp2?_(\w+?)_(?:opencv|facemorpher)_(feret|frgc)_(\d+)',b)
    if m:
        h=f"{m.group(2)}:{m.group(3)}"; P=pool[h]
        # conservative: every rung gets host, partner, and all three photos H, S, B
        g=m.group(1)
        if g in ('S4','R2w4','R4'): return {h,P['B_pid']},{pkey(P['H']),pkey(P['B'])}
        if g in ('S3','R2w'): return {h},{pkey(P['H']),pkey(P['S'])}
        return {h},{pkey(P['H'])}
    m=re.fullmatch(r'sm1h_(feret|frgc)_(\d+)_h[AB]',b)
    if m:
        h=f"{m.group(1)}:{m.group(2)}"; P=pool[h]
        return ({h},{pkey(P['H'])}) if i.endswith('hA') else ({P['B_pid']},{pkey(P['B'])})
    m=re.fullmatch(r'((?:train|val)_\w+?_\d+)(_half[AB])?',b)
    if m and m.group(1) in af0:
        r=af0[m.group(1)]; return {r['pid_A'],r['pid_B']},{pkey(r['A']),pkey(r['B'])}
    unres[re.sub(r'\d+','N',b)]+=1; return set(),set()
TP,TPh=set(),set()
for r in rows(T7/'PN1/fs_tree/pn1/data/manifests/train_Sb.csv'):
    p,ph=res(r['id']); TP|=p; TPh|=ph
print('train Sb persons',len(TP),'photos',len(TPh),'unresolved',dict(unres))
unres.clear()
n=0;hitP=0;hitPh=0;hosts=set()
for r in rows(T7/'PN1/fs_tree/pn1/data/manifests/pn1_eval.csv'):
    if r['fam'] not in ('ladder','splice'): continue
    n+=1; p,ph=res(r['id']); p|={r['host']} if r['host'] else set()
    hitP+=bool(p&TP); hitPh+=bool(ph&TPh); hosts.add(r['host'])
print('eval ladder+splice rows',n,'hosts',len(hosts),'rows sharing a training person',hitP,'rows sharing a training photo',hitPh,'unresolved',dict(unres))
# positive control: dev ladder rows as "training"

print('frgc photos without a raw name (person check only):',len(NOMAP), sorted(NOMAP)[:2])
role={r['pid']:r['role'] for r in rows('/home/narolski/smad-next/experiments/PN1_protocol-network-first-tests/split/ladder_split.csv')}
c=collections.Counter(); ex=collections.defaultdict(list)
for r in rows(T7/'PN1/fs_tree/pn1/data/manifests/pn1_eval.csv'):
    if r['fam'] not in ('ladder','splice'): continue
    p,ph=res(r['id']); p|={r['host']}
    sp=p&TP; sph=ph&TPh
    if sp or sph:
        k=(r['role'],role.get(r['host']),r['fam'],r['rung'],'P' if sp else '', 'Ph' if sph else '')
        c[k]+=1
        if len(ex[k])<2: ex[k].append((r['id'],sorted(sp)[:3],sorted(sph)[:2]))
for k,v in c.most_common(30): print(v,k,ex[k])
print('----')
hits=collections.defaultdict(list)
tests={h for h,r in role.items() if r=='test'}
for r in rows(T7/'PN1/fs_tree/pn1/data/manifests/train_Sb.csv'):
    p,ph=res(r['id'])
    for q in p&tests: hits[q].append((r['id'],r['kind'],r['path']))
print('test persons in Sb training rows:',len(hits))
for q in sorted(hits)[:6]: print(q,len(hits[q]),hits[q][:3])
kinds=collections.Counter(k for v in hits.values() for _,k,_ in v); print(kinds)
print('---- positive control')
E=rows(T7/'AB1/x/manifests/ab1x_eval.csv')
def lad(r): return r['fam']=='ladder' or r['id'].startswith('sp2_')
DP,DPh=set(),set()
for r in E:
    if lad(r) and role.get(r['host'])=='dev':
        p,ph=res(r['id']); DP|=p|{r['host']}; DPh|=ph
unres.clear(); n=f=0; famc=collections.Counter()
for r in E:
    if role.get(r['host'])=='test':
        n+=1; p,ph=res(r['id']); p|={r['host']}
        f+=bool((p&DP) or (ph&DPh)); famc[r['fam']]+=1
print('test-host rows',n,'flagged',f,'by fam',dict(famc),'unresolved',sum(unres.values()),dict(list(unres.items())[:5]))
th=collections.defaultdict(bool)
for r in E:
    if role.get(r['host'])=='test':
        p,ph=res(r['id']); p|={r['host']}
        th[r['host']] |= bool((p&DP) or (ph&DPh))
print('test hosts',len(th),'touching dev',sum(th.values()))
