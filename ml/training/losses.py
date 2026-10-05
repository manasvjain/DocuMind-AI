import torch
from torch import nn
class DiceLoss(nn.Module):
    def forward(self,logits,targets):
        probs=torch.softmax(logits,1);c=logits.shape[1];one=torch.nn.functional.one_hot(targets.clamp(0,c-1),c).permute(0,3,1,2).float();inter=(probs*one).sum((0,2,3));den=probs.sum((0,2,3))+one.sum((0,2,3));return 1-((2*inter+1)/(den+1)).mean()
class FocalLoss(nn.Module):
    def __init__(self,gamma=2.):super().__init__();self.gamma=gamma
    def forward(self,logits,targets):
        ce=torch.nn.functional.cross_entropy(logits,targets);pt=torch.exp(-ce);return ((1-pt)**self.gamma*ce)
class CombinedDiceCELoss(nn.Module):
    def __init__(self):super().__init__();self.dice=DiceLoss();self.ce=nn.CrossEntropyLoss()
    def forward(self,logits,targets):return .5*self.dice(logits,targets)+.5*self.ce(logits,targets)
def build_loss(name):
    k=name.lower().replace(' ','_');return nn.CrossEntropyLoss() if k in {'ce','cross_entropy'} else DiceLoss() if k=='dice' else FocalLoss() if k=='focal' else CombinedDiceCELoss() if k in {'dice_ce','combined','combined_dice_ce'} else (_ for _ in ()).throw(ValueError('Unknown loss: '+name))
