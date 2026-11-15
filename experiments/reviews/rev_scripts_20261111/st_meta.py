import json, struct, sys
p = sys.argv[1]
with open(p, "rb") as f:
    n = struct.unpack("<Q", f.read(8))[0]
    h = json.loads(f.read(n))
print("metadata:", h.get("__metadata__"))
print("n tensors:", len(h) - ("__metadata__" in h))
