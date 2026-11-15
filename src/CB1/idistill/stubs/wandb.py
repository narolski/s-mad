"""CB1 stub: W&B logging disabled (no network on compute nodes); every call is a no-op."""
def login(*a, **k): return True
def init(*a, **k): return None
def watch(*a, **k): return None
def log(*a, **k): return None
def finish(*a, **k): return None
