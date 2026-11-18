"""Patch exact ORIGINAL trainer, never one-step derivative."""
import ast,hashlib,json,pathlib,shutil,sys
ORIGINAL="e905cc241327d0a6f809ef3188ac395353ee4e502e3d91409892f89890b5f55d"
def patched(raw):
 assert hashlib.sha256(raw).hexdigest()==ORIGINAL
 s=raw.decode()
 old="        for epoch in range(self.start_epoch, self.config.num_epoch):\n            self.train_sampler.set_epoch(epoch)"
 new="        from ad5_full_math_runtime import MultiProbe\n        probe = MultiProbe(self, optimizer_model, optimizer_header)\n"+old+"\n            probe.epoch(epoch)"
 assert s.count(old)==2;s=s.replace(old,new,1)
 old="                features_image = self.model.module.encode_image(images)\n                _, loss_image = self.header(F.normalize(features_image), target)\n\n                loss_image.backward()"
 new="                probe.inputs(images, target)\n                with torch.backends.cuda.sdp_kernel(enable_flash=False, enable_math=True, enable_mem_efficient=False):\n                    probe.backend()\n                    features_image = self.model.module.encode_image(images)\n                    _, loss_image = self.header(F.normalize(features_image), target)\n                    probe.loss(loss_image)\n                    loss_image.backward()\n                probe.grads()"
 assert s.count(old)==1;s=s.replace(old,new)
 for group in ("model","header"):
  old="                clip_grad_norm_(self."+group+".parameters(), max_norm=self.config.max_norm, norm_type=2)"
  assert s.count(old)>=1;s=s.replace(old,"                "+group+"_preclip_norm = "+old.strip(),1)
 old="                optimizer_model.step()\n                optimizer_header.step()"
 assert s.count(old)==1;s=s.replace(old,old+"\n                probe.finish(model_preclip_norm, header_preclip_norm)")
 old="            self.callback_save_model(epoch, self.model, self.header)\n        self.tensorboard_callback.close()"
 assert s.count(old)==2;s=s.replace(old,"            self.callback_save_model(epoch, self.model, self.header)\n            probe.saved(epoch)\n        self.tensorboard_callback.close()\n        probe.done()",1)
 ast.parse(s);return s.encode()
def main():
 root=pathlib.Path(sys.argv[1]);p=root/"build/madation_src/src/training/trainer.py";raw=p.read_bytes();new=patched(raw);p.write_bytes(new)
 here=pathlib.Path(__file__).resolve().parent
 for src,dst in (("runtime.py","ad5_full_math_runtime.py"),("base_runtime.py","ad5_full_math_base.py"),("contract.py","ad5_full_math_contract.py")):shutil.copyfile(here/src,p.parent.parent/dst)
 print(json.dumps(dict(original_trainer_sha256=ORIGINAL,patched_trainer_sha256=hashlib.sha256(new).hexdigest(),change="math-only SDPA plus technical observation; all original MADtraining lifecycle preserved")))
if __name__=="__main__":main()
