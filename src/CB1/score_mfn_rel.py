"""CB1 amendment 5: score the released MixFaceNet-MAD (mixfacenet_SMDD.pth, sha256 3d507c8b...) in the 'rel' mode used
for the AG1 and A43 rows of the other releases: our aligned frames through the program loader (common.ImageItems,
PIL bilinear to 224, /255), the release adapter of a12_released.py (BGR, (x-0.5)/0.5, 2-class head, morph logit =
z0 - z1). Imported unchanged from the AG1 job root /mnt/t7/smad_next/AG1/scoring/jobroot/smadcvpr. Writes logit without
flip and the flip-averaged sigmoid per image. CPU or GPU.
  python3 -I score_mfn_rel.py --list LIST.csv (id,path absolute) --out OUT.npz [--device cpu] [--limit N]"""
import argparse, csv, hashlib, pathlib, sys
import numpy as np

J = "/mnt/t7/smad_next/AG1/scoring/jobroot/smadcvpr"
CK = pathlib.Path("/mnt/t7/mixfacenet_mad_official/mixfacenet_SMDD.pth")
CK_SHA = "3d507c8bbd5dbd06bd735ae809fa0095e589c17c0c94cd2ed530cf34a014ab1c"

ap = argparse.ArgumentParser()
ap.add_argument("--list", required=True); ap.add_argument("--out", required=True)
ap.add_argument("--device", default="cpu"); ap.add_argument("--limit", type=int, default=0)
ap.add_argument("--workers", type=int, default=2)
a = ap.parse_args()
sys.path.insert(0, J)
import torch
from torch.utils.data import DataLoader
import common as C
import a12_released as R
R.torch = torch          # a12_released imports torch inside its main(); give the module the same torch
assert hashlib.sha256(CK.read_bytes()).hexdigest() == CK_SHA
torch.set_num_threads(2)
spec = R.RELEASES["mixfacenet_mad_smdd"]
m = R.build_release(spec)
m.load_state_dict(R.extract_state(R.load_release(CK), spec), strict=True)
m.to(a.device).eval()
rows = list(csv.DictReader(open(a.list)))
if a.limit:
    rows = rows[:a.limit]
dl = DataLoader(C.ImageItems([(r["path"], 0) for r in rows], spec["res"], root="/"), batch_size=32,
                num_workers=a.workers)
L, P = [], []
with torch.no_grad():
    for bi, (x, _) in enumerate(dl):
        x = x.to(a.device)
        l0 = R.head_logit(m(R.adapt_input(x, spec)), spec["classes"], spec["morph_index"])
        l1 = R.head_logit(m(R.adapt_input(torch.flip(x, dims=[3]), spec)), spec["classes"], spec["morph_index"])
        L.append(l0.cpu().numpy()); P.append(((torch.sigmoid(l0) + torch.sigmoid(l1)) / 2).cpu().numpy())
        if bi % 50 == 0:
            print(f"batch {bi} of {len(dl)}", flush=True)
np.savez(a.out, id=np.array([r["id"] for r in rows]), logit_noTTA=np.concatenate(L), score=np.concatenate(P),
         list_sha256=hashlib.sha256(pathlib.Path(a.list).read_bytes()).hexdigest(), ckpt_sha256=CK_SHA,
         device=a.device, torch=torch.__version__)
print("WRITTEN", a.out, len(rows))
