import torch
from torch import nn
class MLP(nn.Module):
    def __init__(self,d,hidden): super().__init__();self.net=nn.Sequential(nn.Linear(d,hidden),nn.GELU(),nn.Linear(hidden,d))
    def forward(self,x): return self.net(x)
class TransformerBlock(nn.Module):
    def __init__(self,d,heads=4,mlp_ratio=4): super().__init__();self.norm1=nn.LayerNorm(d);self.attn=nn.MultiheadAttention(d,heads,batch_first=True);self.norm2=nn.LayerNorm(d);self.mlp=MLP(d,d*mlp_ratio)
    def forward(self,x): y=self.norm1(x);x=x+self.attn(y,y,y,need_weights=False)[0];return x+self.mlp(self.norm2(x))
class SegFormerTiny(nn.Module):
    def __init__(self,in_channels=3,num_classes=6,embed_dim=64):
        super().__init__();self.patch=nn.Conv2d(in_channels,embed_dim,7,stride=4,padding=3);self.block1=nn.Sequential(*[TransformerBlock(embed_dim,heads=4) for _ in range(2)]);self.proj=nn.Conv2d(embed_dim,embed_dim*2,3,stride=2,padding=1);self.block2=nn.Sequential(*[TransformerBlock(embed_dim*2,heads=8) for _ in range(2)]);self.head=nn.Sequential(nn.Conv2d(embed_dim*2,embed_dim,1),nn.GELU(),nn.Conv2d(embed_dim,num_classes,1))
    def forward(self,x):
        x=self.patch(x);b,c,h,w=x.shape;x=self.block1(x.flatten(2).transpose(1,2)).transpose(1,2).reshape(b,c,h,w);x=self.proj(x);b,c,h,w=x.shape;x=self.block2(x.flatten(2).transpose(1,2)).transpose(1,2).reshape(b,c,h,w);return nn.functional.interpolate(self.head(x),scale_factor=8,mode="bilinear",align_corners=False)
