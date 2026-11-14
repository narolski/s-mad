"""Exact original packed trainer patch; no importing torch/model, weights or dataset."""
import ast
import hashlib
import json
import pathlib
import sys

ORIGINAL='e905cc241327d0a6f809ef3188ac395353ee4e502e3d91409892f89890b5f55d'

def patched(raw):
    assert hashlib.sha256(raw).hexdigest()==ORIGINAL,'wrong original packed trainer'
    s=raw.decode()
    old='''        for epoch in range(self.start_epoch, self.config.num_epoch):
            self.train_sampler.set_epoch(epoch)
            for _, (images, target) in enumerate(self.dataloader):'''
    # Only MAD_training, not the separate header-only method.
    assert s.count(old)==2
    new='''        from ad5_math_step_runtime import Probe
        probe = Probe(self, optimizer_model, optimizer_header)
        for epoch in range(self.start_epoch, self.config.num_epoch):
            self.train_sampler.set_epoch(epoch)
            probe.epoch(epoch)
            for _, (images, target) in enumerate(self.dataloader):'''
    s=s.replace(old,new,1)
    old='''                features_image = self.model.module.encode_image(images)
                _, loss_image = self.header(F.normalize(features_image), target)

                loss_image.backward()

                clip_grad_norm_(self.model.parameters(), max_norm=self.config.max_norm, norm_type=2)
                clip_grad_norm_(self.header.parameters(), max_norm=self.config.max_norm, norm_type=2)

                optimizer_model.step()
                optimizer_header.step()'''
    assert s.count(old)==1
    new='''                try:
                    probe.inputs(images, target)
                    with torch.backends.cuda.sdp_kernel(enable_flash=False, enable_math=True, enable_mem_efficient=False):
                        probe.backend()
                        features_image = self.model.module.encode_image(images)
                        _, loss_image = self.header(F.normalize(features_image), target)
                        probe.loss(loss_image)
                        loss_image.backward()
                        torch.cuda.synchronize()
                    probe.grads()
                    model_preclip_norm = clip_grad_norm_(self.model.parameters(), max_norm=self.config.max_norm, norm_type=2)
                    header_preclip_norm = clip_grad_norm_(self.header.parameters(), max_norm=self.config.max_norm, norm_type=2)
                    optimizer_model.step()
                    optimizer_header.step()
                    probe.finish(model_preclip_norm, header_preclip_norm)
                except BaseException as error:
                    probe.failed(error)
                    raise
                return  # Stop before poststep callbacks, schedules, evaluation or checkpoint. '''
    s=s.replace(old,new)
    ast.parse(s)
    return s.encode()


def main():
    root=pathlib.Path(sys.argv[1]);path=root/'build/madation_src/src/training/trainer.py';raw=path.read_bytes();new=patched(raw);path.write_bytes(new)
    import shutil
    here=pathlib.Path(__file__).resolve().parent
    shutil.copyfile(here/'runtime.py',path.parent.parent/'ad5_math_step_runtime.py')
    shutil.copyfile(here/'contract.py',path.parent.parent/'ad5_math_step_contract.py')
    print(json.dumps({'original_trainer_sha256':ORIGINAL,'patched_trainer_sha256':hashlib.sha256(new).hexdigest(),
       'change':'one math SDPA context; technical instrumentation and first-update stop only','optimizer_construction':'unchanged originaltwoAdamWobjects'}))


if __name__=='__main__':main()
