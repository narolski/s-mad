"""CB1 IDistill: apply the minimal deviations to the authors' code (commit 0473bb43) in place.
Only paths, seeding and saving the last checkpoint change; the training/eval logic is untouched.
  python3 -I apply_patch.py CODE_DIR      (writes the result; the diff against the pristine copy is kept as idistill_cb1.patch)"""
import pathlib, sys

d = pathlib.Path(sys.argv[1])
R = {
    "data_utils.py": [
        ('"/nas-ctm01/datasets/public/BIOMETRICS/embeddings/unetautoencoder/2023-02-20_15-54-40/', 'os.environ["IDS_LAT"] + "/'),
        ('"/nas-ctm01/datasets/public/BIOMETRICS/embeddings/unetautoencoder/2023-02-23_14-20-28/', 'os.environ["IDS_LAT"] + "/'),
        ('"/nas-ctm01/datasets/public/BIOMETRICS/embeddings/unetautoencoder/2023-02-25_09-04-28/', 'os.environ["IDS_LAT"] + "/'),
    ],
    "train.py": [
        ('"/nas-ctm01/datasets/public/BIOMETRICS/Face_Morphing/facelab_london/', 'os.environ["IDS_FRLL"] + "/'),
        ("    cudnn.benchmark = True\n",
         "    cudnn.benchmark = True\n    import random as _r; _s = int(os.environ.get('IDS_SEED', '0'))  # CB1: seed\n"
         "    torch.manual_seed(_s); np.random.seed(_s); _r.seed(_s)\n"),
        ("        val_loss, val_acc, val_eer_values,out_20,out_10,out_1,out_01 = eval_fn(model, dataloaders['val'], dataset_sizes['val'], criterion, device=device)\n",
         "        val_loss, val_acc, val_eer_values,out_20,out_10,out_1,out_01 = eval_fn(model, dataloaders['val'], dataset_sizes['val'], criterion, device=device)\n"
         "        if val_eer_values < getattr(run_training, '_cb1_best_val', 1e9):  # CB1: checkpoint selected on the SMDD validation split\n"
         "            run_training._cb1_best_val = val_eer_values; torch.save(model.state_dict(), model_path + '.valbest'); print('CB1 valbest epoch', epoch, val_eer_values)\n"),
        ("    torch.save(best_model_wts, model_path)\n",
         "    torch.save(best_model_wts, model_path)\n    torch.save(model.state_dict(), model_path + '.last')  # CB1: last checkpoint\n"),
    ],
}
for f, reps in R.items():
    p = d / f
    t = p.read_text()
    for a, b in reps:
        n = t.count(a)
        if n == 0:
            sys.exit(f"{f}: pattern not found: {a[:60]}")
        t = t.replace(a, b)
    p.write_text(t)
    print(f"patched {f}")
