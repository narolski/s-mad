"""Shared test battery (BATTERY): platform record and platform gate.

Record (every run): GPU model, UUID, compute capability, driver, torch build, CUDA runtime, cuDNN version, TF32 flags
(matmul and cuDNN), cudnn.benchmark, deterministic-algorithms flag, scaled-dot-product-attention backends, Python and
package versions, host, Slurm job. Items 1-11 of TT1's PLATFORM_PINS_FOR_FINAL_READ.md.

Gate (before any battery row is scored): a pinned reference network, stored logits of which were made on this platform
by the fit-job scorer (src/PN1/pn1_score.py: TF32 on, float32, batch 64, manifest order), is scored again by the battery's
own loader and scorer on GATE_ROWS, which are 39 whole batches of the stored run (batch k for k = 0, 8, ..., 304 of the
FS1 evaluation order, i.e. rows 64k .. 64k+63), so batch composition equals the stored run's. Criterion fixed in advance:
byte identity, every one of the 2,496 float32 logits equal to the stored one (max |dlogit| = 0). The rows span the logit
range: camera photos at the floor, FFHQ genuine and morphs, splices (stored reference logits -3.6 to +3.5, about 370-500 of
them between -2 and +2). A platform with no pinned reference is refused (the DGX GB10 among them: TT1 H-new-5)."""
import json
import os
import platform as _pf
import socket
import subprocess
import sys
import time

GATE_BATCH_EVERY, GATE_N_BATCHES, BS = 8, 39, 64
GATE_BATCHES = [8 * j for j in range(GATE_N_BATCHES)]          # 0 .. 304; all inside the 309 full FS1 batches

# platform key -> pinned reference (network files inside its verified result tar; stored logits = scores_eval.npz)
REFERENCES = {
    "NVIDIA A100-PCIE-40GB|torch 2.2.1|tf32 1/1": dict(
        network="PN1_Sb_s403", tar="PN1_Sb_s403.tar",
        tar_sha256="8dec83b880b7bac28db4b6217bc10b58eb78dc65d699734614cf57ae6b444fde",
        scores_eval_sha256="5707f23e224191b7aa294d8fffe93d97274ee9b5e0ddb3244188ab9f8fbf1a1f",
        last_trainable_sha256="a8d12d828116c5a9e596f2d0a446e513227bc79c2afa57b9334b5379614dfbc9",
        stored_by="src/PN1/pn1_score.py (TF32 on), FS1 fit job, NVIDIA A100-PCIE-40GB, driver 610.57.04, torch 2.2.1, "
                  "container smad_torch221_cu121_v1.sif, pn1_eval.csv order, batch 64",
        locations=["/mnt/t7/smad_next/PN1/results_fs/PN1_Sb_s403.tar",
                   "/lustre/pd03/hpc-narolski-1790461090/smad-next/packs/AB1/PN1_Sb_s403.tar"]),
    "NVIDIA H100|torch 2.11.0+cu128|tf32 1/1": dict(
        network="AB1_Sb_s408", tar="AB1_Sb_s408.tar",
        tar_sha256="a84b551f2f18c51898213f4932965f89b88fe7eac0398ac28cd37c04e4b3b0aa",
        scores_eval_sha256="83e3bf359ea39e5b373c453d578c610a7798041efa0d345e7fbf5fc710523a25",
        last_trainable_sha256="656bfcbe1a10c90a601babc50470c7e3b5429ae6d33612bfb60845dfa9a2f804",
        stored_by="src/PN1/pn1_score.py (TF32 on), AB1 fit job 6311579, WCSS r18-8, NVIDIA H100, driver 595.112.07, "
                  "torch 2.11.0+cu128 (~/dmenv), ab1_eval.csv order, batch 64",
        locations=["/mnt/t7/smad_next/AB1/results/AB1_Sb_s408.tar",
                   "/lustre/pd03/hpc-narolski-1790461090/smad-next/results/AB1/AB1_Sb_s408.tar"]),
}


def _smi():
    try:
        q = subprocess.run(["nvidia-smi", "--query-gpu=index,name,uuid,driver_version,compute_cap,memory.total",
                            "--format=csv,noheader"], capture_output=True, text=True, timeout=30)
        return q.stdout.strip()
    except Exception as ex:                       # noqa: BLE001
        return f"nvidia-smi failed: {ex!r}"


def record(device):
    import numpy
    import torch
    r = dict(time=time.strftime("%Y-%m-%d %H:%M:%S %Z"), host=socket.gethostname(), slurm_job=os.environ.get("SLURM_JOB_ID"),
             slurm_array_task=os.environ.get("SLURM_ARRAY_TASK_ID"), python=sys.version.split()[0], machine=_pf.machine(),
             torch=torch.__version__, cuda_runtime=torch.version.cuda, cudnn=torch.backends.cudnn.version(),
             numpy=numpy.__version__, device=str(device), nvidia_smi=_smi(),
             cuda_visible_devices=os.environ.get("CUDA_VISIBLE_DEVICES"))
    for mod in ("timm", "PIL", "safetensors", "huggingface_hub", "scipy", "sklearn"):
        try:
            r[mod] = __import__(mod).__version__
        except Exception:                         # noqa: BLE001
            r[mod] = None
    if str(device).startswith("cuda") and torch.cuda.is_available():
        i = torch.cuda.current_device()
        r.update(gpu_name=torch.cuda.get_device_name(i), gpu_capability=".".join(map(str, torch.cuda.get_device_capability(i))))
    else:
        r.update(gpu_name=None, gpu_capability=None)
    r.update(tf32_matmul=bool(torch.backends.cuda.matmul.allow_tf32), tf32_cudnn=bool(torch.backends.cudnn.allow_tf32),
             cudnn_benchmark=bool(torch.backends.cudnn.benchmark), cudnn_deterministic=bool(torch.backends.cudnn.deterministic),
             deterministic_algorithms=bool(torch.are_deterministic_algorithms_enabled()))
    sdpa = {}
    for k in ("flash_sdp_enabled", "mem_efficient_sdp_enabled", "math_sdp_enabled", "cudnn_sdp_enabled"):
        f = getattr(torch.backends.cuda, k, None)
        sdpa[k] = bool(f()) if callable(f) else None
    r["sdpa"] = sdpa
    r["precision"] = "float32, eval mode, no autocast"
    r["key"] = key(r)
    return r


def key(r):
    return f"{r['gpu_name']}|torch {r['torch']}|tf32 {int(r['tf32_matmul'])}/{int(r['tf32_cudnn'])}"


def gate_rows(dev_rows):
    """the 2,496 gate rows (39 whole stored batches) in order, from the battery's dev set (whose first 19,797 rows are
    the FS1 evaluation order of the stored runs)."""
    out = []
    for k in GATE_BATCHES:
        out += dev_rows[BS * k: BS * k + BS]
    assert len(out) == BS * GATE_N_BATCHES
    return out


def compare(new, stored_ids, stored_logits):
    """byte identity of float32 logits on the gate rows. new: list of (id, float32) in gate order."""
    import numpy as np
    m = dict(zip([str(i) for i in stored_ids], np.asarray(stored_logits, np.float32)))
    ids = [i for i, _ in new]
    a = np.array([v for _, v in new], np.float32)
    b = np.array([m[i] for i in ids], np.float32)
    d = np.abs(a.astype(np.float64) - b.astype(np.float64))
    return dict(n=len(ids), n_differ=int((a != b).sum()), max_abs=float(d.max()), median_abs=float(np.median(d)),
                own_rule_flips=int(((a > 0) != (b > 0)).sum()), stored_range=[float(b.min()), float(b.max())],
                stored_between_m2_p2=int(((b > -2) & (b < 2)).sum()), byte_identical=bool((a == b).all()),
                criterion="byte identity of all float32 logits (fixed in advance)")


def dump(obj, p):
    with open(p, "w") as f:
        json.dump(obj, f, indent=1, default=str)
