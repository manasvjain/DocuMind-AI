from __future__ import annotations
import json,logging
from datetime import datetime,timezone
from pathlib import Path
import cv2,numpy as np,rasterio
from sqlalchemy.orm import Session
from app.core.config import get_settings
from app.gis.metrics import compactness
from app.gis.vectorize import polygonize_class
from app.models import Project,Building,Imagery,JobStatus,Parcel,Prediction,ProcessingJob,Road,RoofPrediction,Vegetation,WaterBody
from gis.raster.tiling import iter_tiles
from ml.inference.predict import SegmentationPredictor
from ml.roof_classifier import RoofClassifier
logger=logging.getLogger(__name__); settings=get_settings()
CLASS_IDS={"building":1,"road":2,"water":3,"vegetation":4,"parcel":5}

def _update_job(db,job,status,stage,progress,**extra):
    job.status=status; job.stage=stage; job.progress=max(0,min(100,progress))
    for key,value in extra.items(): setattr(job,key,value)
    db.commit(); db.refresh(job)
    logger.info("job stage",extra={"job_id":job.id,"project_id":job.project_id,"image_id":job.imagery_id,"stage":stage,"status":status.value})

def demo_segment(tile_rgb):
    rgb=np.moveaxis(tile_rgb[:3],0,-1) if tile_rgb.shape[0]>=3 else np.repeat(np.moveaxis(tile_rgb,0,-1),3,axis=-1)
    rgb=np.clip(rgb,0,255).astype(np.uint8); hsv=cv2.cvtColor(rgb,cv2.COLOR_RGB2HSV); r,g,b=rgb[...,0],rgb[...,1],rgb[...,2]
    mask=np.zeros(rgb.shape[:2],dtype=np.uint8); water=(b>r+35)&(b>g+15); vegetation=(g>r+15)&(g>b+5)&(g>70); building=(np.abs(r.astype(int)-g.astype(int))<20)&(np.abs(g.astype(int)-b.astype(int))<20)&(r>150); road=(r<105)&(g<105)&(b<105)&(~water)&(~vegetation); parcel=(hsv[...,0]>10)&(hsv[...,0]<30)&(hsv[...,1]>70)&(hsv[...,2]>90)
    mask[vegetation]=4; mask[water]=3; mask[road]=2; mask[building]=1; mask[parcel]=5
    return mask,np.where(mask==0,.55,.92).astype(np.float32)

def run_processing_job(db:Session,job_id:str,checkpoint:str|None=None)->None:
    job=db.get(ProcessingJob,job_id)
    if not job: return
    imagery=db.get(Imagery,job.imagery_id)
    if not imagery: return
    job.started_at=datetime.now(timezone.utc); db.commit()
    try:
        _update_job(db,job,JobStatus.VALIDATING,"VALIDATING",5); image_path=Path(settings.storage_root)/imagery.storage_key
        if not image_path.exists(): raise FileNotFoundError(f"Stored imagery missing: {imagery.storage_key}")
        if not imagery.georeferenced or not imagery.crs: raise ValueError("A georeferenced raster with CRS is required for GIS output")
        tiles=list(iter_tiles(imagery.width,imagery.height,settings.default_tile_size,settings.default_tile_overlap)); output=settings.storage_root/"jobs"/job.id; output.mkdir(parents=True,exist_ok=True)
        (output/"tiles.json").write_text(json.dumps([{"row":t.row,"col":t.col,"x":int(t.window.col_off),"y":int(t.window.row_off),"width":int(t.window.width),"height":int(t.window.height)} for t in tiles],indent=2)); _update_job(db,job,JobStatus.TILING,"TILING",20)
        predictor=SegmentationPredictor(job.model_name,checkpoint,num_classes=6) if checkpoint else None
        demo=checkpoint is None and imagery.is_demo and settings.demo_mode
        if not predictor and not demo: raise FileNotFoundError("No trained segmentation checkpoint is configured for non-demo imagery")
        mask=np.memmap(output/"prediction_mask.dat",mode="w+",dtype=np.uint8,shape=(imagery.height,imagery.width)); conf=np.memmap(output/"confidence.dat",mode="w+",dtype=np.float32,shape=(imagery.height,imagery.width)); mask[:]=0; conf[:]=0
        _update_job(db,job,JobStatus.INFERENCE,"INFERENCE (DEMO)" if demo else "INFERENCE",35)
        with rasterio.open(image_path) as src:
            for i,tile in enumerate(tiles,1):
                arr=src.read(window=tile.window); pred,c=demo_segment(arr) if demo else predictor.predict_array(arr); y0,x0=int(tile.window.row_off),int(tile.window.col_off); h,w=pred.shape; mask[y0:y0+h,x0:x0+w]=pred; conf[y0:y0+h,x0:x0+w]=c
                if i%max(1,len(tiles)//10)==0: _update_job(db,job,JobStatus.INFERENCE,"INFERENCE (DEMO)" if demo else "INFERENCE",35+25*i/len(tiles))
            _update_job(db,job,JobStatus.POSTPROCESSING,"POSTPROCESSING",65)
            prediction=Prediction(job_id=job.id,project_id=job.project_id,imagery_id=imagery.id,model_name=job.model_name,model_version=job.model_version,confidence_mean=float(conf.mean()),status="DEMO" if demo else "COMPLETED"); db.add(prediction); db.commit(); db.refresh(prediction)
            _update_job(db,job,JobStatus.GIS_CONVERSION,"GIS_CONVERSION",72)
            for layer,class_id in CLASS_IDS.items():
                feats=polygonize_class(np.asarray(mask),class_id,src.transform,imagery.crs,min_area_m2=1.0)
                for feat in feats:
                    geometry=feat["geometry"]; confidence=float(np.mean(np.asarray(conf)[np.abs(np.asarray(mask)-class_id)<1])) if np.any(np.asarray(mask)==class_id) else 0.0
                    if layer=="building":
                        row=Building(prediction_id=prediction.id,project_id=job.project_id,geometry=geometry,area_m2=feat["area_m2"],perimeter_m=feat["perimeter_m"],compactness=compactness(feat["area_m2"],feat["perimeter_m"]),confidence=confidence,source_image_id=imagery.id,model_version=job.model_version,roof_type="Unknown",roof_confidence=0.0)
                    elif layer=="road": row=Road(prediction_id=prediction.id,project_id=job.project_id,geometry=geometry,length_m=feat["perimeter_m"],width_m=None,confidence=confidence,source_image_id=imagery.id,model_version=job.model_version)
                    elif layer=="water": row=WaterBody(prediction_id=prediction.id,project_id=job.project_id,geometry=geometry,area_m2=feat["area_m2"],perimeter_m=feat["perimeter_m"],confidence=confidence,source_image_id=imagery.id,model_version=job.model_version)
                    elif layer=="vegetation": row=Vegetation(prediction_id=prediction.id,project_id=job.project_id,geometry=geometry,area_m2=feat["area_m2"],coverage_pct=0.0,confidence=confidence,source_image_id=imagery.id,model_version=job.model_version)
                    else: row=Parcel(prediction_id=prediction.id,project_id=job.project_id,geometry=geometry,area_m2=feat["area_m2"],boundary_confidence=confidence,is_authoritative=False,source_image_id=imagery.id,model_version=job.model_version)
                    db.add(row)
            db.commit(); _update_job(db,job,JobStatus.ROOF_CLASSIFICATION,"ROOF_CLASSIFICATION",90)
            job.completed_at=datetime.now(timezone.utc); _update_job(db,job,JobStatus.COMPLETED,"COMPLETED",100); db.get(Project,job.project_id).processing_status="COMPLETED"; db.commit()
    except Exception as exc:
        job.status=JobStatus.FAILED; job.stage="FAILED"; job.error_message=str(exc); job.completed_at=datetime.now(timezone.utc); db.commit(); logger.exception("processing failed",extra={"job_id":job.id}); raise
