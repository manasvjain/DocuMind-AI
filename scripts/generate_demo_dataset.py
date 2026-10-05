from pathlib import Path
import numpy as np,rasterio
from rasterio.transform import from_origin
ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'data/demo';OUT.mkdir(parents=True,exist_ok=True)

def build(h=768,w=1024):
    rng=np.random.default_rng(42);img=np.zeros((3,h,w),np.uint8);img[:]=[80,120,80];mask=np.zeros((h,w),np.uint8)
    for i in range(24):
        y=int(rng.integers(40,h-100));x=int(rng.integers(40,w-120));hh=int(rng.integers(40,100));ww=int(rng.integers(50,120));img[:,y:y+hh,x:x+ww]=[190,190,185];mask[y:y+hh,x:x+ww]=1
    img[:,h//2-18:h//2+18,:]=[95,95,95];mask[h//2-18:h//2+18,:]=2;img[80:180,80:220]=[60,100,190];mask[80:180,80:220]=3;img[:,250:430,700:900]=[50,150,70];mask[250:430,700:900]=4
    return img,mask
img,mask=build();transform=from_origin(500000,2490000,.5,.5)
for name,data,count,dtype in [('demo_village_orthophoto.tif',img,3,'uint8'),('images/synthetic_village_7.tif',img,3,'uint8'),('masks/synthetic_village_7.tif',mask[None],1,'uint8')]:
    p=OUT/name;p.parent.mkdir(parents=True,exist_ok=True)
    with rasterio.open(p,'w',driver='GTiff',height=data.shape[1],width=data.shape[2],count=count,dtype=dtype,crs='EPSG:32643',transform=transform) as dst:dst.write(data)
print('Generated DEMO ONLY dataset under data/demo')
