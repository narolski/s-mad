"""NE1 feature extraction (prereg.md section 2): for each network, the input of head.cls (L2-normalised 512-d CLIP
feature) and the logit (no flip), with rescore.py's model build, eval mode, batch 64, manifest order, PyTorch defaults.
Manifests in order: ne1_gate.csv, ne1_train.csv, ne1_read.csv. Out: <out>/<net>__<manifest stem>.npz (id, feat, logit).
  python ne1_extract.py --code CODE --nets NETS_DIR --out OUT [--limit 8] [--workers 7]"""
import argparse, json, os, pathlib, sys
import numpy as np


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--code", required=True); ap.add_argument("--nets", required=True); ap.add_argument("--out", required=True)
    ap.add_argument("--limit", type=int, default=0); ap.add_argument("--workers", type=int, default=7)
    a = ap.parse_args()
    sys.path.insert(0, str(pathlib.Path(a.code) / "smadcvpr"))
    import torch
    from torch.utils.data import DataLoader
    import common as C
    out = pathlib.Path(a.out); out.mkdir(parents=True, exist_ok=True)
    for n in sorted(os.listdir(a.nets)):
        d = pathlib.Path(a.nets) / n
        meta = json.load(open(d / "meta.json"))
        model, _ = C.build_run_model(meta)
        tr = torch.load(d / "last_trainable.pt", map_location="cpu", weights_only=True)
        names = {k for k, p in model.named_parameters() if p.requires_grad}
        assert set(tr) == names, (n, len(tr), len(names))
        _, unexpected = model.load_state_dict(tr, strict=False); assert not unexpected
        model.to("cuda").eval()
        feats = []
        h = model.head.cls.register_forward_pre_hook(lambda m, inp: feats.append(inp[0].detach().float().cpu()))
        for man in ("ne1_gate.csv", "ne1_train.csv", "ne1_read.csv"):
            rows = C.read_manifest(man)
            if a.limit:
                rows = rows[:a.limit]
            dl = DataLoader(C.ImageItems([(r["path"], int(r["label"])) for r in rows], meta["res"]), batch_size=64, num_workers=a.workers)
            lg = []; feats.clear()
            with torch.no_grad():
                for x, _ in dl:
                    lg += C.forward_logit(model, x.to("cuda"))[0].float().cpu().tolist()
            F = torch.cat(feats).numpy()
            assert F.shape[0] == len(rows), (n, man, F.shape)
            np.savez(out / f"{n}__{man[:-4]}.npz", id=np.array([r["id"] for r in rows]), feat=F.astype(np.float32), logit=np.array(lg, np.float32))
            print("EXTRACTED", n, man, len(rows), flush=True)
        h.remove()
        del model; torch.cuda.empty_cache()


if __name__ == "__main__":
    main()
