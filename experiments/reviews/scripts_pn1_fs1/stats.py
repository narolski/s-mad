import json, numpy as np
from scipy import stats
d=json.load(open("/tmp/claude-1000/-home-narolski-mambamorph/c2840dc9-dd37-4619-9347-d8a76080b93f/scratchpad/fs/recomp.json"))["out"]
S=(403,404,405,406,407)
v=lambda a,k: np.array([d[f"{a}_{s}"][k] for s in S])
for k in ("lcomb","fo_test","fo_dev","fb_test","share","shift_sd","med_shift","flag_nat","flag_rm","miss_lcm","miss_DS4","flag_DS3","flag_DS0","DR0_61"):
    print(k)
    for a in ("A","B","Sb"):
        x=v(a,k); print(f"   {a:3s} mean {x.mean():.3f} SD {x.std(ddof=1):.3f} [{x.min():.3f},{x.max():.3f}]")
    for a,b in (("Sb","B"),("Sb","A"),("B","A")):
        dd=v(a,k)-v(b,k)
        w=stats.wilcoxon(dd,alternative="two-sided",method="exact").pvalue if np.any(dd!=0) else 1
        mw=stats.mannwhitneyu(v(a,k),v(b,k),alternative="two-sided",method="exact").pvalue
        print(f"   {a}-{b}: mean {dd.mean():+.3f} SD {dd.std(ddof=1):.3f} [{dd.min():+.3f},{dd.max():+.3f}] pos {int((dd>0).sum())}/5 wilcoxon2s {w:.4f} MW2s {mw:.4f}")
print("Sb - s_lad 0.8144465:", np.round(v("Sb","lcomb")-0.8144465,4), " Sb - b_lad 0.8138695:",np.round(v("Sb","lcomb")-0.8138695,4))
print("Sb - floor 0.8855815:", np.round(v("Sb","lcomb")-0.8855815,4))
print("B - b_lad:", np.round(v("B","lcomb")-0.8138695,4))
print("A shares incl 401/402:", sorted(list(v("A","share"))+[0.778,0.7205]))
for a in ("A","B","Sb"): print(a,"flag ratio rm/nat", np.round(v(a,"flag_rm")/v(a,"flag_nat"),2))
