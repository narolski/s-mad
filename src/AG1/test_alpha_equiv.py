"""Test (DGX): (1) the mipgan_alpha objective at alpha 0.5 equals generate.mipgan's objective at the same latent
(forward, exact); (2) the run-to-run spread of generate.mipgan itself (same init twice) - the floor against which the
--selfcheck difference (alpha 0.5 path vs generate.mipgan) is read. Usage: python -I test_alpha_equiv.py WORK LATDIR OUT"""
import functools, json, pathlib, sys
W, LAT, OUT = map(pathlib.Path, sys.argv[1:4])
sys.path.insert(0, str(W / "gan_weights/py")); sys.path.insert(0, str(W / "ag1_code/vendor"))
import os
os.environ["GAN_WEIGHTS"] = str(W / "gan_weights"); os.environ["SG1_WEIGHTS"] = str(W / "gan_sg1/stylegan1_ffhq1024.pt")
os.environ["TORCH_HOME"] = str(W / "gan_weights/torch")
import numpy as np, torch, torch.nn.functional as F
_l = torch.load
torch.load = lambda *a, **k: _l(*a, **{**k, "weights_only": True})
import arcface as AF, generate as GEN, generate_mip1 as G1
torch.backends.cuda.matmul.allow_tf32 = False; torch.backends.cudnn.allow_tf32 = False
torch.backends.cudnn.deterministic = True; torch.backends.cudnn.benchmark = False
m = G1.Models1("cuda")
P = json.load(open(W / "ag1_inputs/photos.json"))
a, b = "frll_001__s1", "frll_001__s2"
xa, xb = GEN.load_png(W / "ag1_inputs" / P[a]["crop"]).cuda(), GEN.load_png(W / "ag1_inputs" / P[b]["crop"]).cuda()
ka, kb = np.array(P[a]["kps256"]), np.array(P[b]["kps256"])
Ma, Mb, Mm = AF.estimate_norm(ka), AF.estimate_norm(kb), AF.estimate_norm((ka + kb) / 2)
wa = torch.from_numpy(np.load(LAT / f"inv_{a}.npz")["w"]).cuda(); wb = torch.from_numpy(np.load(LAT / f"inv_{b}.npz")["w"]).cuda()
w0 = (wa + wb) / 2
with torch.no_grad():
    ea, eb = m.emb(xa, Ma), m.emb(xb, Mb); fa, fb = m.vgg_feats(xa), m.vgg_feats(xb)
    y = GEN.down(m.synth(w0)); fy = m.vgg_feats(y); e = m.emb(y, Mm)
    da, db = 1 - (e * ea).sum(), 1 - (e * eb).sum(); y01 = (y + 1) / 2
    s_a = 1 - m.ms_ssim(y01, (xa + 1) / 2, data_range=1.0); s_b = 1 - m.ms_ssim(y01, (xb + 1) / 2, data_range=1.0)
    ref = (GEN.MIP["l1"] * (0.5 * sum(F.mse_loss(f, g) for f, g in zip(fy, fa)) + 0.5 * sum(F.mse_loss(f, g) for f, g in zip(fy, fb)))
           + GEN.MIP["l2"] * (da + db) / 2 + GEN.MIP["l3"] * (0.5 * s_a + 0.5 * s_b) + GEN.MIP["l4"] * (da - db).abs())
    al = 0.5
    alt = (GEN.MIP["l1"] * ((1 - al) * sum(F.mse_loss(f, g) for f, g in zip(fy, fa)) + al * sum(F.mse_loss(f, g) for f, g in zip(fy, fb)))
           + GEN.MIP["l2"] * ((1 - al) * da + al * db) + GEN.MIP["l3"] * ((1 - al) * s_a + al * s_b) + GEN.MIP["l4"] * 2 * ((1 - al) * da - al * db).abs())
r1, _ = GEN.mipgan(m, xa, xb, Ma, Mb, Mm, w0)
r2, _ = GEN.mipgan(m, xa, xb, Ma, Mb, Mm, w0)
res = {"objective_ref": float(ref), "objective_alpha05": float(alt), "objective_equal": bool(float(ref) == float(alt)),
       "mipgan_twice_maxabs_w": float((r1 - r2).abs().max()), "mipgan_twice_meanabs_w": float((r1 - r2).abs().mean())}
json.dump(res, open(OUT / "alpha_equiv.json", "w"), indent=1); print(res)
