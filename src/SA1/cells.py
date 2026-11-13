import csv, collections, sys
cols = ["A","B","Sb","Sp","SbM3","MADation_ViT-B16","MADation_ViT-L14","MixFaceNet-MAD","SelfMAD"]
rows = {
 1:"storage history of genuine photos", 2:"storage history of morphs (evasion)", 3:"JPEG history",
 4:"unseen camera source (source comparison)", 5:"image border or frame", 6:"warp only (R2w)",
 7:"same-person morph (R3)", 8:"same-person face splice (S3)", 9:"blending seam (S0)",
 10:"alignment or crop path", 11:"data volume", 12:"surround blend (whole-frame tools)",
 13:"diffusion render path", 14:"GAN one-person render (MIPGAN)", 15:"training-partner trace (SMDD)",
 16:"expression / capture detail (FRLL smiling half)"}
R,R2,U,U2,NM,EX,PD,NA = "reviewed","reviewed; two seeds only","unreviewed","unreviewed; two seeds only","not measured","not measured (exposure only)","not measured (pending today)","n/a"
S = {
 1:[R,R,R,PD,PD,R,R,R,R],
 2:[U2,R2,PD,NM,NM,NM,NM,NM,NM],
 3:[EX,EX,EX,NM,NM,U,R,U,U],
 4:[R2,R2,R2,PD,PD,R,NM,U,R],
 5:[R2,R2,R2,NM,NM,U,NM,NM,U],
 6:[R2,R2,R2,NM,NM,R,R,R,R],
 7:[R2,R2,NM,NM,NM,R,R,R,R],
 8:[R,R,R,PD,NM,U,U,U,U],
 9:[NM,R2,R2,PD,NM,R,R,R,R],
 10:[R2,R2,R2,NM,NM,R,R,R,R],
 11:[NA,R2,R2,NA,PD,NA,NA,NA,NA],
 12:[U,R2,R,NM,NM,R,R,R,R],
 13:[NM,NM,NM,NM,NM,R,R,NM,R],
 14:[NM,NM,NM,NM,NM,R,R,NM,R],
 15:[NM,NM,NM,NM,NM,R,R,R,NA],
 16:[EX,EX,EX,EX,NM,R,R,NM,R],
}
out = sys.argv[1]
with open(out,"w",newline="") as f:
    w = csv.writer(f); w.writerow(["row","shortcut","column","cell_id","status"])
    for r,st in S.items():
        assert len(st)==9
        for c,s in zip(cols,st): w.writerow([r,rows[r],c,f"{r}-{c}",s])
cnt = collections.Counter(s for st in S.values() for s in st)
tot = sum(cnt.values())
rev = cnt[R]+cnt[R2]; unrev = cnt[U]+cnt[U2]; nm = cnt[NM]+cnt[EX]+cnt[PD]; na = cnt[NA]
print(f"total {tot}; reviewed {rev} (of which two seeds only {cnt[R2]}); unreviewed {unrev} (two seeds only {cnt[U2]}); empty {nm} (not measured {cnt[NM]}, exposure only {cnt[EX]}, pending today {cnt[PD]}); n/a {na}")
# per column block
for name, idx in (("our arms A-SbM3", range(0,5)), ("released detectors", range(5,9))):
    c = collections.Counter(S[r][i] for r in S for i in idx)
    print(name, dict(c))
