"""Instrument exact AD5 packed source, scratch only. No model/weight/data loading here."""
import argparse, hashlib, json
from pathlib import Path

p=argparse.ArgumentParser();p.add_argument('code_root',type=Path);a=p.parse_args()
f=a.code_root/'build/madation_src/src/training/trainer.py'
b=f.read_bytes();expected='e905cc241327d0a6f809ef3188ac395353ee4e502e3d91409892f89890b5f55d'
assert hashlib.sha256(b).hexdigest()==expected, 'wrong packed trainer'
s=b.decode()
old='''                features_image = self.model.module.encode_image(images)
                _, loss_image = self.header(F.normalize(features_image), target)

                loss_image.backward()'''
new='''                # Diagnostic only: exact first forward/backward, no optimizer update/save.
                import json
                print('AD5_BACKWARD_DIAG_INPUT', json.dumps(dict(
                    images_shape=list(images.shape), images_dtype=str(images.dtype),
                    target_shape=list(target.shape), target_dtype=str(target.dtype),
                    torch=torch.__version__, cuda=torch.version.cuda,
                    device=torch.cuda.get_device_name(self.rank),
                    flash_enabled=torch.backends.cuda.flash_sdp_enabled(),
                    mem_efficient_enabled=torch.backends.cuda.mem_efficient_sdp_enabled(),
                    math_enabled=torch.backends.cuda.math_sdp_enabled())), flush=True)
                torch.cuda.synchronize()
                print('AD5_BACKWARD_DIAG_PRE_FORWARD', flush=True)
                with torch.autograd.detect_anomaly(check_nan=False):
                    features_image = self.model.module.encode_image(images)
                    torch.cuda.synchronize()
                    print('AD5_BACKWARD_DIAG_ENCODER_OK', flush=True)
                    _, loss_image = self.header(F.normalize(features_image), target)
                    torch.cuda.synchronize()
                    print('AD5_BACKWARD_DIAG_HEADER_OK', flush=True)
                    loss_image.backward()
                    torch.cuda.synchronize()
                print('AD5_BACKWARD_DIAG_COMPLETE_NO_UPDATE', flush=True)
                raise SystemExit(0)'''
assert s.count(old)==1,'ambiguous training block'
s=s.replace(old,new)
compile(s,str(f),'exec')
f.write_text(s)
print(json.dumps({'original_trainer_sha256':expected,'instrumented_trainer_sha256':hashlib.sha256(s.encode()).hexdigest(),'scope':'first backward only; no optimizer, checkpoint, score'}))
