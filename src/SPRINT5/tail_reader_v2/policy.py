"""Adopted primary/NI policy; diagnostics and auxiliaries remain separately held."""
EXPERIMENT='SPRINT5_3'
ARMS=('bce','mean','cvar')
SEEDS=(521,522,523,524,525)
CONTRASTS=(('cvar_minus_mean',2,1),('bce_minus_mean',0,1))
FAMILIES=('af0_u50','af0_u5061','lad_R4','lad_S4')
CELLS=tuple((s,p) for s in ('feret','frgc') for p in ('native','s61','s112'))
TRAIN_SOURCE='9b50eff7aa5a90f72be7330e3550b0f8a76917dcac9b89516cc0a64ae7086ae1'
STEPS=100
BATCH=256
FORWARDS=25600
DRAWS=10000
RNG=2026111403
NI_ALPHA=.00625
NI_MARGIN=-.02
NI_MIN_COMPONENTS=20
POLICY_BINDING_SHA='007a6fbdb25221d9069a304b5cc25a789dcf9177ef5480e7ad4201908a54d414'
PACKET_SHA='4268acf24217e26342f64f6a0294fa60ccc911489f131825d579464a9a7fbc9b'
REFERENCE_SHA='5d1c7d0ebc4efa558d432011d5c45a87b93f95836fe161c1e2157b3fc469b5db'
ONCE='/mnt/t7/smad_next/SPRINT5_3/reader_once_primary_ni_v1'
OUTPUT='/mnt/t7/smad_next/SPRINT5_3/reader_output_primary_ni_v1/RESULT.json'
ROOT='/home/narolski/smad-next'
BINDING=ROOT+'/experiments/SPRINT5_20261114/tail/reader_implementation_v2/PILOT_READER_BINDING.json'
POLICY_ROOT=ROOT+'/experiments/SPRINT5_20261114/pilot_reader_policy_review'
SCOPE='TAIL_POSITIVE_CALIBRATED_PRIMARY_NI_DIAGNOSTICS_V2'
DIAGNOSTIC_ADOPTION_SHA='3c679d59e513ab3fd405f73ee164229c7914bac80cd1afc650ed824942102f17'


def task(arm,seed):
    assert arm in ARMS and seed in SEEDS
    return f'SPRINT5_3_pilot_v1_{arm}_s{seed}'
