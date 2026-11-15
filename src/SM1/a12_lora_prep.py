"""SM1 amendment A12 item 10: the audit manifest for the scoring-only LoRA jobs, packed for Athena.

  sm1_audit_eval.csv  ad4_eval.csv columns (id,path,set,family,label,variant,src_id): the 10,055 audit images of
                      flists/audit.csv, path "x/" + the absolute DGX path (inside sm1gpu_img_audit.tar), set = audit,
                      family = partner kind (KP, KU, KE, KX, PP, UU), label 1
-> OUT/lora/manifests_audit/sm1_audit_eval.csv and OUT/gpupack/sm1lora_manifests_audit.tar (+ .sha256)

  python3 -I a12_lora_prep.py
"""
import csv
import hashlib
import json
import pathlib
import sys
import tarfile

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import sm1_common as K  # noqa: E402


def main():
    if not sys.flags.isolated:
        sys.exit("run with python3 -I")
    od = K.OUT / "lora/manifests_audit"
    od.mkdir(parents=True, exist_ok=True)
    rows = [dict(id=r["id"], path="x/" + r["path"].lstrip("/"), set="audit", family=r["kind"], label=1, variant="",
                 src_id=r["id"]) for r in csv.DictReader(open(K.OUT / "flists/audit.csv"))]
    f = od / "sm1_audit_eval.csv"
    with open(f, "w", newline="") as fo:
        w = csv.DictWriter(fo, fieldnames=list(rows[0]), lineterminator="\n")
        w.writeheader()
        w.writerows(rows)
    tp = K.OUT / "gpupack/sm1lora_manifests_audit.tar"
    with tarfile.open(tp, "w") as t:
        t.add(f, arcname=f.name)
    sha = hashlib.sha256(open(tp, "rb").read()).hexdigest()
    (tp.parent / (tp.name + ".sha256")).write_text(f"{sha}  {tp.name}\n")
    print(json.dumps(dict(n=len(rows), manifest_sha256=K.sha(f), tar=str(tp), tar_sha256=sha)))


if __name__ == "__main__":
    main()
