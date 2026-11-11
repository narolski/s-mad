# Read-only CPU check: is the training sample order of A47 I-3 M3 seed 1 (WCSS container, torch 2.2.1, timm 1.0.27, x86)
# reproduced by this stack (DGX venv)? Compares the first 200 batch compositions recorded in A47's meta.json with the
# batches this stack's RNG stream produces after the same model build (no image is read, no GPU).
import json, os, pathlib, random, sys
import numpy as np
W = pathlib.Path("/mnt/t7/smad_next/AD4/test/work/task_AD4_m3mf_s401")
sys.path.insert(0, str(W / "ad4/code/smadcvpr"))
os.environ["SMAD_DATA"] = str(W / "data"); os.environ["HF_HOME"] = str(W / "ad4/hf"); os.environ["HF_HUB_OFFLINE"] = "1"
import torch, timm
from torch.utils.data import DataLoader, Dataset
import common as C
ref = json.load(open("/mnt/t7/smad_heldout/a47/runs/A47I3/a12_clip_vitb16_madation_r224_d0_train90_none_lr3.33e-06_s1_i3/meta.json"))
comp_ref = np.array(ref["composition"]["per_batch"])
print("A47 s1 cells", ref["composition"]["cells"], "batches", len(comp_ref), "first", comp_ref[:3].tolist())
seed = 1
random.seed(seed); np.random.seed(seed); torch.manual_seed(seed); torch.cuda.manual_seed_all(seed)
rows = C.run_rows("d0", "train90", "none", [], False, None)
model, extra = C.build_model("a12_clip_vitb16_madation", 224, 0.0)
C.apply_lora(model, 2, targets="qv", alpha=4.0, dropout=0.4, rs=True, train_norms=False)
lab = np.array([int(r["label"]) for r in rows])
class Idx(Dataset):
    def __len__(self): return len(rows)
    def __getitem__(self, i): return i
def draw():
    return int(torch.empty((), dtype=torch.int64).random_().item())
base_seed = draw()                         # _BaseDataLoaderIter.__init__ (once: persistent workers keep the iterator)
comp, n = [], len(rows)
while len(comp) < len(comp_ref):           # each pass: RandomSampler.__iter__ draws its seed from the global stream
    g = torch.Generator(); g.manual_seed(draw())
    perm = torch.randperm(n, generator=g).numpy()
    for k in range(n // 256):              # drop_last
        ii = perm[k * 256:(k + 1) * 256]
        comp.append([int((lab[ii] == 0).sum()), int((lab[ii] == 1).sum()), 0])
        if len(comp) == len(comp_ref): break
comp = np.array(comp)
print("this stack", sys.version.split()[0], torch.__version__, timm.__version__, "first", comp[:3].tolist())
print("identical first-%d-batch compositions:" % len(comp), bool((comp == comp_ref).all()), "n equal rows", int((comp == comp_ref).all(1).sum()))
hw = model.head.cls.weight.detach().flatten()
print("head init fingerprint seed 1: sum %.9f first3 %s" % (float(hw.sum()), [round(float(v), 9) for v in hw[:3]]))
