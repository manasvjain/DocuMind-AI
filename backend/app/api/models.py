from pathlib import Path
from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile, status
from sqlalchemy import select
from sqlalchemy.orm import Session
from app.api.deps import current_user,require_roles
from app.db.session import get_db
from app.models import ModelVersion,Role,User
from app.schemas.model import ModelResponse
from app.services.storage import Storage
router=APIRouter(prefix="/api/v1/models",tags=["models"])

@router.get("",response_model=list[ModelResponse])
def list_models(db:Session=Depends(get_db),user:User=Depends(current_user)): return list(db.scalars(select(ModelVersion).order_by(ModelVersion.created_at.desc())))

@router.get("/comparison")
def comparison(db:Session=Depends(get_db),user:User=Depends(current_user)): return [{"name":m.name,"version":m.version,"architecture":m.architecture,"metrics":m.metrics,"status":m.status} for m in db.scalars(select(ModelVersion).order_by(ModelVersion.name,ModelVersion.version))]

@router.post("/upload",response_model=ModelResponse,status_code=status.HTTP_201_CREATED)
async def upload_model(name:str=Form(...),version:str=Form(...),architecture:str=Form(...),training_dataset:str=Form(...),checkpoint:UploadFile=File(...),db:Session=Depends(get_db),user:User=Depends(require_roles(Role.ADMIN))):
    if Path(checkpoint.filename or "").suffix.lower() not in {".pt",".pth"}: raise HTTPException(415,"Model checkpoint must be .pt or .pth")
    storage=Storage(); key=f"models/{name}/{version}/{checkpoint.filename}"
    try:
        await storage.save_upload(checkpoint,key,64*1024*1024)
        import torch; torch.load(storage.open_path(key),map_location="cpu",weights_only=True)
    except Exception as exc:
        storage.delete(key); raise HTTPException(400,f"Invalid PyTorch checkpoint: {exc}") from exc
    model=ModelVersion(name=name,version=version,architecture=architecture,training_dataset=training_dataset,classes=["background","building","road","water","vegetation","candidate parcel"],metrics=None,checkpoint_location=key,status="INACTIVE",is_demo=False)
    db.add(model); db.commit(); db.refresh(model); return model

@router.post("/{model_id}/activate",response_model=ModelResponse)
def activate(model_id:str,db:Session=Depends(get_db),user:User=Depends(require_roles(Role.ADMIN))):
    target=db.get(ModelVersion,model_id)
    if not target: raise HTTPException(404,"Model not found")
    for model in db.scalars(select(ModelVersion).where(ModelVersion.name==target.name)): model.status="ACTIVE" if model.id==target.id else "INACTIVE"
    db.commit(); db.refresh(target); return target

@router.post("/{model_id}/deactivate",response_model=ModelResponse)
def deactivate(model_id:str,db:Session=Depends(get_db),user:User=Depends(require_roles(Role.ADMIN))):
    target=db.get(ModelVersion,model_id)
    if not target: raise HTTPException(404,"Model not found")
    target.status="INACTIVE"; db.commit(); db.refresh(target); return target
