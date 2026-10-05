import argparse,random,yaml,torch,numpy as np
from pathlib import Path
from torch.utils.data import DataLoader,random_split
from ml.datasets.segmentation_dataset import GeoTiffMaskDataset
from ml.models import create_model
from ml.training.losses import build_loss
from ml.evaluation.metrics import segmentation_metrics

def seed_all(seed):random.seed(seed);np.random.seed(seed);torch.manual_seed(seed);torch.cuda.manual_seed_all(seed)
def main():
    ap=argparse.ArgumentParser();ap.add_argument('--config',required=True);a=ap.parse_args();cfg=yaml.safe_load(Path(a.config).read_text());seed_all(int(cfg.get('seed',42)))
    image_paths=sorted(Path(cfg['image_dir']).glob('*.tif'));mask_paths=[Path(cfg['mask_dir'])/p.name for p in image_paths]
    ds=GeoTiffMaskDataset(image_paths,mask_paths,int(cfg.get('image_size',256)),augment=True)
    n=max(1,int(len(ds)*cfg.get('val_fraction',.2)));train,val=random_split(ds,[len(ds)-n,n],generator=torch.Generator().manual_seed(int(cfg.get('seed',42))));train_ds=torch.utils.data.Subset(ds,train.indices);val_ds=torch.utils.data.Subset(ds,val.indices);val_ds.dataset.augment=False
    device=torch.device('cuda' if torch.cuda.is_available() else 'cpu');model=create_model(cfg.get('model','unet'),num_classes=int(cfg.get('num_classes',6))).to(device);opt=torch.optim.AdamW(model.parameters(),lr=float(cfg.get('learning_rate',1e-3)));loss_fn=build_loss(cfg.get('loss','dice_ce'));best=1e9
    for epoch in range(int(cfg.get('epochs',10))):
        model.train();total=0
        for x,y in DataLoader(train_ds,batch_size=int(cfg.get('batch_size',4)),shuffle=True):
            x,y=x.to(device),y.to(device);opt.zero_grad(set_to_none=True);loss=loss_fn(model(x),y);loss.backward();opt.step();total+=float(loss)
        model.eval();ys=[];ps=[]
        with torch.no_grad():
            for x,y in DataLoader(val_ds,batch_size=int(cfg.get('batch_size',4))):
                pred=model(x.to(device)).argmax(1).cpu().numpy();ys.append(y.numpy());ps.append(pred)
        metrics=segmentation_metrics(np.concatenate(ys),np.concatenate(ps),int(cfg.get('num_classes',6)));val_loss=1-metrics['mean_iou'];print({'epoch':epoch+1,'train_loss':total/max(1,len(DataLoader(train_ds,batch_size=int(cfg.get('batch_size',4))))),'metrics':metrics})
        if val_loss<best:
            best=val_loss;out=Path(cfg.get('output_dir','data/models'));out.mkdir(parents=True,exist_ok=True);torch.save({'model_state':model.state_dict(),'metrics':metrics,'config':cfg,'epoch':epoch+1},out/'unet_baseline.pt')
if __name__=='__main__':main()
