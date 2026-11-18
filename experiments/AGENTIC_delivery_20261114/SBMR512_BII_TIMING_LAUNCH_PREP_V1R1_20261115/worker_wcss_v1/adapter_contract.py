"""Sealed supplement association only; no kernel statistic or payload reads."""
from design import SPECS,SEEDS
def validate_attachment(records,authority):
 assert len(records)==5 and {r["seed"] for r in records}==set(SEEDS)
 assert len({r["sealed_sha256"] for r in records})==5
 for r in records:
  known=authority["trainable_overlays"][str(r["seed"])]
  assert r["archive_sha256"]==known["archive_sha256"]
  assert r["trainable_sha256"]==known["trainable_member"]["sha256"]
  assert r["specs"]==list(SPECS) and r["shape"]==[14,13771] and r["dtype"]=="float32"
  assert r["native_bytegate"] is True and r["scientific_interpretation"]=="PENDING_EXISTING_NEXT_ONCE"
 return records
