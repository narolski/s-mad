"""Writes /mnt/t7/smad_next/AD4/vast/lease.json for watchdog.py from the instance details the main session sends.

  python3 make_lease.py --instance ID --host HOST --port PORT --dph USD_PER_H --created EPOCH --credit-start USD

--created: Unix time of the creation call (the 8 h deadline counts from it); --credit-start: Vast credit read right
before creation (the cap is checked against the drop in credit and against elapsed x dph). Cap 9.6 USD (10 USD minus
a 0.4 USD margin for billing granularity). Refuses to overwrite an existing lease.json.
"""
import argparse
import json
import pathlib

ap = argparse.ArgumentParser()
ap.add_argument("--instance", type=int, required=True)
ap.add_argument("--host", required=True)
ap.add_argument("--port", type=int, required=True)
ap.add_argument("--dph", type=float, required=True)
ap.add_argument("--created", type=float, required=True)
ap.add_argument("--credit-start", type=float, required=True)
ap.add_argument("--cap", type=float, default=9.6)
a = ap.parse_args()
p = pathlib.Path("/mnt/t7/smad_next/AD4/vast/lease.json")
if p.exists():
    raise SystemExit(f"{p} exists")
p.parent.mkdir(parents=True, exist_ok=True)
cfg = dict(label="smad-next-AD4-vitb16-20261111", instance_id=a.instance, ssh_host=a.host, ssh_port=a.port,
           dph=a.dph, cap_usd=a.cap, credit_start=a.credit_start, created_epoch=a.created,
           deadline_epoch=a.created + 8 * 3600, hold=True,
           authority="author approved run on Vast (via lead, 11 Nov); one lease, ten ViT-B/16 tasks, cap 10 USD")
p.write_text(json.dumps(cfg, indent=1))
print(json.dumps(cfg))
