import csv, numpy as np, cv2, sys
m=list(csv.DictReader(open("/mnt/t7/smad_next/DATA/D12a/manifest.csv")))
st=[];shapes=set();bord=[]
for r in m:
    H=cv2.imread(r["frame_host"],cv2.IMREAD_UNCHANGED); R=cv2.imread(r["d1d_render_host"],cv2.IMREAD_UNCHANGED); M=cv2.imread(r["out"],cv2.IMREAD_UNCHANGED)
    shapes.add((H.shape,R.shape,M.shape,H.dtype.str,R.dtype.str))
    d=(R.astype(int)-H.astype(int))
    nz=(d!=0).any(2)
    dm=(M.astype(int)-H.astype(int)); nzm=(dm!=0).any(2)
    # black pixels
    blk=lambda X:(X.max(2)==0).mean()
    st.append([nz.mean(),np.abs(d).max(),np.abs(d).mean(),(d<0).mean(),nzm.mean(),blk(H),blk(R),blk(M)])
st=np.array(st)
print(shapes)
for i,n in enumerate(["frac px changed R-H","max|R-H|","mean|R-H|","frac neg","frac px changed M-H","black H","black R","black M"]):
    print(n, np.percentile(st[:,i],[0,10,50,90,100]).round(5))
