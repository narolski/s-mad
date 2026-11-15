import csv, glob, numpy as np, collections
from scipy.stats import spearmanr, mannwhitneyu
it=list(csv.DictReader(open('/mnt/t7/smad_next/FZ2/read_addon_items.csv')))
th={}; sd={}
for f in glob.glob('/mnt/t7/smad_next/DG1/gen/addon_s*/out_addon_s*/addon_s*/gen_rows.csv'):
    for r in csv.DictReader(open(f)):
        th[(r['pool'],r['name'])]=float(r['theta_xT']) if r['theta_xT'] else np.nan
        sd[(r['pool'],r['name'])]=float(r['std01']) if r['std01'] else np.nan
for r in it:
    parts=r['id'].split('/'); k=(parts[-2],parts[-1]); r['theta']=th.get(k,np.nan); r['std01']=sd.get(k,np.nan)
print('theta missing', sum(np.isnan(r['theta']) for r in it if r['rung'] in('SAME','X')))
def auc(pos,neg):
    pos=np.asarray(pos,float); neg=np.asarray(neg,float)
    pos=pos[~np.isnan(pos)]; neg=neg[~np.isnan(neg)]
    return mannwhitneyu(pos,neg).statistic/(len(pos)*len(neg))
def sel(rung,steps='20',**kw):
    out=[r for r in it if r['rung']==rung and r['steps']==steps]
    for k,v in kw.items(): out=[r for r in out if r[k]==v]
    return out
def col(rs,c): return np.array([float(r[c]) for r in rs])
X=sel('X'); S=sel('SAME'); R=sel('REC'); F1=[r for r in sel('FRESH') if r['key']=='FRESH1_20']; F2=[r for r in sel('FRESH') if r['key']=='FRESH2_20']
print('keys FRESH', collections.Counter(r['key'] for r in it if r['rung']=='FRESH'))
print('repro s401 X vs SAME', auc(col(X,'smdd_s401'),col(S,'smdd_s401')))
print('repro release X vs SAME', auc(col(X,'release_fe_vitl14'),col(S,'release_fe_vitl14')))
print('repro P_XS X vs SAME', auc(col(X,'clip_mad|P_XS'),col(S,'clip_mad|P_XS')))
print('repro D_SR FRESH1 vs REC', auc(col(F1,'clip_mad|D_SR'),col(R,'clip_mad|D_SR')))
print('repro s401 SAME vs FRESH1', auc(col(S,'smdd_s401'),col(F1,'smdd_s401')))
# platform x db
for db in ['frgc','feret']:
  for pl in ['athena','rented']:
    x=[r for r in X if r['db']==db and r['platform']==pl]; s=[r for r in S if r['db']==db and r['platform']==pl]
    if x: print('P_XS A0',db,pl,len(x),round(auc(col(x,'clip_mad|P_XS'),col(s,'clip_mad|P_XS')),3),'s401',round(auc(col(x,'smdd_s401'),col(s,'smdd_s401')),3), 'D_SR F1vR', round(auc(col([r for r in F1 if r['db']==db and r['platform']==pl],'clip_mad|D_SR'),col([r for r in R if r['db']==db and r['platform']==pl],'clip_mad|D_SR')),3))
# theta
tX=col(X,'theta'); tS=col(S,'theta')
print('theta median X',np.nanmedian(tX),'SAME',np.nanmedian(tS),'AUC theta X vs SAME',auc(tX,tS))
pX=col(X,'clip_mad|P_XS'); pS=col(S,'clip_mad|P_XS')
print('spearman P_XS~theta within X',spearmanr(tX,pX,nan_policy='omit')[0],'within SAME',spearmanr(tS,pS,nan_policy='omit')[0])
dX=col(X,'d'); dS=col(S,'d')
print('spearman theta~d within X',spearmanr(tX,dX)[0],'SAME',spearmanr(tS,dS)[0], 'AUC d X vs SAME', auc(dX,dS))
def strat(vx,vs,px,ps,nq=5):
    allv=np.concatenate([vx,vs]); qs=np.nanquantile(allv,np.linspace(0,1,nq+1)); num=den=0; out=[]
    for i in range(nq):
        lo,hi=qs[i],qs[i+1]
        mx=(vx>=lo)&((vx<hi) if i<nq-1 else (vx<=hi)); ms=(vs>=lo)&((vs<hi) if i<nq-1 else (vs<=hi))
        if mx.sum() and ms.sum():
            a=auc(px[mx],ps[ms]); w=mx.sum()*ms.sum(); num+=a*w; den+=w; out.append((int(mx.sum()),int(ms.sum()),round(a,3)))
    return num/den,out
print('P_XS stratified by d', strat(dX,dS,pX,pS))
print('P_XS stratified by theta', strat(tX,tS,pX,pS))
for c in ['lapvar_box','png_bytes','asym_box','std01']:
    vx=col(X,c); vs=col(S,c); a=auc(vx,vs)
    print(c,'X vs SAME',round(a,3),'P_XS strat',strat(vx,vs,pX,pS)[0].round(3) if False else round(strat(vx,vs,pX,pS)[0],3), 'spearman with P_XS in SAME', round(spearmanr(vs,pS)[0],3), 'in X', round(spearmanr(vx,pX)[0],3))
    vx=col(X,c); vs=col(S,c); 
    print('   s401 strat by',c, round(strat(vx,vs,col(X,'smdd_s401'),col(S,'smdd_s401'))[0],3))
# pipeline baselines for noise-only contrasts
NS=sel('NOISES'); SS=sel('SEMS'); NX=sel('NOISEX')
for name,A,B in [('FRESH1 vs REC',F1,R),('FRESH1 vs FRESH2',F1,F2),('NOISES vs REC',NS,R),('SEMS vs REC',SS,R),('SAME vs FRESH1',S,F1),('SAME vs REC',S,R),('X vs REC',X,R)]:
    print(name, {c:round(max(auc(col(A,c),col(B,c)),1-auc(col(A,c),col(B,c))),3) for c in ['png_bytes','lapvar_box','asym_box','std01']})
# same-person dose & theta
print('theta per rung median', {k:round(np.nanmedian([r['theta'] for r in it if r['key']==k]),3) for k in ['SAME20','X20','NOISES20','NOISEX20','SEMS20','DOSES10_20','DOSEX10_20']})
print('=== mechanism split')
for k in ['NOISES','NOISEX','SEMS','SEMX','SAME','X']:
    rs=sel(k); print(k,'median P_XS',round(np.median(col(rs,'clip_mad|P_XS')),2),'spearman theta~P_XS',round(spearmanr(col(rs,'theta'),col(rs,'clip_mad|P_XS'))[0],3), 'theta~lap', round(spearmanr(col(rs,'theta'),col(rs,'lapvar_box'))[0],3))
for a_,b_ in [('NOISEX','NOISES'),('SEMX','SEMS'),('X','SAME')]:
    print('P_XS',a_,'vs',b_, round(auc(col(sel(a_),'clip_mad|P_XS'),col(sel(b_),'clip_mad|P_XS')),3), 's401', round(auc(col(sel(a_),'smdd_s401'),col(sel(b_),'smdd_s401')),3), 'theta', round(auc(col(sel(a_),'theta'),col(sel(b_),'theta')),3))
# lapvar strat for P_XS and lap vs REC
print('lap REC median',np.median(col(R,'lapvar_box')),'SAME',np.median(col(S,'lapvar_box')),'X',np.median(col(X,'lapvar_box')))
