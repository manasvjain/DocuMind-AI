from fastapi import APIRouter,Depends,HTTPException,status
from sqlalchemy import select
from sqlalchemy.orm import Session
from app.api.deps import current_user,require_roles
from app.db.session import get_db
from app.models import Project,Role,User
from app.schemas.project import ProjectCreate,ProjectResponse,ProjectUpdate
router=APIRouter(prefix="/api/v1/projects",tags=["projects"])

def _get_owned(project_id,user,db):
    project=db.get(Project,project_id)
    if not project: raise HTTPException(404,"Project not found")
    if user.role!=Role.ADMIN and project.owner_id!=user.id: raise HTTPException(403,"Project access denied")
    return project

@router.post("",response_model=ProjectResponse,status_code=status.HTTP_201_CREATED)
def create_project(payload:ProjectCreate,db:Session=Depends(get_db),user:User=Depends(require_roles(Role.ADMIN,Role.SURVEYOR,Role.GIS_ANALYST))):
    project=Project(owner_id=user.id,**payload.model_dump()); db.add(project); db.commit(); db.refresh(project); return project

@router.get("",response_model=list[ProjectResponse])
def list_projects(db:Session=Depends(get_db),user:User=Depends(current_user)):
    stmt=select(Project) if user.role==Role.ADMIN else select(Project).where(Project.owner_id==user.id)
    return list(db.scalars(stmt.order_by(Project.created_at.desc())))

@router.get("/{project_id}",response_model=ProjectResponse)
def get_project(project_id:str,db:Session=Depends(get_db),user:User=Depends(current_user)): return _get_owned(project_id,user,db)

@router.put("/{project_id}",response_model=ProjectResponse)
def update_project(project_id:str,payload:ProjectUpdate,db:Session=Depends(get_db),user:User=Depends(require_roles(Role.ADMIN,Role.SURVEYOR,Role.GIS_ANALYST))):
    project=_get_owned(project_id,user,db)
    for key,value in payload.model_dump(exclude_unset=True).items(): setattr(project,key,value)
    db.commit(); db.refresh(project); return project

@router.delete("/{project_id}",status_code=204)
def delete_project(project_id:str,db:Session=Depends(get_db),user:User=Depends(require_roles(Role.ADMIN))):
    project=_get_owned(project_id,user,db); db.delete(project); db.commit()
