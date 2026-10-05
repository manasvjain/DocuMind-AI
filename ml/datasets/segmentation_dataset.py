from pathlib import Path
import cv2,numpy as np,rasterio,torch
from torch.utils.data import Dataset
from ml.preprocessing.transforms import AugmentationConfig,augment_image_mask,normalize_rgb
class GeoTiffMaskDataset(Dataset):
    def __init__(self,image_paths:list[Path],mask_paths:list[Path],image_size=256,normalize=True,augment=False,augmentation=None,seed=42):
        if len(image_paths)!=len(mask_paths) or not image_paths: raise ValueError("Image and mask path lists must be equally sized and non-empty")
        self.image_paths=image_paths; self.mask_paths=mask_paths; self.image_size=image_size; self.normalize=normalize; self.augment=augment; self.augmentation=augmentation or AugmentationConfig(); self.seed=seed
    def __len__(self): return len(self.image_paths)
    def __getitem__(self,idx):
        with rasterio.open(self.image_paths[idx]) as src: image=src.read()
        with rasterio.open(self.mask_paths[idx]) as src: mask=src.read(1)
        image=np.moveaxis(image[:3],0,-1)
        if self.augment:
            rng=np.random.default_rng(self.seed+idx+int(torch.randint(0,1_000_000,(1,)).item())); image,mask=augment_image_mask(image,mask,self.augmentation,rng,self.image_size)
        image=cv2.resize(image,(self.image_size,self.image_size),interpolation=cv2.INTER_AREA); mask=cv2.resize(mask,(self.image_size,self.image_size),interpolation=cv2.INTER_NEAREST)
        image=normalize_rgb(image) if self.normalize else image.astype(np.float32); image=np.moveaxis(image,-1,0)
        return torch.from_numpy(np.ascontiguousarray(image.astype(np.float32))),torch.from_numpy(mask.astype(np.int64))
