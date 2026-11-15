"""Same-capture pattern grounded in runtimephase1 authority.py
SHAe52d657ae5c73001e870964c810f94470fc336a0f161b9caaef67b3023b8b257; no mutable import .
Hardened regular/bounded same-captured-bytes control snapshots for VIS3v2r1.
Root supplies the release digest EXTERNALLY. This helper never derives authority from Git/path state.
"""
from dataclasses import dataclass
import hashlib
import json
import math
import os
from pathlib import Path
import re
import stat

MAX_CONTROL_BYTES=1<<20


@dataclass(frozen=True)
class Snapshot:
    path:str
    raw:bytes
    sha256:str
    value:object=None


def require(ok,message):
    if not ok:raise ValueError(message)


def capture_bytes(path,expected,cap=MAX_CONTROL_BYTES):
    require(isinstance(expected,str) and re.fullmatch('[0-9a-f]{64}',expected),'external expected SHA256 required')
    require(isinstance(cap,int) and 0<cap<=MAX_CONTROL_BYTES,'invalid control cap')
    flags=os.O_RDONLY|os.O_NOFOLLOW|os.O_NONBLOCK
    fd=os.open(path,flags)
    try:
        before=os.fstat(fd)
        require(stat.S_ISREG(before.st_mode) and before.st_size<=cap,'control must be bounded regular file')
        chunks=[];total=0
        while True:
            piece=os.read(fd,cap+1-total)
            if not piece:break
            total+=len(piece);require(total<=cap,'oversize control')
            chunks.append(piece)
        after=os.fstat(fd)
        require((before.st_dev,before.st_ino,before.st_size,before.st_mtime_ns,before.st_ctime_ns)==
                (after.st_dev,after.st_ino,after.st_size,after.st_mtime_ns,after.st_ctime_ns),'control mutated during capture')
    finally:os.close(fd)
    raw=b''.join(chunks);digest=hashlib.sha256(raw).hexdigest()
    require(digest==expected,'captured control hash mismatch')
    return Snapshot(str(path),raw,digest)


def _pairs(pairs):
    result={}
    for key,value in pairs:
        require(key not in result,'duplicate JSON control key');result[key]=value
    return result


def _constant(value):raise ValueError('nonfinite JSON control')


def _float(value):
    result=float(value);require(math.isfinite(result),'nonfinite JSON number');return result


def capture_json(path,expected,cap=MAX_CONTROL_BYTES,kind=dict):
    snapshot=capture_bytes(path,expected,cap)
    value=json.loads(snapshot.raw,object_pairs_hook=_pairs,parse_constant=_constant,parse_float=_float)
    require(isinstance(value,kind),'invalid JSON control root schema')
    return Snapshot(snapshot.path,snapshot.raw,snapshot.sha256,value)


def manifest_entries(snapshot):
    names=set();rows=[]
    for line in snapshot.raw.decode('utf8').splitlines():
        require(bool(re.fullmatch(r'[0-9a-f]{64}  [A-Za-z0-9_][A-Za-z0-9_.-]*',line)),'unsafe manifest line')
        digest,name=line.split('  ',1)
        require(name not in names and name not in ('.','..'),'duplicate/unsafe manifest name')
        names.add(name);rows.append((digest,name))
    require(bool(rows),'empty source manifest')
    return rows
