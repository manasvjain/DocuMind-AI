from pathlib import Path
from uuid import uuid4
from fastapi import APIRouter, Depends, File, HTTPException, UploadFile, status
from fastapi.responses import Response
from sqlalchemy import select
from sqlalchemy.orm import Session
from app.api.deps import current_user, require_roles
from app.core.config import get_settings
from app.db.session import get_db
from app.models import Imagery, Project, Role, User
from app.schemas.imagery import ImageryResponse
from app.services.image_validation import ALLOWED_MIME, inspect_raster
from app.services.storage import Storage

router=APIRouter(prefix="/api/v1/imagery",tags=["imagery"]); settings=get_settings(); storage=Storage()

@router.get("",response_model=list[ImageryResponse])
def list_imagery(project_id:str,db:Session=Depends(get_db),user:User=Depends(current_user)):
    project=db.get(Project,project_id)
    if not project: raise HTTPException(404,"Project not found")
    if user.role!=Role.ADMIN and project.owner_id!=user.id: raise HTTPException(403,"Project access denied")
    return list(db.scalars(select(Imagery).where(Imagery.project_id==project_id).order_by(Imagery.created_at.desc())))

@router.post("/upload",response_model=ImageryResponse,status_code=status.HTTP_201_CREATED)
async def upload(project_id:str,file:UploadFile=File(...),db:Session=Depends(get_db),user:User=Depends(require_roles(Role.ADMIN,Role.SURVEYOR,Role.GIS_ANALYST))):
    project=db.get(Project,project_id)
    if not project: raise HTTPException(404,"Project not found")
    if user.role!=Role.ADMIN and project.owner_id!=user.id: raise HTTPException(403,"Project access denied")
    extension=Path(file.filename or "").suffix.lower()
    if extension not in {".tif",".tiff",".jpg",".jpeg",".png"}: raise HTTPException(415,"Supported formats: GeoTIFF/TIFF/JPG/PNG")
    if file.content_type and file.content_type not in ALLOWED_MIME: raise HTTPException(415,"Unsupported MIME type")
    key=f"imagery/{project_id}/{uuid4()}{extension}"
    try:
        _,size=await storage.save_upload(file,key,settings.max_upload_size); meta=inspect_raster(storage.open_path(key))
    except ValueError as exc:
        storage.delete(key); raise HTTPException(400,str(exc)) from exc
    imagery=Imagery(project_id=project_id,original_name=file.filename or "upload",storage_key=key,mime_type=file.content_type or "application/octet-stream",size_bytes=size,**meta)
    db.add(imagery); db.commit(); db.refresh(imagery); return imagery

@router.get("/{imagery_id}",response_model=ImageryResponse)
def get_imagery(imagery_id:str,db:Session=Depends(get_db),user:User=Depends(current_user)):
    imagery=db.get(Imagery,imagery_id)
    if not imagery: raise HTTPException(404,"Imagery not found")
    project=db.get(Project,imagery.project_id)
    if user.role!=Role.ADMIN and project.owner_id!=user.id: raise HTTPException(403,"Imagery access denied")
    return imagery

@router.get("/{imagery_id}/bounds")
def imagery_bounds(imagery_id:str,db:Session=Depends(get_db),user:User=Depends(current_user)):
    imagery=get_imagery(imagery_id,db,user)
    if not imagery.georeferenced or not imagery.crs or not imagery.bounds: return {"georeferenced":False,"bounds_wgs84":None}
    from pyproj import CRS,Transformer
    from shapely.geometry import box
    from shapely.ops import transform
    try:
        geom=transform(Transformer.from_crs(CRS.from_user_input(imagery.crs),CRS.from_epsg(4326),always_xy=True).transform,box(imagery.bounds["left"],imagery.bounds["bottom"],imagery.bounds["right"],imagery.bounds["top"]))
        minx,miny,maxx,maxy=geom.bounds
        return {"georeferenced":True,"bounds_wgs84":{"left":minx,"bottom":miny,"right":maxx,"top":maxy}}
    except Exception as exc: raise HTTPException(400,f"Unable to transform imagery bounds: {exc}") from exc

@router.get("/{imagery_id}/preview")
def preview_imagery(imagery_id:str,max_size:int=1600,db:Session=Depends(get_db),user:User=Depends(current_user)):
    if max_size<128 or max_size>4096: raise HTTPException(400,"max_size must be between 128 and 4096")
    imagery=get_imagery(imagery_id,db,user); path=storage.open_path(imagery.storage_key)
    try:
        import io,numpy as np,rasterio
        from PIL import Image
        with rasterio.open(path) as src:
            scale=min(1.0,max_size/max(src.width,src.height)); ow=max(1,int(src.width*scale)); oh=max(1,int(src.height*scale)); count=min(3,src.count)
            arr=src.read(out_shape=(count,oh,ow),resampling=rasterio.enums.Resampling.bilinear); rgb=np.repeat(arr,3,axis=0) if count==1 else arr[:3]; rgb=np.moveaxis(rgb,0,-1)
            if np.issubdtype(rgb.dtype,np.integer):
                info=np.iinfo(rgb.dtype); rgb=((rgb.astype(np.float32)-info.min)/max(1.0,info.max-info.min)*255).clip(0,255).astype(np.uint8)
            else:
                lo,hi=np.percentile(rgb,[2,98]) if rgb.size else (0.0,1.0); rgb=((rgb-lo)/max(1e-6,hi-lo)*255).clip(0,255).astype(np.uint8)
            buf=io.BytesIO(); Image.fromarray(rgb,mode="RGB").save(buf,format="PNG",optimize=True); return Response(content=buf.getvalue(),media_type="image/png")
    except Exception as exc: raise HTTPException(400,f"Unable to create preview: {exc}") from exc

@router.delete("/{imagery_id}",status_code=204)
def delete_imagery(imagery_id:str,db:Session=Depends(get_db),user:User=Depends(current_user)):
    imagery=get_imagery(imagery_id,db,user); storage.delete(imagery.storage_key); db.delete(imagery); db.commit()
