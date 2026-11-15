"""Distinct metadata/scientific releases; no payload decoding or primary computation."""
import pathlib
import re
import bridge
import metadata as M
import policy as P


def source_check(code,expected):
    M.need(bridge.sha(code/'SHA256SUMS')==expected,'auxiliary source manifest changed')
    for line in (code/'SHA256SUMS').read_text().splitlines():
        h,name=line.split('  ',1);path=code/name
        M.need(path.resolve().is_relative_to(code.resolve()) and bridge.sha(path)==h,'auxiliary source dependency changed')


def validate_release(release,binding_path,code,decision):
    scope=P.TECH_SCOPE if decision==P.TECH_GO else P.READ_SCOPE
    M.need(release['decision']==decision and release['scope']==scope and release['experiment_id']==P.EXPERIMENT,'wrong auxiliary phase/scope')
    M.need(release['timing']==P.TIMING and release['policy_adoption_sha256']==P.POLICY_SHA,'after-primary policy missing')
    M.need(release['author']!=release['reviewer'] and release['reviewer'],'auxiliary cannot self-release')
    M.need(bridge.sha(binding_path)==release['binding_sha256'],'auxiliary binding changed')
    source_check(code,release['source_sums_sha256'])
    M.need(bridge.sha(release['independent_review_path'])==release['independent_review_sha256'],'independent review changed')
    M.need(bridge.sha(release['input_admission_path'])==release['input_admission_sha256'],'root input admission changed')
    adopted=M.obj(release['input_admission_path'])
    M.need(adopted['decision']=='GO_AUXILIARY_INPUT_BINDING_ONLY' and adopted['binding_sha256']==release['binding_sha256'] and adopted['source_sums_sha256']==release['source_sums_sha256'],'auxiliary input/code not adopted')
    M.need(adopted['author']!=adopted['reviewer'] and adopted['reviewer'] and adopted['policy_adoption_sha256']==P.POLICY_SHA,'input adoption cannot self-approve')
    M.need(adopted['scientific_auxiliary_read']=='HOLD' and adopted['technical_member_access']=='HOLD','input adoption cannot grant live access')
    M.need(release['baseline_archive_sha256']==P.BASELINE_SHA and release['baseline_score_member']==P.MEMBER,'baseline substitution')
    if decision==P.TECH_GO:
        M.need(release['technical_directory']==P.TECHDIR and release['array_deserialization'] is False and release['scientific_auxiliary_read']=='HOLD','technical cannot decode arrays or read science')
    else:
        M.need((release['auxiliary_once'],release['auxiliary_output'])==(P.ONCE,P.OUTPUT),'alternate auxiliary claim/output')
        M.need(release['new_primary_read'] is False and release['candidate_reopening']=='EXACT15_EVALUATION468_ONLY','primary retry or broad candidate scope')
        M.need(release['full_container_validation_after_auxiliary_claim_only'] is True and release['allowed_baseline_numeric_ids']==538 and release['allowed_candidate_numeric_ids']==468,'serialization exception/allowlist missing')
        M.need(release['uncertainty_status']=='NOT_ESTIMATED_DESCRIPTIVE_AUXILIARY' and release['interval'] is None,'unapproved CI')
    return release


def technical_receipt(path):
    M.need(str(pathlib.Path(path))==P.TECH_RECEIPT,'alternate baseline technical receipt')
    t=M.obj(path)
    M.need(t['status']=='TECHNICAL_BASELINE_METADATA_HASH_CAPTURED_NO_ARRAY_DECODE','baseline technical capture failed')
    M.need(t['baseline_archive_sha256']==P.BASELINE_SHA and t['score_member']==P.MEMBER,'baseline technical target changed')
    M.need(re.fullmatch('[0-9a-f]{64}',t['score_member_sha256']) and t['array_deserialization'] is False,'missing opaque member digest')
    M.need(t['source_identity_check']=='PASS' and t['runtime_provenance_status']=='PASS_RECORDED_TORCH_H100_AND_PINNED_SCORER_SOURCE','baseline source/runtime incomplete')
    M.need(t['payload_ID_schema_finiteness']=='UNKNOWN_UNTIL_AUXILIARY_CLAIM','technical cannot pre-read numerical arrays')
    return t


def admit(release_path,technical=False):
    code=pathlib.Path(__file__).resolve().parent;r=M.obj(release_path)
    validate_release(r,pathlib.Path(P.BINDING),code,P.TECH_GO if technical else P.READ_GO)
    b,meta=M.validate(require_committed=True)
    if technical:return b,meta,r,None
    M.need(r['technical_receipt_path']==P.TECH_RECEIPT and bridge.sha(P.TECH_RECEIPT)==r['technical_receipt_sha256'],'technical receipt changed')
    t=technical_receipt(P.TECH_RECEIPT)
    M.need(t['binding_sha256']==bridge.sha(P.BINDING) and t['source_sums_sha256']==r['source_sums_sha256'],'unreviewed technical source/binding')
    M.need(bridge.sha(r['baseline_technical_admission_path'])==r['baseline_technical_admission_sha256'],'technical admission changed')
    a=M.obj(r['baseline_technical_admission_path'])
    M.need(a['decision']=='GO_BASELINE_AUXILIARY_TECHNICAL_INPUTS_ONLY' and a['technical_receipt_sha256']==r['technical_receipt_sha256'],'technical inputs not independently admitted')
    M.need(a['reviewer'] and a['author']!=a['reviewer'] and a['runtime_and_bytegate_status']=='PASS_SAME_BASELINE_ADMITTED_METADATA','runtime/bytegate unknown or self-admitted')
    M.need(a['same_baseline_existing_gate_reuse_authorized'] is True and a['baseline_gate_chain_sha256']==b['baseline_gate_chain_sha256'],'same-baseline gate reuse not bound')
    M.need(bridge.sha(a['independent_review_path'])==a['independent_review_sha256'],'technical review changed')
    for entry in [dict(archive_path=P.BASELINE,archive_sha256=P.BASELINE_SHA),*b['candidates']]:
        M.need(bridge.sha(entry['archive_path'])==entry['archive_sha256'],'opaque archive changed')
    return b,meta,r,t
