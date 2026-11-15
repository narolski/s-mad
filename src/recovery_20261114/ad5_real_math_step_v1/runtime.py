"""Source-grounded technical instrumentation. Loaded only by separately released GPU worker."""
import hashlib
import json
import os
import pathlib
import threading
import time
import torch
from ad5_math_step_contract import expected_names,gradients,updates,batch_order


def put(path,value):
    with pathlib.Path(path).open('x') as f:
        json.dump(value,f,indent=2,allow_nan=False);f.write('\n');f.flush();os.fsync(f.fileno())
    fd=os.open(pathlib.Path(path).parent,os.O_RDONLY)
    try:os.fsync(fd)
    finally:os.close(fd)


class Probe:
    def __init__(self,trainer,optimizer_model,optimizer_header):
        self.t=trainer;self.optimizers={'model':optimizer_model,'header':optimizer_header}
        self.out=pathlib.Path(os.environ['AD5_STEP_OUT']);self.out.mkdir(parents=True,exist_ok=True)
        c=trainer.config
        assert (c.backbone_size,c.batch_size,c.lora_dropout,c.lora_r,c.lora_a,c.lr_model,c.lr_header)==('ViT-B/16',256,.4,2,4,1e-5,1e-4)
        assert c.num_epoch==3 and c.max_norm==5 and c.loss=='BinaryCrossEntropy'
        assert os.environ['AD5_SEED']=='401' and os.environ['ARM']=='B' and os.environ['AD5_NO_TEST']=='1'
        assert trainer.world_size==1 and trainer.rank==0 and len(trainer.trainset)==3311
        assert trainer.dataloader.batch_size==256 and trainer.dataloader.num_workers==0 and trainer.dataloader.drop_last
        assert trainer.dataloader.dataset is trainer.trainset
        assert torch.__version__=='2.0.1+cu118' and torch.version.cuda=='11.8' and torch.cuda.device_count()==1
        assert 'H100' in torch.cuda.get_device_name(0)
        self.parameters={'model':dict(trainer.model.module.named_parameters()),'header':dict(trainer.header.module.named_parameters())}
        expected=expected_names();self.before={};self.visits=[];self.lock=threading.Lock()
        for group,names in expected.items():
            actual=sorted(n for n,p in self.parameters[group].items() if p.requires_grad)
            assert actual==names,'source-derived expected trainable set mismatch '+group
            assert not self.optimizers[group].state,'optimizer moments must be newly constructed'
            for name in names:
                p=self.parameters[group][name];assert p.dtype==torch.float32 and torch.isfinite(p).all()
                self.before[group,name]=p.detach().clone()
        # Observe the ORIGINAL dataset method; return precisely its original result.
        cls=type(trainer.trainset);assert cls.__name__=='FaceDataset'
        original=cls.__getitem__;dataset=trainer.trainset
        def observed_getitem(obj,index):
            value=original(obj,index)
            if obj is dataset:
                with self.lock:self.visits.append(int(index))
            return value
        cls.__getitem__=observed_getitem
        self.expected=None;self.start=time.monotonic();self.forward_steps=0
        put(self.out/'SETUP.json',{'expected_trainable_names':expected,'source_gradient_rationale':'vision-only q/v LoRA all12blocks; only_lora freezes base/text; A firststep zero permitted because B initializedzero; BCE linearheader both parameters expected',
           'optimizer_groups':{k:[{n:g.get(n) for n in ('lr','betas','weight_decay','eps','amsgrad')} for g in o.param_groups] for k,o in self.optimizers.items()},
           'torch':torch.__version__,'cuda':torch.version.cuda,'device':torch.cuda.get_device_name(0),'world_size':1,'global_batch':256,'accumulation':1,
           'csv_rows':3311,'dtype':'float32','no_scores_images_or_checkpoint_saved':True})
    def epoch(self,epoch):
        assert epoch==0 and self.expected is None
        state=torch.get_rng_state().clone()
        self.expected=list(iter(self.t.train_sampler))[:256]
        assert torch.equal(state,torch.get_rng_state()),'sampler proof cannot advance global RNG'
        assert len(self.expected)==256 and self.t.train_sampler.num_replicas==1 and self.t.train_sampler.rank==0
    def inputs(self,images,target):
        self.forward_steps+=1;assert self.forward_steps==1
        assert tuple(images.shape)==(256,3,224,224) and images.dtype==torch.float32
        assert tuple(target.shape)==(256,) and target.dtype==torch.float32
        with self.lock:actual=self.visits[:256].copy()
        batch_order(self.expected,actual)
        crop=os.environ['AD5_CROP_ROOT'];ids=[];labels=[]
        for index in actual:
            row=self.t.trainset.data.iloc[index];path=str(row.iloc[0]);assert path.startswith(crop+'/')
            ids.append('CROP_ROOT'+path[len(crop):]);labels.append(1 if row.iloc[1]=='bonafide' else 0)
        assert target.detach().cpu().tolist()==labels
        torch.cuda.synchronize();torch.cuda.reset_peak_memory_stats()
        put(self.out/'FIRST_BATCH.json',{'actual_indices':actual,'original_sampler_indices':self.expected,'canonical_image_ids_in_order':ids,
           'order_sha256':hashlib.sha256(json.dumps(list(zip(actual,ids)),separators=(',',':')).encode()).hexdigest(),
           'sampler_seed':self.t.train_sampler.seed,'sampler_epoch':self.t.train_sampler.epoch,'global_batch':256,
           'images_shape':list(images.shape),'images_dtype':str(images.dtype),'target_shape':list(target.shape),'target_dtype':str(target.dtype),
           'preprocess':'UNCHANGED FaceDataset:cv2BGR/ToPIL/Resize224/RandomHorizontalFlip/ToTensor/Normalize0.5',
           'proof':'Original FIFO DataLoaderX+DistributedSampler, num_workers0; first256 completed dataset visits observed without replacing data/transform/output.'})
    def backend(self):
        flags={'flash':torch.backends.cuda.flash_sdp_enabled(),'math':torch.backends.cuda.math_sdp_enabled(),'memory_efficient':torch.backends.cuda.mem_efficient_sdp_enabled()}
        assert flags=={'flash':False,'math':True,'memory_efficient':False}
        put(self.out/'MATH_CONTEXT.json',flags)
    def loss(self,value):
        assert value.numel()==1 and torch.isfinite(value).all(),'nonfinite loss'
        put(self.out/'LOSS_FINITE.json',{'finite':True,'numeric_loss_not_reported':True})
    def grads(self):
        torch.cuda.synchronize();records={}
        for group,names in expected_names().items():
            records[group]={}
            for name in names:
                grad=self.parameters[group][name].grad
                records[group][name]={'present':grad is not None,'finite':bool(torch.isfinite(grad).all()) if grad is not None else False,
                    'norm':float(grad.detach().norm(2).item()) if grad is not None else 0.}
        put(self.out/'EXPECTED_GRADIENTS.json',records);gradients(records)
    def finish(self,model_norm,header_norm):
        torch.cuda.synchronize();norms={'model':float(model_norm.item()),'header':float(header_norm.item())}
        assert all(torch.isfinite(torch.tensor(x)) and x>0 for x in norms.values())
        records={}
        for group,names in expected_names().items():
            records[group]={}
            for name in names:
                p=self.parameters[group][name];state=self.optimizers[group].state.get(p,{})
                step=state.get('step');step=int(step.item()) if hasattr(step,'item') else step
                records[group][name]={'finite':bool(torch.isfinite(p).all()),'changed':not torch.equal(p.detach(),self.before[group,name]),'optimizer_step':step}
        put(self.out/'UPDATED_TRAINABLES.json',records);updates(records)
        put(self.out/'STEP_RESULT.json',{'status':'ONE_REAL_EFFECTIVE_STEP_MATH_ONLY_COMPLETE','optimizer_model_updates':1,'optimizer_header_updates':1,
            'effective_batches':1,'global_batch':256,'seed':401,'arm':'B','preclip_gradient_norm':norms,
            'peak_memory_allocated_bytes':torch.cuda.max_memory_allocated(),'elapsed_step_probe_seconds':time.monotonic()-self.start,
            'scientific_performance':'NOT_MEASURED','production_recovery':'NOT_ESTABLISHED','callbacks_scores_evaluation_checkpoint':'NOT_RUN_AFTER_UPDATE'})
        print('AD5_ONE_REAL_MATH_STEP_COMPLETE_NO_SCORES_OR_CHECKPOINT',flush=True)
    def failed(self,error):
        put(self.out/'STEP_FAILURE.json',{'status':'FAILED_OR_INCOMPLETE','error_type':type(error).__name__,'error':str(error),'automatic_retry':False,'production_recovery':'NOT_ESTABLISHED'})
