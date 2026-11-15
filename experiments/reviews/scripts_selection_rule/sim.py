import numpy as np
rng=np.random.default_rng(1); N=200000
def votes(delta,sig,tau,bar,k=4):
    D=delta+tau*rng.standard_normal((N,1))+np.sqrt(2)*sig*rng.standard_normal((N,5))
    return D,( (D>=bar).sum(1)>=k )
print("ladder (ii): P(fail | equal), vote rule >=-0.01 on 4/5 ; seed-mean rule mean>=-0.02")
for tau in [0,0.01,0.02]:
  for sig in [0.01,0.015,0.02,0.025]:
    D,p=votes(0,sig,tau,-0.01)
    print(f" tau={tau} sig={sig}: vote fail {1-p.mean():.2f}; mean>=-0.01 fail {(D.mean(1)<-0.01).mean():.2f}; mean>=-0.02 fail {(D.mean(1)<-0.02).mean():.2f}; true -0.03 arm passes mean>=-0.02 {((D.mean(1)-0.03)>=-0.02).mean():.2f}, vote {(((D-0.03)>=-0.01).sum(1)>=4).mean():.2f}")
print("lcomb (i): +0.03 per-seed on 4/5")
for tau in [0,0.007]:
  for sig in [0.008,0.012,0.016]:
    for g in [0,0.03,0.045,0.06]:
      D,p=votes(g,sig,tau,0.03)
      print(f" tau={tau} sig={sig} gain={g}: vote pass {p.mean():.3f}; seed-mean>=0.03 pass {(D.mean(1)>=0.03).mean():.3f}; seed-mean>=0.02 {(D.mean(1)>=0.02).mean():.3f}")
print("matched (iii): >=0.015 on 4/5 (gain on matched = g_m)")
for tau in [0,0.015,0.025]:
  for sig in [0.015,0.025]:
    for g in [0,0.015,0.03]:
      D,p=votes(g,sig,tau,0.015)
      print(f" tau={tau} sig={sig} gm={g}: vote pass {p.mean():.2f}; seed-mean>=0.015 {(D.mean(1)>=0.015).mean():.2f}")
