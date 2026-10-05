from fastapi import APIRouter,Depends,HTTPException,status
from sqlalchemy import select
from sqlalchemy.orm import Session
from app.api.deps import current_user,require_roles
from app.db.session import get_db
from app.models import Imagery,ModelVersion,ProcessingJob,Project,Role,User
from app.schemas.job import JobCreate,JobResponse
from app.services.storage import Storage
from app.workers.queue import queue
router=APIRouter(prefix='/api/v1/jobs',tags=['jobs'])

def _allowed(job,user,db):
    project=db.get(Project,job.project_id)
    if user.role!=Role.ADMIN and (not project or project.owner_id!=user.id): raise HTTPException(403,'Job access denied')
    return project

@router.post('',response_model=JobResponse,status_code=status.HTTP_202_ACCEPTED)
def create_job(payload:JobCreate,db:Session=Depends(get_db),user:User=Depends(require_roles(Role.ADMIN,Role.SURVEYOR,Role.GIS_ANALYST))):
    project=db.get(Project,payload.project_id); imagery=db.get(Imagery,payload.imagery_id)
    if not project or not imagery or imagery.project_id!=project.id: raise HTTPException(404,'Project or imagery not found')
    if user.role!=Role.ADMIN and project.owner_id!=user.id: raise HTTPException(403,'Project access denied')
    checkpoint=None; chosen_version=payload.model_version; storage=Storage()
    if chosen_version:
        model=db.scalar(select(ModelVersion).where(ModelVersion.name==payload.model_name,ModelVersion.version==chosen_version))
    else:
        model=db.scalar(select(ModelVersion).where(ModelVersion.name==payload.model_name,ModelVersion.status=='ACTIVE'))
        chosen_version=model.version if model else None
    if model and model.checkpoint_location: checkpoint=str(storage.open_path(model.checkpoint_location))
    job=ProcessingJob(project_id=project.id,imagery_id=imagery.id,created_by=user.id,model_name=payload.model_name,model_version=chosen_version)
    project.processing_status='QUEUED'; project.model_version=chosen_version; db.add(job); db.commit(); db.refresh(job); queue.submit(job.id,checkpoint); return job

@router.get('',response_model=list[JobResponse])
def list_jobs(project_id:str|None=None,db:Session=Depends(get_db),user:User=Depends(current_user)):
    stmt=select(ProcessingJob)
    if user.role!=Role.ADMIN: stmt=stmt.where(ProcessingJob.project_id.in_(select(Project.id).where(Project.owner_id==user.id)))
    if project_id: stmt=stmt.where(ProcessingJob.project_id==project_id)
    return list(db.scalars(stmt.order_by(ProcessingJob.created_at.desc())))

@router.get('/{job_id}',response_model=JobResponse)
def get_job(job_id:str,db:Session=Depends(get_db),user:User=Depends(current_user)):
    job=db.get(ProcessingJob,job_id)
    if not job: raise HTTPException(404,'Job not found')
    _allowed(job,user,db); return job

@router.get('/{job_id}/status')
def job_status(job_id:str,db:Session=Depends(get_db),user:User=Depends(current_user)):
    job=get_job(job_id,db,user)
    return {'id':job.id,'status':job.status,'stage':job.stage,'progress':job.progress,'error':job.error,'elapsed_seconds':job.elapsed_seconds if hasattr(job,'elapsed_seconds') else None}

@router.get('/{job_id}/logs')
def job_logs(job_id:str,db:Session=Depends(get_db),user:User=Depends(current_user)):
    job=get_job(job_id,db,user); return {'job_id':job.id,'logs':getattr(job,'logs',[]) or []}
