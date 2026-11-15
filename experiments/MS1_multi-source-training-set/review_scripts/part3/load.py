import tarfile, io, csv, numpy as np, pickle, sys
RES="/mnt/t7/smad_next/MS1/results_rented"
out={}
for arm in ("Sb","SbM3","SbV"):
    for s in range(403,408):
        with tarfile.open(f"{RES}/MS1_{arm}_s{s}.tar") as t:
            d={}
            for m in t.getmembers():
                for nm in ("scores_eval.npz","scores_train.npz"):
                    if m.name.endswith(nm):
                        z=np.load(io.BytesIO(t.extractfile(m).read()),allow_pickle=False)
                        d[nm]={k:z[k] for k in z.files}
            out[(arm,s)]=d
pickle.dump(out,open(sys.argv[1],"wb"))
for k,v in out.items(): print(k,{n:{kk:vv.shape for kk,vv in x.items()} for n,x in v.items()})
