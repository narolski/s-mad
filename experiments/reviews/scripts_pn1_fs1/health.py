import tarfile, json, re, hashlib, pathlib, numpy as np, io, math
R=pathlib.Path("/mnt/t7/smad_next/PN1/results_fs")
for t in sorted(R.glob("PN1_*_s*.tar")):
    n=t.name[:-4]
    with tarfile.open(t) as tf:
        names=tf.getnames()
        info=json.load(tf.extractfile(f"{n}/info.json"))
        meta=json.load(tf.extractfile(f"{n}/meta.json"))
        log=tf.extractfile(f"{n}/train.log").read().decode()
        sb=tf.extractfile(f"{n}/scores_eval.npz").read()
        z=np.load(io.BytesIO(sb))
    up=(R/"unpacked"/n/"scores_eval.npz").read_bytes()
    same=hashlib.sha256(up).hexdigest()==hashlib.sha256(sb).hexdigest()
    L=[float(x) for x in re.findall(r"loss ([0-9.naNinf]+)",log)]
    fin=all(math.isfinite(x) for x in L)
    lg=z["logit"].astype(float)
    print(n, info["device"], info["host"], "steps",info["steps"], "h %.2f"%info["train_hours"], "items",meta["n_items"], "acc %.4f"%info["train_acc_rule0"],
          "nloss",len(L),"fin",fin,"first %.3f last5 %.3f"%(L[0],np.mean(L[-5:])), "neval",len(lg), "allfinite",np.isfinite(lg).all(), "unpacked==tar",same, "DONE" in log)
