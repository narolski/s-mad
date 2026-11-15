"""Bounded single-read authority snapshots; parsed bytes are exactly pinned bytes."""
import hashlib,json
MAX_AUTHORITY_BYTES=1<<20
def capture_bytes(path,expected,cap=MAX_AUTHORITY_BYTES):
 with open(path,'rb') as f:raw=f.read(cap+1)
 if len(raw)>cap or hashlib.sha256(raw).hexdigest()!=expected:raise ValueError('authority size/hash')
 return raw
def capture_json(path,expected,cap=MAX_AUTHORITY_BYTES):
 return json.loads(capture_bytes(path,expected,cap))
