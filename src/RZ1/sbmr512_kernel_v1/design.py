"""Prospective source/metadata-only design. No model or archive imports."""
SEEDS = (408,409,410,411,412)
NAMES = ("pil_bilinear","pil_nearest","pil_bicubic","pil_lanczos","pil_box","cv_area","cv_linear","cv_cubic","cv_lanczos4")
REFERENCE = "fixed:pil_bilinear"
TRAIN = tuple("two:300:"+k+":"+k for k in NAMES)
HELD = ("two:300:pil_hamming:pil_hamming","two:300:cv_nearest:cv_nearest","two:300:cv_linear_exact:cv_linear_exact","two:300:pil_hamming:cv_linear_exact")
SPECS = (REFERENCE,)+TRAIN+HELD
SOURCES = ("replay_attack","msu_mfsd","oulu_npu","casia_fasd","lfw","calfw","cfp_ff","agedb_30")
def masks(cross, ab1x):
    camera = [r["id"] for r in ab1x if r["fam"]=="ladder" and r["role"]=="dev" and r["rung"]=="R0" and r["strength"]==""]
    camera += [r["id"] for r in ab1x if r["fam"]=="af0" and r["role"]=="dev" and r["rung"]=="photo" and r["strength"]==""]
    native = sorted(r["id"] for r in ab1x if r["fam"]=="ms1ffhq" and r["rung"]=="photo" and r["strength"]=="")
    byid={r["id"]:r for r in cross}
    assert len(byid)==len(cross)
    gen=["ab1x:"+i for i in camera+native]+[r["id"] for r in cross if r["src"]=="tt1" and (r["rung"]=="R_cam" or (r["role"]=="tt1" and r["rung"] in SOURCES))]
    gen=[i for i in gen if i in byid]
    mor=["ab1x:"+r["id"] for r in ab1x if r["fam"]=="ffhq_lcomb" and r["rung"]=="landmark_combined_orig"]
    assert gen and mor and len(set(gen))==len(gen) and len(set(mor))==len(mor)
    assert not set(gen)&set(mor)
    assert all(i in byid for i in gen+mor)
    assert all(byid[i]["label"]=="0" for i in gen)
    assert all(byid[i]["label"]=="1" for i in mor)
    return gen,mor
def operational_summary(per_seed):
    """Generated/once-reader input only; absent seed remains in denominator five."""
    assert set(per_seed)<=set(SEEDS)
    def count(key):
        return sum(type(per_seed.get(s,{}).get(key)) in (int,float) and 0<=per_seed[s][key]<=0.05 for s in SEEDS)
    a,b=count("kappa_train512"),count("kappa_ho512")
    return dict(denominator=5,train_pass_seeds=a,heldout_pass_seeds=b,train_condition=a>=4,heldout_condition=b>=4)
