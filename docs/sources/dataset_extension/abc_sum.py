import json,statistics as st,sys
d=json.load(open(sys.argv[1]))
fm=d['family_metrics']
groups={'LM':['frllm:amsl','frllm:facemorpher','frllm:opencv','frllm:webmorph','mad22:FaceMorpher','mad22:OpenCV','mad22:Webmorph'],
'GAN':['frllm:stylegan','mad22:MIPGAN_I','mad22:MIPGAN_II'],
'DIFF':['dim:dim_a','dim:dim_c','dim:fast_dim','dim:fast_dim_ode','dim:greedy_dim','dim:greedy_dim_s','mordiff:mordiff']}
def m(task,f,key='eer'): return fm[task][f][key]
print('arch arm | nat_LM E7_LM | nat_GAN E7_GAN | nat_DIFF E7_DIFF | nat17 E7_17 | H2 H3o H3s (EER) | X3 a256/rec/self AUC')
for a in ['CN','VM','DeiT','D3']:
  for arm in ['A','B','C']:
    tasks=[f'{a}_{arm}_s{s}' for s in range(201,206)]
    row=[]
    for g,fs in groups.items():
      for pool in ['native','E7']:
        row.append(st.mean(st.mean(m(t,f'{pool}:{f}') for f in fs) for t in tasks))
    for pool in ['native','E7']:
      row.append(st.mean(st.mean(m(t,f'{pool}:{f}') for g in groups.values() for f in g) for t in tasks))
    for f in ['H2','H3_orig','H3_spread']:
      row.append(st.mean(m(t,f) for t in tasks))
    for f in ['X3:a256','X3:rec','X3:self']:
      row.append(st.mean(m(t,f,'auc') for t in tasks))
    print(a,arm,'|',' '.join(f'{x:6.2f}' for x in row[:10]),'|',' '.join(f'{x:6.2f}' for x in row[10:13]),'|',' '.join(f'{x:.3f}' for x in row[13:]))
