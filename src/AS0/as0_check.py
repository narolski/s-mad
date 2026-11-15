"""Mirror-asymmetry test (AS0): implementation checks on synthetic in-memory arrays and on mirror equivariance of one
real photo (no contrast is computed). python3 -I as0_check.py -> OUT/check.json"""
import json
import pathlib
import sys

import numpy as np

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import as0_common as K  # noqa: E402
import as0_measure as M  # noqa: E402

pool = K.read_csv(K.AR1 / "pool.csv")
r = pool[0]
import cv2
img = cv2.imread(r["H"])
lm = K.read_tem(r["H"][:-4] + ".tem")
W = img.shape[1]
iod = 130.51
out = {}
EA, ES, cov = M.measure(img, lm, iod, "ar1_512")
# 1 mirror equivariance: flipped image with the mirrored, re-indexed shape gives the same energies (F0)
EAf, ESf, covf = M.measure(np.ascontiguousarray(img[:, ::-1]), K.mirror_shape(lm, W), iod, "ar1_512")
out["equivariance_F0_max_rel_diff"] = float(np.nanmax(np.abs(EAf[:, 0] - EA[:, 0]) / EA[:, 0]))
out["equivariance_F0_ES_max_rel_diff"] = float(np.nanmax(np.abs(ESf[:, 0] - ES[:, 0]) / ES[:, 0]))
# 2 a symmetric image (x + flip x)/2 has no asymmetric energy (F0); an antisymmetric-plus-constant image none symmetric
x = img.astype(np.float64)
sym = np.clip(np.round((x + x[:, ::-1]) / 2), 0, 255).astype(np.uint8)
sym = np.ascontiguousarray(sym)
symm = (sym.astype(int) == sym[:, ::-1].astype(int)).all()
EAs, ESs, _ = M.measure(sym, lm, iod, "ar1_512")
out["symmetric_image_exact"] = bool(symm)
out["symmetric_image_EA_over_ES_F0_max"] = float(np.nanmax(EAs[:, 0] / ESs[:, 0]))
# 3 white noise: E_A / E_S near 1 in every band
rng = np.random.default_rng(1)
noise = rng.integers(0, 256, img.shape, dtype=np.uint8)
EAn, ESn, _ = M.measure(noise, lm, iod, "ar1_512")
out["noise_ratio_F0_Y_by_band"] = (EAn[0, 0] / ESn[0, 0]).round(3).tolist()
out["noise_ratio_F1_Y_by_band"] = (EAn[0, 1] / ESn[0, 1]).round(3).tolist()
# 4 shifted flip: an image symmetric about x = 250 (index map j -> 500 - j) and a shape centred there
sh = img.copy()
j = np.arange(W)
idx = 500 - j
v = (idx >= 0) & (idx < W)
sh2 = sh.astype(np.float64)
sh2[:, v] = (sh2[:, v] + sh2[:, idx[v]]) / 2
sh2 = np.ascontiguousarray(np.clip(np.round(sh2), 0, 255).astype(np.uint8))
lm2 = lm.copy()
lm2[:, 0] = lm2[:, 0] - (lm[:, 0].mean() - 250.0)
EA2, ES2, cov2 = M.measure(sh2, lm2, iod, "ar1_512")
out["shifted_axis_c_mid"] = cov2["c_mid"]
out["shifted_symmetric_EA_over_ES_F1_by_band_Y"] = (EA2[0, 1] / ES2[0, 1]).tolist()
out["real_photo_L_F0_Y"] = np.log(EA[0, 0] / ES[0, 0]).round(3).tolist()
out["real_photo_cov"] = {k: (round(v, 4) if isinstance(v, float) else v) for k, v in cov.items()}
# 5 band partition
Hs = M.band_weights(512, 512, iod)
out["band_weight_sq_sum_minmax"] = [float((Hs.astype(np.float64) ** 2).sum(0).min()), float((Hs.astype(np.float64) ** 2).sum(0).max())]
# 6 shape asymmetry of an exactly symmetric shape
ls = (lm + K.mirror_shape(lm, W)) / 2
out["shape_L_symmetric_shape"] = M.shape_asym(ls, W)
out["shape_L_photo"] = M.shape_asym(lm, W)
json.dump(out, open(K.OUT / "check.json", "w"), indent=1)
json.dump(out, open(K.RES / "check.json", "w"), indent=1)
print(json.dumps(out, indent=1))
