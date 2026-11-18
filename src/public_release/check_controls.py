"""PRIVATE check: the release controls/controls.py rebuilds the internal ladder rungs (OpenCV-style engine) of the
first N hosts of the AR1 pool exactly (R2w, R2w4, R3, R4, S0, S3, S4; pixel equality). Local images only; nothing is
written. python3 -I check_controls.py <release-repo> [N]"""
import csv, sys, importlib.util
import cv2, numpy as np
spec = importlib.util.spec_from_file_location("ctl", sys.argv[1] + "/controls/controls.py")
C = importlib.util.module_from_spec(spec); spec.loader.exec_module(C)
N = int(sys.argv[2]) if len(sys.argv) > 2 else 5
D = "/mnt/t7/smad_next/AR1/img/frgcferet/opencv"
res = {}
for r in list(csv.DictReader(open("/mnt/t7/smad_next/AR1/pool.csv")))[:N]:
    stem = r["pid"].replace(":", "_")
    load = lambda p: (cv2.imread(p), C.read_tem(p[:-4] + ".tem"))
    (H, lH), (S, lS), (B, lB) = load(r["H"]), load(r["S"]), load(r["B"])
    got = C.build_set(H, lH, S, lS, B, lB)
    for k in ("R2w", "R2w4", "R3", "R4", "S0", "S3", "S4"):
        ref = cv2.imread(f"{D}/{k}/{stem}.png")
        d = int(np.abs(ref.astype(int) - got[k].astype(int)).max()) if ref is not None else None
        res.setdefault(k, []).append(d)
print({k: v for k, v in res.items()})
sys.exit(0 if all(x == 0 for v in res.values() for x in v) else 1)
