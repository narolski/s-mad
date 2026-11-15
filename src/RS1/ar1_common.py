"""AR1 shared paths and helpers. Reuses existing code only (imported unchanged, pins checked where the record pins them)."""
import hashlib
import importlib.util
import pathlib
import sys

MC = pathlib.Path("/home/narolski/mambamorph-code")          # main tree: scripts/78, 96, 73, prep_eval, dmad
W46 = pathlib.Path("/home/narolski/mambamorph-code-a46")      # frozen A46 runtime: a12_released, a41g_score, a41_read, a46_corrective_crop
DATA = MC / "smadcvpr_data"                                   # train/ + arms -> /dev/shm/smad_arms
OUT = pathlib.Path("/mnt/t7/smad_next/AR1")                   # large outputs
RES = pathlib.Path("/home/narolski/smad-next/experiments/AR1")
A2F_DIR = pathlib.Path("/mnt/t7/smad_heldout/arc2face/scripts")
PINS = {
    MC / "smadcvpr/prep_eval.py": "374408ab3a886e6df25b563bc2344d190efe2ab7b3163efbb17c9b6ca9100628",
    A2F_DIR / "a2f_common.py": "d27701dbe187dd6fcc2b50f21e3631a1c1a0678cfdc9d5a6989cd9c355bfcc3c",
    W46 / "smadcvpr/a41g_score.py": "f53612cb146e72ca5598d9b01962dcf3fb2f9d4aa8c9d616d80bd99e273c6113",
    W46 / "smadcvpr/a12_released.py": "839f0cd4498577cad5410a63e1da63feeff53e05a3bed2c511ff67cac01e41da",
}
WEIGHTS = {
    "madation_vitb16": pathlib.Path("/mnt/t7/smad_heldout/mad22_production_cpu_stage_v1/payload/models/"
                                    "ddb1455bae4b72331aff4806590bd88ba2447563d803e207099c6b712d6bbe2f.safetensors"),
    "madation_vitl14": pathlib.Path("/mnt/t7/smad_heldout/mad22_production_cpu_stage_v1/payload/models/"
                                    "bb452ded624ffce2dc85168f8dde9293fc3709ec8cce755d8ecf1d5f5370e980.safetensors"),
    "mixfacenet_mad_smdd": pathlib.Path("/mnt/t7/mixfacenet_mad_official/mixfacenet_SMDD.pth"),
    "selfmad_hrnet_w18": OUT / "weights/selfmad_release/hrnet_w18_checkpoint.model.safetensors",
}
WEIGHT_SHA = {
    "madation_vitb16": "ddb1455bae4b72331aff4806590bd88ba2447563d803e207099c6b712d6bbe2f",
    "madation_vitl14": "bb452ded624ffce2dc85168f8dde9293fc3709ec8cce755d8ecf1d5f5370e980",
    "mixfacenet_mad_smdd": "3d507c8bbd5dbd06bd735ae809fa0095e589c17c0c94cd2ed530cf34a014ab1c",
    "selfmad_hrnet_w18": "0ad8db6f8f156cb21606e03ab32c88d122640cb835f7a93c77cca30c01386a26",
}
A12BR_RUNS = pathlib.Path("/mnt/t7/wcss_backups/smadcvpr/runs/A12BR")
A12BR_META = MC / "smadcvpr_runs/A12_scored/A12BR"
M3 = [f"a12_clip_vitb16_madation_r224_d0_train90_none_lr3.33e-06_s{s}_r" for s in range(1, 9)]
M3L = [f"a12_clip_vitl14_madation_r224_d0_train90_none_lr3.33e-06_s{s}_r" for s in range(1, 6)]
PREDICTOR81 = pathlib.Path("/mnt/t7/thirdparty/dlib81_wcss_20261107/shape_predictor_81_face_landmarks.dat")


def sha(p):
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for b in iter(lambda: f.read(1 << 20), b""):
            h.update(b)
    return h.hexdigest()


def forbidden(p):
    s = str(p).lower()
    return any(x in s for x in ("fst", "a12sp", "a12-sp")) or ("valx" in s and not s.endswith("valx_a.csv"))


def load_module(path, name, pin=None):
    path = pathlib.Path(path)
    pin = pin or PINS.get(path)
    if pin and sha(path) != pin:
        sys.exit(f"{path}: not at its pin {pin}")
    spec = importlib.util.spec_from_file_location(name, path)
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


def add_paths(*ps):
    for p in ps:
        if str(p) not in sys.path:
            sys.path.insert(0, str(p))


def read_tem(path):
    import numpy as np
    lines = open(path).read().splitlines()
    n = int(lines[0].strip())
    return np.array([list(map(float, lines[i].split())) for i in range(1, n + 1)], np.float32)
