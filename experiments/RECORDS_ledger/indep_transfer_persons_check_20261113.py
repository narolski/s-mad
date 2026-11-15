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
E=rows(T7/'AB1/x/manifests/ab1x_eval.csv')
c=collections.Counter(); hit=collections.Counter(); un=collections.Counter()
for r in E:
    i=re.sub(r'^bref_','',r['id']); i=re.sub(r'__(replay_attack|msu_mfsd|oulu_npu|casia_fasd|lfw_calfw|cfp_ff|agedb_30)$','',i)
    key=(r['fam'],r['rung'] if r['fam'] in ('border','ladder','splice') else '')
    n0=sum(unres.values()); p,ph=res(i); 
    if sum(unres.values())>n0: un[key]+=1
    h={r['host']} if re.match(r'(feret|frgc):',r['host'] or '') else set()
    p=p|h; c[key]+=1; hit[key]+=bool(p&TP or ph&TPh)
for k in sorted(c): 
    if hit[k] or un[k]: print(k,'rows',c[k],'share person/photo with train_Sb',hit[k],'unresolved',un[k])
print('total rows',sum(c.values()),'sharing',sum(hit.values()))
