"""Guard for one rented machine that an experiment owner operates over SSH (lead-side, runs on the DGX).

  python3 guard.py --config /mnt/t7/smad_next/vast/<NAME>/lease.json

Every 60 s: reads the instance; destroys it when (a) elapsed time times the hourly price reaches cap_usd, (b) the
deadline passes, or (c) the file RELEASE appears beside lease.json (the owner writes it after every result has been
copied back and its hash verified). Writes guard.jsonl and LIVE.json beside lease.json. It never copies data: the
owner does. The credit of the account is logged but not used for the cap, because other rented machines may run at
the same time.

NOT YET RUN (11 Nov 2026): written while the rental itself awaited the author's confirmation.
"""
import argparse
import json
import pathlib
import sys
import time

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1] / "AD4"))
import vast_api as V

ap = argparse.ArgumentParser()
ap.add_argument("--config", required=True)
a = ap.parse_args()
cp = pathlib.Path(a.config)
root = cp.parent


def log(**v):
    v = dict(unix=round(time.time(), 1), **v)
    with open(root / "guard.jsonl", "a") as f:
        f.write(json.dumps(v) + "\n")


cfg = json.loads(cp.read_text())
log(event="GUARD_STARTED", instance_id=cfg["instance_id"], cap=cfg["cap_usd"], deadline=cfg["deadline_epoch"])
while True:
    try:
        cfg = json.loads(cp.read_text())
        iid = cfg["instance_id"]
        now = time.time()
        inst = V.call("GET", f"/instances/{int(iid)}/", params={"owner": "me"}).get("instances") or {}
        status = inst.get("actual_status")
        dph = float(inst.get("dph_total") or cfg.get("dph") or 1.0)
        est = (now - cfg["created_epoch"]) / 3600.0 * dph
        try:
            credit = V.balance()["credit"]
        except BaseException:
            credit = None
        (root / "LIVE.json").write_text(json.dumps(dict(
            instance_id=iid, status=status, dph=dph, est_usd=round(est, 3), cap_usd=cfg["cap_usd"], credit=credit,
            hours=round((now - cfg["created_epoch"]) / 3600, 2)), indent=1))
        if not inst:
            log(event="INSTANCE_GONE")
            break
        reason = None
        if est >= cfg["cap_usd"]:
            reason = "cap"
        elif now >= cfg["deadline_epoch"]:
            reason = "deadline"
        elif (root / "RELEASE").exists():
            reason = "released by owner"
        if reason:
            r = V.call("DELETE", f"/instances/{int(iid)}/", json={})
            log(event="DESTROYED", reason=reason, est_usd=round(est, 3), reply=str(r)[:200])
            break
        log(event="POLL", status=status, est=round(est, 3), credit=credit)
    except BaseException as e:  # keep guarding through API hiccups
        log(event="ERROR", error=repr(e)[:300])
    time.sleep(60)
