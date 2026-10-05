import torch
from torch import nn
class DoubleConv(nn.Module):
    def __init__(self,inp,out):
        super().__init__();self.block=nn.Sequential(nn.Conv2d(inp,out,3,padding=1,bias=False),nn.BatchNorm2d(out),nn.ReLU(inplace=True),nn.Conv2d(out,out,3,padding=1,bias=False),nn.BatchNorm2d(out),nn.ReLU(inplace=True))
    def forward(self,x): return self.block(x)
class UNet(nn.Module):
    def __init__(self,in_channels=3,num_classes=6,base_channels=32):
        super().__init__();self.pool=nn.MaxPool2d(2);self.e1=DoubleConv(in_channels,base_channels);self.e2=DoubleConv(base_channels,base_channels*2);self.e3=DoubleConv(base_channels*2,base_channels*4);self.e4=DoubleConv(base_channels*4,base_channels*8);self.b=DoubleConv(base_channels*8,base_channels*16);self.u4=nn.ConvTranspose2d(base_channels*16,base_channels*8,2,2);self.d4=DoubleConv(base_channels*16,base_channels*8);self.u3=nn.ConvTranspose2d(base_channels*8,base_channels*4,2,2);self.d3=DoubleConv(base_channels*8,base_channels*4);self.u2=nn.ConvTranspose2d(base_channels*4,base_channels*2,2,2);self.d2=DoubleConv(base_channels*4,base_channels*2);self.u1=nn.ConvTranspose2d(base_channels*2,base_channels,2,2);self.d1=DoubleConv(base_channels*2,base_channels);self.out=nn.Conv2d(base_channels,num_classes,1)
    @staticmethod
    def _cat(up,skip,block):
        dy=skip.size(2)-up.size(2);dx=skip.size(3)-up.size(3)
        if dx or dy: up=nn.functional.pad(up,[dx//2,dx-dx//2,dy//2,dy-dy//2])
        return block(torch.cat([skip,up],1))
    def forward(self,x):
        e1=self.e1(x);e2=self.e2(self.pool(e1));e3=self.e3(self.pool(e2));e4=self.e4(self.pool(e3));b=self.b(self.pool(e4));d4=self._cat(self.u4(b),e4,self.d4);d3=self._cat(self.u3(d4),e3,self.d3);d2=self._cat(self.u2(d3),e2,self.d2);d1=self._cat(self.u1(d2),e1,self.d1);return self.out(d1)
