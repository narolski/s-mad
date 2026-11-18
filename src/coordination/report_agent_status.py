"""Refresh local status from recorded observations; does not query live agent registry."""
import datetime,hashlib,json,pathlib,subprocess,shutil
root=pathlib.Path('/home/narolski/smad-next');out=pathlib.Path('/mnt/t7/smad_next/agent_status_reports');out.mkdir(parents=True,exist_ok=True)
now=datetime.datetime.now().astimezone();snapshot=json.loads((out/'agent_observations.json').read_text())
previous=json.loads((out/'latest.json').read_text()) if (out/'latest.json').exists() else {}
files={}
for pattern in ['AGENT_STATUS.md','manuscript_cvpr2027/*ASTRA.md','experiments/AGENTIC_delivery_20261114/*.md','experiments/AGENTIC_delivery_20261114/workflow_state.json']:
 for p in root.glob(pattern):
  files[str(p.relative_to(root))]={'sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'modified_at':datetime.datetime.fromtimestamp(p.stat().st_mtime).astimezone().isoformat()}
changed=[k for k,v in files.items() if previous.get('files',{}).get(k,{}).get('sha256')!=v['sha256']]
report={'generated_at':now.isoformat(),'agent_observations':snapshot,'live_registry_polled':False,'changed_files':changed,'files':files}
text=['# Agent work status',f'Generated: {now.isoformat()}',f'Agent states last verified: {snapshot["observed_at"]}','This report refreshes saved evidence, not the live Codex agent registry. An old observation is not proof of current activity.','', '| Agent | Last verified state |','|---|---|']
text += [f'| {a} | {s} |' for a,s in snapshot['agents'].items()]
text+=['','## Deliverable changes since preceding report']+[f'- {k}' for k in changed]
if not changed:text+=['No recorded deliverable changes.']
text+=['','Full task outputs and blockers: /home/narolski/smad-next/AGENT_STATUS.md','No automatic chat delivery or agent activation is performed.']
for name,data in [('latest.json',json.dumps(report,indent=2)+'\n'),('latest.md','\n'.join(text)+'\n')]:
 tmp=out/(name+'.tmp');tmp.write_text(data);tmp.replace(out/name)
with (out/'history.jsonl').open('a') as f:f.write(json.dumps({'generated_at':report['generated_at'],'observation_time':snapshot['observed_at'],'changed_files':changed})+'\n')
if shutil.which('notify-send'):
 subprocess.run(['notify-send','S-MAD agent status',f'{len(changed)} deliverable changes. Report: {out}/latest.md'],capture_output=True,timeout=10)
print(out/'latest.md')
