import torch
class GradCAM:
    def __init__(self,model,target_layer): self.model=model; self.target_layer=target_layer; self.activations=None; self.gradients=None; target_layer.register_forward_hook(self._save_activation); target_layer.register_full_backward_hook(self._save_gradient)
    def _save_activation(self,_,__,output): self.activations=output.detach()
    def _save_gradient(self,_,__,grad_output): self.gradients=grad_output[0].detach()
    def generate(self,x,class_index=None):
        self.model.zero_grad(set_to_none=True); logits=self.model(x)
        if class_index is None: class_index=int(logits[:,1:].mean((0,2,3)).argmax().item()+1) if logits.shape[1]>1 else 0
        logits[:,class_index].mean().backward(); weights=self.gradients.mean((2,3),keepdim=True); cam=torch.relu((weights*self.activations).sum(1,keepdim=True)); cam=torch.nn.functional.interpolate(cam,size=x.shape[-2:],mode="bilinear",align_corners=False); return cam/(cam.amax((2,3),keepdim=True)+1e-6)
