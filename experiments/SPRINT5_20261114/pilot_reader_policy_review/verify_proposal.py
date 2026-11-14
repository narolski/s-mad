"""Pinned input/source verification only; no candidate path is admitted."""
import hashlib,json,pathlib
O=pathlib.Path(__file__).resolve().parent
sha=lambda p:hashlib.sha256(pathlib.Path(p).read_bytes()).hexdigest()
b=json.loads((O/'BINDING_PROPOSAL.json').read_text());assert b['status']=='PROPOSAL_ONLY_REQUIRES_ROOT_INDEPENDENT_POLICY_REVIEW';assert sha(b['shared_input_binding_path'])==b['shared_input_binding_sha256']
for p,h in b['input_pins'].items():assert sha(p)==h,p
print('PROPOSAL_INPUT_AND_SOURCE_PINS_PASS; NO_READ_RELEASE')
