exec(open("h4.py").read().split("L={}")[0])
import numpy as np
from scipy.stats import spearmanr
F=np.array([norm[mo[i]]["Feminine"] for i in ids]); sx=np.array([mo[i][1]=="F" for i in ids])
print("Feminine F mean/min",F[sx].mean(),F[sx].min(),"M mean/max",F[~sx].mean(),F[~sx].max(),"rho(fem,sex)",spearmanr(F,sx).correlation)
print("overlap: females below male max",(F[sx]<F[~sx].max()).sum(),"males above female min",(F[~sx]>F[sx].min()).sum())
