"""Durable create-only read claim and exactly one terminal disposition."""
import hashlib
import json
import os
import pathlib


def exclusive_json(path,value):
    p=pathlib.Path(path)
    fd=os.open(p,os.O_WRONLY|os.O_CREAT|os.O_EXCL,0o600)
    try:
        with os.fdopen(fd,'w') as f:
            json.dump(value,f,indent=2,allow_nan=False);f.write('\n');f.flush();os.fsync(f.fileno())
    finally:
        d=os.open(p.parent,os.O_RDONLY)
        try:os.fsync(d)
        finally:os.close(d)


class Journal:
    def __init__(self,root):self.root=pathlib.Path(root)
    def claim(self,value):
        self.root.mkdir(parents=True,exist_ok=True)
        exclusive_json(self.root/'CLAIM.json',value)
    def finish(self,status,value):
        assert status in ('COMPLETE','FAILED')
        assert (self.root/'CLAIM.json').is_file()
        exclusive_json(self.root/'TERMINAL.json',dict(value,status=status))


def atomic_result(path,value):
    p=pathlib.Path(path);temp=p.with_name(p.name+'.part')
    exclusive_json(temp,value)
    # Hard-link creates the final name atomically and NEVER replaces an old result.
    os.link(temp,p);temp.unlink()
    d=os.open(p.parent,os.O_RDONLY)
    try:os.fsync(d)
    finally:os.close(d)
    return hashlib.sha256(p.read_bytes()).hexdigest()
