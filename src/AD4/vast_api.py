"""Minimal Vast REST client for the AD4 lease. The API key is read from a file, sent only to console.vast.ai, and never
printed, logged or copied to a rented machine. Errors are printed with the key redacted.

  python3 -I vast_api.py balance
  python3 -I vast_api.py search            # ranked offers for the AD4 ViT-B/16 lease
  python3 -I vast_api.py instances         # our instances (id, label, status, gpu, $/h)
  python3 -I vast_api.py show ID
  python3 -I vast_api.py create OFFER_ID LABEL DISK_GB
  python3 -I vast_api.py destroy ID
"""
import json
import pathlib
import sys

import requests

KEY_FILE = pathlib.Path("/home/narolski/.config/smad-next/vast_api_key")
BASE = "https://console.vast.ai/api/v0"
IMAGE = "pytorch/pytorch:2.2.1-cuda12.1-cudnn8-runtime"


def key():
    return KEY_FILE.read_text().strip()


def call(method, path, **kw):
    k = key()
    try:
        r = requests.request(method, BASE + path, headers={"Authorization": "Bearer " + k}, timeout=30, **kw)
    except Exception as e:  # noqa: BLE001
        raise SystemExit(f"request error: {type(e).__name__}: {str(e).replace(k, '[REDACTED]')[:400]}")
    if r.status_code >= 400:
        raise SystemExit(f"HTTP {r.status_code}: {r.text.replace(k, '[REDACTED]')[:600]}")
    return r.json()


def balance():
    u = call("GET", "/users/current/")
    return {"credit": u.get("credit"), "balance": u.get("balance"), "total_spend": u.get("total_spend")}


def instances():
    out = []
    for i in call("GET", "/instances/", params={"owner": "me"}).get("instances", []):
        out.append({k: i.get(k) for k in ("id", "label", "actual_status", "cur_state", "gpu_name", "num_gpus",
                                           "dph_total", "ssh_host", "ssh_port", "start_date")})
    return out


def search(gpus=("RTX 4090", "RTX 5090", "RTX 3090"), ngpu_min=2):
    q = {"verified": {"eq": True}, "rentable": {"eq": True}, "external": {"eq": False},
         "reliability2": {"gte": 0.98}, "num_gpus": {"gte": ngpu_min, "lte": 4}, "gpu_name": {"in": list(gpus)},
         "cuda_max_good": {"gte": 12.4}, "inet_down": {"gte": 200}, "disk_space": {"gte": 80},
         "cpu_cores_effective": {"gte": 16}, "type": "on-demand", "order": [["dph_total", "asc"]], "limit": 40}
    offers = call("POST", "/bundles/", json=q).get("offers", [])
    rows = []
    for o in offers:
        rows.append({k: o.get(k) for k in ("id", "gpu_name", "num_gpus", "gpu_ram", "dph_total", "reliability2",
                                           "inet_down", "inet_up", "cuda_max_good", "cpu_cores_effective",
                                           "cpu_ram", "disk_space", "cpu_name", "geolocation", "verification",
                                           "dlperf", "machine_id", "host_id")})
    return rows


def create(offer, label, disk):
    body = {"client_id": "me", "image": IMAGE, "label": label, "disk": int(disk), "runtype": "ssh_direct ssh_proxy"}
    return call("PUT", f"/asks/{int(offer)}/", json=body)


def main():
    cmd = sys.argv[1]
    if cmd == "balance":
        print(json.dumps(balance()))
    elif cmd == "instances":
        print(json.dumps(instances(), indent=1))
    elif cmd == "search":
        for r in search():
            print(json.dumps(r))
    elif cmd == "show":
        i = call("GET", f"/instances/{int(sys.argv[2])}/", params={"owner": "me"}).get("instances") or {}
        print(json.dumps({k: i.get(k) for k in ("id", "label", "actual_status", "cur_state", "gpu_name", "num_gpus",
                                                 "dph_total", "ssh_host", "ssh_port", "status_msg", "gpu_ram",
                                                 "public_ipaddr", "direct_port_start")}, indent=1))
    elif cmd == "create":
        print(json.dumps(create(sys.argv[2], sys.argv[3], sys.argv[4])))
    elif cmd == "destroy":
        print(json.dumps(call("DELETE", f"/instances/{int(sys.argv[2])}/", json={})))
    else:
        raise SystemExit(f"unknown command {cmd}")


if __name__ == "__main__":
    main()
