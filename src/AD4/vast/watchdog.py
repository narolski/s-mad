"""DGX-side watchdog for the AD4 ViT-B/16 Vast lease (runs detached; the API key never leaves the DGX).

Every 60 s: reads the instance and the account credit; destroys the instance at the cost cap, at the deadline
(8 h after creation), when no queue was started within 60 min, or when the remote queue is done and every finished
task's result is copied back and verified. Each poll copies results (one tar per task + .sha256) to
/mnt/t7/smad_next/AD4/results_vast/, checks sha256, then copies each verified tar to the WCSS results directory
(through the shared flock lock) and checks it there.

  python3 -I watchdog.py --config /mnt/t7/smad_next/AD4/vast/lease.json
"""
import argparse
import hashlib
import json
import pathlib
import subprocess
import sys
import time

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))
import vast_api as V  # noqa: E402

SSH_KEY = "/home/narolski/.config/smad-next/vast_ssh_key"
LOCK = "/tmp/opencode/wcss-client.lock"
WCSS = "narolski@ui.wcss.pl"
WCSS_RES = "/lustre/pd03/hpc-narolski-1790461090/smad-next/results/AD4"
TASKS = [f"AD4_m3{a}_s{s}" for a in ("mf", "perm") for s in (401, 402, 403, 404, 405)]


def sha(p):
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for b in iter(lambda: f.read(1 << 20), b""):
            h.update(b)
    return h.hexdigest()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--config", required=True)
    a = ap.parse_args()
    cp = pathlib.Path(a.config)
    root = cp.parent
    dest = pathlib.Path("/mnt/t7/smad_next/AD4/results_vast")
    dest.mkdir(parents=True, exist_ok=True)
    state_f = root / "wcss_copied.json"
    wcss_done = set(json.loads(state_f.read_text())) if state_f.exists() else set()

    def log(**v):
        with open(root / "watchdog.jsonl", "a") as f:
            f.write(json.dumps(dict(unix=round(time.time(), 1), **v)) + "\n")

    def sshopts(cfg):
        return ["-o", "BatchMode=yes", "-o", "ConnectTimeout=10", "-o", "StrictHostKeyChecking=accept-new",
                "-o", f"UserKnownHostsFile={root / 'known_hosts'}", "-i", SSH_KEY, "-p", str(cfg["ssh_port"])]

    def rssh(cfg, cmd, timeout=60):
        return subprocess.run(["ssh", *sshopts(cfg), f"root@{cfg['ssh_host']}", cmd], capture_output=True,
                              text=True, timeout=timeout)

    def pull(cfg):
        e = "ssh " + " ".join(sshopts(cfg))
        p1 = subprocess.run(["rsync", "-a", "--partial", "--timeout=60", "-e", e,
                             f"root@{cfg['ssh_host']}:/workspace/ad4/root/smad-next/results/AD4/", str(dest) + "/"],
                            capture_output=True, text=True, timeout=1200)
        p2 = subprocess.run(["rsync", "-a", "--timeout=60", "-e", e,
                             f"root@{cfg['ssh_host']}:/workspace/ad4/logs", f"root@{cfg['ssh_host']}:/workspace/ad4/rc",
                             f"root@{cfg['ssh_host']}:/workspace/ad4/queue.log", str(root / "remote") + "/"],
                            capture_output=True, text=True, timeout=300)
        return p1.returncode, p2.returncode

    def verified():
        ok = []
        for t in TASKS:
            tar, s = dest / f"{t}.tar", dest / f"{t}.tar.sha256"
            if tar.is_file() and s.is_file() and s.read_text().split()[0] == sha(tar):
                ok.append(t)
        return ok

    def to_wcss(t):
        tar, s = dest / f"{t}.tar", dest / f"{t}.tar.sha256"
        p = subprocess.run(["flock", "-w", "120", LOCK, "rsync", "-a", str(tar), str(s), f"{WCSS}:{WCSS_RES}/"],
                           capture_output=True, text=True, timeout=600)
        if p.returncode:
            return False
        q = subprocess.run(["flock", "-w", "120", LOCK, "ssh", "-o", "BatchMode=yes", WCSS,
                            f"cd {WCSS_RES} && sha256sum -c --quiet {t}.tar.sha256 && echo OK"],
                           capture_output=True, text=True, timeout=300)
        return q.returncode == 0 and "OK" in q.stdout

    cfg = json.loads(cp.read_text())
    log(event="WATCHDOG_STARTED", instance_id=cfg["instance_id"], cap=cfg["cap_usd"], deadline=cfg["deadline_epoch"])
    destroyed = False
    while True:
        try:
            cfg = json.loads(cp.read_text())
            iid = cfg["instance_id"]
            now = time.time()
            elapsed = now - cfg["created_epoch"]
            try:
                credit = V.balance()["credit"]
            except SystemExit as e:
                credit = None
                log(event="BALANCE_ERROR", msg=str(e)[:300])
            spent = (cfg["credit_start"] - credit) if credit is not None else None
            est = elapsed / 3600 * cfg["dph"] * 1.05 + 0.10
            upper = max(est, spent or 0.0)
            inst = V.call("GET", f"/instances/{iid}/", params={"owner": "me"}).get("instances")
            if not inst:
                log(event="INSTANCE_ABSENT", spent=spent, est=est)
                (root / "TERMINATED.json").write_text(json.dumps(dict(instance_id=iid, spent=spent, est=est,
                                                                       elapsed_s=elapsed)))
                return
            status = inst.get("actual_status")
            (root / "LIVE_BUDGET.json").write_text(json.dumps(dict(instance_id=iid, status=status, elapsed_s=elapsed,
                                                                   est_usd=est, credit_spent_usd=spent,
                                                                   upper_usd=upper, cap_usd=cfg["cap_usd"]), indent=1))
            reason = None
            if upper >= cfg["cap_usd"]:
                reason = "COST_CAP"
            elif now >= cfg["deadline_epoch"]:
                reason = "DEADLINE_8H"
            done = False
            if status == "running" and cfg.get("ssh_host"):
                rc1, rc2 = pull(cfg)
                ok = verified()
                for t in ok:
                    if t not in wcss_done and to_wcss(t):
                        wcss_done.add(t)
                        state_f.write_text(json.dumps(sorted(wcss_done)))
                        log(event="WCSS_COPIED", task=t)
                qs = rssh(cfg, "test -f /workspace/ad4/QUEUE_STARTED && echo Q; test -f /workspace/ad4/ALL_DONE && echo D")
                started, alldone = "Q" in qs.stdout, "D" in qs.stdout
                log(event="POLL", status=status, upper=round(upper, 3), spent=spent, verified=len(ok),
                    wcss=len(wcss_done), started=started, alldone=alldone, pull_rc=[rc1, rc2])
                if not started and elapsed > 3600 and not cfg.get("hold"):
                    reason = reason or "NO_QUEUE_60MIN"
                if alldone:
                    rcs = {p.name: p.read_text().strip() for p in (root / "remote" / "rc").glob("*")} \
                        if (root / "remote" / "rc").is_dir() else {}
                    finished_ok = [t for t, r in rcs.items() if r == "0"]
                    if all(t in ok for t in finished_ok):
                        done = True
                        reason = reason or "QUEUE_DONE_COPYBACK_VERIFIED"
            if reason and not destroyed:
                if status == "running" and cfg.get("ssh_host"):
                    pull(cfg)          # last copy-back attempt before destroy
                    for t in verified():
                        if t not in wcss_done and to_wcss(t):
                            wcss_done.add(t)
                            state_f.write_text(json.dumps(sorted(wcss_done)))
                r = V.call("DELETE", f"/instances/{iid}/", json={})
                destroyed = True
                log(event="DESTROY_REQUESTED", reason=reason, response=r, upper=upper, done=done)
                (root / "DESTROY_REQUESTED.json").write_text(json.dumps(dict(instance_id=iid, reason=reason,
                                                                              response=r, upper_usd=upper)))
        except SystemExit as e:
            log(event="API_ERROR", msg=str(e)[:400])
        except Exception as e:  # noqa: BLE001
            log(event="ERROR", type=type(e).__name__, msg=str(e)[:400])
        time.sleep(60)


if __name__ == "__main__":
    main()
