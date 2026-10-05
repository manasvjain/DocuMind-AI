import torch
from torch import nn
class ASPP(nn.Module):
    def __init__(self,in_ch,out_ch=128):
        super().__init__();rates=(1,6,12,18);self.branches=nn.ModuleList([nn.Conv2d(in_ch,out_ch,3 if r>1 else 1,padding=r if r>1 else 0,dilation=r,bias=False) for r in rates]);self.project=nn.Sequential(nn.Conv2d(out_ch*len(rates),out_ch,1,bias=False),nn.BatchNorm2d(out_ch),nn.ReLU(inplace=True))
    def forward(self,x): return self.project(torch.cat([nn.functional.relu(b(x)) for b in self.branches],1))
class DeepLabV3PlusLite(nn.Module):
    def __init__(self,in_channels=3,num_classes=6,base=32):
        super().__init__();self.low=nn.Sequential(nn.Conv2d(in_channels,base,3,padding=1,stride=2,bias=False),nn.BatchNorm2d(base),nn.ReLU(inplace=True));self.mid=nn.Sequential(nn.Conv2d(base,base*4,3,padding=1,stride=2,bias=False),nn.BatchNorm2d(base*4),nn.ReLU(inplace=True));self.high=nn.Sequential(nn.Conv2d(base*4,base*8,3,padding=1,stride=2,bias=False),nn.BatchNorm2d(base*8),nn.ReLU(inplace=True));self.aspp=ASPP(base*8,base*4);self.low_proj=nn.Conv2d(base,48,1);self.decoder=nn.Sequential(nn.Conv2d(base*4+48,base*4,3,padding=1,bias=False),nn.BatchNorm2d(base*4),nn.ReLU(inplace=True),nn.Conv2d(base*4,base*2,3,padding=1,bias=False),nn.BatchNorm2d(base*2),nn.ReLU(inplace=True),nn.Conv2d(base*2,num_classes,1))
    def forward(self,x):
        low=self.low(x);x=self.mid(low);x=self.high(x);x=self.aspp(x);x=nn.functional.interpolate(x,size=low.shape[-2:],mode="bilinear",align_corners=False);x=self.decoder(torch.cat([x,self.low_proj(low)],1));return nn.functional.interpolate(x,size=(x.shape[-2]*2,x.shape[-1]*2),mode="bilinear",align_corners=False)
