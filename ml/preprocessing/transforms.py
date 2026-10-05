from dataclasses import dataclass
import cv2,numpy as np
def normalize_rgb(image):
    image=image.astype(np.float32);return image/255.0 if image.size and image.max()>1.5 else image
def optional_hsv(image_rgb,enabled=False): return cv2.cvtColor(image_rgb,cv2.COLOR_RGB2HSV) if enabled else image_rgb
@dataclass(frozen=True)
class AugmentationConfig:
    horizontal_flip:bool=True;vertical_flip:bool=True;rotation:bool=True;random_crop:bool=False;brightness_contrast:bool=True;noise:bool=False
def augment_image_mask(image,mask,config,rng,output_size):
    if config.horizontal_flip and rng.random()<.5:image,mask=np.flip(image,1).copy(),np.flip(mask,1).copy()
    if config.vertical_flip and rng.random()<.5:image,mask=np.flip(image,0).copy(),np.flip(mask,0).copy()
    if config.rotation and rng.random()<.75:
        k=int(rng.integers(1,4));image,mask=np.rot90(image,k).copy(),np.rot90(mask,k).copy()
    if config.random_crop:
        h,w=mask.shape[:2];ch=max(output_size,min(h,int(h*rng.uniform(.7,1))));cw=max(output_size,min(w,int(w*rng.uniform(.7,1))))
        if ch<h or cw<w:
            y0=int(rng.integers(0,h-ch+1));x0=int(rng.integers(0,w-cw+1));image,mask=image[y0:y0+ch,x0:x0+cw],mask[y0:y0+ch,x0:x0+cw]
    if config.brightness_contrast and rng.random()<.5:image=np.clip(image.astype(np.float32)*rng.uniform(.85,1.15)+rng.uniform(-.1,.1)*255,0,255).astype(np.uint8)
    if config.noise and rng.random()<.25:image=np.clip(image.astype(np.float32)+rng.normal(0,5,image.shape),0,255).astype(np.uint8)
    return image,mask
