from pathlib import Path
import numpy as np,rasterio,torch
from ml.models import create_model
from ml.preprocessing.transforms import normalize_rgb
class SegmentationPredictor:
    def __init__(self,model_name,checkpoint,num_classes=6,device=None):
        self.model_name=model_name;self.device=torch.device(device or ("cuda" if torch.cuda.is_available() else "cpu"));self.model=create_model(model_name,num_classes=num_classes).to(self.device)
        if not checkpoint: raise FileNotFoundError("No trained segmentation checkpoint configured")
        ckpt=torch.load(checkpoint,map_location=self.device,weights_only=True);self.model.load_state_dict(ckpt.get("model_state",ckpt));self.model.eval()
    @torch.inference_mode()
    def predict_array(self,image):
        if image.shape[0]<3:image=np.repeat(image,3,axis=0)
        image=normalize_rgb(np.moveaxis(image[:3],0,-1)); tensor=torch.from_numpy(np.moveaxis(image,-1,0)).float().unsqueeze(0).to(self.device); probs=torch.softmax(self.model(tensor),1); conf,mask=probs.max(1); return mask[0].cpu().numpy().astype(np.uint8),conf[0].cpu().numpy().astype(np.float32)
def predict_geotiff(path,predictor,tile_size=512,overlap=64):
    from gis.raster.tiling import iter_tiles
    with rasterio.open(path) as src:
        mask=np.zeros((src.height,src.width),dtype=np.uint8);conf=np.zeros((src.height,src.width),dtype=np.float32);count=np.zeros((src.height,src.width),dtype=np.float32)
        for tile in iter_tiles(src.width,src.height,tile_size,overlap):
            m,c=predictor.predict_array(src.read(window=tile.window));y0,x0=int(tile.window.row_off),int(tile.window.col_off);h,w=m.shape;mask[y0:y0+h,x0:x0+w]=m;conf[y0:y0+h,x0:x0+w]+=c;count[y0:y0+h,x0:x0+w]+=1
        return mask,conf/np.maximum(count,1),{"crs":src.crs.to_string() if src.crs else None,"transform":src.transform,"width":src.width,"height":src.height}
