"""CB1 IDistill: score a trained classifier on OUT_DIR/eval_all.csv with the authors' test path
(data_utils.FaceDataset split 'test': cv2.imread, Resize 224, ToTensor, Normalize 0.5; Resnet18_Mult(latent)).
Writes y~ = outputs[2] (the authors' bona fide probability), id1, id2 and the morph score id1*id2 per crop.
  python3 -I run_code.py CODE STUBS score_idistill.py CSV_DIR CKPT OUT.csv [latent 128]"""
import csv, sys, pathlib, torch
from torch.utils.data import DataLoader
from data_utils import FaceDataset
from resnet_utils_mult import Resnet18_Mult
d, ck, out = pathlib.Path(sys.argv[1]), sys.argv[2], sys.argv[3]
lat = int(sys.argv[4]) if len(sys.argv) > 4 else 128
m = Resnet18_Mult(lat); m.load_state_dict(torch.load(ck, map_location="cpu")); m.cuda().eval()
ds = FaceDataset(file_name=str(d / "eval_all.csv"), split="test", latent_size=lat)
dl = DataLoader(ds, batch_size=64, shuffle=False, num_workers=8)
ys, i1, i2 = [], [], []
with torch.no_grad():
    for x, _ in dl:
        o = m(x.cuda())
        ys += o[2].reshape(-1).double().cpu().tolist(); i1 += o[3].reshape(-1).double().cpu().tolist(); i2 += o[4].reshape(-1).double().cpu().tolist()
meta = list(csv.DictReader(open(d / "eval_all_meta.csv")))
assert len(meta) == len(ys)
with open(out, "w", newline="") as f:
    x = csv.writer(f); x.writerow(["folder", "file", "y_bona", "id1", "id2", "morph_score_id1xid2"])
    for r, y, a, b in zip(meta, ys, i1, i2):   # review F3: morph score = id1 * id2 (no 1 - x cancellation)
        x.writerow([r["folder"], r["file"], f"{y:.10g}", f"{a:.10g}", f"{b:.10g}", f"{a * b:.10g}"])
print(f"scored {len(ys)} -> {out}")
