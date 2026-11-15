import json,statistics as st,sys,math
d=json.load(open(sys.argv[1])); fm=d['family_metrics']
G={'LM':['frllm:amsl','frllm:facemorpher','frllm:opencv','frllm:webmorph','mad22:FaceMorpher','mad22:OpenCV','mad22:Webmorph'],
'DIFF':['dim:dim_a','dim:dim_c','dim:fast_dim','dim:fast_dim_ode','dim:greedy_dim','dim:greedy_dim_s','mordiff:mordiff']}
T4=2.776
def val(t,kind):
    if kind in G: fs=G[kind]; return st.mean(fm[t]['E7:'+f]['eer']-fm[t]['native:'+f]['eer'] for f in fs)
    if kind.startswith('E7') or kind.startswith('nat'):
        g=kind.split('_')[1]; pool='E7' if kind.startswith('E7') else 'native'
        return st.mean(fm[t][f'{pool}:{f}']['eer'] for f in G[g])
    if kind=='Q': return (fm[t]['H2']['eer']+fm[t]['H3_orig']['eer'])/2
    return fm[t][kind]['eer']
def ci(v):
    m=st.mean(v); s=st.stdev(v); h=T4*s/math.sqrt(len(v)); return f'{m:+6.2f} [{m-h:+.2f},{m+h:+.2f}]'
for kind in ['LM','DIFF','E7_DIFF','E7_LM','H2','H3_orig','Q']:
  print('==',kind,'(rise E7-native, EER pts)' if kind in G else '')
  for a in ['CN','VM','DeiT','D3']:
    v={arm:[val(f'{a}_{arm}_s{s}',kind) for s in range(201,206)] for arm in 'ABC'}
    out=f'{a:5s} A {st.mean(v["A"]):6.2f} B {st.mean(v["B"]):6.2f} C {st.mean(v["C"]):6.2f} | B-A '+ci([b-x for b,x in zip(v['B'],v['A'])])+' C-B '+ci([c-b for c,b in zip(v['C'],v['B'])])+' C-A '+ci([c-x for c,x in zip(v['C'],v['A'])])
    print(out)
